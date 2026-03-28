#!/usr/bin/env python3
"""检查数据缺口和时间分布"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("检查数据缺口")
print("=" * 60)

hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period=period, count=10000, allow_stale=True)

if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].sort_values('datetime').reset_index(drop=True)

    print(f"数据总条数: {len(df)}")
    print(f"时间范围: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")

    # 检查时间差
    df['time_diff'] = df['datetime'].diff()

    # 正常5分钟K线的时间差应该是5分钟
    # 超过5分钟的都可能是缺口
    normal_gap = pd.Timedelta(minutes=5)
    large_gaps = df[df['time_diff'] > pd.Timedelta(minutes=10)]  # 超过10分钟的都认为是缺口

    print(f"\n发现 {len(large_gaps)} 个时间缺口:")

    for idx in large_gaps.index[:10]:  # 只显示前10个
        gap_start = df.iloc[idx-1]['datetime'] if idx > 0 else 'N/A'
        gap_end = df.iloc[idx]['datetime']
        gap_size = large_gaps.loc[idx, 'time_diff']
        print(f"  缺口 {idx}: {gap_start} -> {gap_end} (差距: {gap_size})")

    # 特别检查3月6日到3月16日之间的数据
    print("\n" + "=" * 60)
    print("3月1日到3月20日的数据分布:")
    print("=" * 60)

    for day in range(1, 21):
        date_str = f'2026-03-{day:02d}'
        date_start = pd.Timestamp(date_str)
        date_end = date_start + pd.Timedelta(days=1)

        df_day = df[(df['datetime'] >= date_start) & (df['datetime'] < date_end)]

        if not df_day.empty:
            first_time = df_day['datetime'].iloc[0].strftime('%H:%M')
            last_time = df_day['datetime'].iloc[-1].strftime('%H:%M')
            avg_volume = df_day['volume'].mean()
            print(f"{date_str}: {len(df_day):>4} 条 ({first_time}~{last_time}) 平均volume: {avg_volume:>10,.0f}")
        else:
            print(f"{date_str}: 无数据")

    # 检查每个日期的volume单位
    print("\n" + "=" * 60)
    print("检查每个日期的volume单位:")
    print("=" * 60)

    # 获取几个样本日期
    sample_dates = ['2026-03-05', '2026-03-06', '2026-03-07', '2026-03-10', '2026-03-16']

    for date_str in sample_dates:
        date_start = pd.Timestamp(date_str)
        date_end = date_start + pd.Timedelta(days=1)
        df_day = df[(df['datetime'] >= date_start) & (df['datetime'] < date_end)]

        if not df_day.empty:
            sample_vol = df_day['volume'].iloc[0]
            print(f"{date_str}: 样本volume = {sample_vol:>12,.0f}", end="")
            if sample_vol > 1000000:
                print(" (股单位 - 数值过大)")
            elif sample_vol > 1000:
                print(" (手单位 - 正常)")
            else:
                print(" (数值过小)")
        else:
            print(f"{date_str}: 无数据")
