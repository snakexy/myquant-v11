"""
QLib TopkDropoutStrategy实现

该模块实现了与QLib官方完全兼容的TopkDropoutStrategy，包括：
- Topk-Drop算法实现
- 完整的交易决策生成
- 标准的订单列表处理
- 完整的配置参数支持
"""

from typing import Dict, Any
import pandas as pd

from .base_strategy import BaseStrategy, StrategyMixin
from .weight_strategy_base import WeightStrategyBase


class TopkDropoutStrategy(WeightStrategyBase):
    """
    QLib TopkDropoutStrategy实现
    
    该类实现了Topk-Drop算法，包括：
    - Topk股票持有数量控制
    - Drop股票轮换机制
    - 完整的权重计算
    - 标准的订单生成
    """
    
    def __init__(
        self,
        topk: int,
        n_drop: int,
        signal: pd.Series = None,
        **kwargs: Any
    ):
        """
        初始化TopkDropoutStrategy
        
        Parameters
        ----------
        topk : int
            持有的股票数量
        n_drop : int
            每个交易日卖出的股票数量
        signal : pd.Series, optional
            预测信号，索引为<datetime, instrument>，值为score
        **kwargs : dict
            其他参数
        """
        super().__init__(**kwargs)
        
        self.topk = topk
        self.n_drop = n_drop
        self.signal = signal
        
        # TopkDropout特有配置
        self.topk_config = self._get_topk_config()
        self.topk_config.update(kwargs)
        
        # 策略状态
        self._current_holdings = set()
        self._target_holdings = set()
        
        if self.config['verbose']:
            self._log_message(
                f"初始化TopkDropout策略: topk={topk}, n_drop={n_drop}"
            )
    
    def _get_topk_config(self) -> Dict[str, Any]:
        """
        获取TopkDropout策略默认配置
        
        Returns
        -------
        Dict[str, Any]
            默认配置字典
        """
        return {
            'hold_threshold': 0.0,
            'drop_threshold': 0.0,
            'min_score': -float('inf'),
            'max_score': float('inf'),
            'score_column': 'score',
            'date_column': 'datetime',
            'instrument_column': 'instrument'
        }
    
    def _initialize_strategy(self, **kwargs: Any) -> None:
        """
        具体的策略初始化逻辑
        
        Parameters
        ----------
        **kwargs : dict
            初始化参数
        """
        # 验证必要参数
        if self.topk <= 0:
            raise ValueError("topk必须大于0")
        
        if self.n_drop < 0:
            raise ValueError("n_drop必须大于等于0")
        
        if self.n_drop > self.topk:
            self._log_message(
                f"警告：n_drop({self.n_drop})大于topk({self.topk})，"
                f"将调整为topk"
            )
            self.n_drop = self.topk
        
        # 更新配置
        self.topk_config.update(kwargs)
    
    def generate_target_weight_position(
        self,
        score_series: pd.Series,
        current_position: Dict[str, float],
        trade_exchange: Any = None
    ) -> Dict[str, float]:
        """
        生成目标权重位置
        
        使用Topk-Drop算法：
        1. 根据预测分数排序股票
        2. 选择topk只股票作为目标持有
        3. 卖出当前持有中分数最低的n_drop只股票
        4. 买入未持有中分数最高的n_drop只股票
        
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
        # 获取当前时间点的预测分数
        current_scores = self._get_current_scores(score_series)
        
        if current_scores.empty:
            return {}
        
        # 过滤有效股票
        valid_scores = self._filter_valid_scores(current_scores)
        
        if valid_scores.empty:
            return {}
        
        # 按分数排序（降序）
        sorted_scores = valid_scores.sort_values(ascending=False)
        
        # 应用Topk-Drop算法
        target_weights = self._apply_topk_drop_algorithm(
            sorted_scores, current_position
        )
        
        # 更新持有状态
        self._update_holdings(target_weights, current_position)
        
        if self.config['verbose']:
            self._log_algorithm_result(
                sorted_scores, current_position, target_weights
            )
        
        return target_weights
    
    def _get_current_scores(self, score_series: pd.Series) -> pd.Series:
        """
        获取当前时间点的预测分数
        
        Parameters
        ----------
        score_series : pd.Series
            完整的预测分数序列
            
        Returns
        -------
        pd.Series
            当前时间点的预测分数
        """
        if self._current_time is None:
            return pd.Series()
        
        # 获取当前时间
        current_time = self._current_time
        
        # 如果signal是MultiIndex，按时间过滤
        if isinstance(score_series.index, pd.MultiIndex):
            try:
                current_scores = score_series.loc[current_time]
                if isinstance(current_scores, pd.Series):
                    return current_scores
                elif isinstance(current_scores, pd.DataFrame):
                    # 如果是DataFrame，取score列
                    score_col = self.topk_config['score_column']
                    if score_col in current_scores.columns:
                        return current_scores[score_col]
            except (KeyError, TypeError):
                pass
        
        # 如果signal是普通Index，直接使用
        elif isinstance(score_series.index, pd.Index):
            return score_series
        
        return pd.Series()
    
    def _filter_valid_scores(self, scores: pd.Series) -> pd.Series:
        """
        过滤有效的评分
        
        Parameters
        ----------
        scores : pd.Series
            原始评分序列
            
        Returns
        -------
        pd.Series
            过滤后的评分序列
        """
        # 移除NaN值
        valid_scores = scores.dropna()
        
        # 应用分数范围限制
        min_score = self.topk_config['min_score']
        max_score = self.topk_config['max_score']
        
        if min_score != -float('inf'):
            valid_scores = valid_scores[valid_scores >= min_score]
        
        if max_score != float('inf'):
            valid_scores = valid_scores[valid_scores <= max_score]
        
        return valid_scores
    
    def _apply_topk_drop_algorithm(
        self,
        sorted_scores: pd.Series,
        current_position: Dict[str, float]
    ) -> Dict[str, float]:
        """
        应用Topk-Drop算法
        
        Parameters
        ----------
        sorted_scores : pd.Series
            按分数排序的股票
        current_position : Dict[str, float]
            当前持仓
            
        Returns
        -------
        Dict[str, float]
            目标权重
        """
        target_weights = {}
        
        # 获取当前持有的股票
        current_stocks = (
            set(current_position.keys()) if current_position else set()
        )
        
        # 确定要卖出的股票
        stocks_to_drop = set()
        if current_stocks:
            # 从当前持有中找到分数最低的n_drop只股票
            current_scores = sorted_scores[
                sorted_scores.index.isin(current_stocks)
            ]
            
            if len(current_scores) > 0:
                # 选择分数最低的n_drop只股票
                drop_candidates = current_scores.nsmallest(self.n_drop)
                stocks_to_drop = set(drop_candidates.index)
        
        # 确定要买入的股票
        stocks_to_buy = set()
        
        # 从排序的股票中选择topk只
        top_candidates = sorted_scores.head(self.topk)
        
        # 移除要卖出的股票
        buy_candidates = top_candidates[
            ~top_candidates.index.isin(stocks_to_drop)
        ]
        
        # 如果买入候选不足，从剩余股票中补充
        remaining_stocks = sorted_scores[
            ~sorted_scores.index.isin(current_stocks)
        ]
        additional_needed = self.topk - len(buy_candidates)
        
        if additional_needed > 0 and len(remaining_stocks) > 0:
            additional_stocks = remaining_stocks.head(additional_needed)
            stocks_to_buy = (
                set(buy_candidates.index) | set(additional_stocks.index)
            )
        else:
            stocks_to_buy = set(buy_candidates.index)
        
        # 计算目标权重（等权重）
        target_stocks = stocks_to_buy - stocks_to_drop
        if target_stocks:
            weight = 1.0 / len(target_stocks)
            target_weights = {stock: weight for stock in target_stocks}
        
        return target_weights
    
    def _update_holdings(
        self,
        target_weights: Dict[str, float],
        current_position: Dict[str, float]
    ) -> None:
        """
        更新持有状态
        
        Parameters
        ----------
        target_weights : Dict[str, float]
            目标权重
        current_position : Dict[str, float]
            当前持仓
        """
        self._current_holdings = (
            set(current_position.keys()) if current_position else set()
        )
        self._target_holdings = set(target_weights.keys())
    
    def _log_algorithm_result(
        self,
        sorted_scores: pd.Series,
        current_position: Dict[str, float],
        target_weights: Dict[str, float]
    ) -> None:
        """
        记录算法结果
        
        Parameters
        ----------
        sorted_scores : pd.Series
            排序后的分数
        current_position : Dict[str, float]
            当前持仓
        target_weights : Dict[str, float]
            目标权重
        """
        current_stocks = (
            set(current_position.keys()) if current_position else set()
        )
        target_stocks = set(target_weights.keys())
        
        self._log_message(f"当前持有: {len(current_stocks)}只股票")
        self._log_message(f"目标持有: {len(target_stocks)}只股票")
        
        if target_stocks:
            top_scores = sorted_scores[target_stocks]
            self._log_message(f"目标股票分数: {top_scores.head().to_dict()}")
    
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
            'strategy_type': 'TopkDropoutStrategy',
            'topk': self.topk,
            'n_drop': self.n_drop,
            'topk_config': self.topk_config,
            'current_holdings': list(self._current_holdings),
            'target_holdings': list(self._target_holdings)
        })
        return info
    
    def reset(self) -> None:
        """重置策略状态"""
        super().reset()
        self._current_holdings.clear()
        self._target_holdings.clear()
        
        if self.config['verbose']:
            self._log_message("TopkDropout策略状态已重置")
    
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
        # 获取当前持仓
        current_position = {}
        if trade_account is not None:
            current_position = trade_account.get_current_position()
        
        # 生成目标权重
        target_weights = self.generate_target_weight_position(
            self.signal, current_position, trade_exchange
        )
        
        # 生成订单列表
        orders = self.generate_order_list(
            self.signal, current_position, trade_exchange
        )
        
        # 创建交易决策对象
        try:
            from qlib.backtest.decision import BaseTradeDecision
            return BaseTradeDecision(orders)
        except ImportError:
            # 如果QLib不可用，返回简单的字典
            return {
                'orders': orders,
                'target_weights': target_weights,
                'current_position': current_position
            }


# 便捷创建函数
def create_topk_dropout_strategy(
    topk: int,
    n_drop: int,
    signal: pd.Series = None,
    **kwargs: Any
) -> TopkDropoutStrategy:
    """
    创建TopkDropoutStrategy实例的便捷函数
    
    Parameters
    ----------
    topk : int
        持有的股票数量
    n_drop : int
        每个交易日卖出的股票数量
    signal : pd.Series, optional
        预测信号
    **kwargs : dict
        其他参数
        
    Returns
    -------
    TopkDropoutStrategy
        策略实例
    """
    return TopkDropoutStrategy(
        topk=topk,
        n_drop=n_drop,
        signal=signal,
        **kwargs
    )


# 导出主要类和函数
__all__ = [
    'TopkDropoutStrategy',
    'create_topk_dropout_strategy'
]