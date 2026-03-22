import time
from pytdx2.hq import TdxHq_API

servers = [
    ('180.153.18.170', 80),
    ('114.80.63.12', 7709),
    ('60.12.136.250', 7709),
]

print("="*80)
print("PyTdx2 服务器可用性测试")
print("="*80)

for host, port in servers:
    print(f"\n[{host}:{port}]")
    try:
        api = TdxHq_API()
        if api.connect(host, port):
            start = time.time()
            quotes = api.get_security_quotes([(1, '600000')])
            elapsed = (time.time() - start) * 1000
            if quotes and len(quotes) > 0:
                print(f"  耗时: {elapsed:.2f}ms")
                print(f"  返回: {len(quotes)}条")
                print(f"  价格: {quotes[0].get('price', 'N/A')}")
                print(f"  状态: 可用")
            else:
                print(f"  耗时: {elapsed:.2f}ms")
                print(f"  返回: 0条")
                print(f"  状态: 不可用")
        else:
            print(f"  状态: 连接失败")
        api.disconnect()
    except Exception as e:
        print(f"  错误: {e}")
