# -*- coding: utf-8 -*-
"""
批量修复 LocalDB 数据（分页版本）

从在线源重新下载完整历史数据并保存到 LocalDB
支持分页获取，突破 PyTdx 800 条限制
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from myquant.core.market.adapters import get_adapter
from loguru import logger
import pandas as pd


def fetch_full_history_kline(symbol, period, adapter, target_count=5000):
    """
    分页获取完整历史K线数据

    Args:
        symbol: 股票代码
        period: 周期
        adapter: PyTdx 适配器实例
        target_count: 目标总条数

    Returns:
        完整的 DataFrame 或 None
    """
    # 只有 PyTdx 支持分页获取
    if adapter._name != 'pytdx':
        logger.warning(f"数据源 {adapter._name} 不支持分页，使用单次请求")
        df_dict = adapter.get_kline(symbols=[symbol], period=period, count=target_count)
        return df_dict.get(symbol)

    if not adapter._ensure_connected():
        logger.error(f"无法连接 PyTdx 服务器")
        return None

    try:
        market = adapter._get_market(symbol)
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        category = adapter._to_category(period)

        all_data = []
        start_pos = 0
        max_per_request = 800

        while len(all_data) < target_count:
            request_count = min(max_per_request, target_count - len(all_data))

            logger.info(f"  请求第 {start_pos // max_per_request + 1} 批: start={start_pos}, count={request_count}")

            data = adapter._api.get_security_bars(category, market, code, start_pos, request_count)

            if not data or len(data) == 0:
                logger.info(f"  无更多数据（已获取 {len(all_data)} 条）")
                break

            all_data.extend(data)
            logger.info(f"    获取 {len(data)} 条")

            # 如果返回的数据少于请求的数量，说明已经到底了
            if len(data) < request_count:
                break

            start_pos += request_count

        if all_data:
            df = pd.DataFrame(all_data)

            # 分钟线 vol 是股（shares），日线 vol 是手（lots），统一÷100转为手
            is_daily = period in ('1d', '1D', 'day', 'd')
            if not is_daily and 'vol' in df.columns:
                df['vol'] = df['vol'] / 100

            return adapter._normalize_kline_df(df, 'pytdx')

    except Exception as e:
        logger.error(f"分页获取失败: {e}")
        return None


def fix_localdb(symbols, periods=None, source='pytdx', target_count=5000):
    """
    批量修复 LocalDB 数据

    Args:
        symbols: 股票代码列表
        periods: 周期列表，默认 ['1d', '5m']
        source: 数据源，默认 'pytdx'
        target_count: 目标总条数（默认5000，约20年日线数据）
    """
    if periods is None:
        periods = ['1d', '5m']

    total = len(symbols) * len(periods)
    completed = 0

    logger.info(f"开始修复 LocalDB 数据: {len(symbols)} 只股票 x {len(periods)} 个周期")
    logger.info(f"数据源: {source}, 目标: {target_count} 条/周期")

    # 获取适配器
    online_adapter = get_adapter(source)
    localdb_adapter = get_adapter('localdb')

    if not online_adapter or not online_adapter.is_available():
        logger.error(f"在线数据源 {source} 不可用")
        return False

    if not localdb_adapter or not localdb_adapter.is_available():
        logger.error(f"LocalDB 适配器不可用")
        return False

    results = {}

    for symbol in symbols:
        results[symbol] = {}

        for period in periods:
            completed += 1
            percentage = int((completed / total) * 100)

            try:
                logger.info(f"[{percentage:3d}%] 正在获取 {symbol} {period}...")

                # 分页获取完整数据
                df = fetch_full_history_kline(symbol, period, online_adapter, target_count)

                if df is not None and not df.empty:
                    # 去重并排序
                    df = df.drop_duplicates(subset=['datetime']).sort_values('datetime').reset_index(drop=True)

                    logger.info(f"  共获取 {len(df)} 条: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")

                    # 保存到 LocalDB
                    success = localdb_adapter.save_kline(symbol, df, period)

                    if success:
                        results[symbol][period] = {'success': True, 'count': len(df)}
                        logger.info(f"  ✓ 保存成功")
                    else:
                        results[symbol][period] = {'success': False, 'error': '保存失败'}
                        logger.warning(f"  ✗ 保存失败")
                else:
                    results[symbol][period] = {'success': False, 'error': '无数据'}
                    logger.warning(f"  ✗ 无数据")

            except Exception as e:
                results[symbol][period] = {'success': False, 'error': str(e)}
                logger.error(f"  ✗ 错误: {e}")

    # 汇总结果
    logger.info("\n" + "="*60)
    logger.info("修复完成！")
    logger.info("="*60)

    success_count = 0
    failed_count = 0

    for symbol in symbols:
        logger.info(f"\n{symbol}:")
        for period in periods:
            result = results[symbol].get(period, {})
            if result.get('success'):
                success_count += 1
                logger.info(f"  {period}: ✓ {result.get('count', 0)} 条")
            else:
                failed_count += 1
                logger.info(f"  {period}: ✗ {result.get('error', '未知错误')}")

    logger.info(f"\n总计: 成功 {success_count} 项, 失败 {failed_count} 项")

    return failed_count == 0


if __name__ == '__main__':
    import argparse

    # 默认修复常见的自选股
    DEFAULT_SYMBOLS = [
        '601939.SH',  # 建设银行
        '600519.SH',  # 贵州茅台
        '600000.SH',  # 浦发银行
        '000001.SZ',  # 平安银行
        '000002.SZ',  # 万科A
        '600036.SH',  # 招商银行
        '601318.SH',  # 中国平安
    ]

    parser = argparse.ArgumentParser(description='批量修复 LocalDB 数据（支持分页获取完整历史）')
    parser.add_argument('--symbols', nargs='+', help='股票代码列表，如: 601939.SH 600519.SH')
    parser.add_argument('--source', default='pytdx', help='数据源 (pytdx/xtquant/tdxquant)')
    parser.add_argument('--target-count', type=int, default=5000, help='目标总条数（默认5000，约20年日线）')
    parser.add_argument('--yes', action='store_true', help='跳过确认直接执行')

    args = parser.parse_args()

    if args.symbols:
        symbols = args.symbols
    else:
        symbols = DEFAULT_SYMBOLS

    print("\n" + "="*60)
    print("  LocalDB 批量修复工具（分页版本）")
    print("="*60)
    print(f"\n将修复以下股票: {', '.join(symbols)}")
    print(f"数据源: {args.source}")
    print(f"目标条数: {args.target_count} 条/周期")

    if not args.yes:
        confirm = input("\n确认执行？(y/n): ").strip().lower()
        if confirm != 'y':
            print("\n已取消")
            sys.exit(0)

    print()
    fix_localdb(symbols, source=args.source, target_count=args.target_count)
