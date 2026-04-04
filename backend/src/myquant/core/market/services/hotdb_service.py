# -*- coding: utf-8 -*-
"""
HotDB 数据管理服务

提供 HotDB 热数据库的智能更新、缺口检测和数据补全功能。

调用链（符合架构规范）：
    HotdbService
        → KlineService.get_historical_kline()  # 获取在线数据
        → hotdb_adapter.save_kline()            # 保存到 HotDB

不直接调用在线适配器，保持架构分层。
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger
import pandas as pd

from myquant.core.market.adapters import get_adapter
from myquant.core.market.utils.trading_time_detector import is_trading_time


class HotdbService:
    """HotDB 数据管理服务"""

    def __init__(self):
        self._hotdb_adapter = None
        self._kline_service = None

    def _get_hotdb_adapter(self):
        """延迟获取 HotDB 适配器"""
        if self._hotdb_adapter is None:
            self._hotdb_adapter = get_adapter('hotdb')
        return self._hotdb_adapter

    def get_adapter(self, name: str):
        """获取适配器实例（供外部调用）"""
        return get_adapter(name)

    def _get_kline_service(self):
        """延迟获取 KlineService（避免循环导入）"""
        if self._kline_service is None:
            from myquant.core.market.services.kline_service import get_kline_service
            self._kline_service = get_kline_service()
        return self._kline_service

    # ─────────────────────────────────────────────
    # 缺口检测
    # ─────────────────────────────────────────────

    def _detect_gap(self, symbol: str, period: str) -> Dict[str, Any]:
        """检测数据缺口

        Args:
            symbol: 股票代码 (如 600519.SH)
            period: 周期 (1d/1w/1mon/1m/5m/15m/30m/1h)

        Returns:
            {
                'has_gap': bool,
                'reason': str,  # 'no_data', 'intraday_gap', 'date_gap', 'stale'
                'latest': datetime,
                'expected_latest': datetime,
                'missing_count': int,
                'minutes_missing': int  # 仅分钟线
            }
        """
        hotdb = self._get_hotdb_adapter()
        if not hotdb or not hotdb.is_available():
            return {
                'has_gap': True,
                'reason': 'hotdb_unavailable',
                'latest': None,
                'expected_latest': None,
                'missing_count': 0,
                'minutes_missing': 0
            }

        try:
            # 获取最新数据时间
            latest_time = hotdb.get_latest_time(symbol, period)
            record_count = hotdb.get_record_count(symbol, period)

            now = datetime.now()

            # 无数据
            if latest_time is None or record_count == 0:
                return {
                    'has_gap': True,
                    'reason': 'no_data',
                    'latest': None,
                    'expected_latest': now,
                    'missing_count': 0,
                    'minutes_missing': 0
                }

            # 计算预期最新时间
            if period == '1d':
                # 日线：最新交易日收盘
                expected = self._get_latest_trading_day_close()
                is_stale = (expected - latest_time).days > 0
                return {
                    'has_gap': is_stale,
                    'reason': 'stale' if is_stale else 'ok',
                    'latest': latest_time,
                    'expected_latest': expected,
                    'missing_count': 0,
                    'minutes_missing': 0
                }
            else:
                # 分钟线：检查盘中缺口
                trading = is_trading_time()
                if not trading:
                    # 非交易时间，检查最后数据是否在收盘前
                    return {
                        'has_gap': False,
                        'reason': 'market_closed',
                        'latest': latest_time,
                        'expected_latest': latest_time,
                        'missing_count': 0,
                        'minutes_missing': 0
                    }

                # 交易时间，计算缺失分钟数
                minutes_missing = self._calc_minutes_missing(
                    latest_time, now, period
                )
                return {
                    'has_gap': minutes_missing > 5,  # >5分钟算缺口
                    'reason': 'intraday_gap' if minutes_missing > 5 else 'ok',
                    'latest': latest_time,
                    'expected_latest': now,
                    'missing_count': 0,
                    'minutes_missing': minutes_missing
                }

        except Exception as e:
            logger.error(f"[HotdbService] 检测缺口失败 {symbol} {period}: {e}")
            return {
                'has_gap': True,
                'reason': f'error: {e}',
                'latest': None,
                'expected_latest': None,
                'missing_count': 0,
                'minutes_missing': 0
            }

    def _get_latest_trading_day_close(self) -> datetime:
        """获取最近交易日收盘时间（简化版）"""
        now = datetime.now()
        # 简化：如果是交易日下午3点后，返回今天收盘
        # 否则返回昨天收盘
        if now.weekday() < 5:  # 工作日
            if now.hour >= 15:
                return now.replace(hour=15, minute=0, second=0, microsecond=0)
        # 回退到前一天
        yesterday = now - timedelta(days=1)
        while yesterday.weekday() >= 5:  # 跳过周末
            yesterday -= timedelta(days=1)
        return yesterday.replace(hour=15, minute=0, second=0, microsecond=0)

    def _calc_minutes_missing(
        self, latest: datetime, now: datetime, period: str
    ) -> int:
        """计算缺失的分钟数"""
        if latest is None:
            return 9999

        # 解析周期
        minutes_per_bar = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60, '60m': 60
        }
        interval = minutes_per_bar.get(period, 1)

        # 简化计算
        delta = (now - latest).total_seconds() / 60
        return max(0, int(delta / interval))

    # ─────────────────────────────────────────────
    # 智能更新
    # ─────────────────────────────────────────────

    def smart_update(self, symbol: str, period: str) -> Dict[str, Any]:
        """智能更新：检测缺口并自动补全

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            {
                'success': bool,
                'records': int,
                'source': str,
                'error': str
            }
        """
        # 1. 检测缺口
        gap_info = self._detect_gap(symbol, period)

        if not gap_info['has_gap']:
            return {
                'success': True,
                'records': 0,
                'source': 'hotdb',
                'error': None,
                'reason': 'no_gap'
            }

        # 2. 从 KlineService 获取数据（不直接调在线适配器）
        try:
            kline_service = self._get_kline_service()
            if kline_service is None:
                return {
                    'success': False,
                    'records': 0,
                    'source': None,
                    'error': 'KlineService unavailable'
                }

            # 获取数据
            df_dict = kline_service.get_historical_kline(
                symbols=[symbol],
                period=period,
                count=500  # 获取足够多的数据
            )

            if symbol not in df_dict or df_dict[symbol].empty:
                return {
                    'success': False,
                    'records': 0,
                    'source': None,
                    'error': 'No data from online source'
                }

            df = df_dict[symbol]

            # 3. 保存到 HotDB
            hotdb = self._get_hotdb_adapter()
            if hotdb is None:
                return {
                    'success': False,
                    'records': 0,
                    'source': 'online',
                    'error': 'HotDB adapter unavailable'
                }

            success = hotdb.save_kline(symbol, df, period)

            return {
                'success': success,
                'records': len(df) if success else 0,
                'source': 'online',
                'error': None if success else 'Save failed'
            }

        except Exception as e:
            logger.error(f"[HotdbService] smart_update 失败 {symbol} {period}: {e}")
            return {
                'success': False,
                'records': 0,
                'source': None,
                'error': str(e)
            }

    # ─────────────────────────────────────────────
    # 批量检查
    # ─────────────────────────────────────────────

    def auto_check_and_fill_today(
        self, symbols: List[str], periods: List[str] = None
    ) -> Dict[str, Any]:
        """自动检查并补全今天的数据

        Args:
            symbols: 股票代码列表
            periods: 周期列表，默认 ['1d', '1m']

        Returns:
            {
                'checked': int,
                'filled': int,
                'skipped': int,
                'failed': int,
                'details': dict
            }
        """
        if periods is None:
            periods = ['1d', '1m']

        checked = 0
        filled = 0
        skipped = 0
        failed = 0
        details = {}

        for symbol in symbols:
            details[symbol] = {}
            for period in periods:
                checked += 1

                # 检测缺口
                gap_info = self._detect_gap(symbol, period)

                if not gap_info['has_gap']:
                    skipped += 1
                    details[symbol][period] = {
                        'status': 'skipped',
                        'reason': gap_info['reason']
                    }
                    continue

                # 补全
                result = self.smart_update(symbol, period)

                if result['success']:
                    filled += 1
                    details[symbol][period] = {
                        'status': 'filled',
                        'records': result['records'],
                        'source': result['source']
                    }
                else:
                    failed += 1
                    details[symbol][period] = {
                        'status': 'failed',
                        'error': result['error']
                    }

        return {
            'checked': checked,
            'filled': filled,
            'skipped': skipped,
            'failed': failed,
            'details': details
        }


# ─────────────────────────────────────────────
# 单例工厂
# ─────────────────────────────────────────────

_hotdb_service_instance: Optional[HotdbService] = None


def get_hotdb_service() -> HotdbService:
    """获取 HotdbService 单例"""
    global _hotdb_service_instance
    if _hotdb_service_instance is None:
        _hotdb_service_instance = HotdbService()
    return _hotdb_service_instance
