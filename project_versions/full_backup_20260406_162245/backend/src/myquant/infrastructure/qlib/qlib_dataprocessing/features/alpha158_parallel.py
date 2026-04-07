"""
Alpha158特征处理器 - 并行计算版（修复语法错误）

该模块实现了Alpha158特征的并行计算版本，利用多核CPU提升性能。
"""

from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

try:
    from qlib.data.dataset import DatasetH
    from qlib.data.dataset.processor import Processor
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False
    # 定义占位符类
    class Processor:
        def __init__(self, **kwargs):
            pass
    
    class DatasetH:
        pass


class Alpha158ParallelProcessor(Processor):
    """
    Alpha158特征处理器 - 并行计算版
    
    该类实现了完整的Alpha158特征计算，包括：
    - KBar特征（9个）
    - 价格特征（可配置）
    - 成交量特征（可配置）
    - 滚动窗口特征（145个）
    - 并行计算，充分利用多核CPU
    """
    
    def __init__(
        self,
        features: List[str] = None,
        start_time: str = None,
        end_time: str = None,
        n_jobs: int = None,
        **kwargs: Any
    ):
        """
        初始化Alpha158并行处理器
        
        Parameters
        ----------
        features : List[str], optional
            要计算的特征列表，默认为所有Alpha158特征
        start_time : str, optional
            数据开始时间
        end_time : str, optional
            数据结束时间
        n_jobs : int, optional
            并行作业数，默认为CPU核心数
        **kwargs : dict
            其他参数
        """
        # 如果QLib可用，使用QLib的Processor基类
        if QLIB_AVAILABLE:
            # 过滤掉QLib Processor不支持的参数
            filtered_kwargs = {
                k: v for k, v in kwargs.items() if k != 'verbose'
            }
            super().__init__(**filtered_kwargs)
        else:
            # 简单初始化，不调用父类
            pass
        
        self.features = features or self._get_default_alpha158_features()
        self.start_time = start_time
        self.end_time = end_time
        
        # 获取字段表达式和特征名称
        self.fields, self.feature_names = self._get_alpha158_feature_config()
        
        # 并行计算配置
        self.n_jobs = n_jobs or mp.cpu_count()
        self.feature_config = self._get_feature_config()
        self.feature_config.update(kwargs)
        
        # 缓存和优化
        self._feature_cache = {}
        self._enable_cache = kwargs.get('enable_cache', True)
        
        if self.feature_config.get('verbose', False):
            self._log_message(f"Alpha158并行处理器初始化完成，使用 {self.n_jobs} 个并行作业")
    
    def _get_default_alpha158_features(self) -> List[str]:
        """
        获取默认的Alpha158特征列表
        
        Returns
        -------
        List[str]
            Alpha158特征列表
        """
        # 根据QLib官方Alpha158DL实现构建完整特征列表
        fields, names = self._get_alpha158_feature_config()
        return names
    
    def _get_alpha158_feature_config(
        self,
        config={
            "kbar": {},
            "price": {
                "windows": [0],
                "feature": ["OPEN", "HIGH", "LOW", "VWAP"],
            },
            "volume": {
                "windows": [0],
            },
            "rolling": {},
        }
    ) -> Tuple[List[str], List[str]]:
        """
        根据QLib官方Alpha158DL实现创建特征配置
        
        Parameters
        ----------
        config : dict
            特征配置字典
            
        Returns
        -------
        Tuple[List[str], List[str]]
            字段表达式列表和特征名称列表
        """
        fields = []
        names = []
        
        # KBar特征 (9个)
        if "kbar" in config:
            kbar_fields = [
                "($close-$open)/$open",
                "($high-$low)/$open",
                "($close-$open)/($high-$low+1e-12)",
                "($high-Greater($open, $close))/$open",
                "($high-Greater($open, $close))/($high-$low+1e-12)",
                "(Less($open, $close)-$low)/$open",
                "(Less($open, $close)-$low)/($high-$low+1e-12)",
                "(2*$close-$high-$low)/$open",
                "(2*$close-$high-$low)/($high-$low+1e-12)",
            ]
            kbar_names = [
                "KMID", "KLEN", "KMID2", "KUP", "KUP2", 
                "KLOW", "KLOW2", "KSFT", "KSFT2"
            ]
            fields.extend(kbar_fields)
            names.extend(kbar_names)
        
        # 价格特征 (默认5个)
        if "price" in config:
            windows = config["price"].get("windows", [0])
            feature_list = config["price"].get(
                "feature", ["OPEN", "HIGH", "LOW", "CLOSE", "VWAP"]
            )
            for field in feature_list:
                field = field.lower()
                for d in windows:
                    if d != 0:
                        expr = f"Ref(${field}, {d})/$close"
                        name = f"{field.upper()}{d}"
                    else:
                        expr = f"${field}/$close"
                        name = f"{field.upper()}{d}"
                    fields.append(expr)
                    names.append(name)
        
        # 成交量特征 (默认1个)
        if "volume" in config:
            windows = config["volume"].get("windows", [0])
            for d in windows:
                if d != 0:
                    expr = f"Ref($volume, {d})/($volume+1e-12)"
                    name = f"VOLUME{d}"
                else:
                    expr = "$volume/($volume+1e-12)"
                    name = "VOLUME0"
                fields.append(expr)
                names.append(name)
        
        # 滚动窗口特征 (默认145个)
        if "rolling" in config:
            windows = config["rolling"].get("windows", [5, 10, 20, 30, 60])
            include = config["rolling"].get("include", None)
            exclude = config["rolling"].get("exclude", [])
            
            def use(x):
                return x not in exclude and (include is None or x in include)
            
            # 默认包含所有滚动特征
            if include is None:
                include = [
                    "ROC", "MA", "STD", "BETA", "RSQR", "RESI", "MAX", "LOW", 
                    "QTLU", "QTLD", "RANK", "RSV", "IMAX", "IMIN", "IMXD", 
                    "CORR", "CORD", "CNTP", "CNTN", "CNTD", "SUMP", "SUMN", "SUMD", 
                    "VMA", "VSTD", "WVMA", "VSUMP", "VSUMN", "VSUMD"
                ]
            
            # ROC特征 (5个)
            if use("ROC"):
                for d in windows:
                    fields.append(f"Ref($close, {d})/$close")
                    names.append(f"ROC{d}")
            
            # MA特征 (5个)
            if use("MA"):
                for d in windows:
                    fields.append(f"Mean($close, {d})/$close")
                    names.append(f"MA{d}")
            
            # STD特征 (5个)
            if use("STD"):
                for d in windows:
                    fields.append(f"Std($close, {d})/$close")
                    names.append(f"STD{d}")
            
            # BETA特征 (5个) - 简化为斜率
            if use("BETA"):
                for d in windows:
                    fields.append(f"Slope($close, {d})/$close")
                    names.append(f"BETA{d}")
            
            # RSQR特征 (5个) - 简化为相关系数平方
            if use("RSQR"):
                for d in windows:
                    fields.append(f"Corr($close, Ref($close,1), {d})")
                    names.append(f"RSQR{d}")
            
            # RESI特征 (5个) - 简化为残差
            if use("RESI"):
                for d in windows:
                    fields.append(f"Resi($close, {d})/$close")
                    names.append(f"RESI{d}")
            
            # MAX特征 (5个)
            if use("MAX"):
                for d in windows:
                    fields.append(f"Max($high, {d})/$close")
                    names.append(f"MAX{d}")
            
            # MIN特征 (5个)
            if use("LOW"):
                for d in windows:
                    fields.append(f"Min($low, {d})/$close")
                    names.append(f"MIN{d}")
            
            # QTLU特征 (5个) - 80%分位数
            if use("QTLU"):
                for d in windows:
                    fields.append(f"Quantile($close, {d}, 0.8)/$close")
                    names.append(f"QTLU{d}")
            
            # QTLD特征 (5个) - 20%分位数
            if use("QTLD"):
                for d in windows:
                    fields.append(f"Quantile($close, {d}, 0.2)/$close")
                    names.append(f"QTLD{d}")
            
            # RANK特征 (5个)
            if use("RANK"):
                for d in windows:
                    fields.append(f"Rank($close, {d})")
                    names.append(f"RANK{d}")
            
            # RSV特征 (5个)
            if use("RSV"):
                for d in windows:
                    expr = f"($close-Min($low, {d}))/"
                    expr += f"(Max($high, {d})-Min($low, {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"RSV{d}")
            
            # IMAX特征 (5个)
            if use("IMAX"):
                for d in windows:
                    fields.append(f"IdxMax($high, {d})/{d}")
                    names.append(f"IMAX{d}")
            
            # IMIN特征 (5个)
            if use("IMIN"):
                for d in windows:
                    fields.append(f"IdxMin($low, {d})/{d}")
                    names.append(f"IMIN{d}")
            
            # IMXD特征 (5个)
            if use("IMXD"):
                for d in windows:
                    expr = f"(IdxMax($high, {d})-IdxMin($low, {d}))/{d}"
                    fields.append(expr)
                    names.append(f"IMXD{d}")
            
            # CORR特征 (5个)
            if use("CORR"):
                for d in windows:
                    fields.append(f"Corr($close, Log($volume+1), {d})")
                    names.append(f"CORR{d}")
            
            # CORD特征 (5个)
            if use("CORD"):
                for d in windows:
                    expr = "Corr($close/Ref($close,1), "
                    expr += f"Log($volume/Ref($volume, 1)+1, {d})"
                    fields.append(expr)
                    names.append(f"CORD{d}")
            
            # CNTP特征 (5个)
            if use("CNTP"):
                for d in windows:
                    fields.append(f"Mean($close>Ref($close, 1), {d})")
                    names.append(f"CNTP{d}")
            
            # CNTN特征 (5个)
            if use("CNTN"):
                for d in windows:
                    fields.append(f"Mean($close<Ref($close, 1), {d})")
                    names.append(f"CNTN{d}")
            
            # CNTD特征 (5个)
            if use("CNTD"):
                for d in windows:
                    expr = f"Mean($close>Ref($close, 1), {d})-"
                    expr += f"Mean($close<Ref($close, 1), {d})"
                    fields.append(expr)
                    names.append(f"CNTD{d}")
            
            # SUMP特征 (5个)
            if use("SUMP"):
                for d in windows:
                    expr = f"Sum(Greater($close-Ref($close, 1), 0), {d})/"
                    expr += f"(Sum(Abs($close-Ref($close, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"SUMP{d}")
            
            # SUMN特征 (5个)
            if use("SUMN"):
                for d in windows:
                    expr = f"Sum(Greater(Ref($close, 1)-$close, 0), {d})/"
                    expr += f"(Sum(Abs($close-Ref($close, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"SUMN{d}")
            
            # SUMD特征 (5个)
            if use("SUMD"):
                for d in windows:
                    expr = f"(Sum(Greater($close-Ref($close, 1), 0), {d})-"
                    expr += f"Sum(Greater(Ref($close, 1)-$close, 0), {d}))/"
                    expr += f"(Sum(Abs($close-Ref($close, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"SUMD{d}")
            
            # VMA特征 (5个)
            if use("VMA"):
                for d in windows:
                    fields.append(f"Mean($volume, {d})/($volume+1e-12)")
                    names.append(f"VMA{d}")
            
            # VSTD特征 (5个)
            if use("VSTD"):
                for d in windows:
                    fields.append(f"Std($volume, {d})/($volume+1e-12)")
                    names.append(f"VSTD{d}")
            
            # WVMA特征 (5个)
            if use("WVMA"):
                for d in windows:
                    expr = f"Std(Abs($close/Ref($close, 1)-1)*$volume, {d})/"
                    expr += f"(Mean(Abs($close/Ref($close, 1)-1)*$volume, {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"WVMA{d}")
            
            # VSUMP特征 (5个)
            if use("VSUMP"):
                for d in windows:
                    expr = f"Sum(Greater($volume-Ref($volume, 1), 0), {d})/"
                    expr += f"(Sum(Abs($volume-Ref($volume, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"VSUMP{d}")
            
            # VSUMN特征 (5个)
            if use("VSUMN"):
                for d in windows:
                    expr = f"Sum(Greater(Ref($volume, 1)-$volume, 0), {d})/"
                    expr += f"(Sum(Abs($volume-Ref($volume, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"VSUMN{d}")
            
            # VSUMD特征 (5个)
            if use("VSUMD"):
                for d in windows:
                    expr = f"(Sum(Greater($volume-Ref($volume, 1), 0), {d})-"
                    expr += f"Sum(Greater(Ref($volume, 1)-$volume, 0), {d}))/"
                    expr += f"(Sum(Abs($volume-Ref($volume, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"VSUMD{d}")
        
        return fields, names
    
    def _get_feature_config(self) -> Dict[str, Any]:
        """
        获取特征计算配置
        
        Returns
        -------
        Dict[str, Any]
            默认配置字典
        """
        return {
            'kbar_features': True,
            'price_features': True,
            'volume_features': True,
            'rolling_features': True,
            'normalization': 'zscore',
            'fill_method': 'ffill',
            'drop_na': True,
            'verbose': False,
            'parallel': True,
            'n_jobs': self.n_jobs
        }
    
    def fit(self, data: pd.DataFrame) -> 'Alpha158ParallelProcessor':
        """
        拟合处理器
        
        Parameters
        ----------
        data : pd.DataFrame
            训练数据
            
        Returns
        -------
        Alpha158ParallelProcessor
            拟合后的处理器实例
        """
        if self.feature_config.get('verbose', False):
            self._log_message("开始拟合Alpha158并行处理器")
        
        # 保存训练数据的统计信息
        self._fit_stats = {}
        
        if self.feature_config.get('normalization') == 'zscore':
            # 计算每个特征的均值和标准差
            for feature in self.features:
                if feature in data.columns:
                    feature_data = data[feature].dropna()
                    if len(feature_data) > 0:
                        self._fit_stats[feature] = {
                            'mean': feature_data.mean(),
                            'std': feature_data.std()
                        }
        
        if self.feature_config.get('verbose', False):
            self._log_message(f"拟合完成，特征数量: {len(self.features)}")
        
        return self
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        转换数据（并行计算版）
        
        Parameters
        ----------
        data : pd.DataFrame
            原始数据
            
        Returns
        -------
        pd.DataFrame
            处理后的特征数据
        """
        if self.feature_config.get('verbose', False):
            self._log_message("开始Alpha158特征转换（并行计算版）")
        
        result_data = data.copy()
        
        # 计算Alpha158特征（并行）
        result_data = self._compute_alpha158_features_parallel(result_data)
        
        # 数据清理和标准化
        result_data = self._post_process_features(result_data)
        
        if self.feature_config.get('verbose', False):
            self._log_message(f"特征转换完成，输出形状: {result_data.shape}")
        
        return result_data
    
    def _compute_alpha158_features_parallel(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算Alpha158特征（并行版）
        
        Parameters
        ----------
        data : pd.DataFrame
            原始数据
            
        Returns
        -------
        pd.DataFrame
            包含Alpha158特征的数据
        """
        result = data.copy()
        
        # 按股票分组，以便并行计算
        if hasattr(data.index, 'levels') and len(data.index.levels) > 1:
            # 多索引（时间，股票）
            groups = data.groupby(level=1)
        else:
            # 单索引或包含instrument列
            if 'instrument' in data.columns:
                groups = data.groupby('instrument')
            else:
                # 如果没有分组信息，直接计算
                groups = [data]
        
        # 并行计算每组股票的特征
        with ProcessPoolExecutor(max_workers=self.n_jobs) as executor:
            futures = []
            
            for name, group in groups:
                future = executor.submit(
                    self._compute_single_stock_features, group
                )
                futures.append(future)
            
            # 收集结果
            group_results = []
            for future in as_completed(futures):
                group_results.append(future.result())
        
        # 合并所有结果
        if len(group_results) > 1:
            all_features = pd.concat(group_results, axis=0)
        else:
            all_features = group_results[0]
        
        # 合并到原始数据
        result = pd.concat([result, all_features], axis=1)
        
        return result
    
    def _compute_single_stock_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算单只股票的特征
        
        Parameters
        ----------
        data : pd.DataFrame
            单只股票的数据
            
        Returns
        -------
        pd.DataFrame
            包含该股票特征的数据
        """
        # 确保数据按时间排序
        if hasattr(data.index, 'levels') and len(data.index.levels) > 1:
            # 多索引情况，按时间排序
            data = data.sort_index(level=0)
        else:
            # 单索引情况
            if 'datetime' in data.columns:
                data = data.sort_values('datetime')
        
        # 收集所有特征计算结果
        feature_dfs = []
        
        # 计算KBar特征
        if self.feature_config.get('kbar_features', True):
            kbar_features = self._compute_kbar_features(data)
            feature_dfs.append(kbar_features)
        
        # 计算价格特征
        if self.feature_config.get('price_features', True):
            price_features = self._compute_price_features(data)
            feature_dfs.append(price_features)
        
        # 计算成交量特征
        if self.feature_config.get('volume_features', True):
            volume_features = self._compute_volume_features(data)
            feature_dfs.append(volume_features)
        
        # 计算滚动窗口特征
        if self.feature_config.get('rolling_features', True):
            rolling_features = self._compute_rolling_features(data)
            feature_dfs.append(rolling_features)
        
        # 批量合并所有特征，避免碎片化
        if feature_dfs:
            all_features = pd.concat(feature_dfs, axis=1)
            data = pd.concat([data, all_features], axis=1)
        
        return data
    
    def _compute_kbar_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算KBar特征
        
        Parameters
        ----------
        data : pd.DataFrame
            原始数据
            
        Returns
        -------
        pd.DataFrame
            包含KBar特征的数据
        """
        # 确保必要的列存在
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in data.columns:
                data[col] = np.nan
        
        # 批量计算KBar特征
        kbar_data = {
            'KMID': (data['close'] - data['open']) / data['open'],
            'KLEN': (data['high'] - data['low']) / data['open'],
            'KMID2': (data['close'] - data['open']) / 
                     (data['high'] - data['low'] + 1e-12),
            'KUP': (data['high'] - np.maximum(data['open'], data['close'])) / 
                   data['open'],
            'KUP2': (data['high'] - np.maximum(data['open'], data['close'])) / 
                    (data['high'] - data['low'] + 1e-12),
            'KLOW': (np.minimum(data['open'], data['close']) - data['low']) / 
                   data['open'],
            'KLOW2': (np.minimum(data['open'], data['close']) - data['low']) / 
                    (data['high'] - data['low'] + 1e-12),
            'KSFT': (2 * data['close'] - data['high'] - data['low']) / 
                   data['open'],
            'KSFT2': (2 * data['close'] - data['high'] - data['low']) / 
                    (data['high'] - data['low'] + 1e-12)
        }
        
        return pd.DataFrame(kbar_data, index=data.index)
    
    def _compute_price_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算价格特征
        
        Parameters
        ----------
        data : pd.DataFrame
            原始数据
            
        Returns
        -------
        pd.DataFrame
            包含价格特征的数据
        """
        # 确保必要的列存在
        required_cols = ['open', 'high', 'low', 'close', 'vwap']
        for col in required_cols:
            if col not in data.columns:
                data[col] = np.nan
        
        # 批量计算价格特征
        price_data = {}
        price_features = ['open', 'high', 'low', 'close', 'vwap']
        for feature in price_features:
            if feature in data.columns and 'close' in data.columns:
                col_name = feature.upper() + '0'
                price_data[col_name] = data[feature] / data['close']
        
        return pd.DataFrame(price_data, index=data.index)
    
    def _compute_volume_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算成交量特征
        
        Parameters
        ----------
        data : pd.DataFrame
            原始数据
            
        Returns
        -------
        pd.DataFrame
            包含成交量特征的数据
        """
        # 确保成交量列存在
        if 'volume' not in data.columns:
            data['volume'] = np.nan
        
        # 批量计算成交量特征
        volume_data = {
            'VOLUME0': data['volume'] / (data['volume'] + 1e-12)
        }
        
        return pd.DataFrame(volume_data, index=data.index)
    
    def _compute_rolling_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算滚动窗口特征（优化版）
        
        Parameters
        ----------
        data : pd.DataFrame
            原始数据
            
        Returns
        -------
        pd.DataFrame
            包含滚动窗口特征的数据
        """
        # 确保必要的列存在
        if 'close' not in data.columns:
            data['close'] = np.nan
        if 'volume' not in data.columns:
            data['volume'] = np.nan
        if 'high' not in data.columns:
            data['high'] = np.nan
        if 'low' not in data.columns:
            data['low'] = np.nan
        
        # 滚动窗口大小
        windows = [5, 10, 20, 30, 60]
        
        # 收集所有滚动特征计算结果
        rolling_features = {}
        
        # ROC特征 (5个)
        for d in windows:
            col_name = f'ROC{d}'
            rolling_features[col_name] = data['close'].shift(d) / data['close']
        
        # MA特征 (5个)
        for d in windows:
            col_name = f'MA{d}'
            rolling_features[col_name] = (
                data['close'].rolling(d).mean() / data['close']
            )
        
        # STD特征 (5个)
        for d in windows:
            col_name = f'STD{d}'
            rolling_features[col_name] = (
                data['close'].rolling(d).std() / data['close']
            )
        
        # BETA特征 (5个) - 简化为斜率
        for d in windows:
            col_name = f'BETA{d}'
            rolling_features[col_name] = (
                data['close'].diff().rolling(d).mean() / data['close']
            )
        
        # RSQR特征 (5个) - 简化为相关系数平方
        for d in windows:
            col_name = f'RSQR{d}'
            rolling_features[col_name] = (
                data['close'].rolling(d).corr(data['close'].shift(1))
            )
        
        # RESI特征 (5个) - 简化为残差
        for d in windows:
            col_name = f'RESI{d}'
            # 使用简单的线性回归残差
            rolling_mean = data['close'].rolling(d).mean()
            rolling_features[col_name] = data['close'] - rolling_mean
        
        # MAX特征 (5个)
        for d in windows:
            col_name = f'MAX{d}'
            rolling_features[col_name] = (
                data['high'].rolling(d).max() / data['close']
            )
        
        # MIN特征 (5个)
        for d in windows:
            col_name = f'MIN{d}'
            rolling_features[col_name] = (
                data['low'].rolling(d).min() / data['close']
            )
        
        # QTLU特征 (5个) - 80%分位数
        for d in windows:
            col_name = f'QTLU{d}'
            rolling_features[col_name] = (
                data['close'].rolling(d).quantile(0.8) / data['close']
            )
        
        # QTLD特征 (5个) - 20%分位数
        for d in windows:
            col_name = f'QTLD{d}'
            rolling_features[col_name] = (
                data['close'].rolling(d).quantile(0.2) / data['close']
            )
        
        # RANK特征 (5个)
        for d in windows:
            col_name = f'RANK{d}'
            rolling_features[col_name] = (
                data['close'].rolling(d).rank(pct=True)
            )
        
        # RSV特征 (5个)
        for d in windows:
            col_name = f'RSV{d}'
            high_max = data['high'].rolling(d).max()
            low_min = data['low'].rolling(d).min()
            rsv = (data['close'] - low_min) / (high_max - low_min + 1e-12)
            rolling_features[col_name] = rsv
        
        # IMAX特征 (5个) - 修复语法错误
        for d in windows:
            col_name = f'IMAX{d}'
            rolling_features[col_name] = data['high'].rolling(d).apply(
                lambda x: np.argmax(x) + 1
            ) / d
        
        # IMIN特征 (5个) - 修复语法错误
        for d in windows:
            col_name = f'IMIN{d}'
            rolling_features[col_name] = data['low'].rolling(d).apply(
                lambda x: np.argmin(x) + 1
            ) / d
        
        # IMXD特征 (5个)
        for d in windows:
            col_name = f'IMXD{d}'
            imax = data['high'].rolling(d).apply(lambda x: np.argmax(x) + 1)
            imin = data['low'].rolling(d).apply(lambda x: np.argmin(x) + 1)
            rolling_features[col_name] = (imax - imin) / d
        
        # CORR特征 (5个)
        for d in windows:
            col_name = f'CORR{d}'
            rolling_features[col_name] = (
                data['close'].rolling(d).corr(np.log(data['volume'] + 1))
            )
        
        # CORD特征 (5个)
        for d in windows:
            col_name = f'CORD{d}'
            price_ratio = data['close'] / data['close'].shift(1)
            vol_ratio = np.log(data['volume'] / data['volume'].shift(1) + 1)
            rolling_features[col_name] = price_ratio.rolling(d).corr(vol_ratio)
        
        # CNTP特征 (5个)
        for d in windows:
            col_name = f'CNTP{d}'
            rolling_features[col_name] = (
                (data['close'] > data['close'].shift(1)).rolling(d).mean()
            )
        
        # CNTN特征 (5个)
        for d in windows:
            col_name = f'CNTN{d}'
            rolling_features[col_name] = (
                (data['close'] < data['close'].shift(1)).rolling(d).mean()
            )
        
        # CNTD特征 (5个)
        for d in windows:
            col_name = f'CNTD{d}'
            cntp = (data['close'] > data['close'].shift(1)).rolling(d).mean()
            cntn = (data['close'] < data['close'].shift(1)).rolling(d).mean()
            rolling_features[col_name] = cntp - cntn
        
        # SUMP特征 (5个)
        for d in windows:
            col_name = f'SUMP{d}'
            pos_change = (data['close'] - data['close'].shift(1)).clip(lower=0)
            abs_change = abs(data['close'] - data['close'].shift(1))
            sump = pos_change.rolling(d).sum() / (abs_change.rolling(d).sum() + 1e-12)
            rolling_features[col_name] = sump
        
        # SUMN特征 (5个)
        for d in windows:
            col_name = f'SUMN{d}'
            neg_change = (data['close'].shift(1) - data['close']).clip(lower=0)
            abs_change = abs(data['close'] - data['close'].shift(1))
            sumn = neg_change.rolling(d).sum() / (abs_change.rolling(d).sum() + 1e-12)
            rolling_features[col_name] = sumn
        
        # SUMD特征 (5个)
        for d in windows:
            col_name = f'SUMD{d}'
            pos_change = (data['close'] - data['close'].shift(1)).clip(lower=0)
            neg_change = (data['close'].shift(1) - data['close']).clip(lower=0)
            abs_change = abs(data['close'] - data['close'].shift(1))
            sumd = (pos_change.rolling(d).sum() - neg_change.rolling(d).sum()) / \
                   (abs_change.rolling(d).sum() + 1e-12)
            rolling_features[col_name] = sumd
        
        # VMA特征 (5个)
        for d in windows:
            col_name = f'VMA{d}'
            vma = data['volume'].rolling(d).mean() / (data['volume'] + 1e-12)
            rolling_features[col_name] = vma
        
        # VSTD特征 (5个)
        for d in windows:
            col_name = f'VSTD{d}'
            vstd = data['volume'].rolling(d).std() / (data['volume'] + 1e-12)
            rolling_features[col_name] = vstd
        
        # WVMA特征 (5个)
        for d in windows:
            col_name = f'WVMA{d}'
            price_change = abs(data['close'] / data['close'].shift(1) - 1) * data['volume']
            wvma = price_change.rolling(d).std() / \
                   (price_change.rolling(d).mean() + 1e-12)
            rolling_features[col_name] = wvma
        
        # VSUMP特征 (5个)
        for d in windows:
            col_name = f'VSUMP{d}'
            vol_pos_change = (data['volume'] - data['volume'].shift(1)).clip(lower=0)
            vol_abs_change = abs(data['volume'] - data['volume'].shift(1))
            vsump = vol_pos_change.rolling(d).sum() / \
                    (vol_abs_change.rolling(d).sum() + 1e-12)
            rolling_features[col_name] = vsump
        
        # VSUMN特征 (5个)
        for d in windows:
            col_name = f'VSUMN{d}'
            vol_neg_change = (data['volume'].shift(1) - data['volume']).clip(lower=0)
            vol_abs_change = abs(data['volume'] - data['volume'].shift(1))
            vsumn = vol_neg_change.rolling(d).sum() / \
                    (vol_abs_change.rolling(d).sum() + 1e-12)
            rolling_features[col_name] = vsumn
        
        # VSUMD特征 (5个)
        for d in windows:
            col_name = f'VSUMD{d}'
            vol_pos_change = (data['volume'] - data['volume'].shift(1)).clip(lower=0)
            vol_neg_change = (data['volume'].shift(1) - data['volume']).clip(lower=0)
            vol_abs_change = abs(data['volume'] - data['volume'].shift(1))
            vsumd = (vol_pos_change.rolling(d).sum() - vol_neg_change.rolling(d).sum()) / \
                    (vol_abs_change.rolling(d).sum() + 1e-12)
            rolling_features[col_name] = vsumd
        
        return pd.DataFrame(rolling_features, index=data.index)
    
    def _post_process_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        后处理特征
        
        Parameters
        ----------
        data : pd.DataFrame
            原始特征数据
            
        Returns
        -------
        pd.DataFrame
            处理后的特征数据
        """
        result = data.copy()
        
        # 填充缺失值
        fill_method = self.feature_config.get('fill_method', 'ffill')
        if isinstance(result.index, pd.MultiIndex):
            # 多索引情况
            if fill_method == 'ffill':
                result = result.groupby(level=1).ffill()
            elif fill_method == 'bfill':
                result = result.groupby(level=1).bfill()
            elif fill_method == 'mean':
                result = result.groupby(level=1).transform(
                    lambda x: x.fillna(x.mean())
                )
        else:
            # 单索引情况
            if fill_method == 'ffill':
                result = result.ffill()
            elif fill_method == 'bfill':
                result = result.bfill()
            elif fill_method == 'mean':
                result = result.fillna(result.mean())
        
        # 标准化
        if self.feature_config.get('normalization') == 'zscore':
            result = self._normalize_features(result)
        
        # 删除缺失值
        if self.feature_config.get('drop_na', True):
            # 只删除全为NaN的行，而不是任何包含NaN的行
            result = result.dropna(how='all')
        
        return result
    
    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        标准化特征
        
        Parameters
        ----------
        data : pd.DataFrame
            原始数据
            
        Returns
        -------
        pd.DataFrame
            标准化后的数据
        """
        result = data.copy()
        
        if hasattr(self, '_fit_stats'):
            for feature, stats in self._fit_stats.items():
                if feature in result.columns and stats['std'] > 0:
                    result[feature] = (
                        result[feature] - stats['mean']
                    ) / stats['std']
        
        return result
    
    def _log_message(self, message: str) -> None:
        """
        记录日志消息
        
        Parameters
        ----------
        message : str
            日志消息
        """
        print(f"[Alpha158ParallelProcessor] {message}")
    
    def get_feature_info(self) -> Dict[str, Any]:
        """
        获取特征信息
        
        Returns
        -------
        Dict[str, Any]
            特征信息字典
        """
        return {
            'processor_type': 'Alpha158ParallelProcessor',
            'total_features': len(self.features),
            'feature_list': self.features,
            'field_expressions': self.fields,
            'config': self.feature_config,
            'fit_stats': getattr(self, '_fit_stats', {}),
            'qlib_compatible': QLIB_AVAILABLE,
            'parallel_enabled': True,
            'n_jobs': self.n_jobs
        }


# 便捷创建函数
def create_alpha158_parallel_processor(
    features: List[str] = None,
    start_time: str = None,
    end_time: str = None,
    n_jobs: int = None,
    **kwargs: Any
) -> Alpha158ParallelProcessor:
    """
    创建Alpha158ParallelProcessor实例的便捷函数
    
    Parameters
    ----------
    features : List[str], optional
        要计算的特征列表
    start_time : str, optional
        数据开始时间
    end_time : str, optional
        数据结束时间
    n_jobs : int, optional
        并行作业数
    **kwargs : dict
        其他参数
        
    Returns
    -------
    Alpha158ParallelProcessor
        Alpha158并行处理器实例
    """
    return Alpha158ParallelProcessor(
        features=features,
        start_time=start_time,
        end_time=end_time,
        n_jobs=n_jobs,
        **kwargs
    )


# 导出主要类和函数
__all__ = [
    'Alpha158ParallelProcessor',
    'create_alpha158_parallel_processor'
]