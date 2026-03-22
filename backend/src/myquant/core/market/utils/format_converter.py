# -*- coding: utf-8 -*-
"""
V5 数据格式转换工具

从 V4 DataFormatConverter 提取 V5 适配器需要的部分
不依赖 V4 代码，完全独立
"""

from typing import Any
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime


class FormatConverter:
    """
    V5 数据格式转换工具

    将 PyTdx、XtQuant、TdxQuant、LocalDB 等不同数据源的格式
    统一转换为标准格式
    """

    # ===== K线数据转换 =====

    @staticmethod
    def normalize_kline(df: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        将不同源的K线DataFrame转换为统一格式

        统一列名: datetime, open, high, low, close, volume, amount
        """
        try:
            if df is None or len(df) == 0:
                return df

            if source == "pytdx":
                return FormatConverter._pytdx_kline_to_standard(df)
            elif source == "xtquant":
                return FormatConverter._xtquant_kline_to_standard(df)
            elif source == "localdb":
                return FormatConverter._localdb_kline_to_standard(df)
            elif source == "tdxquant":
                return FormatConverter._tdxquant_kline_to_standard(df)
            elif source == "tdxlocal":
                return FormatConverter._tdxlocal_kline_to_standard(df)
            else:
                return df

        except Exception as e:
            logger.error(f"K线数据转换失败 ({source}): {e}")
            return df

    @staticmethod
    def _pytdx_kline_to_standard(df: pd.DataFrame) -> pd.DataFrame:
        """PyTdx K线 → 标准格式

        PyTdx K线成交量单位：手（100股）
        """
        # PyTdx返回的列名: datetime, open, close, high, low, vol, amount
        column_mapping = {
            'datetime': 'datetime',
            'open': 'open',
            'close': 'close',
            'high': 'high',
            'low': 'low',
            'vol': 'volume',      # vol → volume
            'amount': 'amount'
        }

        # 重命名列
        df_normalized = df.rename(columns=column_mapping)

        # PyTdx K线成交量单位是"手"，保持不变

        # 确保有标准列
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']
        for col in required_columns:
            if col not in df_normalized.columns:
                df_normalized[col] = None

        # 按标准列顺序返回
        return df_normalized[required_columns]

    @staticmethod
    def _xtquant_kline_to_standard(df: pd.DataFrame) -> pd.DataFrame:
        """XtQuant K线 → 标准格式"""
        # 列名映射
        column_mapping = {
            'time': 'datetime',
            'datetime': 'datetime',
            'open': 'open',
            'close': 'close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume',
            'vol': 'volume',
            'amount': 'amount',
            'turnover': 'amount'
        }

        # 重命名列
        df_normalized = df.rename(columns=column_mapping)

        # XtQuant返回的datetime列可能是numeric毫秒时间戳，需要转换
        if 'datetime' in df_normalized.columns and not df_normalized['datetime'].isna().all():
            # 检查是否是numeric类型（毫秒时间戳）
            first_val = df_normalized['datetime'].iloc[0] if len(df_normalized) > 0 else None
            if isinstance(first_val, (int, float, np.number)) and first_val > 100000000000:
                # 这是毫秒时间戳（如 1773072000000），转换为datetime对象
                df_normalized['datetime'] = pd.to_datetime(df_normalized['datetime'], unit='ms', errors='coerce')

        # XtQuant K线成交量单位已经是"手"，保持不变

        # 按标准列顺序返回（确保列存在）
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']
        for col in required_columns:
            if col not in df_normalized.columns:
                df_normalized[col] = None

        return df_normalized[required_columns]

    @staticmethod
    def _tdxquant_kline_to_standard(df: pd.DataFrame) -> pd.DataFrame:
        """TdxQuant K线 → 标准格式

        TdxQuant K线成交量单位：手（100股）
        """
        # 列名映射（TdxQuant使用PascalCase）
        column_mapping = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Amount': 'amount'
        }

        # 重命名列
        df_normalized = df.rename(columns=column_mapping)

        # 确保有标准列
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']
        for col in required_columns:
            if col not in df_normalized.columns:
                if col == 'datetime' and df_normalized.index.name:
                    # 使用索引作为datetime
                    df_normalized.reset_index(inplace=True)
                    df_normalized.rename(columns={df_normalized.columns[0]: 'datetime'}, inplace=True)
                else:
                    df_normalized[col] = None

        # 确保datetime列是datetime类型
        if 'datetime' in df_normalized.columns:
            df_normalized['datetime'] = pd.to_datetime(df_normalized['datetime'])

        # 如果 datetime 是索引，重置为普通列（避免歧义）
        if df_normalized.index.name == 'datetime':
            df_normalized.reset_index(inplace=True)

        # 按标准列顺序返回
        available_columns = [col for col in required_columns if col in df_normalized.columns]
        return df_normalized[available_columns]

    @staticmethod
    def _localdb_kline_to_standard(df: pd.DataFrame) -> pd.DataFrame:
        """LocalDB K线 → 标准格式"""
        # LocalDB使用$前缀，需要去除
        column_mapping = {
            '$open': 'open',
            '$high': 'high',
            '$low': 'low',
            '$close': 'close',
            '$volume': 'volume',
            '$amount': 'amount',
            '$vwap': 'vwap'
        }

        # 重命名列
        df_normalized = df.rename(columns=column_mapping)

        # LocalDB 的 volume 字段为0（无成交量数据），amount 字段为成交额
        # 无需单位转换

        # 确保有标准列
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']
        for col in required_columns:
            if col not in df_normalized.columns:
                df_normalized[col] = None

        return df_normalized[required_columns]

    @staticmethod
    def _tdxlocal_kline_to_standard(df: pd.DataFrame) -> pd.DataFrame:
        """TdxLocal K线 → 标准格式（已经是标准格式）"""
        # TdxLocal读取的.day文件已经是标准格式
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        return df[required_columns]

    # ===== 行情数据转换 =====

    @staticmethod
    def normalize_quote(source_data: dict, source: str, code: str = None) -> dict:
        """
        将不同源的L1数据转换为统一格式

        Args:
            source_data: 原始数据
            source: 数据源（pytdx/xtquant/localdb/tdxquant）
            code: 股票代码

        Returns:
            统一格式的L1快照数据
        """
        try:
            if source == "pytdx":
                return FormatConverter._pytdx_to_l1(source_data, code)
            elif source == "xtquant":
                return FormatConverter._xtquant_to_l1(source_data, code)
            elif source == "localdb":
                return FormatConverter._localdb_to_l1(source_data, code)
            elif source == "tdxquant":
                return FormatConverter._tdxquant_to_l1(source_data, code)
            else:
                logger.warning(f"未知数据源: {source}")
                return {}

        except Exception as e:
            logger.error(f"L1数据转换失败 ({source}): {e}")
            return {}

    @staticmethod
    def _pytdx_to_l1(data: dict, code: str = None) -> dict:
        """PyTdx → L1统一格式

        PyTdx L1成交量单位：手（100股）
        """
        price = data.get('price', 0) or 0
        last_close = data.get('last_close', 0) or 0
        change = price - last_close
        change_pct = (change / last_close * 100) if last_close > 0 else 0

        result = {
            # 基础信息
            'code': code,
            'name': data.get('name', ''),

            # 价格信息
            'price': price,
            'open': data.get('open', 0),
            'high': data.get('high', 0),
            'low': data.get('low', 0),
            'last_close': last_close,
            'change': change,
            'change_pct': round(change_pct, 2),

            # 成交信息（PyTdx L1成交量单位已经是"手"）
            'volume': data.get('volume', 0),           # vol → volume（手）
            'amount': data.get('amount', 0),
            'turnover': None,                           # PyTdx无换手率

            # 买卖盘
            'bid1': data.get('bid1'),
            'bid_vol1': data.get('bid_vol1'),
            'ask1': data.get('ask1'),
            'ask_vol1': data.get('ask_vol1'),
            'bid2': data.get('bid2'),
            'bid_vol2': data.get('bid_vol2'),
            'ask2': data.get('ask2'),
            'ask_vol2': data.get('ask_vol2'),
            'bid3': data.get('bid3'),
            'bid_vol3': data.get('bid_vol3'),
            'ask3': data.get('ask3'),
            'ask_vol3': data.get('ask_vol3'),
            'bid4': data.get('bid4'),
            'bid_vol4': data.get('bid_vol4'),
            'ask4': data.get('ask4'),
            'ask_vol4': data.get('ask_vol4'),
            'bid5': data.get('bid5'),
            'bid_vol5': data.get('bid_vol5'),
            'ask5': data.get('ask5'),
            'ask_vol5': data.get('ask_vol5'),

            # 时间戳
            'timestamp': data.get('timestamp', ''),
            'date': data.get('timestamp', '').split(' ')[0] if data.get('timestamp') else '',
            'time': data.get('timestamp', '').split(' ')[1] if len(data.get('timestamp', '').split(' ')) > 1 else ''
        }

        return result

    @staticmethod
    def _xtquant_to_l1(data: dict, code: str = None) -> dict:
        """
        XtQuant → L1统一格式

        XtQuant L1成交量单位：手（100股）
        """
        price = data.get('lastPrice', data.get('price', 0))
        last_close = data.get('lastClose', data.get('last_close', 0))
        change = price - last_close
        change_pct = (change / last_close * 100) if last_close > 0 else 0

        # XtQuant L1成交量单位已经是"手"，无需转换
        volume = data.get('volume', data.get('vol', 0))

        result = {
            # 基础信息
            'code': code,
            'name': data.get('name', ''),

            # 价格信息
            'price': price,
            'open': data.get('open', data.get('openPrice', 0)),
            'high': data.get('high', data.get('highPrice', 0)),
            'low': data.get('low', data.get('lowPrice', 0)),
            'last_close': last_close,
            'change': change,
            'change_pct': round(change_pct, 2),

            # 成交信息（已转换为手）
            'volume': volume,
            'amount': data.get('amount', data.get('turnover', 0)),
            'turnover': data.get('turnoverRate', None),

            # 买卖盘
            'bid1': data.get('bidPrice1'),
            'bid_vol1': data.get('bidVol1'),
            'ask1': data.get('askPrice1'),
            'ask_vol1': data.get('askVol1'),
            'bid2': data.get('bidPrice2'),
            'bid_vol2': data.get('bidVol2'),
            'ask2': data.get('askPrice2'),
            'ask_vol2': data.get('askVol2'),
            'bid3': data.get('bidPrice3'),
            'bid_vol3': data.get('bidVol3'),
            'ask3': data.get('askPrice3'),
            'ask_vol3': data.get('askVol3'),
            'bid4': data.get('bidPrice4'),
            'bid_vol4': data.get('bidVol4'),
            'ask4': data.get('askPrice4'),
            'ask_vol4': data.get('askVol4'),
            'bid5': data.get('bidPrice5'),
            'bid_vol5': data.get('bidVol5'),
            'ask5': data.get('askPrice5'),
            'ask_vol5': data.get('askVol5'),

            # 时间戳
            'timestamp': data.get('time', ''),
            'date': data.get('time', '').split(' ')[0] if data.get('time') else '',
            'time': data.get('time', '').split(' ')[1] if len(data.get('time', '').split(' ')) > 1 else ''
        }

        return result

    @staticmethod
    def _localdb_to_l1(data: dict, code: str = None) -> dict:
        """LocalDB → L1统一格式"""
        # LocalDB通常已经归档，直接返回
        return data

    @staticmethod
    def _tdxquant_to_l1(data: dict, code: str = None) -> dict:
        """
        TdxQuant → L1统一格式

        TdxQuant L1成交量单位：手（100股）
        额外指标（换手率等）由服务层通过 get_more_info() 获取
        """
        try:
            # 获取价格（TdxQuant返回字符串）
            now = data.get('Now', '0')
            last_close = data.get('LastClose', '0')

            try:
                now_val = float(now)
                last_close_val = float(last_close)
                change = now_val - last_close_val
                change_pct = (change / last_close_val * 100) if last_close_val > 0 else 0
            except (ValueError, TypeError, AttributeError):
                now_val = 0
                last_close_val = 0
                change = 0
                change_pct = 0

            result = {
                # 基础信息
                'code': code,
                'name': data.get('name', ''),

                # 价格信息
                'price': now_val,
                'open': FormatConverter.safe_float(data.get('Open')),
                'high': FormatConverter.safe_float(data.get('Max')),
                'low': FormatConverter.safe_float(data.get('Min')),
                'last_close': last_close_val,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),

                # 成交信息（TdxQuant L1成交量单位：手）
                'volume': FormatConverter.safe_int(data.get('Volume')),
                'amount': FormatConverter.safe_float(data.get('Amount')),
                'turnover': None,  # 额外指标由服务层聚合

                # 买卖盘（处理数组格式）
                'bid1': FormatConverter._get_array_value(data, 'Buyp', 0),
                'bid_vol1': FormatConverter._get_array_value(data, 'Buyv', 0),
                'ask1': FormatConverter._get_array_value(data, 'Sellp', 0),
                'ask_vol1': FormatConverter._get_array_value(data, 'Sellv', 0),
                'bid2': FormatConverter._get_array_value(data, 'Buyp', 1),
                'bid_vol2': FormatConverter._get_array_value(data, 'Buyv', 1),
                'ask2': FormatConverter._get_array_value(data, 'Sellp', 1),
                'ask_vol2': FormatConverter._get_array_value(data, 'Sellv', 1),
                'bid3': FormatConverter._get_array_value(data, 'Buyp', 2),
                'bid_vol3': FormatConverter._get_array_value(data, 'Buyv', 2),
                'ask3': FormatConverter._get_array_value(data, 'Sellp', 2),
                'ask_vol3': FormatConverter._get_array_value(data, 'Sellv', 2),
                'bid4': FormatConverter._get_array_value(data, 'Buyp', 3),
                'bid_vol4': FormatConverter._get_array_value(data, 'Buyv', 3),
                'ask4': FormatConverter._get_array_value(data, 'Sellp', 3),
                'ask_vol4': FormatConverter._get_array_value(data, 'Sellv', 3),
                'bid5': FormatConverter._get_array_value(data, 'Buyp', 4),
                'bid_vol5': FormatConverter._get_array_value(data, 'Buyv', 4),
                'ask5': FormatConverter._get_array_value(data, 'Sellp', 4),
                'ask_vol5': FormatConverter._get_array_value(data, 'Sellv', 4),

                # 时间戳
                'timestamp': data.get('RefreshNum', ''),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
            }

            return result

        except Exception as e:
            logger.error(f"TdxQuant L1数据转换失败: {e}")
            return {}

    # ===== 工具方法 =====

    @staticmethod
    def _get_array_value(data: dict, key: str, index: int, default=0.0):
        """从数组中获取值（TdxQuant的Buyp/Buyv/Sellp/Sellv）"""
        try:
            arr = data.get(key, [])
            if arr and len(arr) > index:
                val = arr[index]
                if val and val != '0.00' and val != '0':
                    return float(val)
            return default
        except (IndexError, TypeError, ValueError):
            return default

    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """安全转换为浮点数"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """安全转换为整数"""
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
