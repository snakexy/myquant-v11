"""
盘中 K线服务

提供盘中 K线数据获取，带路由选择和缓存

统一复权架构: 所有数据源返回不复权数据，服务层统一应用复权
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from enum import Enum
from loguru import logger

from myquant.core.market.models import KlineData, KlineDataset
from myquant.core.market.routing import DataLevel, get_source_selector
from myquant.core.market.adapters import get_adapter
from myquant.core.market.utils.adjustment_calculator import get_adjustment_calculator


class CacheStrategy(Enum):
    """缓存策略"""
    ENABLED = "enabled"       # 启用缓存
    DISABLED = "disabled"     # 禁用缓存
    FORCE_REFRESH = "force"   # 强制刷新


@dataclass
class IntradayKlineResult:
    """盘中 K线结果"""
    symbol: str
    period: str
    data: KlineDataset
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    from_cache: bool = False

    @property
    def latest_price(self) -> Optional[float]:
        """最新价格"""
        return self.data.get_latest_price()

    @property
    def change_pct(self) -> Optional[float]:
        """涨跌幅"""
        return self.data.get_change_pct()


class IntradayKlineService:
    """盘中 K线服务

    提供带路由选择和缓存的 K线数据获取
    """

    # 缓存 TTL 配置（秒）
    CACHE_TTL = {
        '1m': 10,     # 1分钟数据缓存10秒
        '5m': 60,     # 5分钟数据缓存60秒
        '15m': 120,   # 15分钟数据缓存2分钟
        '30m': 300,   # 30分钟数据缓存5分钟
        '1h': 600,    # 1小时数据缓存10分钟
        '1d': 3600,   # 日线数据缓存1小时
    }

    def __init__(self):
        self._cache: Dict[tuple, IntradayKlineResult] = {}
        self._selector = get_source_selector()

    def get_kline(
        self,
        symbols: List[str],
        period: str = '5m',
        count: int = 100,
        use_cache: bool = True,
        adapter: Optional[str] = None,
        adjust_type: str = 'none'
    ) -> Dict[str, IntradayKlineResult]:
        """获取 K线数据

        Args:
            symbols: 代码列表
            period: 周期 (1m/5m/15m/30m/1h/1d)
            count: 数据条数
            use_cache: 是否使用缓存
            adapter: 指定适配器（如果为 None，使用路由选择）
            adjust_type: 复权类型 (none/front/back/front_ratio/back_ratio)

        Returns:
            {symbol: IntradayKlineResult} 字典
        """
        result = {}

        for symbol in symbols:
            cache_key = (symbol, period, count, adjust_type)

            # 检查缓存
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached:
                    result[symbol] = cached
                    continue

            # 选择适配器
            if adapter is None:
                adapter = self._select_adapter(symbol, DataLevel.L3)

            if adapter is None:
                continue

            # 获取数据（不复权）
            try:
                adapter_instance = get_adapter(adapter)
                if adapter_instance and adapter_instance.is_available():
                    df_dict = adapter_instance.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=count,
                        adjust_type='none'  # 统一获取不复权数据
                    )

                    if symbol in df_dict:
                        # 应用复权
                        df = df_dict[symbol]
                        if adjust_type != 'none' and not df.empty:
                            df = self._apply_adjustment(df, symbol, adjust_type)

                        dataset = KlineDataset.from_adapter(df, adapter)
                        kline_result = IntradayKlineResult(
                            symbol=symbol,
                            period=period,
                            data=dataset,
                            source=adapter,
                            from_cache=False
                        )

                        # 存入缓存
                        if use_cache:
                            self._store_cache(cache_key, kline_result)

                        result[symbol] = kline_result

            except Exception as e:
                logger.warning(f"[IntradayKline] 获取 {symbol} 数据失败: {e}")
                continue

        return result

    def _apply_adjustment(
        self,
        df: pd.DataFrame,
        symbol: str,
        adjust_type: str
    ) -> pd.DataFrame:
        """应用复权

        Args:
            df: K线数据
            symbol: 股票代码
            adjust_type: 复权类型

        Returns:
            复权后的 DataFrame
        """
        try:
            calculator = get_adjustment_calculator()

            # 获取除权除息数据（优先 TdxQuant）
            xdxr_data = self._get_xdxr_data(symbol)

            if xdxr_data:
                df = calculator.apply_adjustment(df, xdxr_data, symbol, adjust_type)
                logger.debug(f"[IntradayKline] {symbol} 应用 {adjust_type} 复权完成")

        except Exception as e:
            logger.warning(f"[IntradayKline] {symbol} 复权计算失败: {e}")

        return df

    def _get_xdxr_data(self, symbol: str) -> list:
        """获取除权除息数据

        优先级: TdxQuant → PyTdx

        Args:
            symbol: 股票代码

        Returns:
            除权除息记录列表
        """
        # 优先从 TdxQuant 获取
        try:
            tdxquant = get_adapter('tdxquant')
            if tdxquant and tdxquant.is_available() and hasattr(tdxquant._tq, 'get_xdxr_info'):
                xdxr_data = tdxquant._tq.get_xdxr_info([symbol])
                if xdxr_data and symbol in xdxr_data:
                    return xdxr_data[symbol]
        except Exception:
            pass

        # 备用: 从 PyTdx 获取
        try:
            pytdx = get_adapter('pytdx')
            if pytdx and pytdx.is_available():
                return pytdx.get_xdxr_info(symbol)
        except Exception:
            pass

        return []

    def get_multi_period(
        self,
        symbol: str,
        periods: List[str] = None,
        count: int = 100
    ) -> Dict[str, IntradayKlineResult]:
        """获取多周期 K线

        Args:
            symbol: 代码
            periods: 周期列表 (默认 ['5m', '15m', '30m', '1h', '1d'])
            count: 每个周期的数据条数

        Returns:
            {period: IntradayKlineResult} 字典
        """
        if periods is None:
            periods = ['5m', '15m', '30m', '1h', '1d']

        result = {}
        for period in periods:
            kline_data = self.get_kline([symbol], period, count)
            if symbol in kline_data:
                result[period] = kline_data[symbol]

        return result

    def get_ohlcv(
        self,
        symbols: List[str],
        period: str = '5m',
        count: int = 100
    ) -> Dict[str, pd.DataFrame]:
        """获取标准 OHLCV 格式数据

        Args:
            symbols: 代码列表
            period: 周期
            count: 数据条数

        Returns:
            {symbol: DataFrame} 字典
        """
        kline_results = self.get_kline(symbols, period, count)

        result = {}
        for symbol, kline_result in kline_results.items():
            result[symbol] = kline_result.data.df

        return result

    def batch_get_kline(
        self,
        symbols: List[str],
        periods: List[str],
        count: int = 100
    ) -> Dict[str, Dict[str, IntradayKlineResult]]:
        """批量获取多周期 K线

        Args:
            symbols: 代码列表
            periods: 周期列表
            count: 数据条数

        Returns:
            {symbol: {period: IntradayKlineResult}} 字典
        """
        result = {}
        for symbol in symbols:
            result[symbol] = self.get_multi_period(symbol, periods, count)
        return result

    def get_latest_price(
        self,
        symbols: List[str],
        period: str = '1m'
    ) -> Dict[str, Optional[float]]:
        """获取最新价格

        Args:
            symbols: 代码列表
            period: 周期

        Returns:
            {symbol: latest_price} 字典
        """
        kline_results = self.get_kline(symbols, period, count=1)

        result = {}
        for symbol, kline_result in kline_results.items():
            result[symbol] = kline_result.latest_price

        return result

    def clear_cache(
        self,
        symbol: Optional[str] = None,
        period: Optional[str] = None
    ) -> None:
        """清空缓存

        Args:
            symbol: 指定代码（None 表示全部）
            period: 指定周期（None 表示全部）
        """
        if symbol is None and period is None:
            self._cache.clear()
        else:
            keys_to_remove = []
            for key in self._cache.keys():
                sym, per, _ = key
                if symbol is None or sym == symbol:
                    if period is None or per == period:
                        keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._cache[key]

    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        ttl_counts = {period: 0 for period in self.CACHE_TTL.keys()}

        for (symbol, period, count), result in self._cache.items():
            if period in ttl_counts:
                ttl_counts[period] += 1

        return {
            "total_cached_items": len(self._cache),
            "items_by_period": ttl_counts,
        }

    def _select_adapter(self, symbol: str, level: DataLevel) -> Optional[str]:
        """选择适配器（交易时间感知）

        非交易时间跳过 tdxquant/xtquant，直接用 pytdx（24/7 在线）
        避免触发 TdxQuant 终端连接尝试，也避免无意义的初始化报错
        """
        from myquant.core.market.utils.trading_time import TradingTimeChecker
        if not TradingTimeChecker.is_trading_time():
            adapter = get_adapter('pytdx')
            if adapter and adapter.is_available():
                return 'pytdx'
        return self._selector.select_by_code(level, symbol)

    def _get_from_cache(self, key: tuple) -> Optional[IntradayKlineResult]:
        """从缓存获取数据"""
        if key not in self._cache:
            return None

        symbol, period, _ = key
        result = self._cache[key]

        # 检查是否过期
        ttl = self.CACHE_TTL.get(period, 60)
        if datetime.now() - result.timestamp > timedelta(seconds=ttl):
            del self._cache[key]
            return None

        # 标记为来自缓存
        result.from_cache = True
        return result

    def _store_cache(self, key: tuple, result: IntradayKlineResult) -> None:
        """存储到缓存"""
        self._cache[key] = result


# 单例实例
_intraday_kline_service: Optional[IntradayKlineService] = None


def get_intraday_kline_service() -> IntradayKlineService:
    """获取 IntradayKlineService 单例实例"""
    global _intraday_kline_service
    if _intraday_kline_service is None:
        _intraday_kline_service = IntradayKlineService()
    return _intraday_kline_service
