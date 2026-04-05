"""
QLib Core 性能测试模块

提供各种性能基准测试和性能优化工具
"""

from .smart_fetcher_benchmark import SmartFetcherBenchmark, run_benchmark

__all__ = [
    'SmartFetcherBenchmark',
    'run_benchmark'
]
