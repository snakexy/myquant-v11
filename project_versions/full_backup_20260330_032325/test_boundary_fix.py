"""
验证复权因子边界修复 - 确保除权日当天不被调整
"""
import sys
sys.path.insert(0, 'backend/src')

import pandas as pd
from datetime import datetime
from myquant.core.market.services.adjustment_factor_service import AdjustmentFactorService

# 创建服务
service = AdjustmentFactorService()

# 模拟茅台的XDXR数据（2025年12月19日除权）
maotai_xdxr = [
    {'year': 2025, 'month': 12, 'day': 19, 'category': 1, 'fenhong': 23.957, 'songzhuangu': 0.0, 'peigu': 0.0, 'peigujia': 0.0},
    {'year': 2024, 'month': 6, 'day': 19, 'category': 1, 'fenhong': 30.876, 'songzhuangu': 0.0, 'peigu': 0.0, 'peigujia': 0.0},
]

print("=" * 70)
print("复权因子边界条件验证")
print("=" * 70)
print("\n分红记录：")
for record in maotai_xdxr:
    print(f"  {record['year']}-{record['month']:02d}-{record['day']:02d}: "
          f"10派{record['fenhong']}元")

# 计算因子表
factor_table = service._calculate_front_factors(maotai_xdxr)

# 检查关键日期的因子
print(f"\n关键日期因子值：")
test_dates = ['2025-12-17', '2025-12-18', '2025-12-19', '2025-12-20', '2025-12-21']
for date in test_dates:
    factor = factor_table.get(date, 1.0)
    print(f"  {date}: {factor:.6f}")

# 模拟价格数据
test_klines = [
    {'datetime': '2025-12-18', 'open': 1407.04, 'high': 1420.0, 'low': 1395.0, 'close': 1410.00},
    {'datetime': '2025-12-19', 'open': 1410.00, 'high': 1425.0, 'low': 1400.0, 'close': 1410.00},  # 除权日，应不变
]

df = pd.DataFrame(test_klines)
print("\n原始价格：")
print(df[['datetime', 'close']])

# 应用复权
df_adjusted = service.apply_factors(df, factor_table)
print("\n复权后价格：")
print(df_adjusted[['datetime', 'close']])

# 验证边界条件
print("\n" + "=" * 70)
print("边界条件检查：")
print("=" * 70)

# 获取2025-12-19的因子
factor_1219 = factor_table.get('2025-12-19', 1.0)
factor_1218 = factor_table.get('2025-12-18', 1.0)

print(f"\n2025-12-19 (除权日) 因子: {factor_1219:.6f}")
print(f"2025-12-18 (除权前) 因子: {factor_1218:.6f}")

if abs(factor_1219 - 1.0) < 0.0001:
    print("\n✅ 边界条件正确：除权日(12-19)因子为1.0（不复权）")
else:
    print(f"\n❌ 边界条件错误：除权日因子应为1.0，实际是{factor_1219:.6f}")

if factor_1218 < 1.0:
    print(f"✅ 前复权正确：除权前(12-18)因子为{factor_1218:.6f}（<1.0，价格被调低）")
else:
    print(f"❌ 前复权错误：除权前因子应<1.0，实际是{factor_1218:.6f}")

# 验证价格
price_1219 = df_adjusted[df_adjusted['datetime'] == '2025-12-19']['close'].values[0]
if abs(price_1219 - 1410.00) < 0.01:
    print(f"✅ 除权日价格正确：12-19收盘价 = {price_1219:.2f}（应为1410.00）")
else:
    print(f"❌ 除权日价格错误：12-19收盘价 = {price_1219:.2f}（应为1410.00）")

print("\n" + "=" * 70)
