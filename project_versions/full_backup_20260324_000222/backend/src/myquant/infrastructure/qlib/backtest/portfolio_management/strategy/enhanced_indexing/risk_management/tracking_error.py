"""
跟踪误差控制模块

实现投资组合跟踪误差的计算和控制功能
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TrackingErrorController:
    """
    跟踪误差控制器
    
    提供投资组合跟踪误差的计算、分析和控制功能，
    帮助投资组合保持在相对于基准的合适偏离范围内。
    """
    
    def __init__(
        self, 
        max_tracking_error: float = 0.05,
        rebalance_threshold: float = 0.02,
        verbose: bool = False
    ):
        """
        初始化跟踪误差控制器
        
        Parameters
        ----------
        max_tracking_error : float, default 0.05
            最大允许跟踪误差（年化）
        rebalance_threshold : float, default 0.02
            再平衡阈值
        verbose : bool, default False
            是否输出详细日志
        """
        self.max_tracking_error = max_tracking_error
        self.rebalance_threshold = rebalance_threshold
        self.verbose = verbose
        
        # 历史跟踪误差记录
        self.tracking_error_history = []
        
        if self.verbose:
            logger.info("跟踪误差控制器初始化完成")
            logger.info(f"最大跟踪误差: {max_tracking_error}")
            logger.info(f"再平衡阈值: {rebalance_threshold}")
    
    def calculate_tracking_error(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
        annualize: bool = True
    ) -> float:
        """
        计算投资组合相对于基准的跟踪误差
        
        Parameters
        ----------
        portfolio_returns : pd.Series
            投资组合收益率序列
        benchmark_returns : pd.Series
            基准收益率序列
        annualize : bool, default True
            是否年化跟踪误差
            
        Returns
        -------
        float
            跟踪误差
        """
        try:
            # 确保索引对齐
            aligned_portfolio, aligned_benchmark = self._align_series(
                portfolio_returns, benchmark_returns
            )
            
            # 计算主动收益
            active_returns = aligned_portfolio - aligned_benchmark
            
            # 计算跟踪误差（标准差）
            tracking_error = active_returns.std()
            
            # 年化处理
            if annualize:
                # 假设252个交易日
                tracking_error = tracking_error * np.sqrt(252)
            
            if self.verbose:
                logger.info(f"跟踪误差计算完成: {tracking_error:.4f}")
            
            return tracking_error
            
        except Exception as e:
            logger.error(f"计算跟踪误差失败: {e}")
            return float('inf')
    
    def calculate_tracking_error_from_weights(
        self,
        portfolio_weights: np.ndarray,
        benchmark_weights: np.ndarray,
        factor_exposure: np.ndarray,
        factor_covariance: np.ndarray,
        specific_risk: np.ndarray,
        annualize: bool = True
    ) -> float:
        """
        从权重计算跟踪误差
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        benchmark_weights : np.ndarray
            基准权重
        factor_exposure : np.ndarray
            因子暴露矩阵
        factor_covariance : np.ndarray
            因子协方差矩阵
        specific_risk : np.ndarray
            特定风险向量
        annualize : bool, default True
            是否年化跟踪误差
            
        Returns
        -------
        float
            跟踪误差
        """
        try:
            # 计算主动权重
            active_weights = portfolio_weights - benchmark_weights
            
            # 计算主动风险
            active_factor_exposure = factor_exposure.T @ active_weights
            systematic_risk = (
                active_factor_exposure.T @ factor_covariance @ active_factor_exposure
            )
            idiosyncratic_risk = np.sum((active_weights * specific_risk) ** 2)
            
            # 总主动风险
            total_active_risk = systematic_risk + idiosyncratic_risk
            
            # 跟踪误差（风险的标准差）
            tracking_error = np.sqrt(total_active_risk)
            
            # 年化处理
            if annualize:
                tracking_error = tracking_error * np.sqrt(252)
            
            if self.verbose:
                logger.info(f"从权重计算跟踪误差: {tracking_error:.4f}")
            
            return tracking_error
            
        except Exception as e:
            logger.error(f"从权重计算跟踪误差失败: {e}")
            return float('inf')
    
    def check_tracking_error_limit(
        self,
        tracking_error: float
    ) -> bool:
        """
        检查跟踪误差是否超过限制
        
        Parameters
        ----------
        tracking_error : float
            当前跟踪误差
            
        Returns
        -------
        bool
            是否超过限制
        """
        exceeds_limit = tracking_error > self.max_tracking_error
        
        if exceeds_limit and self.verbose:
            logger.warning(
                f"跟踪误差{tracking_error:.4f}超过限制{self.max_tracking_error:.4f}"
            )
        
        return exceeds_limit
    
    def should_rebalance(
        self,
        current_tracking_error: float,
        previous_tracking_error: Optional[float] = None
    ) -> bool:
        """
        判断是否需要再平衡
        
        Parameters
        ----------
        current_tracking_error : float
            当前跟踪误差
        previous_tracking_error : float, optional
            前一次跟踪误差
            
        Returns
        -------
        bool
            是否需要再平衡
        """
        # 检查是否超过最大限制
        if self.check_tracking_error_limit(current_tracking_error):
            if self.verbose:
                logger.info("跟踪误差超过限制，需要再平衡")
            return True
        
        # 检查跟踪误差变化
        if previous_tracking_error is not None:
            error_change = abs(current_tracking_error - previous_tracking_error)
            if error_change > self.rebalance_threshold:
                if self.verbose:
                    logger.info(
                        f"跟踪误差变化{error_change:.4f}超过阈值，需要再平衡"
                    )
                return True
        
        return False
    
    def get_tracking_error_contribution(
        self,
        portfolio_weights: np.ndarray,
        benchmark_weights: np.ndarray,
        factor_exposure: np.ndarray,
        factor_covariance: np.ndarray,
        specific_risk: np.ndarray,
        factor_names: Optional[list] = None
    ) -> Dict[str, float]:
        """
        计算各因子对跟踪误差的贡献
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        benchmark_weights : np.ndarray
            基准权重
        factor_exposure : np.ndarray
            因子暴露矩阵
        factor_covariance : np.ndarray
            因子协方差矩阵
        specific_risk : np.ndarray
            特定风险向量
        factor_names : list, optional
            因子名称列表
            
        Returns
        -------
        Dict[str, float]
            各因子的跟踪误差贡献
        """
        try:
            # 计算主动权重
            active_weights = portfolio_weights - benchmark_weights
            
            # 计算主动因子暴露
            active_factor_exposure = factor_exposure.T @ active_weights
            
            # 计算各因子的风险贡献
            factor_contributions = {}
            n_factors = len(active_factor_exposure)
            
            for i in range(n_factors):
                factor_contribution = (
                    active_factor_exposure[i] ** 2 * factor_covariance[i, i]
                )
                factor_name = (
                    factor_names[i] if factor_names 
                    else f"factor_{i}"
                )
                factor_contributions[factor_name] = factor_contribution
            
            # 添加特定风险贡献
            idiosyncratic_contribution = np.sum((active_weights * specific_risk) ** 2)
            factor_contributions["idiosyncratic"] = idiosyncratic_contribution
            
            if self.verbose:
                logger.info(f"跟踪误差贡献计算完成，共{len(factor_contributions)}个因子")
            
            return factor_contributions
            
        except Exception as e:
            logger.error(f"计算跟踪误差贡献失败: {e}")
            return {}
    
    def update_tracking_error_history(
        self,
        tracking_error: float,
        timestamp: Optional[pd.Timestamp] = None
    ) -> None:
        """
        更新跟踪误差历史记录
        
        Parameters
        ----------
        tracking_error : float
            当前跟踪误差
        timestamp : pd.Timestamp, optional
            时间戳
        """
        if timestamp is None:
            timestamp = pd.Timestamp.now()
        
        self.tracking_error_history.append({
            'timestamp': timestamp,
            'tracking_error': tracking_error
        })
        
        # 保持历史记录在合理范围内
        max_history_size = 1000
        if len(self.tracking_error_history) > max_history_size:
            self.tracking_error_history = self.tracking_error_history[-max_history_size:]
        
        if self.verbose:
            logger.info(f"跟踪误差历史记录已更新，当前记录数: {len(self.tracking_error_history)}")
    
    def get_tracking_error_statistics(self) -> Dict[str, Any]:
        """
        获取跟踪误差统计信息
        
        Returns
        -------
        Dict[str, Any]
            跟踪误差统计信息
        """
        if not self.tracking_error_history:
            return {}
        
        errors = [record['tracking_error'] for record in self.tracking_error_history]
        
        statistics = {
            'count': len(errors),
            'mean': np.mean(errors),
            'std': np.std(errors),
            'min': np.min(errors),
            'max': np.max(errors),
            'median': np.median(errors),
            'current': errors[-1] if errors else None,
            'exceeds_limit': sum(1 for e in errors if e > self.max_tracking_error)
        }
        
        return statistics
    
    def _align_series(
        self,
        series1: pd.Series,
        series2: pd.Series
    ) -> Tuple[pd.Series, pd.Series]:
        """
        对齐两个时间序列
        
        Parameters
        ----------
        series1 : pd.Series
            第一个时间序列
        series2 : pd.Series
            第二个时间序列
            
        Returns
        -------
        Tuple[pd.Series, pd.Series]
            对齐后的时间序列
        """
        # 找到共同的索引
        common_index = series1.index.intersection(series2.index)
        
        # 对齐序列
        aligned_series1 = series1.reindex(common_index)
        aligned_series2 = series2.reindex(common_index)
        
        return aligned_series1, aligned_series2