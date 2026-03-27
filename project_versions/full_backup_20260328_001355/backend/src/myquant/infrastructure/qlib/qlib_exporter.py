#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataManager到QLib数据格式导出器
将DataManager数据转换为QLib兼容格式
"""

import os
import pickle
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import logging

# v9.0.0: 使用新的数据模型
from qlib_core.data_models import StockData

logger = logging.getLogger(__name__)


class QLibExporter:
    """QLib数据格式导出器"""

    def __init__(self, output_dir: str = "./data/qlib_data"):
        """
        初始化QLib导出器

        Args:
            output_dir: QLib数据输出目录
        """
        self.output_dir = Path(output_dir)
        self.setup_directory_structure()

        # 收集所有交易日期
        self.trading_dates: Set[str] = set()

        # 收集所有股票代码
        self.all_instruments: Set[str] = set()

    def setup_directory_structure(self):
        """创建QLib标准目录结构"""
        # 主目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 子目录
        subdirs = [
            "calendars/txt",
            "calendars/pickle",
            "features",
            "instruments",
            "metadata/instruments"
        ]

        for subdir in subdirs:
            (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)

        logger.info(f"QLib目录结构创建完成: {self.output_dir}")

    def export_stock_data(
        self,
        stock_data_list: List[StockData],
        frequency: str = "day"
    ) -> bool:
        """
        导出股票数据到QLib格式

        Args:
            stock_data_list: 股票数据列表
            frequency: 数据频率 (day, 1h, 5m等)

        Returns:
            导出是否成功
        """
        try:
            if not stock_data_list:
                logger.warning("股票数据为空，跳过导出")
                return False

            # 按股票代码分组
            data_by_symbol = {}
            for stock_data in stock_data_list:
                if stock_data.symbol not in data_by_symbol:
                    data_by_symbol[stock_data.symbol] = []
                data_by_symbol[stock_data.symbol].append(stock_data)

                # 收集交易日期和股票代码
                self.trading_dates.add(stock_data.date)
                self.all_instruments.add(stock_data.symbol)

            # 导出每只股票的数据
            for symbol, symbol_data in data_by_symbol.items():
                self._export_symbol_data(symbol, symbol_data, frequency)

            logger.info(f"成功导出 {len(data_by_symbol)} 只股票的数据")
            return True

        except Exception as e:
            logger.error(f"导出股票数据失败: {e}")
            return False

    def _export_symbol_data(
        self,
        symbol: str,
        symbol_data: List[StockData],
        frequency: str
    ):
        """导出单只股票的数据"""
        try:
            # 转换为DataFrame
            df = pd.DataFrame([{
                'date': pd.to_datetime(stock_data.date),
                'open': stock_data.open,
                'high': stock_data.high,
                'low': stock_data.low,
                'close': stock_data.close,
                'volume': stock_data.volume,
                'factor': stock_data.adjust_factor or 1.0,
                'amount': stock_data.amount or 0.0
            } for stock_data in symbol_data])

            # 按日期排序
            df = df.sort_values('date')
            df.set_index('date', inplace=True)

            # 转换为QLib格式 (字典格式)
            qlib_data = {
                'open': df['open'],
                'high': df['high'],
                'low': df['low'],
                'close': df['close'],
                'volume': df['volume'],
                'factor': df['factor'],
                'amount': df['amount']  # 额外字段
            }

            # 创建股票目录
            symbol_dir = self.output_dir / "features" / symbol
            symbol_dir.mkdir(parents=True, exist_ok=True)

            # 保存为pickle文件
            output_file = symbol_dir / f"{frequency}.pkl"
            with open(output_file, 'wb') as f:
                pickle.dump(qlib_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.debug(f"导出 {symbol} 数据到: {output_file}")

        except Exception as e:
            logger.error(f"导出 {symbol} 数据失败: {e}")

    def export_instruments(self, instruments: List[str] = None):
        """导出股票代码列表"""
        try:
            if instruments is None:
                instruments = sorted(list(self.all_instruments))

            # 导出all.txt
            all_file = self.output_dir / "instruments" / "all.txt"
            with open(all_file, 'w', encoding='utf-8') as f:
                for instrument in instruments:
                    f.write(f"{instrument}\n")

            # 创建CSI300列表 (示例)
            csi300_instruments = [inst for inst in instruments if inst.startswith(('SH60', 'SZ00', 'SZ30'))]
            if csi300_instruments:
                csi300_file = self.output_dir / "instruments" / "csi300.txt"
                with open(csi300_file, 'w', encoding='utf-8') as f:
                    for instrument in csi300_instruments:
                        f.write(f"{instrument}\n")

            logger.info(f"导出股票列表: {len(instruments)} 只股票")

        except Exception as e:
            logger.error(f"导出股票列表失败: {e}")

    def export_calendar(self):
        """导出交易日历"""
        try:
            if not self.trading_dates:
                logger.warning("没有交易日期数据，跳过日历导出")
                return

            # 排序交易日期
            sorted_dates = sorted(list(self.trading_dates))

            # 转换为datetime格式
            date_objects = [pd.to_datetime(date) for date in sorted_dates]

            # 导出txt格式
            txt_file = self.output_dir / "calendars" / "txt" / "all.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                for date_str in sorted_dates:
                    f.write(f"{date_str}\n")

            # 导出pickle格式
            pickle_file = self.output_dir / "calendars" / "pickle" / "all.pkl"
            with open(pickle_file, 'wb') as f:
                pickle.dump(date_objects, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.info(f"导出交易日历: {len(sorted_dates)} 个交易日")

        except Exception as e:
            logger.error(f"导出交易日历失败: {e}")

    def export_metadata(self):
        """导出元数据"""
        try:
            metadata = {
                'instruments': sorted(list(self.all_instruments)),
                'trading_days_count': len(self.trading_dates),
                'instruments_count': len(self.all_instruments),
                'export_time': datetime.now().isoformat(),
                'format_version': '1.0'
            }

            metadata_file = self.output_dir / "metadata" / "instruments" / "all.pkl"
            with open(metadata_file, 'wb') as f:
                pickle.dump(metadata, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.info("导出元数据完成")

        except Exception as e:
            logger.error(f"导出元数据失败: {e}")

    def complete_export(self, stock_data_list: List[StockData]) -> bool:
        """完整导出流程"""
        try:
            logger.info("开始QLib格式完整导出...")

            # 1. 导出股票数据
            success1 = self.export_stock_data(stock_data_list)

            # 2. 导出股票列表
            self.export_instruments()

            # 3. 导出交易日历
            self.export_calendar()

            # 4. 导出元数据
            self.export_metadata()

            if success1:
                logger.info(f"QLib格式导出完成！输出目录: {self.output_dir}")
                return True
            else:
                logger.error("QLib格式导出失败")
                return False

        except Exception as e:
            logger.error(f"完整导出失败: {e}")
            return False


def export_quantdatahub_to_qlib(
    stock_data_list: List[StockData],
    output_dir: str = "./data/qlib_data"
) -> bool:
    """
    便捷函数：导出DataManager数据到QLib格式

    Args:
        stock_data_list: 股票数据列表
        output_dir: 输出目录

    Returns:
        导出是否成功
    """
    exporter = QLibExporter(output_dir)
    return exporter.complete_export(stock_data_list)


# 使用示例
if __name__ == "__main__":
    # 示例数据
    sample_data = [
        StockData(
            symbol="000858.SZ",
            date="2025-11-27",
            open=118.0,
            high=118.5,
            low=117.5,
            close=117.94,
            volume=92157.0,
            amount=1087247000.0,
            adjust_factor=1.0
        )
    ]

    # 导出到QLib格式
    success = export_quantdatahub_to_qlib(sample_data)
    print(f"导出结果: {'成功' if success else '失败'}")