# -*- coding: utf-8 -*-
"""
使用 XtQuant 批量下载完整历史数据

XtQuant 连接服务器，可以下载更长的历史数据：
- 日线：730天（2年）
- 5分钟：60天
- 1分钟：通过多次下载获取
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# 直接导入 xtdata
try:
    from xtquant import xtdata
    XTQUANT_AVAILABLE = True
except ImportError:
    XTQUANT_AVAILABLE = False

from myquant.core.market.adapters import get_adapter
from loguru import logger
import time


def download_with_xtquant(symbol, period, target_days=730):
    """
    使用 XtQuant 下载完整历史数据

    Args:
        symbol: 股票代码
        period: 周期 (1d/5m/1m)
        target_days: 目标天数

    Returns:
        DataFrame 或 None
    """
    if not XTQUANT_AVAILABLE:
        logger.error("xtquant 未安装")
        return None

    # 获取 adapter 用于转换格式
    adapter = get_adapter('xtquant')
    if not adapter:
        logger.error("XtQuant 适配器不可用")
        return None

    xt_period = adapter._to_xt_period(period)
    xt_symbol = adapter._to_xt_symbol(symbol)

    logger.info(f"[XtQuant下载] {symbol} {period} (目标 {target_days} 天)")

    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=target_days)

    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')

    logger.info(f"[同步下载] 开始: {symbol} {xt_period} {start_str}~{end_str}")

    try:
        # 调用 xtdata 下载数据
        xtdata.download_history_data(
            stock_code=xt_symbol,
            period=xt_period,
            start_time=start_str,
            end_time=end_str
        )

        logger.info(f"[同步下载] 完成: {symbol} {xt_period}")
        time.sleep(1)

        # 读取下载的数据
        field_list = ['time', 'open', 'high', 'low', 'close', 'volume', 'amount']
        data = xtdata.get_market_data_ex(
            field_list=field_list,
            stock_list=[xt_symbol],
            period=xt_period,
            start_time=start_str,
            end_time=end_str,
            count=0,
            dividend_type='none'
        )

        if data and xt_symbol in data:
            df = data[xt_symbol]
            if df is not None and not df.empty:
                logger.info(f"[XtQuant下载] 成功: {symbol} {period} {len(df)} 条")
                logger.info(f"  范围: {df.index[0]} ~ {df.index[-1]}")
                # _normalize_kline_df 可能返回 datetime 作为索引，需要重置
                df_norm = adapter._normalize_kline_df(df, 'xtquant_local')
                if df_norm.index.name == 'datetime' or 'datetime' in str(df_norm.index.names):
                    df_norm = df_norm.reset_index()
                return df_norm

    except Exception as e:
        logger.error(f"[XtQuant下载] 失败: {e}")

    return None


def batch_download_xtquant(symbols, periods=None, target_days=730, save_to_localdb=True):
    """
    批量下载 XtQuant 历史数据

    Args:
        symbols: 股票代码列表
        periods: 周期列表，默认 ['1d', '5m', '1m']
        target_days: 目标天数
        save_to_localdb: 是否保存到 LocalDB
    """
    if periods is None:
        periods = ['1d', '5m', '1m']

    total = len(symbols) * len(periods)

    logger.info(f"开始批量下载: {len(symbols)} 只股票 x {len(periods)} 个周期")
    logger.info(f"数据源: XtQuant, 目标: {target_days} 天")
    logger.info(f"保存到 LocalDB: {save_to_localdb}")

    # 获取适配器
    localdb_adapter = get_adapter('localdb') if save_to_localdb else None

    results = {}
    completed = 0

    for symbol in symbols:
        results[symbol] = {}

        for period in periods:
            completed += 1
            percentage = int((completed / total) * 100)

            try:
                logger.info(f"[{percentage:3d}%] 正在下载 {symbol} {period}...")

                # 确定目标天数
                if period == '1d':
                    days = 730
                elif period == '5m':
                    days = 60
                else:  # 1m
                    days = 7  # 1分钟只保留7天

                # 下载数据
                df = download_with_xtquant(symbol, period, target_days=days)

                if df is not None and not df.empty:
                    # 确保 datetime 是列而不是索引，XtQuant 返回的是 'time' 列
                    logger.debug(f"  下载后列: {list(df.columns)}")

                    # 将 time 列重命名为 datetime（LocalDB 需要）
                    if 'time' in df.columns and 'datetime' not in df.columns:
                        df = df.rename(columns={'time': 'datetime'})

                    # 确保索引是数字索引
                    if df.index.name == 'datetime' or 'datetime' in str(df.index.names):
                        df = df.reset_index(drop=True)
                    elif 'index' in df.columns:
                        df = df.reset_index(drop=True)

                    # 去重并排序
                    df = df.drop_duplicates(subset=['datetime']).sort_values('datetime').reset_index(drop=True)

                    logger.info(f"  共获取 {len(df)} 条: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")

                    # 保存到 LocalDB
                    if localdb_adapter:
                        success = localdb_adapter.save_kline(symbol, df, period)
                        if success:
                            results[symbol][period] = {'success': True, 'count': len(df)}
                            logger.info(f"  ✓ 保存到 LocalDB 成功")
                        else:
                            results[symbol][period] = {'success': False, 'error': '保存失败'}
                            logger.warning(f"  ✗ 保存失败")
                    else:
                        results[symbol][period] = {'success': True, 'count': len(df)}
                else:
                    results[symbol][period] = {'success': False, 'error': '无数据'}
                    logger.warning(f"  ✗ 无数据")

            except Exception as e:
                results[symbol][period] = {'success': False, 'error': str(e)}
                logger.error(f"  ✗ 错误: {e}")

    # 汇总结果
    logger.info("\n" + "="*60)
    logger.info("下载完成！")
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

    # 默认股票
    DEFAULT_SYMBOLS = [
        '601939.SH',  # 建设银行
        '600519.SH',  # 贵州茅台
        '600000.SH',  # 浦发银行
        '000001.SZ',  # 平安银行
        '000002.SZ',  # 万科A
        '600036.SH',  # 招商银行
        '601318.SH',  # 中国平安
    ]

    parser = argparse.ArgumentParser(description='使用 XtQuant 批量下载完整历史数据')
    parser.add_argument('--symbols', nargs='+', help='股票代码列表')
    parser.add_argument('--periods', nargs='+', default=['1d', '5m', '1m'], help='周期列表')
    parser.add_argument('--no-save', action='store_true', help='不保存到 LocalDB')
    parser.add_argument('--yes', action='store_true', help='跳过确认')

    args = parser.parse_args()

    symbols = args.symbols if args.symbols else DEFAULT_SYMBOLS

    print("\n" + "="*60)
    print("  XtQuant 批量下载工具")
    print("="*60)
    print(f"\n将下载以下股票: {', '.join(symbols)}")
    print(f"周期: {', '.join(args.periods)}")
    print(f"保存到 LocalDB: {not args.no_save}")

    if not args.yes:
        confirm = input("\n确认执行？(y/n): ").strip().lower()
        if confirm != 'y':
            print("\n已取消")
            sys.exit(0)

    print()
    batch_download_xtquant(
        symbols,
        periods=args.periods,
        save_to_localdb=not args.no_save
    )
