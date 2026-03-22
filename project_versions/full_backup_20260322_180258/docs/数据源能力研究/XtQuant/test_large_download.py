# -*- coding: utf-8 -*-
"""
测试大范围下载分钟线数据

目标：
1. 下载大时间范围（如1年）
2. 等待下载完成
3. 检查实际下载了多少数据
4. 验证是否能突破3.8天限制
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime, timedelta

symbol = '600519.SH'

print("="*80)
print("大范围分钟线下载测试")
print("="*80)
print("股票: %s" % symbol)
print()

# ===== 测试1: 下载1年数据 =====
print("[测试1] 下载2024全年5分钟K线数据")
print("-"*80)

start_date_2024 = '20240101'
end_date_2024 = '20241231'

print("开始下载: %s 到 %s" % (start_date_2024, end_date_2024))
print("这可能需要一些时间...")
print()

start_time = time.time()
try:
    result = xtdata.download_history_data(
        stock_code=symbol,
        period='5m',
        start_time=start_date_2024,
        end_time=end_date_2024
    )
    elapsed = time.time() - start_time

    print("[下载] 完成！耗时: %.2f秒" % elapsed)
    print("       返回: %s" % str(result))
    print()

except Exception as e:
    print("[ERROR] 下载失败: %s" % str(e))
    import traceback
    traceback.print_exc()
    print()

# 等待一下，确保数据写入
time.sleep(1)

# 尝试读取
print("[读取] 尝试读取下载的数据...")
try:
    read_start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time=start_date_2024,
        end_time=end_date_2024,
        count=0,
        dividend_type='none'
    )
    read_elapsed = (time.time() - read_start) * 1000

    if data and symbol in data:
        df = data[symbol]
        actual_count = len(df)

        if actual_count > 0:
            time_span_days = actual_count * 5 / 60 / 24
            first_date = df.index[0]
            last_date = df.index[-1]

            print("       成功！")
            print("       数据条数: %d" % actual_count)
            print("       时间跨度: %.2f天" % time_span_days)
            print("       最早时间: %s" % str(first_date))
            print("       最晚时间: %s" % str(last_date))
            print("       读取耗时: %.2fms" % read_elapsed)

            if time_span_days > 10:
                print("\n       *** 成功突破限制！***")
            else:
                print("\n       *** 仍然限制在%.2f天 ***" % time_span_days)
        else:
            print("       下载成功但读取为空！")
    else:
        print("       读取失败，无数据")

except Exception as e:
    print("       读取出错: %s" % str(e))

print()
print()

# ===== 测试2: 下载更长时间（3年）=====
print("[测试2] 下载2022-2024三年数据")
print("-"*80)

start_date_2022 = '20220101'
end_date_2024 = '20241231'

print("开始下载: %s 到 %s" % (start_date_2022, end_date_2024))
print()

start_time = time.time()
try:
    result = xtdata.download_history_data(
        stock_code=symbol,
        period='5m',
        start_time=start_date_2022,
        end_time=end_date_2024
    )
    elapsed = time.time() - start_time

    print("[下载] 完成！耗时: %.2f秒" % elapsed)
    print("       返回: %s" % str(result))
    print()

except Exception as e:
    print("[ERROR] 下载失败: %s" % str(e))

# 等待一下
time.sleep(1)

# 尝试读取
print("[读取] 尝试读取下载的数据...")
try:
    read_start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time=start_date_2022,
        end_time=end_date_2024,
        count=0,
        dividend_type='none'
    )
    read_elapsed = (time.time() - read_start) * 1000

    if data and symbol in data:
        df = data[symbol]
        actual_count = len(df)

        if actual_count > 0:
            time_span_days = actual_count * 5 / 60 / 24

            print("       成功！")
            print("       数据条数: %d" % actual_count)
            print("       时间跨度: %.2f天 (%.2f年)" % (time_span_days, time_span_days/365))
            print("       最早时间: %s" % str(df.index[0]))
            print("       最晚时间: %s" % str(df.index[-1]))
            print("       读取耗时: %.2fms" % read_elapsed)

            if time_span_days > 100:
                print("\n       *** 确认可以下载大量历史数据！***")
        else:
            print("       读取为空")
    else:
        print("       读取失败")

except Exception as e:
    print("       读取出错: %s" % str(e))

print()
print("="*80)
print("结论:")
print("- 确认是否可以下载大量历史分钟线数据")
print("- 下载速度和数据量关系")
print("- 是否真的突破了3.8天限制")
print("="*80)
