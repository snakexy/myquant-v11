# -*- coding: utf-8 -*-
"""
PyTdx2 优化测试

测试内容：
1. 缓存效果验证
2. 异步并发性能
3. 连接池性能

> 创建时间: 2026-03-20
"""
import sys
sys.path.insert(0, 'e:/MyQuant_v10.0.0v2/backend')

import time
import asyncio
from data.adapters.pytdx_adapter import PyTdxAdapter
from data.adapters.pytdx_cache import get_global_cache
from data.adapters.pytdx_adapter_async import AsyncPyTdxAdapter
from data.adapters.pytdx_pool import PyTdxConnectionPool


def test_cache_effectiveness():
    """测试缓存有效性"""
    print("="*80)
    print("测试1: 缓存效果验证")
    print("="*80)

    adapter = PyTdxAdapter(enable_cache=True)
    adapter.connect()

    # 测试股票
    test_symbol = '600000'

    # 第一次请求（缓存未命中）
    print("\n[第一次请求] 获取除权信息（缓存未命中）")
    start = time.time()
    try:
        # 通过获取K线触发除权信息获取
        kline1 = adapter.get_kline_data(test_symbol, period='1d', count=100, adjust='qfq')
        time1 = (time.time() - start) * 1000
        print(f"耗时: {time1:.2f}ms, 获取K线: {len(kline1) if kline1 else 0}条")
    except Exception as e:
        print(f"失败: {e}")
        time1 = 0

    # 第二次请求（缓存命中）
    print("\n[第二次请求] 获取除权信息（缓存应该命中）")
    start = time.time()
    try:
        kline2 = adapter.get_kline_data(test_symbol, period='1d', count=100, adjust='qfq')
        time2 = (time.time() - start) * 1000
        print(f"耗时: {time2:.2f}ms, 获取K线: {len(kline2) if kline2 else 0}条")
    except Exception as e:
        print(f"失败: {e}")
        time2 = 0

    # 显示缓存统计
    cache = get_global_cache()
    stats = cache.get_stats()
    print(f"\n缓存统计: 命中={stats['hits']}, 未命中={stats['misses']}, 命中率={stats['hit_rate']}")

    adapter.disconnect()

    if time1 > 0 and time2 > 0:
        speedup = time1 / time2 if time2 > 0 else 0
        print(f"\n缓存效果: {speedup:.2f}x 加速")


async def test_async_performance():
    """测试异步并发性能"""
    print("\n" + "="*80)
    print("测试2: 异步并发性能")
    print("="*80)

    adapter = AsyncPyTdxAdapter()
    await adapter.connect_async() if hasattr(adapter, 'connect_async') else adapter.connect()

    # 准备测试数据
    symbols = ['600000', '000001', '600036', '000002', '600519']
    groups = [symbols] * 10  # 10组，每组5只股票

    # 同步方式
    print("\n[同步方式] 顺序获取10组K线")
    start = time.time()
    for group in groups:
        try:
            adapter.get_kline('600000', period='1d', count=100)
        except:
            pass
    sync_time = (time.time() - start) * 1000
    print(f"总耗时: {sync_time:.2f}ms")

    # 异步方式
    print("\n[异步方式] 并发获取10组K线")
    start = time.time()
    try:
        tasks = [adapter.get_kline_async('600000', period='1d', count=100) for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        async_time = (time.time() - start) * 1000
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        print(f"总耗时: {async_time:.2f}ms, 成功: {success_count}/10")
    except Exception as e:
        print(f"失败: {e}")
        async_time = 0

    await adapter.close_async()

    if sync_time > 0 and async_time > 0:
        speedup = sync_time / async_time
        print(f"\n异步效果: {speedup:.2f}x 加速")


def test_connection_pool():
    """测试连接池性能"""
    print("\n" + "="*80)
    print("测试3: 连接池性能")
    print("="*80)

    try:
        pool = PyTdxConnectionPool(pool_size=3)
        print(f"连接池初始化: {pool}")

        # 准备测试数据
        symbols_list = [['600000', '000001'], ['600036', '000002'], ['600519', '000858']]

        # 测试并发请求
        print("\n[并发请求] 3组股票快照")
        start = time.time()
        results = pool.request_parallel(symbols_list, func='get_realtime_quote')
        total_time = (time.time() - start) * 1000

        success_count = sum(1 for r in results if r is not None)
        print(f"总耗时: {total_time:.2f}ms, 成功: {success_count}/3")

        # 健康检查
        health = pool.health_check()
        print(f"\n健康检查:")
        for conn_id, status in health.items():
            print(f"  {conn_id}: {status['server']} - 健康={status['healthy']}")

        pool.close_all()

    except Exception as e:
        print(f"连接池测试失败: {e}")


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*80)
    print("PyTdx2 优化测试套件")
    print("="*80)

    # 测试1: 缓存
    test_cache_effectiveness()

    # 测试2: 异步
    await test_async_performance()

    # 测试3: 连接池
    test_connection_pool()

    print("\n" + "="*80)
    print("测试完成")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
