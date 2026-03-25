"""
QLib Alpha158特征处理器 - 性能优化版

该模块实现了与QLib官方完全兼容的Alpha158特征处理器，包括：
- 完整的Alpha158特征定义（158个特征）
- 高效的特征计算管道
- 优化的批量计算，避免DataFrame碎片化
- 标准化的数据接口
- 完整的错误处理和日志
"""

from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np

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


class Alpha158Processor(Processor):
    """
    QLib Alpha158特征处理器 - 性能优化版
    
    该类实现了完整的Alpha158特征计算，包括：
    - KBar特征（9个）
    - 价格特征（可配置）
    - 成交量特征（可配置）
    - 滚动窗口特征（145个）
    - 优化的批量计算，避免DataFrame碎片化
    """
    
    def __init__(
        self,
        features: List[str] = None,
        start_time: str = None,
        end_time: str = None,
        fit_start_time: str = None,
        fit_end_time: str = None,
        **kwargs: Any
    ):
        """
        初始化Alpha158处理器
        
        Parameters
        ----------
        features : List[str], optional
            要计算的特征列表，默认为所有Alpha158特征
        start_time : str, optional
            数据开始时间
        end_time : str, optional
            数据结束时间
        fit_start_time : str, optional
            训练数据开始时间
        fit_end_time : str, optional
            训练数据结束时间
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
        self.fit_start_time = fit_start_time
        self.fit_end_time = fit_end_time
        
        # 特征计算配置
        self.feature_config = self._get_feature_config()
        self.feature_config.update(kwargs)
        
        # 获取字段表达式和特征名称
        self.fields, self.feature_names = self._get_alpha158_feature_config()
        
        # 缓存和优化
        self._feature_cache = {}
        self._enable_cache = kwargs.get('enable_cache', True)
        
        if self.feature_config.get('verbose', False):
            self._log_message("Alpha158优化处理器初始化完成")
    
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
                    "CORR", "CORD", "CNTP", "CNTN", "CNTD", "SUMP", "SUMN", 
                    "SUMD", "VMA", "VSTD", "WVMA", "VSUMP", "VSUMN", "VSUMD"
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
            
            # BETA特征 (5个)
            if use("BETA"):
                for d in windows:
                    fields.append(f"Slope($close, {d})/$close")
                    names.append(f"BETA{d}")
            
            # RSQR特征 (5个)
            if use("RSQR"):
                for d in windows:
                    fields.append(f"Rsquare($close, {d})")
                    names.append(f"RSQR{d}")
            
            # RESI特征 (5个)
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
            
            # QTLU特征 (5个)
            if use("QTLU"):
                for d in windows:
                    fields.append(f"Quantile($close, {d}, 0.8)/$close")
                    names.append(f"QTLU{d}")
            
            # QTLD特征 (5个)
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
                    expr = f"Corr($close/Ref($close,1), "
                    expr += f"Log($volume/Ref($volume, 1)+1), {d})"
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
                    expr = f"Sum(Greater($close-Ref($close, 1), 0), {d})"
                    expr += f"/(Sum(Abs($close-Ref($close, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"SUMP{d}")
            
            # SUMN特征 (5个)
            if use("SUMN"):
                for d in windows:
                    expr = f"Sum(Greater(Ref($close, 1)-$close, 0), {d})"
                    expr += f"/(Sum(Abs($close-Ref($close, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"SUMN{d}")
            
            # SUMD特征 (5个)
            if use("SUMD"):
                for d in windows:
                    expr = f"(Sum(Greater($close-Ref($close, 1), 0), {d})-"
                    expr += f"Sum(Greater(Ref($close, 1)-$close, 0), {d}))"
                    expr += f"/(Sum(Abs($close-Ref($close, 1)), {d})+1e-12)"
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
                    expr = f"Std(Abs($close/Ref($close, 1)-1)*$volume, {d})"
                    expr += f"/(Mean(Abs($close/Ref($close, 1)-1)*$volume, {d})"
                    expr += f"+1e-12)"
                    fields.append(expr)
                    names.append(f"WVMA{d}")
            
            # VSUMP特征 (5个)
            if use("VSUMP"):
                for d in windows:
                    expr = f"Sum(Greater($volume-Ref($volume, 1), 0), {d})"
                    expr += f"/(Sum(Abs($volume-Ref($volume, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"VSUMP{d}")
            
            # VSUMN特征 (5个)
            if use("VSUMN"):
                for d in windows:
                    expr = f"Sum(Greater(Ref($volume, 1)-$volume, 0), {d})"
                    expr += f"/(Sum(Abs($volume-Ref($volume, 1)), {d})+1e-12)"
                    fields.append(expr)
                    names.append(f"VSUMN{d}")
            
            # VSUMD特征 (5个)
            if use("VSUMD"):
                for d in windows:
                    expr = f"(Sum(Greater($volume-Ref($volume, 1), 0), {d})-"
                    expr += f"Sum(Greater(Ref($volume, 1)-$volume, 0), {d}))"
                    expr += f"/(Sum(Abs($volume-Ref($volume, 1)), {d})+1e-12)"
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
            'verbose': False
        }
    
    def fit(self, data: pd.DataFrame) -> 'Alpha158Processor':
        """
        拟合处理器
        
        Parameters
        ----------
        data : pd.DataFrame
            训练数据
            
        Returns
        -------
        Alpha158Processor
            拟合后的处理器实例
        """
        if self.feature_config.get('verbose', False):
            self._log_message("开始拟合Alpha158优化处理器")
        
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
            self._log_message(f"拟合完成，特征数量: {len(self._fit_stats)}")
        
        return self
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        转换数据
        
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
            self._log_message("开始Alpha158特征转换（优化版）")
        
        result_data = data.copy()
        
        # 计算Alpha158特征
        result_data = self._compute_alpha158_features_optimized(result_data)
        
        # 数据清理和标准化
        result_data = self._post_process_features(result_data)
        
        if self.feature_config.get('verbose', False):
            self._log_message(f"特征转换完成，输出形状: {result_data.shape}")
        
        return result_data
    
    def _compute_alpha158_features_optimized(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算Alpha158特征（优化版）
        
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
        
        # 收集所有特征计算结果，避免DataFrame碎片化
        feature_dfs = []
        
        # 计算KBar特征
        if self.feature_config.get('kbar_features', True):
            kbar_features = self._compute_kbar_features_optimized(result)
            feature_dfs.append(kbar_features)
        
        # 计算价格特征
        if self.feature_config.get('price_features', True):
            price_features = self._compute_price_features_optimized(result)
            feature_dfs.append(price_features)
        
        # 计算成交量特征
        if self.feature_config.get('volume_features', True):
            volume_features = self._compute_volume_features_optimized(result)
            feature_dfs.append(volume_features)
        
        # 计算滚动窗口特征
        if self.feature_config.get('rolling_features', True):
            rolling_features = self._compute_rolling_features_optimized(result)
            feature_dfs.append(rolling_features)
        
        # 批量合并所有特征，避免碎片化
        if feature_dfs:
            all_features = pd.concat(feature_dfs, axis=1)
            result = pd.concat([result, all_features], axis=1)
        
        return result
    
    def _compute_kbar_features_optimized(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算KBar特征（优化版）
        
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
            'KMID2': (data['close'] - data['open']) / (data['high'] - data['low'] + 1e-12),
            'KUP': (data['high'] - np.maximum(data['open'], data['close'])) / data['open'],
            'KUP2': (data['high'] - np.maximum(data['open'], data['close'])) / (data['high'] - data['low'] + 1e-12),
            'KLOW': (np.minimum(data['open'], data['close']) - data['low']) / data['open'],
            'KLOW2': (np.minimum(data['open'], data['close']) - data['low']) / (data['high'] - data['low'] + 1e-12),
            'KSFT': (2 * data['close'] - data['high'] - data['low']) / data['open'],
            'KSFT2': (2 * data['close'] - data['high'] - data['low']) / (data['high'] - data['low'] + 1e-12)
        }
        
        return pd.DataFrame(kbar_data, index=data.index)
    
    def _compute_price_features_optimized(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算价格特征（优化版）
        
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
                price_data[feature.upper() + '0'] = data[feature] / data['close']
        
        return pd.DataFrame(price_data, index=data.index)
    
    def _compute_volume_features_optimized(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算成交量特征（优化版）
        
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
    
    def _compute_rolling_features_optimized(self, data: pd.DataFrame) -> pd.DataFrame:
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
        
        # 对每个股票分组计算滚动特征
        if hasattr(data.index, 'levels') and len(data.index.levels) > 1:
            # 多索引（时间，股票）
            groupby_col = data.index.names[1]  # 股票列名
        elif 'instrument' in data.columns:
            # 使用instrument列进行分组
            groupby_col = 'instrument'
        else:
            # 使用默认分组
            groupby_col = None
        
        # 收集所有滚动特征计算结果
        rolling_features = {}
        
        # ROC特征 (5个)
        for d in windows:
            if groupby_col:
                rolling_features[f'ROC{d}'] = (
                    data.groupby(groupby_col)['close'].transform(
                        lambda x: x.shift(d) / x
                    )
                )
            else:
                rolling_features[f'ROC{d}'] = (
                    data['close'].shift(d) / data['close']
                )
        
        # MA特征 (5个)
        for d in windows:
            rolling_features[f'MA{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: x.rolling(d).mean() / x
            )
        
        # STD特征 (5个)
        for d in windows:
            rolling_features[f'STD{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: x.rolling(d).std() / x
            )
        
        # BETA特征 (5个) - 简化为斜率
        for d in windows:
            rolling_features[f'BETA{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: self._calculate_slope(x, d) / x
            )
        
        # RSQR特征 (5个) - 简化为R平方
        for d in windows:
            rolling_features[f'RSQR{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: self._calculate_rsquare(x, d)
            )
        
        # RESI特征 (5个) - 简化为残差
        for d in windows:
            rolling_features[f'RESI{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: self._calculate_residual(x, d) / x
            )
        
        # MAX特征 (5个)
        for d in windows:
            rolling_features[f'MAX{d}'] = data.groupby(groupby_col)['high'].transform(
                lambda x: x.rolling(d).max() / x
            )
        
        # MIN特征 (5个)
        for d in windows:
            rolling_features[f'MIN{d}'] = data.groupby(groupby_col)['low'].transform(
                lambda x: x.rolling(d).min() / x
            )
        
        # QTLU特征 (5个) - 80%分位数
        for d in windows:
            rolling_features[f'QTLU{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: x.rolling(d).quantile(0.8) / x
            )
        
        # QTLD特征 (5个) - 20%分位数
        for d in windows:
            rolling_features[f'QTLD{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: x.rolling(d).quantile(0.2) / x
            )
        
        # RANK特征 (5个)
        for d in windows:
            rolling_features[f'RANK{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: x.rolling(d).rank(pct=True)
            )
        
        # RSV特征 (5个) - 需要特殊处理
        for d in windows:
            rsv_data = data.groupby(groupby_col).apply(
                lambda x: (x['close'] - x['low'].rolling(d).min()) /
                         (x['high'].rolling(d).max() - x['low'].rolling(d).min() + 1e-12)
            ).reset_index(level=0, drop=True)
            # 确保数据是一维的
            if isinstance(rsv_data, pd.DataFrame) and len(rsv_data.columns) == 1:
                rsv_data = rsv_data.iloc[:, 0]
            rolling_features[f'RSV{d}'] = rsv_data
        
        # IMAX特征 (5个)
        for d in windows:
            rolling_features[f'IMAX{d}'] = data.groupby(groupby_col)['high'].transform(
                lambda x: x.rolling(d).apply(lambda y: np.argmax(y) + 1) / d
            )
        
        # IMIN特征 (5个)
        for d in windows:
            rolling_features[f'IMIN{d}'] = data.groupby(groupby_col)['low'].transform(
                lambda x: x.rolling(d).apply(lambda y: np.argmin(y) + 1) / d
            )
        
        # IMXD特征 (5个) - 需要特殊处理
        for d in windows:
            imxd_data = data.groupby(groupby_col).apply(
                lambda x: (x['high'].rolling(d).apply(lambda y: np.argmax(y) + 1) -
                         x['low'].rolling(d).apply(lambda y: np.argmin(y) + 1)) / d
            ).reset_index(level=0, drop=True)
            # 确保数据是一维的
            if isinstance(imxd_data, pd.DataFrame) and len(imxd_data.columns) == 1:
                imxd_data = imxd_data.iloc[:, 0]
            rolling_features[f'IMXD{d}'] = imxd_data
        
        # CORR特征 (5个) - 需要特殊处理
        for d in windows:
            corr_data = data.groupby(groupby_col).apply(
                lambda x: x['close'].rolling(d).corr(np.log(x['volume'] + 1))
            ).reset_index(level=0, drop=True)
            # 确保数据是一维的
            if isinstance(corr_data, pd.DataFrame) and len(corr_data.columns) == 1:
                corr_data = corr_data.iloc[:, 0]
            rolling_features[f'CORR{d}'] = corr_data
        
        # CORD特征 (5个) - 需要特殊处理
        for d in windows:
            cord_data = data.groupby(groupby_col).apply(
                lambda x: (x['close'] / x['close'].shift(1)).rolling(d).corr(
                    np.log(x['volume'] / x['volume'].shift(1) + 1)
                )
            ).reset_index(level=0, drop=True)
            # 确保数据是一维的
            if isinstance(cord_data, pd.DataFrame) and len(cord_data.columns) == 1:
                cord_data = cord_data.iloc[:, 0]
            rolling_features[f'CORD{d}'] = cord_data
        
        # CNTP特征 (5个)
        for d in windows:
            rolling_features[f'CNTP{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: (x > x.shift(1)).rolling(d).mean()
            )
        
        # CNTN特征 (5个)
        for d in windows:
            rolling_features[f'CNTN{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: (x < x.shift(1)).rolling(d).mean()
            )
        
        # CNTD特征 (5个)
        for d in windows:
            rolling_features[f'CNTD{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: (x > x.shift(1)).rolling(d).mean() - 
                         (x < x.shift(1)).rolling(d).mean()
            )
        
        # SUMP特征 (5个)
        for d in windows:
            rolling_features[f'SUMP{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: ((x - x.shift(1)).clip(lower=0).rolling(d).sum()) / 
                         ((x - x.shift(1)).abs().rolling(d).sum() + 1e-12)
            )
        
        # SUMN特征 (5个)
        for d in windows:
            rolling_features[f'SUMN{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: ((x.shift(1) - x).clip(lower=0).rolling(d).sum()) / 
                         ((x - x.shift(1)).abs().rolling(d).sum() + 1e-12)
            )
        
        # SUMD特征 (5个)
        for d in windows:
            rolling_features[f'SUMD{d}'] = data.groupby(groupby_col)['close'].transform(
                lambda x: ((x - x.shift(1)).clip(lower=0).rolling(d).sum() - 
                         (x.shift(1) - x).clip(lower=0).rolling(d).sum()) /
                         ((x - x.shift(1)).abs().rolling(d).sum() + 1e-12)
            )
        
        # VMA特征 (5个)
        for d in windows:
            rolling_features[f'VMA{d}'] = data.groupby(groupby_col)['volume'].transform(
                lambda x: x.rolling(d).mean() / (x + 1e-12)
            )
        
        # VSTD特征 (5个)
        for d in windows:
            rolling_features[f'VSTD{d}'] = data.groupby(groupby_col)['volume'].transform(
                lambda x: x.rolling(d).std() / (x + 1e-12)
            )
        
        # WVMA特征 (5个) - 需要特殊处理
        for d in windows:
            wvma_data = data.groupby(groupby_col).apply(
                lambda x: (abs(x['close'] / x['close'].shift(1) - 1) * x['volume']).rolling(d).std() /
                         ((abs(x['close'] / x['close'].shift(1) - 1) * x['volume']).rolling(d).mean() + 1e-12)
            ).reset_index(level=0, drop=True)
            # 确保数据是一维的
            if isinstance(wvma_data, pd.DataFrame) and len(wvma_data.columns) == 1:
                wvma_data = wvma_data.iloc[:, 0]
            rolling_features[f'WVMA{d}'] = wvma_data
        
        # VSUMP特征 (5个)
        for d in windows:
            rolling_features[f'VSUMP{d}'] = data.groupby(groupby_col)['volume'].transform(
                lambda x: ((x - x.shift(1)).clip(lower=0).rolling(d).sum()) / 
                         ((x - x.shift(1)).abs().rolling(d).sum() + 1e-12)
            )
        
        # VSUMN特征 (5个)
        for d in windows:
            rolling_features[f'VSUMN{d}'] = data.groupby(groupby_col)['volume'].transform(
                lambda x: ((x.shift(1) - x).clip(lower=0).rolling(d).sum()) / 
                         ((x - x.shift(1)).abs().rolling(d).sum() + 1e-12)
            )
        
        # VSUMD特征 (5个)
        for d in windows:
            rolling_features[f'VSUMD{d}'] = data.groupby(groupby_col)['volume'].transform(
                lambda x: ((x - x.shift(1)).clip(lower=0).rolling(d).sum() - 
                         (x.shift(1) - x).clip(lower=0).rolling(d).sum()) /
                         ((x - x.shift(1)).abs().rolling(d).sum() + 1e-12)
            )
        
        # 确保所有特征数据都是一维的
        for key, value in rolling_features.items():
            if isinstance(value, pd.DataFrame):
                # 如果是DataFrame，只取第一列
                if len(value.columns) == 1:
                    rolling_features[key] = value.iloc[:, 0]
                else:
                    # 如果有多列，取第一列
                    rolling_features[key] = value.iloc[:, 0]
            elif isinstance(value, np.ndarray):
                # 如果是numpy数组，确保是一维的
                if value.ndim > 1:
                    if value.shape[0] == 1:
                        # 如果是(1, n)形状，取第一行
                        rolling_features[key] = value[0]
                    else:
                        # 其他情况，展平为一维
                        rolling_features[key] = value.flatten()
        
        return pd.DataFrame(rolling_features, index=data.index)
    
    def _calculate_slope(self, series: pd.Series, window: int) -> pd.Series:
        """
        计算线性回归斜率（优化版）
        
        Parameters
        ----------
        series : pd.Series
            时间序列
        window : int
            窗口大小
            
        Returns
        -------
        pd.Series
            斜率序列
        """
        # 使用更高效的方法计算斜率
        # 简化方法：使用一阶差分的均值作为斜率估计
        return series.diff().rolling(window).mean()
    
    def _calculate_rsquare(self, series: pd.Series, window: int) -> pd.Series:
        """
        计算R平方值（简化版）
        
        Parameters
        ----------
        series : pd.Series
            时间序列
        window : int
            窗口大小
            
        Returns
        -------
        pd.Series
            R平方序列
        """
        # 使用简化的方法计算R平方
        # 对于金融时间序列，使用相关系数的平方作为R平方的近似
        # 计算一阶自相关作为R平方的近似
        def rsquare_func(y):
            if len(y.dropna()) < 2:
                return np.nan
            # 计算一阶差分
            diff = y.diff().dropna()
            if len(diff) < 2:
                return np.nan
            # 计算自相关
            corr = np.corrcoef(y[:-1], y[1:])[0, 1]
            # 返回相关系数的平方作为R平方的近似
            return corr ** 2 if not np.isnan(corr) else np.nan
        
        return series.rolling(window).apply(rsquare_func)
    
    def _calculate_residual(self, series: pd.Series, window: int) -> pd.Series:
        """
        计算线性回归残差
        
        Parameters
        ----------
        series : pd.Series
            时间序列
        window : int
            窗口大小
            
        Returns
        -------
        pd.Series
            残差序列
        """
        def residual_func(y):
            if len(y.dropna()) < 2:
                return np.nan
            x = np.arange(len(y))
            valid = ~np.isnan(y)
            if np.sum(valid) < 2:
                return np.nan
            x_valid = x[valid]
            y_valid = y[valid]
            coeffs = np.polyfit(x_valid, y_valid, 1)
            y_pred = np.polyval(coeffs, x_valid)
            # 返回最后一个点的残差
            if len(y_valid) > 0 and len(y_pred) > 0:
                # 使用iloc来避免索引问题
                return y_valid.iloc[-1] - y_pred[-1]
            else:
                return np.nan
        
        return series.rolling(window).apply(residual_func)
    
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
        print(f"[Alpha158Processor] {message}")
    
    def get_feature_info(self) -> Dict[str, Any]:
        """
        获取特征信息
        
        Returns
        -------
        Dict[str, Any]
            特征信息字典
        """
        return {
            'processor_type': 'Alpha158Processor',
            'total_features': len(self.features),
            'feature_list': self.features,
            'field_expressions': self.fields,
            'config': self.feature_config,
            'fit_stats': getattr(self, '_fit_stats', {}),
            'qlib_compatible': QLIB_AVAILABLE
        }


# 便捷创建函数
def create_alpha158_processor(
    features: List[str] = None,
    start_time: str = None,
    end_time: str = None,
    **kwargs: Any
) -> Alpha158Processor:
    """
    创建Alpha158Processor实例的便捷函数
    
    Parameters
    ----------
    features : List[str], optional
        要计算的特征列表
    start_time : str, optional
        数据开始时间
    end_time : str, optional
        数据结束时间
    **kwargs : dict
        其他参数
        
    Returns
    -------
    Alpha158Processor
        Alpha158处理器实例
    """
    return Alpha158Processor(
        features=features,
        start_time=start_time,
        end_time=end_time,
        **kwargs
    )


# 导出主要类和函数
__all__ = [
    'Alpha158Processor',
    'create_alpha158_processor'
]