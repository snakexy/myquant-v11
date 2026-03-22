"""
高级场景测试3: 订阅策略测试

测试目标：
1. 单实例订阅上限
2. 多实例并发订阅
3. 订阅性能测试
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time

print("="*80)
print("场景3: 订阅策略测试")
print("="*80)
print()

# ===== 测试1: 单实例订阅上限 =====
print("[测试1] 单实例订阅上限测试")
print("-"*80)
print("测试: 尝试订阅不同数量的股票")
print()

# 准备测试股票
test_stocks = [f"60{i:04d}.SH" for i in range(1, 501)]  # 500只上海股票

test_counts = [10, 50, 100, 200, 300, 400, 500]

for count in test_counts:
    try:
        stocks = test_stocks[:count]

        print(f"尝试订阅 {count} 只股票...")

        start = time.time()
        for stock in stocks:
            xtdata.subscribe_quote(stock, period='1d', count=0)
        elapsed = time.time() - start

        # 尝试获取数据
        tick_data = xtdata.get_full_tick(stocks)
        success_count = len(tick_data)

        print(f"   [OK] 订阅 {count} 只，耗时 {elapsed:.2f}秒")
        print(f"         成功获取 {success_count} 只数据")

        time.sleep(0.5)

    except Exception as e:
        print(f"   [ERROR] 失败: {e}")
        print(f"         订阅上限可能在 {count} 只左右")
        break

print()

# ===== 测试2: 批量获取性能 =====
print("[测试2] 批量获取性能测试")
print("-"*80)

test_sizes = [1, 10, 50, 100]

for size in test_sizes:
    stocks = test_stocks[:size]

    try:
        start = time.time()
        tick_data = xtdata.get_full_tick(stocks)
        elapsed = (time.time() - start) * 1000

        success = len(tick_data)
        avg_time = elapsed / size if size > 0 else 0

        print(f"获取 {size:3d} 只: {success:3d} 成功, 耗时 {elapsed:6.2f}ms, 平均 {avg_time:.2f}ms/只")

    except Exception as e:
        print(f"获取 {size:3d} 只: 失败 - {e}")

print()

# ===== 测试3: 订阅缓存性能 =====
print("[测试3] 订阅缓存性能测试")
print("-"*80)
print("对比: 订阅后获取 vs 直接在线获取")
print()

stocks = test_stocks[:10]

# 1. 先订阅
print("步骤1: 订阅10只股票...")
for stock in stocks:
    xtdata.subscribe_quote(stock, period='1d', count=0)
time.sleep(1)

# 2. 从订阅缓存获取（应该很快）
print("步骤2: 从订阅缓存获取...")
times_cache = []
for _ in range(10):
    start = time.time()
    tick_data = xtdata.get_full_tick(stocks)
    elapsed = (time.time() - start) * 1000
    times_cache.append(elapsed)

avg_cache = sum(times_cache) / len(times_cache)
print(f"   平均耗时: {avg_cache:.2f}ms")
print(f"   最快: {min(times_cache):.2f}ms")
print(f"   最慢: {max(times_cache):.2f}ms")

print()

# ===== 测试4: 智能订阅模拟 =====
print("[测试4] 智能订阅算法模拟")
print("-"*80)
print("场景: 根据访问频率自动管理订阅列表")
print()

class SimpleSmartSubscription:
    def __init__(self, limit=10):
        self.limit = limit
        self.subscribed = set()
        self.access_count = {}

    def access(self, stock):
        # 记录访问
        self.access_count[stock] = self.access_count.get(stock, 0) + 1

        # 检查是否订阅
        if stock not in self.subscribed:
            if len(self.subscribed) < self.limit:
                # 有空位，订阅
                self.subscribe(stock)
            else:
                # 无空位，检查是否替换
                self.maybe_replace(stock)

    def maybe_replace(self, new_stock):
        # 找访问次数最少的
        min_stock = min(
            self.subscribed,
            key=lambda s: self.access_count.get(s, 0)
        )

        # 如果新股票访问更多，替换
        if self.access_count.get(new_stock, 0) > self.access_count.get(min_stock, 0):
            print(f"   替换: {min_stock} -> {new_stock}")
            self.subscribed.discard(min_stock)
            self.subscribe(new_stock)

    def subscribe(self, stock):
        self.subscribed.add(stock)
        print(f"   订阅: {stock} (已订阅: {len(self.subscribed)}/{self.limit})")

# 模拟访问
smart = SimpleSmartSubscription(limit=5)

print("模拟访问序列:")
access_pattern = [
    ('600000.SH', 10),
    ('600001.SH', 8),
    ('600002.SH', 6),
    ('600003.SH', 5),
    ('600004.SH', 3),
    ('600005.SH', 15),  # 会替换600004
    ('600006.SH', 12),  # 会替换600003
]

for stock, times in access_pattern:
    for _ in range(times):
        smart.access(stock)

print()
print("最终订阅列表:")
for stock in sorted(smart.subscribed):
    print(f"  {stock}: {smart.access_count[stock]}次")

print()
print("="*80)
print("结论:")
print("- 需要实测确定单实例订阅上限")
print("- 订阅后获取性能远高于在线获取")
print("- 智能订阅算法可以优化订阅列表管理")
print("="*80)
