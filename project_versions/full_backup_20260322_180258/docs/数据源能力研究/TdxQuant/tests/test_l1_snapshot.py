"""
TdxQuant L1实时快照测试

测试目标：
1. 验证TdxQuant的L1实时快照功能
2. 测量单股快照性能
3. 测量批量快照性能
4. 验证数据格式正确性
5. 与文档中的性能数据对比（文档显示0.60ms最快）
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import (
    measure_performance,
    save_test_result,
    print_performance_result,
    validate_snapshot_data,
    format_result
)
from tests.config import (
    TEST_STOCKS,
    DEFAULT_STOCK,
    PERFORMANCE_CONFIG
)

print("="*60)
print("TdxQuant L1实时快照测试")
print("="*60)
print(f"测试股票: {DEFAULT_STOCK}")
print(f"测试次数: {PERFORMANCE_CONFIG['test_count']}")
print(f"预热次数: {PERFORMANCE_CONFIG['warmup_count']}")
print("="*60)


class TdxQuantL1Test:
    """TdxQuant L1快照测试类"""

    def __init__(self):
        # TODO: 初始化TdxQuant连接
        # 这里需要根据实际的TdxQuant API进行初始化
        self.client = None
        print("\n⚠️ 注意: 需要集成实际的TdxQuant API客户端")
        print("  请根据实际的TdxQuant SDK修改此文件")

    def get_single_snapshot(self, symbol: str):
        """
        获取单只股票的实时快照

        Args:
            symbol: 股票代码

        Returns:
            dict: 快照数据
        """
        # TODO: 实现实际的API调用
        # 示例代码（需要根据实际API调整）：
        # return self.client.get_snapshot(symbol)

        # 模拟数据（仅用于演示）
        return {
            "symbol": symbol,
            "price": 1850.00,
            "volume": 123456,
            "amount": 2.28e8,
            "bid1": 1849.50,
            "ask1": 1850.50,
            "timestamp": "2026-03-04 15:00:00"
        }

    def get_batch_snapshots(self, symbols: list):
        """
        批量获取股票的实时快照

        Args:
            symbols: 股票代码列表

        Returns:
            list: 快照数据列表
        """
        # TODO: 实现批量API调用
        # 示例代码（需要根据实际API调整）：
        # return self.client.get_batch_snapshots(symbols)

        # 模拟数据（仅用于演示）
        return [self.get_single_snapshot(symbol) for symbol in symbols]


def test_single_snapshot():
    """测试单股快照获取"""
    print("\n1. 测试单股快照获取")

    test = TdxQuantL1Test()

    def get_snapshot():
        return test.get_single_snapshot(DEFAULT_STOCK)

    # 性能测试
    perf_data = measure_performance(
        get_snapshot,
        warmup_count=PERFORMANCE_CONFIG['warmup_count'],
        test_count=PERFORMANCE_CONFIG['test_count']
    )

    print_performance_result("L1单股快照", perf_data)

    # 数据验证
    sample_data = get_snapshot()
    is_valid, msg = validate_snapshot_data(sample_data)
    print(f"数据验证: {'✅ 通过' if is_valid else f'❌ 失败: {msg}'}")
    if not is_valid:
        print(f"示例数据: {format_result(sample_data)}")

    # 与文档数据对比
    document_time = 0.60  # 文档中记录的时间（ms）
    print(f"\n与文档对比:")
    print(f"  文档记录: {document_time:.2f}ms")
    print(f"  当前测试: {perf_data['avg']:.2f}ms")
    print(f"  差异: {abs(perf_data['avg'] - document_time):.2f}ms ({(abs(perf_data['avg'] - document_time)/document_time)*100:.1f}%)")

    # 保存结果
    result = {
        "test_type": "L1_single_snapshot",
        "success": is_valid,
        "performance": perf_data,
        "document_time": document_time,
        "diff_percentage": (abs(perf_data['avg'] - document_time)/document_time)*100,
        "sample_data": sample_data
    }
    save_test_result("test_l1_single_snapshot", result)

    return result


def test_batch_snapshots():
    """测试批量快照获取"""
    print("\n2. 测试批量快照获取")

    test = TdxQuantL1Test()
    batch_size = PERFORMANCE_CONFIG['batch_size']

    # 准备测试股票列表
    test_symbols = list(TEST_STOCKS.values())[:batch_size]
    print(f"  批量大小: {len(test_symbols)}只股票")
    print(f"  股票列表: {test_symbols}")

    def get_batch():
        return test.get_batch_snapshots(test_symbols)

    # 性能测试
    perf_data = measure_performance(
        get_batch,
        warmup_count=PERFORMANCE_CONFIG['warmup_count'],
        test_count=PERFORMANCE_CONFIG['test_count']
    )

    # 计算单股平均时间
    avg_per_stock = perf_data['avg'] / batch_size if batch_size > 0 else 0
    perf_data['avg_per_stock'] = avg_per_stock

    print_performance_result(f"L1批量快照（{batch_size}只）", perf_data)
    print(f"  单股平均: {avg_per_stock:.2f}ms/股")

    # 数据验证
    batch_data = get_batch()
    all_valid = True
    for i, data in enumerate(batch_data):
        is_valid, msg = validate_snapshot_data(data)
        if not is_valid:
            all_valid = False
            print(f"  第{i+1}只股票验证失败: {msg}")

    print(f"数据验证: {'✅ 全部通过' if all_valid else '❌ 部分失败'}")

    # 与文档数据对比
    document_avg = 0.81  # 文档中记录的批量平均时间（ms/股）
    print(f"\n与文档对比:")
    print(f"  文档记录: {document_avg:.2f}ms/股")
    print(f"  当前测试: {avg_per_stock:.2f}ms/股")
    print(f"  差异: {abs(avg_per_stock - document_avg):.2f}ms/股 ({(abs(avg_per_stock - document_avg)/document_avg)*100:.1f}%)")

    # 保存结果
    result = {
        "test_type": "L1_batch_snapshot",
        "batch_size": batch_size,
        "success": all_valid,
        "performance": perf_data,
        "document_avg": document_avg,
        "diff_percentage": (abs(avg_per_stock - document_avg)/document_avg)*100,
        "symbols": test_symbols
    }
    save_test_result("test_l1_batch_snapshot", result)

    return result


def test_realtime_performance():
    """测试实时性能稳定性"""
    print("\n3. 测试实时性能稳定性")

    test = TdxQuantL1Test()
    test_count = 20  # 连续测试次数

    print(f"  连续测试次数: {test_count}")

    times = []
    for i in range(test_count):
        try:
            start = time.time()
            data = test.get_single_snapshot(DEFAULT_STOCK)
            end = time.time()
            times.append((end - start) * 1000)

            if (i + 1) % 5 == 0:
                print(f"  前{i+1}次平均: {sum(times)/len(times):.2f}ms")
        except Exception as e:
            print(f"  第{i+1}次失败: {e}")

    if times:
        avg = sum(times) / len(times)
        std_dev = (sum((x - avg) ** 2 for x in times) / len(times)) ** 0.5

        print(f"\n实时性能统计:")
        print(f"  平均时间: {avg:.2f}ms")
        print(f"  最小时间: {min(times):.2f}ms")
        print(f"  最大时间: {max(times):.2f}ms")
        print(f"  标准差: {std_dev:.2f}ms")
        print(f"  波动率: {(std_dev/avg)*100:.1f}%")

        result = {
            "test_type": "L1_realtime_stability",
            "success": True,
            "test_count": test_count,
            "avg_time": avg,
            "min_time": min(times),
            "max_time": max(times),
            "std_dev": std_dev,
            "volatility": (std_dev/avg)*100
        }
    else:
        result = {
            "test_type": "L1_realtime_stability",
            "success": False,
            "test_count": test_count,
            "avg_time": 0
        }

    save_test_result("test_l1_realtime_stability", result)
    return result


if __name__ == "__main__":
    import time

    print("\n开始L1实时快照测试...\n")

    try:
        # 执行所有测试
        result1 = test_single_snapshot()
        result2 = test_batch_snapshots()
        result3 = test_realtime_performance()

        # 汇总结果
        all_success = result1['success'] and result2['success'] and result3['success']

        print("\n" + "="*60)
        print("L1测试完成")
        print("="*60)
        print(f"单股快照: {'✅ 通过' if result1['success'] else '❌ 失败'}")
        print(f"批量快照: {'✅ 通过' if result2['success'] else '❌ 失败'}")
        print(f"实时稳定性: {'✅ 通过' if result3['success'] else '❌ 失败'}")
        print("="*60)

        if all_success:
            print("\n✅ 所有L1测试通过！")
        else:
            print("\n⚠️ 部分测试失败，请检查日志")

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
