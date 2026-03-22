# -*- coding: utf-8 -*-
"""
测试4: 下载板块和指数成分股数据

目标：
1. 验证download_sector_data()下载板块数据
2. 验证download_index_weight()下载指数成分股
3. 验证下载后能否获取指数成分股列表
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime

print("="*80)
print("测试: 下载板块和指数成分股数据")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ===== 测试1: 下载板块数据 =====
print("[测试1] download_sector_data() - 下载板块数据")
print("-"*80)

try:
    print("开始下载板块数据...")
    start = time.time()

    result = xtdata.download_sector_data()

    elapsed = time.time() - start
    print(f"[OK] 下载完成, 耗时: {elapsed:.2f}秒")
    print(f"     返回值: {result}")

except Exception as e:
    print(f"[ERROR] 下载板块数据失败: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 测试2: 下载指数成分股权重 =====
print("[测试2] download_index_weight() - 下载指数成分股权重")
print("-"*80)
print("⚠️ 警告: 此操作可能需要较长时间（数据量大）")
print()

response = input("是否继续下载指数权重？(y/n): ")

if response.lower() == 'y':
    try:
        print("开始下载指数成分股权重...")
        start = time.time()

        result = xtdata.download_index_weight()

        elapsed = time.time() - start
        print(f"[OK] 下载完成, 耗时: {elapsed:.2f}秒")
        print(f"     返回值: {result}")

    except Exception as e:
        print(f"[ERROR] 下载指数权重失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("[跳过] 已取消下载指数权重")

print()

# ===== 测试3: 下载后重新获取指数成分股 =====
print("[测试3] 下载后重新获取指数成分股")
print("-"*80)

index_sectors = ['沪深300', '中证500', '中证1000', '上证50']

for sector in index_sectors:
    try:
        stocks = xtdata.get_stock_list_in_sector(sector)
        if stocks:
            print(f"[OK] {sector:8s}: {len(stocks)} 只 ✅")
            print(f"      前5只: {', '.join(stocks[:5])}")
        else:
            print(f"[空] {sector:8s}: 0 只 ⚠️")

    except Exception as e:
        print(f"[ERROR] {sector:8s}: {e}")

print()

# ===== 测试4: 获取板块列表 =====
print("[测试4] get_sector_list() - 查看所有板块")
print("-"*80)

try:
    sector_list = xtdata.get_sector_list()
    print(f"共有 {len(sector_list)} 个板块")
    print()
    print("包含'指数'的板块:")

    index_related = [s for s in sector_list if '指数' in s or '300' in s or '500' in s or '1000' in s or '50' in s]

    for i, sector in enumerate(index_related[:20], 1):
        print(f"  {i:2d}. {sector}")

    if len(index_related) > 20:
        print(f"  ... 还有 {len(index_related) - 20} 个相关板块")

except Exception as e:
    print(f"[ERROR] 获取板块列表失败: {e}")

print()

# ===== 测试5: 测试其他可能的板块名称 =====
print("[测试5] 测试其他可能的指数板块名称")
print("-"*80)

# 尝试不同的板块名称格式
test_names = [
    '沪深300',
    '中证500',
    '中证1000',
    '上证50',
    '上证180',
    '深证成指',
    '创业板指',
    '科创50',
    '中证2000',
    '300',
    '000300.SH',
    '000300',
    'HS300',
]

for name in test_names:
    try:
        stocks = xtdata.get_stock_list_in_sector(name)
        if stocks:
            print(f"[OK] '{name:20s}': {len(stocks):4d} 只 ✅")
        else:
            print(f"[空] '{name:20s}': 0 只")

    except Exception as e:
        print(f"[ERROR] '{name:20s}': {e}")

print()
print("="*80)
print("结论:")
print("- download_sector_data() 可以下载板块分类数据")
print("- download_index_weight() 可以下载指数成分股权重")
print("- 下载后应能正常获取指数成分股列表")
print("="*80)
