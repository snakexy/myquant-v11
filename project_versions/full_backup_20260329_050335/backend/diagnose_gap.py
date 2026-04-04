#!/usr/bin/env python3
"""
诊断脚本：检查HotDB数据缺口检测问题
"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from datetime import datetime
import pandas as pd
from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.hotdb_service import get_hotdb_service

def diagnose_gap_detection(symbol='000001.SZ', period='5m'):
    """诊断缺口检测"""
    print(f"\n{'='*60}")
    print(f"诊断: {symbol} {period}")
    print(f"{'='*60}")

    # 1. 检查HotDB适配器
    hotdb = get_adapter('hotdb')
    print(f"\n1. HotDB适配器: {hotdb}")
    print(f"   可用: {hotdb.is_available() if hotdb else False}")

    # 2. 获取数据信息
    info = hotdb.get_data_info(symbol, period)
    print(f"\n2. get_data_info 结果:")
    print(f"   {info}")

    if info and info.get('has_data'):
        latest = info['latest']
        now = pd.Timestamp.now(tz=None).replace(tzinfo=None)

        print(f"\n3. 时间分析:")
        print(f"   最新数据时间: {latest} (类型: {type(latest)})")
        print(f"   当前时间: {now}")

        if hasattr(latest, 'date'):
            latest_date = latest.date()
            today = now.date()
            days_diff = (today - latest_date).days
            print(f"   最新日期: {latest_date}")
            print(f"   今天: {today}")
            print(f"   相差天数: {days_diff}")

            # 计算时间差（分钟）
            time_diff_minutes = (now - latest).total_seconds() / 60
            print(f"   时间差（分钟）: {time_diff_minutes:.1f}")

            # 阈值
            thresholds = {'1m': 5, '5m': 15, '15m': 30, '30m': 60, '1h': 120}
            threshold = thresholds.get(period, 15)
            print(f"   阈值（分钟）: {threshold}")
            print(f"   是否超过阈值: {time_diff_minutes > threshold}")

    # 4. 检查Service层缺口检测
    print(f"\n4. Service层缺口检测:")
    service = get_hotdb_service()
    gap_info = service._detect_gap(symbol, period)
    print(f"   结果: {gap_info}")

    # 5. 检查实际K线数据
    print(f"\n5. 实际K线数据（最后3条）:")
    df_dict = hotdb.get_kline([symbol], period=period, count=3, allow_stale=True)
    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        print(f"   数据条数: {len(df)}")
        print(f"   时间范围: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")
        print(f"   最后一条数据:\n{df.iloc[-1]}")

        # 检查成交量
        last_vol = df.iloc[-1]['volume']
        print(f"\n6. 成交量检查:")
        print(f"   最后一条成交量: {last_vol:,.0f}")
        print(f"   如果是手: 约 {last_vol/10000:.2f} 万手")
        print(f"   如果是股: 约 {last_vol/1000000:.2f} 百万股")
    else:
        print(f"   无数据")

if __name__ == '__main__':
    diagnose_gap_detection('000001.SZ', '5m')
    diagnose_gap_detection('000001.SZ', '1d')