# -*- coding: utf-8 -*-
"""
批量修复 LocalDB 数据

从在线源重新下载历史数据并保存到 LocalDB
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from myquant.core.market.adapters import get_adapter
from loguru import logger


def fix_localdb(symbols, periods=None, source='pytdx', max_bars_per_request=800, target_count=5000):
    """
    批量修复 LocalDB 数据

    Args:
        symbols: 股票代码列表
        periods: 周期列表，默认 ['1d', '5m']
        source: 数据源，默认 'pytdx'
        max_bars_per_request: 每次请求最大条数（PyTdx限制约800）
        target_count: 目标总条数（默认5000，约20年日线数据）
    """
    if periods is None:
        periods = ['1d', '5m']

    total = len(symbols) * len(periods)
    completed = 0

    logger.info(f"开始修复 LocalDB 数据: {len(symbols)} 只股票 x {len(periods)} 个周期，目标 {target_count} 条/周期")

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
                logger.info(f"[{percentage:3d}%] 正在获取 {symbol} {period}（目标 {target_count} 条）...")

                # 分页获取所有数据
                all_dfs = []
            start_pos = 0

                while len(all_dfs) * max_bars_per_request < target_count:
                    df_dict = online_adapter.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=max_bars_per_request
                    )

                    if symbol not in df_dict or df_dict[symbol].empty:
                        logger.info(f"  无更多数据（已获取 {len(all_dfs) * max_bars_per_request} 条）")
                        break

                    current_df = df_dict[symbol]
                    all_dfs.append(current_df)
                    logger.info(f"  第 {len(all_dfs)} 批: {len(current_df)} 条 ({current_df['datetime'].iloc[-1]} ~ {current_df['datetime'].iloc[0]})")

                    # 如果返回的数据少于请求的数量，说明已经到底了
                    if len(current_df) < max_bars_per_request:
                        break

                # 合并所有批次的数据
                if all_dfs:
                    import pandas as pd
                    df = pd.concat(all_dfs, ignore_index=True)
                    # 去重（按datetime）
                    df = df.drop_duplicates(subset=['datetime']).sort_values('datetime').reset_index(drop=True)

                    logger.info(f"  合并后共 {len(df)} 条: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")

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

    parser = argparse.ArgumentParser(description='批量修复 LocalDB 数据')
    parser.add_argument('--symbols', nargs='+', help='股票代码列表，如: 601939.SH 600519.SH')
    parser.add_argument('--source', default='pytdx', help='数据源 (pytdx/xtquant/tdxquant)')
    parser.add_argument('--yes', action='store_true', help='跳过确认直接执行')

    args = parser.parse_args()

    if args.symbols:
        symbols = args.symbols
    else:
        symbols = DEFAULT_SYMBOLS

    print("\n" + "="*60)
    print("  LocalDB 批量修复工具")
    print("="*60)
    print(f"\n将修复以下股票: {', '.join(symbols)}")
    print(f"数据源: {args.source}")

    if not args.yes:
        confirm = input("\n确认执行？(y/n): ").strip().lower()
        if confirm != 'y':
            print("\n已取消")
            sys.exit(0)

    print()
    fix_localdb(symbols, source=args.source)
