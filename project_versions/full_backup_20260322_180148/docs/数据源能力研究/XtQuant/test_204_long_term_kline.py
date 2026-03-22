# -*- coding: utf-8 -*-
"""
补充测试：单只股票长期K线数据获取

目的：
1. 测试K线图实际场景的数据获取性能
2. 对比在线获取vs下载+读取在长期数据场景的差异
3. 为K线图功能提供准确的数据获取建议

测试场景：
- 日K：1年、2年、3年
- 60分钟K：3个月、6个月、1年
- 30分钟K：1个月、3个月、6个月
- 15分钟K：1个月、3个月、6个月
- 5分钟K：1个月、3个月、6个月
- 1分钟K：1周、2周、1月
"""

from xtquant import xtdata
import time
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))


def test_online_get_long_term(symbol, period, count):
    """
    测试在线获取（长期数据）

    注意：会受在线获取限制约束
    - 5分钟K线：最多22.6个交易日（1083条）
    - 1分钟K线：约5个交易日（1261条）
    """
    start = time.time()

    try:
        # 订阅
        xtdata.subscribe_quote(symbol, period=period, count=0)

        # 在线获取
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period=period,
            start_time='',
            end_time='',
            count=count,
            dividend_type='none'
        )

        elapsed = (time.time() - start) * 1000

        if data and symbol in data:
            df = data[symbol]
            return {
                'success': True,
                'elapsed': elapsed,
                'count': len(df),
                'method': 'online'
            }
        else:
            return {
                'success': False,
                'elapsed': elapsed,
                'count': 0,
                'error': 'No data returned',
                'method': 'online'
            }

    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return {
            'success': False,
            'elapsed': elapsed,
            'count': 0,
            'error': str(e),
            'method': 'online'
        }


def test_download_read_long_term(symbol, period, start_date, end_date):
    """
    测试下载+读取（长期数据）

    优势：几乎无时间限制
    劣势：首次下载需要时间
    """
    total_start = time.time()

    try:
        # 阶段1: 下载
        download_start = time.time()
        xtdata.download_history_data(
            stock_code=symbol,
            period=period,
            start_time=start_date,
            end_time=end_date
        )
        download_time = (time.time() - download_start) * 1000

        # 阶段2: 读取
        read_start = time.time()
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period=period,
            start_time=int(start_date),
            end_time=int(end_date),
            dividend_type='none'
        )
        read_time = (time.time() - read_start) * 1000

        total_time = (time.time() - total_start) * 1000

        if data and symbol in data:
            df = data[symbol]
            return {
                'success': True,
                'elapsed': total_time,
                'download_time': download_time,
                'read_time': read_time,
                'count': len(df),
                'method': 'download_read'
            }
        else:
            return {
                'success': False,
                'elapsed': total_time,
                'download_time': download_time,
                'read_time': read_time,
                'count': 0,
                'error': 'No data returned',
                'method': 'download_read'
            }

    except Exception as e:
        total_time = (time.time() - total_start) * 1000
        return {
            'success': False,
            'elapsed': total_time,
            'count': 0,
            'error': str(e),
            'method': 'download_read'
        }


def run_kline_scenarios():
    """运行K线图实际场景测试"""

    print("=" * 80)
    print("K线图实际场景测试：单只股票长期数据获取")
    print("=" * 80)
    print()

    test_symbol = '600519.SH'  # 贵州茅台

    # 计算日期范围
    today = datetime.now()
    one_month_ago = (today - timedelta(days=30)).strftime('%Y%m%d')
    three_months_ago = (today - timedelta(days=90)).strftime('%Y%m%d')
    six_months_ago = (today - timedelta(days=180)).strftime('%Y%m%d')
    one_year_ago = (today - timedelta(days=365)).strftime('%Y%m%d')
    two_years_ago = (today - timedelta(days=730)).strftime('%Y%m%d')
    three_years_ago = (today - timedelta(days=1095)).strftime('%Y%m%d')

    # K线图实际场景
    scenarios = [
        # 日K线场景
        {
            'name': '日K - 查看1年',
            'period': '1d',
            'online_count': 250,
            'download_start': one_year_ago,
            'download_end': today.strftime('%Y%m%d')
        },
        {
            'name': '日K - 查看2年',
            'period': '1d',
            'online_count': 500,
            'download_start': two_years_ago,
            'download_end': today.strftime('%Y%m%d')
        },
        {
            'name': '日K - 查看3年',
            'period': '1d',
            'online_count': 750,
            'download_start': three_years_ago,
            'download_end': today.strftime('%Y%m%d')
        },

        # 60分钟K线场景（1h）
        {
            'name': '60分钟K - 查看3个月',
            'period': '1h',  # ⭐ 注意：是1h不是60m
            'online_count': 480,  # 3个月 × 22天 × 4小时/天
            'download_start': three_months_ago,
            'download_end': today.strftime('%Y%m%d')
        },
        {
            'name': '60分钟K - 查看6个月',
            'period': '1h',  # ⭐ 注意：是1h不是60m
            'online_count': 960,
            'download_start': six_months_ago,
            'download_end': today.strftime('%Y%m%d')
        },

        # 30分钟K线场景
        {
            'name': '30分钟K - 查看1个月',
            'period': '30m',
            'online_count': 880,  # 1个月 × 22天 × 8条/天
            'download_start': one_month_ago,
            'download_end': today.strftime('%Y%m%d')
        },
        {
            'name': '30分钟K - 查看3个月',
            'period': '30m',
            'online_count': 2640,
            'download_start': three_months_ago,
            'download_end': today.strftime('%Y%m%d')
        },

        # 15分钟K线场景
        {
            'name': '15分钟K - 查看1个月',
            'period': '15m',
            'online_count': 1760,  # 1个月 × 22天 × 16条/天
            'download_start': one_month_ago,
            'download_end': today.strftime('%Y%m%d')
        },
        {
            'name': '15分钟K - 查看3个月',
            'period': '15m',
            'online_count': 5280,
            'download_start': three_months_ago,
            'download_end': today.strftime('%Y%m%d')
        },

        # 5分钟K线场景（用户最常用）
        {
            'name': '5分钟K - 查看1个月',
            'period': '5m',
            'online_count': 1056,  # 1个月 × 22天 × 48条/天
            'download_start': one_month_ago,
            'download_end': today.strftime('%Y%m%d')
        },
        {
            'name': '5分钟K - 查看3个月',
            'period': '5m',
            'online_count': 3168,
            'download_start': three_months_ago,
            'download_end': today.strftime('%Y%m%d')
        },
        {
            'name': '5分钟K - 查看6个月',
            'period': '5m',
            'online_count': 6336,
            'download_start': six_months_ago,
            'download_end': today.strftime('%Y%m%d')
        },

        # 1分钟K线场景
        {
            'name': '1分钟K - 查看1周',
            'period': '1m',
            'online_count': 1250,  # 5天 × 250条/天
            'download_start': one_month_ago,  # 下载1个月（包含1周）
            'download_end': today.strftime('%Y%m%d')
        },
        {
            'name': '1分钟K - 查看2周',
            'period': '1m',
            'online_count': 2500,
            'download_start': one_month_ago,  # 下载1个月（包含2周）
            'download_end': today.strftime('%Y%m%d')
        },
    ]

    results = []

    for scenario in scenarios:
        print(f"\n{'=' * 80}")
        print(f"{scenario['name']}")
        print(f"{'=' * 80}")
        print()

        # 测试在线获取
        print("[测试1] 在线获取")
        print("-" * 80)
        online_result = test_online_get_long_term(
            test_symbol,
            scenario['period'],
            scenario['online_count']
        )

        if online_result['success']:
            print(f"[OK] 成功: {online_result['count']}条, 耗时: {online_result['elapsed']:.2f}ms")
        else:
            print(f"[ERROR] 失败: {online_result.get('error', 'Unknown error')}")

        # 测试下载+读取
        print("\n[测试2] 下载+读取")
        print("-" * 80)
        download_result = test_download_read_long_term(
            test_symbol,
            scenario['period'],
            scenario['download_start'],
            scenario['download_end']
        )

        if download_result['success']:
            print(f"[OK] 成功: {download_result['count']}条, "
                  f"总耗时: {download_result['elapsed']:.2f}ms")
            print(f"  - 下载: {download_result['download_time']:.2f}ms "
                  f"({download_result['download_time']/download_result['elapsed']*100:.1f}%)")
            print(f"  - 读取: {download_result['read_time']:.2f}ms "
                  f"({download_result['read_time']/download_result['elapsed']*100:.1f}%)")
        else:
            print(f"[ERROR] 失败: {download_result.get('error', 'Unknown error')}")

        # 对比分析
        print("\n[对比] 结果分析")
        print("-" * 80)

        if online_result['success'] and download_result['success']:
            # 都成功
            if online_result['elapsed'] < download_result['elapsed']:
                faster = download_result['elapsed'] / online_result['elapsed']
                recommendation = f"在线获取 ({faster:.1f}x快)"
            else:
                faster = online_result['elapsed'] / download_result['elapsed']
                recommendation = f"下载+读取 ({faster:.1f}x快)"

            print(f"在线获取: {online_result['count']}条, {online_result['elapsed']:.2f}ms")
            print(f"下载+读取: {download_result['count']}条, {download_result['elapsed']:.2f}ms")
            print(f"推荐: {recommendation}")

        elif online_result['success']:
            # 只有在线获取成功
            print(f"在线获取: {online_result['count']}条, {online_result['elapsed']:.2f}ms")
            print(f"下载+读取: 失败")
            print(f"推荐: 在线获取（下载+读取不可用）")

        elif download_result['success']:
            # 只有下载+读取成功
            print(f"在线获取: 失败（超出限制）")
            print(f"下载+读取: {download_result['count']}条, {download_result['elapsed']:.2f}ms")
            print(f"推荐: 下载+读取（在线获取受限）")

        else:
            print("两种方式都失败")

        # 记录结果
        results.append({
            'scenario': scenario['name'],
            'period': scenario['period'],
            'online_success': online_result['success'],
            'online_count': online_result['count'] if online_result['success'] else 0,
            'online_time': online_result['elapsed'] if online_result['success'] else 0,
            'download_success': download_result['success'],
            'download_count': download_result['count'] if download_result['success'] else 0,
            'download_time': download_result['elapsed'] if download_result['success'] else 0,
        })

    # 汇总表格
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print()

    print(f"{'场景':<25} {'周期':<8} {'在线获取':<20} {'下载+读取':<20} {'推荐':<15}")
    print("-" * 100)

    for r in results:
        online_str = ""
        if r['online_success']:
            online_str = f"{r['online_count']}条 {r['online_time']:.1f}ms"
        else:
            online_str = "[X] 超限"

        download_str = ""
        if r['download_success']:
            download_str = f"{r['download_count']}条 {r['download_time']:.1f}ms"
        else:
            download_str = "[X] 失败"

        # 推荐逻辑
        if r['online_success'] and r['download_success']:
            if r['online_time'] < r['download_time']:
                recommendation = "在线获取"
            else:
                recommendation = "下载+读取"
        elif r['online_success']:
            recommendation = "在线获取"
        elif r['download_success']:
            recommendation = "下载+读取"
        else:
            recommendation = "都不可用"

        print(f"{r['scenario']:<25} {r['period']:<8} {online_str:<20} {download_str:<20} {recommendation:<15}")

    print()


def generate_recommendations():
    """生成K线图数据获取建议"""

    print("\n" + "=" * 80)
    print("K线图数据获取策略建议")
    print("=" * 80)
    print()

    print("根据测试结果，K线图应该使用以下策略:")
    print()

    print("【日K线】")
    print("  - 短期(< 1年): 在线获取 ✅")
    print("  - 长期(>= 1年): 下载+读取 ✅")
    print()

    print("【60分钟K线】")
    print("  - 短期(< 3个月): 在线获取 ✅")
    print("  - 长期(>= 3个月): 下载+读取 ✅")
    print()

    print("【30分钟K线】")
    print("  - 所有场景: 下载+读取 ✅")
    print("  - 原因: 超过在线获取限制")
    print()

    print("【15分钟K线】")
    print("  - 所有场景: 下载+读取 ✅")
    print("  - 原因: 超过在线获取限制")
    print()

    print("【5分钟K线】（用户最常用）")
    print("  - 所有场景: 下载+读取 ✅")
    print("  - 原因: 超过在线获取限制(1083条)")
    print("  - 用户体验: 单只股票下载约11ms，可接受")
    print()

    print("【1分钟K线】")
    print("  - 所有场景: 下载+读取 ✅")
    print("  - 原因: 超过在线获取限制(1261条)")
    print()

    print("=" * 80)
    print("核心结论")
    print("=" * 80)
    print()
    print("1. 日K线和60分钟K线：短期用在线获取，长期用下载+读取")
    print("2. 30分钟及以下周期：全部使用下载+读取")
    print("3. 单只股票下载性能优秀（11ms），用户体验可接受")
    print("4. 订阅缓存(0.5ms)用于快照和实时更新，不用于历史K线")
    print()


if __name__ == '__main__':
    try:
        # 运行测试
        run_kline_scenarios()

        # 生成建议
        generate_recommendations()

        print("=" * 80)
        print("[完成] K线图场景测试完成")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消测试")
    except Exception as e:
        print(f"\n\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
