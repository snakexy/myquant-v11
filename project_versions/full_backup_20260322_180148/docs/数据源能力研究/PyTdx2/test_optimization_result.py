import sys
sys.path.insert(0, 'backend')

import time
from data.adapters.pytdx_adapter import PyTdxAdapter

print("="*80)
print("PyTdx2 动态服务器选速优化验证")
print("="*80)

symbols = ['600000', '000001', '600036', '000002', '600519'] * 20  # 100只

# 1. 测试配置文件模式
print("\n[1] 配置文件模式")
adapter1 = PyTdxAdapter(auto_select_speed=False)
start = time.time()
quotes1 = adapter1.get_realtime_quote(symbols)
time1 = (time.time() - start) * 1000
print(f"耗时: {time1:.2f}ms, 成功: {len(quotes1)}只")
print(f"服务器: {adapter1.host}:{adapter1.port}")

# 2. 测试动态选速模式
print("\n[2] 动态选速模式")
adapter2 = PyTdxAdapter(auto_select_speed=True)
start = time.time()
quotes2 = adapter2.get_realtime_quote(symbols)
time2 = (time.time() - start) * 1000
print(f"耗时: {time2:.2f}ms, 成功: {len(quotes2)}只")
print(f"服务器: {adapter2.host}:{adapter2.port}")

print("\n" + "="*80)
print("优化效果:")
if time1 > 0 and time2 > 0:
    speedup = time1 / time2
    print(f"速度提升: {speedup:.2f}x")
    print(f"时间减少: {time1 - time2:.2f}ms")
else:
    print("无法计算提升效果")
