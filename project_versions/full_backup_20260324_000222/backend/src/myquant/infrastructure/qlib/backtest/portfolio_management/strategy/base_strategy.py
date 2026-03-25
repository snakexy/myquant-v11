"""
QLib BaseStrategy基类实现

该模块实现了与QLib官方完全兼容的BaseStrategy基类，包括：
- 标准的策略接口定义
- 交易决策生成流程
- 策略状态管理
- 完整的生命周期支持
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd

# 尝试导入QLib
try:
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False


class BaseStrategy(ABC):
    """
    QLib BaseStrategy基类
    
    该类定义了所有策略的通用接口和基础功能，包括：
    - 标准的策略初始化流程
    - 通用的交易决策生成接口
    - 基础的策略状态管理
    - 完整的生命周期支持
    """
    
    def __init__(self, **kwargs: Any):
        """
        初始化BaseStrategy
        
        Parameters
        ----------
        **kwargs : dict
            策略参数
        """
        self.kwargs = kwargs
        self._initialized = False
        self._current_time = None
        self._trade_decision_cache = {}
        
        # 策略配置
        self.config = self._get_default_config()
        self.config.update(kwargs)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns
        -------
        Dict[str, Any]
            默认配置字典
        """
        return {
            'verbose': False,
            'cache_decisions': True,
            'max_cache_size': 1000
        }
    
    def initialize(self, **kwargs: Any) -> None:
        """
        初始化策略
        
        Parameters
        ----------
        **kwargs : dict
            初始化参数
        """
        if self.config['verbose']:
            print(f"[{self.__class__.__name__}] 初始化策略...")
        
        # 更新配置
        self.config.update(kwargs)
        
        # 执行具体的初始化逻辑
        self._initialize_strategy(**kwargs)
        
        self._initialized = True
        
        if self.config['verbose']:
            print(f"[{self.__class__.__name__}] 策略初始化完成")
    
    @abstractmethod
    def _initialize_strategy(self, **kwargs: Any) -> None:
        """
        具体的策略初始化逻辑
        
        Parameters
        ----------
        **kwargs : dict
            初始化参数
        """
        pass
    
    @abstractmethod
    def generate_trade_decision(
        self,
        trade_account: Any = None,
        trade_exchange: Any = None
    ) -> Any:
        """
        生成交易决策
        
        Parameters
        ----------
        trade_account : Any, optional
            交易账户
        trade_exchange : Any, optional
            交易所
            
        Returns
        -------
        Any
            交易决策
        """
        pass
    
    def generate_order_list(
        self,
        score_series: pd.Series,
        current_position: Dict[str, float],
        trade_exchange: Any = None
    ) -> List[Any]:
        """
        生成订单列表
        
        Parameters
        ----------
        score_series : pd.Series
            评分序列
        current_position : Dict[str, float]
            当前持仓
        trade_exchange : Any, optional
            交易所
            
        Returns
        -------
        List[Any]
            订单列表
        """
        # 默认实现：子类可以重写
        return []
    
    def update_time(self, current_time: Any) -> None:
        """
        更新当前时间
        
        Parameters
        ----------
        current_time : Any
            当前时间
        """
        self._current_time = current_time
        
        # 清理过期的决策缓存
        if self.config['cache_decisions']:
            self._clean_decision_cache()
    
    def get_current_time(self) -> Any:
        """
        获取当前时间
        
        Returns
        -------
        Any
            当前时间
        """
        return self._current_time
    
    def is_initialized(self) -> bool:
        """
        检查是否已初始化
        
        Returns
        -------
        bool
            是否已初始化
        """
        return self._initialized
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取策略配置
        
        Returns
        -------
        Dict[str, Any]
            策略配置
        """
        return self.config.copy()
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        设置策略配置
        
        Parameters
        ----------
        config : Dict[str, Any]
            策略配置
        """
        self.config.update(config)
    
    def _cache_decision(self, key: str, decision: Any) -> None:
        """
        缓存交易决策
        
        Parameters
        ----------
        key : str
            缓存键
        decision : Any
            交易决策
        """
        if not self.config['cache_decisions']:
            return
        
        if len(self._trade_decision_cache) >= self.config['max_cache_size']:
            # 删除最旧的缓存项
            oldest_key = next(iter(self._trade_decision_cache))
            del self._trade_decision_cache[oldest_key]
        
        self._trade_decision_cache[key] = decision
    
    def _get_cached_decision(self, key: str) -> Any:
        """
        获取缓存的交易决策
        
        Parameters
        ----------
        key : str
            缓存键
            
        Returns
        -------
        Any
            交易决策，如果不存在则返回None
        """
        return self._trade_decision_cache.get(key)
    
    def _clean_decision_cache(self) -> None:
        """清理过期的决策缓存"""
        # 默认实现：子类可以重写以实现特定的清理逻辑
        pass
    
    def reset(self) -> None:
        """重置策略状态"""
        self._current_time = None
        self._trade_decision_cache.clear()
        self._reset_strategy()
        
        if self.config['verbose']:
            print(f"[{self.__class__.__name__}] 策略状态已重置")
    
    def _reset_strategy(self) -> None:
        """
        具体的策略重置逻辑
        
        子类可以重写此方法以实现特定的重置逻辑
        """
        pass
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        获取策略信息
        
        Returns
        -------
        Dict[str, Any]
            策略信息
        """
        return {
            'class_name': self.__class__.__name__,
            'initialized': self._initialized,
            'current_time': self._current_time,
            'config': self.config,
            'cache_size': len(self._trade_decision_cache)
        }
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}(initialized={self._initialized})"


class StrategyMixin:
    """
    策略混入类
    
    提供通用的策略功能，可以被具体的策略类继承使用
    """
    
    def _log_message(self, message: str) -> None:
        """
        记录日志消息
        
        Parameters
        ----------
        message : str
            日志消息
        """
        if hasattr(self, 'config') and self.config.get('verbose', False):
            print(f"[{self.__class__.__name__}] {message}")
    
    def _validate_inputs(self, **inputs: Any) -> bool:
        """
        验证输入参数
        
        Parameters
        ----------
        **inputs : Any
            输入参数
            
        Returns
        -------
        bool
            是否有效
        """
        # 基本的验证逻辑，子类可以重写
        for key, value in inputs.items():
            if value is None:
                self._log_message(f"警告：参数 {key} 为None")
                return False
        return True
    
    def _prepare_trading_context(
        self,
        trade_account: Any = None,
        trade_exchange: Any = None
    ) -> Dict[str, Any]:
        """
        准备交易上下文
        
        Parameters
        ----------
        trade_account : Any, optional
            交易账户
        trade_exchange : Any, optional
            交易所
            
        Returns
        -------
        Dict[str, Any]
            交易上下文
        """
        context = {
            'current_time': getattr(self, '_current_time', None),
            'strategy_class': self.__class__.__name__
        }
        
        # 添加账户和交易所信息
        if trade_account is not None:
            context['trade_account'] = trade_account
        if trade_exchange is not None:
            context['trade_exchange'] = trade_exchange
        
        return context


# 导出主要类
__all__ = [
    'BaseStrategy',
    'StrategyMixin'
]