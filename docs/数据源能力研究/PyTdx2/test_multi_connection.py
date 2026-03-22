import time
from pytdx2.hq import TdxHq_API
from concurrent.futures import ThreadPoolExecutor
import threading

# 线程安全的API连接池
class APIPool:
    def __init__(self, host, port, size=3):
        self.host = host
        self.port = port
        self.size = size
        self.pool = []
        self.lock = threading.Lock()
        
    def get_api(self):
        with self.lock:
            if not self.pool:
                api = TdxHq_API()
                api.connect(self.host, self.port)
                return api
            return self.pool.pop()
    
    def return_api(self, api):
        with self.lock:
            self.pool.append(api)

pool = APIPool('180.153.18.170', 80, size=3)

symbols = [(1, '600000'), (0, '000001'), (1, '600036'), (0, '000002'), (1, '600519')]

print("="*80)
print("PyTdx2 多连接池测试")
print("="*80)

# 串行
print("\n[串行获取]")
start = time.time()
api = pool.get_api()
for code, market in symbols:
    quotes = api.get_security_quotes([(market, code)])
pool.return_api(api)
serial_time = (time.time() - start) * 1000
print(f"耗时: {serial_time:.2f}ms")

# 并发多连接
print("\n[并发多连接]")
def get_quote(item):
    api = pool.get_api()
    start = time.time()
    quotes = api.get_security_quotes([item])
    elapsed = (time.time() - start) * 1000
    pool.return_api(api)
    return elapsed, len(quotes) if quotes else 0

start = time.time()
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(get_quote, symbols))
concurrent_time = (time.time() - start) * 1000

for elapsed, count in results:
    print(f"  股票: {elapsed:.2f}ms ({count}条)")
print(f"总耗时: {concurrent_time:.2f}ms")
print(f"加速比: {serial_time/concurrent_time:.2f}x")
