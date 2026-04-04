"""
QLib增强指数优化器实现

该模块实现了与QLib官方完全兼容的增强指数优化器，包括：
- 投资组合优化算法
- 风险控制和跟踪误差管理
- 约束条件处理
- 多重优化策略
"""

import numpy as np
from typing import Union, Optional, Dict, Any, List

try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False
    print("警告: cvxpy未安装，增强指数优化器将使用简化实现")

from .base_optimizer import BaseOptimizer


class EnhancedIndexingOptimizer(BaseOptimizer):
    """
    增强指数投资组合优化器
    
    该优化器实现了增强指数投资的核心算法，旨在在控制跟踪误差的同时超越基准指数收益。
    
    优化问题:
        max_w  d @ r - lamb * (v @ cov_b @ v + var_u @ d**2)
        s.t.   w >= 0
               sum(w) == 1
               sum(|w - w0|) <= delta
               d >= -b_dev
               d <= b_dev
               v >= -f_dev
               v <= f_dev
    
    其中:
        w0: 当前持有权重
        wb: 基准权重
        r: 预期收益
        F: 因子暴露
        cov_b: 因子协方差
        var_u: 残差方差(对角线)
        lamb: 风险厌恶参数
        delta: 总换手率限制
        b_dev: 基准偏差限制
        f_dev: 因子偏差限制
        d = w - wb: 基准偏差
        v = d @ F: 因子偏差
    """
    
    def __init__(
        self,
        lamb: float = 1.0,
        delta: Optional[float] = 0.2,
        b_dev: Optional[float] = 0.01,
        f_dev: Optional[Union[List[float], np.ndarray]] = None,
        scale_return: bool = True,
        epsilon: float = 5e-5,
        solver_kwargs: Optional[Dict[str, Any]] = None,
        verbose: bool = False
    ):
        """
        初始化增强指数优化器
        
        Parameters
        ----------
        lamb : float, default 1.0
            风险厌恶参数(较大的lamb意味着更关注风险)
        delta : float, optional, default 0.2
            总换手率限制
        b_dev : float, optional, default 0.01
            基准偏差限制
        f_dev : list or np.ndarray, optional
            因子偏差限制
        scale_return : bool, default True
            是否缩放收益以匹配估计波动率
        epsilon : float, default 5e-5
            最小权重阈值
        solver_kwargs : dict, optional
            cvxpy求解器参数
        verbose : bool, default False
            是否输出详细日志
        """
        super().__init__()
        
        # 参数验证
        assert lamb >= 0, "风险厌恶参数lamb应该为正数"
        self.lamb = lamb
        
        assert delta is None or delta >= 0, "换手率限制delta应该为正数"
        self.delta = delta
        
        assert b_dev is None or b_dev >= 0, "基准偏差限制b_dev应该为正数"
        self.b_dev = b_dev
        
        if isinstance(f_dev, float):
            assert f_dev >= 0, "因子偏差限制f_dev应该为正数"
        elif f_dev is not None:
            f_dev = np.array(f_dev)
            assert all(f_dev >= 0), "因子偏差限制f_dev应该为正数"
        self.f_dev = f_dev
        
        self.scale_return = scale_return
        self.epsilon = epsilon
        self.solver_kwargs = solver_kwargs or {}
        self.verbose = verbose
        
        # 检查cvxpy可用性
        if not CVXPY_AVAILABLE:
            print("警告: cvxpy未安装，将使用简化的优化实现")
    
    def __call__(
        self,
        r: np.ndarray,
        F: np.ndarray,
        cov_b: np.ndarray,
        var_u: np.ndarray,
        w0: np.ndarray,
        wb: np.ndarray,
        mfh: Optional[np.ndarray] = None,
        mfs: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        执行投资组合优化
        
        Parameters
        ----------
        r : np.ndarray
            预期收益
        F : np.ndarray
            因子暴露矩阵
        cov_b : np.ndarray
            因子协方差矩阵
        var_u : np.ndarray
            残差方差(对角线)
        w0 : np.ndarray
            当前持有权重
        wb : np.ndarray
            基准权重
        mfh : np.ndarray, optional
            强制持有掩码
        mfs : np.ndarray, optional
            强制卖出掩码
            
        Returns
        -------
        np.ndarray
            优化后的投资组合权重
        """
        if not CVXPY_AVAILABLE:
            return self._simple_optimization(
                r, F, cov_b, var_u, w0, wb, mfh, mfs
            )
        
        # 缩放收益以匹配波动率
        if self.scale_return:
            r = self._scale_return(r, F, cov_b, var_u)
        
        # 目标权重变量
        w = cp.Variable(len(r), nonneg=True)
        w.value = wb  # 热启动
        
        # 预计算暴露
        d = w - wb  # 基准暴露
        v = d @ F  # 因子暴露
        
        # 目标函数
        ret = d @ r  # 超额收益
        risk = cp.quad_form(v, cov_b) + var_u @ (d**2)  # 跟踪误差
        obj = cp.Maximize(ret - self.lamb * risk)
        
        # 权重边界
        lb = np.zeros_like(wb)
        ub = np.ones_like(wb)
        
        # 基准边界
        if self.b_dev is not None:
            lb = np.maximum(lb, wb - self.b_dev)
            ub = np.minimum(ub, wb + self.b_dev)
        
        # 强制持有
        if mfh is not None:
            lb[mfh] = w0[mfh]
            ub[mfh] = w0[mfh]
        
        # 强制卖出(覆盖强制持有)
        if mfs is not None:
            lb[mfs] = 0
            ub[mfs] = 0
        
        # 约束条件
        constraints = [cp.sum(w) == 1, w >= lb, w <= ub]
        
        # 因子偏差约束
        if self.f_dev is not None:
            constraints.extend([v >= -self.f_dev, v <= self.f_dev])
        
        # 换手率约束
        turnover_constraints = []
        if self.delta is not None:
            if w0 is not None and w0.sum() > 0:
                turnover_constraints.extend([cp.norm(w - w0, 1) <= self.delta])
        
        # 优化求解
        success = False
        prob = None
        
        # 尝试1: 使用所有约束
        try:
            prob = cp.Problem(obj, constraints + turnover_constraints)
            prob.solve(solver=cp.ECOS, warm_start=True, **self.solver_kwargs)
            assert prob.status == "optimal"
            success = True
            if self.verbose:
                print("优化成功(使用所有约束)")
        except Exception as e:
            if self.verbose:
                print(f"尝试1失败: {e} (状态: {prob.status if prob else 'unknown'})")
        
        # 尝试2: 移除换手率约束
        if not success and len(turnover_constraints):
            if self.verbose:
                print("尝试移除换手率约束")
            try:
                w.value = wb
                prob = cp.Problem(obj, constraints)
                prob.solve(
                    solver=cp.ECOS, warm_start=True, **self.solver_kwargs
                )
                assert prob.status in ["optimal", "optimal_inaccurate"]
                success = True
                if self.verbose:
                    print("优化成功(移除换手率约束)")
            except Exception as e:
                if self.verbose:
                    prob_status = prob.status if prob else 'unknown'
                    status_msg = f"尝试2失败: {e} (状态: {prob_status})"
                    print(status_msg)
        
        # 返回当前权重如果优化失败
        if not success:
            if self.verbose:
                print("优化失败，返回当前持有权重")
            return w0
        
        if prob.status == "optimal_inaccurate" and self.verbose:
            print("优化结果不准确")
        
        # 移除小权重
        w = np.asarray(w.value)
        w[w < self.epsilon] = 0
        w /= w.sum()
        
        return w
    
    def _scale_return(
        self, 
        r: np.ndarray, 
        F: np.ndarray, 
        cov_b: np.ndarray, 
        var_u: np.ndarray
    ) -> np.ndarray:
        """
        缩放收益以匹配波动率
        
        Parameters
        ----------
        r : np.ndarray
            原始收益
        F : np.ndarray
            因子暴露
        cov_b : np.ndarray
            因子协方差
        var_u : np.ndarray
            残差方差
            
        Returns
        -------
        np.ndarray
            缩放后的收益
        """
        # 标准化收益
        r = r / r.std()
        # 缩放以匹配估计波动率
        r *= np.sqrt(np.mean(np.diag(F @ cov_b @ F.T) + var_u))
        return r
    
    def _simple_optimization(
        self,
        r: np.ndarray,
        F: np.ndarray,
        cov_b: np.ndarray,
        var_u: np.ndarray,
        w0: np.ndarray,
        wb: np.ndarray,
        mfh: Optional[np.ndarray] = None,
        mfs: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        简化的优化实现(当cvxpy不可用时)
        
        Parameters
        ----------
        r : np.ndarray
            预期收益
        F : np.ndarray
            因子暴露矩阵
        cov_b : np.ndarray
            因子协方差矩阵
        var_u : np.ndarray
            残差方差
        w0 : np.ndarray
            当前持有权重
        wb : np.ndarray
            基准权重
        mfh : np.ndarray, optional
            强制持有掩码
        mfs : np.ndarray, optional
            强制卖出掩码
            
        Returns
        -------
        np.ndarray
            优化后的投资组合权重
        """
        if self.verbose:
            print("使用简化优化实现")
        
        # 创建权重掩码
        mask = np.ones_like(wb, dtype=bool)
        
        # 应用强制卖出掩码
        if mfs is not None:
            mask[mfs] = False
        
        # 应用强制持有掩码
        if mfh is not None:
            mask[mfh] = True
        
        # 简单的收益加权策略
        w = np.zeros_like(wb)
        
        # 对于可交易的股票，使用收益加权
        tradable_mask = mask & (wb > 0)  # 基准中的股票
        if tradable_mask.any():
            # 结合基准权重和预期收益
            tradable_scores = wb[tradable_mask] * (1 + r[tradable_mask])
            w[tradable_mask] = tradable_scores / tradable_scores.sum()
        
        # 对于新股票，使用纯收益加权
        new_mask = mask & (wb == 0) & (r > 0)  # 基准中没有但收益为正的股票
        if new_mask.any():
            new_scores = r[new_mask]
            # 分配一小部分权重给新股票
            new_weight = 0.1 * new_scores / new_scores.sum()
            w[new_mask] = new_weight
        
        # 重新归一化
        w = w / w.sum()
        
        # 应用基准偏差限制
        if self.b_dev is not None:
            max_dev = self.b_dev
            w = np.clip(w, wb - max_dev, wb + max_dev)
            w = w / w.sum()
        
        return w
    
    def get_optimizer_info(self) -> Dict[str, Any]:
        """
        获取优化器信息
        
        Returns
        -------
        Dict[str, Any]
            优化器配置信息
        """
        return {
            'type': 'EnhancedIndexingOptimizer',
            'lamb': self.lamb,
            'delta': self.delta,
            'b_dev': self.b_dev,
            'f_dev': self.f_dev,
            'scale_return': self.scale_return,
            'epsilon': self.epsilon,
            'cvxpy_available': CVXPY_AVAILABLE
        }


# 导出主要类
__all__ = [
    'EnhancedIndexingOptimizer'
]