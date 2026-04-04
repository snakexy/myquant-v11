# -*- coding: utf-8 -*-
"""
TdxQuant refresh_kline 缓存功能说明和测试建议

根据测试结果：
1. refresh_kline 在非交易时间也能成功调用（缓存历史数据）
2. 返回结果：{"ErrorId": "0", "Msg": "refresh kline cache success."}

建议在交易时间（周一至周五 9:30-15:00）运行完整测试，
验证缓存对查询速度的提升效果。
"""
import sys
import json
import time
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


def is_trading_time():
    """判断是否是交易时间"""
    now = datetime.now()
    if now.weekday() >= 5:  # 周末
        return False

    current_time = now.time()
    morning_start = datetime.strptime("09:30", "%H:%M").time()
    morning_end = datetime.strptime("11:30", "%H:%M").time()
    afternoon_start = datetime.strptime("13:00", "%H:%M").time()
    afternoon_end = datetime.strptime("15:00", "%H:%M").time()

    return (morning_start <= current_time <= morning_end or
            afternoon_start <= current_time <= afternoon_end)


def cache_stocks(stock_list, periods):
    """批量缓存股票数据"""
    print("=" * 60)
    print("TdxQuant 批量缓存 K线数据")
    print("=" * 60)
    print("时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("股票: {}".format(', '.join(stock_list)))
    print("周期: {}".format(', '.join(periods)))
    print()

    # 初始化
    if not (hasattr(tq, '_initialized') and tq._initialized):
        tq.dll_path = DLL_PATH
        try:
            print("初始化 TdxQuant...")
            tq.initialize(path=INIT_PATH)
            print("[OK] 初始化成功 (run_id={})\n".format(tq.run_id))
        except Exception as e:
            print("[ERROR] 初始化失败: {}".format(e))
            return

    success_count = 0
    fail_count = 0
    total_count = len(stock_list) * len(periods)

    for period in periods:
        print("\n周期: {}".format(period))
        print("-" * 40)

        for stock in stock_list:
            try:
                start = time.perf_counter()
                result = tq.refresh_kline(stock_list=[stock], period=period)
                refresh_time = time.perf_counter() - start

                if result:
                    result_json = json.loads(result)
                    if result_json.get("ErrorId") == "0":
                        print("  {} [OK] {:.1f} ms".format(stock, refresh_time * 1000))
                        success_count += 1
                    else:
                        print("  {} [FAIL] {}".format(stock, result_json.get('Error')))
                        fail_count += 1
                else:
                    print("  {} [FAIL] 空结果".format(stock))
                    fail_count += 1
            except Exception as e:
                print("  {} [ERROR] {}".format(stock, e))
                fail_count += 1

    print("\n" + "=" * 60)
    print("缓存完成: 成功 {}/{}, 失败 {}/{}".format(
        success_count, total_count, fail_count, total_count))
    print("=" * 60)


if __name__ == "__main__":
    # 检查是否是交易时间
    if is_trading_time():
        print("[INFO] 当前是交易时间，可以测试查询速度")
        print("建议：先缓存数据，再测试查询速度\n")
    else:
        print("[INFO] 当前非交易时间")
        print("refresh_kline 可以缓存历史数据，")
        print("但查询速度测试需要在交易时间进行\n")

    # 缓存示例股票
    stocks = [
        "600000.SH",   # 浦发银行
        "000001.SZ",   # 平安银行
        "600519.SH",   # 贵州茅台
        "000002.SZ",   # 万科A
        "601318.SH",   # 中国平安
    ]

    periods = ["1d", "5m", "1m"]

    cache_stocks(stocks, periods)

    print("\n提示：缓存完成后，下次查询这些股票的数据时会更快")
    print("缓存文件存储在通达信安装目录的 cache 文件夹中")
