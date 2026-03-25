#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataManager到QLib的完整数据桥接器
将数据中枢的数据转换为QLib认识的标准格式，支持真正的回测
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import warnings

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# v9.0.0: 使用新的数据管理器和数据模型
from data.unified_data_manager import UnifiedDataManager as DataManager
from qlib_core.data_models import StockData

logger = logging.getLogger(__name__)


class QLibDataBridge:
    """
    DataManager到QLib的完整数据桥接器
    提供数据转换、格式化和导出功能
    """
    
    def __init__(self, data_hub=None, output_dir: str = "./data/qlib_data"):
        """
        初始化QLib数据桥接器

        Args:
            data_hub: DataManager实例，如果为None则创建新实例
            output_dir: QLib数据输出目录
        """
        self.data_hub = data_hub or DataManager()
        self.output_dir = Path(output_dir)
        self.cache = {}

        # 创建输出目录结构
        self._setup_qlib_directory_structure()

        # 收集所有交易日期和股票代码
        self.trading_dates = set()
        self.all_instruments = set()

        logger.info("✅ QLib数据桥接器初始化完成")
    
    def _setup_qlib_directory_structure(self):
        """创建QLib标准目录结构"""
        # 主目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 子目录结构
        subdirs = [
            "instruments",
            "calendars/txt", 
            "calendars/pickle",
            "features",
            "metadata/instruments",
            "dump_data"
        ]
        
        for subdir in subdirs:
            (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 QLib目录结构创建完成: {self.output_dir}")
    
    def prepare_sample_data(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        frequency: str = 'day'
    ) -> Dict[str, pd.DataFrame]:
        """
        准备示例数据（用于演示）
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            
        Returns:
            股票数据字典
        """
        return self.prepare_qlib_data(symbols, start_date, end_date, frequency)
    
    def convert_to_qlib_format(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        将数据字典转换为QLib格式
        
        Args:
            data: 股票数据字典
            
        Returns:
            合并的DataFrame
        """
        try:
            all_data = []
            for symbol, df in data.items():
                if not df.empty:
                    # 添加股票代码列
                    df_copy = df.copy()
                    df_copy['instrument'] = symbol
                    all_data.append(df_copy)
            
            if not all_data:
                return pd.DataFrame()
            
            # 合并数据
            result_df = pd.concat(all_data, ignore_index=False)
            
            # 设置多级索引
            result_df.reset_index(inplace=True)
            result_df.set_index(['instrument', 'date'], inplace=True)
            result_df.sort_index(inplace=True)
            
            return result_df
            
        except Exception as e:
            logger.error(f"转换为QLib格式失败: {e}")
            return pd.DataFrame()
    
    def check_data_quality(self, data: pd.DataFrame) -> Dict[str, bool]:
        """
        检查数据质量
        
        Args:
            data: 数据DataFrame
            
        Returns:
            质量检查结果
        """
        try:
            quality_report = {}
            
            # 检查数据是否为空
            quality_report['not_empty'] = not data.empty
            
            if not data.empty:
                # 检查必要字段
                required_fields = ['open', 'high', 'low', 'close', 'volume']
                quality_report['has_required_fields'] = all(
                    field in data.columns for field in required_fields
                )
                
                # 检查价格逻辑
                if all(field in data.columns for field in ['open', 'high', 'low', 'close']):
                    # 检查high >= low
                    quality_report['price_logic_high_low'] = (
                        data['high'] >= data['low']
                    ).all()
                    
                    # 检查open和close在high和low之间
                    quality_report['price_logic_open_range'] = (
                        (data['open'] >= data['low']) & 
                        (data['open'] <= data['high'])
                    ).all()
                    quality_report['price_logic_close_range'] = (
                        (data['close'] >= data['low']) & 
                        (data['close'] <= data['high'])
                    ).all()
                
                # 检查缺失值
                quality_report['no_missing_values'] = not data.isnull().any().any()
                
                # 检查数据连续性
                if 'date' in data.columns or isinstance(data.index, pd.DatetimeIndex):
                    quality_report['has_time_index'] = True
                else:
                    quality_report['has_time_index'] = False
            
            return quality_report
            
        except Exception as e:
            logger.error(f"数据质量检查失败: {e}")
            return {'error': True}
    
    def create_qlib_workflow_config(self) -> Dict[str, Any]:
        """
        创建QLib工作流配置
        
        Returns:
            配置字典
        """
        config = {
            "class": "SignalStrategy",
            "module_path": "qlib.strategy.strategy",
            "kwargs": {
                "signal": "simple_signal",
                "trade_exchange": {
                    "class": "SimuExchange",
                    "module_path": "qlib.exchange.simu",
                    "kwargs": {
                        "limit_threshold": None,
                        "deal_price": "close",
                        "open_cost": 0.0005,
                        "close_cost": 0.0015,
                        "min_cost": 5,
                    }
                }
            }
        }
        return config
    
    def prepare_qlib_data(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        frequency: str = 'day',
        fields: List[str] = None,
        forward_adjust: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        准备QLib格式的数据
        
        Args:
            instruments: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            fields: 需要的字段列表
            forward_adjust: 是否前复权
            
        Returns:
            股票数据字典 {股票代码: DataFrame}
        """
        if fields is None:
            fields = ['open', 'high', 'low', 'close', 'volume', 'amount']
        
        data_dict = {}
        
        logger.info(
            f"🔄 开始准备QLib数据: {len(instruments)} 只股票 "
            f"[{start_date} 到 {end_date}]"
        )
        
        for instrument in instruments:
            try:
                # 检查缓存
                cache_key = f"{instrument}_{start_date}_{end_date}_{frequency}"
                if cache_key in self.cache:
                    data_dict[instrument] = self.cache[cache_key]
                    continue
                
                # 从DataManager获取数据
                data = self.data_hub.get_kline_data(
                    symbol=instrument,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency
                )
                
                if not data.empty:
                    # 数据预处理和格式转换
                    qlib_data = self._convert_to_qlib_format(data, fields)
                    
                    if not qlib_data.empty:
                        # 缓存数据
                        self.cache[cache_key] = qlib_data
                        data_dict[instrument] = qlib_data
                        
                        # 收集交易日期和股票代码
                        self.trading_dates.update(
                            qlib_data.index.strftime('%Y-%m-%d')
                        )
                        self.all_instruments.add(instrument)
                        
                        logger.debug(
                            f"✅ 准备 {instrument} 数据: "
                            f"{len(qlib_data)} 条记录"
                        )
                    else:
                        logger.warning(f"⚠️ {instrument} 数据转换后为空")
                else:
                    logger.warning(f"⚠️ {instrument} 数据为空")
                    
            except Exception as e:
                logger.error(f"❌ 准备 {instrument} 数据失败: {e}")
                continue
        
        logger.info(f"✅ QLib数据准备完成: {len(data_dict)} 个股票")
        return data_dict
    
    def _convert_to_qlib_format(self, data: pd.DataFrame, fields: List[str]) -> pd.DataFrame:
        """
        将数据中枢的数据转换为QLib标准格式
        
        Args:
            data: 原始数据DataFrame
            fields: 需要的字段列表
            
        Returns:
            QLib格式DataFrame
        """
        try:
            # 确保日期索引
            if 'datetime' in data.columns:
                data['date'] = pd.to_datetime(data['datetime'])
                data.set_index('date', inplace=True)
            elif 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                data.set_index('date', inplace=True)
            
            # 确保索引是datetime类型
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
            
            # 数据类型转换和清洗
            numeric_fields = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for field in numeric_fields:
                if field in data.columns:
                    data[field] = pd.to_numeric(data[field], errors='coerce')
            
            # 处理缺失值
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            # 移除异常值（3σ规则）
            for field in ['open', 'high', 'low', 'close']:
                if field in data.columns:
                    mean = data[field].mean()
                    std = data[field].std()
                    if std > 0:
                        data[field] = np.clip(
                            data[field], mean - 3*std, mean + 3*std
                        )
            
            # 选择需要的字段
            available_fields = [f for f in fields if f in data.columns]
            if not available_fields:
                logger.warning("没有可用的字段")
                return pd.DataFrame()
            
            result_data = data[available_fields].copy()
            
            # 添加复权因子字段（如果不存在）
            if 'factor' not in result_data.columns and 'adjust_factor' in data.columns:
                result_data['factor'] = data['adjust_factor']
            elif 'factor' not in result_data.columns:
                result_data['factor'] = 1.0
            
            # 确保数据按时间排序
            result_data.sort_index(inplace=True)
            
            return result_data
            
        except Exception as e:
            logger.error(f"数据格式转换失败: {e}")
            return pd.DataFrame()
    
    def export_to_qlib_format(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        frequency: str = 'day',
        fields: List[str] = None
    ) -> bool:
        """
        导出数据为QLib标准格式
        
        Args:
            instruments: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            fields: 字段列表
            
        Returns:
            导出是否成功
        """
        try:
            logger.info("🚀 开始导出QLib格式数据...")
            
            # 1. 准备数据
            data_dict = self.prepare_qlib_data(
                instruments, start_date, end_date, frequency, fields
            )
            
            if not data_dict:
                logger.error("没有可用数据，导出失败")
                return False
            
            # 2. 导出股票数据文件
            self._export_stock_files(data_dict, frequency)
            
            # 3. 导出股票列表文件
            self._export_instruments(instruments)
            
            # 4. 导出交易日历文件
            self._export_calendar()
            
            # 5. 导出元数据
            self._export_metadata()
            
            logger.info(
                f"🎉 QLib格式数据导出完成！输出目录: {self.output_dir}"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ 导出QLib格式数据失败: {e}")
            return False
    
    def _export_stock_files(self, data_dict: Dict[str, pd.DataFrame], frequency: str):
        """导出股票数据文件 - 使用QLib标准格式"""
        try:
            # 创建features目录
            features_dir = self.output_dir / "features"
            features_dir.mkdir(parents=True, exist_ok=True)
            
            # 按股票代码和字段导出，符合QLib标准格式
            all_symbols = list(data_dict.keys())
            
            # 收集所有字段
            all_fields = set()
            for symbol, data in data_dict.items():
                if not data.empty:
                    all_fields.update(data.columns)
            
            logger.info(f"📊 发现字段: {sorted(all_fields)}")
            
            # 为每个股票和字段创建单独的二进制文件
            for symbol in all_symbols:
                if symbol not in data_dict or data_dict[symbol].empty:
                    continue
                    
                data = data_dict[symbol]
                
                # 转换股票代码为小写格式（QLib标准）
                symbol_lower = symbol.lower().replace('.', '')
                symbol_dir = features_dir / symbol_lower
                symbol_dir.mkdir(parents=True, exist_ok=True)
                
                for field in sorted(all_fields):
                    if field not in data.columns:
                        continue
                        
                    # 创建QLib标准格式的二进制文件
                    field_file_path = symbol_dir / f"{field}.{frequency}.bin"
                    
                    # 准备数据：Series with datetime index
                    if hasattr(data.index, 'to_pydatetime'):
                        dates = data.index.to_pydatetime()
                    else:
                        dates = pd.to_datetime(data.index)
                    
                    series_data = pd.Series(
                        data[field].values,
                        index=dates,
                        name=field
                    )
                    
                    # 使用QLib的标准格式保存
                    self._save_qlib_binary(series_data, field_file_path)
                
                logger.debug(f"💾 导出股票 {symbol}: {len(data)} 条记录")
            
            logger.info(f"📋 导出股票数据文件: {len(all_symbols)} 只股票")
            
        except Exception as e:
            logger.error(f"导出股票数据文件失败: {e}")
    
    def _save_qlib_binary(self, data: pd.Series, file_path: Path):
        """保存QLib标准格式的二进制文件"""
        try:
            # 确保数据是Series类型
            if not isinstance(data, pd.Series):
                raise ValueError("数据必须是pandas Series类型")
            
            # 确保索引是datetime类型
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
            
            # 转换为numpy数组，确保数据类型正确
            values = data.values.astype(np.float32)
            
            # 创建QLib标准格式的二进制文件
            # 根据QLib源码分析：
            # 1. 第一个4字节是索引（int32，但以float格式存储）
            # 2. 然后是数据值（float32）
            # 3. 使用np.hstack([index, data_array]).astype("<f")
            with open(file_path, 'wb') as f:
                # 假设索引从0开始（实际应该根据日历计算）
                # 这里简化处理，使用0作为起始索引
                start_index = 0
                
                # 按照QLib源码格式：[index, data_array]
                combined_data = np.hstack([start_index, values]).astype("<f")
                combined_data.tofile(f)
                
        except Exception as e:
            logger.error(f"保存QLib二进制文件失败: {e}")
            raise

    def _export_instruments(self, instruments: List[str]):
        """导出股票列表文件"""
        try:
            # 导出all.txt - 使用QLib标准格式
            all_file = self.output_dir / "instruments" / "all.txt"
            with open(all_file, 'w', encoding='utf-8') as f:
                for instrument in sorted(instruments):
                    # 转换为小写格式（QLib标准）
                    instrument_lower = instrument.lower().replace('.', '')
                    f.write(f"{instrument_lower}\n")
            
            # 导出csi300.txt（示例）
            csi300_instruments = [
                inst for inst in instruments
                if inst.startswith(('SH60', 'SZ00', 'SZ30'))
            ]
            if csi300_instruments:
                csi300_file = self.output_dir / "instruments" / "csi300.txt"
                with open(csi300_file, 'w', encoding='utf-8') as f:
                    for instrument in sorted(csi300_instruments):
                        instrument_lower = instrument.lower().replace('.', '')
                        f.write(f"{instrument_lower}\n")
            
            logger.info(f"📋 导出股票列表: {len(instruments)} 只股票")
            
        except Exception as e:
            logger.error(f"导出股票列表失败: {e}")
    
    def _export_calendar(self):
        """导出交易日历文件"""
        try:
            if not self.trading_dates:
                logger.warning("没有交易日期数据，跳过日历导出")
                return
            
            # 排序交易日期
            sorted_dates = sorted(list(self.trading_dates))
            
            # 转换为datetime对象
            date_objects = [pd.to_datetime(date) for date in sorted_dates]
            
            # 导出txt格式 - 确保目录存在
            txt_dir = self.output_dir / "calendars" / "txt"
            txt_dir.mkdir(parents=True, exist_ok=True)
            txt_file = txt_dir / "all.txt"
            
            with open(txt_file, 'w', encoding='utf-8') as f:
                for date_str in sorted_dates:
                    f.write(f"{date_str}\n")
            
            # 导出pickle格式
            pickle_dir = self.output_dir / "calendars" / "pickle"
            pickle_dir.mkdir(parents=True, exist_ok=True)
            pickle_file = pickle_dir / "all.pkl"
            
            with open(pickle_file, 'wb') as f:
                pickle.dump(date_objects, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # 导出day.txt（QLib标准格式）
            day_file = self.output_dir / "calendars" / "day.txt"
            with open(day_file, 'w', encoding='utf-8') as f:
                for date_obj in date_objects:
                    f.write(f"{date_obj.strftime('%Y-%m-%d')}\n")
            
            logger.info(f"📅 导出交易日历: {len(sorted_dates)} 个交易日")
            
        except Exception as e:
            logger.error(f"导出交易日历失败: {e}")
    
    def _export_metadata(self):
        """导出元数据文件"""
        try:
            metadata = {
                'instruments': sorted(list(self.all_instruments)),
                'trading_days_count': len(self.trading_dates),
                'instruments_count': len(self.all_instruments),
                'export_time': datetime.now().isoformat(),
                'format_version': '1.0',
                'data_source': 'DataManagerV2'
            }
            
            metadata_file = (
                self.output_dir / "metadata" / "instruments" / "all.pkl"
            )
            with open(metadata_file, 'wb') as f:
                pickle.dump(metadata, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            logger.info("📊 导出元数据完成")
            
        except Exception as e:
            logger.error(f"导出元数据失败: {e}")
    
    def get_qlib_dataset(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        fields: List[str] = None
    ) -> pd.DataFrame:
        """
        获取QLib格式的数据集（用于回测）
        
        Args:
            instruments: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            fields: 字段列表
            
        Returns:
            多级索引的DataFrame (instrument, datetime)
        """
        try:
            # 准备数据
            data_dict = self.prepare_qlib_data(
                instruments, start_date, end_date, fields=fields
            )
            
            if not data_dict:
                return pd.DataFrame()
            
            # 合并所有股票数据
            all_data = []
            for symbol, data in data_dict.items():
                if not data.empty:
                    # 添加股票代码列
                    data_copy = data.copy()
                    data_copy['instrument'] = symbol
                    all_data.append(data_copy)
            
            if not all_data:
                return pd.DataFrame()
            
            # 合并数据
            result_df = pd.concat(all_data, ignore_index=False)
            
            # 设置多级索引
            result_df.reset_index(inplace=True)
            result_df.set_index(['instrument', 'date'], inplace=True)
            result_df.sort_index(inplace=True)
            
            logger.info(f"✅ 获取QLib数据集: {result_df.shape}")
            return result_df
            
        except Exception as e:
            logger.error(f"获取QLib数据集失败: {e}")
            return pd.DataFrame()
    
    def create_qlib_config(self, market: str = "cn") -> bool:
        """
        创建QLib配置文件
        
        Args:
            market: 市场类型
            
        Returns:
            创建是否成功
        """
        try:
            config = {
                "provider_uri": str(self.output_dir.absolute()),
                "region": market,
                "calendar_cache": "calendars/pickle/all.pkl",
                "feature_cache": "features",
                "instruments_cache": "instruments/all.txt"
            }
            
            config_file = self.output_dir / "qlib_config.yaml"
            import yaml
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"⚙️ 创建QLib配置文件: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"创建QLib配置文件失败: {e}")
            return False
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.trading_dates.clear()
        self.all_instruments.clear()
        logger.info("🧹 缓存已清空")


# 便捷函数
def create_qlib_bridge(data_hub=None, output_dir: str = "./data/qlib_data") -> QLibDataBridge:
    """
    创建QLib数据桥接器实例
    
    Args:
        data_hub: 数据中枢实例
        output_dir: 输出目录
        
    Returns:
        QLibDataBridge实例
    """
    return QLibDataBridge(data_hub, output_dir)


def get_qlib_bridge(data_hub=None, output_dir: str = "./data/qlib_data") -> QLibDataBridge:
    """
    获取QLib数据桥接器实例（别名函数）

    Args:
        data_hub: 数据中枢实例
        output_dir: 输出目录

    Returns:
        QLibDataBridge实例
    """
    return create_qlib_bridge(data_hub, output_dir)


# 向后兼容别名
QLibBridge = QLibDataBridge


def export_to_qlib(
    instruments: List[str],
    start_date: str,
    end_date: str,
    output_dir: str = "./data/qlib_data",
    frequency: str = 'day',
    fields: List[str] = None
) -> bool:
    """
    便捷函数：导出数据到QLib格式
    
    Args:
        instruments: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
        output_dir: 输出目录
        frequency: 数据频率
        fields: 字段列表
        
    Returns:
        导出是否成功
    """
    bridge = create_qlib_bridge(output_dir=output_dir)
    return bridge.export_to_qlib_format(
        instruments, start_date, end_date, frequency, fields
    )


if __name__ == "__main__":
    # 测试QLib数据桥接器
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("测试QLib数据桥接器")
    print("=" * 70)
    
    try:
        # 创建桥接器
        bridge = create_qlib_bridge(output_dir="./data/qlib_data")
        
        # 测试股票列表
        test_instruments = [
            "000001.SZ", "000002.SZ", "000858.SZ",
            "600000.SH", "600036.SH", "600519.SH"
        ]
        
        # 测试数据准备
        print("🔄 测试数据准备...")
        data_dict = bridge.prepare_qlib_data(
            test_instruments[:3],  # 只测试前3只股票
            "2024-01-01",
            "2024-01-10"
        )
        
        print(f"✅ 数据准备完成: {len(data_dict)} 个股票")
        for symbol, data in data_dict.items():
            print(f"   {symbol}: {data.shape}")
        
        # 测试完整导出
        print("\n🚀 测试完整导出...")
        export_success = bridge.export_to_qlib_format(
            test_instruments,
            "2024-01-01",
            "2024-01-10"
        )
        
        if export_success:
            print("✅ QLib格式导出成功")
            
            # 测试配置文件创建
            config_success = bridge.create_qlib_config()
            if config_success:
                print("✅ QLib配置文件创建成功")
            else:
                print("❌ QLib配置文件创建失败")
        else:
            print("❌ QLib格式导出失败")
        
        print("\n🎉 QLib数据桥接器测试完成")
        
    except Exception as e:
        print(f"❌ QLib数据桥接器测试失败: {e}")
        import traceback
        traceback.print_exc()