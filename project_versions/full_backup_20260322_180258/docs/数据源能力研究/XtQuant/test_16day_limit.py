# -*- coding: utf-8 -*-
"""
16天限制测试

测试目标：
1. 验证分钟线数据是否存在16天限制
2. 测试不同count值的实际获取情况
3. 找出最大可获取条数

计算：
- 1天 = 4小时交易时间 * 60分钟 = 240分钟
- 16天 = 16 * 240 = 3840分钟（1分钟K线）
- 16天 = 16 * 48 = 768条（5分钟K线，因为4小时*12条/小时）
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time

symbol = '600519.SH'

print("="*80)
print("分钟线16天限制测试")
print("="*80)
print("股票: %s" % symbol)
print()

print("理论计算:")
print("  1天交易时间: 4小时 = 240分钟")
print("  1分钟K线: 16天 = 3840条")
print("  5分钟K线: 16天 = 768条 (4小时*12条/小时*16天)")
print()

# ===== 测试1: 1分钟K线 - 不同count值 =====
print("[测试1] 1分钟K线 - 测试不同count值")
print("-"*80)

xtdata.subscribe_quote(symbol, period='1m', count=0)

test_counts_1m = [60, 120, 240, 480, 960, 1920, 3840, 5000]

for count in test_counts_1m:
    try:
        start = time.time()
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period='1m',
            start_time='',
            end_time='',
            count=count,
            dividend_type='none',
            fill_data=True
        )
        elapsed = (time.time() - start) * 1000

        if data and symbol in data:
            df = data[symbol]
            actual_count = len(df)
            time_span = actual_count / 60.0  # 小时

            print("请求%4d条: 实际%4d条, 耗时%6.2fms, 时间跨度%.1f小时" %
                  (count, actual_count, elapsed, time_span))

            if actual_count < count:
                print("  -> 警告: 实际获取少于请求，可能存在限制")
                break
        else:
            print("请求%4d条: 无数据" % count)
            break

    except Exception as e:
        print("请求%4d条: 错误 - %s" % (count, str(e)))
        break

print()

# ===== 测试2: 5分钟K线 - 不同count值 =====
print("[测试2] 5分钟K线 - 测试不同count值")
print("-"*80)

xtdata.subscribe_quote(symbol, period='5m', count=0)

test_counts_5m = [48, 120, 240, 480, 768, 1000, 1500, 2000]

for count in test_counts_5m:
    try:
        start = time.time()
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period='5m',
            start_time='',
            end_time='',
            count=count,
            dividend_type='none',
            fill_data=True
        )
        elapsed = (time.time() - start) * 1000

        if data and symbol in data:
            df = data[symbol]
            actual_count = len(df)
            time_span = actual_count * 5 / 60.0  # 小时

            print("请求%4d条: 实际%4d条, 耗时%6.2fms, 时间跨度%.1f小时" %
                  (count, actual_count, elapsed, time_span))

            if actual_count < count:
                print("  -> 警告: 实际获取少于请求，可能存在限制")
                # 继续测试，看看是否是上限
        else:
            print("请求%4d条: 无数据" % count)
            break

    except Exception as e:
        print("请求%4d条: 错误 - %s" % (count, str(e)))
        break

print()

# ===== 测试3: 使用时间范围代替count =====
print("[测试3] 使用时间范围获取（对比）")
print("-"*80)

# 获取最近20天
from datetime import datetime, timedelta

end_date = datetime.now()
start_date_20d = end_date - timedelta(days=20)
start_date_30d = end_date - timedelta(days=30)

for days in [7, 10, 16, 20, 30]:
    start_date = end_date - timedelta(days=days)

    try:
        # 先下载
        xtdata.download_history_data(
            stock_code=symbol,
            period='5m',
            start_time=start_date.strftime('%Y%m%d'),
            end_time=end_date.strftime('%Y%m%d')
        )

        # 再读取
        start = time.time()
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period='5m',
            start_time=int(start_date.strftime('%Y%m%d')),
            end_time=int(end_date.strftime('%Y%m%d')),
            count=0,
            dividend_type='none'
        )
        elapsed = (time.time() - start) * 1000

        if data and symbol in data:
            df = data[symbol]
            actual_count = len(df)
            time_span_hours = actual_count * 5 / 60.0

            print("请求%2d天: 实际%4d条, 耗时%6.2fms, 时间跨度%.1f小时(%.1f天)" %
                  (days, actual_count, elapsed, time_span_hours, time_span_hours/24))
        else:
            print("请求%2d天: 无数据" % days)

    except Exception as e:
        print("请求%2d天: 错误 - %s" % (days, str(e)))

print()
print("="*80)
print("结论:")
print("- 观察是否存在16天限制")
print("- 观察count和时间范围的关系")
print("- 对比在线获取 vs 下载+读取")
print("="*80)
