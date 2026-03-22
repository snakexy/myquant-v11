import time
from pytdx2.hq import TdxHq_API
from pytdx2.config.hosts import hq_hosts

print("="*80)
print("PyTdx2 服务器速度对比")
print("="*80)

# 测试前30个服务器
results = []
symbol = (1, '600000')

for i, item in enumerate(hq_hosts[:30]):
    name, host, port = item
    try:
        api = TdxHq_API()
        start = time.time()
        if api.connect(host, port, time_out=3):
            # 测试3次取平均
            times = []
            for _ in range(3):
                t_start = time.time()
                quotes = api.get_security_quotes([symbol])
                if quotes and len(quotes) > 0:
                    times.append((time.time() - t_start) * 1000)
                time.sleep(0.1)  # 避免频繁请求
            
            if times:
                avg_time = sum(times) / len(times)
                results.append((name, host, port, avg_time))
                print(f"{i+1:2d}. {host:15s}:{port} - {avg_time:6.2f}ms")
            else:
                print(f"{i+1:2d}. {host:15s}:{port} - 无数据")
        else:
            print(f"{i+1:2d}. {host:15s}:{port} - 连接失败")
        api.disconnect()
    except Exception as e:
        print(f"{i+1:2d}. {host:15s}:{port} - 错误: {str(e)[:20]}")

print("\n" + "="*80)
if results:
    print("最快服务器TOP5:")
    results.sort(key=lambda x: x[3])
    for name, host, port, avg_time in results[:5]:
        print(f"  {host:15s}:{port} - {avg_time:.2f}ms ({name})")
else:
    print("没有可用的服务器")
