"""
基础优化器类

定义增强指数策略优化器的基础接口和通用功能
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseOptimizer:
    """
    基础优化器类
    
    定义了所有优化器应该实现的通用接口和基础功能。
    """
    
    def __init__(self, verbose: bool = False, **kwargs):
        """
        初始化基础优化器
        
        Parameters
        ----------
        verbose : bool, default False
            是否输出详细日志
        **kwargs : dict
            其他优化器参数
        """
        self.verbose = verbose
        self.optimizer_params = kwargs
        
        if self.verbose:
            logger.info("基础优化器初始化完成")
    
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
        执行优化
        
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
        raise NotImplementedError("子类必须实现__call__方法")
    
    def get_optimizer_info(self) -> Dict[str, Any]:
        """
        获取优化器信息
        
        Returns
        -------
        Dict[str, Any]
            优化器信息字典
        """
        info = {
            'optimizer_type': self.__class__.__name__,
            'verbose': self.verbose,
            'params': self.optimizer_params
        }
        return info
    
    def validate_inputs(
        self, 
        r: np.ndarray, 
        F: np.ndarray, 
        cov_b: np.ndarray, 
        var_u: np.ndarray,
        w0: np.ndarray, 
        wb: np.ndarray,
        mfh: np.ndarray, 
        mfs: np.ndarray
    ) -> bool:
        """
        验证输入参数
        
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
        bool
            输入是否有效
        """
        try:
            # 检查维度一致性
            n_assets = len(r)
            
            if F.shape[0] != n_assets:
                logger.error(f"因子暴露矩阵行数({F.shape[0]})与资产数({n_assets})不匹配")
                return False
            
            if len(w0) != n_assets:
                logger.error(f"初始权重长度({len(w0)})与资产数({n_assets})不匹配")
                return False
            
            if len(wb) != n_assets:
                logger.error(f"基准权重长度({len(wb)})与资产数({n_assets})不匹配")
                return False
            
            if len(var_u) != n_assets:
                logger.error(f"特定风险长度({len(var_u)})与资产数({n_assets})不匹配")
                return False
            
            if len(mfh) != n_assets:
                logger.error(f"强制持有掩码长度({len(mfh)})与资产数({n_assets})不匹配")
                return False
            
            if len(mfs) != n_assets:
                logger.error(f"强制卖出掩码长度({len(mfs)})与资产数({n_assets})不匹配")
                return False
            
            # 检查矩阵维度
            if cov_b.shape[0] != cov_b.shape[1]:
                logger.error(f"因子协方差矩阵不是方阵: {cov_b.shape}")
                return False
            
            if F.shape[1] != cov_b.shape[0]:
                logger.error(
                    f"因子暴露矩阵列数({F.shape[1]})与协方差矩阵维度({cov_b.shape[0]})不匹配"
                )
                return False
            
            # 检查权重和为1
            if not np.isclose(np.sum(wb), 1.0, atol=1e-6):
                logger.warning(f"基准权重和不为1: {np.sum(wb)}")
            
            if not np.isclose(np.sum(w0), 1.0, atol=1e-6):
                logger.warning(f"初始权重和不为1: {np.sum(w0)}")
            
            # 检查权重非负
            if np.any(w0 < 0):
                logger.error("初始权重包含负值")
                return False
            
            if np.any(wb < 0):
                logger.error("基准权重包含负值")
                return False
            
            # 检查特定风险非负
            if np.any(var_u < 0):
                logger.error("特定风险包含负值")
                return False
            
            # 检查协方差矩阵正定
            try:
                np.linalg.cholesky(cov_b)
            except np.linalg.LinAlgError:
                logger.error("因子协方差矩阵不是正定的")
                return False
            
            if self.verbose:
                logger.info("输入参数验证通过")
            
            return True
            
        except Exception as e:
            logger.error(f"输入参数验证失败: {e}")
            return False
    
    def preprocess_inputs(
        self, 
        r: np.ndarray, 
        F: np.ndarray, 
        cov_b: np.ndarray, 
        var_u: np.ndarray,
        w0: np.ndarray, 
        wb: np.ndarray,
        mfh: np.ndarray, 
        mfs: np.ndarray
    ) -> tuple:
        """
        预处理输入参数
        
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
        tuple
            预处理后的参数元组
        """
        try:
            # 确保numpy数组
            r = np.asarray(r, dtype=np.float64)
            F = np.asarray(F, dtype=np.float64)
            cov_b = np.asarray(cov_b, dtype=np.float64)
            var_u = np.asarray(var_u, dtype=np.float64)
            w0 = np.asarray(w0, dtype=np.float64)
            wb = np.asarray(wb, dtype=np.float64)
            mfh = np.asarray(mfh, dtype=bool)
            mfs = np.asarray(mfs, dtype=bool)
            
            # 处理数值稳定性问题
            # 确保协方差矩阵正定
            min_eigval = np.min(np.linalg.eigvalsh(cov_b))
            if min_eigval <= 0:
                if self.verbose:
                    logger.warning(f"协方差矩阵最小特征值为{min_eigval}，添加正则化项")
                cov_b += np.eye(cov_b.shape[0]) * abs(min_eigval) * 1.01
            
            # 确保特定风险非负
            var_u = np.maximum(var_u, 1e-8)
            
            # 归一化权重
            w0 = w0 / np.sum(w0)
            wb = wb / np.sum(wb)
            
            if self.verbose:
                logger.info("输入参数预处理完成")
            
            return r, F, cov_b, var_u, w0, wb, mfh, mfs
            
        except Exception as e:
            logger.error(f"输入参数预处理失败: {e}")
            raise