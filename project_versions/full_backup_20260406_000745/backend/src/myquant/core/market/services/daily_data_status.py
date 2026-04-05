"""
每日数据状态管理服务（V2.0 - 哈希校验版本）

职责：
- 管理数据指纹（自动检测数据变化）
- 避免重复检测，提高效率
- 自动清理过期记录（7天）
"""

import json
import hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class DataFingerprint:
    """数据指纹类"""

    def __init__(self, count: int, latest_dt: str, hash_value: str):
        self.count = count
        self.latest_dt = latest_dt
        self.hash = hash_value

    def to_dict(self) -> dict:
        return {
            'count': self.count,
            'latest_dt': self.latest_dt,
            'hash': self.hash
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DataFingerprint':
        return cls(
            count=data.get('count', 0),
            latest_dt=data.get('latest_dt', ''),
            hash_value=data.get('hash', '')
        )


class DailyDataStatusService:
    """每日数据状态管理服务（V2.0）"""

    def __init__(self, status_file: str = None):
        if status_file is None:
            status_file = "E:/MyQuant_v11/data/cache/daily_data_status.json"
        self._status_file = Path(status_file)
        self._status_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()  # 线程锁，保护文件操作
        self._data = self._load()

    def _load(self) -> dict:
        """加载状态文件"""
        with self._lock:  # 加锁保护读取
            if self._status_file.exists():
                try:
                    with open(self._status_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 兼容旧版本
                        if 'fingerprints' not in data:
                            data['fingerprints'] = {}
                        return data
                except Exception as e:
                    logger.warning(f"[DailyDataStatus] 加载状态文件失败: {e}")
            return {"version": "2.0", "updated_at": None, "data": {}, "fingerprints": {}}

    def _save(self) -> None:
        """保存状态文件（线程安全）"""
        with self._lock:  # 加锁保护写入
            self._data["updated_at"] = datetime.now().isoformat()
            with open(self._status_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

    def is_checked_today(self, symbol: str, date_str: str = None) -> bool:
        """检查某股票某日期是否已检查过"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')

        return (
            symbol in self._data["data"] and
            date_str in self._data["data"][symbol]
        )

    def mark_checked(self, symbol: str, date_str: str = None,
                     periods: Dict[str, any] = None) -> None:
        """标记某股票某日期已检查（线程安全）

        Args:
            symbol: 股票代码
            date_str: 日期字符串（YYYYMMDD），默认今天
            periods: 各周期状态字典，如 {"1d": {"had_gap": False, "filled": False}}
        """
        with self._lock:  # 加锁保护整个操作
            if date_str is None:
                date_str = datetime.now().strftime('%Y%m%d')

            if symbol not in self._data["data"]:
                self._data["data"][symbol] = {}

            self._data["data"][symbol][date_str] = {
                "checked_at": datetime.now().isoformat(),
                "periods": periods or {},
                "status": "completed"
            }

            self._data["updated_at"] = datetime.now().isoformat()
            with open(self._status_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

    def mark_checked_range(self, symbol: str, start_date: str, end_date: str,
                          periods: Dict[str, any] = None) -> None:
        """标记某股票日期范围已检查

        用于记录补全数据时涉及的日期范围，确保第二天不会重复检查。

        Args:
            symbol: 股票代码
            start_date: 开始日期字符串（YYYYMMDD）
            end_date: 结束日期字符串（YYYYMMDD）
            periods: 各周期状态字典
        """
        from datetime import timedelta

        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')

        current = start
        while current <= end:
            date_str = current.strftime('%Y%m%d')
            self.mark_checked(symbol, date_str, periods)
            current += timedelta(days=1)

        logger.info(f"[DailyDataStatus] 记录 {symbol} 检查范围: {start_date} ~ {end_date}")

    def clean_old_records(self, days: int = 7) -> None:
        """清理旧记录（只保留最近 N 天）（线程安全）"""
        with self._lock:  # 加锁保护整个操作
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            for symbol in list(self._data["data"].keys()):
                dates_to_remove = [
                    date_str for date_str in self._data["data"][symbol]
                    if date_str < cutoff_date
                ]
                for date_str in dates_to_remove:
                    del self._data["data"][symbol][date_str]

                # 删除无记录的股票
                if not self._data["data"][symbol]:
                    del self._data["data"][symbol]

            self._data["updated_at"] = datetime.now().isoformat()
            with open(self._status_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

            logger.info(f"[DailyDataStatus] 清理了 {days} 天前的旧记录")

    def get_status(self, symbol: str = None) -> dict:
        """获取状态

        Args:
            symbol: 股票代码，如果指定则返回该股票的状态，否则返回全部

        Returns:
            状态字典
        """
        if symbol:
            return self._data["data"].get(symbol, {})
        return self._data

    # ==================== 指纹管理方法 ====================

    def get_fingerprint(self, symbol: str, period: str) -> Optional[DataFingerprint]:
        """获取数据指纹（线程安全）

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            DataFingerprint 对象，如果不存在返回 None
        """
        with self._lock:  # 加锁保护读取
            key = f"{symbol}_{period}"
            fp_data = self._data["fingerprints"].get(key)
            if fp_data:
                return DataFingerprint.from_dict(fp_data)
            return None

    def save_fingerprint(self, symbol: str, period: str,
                        count: int, latest_dt: str, hash_value: str) -> None:
        """保存数据指纹（线程安全）

        Args:
            symbol: 股票代码
            period: 周期
            count: 数据条数
            latest_dt: 最新时间
            hash_value: 哈希值
        """
        with self._lock:  # 加锁保护整个操作
            key = f"{symbol}_{period}"
            fingerprint = DataFingerprint(count, latest_dt, hash_value)

            self._data["fingerprints"][key] = fingerprint.to_dict()

            self._data["updated_at"] = datetime.now().isoformat()
            with open(self._status_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

            logger.debug(f"[DailyDataStatus] 更新指纹: {key}, count={count}, latest={latest_dt}")

    def is_fingerprint_valid(self, symbol: str, period: str,
                            current_count: int, current_latest_dt: str,
                            current_hash: str) -> bool:
        """验证指纹是否有效

        Args:
            symbol: 股票代码
            period: 周期
            current_count: 当前数据条数
            current_latest_dt: 当前最新时间
            current_hash: 当前哈希值

        Returns:
            True 如果指纹有效（数据未变化），False 否则
        """
        saved_fp = self.get_fingerprint(symbol, period)
        if not saved_fp:
            return False  # 无指纹记录

        # 对比哈希值
        hash_match = (saved_fp.hash == current_hash)

        # 对比最新时间（允许1分钟误差）
        try:
            saved_dt = datetime.fromisoformat(saved_fp.latest_dt)
            current_dt = datetime.fromisoformat(current_latest_dt)
            time_diff = abs((current_dt - saved_dt).total_seconds())
            time_match = time_diff <= 60  # 1分钟内
        except:
            time_match = False

        is_valid = hash_match and time_match

        if not is_valid:
            logger.debug(
                f"[DailyDataStatus] {symbol} {period} 指纹失效: "
                f"hash_match={hash_match}, time_match={time_match}"
            )

        return is_valid


# 单例
_daily_status_service: Optional[DailyDataStatusService] = None


def get_daily_status_service() -> DailyDataStatusService:
    """获取状态管理服务单例"""
    global _daily_status_service
    if _daily_status_service is None:
        _daily_status_service = DailyDataStatusService()
    return _daily_status_service
