"""
诊断脚本：测试K线数据流
"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend/src')

from myquant.core.market.services import get_seamless_kline_service
from myquant.core.market.routing import DataLevel, get_source_selector
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=== 测试1: 检查Selector ===")
selector = get_source_selector()
chain = selector.get_fallback_chain_for_code(DataLevel.L3, '000858.SZ')
print(f"L3 fallback chain for 000858.SZ: {chain}")

print("\n=== 测试2: 直接调用Adapter ===")
from myquant.core.market.adapters import get_adapter

xtquant = get_adapter('xtquant')
print(f"XtQuant available: {xtquant.is_available() if xtquant else False}")

if xtquant and xtquant.is_available():
    result = xtquant.get_kline(['000858.SZ'], period='1d', count=10)
    print(f"XtQuant result: {list(result.keys())}")
    if result and '000858.SZ' in result:
        df = result['000858.SZ']
        print(f"Data shape: {df.shape}")
    else:
        print("No data from XtQuant")

print("\n=== 测试3: 调用Seamless Service ===")
service = get_seamless_kline_service()
print(f"Service instance: {service}")

try:
    df = service.get_kline('000858.SZ', period='1d', count=10)
    print(f"Service returned: {type(df)}")
    if df is not None and not df.empty:
        print(f"Data shape: {df.shape}")
        print(df.head())
    else:
        print("Empty data returned")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 完成 ===")
