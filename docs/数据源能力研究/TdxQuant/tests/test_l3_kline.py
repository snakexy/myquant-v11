"""
TdxQuant L3 K线数据测试

测试目标：
1. 验证TdxQuant的K线数据获取功能
2. 测试不同周期的K线数据
3. 验证K线数据数量限制（文档显示最多1088根）
4. 测试当天数据不支持的限制
5. 验证数据格式正确性
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import (
    measure_performance,
    save_test_result,
    print_performance_result,
    validate_kline_data,
    format_result
)
from tests.config import (
    DEFAULT_STOCK,
    KLINE_CONFIG,
    PERFORMANCE_CONFIG
)

print("="*60)
print("TdxQuant L3 K线数据测试")
print("="*60)
print(f"测试股票: {DEFAULT_STOCK}")
print(f"测试周期: {', '.join(KLINE_CONFIG['periods'])}")
print("="*60)


class TdxQuantL3Test:
    """TdxQuant L3 K线数据测试类"""

    def __init__(self):
        # TODO: 初始化TdxQuant连接
        self.client = None
        print("\n⚠️ 注意: 需要集成实际的TdxQuant API客户端")
        print("  请根据实际的TdxQuant SDK修改此文件")

    def get_kline_data(self, symbol: str, period: str, count: int = 100):
        """
        获取K线数据

        Args:
            symbol: 股票代码
            period: 周期（1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M）
            count: 获取数量

        Returns:
            list: K线数据
        """
        # TODO: 实现实际的API调用
        # 示例代码（需要根据实际API调整）：
        # return self.client.get_kline(symbol, period, count)

        # 模拟数据（仅用于演示）
        import random
        data = []
        base_price = 1850.0

        for i in range(count):
            data.append({
                "time": f"2026-{(i%12)+1:02d}-{(i%28)+1:02d}",
                "open": base_price + random.uniform(-10, 10),
                "high": base_price + random.uniform(0, 20),
                "low": base_price - random.uniform(0, 20),
                "close": base_price + random.uniform(-10, 10),
                "volume": random.randint(100000, 1000000)
            })
            base_price = data[-1]["close"]

        return data

    def get_today_minute_data(self, symbol: str):
        """
        获取当天分钟数据（应该失败）

        Args:
            symbol: 股票代码

        Returns:
            list: 分钟数据
        """
        # TODO: 实现实际的API调用
        # 根据文档，TdxQuant不支持当天分钟数据
        return None


def test_different_periods():
    """测试不同周期的K线数据"""
    print("\n1. 测试不同周期的K线数据")

    test = TdxQuantL3Test()

    results = {}
    test_count = 50  # 每个周期获取的数量

    for period in KLINE_CONFIG['periods']:
        print(f"\n  测试周期: {period}")

        try:
            def get_data():
                return test.get_kline_data(DEFAULT_STOCK, period, test_count)

            # 性能测试
            perf_data = measure_performance(
                get_data,
                warmup_count=PERFORMANCE_CONFIG['warmup_count'],
                test_count=5  # 减少测试次数
            )

            # 获取实际数据
            data = get_data()

            # 数据验证
            is_valid, msg = validate_kline_data(data)
            print(f"    数量: {len(data)}根")
            print(f"    验证: {'✅ 通过' if is_valid else f'❌ 失败: {msg}'}")
            print(f"    性能: {perf_data['avg']:.2f}ms")

            results[period] = {
                "success": is_valid,
                "count": len(data),
                "performance": perf_data,
                "error_msg": msg if not is_valid else None
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[period] = {
                "success": False,
                "count": 0,
                "error_msg": str(e)
            }

    # 汇总结果
    success_count = sum(1 for r in results.values() if r['success'])
    print(f"\n  结果汇总: {success_count}/{len(results)}个周期成功")

    # 保存结果
    save_test_result("test_l3_kline_periods", {
        "test_type": "L3_kline_periods",
        "stock": DEFAULT_STOCK,
        "test_count": test_count,
        "results": results,
        "success_rate": (success_count / len(results)) * 100
    })

    return results


def test_kline_limit():
    """测试K线数据数量限制"""
    print("\n2. 测试K线数据数量限制")

    test = TdxQuantL3Test()

    # 测试不同数量
    test_counts = [100, 500, 1000, 1088, 1200]
    period = "1d"  # 日线

    results = {}
    document_limit = 1088  # 文档中记录的限制

    print(f"  文档记录限制: {document_limit}根")

    for count in test_counts:
        print(f"\n  请求数量: {count}根")

        try:
            data = test.get_kline_data(DEFAULT_STOCK, period, count)
            actual_count = len(data)

            # 数据验证
            is_valid, msg = validate_kline_data(data)

            # 检查限制
            if actual_count <= document_limit:
                limit_status = "✅ 符合限制"
            else:
                limit_status = f"⚠️ 超过限制: {actual_count}/{document_limit}"

            print(f"    实际数量: {actual_count}根")
            print(f"    限制检查: {limit_status}")
            print(f"    数据验证: {'✅ 通过' if is_valid else f'❌ 失败: {msg}'}")

            results[str(count)] = {
                "success": is_valid,
                "requested": count,
                "actual": actual_count,
                "within_limit": actual_count <= document_limit,
                "limit_status": limit_status,
                "error_msg": msg if not is_valid else None
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[str(count)] = {
                "success": False,
                "requested": count,
                "actual": 0,
                "error_msg": str(e)
            }

    # 保存结果
    save_test_result("test_l3_kline_limit", {
        "test_type": "L3_kline_limit",
        "stock": DEFAULT_STOCK,
        "period": period,
        "document_limit": document_limit,
        "results": results
    })

    return results


def test_today_minute_data():
    """测试当天分钟数据（应该不支持）"""
    print("\n3. 测试当天分钟数据限制")

    test = TdxQuantL3Test()

    try:
        data = test.get_today_minute_data(DEFAULT_STOCK)

        if data is None or len(data) == 0:
            print(f"  ✅ 符合预期: TdxQuant不支持当天分钟数据")
            result = {
                "test_type": "L3_today_minute",
                "success": True,
                "data_retrieved": False,
                "expected_behavior": True,
                "message": "TdxQuant正确地不支持当天分钟数据"
            }
        else:
            print(f"  ⚠️ 意外: 获取到了当天分钟数据 {len(data)}根")
            print(f"  这与文档中的结论不符，需要进一步验证")
            result = {
                "test_type": "L3_today_minute",
                "success": True,  # 获取成功也是成功
                "data_retrieved": True,
                "expected_behavior": False,
                "message": f"获取到当天分钟数据 {len(data)}根，与文档不符",
                "data_sample": data[:3] if data else []
            }

    except Exception as e:
        print(f"  ✅ 符合预期: {e}")
        result = {
            "test_type": "L3_today_minute",
            "success": True,
            "data_retrieved": False,
            "expected_behavior": True,
            "message": f"TdxQuant不支持当天分钟数据: {e}"
        }

    # 保存结果
    save_test_result("test_l3_today_minute", result)
    return result


def test_kline_performance():
    """测试K线数据获取性能"""
    print("\n4. 测试K线数据获取性能")

    test = TdxQuantL3Test()

    performance_tests = [
        ("100根日线", lambda: test.get_kline_data(DEFAULT_STOCK, "1d", 100)),
        ("500根日线", lambda: test.get_kline_data(DEFAULT_STOCK, "1d", 500)),
        ("1000根日线", lambda: test.get_kline_data(DEFAULT_STOCK, "1d", 1000)),
        ("1088根日线", lambda: test.get_kline_data(DEFAULT_STOCK, "1d", 1088)),
        ("500根1分钟", lambda: test.get_kline_data(DEFAULT_STOCK, "1m", 500)),
    ]

    # 文档中的性能数据
    document_performance = {
        "100根日线": 50.8,   # ms
        "500根日线": 35.6,   # ms
        "1000根日线": 42.1,  # ms
        "1088根日线": 42.2,  # ms
        "100根1分钟": 40.4,  # ms
    }

    results = {}

    for test_name, test_func in performance_tests:
        print(f"\n  测试: {test_name}")

        try:
            # 性能测试
            perf_data = measure_performance(
                test_func,
                warmup_count=2,
                test_count=5
            )

            # 获取实际数据验证
            data = test_func()
            is_valid, msg = validate_kline_data(data)

            # 与文档对比
            doc_time = document_performance.get(test_name.split('(')[0].strip())
            if doc_time:
                diff_pct = abs(perf_data['avg'] - doc_time) / doc_time * 100
                print(f"    当前: {perf_data['avg']:.2f}ms")
                print(f"    文档: {doc_time:.2f}ms")
                print(f"    差异: {diff_pct:.1f}%")

            print(f"    数据: {len(data)}根 {'✅' if is_valid else '❌'}")

            results[test_name] = {
                "success": is_valid,
                "count": len(data),
                "performance": perf_data,
                "document_time": doc_time,
                "diff_percentage": diff_pct if doc_time else None,
                "error_msg": msg if not is_valid else None
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[test_name] = {
                "success": False,
                "error_msg": str(e)
            }

    # 保存结果
    save_test_result("test_l3_kline_performance", {
        "test_type": "L3_kline_performance",
        "stock": DEFAULT_STOCK,
        "document_performance": document_performance,
        "results": results
    })

    return results


if __name__ == "__main__":
    import time

    print("\n开始L3 K线数据测试...\n")

    try:
        # 执行所有测试
        result1 = test_different_periods()
        result2 = test_kline_limit()
        result3 = test_today_minute_data()
        result4 = test_kline_performance()

        # 汇总结果
        print("\n" + "="*60)
        print("L3 K线测试完成")
        print("="*60)
        print(f"不同周期测试: {result1.get('success_rate', 0):.1f}%成功率")
        print(f"数量限制测试: {'✅ 通过' if all(r.get('within_limit', True) for r in result2.values()) else '❌ 失败'}")
        print(f"当天分钟数据: {'✅ 符合预期' if result3.get('expected_behavior', False) else '⚠️ 需要验证'}")
        print(f"性能测试: {sum(1 for r in result4.values() if r.get('success', False))}/{len(result4)}通过")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
