# -*- coding: utf-8 -*-
"""
测试7: 自动下载板块和指数数据（无交互版）

目标：
1. 下载板块分类数据
2. 下载指数成分股权重数据
3. 验证下载后能否正常获取指数成分股
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime

print("="*80)
print("测试: 自动下载板块和指数数据")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ===== 步骤1: 下载板块数据 =====
print("[步骤1/3] download_sector_data() - 下载板块分类数据")
print("-"*80)
print("说明: 这个操作会下载所有板块的分类信息")
print("      包括行业板块、概念板块、地域板块等")
print()

try:
    print("开始下载板块数据...")
    start = time.time()

    result = xtdata.download_sector_data()

    elapsed = time.time() - start
    print(f"[OK] 下载板块数据完成 ✅")
    print(f"     耗时: {elapsed:.2f}秒")
    print(f"     返回值: {result}")

except Exception as e:
    print(f"[ERROR] 下载板块数据失败: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 步骤2: 下载指数权重数据 =====
print("[步骤2/3] download_index_weight() - 下载指数成分股权重")
print("-"*80)
print("说明: 这个操作会下载所有指数的成分股权重数据")
print("      数据量大，可能需要较长时间")
print()

try:
    print("开始下载指数权重数据...")
    print("(这可能需要几分钟，请耐心等待...)")
    start = time.time()

    result = xtdata.download_index_weight()

    elapsed = time.time() - start
    print(f"[OK] 下载指数权重数据完成 ✅")
    print(f"     耗时: {elapsed:.2f}秒 ({elapsed/60:.1f}分钟)")
    print(f"     返回值: {result}")

except Exception as e:
    print(f"[ERROR] 下载指数权重数据失败: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 步骤3: 验证板块列表 =====
print("[步骤3/3] 验证板块和指数数据")
print("-"*80)

try:
    sector_list = xtdata.get_sector_list()
    print(f"[OK] 获取板块列表成功，共 {len(sector_list)} 个板块")
    print()

    # 查找指数相关板块
    index_keywords = ['300', '500', '1000', '50']
    found_index_sectors = []

    for sector in sector_list:
        for keyword in index_keywords:
            if keyword in sector and '指数' in sector:
                found_index_sectors.append(sector)
                break

    if found_index_sectors:
        print(f"找到 {len(found_index_sectors)} 个指数相关板块:")
        for i, sector in enumerate(found_index_sectors[:20], 1):
            print(f"  {i:2d}. {sector}")
    else:
        print("未找到包含'300'、'500'、'1000'、'50'的指数板块")

except Exception as e:
    print(f"[ERROR] 获取板块列表失败: {e}")

print()

# ===== 验证指数成分股 =====
print("[验证] 测试指数成分股获取")
print("-"*80)

# 测试通过板块名称获取
test_sectors = ['沪深300', '中证500', '中证1000', '上证50']

print("方法1: 通过板块名称获取")
success_count = 0
for sector in test_sectors:
    try:
        stocks = xtdata.get_stock_list_in_sector(sector)
        if stocks:
            print(f"[OK] {sector:8s}: {len(stocks):4d} 只 ✅")
            success_count += 1
        else:
            print(f"[空] {sector:8s}: 0 只 ⚠️")
    except Exception as e:
        print(f"[错误] {sector:8s}: {e}")

print()

# 测试通过权重获取
print("方法2: 通过指数权重获取")
index_codes = {
    '000300.SH': '沪深300',
    '000905.SH': '中证500',
    '000852.SH': '中证1000',
    '000016.SH': '上证50'
}

weight_success_count = 0
for code, name in index_codes.items():
    try:
        weights = xtdata.get_index_weight(code)
        if weights:
            # 计算权重总和
            total = sum(weights.values())
            print(f"[OK] {name:8s} ({code}): {len(weights):4d} 只, 权重总和: {total:5.1f}% ✅")
            weight_success_count += 1
        else:
            print(f"[空] {name:8s} ({code}): 0 只")
    except Exception as e:
        print(f"[错误] {name:8s} ({code}): {e}")

print()

# ===== 总结 =====
print("="*80)
print("下载结果总结:")
print("-"*80)

if success_count > 0:
    print(f"✅ 板块名称方法: {success_count}/{len(test_sectors)} 个指数可用")
else:
    print(f"❌ 板块名称方法: 所有指数都返回0只")

if weight_success_count > 0:
    print(f"✅ 指数权重方法: {weight_success_count}/{len(index_codes)} 个指数可用")
else:
    print(f"❌ 指数权重方法: 所有指数都返回0")

print()
print("💡 使用建议:")
print("- 如果两种方法都成功，推荐使用权重方法（数据更详细）")
print("- 如果只有一种成功，使用成功的方法")
print("- 定期更新数据（建议每周一次）")
print("="*80)

print()
print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
