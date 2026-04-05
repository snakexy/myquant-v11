# -*- coding: utf-8 -*-
"""
数据合并工具 - 实现本地数据与在线数据的无缝补齐

支持策略：
1. 本地优先：先读本地，缺失部分在线补齐
2. 在线优先：先读在线，缓存到本地
3. 智能合并：自动检测缺失时间段，合并去重
"""

from typing import Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

import pandas as pd
from loguru import logger


@dataclass
class DataSourceInfo:
    """数据源信息"""
    source_name: str  # 数据源名称
    last_date: Optional[str] = None  # 最后数据日期
    record_count: int = 0  # 记录数
    is_fresh: bool = False  # 是否最新


class DataMerger:
    """数据合并器

    用于合并多个数据源的数据，实现无缝补齐
    """

    @staticmethod
    def merge_kline_data(
        local_df: Optional[pd.DataFrame],
        online_df: Optional[pd.DataFrame],
        date_col: str = 'datetime'
    ) -> Optional[pd.DataFrame]:
        """合并本地和在线K线数据（去重）

        Args:
            local_df: 本地数据
            online_df: 在线数据
            date_col: 日期列名

        Returns:
            合并后的DataFrame
        """
        if local_df is None and online_df is None:
            return None

        if local_df is None or local_df.empty:
            return online_df

        if online_df is None or online_df.empty:
            return local_df

        # 合并数据
        combined = pd.concat([local_df, online_df], ignore_index=True)

        # 去重（保留后出现的，通常是在线数据更新）
        if date_col in combined.columns:
            combined = combined.drop_duplicates(subset=[date_col], keep='last')
            combined = combined.sort_values(date_col).reset_index(drop=True)
        else:
            # 如果日期列不存在，尝试用索引
            combined = combined.drop_duplicates(keep='last')
            combined = combined.sort_index().reset_index(drop=True)

        return combined

    @staticmethod
    def check_data_freshness(
        df: Optional[pd.DataFrame],
        date_col: str = 'datetime',
        trade_calendar: Optional[List[str]] = None
    ) -> DataSourceInfo:
        """检查数据新鲜度

        Args:
            df: 数据DataFrame
            date_col: 日期列名
            trade_calendar: 交易日历（可选，用于精确判断）

        Returns:
            DataSourceInfo 数据源信息
        """
        if df is None or df.empty:
            return DataSourceInfo(source_name='unknown', record_count=0)

        last_date = None
        if date_col in df.columns and len(df) > 0:
            last_val = df[date_col].iloc[-1]
            if isinstance(last_val, str):
                last_date = last_val[:10].replace('-', '')
            elif hasattr(last_val, 'strftime'):
                last_date = last_val.strftime('%Y%m%d')
            else:
                last_date = str(last_val)[:10].replace('-', '')

        # 简单判断：获取最后一个交易日
        expected_last = DataMerger._get_expected_last_trade_date()
        is_fresh = last_date is not None and last_date >= expected_last

        return DataSourceInfo(
            source_name='local',
            last_date=last_date,
            record_count=len(df),
            is_fresh=is_fresh
        )

    @staticmethod
    def _get_expected_last_trade_date() -> str:
        """获取期望的最后交易日（简化版）"""
        now = datetime.now()
        weekday = now.weekday()

        # 周末处理
        if weekday == 5:  # 周六
            last_date = now - timedelta(days=1)
        elif weekday == 6:  # 周日
            last_date = now - timedelta(days=2)
        else:
            last_date = now

        return last_date.strftime('%Y%m%d')

    @staticmethod
    def filter_by_date(
        df: Optional[pd.DataFrame],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date_col: str = 'datetime'
    ) -> Optional[pd.DataFrame]:
        """按日期过滤数据

        Args:
            df: 输入数据
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            date_col: 日期列名

        Returns:
            过滤后的数据
        """
        if df is None or df.empty:
            return df

        result = df.copy()

        if date_col not in result.columns:
            return result

        # 统一日期格式
        def normalize_date(val):
            if isinstance(val, str):
                return val[:10].replace('-', '')
            elif hasattr(val, 'strftime'):
                return val.strftime('%Y%m%d')
            return str(val)[:10].replace('-', '')

        result['_temp_date'] = result[date_col].apply(normalize_date)

        if start_date:
            result = result[result['_temp_date'] >= start_date]

        if end_date:
            result = result[result['_temp_date'] <= end_date]

        result = result.drop(columns=['_temp_date'])
        return result.reset_index(drop=True)

    @staticmethod
    def limit_count(
        df: Optional[pd.DataFrame],
        count: int,
        ascending: bool = True
    ) -> Optional[pd.DataFrame]:
        """限制数据条数

        Args:
            df: 输入数据
            count: 条数限制
            ascending: 是否按时间升序（True=取最新的count条）

        Returns:
            限制条数后的数据
        """
        if df is None or len(df) <= count:
            return df

        if ascending:
            return df.tail(count).reset_index(drop=True)
        else:
            return df.head(count).reset_index(drop=True)


class SmartDataFetcher:
    """智能数据获取器

    封装通用的"本地+在线"数据获取模式
    """

    def __init__(
        self,
        local_fetcher=None,  # 本地数据获取函数
        online_fetcher=None,  # 在线数据获取函数
        merger: Optional[DataMerger] = None
    ):
        self.local_fetcher = local_fetcher
        self.online_fetcher = online_fetcher
        self.merger = merger or DataMerger()

    def fetch(
        self,
        symbol: str,
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        **kwargs
    ) -> Optional[pd.DataFrame]:
        """智能获取数据

        策略：
        1. 日线：优先本地 + 在线补齐缺失
        2. 分钟线：直接在线（本地通常不缓存分钟线）
        """
        is_daily = period in ('1d', '1D', 'day', 'daily')

        # 非日线直接走在线
        if not is_daily:
            if self.online_fetcher:
                return self.online_fetcher(symbol, period, start_date, end_date, count, **kwargs)
            return None

        # 日线：本地 + 在线补齐
        local_df = None
        if self.local_fetcher:
            try:
                local_df = self.local_fetcher(symbol, **kwargs)
            except Exception as e:
                logger.debug(f"本地获取失败 {symbol}: {e}")

        # 检查本地数据新鲜度
        info = self.merger.check_data_freshness(local_df)

        if info.is_fresh:
            logger.debug(f"{symbol} 本地数据已最新，直接返回")
            return self.merger.limit_count(local_df, count) if count else local_df

        # 本地数据不完整，需要在线补齐
        if not self.online_fetcher:
            logger.warning(f"{symbol} 本地数据不完整且无在线获取")
            return local_df

        online_start = info.last_date if info.last_date else start_date
        logger.info(f"{symbol} 本地({info.last_date})需要补齐，在线获取从{online_start}开始")

        try:
            online_df = self.online_fetcher(
                symbol, period, online_start, end_date, count, **kwargs
            )
        except Exception as e:
            logger.error(f"在线获取失败 {symbol}: {e}")
            return local_df

        # 合并数据
        combined = self.merger.merge_kline_data(local_df, online_df)

        # 过滤和限制
        if combined is not None and not combined.empty:
            combined = self.merger.filter_by_date(combined, start_date, end_date)
            if count:
                combined = self.merger.limit_count(combined, count)

        return combined
