"""
复权计算修复验证 - 贵州茅台
"""

import sys
sys.path.insert(0, 'backend/src')

from myquant.core.market.services.adjustment_factor_service import AdjustmentFactorService

# 创建服务
service = AdjustmentFactorService()

# 模拟茅台的XDXR数据（2020-2024年分红送股）
maotai_xdxr = [
    {'year': 2024, 'month': 6, 'day': 19, 'category': 1, 'fenhong': 30.876, 'songzhuangu': 0.0, 'peigu': 0.0, 'peigujia': 0.0},
    {'year': 2023, 'month': 6, 'day': 30, 'category': 1, 'fenhong': 25.911, 'songzhuangu': 0.0, 'peigu': 0.0, 'peigujia': 0.0},
    {'year': 2022, 'month': 6, 'day': 24, 'category': 1, 'fenhong': 21.675, 'songzhuangu': 0.0, 'peigu': 0.0, 'peigujia': 0.0},
    {'year': 2021, 'month': 6, 'day': 18, 'category': 1, 'fenhong': 17.025, 'songzhuangu': 0.0, 'peigu': 0.0, 'peigujia': 0.0},
    {'year': 2020, 'month': 6, 'day': 24, 'category': 1, 'fenhong': 12.3, 'songzhuangu': 0.0, 'peigu': 0.0, 'peigujia': 0.0},
]

print("=" * 70)
print("贵州茅台复权因子计算验证")
print("=" * 70)
print("\n分红记录：")
for record in maotai_xdxr:
    print(f"  {record['year']}-{record['month']:02d}-{record['day']:02d}: "
          f"10派{record['fenhong']}元")

# 计算因子表
factor_table = service._calculate_front_factors(maotai_xdxr)

print(f"\n生成因子表：{len(factor_table)} 天")
print("\n最近5个交易日的因子：")
recent_dates = sorted(factor_table.keys())[-5:]
for date in recent_dates:
    print(f"  {date}: {factor_table[date]:.6f}")

# 模拟应用复权到价格
import pandas as pd

# 假设某天K线数据（不复权）
test_klines = [
    {'datetime': '2024-06-18', 'open': 1500.0, 'high': 1520.0, 'low': 1490.0, 'close': 1510.0},
    {'datetime': '2024-06-19', 'open': 1510.0, 'high': 1530.0, 'low': 1500.0, 'close': 1520.0},
    {'datetime': '2024-06-20', 'open': 1520.0, 'high': 1540.0, 'low': 1510.0, 'close': 1530.0},
]

df = pd.DataFrame(test_klines)
print("\n测试K线数据（不复权）：")
print(df)

# 应用复权
df_adjusted = service.apply_factors(df, factor_table)
print("\n复权后的K线数据：")
print(df_adjusted[['datetime', 'open', 'high', 'low', 'close']])

# 检查是否有负数
has_negative = (df_adjusted[['open', 'high', 'low', 'close']] < 0).any().any()
print(f"\n是否有负数价格: {'❌ 是' if has_negative else '✅ 否'}")

if has_negative:
    print("\n❌ 修复失败！仍存在负数价格")
else:
    print("\n✅ 修复成功！价格正常")
