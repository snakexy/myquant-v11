#!/usr/bin/env python3
"""
数据完整性系统性修复脚本

修复以下问题:
1. 实时数据不更新 - 强制从在线源补全
2. 智能更新机制失效 - 修复检测逻辑
3. 预热机制不完善 - 确保所有自选股都已预热

使用方法:
    cd backend
    python scripts/fix_data_integrity.py [symbol1,symbol2,...]

    # 修复特定股票
    python scripts/fix_data_integrity.py 600519.SH

    # 修复所有测试股票
    python scripts/fix_data_integrity.py --all
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logging
logging.disable(logging.CRITICAL)
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

# 默认测试股票
DEFAULT_SYMBOLS = ['600519.SH', '000001.SZ', '600000.SH', '000002.SZ']


def check_data_source_availability():
    """检查数据源可用性"""
    print("=" * 60)
    print("【步骤1】检查数据源可用性")
    print("=" * 60)

    from myquant.core.market.adapters import get_adapter

    sources = ['pytdx', 'xtquant', 'tdxquant', 'localdb', 'hotdb']
    available = []

    for source in sources:
        try:
            adapter = get_adapter(source)
            if adapter and adapter.is_available():
                available.append(source)
                print(f"  [OK] {source}: 可用")
            else:
                print(f"  [X] {source}: 不可用")
        except Exception as e:
            print(f"  [X] {source}: 异常 - {e}")

    print(f"\n可用数据源: {available}")
    return available


def fix_symbol_data(symbol: str, periods: List[str] = None) -> Dict:
    """
    修复单只股票的数据完整性

    修复流程:
    1. 检查HotDB是否有数据
    2. 检测数据缺口
    3. 从在线源强制补全
    4. 验证修复结果
    """
    if periods is None:
        periods = ['1d', '5m']

    from myquant.core.market.adapters import get_adapter
    from myquant.core.market.services.hotdb_service import get_hotdb_service

    result = {
        'symbol': symbol,
        'fixed': False,
        'issues': [],
        'details': {}
    }

    print(f"\n  修复股票: {symbol}")
    print(f"  {'-' * 50}")

    try:
        hotdb = get_adapter('hotdb')
        hotdb_service = get_hotdb_service()

        if not hotdb or not hotdb.is_available():
            result['issues'].append("HotDB不可用")
            print(f"    [X] HotDB不可用")
            return result

        for period in periods:
            period_result = {
                'before_count': 0,
                'after_count': 0,
                'gap_detected': False,
                'fixed': False
            }

            # 1. 获取当前数据状态
            df_dict = hotdb.get_kline(symbols=[symbol], period=period, count=5000)
            df_before = df_dict.get(symbol)

            if df_before is not None and not df_before.empty:
                period_result['before_count'] = len(df_before)
                latest_before = df_before['datetime'].iloc[-1]
                print(f"    {period}: 当前{len(df_before)}条, 最新{latest_before}")
            else:
                print(f"    {period}: 无数据")

            # 2. 检测缺口
            gap_info = hotdb_service._detect_gap(symbol, period)

            if gap_info and gap_info.get('has_gap'):
                period_result['gap_detected'] = True
                reason = gap_info.get('reason', 'unknown')
                print(f"    [X] 检测到缺口: {reason}")

                # 3. 强制补全数据
                print(f"    正在补全数据...")

                # 使用smart_update进行补全
                update_result = hotdb_service.smart_update(symbol, period)

                if update_result.get('success') and not update_result.get('has_gap'):
                    period_result['fixed'] = True
                    print(f"    [OK] 补全成功")
                else:
                    error = update_result.get('error', update_result.get('reason', 'unknown'))
                    print(f"    [X] 补全失败: {error}")

                    # 尝试强制从在线源获取
                    print(f"    尝试强制从在线源获取...")

                    # 获取数据源
                    from myquant.core.market.routing import get_source_selector, DataLevel
                    selector = get_source_selector()

                    if selector:
                        chain = selector.get_fallback_chain_for_code(DataLevel.L3, symbol)
                        online_sources = [s for s in chain if s not in ('hotdb', 'localdb')]

                        for source_name in online_sources:
                            try:
                                adapter = get_adapter(source_name)
                                if adapter and adapter.is_available():
                                    print(f"      尝试从 {source_name} 获取...")

                                    # 获取数据
                                    df_dict_online = adapter.get_kline(
                                        symbols=[symbol],
                                        period=period,
                                        count=100
                                    )

                                    if symbol in df_dict_online and not df_dict_online[symbol].empty:
                                        df_online = df_dict_online[symbol]

                                        # 保存到HotDB
                                        hotdb.save_kline(symbol, df_online, period)

                                        print(f"      [OK] 从 {source_name} 获取并保存 {len(df_online)} 条")
                                        period_result['fixed'] = True
                                        break
                            except Exception as e:
                                print(f"      [X] {source_name} 失败: {e}")
                                continue
            else:
                print(f"    [OK] 无缺口")
                period_result['fixed'] = True

            # 4. 验证修复结果
            df_dict_after = hotdb.get_kline(symbols=[symbol], period=period, count=5000)
            df_after = df_dict_after.get(symbol)

            if df_after is not None and not df_after.empty:
                period_result['after_count'] = len(df_after)
                latest_after = df_after['datetime'].iloc[-1]

                # 计算是否最新
                days_behind = (datetime.now() - pd.to_datetime(latest_after)).days

                if days_behind <= 1:
                    print(f"    [OK] 验证通过: 最新{latest_after}, 落后{days_behind}天")
                else:
                    print(f"    [X] 仍然落后: 最新{latest_after}, 落后{days_behind}天")
                    period_result['fixed'] = False

            result['details'][period] = period_result

        # 判断是否整体修复成功
        result['fixed'] = all(d.get('fixed', False) for d in result['details'].values())

    except Exception as e:
        result['issues'].append(f"修复异常: {e}")
        print(f"    [X] 修复异常: {e}")

    return result


def batch_fix_symbols(symbols: List[str]) -> Dict:
    """批量修复多只股票"""
    print("\n" + "=" * 60)
    print("【步骤2】批量修复数据")
    print("=" * 60)

    results = {
        'total': len(symbols),
        'fixed': 0,
        'failed': 0,
        'details': []
    }

    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] {symbol}")
        result = fix_symbol_data(symbol)
        results['details'].append(result)

        if result['fixed']:
            results['fixed'] += 1
            print(f"  [OK] 修复成功")
        else:
            results['failed'] += 1
            print(f"  [X] 修复失败: {result['issues']}")

    return results


def verify_fix_results(symbols: List[str]) -> Dict:
    """验证修复结果"""
    print("\n" + "=" * 60)
    print("【步骤3】验证修复结果")
    print("=" * 60)

    from myquant.core.market.adapters import get_adapter

    hotdb = get_adapter('hotdb')

    results = {
        'verified': 0,
        'failed': 0,
        'details': []
    }

    for symbol in symbols:
        try:
            df_dict = hotdb.get_kline(symbols=[symbol], period='1d', count=5)
            df = df_dict.get(symbol)

            if df is not None and not df.empty:
                latest = df['datetime'].iloc[-1]
                days_behind = (datetime.now() - pd.to_datetime(latest)).days

                if days_behind <= 1:
                    results['verified'] += 1
                    print(f"  [OK] {symbol}: 最新{latest}, 落后{days_behind}天")
                else:
                    results['failed'] += 1
                    print(f"  [X] {symbol}: 最新{latest}, 落后{days_behind}天")
            else:
                results['failed'] += 1
                print(f"  [X] {symbol}: 无数据")
        except Exception as e:
            results['failed'] += 1
            print(f"  [X] {symbol}: 验证异常 - {e}")

    return results


def schedule_auto_update(symbols: List[str]):
    """设置自动更新调度"""
    print("\n" + "=" * 60)
    print("【步骤4】设置自动更新")
    print("=" * 60)

    print("  建议配置:")
    print("  1. 启动时自动预热所有自选股")
    print("  2. 每5分钟检查一次数据新鲜度")
    print("  3. 收盘后自动补全当天数据")
    print()
    print("  在main.py中添加以下代码:")
    print("  ```python")
    print("  from myquant.core.market.services.hotdb_service import get_hotdb_service")
    print("  ")
    print("  # 启动时预热")
    print("  hotdb_service = get_hotdb_service()")
    print(f"  hotdb_service.auto_check_and_fill_today({symbols})")
    print("  ```")


def main():
    """主函数"""
    # 解析参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            symbols = DEFAULT_SYMBOLS
        else:
            symbols = sys.argv[1].split(',')
    else:
        symbols = DEFAULT_SYMBOLS

    print("=" * 60)
    print("MyQuant 数据完整性系统性修复")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标股票: {symbols}")
    print("=" * 60)

    # 1. 检查数据源
    available_sources = check_data_source_availability()

    if not available_sources:
        print("\n[X] 没有可用的数据源，无法修复")
        return

    # 2. 批量修复
    fix_results = batch_fix_symbols(symbols)

    # 3. 验证结果
    verify_results = verify_fix_results(symbols)

    # 4. 设置自动更新
    schedule_auto_update(symbols)

    # 汇总
    print("\n" + "=" * 60)
    print("修复汇总")
    print("=" * 60)
    print(f"  总股票数: {fix_results['total']}")
    print(f"  修复成功: {fix_results['fixed']}")
    print(f"  修复失败: {fix_results['failed']}")
    print(f"  验证通过: {verify_results['verified']}")
    print(f"  验证失败: {verify_results['failed']}")
    print("=" * 60)

    if fix_results['failed'] > 0:
        print("\n修复失败的股票:")
        for detail in fix_results['details']:
            if not detail['fixed']:
                print(f"  - {detail['symbol']}: {detail['issues']}")

    print("\n修复完成！")


if __name__ == '__main__':
    main()
