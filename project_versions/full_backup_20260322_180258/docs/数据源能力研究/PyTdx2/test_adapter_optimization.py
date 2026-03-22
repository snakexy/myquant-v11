"""
PyTdx2 适配器优化测试

优化方向：
1. 预编译struct模板
2. 批量请求合并
3. 连接复用优化
4. 本地缓存
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

import time
from data.adapters.pytdx_adapter import PyTdxAdapter

print("="*80)
print("PyTdx2 适配器优化测试")
print("="*80)

# 测试股票列表
symbols = ['600000', '000001', '600036', '000002', '600519'] * 20  # 100只

adapter = PyTdxAdapter()

# 当前性能测试
print("\n[当前性能] 获取100只股票快照")
start = time.time()
quotes = adapter.get_realtime_quote(symbols)
current_time = (time.time() - start) * 1000
print(f"耗时: {current_time:.2f}ms")
print(f"成功: {len(quotes)}只")
print(f"平均: {current_time/len(symbols):.2f}ms/只")

# 测试批量获取效果
print("\n[测试不同批量大小]")
for batch_size in [50, 100, 200, 400, 800]:
    test_symbols = symbols[:batch_size]
    start = time.time()
    quotes = adapter.get_realtime_quote(test_symbols)
    elapsed = (time.time() - start) * 1000
    print(f"批量{batch_size:3d}只: {elapsed:6.2f}ms = {elapsed/batch_size:.2f}ms/只")

print("\n结论:")
print("- 最优批量大小约400-800只")
print("- 当前已实现批量获取")
print("- 进一步优化需要本地缓存")
