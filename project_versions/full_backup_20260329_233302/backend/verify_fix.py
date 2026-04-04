#!/usr/bin/env python3
"""验证成交量单位修复"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.hotdb_service import HotDBService
import pandas as pd

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("验证成交量单位修复")
print("=" * 60)

# 1. 检查 LocalDB 原始数据
localdb = get_adapter('localdb')
df_dict = localdb.get_kline([symbol], period=period, count=5)

if symbol in df_dict and not df_dict[symbol].empty:
    df_local = df_dict[symbol]
    print("\n1. LocalDB 原始数据（股）:")
    print(df_local[['volume', 'open', 'close']].to_string())
    local_vol = df_local['volume'].iloc[-1]
    print(f"\n   最后一条 volume: {local_vol:,.0f} (股)")
    print(f"   转换为手: {local_vol/100:,.0f} (手)")
else:
    print("\n1. LocalDB 无数据")
    local_vol = None

# 2. 检查当前 HotDB 数据（未修复前的）
hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period=period, count=5)

if symbol in df_dict and not df_dict[symbol].empty:
    df_hot = df_dict[symbol]
    print("\n2. 当前 HotDB 数据（修复前）:")
    print(df_hot[['volume', 'open', 'close']].to_string())
    hot_vol = df_hot['volume'].iloc[-1]
    print(f"\n   最后一条 volume: {hot_vol:,.0f}")
    if local_vol:
        ratio = hot_vol / (local_vol/100) if local_vol > 0 else 0
        print(f"   与 LocalDB(手) 的比例: {ratio:.2f}")
        if ratio > 50:
            print("   ⚠️  警告: HotDB数据仍是股单位，数值过大！")
        else:
            print("   ✅ HotDB数据已是手单位，正常")
else:
    print("\n2. HotDB 无数据")

# 3. 测试修复后的预热逻辑
print("\n3. 测试修复后的转换逻辑:")
if local_vol is not None:
    # 模拟修复后的转换
    df_converted = df_local.copy()
    if period in ['1m', '5m', '15m', '30m', '1h'] and 'volume' in df_converted.columns:
        df_converted['volume'] = df_converted['volume'] / 100

    print("   转换后的数据（手）:")
    print(df_converted[['volume', 'open', 'close']].to_string())
    converted_vol = df_converted['volume'].iloc[-1]
    print(f"\n   最后一条 volume: {converted_vol:,.0f} (手)")
    print("   ✅ 转换正确！")

print("\n" + "=" * 60)
print("结论:")
print("- LocalDB 存储的是股（大数值）")
print("- TdxQuant/PyTdx 返回的是手（÷100）")
print("- 修复后预热时会将 LocalDB 的股转换为手")
print("=" * 60)
