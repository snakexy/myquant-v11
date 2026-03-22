"""
风险数据加载器模块

提供增强指数策略所需的风险模型数据的加载功能
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class RiskDataLoader:
    """
    风险数据加载器
    
    负责加载和管理增强指数策略所需的风险模型数据，
    包括因子暴露、因子协方差和特定风险等。
    """
    
    def __init__(
        self,
        riskmodel_root: str,
        file_format: str = "pkl",
        cache_enabled: bool = True,
        verbose: bool = False
    ):
        """
        初始化风险数据加载器
        
        Parameters
        ----------
        riskmodel_root : str
            风险模型根目录路径
        file_format : str, default "pkl"
            文件格式 (csv, pkl, h5)
        cache_enabled : bool, default True
            是否启用缓存
        verbose : bool, default False
            是否输出详细日志
        """
        self.riskmodel_root = riskmodel_root
        self.file_format = file_format
        self.cache_enabled = cache_enabled
        self.verbose = verbose
        
        # 数据缓存
        self._data_cache = {}
        
        # 默认文件名
        self.default_filenames = {
            'factor_exp': f"factor_exp.{file_format}",
            'factor_cov': f"factor_cov.{file_format}",
            'specific_risk': f"specific_risk.{file_format}",
            'blacklist': f"blacklist.{file_format}"
        }
        
        if self.verbose:
            logger.info("风险数据加载器初始化完成")
            logger.info(f"风险模型路径: {riskmodel_root}")
            logger.info(f"文件格式: {file_format}")
            logger.info(f"缓存启用: {cache_enabled}")
    
    def load_risk_data(
        self,
        date: pd.Timestamp,
        file_mapping: Optional[Dict[str, str]] = None
    ) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], List[str]]]:
        """
        加载指定日期的风险数据
        
        Parameters
        ----------
        date : pd.Timestamp
            日期
        file_mapping : Dict[str, str], optional
            文件名映射
            
        Returns
        -------
        Tuple or None
            (factor_exp, factor_cov, specific_risk, universe, blacklist)
        """
        try:
            # 检查缓存
            cache_key = date.strftime("%Y%m%d")
            if self.cache_enabled and cache_key in self._data_cache:
                if self.verbose:
                    logger.info(f"从缓存加载{date:%Y-%m-%d}的风险数据")
                return self._data_cache[cache_key]
            
            # 构建文件路径
            file_paths = self._build_file_paths(date, file_mapping)
            
            # 加载各个文件
            factor_exp = self._load_data_file(file_paths['factor_exp'])
            factor_cov = self._load_data_file(file_paths['factor_cov'])
            specific_risk = self._load_data_file(file_paths['specific_risk'])
            blacklist_data = self._load_data_file(file_paths['blacklist'])
            
            # 检查必要数据是否存在
            if any(x is None for x in [factor_exp, factor_cov, specific_risk]):
                logger.error(f"必要风险数据文件缺失: {date:%Y-%m-%d}")
                return None
            
            # 获取股票池
            universe = factor_exp.index.tolist()
            
            # 处理黑名单
            blacklist = []
            if blacklist_data is not None:
                blacklist = blacklist_data.index.tolist()
            
            # 检查索引一致性
            if not factor_exp.index.equals(specific_risk.index):
                if self.verbose:
                    logger.warning("因子暴露和特定风险索引不一致，进行对齐")
                # 对齐索引
                specific_risk = specific_risk.reindex(
                    factor_exp.index, 
                    fill_value=specific_risk.max()
                )
            
            # 转换为numpy数组
            factor_exp_array = factor_exp.values
            factor_cov_array = factor_cov.values
            specific_risk_array = specific_risk.values
            
            # 验证数据一致性
            if not self._validate_risk_data(
                factor_exp_array, factor_cov_array, 
                specific_risk_array, universe
            ):
                return None
            
            # 缓存结果
            risk_data = (
                factor_exp_array, 
                factor_cov_array, 
                specific_risk_array, 
                universe, 
                blacklist
            )
            
            if self.cache_enabled:
                self._data_cache[cache_key] = risk_data
            
            if self.verbose:
                logger.info(f"成功加载{date:%Y-%m-%d}的风险数据")
                logger.info(f"股票池大小: {len(universe)}")
                logger.info(f"黑名单大小: {len(blacklist)}")
            
            return risk_data
            
        except Exception as e:
            logger.error(f"加载风险数据失败: {e}")
            return None
    
    def load_multiple_dates(
        self,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        file_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[pd.Timestamp, Tuple]:
        """
        加载多个日期的风险数据
        
        Parameters
        ----------
        start_date : pd.Timestamp
            开始日期
        end_date : pd.Timestamp
            结束日期
        file_mapping : Dict[str, str], optional
            文件名映射
            
        Returns
        -------
        Dict[pd.Timestamp, Tuple]
            日期到风险数据的映射
        """
        try:
            # 生成日期列表
            date_range = pd.date_range(start_date, end_date, freq='D')
            
            # 加载每个日期的数据
            risk_data_dict = {}
            for date in date_range:
                risk_data = self.load_risk_data(date, file_mapping)
                if risk_data is not None:
                    risk_data_dict[date] = risk_data
            
            if self.verbose:
                logger.info(
                    f"成功加载{len(risk_data_dict)}个日期的风险数据"
                )
            
            return risk_data_dict
            
        except Exception as e:
            logger.error(f"加载多日期风险数据失败: {e}")
            return {}
    
    def get_available_dates(
        self,
        start_date: Optional[pd.Timestamp] = None,
        end_date: Optional[pd.Timestamp] = None
    ) -> List[pd.Timestamp]:
        """
        获取可用的风险数据日期
        
        Parameters
        ----------
        start_date : pd.Timestamp, optional
            开始日期
        end_date : pd.Timestamp, optional
            结束日期
            
        Returns
        -------
        List[pd.Timestamp]
            可用日期列表
        """
        try:
            if not os.path.exists(self.riskmodel_root):
                logger.warning(f"风险模型目录不存在: {self.riskmodel_root}")
                return []
            
            # 获取所有子目录
            date_dirs = []
            for item in os.listdir(self.riskmodel_root):
                item_path = os.path.join(self.riskmodel_root, item)
                if os.path.isdir(item_path):
                    try:
                        # 尝试解析日期
                        date_str = item
                        date = pd.to_datetime(date_str, format='%Y%m%d')
                        date_dirs.append(date)
                    except ValueError:
                        continue
            
            # 排序日期
            date_dirs.sort()
            
            # 应用日期过滤
            if start_date is not None:
                date_dirs = [d for d in date_dirs if d >= start_date]
            if end_date is not None:
                date_dirs = [d for d in date_dirs if d <= end_date]
            
            if self.verbose:
                logger.info(f"找到{len(date_dirs)}个可用日期")
            
            return date_dirs
            
        except Exception as e:
            logger.error(f"获取可用日期失败: {e}")
            return []
    
    def clear_cache(self) -> None:
        """清空数据缓存"""
        self._data_cache.clear()
        if self.verbose:
            logger.info("风险数据缓存已清空")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns
        -------
        Dict[str, Any]
            缓存信息
        """
        return {
            'cache_enabled': self.cache_enabled,
            'cache_size': len(self._data_cache),
            'cached_dates': list(self._data_cache.keys())
        }
    
    def _build_file_paths(
        self,
        date: pd.Timestamp,
        file_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        构建文件路径
        
        Parameters
        ----------
        date : pd.Timestamp
            日期
        file_mapping : Dict[str, str], optional
            文件名映射
            
        Returns
        -------
        Dict[str, str]
            文件路径字典
        """
        # 构建日期目录路径
        date_str = date.strftime("%Y%m%d")
        date_dir = os.path.join(self.riskmodel_root, date_str)
        
        # 使用自定义映射或默认文件名
        filenames = file_mapping or self.default_filenames
        
        # 构建完整文件路径
        file_paths = {}
        for key, filename in filenames.items():
            file_paths[key] = os.path.join(date_dir, filename)
        
        return file_paths
    
    def _load_data_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        加载数据文件
        
        Parameters
        ----------
        file_path : str
            文件路径
            
        Returns
        -------
        pd.DataFrame or None
            加载的数据
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            # 根据文件扩展名选择加载方式
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path, index_col=0)
            elif file_path.endswith('.pkl'):
                return pd.read_pickle(file_path)
            elif file_path.endswith('.h5'):
                return pd.read_hdf(file_path, key='data')
            else:
                logger.warning(f"不支持的文件格式: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"加载文件失败{file_path}: {e}")
            return None
    
    def _validate_risk_data(
        self,
        factor_exp: np.ndarray,
        factor_cov: np.ndarray,
        specific_risk: np.ndarray,
        universe: List[str]
    ) -> bool:
        """
        验证风险数据的一致性
        
        Parameters
        ----------
        factor_exp : np.ndarray
            因子暴露矩阵
        factor_cov : np.ndarray
            因子协方差矩阵
        specific_risk : np.ndarray
            特定风险向量
        universe : List[str]
            股票池
            
        Returns
        -------
        bool
            数据是否有效
        """
        try:
            # 检查维度
            n_assets = len(universe)
            
            if factor_exp.shape[0] != n_assets:
                logger.error(f"因子暴露矩阵行数{factor_exp.shape[0]}与资产数{n_assets}不匹配")
                return False
            
            if factor_cov.shape[0] != factor_cov.shape[1]:
                logger.error(f"因子协方差矩阵不是方阵: {factor_cov.shape}")
                return False
            
            if factor_exp.shape[1] != factor_cov.shape[0]:
                logger.error(
                    f"因子暴露矩阵列数{factor_exp.shape[1]}与协方差矩阵维度{factor_cov.shape[0]}不匹配"
                )
                return False
            
            if len(specific_risk) != n_assets:
                logger.error(f"特定风险长度{len(specific_risk)}与资产数{n_assets}不匹配")
                return False
            
            # 检查数值有效性
            if np.any(np.isnan(factor_exp)):
                logger.error("因子暴露包含NaN值")
                return False
            
            if np.any(np.isnan(factor_cov)):
                logger.error("因子协方差包含NaN值")
                return False
            
            if np.any(np.isnan(specific_risk)):
                logger.error("特定风险包含NaN值")
                return False
            
            # 检查正定性
            try:
                np.linalg.cholesky(factor_cov)
            except np.linalg.LinAlgError:
                logger.error("因子协方差矩阵不是正定的")
                return False
            
            # 检查特定风险非负
            if np.any(specific_risk < 0):
                logger.error("特定风险包含负值")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证风险数据失败: {e}")
            return False