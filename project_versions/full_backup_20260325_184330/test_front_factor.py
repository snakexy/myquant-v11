"""调试前复权因子计算"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend/src')

from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service
from datetime import datetime

service = get_adjustment_factor_service()

# 删除缓存
import os
cache_file = 'E:/MyQuant_v11/data/xdxr_cache/600519_SH/factors_front.pkl'
if os.path.exists(cache_file):
    os.remove(cache_file)

print("计算茅台前复权因子...")
factor_table = service.get_factor_table('600519.SH', 'front')

# 检查今天的因子
today = datetime.now().strftime('%Y-%m-%d')
today_factor = factor_table.get(today, 'N/A')
print(f"\n今天({today})的因子: {today_factor}")

# 检查最近几天的因子
recent_dates = sorted(factor_table.keys(), reverse=True)[:10]
print("\n最近10天的因子:")
for date in recent_dates:
    print(f"  {date}: {factor_table[date]:.6f}")

# 检查除权日前后的因子
print("\n2025-12-19除权日前后的因子:")
for days in [-3, -2, -1, 0, 1, 2, 3]:
    date = '2025-12-' + str(19 + days)
    factor = factor_table.get(date, 'N/A')
    print(f"  {date}: {factor}")
