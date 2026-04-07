#!/usr/bin/env python3
"""
快速诊断脚本 - 只输出关键结果
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 禁用所有日志
import logging
logging.disable(logging.CRITICAL)
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta
import pandas as pd

# 测试股票
SYMBOLS = ['600519.SH', '000001.SZ', '000001.SH']

def simple_diagnose():
    """简化诊断 - 只检查核心问题"""
    print("=" * 60)
    print("MyQuant 数据完整性快速诊断")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    from myquant.core.market.adapters import get_adapter
    from myquant.core.market.services.hotdb_service import get_hotdb_service

    hotdb = get_adapter('hotdb')
    hotdb_service = get_hotdb_service()

    if not hotdb or not hotdb.is_available():
        print("[X] HotDB 不可用")
        return

    print("[OK] HotDB 连接正常")
    print()

    # 诊断每个股票
    all_issues = []

    for symbol in SYMBOLS:
        print(f"\n【{symbol}】")
        print("-" * 40)

        # 1. 检查日线数据
        try:
            df_dict = hotdb.get_kline(symbols=[symbol], period='1d', count=100)
            df = df_dict.get(symbol)

            if df is None or df.empty:
                print("  [X] 日线: 无数据")
                all_issues.append(f"{symbol}/1d: 无数据")
                continue

            latest = df['datetime'].iloc[-1]
            days_behind = (datetime.now() - pd.to_datetime(latest)).days

            status = "[OK]" if days_behind <= 1 else "[X]"
            print(f"  {status} 日线: {len(df)}条, 最新:{latest}, 落后{days_behind}天")

            if days_behind > 1:
                all_issues.append(f"{symbol}/1d: 落后{days_behind}天")

            # 检测缺口
            if len(df) >= 2:
                df_sorted = df.sort_values('datetime')
                dates = pd.to_datetime(df_sorted['datetime']).dt.date.tolist()
                gaps = []

                for i in range(1, len(dates)):
                    gap_days = (dates[i] - dates[i-1]).days
                    if gap_days > 3:  # 超过3天视为缺口
                        gaps.append(f"{dates[i-1]}~{dates[i]}({gap_days}天)")

                if gaps:
                    print(f"  [X] 发现{len(gaps)}个缺口:")
                    for g in gaps[:3]:
                        print(f"      - {g}")
                    all_issues.append(f"{symbol}/1d: {len(gaps)}个缺口")

        except Exception as e:
            print(f"  [X] 日线诊断失败: {e}")
            all_issues.append(f"{symbol}/1d: 异常-{e}")

        # 2. 检查智能更新机制
        try:
            gap_info = hotdb_service._detect_gap(symbol, '1d')

            if gap_info and gap_info.get('has_gap'):
                reason = gap_info.get('reason', 'unknown')
                print(f"  [X] 缺口检测: {reason}")
                all_issues.append(f"{symbol}: 缺口检测报警-{reason}")
            else:
                print(f"  [OK] 缺口检测: 正常")

        except Exception as e:
            print(f"  [X] 缺口检测失败: {e}")

    # 汇总
    print("\n" + "=" * 60)
    print("诊断汇总")
    print("=" * 60)

    if all_issues:
        print(f"\n发现 {len(all_issues)} 个问题:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n[OK] 未发现明显问题")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    simple_diagnose()
