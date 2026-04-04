#!/usr/bin/env python3
"""直接检查HotDB中存储的数据"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("检查HotDB中存储的数据")
print("=" * 60)

hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period=period, count=10000, allow_stale=True)

if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].sort_values('datetime')

    print(f"\n数据范围: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")
    print(f"总条数: {len(df)}")

    # 检查3月9日数据
    march_9_start = pd.Timestamp('2026-03-09 09:30:00')
    march_9_end = pd.Timestamp('2026-03-09 15:00:00')
    df_march_9 = df[(df['datetime'] >= march_9_start) & (df['datetime'] <= march_9_end)]

    print(f"\n" + "=" * 60)
    print("3月9日数据:")
    print("=" * 60)
    if not df_march_9.empty:
        print(df_march_9[['datetime', 'volume', 'open', 'close']].head(10))
        vol_0 = df_march_9['volume'].iloc[0]
        print(f"\n3月9日第一条volume: {vol_0:,.0f}", end="")
        if vol_0 > 1000000:
            print(" -> 股单位（未转换）")
        else:
            print(" -> 手单位（已转换）")
    else:
        print("无3月9日数据")

    # 检查整个数据范围内，volume是否有不同的数量级
    print(f"\n" + "=" * 60)
    print("Volume分布分析:")
    print("=" * 60)
    print(df['volume'].describe())

    # 检查volume超过100万的条目（可能是股单位）
    large_vol = df[df['volume'] > 1000000]
    print(f"\nVolume > 100万（可能是股单位）: {len(large_vol)} 条")
    if len(large_vol) > 0:
        print("样本:")
        print(large_vol[['datetime', 'volume']].head())

    # 检查volume在1万到100万之间的条目（可能是手单位）
    medium_vol = df[(df['volume'] > 10000) & (df['volume'] <= 1000000)]
    print(f"\nVolume 1万-100万（可能是手单位）: {len(medium_vol)} 条")

    # 检查最近的数据
    print(f"\n" + "=" * 60)
    print("最近20条数据:")
    print("=" * 60)
    print(df[['datetime', 'volume', 'open', 'close']].tail(20))

else:
    print("HotDB中无数据")
