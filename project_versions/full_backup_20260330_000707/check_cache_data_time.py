# -*- coding: utf-8 -*-
"""
查看 refresh_kline 缓存数据的实际时间范围
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加 SDK 路径
sdk_path = Path(__file__).parent / "backend" / "external" / "tdxquant_sdk"
if str(sdk_path) not in sys.path:
    sys.path.insert(0, str(sdk_path))

from tqcenter import tq

# 初始化配置
DLL_PATH = r'E:\new_tdx64\PYPlugins\TPythClient.dll'
INIT_PATH = r'E:\new_tdx64\PYPlugins\user\myquant_init.py'


def show_data_time_range(stock_code, period):
    """查看数据的时间范围"""
    print("\n股票: {}, 周期: {}".format(stock_code, period))
    print("-" * 50)

    try:
        # 获取数据（不限制条数）
        result = tq.get_market_data(
            stock_list=[stock_code],
            period=period,
            count=500  # 获取更多数据
        )

        if result and stock_code in result:
            data = result[stock_code]
            print("数据条数: {}".format(len(data)))

            if len(data) > 0:
                # 显示最早和最新的数据
                first = data[0]
                last = data[-1]

                print("\n最早数据:")
                print("  时间: {}".format(first.get('time', 'N/A')))
                print("  开盘: {}, 最高: {}, 最低: {}, 收盘: {}".format(
                    first.get('open', 'N/A'), first.get('high', 'N/A'),
                    first.get('low', 'N/A'), first.get('close', 'N/A')
                ))

                print("\n最新数据:")
                print("  时间: {}".format(last.get('time', 'N/A')))
                print("  开盘: {}, 最高: {}, 最低: {}, 收盘: {}".format(
                    last.get('open', 'N/A'), last.get('high', 'N/A'),
                    last.get('low', 'N/A'), last.get('close', 'N/A')
                ))

                # 显示最后3条数据
                print("\n最后3条数据:")
                for i, bar in enumerate(data[-3:], 1):
                    print("  {}. {} | O:{} H:{} L:{} C:{} V:{}".format(
                        i, bar.get('time', 'N/A'),
                        bar.get('open', 'N/A'), bar.get('high', 'N/A'),
                        bar.get('low', 'N/A'), bar.get('close', 'N/A'),
                        bar.get('volume', 'N/A')
                    ))
        else:
            print("无数据返回")

    except Exception as e:
        import traceback
        print("查询出错: {}".format(e))
        print(traceback.format_exc())


def main():
    print("=" * 60)
    print("TdxQuant 缓存数据时间范围查看")
    print("=" * 60)
    print("当前时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print()

    # 初始化
    if not (hasattr(tq, '_initialized') and tq._initialized):
        tq.dll_path = DLL_PATH
        try:
            print("初始化 TdxQuant...")
            tq.initialize(path=INIT_PATH)
            print("[OK] 初始化成功\n")
        except Exception as e:
            print("[ERROR] 初始化失败: {}".format(e))
            return

    # 测试不同股票和周期
    test_cases = [
        ("600000.SH", "1d"),   # 浦发银行 日线
        ("600519.SH", "1d"),   # 茅台 日线
        ("600000.SH", "5m"),   # 浦发银行 5分钟
        ("000001.SZ", "1m"),   # 平安银行 1分钟
    ]

    for stock, period in test_cases:
        show_data_time_range(stock, period)

    print("\n" + "=" * 60)
    print("注意：如果是非交易时间，分钟线可能只有历史数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
