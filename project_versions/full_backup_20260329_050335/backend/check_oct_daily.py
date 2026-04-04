#!/usr/bin/env python3
"""检查2025年10月日线数据volume问题"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'

print("=" * 60)
print("检查2025年10月日线volume数据")
print("=" * 60)

hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period='1d', count=1000, allow_stale=True)

if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].sort_values('datetime')
    df['datetime'] = pd.to_datetime(df['datetime'])

    # 2025年10月数据
    oct_start = pd.Timestamp('2025-10-01')
    oct_end = pd.Timestamp('2025-10-31')
    df_oct = df[(df['datetime'] >= oct_start) & (df['datetime'] <= oct_end)]

    print(f"\n2025年10月日线数据:")
    print(df_oct[['datetime', 'volume', 'open', 'close']].to_string())

    # 特别检查10月28和29日
    print(f"\n" + "=" * 60)
    print("10月28-29日详细对比:")
    print("=" * 60)
    for date_str in ['2025-10-28', '2025-10-29', '2025-10-27', '2025-10-30']:
        date_data = df_oct[df_oct['datetime'].dt.strftime('%Y-%m-%d') == date_str]
        if not date_data.empty:
            vol = date_data['volume'].iloc[0]
            print(f"{date_str}: volume = {vol:>12,.0f}", end="")
            if vol > 1000000:
                print(" -> 股单位（可能未转换）")
            else:
                print(" -> 手单位（正常）")
        else:
            print(f"{date_str}: 无数据")

else:
    print("HotDB中无数据")