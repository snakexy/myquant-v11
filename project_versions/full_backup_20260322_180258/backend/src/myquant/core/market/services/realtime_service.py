"""
实时行情服务

提供实时行情获取、K线数据、市场状态判断
API 层通过本服务获取数据，不直接调用适配器
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import pandas as pd
from loguru import logger

from ..adapters import get_adapter
from ..utils import TradingTimeChecker, TimePhase
from .cache import TTLCache


class RealtimeMarketService:
    """实时行情服务

    编排数据获取逻辑，根据交易状态选择最优数据源。
    API 层调用本服务，不直接调用适配器。
    """

    def __init__(self):
        self._quote_cache = TTLCache(maxsize=500, ttl=10)
        self._adapter_cache: Dict[str, object] = {}

    def _get_adapter_cached(self, name: str):
        """获取适配器单例（避免重复初始化 SDK）"""
        if name not in self._adapter_cache:
            adapter = get_adapter(name)
            if adapter is not None:
                self._adapter_cache[name] = adapter
        return self._adapter_cache.get(name)

    # ========== 市场状态 ==========

    def get_market_status(self) -> dict:
        """获取当前市场状态"""
        now = datetime.now()
        phase = TradingTimeChecker.get_current_phase()

        return {
            "is_open": TradingTimeChecker.is_trading_time(),
            "phase": phase.value,
            "phase_description": TradingTimeChecker.get_phase_description(),
            "market": "A股",
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "status": "交易中" if TradingTimeChecker.is_trading_time() else "休市",
            "is_weekend": phase == TimePhase.WEEKEND,
            "refresh_interval": TradingTimeChecker.get_next_refresh_interval(),
            "cache_ttl": TradingTimeChecker.get_cache_ttl(),
        }

    # ========== 适配器选择（基于交易时间） ==========

    def _select_snapshot_adapter(self) -> Optional[tuple]:
        """根据交易时间选择快照适配器

        Returns:
            (name, adapter) 或 None
        """
        is_trading = TradingTimeChecker.is_trading_time()

        if is_trading:
            # 交易时间：TdxQuant (0.60ms) → XtQuant → PyTdx
            for name in ['tdxquant', 'xtquant', 'pytdx']:
                adapter = self._get_adapter_cached(name)
                if adapter and adapter.is_available():
                    return (name, adapter)
        else:
            # 非交易时间：只有 PyTdx 24/7 在线
            adapter = self._get_adapter_cached('pytdx')
            if adapter and adapter.is_available():
                return ('pytdx', adapter)

        return None

    def _select_kline_adapter(self, period: str) -> Optional[tuple]:
        """根据交易时间和周期选择K线适配器

        Args:
            period: K线周期

        Returns:
            (name, adapter) 或 None
        """
        is_trading = TradingTimeChecker.is_trading_time()
        is_minute = period in ['1m', '5m', '15m', '30m', '1h']

        if is_trading and is_minute:
            # 交易时间分钟线：XtQuant (0.90ms) → PyTdx
            for name in ['xtquant', 'pytdx']:
                adapter = self._get_adapter_cached(name)
                if adapter and adapter.is_available():
                    return (name, adapter)
        else:
            # 日线或非交易时间：LocalDB → XtQuant → PyTdx
            for name in ['localdb', 'xtquant', 'pytdx']:
                adapter = self._get_adapter_cached(name)
                if adapter and adapter.is_available():
                    return (name, adapter)

        return None

    # ========== 实时行情 ==========

    def get_realtime_quotes(
        self,
        codes: List[str],
        use_cache: bool = True
    ) -> tuple:
        """获取实时行情（聚合基本行情 + 额外指标）

        Args:
            codes: 代码列表
            use_cache: 是否使用缓存

        Returns:
            (quotes_dict, data_source_name) 元组
        """
        result = {}
        data_source = ""

        # 尝试从缓存获取
        if use_cache:
            for code in codes:
                cached = self._quote_cache.get(f"quote:{code}")
                if cached is not None:
                    result[code] = cached

        remaining = [c for c in codes if c not in result]
        if not remaining:
            return (result, "cache")

        # 选择适配器
        selected = self._select_snapshot_adapter()
        if selected is None:
            logger.warning("没有可用的数据源")
            return (result, "none")

        source_name, adapter = selected
        logger.info(f"通过 {source_name} 获取 {len(remaining)} 只股票行情")

        try:
            # 1. 获取基本行情
            quotes = adapter.get_quote(remaining)
            if quotes:
                data_source = source_name
                for code, quote in quotes.items():
                    if quote:
                        result[code] = quote

                        # 2. 获取额外指标（如果适配器支持）
                        if hasattr(adapter, 'get_extra_indicators'):
                            try:
                                extra = adapter.get_extra_indicators(code)
                                if extra:
                                    # 合并额外指标到行情数据
                                    result[code].update(extra)
                                    logger.debug(f"{code} 获取到额外指标: {list(extra.keys())}")
                            except Exception as e:
                                logger.debug(f"{code} 获取额外指标失败: {e}")

                        # 3. 缓存完整数据
                        self._quote_cache.set(
                            f"quote:{code}",
                            result[code],
                            ttl=TradingTimeChecker.get_cache_ttl()
                        )
        except Exception as e:
            logger.warning(f"{source_name} 获取行情失败: {e}")

        return (result, data_source)

    # ========== K线数据 ==========

    def get_kline(
        self,
        symbol: str,
        period: str = '1d',
        count: int = 100
    ) -> tuple:
        """获取K线数据

        Args:
            symbol: 股票代码
            period: 周期 (1m/5m/15m/30m/1h/1d/1w)
            count: K线根数

        Returns:
            (dataframe, data_source_name) 元组
        """
        selected = self._select_kline_adapter(period)
        if selected is None:
            logger.warning(f"没有可用的K线数据源: {symbol}")
            return (None, "none")

        source_name, adapter = selected
        logger.info(f"通过 {source_name} 获取 {symbol} {period} K线")

        try:
            klines = adapter.get_kline(
                symbols=[symbol],
                period=period,
                count=count
            )
            if klines and symbol in klines:
                df = klines[symbol]
                if df is not None and not df.empty:
                    return (df, source_name)
        except Exception as e:
            logger.warning(f"{source_name} 获取K线失败: {e}")

        return (None, source_name)


# 单例实例
_service: Optional[RealtimeMarketService] = None


def get_realtime_market_service() -> RealtimeMarketService:
    """获取 RealtimeMarketService 单例实例"""
    global _service
    if _service is None:
        _service = RealtimeMarketService()
    return _service
