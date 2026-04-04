# -*- coding: utf-8 -*-
"""
手动下载股票 K 线数据到 LocalDB

使用 pytdx 基础接口下载（绕过连接池）
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from pytdx.hq import TdxHq_API
import pandas as pd
from loguru import logger


def download_to_localdb(symbol: str, period: str = '1d', count: int = 1000):
    """下载单只股票数据到 LocalDB

    Args:
        symbol: 股票代码，如 000001.SZ
        period: 周期，默认 1d
        count: 下载数量
    """
    from myquant.core.market.adapters import get_adapter

    # 解析市场代码
    if symbol.endswith('.SH'):
        market = 1  # 上海
        code = symbol.replace('.SH', '')
    elif symbol.endswith('.SZ'):
        market = 0  # 深圳
        code = symbol.replace('.SZ', '')
    else:
        logger.error(f"无效的股票代码: {symbol}")
        return

    # 使用 pytdx 基础接口
    api = TdxHq_API()
    try:
        # 连接服务器（尝试多个服务器）
        logger.info("连接 pytdx 服务器...")
        servers = [
            ('119.147.212.81', 7709),  # 广州电信
            ('114.80.63.12', 7709),     # 上海电信
            ('60.12.136.250', 7709),    # 备用
        ]

        connected = False
        for host, port in servers:
            try:
                logger.info(f"尝试 {host}:{port}...")
                if api.connect(host, port, time_out=5):
                    connected = True
                    logger.info(f"✅ 连接成功: {host}:{port}")
                    break
            except Exception as e:
                logger.warning(f"❌ {host}:{port} 连接失败: {e}")

        if not connected:
            logger.error("所有服务器连接失败")
            return

        # 周期映射：pytdx category 参数
        # 9=日线, 8=1分钟, 0=5分钟, 1=15分钟, 2=30分钟, 3=60分钟
        period_category_map = {
            '1d': 9,
            '1m': 8,
            '5m': 0,
            '15m': 1,
            '30m': 2,
            '1h': 3,
        }
        category = period_category_map.get(period, 9)

        logger.info(f"下载 {symbol} {period} 数据 (category={category})...")
        data = api.get_security_bars(category, market, code, 0, count)

        if not data:
            logger.error(f"获取数据失败: {symbol}")
            return

        # 转换为 DataFrame
        df = pd.DataFrame(data)

        # pytdx 返回的 datetime 是字符串 "YYYY-MM-DD HH:MM:SS"
        # 分钟线需要保留时间，日线只需要日期
        if period == '1d':
            df['datetime'] = pd.to_datetime(df['datetime'].str.split(' ').str[0])
        else:
            # 分钟线：保留完整时间，但确保时区正确
            df['datetime'] = pd.to_datetime(df['datetime'])

        df = df[['datetime', 'open', 'close', 'high', 'low', 'vol', 'amount']]
        df.columns = ['datetime', 'open', 'close', 'high', 'low', 'volume', 'amount']

        logger.info(f"获取到 {len(df)} 条数据")
        print(df[['datetime', 'open', 'close']].head(5))
        print(df[['datetime', 'open', 'close']].tail(5))

        # 保存到 LocalDB
        localdb = get_adapter('localdb')
        if localdb and localdb.is_available():
            success = localdb.save_kline(symbol, df, period)
            if success:
                logger.info(f"✅ 已保存 {symbol} {len(df)} 条到 LocalDB")
            else:
                logger.error(f"❌ 保存失败: {symbol}")
        else:
            logger.error("LocalDB 不可用")

    finally:
        api.disconnect()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='下载股票数据到 LocalDB')
    parser.add_argument('symbol', help='股票代码，如 000001.SZ')
    parser.add_argument('--count', type=int, default=1000, help='下载数量')
    parser.add_argument('--period', default='1d', help='周期')

    args = parser.parse_args()

    download_to_localdb(args.symbol, args.period, args.count)
