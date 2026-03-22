# -*- coding: utf-8 -*-
"""
快速检查：验证QMT是否已有板块和指数数据
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata

print("="*80)
print("快速检查: QMT数据状态")
print("="*80)
print()

# ===== 检查1: 获取板块列表 =====
print("[检查1] 获取板块列表")
print("-"*80)

try:
    sector_list = xtdata.get_sector_list()
    print(f"[OK] 成功! 共 {len(sector_list)} 个板块")

    # 查找指数相关
    index_related = [s for s in sector_list if '300' in s or '500' in s or '1000' in s]
    if index_related:
        print(f"   找到 {len(index_related)} 个指数相关板块:")
        for s in index_related[:5]:
            print(f"     - {s}")
    else:
        print("   未找到指数相关板块")

except Exception as e:
    print(f"[ERROR] 失败: {e}")

print()

# ===== 检查2: 测试指数成分股 =====
print("[检查2] 测试指数成分股")
print("-"*80)

test_sectors = ['沪深300', '中证500', '中证1000']

for sector in test_sectors:
    try:
        stocks = xtdata.get_stock_list_in_sector(sector)
        if stocks:
            print(f"[OK] {sector:8s}: {len(stocks)} 只")
        else:
            print(f"[WARN] {sector:8s}: 0 只 (需要下载)")
    except Exception as e:
        print(f"[ERROR] {sector:8s}: 错误 - {e}")

print()

# ===== 检查3: 测试指数权重 =====
print("[检查3] 测试指数权重")
print("-"*80)

index_codes = {
    '000300.SH': '沪深300',
    '000905.SH': '中证500'
}

for code, name in index_codes.items():
    try:
        weights = xtdata.get_index_weight(code)
        if weights:
            total = sum(weights.values())
            print(f"[OK] {name:8s} ({code}): {len(weights)} 只, 权重总和: {total:.1f}%")
        else:
            print(f"[WARN] {name:8s} ({code}): 0 只 (需要下载)")
    except Exception as e:
        print(f"[ERROR] {name:8s} ({code}): 错误 - {e}")

print()
print("="*80)
print("结论:")
print("- 如果看到 [OK]，说明数据已存在，无需下载")
print("- 如果看到 [WARN] 0 只 或 [ERROR]，说明需要下载")
print("- download_sector_data() 和 download_index_weight() 下载的是分类信息，")
print("  不是历史K线数据，数据量不大（几MB），不会占用太多空间")
print("="*80)
