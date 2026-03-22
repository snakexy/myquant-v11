# -*- coding: utf-8 -*-
"""
V5 PyTdx 连接池适配器（自实现版本）

基于 pytdx2.hq.TdxHq_API 实现 M+H+P 三层架构：
- M (Main): 主连接，处理所有数据请求
- H (Hot Standby): 热备选，心跳保活，故障时秒级切换
- P (Pool): 连接池，定期速度测试，动态选择最优

实现要点：
1. 多连接管理（主+备选）
2. 心跳线程保活
3. 故障自动切换
4. 定期速度测试
"""

import threading
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from loguru import logger

try:
    from pytdx2.hq import TdxHq_API
    PYTDX_AVAILABLE = True
except ImportError:
    PYTDX_AVAILABLE = False
    logger.error("pytdx2 未安装")

from .base import V5DataAdapter


@dataclass
class ConnectionInfo:
    """连接信息"""
    api: TdxHq_API
    host: str
    port: int
    last_used: float
    is_connected: bool
    avg_latency: float = 999.0  # 平均延迟


class V5PyTdxPoolAdapter(V5DataAdapter):
    """V5 PyTdx 连接池适配器

    实现 M+H+P 三层架构：
    - 主连接：处理所有请求
    - 热备选：心跳保活，故障时接管
    - 连接池：定期速度测试，动态更新
    """

    PERIOD_CATEGORY = {
        '5min': 0, '15min': 1, '30min': 2, '60min': 3, '1h': 3,
        'day': 9, '1d': 9, 'week': 5, '1w': 5, 'month': 6, '1M': 6,
        '1min': 8, '1m': 8,
    }

    # 默认服务器列表
    DEFAULT_SERVERS = [
        ("180.153.18.172", 80),
        ("202.108.253.139", 80),
        ("60.12.136.250", 7709),
        ("114.80.63.12", 7709),
        ("114.80.63.35", 7709),
        ("218.6.170.47", 7709),
        ("123.125.108.14", 7709),
    ]

    def __init__(
        self,
        pool_size: int = 3,
        heartbeat_interval: int = 30,
        speed_test_interval: int = 60
    ):
        super().__init__()
        self._name = 'pytdx_pool'
        self._pool_size = pool_size
        self._heartbeat_interval = heartbeat_interval
        self._speed_test_interval = 600  # 10分钟

        # M+H+P 架构
        self._main_conn: Optional[ConnectionInfo] = None
        self._hot_standby: Optional[ConnectionInfo] = None
        self._pool: List[ConnectionInfo] = []

        # 管理线程
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._speed_test_thread: Optional[threading.Thread] = None
        self._shutdown = False
        self._lock = threading.RLock()

        # 回退适配器
        self._fallback = None

    def _create_connection(self, host: str, port: int) -> Optional[ConnectionInfo]:
        """创建单个连接"""
        try:
            api = TdxHq_API(heartbeat=True, auto_retry=True)
            if api.connect(host, port):
                try:
                    api.setup()
                except Exception:
                    pass
                return ConnectionInfo(
                    api=api,
                    host=host,
                    port=port,
                    last_used=time.time(),
                    is_connected=True
                )
        except Exception as e:
            logger.debug(f"连接 {host}:{port} 失败: {e}")
        return None

    def _test_connection_speed(self, conn: ConnectionInfo) -> float:
        """测试连接延迟"""
        try:
            start = time.time()
            # 获取平安银行的快照作为测试
            conn.api.get_security_quotes([(0, "000001")])
            latency = (time.time() - start) * 1000
            return latency
        except Exception as e:
            logger.debug(f"速度测试失败 {conn.host}:{conn.port}: {e}")
            return 999.0

    def _initialize_pool(self) -> bool:
        """初始化连接池"""
        if not PYTDX_AVAILABLE:
            return False

        with self._lock:
            # 创建多个连接
            connections = []
            for host, port in self.DEFAULT_SERVERS[:self._pool_size + 1]:
                conn = self._create_connection(host, port)
                if conn:
                    # 测试速度
                    conn.avg_latency = self._test_connection_speed(conn)
                    connections.append(conn)
                    logger.info(f"连接池添加: {host}:{port} 延迟={conn.avg_latency:.1f}ms")

            if len(connections) < 2:
                logger.error("连接池初始化失败: 可用连接少于2个")
                # 关闭已创建的连接
                for conn in connections:
                    try:
                        conn.api.disconnect()
                    except Exception:
                        pass
                return False

            # 按延迟排序
            connections.sort(key=lambda c: c.avg_latency)

            # 分配 M+H+P
            self._main_conn = connections[0]
            self._hot_standby = connections[1] if len(connections) > 1 else None
            self._pool = connections[2:] if len(connections) > 2 else []

            logger.info(
                f"连接池初始化成功: "
                f"主={self._main_conn.host}, "
                f"热备={self._hot_standby.host if self._hot_standby else '无'}, "
                f"池大小={len(self._pool)}"
            )

            # 启动管理线程
            self._start_management_threads()
            return True

    def _start_management_threads(self):
        """启动心跳和速度测试线程"""
        # 心跳线程
        if self._heartbeat_thread is None or not self._heartbeat_thread.is_alive():
            self._heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop,
                daemon=True
            )
            self._heartbeat_thread.start()
            logger.debug("心跳线程启动")

        # 速度测试线程
        if self._speed_test_thread is None or not self._speed_test_thread.is_alive():
            self._speed_test_thread = threading.Thread(
                target=self._speed_test_loop,
                daemon=True
            )
            self._speed_test_thread.start()
            logger.debug("速度测试线程启动")

    def _heartbeat_loop(self):
        """心跳保活循环"""
        while not self._shutdown:
            time.sleep(self._heartbeat_interval)

            with self._lock:
                all_conns = []
                if self._main_conn:
                    all_conns.append(self._main_conn)
                if self._hot_standby:
                    all_conns.append(self._hot_standby)
                all_conns.extend(self._pool)

                for conn in all_conns:
                    try:
                        # 简单心跳：获取平安银行的快照
                        conn.api.get_security_quotes([(0, "000001")])
                        conn.is_connected = True
                    except Exception as e:
                        logger.warning(f"心跳失败 {conn.host}:{conn.port}: {e}")
                        conn.is_connected = False

    def _speed_test_loop(self):
        """速度测试循环"""
        while not self._shutdown:
            time.sleep(self._speed_test_interval)

            with self._lock:
                all_conns = []
                if self._main_conn:
                    all_conns.append(self._main_conn)
                if self._hot_standby:
                    all_conns.append(self._hot_standby)
                all_conns.extend(self._pool)

                # 测试所有连接
                for conn in all_conns:
                    conn.avg_latency = self._test_connection_speed(conn)

                # 按速度重新排序
                all_conns.sort(key=lambda c: c.avg_latency)

                # 重新分配 M+H+P
                if all_conns:
                    # 如果主连接不是最快的，切换
                    if all_conns[0] != self._main_conn and all_conns[0].is_connected:
                        old_main = self._main_conn
                        self._main_conn = all_conns[0]
                        # 旧主连接降级为热备或池
                        if old_main.is_connected:
                            if self._hot_standby is None:
                                self._hot_standby = old_main
                            else:
                                self._pool.append(old_main)
                        logger.info(f"主连接切换为: {self._main_conn.host} 延迟={self._main_conn.avg_latency:.1f}ms")

                    # 确保有热备
                    if len(all_conns) > 1 and self._hot_standby != all_conns[1]:
                        self._hot_standby = all_conns[1] if all_conns[1].is_connected else None

                    # 更新池
                    self._pool = [c for c in all_conns[2:] if c.is_connected and c != self._main_conn and c != self._hot_standby]

    def _get_connection(self) -> Optional[ConnectionInfo]:
        """获取可用连接（自动故障转移）"""
        with self._lock:
            # 优先使用主连接
            if self._main_conn and self._main_conn.is_connected:
                self._main_conn.last_used = time.time()
                return self._main_conn

            # 主连接不可用，切换到热备
            if self._hot_standby and self._hot_standby.is_connected:
                logger.warning(f"主连接不可用，切换到热备: {self._hot_standby.host}")
                self._main_conn, self._hot_standby = self._hot_standby, self._main_conn
                if self._main_conn:
                    self._main_conn.last_used = time.time()
                return self._main_conn

            # 尝试池中的连接
            for conn in self._pool:
                if conn.is_connected:
                    logger.warning(f"主/热备都不可用，使用池连接: {conn.host}")
                    return conn

            # 所有连接都不可用，尝试重建
            logger.error("所有连接都不可用，尝试重建...")
            return None

    def _ensure_pool(self) -> bool:
        """确保连接池可用"""
        if self._main_conn is not None:
            return True
        return self._initialize_pool()

    # ============ 数据获取接口 ============

    def _get_market(self, symbol: str) -> int:
        """获取市场代码"""
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        if code.startswith('88'):
            return 31
        return 1 if code[0] in ('6', '5', '9') else 0

    def _to_category(self, period: str) -> int:
        """转换周期"""
        return self.PERIOD_CATEGORY.get(period, 9)

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'
    ) -> Dict[str, pd.DataFrame]:
        """获取K线数据（连接池高可用版本）"""
        if not self._ensure_pool():
            return {}

        result = {}
        category = self._to_category(period)

        for symbol in symbols:
            try:
                conn = self._get_connection()
                if not conn:
                    logger.error(f"无可用连接，无法获取 {symbol}")
                    continue

                market = self._get_market(symbol)
                code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')

                data = conn.api.get_security_bars(category, market, code, 0, count or 100)

                if data and len(data) > 0:
                    df = pd.DataFrame(data)

                    # 日期过滤
                    if end_date and 'datetime' in df.columns:
                        df['datetime_str'] = df['datetime'].astype(str).str[:10]
                        df = df[df['datetime_str'] <= end_date]
                        df = df.drop(columns=['datetime_str'])

                    if start_date and 'datetime' in df.columns:
                        df['datetime_str'] = df['datetime'].astype(str).str[:10]
                        df = df[df['datetime_str'] >= start_date]
                        df = df.drop(columns=['datetime_str'])

                    if count and len(df) > count:
                        df = df.tail(count)

                    result[symbol] = self._normalize_kline_df(df, 'pytdx_pool')
                    logger.debug(f"[Pool] {symbol} K线: {len(df)} 条")

            except Exception as e:
                logger.warning(f"[Pool] 获取 {symbol} 失败: {e}")
                # 标记连接为失败，下次自动切换
                if conn:
                    conn.is_connected = False
                continue

        return result

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """获取实时行情"""
        if not self._ensure_pool():
            return {}

        result = {}
        conn = self._get_connection()
        if not conn:
            return result

        # 构建批量查询
        batch = []
        code_to_symbol = {}
        for symbol in symbols:
            market = self._get_market(symbol)
            code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
            batch.append((market, code))
            code_to_symbol[code] = symbol

        try:
            quotes = conn.api.get_security_quotes(batch)
            if quotes:
                for quote in quotes:
                    code = quote.get('code')
                    if code:
                        key = code_to_symbol.get(code, code)
                        result[key] = self._normalize_quote(key, quote)
        except Exception as e:
            logger.error(f"[Pool] 获取行情失败: {e}")
            conn.is_connected = False

        return result

    def _normalize_quote(self, code: str, quote: dict) -> dict:
        """标准化行情数据"""
        return {
            'code': code,
            'price': quote.get('price', 0),
            'open': quote.get('open', 0),
            'high': quote.get('high', 0),
            'low': quote.get('low', 0),
            'close': quote.get('price', 0),
            'pre_close': quote.get('last_close', 0),
            'volume': quote.get('vol', 0),
            'amount': quote.get('amount', 0),
            'change': quote.get('price', 0) - quote.get('last_close', 0),
            'change_pct': round(
                (quote.get('price', 0) - quote.get('last_close', 0)) / quote.get('last_close', 1) * 100, 2
            ) if quote.get('last_close') else 0,
            'bid1': quote.get('bid1', 0),
            'ask1': quote.get('ask1', 0),
            'bid1_vol': quote.get('bid_vol1', 0),
            'ask1_vol': quote.get('ask_vol1', 0),
            'data_source': 'pytdx_pool',
        }

    def get_pool_stats(self) -> dict:
        """获取连接池统计"""
        with self._lock:
            return {
                "status": "运行中" if self._main_conn else "未初始化",
                "pool_size": self._pool_size,
                "main": f"{self._main_conn.host}:{self._main_conn.port} ({self._main_conn.avg_latency:.1f}ms)" if self._main_conn else "无",
                "hot_standby": f"{self._hot_standby.host}:{self._hot_standby.port} ({self._hot_standby.avg_latency:.1f}ms)" if self._hot_standby else "无",
                "pool_count": len(self._pool),
            }

    def is_available(self) -> bool:
        """检查适配器是否可用"""
        return self._ensure_pool()

    def close(self):
        """关闭连接池"""
        self._shutdown = True

        with self._lock:
            all_conns = []
            if self._main_conn:
                all_conns.append(self._main_conn)
            if self._hot_standby:
                all_conns.append(self._hot_standby)
            all_conns.extend(self._pool)

            for conn in all_conns:
                try:
                    conn.api.disconnect()
                except Exception:
                    pass

            self._main_conn = None
            self._hot_standby = None
            self._pool = []

        logger.info("PyTdx 连接池已关闭")


def create_pytdx_pool_adapter(**kwargs) -> V5PyTdxPoolAdapter:
    """工厂函数：创建 PyTdx 连接池适配器"""
    return V5PyTdxPoolAdapter(**kwargs)
