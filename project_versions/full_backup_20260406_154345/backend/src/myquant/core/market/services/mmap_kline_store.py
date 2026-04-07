"""
Mmap K线存储 - 通达信级别的内存映射文件方案

核心设计：
1. 数据存储在磁盘文件，使用 mmap 内存映射
2. 启动时只映射文件，不加载数据到 Python 内存
3. 访问时系统按需加载，天然 LRU 缓存
4. 内存占用极低（只有系统缓存，无 Python 对象开销）

文件格式（类似通达信 .lday）：
[头部: 64字节][K线数据: 32字节/条 × N条]

头部结构：
- magic: 4字节 'MYQT'
- version: 4字节
- symbol: 12字节
- period: 4字节
- count: 4字节 (实际条数)
- reserved: 36字节

K线数据（32字节）：
- timestamp: 8字节 (uint64)
- open: 4字节 (float32)
- high: 4字节 (float32)
- low: 4字节 (float32)
- close: 4字节 (float32)
- volume: 4字节 (uint32)
- amount: 4字节 (float32)
"""

import mmap
import struct
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass
from collections import OrderedDict
from loguru import logger
import pandas as pd

# 数据目录
MMAP_DATA_DIR = Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "mmap_kline"


# 头部格式: magic(4) + version(4) + symbol(12) + period(4) + count(4) + reserved(36) = 64字节
HEADER_FORMAT = '<4sI12s4sI36s'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# K线记录格式: timestamp(8) + open(4) + high(4) + low(4) + close(4) + volume(4) + amount(4) = 32字节
RECORD_FORMAT = '<Qffffff'  # uint64 + 6个float32
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)


@dataclass
class MmapKlineHeader:
    """Mmap 文件头部"""
    magic: bytes      # 'MYQT'
    version: int      # 版本号
    symbol: str       # 股票代码
    period: str       # 周期
    count: int        # K线条数

    def to_bytes(self) -> bytes:
        """序列化为字节"""
        symbol_bytes = self.symbol.encode('utf-8')[:12].ljust(12, b'\x00')
        period_bytes = self.period.encode('utf-8')[:4].ljust(4, b'\x00')
        return struct.pack(HEADER_FORMAT, self.magic, self.version, symbol_bytes, period_bytes, self.count, b'\x00' * 36)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'MmapKlineHeader':
        """从字节解析"""
        magic, version, symbol_bytes, period_bytes, count, _ = struct.unpack(HEADER_FORMAT, data)
        return cls(
            magic=magic,
            version=version,
            symbol=symbol_bytes.decode('utf-8').rstrip('\x00'),
            period=period_bytes.decode('utf-8').rstrip('\x00'),
            count=count
        )


@dataclass
class MmapKlineRecord:
    """单条 K 线记录"""
    timestamp: int    # Unix 时间戳（秒）
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float

    def to_bytes(self) -> bytes:
        """序列化为字节"""
        return struct.pack(RECORD_FORMAT, self.timestamp, self.open, self.high, self.low, self.close, self.volume, self.amount)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'MmapKlineRecord':
        """从字节解析"""
        ts, o, h, l, c, v, a = struct.unpack(RECORD_FORMAT, data)
        return cls(timestamp=ts, open=o, high=h, low=l, close=c, volume=v, amount=a)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'amount': self.amount
        }


class MmapKlineFile:
    """单个股票的 Mmap K线文件"""

    VERSION = 1
    MAGIC = b'MYQT'

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self._mmap: Optional[mmap.mmap] = None
        self._header: Optional[MmapKlineHeader] = None
        self._lock = threading.RLock()

    def _ensure_dir(self):
        """确保目录存在"""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def create(self, symbol: str, period: str, records: List[MmapKlineRecord]) -> bool:
        """创建新的 mmap 文件"""
        try:
            self._ensure_dir()

            # 计算文件大小
            file_size = HEADER_SIZE + len(records) * RECORD_SIZE

            # 创建文件并写入数据
            with open(self.filepath, 'wb') as f:
                # 写入头部
                header = MmapKlineHeader(
                    magic=self.MAGIC,
                    version=self.VERSION,
                    symbol=symbol,
                    period=period,
                    count=len(records)
                )
                f.write(header.to_bytes())

                # 写入记录
                for record in records:
                    f.write(record.to_bytes())

                # 截断到实际大小
                f.truncate(file_size)

            logger.info(f"[MmapKlineFile] 创建文件: {self.filepath}, {len(records)} 条记录")
            return True

        except Exception as e:
            logger.error(f"[MmapKlineFile] 创建文件失败: {self.filepath}, {e}")
            return False

    def open(self) -> bool:
        """打开并映射文件"""
        try:
            if not self.filepath.exists():
                return False

            with self._lock:
                if self._mmap is not None:
                    return True  # 已经打开

                # 打开文件
                file_size = self.filepath.stat().st_size
                if file_size < HEADER_SIZE:
                    logger.warning(f"[MmapKlineFile] 文件太小: {self.filepath}")
                    return False

                # 使用 mmap 映射文件
                with open(self.filepath, 'rb') as f:
                    self._mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

                # 读取头部
                header_data = self._mmap[:HEADER_SIZE]
                self._header = MmapKlineHeader.from_bytes(header_data)

                # 验证头部
                if self._header.magic != self.MAGIC:
                    logger.warning(f"[MmapKlineFile] 文件格式错误: {self.filepath}")
                    self.close()
                    return False

            return True

        except Exception as e:
            logger.error(f"[MmapKlineFile] 打开文件失败: {self.filepath}, {e}")
            self.close()
            return False

    def close(self):
        """关闭映射"""
        with self._lock:
            if self._mmap is not None:
                self._mmap.close()
                self._mmap = None
            self._header = None

    def is_open(self) -> bool:
        """检查是否已打开"""
        return self._mmap is not None

    @property
    def count(self) -> int:
        """获取记录数"""
        return self._header.count if self._header else 0

    def get_record(self, index: int) -> Optional[MmapKlineRecord]:
        """获取单条记录（O(1)随机访问）"""
        with self._lock:
            if not self.is_open() or index < 0 or index >= self.count:
                return None

            # 直接计算偏移量，从 mmap 读取
            offset = HEADER_SIZE + index * RECORD_SIZE
            record_data = self._mmap[offset:offset + RECORD_SIZE]

            if len(record_data) != RECORD_SIZE:
                return None

            return MmapKlineRecord.from_bytes(record_data)

    def get_records(self, start: int = 0, count: Optional[int] = None) -> List[MmapKlineRecord]:
        """获取多条记录"""
        with self._lock:
            if not self.is_open():
                return []

            if start < 0:
                start = 0
            if count is None or start + count > self.count:
                count = self.count - start

            records = []
            for i in range(start, start + count):
                record = self.get_record(i)
                if record:
                    records.append(record)

            return records

    def get_last_n(self, n: int) -> List[MmapKlineRecord]:
        """获取最后 N 条记录"""
        with self._lock:
            if not self.is_open() or n <= 0:
                return []

            start = max(0, self.count - n)
            return self.get_records(start, n)

    def to_dataframe(self) -> pd.DataFrame:
        """转换为 DataFrame"""
        records = self.get_records()
        if not records:
            return pd.DataFrame(columns=['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount'])

        data = [r.to_dict() for r in records]
        return pd.DataFrame(data)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()


class MmapKlineStore:
    """
    Mmap K线存储管理器

    管理所有股票的 mmap 文件，提供统一的访问接口
    """

    # 支持的周期
    SUPPORTED_PERIODS = ['1m', '5m', '15m', '30m', '1h', '1d', 'week', 'month']

    # 默认预加载周期
    DEFAULT_PERIODS = ['1d', '5m', '15m', '30m', '1h']

    def __init__(self, data_dir: Optional[Path] = None, max_files: int = 200):
        self.data_dir = data_dir or MMAP_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 缓存已打开的文件: key = "symbol_period" -> MmapKlineFile
        self._max_files = max_files
        self._files: OrderedDict[str, MmapKlineFile] = OrderedDict()
        self._lock = threading.RLock()

        # 统计
        self._stats = {
            'opens': 0,
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }

        logger.info(f"[MmapKlineStore] 初始化完成，数据目录: {self.data_dir}, max_files={max_files}")

    def _make_key(self, symbol: str, period: str) -> str:
        """生成缓存键"""
        return f"{symbol}_{period}"

    def _get_filepath(self, symbol: str, period: str) -> Path:
        """获取文件路径"""
        # 文件名: 600519_SH_1d.mmap
        safe_symbol = symbol.replace('.', '_')
        return self.data_dir / f"{safe_symbol}_{period}.mmap"

    def _open_file(self, symbol: str, period: str) -> Optional[MmapKlineFile]:
        """打开文件（如果不存在返回 None），带 LRU 淘汰"""
        key = self._make_key(symbol, period)
        filepath = self._get_filepath(symbol, period)

        with self._lock:
            # 检查缓存并更新访问顺序
            if key in self._files:
                self._files.move_to_end(key)
                return self._files[key]

            # 打开新文件
            mmap_file = MmapKlineFile(filepath)
            if mmap_file.open():
                self._files[key] = mmap_file
                self._stats['opens'] += 1

                # LRU 淘汰：超过上限时关闭最早的文件
                while len(self._files) > self._max_files:
                    oldest_key, oldest_file = self._files.popitem(last=False)
                    oldest_file.close()
                    self._stats['evictions'] += 1
                    logger.debug(f"[MmapKlineStore] LRU 淘汰: {oldest_key}")

                return mmap_file
            else:
                return None

    def get(self, symbol: str, period: str, count: int = 500) -> Optional[pd.DataFrame]:
        """
        获取 K线数据（主要接口）

        Args:
            symbol: 股票代码
            period: 周期
            count: 返回条数（从最后向前数）

        Returns:
            DataFrame 或 None
        """
        mmap_file = self._open_file(symbol, period)

        if mmap_file is None:
            self._stats['misses'] += 1
            return None

        self._stats['hits'] += 1

        # 获取最后 count 条记录
        records = mmap_file.get_last_n(count)

        # 转换为 DataFrame
        data = [r.to_dict() for r in records]
        df = pd.DataFrame(data)
        if not df.empty and 'datetime' in df.columns:
            df = df.sort_values('datetime').reset_index(drop=True)
        return df

    def save(self, symbol: str, period: str, df: pd.DataFrame) -> bool:
        """
        保存 DataFrame 到 mmap 文件

        Args:
            symbol: 股票代码
            period: 周期
            df: K线数据 DataFrame

        Returns:
            是否成功
        """
        if df.empty:
            return False

        try:
            filepath = self._get_filepath(symbol, period)
            key = self._make_key(symbol, period)

            # 先关闭已打开的 mmap 文件（Windows 需要这样才能写入）
            with self._lock:
                if key in self._files:
                    self._files[key].close()
                    del self._files[key]

            # 转换为记录
            records = []
            for _, row in df.iterrows():
                # 处理 datetime 列
                dt = row['datetime']
                if isinstance(dt, str):
                    dt = pd.to_datetime(dt)
                elif isinstance(dt, pd.Timestamp):
                    dt = dt.to_pydatetime()

                timestamp = int(dt.timestamp())

                record = MmapKlineRecord(
                    timestamp=timestamp,
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=float(row['volume']),
                    amount=float(row.get('amount', 0))
                )
                records.append(record)

            # 创建文件
            mmap_file = MmapKlineFile(filepath)
            success = mmap_file.create(symbol, period, records)

            return success

        except Exception as e:
            logger.error(f"[MmapKlineStore] 保存失败: {symbol} {period}, {e}")
            return False

    def preload_symbols(self, symbols: List[str], periods: Optional[List[str]] = None) -> Dict:
        """
        预加载股票数据（实际是 mmap 打开文件，不读数据）

        Args:
            symbols: 股票代码列表
            periods: 周期列表

        Returns:
            统计信息
        """
        if periods is None:
            periods = self.DEFAULT_PERIODS

        logger.info(f"[MmapKlineStore] 开始预加载 {len(symbols)} 只股票 × {len(periods)} 个周期")

        opened = 0
        failed = 0

        for symbol in symbols:
            for period in periods:
                if self._open_file(symbol, period):
                    opened += 1
                else:
                    failed += 1

        result = {
            'total_symbols': len(symbols),
            'total_periods': len(periods),
            'opened': opened,
            'failed': failed,
            'cached_files': len(self._files)
        }

        logger.info(f"[MmapKlineStore] 预加载完成: 打开 {opened} 个文件, 失败 {failed} 个")
        return result

    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self._stats['hits'] + self._stats['misses']
        return {
            'cached_files': len(self._files),
            'max_files': self._max_files,
            'opens': self._stats['opens'],
            'evictions': self._stats.get('evictions', 0),
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': f"{self._stats['hits'] / total * 100:.1f}%" if total > 0 else "N/A"
        }

    def clear_cache(self):
        """关闭所有缓存的文件"""
        with self._lock:
            for mmap_file in self._files.values():
                mmap_file.close()
            self._files.clear()
            logger.info("[MmapKlineStore] 缓存已清空")

    def delete(self, symbol: str, period: str) -> bool:
        """删除指定股票的 mmap 文件

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            是否成功删除
        """
        try:
            key = self._make_key(symbol, period)
            filepath = self._get_filepath(symbol, period)

            with self._lock:
                # 如果文件已打开，先关闭
                if key in self._files:
                    self._files[key].close()
                    del self._files[key]

                # 删除文件
                if filepath.exists():
                    filepath.unlink()
                    logger.info(f"[MmapKlineStore] 已删除 {symbol} {period} 的 mmap 文件")
                    return True
                return False
        except Exception as e:
            logger.warning(f"[MmapKlineStore] 删除 {symbol} {period} 失败: {e}")
            return False


# 单例实例
_mmap_store_instance: Optional[MmapKlineStore] = None


def get_mmap_kline_store() -> MmapKlineStore:
    """获取 MmapKlineStore 单例"""
    global _mmap_store_instance
    if _mmap_store_instance is None:
        _mmap_store_instance = MmapKlineStore()
    return _mmap_store_instance
