# -*- coding: utf-8 -*-
"""
PyTdx2 优化简化测试

> 创建时间: 2026-03-20
"""
import sys
sys.path.insert(0, 'e:/MyQuant_v10.0.0v2/backend')

import time
from data.adapters.pytdx_adapter import PyTdxAdapter
from data.adapters.pytdx_cache import get_global_cache


def test_cache_effectiveness():
    """测试缓存有效性"""
    print("="*80)
    print("测试: 缓存效果验证")
    print("="*80)

    adapter = PyTdxAdapter(enable_cache=True)
    adapter.connect()

    # 测试股票
    test_symbol = '600000'

    # 第一次请求（缓存未命中）
    print("\n[第一次请求] 获取前复权K线（缓存未命中）")
    start = time.time()
    try:
        kline1 = adapter.get_kline_data(
            [test_symbol], period='1d', count=100, adjust_type='qfq'
        )
        time1 = (time.time() - start) * 1000
        count1 = len(kline1[test_symbol]) if kline1 and test_symbol in kline1 else 0
        print(f"耗时: {time1:.2f}ms, 获取K线: {count1}条")
    except Exception as e:
        print(f"失败: {e}")
        time1 = 0
        adapter.disconnect()
        return

    # 第二次请求（缓存命中）
    print("\n[第二次请求] 获取前复权K线（缓存应该命中）")
    start = time.time()
    try:
        kline2 = adapter.get_kline_data(
            [test_symbol], period='1d', count=100, adjust_type='qfq'
        )
        time2 = (time.time() - start) * 1000
        count2 = len(kline2[test_symbol]) if kline2 and test_symbol in kline2 else 0
        print(f"耗时: {time2:.2f}ms, 获取K线: {count2}条")
    except Exception as e:
        print(f"失败: {e}")
        time2 = 0

    # 显示缓存统计
    cache = get_global_cache()
    stats = cache.get_stats()
    print(f"\n缓存统计: 命中={stats['hits']}, 未命中={stats['misses']}, "
          f"命中率={stats['hit_rate']}, 大小={stats['size']}")

    adapter.disconnect()

    if time1 > 0 and time2 > 0:
        speedup = time1 / time2 if time2 > 0 else 0
        print(f"\n缓存效果: {speedup:.2f}x 加速")
        print(f"时间节省: {time1 - time2:.2f}ms")


if __name__ == "__main__":
    test_cache_effectiveness()
