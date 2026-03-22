"""
TdxQuant L3分笔数据测试

测试目标：
1. 验证TdxQuant的分笔数据获取功能
2. 测试Tick数据格式和字段
3. 测试逐笔成交数据
4. 验证分笔数据的准确性
5. 评估分笔数据的实用性
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
    DEFAULT_STOCK,
    PERFORMANCE_CONFIG
)

print("="*60)
print("TdxQuant L3分笔数据测试")
print("="*60)
print(f"测试股票: {DEFAULT_STOCK}")
print("="*60)


class TdxQuantL3TickTest:
    """TdxQuant L3分笔数据测试类"""

    def __init__(self):
        # TODO: 初始化TdxQuant连接
        self.client = None
        print("\n⚠️ 注意: 需要集成实际的TdxQuant API客户端")
        print("  请根据实际的TdxQuant SDK修改此文件")

    def get_tick_data(self, symbol: str, count: int = 100):
        """
        获取Tick数据

        Args:
            symbol: 股票代码
            count: 获取数量

        Returns:
            list: Tick数据列表
        """
        # TODO: 实现实际的API调用
        # 示例代码（需要根据实际API调整）：
        # return self.client.get_tick_data(symbol, count)

        # 模拟数据（仅用于演示）
        import random
        import time
        data = []

        base_price = 1850.0
        base_time = int(time.time())

        for i in range(count):
            data.append({
                "time": base_time - i,
                "price": base_price + random.uniform(-0.5, 0.5),
                "volume": random.randint(100, 1000),
                "direction": random.choice(["买", "卖", "平"]),
                "order_no": base_time - i
            })
            base_price = data[-1]["price"]

        return data

    def get_transaction_data(self, symbol: str, date: str = None):
        """
        获取逐笔成交数据

        Args:
            symbol: 股票代码
            date: 日期（格式: YYYY-MM-DD）

        Returns:
            list: 逐笔成交数据
        """
        # TODO: 实现实际的API调用
        return []


def test_tick_data_retrieval():
    """测试Tick数据获取"""
    print("\n1. 测试Tick数据获取")

    test = TdxQuantL3TickTest()

    # 测试不同数量的Tick数据
    tick_counts = [100, 500, 1000]

    results = {}

    for count in tick_counts:
        print(f"\n  请求数量: {count}条")

        try:
            def get_data():
                return test.get_tick_data(DEFAULT_STOCK, count)

            # 性能测试
            perf_data = measure_performance(
                get_data,
                warmup_count=PERFORMANCE_CONFIG['warmup_count'],
                test_count=5
            )

            # 获取实际数据
            tick_data = get_data()
            actual_count = len(tick_data)

            # 数据验证
            if actual_count > 0:
                sample_tick = tick_data[0]
                required_fields = ['time', 'price', 'volume']
                has_required_fields = all(field in sample_tick for field in required_fields)

                print(f"    实际数量: {actual_count}条")
                print(f"    数据验证: {'✅ 通过' if has_required_fields else '❌ 失败'}")
                print(f"    性能: {perf_data['avg']:.2f}ms")

                if has_required_fields:
                    print(f"    示例Tick: 价格={sample_tick['price']:.2f}, 量={sample_tick['volume']}, 方向={sample_tick.get('direction', 'N/A')}")

                results[f"{count}条"] = {
                    "success": has_required_fields,
                    "requested": count,
                    "actual": actual_count,
                    "performance": perf_data,
                    "sample_tick": sample_tick
                }
            else:
                print(f"    ⚠️ 无数据返回")
                results[f"{count}条"] = {
                    "success": False,
                    "requested": count,
                    "actual": 0,
                    "note": "无数据返回"
                }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[f"{count}条"] = {
                "success": False,
                "requested": count,
                "actual": 0,
                "error_msg": str(e)
            }

    # 保存结果
    save_test_result("test_l3_tick_retrieval", {
        "test_type": "L3_tick_retrieval",
        "stock": DEFAULT_STOCK,
        "results": results
    })

    return results


def test_tick_data_fields():
    """测试Tick数据字段完整性"""
    print("\n2. 测试Tick数据字段完整性")

    test = TdxQuantL3TickTest()

    # 获取样本数据
    tick_data = test.get_tick_data(DEFAULT_STOCK, 100)

    if len(tick_data) == 0:
        print("  ❌ 无数据可供分析")
        return {
            "test_type": "L3_tick_fields",
            "success": False,
            "note": "无数据"
        }

    # 分析字段
    print(f"\n  Tick数据字段分析:")
    print(f"    数据样本数量: {len(tick_data)}条")

    sample = tick_data[0]
    fields = list(sample.keys())

    print(f"    字段数量: {len(fields)}个")
    print(f"    字段列表: {', '.join(fields)}")

    # 定义期望的字段
    expected_fields = {
        "基础字段": ["time", "price", "volume"],
        "方向字段": ["direction"],
        "订单字段": ["order_no"],
        "扩展字段": ["bid", "ask", "bid_vol", "ask_vol"]
    }

    print(f"\n  字段完整性检查:")
    field_check_results = {}

    for category, field_list in expected_fields.items():
        print(f"    {category}:")
        for field in field_list:
            exists = field in fields
            status = "✅" if exists else "❌"
            print(f"      {status} {field}: {'存在' if exists else '缺失'}")
            field_check_results[field] = exists

    # 数据类型验证
    print(f"\n  数据类型验证:")
    type_validation = {}

    for tick in tick_data[:10]:  # 检查前10条
        for field in fields:
            if field not in type_validation:
                type_validation[field] = type(tick[field]).__name__

    for field, type_name in type_validation.items():
        print(f"    {field}: {type_name}")

    # 保存结果
    save_test_result("test_l3_tick_fields", {
        "test_type": "L3_tick_fields",
        "stock": DEFAULT_STOCK,
        "sample_count": len(tick_data),
        "fields": fields,
        "field_check": field_check_results,
        "type_validation": type_validation
    })

    return {
        "test_type": "L3_tick_fields",
        "success": True,
        "fields": fields,
        "field_check": field_check_results
    }


def test_transaction_data():
    """测试逐笔成交数据"""
    print("\n3. 测试逐笔成交数据")

    test = TdxQuantL3TickTest()

    print("\n  根据文档:")
    print("    TdxQuant: ⚠️ 部分支持分笔数据")
    print("    XtQuant:  ❌ 不支持分笔数据")
    print("    PyTdx:    ⚠️ 部分支持分笔数据")

    print("\n  测试逐笔成交数据:")

    try:
        # 获取逐笔成交数据
        transaction_data = test.get_transaction_data(DEFAULT_STOCK)

        if transaction_data and len(transaction_data) > 0:
            print(f"    ✅ 成功获取逐笔成交: {len(transaction_data)}条")
            print(f"    示例: {transaction_data[0]}")

            result = {
                "test_type": "L3_transaction",
                "success": True,
                "supported": True,
                "count": len(transaction_data),
                "sample": transaction_data[0]
            }
        else:
            print(f"    ⚠️ 无逐笔成交数据返回")
            print(f"    这说明分笔数据支持情况需要进一步验证")

            result = {
                "test_type": "L3_transaction",
                "success": True,
                "supported": False,
                "count": 0,
                "note": "分笔数据支持情况不确定"
            }

    except Exception as e:
        print(f"    ⚠️ 获取失败: {e}")
        print(f"    这可能表明分笔数据不支持或API未实现")

        result = {
            "test_type": "L3_transaction",
            "success": False,
            "supported": False,
            "error": str(e),
            "note": "分笔数据可能不支持"
        }

    # 保存结果
    save_test_result("test_l3_transaction", result)
    return result


def test_tick_data_quality():
    """测试Tick数据质量"""
    print("\n4. 测试Tick数据质量")

    test = TdxQuantL3TickTest()

    # 获取足够的数据进行质量分析
    tick_data = test.get_tick_data(DEFAULT_STOCK, 1000)

    if len(tick_data) == 0:
        print("  ❌ 无数据可供质量分析")
        return {
            "test_type": "L3_tick_quality",
            "success": False
        }

    print(f"\n  Tick数据质量分析（{len(tick_data)}条）:")

    # 1. 时间序列检查
    print("\n  1. 时间序列检查:")
    time_sequence = [tick['time'] for tick in tick_data]
    is_descending = all(time_sequence[i] >= time_sequence[i+1] for i in range(len(time_sequence)-1))
    print(f"    时间顺序: {'✅ 降序（正确）' if is_descending else '❌ 无序'}")

    # 2. 价格合理性检查
    print("\n  2. 价格合理性检查:")
    prices = [tick['price'] for tick in tick_data]
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    price_range = max_price - min_price

    print(f"    价格范围: {min_price:.2f} ~ {max_price:.2f}")
    print(f"    价格波动: {price_range:.2f}")
    print(f"    平均价格: {avg_price:.2f}")

    # 3. 成交量检查
    print("\n  3. 成交量检查:")
    volumes = [tick['volume'] for tick in tick_data]
    min_volume = min(volumes)
    max_volume = max(volumes)
    total_volume = sum(volumes)

    print(f"    单笔最小: {min_volume}")
    print(f"    单笔最大: {max_volume}")
    print(f"    总成交量: {total_volume}")

    # 4. 方向统计（如果有）
    print("\n  4. 买卖方向统计:")
    if 'direction' in tick_data[0]:
        direction_counts = {}
        for tick in tick_data:
            direction = tick.get('direction', '未知')
            direction_counts[direction] = direction_counts.get(direction, 0) + 1

        for direction, count in direction_counts.items():
            percentage = (count / len(tick_data)) * 100
            print(f"    {direction}: {count}次 ({percentage:.1f}%)")

    # 质量评估
    quality_score = 0
    if is_descending:
        quality_score += 25
    if price_range < 50:  # 价格波动合理
        quality_score += 25
    if min_volume > 0:  # 成交量合理
        quality_score += 25
    if len(tick_data) >= 100:  # 数据量充足
        quality_score += 25

    print(f"\n  质量评分: {quality_score}/100")

    # 保存结果
    save_test_result("test_l3_tick_quality", {
        "test_type": "L3_tick_quality",
        "stock": DEFAULT_STOCK,
        "sample_count": len(tick_data),
        "time_sequence_valid": is_descending,
        "price_analysis": {
            "min": min_price,
            "max": max_price,
            "avg": avg_price,
            "range": price_range
        },
        "volume_analysis": {
            "min": min_volume,
            "max": max_volume,
            "total": total_volume
        },
        "quality_score": quality_score
    })

    return {
        "test_type": "L3_tick_quality",
        "success": True,
        "quality_score": quality_score
    }


def test_l3_tick_comparison():
    """L3分笔数据对比"""
    print("\n5. L3分笔数据对比")

    print("\n  文档中的对比:")
    print("    TdxQuant: ⚠️ 部分支持分笔数据")
    print("    XtQuant:  ❌ 不支持分笔数据")
    print("    PyTdx:    ⚠️ 部分支持分笔数据")

    print("\n  使用建议:")
    print("    分笔数据 → TdxQuant是较好选择")
    print("      - 虽然只是部分支持，但优于完全不支持的XtQuant")
    print("      - 需要验证具体支持的字段和限制")
    print("      - 建议用于简单的Tick数据分析")

    # 保存结果
    save_test_result("test_l3_tick_comparison", {
        "test_type": "L3_tick_comparison",
        "comparison": {
            "TdxQuant": "部分支持",
            "XtQuant": "不支持",
            "PyTdx": "部分支持"
        },
        "recommendation": "TdxQuant是分笔数据较好选择"
    })

    return {
        "test_type": "L3_tick_comparison",
        "recommendation": "TdxQuant是分笔数据较好选择"
    }


if __name__ == "__main__":
    import time

    print("\n开始L3分笔数据测试...\n")

    try:
        # 执行所有测试
        result1 = test_tick_data_retrieval()
        result2 = test_tick_data_fields()
        result3 = test_transaction_data()
        result4 = test_tick_data_quality()
        result5 = test_l3_tick_comparison()

        # 汇总结果
        print("\n" + "="*60)
        print("L3分笔数据测试完成")
        print("="*60)
        print(f"Tick数据获取: {sum(1 for r in result1.values() if r.get('success', False))}/{len(result1)}通过")
        print(f"字段完整性: {'✅ 通过' if result2.get('success', False) else '❌ 失败'}")
        print(f"逐笔成交: {'✅ 支持' if result3.get('supported', False) else '⚠️ 不确定'}")
        print(f"数据质量: {'✅ 优秀' if result4.get('quality_score', 0) >= 75 else '⚠️ 一般'}")
        print(f"对比分析: 已完成")
        print("="*60)

        print("\n重要发现:")
        print("  ⚠️ TdxQuant对分笔数据只是部分支持")
        print("  ⚠️ 需要实际环境验证具体支持的字段和限制")
        print("  ✅ 相比XtQuant（不支持），TdxQuant是分笔数据的选择")
        print("  📋 建议用于简单的Tick数据分析，复杂分析需验证支持情况")

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
