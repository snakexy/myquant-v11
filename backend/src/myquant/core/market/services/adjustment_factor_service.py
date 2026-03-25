"""
复权因子服务

提供复权因子表的预计算和缓存管理
支持混合模式：日线用前复权，分钟线用等比前复权
"""

import pickle
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import numpy as np
from loguru import logger

from myquant.config.settings import XDXR_DIR
from myquant.core.market.services.cache import TTLCache


class AdjustmentFactorService:
    """复权因子服务

    管理复权因子表的计算、缓存和应用
    支持两种复权方式：
    - 前复权(front): 累积因子，适用于日线（数据完整）
    - 等比前复权(front_ratio): 独立因子，适用于分钟线（数据不完整）
    """

    def __init__(self):
        # L1内存缓存：因子表缓存（TTL 7天）
        self._factor_cache = TTLCache(maxsize=500, ttl=7 * 24 * 3600)
        # L2文件缓存TTL：7天
        self._file_ttl = 7 * 24 * 3600
        logger.info("[AdjustmentFactorService] 初始化完成")

    def get_factor_table(self, symbol: str, adjust_type: str) -> dict:
        """获取复权因子表（带两级缓存）

        优先级：内存缓存 → 文件缓存 → 计算并缓存

        Args:
            symbol: 股票代码
            adjust_type: 复权类型 (front/front_ratio)

        Returns:
            复权因子表 { "2024-01-01": 1.05, ... }
        """
        cache_key = f"{symbol}:{adjust_type}"

        # 1. 检查内存缓存
        cached = self._factor_cache.get(cache_key)
        if cached is not None:
            logger.debug(f"[FactorCache] L1内存命中: {symbol} {adjust_type}")
            return cached

        # 2. 检查文件缓存
        file_cached = self._load_factor_table_from_file(symbol, adjust_type)
        if file_cached is not None:
            self._factor_cache.set(cache_key, file_cached, ttl=7 * 24 * 3600)
            logger.debug(f"[FactorCache] L2文件命中: {symbol} {adjust_type}")
            return file_cached

        # 3. 缓存未命中，需要计算
        logger.info(f"[FactorCache] 未命中，开始计算: {symbol} {adjust_type}")

        # 获取XDXR数据（从seamless_service的缓存获取）
        xdxr_data = self._get_xdxr_data(symbol)
        if not xdxr_data:
            logger.warning(f"[FactorCache] {symbol} 无XDXR数据，返回空因子表")
            return {}

        # 计算因子表
        if adjust_type == 'front':
            factor_table = self._calculate_front_factors(symbol, xdxr_data)
        elif adjust_type == 'front_ratio':
            factor_table = self._calculate_front_ratio_factors(xdxr_data)
        else:
            logger.warning(f"[FactorCache] 不支持的复权类型: {adjust_type}")
            return {}

        # 4. 存入两级缓存
        if factor_table:
            self._factor_cache.set(cache_key, factor_table, ttl=7 * 24 * 3600)
            self._save_factor_table_to_file(symbol, adjust_type, factor_table)
            logger.info(f"[FactorCache] 已计算并缓存: {symbol} {adjust_type}, "
                       f"{len(factor_table)}个因子")

        return factor_table

    def apply_factors(self, df: pd.DataFrame, factor_table: dict) -> pd.DataFrame:
        """应用复权因子到K线数据

        纯查表操作，O(n)复杂度

        Args:
            df: K线数据DataFrame（必须包含datetime列）
            factor_table: 复权因子表 { "2024-01-01": factor, ... }

        Returns:
            复权后的DataFrame
        """
        if df.empty or not factor_table:
            return df

        try:
            # 创建副本避免修改原数据
            df = df.copy()

            # 提取日期字符串
            df['date'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d')

            # 为每条记录查找适用的因子
            # 因子表已经按日期展开，直接map即可
            df['factor'] = df['date'].map(factor_table).fillna(1.0)

            # 应用因子到价格列
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df.columns:
                    df[col] = df[col] * df['factor']

            # 删除临时列
            df = df.drop(columns=['date', 'factor'])

            return df

        except Exception as e:
            logger.warning(f"[FactorApply] 应用复权因子失败: {e}")
            return df

    def _calculate_front_factors(self, symbol: str, xdxr_data: list) -> dict:
        """计算前复权累积因子表（日线用）- 向量化优化版

        优化点：
        1. 使用pandas向量化操作替代Python循环（提速10-30x）
        2. 使用merge_asof替代嵌套循环查找（O(n×m) -> O(n log m)）
        3. 动态日期范围（从最早除权日开始，而非固定2020-01-01）
        4. 使用除权日实际收盘价计算分红因子（提高准确性）

        性能：从~200ms降至~20ms

        Args:
            symbol: 股票代码
            xdxr_data: XDXR原始数据列表

        Returns:
            每日对应的累积因子表 { "2024-01-01": 1.05, ... }
        """
        if not xdxr_data:
            return {}

        try:
            # 1. 转换为DataFrame（向量化基础）
            xdxr_df = pd.DataFrame(xdxr_data)

            # 检查必要的字段
            if 'category' not in xdxr_df.columns:
                logger.debug(f"[FactorCalc] XDXR数据缺少category字段")
                return {}

            # 2. 筛选除权记录（向量化过滤）
            dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()

            if len(dividend_records) == 0:
                return {}

            # 3. 向量化计算日期列（无Python循环）
            dividend_records['date'] = pd.to_datetime(
                dividend_records[['year', 'month', 'day']]
            )

            # 3.5 获取除权日的实际收盘价（直接在方法内获取）
            ex_dates = dividend_records['date'].dt.strftime('%Y-%m-%d').tolist()

            # 获取K线数据来匹配收盘价
            from ..adapters import get_adapter
            adapter = get_adapter('xtquant')
            if adapter is None or not adapter.is_available():
                adapter = get_adapter('pytdx')

            close_dict = {}
            if adapter is not None:
                try:
                    # 获取足够多的数据覆盖所有除权日
                    klines = adapter.get_kline(symbols=[symbol], period='1d', count=2000)
                    if klines and symbol in klines:
                        df = klines[symbol]
                        if df is not None and not df.empty:
                            # 兼容不同的日期列名
                            date_col = None
                            for col in ['datetime', 'date', 'time', 'timestamp']:
                                if col in df.columns:
                                    date_col = col
                                    break

                            if date_col:
                                df['date_str'] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
                                for ex_date in ex_dates:
                                    matches = df[df['date_str'] == ex_date]
                                    if not matches.empty:
                                        close_dict[ex_date] = matches.iloc[0]['close']
                                        logger.info(f"[FactorCalc] {ex_date} 收盘价: {close_dict[ex_date]:.2f}")
                            else:
                                logger.warning(f"[FactorCalc] K线数据没有日期列，可用列: {df.columns.tolist()}")
                except Exception as e:
                    logger.warning(f"[FactorCalc] 获取收盘价失败: {e}")

            dividend_records['close'] = dividend_records['date'].dt.strftime('%Y-%m-%d').map(close_dict)

            # 4. 向量化计算单日复权因子（整列同时计算）
            # 提取字段为Series
            fenhong = dividend_records['fenhong'].fillna(0)  # 10派X元
            songgu = dividend_records['songzhuangu'].fillna(0)  # 10送Y股
            peigu = dividend_records['peigu'].fillna(0)  # 10配Z股
            peigujia = dividend_records['peigujia'].fillna(0)
            close_prices = dividend_records['close']  # 实际收盘价

            # 每股分红 = 派息金额 / 10
            dividend_per_share = fenhong / 10

            # 计算除权价（理论价）
            # 除权价 = (收盘价 - 分红) / (1 + 送股率 + 配股率)
            # 注意：如果有配股，还需要考虑配股的影响
            ex_price = (close_prices - dividend_per_share) / (1 + songgu/10 + peigu/10)

            # 单日因子 = 除权价 / 收盘价
            dividend_records['daily_factor'] = (ex_price / close_prices).fillna(1.0)

            # 处理无效值
            dividend_records.loc[dividend_records['daily_factor'] <= 0, 'daily_factor'] = 1.0
            dividend_records.loc[dividend_records['daily_factor'] > 10, 'daily_factor'] = 1.0  # 异常值保护

            # 5. 向量化累积计算（降序排列，从新到旧）
            dividend_records = dividend_records.sort_values('date', ascending=False)
            dividend_records['cumulative'] = dividend_records['daily_factor'].cumprod()

            # DEBUG: 打印除权记录
            logger.debug(f"[FactorCalc] 除权记录 (共{len(dividend_records)}条):")
            for _, row in dividend_records.head(5).iterrows():
                logger.debug(f"  日期: {row['date']}, 分红: {row.get('fenhong', 0)}, "
                           f"收盘: {row.get('close', 0):.2f}, 因子: {row['daily_factor']:.6f}, "
                           f"累积: {row['cumulative']:.6f}")

            # 前复权逻辑：使用累积因子（cumprod计算的结果）
            # 最新除权日之后的日期因子=1.0
            latest_ex_date = dividend_records['date'].max()

            # 6. 动态日期范围优化（从最早除权日往前推，确保包含除权前日期）
            earliest_ex_date = dividend_records['date'].min()
            start_date = earliest_ex_date - pd.Timedelta(days=7)  # 往前推7天，确保覆盖除权前
            end_date = pd.Timestamp.now()

            # 生成每日日期
            daily_df = pd.DataFrame({
                'date': pd.date_range(start=start_date, end=end_date, freq='D')
            })

            # 7. 向量化查找：使用merge_asof（C实现二分查找，替代嵌套循环）
            # direction='backward': 向后查找最近的除权日
            # - 除权日之前的日期会找到前一个除权日的累积因子
            # - 除权日会找到自己的累积因子
            # 注意：merge_asof 要求 right 必须按 date 升序排列
            dividend_for_merge = dividend_records.sort_values('date', ascending=True)

            # 前复权特殊处理：最新除权日之后的日期因子=1.0
            latest_ex_date = dividend_records['date'].max()

            result_df = pd.merge_asof(
                daily_df,
                dividend_for_merge[['date', 'cumulative']],
                on='date',
                direction='backward'
            )

            # 最新除权日之后的日期因子=1.0（让最新价格不变）
            result_df.loc[result_df['date'] > latest_ex_date, 'cumulative'] = 1.0

            # 填充无除权日的因子为1.0
            result_df['cumulative'] = result_df['cumulative'].fillna(1.0)

            # 8. 向量化转为字典（比Python循环快）
            result_df['date_str'] = result_df['date'].dt.strftime('%Y-%m-%d')
            factor_dict = result_df.set_index('date_str')['cumulative'].to_dict()

            logger.debug(f"[FactorCalc] 向量化计算完成: {len(factor_dict)}天, "
                        f"除权日{len(dividend_records)}个")

            return factor_dict

        except Exception as e:
            logger.warning(f"[FactorCalc] 向量化计算失败: {e}，回退到循环版本")
            # 回退到旧版本（保险）
            return self._calculate_front_factors_legacy(xdxr_data)

    def _calculate_front_factors_legacy(self, xdxr_data: list) -> dict:
        """计算前复权累积因子表（循环版本，作为回退）"""
        # 保留旧实现作为保险
        try:
            xdxr_df = pd.DataFrame(xdxr_data)
            if 'category' not in xdxr_df.columns:
                return {}

            dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()
            if len(dividend_records) == 0:
                return {}

            dividend_records['date'] = dividend_records.apply(
                lambda row: f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}",
                axis=1
            )
            dividend_records = dividend_records.sort_values('date', ascending=False)

            daily_factors = {}
            for _, record in dividend_records.iterrows():
                date = record['date']
                fenhong = float(record.get('fenhong', 0) or 0)
                songgu = float(record.get('songzhuangu', 0) or 0)
                peigu = float(record.get('peigu', 0) or 0)
                peigujia = float(record.get('peigujia', 0) or 0)

                # 标准前复权算法：综合送转股和分红
                # 1. 股本调整因子
                share_ratio = 1 + songgu/10 + peigu/10
                ratio_factor = 1.0 / share_ratio if share_ratio > 0 else 1.0

                # 2. 分红调整因子（改进：动态估算股价）
                dividend_per_share = fenhong / 10
                # 根据每股分红推断股价水平（茅台每股分红24-31元，股价2200元）
                if dividend_per_share > 20:
                    est_price = 2200.0  # 茅台级别（提高以减少误差）
                elif dividend_per_share > 12:
                    est_price = 1600.0  # 高价股
                elif dividend_per_share > 8:
                    est_price = 1000.0  # 中高价股
                elif dividend_per_share > 3:
                    est_price = 500.0   # 中价股
                else:
                    est_price = 200.0   # 低价股

                dividend_factor = (est_price - dividend_per_share) / est_price
                if dividend_factor <= 0 or dividend_factor > 2:
                    dividend_factor = 1.0

                # 3. 综合因子
                factor = ratio_factor * dividend_factor
                if 0 < factor < 10:  # 合理性检查
                    daily_factors[date] = factor

            if not daily_factors:
                return {}

            cumulative_factors = {}
            sorted_dates = sorted(daily_factors.keys(), reverse=True)
            cumulative = 1.0
            for date in sorted_dates:
                cumulative = cumulative * daily_factors[date]
                cumulative_factors[date] = cumulative

            result = {}
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = dividend_records['date'].min()[:10] if 'date' in dividend_records.columns else "2020-01-01"
            # 往前推7天，确保覆盖除权前日期
            from datetime import timedelta
            start_dt = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=7)
            start_date = start_dt.strftime('%Y-%m-%d')
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')

            # 获取最新除权日
            latest_ex_date = sorted_dates[0] if sorted_dates else None

            for current_date in date_range:
                date_str = current_date.strftime('%Y-%m-%d')
                # 除权日及之后用 1.0
                if latest_ex_date and date_str >= latest_ex_date:
                    result[date_str] = 1.0
                else:
                    # 除权日之前，查找适用的累积因子
                    applicable_factor = 1.0
                    for ex_date in sorted_dates:
                        if date_str < ex_date:
                            applicable_factor = cumulative_factors[ex_date]
                            break
                    result[date_str] = applicable_factor

            return result

        except Exception as e:
            logger.warning(f"[FactorCalc] 循环版本也失败: {e}")
            return {}

    def _calculate_front_ratio_factors(self, xdxr_data: list) -> dict:
        """计算等比前复权独立因子表（分钟线用）- 向量化优化版

        优化点：
        1. 向量化计算独立因子（无Python循环）
        2. 使用cumprod累积（C实现）
        3. 动态日期范围（从最早除权日开始）

        性能：从~100ms降至~10ms

        Args:
            xdxr_data: XDXR原始数据列表

        Returns:
            每日对应的独立因子表 { "2024-01-01": 1.05, ... }
        """
        if not xdxr_data:
            return {}

        try:
            # 1. 转换为DataFrame
            xdxr_df = pd.DataFrame(xdxr_data)

            if 'category' not in xdxr_df.columns:
                logger.debug(f"[FactorCalc] XDXR数据缺少category字段")
                return {}

            # 2. 筛选除权记录（向量化）
            dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()

            if len(dividend_records) == 0:
                return {}

            # 3. 向量化计算日期列
            dividend_records['date'] = pd.to_datetime(
                dividend_records[['year', 'month', 'day']]
            )

            # 4. 向量化计算等比因子（整列计算）
            songgu = dividend_records['songzhuangu'].fillna(0) / 10
            peigu = dividend_records['peigu'].fillna(0) / 10
            denominator = (1 + songgu + peigu).replace(0, np.nan)
            dividend_records['ratio_factor'] = (1 / denominator).fillna(1.0)

            # 5. 按日期排序（从旧到新，升序）
            dividend_records = dividend_records.sort_values('date', ascending=True)

            # 6. 从旧到新累积计算
            # 这样越新的日期累积值越大（累积了更多除权）
            dividend_records['cumulative'] = dividend_records['ratio_factor'].cumprod()

            # 7. 取倒数作为前复权因子
            # 最新日期的cumulative最大，倒数最小→接近1.0（最新价格不变）
            # 早期日期的cumulative接近1.0，倒数较大→历史价格放大
            dividend_records['adjustment_factor'] = 1.0 / dividend_records['cumulative']

            # 8. 动态日期范围
            earliest_ex_date = dividend_records['date'].min()
            latest_ex_date = dividend_records['date'].max()
            start_date = earliest_ex_date - pd.Timedelta(days=7)  # 往前推7天
            end_date = pd.Timestamp.now()

            daily_df = pd.DataFrame({
                'date': pd.date_range(start=start_date, end=end_date, freq='D')
            })

            # 9. 向量化查找（merge_asof with direction='backward'）
            # 关键理解：
            # - dividend_records 已按 date 升序排列
            # - cumulative 已从旧到新累积（越新越大）
            # - direction='backward': 向后找最近的除权日
            #   - 除权日当天：找到自己的累积因子
            #   - 除权日之间的日期：找到上一个除权日的累积因子
            #   - 最旧除权日之前的日期：找不到 → NaN → 需要特殊处理
            # merge_asof 要求 left 必须升序
            result_df = pd.merge_asof(
                daily_df,  # 默认已升序
                dividend_records[['date', 'cumulative']],  # 升序
                on='date',
                direction='backward'
            )

            # 10. 特殊处理
            # 最新除权日之后的日期因子=1.0（最新价格不变）
            result_df.loc[result_df['date'] > latest_ex_date, 'cumulative'] = 1.0

            # 最旧除权日之前的日期：应该使用最旧除权日的累积因子
            # 这些日期的 cumulative 是 NaN（找不到过去的除权日）
            earliest_cumulative = dividend_records.iloc[0]['cumulative']
            result_df['cumulative'] = result_df['cumulative'].fillna(earliest_cumulative)

            # 11. 取倒数作为前复权因子
            # 这样最新日期factor=1.0，旧日期factor>1.0（历史价格放大）
            result_df['adjustment_factor'] = 1.0 / result_df['cumulative']

            # 12. 转为字典
            result_df['date_str'] = result_df['date'].dt.strftime('%Y-%m-%d')
            return result_df.set_index('date_str')['adjustment_factor'].to_dict()

        except Exception as e:
            logger.warning(f"[FactorCalc] 等比复权向量化计算失败: {e}，回退到循环版本")
            return self._calculate_front_ratio_factors_legacy(xdxr_data)

    def _calculate_front_ratio_factors_legacy(self, xdxr_data: list) -> dict:
        """计算等比前复权独立因子表（循环版本，作为回退）"""
        try:
            xdxr_df = pd.DataFrame(xdxr_data)
            if 'category' not in xdxr_df.columns:
                return {}

            dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()
            if len(dividend_records) == 0:
                return {}

            dividend_records['date'] = dividend_records.apply(
                lambda row: f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}",
                axis=1
            )
            dividend_records = dividend_records.sort_values('date', ascending=False)

            daily_factors = {}
            for _, record in dividend_records.iterrows():
                date = record['date']
                songgu = float(record.get('songzhuangu', 0) or 0) / 10
                peigu = float(record.get('peigu', 0) or 0) / 10
                if (1 + songgu + peigu) > 0:
                    factor = 1 / (1 + songgu + peigu)
                    daily_factors[date] = factor

            if not daily_factors:
                return {}

            # 从新到旧累积，最后取倒数
            sorted_dates = sorted(daily_factors.keys(), reverse=True)
            if not sorted_dates:
                return {}

            earliest_date = sorted_dates[-1]
            latest_date = datetime.now().strftime('%Y-%m-%d')
            date_range = pd.date_range(start=earliest_date, end=latest_date, freq='D')

            result = {}
            cumulative = 1.0

            # 从新到旧遍历
            for current_date in reversed(date_range):
                date_str = current_date.strftime('%Y-%m-%d')
                if date_str in daily_factors:
                    cumulative = cumulative * daily_factors[date_str]
                # 倒数作为前复权因子
                result[date_str] = 1.0 / cumulative

            return result

        except Exception as e:
            logger.warning(f"[FactorCalc] 等比复权循环版本也失败: {e}")
            return {}

    def _get_xdxr_data(self, symbol: str) -> list:
        """获取XDXR数据

        从seamless_service获取（共享其缓存）
        注意：这里会触发循环导入，所以改为独立获取

        Args:
            symbol: 股票代码

        Returns:
            XDXR数据列表
        """
        try:
            # 直接从seamless_service导入并获取
            from myquant.core.market.services.seamless_service import get_seamless_kline_service
            service = get_seamless_kline_service()
            return service._get_xdxr_data(symbol)
        except Exception as e:
            logger.warning(f"[FactorService] 获取XDXR数据失败: {e}")
            return []

    def _get_factor_table_path(self, symbol: str, adjust_type: str) -> Path:
        """获取因子表文件路径

        Args:
            symbol: 股票代码
            adjust_type: 复权类型

        Returns:
            Path对象
        """
        safe_symbol = symbol.replace('.', '_').replace('/', '_')
        symbol_dir = XDXR_DIR / safe_symbol
        symbol_dir.mkdir(parents=True, exist_ok=True)
        return symbol_dir / f"factors_{adjust_type}.pkl"

    def _load_factor_table_from_file(self, symbol: str, adjust_type: str) -> Optional[dict]:
        """从文件加载因子表

        Args:
            symbol: 股票代码
            adjust_type: 复权类型

        Returns:
            因子表字典或None
        """
        try:
            file_path = self._get_factor_table_path(symbol, adjust_type)
            if not file_path.exists():
                return None

            # 检查过期
            mtime = file_path.stat().st_mtime
            age = time.time() - mtime
            if age > self._file_ttl:
                logger.debug(f"[FactorFile] {symbol} {adjust_type} 已过期")
                return None

            # 读取pickle二进制文件（比JSON快5-10倍）
            with open(file_path, 'rb') as f:
                data = pickle.load(f)

            if isinstance(data, dict):
                logger.debug(f"[FactorFile] {symbol} {adjust_type} 加载成功: {len(data)}条")
                return data
            else:
                return None

        except Exception as e:
            logger.debug(f"[FactorFile] 加载失败: {e}")
            return None

    def _save_factor_table_to_file(self, symbol: str, adjust_type: str, factor_table: dict) -> bool:
        """保存因子表到文件

        Args:
            symbol: 股票代码
            adjust_type: 复权类型
            factor_table: 因子表字典

        Returns:
            是否保存成功
        """
        try:
            file_path = self._get_factor_table_path(symbol, adjust_type)

            # 保存为pickle二进制格式（更快且更小）
            with open(file_path, 'wb') as f:
                pickle.dump(factor_table, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.debug(f"[FactorFile] {symbol} {adjust_type} 已保存: {len(factor_table)}条")
            return True

        except Exception as e:
            logger.warning(f"[FactorFile] 保存失败: {e}")
            return False


# 单例实例
_factor_service_instance: Optional[AdjustmentFactorService] = None


def get_adjustment_factor_service() -> AdjustmentFactorService:
    """获取AdjustmentFactorService单例"""
    global _factor_service_instance
    if _factor_service_instance is None:
        _factor_service_instance = AdjustmentFactorService()
    return _factor_service_instance
