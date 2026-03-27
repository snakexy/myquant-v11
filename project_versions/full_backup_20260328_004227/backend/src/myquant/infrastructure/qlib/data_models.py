#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QLib核心层数据模型
提供QLib相关的基础数据结构
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import pandas as pd
import numpy as np


@dataclass
class StockData:
    """
    股票数据模型
    用于QLib数据交换
    """
    symbol: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = 0.0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'date': self.date,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'amount': self.amount
        }

    @staticmethod
    def to_dataframe(stock_data_list: List['StockData']) -> pd.DataFrame:
        """
        将StockData列表转换为DataFrame

        Args:
            stock_data_list: StockData对象列表

        Returns:
            pandas DataFrame
        """
        if not stock_data_list:
            return pd.DataFrame()

        data = [item.to_dict() for item in stock_data_list]
        df = pd.DataFrame(data)

        # 确保日期列是datetime类型
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        return df

    @staticmethod
    def from_dataframe(df: pd.DataFrame, symbol_col: str = 'symbol') -> List['StockData']:
        """
        从DataFrame创建StockData列表

        Args:
            df: pandas DataFrame
            symbol_col: 股票代码列名

        Returns:
            StockData对象列表
        """
        result = []

        for _, row in df.iterrows():
            symbol = row.get(symbol_col, row.get('instrument', ''))
            result.append(StockData(
                symbol=str(symbol),
                date=str(row.get('date', row.get('datetime', ''))),
                open=float(row.get('open', 0)),
                high=float(row.get('high', 0)),
                low=float(row.get('low', 0)),
                close=float(row.get('close', 0)),
                volume=float(row.get('volume', 0)),
                amount=float(row.get('amount', 0))
            ))

        return result


@dataclass
class PortfolioData:
    """
    投资组合数据模型
    """
    date: str
    positions: dict  # {symbol: weight}
    cash: float
    total_value: float

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'date': self.date,
            'positions': self.positions,
            'cash': self.cash,
            'total_value': self.total_value
        }


@dataclass
class BacktestResult:
    """
    回测结果数据模型
    """
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    nav_curve: List[float]
    dates: List[str]

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'nav_curve': self.nav_curve,
            'dates': self.dates
        }
