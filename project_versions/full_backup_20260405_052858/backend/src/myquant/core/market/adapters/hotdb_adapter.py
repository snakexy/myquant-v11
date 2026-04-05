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
import numpy as np
import time
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
        '1M': 'month',   # 前端传入 '1M'（大写M）
        '1mon': 'month',  # 兼容 '1mon'（小写mon）
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

                # 1. 尝试直接读取文件
                if stock_dir.exists():
                    # 读取各字段 (ext = .{period}.bin)
                    ext = f'.{hotdb_period}.bin'
                    dates = self._read_dates(stock_dir / f'date{ext}')
                    closes = self._read_floats(stock_dir / f'close{ext}')

                    if dates and closes:
                        n = min(len(dates), len(closes))
                        opens = self._read_floats(stock_dir / f'open{ext}') or [0] * n
                        highs = self._read_floats(stock_dir / f'high{ext}') or [0] * n
                        lows = self._read_floats(stock_dir / f'low{ext}') or [0] * n
                        volumes = self._read_floats(stock_dir / f'volume{ext}') or [0] * n
                        amounts = self._read_floats(stock_dir / f'amount{ext}') or [0] * n

                        # 分钟线需要读取 time 文件
                        times = None
                        if hotdb_period in ('min1', 'min5', 'min15', 'min30', 'min60'):
                            times = self._read_dates(stock_dir / f'time{ext}')

                        rows = []
                        for i in range(n):
                            try:
                                # 解析日期
                                d = str(dates[i])
                                if len(d) == 8:
                                    # YYYYMMDD 格式
                                    date_str = f'{d[:4]}-{d[4:6]}-{d[6:8]}'
                                else:
                                    date_str = f'{d[:4]}-{d[4:6]}-{d[6:8]}'

                                # 解析时间（分钟线）
                                if times and i < len(times):
                                    t = str(times[i])
                                    # HHMM 格式，补齐到 4 位
                                    t_padded = t.zfill(4)
                                    time_str = f'{t_padded[:2]}:{t_padded[2:4]}'
                                    dt_str = f'{date_str} {time_str}'
                                else:
                                    dt_str = date_str

                                dt = pd.Timestamp(dt_str)
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

                        if rows:
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
                            continue

                # 2. 文件不存在，尝试从 5m 聚合生成（15m/30m/1h）
                if period in ('15m', '30m', '1h'):
                    logger.info(f"[HotDB] {symbol} {period} 文件不存在，尝试从 5m 聚合生成")
                    df_agg = self._aggregate_from_5m(symbol, period)
                    if df_agg is not None and not df_agg.empty:
                        # 过滤和限制
                        if start_date:
                            df_agg = df_agg[df_agg['datetime'] >= pd.Timestamp(start_date)]
                        if end_date:
                            df_agg = df_agg[df_agg['datetime'] <= pd.Timestamp(end_date)]
                        if count and len(df_agg) > count:
                            df_agg = df_agg.tail(count)

                        if not df_agg.empty:
                            result[symbol] = self._normalize_kline_df(df_agg, 'hotdb')
                            # 自动保存聚合结果
                            self.save_kline(symbol, df_agg, period)
                            logger.info(f"[HotDB] {symbol} {period} 聚合生成并保存: {len(df_agg)} 条")
                            continue

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

            # 提取数据列（统一处理）
            opens = df['open'].astype(float).tolist()
            highs = df['high'].astype(float).tolist()
            lows = df['low'].astype(float).tolist()
            closes = df['close'].astype(float).tolist()
            volumes = df['volume'].astype(float).tolist()
            amounts = df.get('amount', pd.Series([0] * len(df))).astype(float).tolist()

            # 根据周期生成日期值
            if hotdb_period in ('day', 'week', 'month'):
                # 日线、周线、月线：YYYYMMDD 格式
                dates = df['datetime'].dt.strftime('%Y%m%d').astype(int).tolist()
                # 写入文件
                self._write_ints(stock_dir / f'date{ext}', dates)
                self._write_floats(stock_dir / f'open{ext}', opens)
                self._write_floats(stock_dir / f'high{ext}', highs)
                self._write_floats(stock_dir / f'low{ext}', lows)
                self._write_floats(stock_dir / f'close{ext}', closes)
                self._write_floats(stock_dir / f'volume{ext}', volumes)
                self._write_floats(stock_dir / f'amount{ext}', amounts)
            else:
                # 分钟线：Qlib 格式，分别存储 date 和 time
                # date.min5.bin: YYYYMMDD
                # time.min5.bin: HHMM（4位数字）
                dates = df['datetime'].dt.strftime('%Y%m%d').astype(int).tolist()
                times = df['datetime'].dt.strftime('%H%M').astype(int).tolist()

                # 写入文件
                self._write_ints(stock_dir / f'date{ext}', dates)
                self._write_ints(stock_dir / f'time{ext}', times)
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

    # ─────────────────────────────────────────────
    # 聚合功能（从 5m 生成 15m/30m/1h）
    # ─────────────────────────────────────────────

    def _aggregate_from_5m(
        self, symbol: str, target_period: str
    ) -> Optional[pd.DataFrame]:
        """从5分钟数据聚合生成目标周期数据（numpy 向量化）

        Args:
            symbol: 股票代码
            target_period: 目标周期 (15m/30m/1h)

        Returns:
            聚合后的 DataFrame 或 None
        """
        # 先读取 5m 数据
        df_5m = self.get_kline([symbol], period='5m', count=100000)
        if symbol not in df_5m or df_5m[symbol].empty:
            logger.debug(f"[HotDB] 无法获取 {symbol} 的 5m 数据，跳过聚合")
            return None

        try:
            start_time = time.time()

            df = df_5m[symbol].copy().reset_index(drop=True)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)

            if target_period == '1h':
                agg_df = self._aggregate_1h_by_trading_time(df)
            else:
                # 15m/30m 按固定数量聚合
                factor = {'15m': 3, '30m': 6}.get(target_period)
                if factor is None:
                    return None
                agg_df = self._aggregate_by_fixed_count(df, factor)

            if agg_df is None or agg_df.empty:
                return None

            elapsed = (time.time() - start_time) * 1000
            logger.debug(
                f"[HotDB] 聚合 {symbol} 5m → {target_period}: "
                f"{len(df)} 根 → {len(agg_df)} 根 (耗时: {elapsed:.2f}ms)"
            )

            return agg_df

        except Exception as e:
            logger.warning(f"[HotDB] 聚合 {symbol} 5m → {target_period} 失败: {e}")
            return None

    def _aggregate_1h_by_trading_time(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """按交易时间段聚合1小时K线

        A股交易时间：
        - 09:30-10:30 → 10:30 收盘
        - 10:30-11:30 → 11:30 收盘
        - 13:00-14:00 → 14:00 收盘
        - 14:00-15:00 → 15:00 收盘
        """
        def get_hour_period(dt):
            """根据时间返回所属的1小时周期收盘时间"""
            if isinstance(dt, pd.Timestamp):
                hour = dt.hour
                minute = dt.minute
            else:
                dt = pd.Timestamp(dt)
                hour = dt.hour
                minute = dt.minute

            time_val = hour * 100 + minute

            if 930 <= time_val < 1030:
                return dt.replace(hour=10, minute=30).strftime('%Y-%m-%d %H:%M:%S')
            elif 1030 <= time_val < 1130:
                return dt.replace(hour=11, minute=30).strftime('%Y-%m-%d %H:%M:%S')
            elif 1130 <= time_val < 1300:
                return dt.replace(hour=11, minute=30).strftime('%Y-%m-%d %H:%M:%S')
            elif 1300 <= time_val < 1400:
                return dt.replace(hour=14, minute=0).strftime('%Y-%m-%d %H:%M:%S')
            elif 1400 <= time_val < 1500:
                return dt.replace(hour=15, minute=0).strftime('%Y-%m-%d %H:%M:%S')
            elif time_val == 1500:
                return dt.replace(hour=15, minute=0).strftime('%Y-%m-%d %H:%M:%S')
            else:
                return None

        df['period_close'] = df['datetime'].apply(get_hour_period)
        df = df[df['period_close'].notna()].copy()

        if df.empty:
            return None

        df['group_key'] = df['period_close']

        agg_df = df.groupby('group_key').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum'
        }).reset_index()

        agg_df = agg_df.rename(columns={'group_key': 'datetime'})
        agg_df = agg_df[['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        agg_df['datetime'] = pd.to_datetime(agg_df['datetime'])
        agg_df = agg_df.sort_values('datetime').reset_index(drop=True)

        return agg_df

    def _aggregate_by_fixed_count(
        self, df: pd.DataFrame, factor: int
    ) -> Optional[pd.DataFrame]:
        """按固定数量聚合（15m=3根, 30m=6根）numpy 向量化优化版

        性能：比循环快几十倍
        """
        n = len(df)
        n_agg = n // factor

        if n_agg == 0:
            return None

        # 转换为 numpy 数组（向量化操作）
        opens = df['open'].values.astype(np.float64)
        highs = df['high'].values.astype(np.float64)
        lows = df['low'].values.astype(np.float64)
        closes = df['close'].values.astype(np.float64)
        volumes = df['volume'].values.astype(np.float64)
        datetimes = df['datetime'].values
        amount = df.get('amount', pd.Series([0.0] * n)).values.astype(np.float64)

        n_complete = n_agg * factor

        # 完整部分：使用 reshape 向量化
        opens_2d = opens[:n_complete].reshape(n_agg, factor)
        highs_2d = highs[:n_complete].reshape(n_agg, factor)
        lows_2d = lows[:n_complete].reshape(n_agg, factor)
        closes_2d = closes[:n_complete].reshape(n_agg, factor)
        volumes_2d = volumes[:n_complete].reshape(n_agg, factor)
        amount_2d = amount[:n_complete].reshape(n_agg, factor)

        # 向量化聚合
        agg_open = opens_2d[:, 0]
        agg_high = highs_2d.max(axis=1)
        agg_low = lows_2d.min(axis=1)
        agg_close = closes_2d[:, -1]
        agg_volume = volumes_2d.sum(axis=1)
        agg_amount = amount_2d.sum(axis=1)

        # 计算周期结束时间
        period_minutes = factor * 5
        agg_datetime_list = []

        for i in range(n_agg):
            first_dt = pd.Timestamp(datetimes[i * factor])
            hour = first_dt.hour
            minute = first_dt.minute

            if period_minutes == 15:
                minutes_from_open = (hour - 9) * 60 + (minute - 30)
                period_index = max(0, minutes_from_open // 15)
                end_minutes = 30 + (period_index + 1) * 15
                end_hour = 9 + end_minutes // 60
                end_min = end_minutes % 60
                period_end = first_dt.replace(hour=end_hour, minute=end_min, second=0)
            else:  # 30m
                time_val = hour * 100 + minute
                if 930 <= time_val < 1000:
                    period_end = first_dt.replace(hour=10, minute=0, second=0)
                elif 1000 <= time_val < 1030:
                    period_end = first_dt.replace(hour=10, minute=30, second=0)
                elif 1030 <= time_val < 1100:
                    period_end = first_dt.replace(hour=11, minute=0, second=0)
                elif 1100 <= time_val < 1130:
                    period_end = first_dt.replace(hour=11, minute=30, second=0)
                elif 1130 <= time_val < 1300:
                    period_end = first_dt.replace(hour=13, minute=0, second=0)
                elif 1300 <= time_val < 1330:
                    period_end = first_dt.replace(hour=13, minute=30, second=0)
                elif 1330 <= time_val < 1400:
                    period_end = first_dt.replace(hour=14, minute=0, second=0)
                elif 1400 <= time_val < 1430:
                    period_end = first_dt.replace(hour=14, minute=30, second=0)
                else:
                    period_end = first_dt.replace(hour=15, minute=0, second=0)

            agg_datetime_list.append(period_end)

        # 余数部分
        if n_complete < n:
            rem_start = n_complete
            agg_open = np.append(agg_open, opens[rem_start])
            agg_high = np.append(agg_high, highs[rem_start:].max())
            agg_low = np.append(agg_low, lows[rem_start:].min())
            agg_close = np.append(agg_close, closes[-1])
            agg_volume = np.append(agg_volume, volumes[rem_start:].sum())
            agg_amount = np.append(agg_amount, amount[rem_start:].sum())
            agg_datetime_list.append(pd.Timestamp(datetimes[-1]))

        agg_datetime = pd.DatetimeIndex(agg_datetime_list)

        return pd.DataFrame({
            'datetime': agg_datetime,
            'open': agg_open,
            'high': agg_high,
            'low': agg_low,
            'close': agg_close,
            'volume': agg_volume,
            'amount': agg_amount
        })


def create_hotdb_adapter():
    """创建 HotDB 适配器实例"""
    return V5HotDBAdapter()
