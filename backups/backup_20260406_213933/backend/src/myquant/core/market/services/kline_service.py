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

架构职责：
  - WebSocket 推送服务（原有功能）
  - 统一数据入口：get_historical_kline()（新增）
  - 数据路由：hotdb → localdb → 在线源（新增）
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Set

import pandas as pd
from fastapi import WebSocket
from loguru import logger

from myquant.core.market.adapters import get_adapter
from myquant.core.market.routing import DataLevel, get_source_selector
from myquant.core.market.models import KlineDataset
from myquant.core.market.utils.trading_time_detector import is_trading_time
from myquant.core.market.services.hotdb_service import get_hotdb_service


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

    def get_historical_kline(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        _skip_smart_update: bool = False,
    ) -> pd.DataFrame:
        """统一数据入口：获取历史 K 线数据

        按架构设计实现三层路由：
        1. HotDB（快速通道，自选股热数据）- 使用 HotDBService 智能管理
        2. LocalDB（冷数据库，全标历史数据）
        3. 在线源（V5双层路由：tdxquant → pytdx → xtquant）

        Args:
            symbol: 股票代码
            period: 周期 (1m/5m/15m/30m/1h/1d/1w/1M)
            count: 数据条数
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            _skip_smart_update: 内部参数，跳过智能更新（避免循环调用）

        Returns:
            DataFrame with columns: [datetime, open, high, low, close, volume, amount, source]
        """
        # 第1层：HotDB（快速通道）- 使用 HotDBService 智能管理数据新鲜度
        hotdb_service = get_hotdb_service()
        hotdb = get_adapter('hotdb')

        # 非交易时间或内部调用不触发智能更新
        is_trading = is_trading_time()
        skip_update = _skip_smart_update or not is_trading
        if skip_update:
            logger.debug(f"[KlineService] 跳过智能更新（_skip_smart_update={_skip_smart_update}, is_trading={is_trading}）")

        if hotdb and hotdb.is_available():
            try:
                # 先尝试从 HotDB 获取数据
                df_dict = hotdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    count=count
                )

                if symbol in df_dict and not df_dict[symbol].empty:
                    result_len = len(df_dict[symbol])
                    logger.info(f"[KlineService] {symbol} {period} 从 HotDB 获取 {result_len} 条")

                    # 非交易时间：直接返回本地数据，不检查缺口
                    if not is_trading:
                        df_dict[symbol]['source'] = 'hotdb'
                        return df_dict[symbol]

                    # 交易时间：检查数据量和缺口
                    # 检查数据量是否足够（80%阈值，且至少需要10条以上才检查）
                    if count <= 10 or result_len >= count * 0.8:
                        # 日线数据充足时（>=500条），直接返回，不触发智能更新
                        # 原因：500条日线足以覆盖2年交易数据，稍微陈旧也不影响展示
                        if period == '1d' and result_len >= 500:
                            logger.info(f"[KlineService] {symbol} {period} 日线数据充足（{result_len}条），直接返回，跳过缺口检测")
                            df_dict[symbol]['source'] = 'hotdb'
                            return df_dict[symbol]

                        # 数据不够多，检查是否新鲜（是否有缺口）
                        gap_info = hotdb_service._detect_gap(symbol, period)

                        if not gap_info['has_gap']:
                            # 数据新鲜，直接返回
                            df_dict[symbol]['source'] = 'hotdb'
                            return df_dict[symbol]
                        else:
                            # 数据有缺口，触发智能更新
                            logger.info(f"[KlineService] {symbol} {period} 检测到数据缺口: {gap_info['reason']}，触发智能更新")
                            update_result = hotdb_service.smart_update(symbol, period)

                            if update_result['success'] and update_result['records'] > 0:
                                # 更新成功，重新从 HotDB 获取
                                df_dict = hotdb.get_kline(
                                    symbols=[symbol],
                                    period=period,
                                    start_date=start_date,
                                    end_date=end_date,
                                    count=count
                                )
                                if symbol in df_dict and not df_dict[symbol].empty:
                                    df_dict[symbol]['source'] = 'hotdb'
                                    logger.info(f"[KlineService] {symbol} {period} 智能更新后返回 {len(df_dict[symbol])} 条")
                                    return df_dict[symbol]

                    # 数据不足，记录日志后继续尝试下一层
                    logger.debug(f"[KlineService] HotDB 数据不足（{result_len}/{count}），继续尝试 LocalDB")
                else:
                    # HotDB 无数据
                    if not is_trading:
                        # 非交易时间不触发智能更新，直接尝试下一层
                        logger.debug(f"[KlineService] 非交易时间，HotDB 无数据，继续尝试 LocalDB")
                    else:
                        # 交易时间，触发智能更新初始化
                        logger.info(f"[KlineService] {symbol} {period} HotDB 无数据，触发智能更新初始化")
                        update_result = hotdb_service.smart_update(symbol, period)

                        if update_result['success'] and update_result['records'] > 0:
                            # 更新成功，重新从 HotDB 获取
                            df_dict = hotdb.get_kline(
                                symbols=[symbol],
                                period=period,
                                start_date=start_date,
                                end_date=end_date,
                                count=count
                            )
                            if symbol in df_dict and not df_dict[symbol].empty:
                                df_dict[symbol]['source'] = 'hotdb'
                                logger.info(f"[KlineService] {symbol} {period} 初始化后返回 {len(df_dict[symbol])} 条")
                                return df_dict[symbol]

            except Exception as e:
                logger.debug(f"[KlineService] HotDB 获取失败: {e}")

        # 第2层：LocalDB（冷数据库）
        localdb = get_adapter('localdb')
        if localdb and localdb.is_available():
            try:
                df_dict = localdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    count=count
                )
                if symbol in df_dict and not df_dict[symbol].empty:
                    result_len = len(df_dict[symbol])
                    logger.info(f"[KlineService] {symbol} {period} 从 LocalDB 获取 {result_len} 条")
                    # 添加 source 列
                    df_dict[symbol]['source'] = 'localdb'
                    # 检查数据量是否足够（80%阈值，且至少需要10条以上才检查）
                    if count <= 10 or result_len >= count * 0.8:
                        return df_dict[symbol]
                    # 数据不足，继续尝试在线源
                    logger.debug(f"[KlineService] LocalDB 数据不足（{result_len}/{count}），继续尝试在线源")
            except Exception as e:
                logger.debug(f"[KlineService] LocalDB 获取失败: {e}")

        # 第3层：在线源（V5双层路由）
        # 历史数据在非交易时间也可以获取（区别于实时数据）
        # 非交易时间获取历史数据是合理的请求（如用户拖动K线图查看历史）

        dataset = self._dispatch_kline(symbol, period, count)
        if dataset is not None:
            df = dataset.df
            # 添加 source 列标记数据来源
            df['source'] = dataset.adapter
            logger.info(f"[KlineService] {symbol} {period} 从在线源 {dataset.adapter} 获取 {len(df)} 条")

            # 回写 HotDB：将从在线源获取的新数据保存到 HotDB
            hotdb = get_adapter('hotdb')
            if hotdb and hotdb.is_available():
                try:
                    # 去掉 source 列再保存（HotDB 不需要 source 列）
                    df_to_save = df.drop(columns=['source']) if 'source' in df.columns else df
                    hotdb.save_kline(symbol, df_to_save, period)
                    logger.info(f"[KlineService] {symbol} {period} 已回写 HotDB ({len(df)} 条)")
                except Exception as e:
                    logger.warning(f"[KlineService] {symbol} {period} 回写 HotDB 失败: {e}")

            return df

        # 所有数据源都失败
        logger.warning(f"[KlineService] {symbol} {period} 所有数据源均失败")
        return pd.DataFrame()

    def _dispatch_kline(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[KlineDataset]:
        """V5 双层路由决策树：分析数据类型 → 获取数据源链 → 条件过滤 → fallback 遍历

        这是 KlineService 作为"数据调配大脑"的核心方法。
        """
        selector = get_source_selector()

        # Layer 1+2: 获取 fallback chain（已包含 CodeTypeFilter 资产类型识别）
        chain = selector.get_fallback_chain_for_code(DataLevel.L3, symbol)

        # Layer 2.5: 周线/月线特殊处理
        # pytdx 返回 800 根 K线，而 xtquant 仅返回 162 根
        # 因此周线/月线优先使用 pytdx
        is_weekly_or_monthly = period in ['1w', '1M']
        if is_weekly_or_monthly:
            # 将 pytdx 移到链首，如果存在的话
            if 'pytdx' in chain:
                chain = [s for s in chain if s != 'pytdx']
                chain = ['pytdx'] + chain
                logger.debug("[KlineService] {} {} 为周线/月线，优先使用 pytdx（800根）", symbol, period)

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
                    symbols=[symbol],
                    period=period,
                    count=count,
                    start_date=start_date,
                    end_date=end_date
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

    def get_online_kline(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """仅从在线源获取 K 线数据（供 HotDBService.smart_update 使用）

        此方法跳过 HotDB 和 LocalDB，直接从在线源获取数据，避免循环调用。

        Args:
            symbol: 股票代码
            period: 周期 (1m/5m/15m/30m/1h/1d/1w/1M)
            count: 数据条数
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            DataFrame with columns: [datetime, open, high, low, close, volume, amount, source]
        """
        dataset = self._dispatch_kline(symbol, period, count, start_date, end_date)
        if dataset is not None:
            df = dataset.df.copy()
            df['source'] = dataset.adapter
            logger.info(f"[KlineService] {symbol} {period} 从在线源 {dataset.adapter} 获取 {len(df)} 条")
            return df

        logger.warning(f"[KlineService] {symbol} {period} 在线源获取失败")
        return pd.DataFrame()

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

    def download_to_hotdb(
        self,
        symbols: List[str],
        periods: List[str],
        source: str = 'pytdx',
        count: int = 1000,
        start_date: str = None,
        end_date: str = None
    ) -> dict:
        """下载数据到 HotDB

        Args:
            symbols: 股票代码列表
            periods: 周期列表
            source: 数据源
            count: 下载条数
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD

        Returns:
            dict: 下载结果
        """
        try:
            from myquant.core.market.adapters import get_adapter

            # 获取在线适配器
            online_adapter = get_adapter(source)
            if not online_adapter or not online_adapter.is_available():
                return {
                    'success': False,
                    'error': f'数据源 {source} 不可用',
                    'details': {}
                }

            # 获取 HotDB 适配器
            hotdb_adapter = get_adapter('hotdb')

            results = {}
            for symbol in symbols:
                results[symbol] = {}

                for period in periods:
                    try:
                        # 从在线源获取数据（带日期范围）
                        kline_data = online_adapter.get_kline(
                            [symbol],
                            period=period,
                            count=count,
                            start_date=start_date,
                            end_date=end_date
                        )

                        if symbol not in kline_data or kline_data[symbol] is None:
                            results[symbol][period] = {'success': False, 'error': '获取数据失败'}
                            continue

                        df = kline_data[symbol]

                        # 保存到 HotDB
                        save_success = hotdb_adapter.save_kline(symbol, df, period=period)

                        results[symbol][period] = {
                            'success': save_success,
                            'count': len(df) if save_success else 0
                        }

                        logger.info(f"[KlineService] {symbol} {period} 下载完成: {len(df)} 条")

                    except Exception as e:
                        results[symbol][period] = {'success': False, 'error': str(e)}
                        logger.error(f"[KlineService] {symbol} {period} 下载失败: {e}")

            return {'success': True, 'details': results}

        except Exception as e:
            logger.error(f"[KlineService] 批量下载失败: {e}")
            return {'success': False, 'error': str(e)}


# ─────────────────────────────────────────────
# 单例工厂
# ─────────────────────────────────────────────

_kline_service: Optional[KlineService] = None


def get_kline_service() -> KlineService:
    global _kline_service
    if _kline_service is None:
        _kline_service = KlineService()
    return _kline_service
