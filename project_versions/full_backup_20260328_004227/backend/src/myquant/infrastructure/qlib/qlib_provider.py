#!/usr/bin/env python3
"""
QLib数据提供器
完全兼容QLib框架的数据提供器接口
使用我们的数据中枢作为数据源
"""

import os
import sys
import logging
import pandas as pd
from typing import List, Dict, Union
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# v9.0.0: 使用新的数据管理器和数据模型
from data.unified_data_manager import UnifiedDataManager as DataManager
from qlib_core.data_models import StockData

logger = logging.getLogger(__name__)


class QLibDataProvider:
    """
    QLib标准数据提供器
    实现QLib要求的所有数据接口
    """

    def __init__(self, config: Dict = None):
        """初始化数据提供器"""
        self.config = config or {}
        self.data_provider = DataManager()
        self._cache = {}

        logger.info("QLib数据提供器初始化完成")
    
    def list_instruments(
        self,
        market: str = "cn",
        start_time: str = None,
        end_time: str = None,
        freq: str = "day",
        instruments: List[str] = None
    ) -> List[str]:
        """
        获取股票列表 - QLib标准接口
        """
        try:
            # 如果提供了instruments参数，直接返回
            if instruments is not None:
                logger.info(f"使用提供的股票列表: {len(instruments)} 只")
                return instruments
            
            # 使用我们的数据中枢获取股票列表
            # 这里可以扩展为从数据库或配置文件中获取
            default_instruments = [
                "000001.SZ", "000002.SZ", "000858.SZ", "000333.SZ",
                "600000.SH", "600036.SH", "601318.SH", "601888.SH",
                "000651.SZ", "300750.SZ", "603288.SH", "600519.SH"
            ]
            
            logger.info(f"获取到 {len(default_instruments)} 只股票")
            return default_instruments
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    def get_calendar(
        self, 
        market: str = "cn", 
        start_time: str = None,
        end_time: str = None,
        freq: str = "day"
    ) -> List[str]:
        """
        获取交易日历 - QLib标准接口
        """
        try:
            if start_time is None:
                start_time = "2020-01-01"
            if end_time is None:
                end_time = datetime.now().strftime('%Y-%m-%d')
            
            # 使用示例数据生成交易日历
            sample_data = self._get_sample_data_for_calendar()
            if not sample_data.empty:
                dates = sorted(list(
                    set(sample_data.index.strftime('%Y-%m-%d'))
                ))
                return dates
            
            # 生成默认交易日历
            return self._generate_default_calendar(start_time, end_time)
            
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return self._generate_default_calendar(start_time, end_time)
    
    def get_features(
        self,
        instruments: List[str],
        fields: List[str],
        start_time: str,
        end_time: str,
        freq: str = "day"
    ) -> pd.DataFrame:
        """
        获取特征数据 - QLib标准接口
        """
        try:
            all_data = []
            
            for symbol in instruments:
                # 获取股票数据
                stock_data = self._get_stock_data(
                    symbol, start_time, end_time, fields
                )
                
                if not stock_data.empty:
                    # 添加股票代码列
                    stock_data['instrument'] = symbol
                    all_data.append(stock_data)
            
            if all_data:
                result_df = pd.concat(all_data)
                # 设置多级索引 (instrument, datetime)
                if ('instrument' in result_df.columns and
                        'datetime' in result_df.columns):
                    result_df.set_index(
                        ['instrument', 'datetime'], inplace=True
                    )
                
                logger.info(f"成功获取 {len(instruments)} 只股票的特征数据")
                return result_df
            else:
                logger.warning("未获取到任何特征数据")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取特征数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        frequency: str = 'day',
        forward_adjust: bool = True,
        return_dataframe: bool = True
    ) -> Union[List[StockData], pd.DataFrame]:
        """
        获取股票数据 - 支持DataFrame返回格式
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            forward_adjust: 是否前复权
            return_dataframe: 是否返回DataFrame格式
            
        Returns:
            StockData列表或DataFrame
        """
        try:
            # 使用DataManagerV2获取数据
            if return_dataframe:
                data = self.data_provider.get_kline_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency
                )
                return data if data is not None else pd.DataFrame()
            else:
                # 返回StockData列表格式（向后兼容）
                kline_data = self.data_provider.get_kline_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency
                )
                if kline_data is None or kline_data.empty:
                    return []
                # 转换为StockData列表
                stock_data_list = []
                for _, row in kline_data.iterrows():
                    stock_data_list.append(StockData(
                        symbol=symbol,
                        date=row.get('date', row.name.strftime('%Y-%m-%d') if hasattr(row.name, 'strftime') else row.name),
                        open=row.get('open', 0),
                        high=row.get('high', 0),
                        low=row.get('low', 0),
                        close=row.get('close', 0),
                        volume=row.get('volume', 0),
                        amount=row.get('amount', 0)
                    ))
                return stock_data_list
            
            return data
            
        except Exception as e:
            logger.error(f"获取股票数据失败 {symbol}: {e}")
            return [] if not return_dataframe else pd.DataFrame()

    def _get_stock_data(
        self,
        symbol: str,
        start_time: str,
        end_time: str,
        fields: List[str]
    ) -> pd.DataFrame:
        """获取单只股票数据"""
        try:
            # 使用DataManagerV2获取数据
            stock_data_df = self.data_provider.get_kline_data(
                symbol=symbol,
                start_date=start_time,
                end_date=end_time,
                frequency='day'
            )

            if stock_data_df is None or stock_data_df.empty:
                logger.warning(f"未找到股票 {symbol} 的数据")
                return pd.DataFrame()

            df = stock_data_df.copy()
            
            # 设置日期索引
            if 'date' in df.columns:
                df['datetime'] = pd.to_datetime(df['date'])
                df.set_index('datetime', inplace=True)
            
            # 字段映射到QLib标准字段
            field_mapping = {
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'amount': 'amount',
                'factor': 'factor'
            }
            
            # 选择需要的字段
            available_fields = []
            for field in fields:
                our_field = field_mapping.get(field, field)
                if our_field in df.columns:
                    available_fields.append(our_field)
                else:
                    logger.warning(f"字段 {field} 不可用")
            
            if available_fields:
                result_df = df[available_fields].copy()
                # 重命名字段为QLib标准名称
                reverse_mapping = {v: k for k, v in field_mapping.items()}
                result_df.rename(columns=reverse_mapping, inplace=True)
                return result_df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取股票数据失败 {symbol}: {e}")
            return pd.DataFrame()
    
    def _get_sample_data_for_calendar(self) -> pd.DataFrame:
        """获取用于生成交易日历的示例数据"""
        try:
            # 尝试获取一只股票的数据来提取日期
            sample_data = self.data_provider.get_kline_data(
                symbol="SZ000001",
                start_date="2024-01-01",
                end_date="2024-01-10"
            )
            
            if sample_data is not None and not sample_data.empty:
                if 'date' in sample_data.columns:
                    sample_data['date'] = pd.to_datetime(sample_data['date'])
                    sample_data.set_index('date', inplace=True)
                return sample_data
            else:
                return pd.DataFrame()
                
        except Exception:
            return pd.DataFrame()
    
    def _generate_default_calendar(
        self, 
        start_time: str, 
        end_time: str
    ) -> List[str]:
        """生成默认交易日历"""
        try:
            dates = []
            current = datetime.strptime(start_time, '%Y-%m-%d')
            end = datetime.strptime(end_time, '%Y-%m-%d')
            
            while current <= end:
                if current.weekday() < 5:  # 周一到周五
                    dates.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
            
            return dates
            
        except Exception as e:
            logger.error(f"生成默认交易日历失败: {e}")
            return []
    
    def is_available(self) -> bool:
        """
        检查数据提供器是否可用
        
        Returns:
            是否可用
        """
        try:
            # 执行一个简单的测试来验证数据获取功能
            try:
                test_data = self.data_provider.get_kline_data(
                    symbol="SZ000001",
                    start_date="2024-01-01",
                    end_date="2024-01-02"
                )
                if (test_data is None or
                        (hasattr(test_data, 'empty') and test_data.empty)):
                    logger.warning("数据获取测试失败")
                    return False
            except Exception as e:
                logger.warning(f"数据获取测试异常: {e}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"QLib数据提供器可用性检查失败: {e}")
            return False

    def validate(self) -> bool:
        """验证数据提供器是否正常工作"""
        try:
            # 测试获取股票列表
            instruments = self.list_instruments()
            if not instruments:
                logger.error("验证失败：无法获取股票列表")
                return False
            
            # 测试获取交易日历
            calendar = self.get_calendar()
            if not calendar:
                logger.error("验证失败：无法获取交易日历")
                return False
            
            # 测试获取特征数据
            if instruments:
                test_symbol = instruments[0]
                features = self.get_features(
                    [test_symbol],
                    ['close'],
                    '2024-01-01',
                    '2024-01-10'
                )
                if features.empty:
                    logger.error("验证失败：无法获取特征数据")
                    return False
            
            logger.info("QLib数据提供器验证通过")
            return True
            
        except Exception as e:
            logger.error(f"数据提供器验证失败: {e}")
            return False


# QLib兼容的工厂函数
def create_qlib_provider(config: Dict = None) -> QLibDataProvider:
    """创建QLib数据提供器实例"""
    return QLibDataProvider(config)


if __name__ == "__main__":
    # 测试数据提供器
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 50)
    print("测试QLib数据提供器")
    print("=" * 50)
    
    provider = create_qlib_provider()
    
    # 验证数据提供器
    if provider.validate():
        print("✅ QLib数据提供器验证通过")
        
        # 测试获取股票列表
        instruments = provider.list_instruments()
        print(f"股票列表: {len(instruments)} 只")
        
        # 测试获取交易日历
        calendar = provider.get_calendar("2024-01-01", "2024-01-10")
        print(f"交易日历样本: {calendar[:5]} ...")
        
        # 测试获取特征数据
        if instruments:
            test_symbols = instruments[:3]  # 测试前3只股票
            features = provider.get_features(
                test_symbols,
                ['open', 'high', 'low', 'close', 'volume'],
                '2024-01-01',
                '2024-01-10'
            )
            if not features.empty:
                print(f"特征数据形状: {features.shape}")
                print("特征数据样本:")
                print(features.head())
            else:
                print("❌ 获取特征数据失败")
        
        print("🎉 QLib数据提供器测试完成")
    else:
        print("❌ QLib数据提供器验证失败")