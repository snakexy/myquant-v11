"""
调试导入问题
检查各个模块是否可以正确导入
"""

import sys
import traceback
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_import(module_path, class_name=None):
    """检查模块导入"""
    try:
        print(f"\n检查导入: {module_path}")
        if class_name:
            print(f"类: {class_name}")
        
        # 动态导入模块
        module_name = module_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        module = __import__(module_name, fromlist=['*'])
        
        if class_name:
            test_class = getattr(module, class_name)
            print(f"✅ 成功导入类: {class_name}")
        else:
            print(f"✅ 成功导入模块: {module_path}")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        print("详细错误信息:")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("="*60)
    print("调试QLib兼容性升级项目导入问题")
    print("="*60)
    
    # 检查基础模块导入
    print("\n1. 检查基础模块导入")
    basic_modules = [
        'qlib_core',
        'qlib_core.backtest',
        'qlib_core.backtest.portfolio_management',
        'qlib_core.backtest.portfolio_management.strategy',
        'qlib_core.backtest.portfolio_management.strategy.enhanced_indexing',
        'qlib_core.backtest.portfolio_management.strategy.enhanced_indexing.risk_management',
        'qlib_core.backtest.workflow',
    ]
    
    for module in basic_modules:
        check_import(module)
    
    # 检查具体类导入
    print("\n2. 检查具体类导入")
    class_imports = [
        {
            'module': 'qlib_core/backtest/portfolio_management/strategy/enhanced_indexing/risk_management/tracking_error',
            'class': 'TrackingErrorController'
        },
        {
            'module': 'qlib_core/backtest/portfolio_management/strategy/enhanced_indexing/risk_management/risk_exposure',
            'class': 'RiskExposureManager'
        },
        {
            'module': 'qlib_core/backtest/portfolio_management/strategy/enhanced_indexing/optimizer/enhanced_indexing_optimizer',
            'class': 'EnhancedIndexingOptimizer'
        },
        {
            'module': 'qlib_core/backtest/workflow/config_parser',
            'class': 'ConfigParser'
        },
        {
            'module': 'qlib_core/backtest/workflow/task_scheduler',
            'class': 'TaskScheduler'
        },
        {
            'module': 'qlib_core/backtest/workflow/enhanced_workflow_manager',
            'class': 'EnhancedWorkflowManager'
        }
    ]
    
    for item in class_imports:
        check_import(item['module'], item['class'])
    
    # 检查文件是否存在
    print("\n3. 检查文件是否存在")
    files_to_check = [
        'qlib_core/backtest/portfolio_management/strategy/enhanced_indexing/risk_management/tracking_error.py',
        'qlib_core/backtest/portfolio_management/strategy/enhanced_indexing/risk_management/risk_exposure.py',
        'qlib_core/backtest/portfolio_management/strategy/enhanced_indexing/optimizer/enhanced_indexing_optimizer.py',
        'qlib_core/backtest/workflow/config_parser.py',
        'qlib_core/backtest/workflow/task_scheduler.py',
        'qlib_core/backtest/workflow/enhanced_workflow_manager.py'
    ]
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ 文件存在: {file_path}")
        else:
            print(f"❌ 文件不存在: {file_path}")
    
    print("\n4. 检查Python路径")
    print(f"项目根目录: {project_root}")
    print(f"Python路径包含:")
    for path in sys.path[:5]:  # 只显示前5个路径
        print(f"  - {path}")
    
    print("\n5. 检查模块结构")
    enhanced_indexing_path = project_root / 'qlib_core/backtest/portfolio_management/strategy/enhanced_indexing'
    if enhanced_indexing_path.exists():
        print("enhanced_indexing目录结构:")
        for item in enhanced_indexing_path.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(project_root)
                print(f"  - {rel_path}")
    else:
        print("❌ enhanced_indexing目录不存在")

if __name__ == '__main__':
    main()