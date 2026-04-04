#!/usr/bin/env python3
"""清除000001.SZ的日线数据并重新预热"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.services.hotdb_service import HotDBService

symbol = '000001.SZ'
period = '1d'

print("=" * 60)
print(f"清除 {symbol} 的 {period} 数据")
print("=" * 60)

service = HotDBService()

# 清除数据
print(f"\n执行清除 {symbol} {period}...")
result = service.delete_symbol(symbol, period)

if result.get('success'):
    print(f"   [OK] 清除成功")
else:
    print(f"   [警告] 清除结果: {result.get('error', '未知')}")

# 验证清除
print("\n清除后验证:")
hotdb = service._get_hotdb_adapter()
df_dict = hotdb.get_kline([symbol], period=period, count=5)

if symbol in df_dict and not df_dict[symbol].empty:
    print(f"   警告: 数据仍然存在 ({len(df_dict[symbol])} 条)")
else:
    print(f"   [OK] 数据已清除")

print("\n" + "=" * 60)
print("下一步: 重新预热日线数据")
print("=" * 60)