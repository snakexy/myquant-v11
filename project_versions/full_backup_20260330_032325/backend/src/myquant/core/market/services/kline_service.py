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

import pandas as pd

from fastapi import WebSocket
from loguru import logger

from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.intraday_service import get_intraday_kline_service
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
    核心 K 线服务 - V5场景化服务

    定位：
    - 统一的数据获取入口
    - HotDB/LocalDB/在线源路由管理
    - WebSocket 实时推送管理
    - 智能增量更新

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

        路由：交易时间 → xtquant(0.90ms)，非交易时间 → pytdx(10-19ms)
        显式指定 adapter，避免 IntradayKlineService 路由选 tdxquant 后无 fallback
        """
        try:
            adapter = 'xtquant' if is_trading_time() else 'pytdx'
            logger.debug("KlineService: {} 历史加载使用 {}", symbol, adapter)

            intraday_svc = get_intraday_kline_service()
            results = intraday_svc.get_kline(
                symbols=[symbol],
                period='1m',
                count=self.HISTORY_COUNT,
                use_cache=False,
                adapter=adapter,
            )
            bars = []
            if symbol in results:
                bars = results[symbol].data.to_dict_list()

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
        """单次轮询所有订阅 symbol"""
        symbols = list(self._clients.keys())
        if not symbols:
            return

        try:
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
            logger.warning("KlineService: 轮询拉取失败: {}", e)

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

    # ── 下载历史数据 ────────────────────────────

    def get_historical_kline(
        self,
        symbol: str,
        period: str,
        count: int = 500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """获取历史K线数据（统一入口）

        数据源优先级：
        1. HotDB 快速通道（自选股全周期，<10ms）
        2. LocalDB 冷数据库（全标历史，~10ms）
        3. 在线源（V5双层路由：XtQuant/PyTdx/TdxQuant）

        Args:
            symbol: 股票代码
            period: 周期 (1m/5m/15m/30m/1h/1d/1w/1M)
            count: 返回条数
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            K线数据 DataFrame
        """
        # 1. HotDB 快速通道（智能增量更新）
        hotdb_df = self._try_hotdb(symbol, period, count, start_date, end_date)
        if hotdb_df is not None and not hotdb_df.empty:
            logger.info(f"[KlineService] {symbol} {period} 从 HotDB 获取 {len(hotdb_df)} 条")
            return hotdb_df

        # 2. LocalDB 冷数据库
        localdb_df = self._try_localdb(symbol, period, count, start_date, end_date)
        if localdb_df is not None and not localdb_df.empty:
            logger.info(f"[KlineService] {symbol} {period} 从 LocalDB 获取 {len(localdb_df)} 条")
            return localdb_df

        # 3. 在线源（V5双层路由）
        online_df = self._fetch_from_online(symbol, period, count, start_date, end_date)
        logger.info(f"[KlineService] {symbol} {period} 从在线源获取 {len(online_df)} 条")
        return online_df

    def _try_hotdb(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> Optional[pd.DataFrame]:
        """HotDB 快速通道

        - 检查 HotDB 是否有数据
        - 检测数据缺口
        - 智能增量补全
        """
        try:
            from myquant.core.market.services.hotdb_service import get_hotdb_service

            hotdb_service = get_hotdb_service()
            result = hotdb_service.smart_update(symbol, period)

            # 即使 has_data=False，如果有 df 说明是在线获取到了数据
            if result.get('success'):
                df = result.get('df')
                if df is not None and not df.empty:
                    # 应用日期范围过滤
                    if start_date or end_date:
                        from myquant.core.market.models import KlineDataset
                        dataset = KlineDataset.from_adapter(df, 'hotdb')
                        dataset = dataset.slice_by_date(start_date, end_date)
                        if count:
                            dataset = dataset.filter_by_count(count, from_end=True)
                        return dataset.df
                    elif count:
                        return df.tail(count)
                    return df

            return None
        except Exception as e:
            logger.debug(f"[KlineService] HotDB 快速通道失败: {e}")
            return None

    def _try_localdb(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> Optional[pd.DataFrame]:
        """LocalDB 冷数据库"""
        try:
            localdb = get_adapter('localdb')
            if localdb and localdb.is_available():
                df_dict = localdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    count=count,
                    start_date=start_date,
                    end_date=end_date
                )
                if symbol in df_dict and not df_dict[symbol].empty:
                    return df_dict[symbol]
            return None
        except Exception as e:
            logger.debug(f"[KlineService] LocalDB 获取失败: {e}")
            return None

    def _fetch_from_online(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """从在线源获取（V5双层路由）"""
        from myquant.core.market.routing import DataLevel, get_source_selector

        selector = get_source_selector()
        chain = selector.get_fallback_chain_for_code(DataLevel.L3, symbol)

        for source_name in chain:
            adapter = get_adapter(source_name)
            if adapter and adapter.is_available():
                try:
                    df_dict = adapter.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=count,
                        start_date=start_date,
                        end_date=end_date
                    )
                    if symbol in df_dict and not df_dict[symbol].empty:
                        df = df_dict[symbol]
                        logger.info(f"[KlineService] {symbol} {period} 从 {source_name} 获取 {len(df)} 条")

                        # 保存到HotDB（异步模式，不阻塞返回）
                        self._save_to_hotdb_async(symbol, df, period)

                        return df
                except Exception as e:
                    logger.debug(f"[KlineService] {source_name} 获取失败: {e}")
                    continue

        return pd.DataFrame()

    def _save_to_hotdb_async(self, symbol: str, df: pd.DataFrame, period: str):
        """异步保存到HotDB（不阻塞主流程）

        当从在线源获取数据后，异步保存到HotDB以加速下次访问

        Args:
            symbol: 股票代码
            df: K线数据
            period: 周期
        """
        try:
            import threading

            def async_save():
                try:
                    from myquant.core.market.services.hotdb_service import get_hotdb_service
                    hotdb_service = get_hotdb_service()
                    hotdb = hotdb_service._get_hotdb_adapter()
                    if hotdb and hotdb.is_available():
                        hotdb.save_kline(symbol, df, period)
                        logger.debug(f"[KlineService] {symbol} {period} 异步保存到 HotDB: {len(df)} 条")
                except Exception as e:
                    logger.debug(f"[KlineService] 保存到 HotDB 失败: {e}")

            thread = threading.Thread(target=async_save, daemon=True)
            thread.start()
        except Exception as e:
            logger.debug(f"[KlineService] 启动异步保存失败: {e}")

    def download_to_localdb(
        self,
        symbols: List[str],
        periods: List[str],
        source: str = 'xtquant'
    ) -> dict:
        """从在线源下载历史数据到 LocalDB（长期存储）

        Args:
            symbols: 股票代码列表
            periods: 周期列表 (如 ['1d', '5m'])
            source: 数据源 (xtquant/pytdx)

        Returns:
            下载结果: {success: int, failed: int, details: {...}}
        """
        from loguru import logger

        results = {
            'success': 0,
            'failed': 0,
            'details': {}
        }

        # 获取适配器
        adapter = get_adapter(source)
        if not adapter or not adapter.is_available():
            logger.error(f"[KlineService] 数据源 {source} 不可用")
            return {'success': 0, 'failed': len(symbols) * len(periods), 'error': f'{source} 不可用'}

        # 获取 LocalDB 适配器
        localdb = get_adapter('localdb')

        for symbol in symbols:
            results['details'][symbol] = {}

            for period in periods:
                try:
                    logger.info(f"[KlineService] 下载 {symbol} {period} from {source}")

                    # 从在线源获取数据
                    df_dict = adapter.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=10000
                    )

                    if symbol not in df_dict or df_dict[symbol].empty:
                        results['details'][symbol][period] = {'success': False, 'error': '无数据'}
                        results['failed'] += 1
                        continue

                    df = df_dict[symbol]
                    logger.info(f"[KlineService] {symbol} {period}: 获取 {len(df)} 条")

                    # 保存到 LocalDB
                    if localdb and localdb.is_available():
                        success = localdb.save_kline(symbol, df, period)
                        if success:
                            results['details'][symbol][period] = {'success': True, 'count': len(df)}
                            results['success'] += 1
                        else:
                            results['details'][symbol][period] = {'success': False, 'error': '保存失败'}
                            results['failed'] += 1
                    else:
                        results['details'][symbol][period] = {'success': False, 'error': 'LocalDB 不可用'}
                        results['failed'] += 1

                except Exception as e:
                    logger.error(f"[KlineService] {symbol} {period} 下载失败: {e}")
                    results['details'][symbol][period] = {'success': False, 'error': str(e)}
                    results['failed'] += 1

        logger.info(f"[KlineService] 下载完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results

    def download_to_hotdb(
        self,
        symbols: List[str],
        periods: List[str],
        source: str = 'xtquant'
    ) -> dict:
        """从在线源下载临时数据到 HotDB（临时救急）

        Args:
            symbols: 股票代码列表
            periods: 周期列表 (如 ['1d', '5m'])
            source: 数据源 (xtquant/pytdx)

        Returns:
            下载结果: {success: int, failed: int, details: {...}}
        """
        from loguru import logger

        results = {
            'success': 0,
            'failed': 0,
            'details': {}
        }

        # 获取适配器
        adapter = get_adapter(source)
        if not adapter or not adapter.is_available():
            logger.error(f"[KlineService] 数据源 {source} 不可用")
            return {'success': 0, 'failed': len(symbols) * len(periods), 'error': f'{source} 不可用'}

        # 获取 HotDB 适配器
        hotdb = get_adapter('hotdb')

        for symbol in symbols:
            results['details'][symbol] = {}

            for period in periods:
                try:
                    logger.info(f"[KlineService] 下载临时数据 {symbol} {period} from {source}")

                    # 从在线源获取数据
                    df_dict = adapter.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=10000
                    )

                    if symbol not in df_dict or df_dict[symbol].empty:
                        results['details'][symbol][period] = {'success': False, 'error': '无数据'}
                        results['failed'] += 1
                        continue

                    df = df_dict[symbol]
                    logger.info(f"[KlineService] {symbol} {period}: 获取 {len(df)} 条到 HotDB")

                    # 保存到 HotDB
                    if hotdb and hotdb.is_available():
                        success = hotdb.save_kline(symbol, df, period)
                        if success:
                            results['details'][symbol][period] = {'success': True, 'count': len(df)}
                            results['success'] += 1
                        else:
                            results['details'][symbol][period] = {'success': False, 'error': '保存失败'}
                            results['failed'] += 1
                    else:
                        results['details'][symbol][period] = {'success': False, 'error': 'HotDB 不可用'}
                        results['failed'] += 1

                except Exception as e:
                    logger.error(f"[KlineService] {symbol} {period} 下载失败: {e}")
                    results['details'][symbol][period] = {'success': False, 'error': str(e)}
                    results['failed'] += 1

        logger.info(f"[KlineService] 临时数据下载完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results


# ─────────────────────────────────────────────
# 单例工厂
# ─────────────────────────────────────────────

_kline_service: Optional[KlineService] = None


def get_kline_service() -> KlineService:
    global _kline_service
    if _kline_service is None:
        _kline_service = KlineService()
    return _kline_service
