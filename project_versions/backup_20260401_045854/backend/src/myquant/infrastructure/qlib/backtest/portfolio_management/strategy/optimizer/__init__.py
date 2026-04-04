"""
QLib优化器模块

该模块提供了与QLib官方完全兼容的优化器实现，包括：
- 基础优化器抽象类
- 增强指数优化器
- 风险控制和约束处理
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "QLib Compatibility Team"

# 导出的公共接口
__all__ = [
    '__version__',
    '__author__',
    'BaseOptimizer',
    'EnhancedIndexingOptimizer'
]

# 导入主要类
from .base_optimizer import BaseOptimizer
from .enhanced_indexing_optimizer import EnhancedIndexingOptimizer


# 兼容性检查


def check_optimizer_compatibility():
    """
    检查优化器兼容性
    
    Returns
    -------
    dict
        兼容性检查结果
    """
    try:
        import cvxpy
        cvxpy_version = getattr(cvxpy, '__version__', 'unknown')
        return {
            'cvxpy_available': True,
            'cvxpy_version': cvxpy_version,
            'optimizer_compatibility': 'full'
        }
    except ImportError:
        return {
            'cvxpy_available': False,
            'cvxpy_version': None,
            'optimizer_compatibility': 'simplified'
        }


# 模块初始化时输出兼容性信息


if __name__ != "__main__":
    compatibility = check_optimizer_compatibility()
    if compatibility['cvxpy_available']:
        print(f"[QLib Optimizer] CVXPY版本: {compatibility['cvxpy_version']}")
    else:
        print("[QLib Optimizer] CVXPY未安装，使用简化实现")