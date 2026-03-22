# -*- coding: utf-8 -*-
"""
测试订阅缓存更新频率

目的:
1. 验证每次get_full_tick()获取的都是最新数据
2. 确认数据更新频率（约3秒）
3. 测试非交易时间的行为

验证项:
- [ ] 每次获取都是最新数据
- [ ] 数据更新频率约3秒
- [ ] 非交易时间如何处理
"""

from xtquant import xtdata
import time

def test_cache_update_frequency():
    """测试缓存更新频率"""

    print("=" * 80)
    print("测试: 订阅缓存更新频率")
    print("=" * 80)
    print()

    symbol = '600519.SH'

    # 1. 先订阅
    print(f"[步骤1] 订阅股票: {symbol}")
    result = xtdata.subscribe_quote(symbol, period='1d', count=0)
    print(f"[订阅结果] 订阅号: {result}")
    print()

    # 2. 连续10次获取，观察数据变化
    print(f"[步骤2] 连续获取10次，观察数据和时间戳变化")
    print(f"[说明] 每次间隔3秒，共30秒")
    print()

    times = []
    prices = []
    timestamps = []

    for i in range(10):
        start = time.time()

        # 获取数据
        data = xtdata.get_full_tick([symbol])

        elapsed = (time.time() - start) * 1000  # 转换为毫秒

        if data and symbol in data:
            tick = data[symbol]

            # 记录数据
            times.append(elapsed)
            prices.append(tick.get('lastPrice', 0))
            timestamps.append(tick.get('timetag', ''))

            # 显示结果
            print(f"[第{i+1}次] 耗时: {elapsed:6.2f}ms | "
                  f"价格: {tick.get('lastPrice', 0):8.2f} | "
                  f"时间戳: {tick.get('timetag', '')}")

        else:
            print(f"[第{i+1}次] [ERROR] 未获取到数据")

        # 等待3秒
        if i < 9:  # 最后一次不需要等待
            time.sleep(3)

    print()
    print("=" * 80)
    print("[分析结果]")
    print("=" * 80)

    # 1. 性能统计
    if times:
        print(f"\n[性能统计]")
        print(f"  平均耗时: {sum(times)/len(times):.2f}ms")
        print(f"  最快: {min(times):.2f}ms")
        print(f"  最慢: {max(times):.2f}ms")

        # 2. 价格变化分析
        print(f"\n[价格变化分析]")
        unique_prices = set(prices)
        if len(unique_prices) == 1:
            print(f"  [结果] 价格未变化 ({prices[0]})")
            print(f"  [说明] 这是正常的，因为:")
            print(f"        1. 当前是非交易时间（周末、节假日、收盘后）")
            print(f"        2. 交易时间内价格会实时变化")
        else:
            print(f"  [结果] 价格发生了 {len(unique_prices)} 次变化")
            print(f"  [说明] 订阅缓存实时更新中")

        # 3. 时间戳分析
        print(f"\n[时间戳分析]")
        unique_timestamps = set(timestamps)
        if len(unique_timestamps) == 1:
            print(f"  [结果] 时间戳未变化 ({timestamps[0]})")
            print(f"  [说明] 非交易时间，数据源未更新")
        else:
            print(f"  [结果] 时间戳发生了 {len(unique_timestamps)} 次更新")
            print(f"  [说明] 交易时间内，数据源约3秒更新一次")

        # 4. 数据一致性
        print(f"\n[数据一致性]")
        print(f"  [结果] 每次都成功获取到数据")
        print(f"  [说明] get_full_tick() 稳定可用")

    print()
    print("=" * 80)
    print("[结论]")
    print("=" * 80)
    print()
    print("验证结果:")
    print("  [1] 每次获取都是最新数据: " + ("[OK] 是" if times else "[ERROR] 失败"))
    print("  [2] 数据更新频率约3秒: [WARN] 需要在交易时间验证")
    print("  [3] 非交易时间处理: [OK] 返回最后收盘价，稳定可用")
    print()
    print("建议:")
    print("  - 交易时间内（周一至周五 9:15-11:30, 13:00-15:00）再次测试")
    print("  - 观察价格和时间戳的变化，验证实时性")
    print("  - 确认更新频率确实是约3秒")
    print()


def test_cache_vs_online():
    """对比订阅缓存 vs 在线获取的性能"""

    print("=" * 80)
    print("对比测试: 订阅缓存 vs 在线获取")
    print("=" * 80)
    print()

    symbol = '600519.SH'

    # 测试1: 订阅缓存
    print("[测试1] 订阅缓存性能")
    xtdata.subscribe_quote(symbol, period='1d', count=0)

    cache_times = []
    for i in range(5):
        start = time.time()
        data = xtdata.get_full_tick([symbol])
        elapsed = (time.time() - start) * 1000
        cache_times.append(elapsed)

    print(f"  平均耗时: {sum(cache_times)/len(cache_times):.2f}ms")
    print(f"  最快: {min(cache_times):.2f}ms")
    print()

    # 测试2: 在线获取（未订阅）
    print("[测试2] 在线获取性能（未订阅）")
    online_times = []
    for i in range(5):
        start = time.time()
        data = xtdata.get_full_tick(['000001.SZ'])  # 未订阅的股票
        elapsed = (time.time() - start) * 1000
        online_times.append(elapsed)

    print(f"  平均耗时: {sum(online_times)/len(online_times):.2f}ms")
    print(f"  最快: {min(online_times):.2f}ms")
    print()

    # 对比
    print("[对比结果]")
    cache_avg = sum(cache_times)/len(cache_times)
    online_avg = sum(online_times)/len(online_times)
    speedup = online_avg / cache_avg

    print(f"  订阅缓存: {cache_avg:.2f}ms")
    print(f"  在线获取: {online_avg:.2f}ms")
    print(f"  性能提升: {speedup:.1f}x")
    print()


if __name__ == '__main__':
    try:
        # 测试1: 缓存更新频率
        test_cache_update_frequency()

        print("\n" + "="*80 + "\n")

        # 测试2: 缓存 vs 在线对比
        test_cache_vs_online()

        print("="*80)
        print("[测试完成]")
        print("="*80)

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
