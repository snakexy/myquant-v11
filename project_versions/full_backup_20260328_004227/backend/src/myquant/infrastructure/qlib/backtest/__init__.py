"""
QLib回测模块
提供与QLib回测功能的集成接口

该模块包含完整的QLib回测系统，包括：
- QLib回测引擎
- 策略适配器
- 投资组合适配器
- 回测运行器

注意：性能分析功能位于qlib_core/analysis/目录
"""

__version__ = "1.0.0"
__author__ = "智能量化平台团队"

# 导入关键模块
from .qlib_backtest_engine import QLibBacktestEngine
from .strategy_adapter import (
    StrategyAdapter, StrategyAdapterFactory, StrategyConfig,
    convert_strategy_to_qlib
)
from .portfolio_management.portfolio_adapter import (
    PortfolioAdapter, PortfolioAdapterFactory, PortfolioConfig,
    convert_portfolio_to_qlib, calculate_position_weights
)
from .qlib_backtest_runner import (
    QLibBacktestRunner, BacktestConfig, BacktestResult,
    BacktestRunnerFactory, run_qlib_backtest, run_batch_backtests,
    validate_backtest_config
)

__all__ = [
    # QLib回测引擎
    'QLibBacktestEngine',
    
    # 策略适配器
    'StrategyAdapter', 'StrategyAdapterFactory', 'StrategyConfig',
    'convert_strategy_to_qlib',
    
    # 投资组合适配器
    'PortfolioAdapter', 'PortfolioAdapterFactory', 'PortfolioConfig',
    'convert_portfolio_to_qlib', 'calculate_position_weights',
    
    # 回测运行器
    'QLibBacktestRunner', 'BacktestConfig', 'BacktestResult',
    'BacktestRunnerFactory', 'run_qlib_backtest', 'run_batch_backtests',
    'validate_backtest_config'
]