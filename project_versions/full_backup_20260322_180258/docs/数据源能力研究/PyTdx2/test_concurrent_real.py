import time
from pytdx2.hq import TdxHq_API
from concurrent.futures import ThreadPoolExecutor, as_completed

HOST, PORT = '60.12.136.250', 7709

symbols = [(1, '600000'), (0, '000001'), (1, '600036'), (0, '000002'), (1, '600519'), (1, '600036'), (0, '000333')]

print("="*80)
print("PyTdx2 并发性能测试 (可用服务器)")
print("="*80)

# 串行获取
print("\n[串行获取7只]")
api = TdxHq_API()
api.connect(HOST, PORT)
start = time.time()
for market, code in symbols:
    quotes = api.get_security_quotes([(market, code)])
serial_time = (time.time() - start) * 1000
api.disconnect()
print(f"耗时: {serial_time:.2f}ms")

# 并发获取（每个请求独立连接）
print("\n[并发获取7只]")
def get_quote(item):
    api = TdxHq_API()
    api.connect(HOST, PORT)
    start = time.time()
    quotes = api.get_security_quotes([item])
    elapsed = (time.time() - start) * 1000
    api.disconnect()
    return elapsed, len(quotes) if quotes else 0

start = time.time()
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(get_quote, symbols))
concurrent_time = (time.time() - start) * 1000

for elapsed, count in results:
    print(f"  单只: {elapsed:.2f}ms ({count}条)")
print(f"总耗时: {concurrent_time:.2f}ms")
print(f"加速比: {serial_time/concurrent_time:.2f}x")
print(f"平均: {concurrent_time/len(symbols):.2f}ms/只")
