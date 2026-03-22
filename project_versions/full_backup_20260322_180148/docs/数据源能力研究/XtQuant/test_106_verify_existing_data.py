# -*- coding: utf-8 -*-
"""
测试5: 验证已下载的板块和指数数据

目标：
1. 查看所有可用板块
2. 测试指数成分股是否可用
3. 测试指数权重功能
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime

print("="*80)
print("测试: 验证已下载的板块和指数数据")
print("="*80)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ===== 测试1: 查看所有板块（查找指数相关） =====
print("[测试1] 查找所有指数相关板块")
print("-"*80)

try:
    sector_list = xtdata.get_sector_list()
    print(f"共有 {len(sector_list)} 个板块")
    print()

    # 查找包含"指数"、"300"、"500"、"1000"、"50"的板块
    keywords = ['指数', '300', '500', '1000', '50']

    for keyword in keywords:
        matching = [s for s in sector_list if keyword in s]
        if matching:
            print(f"包含'{keyword}'的板块 ({len(matching)}个):")
            for s in matching[:10]:
                print(f"  - {s}")
            if len(matching) > 10:
                print(f"  ... 还有 {len(matching) - 10} 个")
            print()

except Exception as e:
    print(f"[ERROR] 获取板块列表失败: {e}")

print()

# ===== 测试2: 尝试各种指数板块名称 =====
print("[测试2] 测试各种可能的指数板块名称")
print("-"*80)

# 从文档中看到的常见板块名称
test_names = [
    # 中文全称
    '沪深300',
    '中证500',
    '中证1000',
    '上证50',
    '上证180',
    '深证成指',
    '创业板指',
    '科创50',
    '中证2000',

    # 简称
    'HS300',
    'ZZ500',
    'SZ300',
    'ZS1000',

    # 指数代码格式
    '000300.SH',
    '000905.SH',  # 中证500
    '000852.SH',  # 中证1000
]

print(f"{'板块名称':20s} {'结果':10s} {'数量':6s}")
print("-" * 50)

for name in test_names:
    try:
        stocks = xtdata.get_stock_list_in_sector(name)
        if stocks:
            print(f"{name:20s} {'✅成功':10s} {len(stocks):6d}只")
        else:
            print(f"{name:20s} {'空':10s} {0:6d}只")

    except Exception as e:
        print(f"{name:20s} {'错误':10s} {str(e)[:30]}")

print()

# ===== 测试3: 测试指数权重API =====
print("[测试3] 测试指数权重API")
print("-"*80)

# 测试指数权重
index_codes = [
    '000300.SH',  # 沪深300
    '000905.SH',  # 中证500
    '000852.SH',  # 中证1000
    '000016.SH',  # 上证50
]

for index_code in index_codes:
    try:
        print(f"测试指数: {index_code}")
        weights = xtdata.get_index_weight(index_code)

        if weights:
            print(f"  ✅ 成功获取权重: {len(weights)} 只成分股")
            print(f"  前3只:")
            for i, (stock, weight) in enumerate(list(weights.items())[:3], 1):
                print(f"    {i}. {stock}: {weight}%")
        else:
            print(f"  空数据")
        print()

    except Exception as e:
        print(f"  ❌ 错误: {e}")
        print()

print()

# ===== 测试4: 如果权重成功，反推成分股列表 =====
print("[测试4] 从权重数据获取成分股列表")
print("-"*80)

index_code = '000300.SH'  # 沪深300

try:
    print(f"获取指数: {index_code}")

    # 方法1: 通过权重获取
    weights = xtdata.get_index_weight(index_code)

    if weights:
        stocks_from_weight = list(weights.keys())
        print(f"[OK] 从权重获取: {len(stocks_from_weight)} 只")
        print(f"     前5只: {', '.join(stocks_from_weight[:5])}")

    # 方法2: 通过板块名称获取
    stocks_from_sector = xtdata.get_stock_list_in_sector('沪深300')

    if stocks_from_sector:
        print(f"[OK] 从板块获取: {len(stocks_from_sector)} 只")
        print(f"     前5只: {', '.join(stocks_from_sector[:5])}")

    # 对比两种方法
    if weights and stocks_from_sector:
        if set(stocks_from_weight) == set(stocks_from_sector):
            print(f"\n[对比] 两种方法结果一致 ✅")
        else:
            print(f"\n[对比] 两种方法结果不同")
            print(f"      权重方法: {len(stocks_from_weight)} 只")
            print(f"      板块方法: {len(stocks_from_sector)} 只")

except Exception as e:
    print(f"[ERROR] {e}")

print()

# ===== 测试5: 验证数据完整性 =====
print("[测试5] 验证指数成分股数据的完整性")
print("-"*80)

if weights:
    # 计算权重总和
    total = sum(weights.values())
    print(f"权重总和: {total}%")
    print(f"成分股数量: {len(weights)}")

    if 99 <= total <= 101:
        print("[OK] 权重总和正常 (约100%) ✅")
    else:
        print(f"[警告] 权重总和异常: {total}% ⚠️")

print()

print("="*80)
print("结论:")
print("- 如果get_index_weight()成功，可以通过权重数据获取成分股")
print("- 如果get_stock_list_in_sector()返回空，可能需要更新板块数据")
print("- 建议定期调用download_sector_data()和download_index_weight()")
print("="*80)
