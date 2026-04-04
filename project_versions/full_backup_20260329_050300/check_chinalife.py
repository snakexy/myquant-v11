#!/usr/bin/env python3
"""检查中国人寿数据问题"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '601628.SH'  # 中国人寿

print("=" * 60)
print(f"检查 {symbol} 数据问题")
print("=" * 60)

hotdb = get_adapter('hotdb')

# 检查日线数据
print("\n【日线数据】")
df_dict_1d = hotdb.get_kline([symbol], period='1d', count=20, allow_stale=True)
if symbol in df_dict_1d and not df_dict_1d[symbol].empty:
    df_1d = df_dict_1d[symbol].sort_values('datetime')
    print(f"最近{len(df_1d)}条日线数据:")
    print(df_1d[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_string())
    
    # 检查数据间隔
    df_1d['date'] = pd.to_datetime(df_1d['datetime'])
    df_1d['prev_date'] = df_1d['date'].shift(1)
    df_1d['interval_days'] = (df_1d['date'] - df_1d['prev_date']).dt.days
    
    print("\n日期间隔分析:")
    print(df_1d[['datetime', 'interval_days']].to_string())
    
    # 检查是否有月级别的间隔
    monthly_gaps = df_1d[df_1d['interval_days'] > 25]
    if not monthly_gaps.empty:
        print("\n⚠️ 发现月级间隔！数据可能是月线的:")
        print(monthly_gaps[['datetime', 'interval_days']].to_string())
else:
    print("无日线数据")

# 对比其他股票（如平安银行）
print("\n\n" + "=" * 60)
print("对比：平安银行 000001.SZ 日线数据")
print("=" * 60)
df_dict_pab = hotdb.get_kline(['000001.SZ'], period='1d', count=10, allow_stale=True)
if '000001.SZ' in df_dict_pab and not df_dict_pab['000001.SZ'].empty:
    df_pab = df_dict_pab['000001.SZ'].sort_values('datetime')
    print(df_pab[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_string())
    
    # 检查间隔
    df_pab['date'] = pd.to_datetime(df_pab['datetime'])
    df_pab['prev_date'] = df_pab['date'].shift(1)
    df_pab['interval_days'] = (df_pab['date'] - df_pab['prev_date']).dt.days
    print("\n日期间隔:")
    print(df_pab[['datetime', 'interval_days']].to_string())
