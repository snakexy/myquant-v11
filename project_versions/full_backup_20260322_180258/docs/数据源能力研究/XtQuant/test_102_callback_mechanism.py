# -*- coding: utf-8 -*-
"""
测试1: 订阅推送回调机制

目标：
1. 验证register_callback能否正常注册
2. 验证交易时间能收到推送
3. 验证推送数据格式
4. 验证推送频率
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime

print("="*80)
print("测试: 订阅推送回调机制")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 全局变量存储推送数据
push_data_list = []

def on_tick_push(data):
    """Tick数据推送回调"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[推送回调] {timestamp} 收到推送")
    print(f"         数据类型: {type(data)}")

    # 保存到列表
    global push_data_list
    push_data_list.append({
        'timestamp': timestamp,
        'data': data
    })

    # 打印数据内容（前几个股票）
    if isinstance(data, dict):
        for i, (symbol, quote) in enumerate(list(data.items())[:3]):
            print(f"         股票{i+1}: {symbol}")
            if isinstance(quote, dict):
                print(f"           lastPrice: {quote.get('lastPrice')}")
                print(f"           volume: {quote.get('volume')}")
            else:
                print(f"           数据: {quote}")
    else:
        print(f"         原始数据: {data}")
    print()

# ===== 测试1: 注册回调 =====
print("[测试1] 注册订阅回调")
print("-"*80)

try:
    # 注册回调
    xtdata.register_callback(on_tick_push)
    print("[OK] 回调函数已注册")
except Exception as e:
    print(f"[ERROR] 注册回调失败: {e}")
    import traceback
    traceback.print_exc()
    print()

print()

# ===== 测试2: 订阅tick数据 =====
print("[测试2] 订阅tick数据")
print("-"*80)

symbol = '600519.SH'
try:
    xtdata.subscribe_quote(symbol, period='tick', count=0)
    print(f"[OK] 已订阅 {symbol} tick数据")
except Exception as e:
    print(f"[ERROR] 订阅失败: {e}")

print()

# ===== 测试3: 等待推送（交易时间）=====
print("[测试3] 等待推送数据（30秒）")
print("-"*80)
print("说明: 如果当前是交易时间，应该能收到推送")
print("      如果当前是非交易时间，可能收不到推送")
print()

print("开始监听...")
timeout_seconds = 30
start_time = time.time()

push_count = 0
while (time.time() - start_time) < timeout_seconds:
    time.sleep(1)

    # 检查是否有新推送
    current_count = len(push_data_list)
    if current_count > push_count:
        push_count = current_count
        print(f"[收到推送] 总共收到 {push_count} 次推送")

    # 每5秒显示一次状态
    elapsed = int(time.time() - start_time)
    if elapsed % 5 == 0 and elapsed > 0:
        print(f"[等待中] 已等待 {elapsed} 秒，收到 {push_count} 次推送")

print()
print(f"[完成] 等待结束，共收到 {push_count} 次推送")

# ===== 测试4: 分析推送数据 =====
print("[测试4] 分析推送数据格式")
print("-"*80)

if push_data_list:
    print(f"总共收到: {len(push_data_list)} 次推送")
    print()

    # 分析第一次推送
    first_push = push_data_list[0]
    print("第一次推送数据:")
    print(f"  时间戳: {first_push['timestamp']}")
    print(f"  数据类型: {type(first_push['data'])}")

    if isinstance(first_push['data'], dict):
        print("  数据字段:")
        data = first_push['data']
        if symbol in data:
            quote = data[symbol]
            print(f"    {symbol} 字段:")
            for key, value in quote.items():
                print(f"      {key}: {value}")
else:
    print("未收到任何推送数据")
    print("可能原因:")
    print("  1. 当前是非交易时间")
    print("  2. 回调注册方式不对")
    print("  3. 订阅参数不对")

print()

# ===== 测试5: 验证订阅5分钟数据 =====
print("[测试5] 订阅5分钟K线（对比）")
print("-"*80)

print("说明: 对比tick推送和5分钟K线获取")
print()

# 订阅5分钟K线
try:
    xtdata.subscribe_quote(symbol, period='5m', count=0)
    print(f"[OK] 已订阅 {symbol} 5分钟K线")
except Exception as e:
    print(f"[ERROR] 订阅失败: {e}")

# 等待一下
time.sleep(2)

# 获取5分钟K线
try:
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time='',
        end_time='',
        count=10,
        dividend_type='none'
    )

    if data and symbol in data:
        df = data[symbol]
        print(f"[5分钟K线] 获取 {len(df)} 条数据")
        print(f"           最新: {df.index[-1]}")
    else:
        print("[5分钟K线] 无数据")

except Exception as e:
    print(f"[ERROR] 获取5分钟K线失败: {e}")

print()
print("="*80)
print("结论:")
print("- 观察是否收到tick推送")
print("- 如果有推送，说明回调机制有效")
print("- 对比tick推送和5分钟K线的区别")
print("="*80)
