"""
投资组合适配器 - 将自定义投资组合配置转换为QLib格式

该模块负责将平台自定义投资组合配置转换为QLib回测引擎所需的投资组合格式。
支持多种投资组合构建方法和风险控制策略。
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PortfolioConfig:
    """投资组合配置数据类"""
    portfolio_id: str
    portfolio_name: str
    construction_method: str  # 构建方法：equal_weight, risk_parity, mean_variance等
    rebalance_frequency: str  # 调仓频率：daily, weekly, monthly
    risk_control: Dict[str, Any]  # 风险控制参数
    constraints: Dict[str, Any]  # 约束条件
    initial_capital: float  # 初始资金


class PortfolioAdapter:
    """投资组合适配器基类"""
    
    def __init__(self, portfolio_config: PortfolioConfig):
        self.portfolio_config = portfolio_config
        self.qlib_portfolio_config = None
        
    def convert_to_qlib_format(self) -> Any:
        """将自定义投资组合配置转换为QLib格式"""
        raise NotImplementedError("子类必须实现此方法")
    
    def validate_portfolio_config(self) -> bool:
        """验证投资组合配置的有效性"""
        required_fields = ['portfolio_id', 'construction_method', 
                          'rebalance_frequency', 'initial_capital']
        for field in required_fields:
            if not getattr(self.portfolio_config, field, None):
                logger.error(f"投资组合配置缺失必要字段: {field}")
                return False
                
        if self.portfolio_config.initial_capital <= 0:
            logger.error("初始资金必须大于0")
            return False
            
        return True


class EqualWeightPortfolioAdapter(PortfolioAdapter):
    """等权重投资组合适配器"""
    
    def convert_to_qlib_format(self) -> Any:
        """将等权重投资组合转换为QLib格式"""
        if not self.validate_portfolio_config():
            return None
            
        logger.info(f"转换等权重投资组合: {self.portfolio_config.portfolio_id}")
        return {
            'method': 'equal_weight',
            'frequency': self.portfolio_config.rebalance_frequency,
            'initial_capital': self.portfolio_config.initial_capital,
            'constraints': self.portfolio_config.constraints
        }


class RiskParityPortfolioAdapter(PortfolioAdapter):
    """风险平价投资组合适配器"""
    
    def convert_to_qlib_format(self) -> Any:
        """将风险平价投资组合转换为QLib格式"""
        if not self.validate_portfolio_config():
            return None
            
        logger.info(f"转换风险平价投资组合: {self.portfolio_config.portfolio_id}")
        return {
            'method': 'risk_parity',
            'frequency': self.portfolio_config.rebalance_frequency,
            'initial_capital': self.portfolio_config.initial_capital,
            'risk_control': self.portfolio_config.risk_control,
            'constraints': self.portfolio_config.constraints
        }


class MeanVariancePortfolioAdapter(PortfolioAdapter):
    """均值方差投资组合适配器"""
    
    def convert_to_qlib_format(self) -> Any:
        """将均值方差投资组合转换为QLib格式"""
        if not self.validate_portfolio_config():
            return None
            
        logger.info(f"转换均值方差投资组合: {self.portfolio_config.portfolio_id}")
        return {
            'method': 'mean_variance',
            'frequency': self.portfolio_config.rebalance_frequency,
            'initial_capital': self.portfolio_config.initial_capital,
            'risk_control': self.portfolio_config.risk_control,
            'constraints': self.portfolio_config.constraints
        }


class PortfolioAdapterFactory:
    """投资组合适配器工厂"""
    
    @staticmethod
    def create_adapter(portfolio_config: PortfolioConfig) -> Optional[PortfolioAdapter]:
        """根据构建方法创建对应的适配器"""
        adapter_map = {
            'equal_weight': EqualWeightPortfolioAdapter,
            'risk_parity': RiskParityPortfolioAdapter,
            'mean_variance': MeanVariancePortfolioAdapter
        }
        
        adapter_class = adapter_map.get(portfolio_config.construction_method)
        if not adapter_class:
            logger.error(f"不支持的投资组合构建方法: "
                        f"{portfolio_config.construction_method}")
            return None
            
        return adapter_class(portfolio_config)


def calculate_position_weights(signals: Dict[str, float], 
                              method: str = 'equal_weight',
                              **kwargs) -> Dict[str, float]:
    """
    根据信号计算持仓权重
    
    Args:
        signals: 股票信号字典 {股票代码: 信号值}
        method: 权重计算方法
        **kwargs: 其他参数
        
    Returns:
        持仓权重字典 {股票代码: 权重}
    """
    if not signals:
        return {}
        
    if method == 'equal_weight':
        # 等权重分配
        n_stocks = len(signals)
        weight = 1.0 / n_stocks if n_stocks > 0 else 0
        return {stock: weight for stock in signals.keys()}
        
    elif method == 'signal_weight':
        # 按信号强度分配权重
        total_signal = sum(abs(signal) for signal in signals.values())
        if total_signal == 0:
            return {stock: 0 for stock in signals.keys()}
        return {stock: abs(signal)/total_signal 
                for stock, signal in signals.items()}
                
    elif method == 'rank_weight':
        # 按信号排名分配权重
        ranked_stocks = sorted(signals.items(), 
                              key=lambda x: x[1], reverse=True)
        n_stocks = len(ranked_stocks)
        weights = {}
        for i, (stock, _) in enumerate(ranked_stocks):
            # 线性递减权重
            weight = (n_stocks - i) / sum(range(1, n_stocks + 1))
            weights[stock] = weight
        return weights
        
    else:
        logger.warning(f"不支持的权重计算方法: {method}, 使用等权重")
        n_stocks = len(signals)
        weight = 1.0 / n_stocks if n_stocks > 0 else 0
        return {stock: weight for stock in signals.keys()}


def convert_portfolio_to_qlib(portfolio_config: PortfolioConfig) -> Any:
    """
    将自定义投资组合配置转换为QLib格式的便捷函数
    
    Args:
        portfolio_config: 投资组合配置
        
    Returns:
        QLib格式的投资组合配置，如果转换失败则返回None
    """
    adapter = PortfolioAdapterFactory.create_adapter(portfolio_config)
    if adapter:
        return adapter.convert_to_qlib_format()
    return None