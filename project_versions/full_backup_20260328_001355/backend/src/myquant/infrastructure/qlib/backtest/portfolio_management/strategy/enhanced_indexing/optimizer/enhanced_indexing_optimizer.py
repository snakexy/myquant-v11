"""
增强指数优化器实现

实现了专门用于增强指数策略的投资组合优化算法
"""

import numpy as np
import cvxpy as cp
from typing import Dict, Any, Optional
import logging

from .base_optimizer import BaseOptimizer

logger = logging.getLogger(__name__)


class EnhancedIndexingOptimizer(BaseOptimizer):
    """
    增强指数优化器
    
    实现了专门用于增强指数策略的投资组合优化算法，
    目标是在控制跟踪误差的同时最大化超额收益。
    """
    
    def __init__(
        self, 
        verbose: bool = False,
        delta: float = 0.2,
        lambda_risk: float = 0.5,
        lambda_return: float = 0.5,
        **kwargs
    ):
        """
        初始化增强指数优化器
        
        Parameters
        ----------
        verbose : bool, default False
            是否输出详细日志
        delta : float, default 0.2
            换手率限制
        lambda_risk : float, default 0.5
            风险惩罚系数
        lambda_return : float, default 0.5
            收益系数
        **kwargs : dict
            其他优化器参数
        """
        super().__init__(verbose=verbose, **kwargs)
        
        self.delta = delta
        self.lambda_risk = lambda_risk
        self.lambda_return = lambda_return
        
        if self.verbose:
            logger.info("增强指数优化器初始化完成")
            logger.info(f"换手率限制: {delta}")
            logger.info(f"风险惩罚系数: {lambda_risk}")
            logger.info(f"收益系数: {lambda_return}")
    
    def __call__(
        self, 
        r: np.ndarray, 
        F: np.ndarray, 
        cov_b: np.ndarray, 
        var_u: np.ndarray,
        w0: np.ndarray, 
        wb: np.ndarray,
        mfh: np.ndarray, 
        mfs: np.ndarray
    ) -> np.ndarray:
        """
        执行增强指数优化
        
        Parameters
        ----------
        r : np.ndarray
            股票预期收益
        F : np.ndarray
            因子暴露矩阵
        cov_b : np.ndarray
            因子协方差矩阵
        var_u : np.ndarray
            特定风险向量
        w0 : np.ndarray
            初始权重
        wb : np.ndarray
            基准权重
        mfh : np.ndarray
            强制持有掩码
        mfs : np.ndarray
            强制卖出掩码
            
        Returns
        -------
        np.ndarray
            优化后的权重
        """
        try:
            # 验证输入
            if not self.validate_inputs(r, F, cov_b, var_u, w0, wb, mfh, mfs):
                raise ValueError("输入参数验证失败")
            
            # 预处理输入
            r, F, cov_b, var_u, w0, wb, mfh, mfs = self.preprocess_inputs(
                r, F, cov_b, var_u, w0, wb, mfh, mfs
            )
            
            # 获取资产数量
            n_assets = len(r)
            
            # 定义优化变量
            w = cp.Variable(n_assets)
            
            # 计算主动权重
            w_active = w - wb
            
            # 计算风险
            factor_risk = cp.quad_form(w_active.T @ F.T, cov_b)
            specific_risk = cp.sum_squares(cp.multiply(w_active, np.sqrt(var_u)))
            total_risk = factor_risk + specific_risk
            
            # 计算预期收益
            expected_return = r @ w
            
            # 计算换手率
            turnover = cp.sum(cp.abs(w - w0)) / 2
            
            # 构建目标函数
            # 最大化收益，同时最小化风险和换手率
            objective = cp.Maximize(
                self.lambda_return * expected_return -
                self.lambda_risk * cp.sqrt(total_risk) -
                self.delta * turnover
            )
            
            # 添加约束条件
            constraints = [
                # 权重和为1
                cp.sum(w) == 1,
                # 权重非负
                w >= 0,
                # 强制持有约束
                w[mfh] >= w0[mfh],
                # 强制卖出约束
                w[mfs] == 0
            ]
            
            # 构建并求解优化问题
            problem = cp.Problem(objective, constraints)
            
            # 设置求解器参数
            problem.solve(
                solver=cp.ECOS,
                max_iters=1000,
                feastol=1e-9,
                reltol=1e-9,
                abstol=1e-9,
                verbose=self.verbose
            )
            
            # 检查求解状态
            if problem.status not in ["optimal", "optimal_inaccurate"]:
                logger.error(f"优化失败，状态: {problem.status}")
                # 返回初始权重作为后备
                return w0
            
            # 获取优化结果
            optimized_weights = w.value
            
            # 确保权重非负且和为1
            optimized_weights = np.maximum(optimized_weights, 0)
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            if self.verbose:
                logger.info(f"优化完成，状态: {problem.status}")
                logger.info(f"预期收益: {expected_return.value:.4f}")
                logger.info(f"风险: {np.sqrt(total_risk.value):.4f}")
                logger.info(f"换手率: {turnover.value:.4f}")
            
            return optimized_weights
            
        except Exception as e:
            logger.error(f"增强指数优化失败: {e}")
            # 返回初始权重作为后备
            return w0
    
    def get_optimizer_info(self) -> Dict[str, Any]:
        """
        获取优化器信息
        
        Returns
        -------
        Dict[str, Any]
            优化器信息字典
        """
        info = super().get_optimizer_info()
        info.update({
            'delta': self.delta,
            'lambda_risk': self.lambda_risk,
            'lambda_return': self.lambda_return,
            'solver': 'ECOS'
        })
        return info
    
    def _solve_with_alternative_method(
        self,
        r: np.ndarray, 
        F: np.ndarray, 
        cov_b: np.ndarray, 
        var_u: np.ndarray,
        w0: np.ndarray, 
        wb: np.ndarray,
        mfh: np.ndarray, 
        mfs: np.ndarray
    ) -> np.ndarray:
        """
        使用替代方法求解优化问题
        
        当主优化方法失败时，使用更简单的启发式方法
        
        Parameters
        ----------
        r : np.ndarray
            股票预期收益
        F : np.ndarray
            因子暴露矩阵
        cov_b : np.ndarray
            因子协方差矩阵
        var_u : np.ndarray
            特定风险向量
        w0 : np.ndarray
            初始权重
        wb : np.ndarray
            基准权重
        mfh : np.ndarray
            强制持有掩码
        mfs : np.ndarray
            强制卖出掩码
            
        Returns
        -------
        np.ndarray
            优化后的权重
        """
        try:
            n_assets = len(r)
            
            # 计算风险调整后的收益
            total_risk = np.diag(F @ cov_b @ F.T) + var_u
            risk_adjusted_return = r / np.sqrt(total_risk)
            
            # 应用强制约束
            risk_adjusted_return[mfs] = -np.inf  # 强制卖出
            risk_adjusted_return[mfh] = np.max(risk_adjusted_return)  # 强制持有
            
            # 简单的启发式分配
            # 基于风险调整后收益的排序
            sorted_indices = np.argsort(-risk_adjusted_return)
            
            # 初始化权重
            weights = np.zeros(n_assets)
            
            # 分配权重给前N只股票
            top_n = min(50, n_assets)  # 最多持有50只股票
            for i in range(top_n):
                idx = sorted_indices[i]
                weights[idx] = 1.0 / top_n
            
            # 应用换手率限制
            max_change = self.delta / 2
            weight_change = weights - w0
            weight_change = np.clip(weight_change, -max_change, max_change)
            weights = w0 + weight_change
            
            # 确保权重非负且和为1
            weights = np.maximum(weights, 0)
            weights = weights / np.sum(weights)
            
            if self.verbose:
                logger.info("使用替代方法完成优化")
            
            return weights
            
        except Exception as e:
            logger.error(f"替代优化方法失败: {e}")
            return w0