# -*- coding: utf-8 -*-
"""
V5 LocalDB 适配器

直接读取本地数据库的 .day.bin 二进制文件。
数据目录: {project_root}/data/qlib_data/stock/{exchange}/day/{exchange}{code}/

不依赖 Qlib SDK，无初始化延迟。
"""

from typing import Dict, List, Optional
from loguru import logger
import struct
import pandas as pd
from pathlib import Path

import os

from .base import V5DataAdapter


class V5LocalDBAdapter(V5DataAdapter):
    """V5 LocalDB 适配器 - 直接读取二进制文件"""

    def __init__(self):
        super().__init__()
        self._name = 'localdb'
        # localdb_adapter.py -> adapters -> market -> core -> myquant -> src -> backend -> root
        # 修正：往上6层到项目根目录
        # 强制重载标记: 2026-03-25-03-45
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent

        # 优先使用通达信 vipdoc 目录（原始数据）
        tdx_vipdoc = Path(r'E:\new_tdx64\vipdoc')
        if tdx_vipdoc.exists():
            self._data_dir = tdx_vipdoc
            self._use_tdx_format = True
            logger.info(f"[LocalDB] 使用通达信格式: {self._data_dir}")
        else:
            # 降级：使用 qlib_data 格式
            self._data_dir = project_root / 'data' / 'qlib_data' / 'stock'
            self._use_tdx_format = False
            logger.info(f"[LocalDB] 使用 Qlib 格式: {self._data_dir}")

        self._ready = self._data_dir.exists()

        if not self._ready:
            logger.warning(f"[LocalDB] 数据目录不存在: {self._data_dir}")

    def is_available(self) -> bool:
        return self._ready

    def _read_floats(self, filepath: Path) -> Optional[List[float]]:
        """读取 float32 二进制文件: int32 count + float32[count]"""
        if not filepath.exists():
            return None
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            if len(data) < 8:
                return None
            count = struct.unpack('<i', data[:4])[0]
            return list(struct.unpack(f'<{count}f', data[4:4 + count * 4]))
        except Exception:
            return None

    def _read_dates(self, filepath: Path) -> Optional[List[str]]:
        """读取 date.day.bin: int32 count + int32[count] YYYYMMDD"""
        if not filepath.exists():
            return None
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            if len(data) < 8:
                return None
            count = struct.unpack('<i', data[:4])[0]
            return [f'{d}' for d in struct.unpack(f'<{count}i', data[4:4 + count * 4])]
        except Exception:
            return None

    def _exchange(self, symbol: str) -> str:
        """600000.SH -> sh"""
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        if code[0] in ('6', '5', '9'):
            return 'sh'
        elif code[0] in ('4', '8'):
            return 'bj'
        else:
            return 'sz'

    def _dir_name(self, symbol: str) -> str:
        """600000.SH -> sh600000"""
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        return f"{self._exchange(symbol)}{code}"

    def _read_tdx_day_file(self, filepath: Path) -> Optional[pd.DataFrame]:
        """读取通达信 .day 文件格式（32字节/记录）

        格式：IIIIIIII（8个int32）= 日期 + 开 + 高 + 低 + 收 + 成交额 + 成交量 + 保留
        """
        try:
            with open(filepath, 'rb') as f:
                data = f.read()

            record_size = 32
            num_records = len(data) // record_size

            rows = []
            for i in range(num_records):
                offset = i * record_size
                # 通达信格式：8个int32
                record = struct.unpack('iiiiiiII', data[offset:offset + record_size])

                # 转换日期格式 (YYYYMMDD -> datetime)
                date_int = record[0]
                year = date_int // 10000
                month = (date_int % 10000) // 100
                day = date_int % 100

                from datetime import datetime as dt_class
                date_time = dt_class(year, month, day)

                # 价格需要除以 100，成交量是股需要除以100转为手
                rows.append({
                    'datetime': pd.Timestamp(date_time),
                    'open': record[1] / 100.0,
                    'high': record[2] / 100.0,
                    'low': record[3] / 100.0,
                    'close': record[4] / 100.0,
                    'amount': record[5],
                    'volume': record[6] // 100,  # 通达信成交量是股，转为手
                })

            df = pd.DataFrame(rows)
            return df
        except Exception as e:
            logger.warning(f"[LocalDB] 读取通达信文件失败 {filepath}: {e}")
            return None

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'  # 参数保留（兼容性），本地文件始终是不复权数据
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据（只支持日线和5分钟线）

        注意：本地文件存储的是不复权原始数据，复权由服务层统一处理。
        - 1d（日线）：从通达信 vipdoc/{市场}/lday/ 读取
        - 5m（5分钟）：从通达信 vipdoc/{市场}/fzline/ 读取（.lc5文件）
        - 其他周期：不支持，返回空（让 KlineService 降级到在线源）
        """
        if not self._ready:
            return {}

        # 只支持日线和5分钟线
        if period not in ['1d', '5m']:
            logger.debug(f"[LocalDB] 通达信格式只支持 1d/5m，请求的 {period} 将跳过")
            return {}

        # 5m 数据使用 numpy 批量解析
        if period == '5m':
            return self._get_5m_data(symbols, count, start_date, end_date)

        # 日线数据
        return self._get_daily_data(symbols, count, start_date, end_date)

    def _read_tdx_5m_file(self, filepath: Path) -> Optional[pd.DataFrame]:
        """读取通达信 .lc5 文件格式（32字节/记录）

        格式（旧版本验证正确）：
        - 00-01: 日期 (short, 编码: year=val//2048+2004, month=(val%2048)//100, day=(val%2048)%100)
        - 02-03: 从0点开始分钟数 (short)
        - 04-07: 开盘价 (float)
        - 08-11: 最高价 (float)
        - 12-15: 最低价 (float)
        - 16-19: 收盘价 (float)
        - 20-23: 成交额 (float)
        - 24-27: 成交量 (int，单位：股)
        - 28-31: 保留字段
        """
        try:
            import numpy as np

            with open(filepath, 'rb') as f:
                data = f.read()

            # 定义结构化 dtype（32字节）
            dtype = np.dtype([
                ('date', '<u2'),     # 2 bytes: 通达信编码日期
                ('minutes', '<u2'),   # 2 bytes: 从0点开始分钟数
                ('open', '<f4'),      # 4 bytes: 开盘价
                ('high', '<f4'),      # 4 bytes: 最高价
                ('low', '<f4'),       # 4 bytes: 最低价
                ('close', '<f4'),     # 4 bytes: 收盘价
                ('amount', '<f4'),    # 4 bytes: 成交额
                ('volume', '<u4'),    # 4 bytes: 成交量
                ('reserved', '<u4')   # 4 bytes: 保留字段
            ])

            # numpy.frombuffer 批量解析（零拷贝）
            arr = np.frombuffer(data, dtype=dtype)

            # 过滤有效记录（date > 0）
            valid_mask = arr['date'] > 0
            arr_valid = arr[valid_mask]

            if len(arr_valid) == 0:
                return None

            # 向量化提取各列
            dates_val = arr_valid['date'].astype(np.uint16)
            minutes_val = arr_valid['minutes'].astype(np.uint16)
            opens = arr_valid['open'].astype(np.float64)
            highs = arr_valid['high'].astype(np.float64)
            lows = arr_valid['low'].astype(np.float64)
            closes = arr_valid['close'].astype(np.float64)
            amounts = arr_valid['amount'].astype(np.float64)
            volumes = arr_valid['volume'].astype(np.int64)

            # 向量化日期转换（通达信特殊编码）
            years = dates_val // 2048 + 2004
            months = (dates_val % 2048) // 100
            days = (dates_val % 2048) % 100

            # 向量化时间转换（分钟数 -> HH:MM）
            hours = minutes_val // 60
            mins = minutes_val % 60

            # 构造 datetime（向量化）
            datetimes = pd.to_datetime({
                'year': years,
                'month': months,
                'day': days,
                'hour': hours,
                'minute': mins
            })

            # 成交量单位转换：股 -> 手
            volumes = volumes / 100.0

            df = pd.DataFrame({
                'datetime': datetimes.values,
                'open': opens,
                'high': highs,
                'low': lows,
                'close': closes,
                'amount': amounts,
                'volume': volumes
            })

            return df
        except Exception as e:
            logger.warning(f"[LocalDB] 读取通达信5m文件失败 {filepath}: {e}")
            return None

    def _get_5m_data(
        self, symbols: List[str], count: Optional[int],
        start_date: Optional[str], end_date: Optional[str]
    ) -> Dict[str, pd.DataFrame]:
        """获取5分钟数据（直接读取 .lc5 二进制文件）

        格式：<HHfffffII (32字节/记录)
        价格是 float，不需要除以100
        成交量是股，需要除以100转为手
        """
        result = {}
        for symbol in symbols:
            try:
                code = symbol.replace('.SZ', '').replace('.SH', '')
                exchange = self._exchange(symbol).lower()
                filename = f'{exchange}{code}.lc5'
                filepath = self._data_dir / exchange / 'fzline' / filename

                if not filepath.exists():
                    continue

                df = self._read_tdx_5m_file(filepath)
                if df is None or df.empty:
                    continue

                # 过滤日期
                if start_date:
                    df = df[df['datetime'] >= pd.to_datetime(start_date)]
                if end_date:
                    df = df[df['datetime'] <= pd.to_datetime(end_date)]
                if count and len(df) > count:
                    df = df.tail(count)

                if not df.empty:
                    result[symbol] = self._normalize_kline_df(df, 'localdb')

            except Exception as e:
                logger.warning(f"[LocalDB] 获取5m数据失败 {symbol}: {e}")
                continue

        return result

    def _get_daily_data(
        self, symbols: List[str], count: Optional[int],
        start_date: Optional[str], end_date: Optional[str]
    ) -> Dict[str, pd.DataFrame]:
        """获取日线数据"""
        result = {}
        for symbol in symbols:
            try:
                # 根据格式选择读取方式
                if self._use_tdx_format:
                    # 通达信格式：vipdoc/{市场}/lday/{代码}.day
                    code = symbol.replace('.SZ', '').replace('.SH', '')
                    exchange = self._exchange(symbol).lower()
                    filename = f'{exchange}{code}.day'
                    stock_file = self._data_dir / exchange / 'lday' / filename

                    if not stock_file.exists():
                        continue

                    df = self._read_tdx_day_file(stock_file)
                    if df is None or df.empty:
                        continue
                else:
                    # Qlib 格式：分离的 .day.bin 文件
                    stock_dir = (
                        self._data_dir / self._exchange(symbol) / 'day'
                        / self._dir_name(symbol)
                    )

                    if not stock_dir.exists():
                        continue

                    dates = self._read_dates(stock_dir / 'date.day.bin')
                    closes = self._read_floats(stock_dir / 'close.day.bin')
                    if not dates or not closes:
                        continue

                    n = min(len(dates), len(closes))
                    opens = self._read_floats(stock_dir / 'open.day.bin') or [0] * n
                    highs = self._read_floats(stock_dir / 'high.day.bin') or [0] * n
                    lows = self._read_floats(stock_dir / 'low.day.bin') or [0] * n
                    volumes = self._read_floats(stock_dir / 'volume.day.bin') or [0] * n
                    amounts = self._read_floats(stock_dir / 'amount.day.bin') or [0] * n

                    rows = []
                    for i in range(n):
                        dt = pd.Timestamp(
                            f'{dates[i][:4]}-{dates[i][4:6]}-{dates[i][6:8]}'
                        )
                        rows.append({
                            'datetime': dt,
                            'open': opens[i],
                            'high': highs[i],
                            'low': lows[i],
                            'close': closes[i],
                            'volume': volumes[i] if volumes else 0,
                            'amount': amounts[i] if amounts else 0,
                        })

                    df = pd.DataFrame(rows)

                # 过滤日期
                if start_date:
                    df = df[df['datetime'] >= pd.to_datetime(start_date)]
                if end_date:
                    df = df[df['datetime'] <= pd.to_datetime(end_date)]
                if count and len(df) > count:
                    df = df.tail(count)

                if not df.empty:
                    result[symbol] = self._normalize_kline_df(df, 'localdb')

            except Exception as e:
                logger.warning(f"[LocalDB] 获取 {symbol} K线失败: {e}")
                continue

        return result

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """LocalDB 不支持实时行情"""
        return {}


    def save_kline(self, symbol: str, df: pd.DataFrame, period: str = '1d') -> bool:
        """保存K线数据到本地bin文件（仅支持日线）

        Args:
            symbol: 股票代码 (如 600519.SH)
            df: DataFrame with columns [datetime, open, high, low, close, volume, amount]
            period: 周期，仅支持 '1d' (日线)

        Returns:
            是否保存成功
        """
        if period != '1d':
            logger.debug(f"LocalDB 仅支持日线数据存储，跳过 {period}")
            return False

        if df is None or df.empty:
            logger.warning(f"保存 {symbol} 数据为空，跳过")
            return False

        try:
            # 确保目录存在
            stock_dir = self._data_dir / self._exchange(symbol) / 'day' / self._dir_name(symbol)
            stock_dir.mkdir(parents=True, exist_ok=True)

            # 准备数据
            df = df.copy()

            # 统一列名：有些适配器用 'time' 而不是 'datetime'
            if 'datetime' not in df.columns and 'time' in df.columns:
                df.rename(columns={'time': 'datetime'}, inplace=True)

            # 确保 datetime 列存在
            if 'datetime' not in df.columns:
                logger.error(f"[LocalDB] 保存 {symbol} 失败: DataFrame 缺少 'datetime' 或 'time' 列，现有列: {list(df.columns)}")
                return False

            df['datetime'] = pd.to_datetime(df['datetime'])

            # 日期转换为YYYYMMDD格式
            dates = df['datetime'].dt.strftime('%Y%m%d').astype(int).tolist()
            opens = df['open'].astype(float).tolist()
            highs = df['high'].astype(float).tolist()
            lows = df['low'].astype(float).tolist()
            closes = df['close'].astype(float).tolist()
            volumes = df['volume'].astype(float).tolist()
            amounts = df.get('amount', pd.Series([0] * len(df))).astype(float).tolist()

            # 写入bin文件
            self._write_ints(stock_dir / 'date.day.bin', dates)
            self._write_floats(stock_dir / 'open.day.bin', opens)
            self._write_floats(stock_dir / 'high.day.bin', highs)
            self._write_floats(stock_dir / 'low.day.bin', lows)
            self._write_floats(stock_dir / 'close.day.bin', closes)
            self._write_floats(stock_dir / 'volume.day.bin', volumes)
            self._write_floats(stock_dir / 'amount.day.bin', amounts)

            logger.info(f"[LocalDB] 保存 {symbol} {period}: {len(df)} 条数据到 {stock_dir}")
            return True

        except Exception as e:
            logger.error(f"[LocalDB] 保存 {symbol} {period} 失败: {e}")
            return False

    def _write_floats(self, filepath: Path, values: List[float]):
        """写入 float32 二进制文件: int32 count + float32[count]"""
        with open(filepath, 'wb') as f:
            count = len(values)
            f.write(struct.pack('<i', count))
            f.write(struct.pack(f'<{count}f', *values))

    def _write_ints(self, filepath: Path, values: List[int]):
        """写入 int32 二进制文件: int32 count + int32[count]"""
        with open(filepath, 'wb') as f:
            count = len(values)
            f.write(struct.pack('<i', count))
            f.write(struct.pack(f'<{count}i', *values))


def create_localdb_adapter():
    """创建 LocalDB 适配器实例"""
    return V5LocalDBAdapter()
