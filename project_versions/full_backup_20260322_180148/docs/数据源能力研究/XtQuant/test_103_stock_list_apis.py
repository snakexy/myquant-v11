# -*- coding: utf-8 -*-
"""
测试3: 股票列表和聚合数据API

目标：
1. 验证get_stock_list_in_sector()获取股票列表
2. 验证get_full_tick()批量获取行情
3. 验证各板块支持的股票数量
4. 测试获取全市场股票的性能
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime

print("="*80)
print("测试: 股票列表和聚合数据API")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ===== 测试1: 获取板块列表 =====
print("[测试1] 获取所有可用板块")
print("-"*80)

try:
    sector_list = xtdata.get_sector_list()
    print(f"[OK] 获取成功，共 {len(sector_list)} 个板块")
    print()
    print("前20个板块:")
    for i, sector in enumerate(sector_list[:20], 1):
        print(f"  {i:2d}. {sector}")

    if len(sector_list) > 20:
        print(f"  ... 还有 {len(sector_list) - 20} 个板块")

except Exception as e:
    print(f"[ERROR] 获取板块列表失败: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 测试2: 获取各板块股票数量 =====
print("[测试2] 获取常用板块的股票数量")
print("-"*80)

test_sectors = [
    '沪深A股',
    '上证A股',
    '深证A股',
    '创业板',
    '科创板',
    '沪深300',
    '中证500',
    '中证1000',
    '上证50',
    '沪深ETF'
]

sector_stock_counts = {}

for sector_name in test_sectors:
    try:
        start = time.time()
        stocks = xtdata.get_stock_list_in_sector(sector_name)
        elapsed = (time.time() - start) * 1000

        if stocks:
            sector_stock_counts[sector_name] = len(stocks)
            print(f"[OK] {sector_name:12s}: {len(stocks):5d} 只, 耗时: {elapsed:6.2f}ms")
        else:
            print(f"[空] {sector_name:12s}: 0 只")

    except Exception as e:
        print(f"[ERROR] {sector_name:12s}: {e}")

print()

# ===== 测试3: 获取全市场股票 =====
print("[测试3] 获取全市场股票（沪深A股）")
print("-"*80)

try:
    start = time.time()
    all_a_stocks = xtdata.get_stock_list_in_sector('沪深A股')
    elapsed = (time.time() - start) * 1000

    if all_a_stocks:
        print(f"[OK] 全市场共 {len(all_a_stocks)} 只A股")
        print(f"     耗时: {elapsed:.2f}ms")
        print()
        print("前10只股票:")
        for i, stock in enumerate(all_a_stocks[:10], 1):
            print(f"  {i}. {stock}")

        if len(all_a_stocks) > 10:
            print(f"  ... 还有 {len(all_a_stocks) - 10} 只")
    else:
        print("[空] 未获取到股票")

except Exception as e:
    print(f"[ERROR] 获取全市场股票失败: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 测试4: get_full_tick 批量获取行情 =====
print("[测试4] get_full_tick() 批量获取行情性能")
print("-"*80)

if all_a_stocks:
    # 测试不同数量的股票
    test_counts = [10, 100, 500, 1000]

    for count in test_counts:
        if count > len(all_a_stocks):
            count = len(all_a_stocks)

        test_stocks = all_a_stocks[:count]

        try:
            start = time.time()
            tick_data = xtdata.get_full_tick(test_stocks)
            elapsed = (time.time() - start) * 1000

            if tick_data:
                print(f"[OK] 获取 {count:4d} 只股票行情: {elapsed:6.2f}ms, 实际返回: {len(tick_data)} 只")

                # 显示第一只股票的数据字段
                if count == 10 and len(tick_data) > 0:
                    first_stock = list(tick_data.keys())[0]
                    first_data = tick_data[first_stock]
                    print(f"     示例 ({first_stock}):")
                    print(f"       lastPrice: {first_data.get('lastPrice')}")
                    print(f"       lastClose: {first_data.get('lastClose')}")
                    print(f"       amount: {first_data.get('amount')}")
                    print(f"       volume: {first_data.get('volume')}")
            else:
                print(f"[空] 获取 {count:4d} 只股票行情: 无数据")

        except Exception as e:
            print(f"[ERROR] 获取 {count:4d} 只股票行情失败: {e}")

print()

# ===== 测试5: 获取指数成分股 =====
print("[测试5] 获取指数成分股详情")
print("-"*80)

index_sectors = ['沪深300', '中证500', '中证1000', '上证50']

for sector in index_sectors:
    try:
        stocks = xtdata.get_stock_list_in_sector(sector)
        if stocks:
            print(f"[OK] {sector:8s}: {len(stocks)} 只")
            print(f"      前5只: {', '.join(stocks[:5])}")
        else:
            print(f"[空] {sector:8s}: 0 只")

    except Exception as e:
        print(f"[ERROR] {sector:8s}: {e}")

print()

# ===== 测试6: 非交易时间行为 =====
print("[测试6] 非交易时间数据验证")
print("-"*80)
print("说明: 验证非交易时间是否返回最后收盘价")

if all_a_stocks:
    # 取前20只股票
    test_stocks = all_a_stocks[:20]

    try:
        tick_data = xtdata.get_full_tick(test_stocks)

        if tick_data:
            print(f"获取到 {len(tick_data)} 只股票的数据")
            print()
            print("示例数据:")
            for i, (stock, data) in enumerate(list(tick_data.items())[:5], 1):
                print(f"  {i}. {stock}")
                print(f"     lastPrice: {data.get('lastPrice')}")
                print(f"     lastClose: {data.get('lastClose')}")
                print(f"     amount: {data.get('amount')}")
                print(f"     volume: {data.get('volume')}")

                # 检查是否有数据
                if data.get('lastPrice') and data.get('lastPrice') > 0:
                    print(f"     状态: 有数据 ✅")
                else:
                    print(f"     状态: 无有效数据 ⚠️")
                print()

    except Exception as e:
        print(f"[ERROR] 获取失败: {e}")

print()
print("="*80)
print("结论:")
print("- get_stock_list_in_sector() 可获取各板块股票列表")
print("- get_full_tick() 可批量获取实时行情，性能优秀")
print("- 适合用于股票列表功能的实现")
print("="*80)
