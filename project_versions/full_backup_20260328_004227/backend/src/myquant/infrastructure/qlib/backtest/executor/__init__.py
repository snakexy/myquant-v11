"""
QLib执行器模块

该模块提供了与QLib官方完全兼容的执行器实现，包括：
- BaseExecutor基类：定义执行器标准接口
- SimulatorExecutor：完整模拟交易执行器
- NestedExecutor：嵌套执行器支持
- 基础设施管理模块
"""

# 导入基础设施模块
from .infrastructure_clean import (
    CommonInfrastructure,
    LevelInfrastructure,
    TradeCalendarManager,
    get_start_end_idx,
    create_common_infrastructure,
    create_level_infrastructure
)

# 导入执行器类
from .base_executor import BaseExecutor, ExecutorMixin
from .simulator_executor_clean import (
    SimulatorExecutor, create_simulator_executor
)
from .nested_executor import NestedExecutor, create_nested_executor

# 版本信息
__version__ = "1.0.0"
__author__ = "QLib Compatibility Team"

# 导出的公共接口
__all__ = [
    # 基础设施
    'CommonInfrastructure',
    'LevelInfrastructure',
    'TradeCalendarManager',
    'get_start_end_idx',
    'create_common_infrastructure',
    'create_level_infrastructure',
    
    # 执行器基类
    'BaseExecutor',
    'ExecutorMixin',
    
    # 具体执行器
    'SimulatorExecutor',
    'create_simulator_executor',
    'NestedExecutor',
    'create_nested_executor',
    
    # 版本信息
    '__version__',
    '__author__'
]

# 兼容性检查


def check_qlib_compatibility():
    """
    检查QLib兼容性
    
    Returns
    -------
    dict
        兼容性检查结果
    """
    try:
        import qlib
        qlib_version = getattr(qlib, '__version__', 'unknown')
        return {
            'qlib_available': True,
            'qlib_version': qlib_version,
            'executor_compatibility': 'full'
        }
    except ImportError:
        return {
            'qlib_available': False,
            'qlib_version': None,
            'executor_compatibility': 'standalone'
        }


# 便捷函数
def create_executor(
    executor_type: str = "simulator",
    time_per_step: str = "day",
    **kwargs
):
    """
    创建执行器的便捷函数
    
    Parameters
    ----------
    executor_type : str
        执行器类型，可选值：'simulator', 'nested'
    time_per_step : str
        时间步长
    **kwargs : dict
        其他参数
        
    Returns
    -------
    BaseExecutor
        执行器实例
        
    Raises
    ------
    ValueError
        不支持的执行器类型
    """
    if executor_type == "simulator":
        return create_simulator_executor(
            time_per_step=time_per_step,
            **kwargs
        )
    elif executor_type == "nested":
        return create_nested_executor(
            time_per_step=time_per_step,
            **kwargs
        )
    else:
        raise ValueError(f"不支持的执行器类型: {executor_type}")


def get_executor_info():
    """
    获取执行器模块信息
    
    Returns
    -------
    dict
        模块信息
    """
    return {
        'version': __version__,
        'author': __author__,
        'available_executors': [
            'SimulatorExecutor',
            'NestedExecutor'
        ],
        'base_classes': [
            'BaseExecutor',
            'ExecutorMixin'
        ],
        'infrastructure': [
            'CommonInfrastructure',
            'LevelInfrastructure',
            'TradeCalendarManager'
        ]
    }


# 模块初始化时输出兼容性信息
if __name__ != "__main__":
    compatibility = check_qlib_compatibility()
    if compatibility['qlib_available']:
        print(f"[QLib Executor] QLib版本: {compatibility['qlib_version']}")
    else:
        print("[QLib Executor] QLib未安装，使用独立模式")