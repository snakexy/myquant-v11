"""
投资分析系统 - Investment Analytics System

专注于投资决策后的深度分析和绩效评估，为投资经理提供专业的分析工具和决策支持。

该模块是 QLib 核心层的一部分，提供：
- PortfolioAnalyzer: 投资组合分析
- PortfolioOptimizer: 投资组合优化
- PortfolioVisualizer: 投资组合可视化
- PerformanceAttribution: 绩效归因分析
- RiskAttribution: 风险归因分析
- AttributionVisualizer: 归因可视化

注：策略实现请使用 qlib_core.backtest.portfolio_management.strategy
"""
__version__ = "1.0.0"
__author__ = "MyQuant Team"

from .portfolio import (
    PortfolioAnalyzer,
    PortfolioOptimizer,
    PortfolioVisualizer
)
from .attribution import (
    PerformanceAttribution,
    RiskAttribution,
    AttributionVisualizer
)

__all__ = [
    'PortfolioAnalyzer',
    'PortfolioOptimizer',
    'PortfolioVisualizer',
    'PerformanceAttribution',
    'RiskAttribution',
    'AttributionVisualizer'
]