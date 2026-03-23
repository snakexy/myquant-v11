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

    def _get_adapter_cached(self, name: str, force_retry: bool = False):
        """获取适配器单例（避免重复初始化 SDK）

        Args:
            name: 适配器名称
            force_retry: 是否强制重试初始化（用于 TdxQuant 等可能初始化失败的适配器）
        """
        if name not in self._adapter_cache:
            adapter = get_adapter(name)
            if adapter is not None:
                # 如果是 TdxQuant 且强制重试，调用强制初始化
                if force_retry and name == 'tdxquant' and hasattr(adapter, '_ensure_initialized'):
                    adapter._ensure_initialized(force_retry=True)
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
                # TdxQuant 使用强制重试（因为可能之前初始化失败）
                adapter = self._get_adapter_cached(name, force_retry=(name=='tdxquant'))
                if adapter and adapter.is_available():
                    return (name, adapter)
        else:
            # 非交易时间：优先尝试 TdxQuant/XtQuant 获取完整字段
            for name in ['tdxquant', 'xtquant', 'pytdx']:
                # 对 TdxQuant 强制重试，避免之前的失败标志影响
                adapter = self._get_adapter_cached(name, force_retry=(name=='tdxquant'))
                if adapter and adapter.is_available():
                    logger.info(f"非交易时间使用 {name} 获取完整行情数据")
                    return (name, adapter)

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

    def _calculate_limit_prices(self, pre_close: float, code: str = '') -> tuple:
        """计算涨停跌停价

        A股规则：
        - 主板/中小板：±10%
        - ST股票：±5%
        - 科创板/创业板：±20%
        - 北交所：±30%

        简化判断：根据代码后缀和前缀
        """
        if not pre_close or pre_close <= 0:
            return (0, 0)

        # 判断是否为ST（简单判断，实际需要查询股票名称）
        is_st = False  # TODO: 从股票名称判断

        # 判断板块
        limit_up_percent = 0.10  # 默认10%
        limit_down_percent = 0.10

        if code.startswith('68'):  # 科创板
            limit_up_percent = 0.20
            limit_down_percent = 0.20
        elif code.startswith('30'):  # 创业板
            limit_up_percent = 0.20
            limit_down_percent = 0.20
        elif code.startswith('8') or code.startswith('4'):  # 北交所
            limit_up_percent = 0.30
            limit_down_percent = 0.30
        elif is_st:
            limit_up_percent = 0.05
            limit_down_percent = 0.05

        zt_price = round(pre_close * (1 + limit_up_percent), 2)
        dt_price = round(pre_close * (1 - limit_down_percent), 2)

        return (zt_price, dt_price)

    def _fill_calculated_fields(self, quote: dict) -> None:
        """补充可计算的字段

        Args:
            quote: 行情数据字典（会被修改）
        """
        pre_close = quote.get('pre_close', 0)

        # 计算涨停跌停价
        if pre_close and pre_close > 0:
            zt_price, dt_price = self._calculate_limit_prices(
                pre_close, quote.get('code', '')
            )
            quote['zt_price'] = zt_price
            quote['dt_price'] = dt_price

        # 计算振幅（如果已开盘）
        high = quote.get('high', 0)
        low = quote.get('low', 0)
        if high and low and high >= low:
            quote['amplitude'] = round((high - low) / pre_close * 100, 2) if pre_close else 0
        else:
            quote['amplitude'] = 0

    def get_realtime_quotes(
        self,
        codes: List[str],
        use_cache: bool = True
    ) -> tuple:
        """获取实时行情（聚合基本行情 + 额外指标，支持字段级数据源混合）

        主数据源获取大部分字段，如果缺少关键字段（如量比），自动从备用源补充。

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

        # 选择主适配器
        selected = self._select_snapshot_adapter()
        if selected is None:
            logger.warning("没有可用的数据源")
            return (result, "none")

        source_name, adapter = selected
        logger.info(f"通过 {source_name} 获取 {len(remaining)} 只股票行情")

        # 记录需要从备用源补充的字段
        missing_fields_codes = []

        try:
            # 1. 获取基本行情（主数据源）
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

                        # 3. 补充可计算的字段（涨停跌停价、振幅）
                        self._fill_calculated_fields(result[code])

                        # 检查是否有关键字段缺失（如量比）
                        if self._check_missing_key_fields(quote):
                            missing_fields_codes.append(code)

                        # 4. 缓存完整数据
                        self._quote_cache.set(
                            f"quote:{code}",
                            result[code],
                            ttl=TradingTimeChecker.get_cache_ttl()
                        )

            # 5. 字段级fallback：从备用源补充缺失的字段
            if missing_fields_codes:
                self._fill_missing_fields_from_fallback(result, missing_fields_codes)

        except Exception as e:
            logger.warning(f"{source_name} 获取行情失败: {e}")

        return (result, data_source)

    def _check_missing_key_fields(self, quote: dict) -> bool:
        """检查报价数据是否缺少关键字段

        Args:
            quote: 报价数据字典

        Returns:
            如果缺少关键字段返回 True
        """
        # 定义关键字段（TdxQuant有但PyTdx没有的）
        key_fields = ['volume_ratio', 'turnover_rate', 'pe_ratio', 'pb_ratio']

        for field in key_fields:
            value = quote.get(field)
            # 如果字段为0、None或空字符串，认为缺失
            if not value or value == 0 or value == '0':
                return True

        return False

    def _fill_missing_fields_from_fallback(
        self,
        result: dict,
        codes: List[str]
    ) -> None:
        """从备用数据源补充缺失的字段

        Args:
            result: 当前结果字典（会被修改）
            codes: 需要补充字段的股票代码列表
        """
        # 尝试备用数据源（优先级：tdxquant > xtquant > pytdx）
        fallback_sources = ['tdxquant', 'xtquant']

        for fallback_name in fallback_sources:
            if not codes:
                break

            fallback_adapter = self._get_adapter_cached(fallback_name)
            if not fallback_adapter or not fallback_adapter.is_available():
                continue

            logger.info(f"从 {fallback_name} 补充 {len(codes)} 只股票的缺失字段")

            still_missing = []

            for code in codes:
                try:
                    # 获取备用源的完整行情
                    fallback_quotes = fallback_adapter.get_quote([code])
                    if not fallback_quotes or code not in fallback_quotes:
                        still_missing.append(code)
                        continue

                    fallback_quote = fallback_quotes[code]
                    if not fallback_quote:
                        still_missing.append(code)
                        continue

                    # 合并关键字段（只补充缺失的）
                    key_fields = ['volume_ratio', 'turnover_rate', 'pe_ratio',
                                  'pb_ratio', 'amplitude', 'zt_price', 'dt_price']

                    filled_count = 0
                    for field in key_fields:
                        current_value = result[code].get(field)
                        fallback_value = fallback_quote.get(field)

                        # 如果当前值为空或0，且备用源有值，则补充
                        if (not current_value or current_value == 0) and fallback_value:
                            result[code][field] = fallback_value
                            filled_count += 1

                    if filled_count > 0:
                        logger.debug(f"{code} 从 {fallback_name} 补充了 {filled_count} 个字段")

                        # 更新缓存
                        self._quote_cache.set(
                            f"quote:{code}",
                            result[code],
                            ttl=TradingTimeChecker.get_cache_ttl()
                        )
                    else:
                        still_missing.append(code)

                except Exception as e:
                    logger.debug(f"{code} 从 {fallback_name} 补充字段失败: {e}")
                    still_missing.append(code)

            codes = still_missing

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
