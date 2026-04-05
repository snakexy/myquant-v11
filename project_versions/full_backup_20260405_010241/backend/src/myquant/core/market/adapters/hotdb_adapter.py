# -*- coding: utf-8 -*-
"""
V5 HotDB 适配器

热数据库适配器，存储自选股的最新数据。
数据格式：Qlib bin 格式
数据目录：data/hotdata/{exchange}/{period}/{exchange}{code}/

与 LocalDB 的区别：
- LocalDB：通达信历史数据（冷数据）
- HotDB：自选股最新数据（热数据，qlib格式）
"""

from typing import Dict, List, Optional
from loguru import logger
import struct
import pandas as pd
from pathlib import Path

from .base import V5DataAdapter


class V5HotDBAdapter(V5DataAdapter):
    """V5 HotDB 适配器 - 直接读取热数据 bin 文件"""

    # 周期映射：API 周期 → HotDB 目录名
    PERIOD_MAP = {
        '1m': 'min1',
        '5m': 'min5',
        '15m': 'min15',
        '30m': 'min30',
        '1h': 'min60',
        '60m': 'min60',
        '1d': 'day',
        '1w': 'week',
        '1mon': 'month',
    }

    def __init__(self):
        super().__init__()
        self._name = 'hotdb'
        # 数据目录：项目根目录/data/hotdata
        # hotdb_adapter.py -> adapters -> market -> core -> myquant -> src -> backend -> root
        # 需要往上 7 层到项目根目录
        project_root = Path(__file__).resolve().parents[6]
        self._data_dir = project_root / 'data' / 'hotdata'
        self._ready = self._data_dir.exists()

        if not self._ready:
            logger.warning(f"[HotDB] 数据目录不存在: {self._data_dir}")
        else:
            logger.info(f"[HotDB] 数据目录就绪: {self._data_dir}")

    def is_available(self) -> bool:
        """检查 HotDB 是否可用"""
        return self._ready

    def _exchange(self, symbol: str) -> str:
        """提取交易所代码：600000.SH → sh"""
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        if code[0] in ('6', '5', '9'):
            return 'sh'
        elif code[0] in ('4', '8'):
            return 'bj'
        else:
            return 'sz'

    def _dir_name(self, symbol: str) -> str:
        """生成目录名：600000.SH → sh600000"""
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        return f"{self._exchange(symbol)}{code}"

    def _hotdb_period(self, period: str) -> str:
        """API 周期转 HotDB 目录名"""
        return self.PERIOD_MAP.get(period, period)

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
        """读取 date bin 文件: int32 count + int32[count] YYYYMMDD"""
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

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'
    ) -> Dict[str, pd.DataFrame]:
        """获取 K 线数据

        Args:
            symbols: 代码列表
            period: 周期 (1m/5m/15m/30m/1h/1d/1w/1mon)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            count: 数据条数
            adjust_type: 复权类型 (HotDB 存原始数据)

        Returns:
            {symbol: DataFrame} 字典
        """
        if not self._ready:
            return {}

        hotdb_period = self._hotdb_period(period)
        result = {}

        for symbol in symbols:
            try:
                stock_dir = self._data_dir / self._exchange(symbol) / hotdb_period / self._dir_name(symbol)
                if not stock_dir.exists():
                    continue

                # 读取各字段 (ext = .{period}.bin)
                ext = f'.{hotdb_period}.bin'
                dates = self._read_dates(stock_dir / f'date{ext}')
                closes = self._read_floats(stock_dir / f'close{ext}')

                if not dates or not closes:
                    continue

                n = min(len(dates), len(closes))
                opens = self._read_floats(stock_dir / f'open{ext}') or [0] * n
                highs = self._read_floats(stock_dir / f'high{ext}') or [0] * n
                lows = self._read_floats(stock_dir / f'low{ext}') or [0] * n
                volumes = self._read_floats(stock_dir / f'volume{ext}') or [0] * n
                amounts = self._read_floats(stock_dir / f'amount{ext}') or [0] * n

                rows = []
                for i in range(n):
                    try:
                        # 解析日期
                        d = str(dates[i])
                        if len(d) == 8:
                            dt = pd.Timestamp(f'{d[:4]}-{d[4:6]}-{d[6:8]}')
                        else:
                            # 分钟线：YYYYMMDDHHMM 格式
                            dt = pd.Timestamp(str(d).zfill(8))
                        rows.append({
                            'datetime': dt,
                            'open': opens[i],
                            'high': highs[i],
                            'low': lows[i],
                            'close': closes[i],
                            'volume': volumes[i],
                            'amount': amounts[i],
                        })
                    except Exception:
                        continue

                if not rows:
                    continue

                df = pd.DataFrame(rows)

                # 日期过滤
                if start_date:
                    df = df[df['datetime'] >= pd.Timestamp(start_date)]
                if end_date:
                    df = df[df['datetime'] <= pd.Timestamp(end_date)]

                # 数量限制
                if count and len(df) > count:
                    df = df.tail(count)

                if not df.empty:
                    result[symbol] = self._normalize_kline_df(df, 'hotdb')

            except Exception as e:
                logger.warning(f"[HotDB] 获取 {symbol} {period} K线失败: {e}")

        return result

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """获取实时行情（HotDB 不支持）

        HotDB 只存储历史 K 线，实时行情由 RealtimeMarketService 提供。
        """
        return {}

    def save_kline(self, symbol: str, df: pd.DataFrame, period: str = '1d') -> bool:
        """保存 K 线数据到 HotDB

        Args:
            symbol: 股票代码 (如 600519.SH)
            df: DataFrame with columns [datetime, open, high, low, close, volume, amount]
            period: 周期

        Returns:
            是否保存成功
        """
        if df is None or df.empty:
            logger.warning(f"[HotDB] 保存 {symbol} 数据为空，跳过")
            return False

        try:
            hotdb_period = self._hotdb_period(period)

            # 确保目录存在
            stock_dir = self._data_dir / self._exchange(symbol) / hotdb_period / self._dir_name(symbol)
            stock_dir.mkdir(parents=True, exist_ok=True)

            # 准备数据
            df = df.copy()

            # 统一列名
            if 'datetime' not in df.columns and 'time' in df.columns:
                df.rename(columns={'time': 'datetime'}, inplace=True)

            if 'datetime' not in df.columns:
                logger.error(f"[HotDB] 保存 {symbol} 失败: DataFrame 缺少 datetime 列")
                return False

            df['datetime'] = pd.to_datetime(df['datetime'])

            # 去重排序
            df = df.drop_duplicates(subset=['datetime'], keep='last')
            df = df.sort_values('datetime').reset_index(drop=True)

            # 转换数据
            ext = f'.{hotdb_period}.bin'

            # 根据周期生成日期值
            if hotdb_period == 'day':
                dates = df['datetime'].dt.strftime('%Y%m%d').astype(int).tolist()
            else:
                # 分钟线：YYYYMMDDHHMM 格式
                dates = (df['datetime'].dt.strftime('%Y%m%d%H%M').astype(int) / 100).astype(int).tolist()

            opens = df['open'].astype(float).tolist()
            highs = df['high'].astype(float).tolist()
            lows = df['low'].astype(float).tolist()
            closes = df['close'].astype(float).tolist()
            volumes = df['volume'].astype(float).tolist()
            amounts = df.get('amount', pd.Series([0] * len(df))).astype(float).tolist()

            # 写入 bin 文件
            self._write_ints(stock_dir / f'date{ext}', dates)
            self._write_floats(stock_dir / f'open{ext}', opens)
            self._write_floats(stock_dir / f'high{ext}', highs)
            self._write_floats(stock_dir / f'low{ext}', lows)
            self._write_floats(stock_dir / f'close{ext}', closes)
            self._write_floats(stock_dir / f'volume{ext}', volumes)
            self._write_floats(stock_dir / f'amount{ext}', amounts)

            logger.info(f"[HotDB] 保存 {symbol} {hotdb_period}: {len(df)} 条到 {stock_dir}")
            return True

        except Exception as e:
            logger.error(f"[HotDB] 保存 {symbol} {period} 失败: {e}")
            return False

    def _write_floats(self, filepath: Path, values: List[float]):
        """写入 float32 二进制文件"""
        with open(filepath, 'wb') as f:
            count = len(values)
            f.write(struct.pack('<i', count))
            f.write(struct.pack(f'<{count}f', *values))

    def _write_ints(self, filepath: Path, values: List[int]):
        """写入 int32 二进制文件"""
        with open(filepath, 'wb') as f:
            count = len(values)
            f.write(struct.pack('<i', count))
            f.write(struct.pack(f'<{count}i', *values))

    def get_latest_time(self, symbol: str, period: str = '1d') -> Optional[pd.Timestamp]:
        """获取最新数据时间"""
        try:
            df = self.get_kline([symbol], period, count=1)
            if symbol in df and not df[symbol].empty:
                return pd.Timestamp(df[symbol].iloc[-1]['datetime'])
            return None
        except Exception:
            return None

    def get_record_count(self, symbol: str, period: str = '1d') -> int:
        """获取数据条数"""
        try:
            df = self.get_kline([symbol], period, count=1000000)
            if symbol in df:
                return len(df[symbol])
            return 0
        except Exception:
            return 0


def create_hotdb_adapter():
    """创建 HotDB 适配器实例"""
    return V5HotDBAdapter()
