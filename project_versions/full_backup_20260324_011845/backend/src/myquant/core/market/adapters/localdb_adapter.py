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

from .base import V5DataAdapter


class V5LocalDBAdapter(V5DataAdapter):
    """V5 LocalDB 适配器 - 直接读取二进制文件"""

    def __init__(self):
        super().__init__()
        self._name = 'localdb'
        # v5 -> adapters -> data_providers -> backend -> root
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self._data_dir = project_root / 'data' / 'qlib_data' / 'stock'
        self._ready = self._data_dir.exists()

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

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'  # 参数保留（兼容性），本地文件始终是不复权数据
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据（仅支持日线）

        注意：本地文件存储的是不复权原始数据，复权由服务层统一处理。
        """
        if not self._ready:
            return {}

        result = {}
        for symbol in symbols:
            try:
                stock_dir = self._data_dir / self._exchange(symbol) / 'day' / self._dir_name(symbol)
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

                rows = [{
                    'datetime': pd.Timestamp(f'{dates[i][:4]}-{dates[i][4:6]}-{dates[i][6:8]}'),
                    'open': opens[i], 'high': highs[i], 'low': lows[i],
                    'close': closes[i],
                    'volume': volumes[i] if volumes else 0,  # volume.day.bin 存储成交量（手）
                    'amount': amounts[i] if amounts else 0,  # amount.day.bin 存储成交额（元）
                } for i in range(n)]

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


def create_localdb_adapter() -> V5LocalDBAdapter:
    return V5LocalDBAdapter()
