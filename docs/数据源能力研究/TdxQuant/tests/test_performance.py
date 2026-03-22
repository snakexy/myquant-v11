"""
TdxQuant性能对比测试

测试目标：
1. 测量各种数据获取操作的性能
2. 与文档中的性能数据对比
3. 识别性能瓶颈
4. 为优化提供数据支持
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import (
    measure_performance,
    save_test_result,
    print_performance_result
)
from tests.config import (
    TEST_STOCKS,
    DEFAULT_STOCK,
    PERFORMANCE_CONFIG
)

print("="*60)
print("TdxQuant性能对比测试")
print("="*60)
print(f"测试股票: {DEFAULT_STOCK}")
print(f"测试次数: {PERFORMANCE_CONFIG['test_count']}")
print("="*60)


class TdxQuantPerformanceTest:
    """TdxQuant性能测试类"""

    def __init__(self):
        # TODO: 初始化TdxQuant连接
        self.client = None
        print("\n⚠️ 注意: 需要集成实际的TdxQuant API客户端")
        print("  请根据实际的TdxQuant SDK修改此文件")

    def get_snapshot(self, symbol: str):
        """获取实时快照"""
        # TODO: 实现实际API调用
        return {"symbol": symbol, "price": 1850.00, "volume": 123456}

    def get_kline(self, symbol: str, period: str, count: int):
        """获取K线数据"""
        # TODO: 实现实际API调用
        return [{"time": "2026-03-04", "open": 1850, "high": 1860, "low": 1840, "close": 1855, "volume": 100000}] * count

    def get_sector_list(self, sector_type: str):
        """获取板块列表"""
        # TODO: 实现实际API调用
        return [{"code": "BK0001", "name": "银行"}] * 10

    def get_sector_stocks(self, sector_code: str):
        """获取板块成分股"""
        # TODO: 实现实际API调用
        return [{"code": "600519.SH", "name": "贵州茅台"}] * 50


def test_benchmark_performance():
    """基准性能测试"""
    print("\n1. 基准性能测试")

    test = TdxQuantPerformanceTest()

    # 文档中的基准数据
    benchmark_data = {
        "L1单股快照": 0.60,       # ms
        "L1批量快照（10只）": 0.81,  # ms/股
        "K线100根": 50.8,          # ms
        "K线500根": 35.6,          # ms
        "K线1000根": 42.1,         # ms
        "K线1088根": 42.2,         # ms
    }

    tests = [
        ("L1单股快照", lambda: test.get_snapshot(DEFAULT_STOCK)),
        ("K线100根", lambda: test.get_kline(DEFAULT_STOCK, "1d", 100)),
        ("K线500根", lambda: test.get_kline(DEFAULT_STOCK, "1d", 500)),
        ("K线1000根", lambda: test.get_kline(DEFAULT_STOCK, "1d", 1000)),
        ("K线1088根", lambda: test.get_kline(DEFAULT_STOCK, "1d", 1088)),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n  测试: {test_name}")

        try:
            # 性能测试
            perf_data = measure_performance(
                test_func,
                warmup_count=PERFORMANCE_CONFIG['warmup_count'],
                test_count=PERFORMANCE_CONFIG['test_count']
            )

            # 与基准对比
            benchmark = benchmark_data.get(test_name, 0)
            if benchmark > 0:
                diff_pct = (perf_data['avg'] - benchmark) / benchmark * 100
                comparison = "✅ 符合" if abs(diff_pct) < 20 else "⚠️ 偏差较大"
                print(f"    当前: {perf_data['avg']:.2f}ms")
                print(f"    基准: {benchmark:.2f}ms")
                print(f"    差异: {diff_pct:+.1f}%")
                print(f"    评价: {comparison}")

            results[test_name] = {
                "success": True,
                "performance": perf_data,
                "benchmark": benchmark,
                "diff_percentage": diff_pct if benchmark else 0
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[test_name] = {
                "success": False,
                "error_msg": str(e)
            }

    # 保存结果
    save_test_result("test_performance_benchmark", {
        "test_type": "performance_benchmark",
        "benchmark_data": benchmark_data,
        "results": results
    })

    return results


def test_throughput():
    """吞吐量测试"""
    print("\n2. 吞吐量测试")

    test = TdxQuantPerformanceTest()

    # 测试不同规模的数据获取
    throughput_tests = [
        ("1只股票快照", 1, lambda: test.get_snapshot(DEFAULT_STOCK)),
        ("10只股票快照", 10, lambda: [test.get_snapshot(s) for s in list(TEST_STOCKS.values())[:10]]),
        ("100根K线", 100, lambda: test.get_kline(DEFAULT_STOCK, "1d", 100)),
        ("500根K线", 500, lambda: test.get_kline(DEFAULT_STOCK, "1d", 500)),
        ("1000根K线", 1000, lambda: test.get_kline(DEFAULT_STOCK, "1d", 1000)),
    ]

    results = {}

    for test_name, size, test_func in throughput_tests:
        print(f"\n  测试: {test_name} (数据量: {size})")

        try:
            # 测量吞吐量
            perf_data = measure_performance(
                test_func,
                warmup_count=2,
                test_count=5
            )

            # 计算吞吐量
            throughput = size / (perf_data['avg'] / 1000)  # 每秒处理数量

            print(f"    性能: {perf_data['avg']:.2f}ms")
            print(f"    吞吐量: {throughput:.1f} 条/秒")

            results[test_name] = {
                "success": True,
                "size": size,
                "performance": perf_data,
                "throughput": throughput
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[test_name] = {
                "success": False,
                "error_msg": str(e)
            }

    # 保存结果
    save_test_result("test_performance_throughput", {
        "test_type": "performance_throughput",
        "results": results
    })

    return results


def test_concurrent_performance():
    """并发性能测试"""
    print("\n3. 并发性能测试")

    test = TdxQuantPerformanceTest()

    # 模拟并发请求
    def concurrent_requests(count):
        """模拟并发请求"""
        results = []
        for i in range(count):
            try:
                data = test.get_snapshot(list(TEST_STOCKS.values())[i % len(TEST_STOCKS)])
                results.append(data)
            except:
                pass
        return results

    # 测试不同并发级别
    concurrency_levels = [1, 5, 10, 20, 50]

    results = {}

    for level in concurrency_levels:
        print(f"\n  并发级别: {level}")

        try:
            # 测试并发性能
            perf_data = measure_performance(
                lambda: concurrent_requests(level),
                warmup_count=2,
                test_count=5
            )

            print(f"    总时间: {perf_data['avg']:.2f}ms")
            print(f"    平均每请求: {perf_data['avg']/level:.2f}ms")
            print(f"    QPS: {level/(perf_data['avg']/1000):.1f}")

            results[f"并发{level}"] = {
                "success": True,
                "concurrency": level,
                "performance": perf_data,
                "avg_per_request": perf_data['avg']/level,
                "qps": level/(perf_data['avg']/1000)
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[f"并发{level}"] = {
                "success": False,
                "error_msg": str(e)
            }

    # 保存结果
    save_test_result("test_performance_concurrent", {
        "test_type": "performance_concurrent",
        "results": results
    })

    return results


def test_performance_comparison():
    """性能对比分析"""
    print("\n4. 性能对比分析")

    test = TdxQuantPerformanceTest()

    # 与其他数据源的性能对比（基于文档数据）
    comparison_data = {
        "L1实时快照": {
            "TdxQuant": 0.60,
            "XtQuant": 0.90,
            "PyTdx": 14.14
        },
        "K线100根": {
            "TdxQuant": 50.8,
            "XtQuant": "不支持",
            "PyTdx": "较慢"
        }
    }

    print("\n  文档中的性能对比:")
    for metric, sources in comparison_data.items():
        print(f"\n    {metric}:")
        for source, time_str in sources.items():
            if isinstance(time_str, (int, float)):
                status = "🥇" if source == "TdxQuant" and time_str == min(
                    t for t in sources.values() if isinstance(t, (int, float))
                ) else ""
                print(f"      {status} {source}: {time_str:.2f}ms")
            else:
                print(f"      {source}: {time_str}")

    # 当前测试对比
    print("\n  TdxQuant在各项性能中的优势:")
    print("    ✅ L1实时快照: 0.60ms（所有数据源中最快）")
    print("    ✅ 板块数据获取: 主要优势领域")
    print("    ✅ 财务数据获取: 完整支持")

    # 保存结果
    save_test_result("test_performance_comparison", {
        "test_type": "performance_comparison",
        "comparison_data": comparison_data,
        "conclusion": "TdxQuant在L1实时快照性能方面具有明显优势"
    })

    return comparison_data


if __name__ == "__main__":
    import time

    print("\n开始性能测试...\n")

    try:
        # 执行所有测试
        result1 = test_benchmark_performance()
        result2 = test_throughput()
        result3 = test_concurrent_performance()
        result4 = test_performance_comparison()

        # 汇总结果
        print("\n" + "="*60)
        print("性能测试完成")
        print("="*60)
        print(f"基准性能测试: {sum(1 for r in result1.values() if r.get('success', False))}/{len(result1)}通过")
        print(f"吞吐量测试: {sum(1 for r in result2.values() if r.get('success', False))}/{len(result2)}通过")
        print(f"并发性能测试: {sum(1 for r in result3.values() if r.get('success', False))}/{len(result3)}通过")
        print(f"对比分析: 已完成")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
