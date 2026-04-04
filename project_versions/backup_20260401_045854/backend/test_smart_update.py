"""测试智能补全功能"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend')

from myquant.core.market.services.hotdb_service import get_hotdb_service
from myquant.core.market.adapters import get_adapter

symbol = "300046.SZ"
period = "5m"

print("=" * 70)
print(f"测试 {symbol} {period} 智能补全")
print("=" * 70)

# 先检查 HotDB 当前状态
hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    info = hotdb.get_data_info(symbol, period)
    print(f"\n[HotDB当前状态]")
    print(f"  has_data: {info.get('has_data')}")
    print(f"  count: {info.get('count')}")
    print(f"  earliest: {info.get('earliest')}")
    print(f"  latest: {info.get('latest')}")

# 调用缺口检测
hotdb_service = get_hotdb_service()
print(f"\n[缺口检测]")
gap_info = hotdb_service._detect_gap(symbol, period)
if gap_info:
    print(f"  has_gap: {gap_info.get('has_gap')}")
    print(f"  reason: {gap_info.get('reason')}")
    print(f"  latest: {gap_info.get('latest')}")
    if gap_info.get('has_gap'):
        print(f"  missing_start: {gap_info.get('missing_start')}")
        print(f"  missing_end: {gap_info.get('missing_end')}")

# 调用 smart_update
print(f"\n[调用 smart_update]")
result = hotdb_service.smart_update(symbol, period)
print(f"  success: {result.get('success')}")
print(f"  has_data: {result.get('has_data')}")
print(f"  has_gap: {result.get('has_gap')}")
print(f"  reason: {result.get('reason')}")

if result.get('df') is not None:
    df = result['df']
    print(f"\n[更新后的数据]")
    print(f"  总条数: {len(df)}")
    print(f"  最早: {df['datetime'].min()}")
    print(f"  最新: {df['datetime'].max()}")
    print(f"  最新3条:")
    for _, row in df.sort_values('datetime', ascending=False).head(3).iterrows():
        print(f"    {row['datetime']}  volume={int(row['volume']):>10} 手")

print("\n" + "=" * 70)
