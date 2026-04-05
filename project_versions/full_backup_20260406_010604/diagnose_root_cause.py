#!/usr/bin/env python3
"""
诊断日线/月线混淆问题的根本原因
"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter

symbol = '000001.SZ'


def diagnose_period_mixup_root_cause():
    """诊断周期混淆的根本原因"""
    print("=" * 70)
    print("诊断周期混淆问题的根本原因")
    print("=" * 70)

    hotdb = get_adapter('hotdb')

    # 1. 检查内存缓存中的键
    print("\n【1. 内存缓存检查】")
    cache_keys = list(hotdb._memory_cache.keys())
    print(f"当前内存缓存键: {cache_keys}")

    # 2. 检查存储路径
    print("\n【2. 存储路径检查】")
    for period in ['1d', '1w', '1mon']:
        stock_dir = hotdb._get_stock_dir(symbol, period)
        print(f"\n周期 {period}:")
        print(f"  路径: {stock_dir}")
        if stock_dir.exists():
            print("  状态: [OK] 存在")
            # 列出所有文件
            files = list(stock_dir.glob('*.bin'))
            for f in files:
                size = f.stat().st_size
                print(f"    - {f.name} ({size} bytes)")
        else:
            print("  状态: [EMPTY] 不存在")

    # 3. 直接读取各周期数据并验证
    print("\n【3. 数据验证】")
    for period in ['1d', '1mon']:
        print(f"\n周期 {period}:")
        df_dict = hotdb.get_kline([symbol], period=period, count=10)
        if symbol in df_dict and not df_dict[symbol].empty:
            df = df_dict[symbol]
            print(f"  获取到 {len(df)} 条数据")
            if len(df) > 1:
                first_date = df['datetime'].iloc[0]
                last_date = df['datetime'].iloc[-1]
                avg_interval = (last_date - first_date).days / len(df)
                print(f"  首条日期: {first_date}")
                print(f"  末条日期: {last_date}")
                print(f"  平均间隔: {avg_interval:.1f} 天")

                # 判断数据类型
                if period == '1d':
                    if avg_interval > 20:
                        print(f"  [WARNING] 日线平均间隔 {avg_interval:.1f} 天，疑似月线数据！")
                    else:
                        print("  [OK] 正常日线数据")
                elif period == '1mon':
                    if 25 <= avg_interval <= 35:
                        print("  [OK] 正常月线数据")
                    else:
                        print(f"  [WARNING] 月线平均间隔 {avg_interval:.1f} 天，不正常")
        else:
            print("  无数据")

    # 4. 检查内存缓存的内容
    print("\n【4. 内存缓存内容检查】")
    for period in ['1d', '1mon']:
        cache_key = f"{symbol}:{period}"
        if cache_key in hotdb._memory_cache:
            df = hotdb._memory_cache[cache_key]
            print(f"\n缓存键 {cache_key}:")
            print(f"  条数: {len(df)}")
            if len(df) > 1:
                first_date = df['datetime'].iloc[0]
                last_date = df['datetime'].iloc[-1]
                avg_interval = (last_date - first_date).days / len(df)
                print(f"  平均间隔: {avg_interval:.1f} 天")

                # 判断数据类型
                if period == '1d' and avg_interval > 20:
                    print("  [WARNING] 日线缓存中的数据疑似月线！")
                elif period == '1mon' and 25 <= avg_interval <= 35:
                    print("  [OK] 正常")

    # 5. 检查是否有交叉污染
    print("\n【5. 交叉污染检查】")
    day_key = f"{symbol}:1d"
    month_key = f"{symbol}:1mon"

    if day_key in hotdb._memory_cache and month_key in hotdb._memory_cache:
        day_df = hotdb._memory_cache[day_key]
        month_df = hotdb._memory_cache[month_key]

        # 比较数据内容是否相同
        if len(day_df) == len(month_df):
            # 检查日期是否相同
            day_dates = set(day_df['datetime'].dt.strftime('%Y-%m-%d'))
            month_dates = set(month_df['datetime'].dt.strftime('%Y-%m-%d'))

            if day_dates == month_dates:
                print("[CRITICAL] 严重警告: 日线和月线的日期完全相同！")
                print("    这证实存在数据交叉污染！")
            else:
                print("[OK] 日线和月线的日期不同，无交叉污染")
        else:
            print(f"[OK] 数据条数不同: 日线{len(day_df)}条, 月线{len(month_df)}条")

    print("\n" + "=" * 70)
    print("诊断完成")
    print("=" * 70)


if __name__ == '__main__':
    diagnose_period_mixup_root_cause()
