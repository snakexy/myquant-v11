"""
TdxQuant快速测试脚本

使用项目中已有的TdxQuant适配器进行快速功能验证
"""

import sys
import os
import json
from datetime import datetime

# 添加backend目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
backend_dir = os.path.join(project_root, 'backend')

print(f"当前目录: {current_dir}")
print(f"项目根目录: {project_root}")
print(f"Backend目录: {backend_dir}")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 导入TdxQuant适配器
try:
    from data.adapters.tdxquant_adapter import TdxQuantAdapter
except ImportError:
    print("无法导入 TdxQuantAdapter")
    print(f"backend目录: {backend_dir}")
    print(f"当前Python路径: {sys.path}")
    sys.exit(1)

print("="*70)
print("TdxQuant 快速功能测试")
print("="*70)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# 初始化适配器（使用实时模式）
print("\n初始化TdxQuant适配器（实时模式）...")
adapter = TdxQuantAdapter(use_real_tdxquant=True)

test_results = {}

# 测试1: 获取股票列表
print("\n[测试1] 获取股票列表")
try:
    stock_list = adapter.get_stock_list()
    print(f"  股票数量: {len(stock_list)}")
    print(f"  前10只: {stock_list[:10]}")
    test_results['get_stock_list'] = {
        'success': True,
        'count': len(stock_list),
        'sample': stock_list[:5]
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['get_stock_list'] = {
        'success': False,
        'error': str(e)
    }

# 测试2: 获取股票名称
print("\n[测试2] 获取股票名称")
try:
    stock_name = adapter.get_stock_name("600519.SH")
    print(f"  600519.SH: {stock_name}")
    test_results['get_stock_name'] = {
        'success': True,
        'stock': '600519.SH',
        'name': stock_name
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['get_stock_name'] = {
        'success': False,
        'error': str(e)
    }

# 测试3: L1 实时快照
print("\n[测试3] L1 实时快照")
try:
    snapshot = adapter.get_market_snapshot("600519.SH")
    print(f"  快照数据: {snapshot}")
    test_results['l1_snapshot'] = {
        'success': snapshot is not None,
        'data': snapshot
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['l1_snapshot'] = {
        'success': False,
        'error': str(e)
    }

# 测试4: L2/L3 K线数据
print("\n[测试4] L2/L3 K线数据")
periods = ["1m", "5m", "15m", "30m", "60m", "1d"]
for period in periods:
    try:
        kline_data = adapter.get_market_data(
            ["600519.SH"],
            period=period,
            count=10
        )
        if kline_data and "600519.SH" in kline_data:
            data = kline_data["600519.SH"]
            print(f"  {period}: {len(data)}根")
            if len(data) > 0:
                print(f"    最新: {data[0]}")
            test_results[f'l3_kline_{period}'] = {
                'success': True,
                'count': len(data),
                'period': period
            }
        else:
            print(f"  {period}: 无数据")
            test_results[f'l3_kline_{period}'] = {
                'success': False,
                'count': 0
            }
    except Exception as e:
        print(f"  {period}: 失败 - {e}")
        test_results[f'l3_kline_{period}'] = {
            'success': False,
            'error': str(e)
        }

# 测试5: L4 财务数据
print("\n[测试5] L4 财务数据")
try:
    financial_data = adapter.get_financial_data(
        ["600519.SH"],
        report_type=1,
        start_date="2025-01-01",
        end_date="2025-12-31"
    )
    print(f"  财务数据: {financial_data}")
    test_results['l4_financial'] = {
        'success': financial_data is not None,
        'data': financial_data
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['l4_financial'] = {
        'success': False,
        'error': str(e)
    }

# 测试6: L5 板块数据
print("\n[测试6] L5 板块数据")
try:
    # 获取板块列表
    sector_list = adapter.get_sector_list()
    print(f"  板块数量: {len(sector_list)}")
    print(f"  前5个: {sector_list[:5]}")

    # 获取板块成分股
    if len(sector_list) > 0:
        test_sector = sector_list[0]
        stocks_in_sector = adapter.get_stock_list_in_sector(test_sector)
        print(f"  {test_sector}: {len(stocks_in_sector)}只股票")
        if len(stocks_in_sector) > 0:
            print(f"    前5只: {stocks_in_sector[:5]}")

    test_results['l5_sector'] = {
        'success': True,
        'sector_count': len(sector_list),
        'sample_sector': sector_list[0] if sector_list else None
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['l5_sector'] = {
        'success': False,
        'error': str(e)
    }

# 保存测试结果
results_dir = os.path.join(os.path.dirname(__file__), 'test_results')
os.makedirs(results_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
results_file = os.path.join(results_dir, f'quick_test_{timestamp}.json')

results_data = {
    'timestamp': timestamp,
    'test_results': test_results
}

with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results_data, f, ensure_ascii=False, indent=2)

print(f"\n测试结果已保存到: {results_file}")

# 汇总
print("\n" + "="*70)
print("测试汇总")
print("="*70)

success_count = sum(1 for r in test_results.values() if r.get('success', False))
total_count = len(test_results)

print(f"成功: {success_count}/{total_count}")
print("="*70)
