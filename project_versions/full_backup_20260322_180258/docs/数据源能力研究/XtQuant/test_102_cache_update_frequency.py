# -*- coding: utf-8 -*-
"""
测试2: 订阅缓存更新频率

目标：
1. 验证订阅后缓存多久更新一次
2. 验证每次获取都是最新数据
3. 验证非交易时间如何处理
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime

print("="*80)
print("测试: 订阅缓存更新频率")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ===== 准备：订阅股票 =====
print("[准备] 订阅股票")
print("-"*80)

symbol = '600519.SH'
try:
    xtdata.subscribe_quote(symbol, period='1d', count=0)
    print(f"[OK] 已订阅 {symbol} 日K线")
except Exception as e:
    print(f"[ERROR] 订阅失败: {e}")
    print("无法继续测试")
    exit(1)

print()

# ===== 测试1: 连续获取，观察缓存更新 =====
print("[测试1] 连续获取10次（观察更新频率）")
print("-"*80)
print("说明: 每次获取间隔3秒，观察数据是否有变化")
print()

times = []
prices = []
last_price = None

for i in range(10):
    start = time.time()
    try:
        # 获取快照
        data = xtdata.get_full_tick([symbol])
        elapsed = (time.time() - start) * 1000

        if data and symbol in data:
            quote = data[symbol]
            current_price = quote.get('lastPrice')

            times.append(elapsed)
            prices.append(current_price)

            # 检查价格是否变化
            price_change = "相同" if current_price == last_price else f"变化({last_price} → {current_price})"
            last_price = current_price

            print(f"第{i+1:2d}次: {elapsed:6.2f}ms, 价格={current_price:8.2f}, {price_change}")
        else:
            print(f"第{i+1:2d}次: 无数据")

    except Exception as e:
        print(f"第{i+1:2d}次: 错误 - {e}")

    # 等待3秒
    if i < 9:
        time.sleep(3)

print()
print(f"统计: 平均耗时 {sum(times)/len(times):.2f}ms")
print(f"最快: {min(times):.2f}ms")
print(f"最慢: {max(times):.2f}ms")

# 检查价格是否有变化
unique_prices = len(set(prices))
print(f"价格变化次数: {len(prices) - 1} 次")
print()

# ===== 测试2: 检查缓存一致性 =====
print("[测试2] 检查缓存一致性")
print("-"*80)
print("说明: 同一时刻获取多次，验证数据是否一致")
print()

# 快速连续获取5次
snapshots = []
for i in range(5):
    start = time.time()
    data = xtdata.get_full_tick([symbol])
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        quote = data[symbol].copy()  # 复制避免引用
        snapshots.append(quote)

    time.sleep(0.1)  # 间隔100ms

# 比较所有快照
if len(snapshots) >= 2:
    print("比较5次快照的字段:")

    reference = snapshots[0]
    fields_to_check = ['lastPrice', 'lastClose', 'amount', 'volume']

    all_match = True
    for field in fields_to_check:
        values = [s.get(field) for s in snapshots]
        if len(set(values)) == 1:
            print(f"  {field}: 所有快照一致 ✅")
        else:
            print(f"  {field}: 快照不一致 ❌")
            all_match = False

    if all_match:
        print("结论: 同一时刻获取的数据完全一致（缓存机制正常）✅")
    else:
        print("结论: 数据不一致（缓存可能更新）⚠️")
else:
    print("快照数据不足，无法比较")

print()

# ===== 测试3: 测试K线数据更新 =====
print("[测试3] 测试K线数据更新")
print("-"*80)
print("说明: 观察5分钟内K线数据是否更新")
print()

# 获取当前K线
try:
    data1 = xtdata.get_market_data_ex(
        field_list=['time', 'close'],
        stock_list=[symbol],
        period='1d',
        start_time='',
        end_time='',
        count=5,
        dividend_type='none'
    )

    if data1 and symbol in data1:
        df1 = data1[symbol]
        print(f"第一次获取: {len(df1)} 条")
        if len(df1) > 0:
            print(f"  最新: {df1.index[-1]}, 收盘: {df1['close'].iloc[-1]}")

    # 等待5秒
    print("等待5秒...")
    time.sleep(5)

    # 再次获取
    data2 = xtdata.get_market_data_ex(
        field_list=['time', 'close'],
        stock_list=[symbol],
        period='1d',
        start_time='',
        end_time='',
        count=5,
        dividend_type='none'
    )

    if data2 and symbol in data2:
        df2 = data2[symbol]
        print(f"第二次获取: {len(df2)} 条")
        if len(df2) > 0:
            print(f"  最新: {df2.index[-1]}, 收盘: {df2['close'].iloc[-1]}")

        # 比较两次数据
        if len(df1) > 0 and len(df2) > 0:
            if df1['close'].iloc[-1] != df2['close'].iloc[-1]:
                print("结论: 收盘价有变化，数据已更新 ✅")
            else:
                print("结论: 收盘价相同，可能未更新")

except Exception as e:
    print(f"[ERROR] 测试失败: {e}")

print()
print("="*80)
print("结论:")
print("- 订阅缓存应该实时更新（交易时间）")
print("- 非交易时间可能使用最后收盘价")
print("- 缓存一致性验证：同一时刻多次获取应返回相同数据")
print("="*80)
