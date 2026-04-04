#!/usr/bin/env python3
"""
精准测试：检查缺口检测逻辑
"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from datetime import datetime
import pandas as pd
from myquant.core.market.adapters import get_adapter

# 1. 测试 get_data_info 返回的时间精度
hotdb = get_adapter('hotdb')
symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("测试1: get_data_info 返回的时间精度")
print("=" * 60)

info = hotdb.get_data_info(symbol, period)
if info:
    latest = info['latest']
    print(f"get_data_info 返回的 latest: {latest}")
    print(f"类型: {type(latest)}")
    print(f"日期部分: {latest.date()}")
    print(f"时间部分: {latest.time()}")

# 2. 获取实际K线数据的最后一个时间点
print("\n" + "=" * 60)
print("测试2: 实际K线数据的最后时间点")
print("=" * 60)

df_dict = hotdb.get_kline([symbol], period=period, count=3, allow_stale=True)
if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol]
    last_dt = df['datetime'].iloc[-1]
    print(f"实际最后一条数据时间: {last_dt}")
    print(f"类型: {type(last_dt)}")
    print(f"日期部分: {last_dt.date()}")
    print(f"时间部分: {last_dt.time()}")

# 3. 计算正确的缺口
print("\n" + "=" * 60)
print("测试3: 缺口计算")
print("=" * 60)

now = pd.Timestamp.now(tz=None).replace(tzinfo=None)
print(f"当前时间: {now}")

# 使用 get_data_info 的时间（错误）
latest_info = info['latest']
time_diff_info = (now - latest_info).total_seconds() / 60
print(f"\n使用 get_data_info 的时间: {latest_info}")
print(f"时间差（分钟）: {time_diff_info:.1f}")

# 使用实际K线最后时间（正确）
latest_actual = df['datetime'].iloc[-1]
time_diff_actual = (now - latest_actual).total_seconds() / 60
print(f"\n使用实际K线最后时间: {latest_actual}")
print(f"时间差（分钟）: {time_diff_actual:.1f}")

# 阈值
thresholds = {'1m': 5, '5m': 15, '15m': 30, '30m': 60, '1h': 120}
threshold = thresholds.get(period, 15)
print(f"\n阈值（分钟）: {threshold}")
print(f"使用 get_data_info: {'超过阈值' if time_diff_info > threshold else '未超过'}")
print(f"使用实际K线时间: {'超过阈值' if time_diff_actual > threshold else '未超过'}")

# 4. 分析内部缺口
print("\n" + "=" * 60)
print("测试4: 分析内部缺口")
print("=" * 60)

# 获取全部数据
df_dict = hotdb.get_kline([symbol], period=period, count=10000, allow_stale=True)
if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].copy()
    df = df.sort_values('datetime').reset_index(drop=True)

    # 计算时间差
    time_diffs = df['datetime'].diff()

    # 检查超过4小时的缺口
    large_gaps = time_diffs[time_diffs > pd.Timedelta(hours=4)]

    print(f"数据总数: {len(df)}")
    print(f"时间范围: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")
    print(f"\n发现 {len(large_gaps)} 个超过4小时的缺口:")

    for gap_idx, gap in large_gaps.head(5).items():
        gap_start = df.iloc[gap_idx - 1]['datetime']
        gap_end = df.iloc[gap_idx]['datetime']
        print(f"  缺口 {gap_idx}: {gap_start} -> {gap_end} ({gap})")
