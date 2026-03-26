"""
实时 K 线推送服务（KlineService）

方案 C 高频路：
  - 初始化：通过 IntradayKlineService 加载今天历史分钟线
  - 实时：每秒轮询 XtQuant 最新 bar，检测变化后通过 WebSocket 推送

消息格式：
  {"type": "history",    "symbol": "000001.SZ", "bars": [...]}
  {"type": "bar_update", "symbol": "000001.SZ", "bar": {...}}
  {"type": "bar_close",  "symbol": "000001.SZ", "bar": {...}}
  {"type": "error",      "message": "..."}
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Set

from fastapi import WebSocket
from loguru import logger

from myquant.core.market.adapters import get_adapter
from myquant.core.market.routing import DataLevel, get_source_selector
from myquant.core.market.models import KlineDataset
from myquant.core.market.utils.trading_time_detector import is_trading_time


# ─────────────────────────────────────────────
# MinuteAggregator
# ─────────────────────────────────────────────

class MinuteAggregator:
    """检测 K 线变化：新增一根（bar_close）或最后一根更新（bar_update）"""

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


# ─────────────────────────────────────────────
# KlineService
# ─────────────────────────────────────────────

class KlineService:
    """
    实时 K 线推送服务（单例）

    职责：
    - 管理 WebSocket 客户端连接 (symbol → Set[WebSocket])
    - 后台轮询任务（每秒），检测 K 线变化并广播
    - 客户端连接时发送今天历史分钟线
    """

    POLL_INTERVAL = 1.0   # 轮询间隔（秒）
    HISTORY_COUNT = 300   # 初始化历史条数（1分钟线约1.5个交易日）

    def __init__(self):
        # symbol → 订阅该 symbol 的 WebSocket 集合
        self._clients: Dict[str, Set[WebSocket]] = {}
        self._aggregator = MinuteAggregator()
        self._poll_task: Optional[asyncio.Task] = None

    # ── 数据调配 ─────────────────────────────────

    def _dispatch_kline(
        self,
        symbol: str,
        period: str,
        count: int,
    ) -> Optional[KlineDataset]:
        """V5 双层路由决策树：分析数据类型 → 获取数据源链 → 条件过滤 → fallback 遍历

        这是 KlineService 作为"数据调配大脑"的核心方法。
        """
        logger.info(f"[KlineService._dispatch_kline] symbol={symbol}, period={period}, count={count}")
        selector = get_source_selector()

        # Layer 1+2: 获取 fallback chain（已包含 CodeTypeFilter 资产类型识别）
        chain = selector.get_fallback_chain_for_code(DataLevel.L3, symbol)

        # Layer 3: 条件过滤
        if not is_trading_time():
            chain = [s for s in chain if s != 'tdxquant']

        # Layer 4: Fallback 遍历
        for source in chain:
            adapter = get_adapter(source)
            if adapter is None or not adapter.is_available():
                continue

            try:
                df_dict = adapter.get_kline(
                    symbols=[symbol], period=period, count=count
                )
                if symbol in df_dict and df_dict[symbol] is not None and not df_dict[symbol].empty:
                    logger.debug(
                        "[KlineService] {} {} 命中 {}",
                        symbol, period, source
                    )
                    return KlineDataset.from_adapter(df_dict[symbol], source)
            except Exception as e:
                logger.warning(
                    "[KlineService] {} {} 从 {} 获取失败: {}",
                    symbol, period, source, e
                )
                continue

        logger.warning("[KlineService] {} {} 所有数据源均失败", symbol, period)
        return None

    def get_aggregated_bars(
        self,
        symbol: str,
        period: str,
        count: int = 800,
    ) -> Optional[tuple[List[dict], str]]:
        """获取预聚合的 K 线数据（同步方法，供 API 调用）

        从 HotDB 获取预聚合数据（15m/30m/1h 由 5m 自动聚合生成）。
        如果 HotDB 没有数据，返回 None 让调用者降级到其他数据源。

        Args:
            symbol: 股票代码
            period: 周期（1d, 5m, 15m, 30m, 1h）
            count: 返回条数

        Returns:
            (dict list, data_source) 元组: ([{'time': ..., 'open': ..., ...}, ...], 'hotdb')
            如果 HotDB 无数据则返回 None
        """
        hotdb = get_adapter('hotdb')
        if hotdb is None or not hotdb.is_available():
            return None

        try:
            df_dict = hotdb.get_kline(
                symbols=[symbol],
                period=period,
                count=count
            )

            if symbol in df_dict and df_dict[symbol] is not None and not df_dict[symbol].empty:
                logger.debug(
                    "[KlineService] get_aggregated_bars: {} {} 从 HotDB 获取 {} 条",
                    symbol, period, len(df_dict[symbol])
                )
                # 使用 KlineDataset.to_dict_list() 确保时区处理正确
                from myquant.core.market.models import KlineDataset
                dataset = KlineDataset(df_dict[symbol], 'hotdb')
                return dataset.to_dict_list(), 'hotdb'

            return None

        except Exception as e:
            logger.warning("[KlineService] get_aggregated_bars 失败: {}", e)
            return None

    def get_kline_bars(
        self,
        symbol: str,
        period: str,
        count: int = 100,
    ) -> Optional[tuple[List[dict], str]]:
        """获取 K 线数据（同步方法，供 API 调用）

        优先从 HotDB 获取数据（预聚合，时区处理正确），
        如果 HotDB 无数据则使用 V5 双层路由决策树自动选择最佳数据源。

        自动保存：当从在线源（pytdx/xtquant）获取日线数据时，自动保存到 LocalDB。

        Args:
            symbol: 股票代码
            period: 周期（1d, 5m, 15m, 30m, 1h, 1m）
            count: 返回条数

        Returns:
            (dict list, data_source) 元组: ([{'time': ..., 'open': ..., ...}, ...], 'hotdb'|'localdb'|'pytdx'|'xtquant'|'tdxquant')
            如果所有数据源均失败则返回 None
        """
        logger.info(f"[get_kline_bars] symbol={symbol}, period={period}, count={count}")

        # 优先从 HotDB 获取（时区处理正确）
        aggregated = self.get_aggregated_bars(symbol, period, count)
        if aggregated:
            bars, source = aggregated
            logger.info(f"[get_kline_bars] 使用 HotDB 聚合数据: {len(bars)} 条")
            return bars, source

        # HotDB 无数据，使用 fallback 路由
        dataset = self._dispatch_kline(symbol, period, count)
        if dataset is None:
            logger.warning("[get_kline_bars] _dispatch_kline returned None")
            return None

        logger.info(
            f"[get_kline_bars] _dispatch_kline 返回: adapter={dataset.adapter}, {len(dataset)} bars"
        )
        if len(dataset) > 0:
            first_dt = dataset.df['datetime'].iloc[0]
            last_dt = dataset.df['datetime'].iloc[-1]
            logger.info(f"[get_kline_bars] 数据范围: {first_dt} ~ {last_dt}")

        # 自动保存到 LocalDB（仅日线数据，仅在线源）
        if period == '1d' and dataset.adapter in ('pytdx', 'pytdx_pool', 'xtquant', 'tdxquant'):
            self._async_save_to_localdb(symbol, dataset)

        return dataset.to_dict_list(), dataset.adapter

    def _async_save_to_localdb(self, symbol: str, dataset: 'KlineDataset'):
        """异步保存数据到 LocalDB（不阻塞返回）

        使用线程池在后台保存，避免影响 API 响应速度。
        """
        import threading
        import traceback

        def save_worker():
            try:
                localdb = get_adapter('localdb')
                if localdb and localdb.is_available():
                    success = localdb.save_kline(symbol, dataset.df, '1d')
                    if success:
                        logger.info(
                            "[KlineService] 自动保存 {} 从 {} 到 LocalDB: {} 条",
                            symbol, dataset.adapter, len(dataset.df)
                        )
                    else:
                        logger.warning("[KlineService] 保存 {} 到 LocalDB 失败", symbol)
            except Exception as e:
                logger.warning("[KlineService] 保存 {} 到 LocalDB 异常: {}", symbol, e)

        # 启动后台线程
        thread = threading.Thread(target=save_worker, daemon=True)
        thread.start()

    # ── 连接管理 ──────────────────────────────

    async def connect(self, ws: WebSocket, symbol: str):
        """客户端连接：注册 + 发送历史"""
        if symbol not in self._clients:
            self._clients[symbol] = set()
        self._clients[symbol].add(ws)
        logger.info("KlineService: {} 连接，当前订阅数 {}", symbol, len(self._clients[symbol]))

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
                logger.info("KlineService: {} 无订阅者，移除", symbol)

        # 无任何订阅时停止轮询
        if not self._clients and self._poll_task:
            self._poll_task.cancel()
            self._poll_task = None

    # ── 历史数据初始化 ────────────────────────

    async def _send_history(self, ws: WebSocket, symbol: str):
        """向单个客户端发送今天历史分钟线

        使用 V5 双层路由决策树自动选择最佳数据源。
        """
        try:
            dataset = self._dispatch_kline(symbol, '1m', self.HISTORY_COUNT)
            bars = []
            if dataset is not None:
                bars = dataset.to_dict_list()

            await ws.send_text(json.dumps({
                "type": "history",
                "symbol": symbol,
                "bars": bars,
            }, default=str))

            logger.debug("KlineService: {} 历史推送 {} 根", symbol, len(bars))

        except Exception as e:
            logger.warning("KlineService: {} 历史加载失败: {}", symbol, e)
            await self._send_error(ws, f"历史数据加载失败: {e}")

    # ── 轮询任务 ──────────────────────────────

    def _ensure_poll_task(self):
        """确保后台轮询任务在运行"""
        if self._poll_task is None or self._poll_task.done():
            self._poll_task = asyncio.create_task(self._poll_loop())

    async def _poll_loop(self):
        """后台轮询：交易时间运行，收盘后停止"""
        logger.info("KlineService: 轮询任务启动")
        check_interval = 60  # 非交易时间检查间隔（秒）
        last_status = None  # 上次状态，用于避免重复日志

        try:
            while self._clients:
                # 检查是否在交易时间
                trading = is_trading_time()

                # 状态变化时记录日志
                if trading != last_status:
                    if trading:
                        logger.info("[KlineService] 进入交易时间，开始数据轮询")
                    else:
                        logger.info("[KlineService] 离开交易时间，停止数据轮询，仅保持连接")
                    last_status = trading

                if not trading:
                    # 收盘后：完全停止数据轮询，只保持连接
                    # 等待一段时间后重新检查是否开盘
                    await asyncio.sleep(check_interval)
                    continue  # 跳过数据获取，继续循环

                # 交易时间：正常轮询
                await self._poll_once()
                await asyncio.sleep(self.POLL_INTERVAL)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("KlineService: 轮询异常: {}", e)
        finally:
            logger.info("KlineService: 轮询任务停止")

    async def _poll_once(self):
        """单次轮询所有订阅 symbol

        使用 V5 双层路由决策树自动选择最佳数据源。
        """
        symbols = list(self._clients.keys())
        if not symbols:
            return

        for symbol in symbols:
            try:
                dataset = self._dispatch_kline(symbol, '1m', 10)
                if dataset is None:
                    continue

                bars = dataset.to_dict_list()
                if not bars:
                    continue

                event = self._aggregator.update(symbol, bars)
                if event:
                    await self._broadcast(symbol, event["event"], event["bar"])

            except Exception as e:
                logger.warning("[KlineService] {} 轮询失败: {}", symbol, e)

    # ── 广播 ─────────────────────────────────

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
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)

        # 清理断开的连接
        for ws in dead:
            self._clients[symbol].discard(ws)

    async def _send_error(self, ws: WebSocket, message: str):
        try:
            await ws.send_text(json.dumps({"type": "error", "message": message}))
        except Exception:
            pass


# ─────────────────────────────────────────────
# 单例工厂
# ─────────────────────────────────────────────

_kline_service: Optional[KlineService] = None


def get_kline_service() -> KlineService:
    global _kline_service
    if _kline_service is None:
        _kline_service = KlineService()
    return _kline_service
