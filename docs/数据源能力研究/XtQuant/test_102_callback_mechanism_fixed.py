# -*- coding: utf-8 -*-
"""
测试1修正: 订阅推送回调机制（正确版本）

目标：
1. 验证subscribe_quote()的callback参数
2. 验证xtdata.run()的阻塞作用
3. 验证交易时间能收到推送
4. 验证推送数据格式
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime

print("="*80)
print("测试: 订阅推送回调机制（修正版）")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 全局变量
push_count = 0
push_data_list = []

def on_tick_push(data):
    """Tick数据推送回调"""
    global push_count, push_data_list

    push_count += 1
    timestamp = datetime.now().strftime('%H:%M:%S')

    print(f"[推送 #{push_count}] {timestamp}")
    print(f"  数据类型: {type(data)}")
    print(f"  数据内容: {data}")

    # 保存数据
    push_data_list.append({
        'timestamp': timestamp,
        'data': data
    })

print("="*80)
print("准备开始测试")
print("="*80)
print()

# ===== 测试1: 订阅tick数据（带callback） =====
print("[测试1] 订阅tick数据（带callback）")
print("-"*80)

symbol = '600519.SH'

try:
    print(f"订阅股票: {symbol}")
    print(f"周期: tick")
    print()

    xtdata.subscribe_quote(
        stock_code=symbol,  # ⭐ 正确参数名
        period='tick',
        count=-1,
        callback=on_tick_push
    )

    print("[OK] 订阅成功，已设置回调函数")
    print()
    print("说明: 订阅后需要调用 xtdata.run() 来接收推送")
    print("      run() 会阻塞当前线程，持续接收推送")
    print()

except Exception as e:
    print(f"[ERROR] 订阅失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ===== 测试2: 短时间接收推送 =====
print("[测试2] 短时间接收推送（30秒）")
print("-"*80)
print("说明: 调用xtdata.run()阻塞线程30秒")
print("      如果是交易时间，应该能收到推送")
print("      如果是非交易时间，可能收不到推送")
print()

# 保存原始的run_time参数（如果有）
import threading

def run_with_timeout(timeout_seconds=30):
    """在独立线程中run，避免永久阻塞"""

    def run_thread():
        try:
            print("[run] 开始阻塞等待推送...")
            print(f"[run] 将等待 {timeout_seconds} 秒或直到用户手动停止")
            print()

            # 这个调用会阻塞
            # 在实际使用中，应该一直在后台运行
            # 这里为了测试，我们在独立线程中运行
            xtdata.run()

        except Exception as e:
            print(f"[run] 异常: {e}")

    thread = threading.Thread(target=run_thread, daemon=True)
    thread.start()

    # 等待指定时间
    print(f"[主线程] 等待 {timeout_seconds} 秒...")

    for i in range(timeout_seconds):
        time.sleep(1)

        # 每5秒显示一次状态
        if (i + 1) % 5 == 0:
            print(f"[主线程] 已等待 {i + 1} 秒，收到 {push_count} 次推送")

    print()
    print(f"[主线程] 等待结束")
    print(f"[主线程] 总共收到 {push_count} 次推送")

# 执行测试
try:
    run_with_timeout(timeout_seconds=30)
except KeyboardInterrupt:
    print("\n[用户中断] 测试已停止")
except Exception as e:
    print(f"\n[ERROR] 测试异常: {e}")

print()

# ===== 测试3: 分析推送数据 =====
print("[测试3] 分析推送数据格式")
print("-"*80)

if push_data_list:
    print(f"总共收到: {len(push_data_list)} 次推送")
    print()

    if len(push_data_list) > 0:
        first_push = push_data_list[0]
        print("第一次推送数据:")
        print(f"  时间戳: {first_push['timestamp']}")
        print(f"  数据类型: {type(first_push['data'])}")
        print(f"  数据内容: {first_push['data']}")

        # 分析数据格式
        data = first_push['data']
        if isinstance(data, dict):
            print("  数据是字典格式，包含以下字段:")
            for key, value in data.items():
                print(f"    {key}: {value}")

        elif isinstance(data, list):
            print(f"  数据是列表格式，包含 {len(data)} 个元素")
            if len(data) > 0:
                print(f"  第一个元素类型: {type(data[0])}")
                print(f"  第一个元素: {data[0]}")

        else:
            print(f"  数据类型: {type(data)}")
else:
    print("[结果] 未收到任何推送数据")
    print()
    print("可能原因:")
    print("  1. 当前是非交易时间（周末、节假日、收盘后）")
    print("  2. 股票停牌")
    print("  3. 网络连接问题")
    print()
    print("建议:")
    print("  - 在交易时间（周一至周五 9:30-15:00）测试")
    print("  - 确保QMT客户端已登录")
    print("  - 确保网络连接正常")

print()
print("="*80)
print("结论:")
print("="*80)

if push_count > 0:
    print("✅ 订阅推送功能正常工作")
    print(f"   在30秒内收到 {push_count} 次推送")
    print("   推送频率约: {:.1f}秒/次".format(30 / push_count))
    print()
    print("可以用于:")
    print("  - 实时分时图（tick数据实时聚合）")
    print("  - 实时行情监控")
    print("  - 异常检测（突然拉涨、放量等）")
else:
    print("⚠️ 未收到推送数据")
    print()
    print("原因分析:")
    print("  1. 当前是非交易时间（最可能）")
    print("  2. 需要调用 xtdata.run() 阻塞线程")
    print()
    print("使用建议:")
    print("  - 在交易时间测试")
    print("  - 在独立线程中调用 xtdata.run()")
    print("  - 或者使用轮询模式：get_full_tick() 每3秒")

print()
print(f"测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
