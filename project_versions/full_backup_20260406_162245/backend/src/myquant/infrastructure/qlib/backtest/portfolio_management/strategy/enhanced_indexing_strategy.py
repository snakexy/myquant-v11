"""
QLib增强指数策略实现

该模块实现了与QLib官方完全兼容的增强指数策略，包括：
- 增强指数投资组合管理
- 风险模型数据加载
- 跟踪误差控制
- 基准偏差管理
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any

from .weight_strategy_base import WeightStrategyBase
from .optimizer.enhanced_indexing_optimizer import EnhancedIndexingOptimizer


class EnhancedIndexingStrategy(WeightStrategyBase):
    """
    增强指数策略
    
    增强指数结合了主动管理和被动管理的艺术，
    目的是在控制风险暴露（即跟踪误差）的同时，
    在投资组合回报方面超越基准指数（例如标普500）。
    
    用户需要准备风险模型数据，格式如下：
    
    .. code-block:: text
    
        ├── /path/to/riskmodel
        ├──── 20210101
        ├────── factor_exp.{csv|pkl|h5}
        ├────── factor_cov.{csv|pkl|h5}
        ├────── specific_risk.{csv|pkl|h5}
        ├────── blacklist.{csv|pkl|h5}  # 可选
    
    风险模型数据可以从风险数据提供商获取。也可以使用
    `qlib.model.riskmodel.structured.StructuredCovEstimator`来准备这些数据。
    
    Parameters
    ----------
    riskmodel_root : str
        风险模型根目录路径
    market : str, default "csi500"
        基准市场
    turn_limit : float, optional
        换手率限制
    name_mapping : dict, optional
        替代文件名映射
    optimizer_kwargs : dict, optional
        优化器参数
    verbose : bool, default False
        是否输出详细日志
    """
    
    # 默认文件名
    FACTOR_EXP_NAME = "factor_exp.pkl"
    FACTOR_COV_NAME = "factor_cov.pkl"
    SPECIFIC_RISK_NAME = "specific_risk.pkl"
    BLACKLIST_NAME = "blacklist.pkl"
    
    def __init__(
        self,
        *,
        riskmodel_root: str,
        market: str = "csi500",
        turn_limit: Optional[float] = None,
        name_mapping: Optional[Dict[str, str]] = None,
        optimizer_kwargs: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
        **kwargs
    ):
        """
        初始化增强指数策略
        
        Parameters
        ----------
        riskmodel_root : str
            风险模型根目录路径
        market : str, default "csi500"
            基准市场
        turn_limit : float, optional
            换手率限制
        name_mapping : dict, optional
            替代文件名映射
        optimizer_kwargs : dict, optional
            优化器参数
        verbose : bool, default False
            是否输出详细日志
        """
        super().__init__(**kwargs)
        
        # 策略配置
        self.riskmodel_root = riskmodel_root
        self.market = market
        self.turn_limit = turn_limit
        self.verbose = verbose
        
        # 文件名映射
        name_mapping = name_mapping or {}
        self.factor_exp_path = name_mapping.get(
            "factor_exp", self.FACTOR_EXP_NAME
        )
        self.factor_cov_path = name_mapping.get(
            "factor_cov", self.FACTOR_COV_NAME
        )
        self.specific_risk_path = name_mapping.get(
            "specific_risk", self.SPECIFIC_RISK_NAME
        )
        self.blacklist_path = name_mapping.get(
            "blacklist", self.BLACKLIST_NAME
        )
        
        # 优化器配置
        optimizer_kwargs = optimizer_kwargs or {}
        if turn_limit is not None:
            optimizer_kwargs['delta'] = turn_limit
        
        self.optimizer = EnhancedIndexingOptimizer(
            verbose=verbose, **optimizer_kwargs
        )
        
        # 风险数据缓存
        self._riskdata_cache = {}
        
        # 日志配置
        if self.verbose:
            self._log_message("增强指数策略初始化完成")
            self._log_message(f"风险模型路径: {riskmodel_root}")
            self._log_message(f"基准市场: {market}")
            self._log_message(f"换手率限制: {turn_limit}")
    
    def generate_target_weight_position(
        self,
        score_series: pd.Series,
        current_position: Dict[str, float],
        trade_exchange: Any = None
    ) -> Optional[Dict[str, float]]:
        """
        生成目标权重位置
        
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
        Dict[str, float] or None
            目标权重字典，键为股票代码，值为权重
        """
        # 获取交易日期
        trade_date = self._get_trade_date()
        if trade_date is None:
            if self.verbose:
                self._log_message("无法获取交易日期，跳过优化")
            return None
        
        # 获取前一个交易日
        pre_date = self._get_previous_trading_date(trade_date)
        if pre_date is None:
            if self.verbose:
                self._log_message("无法获取前一个交易日，跳过优化")
            return None
        
        # 加载风险数据
        risk_data = self._load_risk_data(pre_date)
        if risk_data is None:
            if self.verbose:
                self._log_message(f"无法加载{pre_date:%Y-%m-%d}的风险数据，跳过优化")
            return None
        
        factor_exp, factor_cov, specific_risk, universe, blacklist = risk_data
        
        # 转换评分
        # 注意：对于缺少评分的股票，我们总是假设它们具有最低评分
        score = score_series.reindex(universe).fillna(
            score_series.min()
        ).values
        
        # 获取当前权重
        # 注意：如果股票不在universe中，其当前权重将为零
        cur_weight = self._get_current_weight_dict(current_position, universe)
        
        # 加载基准权重
        bench_weight = self._load_benchmark_weight(pre_date, universe)
        
        # 检查股票可交易性
        tradable = self._check_tradable_stocks(pre_date, universe)
        mask_force_hold = ~tradable  # 强制持有不可交易股票
        
        # 强制卖出掩码
        mask_force_sell = np.array(
            [stock in blacklist for stock in universe], dtype=bool
        )
        
        # 执行优化
        try:
            weight = self.optimizer(
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
            
            if self.verbose:
                self._log_message(f"交易日期: {trade_date:%Y-%m-%d}")
                self._log_message(f"持有股票数量: {len(target_weight_position)}")
                self._log_message(f"总持有权重: {weight.sum():.6f}")
            
            return target_weight_position
            
        except Exception as e:
            if self.verbose:
                self._log_message(f"优化失败: {e}")
            return None
    
    def _get_trade_date(self) -> Optional[pd.Timestamp]:
        """
        获取当前交易日期
        
        Returns
        -------
        pd.Timestamp or None
            交易日期
        """
        try:
            # 尝试从交易日历获取
            if hasattr(self, 'trade_calendar') and self.trade_calendar:
                trade_step = self.trade_calendar.get_trade_step()
                trade_start_time, _ = (
                    self.trade_calendar.get_step_time(trade_step)
                )
                return trade_start_time
        except Exception:
            pass
        
        # 如果无法获取，返回当前日期
        return pd.Timestamp.now().normalize()
    
    def _get_previous_trading_date(
        self, trade_date: pd.Timestamp
    ) -> Optional[pd.Timestamp]:
        """
        获取前一个交易日
        
        Parameters
        ----------
        trade_date : pd.Timestamp
            当前交易日期
            
        Returns
        -------
        pd.Timestamp or None
            前一个交易日
        """
        try:
            # 尝试从交易日历获取
            if hasattr(self, 'trade_calendar') and self.trade_calendar:
                pre_date = (
                    self.trade_calendar.previous_trading_date(trade_date)
                )
                return pre_date
        except Exception:
            pass
        
        # 如果无法获取，返回前一天
        return trade_date - pd.Timedelta(days=1)
    
    def _load_risk_data(self, date: pd.Timestamp) -> Optional[Tuple]:
        """
        加载风险数据
        
        Parameters
        ----------
        date : pd.Timestamp
            日期
            
        Returns
        -------
        Tuple or None
            (factor_exp, factor_cov, specific_risk, universe, blacklist)
        """
        # 检查缓存
        if date in self._riskdata_cache:
            return self._riskdata_cache[date]
        
        # 构建风险数据路径
        date_str = date.strftime("%Y%m%d")
        risk_dir = os.path.join(self.riskmodel_root, date_str)
        
        if not os.path.exists(risk_dir):
            return None
        
        try:
            # 加载风险数据文件
            factor_exp_path = os.path.join(risk_dir, self.factor_exp_path)
            factor_cov_path = os.path.join(risk_dir, self.factor_cov_path)
            specific_risk_path = os.path.join(
                risk_dir, self.specific_risk_path
            )
            
            # 使用pandas加载数据
            factor_exp = self._load_data_file(factor_exp_path)
            factor_cov = self._load_data_file(factor_cov_path)
            specific_risk = self._load_data_file(specific_risk_path)
            
            if any(x is None for x in [factor_exp, factor_cov, specific_risk]):
                return None
            
            # 获取股票池
            universe = factor_exp.index.tolist()
            
            # 加载黑名单
            blacklist_path = os.path.join(risk_dir, self.blacklist_path)
            blacklist = []
            if os.path.exists(blacklist_path):
                blacklist_data = self._load_data_file(blacklist_path)
                if blacklist_data is not None:
                    blacklist = blacklist_data.index.tolist()
            
            # 检查索引一致性
            if not factor_exp.index.equals(specific_risk.index):
                # 注意：对于缺少specific_risk的股票，我们总是假设它们具有最高波动率
                specific_risk = specific_risk.reindex(
                    factor_exp.index, 
                    fill_value=specific_risk.max()
                )
            
            # 缓存结果
            risk_data = (
                factor_exp.values, 
                factor_cov.values, 
                specific_risk.values, 
                universe, 
                blacklist
            )
            self._riskdata_cache[date] = risk_data
            
            return risk_data
            
        except Exception as e:
            if self.verbose:
                self._log_message(f"加载风险数据失败: {e}")
            return None
    
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
                return None
        except Exception:
            return None
    
    def _get_current_weight_dict(
        self, 
        current_position: Dict[str, float], 
        universe: List[str]
    ) -> np.ndarray:
        """
        获取当前权重字典
        
        Parameters
        ----------
        current_position : Dict[str, float]
            当前持仓
        universe : List[str]
            股票池
            
        Returns
        -------
        np.ndarray
            当前权重数组
        """
        # 获取风险暴露度
        risk_degree = self.get_risk_degree()
        
        # 构建当前权重字典
        cur_weight = {}
        for stock in universe:
            cur_weight[stock] = current_position.get(stock, 0)
        
        # 转换为numpy数组
        cur_weight_array = np.array([cur_weight[stock] for stock in universe])
        
        # 确保权重非负
        assert all(cur_weight_array >= 0), "当前权重有负值"
        
        # 归一化权重
        cur_weight_array = cur_weight_array / risk_degree
        
        # 检查总权重
        if cur_weight_array.sum() > 1 and self.verbose:
            self._log_message(
                f"之前总持仓超过风险暴露度 (当前: {cur_weight_array.sum()})"
            )
        
        return cur_weight_array
    
    def _load_benchmark_weight(
        self, 
        pre_date: pd.Timestamp, 
        universe: List[str]
    ) -> np.ndarray:
        """
        加载基准权重
        
        Parameters
        ----------
        pre_date : pd.Timestamp
            前一个交易日
        universe : List[str]
            股票池
            
        Returns
        -------
        np.ndarray
            基准权重数组
        """
        try:
            # 尝试从数据提供器获取基准权重
            if hasattr(self, 'trade_exchange') and self.trade_exchange:
                # 使用交易所获取基准权重
                bench_weight = self.trade_exchange.get_benchmark_weight(
                    market=self.market, 
                    start_time=pre_date, 
                    end_time=pre_date
                )
                
                if bench_weight is not None:
                    # 重新索引以匹配universe
                    bench_weight = bench_weight.reindex(
                        universe
                    ).fillna(0).values
                    return bench_weight
        except Exception:
            pass
        
        # 如果无法获取基准权重，使用等权重
        if self.verbose:
            self._log_message("无法获取基准权重，使用等权重")
        return np.ones(len(universe)) / len(universe)
    
    def _check_tradable_stocks(
        self, 
        pre_date: pd.Timestamp, 
        universe: List[str]
    ) -> np.ndarray:
        """
        检查股票可交易性
        
        Parameters
        ----------
        pre_date : pd.Timestamp
            前一个交易日
        universe : List[str]
            股票池
            
        Returns
        -------
        np.ndarray
            可交易性掩码
        """
        try:
            # 尝试从交易所获取成交量信息
            if hasattr(self, 'trade_exchange') and self.trade_exchange:
                volume_data = self.trade_exchange.get_volume(
                    instruments=universe,
                    start_time=pre_date,
                    end_time=pre_date
                )
                
                if volume_data is not None:
                    # 成交量大于0的股票可交易
                    tradable = volume_data > 0
                    return tradable.values
        except Exception:
            pass
        
        # 如果无法获取成交量信息，假设所有股票都可交易
        if self.verbose:
            self._log_message("无法获取成交量信息，假设所有股票都可交易")
        return np.ones(len(universe), dtype=bool)
    
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
            'strategy_type': 'EnhancedIndexingStrategy',
            'riskmodel_root': self.riskmodel_root,
            'market': self.market,
            'turn_limit': self.turn_limit,
            'optimizer_info': self.optimizer.get_optimizer_info(),
            'cache_size': len(self._riskdata_cache)
        })
        return info
    
    def reset(self) -> None:
        """重置策略状态"""
        super().reset()
        self._riskdata_cache.clear()
        
        if self.verbose:
            self._log_message("增强指数策略状态已重置")


# 导出主要类
__all__ = [
    'EnhancedIndexingStrategy'
]