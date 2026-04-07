"""检查中国长城 000066.SZ 3-26 数据"""
from myquant.core.market.adapters import get_adapter
import pandas as pd

# 从不同数据源获取
print("=== 检查中国长城 000066.SZ 3-26 数据 ===")

# 1. XtQuant（在线）
try:
    xt = get_adapter('xtquant')
    if xt and xt.is_available():
        df = xt.get_kline(
            symbols=['000066.SZ'],
            period='1d',
            count=5,
            start_date='20260326',
            end_date='20260326'
        )
        if '000066.SZ' in df and not df['000066.SZ'].empty:
            print("\n【XtQuant 在线源】")
            print(df['000066.SZ'][['datetime', 'open', 'high', 'low', 'close', 'volume']])
        else:
            print("\n【XtQuant】无数据")
except Exception as e:
    print(f"\n【XtQuant】错误: {e}")

# 2. HotDB（本地缓存）
try:
    hotdb = get_adapter('hotdb')
    if hotdb and hotdb.is_available():
        df = hotdb.get_kline(
            symbols=['000066.SZ'],
            period='1d',
            count=5,
            start_date='20260326',
            end_date='20260326'
        )
        if '000066.SZ' in df and not df['000066.SZ'].empty:
            print("\n【HotDB 本地缓存】")
            print(df['000066.SZ'][['datetime', 'open', 'high', 'low', 'close', 'volume']])
        else:
            print("\n【HotDB】无数据")
except Exception as e:
    print(f"\n【HotDB】错误: {e}")

# 3. PyTdx（在线备用）
try:
    pytdx = get_adapter('pytdx')
    if pytdx and pytdx.is_available():
        df = pytdx.get_kline(
            symbols=['000066.SZ'],
            period='1d',
            count=5,
            start_date='20260326',
            end_date='20260326'
        )
        if '000066.SZ' in df and not df['000066.SZ'].empty:
            print("\n【PyTdx 在线源】")
            print(df['000066.SZ'][['datetime', 'open', 'high', 'low', 'close', 'volume']])
        else:
            print("\n【PyTdx】无数据")
except Exception as e:
    print(f"\n【PyTdx】错误: {e}")
