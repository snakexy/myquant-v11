"""
QLib核心接口层 (QLib Core Interface Layer)
提供与QLib框架的深度集成和数据格式桥接
"""

__version__ = "1.0.0"
__author__ = "智能量化平台团队"

# 注：QLib核心接口层提供与QLib框架的深度集成
# 主要模块包括：
# - QLib数据提供器 (qlib_data_provider)
# - QLib环境管理器 (qlib_env_manager)
# - QLib导出器 (qlib_exporter)
# - 分析模块 (analysis)
# - 回测模块 (backtest)
# - 投资分析模块 (investment_analytics)

# 懒加载导入，避免顶层导入时的依赖问题
__all__ = [
    'EnhancedPerformanceAnalyzer',
    'EnhancedBacktestExecutor',
    'get_enhanced_performance_analyzer',
    'get_enhanced_backtest_executor'
]

def __getattr__(name: str):
    """懒加载模块"""
    if name == 'EnhancedPerformanceAnalyzer':
        from .analysis.enhanced_performance_analyzer import EnhancedPerformanceAnalyzer
        return EnhancedPerformanceAnalyzer
    elif name == 'EnhancedBacktestExecutor':
        from .backtest.enhanced_backtest_executor import EnhancedBacktestExecutor
        return EnhancedBacktestExecutor
    elif name == 'get_enhanced_performance_analyzer':
        from .analysis.enhanced_performance_analyzer import get_enhanced_performance_analyzer
        return get_enhanced_performance_analyzer
    elif name == 'get_enhanced_backtest_executor':
        from .backtest.enhanced_backtest_executor import get_enhanced_backtest_executor
        return get_enhanced_backtest_executor
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")