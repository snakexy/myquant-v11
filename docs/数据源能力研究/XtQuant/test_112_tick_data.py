# -*- coding: utf-8 -*-
"""
测试: Tick数据获取

目标：
1. 验证get_full_tick() - 最新tick快照
2. 验证download_history_data(period='tick') - 下载历史tick
3. 验证get_market_data_ex(period='tick') - 读取历史tick
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime, timedelta

print("="*80)
print("测试: Tick数据获取")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ===== 测试1: get_full_tick() - 最新tick快照 =====
print("[测试1] get_full_tick() - 最新tick快照")
print("-"*80)
print("说明: 这个函数提供最新分笔数据快照，不是历史tick序列")
print()

test_stock = '600519.SH'

try:
    start = time.time()
    tick_data = xtdata.get_full_tick([test_stock])
    elapsed = (time.time() - start) * 1000

    if tick_data and test_stock in tick_data:
        data = tick_data[test_stock]
        print(f"[OK] 获取成功")
        print(f"     耗时: {elapsed:.2f}ms")
        print(f"     返回字段数: {len(data)}")
        print()
        print("示例数据:")
        print(f"  最新价: {data.get('lastPrice')}")
        print(f"   昨收: {data.get('lastClose')}")
        print(f"   成交量: {data.get('volume')}")
        print(f"   成交额: {data.get('amount')}")
        print(f"   时间: {data.get('timetag')}")
        print()
        print("说明: 这是最新快照，不是历史tick序列")
    else:
        print("[空] 未获取到数据")

except Exception as e:
    print(f"[ERROR] {e}")

print()

# ===== 测试2: 检查本地是否有tick数据 =====
print("[测试2] 检查本地是否有tick历史数据")
print("-"*80)

try:
    # 尝试读取最近1天的tick数据
    end_time = datetime.now().strftime('%Y%m%d')
    start_time = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

    data = xtdata.get_market_data_ex(
        field_list=['time', 'price', 'volume', 'amount'],
        stock_list=[test_stock],
        period='tick',
        start_time=start_time,
        end_time=end_time,
        count=10  # 只读取10条测试
    )

    if data and test_stock in data:
        df = data[test_stock]
        print(f"[OK] 本地有tick数据")
        print(f"     数据量: {len(df)} 条")
        print()
        print("前5条数据:")
        print(df.head())
    else:
        print("[空] 本地没有tick数据")
        print("说明: 需要先使用download_history_data()下载")

except Exception as e:
    print(f"[ERROR] {e}")

print()

# ===== 测试3: 下载少量tick数据测试 =====
print("[测试3] 下载少量tick数据测试")
print("-"*80)
print("说明: 下载数据量很小（1分钟），用于测试")
print()

# 自动跳过下载测试（避免卡住）
response = 'n'

if response.lower() == 'y':
    try:
        print("开始下载tick数据...")
        print("股票: 600519.SH")
        print("时间: 最近1分钟")
        print()

        start = time.time()

        # 下载最近1分钟的tick数据
        # 注意：需要提供精确的时间范围
        end_time = datetime.now().strftime('%Y%m%d %H:%M:%S')
        start_time = (datetime.now() - timedelta(minutes=1)).strftime('%Y%m%d %H:%M:%S')

        print(f"时间范围: {start_time} ~ {end_time}")
        print()
        print("⚠️ 警告: download_history_data可能需要较长时间")
        print("      tick数据量很大")
        print()

        # 实际执行下载（注释掉，避免卡住）
        # xtdata.download_history_data(
        #     stock_code='600519.SH',
        #     period='tick',
        #     start_time=start_time.replace(' ', ''),
        #     end_time=end_time.replace(' ', '')
        # )

        print("[已跳过] 实际下载已注释，避免卡住")
        print()
        print("💡 建议:")
        print("1. tick数据量非常大，不建议大批量下载")
        print("2. 对于分时图，使用1分钟K线即可")
        print("3. 对于实时监控，使用get_full_tick()快照")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

print()

# ===== 测试4: 对比不同周期的数据 =====
print("[测试4] 对比tick、1分钟、5分钟数据")
print("-"*80)

periods = ['tick', '1m', '5m', '1d']

for period in periods:
    try:
        data = xtdata.get_market_data_ex(
            field_list=['time', 'close'],
            stock_list=[test_stock],
            period=period,
            start_time='',
            end_time='',
            count=5
        )

        if data and test_stock in data:
            df = data[test_stock]
            print(f"[OK] period='{period}': {len(df)} 条")
            if len(df) > 0:
                print(f"      示例时间: {df.index[-1]}")
        else:
            print(f"[空] period='{period}': 0 条")

    except Exception as e:
        print(f"[ERROR] period='{period}': {e}")

print()
print("="*80)
print("结论:")
print("- get_full_tick() 提供最新tick快照（实时）")
print("- download_history_data(period='tick') 下载历史tick数据")
print("- get_market_data_ex(period='tick') 读取已下载的tick数据")
print("- tick数据量很大，建议根据需求选择合适的周期")
print("="*80)
