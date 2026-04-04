"""
QLib特征工程模块

该模块提供了与QLib官方标准兼容的特征工程功能，包括：
- Alpha158特征集
- 特征计算引擎
- 向量化操作
"""

from .alpha158 import Alpha158Processor, create_alpha158_processor
from .alpha158_parallel import (
    Alpha158ParallelProcessor, 
    create_alpha158_parallel_processor
)

__all__ = [
    'Alpha158Processor',
    'create_alpha158_processor',
    'Alpha158ParallelProcessor',
    'create_alpha158_parallel_processor'
]