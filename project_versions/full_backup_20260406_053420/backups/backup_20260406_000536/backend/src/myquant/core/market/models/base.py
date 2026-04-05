"""
数据模型基类和工具函数

提供统一的模型基类、序列化/反序列化、DataFrame 转换等功能
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Type, TypeVar
import pandas as pd
from abc import ABC, abstractmethod


T = TypeVar('T', bound='BaseModel')


@dataclass
class BaseModel:
    """数据模型基类

    所有 V5 数据模型的基类，提供统一的序列化/反序列化接口
    """

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, pd.DataFrame):
                result[key] = value.to_dict('records')
            elif isinstance(value, list):
                result[key] = [v.to_dict() if hasattr(v, 'to_dict') else v for v in value]
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """从字典创建实例"""
        # 子类可以覆盖此方法以处理复杂转换
        return cls(**data)


class TimestampMixin:
    """时间戳混入类

    为模型添加 created_at 和 updated_at 字段
    """

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def touch(self) -> None:
        """更新 updated_at 时间戳"""
        self.updated_at = datetime.now()


def df_to_model_list(df: pd.DataFrame, model_class: Type[T]) -> List[T]:
    """将 DataFrame 转换为模型列表

    Args:
        df: 输入 DataFrame，每行对应一个模型实例
        model_class: 模型类，必须实现 from_dict 方法

    Returns:
        模型列表
    """
    if df is None or df.empty:
        return []

    records = df.to_dict('records')
    return [model_class.from_dict(record) for record in records]


def model_list_to_df(models: List[T]) -> pd.DataFrame:
    """将模型列表转换为 DataFrame

    Args:
        models: 模型列表，每个模型必须实现 to_dict 方法

    Returns:
        DataFrame
    """
    if not models:
        return pd.DataFrame()

    data = [model.to_dict() for model in models]
    return pd.DataFrame(data)


def standardize_dataframe_columns(
    df: pd.DataFrame,
    required_columns: List[str],
    datetime_column: str = 'datetime'
) -> pd.DataFrame:
    """标准化 DataFrame 列名和格式

    确保 DataFrame 包含所需的列，并转换 datetime 列

    Args:
        df: 输入 DataFrame
        required_columns: 必需的列名列表
        datetime_column: datetime 列名

    Returns:
        标准化后的 DataFrame
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=required_columns)

    # 转换 datetime 列
    if datetime_column in df.columns:
        dt_col = df[datetime_column]

        # 检查是否是 numeric 类型（Unix 时间戳）
        if pd.api.types.is_numeric_dtype(dt_col):
            # 检查是否是毫秒时间戳（值 > 100000000000 表示毫秒，不是秒）
            first_val = dt_col.iloc[0] if len(dt_col) > 0 else 0
            if isinstance(first_val, (int, float)) and first_val > 100000000000:
                # 毫秒时间戳（如 1773039600000）
                df[datetime_column] = pd.to_datetime(dt_col, unit='ms', errors='coerce')
            else:
                # 秒时间戳或其他格式
                df[datetime_column] = pd.to_datetime(dt_col, unit='s', errors='coerce')
        else:
            # 已经是 datetime 或字符串格式
            df[datetime_column] = pd.to_datetime(dt_col, errors='coerce')

    # 确保所有必需列存在
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    # 只保留需要的列
    existing_columns = [col for col in required_columns if col in df.columns]
    return df[existing_columns].copy()


def merge_dataframes(
    dfs: List[pd.DataFrame],
    on: str = 'datetime',
    how: str = 'outer'
) -> pd.DataFrame:
    """合并多个 DataFrame

    按指定列合并多个 DataFrame，常用于合并历史和实时数据

    Args:
        dfs: DataFrame 列表
        on: 合并的键列名
        how: 合并方式 (left, right, outer, inner)

    Returns:
        合并后的 DataFrame
    """
    if not dfs:
        return pd.DataFrame()

    if len(dfs) == 1:
        return dfs[0].copy() if not dfs[0].empty else pd.DataFrame()

    # 过滤掉空的 DataFrame
    valid_dfs = [df for df in dfs if df is not None and not df.empty]
    if not valid_dfs:
        return pd.DataFrame()

    result = valid_dfs[0]
    for df in valid_dfs[1:]:
        result = pd.merge(result, df, on=on, how=how)

    return result.sort_values(on).reset_index(drop=True)
