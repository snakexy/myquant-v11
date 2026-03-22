# -*- coding: utf-8 -*-
"""
PyTdx2 动态服务器选速模块

功能:
1. 测试所有服务器的响应速度
2. 自动选择TOP5最快服务器
3. 定期重新测试(可选)
4. 缓存测试结果
"""

import time
import threading
from typing import List, Tuple, Optional
from loguru import logger

try:
    from pytdx2.hq import TdxHq_API
    from pytdx2.config.hosts import hq_hosts
    PYTDX_AVAILABLE = True
except ImportError:
    PYTDX_AVAILABLE = False


class ServerSpeedTester:
    """服务器速度测试器"""

    def __init__(self, test_symbol: Tuple[int, str] = (1, '600000')):
        """
        初始化测试器

        Args:
            test_symbol: 用于测试的股票代码 (market, code)
        """
        if not PYTDX_AVAILABLE:
            raise ImportError("pytdx2未安装")

        self.test_symbol = test_symbol
        self._cache = {}  # 缓存测试结果
        self._cache_time = 0
        self._lock = threading.Lock()

    def test_server(self, host: str, port: int, timeout: float = 3.0) -> Optional[float]:
        """
        测试单个服务器速度

        Args:
            host: 服务器地址
            port: 服务器端口
            timeout: 超时时间(秒)

        Returns:
            平均响应时间(ms)，失败返回None
        """
        api = TdxHq_API()
        try:
            start = time.time()
            if not api.connect(host, port, time_out=timeout):
                api.disconnect()
                return None

            # 测试3次取平均值
            times = []
            for _ in range(3):
                t_start = time.time()
                quotes = api.get_security_quotes([self.test_symbol])
                if quotes and len(quotes) > 0:
                    times.append((time.time() - t_start) * 1000)
                time.sleep(0.05)  # 避免频繁请求

            api.disconnect()

            if times:
                return sum(times) / len(times)
            else:
                return None

        except Exception as e:
            logger.debug(f"测试服务器 {host}:{port} 失败: {e}")
            return None

    def test_all_servers(
        self,
        server_list: List[Tuple[str, str, int]] = None,
        top_n: int = 5
    ) -> List[Tuple[str, int, float]]:
        """
        测试所有服务器并返回最快的N个

        Args:
            server_list: 服务器列表 [(name, host, port), ...]
            top_n: 返回最快的N个

        Returns:
            [(host, port, avg_time_ms), ...] 按速度排序
        """
        if server_list is None:
            server_list = hq_hosts[:30]  # 测试前30个

        results = []
        total = len(server_list)

        logger.info(f"开始测试{total}个服务器速度...")
        for i, (name, host, port) in enumerate(server_list):
            elapsed = self.test_server(host, port)
            if elapsed is not None:
                results.append((host, port, elapsed))
                logger.debug(f"[{i+1}/{total}] {host}:{port} - {elapsed:.2f}ms")
            else:
                logger.debug(f"[{i+1}/{total}] {host}:{port} - 失败")

        # 按速度排序
        results.sort(key=lambda x: x[2])

        # 缓存结果
        with self._lock:
            self._cache = {'results': results[:top_n], 'time': time.time()}
            self._cache_time = time.time()

        logger.info(f"服务器测试完成，最快服务器:")
        for host, port, avg_time in results[:top_n]:
            logger.info(f"  {host}:{port} - {avg_time:.2f}ms")

        return results[:top_n]

    def get_fastest_servers(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        获取最快的N个服务器（使用缓存）

        Args:
            top_n: 返回最快的N个

        Returns:
            [(host, port), ...]
        """
        with self._lock:
            # 缓存1小时有效
            if self._cache and (time.time() - self._cache_time) < 3600:
                return [(host, port) for host, port, _ in self._cache['results']]

        # 缓存过期，重新测试
        results = self.test_all_servers(top_n=top_n)
        return [(host, port) for host, port, _ in results]


# 全局实例
_tester = None


def get_server_tester() -> ServerSpeedTester:
    """获取全局测试器实例"""
    global _tester
    if _tester is None:
        _tester = ServerSpeedTester()
    return _tester
