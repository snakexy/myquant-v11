#!/usr/bin/env python3
"""清除 000001.SZ 的 5分钟数据，以便用修复后的逻辑重新预热"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.services.hotdb_service import HotDBService

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print(f"清除 {symbol} 的 {period} 数据")
print("=" * 60)

service = HotDBService()

# 先检查当前状态
print("\n1. 清除前状态:")
status_before = service.has_symbol(symbol)
print(f"   股票存在: {status_before}")

# 清除数据
print(f"\n2. 执行清除 {symbol} {period}...")
result = service.delete_symbol(symbol, period)

if result.get('success'):
    print(f"   [OK] 清除成功: {result.get('message', '完成')}")
else:
    print(f"   [警告] 清除结果: {result.get('error', '未知')}")

# 验证清除后状态
print("\n3. 清除后验证:")
hotdb = service._get_hotdb_adapter()
df_dict = hotdb.get_kline([symbol], period=period, count=5)

if symbol in df_dict and not df_dict[symbol].empty:
    print(f"   警告: 数据仍然存在 ({len(df_dict[symbol])} 条)")
else:
    print(f"   [OK] 数据已清除")

print("\n" + "=" * 60)
print("下一步操作:")
print("1. 重新预热该股票的5分钟数据")
print("2. 或者等待系统自动通过智能更新获取")
print("=" * 60)
