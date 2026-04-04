#!/usr/bin/env python3
"""测试完整的周K/月K获取流程"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.services.hotdb_service import HotDBService

symbol = '000001.SZ'

print("=" * 60)
print("测试周K/月K完整获取流程")
print("=" * 60)

service = HotDBService()

# 清除现有的周K和月K数据（如果有）
print("\n1. 清除现有数据...")
hotdb = service._get_hotdb_adapter()
for period in ['1w', '1mon']:
    hotdb.delete_kline(symbol, period)
    print(f"   清除 {period} 数据")

# 测试 smart_update 获取周K
print("\n2. 测试获取周K...")
result = service.smart_update(symbol, '1w')
print(f"   成功: {result.get('success')}")
print(f"   有数据: {result.get('has_data')}")
print(f"   有缺口: {result.get('has_gap')}")
print(f"   原因: {result.get('reason')}")
if result.get('df') is not None:
    df = result['df']
    print(f"   获取条数: {len(df)}")
    if not df.empty:
        print(f"   最早日期: {df['datetime'].iloc[0]}")
        print(f"   最晚日期: {df['datetime'].iloc[-1]}")

# 测试 smart_update 获取月K
print("\n3. 测试获取月K...")
result = service.smart_update(symbol, '1mon')
print(f"   成功: {result.get('success')}")
print(f"   有数据: {result.get('has_data')}")
print(f"   有缺口: {result.get('has_gap')}")
print(f"   原因: {result.get('reason')}")
if result.get('df') is not None:
    df = result['df']
    print(f"   获取条数: {len(df)}")
    if not df.empty:
        print(f"   最早日期: {df['datetime'].iloc[0]}")
        print(f"   最晚日期: {df['datetime'].iloc[-1]}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)