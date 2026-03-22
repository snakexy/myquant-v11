# -*- coding: utf-8 -*-
"""
分钟线限制全面测试

对比：
1. 在线获取（count方式）的限制
2. 下载+读取（时间范围方式）的限制
3. 验证是否存在16天限制
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime, timedelta

symbol = '600519.SH'

print("="*80)
print("分钟线限制全面测试")
print("="*80)
print("股票: %s" % symbol)
print()

# ===== 理论计算 =====
print("理论计算:")
print("  16天 = 16 * 4小时 * 60分钟 = 3840条 (1分钟K线)")
print("  16天 = 16 * 4小时 * 12条/小时 = 768条 (5分钟K线)")
print()

# ===== 测试1: 在线获取 - 大count值 =====
print("[测试1] 在线获取 - 测试大count值（验证16天限制）")
print("-"*80)

xtdata.subscribe_quote(symbol, period='5m', count=0)

# 测试不同count值
test_counts = [
    120,    # 2.5天
    240,    # 5天
    480,    # 10天
    768,    # 16天（理论限制）
    1000,   # 超过16天
    1500,   # 远超16天
    2000,   # 更远超
]

for count in test_counts:
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
            actual = len(df)
            time_span_days = actual * 5 / 60 / 24  # 转换为天数

            status = "OK" if actual == count else "LIMIT"

            print("请求%4d条: 实际%4d条, %.2f天, [%s], %.2fms" %
                  (count, actual, time_span_days, status, elapsed))

            if actual < count and actual == 678:  # 发现上限
                print("  -> 达到上限: %d条 = %.2f天" % (actual, time_span_days))
                break
        else:
            print("请求%4d条: 无数据" % count)
            break

    except Exception as e:
        print("请求%4d条: 错误 - %s" % (count, str(e)))
        break

print()

# ===== 测试2: 下载+读取 - 不同天数 =====
print("[测试2] 下载+读取 - 测试不同天数")
print("-"*80)

test_days = [7, 10, 16, 20, 30]

for days in test_days:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')

    try:
        # 先下载
        download_start = time.time()
        xtdata.download_history_data(
            stock_code=symbol,
            period='5m',
            start_time=start_str,
            end_time=end_str
        )
        download_time = (time.time() - download_start) * 1000

        # 再读取
        read_start = time.time()
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period='5m',
            start_time=start_str,
            end_time=end_str,
            count=0,
            dividend_type='none'
        )
        read_time = (time.time() - read_start) * 1000

        if data and symbol in data:
            df = data[symbol]
            actual = len(df)
            time_span_days = actual * 5 / 60 / 24

            print("请求%2d天: 实际%4d条, %.2f天, 下载%.2fms, 读取%.2fms" %
                  (days, actual, time_span_days, download_time, read_time))
        else:
            print("请求%2d天: 无数据" % days)

    except Exception as e:
        print("请求%2d天: 错误 - %s" % (days, str(e)))

print()

# ===== 测试3: 混合方式 - 先下载历史，再在线获取 =====
print("[测试3] 混合方式 - 验证是否可以突破限制")
print("-"*80)

# 1. 先下载30天数据
print("步骤1: 下载30天历史数据...")
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

try:
    xtdata.download_history_data(
        stock_code=symbol,
        period='5m',
        start_time=start_date.strftime('%Y%m%d'),
        end_time=end_date.strftime('%Y%m%d')
    )
    print("  -> 下载完成")
except Exception as e:
    print("  -> 下载失败: %s" % str(e))

# 2. 尝试在线获取（看是否能利用本地数据）
print("步骤2: 在线获取count=2000（看是否能读取本地数据）")
try:
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time='',
        end_time='',
        count=2000,
        dividend_type='none',
        fill_data=True
    )

    if data and symbol in data:
        df = data[symbol]
        print("  -> 获取 %d 条" % len(df))
        if len(df) > 678:
            print("  -> 成功突破2-3天限制！")
        else:
            print("  -> 仍然限制在 %d 条" % len(df))
    else:
        print("  -> 无数据")
except Exception as e:
    print("  -> 错误: %s" % str(e))

print()

# ===== 测试4: 使用具体时间范围对比 =====
print("[测试4] 使用具体时间范围（start_time/end_time）在线获取")
print("-"*80)

# 测试1: 7天
end_date = datetime.now()
start_date_7d = end_date - timedelta(days=7)

try:
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time=start_date_7d.strftime('%Y%m%d'),  # 字符串格式
        end_time=end_date.strftime('%Y%m%d'),
        count=0,
        dividend_type='none'
    )

    if data and symbol in data:
        df = data[symbol]
        print("在线获取7天: %d条" % len(df))
    else:
        print("在线获取7天: 无数据")
except Exception as e:
    print("在线获取7天: 错误 - %s" % str(e))

# 测试2: 16天
start_date_16d = end_date - timedelta(days=16)

try:
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time=start_date_16d.strftime('%Y%m%d'),
        end_time=end_date.strftime('%Y%m%d'),
        count=0,
        dividend_type='none'
    )

    if data and symbol in data:
        df = data[symbol]
        print("在线获取16天: %d条" % len(df))
    else:
        print("在线获取16天: 无数据")
except Exception as e:
    print("在线获取16天: 错误 - %s" % str(e))

print()
print("="*80)
print("总结:")
print("- 在线获取count方式的实际限制")
print("- 下载+读取方式的实际限制")
print("- 是否真的存在16天限制")
print("- count方式和时间范围方式的区别")
print("="*80)
