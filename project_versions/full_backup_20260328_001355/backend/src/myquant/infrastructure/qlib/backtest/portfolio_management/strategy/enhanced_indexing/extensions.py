"""
EnhancedIndexingStrategy扩展功能

该模块提供了增强指数策略的扩展功能，包括：
- 跟踪误差控制
- 风险暴露管理
- 优化算法集成
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class EnhancedIndexingStrategyExtensions:
    """
    增强指数策略扩展类
    
    提供额外的功能来增强基础的增强指数策略，包括更高级的
    跟踪误差控制、风险暴露管理和优化算法集成。
    """
    
    def __init__(self, strategy_instance=None, verbose: bool = False):
        """
        初始化扩展功能
        
        Parameters
        ----------
        strategy_instance : EnhancedIndexingStrategy, optional
            策略实例
        verbose : bool, default False
            是否输出详细日志
        """
        self.strategy = strategy_instance
        self.verbose = verbose
        
        if self.verbose:
            logger.info("增强指数策略扩展功能初始化完成")
    
    def calculate_tracking_error(
        self, 
        portfolio_weights: np.ndarray, 
        benchmark_weights: np.ndarray,
        factor_exp: np.ndarray, 
        factor_cov: np.ndarray, 
        specific_risk: np.ndarray
    ) -> float:
        """
        计算投资组合的跟踪误差
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        benchmark_weights : np.ndarray
            基准权重
        factor_exp : np.ndarray
            因子暴露
        factor_cov : np.ndarray
            因子协方差矩阵
        specific_risk : np.ndarray
            特定风险
            
        Returns
        -------
        float
            跟踪误差（年化）
        """
        try:
            # 计算主动权重
            active_weights = portfolio_weights - benchmark_weights
            
            # 计算主动风险
            active_factor_exp = factor_exp.T @ active_weights
            active_risk = (
                active_factor_exp.T @ factor_cov @ active_factor_exp +
                np.sum((active_weights * specific_risk) ** 2)
            )
            
            # 年化跟踪误差（假设252个交易日）
            tracking_error = np.sqrt(active_risk * 252)
            
            if self.verbose:
                logger.info(f"跟踪误差计算完成: {tracking_error:.4f}")
            
            return tracking_error
            
        except Exception as e:
            logger.error(f"计算跟踪误差失败: {e}")
            return float('inf')
    
    def calculate_risk_exposure(
        self, 
        portfolio_weights: np.ndarray, 
        factor_exp: np.ndarray, 
        factor_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        计算投资组合的风险因子暴露
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        factor_exp : np.ndarray
            因子暴露矩阵
        factor_names : List[str], optional
            因子名称列表
            
        Returns
        -------
        Dict[str, float]
            风险因子暴露字典
        """
        try:
            # 计算加权因子暴露
            weighted_factor_exp = factor_exp.T @ portfolio_weights
            
            # 创建因子名称
            if factor_names is None:
                factor_names = [f"factor_{i}" for i in range(len(weighted_factor_exp))]
            
            # 构建暴露字典
            exposure_dict = {
                factor_names[i]: weighted_factor_exp[i] 
                for i in range(len(weighted_factor_exp))
            }
            
            if self.verbose:
                logger.info(f"风险暴露计算完成，共{len(exposure_dict)}个因子")
            
            return exposure_dict
            
        except Exception as e:
            logger.error(f"计算风险暴露失败: {e}")
            return {}
    
    def calculate_sector_exposure(
        self, 
        portfolio_weights: np.ndarray, 
        sector_mapping: Dict[str, str]
    ) -> Dict[str, float]:
        """
        计算投资组合的行业暴露
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        sector_mapping : Dict[str, str]
            股票到行业的映射
            
        Returns
        -------
        Dict[str, float]
            行业暴露字典
        """
        try:
            # 初始化行业暴露字典
            sector_exposure = {}
            
            # 计算每个行业的总权重
            for stock_idx, (stock, weight) in enumerate(zip(sector_mapping.keys(), portfolio_weights)):
                sector = sector_mapping[stock]
                sector_exposure[sector] = sector_exposure.get(sector, 0) + weight
            
            if self.verbose:
                logger.info(f"行业暴露计算完成，共{len(sector_exposure)}个行业")
            
            return sector_exposure
            
        except Exception as e:
            logger.error(f"计算行业暴露失败: {e}")
            return {}
    
    def optimize_tracking_error(
        self,
        score_series: pd.Series,
        current_position: Dict[str, float],
        benchmark_weights: np.ndarray,
        risk_data: Tuple,
        max_tracking_error: float = 0.05,
        lambda_te: float = 0.5,
        lambda_ret: float = 0.5
    ) -> Optional[Dict[str, float]]:
        """
        优化投资组合以控制跟踪误差
        
        Parameters
        ----------
        score_series : pd.Series
            股票评分序列
        current_position : Dict[str, float]
            当前持仓
        benchmark_weights : np.ndarray
            基准权重
        risk_data : Tuple
            风险数据 (factor_exp, factor_cov, specific_risk, universe, blacklist)
        max_tracking_error : float, default 0.05
            最大跟踪误差
        lambda_te : float, default 0.5
            跟踪误差权重
        lambda_ret : float, default 0.5
            收益权重
            
        Returns
        -------
        Dict[str, float] or None
            优化后的权重字典
        """
        try:
            factor_exp, factor_cov, specific_risk, universe, blacklist = risk_data
            
            # 转换评分
            score = score_series.reindex(universe).fillna(score_series.min()).values
            
            # 获取当前权重
            cur_weight = np.array([
                current_position.get(stock, 0) for stock in universe
            ])
            
            # 构建优化问题
            n_assets = len(universe)
            
            # 目标函数：最大化收益，同时控制跟踪误差
            # 这里简化为线性组合，实际应用中可能需要更复杂的优化
            objective = lambda_ret * score - lambda_te * np.abs(cur_weight - benchmark_weights)
            
            # 约束条件
            constraints = [
                # 权重和为1
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                # 权重非负
                {'type': 'ineq', 'fun': lambda w: w}
            ]
            
            # 跟踪误差约束
            def tracking_error_constraint(w):
                active_weights = w - benchmark_weights
                active_risk = (
                    active_weights @ factor_cov @ active_weights.T +
                    np.sum((w * specific_risk) ** 2)
                )
                te = np.sqrt(active_risk * 252)
                return max_tracking_error - te
            
            constraints.append({
                'type': 'ineq', 
                'fun': tracking_error_constraint
            })
            
            # 使用scipy优化器求解
            from scipy.optimize import minimize
            
            result = minimize(
                lambda w: -objective @ w,
                x0=cur_weight,
                method='SLSQP',
                constraints=constraints,
                bounds=[(0, 1) for _ in range(n_assets)],
                options={'ftol': 1e-9, 'disp': False}
            )
            
            if result.success:
                # 构建权重字典
                optimized_weights = {
                    stock: weight 
                    for stock, weight in zip(universe, result.x) 
                    if weight > 1e-6  # 过滤掉极小权重
                }
                
                if self.verbose:
                    logger.info(f"跟踪误差优化完成，持有{len(optimized_weights)}只股票")
                
                return optimized_weights
            else:
                logger.warning(f"跟踪误差优化失败: {result.message}")
                return None
                
        except Exception as e:
            logger.error(f"跟踪误差优化失败: {e}")
            return None
    
    def get_risk_metrics(
        self,
        portfolio_weights: np.ndarray,
        benchmark_weights: np.ndarray,
        risk_data: Tuple,
        factor_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        获取投资组合的风险指标
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        benchmark_weights : np.ndarray
            基准权重
        risk_data : Tuple
            风险数据 (factor_exp, factor_cov, specific_risk, universe, blacklist)
        factor_names : List[str], optional
            因子名称列表
            
        Returns
        -------
        Dict[str, Any]
            风险指标字典
        """
        try:
            factor_exp, factor_cov, specific_risk, universe, blacklist = risk_data
            
            # 计算跟踪误差
            tracking_error = self.calculate_tracking_error(
                portfolio_weights, benchmark_weights,
                factor_exp, factor_cov, specific_risk
            )
            
            # 计算风险暴露
            risk_exposure = self.calculate_risk_exposure(
                portfolio_weights, factor_exp, factor_names
            )
            
            # 计算主动风险
            active_weights = portfolio_weights - benchmark_weights
            active_factor_exp = factor_exp.T @ active_weights
            active_risk = (
                active_factor_exp.T @ factor_cov @ active_factor_exp +
                np.sum((active_weights * specific_risk) ** 2)
            )
            
            # 计算总风险
            total_factor_exp = factor_exp.T @ portfolio_weights
            total_risk = (
                total_factor_exp.T @ factor_cov @ total_factor_exp +
                np.sum((portfolio_weights * specific_risk) ** 2)
            )
            
            # 计算风险分解
            systematic_risk = total_factor_exp.T @ factor_cov @ total_factor_exp
            idiosyncratic_risk = np.sum((portfolio_weights * specific_risk) ** 2)
            
            # 计算主动风险分解
            active_systematic_risk = active_factor_exp.T @ factor_cov @ active_factor_exp
            active_idiosyncratic_risk = np.sum((active_weights * specific_risk) ** 2)
            
            # 构建风险指标字典
            risk_metrics = {
                'tracking_error': tracking_error,
                'tracking_variance': tracking_error ** 2,
                'active_risk': np.sqrt(active_risk * 252),
                'total_risk': np.sqrt(total_risk * 252),
                'systematic_risk': np.sqrt(systematic_risk * 252),
                'idiosyncratic_risk': np.sqrt(idiosyncratic_risk * 252),
                'active_systematic_risk': np.sqrt(active_systematic_risk * 252),
                'active_idiosyncratic_risk': np.sqrt(active_idiosyncratic_risk * 252),
                'risk_exposure': risk_exposure,
                'portfolio_concentration': np.sum(portfolio_weights ** 2),
                'active_share': np.sum(np.abs(active_weights)),
                'turnover_estimate': np.sum(np.abs(active_weights)) / 2
            }
            
            if self.verbose:
                logger.info(f"风险指标计算完成，跟踪误差: {tracking_error:.4f}")
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"计算风险指标失败: {e}")
            return {}