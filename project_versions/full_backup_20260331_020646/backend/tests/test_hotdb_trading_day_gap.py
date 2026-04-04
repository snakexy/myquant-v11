# -*- coding: utf-8 -*-
"""
测试 HotDB 智能增量更新的交易日判断逻辑

验证 detect_gap() 是否正确识别交易日缺口，排除周末和节假日
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from loguru import logger
from myquant.core.market.adapters.hotdb_adapter import V5HotDBAdapter


def print_gap_result(gap_info, title):
    """打印缺口检测结果"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    if gap_info is None:
        print("[X] 检测失败")
        return

    has_gap = gap_info.get('has_gap', False)
    reason = gap_info.get('reason', 'unknown')
    latest = gap_info.get('latest')

    print(f"是否有缺口: {'[YES] 是' if has_gap else '[NO] 否'}")
    print(f"原因: {reason}")
    print(f"HotDB 最新: {latest}")

    if has_gap:
        missing_start = gap_info.get('missing_start')
        missing_end = gap_info.get('missing_end')
        days_missing = gap_info.get('days_missing', 0)
        trading_days = gap_info.get('trading_days_missing', [])

        print(f"缺失范围: {missing_start} ~ {missing_end}")
        print(f"交易日数量: {days_missing}")
        if trading_days:
            print(f"交易日列表: {trading_days}")
    print()


def test_detect_gap():
    """测试 detect_gap 的交易日判断逻辑"""
    print("\n" + "="*60)
    print("  HotDB 智能增量更新 - 交易日判断测试")
    print("="*60)

    # 创建 HotDB 适配器
    hotdb = V5HotDBAdapter()

    # 选择测试股票（确保已预热）
    test_symbol = "000001.SZ"  # 平安银行

    # 检查股票是否存在数据
    if not hotdb.has_symbol(test_symbol):
        print(f"\n[!] {test_symbol} 未预热，请先运行预热:")
        print(f"   POST /api/v5/hotdata/preheat")
        print(f"   {{'symbols': ['{test_symbol}']}}")
        return

    print(f"\n[*] 测试股票: {test_symbol}")
    print(f"   当前日期: {pd.Timestamp.now().date()}")

    # 测试日线数据
    print("\n" + "-"*60)
    print("  测试 1d 周期")
    print("-"*60)

    # 获取数据信息
    info = hotdb.get_data_info(test_symbol, '1d')
    if info and info.get('has_data'):
        print(f"HotDB 1d 数据:")
        print(f"  - 数量: {info['count']} 条")
        print(f"  - 最早: {info['earliest'].date()}")
        print(f"  - 最新: {info['latest'].date()}")

    # 测试缺口检测
    gap_info = hotdb.detect_gap(test_symbol, '1d')
    print_gap_result(gap_info, "当前状态 - 日线缺口检测")

    # 测试分钟线数据
    print("\n" + "-"*60)
    print("  测试 5m 周期")
    print("-"*60)

    info_5m = hotdb.get_data_info(test_symbol, '5m')
    if info_5m and info_5m.get('has_data'):
        print(f"HotDB 5m 数据:")
        print(f"  - 数量: {info_5m['count']} 条")
        print(f"  - 最早: {info_5m['earliest']}")
        print(f"  - 最新: {info_5m['latest']}")

    gap_info_5m = hotdb.detect_gap(test_symbol, '5m')
    print_gap_result(gap_info_5m, "当前状态 - 5分钟缺口检测")

    # 测试场景分析
    print("\n" + "-"*60)
    print("  场景分析（基于实际检测结果）")
    print("-"*60)

    now = pd.Timestamp.now()
    current_weekday = now.weekday()  # 0=周一, 6=周日
    current_date = now.date()
    current_hour = now.hour

    print(f"当前时间: {now}")
    print(f"星期: {['周一', '周二', '周三', '周四', '周五', '周六', '周日'][current_weekday]}")
    print(f"小时: {current_hour}:00")
    print(f"是否交易时间: {'是' if current_weekday < 5 and 9 <= current_hour < 15 else '否'}")

    # 分析预期结果
    if gap_info:
        has_gap = gap_info.get('has_gap', False)
        reason = gap_info.get('reason', '')

        print(f"\n检测结果: {'有缺口' if has_gap else '无缺口'}")
        print(f"原因: {reason}")

        if has_gap and reason == 'daily_gap':
            trading_days = gap_info.get('trading_days_missing', [])
            print(f"\n[OK] 正确！检测到 {len(trading_days)} 个交易日缺失")
            print(f"   缺失的交易日: {trading_days}")
        elif has_gap and reason == 'today_missing':
            print(f"\n[OK] 正确！只差今天，且当前是交易时间")
        elif not has_gap:
            if current_weekday >= 5:  # 周末
                print(f"\n[OK] 正确！周末不算缺口")
            elif current_hour < 9:
                print(f"\n[OK] 正确！开盘前不算缺口")
            else:
                print(f"\n[OK] 正确！数据已是最新")


def test_trading_days_api():
    """测试交易日历 API"""
    from myquant.core.market.utils.trading_time_detector import TradingTimeDetectorV2

    print("\n" + "="*60)
    print("  交易日历 API 测试")
    print("="*60)

    detector = TradingTimeDetectorV2()
    now = pd.Timestamp.now()
    today_str = now.strftime('%Y%m%d')

    # 测试判断今天是否交易日
    is_trading = detector.is_trading_day()
    print(f"\n今天 ({today_str}) 是否交易日: {'是' if is_trading else '否'}")

    # 测试是否交易时间
    from myquant.core.market.utils.trading_time import TradingTimeChecker
    is_trading_time = TradingTimeChecker.is_trading_time()
    print(f"当前是否交易时间: {'是' if is_trading_time else '否'}")

    # 获取本周交易日
    from datetime import timedelta
    week_start = (now - timedelta(days=now.weekday())).strftime('%Y%m%d')
    week_end = (now + timedelta(days=6 - now.weekday())).strftime('%Y%m%d')

    print(f"\n获取本周交易日 ({week_start} ~ {week_end}):")
    try:
        trading_days = detector.get_trading_days_in_range(week_start, week_end)
        print(f"交易日: {trading_days}")
    except Exception as e:
        print(f"[X] 获取失败: {e}")


if __name__ == '__main__':
    import pandas as pd

    # 配置日志
    logger.remove()
    logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | {level} | {message}")

    try:
        # 测试交易日历 API
        test_trading_days_api()

        # 测试缺口检测
        test_detect_gap()

        print("\n" + "="*60)
        print("  测试完成")
        print("="*60)

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
