"""
策略适配器 - 将自定义策略转换为QLib格式

该模块负责将平台自定义策略格式转换为QLib回测引擎所需的策略格式。
提供统一的策略接口，支持多种策略类型的转换。
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StrategyConfig:
    """策略配置数据类"""
    strategy_id: str
    strategy_name: str
    strategy_type: str  # 如：momentum, mean_reversion, factor_based
    parameters: Dict[str, Any]
    universe: List[str]  # 股票池
    frequency: str  # 频率：daily, minute等
    start_time: str
    end_time: str


class StrategyAdapter:
    """策略适配器基类"""
    
    def __init__(self, strategy_config: StrategyConfig):
        self.strategy_config = strategy_config
        self.qlib_strategy = None
        
    def convert_to_qlib_format(self) -> Any:
        """将自定义策略转换为QLib策略格式"""
        raise NotImplementedError("子类必须实现此方法")
    
    def validate_strategy(self) -> bool:
        """验证策略配置的有效性"""
        required_fields = ['strategy_id', 'strategy_type', 'universe', 'frequency']
        for field in required_fields:
            if not getattr(self.strategy_config, field, None):
                logger.error(f"策略配置缺失必要字段: {field}")
                return False
        return True


class MomentumStrategyAdapter(StrategyAdapter):
    """动量策略适配器"""
    
    def convert_to_qlib_format(self) -> Any:
        """将动量策略转换为QLib格式"""
        if not self.validate_strategy():
            return None
            
        # 这里实现具体的转换逻辑
        # 由于QLib策略格式较为复杂，这里返回一个占位符
        logger.info(f"转换动量策略: {self.strategy_config.strategy_id}")
        return {
            'type': 'momentum',
            'config': self.strategy_config.parameters,
            'universe': self.strategy_config.universe,
            'frequency': self.strategy_config.frequency
        }


class MeanReversionStrategyAdapter(StrategyAdapter):
    """均值回归策略适配器"""
    
    def convert_to_qlib_format(self) -> Any:
        """将均值回归策略转换为QLib格式"""
        if not self.validate_strategy():
            return None
            
        logger.info(f"转换均值回归策略: {self.strategy_config.strategy_id}")
        return {
            'type': 'mean_reversion',
            'config': self.strategy_config.parameters,
            'universe': self.strategy_config.universe,
            'frequency': self.strategy_config.frequency
        }


class FactorStrategyAdapter(StrategyAdapter):
    """因子策略适配器"""
    
    def convert_to_qlib_format(self) -> Any:
        """将因子策略转换为QLib格式"""
        if not self.validate_strategy():
            return None
            
        logger.info(f"转换因子策略: {self.strategy_config.strategy_id}")
        return {
            'type': 'factor',
            'config': self.strategy_config.parameters,
            'universe': self.strategy_config.universe,
            'frequency': self.strategy_config.frequency
        }


class StrategyAdapterFactory:
    """策略适配器工厂"""
    
    @staticmethod
    def create_adapter(strategy_config: StrategyConfig) -> Optional[StrategyAdapter]:
        """根据策略类型创建对应的适配器"""
        adapter_map = {
            'momentum': MomentumStrategyAdapter,
            'mean_reversion': MeanReversionStrategyAdapter,
            'factor_based': FactorStrategyAdapter
        }
        
        adapter_class = adapter_map.get(strategy_config.strategy_type)
        if not adapter_class:
            logger.error(f"不支持的策略类型: {strategy_config.strategy_type}")
            return None
            
        return adapter_class(strategy_config)


def convert_strategy_to_qlib(strategy_config: StrategyConfig) -> Any:
    """
    将自定义策略转换为QLib格式的便捷函数
    
    Args:
        strategy_config: 策略配置
        
    Returns:
        QLib格式的策略配置，如果转换失败则返回None
    """
    adapter = StrategyAdapterFactory.create_adapter(strategy_config)
    if adapter:
        return adapter.convert_to_qlib_format()
    return None