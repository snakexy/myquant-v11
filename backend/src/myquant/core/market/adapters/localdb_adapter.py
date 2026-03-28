# -*- coding: utf-8 -*-
"""
V5 LocalDB 适配器

支持两种模式：
1. tdx_direct=True: 直接读取通达信本地数据库（.day/.lc5），零拷贝
2. tdx_direct=False: 读取 Qlib bin 文件（data/qlib_data/stock/）

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
    """V5 LocalDB 适配器 - 支持通达信直连和 Qlib bin 两种模式"""

    def __init__(self, use_tdx_direct: bool = True, tdx_path: Optional[str] = None):
        """初始化 LocalDB 适配器

        Args:
            use_tdx_direct: 是否直接读取通达信数据库（默认 True，零拷贝）
            tdx_path: 通达信安装路径（默认从环境变量 TDX_PATH 读取）
        """
        super().__init__()
        self._name = 'localdb'
        self._mode = 'tdx_direct' if use_tdx_direct else 'qlib_bin'

        if self._mode == 'tdx_direct':
            # 直接读取通达信本地数据库
            from .tdxlocal_adapter import V5TdxLocalAdapter
            self._tdx_reader = V5TdxLocalAdapter(tdx_path)
            self._ready = self._tdx_reader.is_available()
            logger.info(f"[LocalDB] 模式: tdx_direct, 通达信路径: {self._tdx_reader._tdx_path}")
        else:
            # 读取 Qlib bin 文件
            # localdb_adapter.py -> adapters -> market -> core -> myquant -> src -> backend -> root
            # 修正：往上6层到项目根目录（与 HotDB 一致）
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
            self._data_dir = project_root / 'data' / 'qlib_data' / 'stock'
            self._ready = self._data_dir.exists()

            if not self._ready:
                logger.warning(f"[LocalDB] 数据目录不存在: {self._data_dir}")
            else:
                logger.info(f"[LocalDB] 模式: qlib_bin, 数据目录: {self._data_dir}")

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

    def _get_period_dir(self, period: str) -> str:
        """获取周期对应的目录名"""
        period_map = {
            '1d': 'day',
            '1w': 'week',
            '1mon': 'month',
            '1m': 'min1',
            '5m': 'min5',
            '15m': 'min15',
            '30m': 'min30',
            '1h': 'min60',
        }
        return period_map.get(period, 'day')

    def _get_period_suffix(self, period: str) -> str:
        """获取周期对应的文件后缀"""
        return self._get_period_dir(period)

    def _dir_name(self, symbol: str) -> str:
        """600000.SH -> sh600000"""
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        return f"{self._exchange(symbol)}{code}"

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据（支持多周期）

        注意：本地文件存储的是不复权原始数据，复权由服务层统一处理。
        """
        if not self._ready:
            return {}

        if self._mode == 'tdx_direct':
            # 直接从通达信读取（支持 1d 和 5m）
            if period not in ['1d', '5m']:
                logger.warning(f"[LocalDB] 通达信直连模式只支持 1d/5m，请求的 {period} 将返回空")
                return {}
            return self._tdx_reader.get_kline(symbols, period, start_date, end_date, count, adjust_type)

        # Qlib bin 模式
        return self._get_kline_from_qlib_bin(symbols, period, start_date, end_date, count)

    def _get_kline_from_qlib_bin(
        self,
        symbols: List[str],
        period: str,
        start_date: Optional[str],
        end_date: Optional[str],
        count: Optional[int]
    ) -> Dict[str, pd.DataFrame]:

        """从 Qlib bin 文件读取 K线数据"""
        # 获取周期目录和文件后缀
        period_dir = self._get_period_dir(period)
        period_suffix = self._get_period_suffix(period)
        is_minute = period in ['1m', '5m', '15m', '30m', '1h']

        result = {}
        for symbol in symbols:
            try:
                stock_dir = self._data_dir / self._exchange(symbol) / period_dir / self._dir_name(symbol)
                if not stock_dir.exists():
                    continue

                dates = self._read_dates(stock_dir / f'date.{period_suffix}.bin')
                closes = self._read_floats(stock_dir / f'close.{period_suffix}.bin')
                if not dates or not closes:
                    continue

                n = min(len(dates), len(closes))
                opens = self._read_floats(stock_dir / f'open.{period_suffix}.bin') or [0] * n
                highs = self._read_floats(stock_dir / f'high.{period_suffix}.bin') or [0] * n
                lows = self._read_floats(stock_dir / f'low.{period_suffix}.bin') or [0] * n
                volumes = self._read_floats(stock_dir / f'volume.{period_suffix}.bin') or [0] * n
                amounts = self._read_floats(stock_dir / f'amount.{period_suffix}.bin') or [0] * n

                # 分钟线需要读取时间信息
                times = None
                if is_minute:
                    times = self._read_dates(stock_dir / f'time.{period_suffix}.bin')

                rows = []
                for i in range(n):
                    # 构造 datetime
                    date_str = f'{dates[i][:4]}-{dates[i][4:6]}-{dates[i][6:8]}'
                    if is_minute and times and i < len(times):
                        # 分钟线：拼接日期和时间（times 是字符串，需补零到6位）
                        time_val = times[i]
                        # 补零到 6 位 (93500 -> 093500)
                        time_padded = str(time_val).zfill(6)
                        datetime_str = f'{date_str} {time_padded[:2]}:{time_padded[2:4]}:{time_padded[4:6]}'
                    else:
                        # 日线：只有日期
                        datetime_str = date_str

                    rows.append({
                        'datetime': pd.Timestamp(datetime_str),
                        'open': opens[i], 'high': highs[i], 'low': lows[i],
                        'close': closes[i],
                        'volume': volumes[i] if volumes else 0,
                        'amount': amounts[i] if amounts else 0,
                    })

                df = pd.DataFrame(rows)
                if start_date:
                    df = df[df['datetime'] >= pd.Timestamp(start_date)]
                if end_date:
                    df = df[df['datetime'] <= pd.Timestamp(end_date)]
                if count and len(df) > count:
                    df = df.tail(count)

                if not df.empty:
                    result[symbol] = self._normalize_kline_df(df, 'localdb')

            except Exception as e:
                logger.warning(f"LocalDB 获取 {symbol} K线失败: {e}")

        return result

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """LocalDB 不支持实时行情"""
        return {}


    def save_kline(self, symbol: str, df: pd.DataFrame, period: str = '1d') -> bool:
        """保存K线数据到本地

        注意：tdx_direct 模式下不支持保存（通达信文件只读）
        """
        if self._mode == 'tdx_direct':
            logger.warning(f"[LocalDB] tdx_direct 模式不支持保存数据（通达信文件只读）")
            return False

        return self._save_kline_to_qlib_bin(symbol, df, period)

    def _save_kline_to_qlib_bin(self, symbol: str, df: pd.DataFrame, period: str) -> bool:
        """保存K线数据到本地bin文件（支持多周期）

        Args:
            symbol: 股票代码 (如 600519.SH)
            df: DataFrame with columns [datetime, open, high, low, close, volume, amount]
            period: 周期 (1d/1w/1mon/1m/5m/15m/30m/1h)

        Returns:
            是否保存成功
        """
        if df is None or df.empty:
            logger.warning(f"保存 {symbol} 数据为空，跳过")
            return False

        try:
            # 获取周期目录和文件后缀
            period_dir = self._get_period_dir(period)
            period_suffix = self._get_period_suffix(period)

            # 确保目录存在
            stock_dir = self._data_dir / self._exchange(symbol) / period_dir / self._dir_name(symbol)
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
            self._write_ints(stock_dir / f'date.{period_suffix}.bin', dates)
            self._write_floats(stock_dir / f'open.{period_suffix}.bin', opens)
            self._write_floats(stock_dir / f'high.{period_suffix}.bin', highs)
            self._write_floats(stock_dir / f'low.{period_suffix}.bin', lows)
            self._write_floats(stock_dir / f'close.{period_suffix}.bin', closes)
            self._write_floats(stock_dir / f'volume.{period_suffix}.bin', volumes)
            self._write_floats(stock_dir / f'amount.{period_suffix}.bin', amounts)

            # 分钟线需要额外保存时间信息
            if period in ['1m', '5m', '15m', '30m', '1h']:
                times = df['datetime'].dt.strftime('%H%M%S').astype(int).tolist()
                self._write_ints(stock_dir / f'time.{period_suffix}.bin', times)
                logger.debug(f"[LocalDB] 保存时间信息: {len(times)} 条 ({period})")

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


def create_localdb_adapter(use_tdx_direct: bool = True, tdx_path: Optional[str] = None):
    """创建 LocalDB 适配器实例

    Args:
        use_tdx_direct: 是否直接读取通达信数据库（默认 True，零拷贝）
        tdx_path: 通达信安装路径（默认从环境变量 TDX_PATH 读取）
    """
    return V5LocalDBAdapter(use_tdx_direct=use_tdx_direct, tdx_path=tdx_path)
