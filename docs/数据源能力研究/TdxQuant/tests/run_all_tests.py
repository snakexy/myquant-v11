"""
TdxQuant测试套件 - 运行所有测试

该脚本会运行所有TdxQuant测试，并生成综合测试报告
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("="*70)
print("TdxQuant 测试套件 - 所有测试运行器")
print("="*70)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# 测试文件列表（按优先级排序）
TEST_FILES = [
    # L0-L5层级测试
    ("L0订阅推送测试", "test_l0_subscription.py"),
    ("L1实时快照测试", "test_l1_snapshot.py"),
    ("L2历史数据测试", "test_l2_history.py"),
    ("L3 K线数据测试", "test_l3_kline.py"),
    ("L3分笔数据测试", "test_l3_tick.py"),
    ("L4财务数据测试", "test_l4_financial.py"),
    ("L5板块数据测试", "test_l5_sector.py"),

    # 专项测试
    ("性能对比测试", "test_performance.py"),
    ("限制测试", "test_limits.py"),
    ("边界测试", "test_edge_cases.py"),
]

# 测试结果存储
test_results = {}


def run_test(test_name, test_file):
    """
    运行单个测试文件

    Args:
        test_name: 测试名称
        test_file: 测试文件名

    Returns:
        bool: 测试是否成功
    """
    print(f"\n{'='*70}")
    print(f"运行测试: {test_name}")
    print(f"{'='*70}")

    test_path = os.path.join(current_dir, test_file)

    if not os.path.exists(test_path):
        print(f"❌ 测试文件不存在: {test_path}")
        return False

    try:
        # 运行测试
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        end_time = time.time()
        execution_time = end_time - start_time

        # 输出测试结果
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        # 记录结果
        test_results[test_name] = {
            "success": result.returncode == 0,
            "execution_time": execution_time,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

        if result.returncode == 0:
            print(f"\n✅ {test_name} - 测试完成 ({execution_time:.2f}秒)")
            return True
        else:
            print(f"\n❌ {test_name} - 测试失败 (返回码: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} - 测试超时（5分钟）")
        test_results[test_name] = {
            "success": False,
            "error": "超时"
        }
        return False
    except Exception as e:
        print(f"❌ {test_name} - 测试异常: {e}")
        test_results[test_name] = {
            "success": False,
            "error": str(e)
        }
        return False


def generate_summary():
    """生成测试总结报告"""
    print(f"\n{'='*70}")
    print("测试总结")
    print(f"{'='*70}")

    total_tests = len(test_results)
    success_tests = sum(
        1 for r in test_results.values() if r.get('success', False)
    )
    fail_tests = total_tests - success_tests
    total_time = sum(
        r.get('execution_time', 0) for r in test_results.values()
    )

    print("\n总体统计:")
    print(f"  总测试数: {total_tests}")
    print(f"  成功数: {success_tests} ✅")
    print(f"  失败数: {fail_tests} ❌")
    print(f"  成功率: {(success_tests/total_tests)*100:.1f}%")
    print(f"  总耗时: {total_time:.2f}秒")

    print("\n详细结果:")
    for test_name, result in test_results.items():
        status = "✅ 成功" if result.get('success', False) else "❌ 失败"
        if result.get('success', False):
            time_str = f"{result.get('execution_time', 0):.2f}秒"
        else:
            time_str = "N/A"
        print(f"  {test_name}: {status} ({time_str})")

    print(f"\n{'='*70}")


def main():
    """主函数"""
    total_start_time = time.time()

    # 运行所有测试
    for test_name, test_file in TEST_FILES:
        run_test(test_name, test_file)
        # 在测试之间稍作停顿
        time.sleep(1)

    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time

    # 生成总结
    generate_summary()

    end_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n结束时间: {end_time_str}")
    print(f"总执行时间: {total_execution_time:.2f}秒")
    print(f"{'='*70}\n")

    # 返回退出码
    success_tests = sum(1 for r in test_results.values() if r.get('success', False))
    if success_tests == len(test_results):
        print("✅ 所有测试通过！")
        return 0
    else:
        print(f"⚠️ {len(test_results) - success_tests}个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
