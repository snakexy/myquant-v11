# -*- coding: utf-8 -*-
"""
测试分钟线下载的正确方式

参考日K线的成功经验：
1. download_history_data() 使用字符串格式 '20240101'
2. get_market_data_ex() 可能也用字符串格式？
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime, timedelta

symbol = '600519.SH'

print("="*80)
print("分钟线下载方式测试 - 使用正确参数格式")
print("="*80)
print("股票: %s" % symbol)
print()

# 计算时间范围
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

start_str = start_date.strftime('%Y%m%d')
end_str = end_date.strftime('%Y%m%d')

print("时间范围: %s 到 %s" % (start_str, end_str))
print()

# ===== 测试1: 下载5分钟K线（字符串参数）=====
print("[测试1] 下载5分钟K线（使用字符串参数）")
print("-"*80)
try:
    start = time.time()
    result = xtdata.download_history_data(
        stock_code=symbol,
        period='5m',
        start_time=start_str,  # 字符串格式
        end_time=end_str       # 字符串格式
    )
    elapsed = time.time() - start

    print("[OK] 下载完成！耗时: %.2f秒" % elapsed)
    print("     返回: %s" % str(result))

except Exception as e:
    print("[ERROR] %s" % str(e))
    import traceback
    traceback.print_exc()

print()

# ===== 测试2: 读取（测试不同参数格式）=====
print("[测试2] 读取5分钟K线 - 测试不同参数格式")
print("-"*80)

# 格式1: 整数 + count=0
print("格式1: start_time=int, end_time=int, count=0")
try:
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time=int(start_str),
        end_time=int(end_str),
        count=0,
        dividend_type='none'
    )
    if data and symbol in data:
        print("  -> 获取 %d 条" % len(data[symbol]))
    else:
        print("  -> 无数据")
except Exception as e:
    print("  -> 错误: %s" % str(e))

# 格式2: 字符串 + count=0
print("格式2: start_time=str, end_time=str, count=0")
try:
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time=start_str,  # 字符串
        end_time=end_str,      # 字符串
        count=0,
        dividend_type='none'
    )
    if data and symbol in data:
        print("  -> 获取 %d 条" % len(data[symbol]))
    else:
        print("  -> 无数据")
except Exception as e:
    print("  -> 错误: %s" % str(e))

# 格式3: 空字符串 + count
print("格式3: start_time='', end_time='', count=500")
try:
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time='',
        end_time='',
        count=500,
        dividend_type='none',
        fill_data=True
    )
    if data and symbol in data:
        print("  -> 获取 %d 条" % len(data[symbol]))
    else:
        print("  -> 无数据")
except Exception as e:
    print("  -> 错误: %s" % str(e))

print()

# ===== 测试3: 对比日K线（确认下载方式有效）=====
print("[测试3] 对比日K线下载（验证下载方式本身有效）")
print("-"*80)

try:
    # 下载日K线
    xtdata.download_history_data(
        stock_code=symbol,
        period='1d',
        start_time=start_str,
        end_time=end_str
    )

    # 读取日K线
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        start_time=int(start_str),
        end_time=int(end_str),
        count=0,
        dividend_type='none'
    )

    if data and symbol in data:
        print("[OK] 日K线下载有效，获取 %d 条" % len(data[symbol]))
    else:
        print("[FAIL] 日K线下载也失败")

except Exception as e:
    print("[ERROR] %s" % str(e))

print()
print("="*80)
print("结论:")
print("- 确认分钟线是否支持下载+读取")
print("- 找出正确的参数格式")
print("- 对比日K线和分钟线的区别")
print("="*80)
