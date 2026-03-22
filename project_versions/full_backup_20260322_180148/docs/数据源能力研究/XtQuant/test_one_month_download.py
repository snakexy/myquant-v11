# -*- coding: utf-8 -*-
"""
测试下载一个月的分钟线数据
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime, timedelta

symbol = '600519.SH'

print("="*80)
print("下载一个月分钟线数据测试")
print("="*80)
print("股票: %s" % symbol)
print()

# 测试1: 下载2024年1月（完整月）
print("[测试1] 下载2024年1月完整数据")
print("-"*80)

start_date = '20240101'
end_date = '20240131'

print("时间范围: %s 到 %s" % (start_date, end_date))
print()

# 下载
start = time.time()
result = xtdata.download_history_data(
    stock_code=symbol,
    period='5m',
    start_time=start_date,
    end_time=end_date
)
download_time = time.time() - start

print("[下载] 完成！耗时: %.2f秒" % download_time)

# 读取
start = time.time()
data = xtdata.get_market_data_ex(
    field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=[symbol],
    period='5m',
    start_time=start_date,
    end_time=end_date,
    count=0,
    dividend_type='none'
)
read_time = (time.time() - start) * 1000

if data and symbol in data:
    df = data[symbol]
    count = len(df)
    time_span_days = count * 5 / 60 / 24
    time_span_hours = count * 5 / 60

    print("[读取] 成功！")
    print("       数据条数: %d" % count)
    print("       时间跨度: %.2f小时 (%.2f天)" % (time_span_hours, time_span_days))
    print("       读取耗时: %.2fms" % read_time)
    print("       最早: %s" % str(df.index[0]))
    print("       最晚: %s" % str(df.index[-1]))
    print()

    # 计算理论值
    print("理论计算:")
    print("  1个月约22个交易日")
    print("  每天交易4小时")
    print("  5分钟K线: 22 * 4 * 12 = %d条" % (22 * 4 * 12))
    print()

print()

# 测试2: 下载最近一个月（自然日）
print("[测试2] 下载最近一个月（自然日）")
print("-"*80)

end_date = datetime.now()
start_date = end_date - timedelta(days=30)

start_str = start_date.strftime('%Y%m%d')
end_str = end_date.strftime('%Y%m%d')

print("时间范围: %s 到 %s" % (start_str, end_str))
print()

# 下载
start = time.time()
result = xtdata.download_history_data(
    stock_code=symbol,
    period='5m',
    start_time=start_str,
    end_time=end_str
)
download_time = time.time() - start

print("[下载] 完成！耗时: %.2f秒" % download_time)

# 读取
start = time.time()
data = xtdata.get_market_data_ex(
    field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=[symbol],
    period='5m',
    start_time=start_str,
    end_time=end_str,
    count=0,
    dividend_type='none'
)
read_time = (time.time() - start) * 1000

if data and symbol in data:
    df = data[symbol]
    count = len(df)
    time_span_days = count * 5 / 60 / 24

    print("[读取] 成功！")
    print("       数据条数: %d" % count)
    print("       时间跨度: %.2f天" % time_span_days)
    print("       读取耗时: %.2fms" % read_time)
    print("       最早: %s" % str(df.index[0]))
    print("       最晚: %s" % str(df.index[-1]))
    print()

print()
print("="*80)
print("对比:")
print("- 完整月（20240101-0131）vs 最近30天（自然日）")
print("- 理论值vs实际值")
print("="*80)
