"""
测试茅台复权因子计算 - 独立测试（不依赖TdxQuant）
"""
import sys
sys.path.insert(0, 'backend/src')

import pandas as pd
from myquant.core.market.services.adjustment_factor_service import AdjustmentFactorService

print("=" * 70)
print("茅台复权因子独立测试")
print("=" * 70)

# 模拟茅台XDXR数据（2025年12月19日除权，每10股派23.957元）
maotai_xdxr = [
    {'year': 2025, 'month': 12, 'day': 19, 'category': 1, 'fenhong': 23.957, 'songzhuangu': 0.0, 'peigu': 0.0, 'peigujia': 0.0},
]

# 创建服务并计算因子
service = AdjustmentFactorService()
factor_table = service._calculate_front_factors(maotai_xdxr)

print("\n=== 因子表 ===")
for date in ['2025-12-17', '2025-12-18', '2025-12-19', '2025-12-20']:
    factor = factor_table.get(date, 999)
    print(f'{date}: {factor:.6f}')

# 模拟K线数据
test_klines = pd.DataFrame([
    {'datetime': '2025-12-18', 'open': 1410.0, 'high': 1420.0, 'low': 1400.0, 'close': 1410.0},
    {'datetime': '2025-12-19', 'open': 1410.0, 'high': 1425.0, 'low': 1405.0, 'close': 1410.0},
])

print("\n=== 原始K线 ===")
print(test_klines[['datetime', 'close']])

# 应用复权
result = service.apply_factors(test_klines, factor_table)

print("\n=== 复权后K线 ===")
print(result[['datetime', 'close']])

# 验证
price_1218 = result[result['datetime'] == '2025-12-18']['close'].values[0]
price_1219 = result[result['datetime'] == '2025-12-19']['close'].values[0]

print("\n=== 验证 ===")
print(f"2025-12-18: {price_1218:.2f} (预期约1393)")
print(f"2025-12-19: {price_1219:.2f} (预期1410.00)")

if abs(price_1219 - 1410.0) < 0.01:
    print("\n✅ 除权日复权正确！除权日价格保持不变")
else:
    print(f"\n❌ 除权日复权错误！价格是 {price_1219:.2f}，应为 1410.00")
