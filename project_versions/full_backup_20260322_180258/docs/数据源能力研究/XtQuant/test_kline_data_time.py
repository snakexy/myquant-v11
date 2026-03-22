import sys
sys.path.insert(0, 'e:\MyQuant_v10.0.0\backend')
from xtquant import xtdata
import time

symbol = '600519.SH'

print("="*80)
print("XtQuant L3 K线数据时间范围测试")
print("="*80)

# 获取500条日K线
start = time.time()
data = xtdata.get_market_data_ex(
    field_list=['open', 'high', 'low', 'close', 'volume'],
    stock_list=[symbol],
    period='1d',
    count=500,
    dividend_type='none'
)
elapsed = (time.time() - start) * 1000

if data and symbol in data:
    df = data[symbol]
    print(f"耗时: {elapsed:.2f}ms")
    print(f"获取: {len(df)}条")
    print(f"最新: {df.index[-1]}, 收盘: {df['close'].iloc[-1]}")
    print(f"最旧: {df.index[0]}, 收盘: {df['close'].iloc[0]}")
    print(f"\n最新5条:")
    for i in range(-1, -6, -1) if len(df) >= 5 else range(-1, -len(df)-1, -1):
        print(f"  {df.index[i]}: close={df['close'].iloc[i]}")
else:
    print("无数据")
