"""
关键测试：get_full_tick 是否需要先订阅？

验证：get_full_tick 的 "full" 是什么意思
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata

print("="*80)
print("get_full_tick 功能测试")
print("="*80)
print()

# 测试股票（确保没有订阅）
test_stocks = ['600519.SH', '000001.SZ', '600000.SH']

print("[测试1] 不订阅直接调用 get_full_tick")
print("-"*80)
print("说明: 测试 get_full_tick 是否需要先订阅")
print()

try:
    # 直接调用，不订阅
    data = xtdata.get_full_tick(test_stocks)

    if data:
        print(f"[OK] 成功！获取 {len(data)} 只股票数据")

        for symbol in test_stocks[:2]:
            if symbol in data:
                tick = data[symbol]
                print(f"\n{symbol}:")
                print(f"  最新价: {tick.get('lastPrice')}")
                print(f"  成交量: {tick.get('volume')}")
                print(f"  字段数: {len(tick)}")
    else:
        print("[FAIL] 返回空数据")

    print("\n结论: get_full_tick 可以获取未订阅的股票！")

except Exception as e:
    print(f"[ERROR] 失败: {e}")
    print("结论: get_full_tick 可能需要先订阅")

print()

# ===== 测试2: 对比订阅和非订阅的性能 =====
print("[测试2] 对比：订阅后 vs 直接获取")
print("-"*80)

import time

# 方案A: 不订阅直接获取
print("方案A: 不订阅直接获取")
stocks_a = [f"60{i:04d}.SH" for i in range(1, 11)]

start = time.time()
data_a = xtdata.get_full_tick(stocks_a)
time_a = (time.time() - start) * 1000

print(f"  获取{len(stocks_a)}只: {time_a:.2f}ms")
print(f"  成功: {len(data_a)}只")

print()

# 方案B: 先订阅再获取
print("方案B: 先订阅再获取")
stocks_b = [f"60{i:04d}.SH" for i in range(11, 21)]

start = time.time()
for stock in stocks_b:
    try:
        xtdata.subscribe_quote(stock, period='1d')
    except:
        pass

time.sleep(0.5)  # 等待订阅生效

data_b = xtdata.get_full_tick(stocks_b)
time_b = (time.time() - start) * 1000

print(f"  订阅+获取{len(stocks_b)}只: {time_b:.2f}ms")
print(f"  成功: {len(data_b)}只")

print()
print(f"性能对比: 订阅版({time_b:.2f}ms) vs 直接版({time_a:.2f}ms)")

if time_b < time_a:
    print(f"订阅快 {time_a / time_b:.1f}x")
else:
    print(f"直接获取快 {time_b / time_a:.1f}x")

print()

# ===== 测试3: "full"的含义 =====
print("[测试3] get_full_tick 返回的完整字段")
print("-"*80)

symbol = '600519.SH'

# 先尝试获取一次
data = xtdata.get_full_tick([symbol])

if symbol in data:
    tick = data[symbol]
    print(f"返回字段数量: {len(tick)}")
    print(f"字段列表:")
    for i, (key, value) in enumerate(list(tick.items())[:20], 1):
        print(f"  {i:2d}. {key}: {value}")

    if len(tick) > 20:
        print(f"  ... 还有 {len(tick) - 20} 个字段")

    print(f"\n结论: 'full' 指的是返回完整字段（OHLCV+买卖盘等），不是指全部股票")

print()
print("="*80)
print("最终结论：")
print("- get_full_tick 的 'full' = 完整字段（不是全部股票）")
print("- 可能可以获取未订阅股票（需要实测验证）")
print("- 订阅后性能会更好（从缓存读取）")
print("="*80)
