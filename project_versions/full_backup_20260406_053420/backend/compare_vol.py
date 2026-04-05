"""对比 HotDB、LocalDB、PyTdx 的成交量"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '300046.SZ'
period = '5m'
count = 3

print("=" * 70)
print(f"对比 {symbol} {period} 成交量单位")
print("=" * 70)

# HotDB
hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    df = hotdb.get_kline(symbols=[symbol], period=period, count=count)
    if symbol in df and not df[symbol].empty:
        d = df[symbol].sort_values('datetime', ascending=False)
        print(f"\n[HotDB] 最新 {count} 条:")
        for _, row in d.iterrows():
            print(f"  {row['datetime']}  volume={int(row['volume']):>10} 手")

# LocalDB
localdb = get_adapter('localdb')
if localdb and localdb.is_available():
    df = localdb.get_kline(symbols=[symbol], period=period, count=count)
    if symbol in df and not df[symbol].empty:
        d = df[symbol].sort_values('datetime', ascending=False).head(count)
        print(f"\n[LocalDB] 最新 {count} 条:")
        for _, row in d.iterrows():
            print(f"  {row['datetime']}  volume={int(row['volume']):>10} 手")

# PyTdx (原始数据，单位是股)
pytdx = get_adapter('pytdx')
if pytdx and pytdx.is_available():
    df = pytdx.get_kline(symbols=[symbol], period=period, count=count)
    if symbol in df and not df[symbol].empty:
        d = df[symbol].sort_values('datetime', ascending=False).head(count)
        print(f"\n[PyTdx] 原始数据（单位：股，需÷100转手）:")
        for _, row in d.iterrows():
            vol_shares = int(row['volume'])
            vol_lots = vol_shares / 100
            print(f"  {row['datetime']}  volume={vol_shares:>10} 股 = {vol_lots:>10.1f} 手")

print("\n" + "=" * 70)
print("分析：HotDB 应该 = PyTdx/100，LocalDB 应该 = HotDB")
print("=" * 70)
