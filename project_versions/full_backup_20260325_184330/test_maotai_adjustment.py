"""
测试茅台复权 - 完整流程模拟
"""
import sys
sys.path.insert(0, 'backend/src')

import pandas as pd
from myquant.core.market.services.seamless_service import get_seamless_kline_service

print("=" * 70)
print("测试茅台 2025-12-18/19 复权")
print("=" * 70)

# 获取服务
service = get_seamless_kline_service()

# 获取日线数据
symbol = '600519.SH'
result = service.get_kline(
    symbol=symbol,
    period='1d',
    count=5,
    adjust_type='front'
)

if result is not None and hasattr(result, 'data') and result.data is not None and not result.data.empty:
    df = result.data
    print(f"\n获取到 {len(df)} 条K线数据:")
    print(df[['datetime', 'open', 'high', 'low', 'close']].to_string())

    # 检查 12-18 和 12-19
    for _, row in df.iterrows():
        date_str = str(row['datetime'])[:10]
        if '2025-12-18' in date_str or '2025-12-19' in date_str:
            print(f"\n{date_str}: close = {row['close']:.2f}")

    # 验证
    dec19 = df[df['datetime'].astype(str).str.contains('2025-12-19')]
    if not dec19.empty:
        price = dec19.iloc[0]['close']
        if abs(price - 1410.0) < 0.1:
            print(f"\n✅ 12-19 复权正确: {price:.2f}")
        else:
            print(f"\n❌ 12-19 复权错误: {price:.2f} (应为 1410.00)")
else:
    print("\n❌ 未获取到数据")
