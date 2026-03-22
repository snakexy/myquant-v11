import time
from pytdx2.hq import TdxHq_API
from concurrent.futures import ThreadPoolExecutor

api = TdxHq_API()
api.connect('180.153.18.170', 80)

symbols_list = [[(1, '600000'), (0, '000001'), (1, '600036')]] * 3  # 9只股票

print("="*80)
print("PyTdx2 快照并发测试")
print("="*80)

# 串行获取9只
print("\n[串行获取9只]")
start = time.time()
for symbols in symbols_list:
    quotes = api.get_security_quotes(symbols)
serial_time = (time.time() - start) * 1000
print(f"耗时: {serial_time:.2f}ms")

# 并发获取9只
print("\n[并发获取9只]")
def get_quotes(symbols):
    start = time.time()
    quotes = api.get_security_quotes(symbols)
    elapsed = (time.time() - start) * 1000
    return elapsed, len(quotes) if quotes else 0

start = time.time()
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(get_quotes, symbols_list))
concurrent_time = (time.time() - start) * 1000

for elapsed, count in results:
    print(f"  批次: {elapsed:.2f}ms ({count}只)")
print(f"总耗时: {concurrent_time:.2f}ms")
print(f"加速比: {serial_time/concurrent_time:.2f}x")

api.disconnect()
