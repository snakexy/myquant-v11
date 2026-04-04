#!/usr/bin/env python3
"""测试 XtQuant 是否支持周K和月K"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter

symbol = '000001.SZ'

print("=" * 60)
print("测试 XtQuant 周K和月K支持")
print("=" * 60)

xtquant = get_adapter('xtquant')

if xtquant and xtquant.is_available():
    for period in ['1d', '1w', '1mon', '1M', 'week', 'month']:
        print(f"\n测试周期: {period}")
        try:
            df_dict = xtquant.get_kline([symbol], period=period, count=5)
            if symbol in df_dict and not df_dict[symbol].empty:
                df = df_dict[symbol]
                print(f"  [OK] 成功: {len(df)} 条")
                print(f"       字段: {list(df.columns)}")
                print(f"       首条日期: {df.iloc[0]['datetime']}")
            else:
                print(f"  [空] 无数据")
        except Exception as e:
            print(f"  [错误] {e}")
else:
    print("XtQuant 不可用")
