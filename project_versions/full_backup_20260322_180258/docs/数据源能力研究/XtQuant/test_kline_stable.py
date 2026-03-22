import sys
sys.path.insert(0, 'e:\MyQuant_v10.0.0\backend')
from xtquant import xtdata
import time

symbol = '600519.SH'

# 预热连接
xtdata.get_market_data_ex(
    field_list=['close'],
    stock_list=[symbol],
    period='1d',
    count=10,
    dividend_type='none'
)

print("="*80)
print("XtQuant L3 K线稳定性能测试 (已连接)")
print("="*80)

# 测试多次调用
for i in range(5):
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
        print(f"第{i+1}次: {elapsed:.2f}ms ({len(df)}条)")
