"""
验证工具模块

提供增强指数策略的各种验证功能
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class Validators:
    """
    验证工具类
    
    提供各种验证功能，确保输入数据的有效性和一致性。
    """
    
    @staticmethod
    def validate_portfolio_weights(weights: np.ndarray) -> Dict[str, Any]:
        """
        验证投资组合权重
        
        Parameters
        ----------
        weights : np.ndarray
            投资组合权重
            
        Returns
        -------
        Dict[str, Any]
            验证结果
        """
        try:
            result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查权重非负
            if np.any(weights < 0):
                result['is_valid'] = False
                result['errors'].append("权重包含负值")
            
            # 检查权重和
            weight_sum = np.sum(weights)
            if not np.isclose(weight_sum, 1.0, atol=1e-6):
                result['warnings'].append(f"权重和不为1: {weight_sum:.6f}")
            
            # 检查极端权重
            max_weight = np.max(weights)
            if max_weight > 0.5:
                result['warnings'].append(f"存在极端权重: {max_weight:.4f}")
            
            # 检查零权重数量
            zero_count = np.sum(weights < 1e-8)
            if zero_count > len(weights) * 0.8:
                result['warnings'].append(f"零权重数量过多: {zero_count}/{len(weights)}")
            
            return result
            
        except Exception as e:
            logger.error(f"验证投资组合权重失败: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    @staticmethod
    def validate_risk_data(
        factor_exposure: np.ndarray,
        factor_covariance: np.ndarray,
        specific_risk: np.ndarray
    ) -> Dict[str, Any]:
        """
        验证风险数据
        
        Parameters
        ----------
        factor_exposure : np.ndarray
            因子暴露矩阵
        factor_covariance : np.ndarray
            因子协方差矩阵
        specific_risk : np.ndarray
            特定风险向量
            
        Returns
        -------
        Dict[str, Any]
            验证结果
        """
        try:
            result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查维度一致性
            n_assets = factor_exposure.shape[0]
            
            if factor_covariance.shape[0] != factor_covariance.shape[1]:
                result['is_valid'] = False
                result['errors'].append("协方差矩阵不是方阵")
            
            if factor_exposure.shape[1] != factor_covariance.shape[0]:
                result['is_valid'] = False
                result['errors'].append("因子暴露矩阵与协方差矩阵维度不匹配")
            
            if len(specific_risk) != n_assets:
                result['is_valid'] = False
                result['errors'].append("特定风险向量长度与资产数不匹配")
            
            # 检查NaN值
            if np.any(np.isnan(factor_exposure)):
                result['is_valid'] = False
                result['errors'].append("因子暴露包含NaN值")
            
            if np.any(np.isnan(factor_covariance)):
                result['is_valid'] = False
                result['errors'].append("协方差矩阵包含NaN值")
            
            if np.any(np.isnan(specific_risk)):
                result['is_valid'] = False
                result['errors'].append("特定风险包含NaN值")
            
            # 检查负值
            if np.any(specific_risk < 0):
                result['is_valid'] = False
                result['errors'].append("特定风险包含负值")
            
            # 检查协方差矩阵正定性
            try:
                np.linalg.cholesky(factor_covariance)
            except np.linalg.LinAlgError:
                result['warnings'].append("协方差矩阵可能不是正定的")
            
            return result
            
        except Exception as e:
            logger.error(f"验证风险数据失败: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    @staticmethod
    def validate_benchmark_weights(
        weights: pd.Series,
        stock_universe: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        验证基准权重
        
        Parameters
        ----------
        weights : pd.Series
            基准权重
        stock_universe : List[str], optional
            股票池
            
        Returns
        -------
        Dict[str, Any]
            验证结果
        """
        try:
            result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查权重非负
            if np.any(weights.values < 0):
                result['is_valid'] = False
                result['errors'].append("基准权重包含负值")
            
            # 检查权重和
            weight_sum = weights.sum()
            if not np.isclose(weight_sum, 1.0, atol=1e-6):
                result['warnings'].append(f"基准权重和不为1: {weight_sum:.6f}")
            
            # 检查与股票池的一致性
            if stock_universe is not None:
                missing_stocks = set(stock_universe) - set(weights.index)
                if missing_stocks:
                    result['warnings'].append(f"基准权重缺少股票: {list(missing_stocks)}")
                
                extra_stocks = set(weights.index) - set(stock_universe)
                if extra_stocks:
                    result['warnings'].append(f"基准权重包含额外股票: {list(extra_stocks)}")
            
            return result
            
        except Exception as e:
            logger.error(f"验证基准权重失败: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    @staticmethod
    def validate_optimization_parameters(
        lambda_risk: float,
        lambda_return: float,
        delta: float,
        max_iterations: int,
        tolerance: float
    ) -> Dict[str, Any]:
        """
        验证优化参数
        
        Parameters
        ----------
        lambda_risk : float
            风险惩罚系数
        lambda_return : float
            收益系数
        delta : float
            换手率限制
        max_iterations : int
            最大迭代次数
        tolerance : float
            收敛容差
            
        Returns
        -------
        Dict[str, Any]
            验证结果
        """
        try:
            result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查系数范围
            if lambda_risk < 0 or lambda_risk > 1:
                result['warnings'].append(f"风险惩罚系数超出范围: {lambda_risk}")
            
            if lambda_return < 0 or lambda_return > 1:
                result['warnings'].append(f"收益系数超出范围: {lambda_return}")
            
            if not np.isclose(lambda_risk + lambda_return, 1.0, atol=1e-6):
                result['warnings'].append(f"系数和不为1: {lambda_risk + lambda_return:.6f}")
            
            # 检查换手率限制
            if delta < 0 or delta > 1:
                result['warnings'].append(f"换手率限制超出范围: {delta}")
            
            # 检查迭代次数
            if max_iterations < 10 or max_iterations > 10000:
                result['warnings'].append(f"最大迭代次数可能不合理: {max_iterations}")
            
            # 检查容差
            if tolerance <= 0 or tolerance > 1e-3:
                result['warnings'].append(f"收敛容差可能不合理: {tolerance}")
            
            return result
            
        except Exception as e:
            logger.error(f"验证优化参数失败: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    @staticmethod
    def validate_date_range(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp
    ) -> Dict[str, Any]:
        """
        验证日期范围
        
        Parameters
        ----------
        start_date : pd.Timestamp
            开始日期
        end_date : pd.Timestamp
            结束日期
            
        Returns
        -------
        Dict[str, Any]
            验证结果
        """
        try:
            result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查日期顺序
            if start_date >= end_date:
                result['is_valid'] = False
                result['errors'].append("开始日期不能晚于或等于结束日期")
            
            # 检查日期范围
            date_range_days = (end_date - start_date).days
            if date_range_days > 365 * 5:  # 超过5年
                result['warnings'].append(f"日期范围过大: {date_range_days}天")
            
            # 检查日期是否为未来
            current_date = pd.Timestamp.now().normalize()
            if end_date > current_date:
                result['warnings'].append("结束日期在未来")
            
            return result
            
        except Exception as e:
            logger.error(f"验证日期范围失败: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    @staticmethod
    def validate_sector_mapping(
        stock_sectors: Dict[str, str],
        stock_universe: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        验证行业映射
        
        Parameters
        ----------
        stock_sectors : Dict[str, str]
            股票到行业的映射
        stock_universe : List[str], optional
            股票池
            
        Returns
        -------
        Dict[str, Any]
            验证结果
        """
        try:
            result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查映射完整性
            if not stock_sectors:
                result['is_valid'] = False
                result['errors'].append("行业映射为空")
            
            # 检查与股票池的一致性
            if stock_universe is not None:
                mapped_stocks = set(stock_sectors.keys())
                universe_stocks = set(stock_universe)
                
                missing_stocks = universe_stocks - mapped_stocks
                if missing_stocks:
                    result['warnings'].append(f"股票池中股票未映射行业: {list(missing_stocks)}")
                
                extra_stocks = mapped_stocks - universe_stocks
                if extra_stocks:
                    result['warnings'].append(f"行业映射中包含额外股票: {list(extra_stocks)}")
            
            # 检查行业分布
            sector_counts = {}
            for sector in stock_sectors.values():
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            
            if len(sector_counts) < 3:
                result['warnings'].append(f"行业数量过少: {len(sector_counts)}")
            
            # 检查行业集中度
            total_stocks = len(stock_sectors)
            max_sector_ratio = max(sector_counts.values()) / total_stocks
            if max_sector_ratio > 0.6:
                result['warnings'].append(f"行业集中度过高: {max_sector_ratio:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"验证行业映射失败: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }