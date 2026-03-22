# -*- coding: utf-8 -*-
"""
验证下载结果
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata

print("="*80)
print("验证: 检查下载结果")
print("="*80)
print()

# 测试指数成分股
test_sectors = ['沪深300', '中证500', '中证1000', '上证50']
index_codes = {
    '000300.SH': '沪深300',
    '000905.SH': '中证500',
    '000852.SH': '中证1000',
    '000016.SH': '上证50'
}

print("[方法1] 通过板块名称获取")
for sector in test_sectors:
    try:
        stocks = xtdata.get_stock_list_in_sector(sector)
        if stocks:
            print(f"[OK] {sector:8s}: {len(stocks)} 只")
        else:
            print(f"[   ] {sector:8s}: 0 只")
    except Exception as e:
        print(f"[ERROR] {sector}: {e}")

print()
print("[方法2] 通过指数权重获取")
for code, name in index_codes.items():
    try:
        weights = xtdata.get_index_weight(code)
        if weights:
            total = sum(weights.values())
            print(f"[OK] {name:8s} ({code}): {len(weights)} 只, 权重: {total:.1f}%")
        else:
            print(f"[   ] {name:8s} ({code}): 0 只")
    except Exception as e:
        print(f"[ERROR] {name}: {e}")

print()
print("="*80)
print("如果看到 [OK]，说明下载成功！")
print("="*80)
