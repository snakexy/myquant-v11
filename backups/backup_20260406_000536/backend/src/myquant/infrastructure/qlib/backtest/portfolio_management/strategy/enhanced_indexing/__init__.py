"""
EnhancedIndexingStrategy模块

该模块提供了完整的增强指数策略实现，包括：
- 主要策略类
- 扩展功能
- 优化器
- 风险管理
- 数据处理
- 工具函数
- 测试用例
"""

from .strategy import EnhancedIndexingStrategy
from .extensions import EnhancedIndexingStrategyExtensions

# 导入子模块
from .optimizer import BaseOptimizer, EnhancedIndexingOptimizer
from .risk_management import (
    TrackingErrorController,
    RiskExposureManager,
    SectorExposureManager
)
from .data_loaders import RiskDataLoader, BenchmarkLoader
from .utils import CacheManager, Validators

# 导入测试模块
from .tests import (
    TestEnhancedIndexingStrategy,
    TestEnhancedIndexingOptimizer,
    TestRiskManagement
)

__all__ = [
    'EnhancedIndexingStrategy',
    'EnhancedIndexingStrategyExtensions',
    'BaseOptimizer',
    'EnhancedIndexingOptimizer',
    'TrackingErrorController',
    'RiskExposureManager',
    'SectorExposureManager',
    'RiskDataLoader',
    'BenchmarkLoader',
    'CacheManager',
    'Validators',
    'TestEnhancedIndexingStrategy',
    'TestEnhancedIndexingOptimizer',
    'TestRiskManagement'
]