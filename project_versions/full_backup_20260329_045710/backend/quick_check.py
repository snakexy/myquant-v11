#!/usr/bin/env python3
"""快速验证volume单位"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'
period = '5m'

hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period=period, count=10000, allow_stale=True)

if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol].sort_values('datetime')

    # March 9
    march_9 = df[df['datetime'].between('2026-03-09 09:30:00', '2026-03-09 15:00:00')]
    if not march_9.empty:
        vol = march_9['volume'].iloc[0]
        print(f"March 9 first volume: {vol:,.0f}")
        if vol > 1000000:
            print("STATUS: STILL IN SHARES (股)")
        else:
            print("STATUS: CORRECT (手)")

    # March 16
    march_16 = df[df['datetime'].between('2026-03-16 09:30:00', '2026-03-16 15:00:00')]
    if not march_16.empty:
        vol = march_16['volume'].iloc[0]
        print(f"March 16 first volume: {vol:,.0f}")
        if vol > 1000000:
            print("STATUS: STILL IN SHARES (股)")
        else:
            print("STATUS: CORRECT (手)")

    # Latest
    latest = df.iloc[-1]
    print(f"Latest volume ({latest['datetime']}): {latest['volume']:,.0f}")
