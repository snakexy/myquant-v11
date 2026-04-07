"""验证通达信本地文件的成交量单位"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = "300046.SZ"  # 台基股份

print("=" * 70)
print(f"验证 {symbol} 通达信本地文件 vs PyTdx 在线的成交量单位")
print("=" * 70)

# 1. 通达信本地文件（LocalDB）
localdb = get_adapter('localdb')
if localdb and localdb.is_available():
    # 5m
    df_5m = localdb.get_kline(symbols=[symbol], period='5m', count=3)
    if symbol in df_5m and not df_5m[symbol].empty:
        d = df_5m[symbol].sort_values('datetime', ascending=False).head(3)
        print(f"\n[通达信本地] 5m 最新3条:")
        for _, row in d.iterrows():
            print(f"  {row['datetime']}  volume={int(row['volume']):>10}")

    # 1d
    df_1d = localdb.get_kline(symbols=[symbol], period='1d', count=3)
    if symbol in df_1d and not df_1d[symbol].empty:
        d = df_1d[symbol].sort_values('datetime', ascending=False).head(3)
        print(f"\n[通达信本地] 1d 最新3条:")
        for _, row in d.iterrows():
            print(f"  {row['datetime']}  volume={int(row['volume']):>10}")

# 2. PyTdx 在线原始数据（未转换）
from pytdx2.hq import TdxHq_API

api = TdxHq_API()
if api.connect("180.153.18.172", 80):
    api.setup()

    # 5m 原始
    data_5m = api.get_security_bars(0, 0, "300046", 0, 3)
    print(f"\n[PyTdx原始] 5m 最新3条 (未转换):")
    for bar in reversed(data_5m):
        vol = bar.get('vol', 0)
        print(f"  {bar['datetime']}  vol={vol:>10} 股 → 转手后={vol/100:>10.1f} 手")

    # 1d 原始
    data_1d = api.get_security_bars(9, 0, "300046", 0, 3)
    print(f"\n[PyTdx原始] 1d 最新3条 (未转换):")
    for bar in reversed(data_1d):
        vol = bar.get('vol', 0)
        print(f"  {bar['datetime']}  vol={vol:>10} (单位：手)")

    api.disconnect()

# 3. pytdx_pool_adapter（已转换）
pytdx = get_adapter('pytdx_pool')
if pytdx and pytdx.is_available():
    df_5m = pytdx.get_kline(symbols=[symbol], period='5m', count=3)
    if symbol in df_5m and not df_5m[symbol].empty:
        d = df_5m[symbol].sort_values('datetime', ascending=False).head(3)
        print(f"\n[PyTdx适配器] 5m 最新3条 (已转换):")
        for _, row in d.iterrows():
            print(f"  {row['datetime']}  volume={int(row['volume']):>10} 手")

    df_1d = pytdx.get_kline(symbols=[symbol], period='1d', count=3)
    if symbol in df_1d and not df_1d[symbol].empty:
        d = df_1d[symbol].sort_values('datetime', ascending=False).head(3)
        print(f"\n[PyTdx适配器] 1d 最新3条 (已转换):")
        for _, row in d.iterrows():
            print(f"  {row['datetime']}  volume={int(row['volume']):>10} 手")

print("\n" + "=" * 70)
print("分析：")
print("  如果 通达信本地5m ≈ PyTdx适配器5m → 都是手")
print("  如果 通达信本地5m ≈ PyTdx原始5m/100 → 都是手")
print("  如果 通达信本地5m ≈ PyTdx原始5m → 通达信是股（需要转换）")
print("=" * 70)
