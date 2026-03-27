"""
QLib BaseExecutor基类实现

该模块实现了与QLib官方完全兼容的BaseExecutor基类，包括：
- 标准的执行器接口定义
- 通用的交易决策执行流程
- 基础设施管理功能
- 执行器层级管理
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union

# 导入基础设施模块
from .infrastructure_clean import (
    CommonInfrastructure, LevelInfrastructure
)


class BaseExecutor(ABC):
    """
    QLib BaseExecutor基类
    
    该类定义了所有执行器的通用接口和基础功能，包括：
    - 标准的执行器初始化流程
    - 通用的交易决策执行接口
    - 基础设施管理功能
    - 执行器层级管理
    """
    
    def __init__(
        self,
        time_per_step: str,
        start_time: Union[str, Any] = None,
        end_time: Union[str, Any] = None,
        indicator_config: Dict[str, Any] = None,
        generate_portfolio_metrics: bool = False,
        verbose: bool = False,
        track_data: bool = False,
        **kwargs: Any
    ):
        """
        初始化BaseExecutor
        
        Parameters
        ----------
        time_per_step : str
            每个交易步骤的时间频率
        start_time : str, optional
            开始时间
        end_time : str, optional
            结束时间
        indicator_config : dict, optional
            指标配置
        generate_portfolio_metrics : bool, optional
            是否生成投资组合指标
        verbose : bool, optional
            是否输出详细信息
        track_data : bool, optional
            是否跟踪数据
        **kwargs : dict
            其他参数
        """
        self.time_per_step = time_per_step
        self.indicator_config = indicator_config or {}
        self.generate_portfolio_metrics = generate_portfolio_metrics
        self.verbose = verbose
        self.track_data = track_data
        
        # 子类需要初始化基础设施
        self.level_infra = None
    
    @abstractmethod
    def reset(
        self,
        start_time: Union[str, Any] = None,
        end_time: Union[str, Any] = None,
        common_infra: CommonInfrastructure = None,
        **kwargs: Any
    ) -> None:
        """
        重置执行器
        
        Parameters
        ----------
        start_time : str, optional
            开始时间
        end_time : str, optional
            结束时间
        common_infra : CommonInfrastructure, optional
            通用基础设施
        **kwargs : dict
            其他参数
        """
        pass
    
    @abstractmethod
    def finished(self) -> bool:
        """检查是否完成"""
        pass
    
    @abstractmethod
    def get_level_infra(self) -> LevelInfrastructure:
        """获取层级基础设施"""
        pass
    
    @abstractmethod
    def get_all_executors(self) -> List['BaseExecutor']:
        """获取所有执行器"""
        pass
    
    @abstractmethod
    def _collect_data(
        self,
        trade_decision: Any,
        level: int = 0
    ) -> tuple:
        """
        收集交易数据
        
        Parameters
        ----------
        trade_decision : Any
            交易决策
        level : int
            层级
            
        Returns
        -------
        tuple
            (执行结果, 额外参数)
        """
        pass
    
    def collect_data(
        self,
        trade_decision: Any,
        return_value: dict = None,
        level: int = 0
    ):
        """
        收集交易数据（生成器版本）
        
        Parameters
        ----------
        trade_decision : Any
            交易决策
        return_value : dict, optional
            返回值字典
        level : int
            层级
            
        Yields
        ------
        Any
            交易决策或结果
        """
        # 如果需要跟踪数据
        if self.track_data:
            yield trade_decision
        
        # 执行数据收集
        result, kwargs = self._collect_data(trade_decision, level)
        
        # 返回结果
        if return_value is not None:
            return_value.update(kwargs)
            yield return_value
    
    def execute(
        self,
        trade_decision: Any,
        level: int = 0
    ) -> List[object]:
        """
        执行交易决策
        
        Parameters
        ----------
        trade_decision : Any
            交易决策
        level : int
            层级
            
        Returns
        -------
        List[object]
            执行结果列表
        """
        result, _ = self._collect_data(trade_decision, level)
        return result
    
    def get_indicator_config(self) -> Dict[str, Any]:
        """获取指标配置"""
        return self.indicator_config
    
    def set_indicator_config(self, config: Dict[str, Any]) -> None:
        """设置指标配置"""
        self.indicator_config = config
    
    def is_generating_portfolio_metrics(self) -> bool:
        """是否生成投资组合指标"""
        return self.generate_portfolio_metrics
    
    def set_generate_portfolio_metrics(self, generate: bool) -> None:
        """设置是否生成投资组合指标"""
        self.generate_portfolio_metrics = generate
    
    def is_verbose(self) -> bool:
        """是否输出详细信息"""
        return self.verbose
    
    def set_verbose(self, verbose: bool) -> None:
        """设置是否输出详细信息"""
        self.verbose = verbose
    
    def is_tracking_data(self) -> bool:
        """是否跟踪数据"""
        return self.track_data
    
    def set_track_data(self, track: bool) -> None:
        """设置是否跟踪数据"""
        self.track_data = track


class ExecutorMixin:
    """
    执行器混入类
    
    提供通用的执行器功能，可以被具体的执行器类继承使用
    """
    
    def _log_message(self, message: str) -> None:
        """
        记录日志消息
        
        Parameters
        ----------
        message : str
            日志消息
        """
        if hasattr(self, 'verbose') and self.verbose:
            print(message)
    
    def _validate_trade_decision(self, trade_decision: Any) -> bool:
        """
        验证交易决策
        
        Parameters
        ----------
        trade_decision : Any
            交易决策
            
        Returns
        -------
        bool
            是否有效
        """
        if trade_decision is None:
            return False
        
        # 子类可以重写此方法以实现特定的验证逻辑
        return True
    
    def _prepare_execution_context(self, level: int = 0) -> Dict[str, Any]:
        """
        准备执行上下文
        
        Parameters
        ----------
        level : int
            层级
            
        Returns
        -------
        Dict[str, Any]
            执行上下文
        """
        context = {
            'level': level,
            'time_per_step': getattr(self, 'time_per_step', 'day'),
            'executor_type': self.__class__.__name__
        }
        
        # 添加基础设施信息
        if hasattr(self, 'level_infra') and self.level_infra:
            context['trade_calendar'] = self.level_infra.trade_calendar
            context['common_infra'] = self.level_infra.common_infra
        
        return context


# 导出主要类
__all__ = [
    'BaseExecutor',
    'ExecutorMixin'
]