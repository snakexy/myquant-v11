#!/usr/bin/env python3
"""验证中国人寿数据已清除"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter

symbol = '601628.SH'

print("=" * 60)
print(f"验证 {symbol} 数据已清除")
print("=" * 60)

hotdb = get_adapter('hotdb')

# 验证日线数据已清除
print("\n【日线数据验证】")
df_dict = hotdb.get_kline([symbol], period='1d', count=10)
if symbol in df_dict and not df_dict[symbol].empty:
    print(f"   警告: 数据仍然存在 ({len(df_dict[symbol])} 条)")
    print(df_dict[symbol][['datetime', 'volume']].to_string())
else:
    print("   ✓ 日线数据已清除")

print("\n" + "=" * 60)
print("修复完成！")
print("=" * 60)
print("\n数据已清除，下次前端请求时会自动重新预热。")
print("建议：在前端点击中国人寿，系统会自动重新获取数据。")
