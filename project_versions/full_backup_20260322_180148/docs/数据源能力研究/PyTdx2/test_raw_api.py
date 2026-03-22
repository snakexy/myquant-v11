import time
from pytdx2.hq import TdxHq_API

print("="*80)
print("PyTdx2 原始API性能测试")
print("="*80)

api = TdxHq_API()
api.connect('180.153.18.172', 80)  # 使用最快服务器

# 准备测试数据
symbols = [(1, '600000'), (0, '000001'), (1, '600036'), (0, '000002'), (1, '600519')]
symbols += [(1, '600036'), (0, '000002'), (1, '600519'), (1, '600000'), (0, '000001')]  # 100只
symbols += symbols * 9  # 总共100只

print(f"\n[测试] 获取{len(symbols)}只股票快照")

start = time.time()
quotes = api.get_security_quotes(symbols)
elapsed = (time.time() - start) * 1000

print(f"耗时: {elapsed:.2f}ms")
print(f"返回: {len(quotes)}只")
print(f"平均: {elapsed/len(symbols):.2f}ms/只")

# 验证数据
if quotes and len(quotes) > 0:
    print(f"\n第一只股票: {quotes[0]}")

api.disconnect()

# 批量大小对比
print("\n[批量大小对比]")
for batch_size in [50, 100, 200, 400]:
    test_symbols = symbols[:batch_size]
    start = time.time()
    quotes = api.get_security_quotes(test_symbols)
    elapsed = (time.time() - start) * 1000
    print(f"批量{batch_size:3d}只: {elapsed:6.2f}ms ({len(quotes)}只成功)")
