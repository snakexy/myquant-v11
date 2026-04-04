"""
实时行情服务（QuoteService）

提供：
1. 实时快照获取
2. WebSocket K线实时推送
3. 市场状态判断
4. 盘中K线获取

API 层通过本服务获取实时数据，不直接调用适配器。
"""

import asyncio
import json
from typing import Dict, List, Optional, Set
from datetime import datetime
from loguru import logger

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from ..utils import TradingTimeChecker, TimePhase
from .cache import TTLCache
from .cache_manager_service import get_cache_manager
from .kline_service import get_kline_service
from ..utils.trading_time_detector import is_trading_time


# ─────────────────────────────────────────────
# MinuteAggregator - K线变化检测
# ─────────────────────────────────────────────

class MinuteAggregator:
    """检测 K线变化：新增一根（bar_close）或最后一根更新（bar_update）"""

    def __init__(self):
        # symbol → 上一次已知的最后一根 bar dict
        self._last_bar: Dict[str, Optional[dict]] = {}
        # symbol → 上一次已知的 bar 数量
        self._last_count: Dict[str, int] = {}

    def update(self, symbol: str, bars: List[dict]) -> Optional[dict]:
        """
        传入最新 bars 列表，返回事件 dict 或 None（无变化）。

        返回格式:
            {"event": "bar_close",  "bar": {...}}
            {"event": "bar_update", "bar": {...}}
            None  → 无变化
        """
        if not bars:
            return None

        current_count = len(bars)
        current_last = bars[-1]

        prev_count = self._last_count.get(symbol, 0)
        prev_last = self._last_bar.get(symbol)

        # 更新状态
        self._last_count[symbol] = current_count
        self._last_bar[symbol] = current_last

        if prev_count == 0:
            # 首次拿到数据，不触发事件（history 已单独发送）
            return None

        if current_count > prev_count:
            # 根数增加：上一根已收线，有新的开盘 bar
            closed_bar = bars[-2] if len(bars) >= 2 else current_last
            return {"event": "bar_close", "bar": closed_bar}

        if prev_last and current_last.get("time") == prev_last.get("time"):
            # 同一根 bar 有变化
            if current_last != prev_last:
                return {"event": "bar_update", "bar": current_last}

        return None

    def reset(self, symbol: str):
        self._last_bar.pop(symbol, None)
        self._last_count.pop(symbol, None)


class RealtimeMarketService:
    """实时行情服务（QuoteService）

    负责：
    1. 实时快照获取
    2. WebSocket K线实时推送
    3. 市场状态判断

    注意：数据源选择委托给 KlineService，本服务专注于实时推送
    """

    POLL_INTERVAL = 1.0   # 轮询间隔（秒）
    HISTORY_COUNT = 100   # 初始化历史条数（减少内存占用）

    def __init__(self):
        # 快照缓存
        self._quote_cache = TTLCache(maxsize=500, ttl=10)
        # 适配器缓存（用于快照获取）
        self._adapter_cache = TTLCache(maxsize=20, ttl=3600)
        # 统一缓存管理器
        self._cache_manager = get_cache_manager()

        # WebSocket 连接管理: symbol → Set[WebSocket]
        self._clients: Dict[str, Set[WebSocket]] = {}
        self._aggregator = MinuteAggregator()
        self._poll_task: Optional[asyncio.Task] = None

    def _get_adapter_cached(self, name: str, force_retry: bool = False):
        """获取适配器单例（避免重复初始化 SDK）

        Args:
            name: 适配器名称
            force_retry: 是否强制重试初始化（用于 TdxQuant 等可能初始化失败的适配器）
        """
        # 延迟导入避免循环依赖
        from ..adapters import get_adapter

        # 如果强制重试，清除缓存并创建新实例
        if force_retry and name == 'tdxquant':
            self._adapter_cache.delete(name)

        # 先检查缓存
        cached = self._adapter_cache.get(name)
        if cached is not None:
            return cached

        # 缓存未命中，创建新适配器
        adapter = get_adapter(name)
        if adapter is not None:
            # 如果是 TdxQuant 且强制重试，调用强制初始化
            if force_retry and name == 'tdxquant' and hasattr(
                adapter, '_ensure_initialized'
            ):
                adapter._ensure_initialized(force_retry=True)
            # 缓存适配器实例（TTL 1小时，自动过期）
            self._adapter_cache.set(name, adapter, ttl=3600)
        return adapter

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
                adapter = self._get_adapter_cached(name, force_retry=(name == 'tdxquant'))
                if adapter and adapter.is_available():
                    return (name, adapter)
        else:
            # 非交易时间：优先尝试 TdxQuant/XtQuant 获取完整字段
            for name in ['tdxquant', 'xtquant', 'pytdx']:
                # 对 TdxQuant 强制重试，避免之前的失败标志影响
                adapter = self._get_adapter_cached(name, force_retry=(name == 'tdxquant'))
                if adapter and adapter.is_available():
                    logger.info(f"非交易时间使用 {name} 获取完整行情数据")
                    return (name, adapter)

        return None

    # ========== K线数据（委托给 KlineService） ==========

    def get_kline(
        self,
        symbol: str,
        period: str = '1d',
        count: int = 100
    ) -> tuple:
        """获取K线数据（委托给 KlineService）

        KlineService 负责数据源路由选择，QuoteService 只做转发。

        Args:
            symbol: 股票代码
            period: 周期 (1m/5m/15m/30m/1h/1d/1w)
            count: K线根数

        Returns:
            (dataframe, data_source_name) 元组
        """
        kline_svc = get_kline_service()
        result_dict, source = kline_svc.get_historical_kline(
            symbols=[symbol],
            period=period,
            count=count
        )
        # 返回单个股票的 DataFrame
        df = result_dict.get(symbol)
        return (df, source)

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

    # ── WebSocket K线实时推送 ─────────────────────

    async def connect(self, ws: WebSocket, symbol: str):
        """客户端连接：注册 + 发送历史"""
        if symbol not in self._clients:
            self._clients[symbol] = set()
        self._clients[symbol].add(ws)
        logger.info(f"[QuoteService] {symbol} 连接，当前订阅数 {len(self._clients[symbol])}")

        # 发送历史分钟线
        await self._send_history(ws, symbol)

        # 确保轮询任务在运行
        self._ensure_poll_task()

    async def disconnect(self, ws: WebSocket, symbol: str):
        """客户端断开：注销"""
        if symbol in self._clients:
            self._clients[symbol].discard(ws)
            if not self._clients[symbol]:
                del self._clients[symbol]
                self._aggregator.reset(symbol)
                logger.info(f"[QuoteService] {symbol} 无订阅者，移除")

        # 无任何订阅时停止轮询
        if not self._clients and self._poll_task:
            self._poll_task.cancel()
            self._poll_task = None

    async def _send_history(self, ws: WebSocket, symbol: str):
        """向单个客户端发送今天历史分钟线（委托给 KlineService）"""
        try:
            kline_svc = get_kline_service()
            result_dict, source = kline_svc.get_historical_kline(
                symbols=[symbol],
                period='1m',
                count=self.HISTORY_COUNT
            )

            bars = []
            df = result_dict.get(symbol)
            if df is not None and not df.empty:
                # 转换为字典列表
                from myquant.core.market.models import KlineDataset
                dataset = KlineDataset.from_adapter(df, source)
                bars = dataset.to_dict_list()

            # 立即释放DataFrame
            del df, result_dict

            await ws.send_text(json.dumps({
                "type": "history",
                "symbol": symbol,
                "bars": bars,
            }, default=str))

            logger.debug(f"[QuoteService] {symbol} 历史推送 {len(bars)} 根 (来源: {source})")

        except Exception as e:
            logger.warning(f"[QuoteService] {symbol} 历史加载失败: {e}")
            await self._send_error(ws, f"历史数据加载失败: {e}")

    def _ensure_poll_task(self):
        """确保后台轮询任务在运行"""
        if self._poll_task is None or self._poll_task.done():
            self._poll_task = asyncio.create_task(self._poll_loop())

    async def _poll_loop(self):
        """后台轮询：交易时间运行，收盘后停止"""
        logger.info("[QuoteService] 轮询任务启动")
        check_interval = 60  # 非交易时间检查间隔（秒）
        last_status = None  # 上次状态，用于避免重复日志

        try:
            while self._clients:
                # 检查是否在交易时间
                trading = is_trading_time()

                # 状态变化时记录日志
                if trading != last_status:
                    if trading:
                        logger.info("[QuoteService] 进入交易时间，开始数据轮询")
                    else:
                        logger.info("[QuoteService] 离开交易时间，停止数据轮询，仅保持连接")
                    last_status = trading

                if not trading:
                    # 收盘后：完全停止数据轮询，只保持连接
                    await asyncio.sleep(check_interval)
                    continue  # 跳过数据获取，继续循环

                # 交易时间：正常轮询
                await self._poll_once()
                await asyncio.sleep(self.POLL_INTERVAL)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[QuoteService] 轮询异常: {e}")
        finally:
            logger.info("[QuoteService] 轮询任务停止")

    async def _poll_once(self):
        """单次轮询所有订阅 symbol"""
        # 清理死连接（防止内存泄漏）
        self._cleanup_dead_connections()

        symbols = list(self._clients.keys())
        if not symbols:
            return

        try:
            from ..adapters import get_adapter
            xt = get_adapter('xtquant')
            if xt is None or not xt.is_available():
                return

            df_dict = xt.get_kline(symbols=symbols, period='1m', count=10)

            for symbol, df in df_dict.items():
                if df is None or df.empty:
                    continue

                # 转为 dict 列表
                from myquant.core.market.models import KlineDataset
                dataset = KlineDataset.from_adapter(df, 'xtquant')
                bars = dataset.to_dict_list()

                event = self._aggregator.update(symbol, bars)
                if event:
                    await self._broadcast(symbol, event["event"], event["bar"])

        except Exception as e:
            logger.warning(f"[QuoteService] 轮询拉取失败: {e}")

    async def _broadcast(self, symbol: str, event_type: str, bar: dict):
        """向所有订阅该 symbol 的客户端广播"""
        if symbol not in self._clients:
            return

        message = json.dumps({
            "type": event_type,
            "symbol": symbol,
            "bar": bar,
        }, default=str)

        dead: Set[WebSocket] = set()
        for ws in list(self._clients[symbol]):
            # 先检查连接状态
            if ws.client_state != WebSocketState.OPEN:
                dead.add(ws)
                continue

            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)

        # 清理死连接
        for ws in dead:
            self._clients[symbol].discard(ws)

        # 如果没有订阅者了，清理该股票
        if not self._clients[symbol]:
            del self._clients[symbol]
            self._aggregator.reset(symbol)
            logger.info(f"[QuoteService] {symbol} 所有连接断开，已清理")

    async def _send_error(self, ws: WebSocket, message: str):
        try:
            await ws.send_text(json.dumps({"type": "error", "message": message}))
        except Exception:
            pass

    def _cleanup_dead_connections(self, symbol: Optional[str] = None):
        """清理死连接（防止内存泄漏）

        Args:
            symbol: 指定股票，None 表示清理所有
        """
        to_remove = []

        if symbol:
            clients = self._clients.get(symbol, set())
            for ws in clients:
                if ws.client_state != WebSocketState.OPEN:
                    to_remove.append((symbol, ws))
        else:
            for sym, clients in self._clients.items():
                for ws in clients:
                    if ws.client_state != WebSocketState.OPEN:
                        to_remove.append((sym, ws))

        for sym, ws in to_remove:
            self._clients[sym].discard(ws)
            if not self._clients[sym]:
                del self._clients[sym]
                self._aggregator.reset(sym)
            logger.debug(f"[QuoteService] 清理死连接 {sym}")

        if to_remove:
            logger.info(f"[QuoteService] 清理了 {len(to_remove)} 个死连接")


# 单例实例
_service: Optional[RealtimeMarketService] = None


def get_realtime_market_service() -> RealtimeMarketService:
    """获取 RealtimeMarketService 单例实例"""
    global _service
    if _service is None:
        _service = RealtimeMarketService()
    return _service
