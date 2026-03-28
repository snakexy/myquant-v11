#!/usr/bin/env python3
"""检查3月6日到3月9日的数据详情"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("检查3月6日到3月9日的volume数据")
print("=" * 60)

hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period=period, count=10000, allow_stale=True)

if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].sort_values('datetime')

    # 检查3月6日到3月9日的数据
    march_6 = pd.Timestamp('2026-03-06 09:30:00')
    march_10 = pd.Timestamp('2026-03-10 15:00:00')

    df_range = df[(df['datetime'] >= march_6) & (df['datetime'] <= march_10)]

    print(f"\n3月6日到3月9日数据条数: {len(df_range)}")

    if not df_range.empty:
        print("\n详细数据:")
        print(df_range[['datetime', 'volume', 'open', 'close', 'data_source']].to_string())

        # 按日期分组查看统计
        print("\n\n按日期分组统计:")
        df_range['date'] = df_range['datetime'].dt.strftime('%Y-%m-%d')
        for date, group in df_range.groupby('date'):
            vol_first = group['volume'].iloc[0]
            vol_last = group['volume'].iloc[-1]
            vol_mean = group['volume'].mean()
            source = group['data_source'].iloc[0] if 'data_source' in group.columns else 'unknown'
            print(f"{date}: 条数={len(group)}, 首条vol={vol_first:>12,.0f}, 末条vol={vol_last:>12,.0f}, 平均={vol_mean:>12,.0f}, 来源={source}")

        # 特别标记可能未转换的数据
        print("\n\n⚠️ 检查可能未转换的数据（volume > 1,000,000）:")
        large_vol = df_range[df_range['volume'] > 1000000]
        if not large_vol.empty:
            for idx, row in large_vol.iterrows():
                print(f"  {row['datetime']}: {row['volume']:>15,.0f} -> 可能是股单位 (应转换为 {row['volume']/100:>12,.0f})")
        else:
            print("  没有发现volume > 1,000,000的数据")
    else:
        print("该时间段无数据")
else:
    print("HotDB中无数据")