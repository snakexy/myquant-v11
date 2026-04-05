# -*- coding: utf-8 -*-
"""
训练数据加载器
================
为在线学习模块提供训练数据加载和预处理功能

核心功能：
- 加载历史市场数据
- 数据预处理（清洗、标准化）
- 滚动窗口数据分割
- Qlib数据格式转换

使用示例：
```python
loader = DataLoader()
dataset = loader.load(
    start_date="2023-01-01",
    end_date="2024-01-01"
)
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class DataLoader:
    """训练数据加载器

    职责：
    1. 从数据源加载历史市场数据
    2. 数据预处理（清洗、特征工程）
    3. 滚动窗口数据分割
    4. 转换为Qlib训练格式

    使用示例：
    ```python
    loader = DataLoader()

    # 加载训练数据
    dataset = loader.load(
        start_date="2023-01-01",
        end_date="2024-01-01",
        features=["open", "high", "low", "close", "volume"]
    )
    ```
    """

    def __init__(self):
        """初始化数据加载器"""
        # 默认特征列表
        self.default_features = [
            "open", "high", "low", "close", "volume",
            "vwap", "returns", "volatility"
        ]

        # 数据缓存
        self._cache = {}
        self._cache_ttl = 3600  # 1小时缓存

        logger.info("DataLoader initialized")

    def load(
        self,
        start_date: str,
        end_date: str,
        features: Optional[List[str]] = None,
        instruments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """加载训练数据

        Args:
            start_date: 训练数据开始日期
            end_date: 训练数据结束日期
            features: 特征列表（None则使用默认）
            instruments: 股票池列表（None则使用默认池）

        Returns:
            数据集字典，包含：
            - df: DataFrame格式的数据
            - features: 使用的特征列表
            - instruments: 股票池列表
            - date_range: 时间范围
        """
        features = features or self.default_features
        instruments = instruments or self._get_default_instruments()

        logger.info(
            f"Loading data: {start_date} to {end_date}, "
            f"{len(instruments)} instruments, {len(features)} features"
        )

        # 检查缓存
        cache_key = f"{start_date}_{end_date}_{len(instruments)}"
        if cache_key in self._cache:
            logger.debug("Returning cached data")
            return self._cache[cache_key]

        # 加载数据
        df = self._load_from_database(start_date, end_date, instruments, features)

        # 数据预处理
        df = self._preprocess(df)

        # 构建数据集
        dataset = {
            "df": df,
            "features": features,
            "instruments": instruments,
            "date_range": {"start": start_date, "end": end_date},
            "shape": df.shape,
            "loaded_at": datetime.now().isoformat()
        }

        # 更新缓存
        self._cache[cache_key] = dataset

        logger.info(
            f"Data loaded successfully: {df.shape[0]} rows, "
            f"{df.shape[1]} columns"
        )

        return dataset

    def _get_default_instruments(self) -> List[str]:
        """获取默认股票池"""
        # 使用市场主流股票池
        return [
            "000001.SZ",  # 平安银行
            "000002.SZ",  # 万科A
            "600000.SH",  # 浦发银行
            "600036.SH",  # 招商银行
            "600519.SH",  # 贵州茅台
            "600887.SH",  # 伊利股份
            "000858.SZ",  # 五粮液
            "002475.SZ",  # 立讯精密
            "300059.SZ",  # 东方财富
            "601318.SH"   # 中国平安
        ]

    def _load_from_database(
        self,
        start_date: str,
        end_date: str,
        instruments: List[str],
        features: List[str]
    ) -> pd.DataFrame:
        """从数据库加载原始数据

        Args:
            start_date: 开始日期
            end_date: 结束日期
            instruments: 股票池
            features: 特征列表

        Returns:
            原始数据DataFrame
        """
        # TODO: 后续从真实的数据库或API加载数据
        # 目前使用模拟数据生成

        logger.debug(f"Loading data from database for {len(instruments)} instruments")

        # 生成日期范围
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # 过滤交易日（简单模拟：排除周末）
        trading_days = [d for d in dates if d.weekday() < 5]

        # 生成模拟数据
        data = []
        for instrument in instruments:
            # 基础价格（随机初始值）
            base_price = np.random.uniform(10, 100)

            for date in trading_days:
                # 随机价格变动
                daily_return = np.random.normal(0, 0.02)  # 2%日波动率
                open_price = base_price * (1 + np.random.uniform(-0.01, 0.01))
                close_price = base_price * (1 + daily_return)
                high_price = max(open_price, close_price) * (1 + abs(np.random.uniform(0, 0.01)))
                low_price = min(open_price, close_price) * (1 - abs(np.random.uniform(0, 0.01)))
                volume = np.random.uniform(1000000, 10000000)

                row = {
                    "datetime": date,
                    "instrument": instrument,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume
                }

                # 计算衍生特征
                row["vwap"] = (row["high"] + row["low"] + row["close"]) / 3
                row["returns"] = daily_return
                row["volatility"] = abs(daily_return)

                data.append(row)

            base_price = close_price  # 下一天的基准价格

        df = pd.DataFrame(data)
        df.set_index(["datetime", "instrument"], inplace=True)

        logger.debug(f"Generated mock data: {df.shape}")

        return df

    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据预处理

        Args:
            df: 原始数据

        Returns:
            预处理后的数据
        """
        logger.debug("Preprocessing data")

        # 1. 处理缺失值（使用新版pandas API）
        df = df.ffill().bfill()

        # 2. 删除异常值
        for col in df.select_dtypes(include=[np.number]).columns:
            if col != "volume":
                # 使用3-sigma规则删除异常值
                mean = df[col].mean()
                std = df[col].std()
                df = df[(df[col] >= mean - 3*std) & (df[col] <= mean + 3*std)]

        # 3. 特征标准化（可选）
        # df = self._normalize(df)

        logger.debug(f"Preprocessed data shape: {df.shape}")

        return df

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """特征标准化（Z-score标准化）

        Args:
            df: 数据DataFrame

        Returns:
            标准化后的数据
        """
        # 对数值特征进行标准化
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if col not in ["volume", "returns"]:  # 跳过不需要标准化的特征
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    df[col] = (df[col] - mean) / std

        return df

    def load_rolling_data(
        self,
        cur_time: str,
        window_size: int,
        rolling_step: int
    ) -> Dict[str, Any]:
        """加载滚动窗口数据

        Args:
            cur_time: 当前时间点
            window_size: 训练窗口大小（交易日）
            rolling_step: 滚动步长（交易日）

        Returns:
            滚动窗口数据集
        """
        # 计算训练时间范围
        cur_date = datetime.fromisoformat(cur_time.replace('T', ' ').split()[0])

        # 交易日转自然日（252交易日 ≈ 365自然日）
        trading_to_natural = 365.0 / 252.0

        # 训练结束时间 = 当前时间
        train_end = cur_date

        # 训练开始时间 = 当前时间 - 窗口大小
        natural_days = int(window_size * trading_to_natural)
        train_start = train_end - timedelta(days=natural_days)

        logger.info(
            f"Loading rolling data: {train_start.date()} to {train_end.date()}, "
            f"window_size={window_size} trading days"
        )

        # 加载数据
        dataset = self.load(
            start_date=train_start.strftime('%Y-%m-%d'),
            end_date=train_end.strftime('%Y-%m-%d')
        )

        # 添加滚动窗口信息
        dataset["rolling_config"] = {
            "cur_time": cur_time,
            "window_size": window_size,
            "rolling_step": rolling_step,
            "train_start": train_start.strftime('%Y-%m-%d'),
            "train_end": train_end.strftime('%Y-%m-%d')
        }

        return dataset

    def clear_cache(self):
        """清除数据缓存"""
        self._cache.clear()
        logger.debug("Data cache cleared")
