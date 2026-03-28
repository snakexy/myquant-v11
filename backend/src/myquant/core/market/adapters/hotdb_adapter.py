# -*- coding: utf-8 -*-
"""
V5 热数据库（HotDB）适配器

独立热数据库，用于自选股实时行情加速。
数据目录: {project_root}/data/hotdata/
支持多周期，智能追加保存，自动清理。

多级缓存架构：
- L1: 内存缓存（TTL 5分钟，瞬间返回）
- L2: 文件缓存（bin文件，~10ms）
- L3: 元数据（index.json，记录最后更新时间）
"""

from typing import Dict, List, Optional
from loguru import logger
import struct
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from myquant.core.market.adapters.base import V5DataAdapter
from ..utils.trading_time import TradingTimeChecker
from ..utils.trading_time_detector import TradingTimeDetectorV2


# 周期到文件后缀的映射
# 注意：1h是HotDB专用的（聚合存储），LocalDB不支持
_PERIOD_SUFFIX = {
    '1d': 'day',
    '1w': 'week',
    '1mon': 'month',
    '1m': 'min1',
    '5m': 'min5',
    '15m': 'min15',
    '30m': 'min30',
    '1h': 'min60',  # HotDB专用，用于存储聚合的1h数据
}


def period_to_minutes(period: str) -> int:
    """将周期转换为分钟数"""
    mapping = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '1d': 1440,  # 24 * 60
        '1w': 10080,  # 7 * 24 * 60
        '1mon': 43200,  # 30 * 24 * 60
    }
    return mapping.get(period, 1)


class V5HotDBAdapter(V5DataAdapter):
    """V5 热数据库适配器 - 自选股加速缓存"""

    def __init__(self):
        super().__init__()
        self._name = 'hotdb'
        # hotdb_adapter.py -> adapters -> market -> core -> myquant -> src -> backend -> root
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
        self._data_dir = project_root / 'data' / 'hotdata'
        self._metadata_dir = self._data_dir / 'metadata'
        self._metadata_file = self._metadata_dir / 'index.json'

        # 创建目录
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._metadata_dir.mkdir(parents=True, exist_ok=True)

        # L1: 内存缓存（TTL 5分钟）
        self._memory_cache: Dict[str, pd.DataFrame] = {}
        self._memory_cache_time: Dict[str, float] = {}
        self._memory_cache_ttl = 300  # 5分钟

        # 是否尝试在线补全（默认启用）
        self._try_online_completion = True

        self._ready = True
        self._metadata = self._load_metadata()

        logger.info(
            f"[HotDB] 数据目录: {self._data_dir}, "
            f"内存缓存已启用（TTL={self._memory_cache_ttl}秒）"
        )

    def is_available(self) -> bool:
        return self._ready

    def _load_metadata(self) -> dict:
        """加载元数据"""
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"[HotDB] 加载元数据失败: {e}")
        return {}

    def _save_metadata(self):
        """保存元数据"""
        try:
            with open(self._metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"[HotDB] 保存元数据失败: {e}")

    def _get_period_dir(self, period: str) -> str:
        """获取周期对应的目录名（Qlib 标准）"""
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
        """读取 date.bin: int32 count + int32[count] YYYYMMDD"""
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

    def _read_times(self, filepath: Path) -> Optional[List[int]]:
        """读取 time.bin: int32 count + int32[count] HHMMSS（分钟线专用）"""
        if not filepath.exists():
            return None
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            if len(data) < 8:
                return None
            count = struct.unpack('<i', data[:4])[0]
            return list(struct.unpack(f'<{count}i', data[4:4 + count * 4]))
        except Exception:
            return None

    def _write_floats(self, filepath: Path, values: List[float]):
        """写入 float32 二进制文件: int32 count + float32[count]"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            count = len(values)
            f.write(struct.pack('<i', count))
            f.write(struct.pack(f'<{count}f', *values))

    def _write_ints(self, filepath: Path, values: List[int]):
        """写入 int32 二进制文件: int32 count + int32[count]"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            count = len(values)
            f.write(struct.pack('<i', count))
            f.write(struct.pack(f'<{count}i', *values))

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

    def _get_stock_dir(self, symbol: str, period: str) -> Path:
        """获取股票数据目录（Qlib 标准结构）

        Qlib 标准目录: hotdata/SH/min1/sh600519/
        """
        period_dir = self._get_period_dir(period)
        return self._data_dir / self._exchange(symbol) / period_dir / self._dir_name(symbol)

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none',
        allow_stale: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据（支持多周期，带L1内存缓存和智能聚合）

        Args:
            symbols: 股票代码列表
            period: 周期
            start_date: 开始日期
            end_date: 结束日期
            count: 返回数量
            adjust_type: 复权类型
            allow_stale: 是否允许返回过期数据（增量更新场景使用）

        如果请求 15m/30m/1h 周期但没有数据，会自动从 5m 数据聚合生成
        """
        if not self._ready:
            return {}

        result = {}
        current_time = time.time()

        for symbol in symbols:
            try:
                # L1: 内存缓存检查
                cache_key = f"{symbol}:{period}"
                if cache_key in self._memory_cache:
                    cache_age = current_time - self._memory_cache_time[cache_key]
                    if cache_age < self._memory_cache_ttl:
                        cached_df = self._memory_cache[cache_key]
                        logger.debug(
                            f"[HotDB-L1] 缓存命中: {symbol} {period} "
                            f"(年龄: {cache_age:.1f}秒)"
                        )

                        df = cached_df.copy()
                        if start_date:
                            df = df[df['datetime'] >= pd.Timestamp(start_date)]
                        if end_date:
                            df = df[df['datetime'] <= pd.Timestamp(end_date)]
                        if count and len(df) > count:
                            df = df.tail(count)

                        if not df.empty:
                            result[symbol] = self._normalize_kline_df(df, 'hotdb')
                        continue

                # L2: 文件读取（或智能聚合生成）
                df = self._get_or_generate_data(symbol, period)

                if df is None or df.empty:
                    # 无数据，直接跳过（由 fallback 继续尝试其他数据源）
                    continue
                else:
                    # 数据有效性检查（无效数据如 19700101）
                    earliest_time = df['datetime'].iloc[0]
                    latest_time = df['datetime'].iloc[-1]
                    now = pd.Timestamp.now(tz=None).replace(tzinfo=None)

                    # 检查日期是否有效（不能是 1970-01-01 或其他异常值）
                    min_valid_date = pd.Timestamp('2010-01-01')
                    is_invalid = earliest_time < min_valid_date

                    if is_invalid:
                        logger.warning(
                            f"[HotDB] {symbol} {period} 数据无效: "
                            f"最早 {earliest_time.date()}, 最新 {latest_time.date()}"
                        )
                        # 清除无效的缓存数据
                        cache_key = f"{symbol}:{period}"
                        if cache_key in self._memory_cache:
                            del self._memory_cache[cache_key]
                            del self._memory_cache_time[cache_key]
                        # 返回 None 让 fallback 继续尝试
                        continue

                    # 检查数据新鲜度
                    days_old = (now - latest_time).days

                    # HotDB 过期策略：
                    # - 1m 数据：只保留 7 天滚动窗口，超过 7 天视为过期
                    # - 其他周期（5m/15m/30m/1h/1d/1w/1mon）：全量保留，永不过期
                    #   （这些数据从 LocalDB 预热，会智能增量更新保持最新）
                    is_expired = (period == '1m' and days_old > 7)

                    # 如果 allow_stale=True，允许返回过期数据（用于增量更新场景）
                    if is_expired and not allow_stale:
                        logger.info(
                            f"[HotDB] {symbol} {period} 数据已过期: "
                            f"最新 {latest_time.date()}, 已过期 {days_old} 天"
                        )
                        # 清除过期的缓存数据
                        self._memory_cache.pop(cache_key, None)
                        self._memory_cache_time.pop(cache_key, None)
                        # 返回 None 让 fallback 继续尝试
                        continue

                # 保存到内存缓存（完整的未过滤数据）
                self._memory_cache[cache_key] = df.copy()
                self._memory_cache_time[cache_key] = current_time
                logger.debug(f"[HotDB-L1] 已缓存: {symbol} {period}, {len(df)} 条")

                # 应用过滤条件
                if start_date:
                    df = df[df['datetime'] >= pd.Timestamp(start_date)]
                if end_date:
                    df = df[df['datetime'] <= pd.Timestamp(end_date)]
                if count and len(df) > count:
                    df = df.tail(count)

                if not df.empty:
                    result[symbol] = self._normalize_kline_df(df, 'hotdb')

            except Exception as e:
                logger.warning(f"HotDB 获取 {symbol} {period} K线失败: {e}")

        return result

    def _get_or_generate_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """获取或生成数据（支持智能聚合）

        优先级：
        1. 直接从文件读取（1d, 5m, 1m 等原始周期）
        2. 从 5m 聚合生成（15m, 30m, 1h）

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            DataFrame 或 None
        """
        stock_dir = self._get_stock_dir(symbol, period)

        # 1. 尝试直接从文件读取
        if stock_dir.exists():
            period_suffix = self._get_period_suffix(period)
            dates = self._read_dates(stock_dir / f'date.{period_suffix}.bin')
            closes = self._read_floats(stock_dir / f'close.{period_suffix}.bin')

            if dates and closes:
                # 文件存在，直接读取
                return self._read_from_file(symbol, period)

        # 2. 文件不存在，尝试聚合生成（仅 15m/30m/1h）
        if period in ('15m', '30m', '1h'):
            # 先检查5m数据是否存在，如果不存在则从1m聚合生成
            stock_dir_5m = self._get_stock_dir(symbol, '5m')
            if not stock_dir_5m.exists():
                logger.info(f"[HotDB] {symbol} 5m数据不存在，尝试从1m聚合生成")
                df_5m = self._aggregate_from_1m(symbol, '5m')
                if df_5m is not None and not df_5m.empty:
                    # 保存5m数据（使用无递归版本）
                    self._save_kline_no_agg(symbol, df_5m, '5m')
                    logger.info(f"[HotDB] 从1m聚合生成5m数据: {len(df_5m)} 条")

            logger.info(
                f"[HotDB] {symbol} {period} 无数据，尝试从 5m 聚合生成"
            )
            return self._aggregate_from_5m(symbol, period)

        # 3. 无法生成
        return None

    def _read_from_file(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """从文件读取 K线数据（Qlib 标准格式）"""
        stock_dir = self._get_stock_dir(symbol, period)
        period_suffix = self._get_period_suffix(period)

        dates = self._read_dates(stock_dir / f'date.{period_suffix}.bin')
        closes = self._read_floats(stock_dir / f'close.{period_suffix}.bin')
        if not dates or not closes:
            return None

        n = min(len(dates), len(closes))
        opens = self._read_floats(stock_dir / f'open.{period_suffix}.bin') or [0] * n
        highs = self._read_floats(stock_dir / f'high.{period_suffix}.bin') or [0] * n
        lows = self._read_floats(stock_dir / f'low.{period_suffix}.bin') or [0] * n
        volumes = self._read_floats(stock_dir / f'volume.{period_suffix}.bin') or [0] * n
        amounts = self._read_floats(stock_dir / f'amount.{period_suffix}.bin') or [0] * n

        times = None
        if period in ['1m', '5m', '15m', '30m', '1h']:
            times = self._read_times(stock_dir / f'time.{period_suffix}.bin')

        rows = []
        for i in range(n):
            date_str = f'{dates[i][:4]}-{dates[i][4:6]}-{dates[i][6:8]}'

            if times and i < len(times):
                time_val = times[i]
                hour = time_val // 10000
                minute = (time_val // 100) % 100
                second = time_val % 100
                datetime_str = f'{date_str} {hour:02d}:{minute:02d}:{second:02d}'
            else:
                # 日线没有时间部分，使用收盘时间 15:00:00
                datetime_str = f'{date_str} 15:00:00'

            rows.append({
                'datetime': pd.Timestamp(datetime_str),
                'open': opens[i], 'high': highs[i], 'low': lows[i],
                'close': closes[i],
                'volume': volumes[i] if volumes else 0,
                'amount': amounts[i] if amounts else 0,
                '_timezone': 'Asia/Shanghai',  # 标记为北京时间
            })

        return pd.DataFrame(rows)

    def _aggregate_from_5m(self, symbol: str, target_period: str) -> Optional[pd.DataFrame]:
        """从5分钟数据聚合生成目标周期数据

        对于 15m/30m：简单按固定数量聚合（3根/6根）
        对于 1h：按交易时间段聚合（09:30-10:30, 10:30-11:30, 13:00-14:00, 14:00-15:00）

        Args:
            symbol: 股票代码
            target_period: 目标周期 (15m/30m/1h)

        Returns:
            聚合后的 DataFrame 或 None
        """
        # 先读取 5m 数据
        df_5m = self._get_or_generate_data(symbol, '5m')
        if df_5m is None or df_5m.empty:
            logger.debug(f"[HotDB] 无法获取 {symbol} 的 5m 数据，跳过聚合")
            return None

        try:
            start_time = time.time()

            # 确保数据已排序
            df = df_5m.copy().reset_index(drop=True)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)

            if target_period == '1h':
                # 1小时按交易时间段聚合
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
                f"{len(df_5m)} 根 → {len(agg_df)} 根 (耗时: {elapsed:.2f}ms)"
            )

            # 自动保存聚合结果
            self._save_kline_no_agg(symbol, agg_df, target_period)

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

            # 09:30-10:25 → 10:30 收盘
            if 930 <= time_val < 1030:
                return dt.replace(hour=10, minute=30).strftime('%Y-%m-%d %H:%M:%S')
            # 10:30-11:25 → 11:30 收盘
            elif 1030 <= time_val < 1130:
                return dt.replace(hour=11, minute=30).strftime('%Y-%m-%d %H:%M:%S')
            # 11:30-12:55 → 11:30（上午最后一根）
            elif 1130 <= time_val < 1300:
                return dt.replace(hour=11, minute=30).strftime('%Y-%m-%d %H:%M:%S')
            # 13:00-13:55 → 14:00 收盘
            elif 1300 <= time_val < 1400:
                return dt.replace(hour=14, minute=0).strftime('%Y-%m-%d %H:%M:%S')
            # 14:00-14:55 → 15:00 收盘
            elif 1400 <= time_val < 1500:
                return dt.replace(hour=15, minute=0).strftime('%Y-%m-%d %H:%M:%S')
            # 15:00 → 15:00 收盘
            elif time_val == 1500:
                return dt.replace(hour=15, minute=0).strftime('%Y-%m-%d %H:%M:%S')
            else:
                return None  # 非交易时间

        # 分配每根5分钟K线到对应的1小时周期
        df['period_close'] = df['datetime'].apply(get_hour_period)

        # 过滤掉非交易时间的数据
        df = df[df['period_close'].notna()].copy()

        if df.empty:
            return None

        # 按日期+周期收盘时间分组聚合
        df['group_key'] = df['period_close']

        agg_df = df.groupby('group_key').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum'
        }).reset_index()

        # 重命名 group_key 为 datetime（这就是收盘时间）
        agg_df = agg_df.rename(columns={'group_key': 'datetime'})
        agg_df = agg_df[['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        # 修复：将字符串转换为 Timestamp
        agg_df['datetime'] = pd.to_datetime(agg_df['datetime'])
        agg_df = agg_df.sort_values('datetime').reset_index(drop=True)

        return agg_df

    def _aggregate_by_fixed_count(self, df: pd.DataFrame, factor: int) -> Optional[pd.DataFrame]:
        """按固定数量聚合（15m=3根, 30m=6根）

        修复时间对齐问题：
        - 15分钟聚合应在 xx:15, xx:30, xx:45, xx:00 结束
        - 30分钟聚合应在 xx:00, xx:30 结束
        """
        n = len(df)
        n_agg = n // factor

        if n_agg == 0:
            return None

        # 转换为 numpy 数组
        opens = df['open'].values.astype(np.float64)
        highs = df['high'].values.astype(np.float64)
        lows = df['low'].values.astype(np.float64)
        closes = df['close'].values.astype(np.float64)
        volumes = df['volume'].values.astype(np.float64)
        datetimes = df['datetime'].values
        amount = df.get('amount', pd.Series([0.0] * n)).values.astype(np.float64)

        n_complete = n_agg * factor

        # 完整部分
        opens_2d = opens[:n_complete].reshape(n_agg, factor)
        highs_2d = highs[:n_complete].reshape(n_agg, factor)
        lows_2d = lows[:n_complete].reshape(n_agg, factor)
        closes_2d = closes[:n_complete].reshape(n_agg, factor)
        volumes_2d = volumes[:n_complete].reshape(n_agg, factor)
        amount_2d = amount[:n_complete].reshape(n_agg, factor)
        datetimes_2d = datetimes[:n_complete].reshape(n_agg, factor)

        agg_open = opens_2d[:, 0]
        agg_high = highs_2d.max(axis=1)
        agg_low = lows_2d.min(axis=1)
        agg_close = closes_2d[:, -1]
        agg_volume = volumes_2d.sum(axis=1)
        agg_amount = amount_2d.sum(axis=1)

        # 修复：计算正确的周期结束时间
        # 基于每组的开盘时间，计算它所属的固定时间槽
        period_minutes = factor * 5  # 15m 或 30m
        agg_datetime_list = []

        for i in range(n_agg):
            first_dt = pd.Timestamp(datetimes_2d[i, 0])
            hour = first_dt.hour
            minute = first_dt.minute
            time_val = hour * 100 + minute

            if period_minutes == 15:
                # 15分钟周期时间槽：
                # 09:30-09:45 -> 09:45
                # 09:45-10:00 -> 10:00
                # 10:00-10:15 -> 10:15
                # ...
                # 14:45-15:00 -> 15:00
                # 计算从09:30开始的第几个15分钟周期
                minutes_from_open = (hour - 9) * 60 + (minute - 30)
                period_index = minutes_from_open // 15
                # 结束时间 = 09:30 + (period_index + 1) * 15分钟
                end_minutes = 30 + (period_index + 1) * 15
                end_hour = 9 + end_minutes // 60
                end_min = end_minutes % 60
                period_end = first_dt.replace(hour=end_hour, minute=end_min, second=0)
            else:  # period_minutes == 30
                # 30分钟周期时间槽：
                # 09:30-10:00 -> 10:00
                # 10:00-10:30 -> 10:30
                # 10:30-11:00 -> 11:00
                # ...
                # 14:30-15:00 -> 15:00
                if 930 <= time_val < 1000:
                    period_end = first_dt.replace(hour=10, minute=0, second=0)
                elif 1000 <= time_val < 1030:
                    period_end = first_dt.replace(hour=10, minute=30, second=0)
                elif 1030 <= time_val < 1100:
                    period_end = first_dt.replace(hour=11, minute=0, second=0)
                elif 1100 <= time_val < 1130:
                    period_end = first_dt.replace(hour=11, minute=30, second=0)
                elif 1130 <= time_val < 1330:
                    # 上午收盘，跳过午休
                    # 11:30-13:00 不应该有数据，但如果有的话归到13:30
                    period_end = first_dt.replace(hour=13, minute=30, second=0)
                elif 1300 <= time_val < 1330:
                    period_end = first_dt.replace(hour=13, minute=30, second=0)
                elif 1330 <= time_val < 1400:
                    period_end = first_dt.replace(hour=14, minute=0, second=0)
                elif 1400 <= time_val < 1430:
                    period_end = first_dt.replace(hour=14, minute=30, second=0)
                elif 1430 <= time_val < 1500:
                    period_end = first_dt.replace(hour=15, minute=0, second=0)
                else:
                    # 超出交易时间，用最后一根K线时间
                    period_end = pd.Timestamp(datetimes_2d[i, -1])

            agg_datetime_list.append(period_end)

        agg_datetime = pd.DatetimeIndex(agg_datetime_list)

        # 处理余数部分
        n_remainder = n % factor
        if n_remainder > 0:
            rem_start = n_complete
            agg_open = np.append(agg_open, opens[rem_start])
            agg_high = np.append(agg_high, highs[rem_start:].max())
            agg_low = np.append(agg_low, lows[rem_start:].min())
            agg_close = np.append(agg_close, closes[-1])
            agg_volume = np.append(agg_volume, volumes[rem_start:].sum())
            agg_amount = np.append(agg_amount, amount[rem_start:].sum())
            # 余数部分使用最后一根K线的时间
            agg_datetime = agg_datetime.append(pd.DatetimeIndex([pd.Timestamp(datetimes[-1])]))

        return pd.DataFrame({
            'datetime': agg_datetime,
            'open': agg_open,
            'high': agg_high,
            'low': agg_low,
            'close': agg_close,
            'volume': agg_volume,
            'amount': agg_amount
        })

    def _aggregate_from_1m(self, symbol: str, target_period: str = '5m') -> Optional[pd.DataFrame]:
        """从1分钟数据聚合生成5分钟数据（numpy 向量化优化版）

        从1m数据聚合生成5m数据，用于当HotDB只有1m数据时自动生成5m数据。

        Args:
            symbol: 股票代码
            target_period: 目标周期 (目前仅支持 5m)

        Returns:
            聚合后的 DataFrame 或 None
        """
        # 先读取 1m 数据
        df_1m = self._get_or_generate_data(symbol, '1m')
        if df_1m is None or df_1m.empty:
            logger.debug(f"[HotDB] 无法获取 {symbol} 的 1m 数据，跳过聚合")
            return None

        # 聚合倍数：1m → 5m = 5倍
        factor = 5
        if target_period != '5m':
            return None

        try:
            start_time = time.time()

            # 确保数据已排序
            df = df_1m.copy().reset_index(drop=True)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)

            n = len(df)
            n_agg = n // factor
            n_remainder = n % factor

            if n_agg == 0:
                logger.debug(f"[HotDB] {symbol} 1m 数据不足 {factor} 条，无法聚合 {target_period}")
                return None

            # 转换为 numpy 数组
            opens = df['open'].values.astype(np.float64)
            highs = df['high'].values.astype(np.float64)
            lows = df['low'].values.astype(np.float64)
            closes = df['close'].values.astype(np.float64)
            volumes = df['volume'].values.astype(np.float64)
            datetimes = df['datetime'].values

            amount = df.get('amount', pd.Series([0.0] * n)).values.astype(np.float64)

            # 分离完整部分和余数部分
            n_complete = n_agg * factor

            # 完整部分：使用 reshape 向量化
            opens_2d = opens[:n_complete].reshape(n_agg, factor)
            highs_2d = highs[:n_complete].reshape(n_agg, factor)
            lows_2d = lows[:n_complete].reshape(n_agg, factor)
            closes_2d = closes[:n_complete].reshape(n_agg, factor)
            volumes_2d = volumes[:n_complete].reshape(n_agg, factor)
            amount_2d = amount[:n_complete].reshape(n_agg, factor)
            datetimes_2d = datetimes[:n_complete].reshape(n_agg, factor)

            # 向量化聚合
            agg_open = opens_2d[:, 0]
            agg_high = highs_2d.max(axis=1)
            agg_low = lows_2d.min(axis=1)
            agg_close = closes_2d[:, -1]
            agg_volume = volumes_2d.sum(axis=1)
            agg_amount = amount_2d.sum(axis=1)
            agg_datetime = datetimes_2d[:, -1]  # 使用收盘时间（最后一根5分钟的时间）

            # 处理余数部分（最后一组不完整）
            if n_remainder > 0:
                rem_start = n_complete
                agg_open = np.append(agg_open, opens[rem_start])
                agg_high = np.append(agg_high, highs[rem_start:].max())
                agg_low = np.append(agg_low, lows[rem_start:].min())
                agg_close = np.append(agg_close, closes[-1])
                agg_volume = np.append(agg_volume, volumes[rem_start:].sum())
                agg_amount = np.append(agg_amount, amount[rem_start:].sum())
                agg_datetime = np.append(agg_datetime, datetimes[-1])  # 使用最后一根的时间作为收盘时间

            # 构造结果 DataFrame
            agg_df = pd.DataFrame({
                'datetime': agg_datetime,
                'open': agg_open,
                'high': agg_high,
                'low': agg_low,
                'close': agg_close,
                'volume': agg_volume,
                'amount': agg_amount
            })

            elapsed = (time.time() - start_time) * 1000

            logger.debug(
                f"[HotDB] 聚合 {symbol} 1m → {target_period}: "
                f"{len(df_1m)} 根 → {len(agg_df)} 根 (耗时: {elapsed:.2f}ms)"
            )

            return agg_df

        except Exception as e:
            logger.warning(f"[HotDB] 聚合 {symbol} 1m → {target_period} 失败: {e}")
            return None

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """HotDB 不支持实时行情"""
        return {}

    def save_kline(self, symbol: str, df: pd.DataFrame, period: str = '1d') -> bool:
        """保存K线数据到 HotDB（智能模式）

        - 日线: 追加模式（读取现有 -> 合并去重 -> 写入）
        - 分钟线: 覆盖模式（直接替换）
        - 1分钟线: 保存3天，自动清理超期数据

        Args:
            symbol: 股票代码 (如 600519.SH)
            df: DataFrame with columns [datetime, open, high, low, close, volume, amount]
            period: 周期 (1d/1w/1mon/1m/5m/15m/30m/1h)

        Returns:
            是否保存成功
        """
        if df is None or df.empty:
            logger.warning(f"[HotDB] 保存 {symbol} {period} 数据为空，跳过")
            return False

        try:
            stock_dir = self._get_stock_dir(symbol, period)

            # 准备数据
            df = df.copy()

            # 如果 datetime 是索引，转为列
            if df.index.name == 'datetime' or 'datetime' not in df.columns:
                df = df.reset_index()

            # 统一列名
            if 'datetime' not in df.columns and 'time' in df.columns:
                df.rename(columns={'time': 'datetime'}, inplace=True)

            if 'datetime' not in df.columns:
                logger.error(f"[HotDB] 保存 {symbol} {period} 失败: DataFrame 缺少 'datetime' 或 'time' 列")
                return False

            df['datetime'] = pd.to_datetime(df['datetime'])

            # 1分钟数据：清理7天前的数据（增加保留天数）
            if period == '1m':
                self._cleanup_old_1m_data(symbol, df, days=7)

            # 日线使用智能合并（追加新日期）
            if period == '1d':
                # 读取现有数据
                existing_df = self._read_existing_kline(symbol, period)
                if existing_df is not None and not existing_df.empty:
                    # 合并并去重
                    merged_df = pd.concat([existing_df, df], ignore_index=True)
                    merged_df['datetime'] = pd.to_datetime(merged_df['datetime'])
                    merged_df = merged_df.drop_duplicates(subset=['datetime'], keep='last')
                    merged_df = merged_df.sort_values('datetime').reset_index(drop=True)
                    df = merged_df
                    logger.info(
                        f"[HotDB] 合并 {symbol} {period}: "
                        f"现有 {len(existing_df)} 条 + 新增 {len(df)} 条"
                    )
                else:
                    logger.info(f"[HotDB] 新增 {symbol} {period}: {len(df)} 条")

            # 分钟线也使用追加合并模式
            elif period in ['1m', '5m', '15m', '30m', '1h']:
                # 读取现有数据
                existing_df = self._read_existing_kline(symbol, period)
                if existing_df is not None and not existing_df.empty:
                    # 合并并去重
                    merged_df = pd.concat([existing_df, df], ignore_index=True)
                    merged_df['datetime'] = pd.to_datetime(merged_df['datetime'])
                    merged_df = merged_df.drop_duplicates(subset=['datetime'], keep='last')
                    merged_df = merged_df.sort_values('datetime').reset_index(drop=True)
                    df = merged_df
                    logger.info(
                        f"[HotDB] 合并 {symbol} {period}: "
                        f"现有 {len(existing_df)} 条 + 新增 {len(df)} 条"
                    )
                else:
                    logger.info(f"[HotDB] 新增 {symbol} {period}: {len(df)} 条")

            # 统一时区：将所有时间转换为北京时间（naive）
            def localize_to_beijing(dt):
                """将 datetime 转换为北京时间（naive）"""
                if pd.isna(dt):
                    return dt
                if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                    # 有时区信息：转换为 UTC+8，然后移除时区标记
                    beijing_time = dt.tz_convert('Asia/Shanghai')
                    return beijing_time.tz_localize(None)
                else:
                    # naive datetime：假设已经是北京时间，直接返回
                    return dt

            df['datetime'] = df['datetime'].apply(localize_to_beijing)

            # 过滤掉无效日期（1970-01-01 或 NaT）
            min_valid_date = pd.Timestamp('2010-01-01')
            before_filter = len(df)
            df = df[df['datetime'] >= min_valid_date].copy()
            after_filter = len(df)
            if before_filter != after_filter:
                logger.warning(f"[HotDB] 过滤掉 {before_filter - after_filter} 条无效日期数据（< 2010-01-01）")

            # 日期转换为YYYYMMDD格式
            period_suffix = self._get_period_suffix(period)
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

            # 对于分钟线，额外保存时间信息（HHMMSS格式）
            if period in ['1m', '5m', '15m', '30m', '1h']:
                times = df['datetime'].dt.strftime('%H%M%S').astype(int).tolist()
                self._write_ints(stock_dir / f'time.{period_suffix}.bin', times)
                logger.debug(f"[HotDB] 保存时间信息: {len(times)} 条 ({period})")

            # 更新元数据
            self._update_metadata(symbol, period, len(df))

            # 清除内存缓存（数据已更新）
            cache_key = f"{symbol}:{period}"
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
                del self._memory_cache_time[cache_key]
                logger.debug(f"[HotDB-L1] 清除缓存: {cache_key}")

            logger.info(f"[HotDB] 保存 {symbol} {period}: {len(df)} 条数据")

            # 5m 数据保存后，自动聚合生成 15m/30m/1h
            if period == '5m':
                self._auto_aggregate_from_5m(symbol, df)

            return True

        except Exception as e:
            logger.error(f"[HotDB] 保存 {symbol} {period} 失败: {e}")
            return False

    def _auto_aggregate_from_5m(self, symbol: str, df_5m: pd.DataFrame):
        """5m 数据保存后，自动聚合生成 15m/30m/1h（numpy 向量化 + 并行保存）

        优化说明：
        - 一次性聚合所有周期，避免重复数据准备
        - 使用 numpy reshape 向量化操作
        - 使用线程池并行保存 3 个周期（IO 并行）

        Args:
            symbol: 股票代码
            df_5m: 刚保存的 5m 数据
        """
        if df_5m is None or df_5m.empty:
            return

        try:
            start_total = time.time()

            # 准备数据（只准备一次）
            df = df_5m.copy().reset_index(drop=True)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)

            n = len(df)

            # 转换为 numpy 数组
            opens = df['open'].values.astype(np.float64)
            highs = df['high'].values.astype(np.float64)
            lows = df['low'].values.astype(np.float64)
            closes = df['close'].values.astype(np.float64)
            volumes = df['volume'].values.astype(np.float64)
            datetimes = df['datetime'].values
            amount = df.get('amount', pd.Series([0.0] * n)).values.astype(np.float64)

            # 聚合配置
            periods_config = [
                ('15m', 3),
                ('30m', 6),
                ('1h', 12),
            ]

            # 聚合所有周期
            agg_results = {}
            for target_period, factor in periods_config:
                n_agg = n // factor
                n_remainder = n % factor

                if n_agg == 0:
                    continue

                n_complete = n_agg * factor

                # 向量化聚合
                opens_2d = opens[:n_complete].reshape(n_agg, factor)
                highs_2d = highs[:n_complete].reshape(n_agg, factor)
                lows_2d = lows[:n_complete].reshape(n_agg, factor)
                closes_2d = closes[:n_complete].reshape(n_agg, factor)
                volumes_2d = volumes[:n_complete].reshape(n_agg, factor)
                amount_2d = amount[:n_complete].reshape(n_agg, factor)
                datetimes_2d = datetimes[:n_complete].reshape(n_agg, factor)

                agg_open = opens_2d[:, 0]
                agg_high = highs_2d.max(axis=1)
                agg_low = lows_2d.min(axis=1)
                agg_close = closes_2d[:, -1]
                agg_volume = volumes_2d.sum(axis=1)
                agg_amount = amount_2d.sum(axis=1)
                agg_datetime = datetimes_2d[:, -1]

                # 处理余数
                if n_remainder > 0:
                    rem_start = n_complete
                    agg_open = np.append(agg_open, opens[rem_start])
                    agg_high = np.append(agg_high, highs[rem_start:].max())
                    agg_low = np.append(agg_low, lows[rem_start:].min())
                    agg_close = np.append(agg_close, closes[-1])
                    agg_volume = np.append(agg_volume, volumes[rem_start:].sum())
                    agg_amount = np.append(agg_amount, amount[rem_start:].sum())
                    agg_datetime = np.append(agg_datetime, datetimes[rem_start])

                agg_df = pd.DataFrame({
                    'datetime': agg_datetime,
                    'open': agg_open,
                    'high': agg_high,
                    'low': agg_low,
                    'close': agg_close,
                    'volume': agg_volume,
                    'amount': agg_amount
                })

                agg_results[target_period] = agg_df

            # 并行保存
            def save_one_period(period_data):
                target_period, agg_df = period_data
                try:
                    self._save_kline_no_agg(symbol, agg_df, target_period)
                    return target_period, len(agg_df), None
                except Exception as e:
                    return target_period, 0, str(e)

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(save_one_period, (period, df))
                    for period, df in agg_results.items()
                }

                for future in as_completed(futures):
                    period, count, error = future.result()
                    if error:
                        logger.warning(f"[HotDB] 保存 {symbol} {period} 失败: {error}")
                    else:
                        logger.debug(f"[HotDB] 保存 {symbol} {period}: {count} 条")

            elapsed = (time.time() - start_total) * 1000
            logger.info(
                f"[HotDB] 聚合+保存 {symbol}: 3 个周期 (总耗时: {elapsed:.2f}ms)"
            )

        except Exception as e:
            logger.warning(f"[HotDB] 聚合 {symbol} 失败: {e}")

    def _save_kline_no_agg(
        self, symbol: str, df: pd.DataFrame, period: str = '1d'
    ) -> bool:
        """保存K线数据到 HotDB（不触发聚合）

        用于自动聚合时保存结果，避免递归触发聚合
        """
        if df is None or df.empty:
            return False

        try:
            stock_dir = self._get_stock_dir(symbol, period)
            df = df.copy()

            if df.index.name == 'datetime' or 'datetime' not in df.columns:
                df = df.reset_index()

            if 'datetime' not in df.columns and 'time' in df.columns:
                df.rename(columns={'time': 'datetime'}, inplace=True)

            if 'datetime' not in df.columns:
                return False

            df['datetime'] = pd.to_datetime(df['datetime'])

            # 统一时区：将所有时间转换为北京时间（naive）
            def localize_to_beijing(dt):
                """将 datetime 转换为北京时间（naive）"""
                if pd.isna(dt):
                    return dt
                if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                    beijing_time = dt.tz_convert('Asia/Shanghai')
                    return beijing_time.tz_localize(None)
                else:
                    return dt

            df['datetime'] = df['datetime'].apply(localize_to_beijing)

            # 日期转换
            period_suffix = self._get_period_suffix(period)
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

            # 分钟线额外保存时间
            if period in ['1m', '5m', '15m', '30m', '1h']:
                times = df['datetime'].dt.strftime('%H%M%S').astype(int).tolist()
                self._write_ints(stock_dir / f'time.{period_suffix}.bin', times)

            # 更新元数据
            self._update_metadata(symbol, period, len(df))

            # 清除内存缓存
            cache_key = f"{symbol}:{period}"
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
                del self._memory_cache_time[cache_key]

            return True

        except Exception:
            return False

    def _read_existing_kline(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """读取现有的 K线数据（用于合并）"""
        try:
            result = self.get_kline([symbol], period=period)
            return result.get(symbol)
        except Exception:
            return None

    def delete_kline(self, symbol: str, period: Optional[str] = None) -> bool:
        """删除股票数据

        Args:
            symbol: 股票代码
            period: 周期 (如 '1d', '1m')，None 表示删除所有周期

        Returns:
            是否删除成功
        """
        try:
            exchange = self._exchange(symbol)
            dir_name = self._dir_name(symbol)

            if period:
                # 删除指定周期
                period_suffix = self._get_period_suffix(period)
                period_dir = self._data_dir / exchange / period_suffix / dir_name
                if period_dir.exists():
                    import shutil
                    shutil.rmtree(period_dir)
                    logger.info(f"[HotDB] 删除 {symbol} {period} 数据")
                    # 更新元数据
                    self._remove_from_metadata(symbol, period)
                    # 清除内存缓存
                    cache_key = f"{symbol}:{period}"
                    if cache_key in self._memory_cache:
                        del self._memory_cache[cache_key]
                    if cache_key in self._memory_cache_time:
                        del self._memory_cache_time[cache_key]
                    return True
            else:
                # 删除所有周期
                exchange_dir = self._data_dir / exchange
                if exchange_dir.exists():
                    for period_dir in exchange_dir.glob('*/'):
                        if (period_dir / dir_name).exists():
                            import shutil
                            shutil.rmtree(period_dir / dir_name)
                    logger.info(f"[HotDB] 删除 {symbol} 所有周期数据")
                    # 更新元数据
                    self._remove_from_metadata(symbol, None)
                    # 清除所有周期的内存缓存
                    cache_keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(f"{symbol}:")]
                    for cache_key in cache_keys_to_delete:
                        del self._memory_cache[cache_key]
                        if cache_key in self._memory_cache_time:
                            del self._memory_cache_time[cache_key]
                    if cache_keys_to_delete:
                        logger.info(f"[HotDB] 已清除 {len(cache_keys_to_delete)} 个内存缓存项")
                    return True

            return False

        except Exception as e:
            logger.error(f"[HotDB] 删除 {symbol} 失败: {e}")
            return False

    def get_data_info(self, symbol: str, period: str) -> Optional[Dict]:
        """获取数据摘要信息（O(1) 复杂度，只读取 date.bin 首尾）

        用于快速检查数据范围，判断是否需要增量更新。

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            dict: {count, earliest, latest, has_data} 或 None
        """
        try:
            stock_dir = self._get_stock_dir(symbol, period)
            period_suffix = self._get_period_suffix(period)
            date_file = stock_dir / f'date.{period_suffix}.bin'

            if not date_file.exists():
                return {'count': 0, 'earliest': None, 'latest': None, 'has_data': False}

            with open(date_file, 'rb') as f:
                data = f.read()

            if len(data) < 8:
                return {'count': 0, 'earliest': None, 'latest': None, 'has_data': False}

            count = struct.unpack('<i', data[:4])[0]
            if count == 0:
                return {'count': 0, 'earliest': None, 'latest': None, 'has_data': False}

            # 只读首尾元素
            earliest_int = struct.unpack('<i', data[4:8])[0]
            latest_int = struct.unpack('<i', data[4 + (count - 1) * 4:4 + count * 4])[0]

            # 转换为日期字符串
            earliest_str = f'{earliest_int}'
            latest_str = f'{latest_int}'

            earliest_date = f'{earliest_str[:4]}-{earliest_str[4:6]}-{earliest_str[6:8]}'
            latest_date = f'{latest_str[:4]}-{latest_str[4:6]}-{latest_str[6:8]}'

            # === 修复：分钟线需要精确时间戳 ===
            if period != '1d':
                # 分钟线：从文件名读取的日期只有年月日，需要加上时间
                # 获取实际K线数据来确定精确的最后时间
                try:
                    # 读取最后一条K线的时间
                    time_file = stock_dir / f'time.{period_suffix}.bin'
                    if time_file.exists():
                        with open(time_file, 'rb') as f:
                            # 读取文件最后4字节（最后一条时间）
                            f.seek(-4, 2)  # 从结尾往前移4字节
                            last_time_int = struct.unpack('<i', f.read(4))[0]
                            # 转换为时间字符串 HHMMSS
                            last_time_str = f'{last_time_int:06d}'
                            latest_time = f'{last_time_str[:2]}:{last_time_str[2:4]}:{last_time_str[4:6]}'
                            latest_ts = pd.Timestamp(f'{latest_date} {latest_time}')
                    else:
                        # 没有时间文件，假设是收盘时间 15:00:00
                        latest_ts = pd.Timestamp(f'{latest_date} 15:00:00')
                except Exception:
                    # 出错时假设是收盘时间
                    latest_ts = pd.Timestamp(f'{latest_date} 15:00:00')
            else:
                # 日线：只需要日期精度
                latest_ts = pd.Timestamp(latest_date)

            return {
                'count': count,
                'earliest': pd.Timestamp(earliest_date),
                'latest': latest_ts,
                'has_data': True
            }

        except Exception as e:
            logger.warning(f"[HotDB] 获取 {symbol} {period} 数据信息失败: {e}")
            return None

    def detect_gap(self, symbol: str, period: str) -> Optional[Dict]:
        """检测数据缺口

        判断 HotDB 数据是否需要增量更新：
        - 日线：最新日期与今天相差 > 1 天，且当前已过 09:30
        - 分钟线：最新时间与现在相差超过阈值

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            dict: {has_gap, latest, missing_start, missing_end, reason} 或 None
        """
        try:
            info = self.get_data_info(symbol, period)
            if not info or not info['has_data']:
                return {'has_gap': True, 'reason': 'no_data', 'latest': None}

            latest = info['latest']
            now = pd.Timestamp.now(tz=None).replace(tzinfo=None)

            if period == '1d':
                # 日线：检查缺失的交易日（排除周末、节假日）
                today = now.date()
                latest_date = latest.date()

                # 计算自然日差异
                natural_days_diff = (today - latest_date).days

                if natural_days_diff <= 0:
                    # 数据是未来的（不应该发生），不算缺口
                    return {'has_gap': False, 'reason': 'up_to_date', 'latest': latest}

                # 计算 (latest_date, today] 范围内的实际交易日
                missing_trading_days = []
                current_date = latest_date + timedelta(days=1)

                detector = TradingTimeDetectorV2()

                while current_date <= today:
                    date_str = current_date.strftime('%Y%m%d')
                    # 使用 is_trading_day 判断（已排除周末和节假日）
                    try:
                        current_dt = datetime.combine(current_date, datetime.min.time())
                        if detector.is_trading_day(current_dt):
                            missing_trading_days.append(date_str)
                    except Exception:
                        # 判断失败，使用简单逻辑：排除周末
                        weekday = current_date.weekday()
                        if weekday < 5:  # 0-4 是周一到周五
                            missing_trading_days.append(date_str)
                    current_date += timedelta(days=1)

                trading_days_count = len(missing_trading_days)

                if trading_days_count > 0:
                    # 有交易日缺失，报告缺口
                    # 缺口范围：第一个缺失交易日 ~ 最后一个缺失交易日
                    first_missing_str = missing_trading_days[0]
                    last_missing_str = missing_trading_days[-1]
                    first_missing = pd.Timestamp(first_missing_str)
                    last_missing = pd.Timestamp(last_missing_str)

                    # 检查是否"只差今天"
                    is_only_today = (
                        trading_days_count == 1 and
                        first_missing.date() == today
                    )

                    if is_only_today:
                        # 只差今天，需要判断交易时间
                        if TradingTimeChecker.is_trading_time():
                            return {
                                'has_gap': True,
                                'reason': 'today_missing',
                                'latest': latest,
                                'missing_start': first_missing,
                                'missing_end': last_missing,
                                'days_missing': trading_days_count,
                                'trading_days_missing': missing_trading_days
                            }
                        # 开盘前，今天缺失不算缺口
                        return {'has_gap': False, 'reason': 'up_to_date', 'latest': latest}
                    else:
                        # 缺失多个交易日（包括历史），永远算缺口
                        # 检查是否是大缺口（>2周，约10个交易日）
                        is_large_gap = trading_days_count > 10

                        if is_large_gap:
                            logger.warning(
                                f"[HotDB] {symbol} 检测到大缺口: 缺失 {trading_days_count} 个交易日 "
                                f"({first_missing.date()} ~ {last_missing.date()}) "
                                f"建议更新 LocalDB（冷数据库）以加快获取速度"
                            )

                        return {
                            'has_gap': True,
                            'reason': 'daily_gap',
                            'latest': latest,
                            'missing_start': first_missing,
                            'missing_end': last_missing,
                            'days_missing': trading_days_count,
                            'trading_days_missing': missing_trading_days,
                            'is_large_gap': is_large_gap
                        }

                return {'has_gap': False, 'reason': 'up_to_date', 'latest': latest}

            else:
                # 分钟线：首先检查数据内部缺口（排除周末、节假日、正常隔夜）

                # === 1. 检查数据内部缺口（只检测真正的交易日缺失）===
                df_dict = self.get_kline(symbols=[symbol], period=period, count=10000, allow_stale=True)
                if symbol in df_dict and not df_dict[symbol].empty:
                    df = df_dict[symbol].copy()
                    df = df.sort_values('datetime').reset_index(drop=True)

                    # 计算相邻数据点的时间差
                    time_diffs = df['datetime'].diff()

                    # 只检查超过4小时的缺口（排除正常隔夜和午休）
                    large_gaps = time_diffs[time_diffs > pd.Timedelta(hours=4)]

                    if len(large_gaps) > 0:
                        # 检查每个大缺口，找出缺失交易日最多的那个
                        from ..utils.trading_time_detector import TradingTimeDetectorV2
                        detector = TradingTimeDetectorV2()

                        max_missing_days = 0
                        max_gap_info = None

                        for gap_idx, gap in large_gaps.items():
                            if gap_idx == 0:
                                continue

                            # 缺口前后的时间
                            gap_start = df.iloc[gap_idx - 1]['datetime']
                            gap_end = df.iloc[gap_idx]['datetime']

                            # 计算这两个日期之间缺失的交易日
                            current_date = gap_start.date()
                            end_date = gap_end.date()
                            missing_trading_days = []

                            while current_date < end_date:
                                current_date = current_date + pd.Timedelta(days=1)
                                try:
                                    current_dt = datetime.combine(current_date, datetime.min.time())
                                    if detector.is_trading_day(current_dt):
                                        missing_trading_days.append(current_date)
                                except Exception:
                                    # 判断失败，简单排除周末
                                    weekday = current_date.weekday()
                                    if weekday < 5:  # 0-4 是周一到周五
                                        missing_trading_days.append(current_date)

                            # 记录缺失交易日最多的缺口
                            if len(missing_trading_days) > max_missing_days:
                                max_missing_days = len(missing_trading_days)
                                max_gap_info = {
                                    'gap_start': gap_start,
                                    'gap_end': gap_end,
                                    'gap': gap,
                                    'missing_days': missing_trading_days
                                }

                        # 如果有缺失交易日的缺口，返回最大的那个
                        if max_gap_info:
                            logger.warning(
                                f"[HotDB] {symbol} {period} 发现交易日缺口: "
                                f"{max_gap_info['gap_start']} -> {max_gap_info['gap_end']} "
                                f"(缺失 {max_missing_days} 个交易日)"
                            )

                            return {
                                'has_gap': True,
                                'reason': 'internal_gap',
                                'latest': df['datetime'].iloc[-1],
                                'missing_start': max_gap_info['gap_start'],
                                'missing_end': max_gap_info['gap_end'],
                                'gap_size_hours': max_gap_info['gap'].total_seconds() / 3600,
                                'missing_trading_days': max_missing_days
                            }

                # === 2. 检查最新数据与当前时间的差距 ===
                time_diff_minutes = (now - latest).total_seconds() / 60

                # 阈值设置（分钟）
                thresholds = {
                    '1m': 5,
                    '5m': 15,
                    '15m': 30,
                    '30m': 60,
                    '1h': 120
                }

                threshold = thresholds.get(period, 15)

                # 分钟线缺口检测：只要有差距就认为是缺口
                # 注意：非交易时间在线获取可能失败，但检测应该正常工作
                if time_diff_minutes > threshold:
                    return {
                        'has_gap': True,
                        'reason': 'intraday_gap',
                        'latest': latest,
                        'missing_start': latest + timedelta(minutes=period_to_minutes(period)),
                        'missing_end': now,
                        'minutes_missing': int(time_diff_minutes)
                    }

                return {'has_gap': False, 'reason': 'up_to_date', 'latest': latest}

        except Exception as e:
            logger.warning(f"[HotDB] 检测 {symbol} {period} 缺口失败: {e}")
            return None

    def has_symbol(self, symbol: str) -> bool:
        """检查股票是否在热数据库中"""
        try:
            # 检查至少日线数据存在
            stock_dir = self._get_stock_dir(symbol, '1d')
            return stock_dir.exists() and (stock_dir / 'close.day.bin').exists()
        except Exception:
            return False

    def list_symbols(self) -> List[str]:
        """列出热数据库中的所有股票"""
        try:
            symbols = []
            for exchange in ['sh', 'sz', 'bj']:
                exchange_dir = self._data_dir / exchange
                if not exchange_dir.exists():
                    continue
                for period_dir in exchange_dir.iterdir():
                    if period_dir.is_dir():
                        for stock_dir in period_dir.iterdir():
                            if stock_dir.is_dir() and (stock_dir / 'close.day.bin').exists():
                                # 提取股票代码
                                dir_name = stock_dir.name
                                if dir_name.startswith(exchange):
                                    code = dir_name[2:]  # 去掉交易所前缀
                                    if exchange == 'sh':
                                        suffix = '.SH'
                                    elif exchange == 'sz':
                                        suffix = '.SZ'
                                    else:
                                        suffix = '.BJ'
                                    symbols.append(f"{code}{suffix}")
            return sorted(set(symbols))
        except Exception as e:
            logger.warning(f"[HotDB] 列出股票失败: {e}")
            return []

    def _update_metadata(self, symbol: str, period: str, count: int):
        """更新元数据"""
        try:
            key = f"{symbol}_{period}"
            self._metadata[key] = {
                'symbol': symbol,
                'period': period,
                'count': count,
                'last_update': datetime.now().isoformat()
            }
            self._save_metadata()
        except Exception as e:
            logger.warning(f"[HotDB] 更新元数据失败: {e}")

    def _remove_from_metadata(self, symbol: str, period: Optional[str]):
        """从元数据中移除"""
        try:
            if period:
                key = f"{symbol}_{period}"
                if key in self._metadata:
                    del self._metadata[key]
            else:
                # 移除该股票的所有周期
                keys_to_remove = [k for k in self._metadata.keys() if k.startswith(f"{symbol}_")]
                for key in keys_to_remove:
                    del self._metadata[key]
            self._save_metadata()
        except Exception as e:
            logger.warning(f"[HotDB] 移除元数据失败: {e}")

    def _cleanup_old_1m_data(self, symbol: str, new_df: pd.DataFrame, days: int = 3):
        """清理1分钟数据中超过指定天数的旧数据

        Args:
            symbol: 股票代码
            new_df: 新数据（将要保存的数据）
            days: 保留天数（默认3天）
        """
        try:
            if new_df.empty:
                return

            # 计算截止时间
            cutoff_time = new_df['datetime'].max() - timedelta(days=days)

            # 过滤掉截止时间之前的数据
            filtered_df = new_df[new_df['datetime'] >= cutoff_time].copy()

            removed_count = len(new_df) - len(filtered_df)
            if removed_count > 0:
                logger.info(
                    f"[HotDB] 清理 {symbol} 1m 数据: 删除 {removed_count} 条超过 "
                    f"{days} 天的数据，保留 {len(filtered_df)} 条"
                )

                # 更新 new_df（通过修改引用）
                new_df.drop(new_df.index, inplace=True)
                new_df.update(filtered_df)

        except Exception as e:
            logger.warning(f"[HotDB] 清理 {symbol} 1m 数据失败: {e}")


def create_hotdb_adapter():
    """创建 HotDB 适配器实例"""
    return V5HotDBAdapter()
