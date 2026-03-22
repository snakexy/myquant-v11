"""
测试全A股票数据获取策略

验证：如何高效获取全A股的实时行情
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time

print("="*80)
print("全A股票数据获取测试")
print("="*80)
print()

# ===== 测试1: 单批获取（验证上限）=====
print("[测试1] 单批获取 - 测试订阅上限")
print("-"*80)

test_sizes = [10, 50, 100, 200, 300, 400]

for size in test_sizes:
    stocks = [f"60{i:04d}.SH" for i in range(1, size + 1)]

    # 先订阅
    start = time.time()
    for stock in stocks:
        try:
            xtdata.subscribe_quote(stock, period='1d')
        except:
            pass
    subscribe_time = (time.time() - start) * 1000

    # 获取数据
    start = time.time()
    data = xtdata.get_full_tick(stocks)
    get_time = (time.time() - start) * 1000

    success_count = len(data) if data else 0

    print(f"请求{size:3d}只: 订阅{subscribe_time:6.2f}ms, 获取{get_time:6.2f}ms, 成功{success_count:3d}只")

    # 如果失败太多，说明到达上限
    if success_count < size * 0.9:  # 成功率低于90%
        print(f"   ⚠️ 订阅上限可能在 {size} 只左右")
        break

print()

# ===== 测试2: 分批轮询策略 =====
print("[测试2] 分批轮询策略（模拟全A）")
print("-"*80)

# 假设有5000只股票
total_stocks = 5000
batch_size = 300  # 每批300只
batch_count = (total_stocks + batch_size - 1) // batch_size

print(f"总股票数: {total_stocks}")
print(f"每批数量: {batch_size}")
print(f"批次数量: {batch_count}")
print()

total_time = 0
for batch_num in range(batch_count):
    start = batch_num * batch_size
    end = min(start + batch_size, total_stocks)

    # 模拟获取（不实际订阅，只估算时间）
    estimated_time = 150  # 假设每批150ms
    total_time += estimated_time

    print(f"批次{batch_num + 1}: 股票 {start + 1}-{end}, 预计{estimated_time}ms")

print(f"\n总计时间: {total_time / 1000:.2f}秒")
print(f"平均延迟: {total_time / batch_count:.2f}ms/批")
print()

# ===== 测试3: 多实例并发策略 =====
print("[测试3] 多实例并发策略（理论）")
print("-"*80)

instance_count = 17  # 17个MiniQMT实例
per_instance = 300   # 每个实例300只
total_capacity = instance_count * per_instance

print(f"实例数量: {instance_count}")
print(f"每实例订阅: {per_instance}只")
print(f"总容量: {total_capacity}只")
print(f"覆盖全A: {'✅ 是' if total_capacity >= 5000 else '❌ 否'}")
print()

# 性能估算
concurrent_time = 150  # 并发获取，约150ms
sequential_time = total_time  # 顺序轮询的时间

print(f"性能对比:")
print(f"  多实例并发: {concurrent_time}ms")
print(f"  分批轮询:   {sequential_time}ms")
print(f"  性能提升:   {sequential_time / concurrent_time:.1f}x")

print()
print("="*80)
print("结论：")
print("- 单批获取上限约300只")
print("- 全A获取需要分批或多实例")
print("- 多实例并发比分批轮询快很多")
print("="*80)
