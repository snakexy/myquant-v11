"""
无缝 K线服务

提供历史 K线 + 实时 K线的无缝拼接

统一复权架构:
- 所有数据源返回不复权原始数据
- 服务层统一应用 AdjustmentFactorService 进行复权
"""

from typing import Optional
import pandas as pd
from datetime import datetime
from pathlib import Path
from loguru import logger

from myquant.core.market.models import KlineDataset
from myquant.core.market.adapters import get_adapter
from myquant.core.market.utils.trading_time import TradingTimeChecker
from myquant.core.market.services.kline_service import get_kline_service
from myquant.core.market.services.hotdb_service import get_hotdb_service
from myquant.core.market.services.cache import TTLCache
from myquant.config.settings import XDXR_DIR
from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service


# 自动保存配置


import pickle
import os
import time

# 目录创建标记（类级别，只检查一次）
_xdxr_dir_initialized = False

def _ensure_xdxr_dir():
    """确保XDXR目录存在（只执行一次）"""
    global _xdxr_dir_initialized
    if not _xdxr_dir_initialized:
        XDXR_DIR.mkdir(parents=True, exist_ok=True)
        _xdxr_dir_initialized = True


class SeamlessKlineService:
    """无缝 K线服务

    合并历史数据和实时数据，提供连续的 K线序列
    带复权结果缓存（L1内存缓存）
    """

    def __init__(self):
        self._adapter_cache = {}
        # XDXR除权除息数据缓存（TTL 1小时，因为这数据变化不频繁）
        self._xdxr_cache = TTLCache(maxsize=200, ttl=3600)  # 1小时TTL
        # XDXR文件缓存TTL（秒）：1天
        self._xdxr_file_ttl = 24 * 3600
        # K线数据缓存（TTL 60秒，加速周期切换）
        self._kline_cache = TTLCache(maxsize=500, ttl=60)
        # 复权因子服务（预计算复权因子表，支持混合模式）
        self._factor_service = get_adjustment_factor_service()
        logger.info("[SeamlessKlineService] 初始化完成，混合模式复权已启用，K线缓存已开启")


    def get_kline(
        self,
        symbol: str,
        period: str = '1d',
        count: int = 500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_realtime: bool = True,
        adjust_type: str = 'none'
    ) -> pd.DataFrame:
        """获取无缝 K线数据

        Args:
            symbol: 代码
            period: 周期 (1m/5m/15m/30m/1h/1d/1w/1M)
            count: 数据条数
            start_date: 开始日期
            end_date: 结束日期
            include_realtime: 是否包含实时数据
            adjust_type: 复权类型 (none/front/back)

        Returns:
            DataFrame with OHLCV columns
        """
        # ── 增量缓存策略────────────────────────────────────
        CACHE_SIZE = 5000
        cache_key = f"kline:{symbol}:{period}:{adjust_type}"

        # 检查缓存（仅对分钟线和日线有效）
        use_cache = period in ['1m', '5m', '15m', '30m', '1h', '1d']
        cached_data = None
        cached_last_time = None
        incremental_fetch = False

        if use_cache:
            cached_entry = self._kline_cache.get(cache_key)
            if cached_entry is not None:
                # 缓存条目格式: {'df': DataFrame, 'last_time': timestamp}
                if isinstance(cached_entry, dict):
                    cached_data = cached_entry.get('df')
                    cached_last_time = cached_entry.get('last_time')
                else:
                    # 兼容旧格式（直接是DataFrame）
                    cached_data = cached_entry
                    if not cached_data.empty:
                        cached_last_time = cached_data.iloc[-1]['datetime']

                if cached_data is not None and not cached_data.empty:
                    logger.debug(f"[K线缓存] 命中: {symbol} {period} {adjust_type}, "
                               f"缓存{len(cached_data)}条, 最后时间={cached_last_time}")

                    # 检查缓存数据量是否足够
                    if len(cached_data) < count:
                        logger.info(f"[K线缓存] 缓存数据不足（{len(cached_data)} < {count}），清除缓存重新获取")
                        self._kline_cache.delete(cache_key)
                        cached_data = None
                        cached_last_time = None
                    # 先检查数据新鲜度和缺口（即使启用增量获取）
                    elif use_cache:
                        hotdb_service = get_hotdb_service()
                        gap_info = hotdb_service._detect_gap(symbol, period)

                        if gap_info['has_gap']:
                            # 数据有缺口，触发智能更新并禁用增量获取
                            logger.info(f"[K线缓存] {symbol} {period} 检测到数据缺口: {gap_info['reason']}，触发智能更新")
                            update_result = hotdb_service.smart_update(symbol, period)

                            if update_result['success'] and update_result['records'] > 0:
                                # 更新成功，清除缓存以重新获取完整数据
                                logger.info(f"[K线缓存] 智能更新完成，清除缓存重新获取")
                                self._kline_cache.delete(cache_key)
                                cached_data = None
                                cached_last_time = None
                                incremental_fetch = False
                            else:
                                # 更新失败，记录日志但仍返回缓存（降级处理）
                                logger.warning(f"[K线缓存] 智能更新失败: {update_result.get('error')}，返回缓存数据")
                                return cached_data.copy()
                        else:
                            # 数据新鲜，启用增量获取
                            incremental_fetch = True
                    else:
                        # 不使用缓存，启用增量获取
                        incremental_fetch = True

        # 增量获取逻辑
        fetch_count = count
        start_date_for_fetch = start_date

        if incremental_fetch and cached_last_time is not None:
            # 只获取从最后时间戳之后的新数据
            # 多获取几条以确保覆盖（去重时会处理）
            fetch_count = count + 10 if count < 100 else count
            start_date_for_fetch = cached_last_time
            logger.info(f"[增量获取] {symbol} {period}: 从 {cached_last_time} 开始获取新数据")
        elif cached_data is not None and not cached_data.empty:
            # 缓存存在且没有缺口，直接返回缓存
            logger.debug(f"[K线缓存] 数据新鲜，直接返回缓存数据")
            return cached_data.copy()

        # 获取历史数据（始终获取不复权原始数据）
        historical = self._get_historical_kline(
            symbol, period, fetch_count,
            start_date_for_fetch, end_date, 'none'
        )

        if historical.df.empty:
            # 如果没有获取到新数据且缓存存在，返回缓存
            if cached_data is not None and not cached_data.empty:
                logger.debug(f"[增量获取] 无新数据，返回缓存")
                return cached_data.copy()
            return historical.df

        # 判断是否需要补充实时数据
        if include_realtime and self._need_realtime_supplement(historical, period):
            # 获取从最后一条数据日期到今天的数据（可能覆盖同一天的数据）
            last_date = historical.df.iloc[-1]['datetime']
            start_date_formatted = last_date.strftime('%Y%m%d')  # 使用YYYYMMDD格式，与DataMerger保持一致

            logger.info(f"[数据补全] 准备获取补充数据，start_date={start_date_formatted}")

            # 实时数据也是不复权原始数据
            realtime = self._get_realtime_kline(
                symbol, period, 'none',
                start_date=start_date_formatted,
                end_date=datetime.now().strftime('%Y%m%d'),  # 添加end_date，确保适配器使用正确的日期范围
                filter_today=False, get_realtime=True
            )

            logger.info(f"[数据补全] 获取到实时数据: {len(realtime.df)} 条")
            if not realtime.df.empty:
                logger.info(f"[数据补全] 实时数据日期范围: {realtime.df['datetime'].min()} 到 {realtime.df['datetime'].max()}")
                # 合并历史和实时数据
                historical = historical.merge(realtime)
                logger.info(f"[数据补全] 合并后总计: {len(historical.df)} 条，最新日期: {historical.df['datetime'].max()}")
            else:
                logger.warning(f"[数据补全] 未获取到补充数据 (从 {start_date_formatted})")
        else:
            logger.info("[数据补全] 不需要补充数据")

        # 应用日期范围过滤
        if start_date or end_date:
            historical = historical.slice_by_date(start_date, end_date)

        # 增量合并：合并缓存数据和新获取的数据
        if incremental_fetch and cached_data is not None and not cached_data.empty:
            if not historical.df.empty:
                # 关键修复：统一 datetime 格式（移除时区信息，避免去重失败）
                # 缓存数据和新数据的 datetime 格式可能不一致（带时区 vs 不带时区）
                def normalize_datetime(dt):
                    """移除时区信息，统一为 naive datetime"""
                    if pd.isna(dt):
                        return dt
                    if hasattr(dt, 'tz') and dt.tz is not None:
                        return dt.tz_localize(None)
                    return dt

                cached_copy = cached_data.copy()
                historical_copy = historical.df.copy()

                cached_copy['datetime'] = cached_copy['datetime'].apply(normalize_datetime)
                historical_copy['datetime'] = historical_copy['datetime'].apply(normalize_datetime)

                # 合并新旧数据并去重
                merged_df = pd.concat([cached_copy, historical_copy], ignore_index=True)

                # 按datetime去重，保留最后出现的（新数据覆盖旧数据）
                merged_df = merged_df.drop_duplicates(subset=['datetime'], keep='last')

                # 按时间排序
                merged_df = merged_df.sort_values('datetime').reset_index(drop=True)

                new_data_count = len(historical.df)
                unique_new_count = len(merged_df) - len(cached_data)

                logger.info(f"[增量合并] {symbol} {period}: 新获取{new_data_count}条, "
                           f"实际新增{unique_new_count}条, 合并后总计{len(merged_df)}条")

                historical.df = merged_df
            else:
                # 没有获取到新数据，使用缓存
                logger.debug(f"[增量合并] 无新数据，使用缓存")
                historical.df = cached_data

        # 复权功能已禁用（短期策略不需要，需要时可恢复）
        # 原代码保留供参考：
        # if adjust_type != 'none' and not historical.df.empty:
        #     historical.df = self._apply_adjustment(
        #         historical.df, symbol, adjust_type, period
        #     )

        # 写入缓存（缓存原始数据，包含时间戳）
        if use_cache and not historical.df.empty:
            cache_df = historical.df.tail(CACHE_SIZE).copy() if len(historical.df) > CACHE_SIZE else historical.df.copy()
            last_time = cache_df.iloc[-1]['datetime']

            # 新缓存格式：包含DataFrame和最后时间戳
            cache_entry = {
                'df': cache_df,
                'last_time': last_time
            }

            ttl = 60 if period in ['1m', '5m', '15m', '30m', '1h'] else 300
            self._kline_cache.set(cache_key, cache_entry, ttl=ttl)
            logger.debug(f"[K线缓存] 已缓存: {symbol} {period} {adjust_type}, {len(cache_df)}条")

        # 日线特殊处理：标准化时间并过滤周末
        # 日线特殊处理：标准化时间并过滤周末
        if period == '1d' and not historical.df.empty:
            def normalize_daily_time(dt):
                if pd.isna(dt):
                    return dt
                if isinstance(dt, str):
                    dt = pd.to_datetime(dt)
                return dt.replace(hour=15, minute=0, second=0, microsecond=0)
            historical.df['datetime'] = historical.df['datetime'].apply(normalize_daily_time)
            # 过滤周末
            historical.df = historical.df[historical.df['datetime'].dt.weekday < 5].copy()

        # 全周期通用去重：同一时间戳可能来自多个数据源，保留最后一条（在线数据）
        if not historical.df.empty:
            before_dedup = len(historical.df)
            historical.df = historical.df.drop_duplicates(subset=['datetime'], keep='last')
            after_dedup = len(historical.df)
            if before_dedup != after_dedup:
                logger.info(f"[去重] 移除 {before_dedup - after_dedup} 条重复数据（优先保留在线数据）")

        # 应用数量限制（必须在周末过滤和去重之后，确保返回的是最新的交易日数据）
        if count:
            # 返回用户请求的数量
            return_count = count
            before_count = len(historical.df)
            historical = historical.filter_by_count(return_count, from_end=True)
            after_count = len(historical.df)
            logger.info(f"[数量限制] {symbol} {period}: 请求={count}, return_count={return_count}, 限制前={before_count}, 限制后={after_count}")
        else:
            logger.info(f"[数量限制] {symbol} {period}: count为None或0，跳过数量限制，返回全部{len(historical.df)}条")

        # 标记正在形成的K线
        historical.df = self._mark_forming_kline(historical.df, period)

        # 注意：数据回写由 KlineService 负责，SeamlessKlineService 只负责无缝拼接逻辑
        # KlineService.get_historical_kline() 已确保从在线源获取的数据回写到 HotDB

        return historical.df

    def _apply_adjustment(
        self,
        df: pd.DataFrame,
        symbol: str,
        adjust_type: str,
        period: str = '1d'
    ) -> pd.DataFrame:
        """应用复权

        使用前复权(front)：累积因子，最新价不变

        Args:
            df: K线数据
            symbol: 股票代码
            adjust_type: 复权类型 (none/front/back)
            period: 周期

        Returns:
            复权后的 DataFrame
        """
        if df.empty or adjust_type == 'none':
            return df

        try:
            # 所有周期统一使用前复权
            actual_adjust_type = 'front'

            # 如果用户明确请求了其他复权类型，尊重用户选择
            if adjust_type in ['back', 'back_ratio']:
                actual_adjust_type = adjust_type

            logger.info(f"[复权] {symbol} {period}: 用户请求{adjust_type}, 实际使用{actual_adjust_type}")

            # 使用因子服务获取预计算的因子表并应用
            factor_table = self._factor_service.get_factor_table(symbol, actual_adjust_type)
            if factor_table:
                # DEBUG: 打印今天的因子
                from datetime import datetime
                today = datetime.now().strftime('%Y-%m-%d')
                today_factor = factor_table.get(today, 'N/A')
                logger.info(f"[复权DEBUG] 今天({today})的{actual_adjust_type}因子: {today_factor}")

                result = self._factor_service.apply_factors(df, factor_table)
                logger.info(f"[复权] {symbol} {period} 应用 {actual_adjust_type} 复权完成，"
                           f"共{len(factor_table)}个因子")
                return result
            else:
                logger.debug(f"[复权] {symbol} 无复权因子，返回原始数据")
                return df

        except Exception as e:
            logger.warning(f"[复权] {symbol} {period} 复权应用失败: {e}")
            return df

    def _get_xdxr_data(self, symbol: str) -> list:
        """获取除权除息数据（带内存缓存+文件持久化缓存）

        优先级: 内存缓存 → 文件缓存 → TdxQuant → PyTdx
        - 内存缓存: TTL 1小时（高频访问）
        - 文件缓存: TTL 1天（持久化，按股票分文件夹）
        - TdxQuant: 覆盖范围更广（支持板块和指数），仅交易时间可用
        - PyTdx: 作为备用，24/7可用

        Args:
            symbol: 股票代码

        Returns:
            除权除息记录列表
        """
        # 委托给 XdxrService（统一管理，避免直接访问适配器）
        try:
            from myquant.core.market.services.xdxr_service import get_xdxr_service
            xdxr_service = get_xdxr_service()
            return xdxr_service.get_xdxr_data(symbol)
        except Exception as e:
            logger.warning(f"[SeamlessService] 获取XDXR数据失败: {e}")
            return []

    def _get_xdxr_file_path(self, symbol: str, use_binary: bool = True) -> Path:
        """获取XDXR数据文件路径

        Args:
            symbol: 股票代码
            use_binary: 是否使用二进制格式（.pkl 比 .json 快 5-10 倍）

        Returns:
            Path对象
        """
        # 确保目录已创建（只执行一次）
        _ensure_xdxr_dir()

        # 清理股票代码中的特殊字符
        safe_symbol = symbol.replace('.', '_').replace('/', '_')
        symbol_dir = XDXR_DIR / safe_symbol

        # 只在目录不存在时创建（减少磁盘IO）
        if not symbol_dir.exists():
            symbol_dir.mkdir(parents=True, exist_ok=True)

        ext = 'pkl' if use_binary else 'json'
        return symbol_dir / f"{safe_symbol}.{ext}"

    def _load_xdxr_from_file(self, symbol: str) -> Optional[list]:
        """从文件加载XDXR数据（高性能版本）

        优化点：
        1. 使用 pickle 二进制格式（比 JSON 快 5-10 倍）
        2. 减少磁盘 IO 检查次数
        3. 优先读取 .pkl，如果不存在则回退到 .json

        Args:
            symbol: 股票代码

        Returns:
            XDXR数据列表，或None（如果文件不存在或过期）
        """
        try:
            # 优先尝试二进制格式（更快）
            file_path = self._get_xdxr_file_path(symbol, use_binary=True)

            # 检查文件是否存在且未过期
            if not file_path.exists():
                # 回退到 JSON 格式（兼容旧数据）
                file_path = self._get_xdxr_file_path(symbol, use_binary=False)
                if not file_path.exists():
                    return None

            # 检查文件修改时间（使用缓存的 stat 结果）
            stat = file_path.stat()
            age = time.time() - stat.st_mtime
            if age > self._xdxr_file_ttl:
                logger.debug(f"[XDXR文件缓存] {symbol} 已过期 ({age/3600:.1f}小时)")
                return None

            # 根据扩展名选择读取方式
            if file_path.suffix == '.pkl':
                # 二进制格式：快 5-10 倍
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
            else:
                # JSON 格式：兼容旧数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

            # 验证数据格式
            if isinstance(data, list):
                logger.debug(f"[XDXR文件缓存] {symbol} 加载成功: {len(data)}条 ({file_path.suffix})")
                return data
            else:
                logger.warning(f"[XDXR文件缓存] {symbol} 数据格式错误")
                return None

        except Exception as e:
            logger.debug(f"[XDXR文件缓存] {symbol} 加载失败: {e}")
            return None

    def _save_xdxr_to_file(self, symbol: str, data: list, use_binary: bool = True) -> bool:
        """保存XDXR数据到文件（高性能版本）

        Args:
            symbol: 股票代码
            data: XDXR数据列表
            use_binary: 是否使用二进制格式（默认True）

        Returns:
            是否保存成功
        """
        try:
            file_path = self._get_xdxr_file_path(symbol, use_binary=use_binary)

            if use_binary:
                # 二进制格式：更快且更小
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                # JSON 格式：便于调试
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)

            logger.debug(f"[XDXR文件缓存] {symbol} 已保存: {len(data)}条 -> {file_path}")
            return True

        except Exception as e:
            logger.warning(f"[XDXR文件缓存] {symbol} 保存失败: {e}")
            return False

    def _get_historical_kline(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str],
        end_date: Optional[str],
        adjust_type: str
    ) -> KlineDataset:
        """获取历史 K线数据（调用 KlineService 统一入口）

        按架构设计：不再直接调用适配器，统一通过 KlineService 获取数据
        KlineService 负责三层路由：HotDB → LocalDB → 在线源（V5双层路由）
        """
        kline_service = get_kline_service()
        df = kline_service.get_historical_kline(
            symbol=symbol,
            period=period,
            count=count,
            start_date=start_date,
            end_date=end_date
        )

        if df.empty:
            return KlineDataset.empty()

        # 从 source 列获取数据源名称
        source = df['source'].iloc[0] if 'source' in df.columns else 'kline_service'
        return KlineDataset.from_adapter(df, source)

    def _get_realtime_kline(
        self,
        symbol: str,
        period: str,
        adjust_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filter_today: bool = True,
        get_realtime: bool = True
    ) -> KlineDataset:
        """获取补充的 K线数据（调用 KlineService 统一入口）

        Args:
            symbol: 股票代码
            period: 周期
            adjust_type: 复权类型
            start_date: 开始日期 (YYYYMMDD)，默认为今天
            end_date: 结束日期 (YYYYMMDD)，默认为今天
            filter_today: 是否只过滤今天的数据
            get_realtime: 是否获取实时数据
        """
        kline_service = get_kline_service()
        df = kline_service.get_historical_kline(
            symbol=symbol,
            period=period,
            count=500,  # 补充数据用较大数量
            start_date=start_date,
            end_date=end_date
        )

        if df.empty:
            return KlineDataset.empty()

        source = df['source'].iloc[0] if 'source' in df.columns else 'kline_service'
        return KlineDataset.from_adapter(df, source)

    def _need_realtime_supplement(self, historical: KlineDataset, period: str) -> bool:
        """判断是否需要补充实时数据

        修复：考虑交易时间，避免开盘前误判需要补数据
        """
        if historical.df.empty:
            return False

        last_time = historical.df.iloc[-1]['datetime']
        now = datetime.now()
        today = now.date()
        last_date = last_time.date()

        # 判断最后数据日期 vs 今天
        logger.info(f"[数据补全检查] 最后数据日期: {last_date}, 今天: {today}, 当前时间: {now.strftime('%H:%M')}")

        if last_date < today:
            # 最后数据是昨天或更早
            # 关键修复：如果现在还在当天开盘前（< 09:30），今天本来就没有数据
            current_time = now.time()
            market_open = datetime.strptime("09:30", "%H:%M").time()

            if current_time < market_open:
                # 开盘前：昨天的数据是完整的，不需要补"今天"的数据
                logger.info(f"[数据补全] 当前时间 {current_time.strftime('%H:%M')} 早于开盘时间 09:30，昨天的数据已完整，不需要补充")
                return False
            else:
                # 开盘后：如果最后数据还是昨天，需要补充
                logger.info(f"[数据补全] 需要补充: 最后数据({last_date}) 早于今天({today}) 且已过开盘时间")
                return True
        elif last_date == today:
            # 最后数据是今天，检查是否需要更新（分钟级数据）
            if period in ['1m', '5m', '15m', '30m', '1h']:
                time_diff = (now - last_time).total_seconds()

                # 如果超过2个周期，认为需要补充
                period_minutes = {'1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60}.get(period, 5)
                if time_diff > period_minutes * 2 * 60:
                    logger.info(f"[数据补全] 今天数据需要更新: 最后数据时间 {last_time}, 距离现在 {time_diff/60:.1f} 分钟")
                    return True

        return False



    def _mark_forming_kline(self, df: pd.DataFrame, period: str) -> pd.DataFrame:
        """标记正在形成的K线

        Args:
            df: K线数据 DataFrame
            period: 周期 (1m/5m/15m/30m/1h/1d)

        Returns:
            添加了 is_complete 列的 DataFrame
        """
        if df.empty:
            return df

        # 创建 is_complete 列，默认为 True
        df = df.copy()
        df['is_complete'] = True

        # 判断最后一根K线是否正在形成
        now = datetime.now()
        last_time = df.iloc[-1]['datetime']

        # 处理 datetime 类型
        if isinstance(last_time, str):
            last_time = pd.to_datetime(last_time)
        elif not isinstance(last_time, pd.Timestamp):
            last_time = pd.Timestamp(last_time)

        is_forming = False

        # 分钟线判断
        if period in ['1m', '5m', '15m', '30m', '1h']:
            period_minutes = {'1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60}
            mins = period_minutes.get(period, 5)

            # 计算当前周期开始时间
            current_period_start = now.replace(
                minute=now.minute // mins * mins,
                second=0,
                microsecond=0
            )

            # 如果最后一根K线的时间 >= 当前周期开始时间，说明正在形成
            is_forming = last_time >= current_period_start

        # 日线判断
        elif period == '1d':
            # 日线：检查是否是今天且在交易时间内
            is_trading = TradingTimeChecker.is_trading_time()
            is_today = last_time.date() == now.date()

            # 交易时间内当天的K线正在形成
            is_forming = is_today and is_trading

        # 标记最后一根K线
        if is_forming:
            df.iloc[-1, df.columns.get_loc('is_complete')] = False
            logger.debug(f"[K线标记] 最后一根K线正在形成: {last_time}")

        return df

    def clear_cache(self) -> None:
        """清空适配器缓存"""
        self._adapter_cache.clear()


# 单例实例
_seamless_kline_service: Optional[SeamlessKlineService] = None


def get_seamless_kline_service() -> SeamlessKlineService:
    """获取 SeamlessKlineService 单例实例"""
    global _seamless_kline_service
    if _seamless_kline_service is None:
        _seamless_kline_service = SeamlessKlineService()
    return _seamless_kline_service
