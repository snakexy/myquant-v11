# -*- coding: utf-8 -*-
"""
验证XtQuant支持的period参数格式

目的：确认正确的period参数表示法
"""

from xtquant import xtdata
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

test_symbol = '600519.SH'

# 测试不同的period参数格式
periods_to_test = [
    '1d',      # 日K
    '1w',      # 周K
    '1M',      # 月K
    '1m',      # 1分钟
    '5m',      # 5分钟
    '15m',     # 15分钟
    '30m',     # 30分钟
    '60m',     # 60分钟（可能有问题）
    '1h',      # 1小时（正确写法）
    'tick',    # 分笔
]

print("=" * 80)
print("XtQuant period参数格式验证")
print("=" * 80)
print()

valid_periods = []
invalid_periods = []

for period in periods_to_test:
    print(f"[测试] period='{period}'")

    try:
        # 尝试订阅
        xtdata.subscribe_quote(test_symbol, period=period, count=0)

        # 尝试获取少量数据
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume'],
            stock_list=[test_symbol],
            period=period,
            start_time='',
            end_time='',
            count=10,
            dividend_type='none'
        )

        if data and test_symbol in data:
            count = len(data[test_symbol])
            print(f"  [OK] 成功 - 获取{count}条数据")
            valid_periods.append(period)
        else:
            print(f"  [WARN] 订阅成功但无数据")
            valid_periods.append(period)  # 无数据可能是非交易时间

    except Exception as e:
        error_msg = str(e)
        if 'invalid period' in error_msg.lower():
            print(f"  [ERROR] 无效的period参数")
            invalid_periods.append(period)
        else:
            print(f"  [ERROR] {error_msg[:50]}")
            invalid_periods.append(period)

    print()

print("=" * 80)
print("测试结果汇总")
print("=" * 80)
print()

print(f"有效的period参数: {valid_periods}")
print()
print(f"无效的period参数: {invalid_periods}")
print()

print("=" * 80)
print("建议")
print("=" * 80)
print()

if '60m' in invalid_periods and '1h' in valid_periods:
    print("[发现] 60分钟K线应该使用 period='1h' 而不是 period='60m'")
elif '60m' in valid_periods:
    print("[发现] period='60m' 可用")
elif '1h' in valid_periods:
    print("[发现] period='1h' 可用")
else:
    print("[WARN] 60分钟K线格式待确认")

print()
print("推荐的period参数:")
for p in valid_periods:
    print(f"  - '{p}'")
