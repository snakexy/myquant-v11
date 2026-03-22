# -*- coding: utf-8 -*-
"""
测试两级市场监控系统

目的:
1. 验证服务模块可正常导入
2. 验证各个组件可正常初始化
3. 验证基本功能（短时间运行）
"""

import sys
import os
from pathlib import Path

# 获取项目根目录
current_file = Path(__file__).resolve()
project_root = current_file.parents[3]  # 回退3级到项目根目录

# 添加项目根目录到Python路径（这样import backend才能工作）
sys.path.insert(0, str(project_root))
print(f"[路径] 项目根目录: {project_root}")
print(f"[路径] Python路径已添加")
print(f"[路径] 当前工作目录: {os.getcwd()}")

from xtquant import xtdata
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


def test_import():
    """测试1: 模块导入"""
    print("\n" + "=" * 80)
    print("[测试1] 模块导入")
    print("=" * 80)

    try:
        from backend.services.market_monitor_service import (
            FullMarketScanner,
            FocusedMonitor,
            TwoLevelMarketMonitor,
            get_market_monitor
        )
        print("[OK] 模块导入成功")
        return True
    except Exception as e:
        print(f"[ERROR] 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scanner_init():
    """测试2: 全A扫描器初始化"""
    print("\n" + "=" * 80)
    print("[测试2] 全A扫描器初始化")
    print("=" * 80)

    try:
        from backend.services.market_monitor_service import FullMarketScanner

        scanner = FullMarketScanner()

        print(f"[OK] 股票总数: {len(scanner.all_stocks)}")
        print(f"[OK] 异常池初始: {len(scanner.anomaly_watchlist)}")

        if len(scanner.all_stocks) > 0:
            print("[OK] 全A扫描器初始化成功")
            return True
        else:
            print("[ERROR] 未获取到股票列表")
            return False

    except Exception as e:
        print(f"[ERROR] 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitor_init():
    """测试3: 重点监控器初始化"""
    print("\n" + "=" * 80)
    print("[测试3] 重点监控器初始化")
    print("=" * 80)

    try:
        from backend.services.market_monitor_service import FocusedMonitor

        monitor = FocusedMonitor(max_subscriptions=500)

        print(f"[OK] 监控股票数: {len(monitor.focused_watchlist)}/500")
        print(f"[OK] 最大订阅数: {monitor.max_subscriptions}")

        print("[OK] 重点监控器初始化成功")
        return True

    except Exception as e:
        print(f"[ERROR] 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scanner_single_batch():
    """测试4: 全A扫描器单批次扫描"""
    print("\n" + "=" * 80)
    print("[测试4] 全A扫描器单批次扫描")
    print("=" * 80)

    try:
        from backend.services.market_monitor_service import FullMarketScanner

        scanner = FullMarketScanner()

        # 测试单个批次（10只股票）
        test_symbols = scanner.all_stocks[:10]

        print(f"[测试] 扫描 {len(test_symbols)} 只股票...")

        start = time.time()
        quotes = xtdata.get_full_tick(test_symbols)
        elapsed = (time.time() - start) * 1000

        print(f"[OK] 耗时: {elapsed:.2f}ms")
        print(f"[OK] 获取数据: {len(quotes)} 只")

        # 检测异常
        anomalies = scanner._detect_anomalies(quotes)

        print(f"[OK] 检测到异常: {len(anomalies)} 只")

        if len(anomalies) > 0:
            print("[异常列表]")
            for anomaly in anomalies[:5]:  # 只显示前5个
                print(f"  - {anomaly['symbol']}: {anomaly['type']} ({anomaly['details']})")

        print("[OK] 单批次扫描测试成功")
        return True

    except Exception as e:
        print(f"[ERROR] 扫描失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitor_add_remove():
    """测试5: 重点监控器添加/移除"""
    print("\n" + "=" * 80)
    print("[测试5] 重点监控器添加/移除")
    print("=" * 80)

    try:
        from backend.services.market_monitor_service import FocusedMonitor

        monitor = FocusedMonitor(max_subscriptions=500)

        initial_count = len(monitor.focused_watchlist)
        print(f"[初始] 监控股票: {initial_count} 只")

        # 添加测试股票
        test_symbol = '601888.SH'  # 中国中免

        print(f"[测试] 添加 {test_symbol}...")
        success = monitor.add_to_focused(test_symbol)

        after_add = len(monitor.focused_watchlist)
        print(f"[结果] 添加后: {after_add} 只 (成功: {success})")

        # 移除测试股票
        print(f"[测试] 移除 {test_symbol}...")
        monitor.remove_from_focused(test_symbol)

        after_remove = len(monitor.focused_watchlist)
        print(f"[结果] 移除后: {after_remove} 只")

        print("[OK] 添加/移除测试成功")
        return True

    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_init():
    """测试6: 两级监控系统初始化"""
    print("\n" + "=" * 80)
    print("[测试6] 两级监控系统初始化")
    print("=" * 80)

    try:
        from backend.services.market_monitor_service import TwoLevelMarketMonitor

        system = TwoLevelMarketMonitor(
            scanner_interval=60,
            monitor_interval=3
        )

        print(f"[OK] Level 1 股票数: {len(system.scanner.all_stocks)}")
        print(f"[OK] Level 2 监控数: {len(system.monitor.focused_watchlist)}")

        status = system.get_status()

        print(f"[OK] 系统状态获取成功")
        print(f"  - scanner.stocks: {status['scanner']['all_stocks_count']}")
        print(f"  - monitor.watchlist: {status['monitor']['watchlist_count']}")

        print("[OK] 系统初始化测试成功")
        return True

    except Exception as e:
        print(f"[ERROR] 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_short_run():
    """测试7: 系统短时间运行"""
    print("\n" + "=" * 80)
    print("[测试7] 系统短时间运行")
    print("=" * 80)

    try:
        from backend.services.market_monitor_service import TwoLevelMarketMonitor

        # 创建系统（使用较短的间隔）
        system = TwoLevelMarketMonitor(
            scanner_interval=10,  # 10秒扫描一次
            monitor_interval=2    # 2秒刷新一次
        )

        print("[启动] 启动两级监控系统...")
        system.start()

        print("[运行] 运行15秒...")

        # 运行15秒
        for i in range(15):
            time.sleep(1)
            if (i + 1) % 5 == 0:
                status = system.get_status()
                print(
                    f"[{i+1}s] "
                    f"L1扫描: {status['scanner']['scan_count']}次, "
                    f"L2监控: {status['monitor']['monitor_count']}次, "
                    f"异常池: {status['scanner']['anomaly_watchlist_count']}只"
                )

        print("[停止] 停止系统...")
        system.stop()

        # 最终状态
        final_status = system.get_status()
        print("\n[最终状态]")
        print(f"  - L1扫描次数: {final_status['scanner']['scan_count']}")
        print(f"  - L2监控次数: {final_status['monitor']['monitor_count']}")
        print(f"  - 异常池股票: {final_status['scanner']['anomaly_watchlist_count']}")
        print(f"  - 重点监控数: {final_status['monitor']['watchlist_count']}")

        print("[OK] 短时间运行测试成功")
        return True

    except Exception as e:
        print(f"[ERROR] 运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("两级市场监控系统 - 完整测试")
    print("=" * 80)

    tests = [
        ("模块导入", test_import),
        ("全A扫描器初始化", test_scanner_init),
        ("重点监控器初始化", test_monitor_init),
        ("单批次扫描", test_scanner_single_batch),
        ("添加/移除股票", test_monitor_add_remove),
        ("系统初始化", test_system_init),
        ("短时间运行", test_short_run),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] 测试 '{name}' 抛出异常: {e}")
            results.append((name, False))

    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)

    passed = 0
    failed = 0

    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "-" * 80)
    print(f"总计: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n[成功] 所有测试通过!")
    else:
        print(f"\n[警告] {failed} 个测试失败")

    print("=" * 80)

    return failed == 0


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] 测试程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
