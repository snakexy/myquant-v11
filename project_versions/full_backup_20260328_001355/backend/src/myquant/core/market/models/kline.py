"""
K线数据模型

定义 K 线数据的标准格式和操作
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from .base import BaseModel, df_to_model_list, standardize_dataframe_columns


@dataclass
class KlineData(BaseModel):
    """单条 K 线数据

    标准化的 OHLCV 数据格式
    """
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float = 0.0

    def __post_init__(self):
        """数据校验"""
        if self.high < max(self.open, self.close):
            raise ValueError(f"high ({self.high}) 不能低于 open/close 的最大值")
        if self.low > min(self.open, self.close):
            raise ValueError(f"low ({self.low}) 不能高于 open/close 的最小值")
        if self.volume < 0:
            raise ValueError(f"volume ({self.volume}) 不能为负数")

    @property
    def is_up(self) -> bool:
        """是否上涨（收盘价 > 开盘价）"""
        return self.close > self.open

    @property
    def is_down(self) -> bool:
        """是否下跌（收盘价 < 开盘价）"""
        return self.close < self.open

    @property
    def body(self) -> float:
        """实体长度"""
        return abs(self.close - self.open)

    @property
    def upper_shadow(self) -> float:
        """上影线长度"""
        return self.high - max(self.open, self.close)

    @property
    def lower_shadow(self) -> float:
        """下影线长度"""
        return min(self.open, self.close) - self.low

    @property
    def amplitude(self) -> float:
        """振幅 (%)"""
        if self.low == 0:
            return 0.0
        return (self.high - self.low) / self.low * 100

    @property
    def change_pct(self) -> float:
        """涨跌幅 (%)"""
        if self.open == 0:
            return 0.0
        return (self.close - self.open) / self.open * 100


class KlineDataset:
    """K 线数据集

    DataFrame 包装类，提供标准化的 OHLCV 数据操作
    """

    STANDARD_COLUMNS = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']

    def __init__(self, df: pd.DataFrame, adapter: str = 'unknown'):
        """
        Args:
            df: K线数据 DataFrame，必须包含 OHLCV 列
            adapter: 数据源适配器名称 ('pytdx', 'xtquant', 'localdb', etc.)
        """
        self.adapter = adapter

        # 先进行标准化
        normalized_df = standardize_dataframe_columns(
            df,
            required_columns=self.STANDARD_COLUMNS,
            datetime_column='datetime'
        )

        # 添加数据来源列（只在不存在时添加，保留已有的）
        # 这样可以保留 merge 后的数据源信息
        if 'data_source' not in normalized_df.columns:
            normalized_df['data_source'] = adapter

        self.df = normalized_df

    @classmethod
    def from_adapter(cls, df: pd.DataFrame, source: str) -> 'KlineDataset':
        """从适配器原始数据创建 K线数据集

        使用 V5 FormatConverter 标准化数据格式

        Args:
            df: 适配器返回的 DataFrame
            source: 数据源名称 ('pytdx', 'xtquant', 'tdxquant', 'localdb')

        Returns:
            KlineDataset 实例
        """
        from myquant.core.market.utils.format_converter import FormatConverter

        # 检查数据是否已经标准化过（包含标准列名）
        if all(col in df.columns for col in ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']):
            # 已经是标准格式，直接使用
            normalized_df = df
        else:
            # 需要标准化
            normalized_df = FormatConverter.normalize_kline(df, source)
        return cls(normalized_df, source)

    @classmethod
    def from_dict_list(cls, data: List[Dict[str, Any]]) -> 'KlineDataset':
        """从字典列表创建"""
        if not data:
            return cls(pd.DataFrame(columns=cls.STANDARD_COLUMNS))

        df = pd.DataFrame(data)
        return cls(df)

    @classmethod
    def empty(cls) -> 'KlineDataset':
        """创建空数据集"""
        return cls(pd.DataFrame(columns=cls.STANDARD_COLUMNS))

    def to_list(self) -> List[KlineData]:
        """转换为 KlineData 列表"""
        return df_to_model_list(self.df, KlineData)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """转换为字典列表"""
        return self.df.to_dict('records')

    def head(self, n: int = 5) -> 'KlineDataset':
        """返回前 n 条数据"""
        return KlineDataset(self.df.head(n))

    def tail(self, n: int = 5) -> 'KlineDataset':
        """返回后 n 条数据"""
        return KlineDataset(self.df.tail(n))

    def slice_by_date(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> 'KlineDataset':
        """按日期范围切片"""
        df = self.df.copy()

        if start_date:
            df = df[df['datetime'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['datetime'] <= pd.to_datetime(end_date)]

        return KlineDataset(df)

    def filter_by_count(self, count: int, from_end: bool = True) -> 'KlineDataset':
        """按数量过滤

        Args:
            count: 返回的数据条数
            from_end: True 从最新开始，False 从最早开始
        """
        if from_end:
            return self.tail(count)
        return self.head(count)

    def merge(self, other: 'KlineDataset', on: str = 'datetime') -> 'KlineDataset':
        """合并另一个 K线数据集

        常用于合并历史数据和实时数据

        数据对齐策略：
        - 实时数据（右侧）覆盖历史数据（左侧）的同日期记录
        - 保留数据来源信息，便于追踪

        对于日线数据，忽略时间部分，只按日期合并
        """
        # 创建用于合并的日期列（只保留日期部分，忽略时间）
        left_df = self.df.copy()
        right_df = other.df.copy()

        # 关键修复：统一 datetime 格式（移除时区信息，避免去重失败）
        # 历史数据可能是 naive datetime，实时数据可能是 UTC datetime
        # 需要统一为 naive datetime 才能正确去重
        def normalize_datetime(dt):
            """移除时区信息，统一为 naive datetime"""
            if pd.isna(dt):
                return dt
            if hasattr(dt, 'tz') and dt.tz is not None:
                # 保留本地时间，移除时区信息
                return dt.tz_localize(None)
            return dt

        left_df['datetime'] = left_df['datetime'].apply(normalize_datetime)
        right_df['datetime'] = right_df['datetime'].apply(normalize_datetime)

        # 确保有 data_source 列
        if 'data_source' not in left_df.columns:
            left_df['data_source'] = self.adapter
        if 'data_source' not in right_df.columns:
            right_df['data_source'] = other.adapter

        # 判断是否为日线数据（通过时间部分是否都是00:00:00或15:00:00）
        def is_daily_data(df):
            if df.empty or 'datetime' not in df.columns:
                return False
            times = df['datetime'].apply(lambda x: str(x).split()[-1] if isinstance(x, (str, datetime)) else '')
            # 如果大部分数据是00:00:00或15:00:00，认为是日线数据
            return times.str.contains('00:00:00|15:00:00').sum() > len(times) * 0.5

        if is_daily_data(left_df) and is_daily_data(right_df):
            # 日线数据：创建日期列用于合并
            left_df['_merge_date'] = pd.to_datetime(left_df['datetime']).dt.date
            right_df['_merge_date'] = pd.to_datetime(right_df['datetime']).dt.date

            merged_df = pd.merge(
                left_df,
                right_df,
                on='_merge_date',
                how='outer',
                suffixes=('_left', '_right')
            )

            # 优先使用右侧数据（实时数据），并合并时间列
            for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                if f'{col}_right' in merged_df.columns:
                    merged_df[col] = merged_df[f'{col}_right'].fillna(merged_df[f'{col}_left'])
                    merged_df = merged_df.drop(columns=[f'{col}_left', f'{col}_right'])

            # 合并 data_source：实时数据优先
            if 'data_source_right' in merged_df.columns:
                merged_df['data_source'] = merged_df['data_source_right'].fillna(merged_df['data_source_left'])
            else:
                merged_df['data_source'] = merged_df['data_source_left'].fillna(merged_df['data_source_right'])

            # 优先使用右侧的datetime（实时数据通常有正确的时间15:00:00）
            if 'datetime_right' in merged_df.columns:
                merged_df['datetime'] = merged_df['datetime_right'].fillna(merged_df['datetime_left'])
            else:
                merged_df['datetime'] = merged_df['datetime_left'].fillna(merged_df['datetime_right'])

            # 清理临时列
            merged_df = merged_df.drop(columns=['_merge_date', 'datetime_left', 'datetime_right',
                                                    'data_source_left', 'data_source_right'], errors='ignore')

            # 标准化日线数据时间为 15:00:00
            def normalize_daily_time(dt):
                if pd.isna(dt):
                    return dt
                if isinstance(dt, str):
                    dt = pd.to_datetime(dt)
                # 将时间部分设置为 15:00:00
                return dt.replace(hour=15, minute=0, second=0, microsecond=0)

            merged_df['datetime'] = merged_df['datetime'].apply(normalize_daily_time)
        else:
            # 非日线数据，使用原有的合并逻辑
            merged_df = pd.merge(
                left_df,
                right_df,
                on=on,
                how='outer',
                suffixes=('_left', '_right')
            )

            # 对于重复的 datetime，优先使用右侧数据（实时数据）
            for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                if f'{col}_right' in merged_df.columns:
                    merged_df[col] = merged_df[f'{col}_right'].fillna(merged_df[f'{col}_left'])
                    merged_df = merged_df.drop(columns=[f'{col}_left', f'{col}_right'])

            # 合并 data_source：实时数据优先
            if 'data_source_right' in merged_df.columns:
                merged_df['data_source'] = merged_df['data_source_right'].fillna(merged_df['data_source_left'])
            else:
                merged_df['data_source'] = merged_df['data_source_left'].fillna(merged_df['data_source_right'])

            # 清理临时列
            merged_df = merged_df.drop(columns=['data_source_left', 'data_source_right'], errors='ignore')

        # 去重：对于完全相同的 datetime，只保留一条
        merged_df = merged_df.drop_duplicates(subset=['datetime'], keep='last')

        return KlineDataset(merged_df.sort_values('datetime').reset_index(drop=True))

    def append(self, other: 'KlineDataset') -> 'KlineDataset':
        """追加另一个 K线数据集"""
        combined_df = pd.concat([self.df, other.df], ignore_index=True)
        return KlineDataset(combined_df.drop_duplicates(subset=['datetime']).sort_values('datetime').reset_index(drop=True))

    def __len__(self) -> int:
        return len(self.df)

    def __bool__(self) -> bool:
        return not self.df.empty

    def __repr__(self) -> str:
        if self.df.empty:
            return "KlineDataset(empty)"
        return f"KlineDataset(count={len(self)}, start={self.df['datetime'].min()}, end={self.df['datetime'].max()})"

    def __getitem__(self, key):
        """支持索引访问"""
        if isinstance(key, int):
            return KlineData(**self.df.iloc[key].to_dict())
        return KlineDataset(self.df[key])

    def get_latest_price(self) -> Optional[float]:
        """获取最新收盘价"""
        if self.df.empty:
            return None
        return float(self.df.iloc[-1]['close'])

    def get_change_pct(self) -> Optional[float]:
        """获取最新涨跌幅"""
        if len(self.df) < 2:
            return None
        latest = self.df.iloc[-1]['close']
        previous = self.df.iloc[-2]['close']
        if previous == 0:
            return None
        return (latest - previous) / previous * 100


def create_kline_dataset(data: Any, source: str = 'pytdx') -> KlineDataset:
    """便捷函数：创建 KlineDataset

    Args:
        data: 输入数据，支持 DataFrame 或 dict list
        source: 数据源名称

    Returns:
        KlineDataset 实例
    """
    if isinstance(data, KlineDataset):
        return data

    if isinstance(data, pd.DataFrame):
        return KlineDataset.from_adapter(data, source)

    if isinstance(data, list):
        return KlineDataset.from_dict_list(data)

    return KlineDataset.empty()
