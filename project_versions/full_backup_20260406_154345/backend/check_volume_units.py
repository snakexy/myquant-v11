"""
检查 300046.SZ 各周期成交量单位
"""

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = "300046.SZ"
periods = ['1m', '5m', '15m', '30m', '1h', '1d', '1w']

print(f"\n{'='*70}")
print(f"检查 {symbol} 各周期成交量")
print(f"{'='*70}\n")

# 检查 HotDB 数据
hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    print(f"[HotDB] 各周期最新数据成交量:")
    print(f"{'周期':<8} {'成交量':>15} {'说明':>30}")
    print(f"{'-'*70}")

    for period in periods:
        try:
            df_dict = hotdb.get_kline(symbols=[symbol], period=period, count=1)
            if symbol in df_dict and not df_dict[symbol].empty:
                df = df_dict[symbol]
                volume = int(df['volume'].iloc[-1])
                print(f"{period:<8} {volume:>15} {'HotDB 最新一条数据':>30}")
        except Exception as e:
            print(f"{period:<8} {'获取失败':>15} {str(e):>30}")

print(f"\n{'='*70}\n")

# 检查在线源原始数据（未转换）
print(f"[在线源 PyTdx] 原始数据（未转换）:")
print(f"{'周期':<8} {'成交量':>15} {'说明':>30}")
print(f"{'-'*70}")

pytdx = get_adapter('pytdx')
if pytdx and pytdx.is_available():
    for period in ['5m', '1d', '1w']:  # 只检查几个典型周期
        try:
            df_dict = pytdx.get_kline(symbols=[symbol], period=period, count=1)
            if symbol in df_dict and not df_dict[symbol].empty:
                df = df_dict[symbol]
                volume_raw = int(df['volume'].iloc[-1])
                print(f"{period:<8} {volume_raw:>15} {'PyTdx 返回原始值':>30}")
        except Exception as e:
            print(f"{period:<8} {'获取失败':>15} {str(e):>30}")

print(f"\n{'='*70}\n")

# 检查 LocalDB 数据
print(f"[LocalDB] 各周期最新数据成交量:")
print(f"{'周期':<8} {'成交量':>15} {'说明':>30}")
print(f"{'-'*70}")

localdb = get_adapter('localdb')
if localdb and localdb.is_available():
    for period in ['5m', '1d']:  # 只检查几个典型周期
        try:
            df_dict = localdb.get_kline(symbols=[symbol], period=period, count=1)
            if symbol in df_dict and not df_dict[symbol].empty:
                df = df_dict[symbol]
                volume = int(df['volume'].iloc[-1])
                print(f"{period:<8} {volume:>15} {'LocalDB 数据':>30}")
        except Exception as e:
            print(f"{period:<8} {'获取失败':>15} {str(e):>30}")

print(f"{'='*70}\n")

# 分析：如果 HotDB 的值是 PyTdx 的 1/100，说明被错误转换了
print(f"[分析] 成交量单位规则:")
print(f"  - LocalDB: 手（不需要 ÷100）")
print(f"  - PyTdx 分钟线/日线: 股（需要 ÷100 转换为手）")
print(f"  - PyTdx 周线/月线: 手（不需要转换）")
print(f"{'='*70}\n")
