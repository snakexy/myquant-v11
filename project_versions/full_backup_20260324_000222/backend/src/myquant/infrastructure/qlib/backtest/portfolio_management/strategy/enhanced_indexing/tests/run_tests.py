"""
EnhancedIndexingStrategy测试运行脚本

运行所有测试并生成测试报告
"""

import unittest
import sys
import os

# 添加路径到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入测试模块
try:
    from test_strategy import TestEnhancedIndexingStrategy
    from test_optimizer import TestEnhancedIndexingOptimizer
    from test_risk_management import TestRiskManagement
except ImportError as e:
    print(f"导入错误: {e}")
    print("尝试使用绝对导入...")
    try:
        module_path = (
            "qlib_core.backtest.portfolio_management."
            "strategy.enhanced_indexing.tests"
        )
        from importlib import import_module
        test_strategy = import_module(f"{module_path}.test_strategy")
        test_optimizer = import_module(f"{module_path}.test_optimizer")
        test_risk_mgmt = import_module(f"{module_path}.test_risk_management")
        
        TestEnhancedIndexingStrategy = (
            test_strategy.TestEnhancedIndexingStrategy
        )
        TestEnhancedIndexingOptimizer = (
            test_optimizer.TestEnhancedIndexingOptimizer
        )
        TestRiskManagement = test_risk_mgmt.TestRiskManagement
    except ImportError as e2:
        print(f"绝对导入也失败: {e2}")
        sys.exit(1)


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedIndexingStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedIndexingOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManagement))
    
    # 运行测试
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout
    )
    
    result = runner.run(suite)
    
    # 生成测试报告
    generate_test_report(result)
    
    return result.wasSuccessful()


def generate_test_report(result):
    """生成测试报告"""
    print("\n" + "="*60)
    print("EnhancedIndexingStrategy模块测试报告")
    print("="*60)
    
    # 测试概要
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    success_rate = (total_tests - failures - errors) / total_tests * 100
    
    print(f"总测试数: {total_tests}")
    print(f"成功: {total_tests - failures - errors}")
    print(f"失败: {failures}")
    print(f"错误: {errors}")
    print(f"跳过: {skipped}")
    print(f"成功率: {success_rate:.2f}%")
    
    # 详细失败信息
    if failures > 0:
        print("\n失败详情:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError:')[-1].strip()
            print(f"- {test}: {error_msg}")
    
    # 详细错误信息
    if errors > 0:
        print("\n错误详情:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    success = run_all_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)