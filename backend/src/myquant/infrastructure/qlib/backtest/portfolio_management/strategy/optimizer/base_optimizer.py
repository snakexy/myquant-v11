"""
QLib优化器基类

该模块定义了所有优化器的基类接口，包括：
- 基础优化器抽象类
- 通用优化接口定义
- 优化结果验证
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseOptimizer(ABC):
    """
    优化器基类
    
    所有具体的优化器实现都应该继承这个基类，并实现相应的接口。
    """
    
    def __init__(self):
        """初始化优化器"""
        pass
    
    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """
        执行优化
        
        Parameters
        ----------
        *args : list
            位置参数
        **kwargs : dict
            关键字参数
            
        Returns
        -------
        Any
            优化结果
        """
        pass
    
    def validate_inputs(self, **kwargs) -> bool:
        """
        验证输入参数
        
        Parameters
        ----------
        **kwargs : dict
            输入参数
            
        Returns
        -------
        bool
            验证结果
        """
        return True
    
    def validate_output(self, output: Any) -> bool:
        """
        验证输出结果
        
        Parameters
        ----------
        output : Any
            优化结果
            
        Returns
        -------
        bool
            验证结果
        """
        return True
    
    def get_optimizer_info(self) -> Dict[str, Any]:
        """
        获取优化器信息
        
        Returns
        -------
        Dict[str, Any]
            优化器信息
        """
        return {
            'type': self.__class__.__name__,
            'module': self.__class__.__module__
        }


# 导出主要类
__all__ = [
    'BaseOptimizer'
]