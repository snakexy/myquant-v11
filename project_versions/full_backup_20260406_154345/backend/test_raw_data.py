"""直接测试TdxQuant获取000066.SZ的3-26数据"""
import sys
sys.path.insert(0, 'src')

from myquant.core.market.adapters import get_adapter

print("=== 测试 TdxQuant 原始数据 ===")
tdx = get_adapter('tdxquant')
if tdx and tdx.is_available():
    try:
        df = tdx.get_kline(['000066.SZ'], '1d', 5, '20260326', '20260326')
        if '000066.SZ' in df and not df['000066.SZ'].empty:
            print("TdxQuant 返回的3-26数据:")
            print(df['000066.SZ'])
        else:
            print("TdxQuant 无数据")
    except Exception as e:
        print(f"TdxQuant 错误: {e}")
else:
    print("TdxQuant 不可用")

print("\n=== 测试 HotDB 原始数据 ===")
hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    try:
        df = hotdb.get_kline(['000066.SZ'], '1d', 5, '20260326', '20260326')
        if '000066.SZ' in df and not df['000066.SZ'].empty:
            print("HotDB 返回的3-26数据:")
            print(df['000066.SZ'][['datetime', 'open', 'high', 'low', 'close', 'volume']])
        else:
            print("HotDB 无数据")
    except Exception as e:
        print(f"HotDB 错误: {e}")
else:
    print("HotDB 不可用")
