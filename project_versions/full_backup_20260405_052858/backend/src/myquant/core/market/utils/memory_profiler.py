# -*- coding: utf-8 -*-
"""
内存性能分析器 - 追踪内存增长

使用：
    from myquant.core.market.utils.memory_profiler import memory_tracker

    @memory_tracker("操作名称")
    def some_function():
        pass
"""

import os
import sys
import gc
import functools
import threading
from typing import Optional
from loguru import logger

# 尝试导入 psutil
# 先创建模拟类，避免导入失败时崩溃
class MockProcess:
    """模拟 psutil.Process，避免导入失败"""
    def __init__(self, pid):
        self.pid = pid

    def memory_info(self):
        class MockMemoryInfo:
            rss = 0
            vms = 0
        return MockMemoryInfo()

    def memory_percent(self):
        return 0.0

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False
    logger.warning("[内存监控] psutil 未安装，使用模拟模式")


class MemoryTracker:
    """内存追踪器"""

    def __init__(self):
        self._lock = threading.Lock()
        self._records = []
        self._enabled = True
        self._threshold_mb = 10  # 超过10MB变化才记录

    def get_memory_mb(self) -> float:
        """获取当前内存使用（MB）"""
        if not _PSUTIL_AVAILABLE:
            return 0.0
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except Exception as e:
            logger.debug(f"[内存监控] 获取内存失败: {e}")
            return 0.0

    def record(self, operation: str, delta_mb: float, total_mb: float):
        """记录内存变化"""
        if not self._enabled:
            return

        with self._lock:
            self._records.append({
                'operation': operation,
                'delta_mb': delta_mb,
                'total_mb': total_mb,
                'timestamp': __import__('time').time()
            })

            # 只保留最近100条记录
            if len(self._records) > 100:
                self._records = self._records[-100:]

    def track(self, operation: str):
        """装饰器：追踪函数内存变化"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)

                # 强制GC后获取基准内存
                gc.collect()
                gc.collect()
                before_mb = self.get_memory_mb()

                try:
                    result = func(*args, **kwargs)

                    # 再次GC后获取内存
                    gc.collect()
                    after_mb = self.get_memory_mb()
                    delta_mb = after_mb - before_mb

                    # 超过阈值才记录
                    if abs(delta_mb) > self._threshold_mb:
                        self.record(operation, delta_mb, after_mb)
                        logger.warning(
                            f"[内存监控] {operation}: "
                            f"+{delta_mb:.1f}MB (总计: {after_mb:.1f}MB)"
                        )
                    else:
                        logger.debug(
                            f"[内存监控] {operation}: "
                            f"+{delta_mb:.1f}MB (总计: {after_mb:.1f}MB)"
                        )

                    return result
                except Exception as e:
                    after_mb = self.get_memory_mb()
                    delta_mb = after_mb - before_mb
                    logger.error(
                        f"[内存监控] {operation} 失败: {e}, "
                        f"内存变化: +{delta_mb:.1f}MB"
                    )
                    raise

            return wrapper
        return decorator

    def get_top_growth(self, n: int = 10) -> list:
        """获取内存增长最多的操作"""
        with self._lock:
            sorted_records = sorted(
                self._records,
                key=lambda x: x['delta_mb'],
                reverse=True
            )
            return sorted_records[:n]

    def print_summary(self):
        """打印内存使用摘要"""
        if not self._records:
            logger.info("[内存监控] 暂无记录")
            return

        logger.info("=" * 60)
        logger.info("内存使用摘要 (Top 10 增长)")
        logger.info("=" * 60)

        top_growth = self.get_top_growth(10)
        for i, record in enumerate(top_growth, 1):
            logger.info(
                f"{i}. {record['operation']}: "
                f"+{record['delta_mb']:.1f}MB "
                f"(总计: {record['total_mb']:.1f}MB)"
            )

        logger.info("=" * 60)

    def enable(self):
        """启用监控"""
        self._enabled = True
        logger.info("[内存监控] 已启用")

    def disable(self):
        """禁用监控"""
        self._enabled = False
        logger.info("[内存监控] 已禁用")


# 全局实例
memory_tracker = MemoryTracker()


# 快捷函数
def track_memory(operation: str):
    """快捷装饰器"""
    return memory_tracker.track(operation)


def print_memory_summary():
    """打印内存摘要"""
    memory_tracker.print_summary()


def get_current_memory_mb() -> float:
    """获取当前内存"""
    return memory_tracker.get_memory_mb()


if __name__ == "__main__":
    # 测试
    print(f"当前内存: {get_current_memory_mb():.1f} MB")

    @track_memory("测试操作")
    def test_func():
        # 分配一些内存
        data = [i for i in range(1000000)]
        return data

    result = test_func()
    print_memory_summary()
