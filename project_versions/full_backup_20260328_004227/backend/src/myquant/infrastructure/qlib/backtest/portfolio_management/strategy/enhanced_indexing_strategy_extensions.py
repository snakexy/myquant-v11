"""
QLib增强指数策略扩展功能

该模块实现了增强指数策略的扩展功能，包括：
- 高级跟踪误差控制
- 风险暴露管理
- 行业暴露分析
- 优化算法集成
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any

from .enhanced_indexing_strategy import EnhancedIndexingStrategy


class EnhancedIndexingStrategyExtensions(EnhancedIndexingStrategy):
    """
    增强指数策略扩展类
    
    该类扩展了基础的增强指数策略，添加了更高级的风险控制和分析功能。
    """
    
    def __init__(self, **kwargs):
        """
        初始化增强指数策略扩展
        
        Parameters
        ----------
        **kwargs : dict
            策略参数
        """
        super().__init__(**kwargs)
        
        # 扩展配置
        self.extended_config = {
            'max_tracking_error': 0.02,  # 最大跟踪误差（年化）
            'max_sector_deviation': 0.05,  # 最大行业偏差
            'enable_risk_monitoring': True,  # 启用风险监控
            'enable_sector_constraints': True,  # 启用行业约束
        }
        
        # 更新配置
        if 'extended_config' in kwargs:
            self.extended_config.update(kwargs['extended_config'])
    
    def calculate_tracking_error(
        self,
        portfolio_weights: Dict[str, float],
        benchmark_weights: Dict[str, float],
        factor_exp: np.ndarray,
        factor_cov: np.ndarray,
        specific_risk: np.ndarray
    ) -> float:
        """
        计算投资组合相对于基准的跟踪误差
        
        Parameters
        ----------
        portfolio_weights : Dict[str, float]
            投资组合权重
        benchmark_weights : Dict[str, float]
            基准权重
        factor_exp : np.ndarray
            因子暴露矩阵
        factor_cov : np.ndarray
            因子协方差矩阵
        specific_risk : np.ndarray
            特异性风险
            
        Returns
        -------
        float
            跟踪误差（年化）
        """
        # 确保权重顺序一致
        universe = list(portfolio_weights.keys())
        w_port = np.array([portfolio_weights[stock] for stock in universe])
        w_bench = np.array([
            benchmark_weights.get(stock, 0) for stock in universe
        ])
        
        # 计算权重偏差
        weight_diff = w_port - w_bench
        
        # 计算因子暴露偏差
        factor_diff = weight_diff @ factor_exp
        
        # 计算跟踪误差方差
        factor_risk = factor_diff @ factor_cov @ factor_diff.T
        specific_risk_total = np.sum((weight_diff ** 2) * (specific_risk ** 2))
        
        # 年化跟踪误差（假设日频数据）
        tracking_error_var = factor_risk + specific_risk_total
        tracking_error = np.sqrt(tracking_error_var * 252)  # 年化
        
        return tracking_error
    
    def calculate_risk_exposure(
        self,
        portfolio_weights: Dict[str, float],
        factor_exp: np.ndarray,
        factor_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        计算投资组合的风险暴露
        
        Parameters
        ----------
        portfolio_weights : Dict[str, float]
            投资组合权重
        factor_exp : np.ndarray
            因子暴露矩阵
        factor_names : List[str], optional
            因子名称列表
            
        Returns
        -------
        Dict[str, float]
            因子风险暴露字典
        """
        # 转换权重为numpy数组
        universe = list(portfolio_weights.keys())
        weights = np.array([portfolio_weights[stock] for stock in universe])
        
        # 计算因子暴露
        risk_exposure = weights @ factor_exp
        
        # 构建结果字典
        if factor_names is None:
            factor_names = [f"factor_{i}" for i in range(len(risk_exposure))]
        
        exposure_dict = {
            factor_names[i]: risk_exposure[i] 
            for i in range(len(risk_exposure))
        }
        
        return exposure_dict
    
    def calculate_sector_exposure(
        self,
        portfolio_weights: Dict[str, float],
        sector_mapping: Dict[str, str]
    ) -> Dict[str, float]:
        """
        计算行业暴露
        
        Parameters
        ----------
        portfolio_weights : Dict[str, float]
            投资组合权重
        sector_mapping : Dict[str, str]
            股票到行业的映射
            
        Returns
        -------
        Dict[str, float]
            行业暴露字典
        """
        sector_exposure = {}
        
        for stock, weight in portfolio_weights.items():
            sector = sector_mapping.get(stock, "其他")
            sector_exposure[sector] = sector_exposure.get(sector, 0) + weight
        
        return sector_exposure
    
    def optimize_tracking_error(
        self,
        score_series: pd.Series,
        current_position: Dict[str, float],
        benchmark_weights: Dict[str, float],
        risk_data: Tuple,
        max_tracking_error: Optional[float] = None,
        max_sector_deviation: Optional[float] = None,
        sector_mapping: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, float]]:
        """
        优化投资组合以控制跟踪误差
        
        Parameters
        ----------
        score_series : pd.Series
            评分序列
        current_position : Dict[str, float]
            当前持仓
        benchmark_weights : Dict[str, float]
            基准权重
        risk_data : Tuple
            风险数据元组 (factor_exp, factor_cov, specific_risk, universe, blacklist)
        max_tracking_error : float, optional
            最大跟踪误差（年化）
        max_sector_deviation : float, optional
            最大行业偏差
        sector_mapping : Dict[str, str], optional
            股票到行业的映射
            
        Returns
        -------
        Dict[str, float] or None
            优化后的权重
        """
        # 使用默认参数
        if max_tracking_error is None:
            max_tracking_error = self.extended_config['max_tracking_error']
        if max_sector_deviation is None:
            max_sector_deviation = self.extended_config['max_sector_deviation']
        
        factor_exp, factor_cov, specific_risk, universe, blacklist = risk_data
        
        # 转换评分
        score = score_series.reindex(universe).fillna(
            score_series.min()
        ).values
        
        # 获取当前权重
        cur_weight = self._get_current_weight_dict(current_position, universe)
        
        # 转换基准权重
        bench_weight = np.array([
            benchmark_weights.get(stock, 0) for stock in universe
        ])
        
        # 检查股票可交易性
        trade_date = self._get_trade_date()
        if trade_date is None:
            trade_date = pd.Timestamp.now().normalize()
        pre_date = self._get_previous_trading_date(trade_date)
        if pre_date is None:
            pre_date = trade_date - pd.Timedelta(days=1)
        
        tradable = self._check_tradable_stocks(pre_date, universe)
        mask_force_hold = ~tradable
        mask_force_sell = np.array([
            stock in blacklist for stock in universe
        ], dtype=bool)
        
        # 使用增强的优化器进行跟踪误差控制
        try:
            # 设置优化器参数以控制跟踪误差
            optimizer_kwargs = {
                'lamb': 2.0,  # 增加风险厌恶参数
                'b_dev': max_tracking_error / np.sqrt(252),  # 转换为日频
                'delta': self.turn_limit if self.turn_limit else 0.2
            }
            
            # 创建临时优化器
            from .optimizer.enhanced_indexing_optimizer import (
                EnhancedIndexingOptimizer
            )
            temp_optimizer = EnhancedIndexingOptimizer(
                verbose=self.verbose, **optimizer_kwargs
            )
            
            # 执行优化
            weight = temp_optimizer(
                r=score,
                F=factor_exp,
                cov_b=factor_cov,
                var_u=specific_risk**2,
                w0=cur_weight,
                wb=bench_weight,
                mfh=mask_force_hold,
                mfs=mask_force_sell
            )
            
            # 构建目标权重位置
            target_weight_position = {
                stock: weight_val 
                for stock, weight_val in zip(universe, weight) 
                if weight_val > 0
            }
            
            # 验证跟踪误差
            if self.verbose:
                te = self.calculate_tracking_error(
                    target_weight_position, benchmark_weights,
                    factor_exp, factor_cov, specific_risk
                )
                self._log_message(f"优化后跟踪误差: {te:.4f}")
                
                # 计算行业暴露（如果提供了行业映射）
                if sector_mapping:
                    portfolio_sectors = self.calculate_sector_exposure(
                        target_weight_position, sector_mapping
                    )
                    benchmark_sectors = self.calculate_sector_exposure(
                        benchmark_weights, sector_mapping
                    )
                    
                    all_sectors = (
                        set(portfolio_sectors.keys()) | 
                        set(benchmark_sectors.keys())
                    )
                    for sector in all_sectors:
                        port_exp = portfolio_sectors.get(sector, 0)
                        bench_exp = benchmark_sectors.get(sector, 0)
                        deviation = port_exp - bench_exp
                        if abs(deviation) > max_sector_deviation:
                            msg = f"行业 {sector} 偏差过大: {deviation:.4f}"
                            self._log_message(msg)
            
            return target_weight_position
            
        except Exception as e:
            if self.verbose:
                self._log_message(f"跟踪误差优化失败: {e}")
            return None
    
    def get_risk_metrics(
        self,
        portfolio_weights: Dict[str, float],
        benchmark_weights: Dict[str, float],
        risk_data: Tuple,
        factor_names: Optional[List[str]] = None,
        sector_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        获取投资组合的风险指标
        
        Parameters
        ----------
        portfolio_weights : Dict[str, float]
            投资组合权重
        benchmark_weights : Dict[str, float]
            基准权重
        risk_data : Tuple
            风险数据元组
        factor_names : List[str], optional
            因子名称列表
        sector_mapping : Dict[str, str], optional
            股票到行业的映射
            
        Returns
        -------
        Dict[str, Any]
            风险指标字典
        """
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
        
        # 计算行业暴露（如果提供了行业映射）
        sector_exposure = None
        if sector_mapping:
            sector_exposure = self.calculate_sector_exposure(
                portfolio_weights, sector_mapping
            )
        
        # 计算主动权重
        all_stocks = (
            set(portfolio_weights.keys()) | 
            set(benchmark_weights.keys())
        )
        active_weights = {
            stock: portfolio_weights.get(stock, 0) - 
            benchmark_weights.get(stock, 0)
            for stock in all_stocks
        }
        
        # 计算主动风险
        active_risk = np.sqrt(sum(w**2 for w in active_weights.values()))
        
        # 计算主动股票数量
        active_count = len([
            w for w in active_weights.values() if abs(w) > 0.001
        ])
        
        return {
            'tracking_error': tracking_error,
            'risk_exposure': risk_exposure,
            'sector_exposure': sector_exposure,
            'active_weights': active_weights,
            'active_risk': active_risk,
            'portfolio_count': len(portfolio_weights),
            'active_count': active_count
        }


# 导出主要类
__all__ = [
    'EnhancedIndexingStrategyExtensions'
]