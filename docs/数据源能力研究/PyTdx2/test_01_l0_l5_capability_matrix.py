# -*- coding: utf-8 -*-
"""
PyTdx2 L0-L5 能力矩阵测试

测试 PyTdx2 在各个数据层级的能力和限制
"""

import time
from pytdx2.hq import TdxHq_API
from pytdx2.params import TDXParams
import pandas as pd
from datetime import datetime


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_l0_subscription():
    """测试 L0 订阅推送能力"""
    print_section("L0: 订阅推送能力测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            print("❌ PyTdx2 不支持订阅推送功能")
            print("说明: PyTdx2 是轮询模式，不支持事件驱动的订阅推送")
            return False
    except Exception as e:
        print(f"❌ 订阅功能不支持: {e}")
        return False
    finally:
        api.disconnect()


def test_l1_realtime_snapshot():
    """测试 L1 实时快照能力"""
    print_section("L1: 实时快照能力测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            # 测试单只股票
            start = time.time()
            quotes = api.get_security_quotes([(0, "000001")])
            elapsed = (time.time() - start) * 1000

            print(f"✅ 单股快照: {elapsed:.2f}ms")
            print(f"   返回字段: {list(quotes[0].keys()) if quotes else 'None'}")

            # 测试批量获取
            start = time.time()
            symbols = [(0, "000001"), (1, "600000"), (0, "000002"),
                      (1, "600036"), (0, "000333")]
            quotes = api.get_security_quotes(symbols)
            elapsed = (time.time() - start) * 1000

            print(f"✅ 批量快照(5只): {elapsed:.2f}ms, {elapsed/len(symbols):.2f}ms/股")

            return True
    except Exception as e:
        print(f"❌ 实时快照失败: {e}")
        return False
    finally:
        api.disconnect()


def test_l2_history_summary():
    """测试 L2 历史摘要能力"""
    print_section("L2: 历史摘要能力测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            # 获取最近30天K线数据
            start = time.time()
            data = api.get_security_bars(
                category=TDXParams.KLINE_TYPE_RI_K,  # 日线
                market=1,
                code="600000",
                start=0,
                count=30
            )
            elapsed = (time.time() - start) * 1000

            print(f"✅ 30天K线摘要: {elapsed:.2f}ms")
            print(f"   数据条数: {len(data)}")

            return True
    except Exception as e:
        print(f"❌ 历史摘要失败: {e}")
        return False
    finally:
        api.disconnect()


def test_l3_kline_data():
    """测试 L3 完整K线能力"""
    print_section("L3: 完整K线能力测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            # 测试不同周期的K线
            periods = [
                (TDXParams.KLINE_TYPE_1MIN, "1分钟"),
                (TDXParams.KLINE_TYPE_5MIN, "5分钟"),
                (TDXParams.KLINE_TYPE_15MIN, "15分钟"),
                (TDXParams.KLINE_TYPE_30MIN, "30分钟"),
                (TDXParams.KLINE_TYPE_1HOUR, "1小时"),
                (TDXParams.KLINE_TYPE_RI_K, "日线"),
                (TDXParams.KLINE_TYPE_WEEKLY, "周线"),
                (TDXParams.KLINE_TYPE_MONTHLY, "月线"),
            ]

            results = []
            for category, name in periods:
                start = time.time()
                data = api.get_security_bars(
                    category=category,
                    market=1,
                    code="600000",
                    start=0,
                    count=100
                )
                elapsed = (time.time() - start) * 1000
                results.append((name, len(data), elapsed))
                print(f"✅ {name}: {len(data)}条, {elapsed:.2f}ms")

            # 测试数据量限制
            print("\n数据量限制测试:")
            for count in [100, 500, 800, 900]:
                start = time.time()
                data = api.get_security_bars(
                    category=TDXParams.KLINE_TYPE_RI_K,
                    market=1,
                    code="600000",
                    start=0,
                    count=count
                )
                elapsed = (time.time() - start) * 1000
                print(f"   请求{count}条 → 实际{len(data)}条, {elapsed:.2f}ms")

            return True
    except Exception as e:
        print(f"❌ K线数据失败: {e}")
        return False
    finally:
        api.disconnect()


def test_l3_tick_data():
    """测试 L3 分笔成交能力"""
    print_section("L3: 分笔成交能力测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            # 测试当日分笔
            start = time.time()
            data = api.get_transaction_data(
                market=1,
                code="600000",
                start=0,
                count=100
            )
            elapsed = (time.time() - start) * 1000

            print(f"✅ 当日分笔: {len(data)}条, {elapsed:.2f}ms")
            if data:
                print(f"   字段: {list(data[0].keys())}")

            # 测试历史分笔
            start = time.time()
            data = api.get_history_transaction_data(
                market=1,
                code="600000",
                start=0,
                count=100,
                date=20240301
            )
            elapsed = (time.time() - start) * 1000

            print(f"✅ 历史分笔: {len(data)}条, {elapsed:.2f}ms")

            return True
    except Exception as e:
        print(f"❌ 分笔数据失败: {e}")
        return False
    finally:
        api.disconnect()


def test_l4_financial_data():
    """测试 L4 财务数据能力"""
    print_section("L4: 财务数据能力测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            start = time.time()
            data = api.get_finance_info(
                market=1,
                code="600000"
            )
            elapsed = (time.time() - start) * 1000

            print(f"✅ 财务数据: {elapsed:.2f}ms")
            if data:
                print(f"   字段数量: {len(data)}")
                print(f"   前5个字段: {list(data.keys())[:5]}")

            return True
    except Exception as e:
        print(f"❌ 财务数据失败: {e}")
        return False
    finally:
        api.disconnect()


def test_l5_sector_data():
    """测试 L5 板块数据能力"""
    print_section("L5: 板块数据能力测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            # 测试板块信息
            block_files = [
                (TDXParams.BLOCK_SZ, "自选板块"),
                (TDXParams.BLOCK_FG, "分类板块"),
                (TDXParams.BLOCK_GN, "概念板块"),
            ]

            for block_file, name in block_files:
                try:
                    start = time.time()
                    data = api.get_and_parse_block_info(block_file)
                    elapsed = (time.time() - start) * 1000
                    print(f"✅ {name}: {len(data)}个板块, {elapsed:.2f}ms")
                except Exception as e:
                    print(f"⚠️ {name}: {e}")

            return True
    except Exception as e:
        print(f"❌ 板块数据失败: {e}")
        return False
    finally:
        api.disconnect()


def test_additional_features():
    """测试其他功能"""
    print_section("其他功能测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            # 股票列表
            start = time.time()
            count = api.get_security_count(1)
            elapsed = (time.time() - start) * 1000
            print(f"✅ 股票总数(上海): {count}, {elapsed:.2f}ms")

            # 获取部分股票列表
            start = time.time()
            stocks = api.get_security_list(1, 0)
            elapsed = (time.time() - start) * 1000
            print(f"✅ 股票列表: {len(stocks)}条, {elapsed:.2f}ms")
            if stocks:
                print(f"   字段: {list(stocks[0].keys())}")

            # 分时数据
            start = time.time()
            data = api.get_minute_time_data(1, "600000")
            elapsed = (time.time() - start) * 1000
            print(f"✅ 当日分时: {len(data)}条, {elapsed:.2f}ms")

            return True
    except Exception as e:
        print(f"❌ 其他功能失败: {e}")
        return False
    finally:
        api.disconnect()


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  PyTdx2 L0-L5 能力矩阵测试")
    print("=" * 60)

    results = {}

    # L0 订阅推送
    results['L0'] = test_l0_subscription()

    # L1 实时快照
    results['L1'] = test_l1_realtime_snapshot()

    # L2 历史摘要
    results['L2'] = test_l2_history_summary()

    # L3 K线数据
    results['L3_KLINE'] = test_l3_kline_data()

    # L3 分笔数据
    results['L3_TICK'] = test_l3_tick_data()

    # L4 财务数据
    results['L4'] = test_l4_financial_data()

    # L5 板块数据
    results['L5'] = test_l5_sector_data()

    # 其他功能
    results['OTHER'] = test_additional_features()

    # 打印总结
    print_section("测试总结")
    for level, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{level}: {status}")


if __name__ == '__main__':
    main()
