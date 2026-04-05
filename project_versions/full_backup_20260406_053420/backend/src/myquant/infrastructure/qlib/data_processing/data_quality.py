"""
数据质量控制模块
提供数据预处理、清洗和质量验证功能
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)

logger = logging.getLogger(__name__)

# 尝试导入高级数据处理库
try:
    from scipy.signal import medfilt
    SCIPY_AVAILABLE = True
    logger.info("✅ SciPy数据处理库导入成功")
except ImportError as e:
    SCIPY_AVAILABLE = False
    logger.warning(f"⚠️ SciPy不可用，将使用基础数据处理: {e}")

try:
    from sklearn.preprocessing import RobustScaler
    SKLEARN_AVAILABLE = True
    logger.info("✅ Scikit-learn数据预处理库导入成功")
except ImportError as e:
    SKLEARN_AVAILABLE = False
    logger.warning(f"⚠️ Scikit-learn不可用，将使用基础标准化: {e}")


class DataQualityController:
    """
    数据质量控制控制器
    
    提供数据预处理、清洗和质量验证功能
    """
    
    def __init__(self, config=None):
        """
        初始化数据质量控制器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.cache = {}
        self.cache_enabled = self.config.get('cache_enabled', True)
        
        # 数据质量控制参数
        self.outlier_method = self.config.get('outlier_method', 'iqr')
        self.missing_method = self.config.get('missing_method', 'interpolate')
        self.min_data_points = self.config.get('min_data_points', 20)
        
        logger.info("数据质量控制器初始化完成")
    
    def preprocess_data_advanced(
        self, 
        data: pd.DataFrame,
        instrument: str = None
    ) -> pd.DataFrame:
        """
        高级数据预处理
        
        Args:
            data: 原始数据
            instrument: 股票代码（用于日志）
            
        Returns:
            预处理后的数据
        """
        try:
            if data.empty:
                logger.warning(f"{instrument or 'Unknown'} 数据为空")
                return data
            
            result_data = data.copy()
            
            # 1. 数据类型优化
            result_data = self._optimize_data_types(result_data)
            
            # 2. 时间序列处理
            result_data = self._process_time_series(result_data)
            
            # 3. 缺失值处理
            result_data = self._handle_missing_values(result_data)
            
            # 4. 异常值检测和处理
            result_data = self._handle_outliers(result_data, instrument)
            
            # 5. 数据平滑
            result_data = self._smooth_data(result_data)
            
            # 6. 数据质量验证
            result_data = self._validate_data_quality(result_data, instrument)
            
            msg = f"{instrument or 'Unknown'} 数据预处理完成: {len(result_data)} 条记录"
            logger.debug(msg)
            return result_data
            
        except Exception as e:
            logger.error(f"{instrument or 'Unknown'} 数据预处理失败: {e}")
            return data
    
    def _optimize_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """优化数据类型"""
        # 确保数值列使用最优数据类型
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        
        for col in numeric_columns:
            if col in data.columns:
                # 转换为float32以节省内存
                data[col] = pd.to_numeric(
                    data[col], errors='coerce'
                ).astype('float32')
        
        return data
    
    def _process_time_series(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理时间序列"""
        # 确保日期索引
        if 'datetime' in data.columns:
            data['date'] = pd.to_datetime(data['datetime'])
            data.set_index('date', inplace=True)
        elif 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            data.set_index('date', inplace=True)
        elif not isinstance(data.index, pd.DatetimeIndex):
            # 如果索引不是日期类型，尝试重置索引
            if len(data.columns) > 0:
                data.index = pd.to_datetime(data.index)
        
        # 排序并去重
        if isinstance(data.index, pd.DatetimeIndex):
            data = data.sort_index()
            data = data[~data.index.duplicated(keep='first')]
        
        return data
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        
        for col in numeric_columns:
            if col in data.columns:
                if self.missing_method == 'interpolate':
                    # 时间序列插值
                    data[col] = data[col].interpolate(
                        method='time', limit_direction='both'
                    )
                elif self.missing_method == 'forward':
                    # 前向填充
                    data[col] = data[col].ffill()
                elif self.missing_method == 'backward':
                    # 后向填充
                    data[col] = data[col].bfill()
                else:
                    # 默认：前向+后向填充
                    data[col] = data[col].ffill().bfill()
        
        return data
    
    def _handle_outliers(
        self, 
        data: pd.DataFrame, 
        instrument: str = None
    ) -> pd.DataFrame:
        """处理异常值"""
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        
        for col in numeric_columns:
            if col not in data.columns:
                continue
            
            if self.outlier_method == 'iqr':
                data[col] = self._handle_outliers_iqr(data[col])
            elif self.outlier_method == 'zscore':
                data[col] = self._handle_outliers_zscore(data[col])
            elif self.outlier_method == 'isolation' and SCIPY_AVAILABLE:
                data[col] = self._handle_outliers_isolation(data[col])
            else:
                # 默认使用IQR方法
                data[col] = self._handle_outliers_iqr(data[col])
        
        return data
    
    def _handle_outliers_iqr(self, series: pd.Series) -> pd.Series:
        """使用IQR方法处理异常值"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 使用边界值替换异常值，而不是删除
        return series.clip(lower_bound, upper_bound)
    
    def _handle_outliers_zscore(self, series: pd.Series) -> pd.Series:
        """使用Z-Score方法处理异常值"""
        mean = series.mean()
        std = series.std()
        
        if std == 0:
            return series
        
        z_scores = np.abs((series - mean) / std)
        # 3σ原则
        outlier_mask = z_scores > 3
        
        # 使用中位数替换异常值
        median_value = series.median()
        result = series.copy()
        result[outlier_mask] = median_value
        
        return result
    
    def _handle_outliers_isolation(self, series: pd.Series) -> pd.Series:
        """使用孤立森林处理异常值"""
        try:
            from sklearn.ensemble import IsolationForest
            
            # 重塑数据
            values = series.values.reshape(-1, 1)
            
            # 训练孤立森林
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outlier_labels = iso_forest.fit_predict(values)
            
            # 替换异常值为中位数
            result = series.copy()
            outlier_mask = outlier_labels == -1
            median_value = series.median()
            result[outlier_mask] = median_value
            
            return result
            
        except Exception:
            # 如果孤立森林失败，回退到IQR方法
            return self._handle_outliers_iqr(series)
    
    def _smooth_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据平滑"""
        if not SCIPY_AVAILABLE:
            return data
        
        numeric_columns = ['close', 'volume']
        
        for col in numeric_columns:
            if col in data.columns:
                # 使用中值滤波器平滑数据
                window_size = min(5, len(data) // 4)
                if window_size >= 3:
                    data[col] = medfilt(data[col], kernel_size=window_size)
        
        return data
    
    def _validate_data_quality(
        self, 
        data: pd.DataFrame, 
        instrument: str = None
    ) -> pd.DataFrame:
        """验证数据质量"""
        # 检查数据量
        if len(data) < self.min_data_points:
            msg = (f"{instrument or 'Unknown'} 数据点不足: {len(data)} < "
                   f"{self.min_data_points}")
            logger.warning(msg)
        
        # 检查价格逻辑
        price_cols = ['open', 'high', 'low', 'close']
        if all(col in data.columns for col in price_cols):
            # 检查价格逻辑：high >= max(open, close) 和 low <= min(open, close)
            invalid_high = data['high'] < data[['open', 'close']].max(axis=1)
            invalid_low = data['low'] > data[['open', 'close']].min(axis=1)
            
            if invalid_high.any():
                msg = (f"{instrument or 'Unknown'} 发现无效高价数据点: "
                       f"{invalid_high.sum()}")
                logger.warning(msg)
                # 修正高价
                price_cols = ['open', 'close']
                max_vals = data.loc[invalid_high, price_cols].max(axis=1)
                data.loc[invalid_high, 'high'] = max_vals.astype('float32')
            
            if invalid_low.any():
                msg = (f"{instrument or 'Unknown'} 发现无效低价数据点: "
                       f"{invalid_low.sum()}")
                logger.warning(msg)
                # 修正低价
                price_cols = ['open', 'close']
                min_vals = data.loc[invalid_low, price_cols].min(axis=1)
                data.loc[invalid_low, 'low'] = min_vals.astype('float32')
        
        # 检查成交量
        if 'volume' in data.columns:
            negative_volume = data['volume'] < 0
            if negative_volume.any():
                msg = (f"{instrument or 'Unknown'} 发现负成交量: "
                       f"{negative_volume.sum()}")
                logger.warning(msg)
                data.loc[negative_volume, 'volume'] = 0
        
        return data
    
    def analyze_data_quality(
        self,
        data: pd.DataFrame,
        instrument: str = None
    ) -> Dict[str, Any]:
        """
        分析数据质量
        
        Args:
            data: 数据
            instrument: 股票代码
            
        Returns:
            数据质量报告
        """
        try:
            if data.empty:
                return {
                    "overall_score": 0.0,
                    "issues": ["数据为空"],
                    "recommendations": ["检查数据源"],
                    "details": {}
                }
            
            issues = []
            recommendations = []
            details = {}
            total_score = 100.0
            
            # 1. 检查数据量
            data_points = len(data)
            if data_points < self.min_data_points:
                issues.append(f"数据点不足: {data_points} < {self.min_data_points}")
                recommendations.append("增加数据量或调整最小数据点要求")
                total_score -= 20
            
            details["data_points"] = data_points
            details["min_required"] = self.min_data_points
            
            # 2. 检查缺失值
            missing_info = {}
            for col in data.columns:
                missing_count = data[col].isnull().sum()
                if missing_count > 0:
                    missing_ratio = missing_count / data_points
                    missing_info[col] = {
                        "count": int(missing_count),
                        "ratio": float(missing_ratio)
                    }
                    
                    if missing_ratio > 0.1:  # 超过10%缺失
                        issues.append(f"{col}列缺失值过多: {missing_ratio:.2%}")
                        recommendations.append(f"处理{col}列的缺失值")
                        total_score -= 10
            
            details["missing_values"] = missing_info
            
            # 3. 检查异常值
            outlier_info = {}
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                    Q1 = data[col].quantile(0.25)
                    Q3 = data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    if IQR > 0:
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        
                        outliers = ((data[col] < lower_bound) |
                                    (data[col] > upper_bound)).sum()
                        
                        if outliers > 0:
                            outlier_ratio = outliers / data_points
                            outlier_info[col] = {
                                "count": int(outliers),
                                "ratio": float(outlier_ratio)
                            }
                            
                            if outlier_ratio > 0.05:  # 超过5%异常值
                                issues.append(
                                    f"{col}列异常值过多: {outlier_ratio:.2%}"
                                )
                                recommendations.append(f"检查{col}列的数据质量")
                                total_score -= 5
            
            details["outliers"] = outlier_info
            
            # 4. 检查价格逻辑
            price_logic_issues = []
            price_cols = ['open', 'high', 'low', 'close']
            if all(col in data.columns for col in price_cols):
                # 检查价格逻辑
                invalid_high = (
                    data['high'] < data[['open', 'close']].max(axis=1)
                ).sum()
                invalid_low = (
                    data['low'] > data[['open', 'close']].min(axis=1)
                ).sum()
                
                if invalid_high > 0:
                    price_logic_issues.append(f"无效高价数据点: {invalid_high}")
                    total_score -= 5
                
                if invalid_low > 0:
                    price_logic_issues.append(f"无效低价数据点: {invalid_low}")
                    total_score -= 5
                
                # 检查负价格
                negative_prices = (data[price_cols] < 0).any().any()
                if negative_prices:
                    price_logic_issues.append("发现负价格数据")
                    total_score -= 10
            
            if price_logic_issues:
                issues.extend(price_logic_issues)
                recommendations.append("检查价格数据的逻辑性")
            
            details["price_logic"] = {
                "issues": price_logic_issues,
                "invalid_high": int(invalid_high) if 'invalid_high' in locals()
                else 0,
                "invalid_low": int(invalid_low) if 'invalid_low' in locals()
                else 0
            }
            
            # 5. 检查成交量
            volume_issues = []
            if 'volume' in data.columns:
                negative_volume = (data['volume'] < 0).sum()
                if negative_volume > 0:
                    volume_issues.append(f"负成交量数据点: {negative_volume}")
                    total_score -= 5
                
                zero_volume_ratio = (data['volume'] == 0).sum() / data_points
                if zero_volume_ratio > 0.5:  # 超过50%零成交量
                    volume_issues.append(f"零成交量过多: {zero_volume_ratio:.2%}")
                    total_score -= 5
            
            if volume_issues:
                issues.extend(volume_issues)
                recommendations.append("检查成交量数据")
            
            details["volume"] = {
                "issues": volume_issues,
                "negative_volume": int(negative_volume) if 'negative_volume'
                in locals() else 0,
                "zero_volume_ratio": (
                    float(zero_volume_ratio) if 'zero_volume_ratio'
                    in locals() else 0.0
                )
            }
            
            # 6. 检查数据连续性
            continuity_issues = []
            if isinstance(data.index, pd.DatetimeIndex):
                # 检查日期间隔
                time_diffs = data.index.to_series().diff().dropna()
                expected_freq = time_diffs.mode()
                
                if len(expected_freq) > 0:
                    expected_freq = expected_freq.iloc[0]
                    irregular_gaps = (time_diffs > expected_freq * 2).sum()
                    
                    if irregular_gaps > 0:
                        continuity_issues.append(f"数据间隔不规律: {irregular_gaps}处")
                        total_score -= 5
            
            if continuity_issues:
                issues.extend(continuity_issues)
                recommendations.append("检查数据的时间连续性")
            
            details["continuity"] = {
                "issues": continuity_issues,
                "irregular_gaps": int(irregular_gaps) if 'irregular_gaps'
                in locals() else 0
            }
            
            # 确保分数在0-100范围内
            overall_score = max(0.0, min(100.0, total_score))
            
            # 生成质量等级
            if overall_score >= 90:
                quality_grade = "优秀"
            elif overall_score >= 80:
                quality_grade = "良好"
            elif overall_score >= 70:
                quality_grade = "一般"
            elif overall_score >= 60:
                quality_grade = "较差"
            else:
                quality_grade = "很差"
            
            return {
                "overall_score": overall_score,
                "quality_grade": quality_grade,
                "issues": issues,
                "recommendations": recommendations,
                "details": details,
                "instrument": instrument or "Unknown"
            }
            
        except Exception as e:
            logger.error(f"数据质量分析失败: {e}")
            return {
                "overall_score": 0.0,
                "issues": [f"分析失败: {str(e)}"],
                "recommendations": ["检查数据格式和内容"],
                "details": {"error": str(e)}
            }
    
    def standardize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        标准化数据
        
        Args:
            data: 原始数据
            
        Returns:
            标准化后的数据
        """
        try:
            result_data = data.copy()
            
            # 确保只处理数值型因子列
            numeric_columns = []
            for col in data.columns:
                if pd.api.types.is_numeric_dtype(data[col]):
                    numeric_columns.append(col)
            
            if not SKLEARN_AVAILABLE:
                # 使用简单的Z-Score标准化
                for col in numeric_columns:
                    if data[col].std() > 0:
                        # 确保数据类型为float64以避免精度问题
                        result_data[col] = result_data[col].astype('float64')
                        mean_val = result_data[col].mean()
                        std_val = result_data[col].std()
                        result_data[col] = (
                            result_data[col] - mean_val
                        ) / std_val
                
                return result_data
            
            # 使用RobustScaler标准化（对异常值更鲁棒）
            if numeric_columns:
                # 确保数据类型兼容性
                for col in numeric_columns:
                    result_data[col] = result_data[col].astype('float64')
                
                scaler = RobustScaler()
                result_data[numeric_columns] = scaler.fit_transform(
                    result_data[numeric_columns]
                )
            
            return result_data
            
        except Exception as e:
            logger.error(f"数据标准化失败: {e}")
            return data


# 全局数据质量控制器实例
_global_quality_controller = None


def get_quality_controller(config=None) -> DataQualityController:
    """获取全局数据质量控制器实例"""
    global _global_quality_controller
    
    if _global_quality_controller is None:
        _global_quality_controller = DataQualityController(config)
    
    return _global_quality_controller