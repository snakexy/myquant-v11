"""
诊断台基股份（300046.SZ）5分钟数据缺口
"""

from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.hotdb_service import get_hotdb_service
import pandas as pd

symbol = "300046.SZ"
period = "5m"

print(f"\n{'='*60}")
print(f"诊断 {symbol} {period} 数据缺口")
print(f"{'='*60}\n")

# 1. 获取 HotDB 数据信息
hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    info = hotdb.get_data_info(symbol, period)
    if info and info.get('has_data'):
        print(f"[HotDB] 数据信息:")
        print(f"  - 数量: {info.get('count')} 条")
        print(f"  - 最早: {info.get('earliest')}")
        print(f"  - 最新: {info.get('latest')}")

        # 获取3月份的数据
        df_dict = hotdb.get_kline(
            symbols=[symbol],
            period=period,
            start_date="20260301",
            end_date="20260331"
        )

        if symbol in df_dict and not df_dict[symbol].empty:
            df = df_dict[symbol]
            print(f"\n[HotDB] 3月份数据: {len(df)} 条")

            # 检查3月16日前后的数据
            march_16 = df[df['datetime'].dt.strftime('%Y%m%d') == '20260316']
            march_17_to_25 = df[(df['datetime'].dt.strftime('%Y%m%d') >= '20260317') &
                               (df['datetime'].dt.strftime('%Y%m%d') <= '20260325')]
            march_26 = df[df['datetime'].dt.strftime('%Y%m%d') == '20260326']

            print(f"\n  3月16日: {len(march_16)} 条")
            if not march_16.empty:
                print(f"    时间范围: {march_16['datetime'].min()} ~ {march_16['datetime'].max()}")

            print(f"  3月17-25日: {len(march_17_to_25)} 条")
            if not march_17_to_25.empty:
                print(f"    时间范围: {march_17_to_25['datetime'].min()} ~ {march_17_to_25['datetime'].max()}")

            print(f"  3月26日: {len(march_26)} 条")
            if not march_26.empty:
                print(f"    时间范围: {march_26['datetime'].min()} ~ {march_26['datetime'].max()}")

            # 检查时间差
            df_sorted = df.sort_values('datetime').reset_index(drop=True)
            df_sorted['time_diff'] = df_sorted['datetime'].diff()

            # 找出超过4小时的缺口
            large_gaps = df_sorted[df_sorted['time_diff'] > pd.Timedelta(hours=4)]

            print(f"\n[HotDB] 发现 {len(large_gaps)} 个大缺口（>4小时）:")
            for idx, row in large_gaps.iterrows():
                if idx > 0:
                    gap_start = df_sorted.iloc[idx - 1]['datetime']
                    gap_end = row['datetime']
                    gap_hours = row['time_diff'].total_seconds() / 3600
                    print(f"  - {gap_start} -> {gap_end} ({gap_hours:.1f} 小时)")
        else:
            print(f"\n[HotDB] 3月份无数据")
    else:
        print(f"\n[HotDB] 无数据")

# 2. 获取 LocalDB 数据信息
print(f"\n{'='*60}")
localdb = get_adapter('localdb')
if localdb and localdb.is_available():
    try:
        info = localdb.get_data_info(symbol, period)
    except AttributeError:
        print(f"[LocalDB] 不支持 get_data_info，直接获取数据...")
        # 直接获取数据
        df_dict = localdb.get_kline(
            symbols=[symbol],
            period=period,
            start_date="20260301",
            end_date="20260331"
        )

        if symbol in df_dict and not df_dict[symbol].empty:
            df = df_dict[symbol]
            print(f"[LocalDB] 3月份数据: {len(df)} 条")

            # 检查3月16日前后的数据
            march_16 = df[df['datetime'].dt.strftime('%Y%m%d') == '20260316']
            march_17_to_25 = df[(df['datetime'].dt.strftime('%Y%m%d') >= '20260317') &
                               (df['datetime'].dt.strftime('%Y%m%d') <= '20260325')]
            march_26 = df[df['datetime'].dt.strftime('%Y%m%d') == '20260326']

            print(f"\n  3月16日: {len(march_16)} 条")
            if not march_16.empty:
                print(f"    时间范围: {march_16['datetime'].min()} ~ {march_16['datetime'].max()}")

            print(f"  3月17-25日: {len(march_17_to_25)} 条")
            if not march_17_to_25.empty:
                print(f"    时间范围: {march_17_to_25['datetime'].min()} ~ {march_17_to_25['datetime'].max()}")

            print(f"  3月26日: {len(march_26)} 条")
            if not march_26.empty:
                print(f"    时间范围: {march_26['datetime'].min()} ~ {march_26['datetime'].max()}")

            # 检查时间差
            df_sorted = df.sort_values('datetime').reset_index(drop=True)
            df_sorted['time_diff'] = df_sorted['datetime'].diff()

            # 找出超过4小时的缺口
            large_gaps = df_sorted[df_sorted['time_diff'] > pd.Timedelta(hours=4)]

            print(f"\n[LocalDB] 发现 {len(large_gaps)} 个大缺口（>4小时）:")
            for idx, row in large_gaps.iterrows():
                if idx > 0:
                    gap_start = df_sorted.iloc[idx - 1]['datetime']
                    gap_end = row['datetime']
                    gap_hours = row['time_diff'].total_seconds() / 3600
                    print(f"  - {gap_start} -> {gap_end} ({gap_hours:.1f} 小时)")
        else:
            print(f"\n[LocalDB] 3月份无数据")
else:
    print(f"\n[LocalDB] 不可用")

print(f"\n{'='*60}")

# 3. 测试缺口检测
print(f"\n测试 _detect_gap 方法:")
hotdb_service = get_hotdb_service()
gap_info = hotdb_service._detect_gap(symbol, period)
if gap_info:
    print(f"  - has_gap: {gap_info.get('has_gap')}")
    print(f"  - reason: {gap_info.get('reason')}")
    if gap_info.get('has_gap'):
        print(f"  - gap_start: {gap_info.get('missing_start')}")
        print(f"  - gap_end: {gap_info.get('missing_end')}")
else:
    print(f"  - 无返回结果")

print(f"\n{'='*60}\n")
