#!/usr/bin/env python3
"""
检查成交量单位问题
"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter

symbol = '000001.SZ'
hotdb = get_adapter('hotdb')

print("=" * 60)
print("检查5分钟线成交量")
print("=" * 60)

# 获取5分钟数据
df_dict = hotdb.get_kline([symbol], period='5m', count=100, allow_stale=True)
if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol]

    # 显示最后10条数据的成交量
    print("\n最后10条5分钟K线:")
    for idx in range(-10, 0):
        row = df.iloc[idx]
        vol = row['volume']
        dt = row['datetime']
        print(f"  {dt}: 成交量 {vol:>12,.0f} ({vol/10000:>6.2f}万)")

    # 计算一天的总成交量（假设数据包含完整一天）
    last_date = df['datetime'].iloc[-1].date()
    day_data = df[df['datetime'].dt.date == last_date]
    total_vol = day_data['volume'].sum()

    print(f"\n{last_date} 5分钟线总成交量: {total_vol:,.0f} ({total_vol/10000:.2f}万)")

print("\n" + "=" * 60)
print("检查日线成交量")
print("=" * 60)

# 获取日线数据
df_dict = hotdb.get_kline([symbol], period='1d', count=5, allow_stale=True)
if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol]

    print("\n最近5天日线:")
    for idx in range(len(df)):
        row = df.iloc[idx]
        vol = row['volume']
        dt = row['datetime']
        print(f"  {dt.date()}: 成交量 {vol:>12,.0f} ({vol/10000:>8.2f}万)")

    # 比较同一天5分钟线总和 vs 日线
    if last_date == df['datetime'].iloc[-1].date():
        day_vol = df.iloc[-1]['volume']
        print(f"\n对比:")
        print(f"  5分钟线总和: {total_vol:>12,.0f} ({total_vol/10000:>8.2f}万)")
        print(f"  日线成交量: {day_vol:>12,.0f} ({day_vol/10000:>8.2f}万)")
        print(f"  比例: {total_vol/day_vol:.2%}")
