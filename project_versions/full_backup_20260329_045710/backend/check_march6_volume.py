#!/usr/bin/env python3
"""检查3月6日后的成交量数据"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("检查3月6日后的成交量数据")
print("=" * 60)

hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period=period, count=10000, allow_stale=True)

if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].sort_values('datetime')

    print(f"\n数据范围: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")
    print(f"总数据条数: {len(df)}")

    # 查找3月6日的数据
    march_6 = pd.Timestamp('2026-03-06')
    march_7 = pd.Timestamp('2026-03-07')

    df_march_6 = df[(df['datetime'] >= march_6) & (df['datetime'] < march_7)]

    print(f"\n3月6日数据条数: {len(df_march_6)}")
    if not df_march_6.empty:
        print("\n3月6日最后5条数据:")
        print(df_march_6[['datetime', 'volume', 'open', 'close']].tail())
        print(f"\n3月6日最后一条volume: {df_march_6['volume'].iloc[-1]:,.0f}")

    # 查找3月6日之后的数据
    df_after_march_6 = df[df['datetime'] >= march_7]

    print(f"\n3月6日之后数据条数: {len(df_after_march_6)}")
    if not df_after_march_6.empty:
        print(f"\n3月6日之后数据范围: {df_after_march_6['datetime'].iloc[0]} ~ {df_after_march_6['datetime'].iloc[-1]}")
        print("\n3月6日之后前5条数据:")
        print(df_after_march_6[['datetime', 'volume', 'open', 'close']].head())
        print("\n3月6日之后最后5条数据:")
        print(df_after_march_6[['datetime', 'volume', 'open', 'close']].tail())

        # 统计volume分布
        print(f"\n3月6日之后volume统计:")
        print(df_after_march_6['volume'].describe())
    else:
        print("\n[警告] 3月6日之后无数据！")
        print("数据只到3月6日，需要检查智能更新是否正常工作")

    # 检查最新数据的volume
    print(f"\n\n最后一条数据:")
    last_row = df.iloc[-1]
    print(f"时间: {last_row['datetime']}")
    print(f"Volume: {last_row['volume']:,.0f}")
    print(f"Open: {last_row['open']}")
    print(f"Close: {last_row['close']}")
else:
    print("[错误] HotDB中无数据")