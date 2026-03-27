# -*- coding: utf-8 -*-
"""
查看 TdxQuant refresh_kline 后的实际数据时间

**重要**：此脚本需要在交易时间（周一至周五 9:30-15:00）
且通达信终端运行时才能获取到数据。

运行后会显示：
1. refresh_kline 缓存结果
2. get_market_data 返回数据的实际时间范围
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

DLL_PATH = r'E:\new_tdx64\PYPlugins\TPythClient.dll'
INIT_PATH = r'E:\new_tdx64\PYPlugins\user\myquant_init.py'


def check_data_time():
    print("=" * 70)
    print("TdxQuant refresh_kline 数据时间范围检查")
    print("=" * 70)
    print("当前时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print()

    # 检查是否是交易时间
    now = datetime.now()
    weekday = now.weekday()
    current_time = now.time()

    if weekday >= 5:
        print("[WARNING] 今天是周末，可能无法获取数据")
    else:
        morning_start = datetime.strptime("09:30", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()

        if not (morning_start <= current_time <= afternoon_end):
            print("[WARNING] 当前非交易时间，可能无法获取数据")

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
            print("请确保通达信终端正在运行\n")
            return

    # 测试股票
    test_stock = "600000.SH"  # 浦发银行

    for period in ["1d", "5m", "1m"]:
        print("=" * 70)
        print("股票: {}, 周期: {}".format(test_stock, period))
        print("=" * 70)

        # 1. 调用 refresh_kline
        print("\n[1] 调用 refresh_kline...")
        try:
            result = tq.refresh_kline(stock_list=[test_stock], period=period)
            if result:
                result_json = json.loads(result)
                if result_json.get("ErrorId") == "0":
                    print("     [OK] 缓存成功")
                else:
                    print("     [FAIL] {}".format(result_json.get('Error')))
                    continue
            else:
                print("     [FAIL] 返回空")
                continue
        except Exception as e:
            print("     [ERROR] {}".format(e))
            continue

        # 2. 立即查询数据
        print("\n[2] 查询缓存后的数据...")
        try:
            data_result = tq.get_market_data(
                stock_list=[test_stock],
                period=period,
                count=500
            )

            if data_result and test_stock in data_result:
                data = data_result[test_stock]

                if len(data) == 0:
                    print("     [WARN] 返回数据为空（可能是非交易时间）")
                    continue

                print("     数据条数: {}".format(len(data)))
                print()

                # 3. 显示时间范围
                print("[3] 数据时间范围:")
                first = data[0]
                last = data[-1]

                print("     最早: {}".format(first.get('time', 'N/A')))
                print("            开盘:{}, 最高:{}, 最低:{}, 收盘:{}, 成交量:{}".format(
                    first.get('open', 'N/A'), first.get('high', 'N/A'),
                    first.get('low', 'N/A'), first.get('close', 'N/A'),
                    first.get('volume', 'N/A')
                ))
                print()
                print("     最新: {}".format(last.get('time', 'N/A')))
                print("            开盘:{}, 最高:{}, 最低:{}, 收盘:{}, 成交量:{}".format(
                    last.get('open', 'N/A'), last.get('high', 'N/A'),
                    last.get('low', 'N/A'), last.get('close', 'N/A'),
                    last.get('volume', 'N/A')
                ))

                # 显示最后几条
                print()
                print("[4] 最后 5 条数据:")
                for i, bar in enumerate(data[-5:], 1):
                    print("     {}. {} | O:{} H:{} L:{} C:{} V:{}".format(
                        i, bar.get('time', 'N/A'),
                        bar.get('open', 'N/A'), bar.get('high', 'N/A'),
                        bar.get('low', 'N/A'), bar.get('close', 'N/A'),
                        bar.get('volume', 'N/A')
                    ))

            else:
                print("     [WARN] 无数据返回（需要通达信运行且在交易时间）")

        except Exception as e:
            import traceback
            print("     [ERROR] {}".format(e))
            print(traceback.format_exc())

        print()

    print("=" * 70)
    print("检查完成")
    print("=" * 70)


if __name__ == "__main__":
    check_data_time()
