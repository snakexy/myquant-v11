# -*- coding: utf-8 -*-
"""
Research阶段 - 数据清洗服务
=============================
职责：
- 数据质量检查
- 异常值检测和处理
- 数据标准化
- 缺失值填充

架构层次：
- Research阶段：为因子计算提供清洗后的高质量数据
- 确保数据质量符合量化研究要求
"""

from typing import List, Dict, Optional, Any, Tuple
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass


@dataclass
class DataQualityReport:
    """数据质量报告"""
    total_rows: int                    # 总行数
    missing_values: int                # 缺失值数量
    missing_percentage: float          # 缺失值比例
    duplicate_rows: int                # 重复行数
    outliers_detected: int             # 检测到的异常值数量
    outliers_handled: int              # 已处理的异常值数量
    quality_score: float               # 质量评分（0-100）
    issues: List[str]                  # 问题列表
    warnings: List[str]                # 警告列表


class DataCleaningService:
    """
    数据清洗服务

    核心职责：
    1. 数据质量检查和评估
    2. 异常值检测和处理
    3. 缺失值填充
    4. 数据标准化
    5. 重复数据处理

    使用场景：
    - 因子计算前的数据准备
    - K线数据清洗
    - 财务数据标准化
    """

    def __init__(
        self,
        auto_fix: bool = True,  # 自动修复数据问题
        strict_mode: bool = False,  # 严格模式（质量低于阈值时报错）
        min_quality_score: float = 70.0,  # 最低质量评分
    ):
        """
        初始化数据清洗服务

        Args:
            auto_fix: 自动修复数据问题
            strict_mode: 严格模式
            min_quality_score: 最低质量评分（0-100）
        """
        self.auto_fix = auto_fix
        self.strict_mode = strict_mode
        self.min_quality_score = min_quality_score

        logger.info("✅ DataCleaningService初始化完成")

    # ==================== 数据质量检查 ====================

    def check_quality(
        self,
        df: pd.DataFrame,
        data_type: str = "kline"
    ) -> DataQualityReport:
        """
        检查数据质量

        Args:
            df: 待检查的数据
            data_type: 数据类型（kline/financial/tick等）

        Returns:
            DataQualityReport对象
        """
        if df is None or df.empty:
            return DataQualityReport(
                total_rows=0,
                missing_values=0,
                missing_percentage=100.0,
                duplicate_rows=0,
                outliers_detected=0,
                outliers_handled=0,
                quality_score=0.0,
                issues=["数据为空"],
                warnings=[]
            )

        issues = []
        warnings = []

        # 1. 检查缺失值
        missing_count = df.isnull().sum().sum()
        missing_pct = (missing_count / (len(df) * len(df.columns))) * 100

        if missing_pct > 20:
            issues.append(f"缺失值比例过高: {missing_pct:.2f}%")
        elif missing_pct > 5:
            warnings.append(f"缺失值比例较高: {missing_pct:.2f}%")

        # 2. 检查重复行
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            issues.append(f"存在{duplicate_count}条重复数据")

        # 3. 检查异常值（根据数据类型）
        outliers = self._detect_outliers(df, data_type)

        # 4. 计算质量评分
        quality_score = self._calculate_quality_score(
            missing_pct=missing_pct,
            duplicate_count=duplicate_count,
            outlier_count=len(outliers),
            total_rows=len(df)
        )

        return DataQualityReport(
            total_rows=len(df),
            missing_values=missing_count,
            missing_percentage=missing_pct,
            duplicate_rows=duplicate_count,
            outliers_detected=len(outliers),
            outliers_handled=0,
            quality_score=quality_score,
            issues=issues,
            warnings=warnings
        )

    def _detect_outliers(
        self,
        df: pd.DataFrame,
        data_type: str
    ) -> List[Tuple[str, int]]:
        """
        检测异常值

        Args:
            df: 数据DataFrame
            data_type: 数据类型

        Returns:
            异常值列表 [(列名, 行索引), ...]
        """
        outliers = []

        if data_type == "kline":
            # K线数据异常值检测
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in numeric_columns:
                if col in df.columns:
                    # 使用IQR方法检测异常值
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 3 * IQR
                    upper_bound = Q3 + 3 * IQR

                    outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                    outlier_indices = df[outlier_mask].index.tolist()

                    for idx in outlier_indices:
                        outliers.append((col, idx))

        return outliers

    def _calculate_quality_score(
        self,
        missing_pct: float,
        duplicate_count: int,
        outlier_count: int,
        total_rows: int
    ) -> float:
        """
        计算数据质量评分

        Args:
            missing_pct: 缺失值比例
            duplicate_count: 重复行数
            outlier_count: 异常值数量
            total_rows: 总行数

        Returns:
            质量评分（0-100）
        """
        score = 100.0

        # 缺失值扣分
        score -= missing_pct * 2

        # 重复数据扣分
        if total_rows > 0:
            duplicate_pct = (duplicate_count / total_rows) * 100
            score -= duplicate_pct * 1

        # 异常值扣分
        if total_rows > 0:
            outlier_pct = (outlier_count / total_rows) * 100
            score -= outlier_pct * 0.5

        return max(0.0, min(100.0, score))

    # ==================== 数据清洗 ====================

    def clean_kline_data(
        self,
        df: pd.DataFrame,
        report_quality: bool = True
    ) -> Tuple[pd.DataFrame, Optional[DataQualityReport]]:
        """
        清洗K线数据

        Args:
            df: K线数据DataFrame
            report_quality: 是否返回质量报告

        Returns:
            (清洗后的数据, 质量报告)
        """
        if df is None or df.empty:
            logger.warning("K线数据为空，无需清洗")
            return df, None

        # 1. 数据质量检查
        quality_report = self.check_quality(df, data_type="kline") if report_quality else None

        if quality_report and self.strict_mode and quality_report.quality_score < self.min_quality_score:
            error_msg = f"数据质量评分过低: {quality_report.quality_score:.2f}，最低要求: {self.min_quality_score}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 2. 去除重复行
        df_cleaned = df.drop_duplicates()

        # 3. 处理缺失值
        if self.auto_fix:
            df_cleaned = self._handle_missing_values(df_cleaned, data_type="kline")

        # 4. 处理异常值
        if self.auto_fix:
            df_cleaned = self._handle_outliers(df_cleaned, data_type="kline")

        # 5. 数据类型转换和标准化
        df_cleaned = self._standardize_dtypes(df_cleaned, data_type="kline")

        # 6. 排序
        if 'datetime' in df_cleaned.columns:
            df_cleaned = df_cleaned.sort_values('datetime')
        elif df_cleaned.index.name == 'datetime':
            df_cleaned = df_cleaned.sort_index()

        logger.info(f"K线数据清洗完成: {len(df)} → {len(df_cleaned)} 行")

        return df_cleaned, quality_report

    def _handle_missing_values(
        self,
        df: pd.DataFrame,
        data_type: str
    ) -> pd.DataFrame:
        """
        处理缺失值

        Args:
            df: 数据DataFrame
            data_type: 数据类型

        Returns:
            处理后的DataFrame
        """
        df_filled = df.copy()

        if data_type == "kline":
            # K线数据缺失值处理策略
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']

            for col in numeric_columns:
                if col in df_filled.columns:
                    # 前向填充 + 后向填充 (使用新API)
                    df_filled[col] = df_filled[col].ffill().bfill()

                    # 如果还有缺失值，用0填充
                    df_filled[col] = df_filled[col].fillna(0)

        return df_filled

    def _handle_outliers(
        self,
        df: pd.DataFrame,
        data_type: str
    ) -> pd.DataFrame:
        """
        处理异常值

        Args:
            df: 数据DataFrame
            data_type: 数据类型

        Returns:
            处理后的DataFrame
        """
        df_handled = df.copy()

        if data_type == "kline":
            # K线数据异常值处理
            # 对于价格数据，使用中位数替换
            price_columns = ['open', 'high', 'low', 'close']

            for col in price_columns:
                if col in df_handled.columns:
                    # 使用IQR方法检测并替换异常值
                    Q1 = df_handled[col].quantile(0.25)
                    Q3 = df_handled[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 3 * IQR
                    upper_bound = Q3 + 3 * IQR

                    median_value = df_handled[col].median()
                    df_handled.loc[df_handled[col] < lower_bound, col] = median_value
                    df_handled.loc[df_handled[col] > upper_bound, col] = median_value

        return df_handled

    def _standardize_dtypes(
        self,
        df: pd.DataFrame,
        data_type: str
    ) -> pd.DataFrame:
        """
        标准化数据类型

        Args:
            df: 数据DataFrame
            data_type: 数据类型

        Returns:
            类型标准化后的DataFrame
        """
        df_standardized = df.copy()

        if data_type == "kline":
            # 确保datetime列是datetime类型
            if 'datetime' in df_standardized.columns:
                df_standardized['datetime'] = pd.to_datetime(df_standardized['datetime'])

            # 确保数值列是float类型
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in numeric_columns:
                if col in df_standardized.columns:
                    df_standardized[col] = pd.to_numeric(df_standardized[col], errors='coerce')

        return df_standardized

    # ==================== 数据标准化 ====================

    def standardize_features(
        self,
        df: pd.DataFrame,
        method: str = "zscore"
    ) -> pd.DataFrame:
        """
        特征标准化

        Args:
            df: 特征DataFrame
            method: 标准化方法（zscore/minmax/robust）

        Returns:
            标准化后的DataFrame
        """
        df_standardized = df.copy()
        numeric_columns = df_standardized.select_dtypes(include=[np.number]).columns

        if method == "zscore":
            # Z-score标准化
            for col in numeric_columns:
                mean = df_standardized[col].mean()
                std = df_standardized[col].std()
                if std > 0:
                    df_standardized[col] = (df_standardized[col] - mean) / std

        elif method == "minmax":
            # Min-Max标准化
            for col in numeric_columns:
                min_val = df_standardized[col].min()
                max_val = df_standardized[col].max()
                if max_val > min_val:
                    df_standardized[col] = (df_standardized[col] - min_val) / (max_val - min_val)

        elif method == "robust":
            # 鲁棒标准化（使用中位数和IQR）
            for col in numeric_columns:
                median = df_standardized[col].median()
                Q1 = df_standardized[col].quantile(0.25)
                Q3 = df_standardized[col].quantile(0.75)
                IQR = Q3 - Q1
                if IQR > 0:
                    df_standardized[col] = (df_standardized[col] - median) / IQR

        return df_standardized


# ==================== 全局单例 ====================

_data_cleaning_service_instance: Optional[DataCleaningService] = None


def get_data_cleaning_service() -> DataCleaningService:
    """
    获取数据清洗服务单例

    Returns:
        DataCleaningService实例
    """
    global _data_cleaning_service_instance

    if _data_cleaning_service_instance is None:
        _data_cleaning_service_instance = DataCleaningService()

    return _data_cleaning_service_instance
