import time
from pytdx2.hq import TdxHq_API

HOST, PORT = '60.12.136.250', 7709

symbols = [(1, '600000'), (0, '000001'), (1, '600036'), (0, '000002'), (1, '600519'), (1, '600036'), (0, '000333')]

print("="*80)
print("PyTdx2 连接复用测试")
print("="*80)

# 每次新建连接
print("\n[每次新建连接]")
total_time = 0
for market, code in symbols:
    api = TdxHq_API()
    api.connect(HOST, PORT)
    start = time.time()
    quotes = api.get_security_quotes([(market, code)])
    elapsed = (time.time() - start) * 1000
    api.disconnect()
    total_time += elapsed
    print(f"  单只: {elapsed:.2f}ms")
print(f"总耗时: {total_time:.2f}ms")

# 复用连接
print("\n[复用连接]")
api = TdxHq_API()
api.connect(HOST, PORT)
start = time.time()
for market, code in symbols:
    quotes = api.get_security_quotes([(market, code)])
reused_time = (time.time() - start) * 1000
api.disconnect()
print(f"总耗时: {reused_time:.2f}ms")
print(f"平均: {reused_time/len(symbols):.2f}ms/只")
print(f"提升: {total_time/reused_time:.2f}x")
