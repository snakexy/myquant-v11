"""清除缓存并重新获取000066.SZ数据"""
import sys
sys.path.insert(0, 'src')

from myquant.core.market.services import get_seamless_kline_service

service = get_seamless_kline_service()

# 清除所有000066.SZ的缓存
for key in list(service._kline_cache._cache.keys()):
    if '000066.SZ' in key:
        print(f"清除缓存: {key}")
        service._kline_cache.delete(key)

print("缓存已清除")

# 获取不复权数据
print("\n=== 重新获取不复权数据 ===")
df_none = service.get_kline('000066.SZ', '1d', 5, '20260326', '20260326', adjust_type='none')
if not df_none.empty:
    print(df_none[['datetime', 'open', 'high', 'low', 'close', 'volume']])
else:
    print("无数据")

# 获取前复权数据
print("\n=== 重新获取前复权数据 ===")
df_qfq = service.get_kline('000066.SZ', '1d', 5, '20260326', '20260326', adjust_type='front')
if not df_qfq.empty:
    print(df_qfq[['datetime', 'open', 'high', 'low', 'close', 'volume']])
else:
    print("无数据")
