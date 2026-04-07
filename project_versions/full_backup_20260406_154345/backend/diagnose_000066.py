"""诊断000066.SZ 3-26数据问题"""
import sys
sys.path.insert(0, 'src')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000066.SZ'
target_date = '2026-03-26'

print(f"=== 诊断 {symbol} {target_date} 数据问题 ===\n")

# 1. HotDB原始数据
print("【1. HotDB 原始数据】")
hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    try:
        df = hotdb.get_kline([symbol], '1d', 5, '20260326', '20260326')
        if symbol in df and not df[symbol].empty:
            print(df[symbol][['datetime', 'open', 'high', 'low', 'close', 'volume']])
        else:
            print("HotDB 无数据")
    except Exception as e:
        print(f"HotDB 错误: {e}")
else:
    print("HotDB 不可用")

# 2. TdxQuant原始数据
print("\n【2. TdxQuant 原始数据】")
tdx = get_adapter('tdxquant')
if tdx and tdx.is_available():
    try:
        df = tdx.get_kline([symbol], '1d', 5, '20260326', '20260326')
        if symbol in df and not df[symbol].empty:
            print(df[symbol][['datetime', 'open', 'high', 'low', 'close', 'volume']])
        else:
            print("TdxQuant 无数据")
    except Exception as e:
        print(f"TdxQuant 错误: {e}")
else:
    print("TdxQuant 不可用")

# 3. PyTdx原始数据
print("\n【3. PyTdx 原始数据】")
pytdx = get_adapter('pytdx')
if pytdx and pytdx.is_available():
    try:
        df = pytdx.get_kline([symbol], '1d', 5, '20260326', '20260326')
        if symbol in df and not df[symbol].empty:
            print(df[symbol][['datetime', 'open', 'high', 'low', 'close', 'volume']])
        else:
            print("PyTdx 无数据")
    except Exception as e:
        print(f"PyTdx 错误: {e}")
else:
    print("PyTdx 不可用")

# 4. 检查除权除息记录
print("\n【4. 检查除权除息记录】")
from myquant.core.market.services import get_seamless_kline_service
service = get_seamless_kline_service()
xdxr_list = service._get_xdxr_data(symbol)
if xdxr_list:
    print(f"找到 {len(xdxr_list)} 条除权除息记录:")
    for xdxr in xdxr_list[-5:]:  # 显示最近5条
        print(f"  {xdxr}")
else:
    print("无除权除息记录")

print("\n=== 诊断完成 ===")
