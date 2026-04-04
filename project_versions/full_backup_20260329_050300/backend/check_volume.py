#!/usr/bin/env python3
"""检查TdxQuant和PyTdx的volume数据"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("检查TdxQuant原始数据")
print("=" * 60)

tdx = get_adapter('tdxquant')
if tdx and tdx._ensure_initialized():
    # 获取原始数据
    tdx_raw = tdx._tq.get_market_data(
        stock_list=[symbol],
        period='5m',
        start_time='',
        end_time='',
        count=5,
        dividend_type='none'
    )

    print("\n原始数据结构:")
    for field, data in list(tdx_raw.items())[:10]:
        if hasattr(data, 'iloc'):
            print(f"  {field}: {data.iloc[:3, 0].values}")

    # 获取标准化后的K线
    df_dict = tdx.get_kline([symbol], period=period, count=5)
    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        print(f"\n标准化后的K线 (TdxQuant):")
        print(df[['volume', 'amount', 'open', 'close']].to_string())
        print(f"\n索引 (datetime): {df.index}")
else:
    print("TdxQuant不可用")

print("\n" + "=" * 60)
print("检查PyTdx数据")
print("=" * 60)

pytdx = get_adapter('pytdx_pool')
if pytdx and pytdx._ensure_pool():
    df_dict = pytdx.get_kline([symbol], period=period, count=5)
    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        print("\n标准化后的K线 (PyTdx):")
        print(df[['volume', 'amount', 'open', 'close']].to_string())

        # 显示原始vol值
        print("\n确认PyTdx原始数据中的vol字段:")
        print(f"  最后一条volume: {df['volume'].iloc[-1]:,.2f}")
else:
    print("PyTdx不可用")

print("\n" + "=" * 60)
print("检查HotDB存储的数据")
print("=" * 60)

hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period=period, count=5)
if symbol in df_dict and not df_dict[symbol].empty:
    df = df_dict[symbol]
    print("\nHotDB中的K线数据:")
    print(df[['volume', 'open', 'close']].to_string())
    print(f"\n  最后一条volume: {df['volume'].iloc[-1]:,.2f}")
else:
    print("HotDB中没有数据")
