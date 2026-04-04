#!/usr/bin/env python3
"""详细检查中国人寿数据问题"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '601628.SH'

print("=" * 60)
print(f"检查 {symbol} 数据问题（详细）")
print("=" * 60)

hotdb = get_adapter('hotdb')

# 获取日线数据
print("\n【日线数据 - 最近30条】")
df_dict = hotdb.get_kline([symbol], period='1d', count=30, allow_stale=True)
if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].sort_values('datetime')
    print(df[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_string())
    
    # 检查是否有重复日期
    print("\n\n【检查重复日期】")
    df['date_str'] = df['datetime'].astype(str)
    duplicates = df[df.duplicated(subset=['date_str'], keep=False)]
    if not duplicates.empty:
        print("⚠️ 发现重复日期:")
        print(duplicates[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_string())
    else:
        print("✓ 无重复日期")
    
    # 检查最后一条数据是否异常
    print("\n\n【检查最后一条数据】")
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    print(f"倒数第二条: {prev_row['datetime']}, 收盘={prev_row['close']}, 成交量={prev_row['volume']}")
    print(f"倒数第一条: {last_row['datetime']}, 收盘={last_row['close']}, 成交量={last_row['volume']}")
    
    # 检查成交量差异
    vol_ratio = last_row['volume'] / prev_row['volume'] if prev_row['volume'] > 0 else 0
    price_diff = abs(last_row['close'] - prev_row['close']) / prev_row['close'] * 100 if prev_row['close'] > 0 else 0
    
    print(f"\n成交量比例: {vol_ratio:.1f}x")
    print(f"收盘价变动: {price_diff:.2f}%")
    
    if vol_ratio > 10 or price_diff > 20:
        print("⚠️ 最后一条数据可能异常！")
        
    # 检查是否有月线数据
    print("\n\n【对比：月线数据】")
    df_dict_month = hotdb.get_kline([symbol], period='1M', count=5, allow_stale=True)
    if symbol in df_dict_month and not df_dict_month[symbol].empty:
        df_month = df_dict_month[symbol].sort_values('datetime')
        print(df_month[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_string())
        
        # 对比最后一条日线和月线
        last_month = df_month.iloc[-1]
        print(f"\n最后一条月线: {last_month['datetime']}, 收盘={last_month['close']}, 成交量={last_month['volume']}")
        
        if abs(last_row['volume'] - last_month['volume']) < 1000:
            print("⚠️ 最后一条日线成交量与月线相同！确认月线数据混入了日线！")
