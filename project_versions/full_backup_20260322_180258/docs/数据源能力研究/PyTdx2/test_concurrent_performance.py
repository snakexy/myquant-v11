import time
from pytdx2.hq import TdxHq_API
from concurrent.futures import ThreadPoolExecutor
import threading

api = TdxHq_API()
api.connect('180.153.18.170', 80)

symbols = [('600000', 1), ('000001', 0), ('600036', 1), ('000002', 0), ('600519', 1)]

print("="*80)
print("PyTdx2 并发优化测试")
print("="*80)

# 串行获取
print("\n[串行获取]")
start = time.time()
for code, market in symbols:
    data = api.get_security_bars(9, market, code, 0, 100)
serial_time = (time.time() - start) * 1000
print(f"总耗时: {serial_time:.2f}ms")
print(f"平均每只: {serial_time/len(symbols):.2f}ms")

# 并发获取
print("\n[并发获取]")
def get_kline(item):
    code, market = item
    start = time.time()
    data = api.get_security_bars(9, market, code, 0, 100)
    elapsed = (time.time() - start) * 1000
    return code, elapsed, len(data) if data else 0

start = time.time()
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(get_kline, symbols))
concurrent_time = (time.time() - start) * 1000

for code, elapsed, count in results:
    print(f"  {code}: {elapsed:.2f}ms ({count}条)")
print(f"总耗时: {concurrent_time:.2f}ms")
print(f"加速比: {serial_time/concurrent_time:.2f}x")

api.disconnect()
