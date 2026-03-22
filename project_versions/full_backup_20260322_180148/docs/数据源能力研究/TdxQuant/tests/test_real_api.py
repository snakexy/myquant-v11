"""
TdxQuant真实API测试脚本

直接使用项目中的tqcenter API进行功能测试
"""

import sys
import os
import json
from datetime import datetime

# 添加backend目录到路径
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 导入tqcenter
from data.adapters.tdxquant_sdk import tqcenter

print("="*70)
print("TdxQuant 真实API测试")
print("="*70)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

test_results = {}

# 初始化tqcenter
print("\n初始化TdxQuant...")
try:
    tq = tqcenter.tq
    # 注意：这里不需要调用initialize，tdxquant_adapter已经处理了
    print("  TdxQuant API 已加载")
    test_results['initialization'] = {
        'success': True,
        'message': 'API加载成功'
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['initialization'] = {
        'success': False,
        'error': str(e)
    }
    # 继续测试，使用Mock模式

# 测试1: 获取股票列表
print("\n[测试1] 获取股票列表")
try:
    stock_list = tq.get_stock_list()
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
    stock_name = tq.get_stock_name("600519.SH")
    print(f"  600519.SH: {stock_name}")
    test_results['get_stock_name'] = {
        'success': stock_name is not None,
        'stock': '600519.SH',
        'name': stock_name
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['get_stock_name'] = {
        'success': False,
        'error': str(e)
    }

# 测试3: L1 实时快照（使用get_market_data代替）
print("\n[测试3] L1 实时快照（K线）")
try:
    kline_data = tq.get_market_data(
        stock_list=["600519.SH"],
        period="1m",
        count=1
    )
    print(f"  K线数据: {kline_data}")
    test_results['l1_snapshot'] = {
        'success': kline_data is not None and 'error' not in kline_data,
        'data': kline_data
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['l1_snapshot'] = {
        'success': False,
        'error': str(e)
    }

# 测试4: L2/L3 K线数据（多周期）
print("\n[测试4] L2/L3 K线数据（多周期）")
periods = ["5m", "15m", "30m", "1d"]
kline_results = {}

for period in periods:
    try:
        kline_data = tq.get_market_data(
            stock_list=["600519.SH"],
            period=period,
            count=10
        )
        if 'error' not in kline_data:
            data = kline_data.get('600519.SH', [])
            print(f"  {period}: {len(data)}根")
            kline_results[period] = {
                'success': True,
                'count': len(data),
                'period': period
            }
        else:
            print(f"  {period}: 错误 - {kline_data.get('msg', '未知错误')}")
            kline_results[period] = {
                'success': False,
                'error': kline_data.get('msg', '未知错误')
            }
    except Exception as e:
        print(f"  {period}: 失败 - {e}")
        kline_results[period] = {
            'success': False,
            'error': str(e)
        }

test_results['l3_kline'] = kline_results

# 测试5: L5 板块数据
print("\n[测试5] L5 板块数据")
try:
    # 获取板块列表
    sector_list = tq.get_sector_list()
    print(f"  板块数量: {len(sector_list)}")
    print(f"  前5个: {sector_list[:5] if len(sector_list) > 0 else '无'}")

    # 获取板块成分股
    if len(sector_list) > 0:
        test_sector = sector_list[0]
        stocks_in_sector = tq.get_stock_list_in_sector(test_sector)
        print(f"  {test_sector}: {len(stocks_in_sector)}只股票")
        if len(stocks_in_sector) > 0:
            print(f"    前5只: {stocks_in_sector[:5]}")

    test_results['l5_sector'] = {
        'success': len(sector_list) > 0,
        'sector_count': len(sector_list),
        'sample_sector': sector_list[0] if sector_list else None
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['l5_sector'] = {
        'success': False,
        'error': str(e)
    }

# 测试6: L4 财务数据
print("\n[测试6] L4 财务数据")
try:
    financial_data = tq.get_divid_factors(
        stock_list=["600519.SH"],
        start_time="2025-01-01",
        end_time="2025-12-31"
    )
    print(f"  除权数据: {financial_data}")
    test_results['l4_financial'] = {
        'success': financial_data is not None and 'error' not in financial_data,
        'data': financial_data
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['l4_financial'] = {
        'success': False,
        'error': str(e)
    }

# 测试7: 获取股票详细信息
print("\n[测试7] 获取股票详细信息")
try:
    stock_info = tq.get_more_info("600519.SH")
    print(f"  股票信息: {stock_info}")
    test_results['stock_info'] = {
        'success': stock_info is not None,
        'data': stock_info
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['stock_info'] = {
        'success': False,
        'error': str(e)
    }

# 测试8: 获取股票基本信息
print("\n[测试8] 获取股票基本信息")
try:
    stock_base_info = tq.get_stock_info("600519.SH")
    print(f"  基本信息: {stock_base_info}")
    test_results['stock_base_info'] = {
        'success': stock_base_info is not None,
        'data': stock_base_info
    }
except Exception as e:
    print(f"  失败: {e}")
    test_results['stock_base_info'] = {
        'success': False,
        'error': str(e)
    }

# 保存测试结果
results_dir = os.path.join(os.path.dirname(__file__), 'test_results')
os.makedirs(results_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
results_file = os.path.join(results_dir, f'real_api_test_{timestamp}.json')

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

# 详细结果
for test_name, result in test_results.items():
    status = "✅ 成功" if result.get('success', False) else "❌ 失败"
    print(f"  {test_name}: {status}")
    if not result.get('success', False):
        print(f"    错误: {result.get('error', '未知错误')}")

print("="*70)
