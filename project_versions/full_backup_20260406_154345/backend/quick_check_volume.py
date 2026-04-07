"""
快速检查 300046.SZ 5m 成交量问题
"""

from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.hotdb_service import get_hotdb_service
import pandas as pd

symbol = "300046.SZ"
period = "5m"

print(f"\n{'='*70}")
print(f"检查 {symbol} {period} 成交量单位问题")
print(f"{'='*70}\n")

# 1. 检查 HotDB 最新几条数据
hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    df_dict = hotdb.get_kline(symbols=[symbol], period=period, count=5)
    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        print(f"[HotDB] 最新5条数据:")
        for idx, row in df.iterrows():
            print(f"  {row['datetime']}  成交量: {int(row['volume']):>10} 手")

# 2. 检查 LocalDB 最新几条数据
localdb = get_adapter('localdb')
if localdb and localdb.is_available():
    df_dict = localdb.get_kline(symbols=[symbol], period=period, count=5)
    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        df = df.sort_values('datetime', ascending=False).head(5)
        print(f"\n[LocalDB] 最新5条数据:")
        for idx, row in df.iterrows():
            print(f"  {row['datetime']}  成交量: {int(row['volume']):>10} 手")

# 3. 检查 PyTdx 原始数据（未转换）
pytdx = get_adapter('pytdx')
if pytdx and pytdx.is_available():
    df_dict = pytdx.get_kline(symbols=[symbol], period=period, count=5)
    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        print(f"\n[PyTdx] 原始数据（未转换）:")
        for idx, row in df.iterrows():
            print(f"  {row['datetime']}  成交量: {int(row['volume']):>10} 股（需要÷100=手）")
            print(f"            转换后: {int(row['volume'])/100:>10.1f} 手")

print(f"\n{'='*70}")
print(f"[分析]")
print(f"  如果 HotDB 成交量 = PyTdx 成交量/100  → 单位正确")
print(f"  如果 HotDB 成交量 = LocalDB 成交量  → 单位正确")
print(f"  如果不一致 → 说明有地方转换错误")
print(f"{'='*70}\n")
