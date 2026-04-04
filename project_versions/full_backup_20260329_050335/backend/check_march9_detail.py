#!/usr/bin/env python3
"""检查3月9日数据的来源和保存时间"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("检查HotDB中3月9日数据的详情")
print("=" * 60)

hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period=period, count=10000, allow_stale=True)

if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].sort_values('datetime')

    # 3月9日数据
    march_9_start = pd.Timestamp('2026-03-09 09:30:00')
    march_9_end = pd.Timestamp('2026-03-09 15:00:00')
    df_march_9 = df[(df['datetime'] >= march_9_start) & (df['datetime'] <= march_9_end)]

    print(f"\n3月9日数据条数: {len(df_march_9)}")
    if not df_march_9.empty:
        print("\n3月9日前5条数据:")
        print(df_march_9.head())

        # 检查volume列统计
        print(f"\n3月9日volume统计:")
        print(df_march_9['volume'].describe())

        # 检查第一条和最后一条的volume
        first_vol = df_march_9['volume'].iloc[0]
        last_vol = df_march_9['volume'].iloc[-1]
        print(f"\n第一条volume: {first_vol:,.0f}")
        print(f"最后一条volume: {last_vol:,.0f}")

        if first_vol > 1000000:
            print("\n⚠️  确认: 3月9日数据单位是股（未转换）")
            print("    预期手单位应为: {:.0f}".format(first_vol/100))

    # 检查数据范围
    print(f"\n" + "=" * 60)
    print("HotDB数据范围:")
    print("=" * 60)
    print(f"最早: {df['datetime'].iloc[0]}")
    print(f"最晚: {df['datetime'].iloc[-1]}")
    print(f"总条数: {len(df)}")

else:
    print("HotDB中无数据")