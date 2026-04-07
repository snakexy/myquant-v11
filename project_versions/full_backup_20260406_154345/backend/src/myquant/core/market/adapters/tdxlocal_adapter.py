"""
V5 TdxLocal 适配器

读取通达信本地 .day 文件，用于数据转换服务
"""

from typing import Dict, List, Optional
import pandas as pd
import os
from pathlib import Path

from .base import V5DataAdapter


class V5TdxLocalAdapter(V5DataAdapter):
    """V5 TdxLocal 适配器

    直接读取通达信本地 .day 文件
    """

    def __init__(self, tdx_path: Optional[str] = None):
        super().__init__()
        self._name = 'tdxlocal'
        self._tdx_path = tdx_path or os.environ.get('TDX_PATH', 'E:/new_tdx64')

    def _get_day_file_path(self, symbol: str, period: str = 'day') -> Optional[str]:
        """获取 .day 文件路径"""
        from myquant.core.market.models import normalize_stock_code

        code = normalize_stock_code(symbol)

        # 确定市场目录
        if code[0] in ['6', '5', '9']:
            market_dir = "shday"
        elif code[0] in ['0', '2', '3']:
            market_dir = "szday"
        else:
            return None

        # 构建文件路径
        vipdoc_path = os.path.join(self._tdx_path, "vipdoc", market_dir, f"{code}.day")

        if os.path.exists(vipdoc_path):
            return vipdoc_path

        return None

    def _read_day_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """读取 .day 文件"""
        try:
            import struct

            with open(file_path, 'rb') as f:
                data = f.read()

            # .day 文件格式：每条记录 32 字节
            # 日期(4) + 开(4) + 高(4) + 低(4) + 收(4) + 成交额(4) + 成交量(4) + 保留(4)
            record_size = 32
            num_records = len(data) // record_size

            records = []
            for i in range(num_records):
                offset = i * record_size
                record = struct.unpack('IIIIIIFI', data[offset:offset + record_size])

                # 转换日期格式 (YYYYMMDD -> datetime)
                date_int = record[0]
                year = date_int // 10000
                month = (date_int % 10000) // 100
                day = date_int % 100

                from datetime import datetime
                dt = datetime(year, month, day)

                # 价格需要除以 100
                records.append({
                    'datetime': dt,
                    'open': record[1] / 100.0,
                    'high': record[2] / 100.0,
                    'low': record[3] / 100.0,
                    'close': record[4] / 100.0,
                    'amount': record[5],
                    'volume': record[6]
                })

            df = pd.DataFrame(records)
            return df

        except Exception:
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
        """获取 K线数据

        注意：本地 .day 文件存储的是不复权原始数据，复权由服务层统一处理。
        """
        result = {}

        for symbol in symbols:
            try:
                file_path = self._get_day_file_path(symbol, period)
                if not file_path:
                    continue

                df = self._read_day_file(file_path)
                if df is None or df.empty:
                    continue

                # 过滤日期范围
                if start_date:
                    df = df[df['datetime'] >= pd.to_datetime(start_date)]
                if end_date:
                    df = df[df['datetime'] <= pd.to_datetime(end_date)]

                # 限制数量
                if count:
                    df = df.tail(count)

                result[symbol] = self._normalize_kline_df(df, 'tdxlocal')

            except Exception:
                continue

        return result

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """获取实时行情（不支持）"""
        return {}

    def check_availability(self, symbols: List[str]) -> Dict[str, bool]:
        """检查文件是否存在"""
        result = {}
        for symbol in symbols:
            file_path = self._get_day_file_path(symbol)
            result[symbol] = file_path is not None and os.path.exists(file_path)
        return result

    def is_available(self) -> bool:
        """检查适配器是否可用"""
        return os.path.exists(self._tdx_path)


def create_tdxlocal_adapter(tdx_path: Optional[str] = None) -> V5TdxLocalAdapter:
    """工厂函数：创建 TdxLocal 适配器"""
    return V5TdxLocalAdapter(tdx_path)
