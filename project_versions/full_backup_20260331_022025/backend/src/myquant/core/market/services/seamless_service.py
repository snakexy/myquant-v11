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
import json
from loguru import logger

from myquant.core.market.models import KlineDataset
from myquant.core.market.utils.trading_time import TradingTimeChecker
from myquant.config.settings import XDXR_DIR
from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service
from myquant.core.market.services.kline_service import get_kline_service
from myquant.core.market.services.cache_manager_service import get_cache_manager, CachePartition


# 自动保存配置
AUTO_SAVE_TO_LOCALDB = True  # 开关
SAVE_PERIODS = {'1d'}  # 只保存日线数据
SAVE_ONLINE_SOURCES = {'xtquant', 'pytdx', 'tdxquant'}  # 只保存从在线源获取的数据


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
        # ✅ 依赖 KlineService（统一数据获取入口）
        self._kline_service = get_kline_service()
        self._factor_service = get_adjustment_factor_service()
        # ✅ 使用统一缓存管理服务
        self._cache_manager = get_cache_manager()
        # XDXR文件缓存TTL（秒）：1天
        self._xdxr_file_ttl = 24 * 3600
        logger.info("[SeamlessKlineService] 初始化完成，使用 CacheManagerService 统一缓存")

    def _ensure_naive_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """确保 DataFrame 中的 datetime 列为 timezone-naive

        将所有 timezone-aware 的 datetime 转换为 timezone-naive（北京时间），
        避免 concat/merge 时出现 object 类型或 timezone 混乱问题。

        Args:
            df: 输入 DataFrame

        Returns:
            datetime 列为 timezone-naive 的 DataFrame
        """
        if df.empty or 'datetime' not in df.columns:
            return df

        def make_naive(dt):
            """将 datetime 转换为 naive（保留本地时间，移除时区信息）"""
            if pd.isna(dt):
                return dt
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                # 保留本地时间，移除时区信息
                return dt.tz_localize(None)
            return dt

        df = df.copy()
        df['datetime'] = df['datetime'].apply(make_naive)
        return df

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
            cached_entry = self._cache_manager.get(CachePartition.MERGED_KLINE, cache_key)
            if cached_entry is not None:
                # 新缓存条目格式: {'data': dict_list, 'last_time': timestamp}
                if isinstance(cached_entry, dict) and 'data' in cached_entry:
                    # 新格式：转换为DataFrame
                    cached_data_list = cached_entry.get('data')
                    cached_last_time = cached_entry.get('last_time')
                    if cached_data_list:
                        cached_data = pd.DataFrame(cached_data_list)
                    else:
                        cached_data = None
                elif isinstance(cached_entry, dict) and 'df' in cached_entry:
                    # 旧格式兼容：{'df': DataFrame, 'last_time': timestamp}
                    cached_data = cached_entry.get('df')
                    cached_last_time = cached_entry.get('last_time')
                else:
                    # 更旧的格式：直接是DataFrame
                    cached_data = cached_entry
                    if not cached_data.empty:
                        cached_last_time = cached_data.iloc[-1]['datetime']

                if cached_data is not None and not cached_data.empty:
                    logger.debug(f"[K线缓存] 命中: {symbol} {period} {adjust_type}, "
                               f"缓存{len(cached_data)}条, 最后时间={cached_last_time}")

                    # 启用增量获取
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
        elif use_cache and cached_data is not None and not cached_data.empty:
            # 缓存存在但不需要增量（时间戳为空或请求指定了start_date）
            logger.debug(f"[K线缓存] 直接返回缓存数据")
            return self._ensure_naive_datetime(cached_data.copy())

        # 获取历史数据（始终获取不复权原始数据）
        historical = self._get_historical_kline(
            symbol, period, fetch_count,
            start_date_for_fetch, end_date, 'none'
        )

        # 确保历史数据 datetime 为 naive（避免 timezone 混乱）
        historical.df = self._ensure_naive_datetime(historical.df)

        if historical.df.empty:
            # 如果没有获取到新数据且缓存存在，返回缓存
            if cached_data is not None and not cached_data.empty:
                logger.debug(f"[增量获取] 无新数据，返回缓存")
                return self._ensure_naive_datetime(cached_data.copy())
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

            # 确保实时数据 datetime 为 naive
            realtime.df = self._ensure_naive_datetime(realtime.df)

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

        # ── 数据完整性检查与自动补全 ─────────────────────
        # 检查是否有数据缺口（仅日线检查）
        if period == '1d':
            missing_dates = self._detect_data_gaps(historical.df, period, days_back=30)
            if missing_dates:
                logger.info(f"[自动补全] 发现 {len(missing_dates)} 个缺口，触发自动补全")
                # 可以在这里添加自动补全逻辑，但为了避免阻塞请求，暂时只记录
                # 实际补全可以在后台任务中进行
                pass

        # 应用日期范围过滤
        if start_date or end_date:
            historical = historical.slice_by_date(start_date, end_date)

        # 增量合并：合并缓存数据和新获取的数据
        if incremental_fetch and cached_data is not None and not cached_data.empty:
            if not historical.df.empty:
                # 确保两边的 datetime 都是 naive 且类型一致
                cached_data = self._ensure_naive_datetime(cached_data.copy())
                historical.df = self._ensure_naive_datetime(historical.df.copy())

                # 强制转换 datetime 列为 datetime64 类型（避免 object 类型）
                if cached_data['datetime'].dtype == 'object':
                    cached_data['datetime'] = pd.to_datetime(cached_data['datetime'])
                if historical.df['datetime'].dtype == 'object':
                    historical.df['datetime'] = pd.to_datetime(historical.df['datetime'])

                # 合并新旧数据并去重
                merged_df = pd.concat([cached_data, historical.df], ignore_index=True)

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

        # 应用复权到数据
        if adjust_type != 'none' and not historical.df.empty:
            historical.df = self._apply_adjustment(
                historical.df, symbol, adjust_type, period
            )

        # 写入缓存（完全禁用缓存以排查内存问题）
        if False and use_cache and not historical.df.empty:  # 强制禁用
            cache_df = historical.df.tail(CACHE_SIZE).copy() if len(historical.df) > CACHE_SIZE else historical.df.copy()
            last_time = cache_df.iloc[-1]['datetime']

            # 转换为字典列表（比DataFrame占用内存小得多）
            cache_data = cache_df.to_dict('records')
            del cache_df  # 立即释放DataFrame

            # 新缓存格式：只缓存字典数据
            cache_entry = {
                'data': cache_data,
                'last_time': last_time,
                'count': len(cache_data)
            }

            ttl = 60 if period in ['1m', '5m', '15m', '30m', '1h'] else 300
            self._cache_manager.set(CachePartition.MERGED_KLINE, cache_key, cache_entry, ttl=ttl)
            logger.debug(f"[K线缓存] 已缓存: {symbol} {period} {adjust_type}, {len(cache_data)}条")

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

        # 最终确保所有 datetime 为 naive（避免 API 层 timezone 错误）
        historical.df = self._ensure_naive_datetime(historical.df)

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
        # 1. 检查缓存（使用 CacheManagerService）
        cached = self._cache_manager.get(CachePartition.XDXR, symbol)
        if cached is not None:
            logger.debug(f"[XDXR缓存] 命中: {symbol}, {len(cached)}条")
            return cached

        # 2. 检查文件缓存（L2持久化）
        file_cached = self._load_xdxr_from_file(symbol)
        if file_cached is not None:
            # 放入缓存
            self._cache_manager.set(CachePartition.XDXR, symbol, file_cached, ttl=3600)
            logger.debug(f"[XDXR文件缓存] L2文件命中: {symbol}, {len(file_cached)}条")
            return file_cached

        # 3. 缓存未命中，从数据源获取
        xdxr_data = None

        # 优先从 TdxQuant 获取（覆盖范围更广，仅交易时间可用）
        if TradingTimeChecker.is_trading_time():
            try:
                tdxquant = self._get_adapter('tdxquant')
                if tdxquant and tdxquant.is_available():
                    # TdxQuant SDK 的 get_xdxr_info 方法
                    if hasattr(tdxquant._tq, 'get_xdxr_info'):
                        xdxr_data = tdxquant._tq.get_xdxr_info([symbol])
                        if xdxr_data and symbol in xdxr_data:
                            xdxr_data = xdxr_data[symbol]
                            logger.debug(f"[XDXR] TdxQuant 获取 {symbol} 除权数据: {len(xdxr_data)} 条")
            except Exception as e:
                logger.debug(f"[XDXR] TdxQuant 获取除权数据失败: {e}")

        # 备用: 从 PyTdx 获取（24/7可用）
        if xdxr_data is None:
            try:
                pytdx = self._get_adapter('pytdx')
                if pytdx and pytdx.is_available():
                    xdxr_data = pytdx.get_xdxr_info(symbol)
                    if xdxr_data:
                        logger.debug(f"[XDXR] PyTdx 获取 {symbol} 除权数据: {len(xdxr_data)} 条")
            except Exception as e:
                logger.debug(f"[XDXR] PyTdx 获取除权数据失败: {e}")

        # 4. 如果获取成功，存入缓存和文件
        if xdxr_data:
            # 存入缓存
            self._cache_manager.set(CachePartition.XDXR, symbol, xdxr_data, ttl=3600)
            # 存入文件缓存
            self._save_xdxr_to_file(symbol, xdxr_data)
            logger.info(f"[XDXR缓存] 已更新: {symbol}, {len(xdxr_data)}条")
            return xdxr_data

        logger.debug(f"[XDXR] {symbol} 无除权数据")
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

        Args:
            period: 周期
            adjust_type: 复权类型（暂不使用，复权由服务层统一处理）
        """
        # ── 调用 KlineService 统一入口（内部已包含 HotDB 快速通道）────────────────────────────
        result_dict, data_source = self._kline_service.get_historical_kline(
            symbols=[symbol],
            period=period,
            count=count,
            start_date=start_date,
            end_date=end_date
        )

        # 从结果字典中提取 DataFrame
        df = result_dict.get(symbol) if result_dict else None

        if df is None or df.empty:
            return KlineDataset.empty()

        return KlineDataset.from_adapter(df, data_source)

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
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            filter_today: 是否只过滤今天的数据（保留参数兼容性）
            get_realtime: 是否获取实时数据（保留参数兼容性）
        """
        if not start_date:
            start_date = datetime.now().strftime('%Y%m%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')

        logger.info(f"[SeamlessKlineService] 获取补充数据 {symbol} 从 {start_date} 到 {end_date}")

        # 调用 KlineService 统一入口
        result_dict, data_source = self._kline_service.get_historical_kline(
            symbols=[symbol],
            period=period,
            count=500,
            start_date=start_date,
            end_date=end_date
        )

        # 从结果字典中提取 DataFrame
        df = result_dict.get(symbol) if result_dict else None

        if df is None or df.empty:
            logger.warning(f"[SeamlessKlineService] 未获取到补充数据 {symbol} 从 {start_date}")
            return KlineDataset.empty()

        logger.info(f"[SeamlessKlineService] 获取补充数据成功 {symbol}: {len(df)} 条")

        # ── 回写 HotDB（在线获取的新数据）────────────────────
        # 判断数据来源（通过检查数据是否是最近获取的）
        is_online_source = self._is_from_online_source(df, start_date, end_date)

        if is_online_source and not df.empty:
            # 异步回写到 HotDB（后台任务）
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                asyncio.ensure_future(self._save_to_hotdb(
                    symbol, df, period, source='online'
                ), loop=loop)
                logger.debug(f"[回写任务] 已提交后台保存: {symbol} {period}")
            except RuntimeError:
                # 没有运行中的事件循环，在同步上下文中无法创建异步任务
                logger.debug(f"[回写任务] 无事件循环，跳过后台保存: {symbol} {period}")

        return KlineDataset.from_adapter(df, data_source)

    def _need_realtime_supplement(self, historical: KlineDataset, period: str) -> bool:
        """判断是否需要补充实时数据

        修复：考虑交易时间，避免开盘前误判需要补数据
        """
        if historical.df.empty:
            return False

        last_time = historical.df.iloc[-1]['datetime']
        # 修复：检查 last_time 是否为 None 或 NaT
        if pd.isna(last_time) or last_time is None:
            return False

        now = datetime.now()
        today = now.date()
        last_date = last_time.date()

        # 判断最后数据日期 vs 今天
        logger.info(f"[数据补全检查] 最后数据日期: {last_date}, 今天: {today}, 当前时间: {now.strftime('%H:%M')}")

        if last_date < today:
            # 计算日期差距
            days_diff = (today - last_date).days

            if days_diff > 1:
                # 缺口超过1天，无论当前时间都需要补
                logger.info(f"[数据补全] 数据缺口过大: 缺少 {days_diff} 天数据，需要补全")
                return True

            # 缺口正好1天（昨天）
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

    def _save_to_localdb(self, symbol: str, df: pd.DataFrame, period: str, source: str):
        """异步保存数据到LocalDB

        Args:
            symbol: 股票代码
            df: K线数据DataFrame
            period: 周期
            source: 数据源名称
        """
        # 检查是否需要保存
        if period not in SAVE_PERIODS:
            return

        try:
            # 获取LocalDB适配器
            localdb = self._get_adapter('localdb')
            if not localdb:
                logger.debug("[LocalDB] 适配器不可用，跳过保存")
                return

            # 检查LocalDB是否已有该股票的数据
            existing = localdb.get_kline([symbol], period=period, count=1)
            if symbol in existing and not existing[symbol].empty:
                logger.debug(f"[LocalDB] {symbol} {period} 已存在，跳过保存")
                return

            # 保存数据
            success = localdb.save_kline(symbol, df, period)
            if success:
                logger.info(f"[LocalDB] 从 {source} 自动保存 {symbol} {period}: {len(df)} 条")
            else:
                logger.warning(f"[LocalDB] 保存 {symbol} {period} 失败")

        except Exception as e:
            logger.warning(f"[LocalDB] 保存过程出错: {e}")

    def _get_adapter(self, name: str):
        """获取适配器实例（简化版，不使用缓存）"""
        from myquant.core.market.adapters import get_adapter
        return get_adapter(name)

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

    # ── 数据完整性检查与自动补全 ─────────────────────

    def _detect_data_gaps(
        self,
        df: pd.DataFrame,
        period: str = '1d',
        days_back: int = 30
    ) -> list:
        """检测数据缺口

        Args:
            df: 当前K线数据
            period: 周期
            days_back: 回溯天数

        Returns:
            缺失日期列表
        """
        if df.empty:
            return []

        from datetime import timedelta, date
        import pandas as pd

        # 获取最后日期
        last_date = df.iloc[-1]['datetime']
        if isinstance(last_date, str):
            last_date = pd.to_datetime(last_date)
        elif not isinstance(last_date, pd.Timestamp):
            last_date = pd.Timestamp(last_date)

        if not isinstance(last_date, pd.Timestamp):
            last_date = pd.Timestamp(last_date)

        # 生成应该有的交易日期
        expected_dates = []
        current_date = last_date.date()
        today = date.today()

        # 生成过去N天的交易日（排除周末）
        for i in range(days_back):
            check_date = current_date - timedelta(days=i)
            # 排除周末
            if check_date.weekday() < 5:  # 0-4 是周一到周五
                expected_dates.append(check_date)

        # 转换为集合比较
        actual_dates = set()
        for dt in df['datetime']:
            if isinstance(dt, pd.Timestamp):
                actual_dates.add(dt.date())
            elif isinstance(dt, str):
                actual_dates.add(pd.to_datetime(dt).date())

        expected_set = set(expected_dates)

        # 找出缺失的日期
        missing_dates = expected_set - actual_dates

        if missing_dates:
            missing_sorted = sorted(list(missing_dates))
            logger.info(f"[数据缺口] {period} 缺失 {len(missing_sorted)} 个交易日: {missing_sorted[:5]}...")
            return missing_sorted

        return []

    async def _backfill_missing_data(
        self,
        symbol: str,
        period: str = '1d',
        missing_dates: list = None
    ) -> dict:
        """自动补全缺失数据

        Args:
            symbol: 股票代码
            period: 周期
            missing_dates: 缺失日期列表（None表示自动检测）

        Returns:
            补全结果: {success: bool, count: int, dates: list}
        """
        result = {
            'success': False,
            'count': 0,
            'dates': [],
            'error': None
        }

        try:
            # 如果没有提供缺失日期，先检测
            if missing_dates is None:
                historical = self._get_historical_kline(
                    symbol, period, count=100
                )
                missing_dates = self._detect_data_gaps(
                    historical.df, period, days_back=30
                )

            if not missing_dates:
                result['success'] = True
                result['error'] = '无缺失数据'
                return result

            # 从在线源获取缺失数据
            from myquant.core.market.routing import get_source_selector, DataLevel

            selector = get_source_selector()
            adapter_name = selector.select_by_code(DataLevel.L3, symbol)

            if not adapter_name:
                result['error'] = '无可用数据源'
                return result

            adapter = self._get_adapter(adapter_name)
            if not adapter or not adapter.is_available():
                result['error'] = f'数据源 {adapter_name} 不可用'
                return result

            # 转换日期格式
            start_date = missing_dates[0].strftime('%Y%m%d')
            end_date = missing_dates[-1].strftime('%Y%m%d')

            # 获取数据
            df_dict = adapter.get_kline(
                symbols=[symbol],
                period=period,
                start_date=start_date,
                end_date=end_date
            )

            if symbol not in df_dict or df_dict[symbol].empty:
                result['error'] = '在线获取失败'
                return result

            df = df_dict[symbol]
            result['count'] = len(df)

            # 回写到 HotDB
            hotdb = self._get_adapter('hotdb')
            if hotdb and hotdb.is_available():
                save_success = hotdb.save_kline(symbol, df, period)
                if save_success:
                    logger.info(f"[数据补全] {symbol} {period} 成功回写 HotDB: {len(df)} 条")
                    result['dates'] = [d.strftime('%Y-%m-%d') for d in missing_dates]
                    result['success'] = True
                else:
                    result['error'] = 'HotDB 保存失败'
            else:
                result['error'] = 'HotDB 不可用'

        except Exception as e:
            logger.error(f"[数据补全] {symbol} {period} 失败: {e}")
            result['error'] = str(e)

        return result

    def _synthesize_daily_bar(
        self,
        symbol: str,
        minute_data: pd.DataFrame
    ) -> pd.DataFrame:
        """合成日线数据

        盘中分钟K线 → 收盘时合成为一根完整的日线

        Args:
            symbol: 股票代码
            minute_data: 分钟K线数据

        Returns:
            合成的日线数据（1行DataFrame）
        """
        if minute_data.empty:
            return pd.DataFrame()

        try:
            # 按日期分组
            minute_data = minute_data.copy()
            minute_data['date'] = pd.to_datetime(minute_data['datetime']).dt.date

            # 按日期聚合
            daily_bars = minute_data.groupby('date').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'amount': 'sum'
            }).reset_index()

            # 重命名列
            daily_bars.rename(columns={'date': 'datetime'}, inplace=True)
            daily_bars['datetime'] = pd.to_datetime(daily_bars['datetime'])

            # 标记为完整K线
            daily_bars['is_complete'] = True

            return daily_bars

        except Exception as e:
            logger.error(f"[日线合成] {symbol} 失败: {e}")
            return pd.DataFrame()

    async def _save_to_hotdb(
        self,
        symbol: str,
        df: pd.DataFrame,
        period: str,
        source: str = 'online'
    ) -> bool:
        """回写数据到 HotDB

        Args:
            symbol: 股票代码
            df: K线数据
            period: 周期
            source: 数据来源（online/synthesized）

        Returns:
            是否成功
        """
        try:
            hotdb = self._get_adapter('hotdb')
            if not hotdb or not hotdb.is_available():
                logger.warning(f"[HotDB回写] HotDB 不可用")
                return False

            success = hotdb.save_kline(symbol, df, period)
            if success:
                logger.info(f"[HotDB回写] {symbol} {period} 成功保存 {len(df)} 条 (来源: {source})")
            else:
                logger.warning(f"[HotDB回写] {symbol} {period} 保存失败")

            return success

        except Exception as e:
            logger.error(f"[HotDB回写] {symbol} {period} 异常: {e}")
            return False

    def _is_from_online_source(
        self,
        df: pd.DataFrame,
        start_date: str,
        end_date: str
    ) -> bool:
        """判断数据是否来自在线源

        通过检查数据的日期范围和请求的日期范围来判断

        Args:
            df: K线数据
            start_date: 请求的开始日期
            end_date: 请求的结束日期

        Returns:
            是否来自在线源
        """
        if df.empty:
            return False

        try:
            # 如果请求的日期包含今天，很可能是在线源
            from datetime import datetime
            today = datetime.now().strftime('%Y%m%d')

            if end_date == today or start_date == today:
                return True

            # 如果数据量小于请求数量的一定比例，可能是增量获取
            # 这里简化处理，假设需要实时更新的都是在线源
            return False

        except Exception:
            return False

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
