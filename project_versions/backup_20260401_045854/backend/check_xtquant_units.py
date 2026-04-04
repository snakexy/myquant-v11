#!/usr/bin/env python3
"""验证XtQuant返回的volume单位"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'

print("=" * 60)
print("验证XtQuant返回的volume单位")
print("=" * 60)

# 获取XtQuant适配器
xtquant = get_adapter('xtquant')
if xtquant and xtquant.is_available():
    # 获取5分钟数据
    df_dict_5m = xtquant.get_kline([symbol], period='5m', count=10)
    if symbol in df_dict_5m and not df_dict_5m[symbol].empty:
        df_5m = df_dict_5m[symbol]
        vol_5m = df_5m['volume'].iloc[-1]
        print(f"\nXtQuant 5m volume样本: {vol_5m:,.0f}")
        if vol_5m > 1000000:
            print("(股单位 - 数值过大)")
        else:
            print("(手单位 - 正常)")

    # 获取日线数据
    df_dict_1d = xtquant.get_kline([symbol], period='1d', count=10)
    if symbol in df_dict_1d and not df_dict_1d[symbol].empty:
        df_1d = df_dict_1d[symbol]
        vol_1d = df_1d['volume'].iloc[-1]
        print(f"\nXtQuant 1d volume样本: {vol_1d:,.0f}")
        if vol_1d > 10000000:
            print("(股单位 - 数值过大)")
        else:
            print("(手单位 - 正常)")
else:
    print("XtQuant不可用")

# 对比HotDB中的数据
print("\n" + "=" * 60)
print("对比HotDB中的数据:")
print("=" * 60)

hotdb = get_adapter('hotdb')
for period in ['5m', '1d']:
    df_dict = hotdb.get_kline([symbol], period=period, count=5, allow_stale=True)
    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        vol = df['volume'].iloc[-1]
        print(f"\nHotDB {period} volume: {vol:,.0f}")
        if vol > 1000000:
            print("(股单位 - 未转换)")
        else:
            print("(手单位 - 已转换)")
