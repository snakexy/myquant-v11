"""
TdxQuant测试工具函数
"""

import time
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple


def time_execution(func):
    """装饰器：测量函数执行时间"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # 转换为毫秒
        return result, execution_time
    return wrapper


def measure_performance(func, warmup_count=3, test_count=10):
    """
    测量函数性能

    Args:
        func: 要测试的函数
        warmup_count: 预热次数
        test_count: 测试次数

    Returns:
        dict: 包含平均、最小、最大执行时间的性能数据
    """
    # 预热
    for _ in range(warmup_count):
        try:
            func()
        except:
            pass

    # 实际测试
    times = []
    errors = 0

    for i in range(test_count):
        try:
            start_time = time.time()
            result = func()
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # 毫秒
            times.append(execution_time)
        except Exception as e:
            errors += 1
            print(f"  第{i+1}次测试失败: {e}")

    if times:
        return {
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "count": len(times),
            "errors": errors,
            "success_rate": (len(times) / test_count) * 100
        }
    else:
        return {
            "avg": 0,
            "min": 0,
            "max": 0,
            "count": 0,
            "errors": errors,
            "success_rate": 0
        }


def save_test_result(test_name: str, result: Dict[str, Any]):
    """
    保存测试结果到JSON文件

    Args:
        test_name: 测试名称
        result: 测试结果字典
    """
    results_dir = "../test_results"
    os.makedirs(results_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{results_dir}/{test_name}_{timestamp}.json"

    result["timestamp"] = timestamp
    result["test_name"] = test_name

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  测试结果已保存到: {filename}")
    return filename


def print_performance_result(test_name: str, perf_data: Dict[str, Any]):
    """
    打印性能测试结果

    Args:
        test_name: 测试名称
        perf_data: 性能数据字典
    """
    print(f"\n{'='*60}")
    print(f"{test_name} - 性能测试结果")
    print(f"{'='*60}")
    print(f"  平均时间: {perf_data['avg']:.2f}ms")
    print(f"  最小时间: {perf_data['min']:.2f}ms")
    print(f"  最大时间: {perf_data['max']:.2f}ms")
    print(f"  测试次数: {perf_data['count']}")
    print(f"  错误次数: {perf_data['errors']}")
    print(f"  成功率: {perf_data['success_rate']:.1f}%")
    print(f"{'='*60}\n")


def validate_kline_data(data: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    验证K线数据格式和内容

    Args:
        data: K线数据列表

    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not data:
        return False, "K线数据为空"

    required_fields = ['time', 'open', 'high', 'low', 'close', 'volume']

    for i, item in enumerate(data):
        # 检查必要字段
        for field in required_fields:
            if field not in item:
                return False, f"第{i+1}条数据缺少字段: {field}"

        # 检查数据类型
        try:
            assert isinstance(item['time'], (str, int)), "时间字段类型错误"
            assert isinstance(item['open'], (int, float)), "开字段类型错误"
            assert isinstance(item['high'], (int, float)), "高字段类型错误"
            assert isinstance(item['low'], (int, float)), "低字段类型错误"
            assert isinstance(item['close'], (int, float)), "收字段类型错误"
            assert isinstance(item['volume'], (int, float)), "量字段类型错误"

            # 检查逻辑有效性
            assert item['high'] >= item['open'], f"第{i+1}条: 最高价<开盘价"
            assert item['high'] >= item['close'], f"第{i+1}条: 最高价<收盘价"
            assert item['high'] >= item['low'], f"第{i+1}条: 最高价<最低价"
            assert item['low'] <= item['open'], f"第{i+1}条: 最低价>开盘价"
            assert item['low'] <= item['close'], f"第{i+1}条: 最低价>收盘价"
            assert item['volume'] >= 0, f"第{i+1}条: 成交量<0"
        except AssertionError as e:
            return False, f"第{i+1}条数据验证失败: {e}"

    return True, "数据格式正确"


def validate_snapshot_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    验证快照数据格式和内容

    Args:
        data: 快照数据字典

    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not data:
        return False, "快照数据为空"

    # 检查必要字段（根据实际API返回调整）
    required_fields = ['symbol', 'price', 'volume']

    for field in required_fields:
        if field not in data:
            return False, f"缺少必要字段: {field}"

    try:
        assert data['price'] > 0, "价格必须大于0"
        assert data['volume'] >= 0, "成交量必须>=0"
    except AssertionError as e:
        return False, f"数据验证失败: {e}"

    return True, "数据格式正确"


def format_result(result: Any) -> str:
    """
    格式化输出结果

    Args:
        result: 任意类型的结果对象

    Returns:
        str: 格式化后的字符串
    """
    if isinstance(result, (list, dict)):
        return json.dumps(result, ensure_ascii=False, indent=2)
    elif hasattr(result, '__dict__'):
        return str(result.__dict__)
    else:
        return str(result)


def get_test_summary(results: Dict[str, Any]) -> str:
    """
    生成测试总结

    Args:
        results: 测试结果字典

    Returns:
        str: 测试总结字符串
    """
    summary = f"\n{'='*60}\n"
    summary += f"测试总结\n"
    summary += f"{'='*60}\n"

    for test_name, test_result in results.items():
        status = "✅ 成功" if test_result.get('success', False) else "❌ 失败"
        summary += f"{test_name}: {status}\n"

    summary += f"{'='*60}\n"
    return summary
