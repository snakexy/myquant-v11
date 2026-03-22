import sys
sys.path.insert(0, 'e:\MyQuant_v10.0.0\backend')
from xtquant import xtdata
import time

symbol = '600519.SH'

print("="*80)
print("XtQuant L3 K线在线获取性能测试")
print("="*80)

tests = [
    ('1d', 30),
    ('1d', 100),
    ('1d', 500),
    ('1d', 1000),
]

for period, count in tests:
    print(f"\n[{period} x {count条}]")
    try:
        start = time.time()
        data = xtdata.get_market_data_ex(
            field_list=['open', 'high', 'low', 'close', 'volume'],
            stock_list=[symbol],
            period=period,
            count=count,
            dividend_type='none'
        )
        elapsed = (time.time() - start) * 1000
        
        if data and symbol in data:
            df = data[symbol]
            print(f"  耗时: {elapsed:.2f}ms")
            print(f"  获取: {len(df)}条")
            if len(df) > 0:
                print(f"  平均: {elapsed/len(df):.2f}ms/条")
        else:
            print(f"  无数据")
    except Exception as e:
        print(f"  错误: {e}")
