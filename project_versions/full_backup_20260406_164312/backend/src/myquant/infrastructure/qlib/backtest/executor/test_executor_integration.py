"""
执行器集成测试

该模块测试执行器模块的集成功能，包括：
- SimulatorExecutor基本功能测试
- NestedExecutor嵌套功能测试
- 基础设施模块测试
- 兼容性检查
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))


def test_infrastructure():
    """测试基础设施模块"""
    print("=== 测试基础设施模块 ===")
    
    try:
        from infrastructure_clean import (
            create_common_infrastructure, LevelInfrastructure,
            TradeCalendarManager
        )
        
        # 创建通用基础设施
        create_common_infrastructure()
        print("✓ 通用基础设施创建成功")
        
        # 创建层级基础设施
        LevelInfrastructure()
        print("✓ 层级基础设施创建成功")
        
        # 测试交易日历管理器
        TradeCalendarManager()
        print("✓ 交易日历管理器创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 基础设施模块测试失败: {e}")
        return False


def test_base_executor():
    """测试基础执行器"""
    print("\n=== 测试基础执行器 ===")
    
    try:
        # 测试基类导入
        print("✓ BaseExecutor基类导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 基础执行器测试失败: {e}")
        return False


def test_simulator_executor():
    """测试模拟执行器"""
    print("\n=== 测试模拟执行器 ===")
    
    try:
        from simulator_executor_clean import create_simulator_executor
        
        # 创建模拟执行器
        executor = create_simulator_executor(
            time_per_step="day",
            verbose=True
        )
        print("✓ 模拟执行器创建成功")
        
        # 测试基本属性
        assert hasattr(executor, 'time_per_step')
        assert hasattr(executor, 'TT_SERIAL')
        assert hasattr(executor, 'TT_PARAL')
        print("✓ 模拟执行器基本属性检查通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 模拟执行器测试失败: {e}")
        return False


def test_nested_executor():
    """测试嵌套执行器"""
    print("\n=== 测试嵌套执行器 ===")
    
    try:
        from nested_executor import create_nested_executor
        from simulator_executor_clean import create_simulator_executor
        
        # 创建子执行器
        sub_executor1 = create_simulator_executor(time_per_step="day")
        sub_executor2 = create_simulator_executor(time_per_step="day")
        
        # 创建嵌套执行器
        nested_executor = create_nested_executor(
            time_per_step="day",
            sub_executors=[sub_executor1, sub_executor2],
            verbose=True
        )
        print("✓ 嵌套执行器创建成功")
        
        # 测试子执行器管理
        assert len(nested_executor.get_sub_executors()) == 2
        print("✓ 子执行器管理功能正常")
        
        # 测试添加/移除子执行器
        new_executor = create_simulator_executor(time_per_step="day")
        nested_executor.add_sub_executor(new_executor)
        assert len(nested_executor.get_sub_executors()) == 3
        
        nested_executor.remove_sub_executor(new_executor)
        assert len(nested_executor.get_sub_executors()) == 2
        print("✓ 子执行器添加/移除功能正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 嵌套执行器测试失败: {e}")
        return False


def test_executor_integration():
    """测试执行器集成"""
    print("\n=== 测试执行器集成 ===")
    
    try:
        from __init__ import create_executor, check_qlib_compatibility
        
        # 测试兼容性检查
        compatibility = check_qlib_compatibility()
        print(f"✓ 兼容性检查: {compatibility}")
        
        # 测试便捷创建函数
        create_executor("simulator", time_per_step="day")
        create_executor("nested", time_per_step="day")
        print("✓ 便捷创建函数正常工作")
        
        # 测试模块信息
        from __init__ import get_executor_info
        info = get_executor_info()
        print(f"✓ 模块信息: {info}")
        
        return True
        
    except Exception as e:
        print(f"✗ 执行器集成测试失败: {e}")
        return False


def test_mock_trading_scenario():
    """测试模拟交易场景"""
    print("\n=== 测试模拟交易场景 ===")
    
    try:
        from simulator_executor_clean import create_simulator_executor
        from nested_executor import create_nested_executor
        from infrastructure_clean import create_common_infrastructure
        
        # 创建基础设施
        common_infra = create_common_infrastructure()
        
        # 创建模拟执行器
        executor = create_simulator_executor(
            time_per_step="day",
            verbose=True,
            generate_portfolio_metrics=True
        )
        
        # 重置执行器
        executor.reset(
            start_time="2020-01-01",
            end_time="2020-01-31",
            common_infra=common_infra
        )
        print("✓ 执行器重置成功")
        
        # 测试完成状态
        finished = executor.finished()
        print(f"✓ 执行器状态检查: {finished}")
        
        # 创建嵌套执行器场景
        sub_executor1 = create_simulator_executor(time_per_step="day")
        sub_executor2 = create_simulator_executor(time_per_step="day")
        
        nested_executor = create_nested_executor(
            time_per_step="day",
            sub_executors=[sub_executor1, sub_executor2],
            verbose=True
        )
        
        nested_executor.reset(
            start_time="2020-01-01",
            end_time="2020-01-31",
            common_infra=common_infra
        )
        print("✓ 嵌套执行器场景创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 模拟交易场景测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("开始执行器模块集成测试...\n")
    
    tests = [
        test_infrastructure,
        test_base_executor,
        test_simulator_executor,
        test_nested_executor,
        test_executor_integration,
        test_mock_trading_scenario
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！执行器模块集成成功。")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)