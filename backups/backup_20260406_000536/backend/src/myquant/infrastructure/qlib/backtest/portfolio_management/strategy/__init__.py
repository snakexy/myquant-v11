"""
QLib策略接口模块

该模块提供了与QLib官方完全兼容的策略接口实现，包括：
- BaseStrategy基类：定义策略标准接口
- WeightStrategyBase权重策略基类
- TopkDropoutStrategy实现
- 增强指数策略支持
"""

# 导入基础策略类
from .base_strategy import BaseStrategy, StrategyMixin
from .weight_strategy_base import WeightStrategyBase

# 导入TopkDropout策略（注意：类名是TopkDropoutStrategy，小写k）
from .topk_dropout_strategy import TopkDropoutStrategy as TopkDropoutStrategy
from .topk_dropout_strategy import create_topk_dropout_strategy

# 提供大写K的别名，方便使用
TopKDropoutStrategy = TopkDropoutStrategy

# 导入增强指数策略（可选）
try:
    from .enhanced_indexing_strategy import EnhancedIndexingStrategy
except ImportError:
    EnhancedIndexingStrategy = None

# 版本信息
__version__ = "1.0.0"
__author__ = "QLib Compatibility Team"

# 导出的公共接口
__all__ = [
    '__version__',
    '__author__',
    'BaseStrategy',
    'StrategyMixin',
    'WeightStrategyBase',
    'TopkDropoutStrategy',  # 原始类名（小写k）
    'TopKDropoutStrategy',  # 别名（大写K）
    'EnhancedIndexingStrategy',
    'create_topk_dropout_strategy'
]

# 兼容性检查


def check_qlib_compatibility():
    """
    检查QLib策略兼容性
    
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
            'strategy_compatibility': 'full'
        }
    except ImportError:
        return {
            'qlib_available': False,
            'qlib_version': None,
            'strategy_compatibility': 'standalone'
        }


# 模块初始化时输出兼容性信息
if __name__ != "__main__":
    compatibility = check_qlib_compatibility()
    if compatibility['qlib_available']:
        print(f"[QLib Strategy] QLib版本: {compatibility['qlib_version']}")
    else:
        print("[QLib Strategy] QLib未安装，使用独立模式")