#!/usr/bin/env python3
"""诊断日线/月线混淆问题"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.hotdb_service import get_hotdb_service

symbol = '000001.SZ'

def test_storage_paths():
    """测试存储路径是否正确分离"""
    print("=" * 60)
    print("测试存储路径分离")
    print("=" * 60)

    hotdb = get_adapter('hotdb')

    # 获取不同周期的存储路径
    for period in ['1d', '1w', '1mon']:
        stock_dir = hotdb._get_stock_dir(symbol, period)
        print(f"\n周期 {period}:")
        print(f"  存储路径: {stock_dir}")

        # 检查目录是否存在
        if stock_dir.exists():
            print(f"  状态: 目录存在")
            # 列出文件
            files = list(stock_dir.glob('*.bin'))
            if files:
                for f in files:
                    print(f"    - {f.name}")
            else:
                print(f"    (无bin文件)")
        else:
            print(f"  状态: 目录不存在")

    print("\n" + "=" * 60)

def test_memory_cache_separation():
    """测试内存缓存是否正确分离"""
    print("\n测试内存缓存分离")
    print("=" * 60)

    hotdb = get_adapter('hotdb')

    # 检查当前内存缓存的键
    print("\n当前内存缓存中的键:")
    cache_keys = list(hotdb._memory_cache.keys())
    if cache_keys:
        for key in cache_keys:
            df = hotdb._memory_cache[key]
            print(f"  {key}: {len(df)} 条")
            if not df.empty:
                print(f"    最早: {df['datetime'].iloc[0]}")
                print(f"    最晚: {df['datetime'].iloc[-1]}")
    else:
        print("  (无缓存)")

    print("\n" + "=" * 60)

def test_data_retrieval():
    """测试数据获取流程"""
    print("\n测试数据获取")
    print("=" * 60)

    hotdb_service = get_hotdb_service()

    for period in ['1d', '1mon']:
        print(f"\n获取 {symbol} {period}:")
        result = hotdb_service.smart_update(symbol, period)

        print(f"  成功: {result.get('success')}")
        print(f"  有数据: {result.get('has_data')}")
        print(f"  有缺口: {result.get('has_gap')}")

        df = result.get('df')
        if df is not None and not df.empty:
            print(f"  条数: {len(df)}")
            print(f"  最早: {df['datetime'].iloc[0]}")
            print(f"  最晚: {df['datetime'].iloc[-1]}")

            # 检查日期差异（日K应该每天一条，月K应该每月一条）
            date_diff = (df['datetime'].iloc[-1] - df['datetime'].iloc[0]).days
            avg_interval = date_diff / len(df)
            print(f"  平均间隔: {avg_interval:.1f} 天")

            if period == '1d':
                if avg_interval > 20:
                    print(f"  ⚠️ 警告: 日线平均间隔 {avg_interval:.1f} 天，疑似月线数据！")
                else:
                    print(f"  ✓ 正常: 日线平均间隔合理")
            elif period == '1mon':
                if 25 <= avg_interval <= 35:
                    print(f"  ✓ 正常: 月线平均间隔合理")
                else:
                    print(f"  ⚠️ 警告: 月线平均间隔 {avg_interval:.1f} 天，不正常")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_storage_paths()
    test_memory_cache_separation()
    test_data_retrieval()
