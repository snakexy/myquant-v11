#!/usr/bin/env python3
"""
复权算法验证 - 对比通达信

以茅台(600519.SH)为例，验证前复权价格是否正确。
通达信显示：2025-12-18 前复权价 约 1407.04 元
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logging
logging.disable(logging.CRITICAL)
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime


def verify_moutai_adjustment():
    """验证茅台复权"""
    print("=" * 60)
    print("复权算法验证 - 茅台(600519.SH)")
    print("=" * 60)
    print("对比日期: 2025-12-18")
    print("通达信参考: 前复权约 1407.04 元")
    print()

    from myquant.core.market.services.seamless_service import get_seamless_kline_service
    from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service

    service = get_seamless_kline_service()
    factor_service = get_adjustment_factor_service()

    symbol = "600519.SH"

    # 1. 获取XDXR数据
    print("【1】除权除息数据")
    print("-" * 40)
    xdxr_data = service._get_xdxr_data(symbol)
    print(f"  XDXR记录数: {len(xdxr_data)}")

    if xdxr_data:
        # 显示最新的几条
        for record in xdxr_data[-3:]:
            date = f"{int(record.get('year', 0))}-{int(record.get('month', 0)):02d}-{int(record.get('day', 0)):02d}"
            fenhong = record.get('fenhong', 0)
            songgu = record.get('songzhuangu', 0)
            print(f"  {date}: 10派{fenhong}元, 10送{songgu}股")

    # 2. 获取复权因子表
    print()
    print("【2】复权因子表")
    print("-" * 40)
    factor_table = factor_service.get_factor_table(symbol, 'front')
    print(f"  因子表天数: {len(factor_table)}")

    # 显示最新日期的因子
    today = datetime.now().strftime('%Y-%m-%d')
    latest_factor = factor_table.get(today, factor_table.get(list(factor_table.keys())[-1]) if factor_table else None)
    print(f"  最新因子({today}): {latest_factor}")

    # 3. 获取不复权价格
    print()
    print("【3】价格对比")
    print("-" * 40)

    df_raw = service.get_kline(symbol, period='1d', count=10, adjust_type='none')
    df_adj = service.get_kline(symbol, period='1d', count=10, adjust_type='front')

    if not df_raw.empty and not df_adj.empty:
        # 找到2025-12-18的数据
        target_date = "2025-12-18"
        raw_row = df_raw[df_raw['datetime'].astype(str).str.contains(target_date)]
        adj_row = df_adj[df_adj['datetime'].astype(str).str.contains(target_date)]

        if not raw_row.empty and not adj_row.empty:
            raw_price = raw_row.iloc[-1]['close']
            adj_price = adj_row.iloc[-1]['close']
            factor = adj_price / raw_price if raw_price else 0

            print(f"  日期: {target_date}")
            print(f"  不复权价: {raw_price:.2f}")
            print(f"  前复权价: {adj_price:.2f}")
            print(f"  计算因子: {factor:.6f}")
            print()
            print(f"  通达信参考: 1407.04 元")
            print(f"  本系统计算: {adj_price:.2f} 元")
            diff = abs(adj_price - 1407.04)
            print(f"  误差: {diff:.2f} 元 ({diff/1407.04*100:.2f}%)")

            if diff < 1.0:
                print("  [OK] 误差在可接受范围内")
            else:
                print("  [X] 误差过大，需要检查")
        else:
            print(f"  [X] 未找到 {target_date} 的数据")
            print(f"  最新数据日期: {df_raw['datetime'].iloc[-1]}")

    # 4. 显示最近5天的对比
    print()
    print("【4】最近5天价格对比")
    print("-" * 40)
    print(f"  {'日期':<12} {'不复权':<10} {'前复权':<10} {'因子':<8}")
    print("  " + "-" * 44)

    for i in range(min(5, len(df_raw))):
        raw_row = df_raw.iloc[-(i+1)]
        adj_row = df_adj.iloc[-(i+1)]
        date = str(raw_row['datetime'])[:10]
        raw_price = raw_row['close']
        adj_price = adj_row['close']
        factor = adj_price / raw_price if raw_price else 0
        print(f"  {date:<12} {raw_price:<10.2f} {adj_price:<10.2f} {factor:<8.4f}")

    print()
    print("=" * 60)


if __name__ == '__main__':
    verify_moutai_adjustment()
