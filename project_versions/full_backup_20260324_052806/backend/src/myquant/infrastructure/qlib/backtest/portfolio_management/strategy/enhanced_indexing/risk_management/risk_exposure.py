"""
风险暴露管理模块

实现投资组合风险因子暴露的计算和管理功能
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class RiskExposureManager:
    """
    风险暴露管理器
    
    提供投资组合风险因子暴露的计算、分析和控制功能，
    帮助投资组合保持在合适的风险水平。
    """
    
    def __init__(
        self, 
        factor_limits: Optional[Dict[str, float]] = None,
        verbose: bool = False
    ):
        """
        初始化风险暴露管理器
        
        Parameters
        ----------
        factor_limits : Dict[str, float], optional
            因子暴露限制
        verbose : bool, default False
            是否输出详细日志
        """
        self.factor_limits = factor_limits or {}
        self.verbose = verbose
        
        # 历史风险暴露记录
        self.exposure_history = []
        
        if self.verbose:
            logger.info("风险暴露管理器初始化完成")
            if self.factor_limits:
                logger.info(f"因子暴露限制: {self.factor_limits}")
    
    def calculate_risk_exposure(
        self,
        portfolio_weights: np.ndarray,
        factor_exposure: np.ndarray,
        factor_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        计算投资组合的风险因子暴露
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        factor_exposure : np.ndarray
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
            weighted_factor_exposure = factor_exposure.T @ portfolio_weights
            
            # 创建因子名称
            if factor_names is None:
                factor_names = [f"factor_{i}" for i in range(len(weighted_factor_exposure))]
            
            # 构建暴露字典
            exposure_dict = {
                factor_names[i]: weighted_factor_exposure[i] 
                for i in range(len(weighted_factor_exposure))
            }
            
            if self.verbose:
                logger.info(f"风险暴露计算完成，共{len(exposure_dict)}个因子")
            
            return exposure_dict
            
        except Exception as e:
            logger.error(f"计算风险暴露失败: {e}")
            return {}
    
    def calculate_active_risk_exposure(
        self,
        portfolio_weights: np.ndarray,
        benchmark_weights: np.ndarray,
        factor_exposure: np.ndarray,
        factor_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        计算投资组合的主动风险因子暴露
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        benchmark_weights : np.ndarray
            基准权重
        factor_exposure : np.ndarray
            因子暴露矩阵
        factor_names : List[str], optional
            因子名称列表
            
        Returns
        -------
        Dict[str, float]
            主动风险因子暴露字典
        """
        try:
            # 计算主动权重
            active_weights = portfolio_weights - benchmark_weights
            
            # 计算主动因子暴露
            active_factor_exposure = factor_exposure.T @ active_weights
            
            # 创建因子名称
            if factor_names is None:
                factor_names = [f"factor_{i}" for i in range(len(active_factor_exposure))]
            
            # 构建主动暴露字典
            active_exposure_dict = {
                factor_names[i]: active_factor_exposure[i] 
                for i in range(len(active_factor_exposure))
            }
            
            if self.verbose:
                logger.info(f"主动风险暴露计算完成，共{len(active_exposure_dict)}个因子")
            
            return active_exposure_dict
            
        except Exception as e:
            logger.error(f"计算主动风险暴露失败: {e}")
            return {}
    
    def check_exposure_limits(
        self,
        risk_exposure: Dict[str, float]
    ) -> Dict[str, bool]:
        """
        检查风险暴露是否超过限制
        
        Parameters
        ----------
        risk_exposure : Dict[str, float]
            风险暴露字典
            
        Returns
        -------
        Dict[str, bool]
            各因子是否超过限制
        """
        limit_results = {}
        
        for factor, limit in self.factor_limits.items():
            exposure = risk_exposure.get(factor, 0)
            exceeds_limit = abs(exposure) > abs(limit)
            limit_results[factor] = exceeds_limit
            
            if exceeds_limit and self.verbose:
                logger.warning(
                    f"因子{factor}暴露{exposure:.4f}超过限制{limit:.4f}"
                )
        
        return limit_results
    
    def calculate_exposure_contribution(
        self,
        portfolio_weights: np.ndarray,
        factor_exposure: np.ndarray,
        factor_covariance: np.ndarray,
        factor_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        计算各因子对投资组合风险的贡献
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        factor_exposure : np.ndarray
            因子暴露矩阵
        factor_covariance : np.ndarray
            因子协方差矩阵
        factor_names : List[str], optional
            因子名称列表
            
        Returns
        -------
        Dict[str, float]
            各因子的风险贡献
        """
        try:
            # 计算加权因子暴露
            weighted_factor_exposure = factor_exposure.T @ portfolio_weights
            
            # 计算各因子的风险贡献
            factor_contributions = {}
            n_factors = len(weighted_factor_exposure)
            
            for i in range(n_factors):
                # 计算因子i的风险贡献
                factor_contribution = 0
                for j in range(n_factors):
                    factor_contribution += (
                        weighted_factor_exposure[i] * 
                        factor_covariance[i, j] * 
                        weighted_factor_exposure[j]
                    )
                
                factor_name = (
                    factor_names[i] if factor_names 
                    else f"factor_{i}"
                )
                factor_contributions[factor_name] = factor_contribution
            
            if self.verbose:
                logger.info(f"风险贡献计算完成，共{len(factor_contributions)}个因子")
            
            return factor_contributions
            
        except Exception as e:
            logger.error(f"计算风险贡献失败: {e}")
            return {}
    
    def get_top_risk_factors(
        self,
        risk_exposure: Dict[str, float],
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        获取风险暴露最高的因子
        
        Parameters
        ----------
        risk_exposure : Dict[str, float]
            风险暴露字典
        top_n : int, default 5
            返回的因子数量
            
        Returns
        -------
        List[Tuple[str, float]]
            按风险暴露排序的因子列表
        """
        try:
            # 按绝对值排序
            sorted_factors = sorted(
                risk_exposure.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )
            
            # 返回前N个因子
            top_factors = sorted_factors[:top_n]
            
            if self.verbose:
                logger.info(f"获取前{top_n}个风险因子")
            
            return top_factors
            
        except Exception as e:
            logger.error(f"获取主要风险因子失败: {e}")
            return []
    
    def update_exposure_history(
        self,
        risk_exposure: Dict[str, float],
        timestamp: Optional[pd.Timestamp] = None
    ) -> None:
        """
        更新风险暴露历史记录
        
        Parameters
        ----------
        risk_exposure : Dict[str, float]
            当前风险暴露
        timestamp : pd.Timestamp, optional
            时间戳
        """
        if timestamp is None:
            timestamp = pd.Timestamp.now()
        
        self.exposure_history.append({
            'timestamp': timestamp,
            'exposure': risk_exposure.copy()
        })
        
        # 保持历史记录在合理范围内
        max_history_size = 1000
        if len(self.exposure_history) > max_history_size:
            self.exposure_history = self.exposure_history[-max_history_size:]
        
        if self.verbose:
            logger.info(f"风险暴露历史记录已更新，当前记录数: {len(self.exposure_history)}")
    
    def get_exposure_statistics(self) -> Dict[str, Any]:
        """
        获取风险暴露统计信息
        
        Returns
        -------
        Dict[str, Any]
            风险暴露统计信息
        """
        if not self.exposure_history:
            return {}
        
        # 收集所有因子的历史数据
        all_factors = set()
        for record in self.exposure_history:
            all_factors.update(record['exposure'].keys())
        
        # 计算每个因子的统计信息
        statistics = {
            'record_count': len(self.exposure_history),
            'factor_statistics': {}
        }
        
        for factor in all_factors:
            factor_values = [
                record['exposure'].get(factor, 0) 
                for record in self.exposure_history
            ]
            
            factor_stats = {
                'mean': np.mean(factor_values),
                'std': np.std(factor_values),
                'min': np.min(factor_values),
                'max': np.max(factor_values),
                'median': np.median(factor_values),
                'current': factor_values[-1] if factor_values else 0
            }
            
            # 检查是否有限制
            if factor in self.factor_limits:
                factor_stats['limit'] = self.factor_limits[factor]
                factor_stats['exceeds_limit'] = (
                    abs(factor_stats['current']) > abs(factor_stats['limit'])
                )
            
            statistics['factor_statistics'][factor] = factor_stats
        
        return statistics
    
    def get_risk_budget_utilization(
        self,
        risk_exposure: Dict[str, float]
    ) -> Dict[str, float]:
        """
        计算风险预算利用率
        
        Parameters
        ----------
        risk_exposure : Dict[str, float]
            当前风险暴露
            
        Returns
        -------
        Dict[str, float]
            各因子的风险预算利用率
        """
        utilization = {}
        
        for factor, limit in self.factor_limits.items():
            exposure = abs(risk_exposure.get(factor, 0))
            limit_abs = abs(limit)
            
            if limit_abs > 0:
                utilization_ratio = exposure / limit_abs
                utilization[factor] = utilization_ratio
                
                if utilization_ratio > 1.0 and self.verbose:
                    logger.warning(
                        f"因子{factor}风险预算利用率{utilization_ratio:.2%}超过100%"
                    )
            else:
                utilization[factor] = 0.0
        
        return utilization