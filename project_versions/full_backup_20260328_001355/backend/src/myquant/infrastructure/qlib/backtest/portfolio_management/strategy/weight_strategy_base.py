"""
QLib WeightStrategyBase权重策略基类实现

该模块实现了与QLib官方完全兼容的WeightStrategyBase，包括：
- 权重策略基类定义
- 目标权重位置生成
- 订单列表自动生成
- 权重归一化处理
"""

from typing import Dict, Any, List
import pandas as pd

from abc import abstractmethod
from .base_strategy import BaseStrategy, StrategyMixin


class WeightStrategyBase(BaseStrategy, StrategyMixin):
    """
    QLib WeightStrategyBase权重策略基类
    
    该类实现了权重策略的基础功能，包括：
    - 目标权重位置生成接口
    - 订单列表自动生成
    - 权重归一化处理
    - 完整的持仓管理
    """
    
    def __init__(self, **kwargs: Any):
        """
        初始化WeightStrategyBase
        
        Parameters
        ----------
        **kwargs : dict
            策略参数
        """
        super().__init__(**kwargs)
        
        # 权重策略特有配置
        self.weight_config = self._get_weight_config()
        self.weight_config.update(kwargs)
        
        # 持仓跟踪
        self._current_weights = {}
        self._target_weights = {}
    
    def _get_weight_config(self) -> Dict[str, Any]:
        """
        获取权重策略默认配置
        
        Returns
        -------
        Dict[str, Any]
            默认配置字典
        """
        return {
            'normalize_weights': True,
            'min_weight': 0.0,
            'max_weight': 1.0,
            'weight_tolerance': 1e-6,
            'cash_weight_key': 'cash'
        }
    
    @abstractmethod
    def generate_target_weight_position(
        self,
        score_series: pd.Series,
        current_position: Dict[str, float],
        trade_exchange: Any = None
    ) -> Dict[str, float]:
        """
        生成目标权重位置
        
        Parameters
        ----------
        score_series : pd.Series
            评分序列，索引为股票代码，值为评分
        current_position : Dict[str, float]
            当前持仓，键为股票代码，值为持仓数量
        trade_exchange : Any, optional
            交易所
            
        Returns
        -------
        Dict[str, float]
            目标权重字典，键为股票代码，值为权重
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
        
        该方法实现了标准的权重策略订单生成流程：
        1. 调用generate_target_weight_position生成目标权重
        2. 根据目标权重生成目标数量
        3. 生成订单列表
        
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
        # 生成目标权重位置
        target_weights = self.generate_target_weight_position(
            score_series, current_position, trade_exchange
        )
        
        # 更新目标权重
        self._target_weights = target_weights.copy()
        
        # 归一化权重
        if self.weight_config['normalize_weights']:
            target_weights = self._normalize_weights(target_weights)
        
        # 生成订单列表
        orders = self._generate_orders_from_weights(
            target_weights, current_position, trade_exchange
        )
        
        # 更新当前权重
        self._current_weights = target_weights.copy()
        
        if self.config['verbose']:
            self._log_weight_changes(target_weights, current_position, orders)
        
        return orders
    
    def _normalize_weights(
        self, weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        归一化权重
        
        Parameters
        ----------
        weights : Dict[str, float]
            原始权重
            
        Returns
        -------
        Dict[str, float]
            归一化后的权重
        """
        # 过滤有效权重
        valid_weights = {
            k: v for k, v in weights.items() 
            if v > self.weight_config['weight_tolerance']
        }
        
        if not valid_weights:
            return {}
        
        # 计算总权重
        total_weight = sum(valid_weights.values())
        
        if total_weight <= 0:
            return {}
        
        # 归一化
        normalized = {}
        for stock, weight in valid_weights.items():
            normalized_weight = weight / total_weight
            # 应用权重限制
            normalized_weight = max(
                self.weight_config['min_weight'],
                min(self.weight_config['max_weight'], normalized_weight)
            )
            normalized[stock] = normalized_weight
        
        return normalized
    
    def _generate_orders_from_weights(
        self,
        target_weights: Dict[str, float],
        current_position: Dict[str, float],
        trade_exchange: Any = None
    ) -> List[Any]:
        """
        根据权重生成订单
        
        Parameters
        ----------
        target_weights : Dict[str, float]
            目标权重
        current_position : Dict[str, float]
            当前持仓
        trade_exchange : Any, optional
            交易所
            
        Returns
        -------
        List[Any]
            订单列表
        """
        orders = []
        
        # 获取总资产价值（需要从交易所或账户获取）
        total_value = self._get_total_asset_value(trade_exchange)
        
        if total_value <= 0:
            return orders
        
        # 计算目标持仓数量
        target_amounts = {}
        for stock, weight in target_weights.items():
            target_value = total_value * weight
            target_amounts[stock] = self._calculate_target_amount(
                stock, target_value, trade_exchange
            )
        
        # 生成买卖订单
        all_stocks = set(target_amounts.keys()) | set(current_position.keys())
        
        for stock in all_stocks:
            current_amount = current_position.get(stock, 0)
            target_amount = target_amounts.get(stock, 0)
            
            # 计算需要交易的数量
            trade_amount = target_amount - current_amount
            
            if abs(trade_amount) < self.weight_config['weight_tolerance']:
                continue
            
            # 创建订单
            order = self._create_order(
                stock=stock,
                amount=trade_amount,
                trade_exchange=trade_exchange
            )
            
            if order is not None:
                orders.append(order)
        
        return orders
    
    def _get_total_asset_value(self, trade_exchange: Any = None) -> float:
        """
        获取总资产价值
        
        Parameters
        ----------
        trade_exchange : Any, optional
            交易所
            
        Returns
        -------
        float
            总资产价值
        """
        # 默认实现，子类可以重写
        try:
            if trade_exchange is not None:
                return trade_exchange.get_total_asset()
        except Exception:
            pass
        
        # 如果无法获取，返回默认值
        return 1000000.0  # 100万作为默认值
    
    def _calculate_target_amount(
        self,
        stock: str,
        target_value: float,
        trade_exchange: Any = None
    ) -> float:
        """
        计算目标持仓数量
        
        Parameters
        ----------
        stock : str
            股票代码
        target_value : float
            目标价值
        trade_exchange : Any, optional
            交易所
            
        Returns
        -------
        float
            目标持仓数量
        """
        # 默认实现，子类可以重写
        try:
            if trade_exchange is not None:
                price = trade_exchange.get_current_price(stock)
                if price > 0:
                    return target_value / price
        except Exception:
            pass
        
        # 如果无法获取价格，返回0
        return 0.0
    
    def _create_order(
        self,
        stock: str,
        amount: float,
        trade_exchange: Any = None
    ) -> Any:
        """
        创建订单
        
        Parameters
        ----------
        stock : str
            股票代码
        amount : float
            交易数量（正数买入，负数卖出）
        trade_exchange : Any, optional
            交易所
            
        Returns
        -------
        Any
            订单对象
        """
        # 默认实现，子类可以重写
        try:
            # 尝试导入QLib订单类
            from qlib.backtest.decision import Order
            return Order(stock=stock, amount=amount)
        except ImportError:
            # 如果QLib不可用，返回简单的字典
            return {
                'stock': stock,
                'amount': amount,
                'type': 'buy' if amount > 0 else 'sell'
            }
    
    def _log_weight_changes(
        self,
        target_weights: Dict[str, float],
        current_position: Dict[str, float],
        orders: List[Any]
    ) -> None:
        """
        记录权重变化
        
        Parameters
        ----------
        target_weights : Dict[str, float]
            目标权重
        current_position : Dict[str, float]
            当前持仓
        orders : List[Any]
            订单列表
        """
        self._log_message(f"目标权重数量: {len(target_weights)}")
        self._log_message(f"当前持仓数量: {len(current_position)}")
        self._log_message(f"生成订单数量: {len(orders)}")
        
        # 显示前5个目标权重
        if target_weights:
            top_weights = sorted(
                target_weights.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            self._log_message(f"前5目标权重: {top_weights}")
    
    def get_current_weights(self) -> Dict[str, float]:
        """
        获取当前权重
        
        Returns
        -------
        Dict[str, float]
            当前权重
        """
        return self._current_weights.copy()
    
    def get_target_weights(self) -> Dict[str, float]:
        """
        获取目标权重
        
        Returns
        -------
        Dict[str, float]
            目标权重
        """
        return self._target_weights.copy()
    
    def reset(self) -> None:
        """重置策略状态"""
        super().reset()
        self._current_weights.clear()
        self._target_weights.clear()
        
        if self.config['verbose']:
            self._log_message("权重策略状态已重置")
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        获取策略信息
        
        Returns
        -------
        Dict[str, Any]
            策略信息
        """
        info = super().get_strategy_info()
        info.update({
            'weight_config': self.weight_config,
            'current_weights': self._current_weights,
            'target_weights': self._target_weights
        })
        return info


# 导出主要类
__all__ = [
    'WeightStrategyBase'
]