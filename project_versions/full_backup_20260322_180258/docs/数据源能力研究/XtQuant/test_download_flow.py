import sys
sys.path.insert(0, 'e:\MyQuant_v10.0.0\backend')
from xtquant import xtdata
import time

symbol = '000001.SZ'

print("="*80)
print("XtQuant 下载流程验证")
print("="*80)

# 1. 首次获取（会触发下载）
print("\n[1] 首次获取1000条（触发下载）")
start = time.time()
data = xtdata.get_market_data_ex(
    field_list=['close'],
    stock_list=[symbol],
    period='1d',
    count=1000,
    dividend_type='none'
)
elapsed1 = (time.time() - start) * 1000
if data and symbol in data:
    print(f"耗时: {elapsed1:.2f}ms, 获取: {len(data[symbol])}条")

# 2. 再次获取（从本地读）
print("\n[2] 再次获取1000条（本地读取）")
start = time.time()
data = xtdata.get_market_data_ex(
    field_list=['close'],
    stock_list=[symbol],
    period='1d',
    count=1000,
    dividend_type='none'
)
elapsed2 = (time.time() - start) * 1000
if data and symbol in data:
    print(f"耗时: {elapsed2:.2f}ms, 获取: {len(data[symbol])}条")

print(f"\n结论: 首次下载耗时 {elapsed1:.2f}ms, 后续读取耗时 {elapsed2:.2f}ms")
print(f"速度提升: {elapsed1/elapsed2:.1f}倍")
