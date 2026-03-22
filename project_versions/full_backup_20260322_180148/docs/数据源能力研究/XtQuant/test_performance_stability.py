# -*- coding: utf-8 -*-
"""
分钟线性能稳定性测试

验证：
1. 第一次调用 vs 后续调用
2. 缓存机制
3. 性能稳定性
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time

symbol = '600519.SH'

print("="*80)
print("性能稳定性测试")
print("="*80)
print("股票: %s" % symbol)
print()

# ===== 测试1: 5分钟K线 - 多次调用 =====
print("[测试1] 5分钟K线 - 连续调用10次")
print("-"*80)

xtdata.subscribe_quote(symbol, period='5m', count=0)

times_5m = []
for i in range(10):
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time='',
        end_time='',
        count=120,
        dividend_type='none',
        fill_data=True
    )
    elapsed = (time.time() - start) * 1000
    times_5m.append(elapsed)

    if i == 0:
        print("第1次调用: %.2fms (首次)" % elapsed)
    else:
        print("第%d次调用: %.2fms" % (i+1, elapsed))

    if data and symbol in data:
        print("  -> 数据条数: %d" % len(data[symbol]))

print()
print("统计:")
print("  平均: %.2fms" % (sum(times_5m) / len(times_5m)))
print("  最快: %.2fms" % min(times_5m))
print("  最慢: %.2fms" % max(times_5m))
print("  首次: %.2fms" % times_5m[0])
print("  后续平均: %.2fms" % (sum(times_5m[1:]) / len(times_5m[1:])))
print()

# ===== 测试2: 1分钟K线 - 多次调用 =====
print("[测试2] 1分钟K线 - 连续调用10次")
print("-"*80)

xtdata.subscribe_quote(symbol, period='1m', count=0)

times_1m = []
for i in range(10):
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1m',
        start_time='',
        end_time='',
        count=240,
        dividend_type='none',
        fill_data=True
    )
    elapsed = (time.time() - start) * 1000
    times_1m.append(elapsed)

    if i == 0:
        print("第1次调用: %.2fms (首次)" % elapsed)
    else:
        print("第%d次调用: %.2fms" % (i+1, elapsed))

    if data and symbol in data:
        print("  -> 数据条数: %d" % len(data[symbol]))

print()
print("统计:")
print("  平均: %.2fms" % (sum(times_1m) / len(times_1m)))
print("  最快: %.2fms" % min(times_1m))
print("  最慢: %.2fms" % max(times_1m))
print("  首次: %.2fms" % times_1m[0])
print("  后续平均: %.2fms" % (sum(times_1m[1:]) / len(times_1m[1:])))
print()

# ===== 测试3: 不同count对比 =====
print("[测试3] 不同count值对比 - 各5次")
print("-"*80)

for count in [60, 120, 240, 480]:
    xtdata.subscribe_quote(symbol, period='5m', count=0)
    times = []

    for i in range(5):
        start = time.time()
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period='5m',
            start_time='',
            end_time='',
            count=count,
            dividend_type='none',
            fill_data=True
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

    print("count=%3d: 平均 %.2fms, 范围 [%.2f, %.2f]" % (
        count, sum(times)/len(times), min(times), max(times)
    ))

print()
print("="*80)
print("结论:")
print("- 观察首次调用是否有额外开销")
print("- 观察后续调用是否使用缓存")
print("- 观察count对性能的影响")
print("="*80)
