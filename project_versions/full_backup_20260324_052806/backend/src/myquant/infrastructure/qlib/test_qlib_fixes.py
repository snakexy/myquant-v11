"""
QLib修复测试脚本
测试QLib数据路径和SignalStrategy导入修复
"""

import os
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_qlib_data_path():
    """测试QLib数据路径修复"""
    print("=" * 70)
    print("测试QLib数据路径修复")
    print("=" * 70)
    
    try:
        # 导入QLib环境管理器
        from qlib_core.qlib_env_manager import get_qlib_env_manager, QLibConfig
        
        # 创建配置 - 使用项目绝对路径
        project_root = Path(__file__).parent.parent
        data_dir = str(project_root / "data" / "qlib_data")
        
        config = QLibConfig(
            data_dir=data_dir,
            provider_uri=data_dir,
            market="cn"
        )
        
        # 验证配置
        print(f"配置的数据路径: {config.data_dir}")
        print(f"配置的provider_uri: {config.provider_uri}")
        print(f"数据路径是否存在: {os.path.exists(config.data_dir)}")
        
        # 创建环境管理器
        manager = get_qlib_env_manager(config)
        
        # 设置环境
        print("设置QLib环境...")
        success = manager.setup_environment()
        
        if success:
            print("✅ QLib环境设置成功")
            
            # 获取环境信息
            info = manager.get_environment_info()
            print(f"环境变量QLIB_DATA_DIR: {info['environment_variables']['QLIB_DATA_DIR']}")
            print(f"环境变量QLIB_PROVIDER_URI: {info['environment_variables']['QLIB_PROVIDER_URI']}")
            
            # 验证QLib配置
            try:
                import qlib
                from qlib.config import C
                actual_provider_uri = C.get("provider_uri", None)
                print(f"QLib实际使用的provider_uri: {actual_provider_uri}")
                
                if actual_provider_uri == os.path.abspath(config.provider_uri):
                    print("✅ QLib使用了正确的数据路径")
                else:
                    print(f"❌ QLib使用了错误的数据路径")
                    return False
                    
            except Exception as e:
                print(f"❌ 验证QLib配置时出错: {e}")
                return False
                
        else:
            print("❌ QLib环境设置失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 测试QLib数据路径修复失败: {e}")
        return False

def test_signal_strategy_fix():
    """测试SignalStrategy导入修复"""
    print("\n" + "=" * 70)
    print("测试SignalStrategy导入修复")
    print("=" * 70)
    
    try:
        # 导入策略修复模块
        from qlib_core.qlib_strategy_fix import fix_qlib_strategy_import
        
        # 尝试修复导入问题
        success = fix_qlib_strategy_import()
        
        if success:
            print("✅ 原始SignalStrategy模块可用")
        else:
            print("⚠️ 使用兼容性SignalStrategy模块")
        
        # 测试导入
        try:
            from qlib.contrib.strategy.signal_strategy import SignalStrategy
            print("✅ SignalStrategy导入成功")
            
            # 测试创建实例
            strategy = SignalStrategy(test_param="test_value")
            print(f"✅ SignalStrategy实例创建成功: {type(strategy)}")
            
            # 测试方法调用
            orders = strategy.generate_order_list()
            print(f"✅ generate_order_list方法调用成功: {orders}")
            
            return True
            
        except ImportError as e:
            print(f"❌ SignalStrategy导入失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 测试SignalStrategy导入修复失败: {e}")
        return False

def test_meta_learning_integration():
    """测试元学习集成"""
    print("\n" + "=" * 70)
    print("测试元学习集成")
    print("=" * 70)
    
    try:
        # 测试元学习模块导入
        from ai_strategy_engine.meta_learning import (
            MetaTaskManager, 
            MetaDatasetProcessor, 
            MetaModelAdapter
        )
        print("✅ 元学习核心模块导入成功")
        
        # 测试适配器导入
        from ai_strategy_engine.meta_learning.adapters import (
            OnlineTrainerAdapter,
            QLibForecastAdapter,
            AIRealtimeAdapter
        )
        print("✅ 元学习适配器模块导入成功")
        
        # 测试创建实例
        task_manager = MetaTaskManager()
        print("✅ MetaTaskManager实例创建成功")
        
        dataset_processor = MetaDatasetProcessor()
        print("✅ MetaDatasetProcessor实例创建成功")
        
        model_adapter = MetaModelAdapter()
        print("✅ MetaModelAdapter实例创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试元学习集成失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始QLib修复综合测试")
    
    # 测试结果
    results = []
    
    # 测试QLib数据路径修复
    results.append(("QLib数据路径修复", test_qlib_data_path()))
    
    # 测试SignalStrategy导入修复
    results.append(("SignalStrategy导入修复", test_signal_strategy_fix()))
    
    # 测试元学习集成
    results.append(("元学习集成", test_meta_learning_integration()))
    
    # 输出测试结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！QLib修复完成！")
        print("   - QLib数据路径已正确配置")
        print("   - SignalStrategy导入问题已解决")
        print("   - 元学习模块集成成功")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)