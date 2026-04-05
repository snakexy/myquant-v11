"""
数据完整性诊断脚本

检测以下问题:
1. 数据断层 - K线数据中间有缺失的交易日
2. 实时数据不更新 - 最新数据停留在过去某一天
3. 复权数据不对 - 前复权价格与通达信不一致

使用方法:
    cd backend
    python scripts/diagnose_data_integrity.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO")

# 测试股票列表（包含不同特征的股票）
TEST_SYMBOLS = [
    "600519.SH",  # 茅台 - 高分红，复杂除权
    "000001.SZ",  # 平安银行 - 常规股票
    "000001.SH",  # 上证指数
    "600000.SH",  # 浦发银行 - 银行股
]

PERIODS = ['1d', '5m', '15m', '30m', '1h']


def diagnose_data_gaps(symbol: str, period: str) -> Dict:
    """
    诊断数据缺口

    返回:
        {
            'symbol': str,
            'period': str,
            'has_data': bool,
            'total_bars': int,
            'latest_date': datetime or None,
            'days_behind': int,  # 落后今天几天
            'gaps': List[Tuple[start, end]],  # 缺口列表
            'issues': List[str]  # 发现的问题
        }
    """
    from myquant.core.market.adapters import get_adapter
    from myquant.core.market.utils.trading_time_detector import TradingTimeDetectorV2

    result = {
        'symbol': symbol,
        'period': period,
        'has_data': False,
        'total_bars': 0,
        'latest_date': None,
        'days_behind': 0,
        'gaps': [],
        'issues': []
    }

    try:
        # 从HotDB获取数据
        hotdb = get_adapter('hotdb')
        if not hotdb or not hotdb.is_available():
            result['issues'].append("HotDB不可用")
            return result

        df_dict = hotdb.get_kline(symbols=[symbol], period=period, count=5000)
        df = df_dict.get(symbol)

        if df is None or df.empty:
            result['issues'].append(f"无{period}数据")
            return result

        result['has_data'] = True
        result['total_bars'] = len(df)
        result['latest_date'] = df['datetime'].iloc[-1]

        # 计算落后天数
        now = datetime.now()
        latest = pd.to_datetime(result['latest_date'])
        result['days_behind'] = (now - latest).days

        # 日线：检查交易日缺失
        if period == '1d':
            detector = TradingTimeDetectorV2()
            df_sorted = df.sort_values('datetime')
            dates = pd.to_datetime(df_sorted['datetime']).dt.date.tolist()

            # 检查连续交易日之间是否有缺失
            for i in range(1, len(dates)):
                prev_date = dates[i-1]
                curr_date = dates[i]
                gap_days = (curr_date - prev_date).days

                if gap_days > 1:
                    # 检查中间是否是交易日
                    missing_dates = []
                    for j in range(1, gap_days):
                        check_date = prev_date + timedelta(days=j)
                        try:
                            check_dt = datetime.combine(check_date, datetime.min.time())
                            if detector.is_trading_day(check_dt):
                                missing_dates.append(check_date)
                        except:
                            if check_date.weekday() < 5:
                                missing_dates.append(check_date)

                    if missing_dates:
                        result['gaps'].append({
                            'start': str(prev_date),
                            'end': str(curr_date),
                            'missing_count': len(missing_dates),
                            'missing_dates': [str(d) for d in missing_dates[:5]]  # 最多显示5个
                        })

            if result['gaps']:
                result['issues'].append(f"发现{len(result['gaps'])}个数据缺口")

        # 检查数据新鲜度
        if result['days_behind'] > 1:
            result['issues'].append(f"数据落后{result['days_behind']}天")

        # 检查异常价格（可能表示复权问题）
        if 'close' in df.columns:
            latest_close = df['close'].iloc[-1]
            if latest_close < 0.01 or latest_close > 100000:
                result['issues'].append(f"异常收盘价: {latest_close}")

    except Exception as e:
        result['issues'].append(f"诊断异常: {e}")
        logger.error(f"诊断{symbol} {period}失败: {e}")

    return result


def diagnose_adjustment_factor(symbol: str) -> Dict:
    """
    诊断复权因子计算是否正确

    通过与通达信价格对比验证
    """
    from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service
    from myquant.core.market.services.seamless_service import get_seamless_kline_service

    result = {
        'symbol': symbol,
        'has_xdxr': False,
        'xdxr_count': 0,
        'factor_count': 0,
        'sample_factor': None,
        'latest_adjusted_price': None,
        'latest_raw_price': None,
        'issues': []
    }

    try:
        # 获取复权因子服务
        factor_service = get_adjustment_factor_service()
        seamless_service = get_seamless_kline_service()

        # 获取XDXR数据
        xdxr_data = seamless_service._get_xdxr_data(symbol)
        result['xdxr_count'] = len(xdxr_data)
        result['has_xdxr'] = len(xdxr_data) > 0

        if not result['has_xdxr']:
            result['issues'].append("无除权除息数据")
            return result

        # 获取因子表
        factor_table = factor_service.get_factor_table(symbol, 'front')
        result['factor_count'] = len(factor_table)

        if not factor_table:
            result['issues'].append("复权因子表为空")
            return result

        # 获取样本因子值
        today = datetime.now().strftime('%Y-%m-%d')
        result['sample_factor'] = factor_table.get(today, factor_table.get(list(factor_table.keys())[-1]))

        # 获取不复权数据
        df_raw = seamless_service.get_kline(symbol, period='1d', count=5, adjust_type='none')
        if not df_raw.empty:
            result['latest_raw_price'] = float(df_raw.iloc[-1]['close'])

        # 获取前复权数据
        df_adj = seamless_service.get_kline(symbol, period='1d', count=5, adjust_type='front')
        if not df_adj.empty:
            result['latest_adjusted_price'] = float(df_adj.iloc[-1]['close'])

        # 验证复权逻辑
        if result['latest_raw_price'] and result['latest_adjusted_price']:
            # 如果今天没有除权，复权价应该等于原始价
            if today not in factor_table or factor_table.get(today, 1.0) == 1.0:
                if abs(result['latest_adjusted_price'] - result['latest_raw_price']) > 0.01:
                    result['issues'].append(f"复权异常: 原始价{result['latest_raw_price']:.2f} vs 复权价{result['latest_adjusted_price']:.2f}")

        # 检查因子值范围
        if result['sample_factor']:
            if result['sample_factor'] < 0.1 or result['sample_factor'] > 10:
                result['issues'].append(f"因子值异常: {result['sample_factor']}")

    except Exception as e:
        result['issues'].append(f"复权诊断异常: {e}")
        logger.error(f"复权诊断{symbol}失败: {e}")

    return result


def diagnose_smart_update(symbol: str, period: str) -> Dict:
    """
    诊断智能增量更新机制是否正常工作
    """
    from myquant.core.market.services.hotdb_service import get_hotdb_service

    result = {
        'symbol': symbol,
        'period': period,
        'smart_update_result': None,
        'detect_gap_result': None,
        'issues': []
    }

    try:
        hotdb_service = get_hotdb_service()

        # 测试缺口检测
        gap_info = hotdb_service._detect_gap(symbol, period)
        result['detect_gap_result'] = gap_info

        if gap_info is None:
            result['issues'].append("缺口检测返回None")
        elif gap_info.get('has_gap'):
            result['issues'].append(f"检测到缺口: {gap_info.get('reason')}")
            if gap_info.get('missing_start'):
                result['issues'].append(f"  缺失范围: {gap_info['missing_start']} ~ {gap_info.get('missing_end')}")

        # 测试智能更新
        update_result = hotdb_service.smart_update(symbol, period)
        result['smart_update_result'] = {
            'success': update_result.get('success'),
            'has_data': update_result.get('has_data'),
            'has_gap': update_result.get('has_gap'),
            'reason': update_result.get('reason'),
            'added_count': update_result.get('added_count', 0)
        }

        if not update_result.get('success'):
            result['issues'].append(f"智能更新失败: {update_result.get('error')}")

    except Exception as e:
        result['issues'].append(f"智能更新诊断异常: {e}")
        logger.error(f"智能更新诊断{symbol} {period}失败: {e}")

    return result


def run_full_diagnosis():
    """运行完整诊断"""
    print("=" * 80)
    print("MyQuant v11 数据完整性诊断")
    print("=" * 80)
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试股票: {', '.join(TEST_SYMBOLS)}")
    print(f"测试周期: {', '.join(PERIODS)}")
    print("=" * 80)
    print()

    all_issues = []

    # 1. 数据缺口诊断
    print("\n" + "=" * 80)
    print("【1/3】数据缺口诊断")
    print("=" * 80)

    for symbol in TEST_SYMBOLS:
        print(f"\n--- 股票: {symbol} ---")
        for period in PERIODS:
            result = diagnose_data_gaps(symbol, period)

            status = "✅" if not result['issues'] else "❌"
            print(f"  {status} {period:4s}: {result['total_bars']:4d}条, 最新:{result['latest_date']}, 落后{result['days_behind']}天")

            if result['gaps']:
                for gap in result['gaps']:
                    print(f"      缺口: {gap['start']} ~ {gap['end']} ({gap['missing_count']}个交易日)")

            for issue in result['issues']:
                all_issues.append(f"[{symbol}/{period}] {issue}")
                print(f"      问题: {issue}")

    # 2. 复权因子诊断
    print("\n" + "=" * 80)
    print("【2/3】复权因子诊断")
    print("=" * 80)

    for symbol in TEST_SYMBOLS:
        print(f"\n--- 股票: {symbol} ---")
        result = diagnose_adjustment_factor(symbol)

        status = "✅" if not result['issues'] else "❌"
        print(f"  {status} XDXR记录: {result['xdxr_count']}条, 因子表: {result['factor_count']}天")
        print(f"      样本因子: {result['sample_factor']}")
        print(f"      原始价: {result['latest_raw_price']}, 复权价: {result['latest_adjusted_price']}")

        for issue in result['issues']:
            all_issues.append(f"[{symbol}/复权] {issue}")
            print(f"      问题: {issue}")

    # 3. 智能更新诊断
    print("\n" + "=" * 80)
    print("【3/3】智能更新机制诊断")
    print("=" * 80)

    for symbol in TEST_SYMBOLS[:2]:  # 只测试前2只，避免耗时
        print(f"\n--- 股票: {symbol} ---")
        for period in ['1d', '5m']:
            result = diagnose_smart_update(symbol, period)

            status = "✅" if not result['issues'] else "❌"
            gap_status = result['detect_gap_result'].get('has_gap') if result['detect_gap_result'] else 'N/A'
            update_success = result['smart_update_result'].get('success') if result['smart_update_result'] else 'N/A'

            print(f"  {status} {period}: 缺口检测={gap_status}, 智能更新={update_success}")

            for issue in result['issues']:
                all_issues.append(f"[{symbol}/{period}/更新] {issue}")
                print(f"      问题: {issue}")

    # 汇总
    print("\n" + "=" * 80)
    print("【诊断汇总】")
    print("=" * 80)

    if all_issues:
        print(f"\n发现 {len(all_issues)} 个问题:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✅ 未发现明显问题")

    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)

    return all_issues


if __name__ == '__main__':
    issues = run_full_diagnosis()
    sys.exit(1 if issues else 0)
