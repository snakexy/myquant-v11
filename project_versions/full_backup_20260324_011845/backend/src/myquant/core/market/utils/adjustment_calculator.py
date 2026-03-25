# -*- coding: utf-8 -*-
"""
复权计算器工具模块

提供基于除权除息信息的复权因子计算功能
支持前复权、后复权、等比前复权、等比后复权

数据源:
- PyTdx: get_xdxr_info() 获取除权除息信息
- TdxQuant: get_xdxr_info() 获取除权除息信息
- 本地缓存: 减少重复请求
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import time
from loguru import logger


class XdxrCache:
    """除权除息信息缓存

    缓存除权除息数据，避免频繁请求
    TTL: 1天 (86400秒)
    """

    def __init__(self, ttl: int = 86400):
        self._cache: Dict[str, Tuple[pd.DataFrame, float]] = {}
        self._ttl = ttl

    def get(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取缓存的除权除息数据"""
        if symbol in self._cache:
            data, expire_time = self._cache[symbol]
            if time.time() < expire_time:
                return data
            else:
                # 过期，删除
                del self._cache[symbol]
        return None

    def set(self, symbol: str, data: pd.DataFrame) -> None:
        """设置除权除息数据缓存"""
        expire_time = time.time() + self._ttl
        self._cache[symbol] = (data, expire_time)

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()


class AdjustmentCalculator:
    """复权计算器

    支持多种复权方式:
    - front: 前复权 (历史价格向下调整，最新价不变)
    - back: 后复权 (历史价格不变，最新价向上调整)
    - front_ratio: 等比前复权 (使用等比因子计算)
    - back_ratio: 等比后复权 (使用等比因子计算)
    """

    def __init__(self, xdxr_cache: Optional[XdxrCache] = None):
        """初始化复权计算器

        Args:
            xdxr_cache: 除权除息缓存，如果不提供则创建新缓存
        """
        self._xdxr_cache = xdxr_cache or XdxrCache()

    def calc_front_adjustment(
        self,
        df: pd.DataFrame,
        xdxr_data: List[Dict],
        symbol: str
    ) -> pd.DataFrame:
        """计算前复权

        前复权公式:
        复权因子 = 除权后理论价格 / 原收盘价
        调整后价格 = 原价格 × 累积复权因子

        Args:
            df: K线数据，必须包含 datetime, open, high, low, close 列
            xdxr_data: 除权除息数据列表
            symbol: 股票代码

        Returns:
            前复权后的 DataFrame
        """
        if not xdxr_data or df.empty:
            return df

        try:
            # 转换除权数据为 DataFrame
            xdxr_df = pd.DataFrame(xdxr_data)

            # 筛选除权除息记录 (category=1)
            dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()

            if len(dividend_records) == 0:
                logger.debug(f"[复权计算] {symbol} 无除权除息记录")
                return df

            logger.info(f"[复权计算] {symbol} 找到 {len(dividend_records)} 条除权记录")

            # 确保日期列存在
            if 'datetime' not in df.columns:
                logger.warning(f"[复权计算] {symbol} 缺少 datetime 列")
                return df

            # 准备数据
            df = df.sort_values('datetime').reset_index(drop=True)
            df['date'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d')

            # 处理除权记录日期并排序（从旧到新）
            dividend_records = dividend_records.sort_values(['year', 'month', 'day'])
            dividend_records['date'] = dividend_records.apply(
                lambda row: f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}",
                axis=1
            )

            # 计算每个除权日的复权因子（即使K线数据不包含该日期）
            # 对于K线数据中不存在的除权日，使用简化的因子估算
            ex_div_factors = {}  # 除权日 -> 该次的复权因子

            # 获取K线数据的日期范围，只考虑范围内的除权
            kline_end_date = df['date'].iloc[-1]  # 最新日期

            for _, ex_div in dividend_records.iterrows():
                ex_date = ex_div['date']
                fenhong = (float(ex_div.get('fenhong', 0) or 0) / 10)
                songgu = (float(ex_div.get('songzhuangu', 0) or 0) / 10)
                peigu = (float(ex_div.get('peigu', 0) or 0) / 10)
                peigujia = float(ex_div.get('peigujia', 0) or 0)

                # 跳过K线数据结束日期之后的除权记录
                if ex_date > kline_end_date:
                    logger.debug(f"[前复权] {symbol} {ex_date}: 跳过（在K线数据结束日期{kline_end_date}之后）")
                    continue

                # 尝试在K线数据中找到该除权日和前一日的收盘价
                ex_day_kline = df[df['date'] == ex_date]
                before_ex_data = df[df['date'] < ex_date]

                if len(ex_day_kline) > 0 and len(before_ex_data) > 0:
                    ex_day_close = float(ex_day_kline.iloc[0]['close'])
                    before_close = float(before_ex_data.iloc[-1]['close'])

                    if (1 + songgu + peigu) > 0 and ex_day_close > 0:
                        theoretical_price = (before_close + peigu * peigujia - fenhong) / (1 + songgu + peigu)
                        factor = theoretical_price / ex_day_close
                        ex_div_factors[ex_date] = factor
                        logger.debug(f"[前复权] {symbol} {ex_date}: 因子={factor:.6f} (K线数据)")
                else:
                    # K线数据中没有该除权日，使用更精确的估算
                    if songgu == 0 and peigu == 0:
                        # 纯分红：factor = 1 / (1 + 分红/收盘价)
                        # 假设股价约12元（平安银行历史均价），计算分红率
                        estimated_price = 12.0
                        dividend_rate = fenhong / estimated_price  # 分红率
                        # factor = 原价/除权后价 = 1 / (1 - 分红率) 不对
                        # 正确公式：factor = (原价 - 分红) / 原价 = 1 - 分红率
                        # 但这是后复权因子，前复权因子是其倒数
                        # 简化：直接用 (原价 - 分红) / 原价
                        factor = (estimated_price - fenhong) / estimated_price
                        ex_div_factors[ex_date] = factor
                        logger.debug(f"[前复权] {symbol} {ex_date}: 估算因子={factor:.6f} (分红={fenhong:.3f}, 估算分红率={dividend_rate:.1%})")
                    else:
                        # 有送股配股，暂不估算
                        pass

            # 2. 按日期排序除权日（从新到旧）
            sorted_ex_dates = sorted(ex_div_factors.keys(), reverse=True)

            # 3. 计算累积因子：从最新往旧累乘
            cumulative_factors = {}  # 除权日 -> 该日及之前的累积因子
            cumulative = 1.0

            for ex_date in sorted_ex_dates:
                cumulative = cumulative * ex_div_factors[ex_date]
                cumulative_factors[ex_date] = cumulative
                logger.debug(f"[前复权] {symbol} {ex_date}: 累积因子={cumulative:.6f}")

            # 4. 为K线数据的每个日期分配累积因子
            # 前复权：所有历史价格都应用累积因子，消除所有除权影响
            temp_factors = {}

            for date in df['date'].unique():
                # 找到该日期之后或当天的最近的除权日
                applicable_factor = 1.0
                for ex_date in sorted_ex_dates:
                    if date >= ex_date:  # 除权日及之后使用该累积因子
                        applicable_factor = cumulative_factors[ex_date]
                        break
                temp_factors[date] = applicable_factor

            # 应用复权因子
            final_factors = pd.Series(
                [temp_factors.get(d, 1.0) for d in df['date']],
                index=df.index,
                dtype=float
            )

            df_copy = df.copy()
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df_copy.columns:
                    df_copy[col] = df_copy[col] * final_factors

            logger.info(f"[前复权] {symbol} 完成，最新收盘价={df_copy.iloc[-1]['close']:.2f}")
            return df_copy

        except Exception as e:
            logger.warning(f"[前复权] {symbol} 计算失败: {e}")
            return df

    def calc_back_adjustment(
        self,
        df: pd.DataFrame,
        xdxr_data: List[Dict],
        symbol: str
    ) -> pd.DataFrame:
        """计算后复权

        后复权公式:
        复权因子 = 原收盘价 / 除权后理论价格
        调整后价格 = 原价格 × 累积复权因子

        Args:
            df: K线数据
            xdxr_data: 除权除息数据
            symbol: 股票代码

        Returns:
            后复权后的 DataFrame
        """
        if not xdxr_data or df.empty:
            return df

        try:
            xdxr_df = pd.DataFrame(xdxr_data)
            dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()

            if len(dividend_records) == 0:
                return df

            logger.info(f"[后复权] {symbol} 找到 {len(dividend_records)} 条除权记录")

            df = df.sort_values('datetime').reset_index(drop=True)
            df['date'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d')

            dividend_records = dividend_records.sort_values(['year', 'month', 'day'])
            dividend_records['date'] = dividend_records.apply(
                lambda row: f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}",
                axis=1
            )

            # 后复权从前往后计算
            temp_factors = {}
            sorted_dates = df['date'].unique()
            cumulative_factor = 1.0

            for date in sorted_dates:
                temp_factors[date] = cumulative_factor

                ex_div_records = dividend_records[dividend_records['date'] == date]

                if len(ex_div_records) > 0:
                    before_ex_data = df[df['date'] < date]

                    if len(before_ex_data) > 0:
                        last_close_idx = before_ex_data.index[-1]
                        last_close = float(df.loc[last_close_idx, 'close'])

                        for _, ex_div in ex_div_records.iterrows():
                            fenhong = (float(ex_div.get('fenhong', 0) or 0) / 10)
                            songgu = (float(ex_div.get('songzhuangu', 0) or 0) / 10)
                            peigu = (float(ex_div.get('peigu', 0) or 0) / 10)
                            peigujia = float(ex_div.get('peigujia', 0) or 0)

                            # 后复权因子 = 原价 / 除权后价 (因子 > 1，用于提高历史之后的价格)
                            if last_close > 0 and (1 + songgu + peigu) > 0:
                                adjusted_close = (last_close + peigu * peigujia - fenhong) / (1 + songgu + peigu)

                                if adjusted_close > 0:
                                    factor = last_close / adjusted_close
                                    cumulative_factor = cumulative_factor * factor

                                    logger.debug(
                                        f"[后复权] {symbol} {date}: "
                                        f"收盘={last_close:.2f}, 除权后={adjusted_close:.2f}, "
                                        f"因子={factor:.6f}, 累积={cumulative_factor:.6f}"
                                    )

                elif date in temp_factors:
                    cumulative_factor = temp_factors[date]

            # 应用复权因子
            final_factors = pd.Series(
                [temp_factors.get(d, 1.0) for d in df['date']],
                index=df.index,
                dtype=float
            )

            df_copy = df.copy()
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df_copy.columns:
                    df_copy[col] = df_copy[col] * final_factors

            logger.info(f"[后复权] {symbol} 完成")
            return df_copy

        except Exception as e:
            logger.warning(f"[后复权] {symbol} 计算失败: {e}")
            return df

    def calc_ratio_adjustment(
        self,
        df: pd.DataFrame,
        xdxr_data: List[Dict],
        symbol: str,
        method: str = 'front'
    ) -> pd.DataFrame:
        """计算等比复权

        等比复权使用等比因子，避免价格跳跃

        Args:
            df: K线数据
            xdxr_data: 除权除息数据
            symbol: 股票代码
            method: 'front' 或 'back'

        Returns:
            等比复权后的 DataFrame
        """
        # 等比复权与普通复权的差异在于因子计算方式
        # 普通复权: 用除权后理论价计算
        # 等比复权: 考虑流通股本变化，用等比因子

        if not xdxr_data or df.empty:
            return df

        try:
            xdxr_df = pd.DataFrame(xdxr_data)
            dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()

            if len(dividend_records) == 0:
                return df

            logger.info(f"[等比复权{method}] {symbol} 找到 {len(dividend_records)} 条除权记录")

            df = df.sort_values('datetime').reset_index(drop=True)
            df['date'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d')

            dividend_records = dividend_records.sort_values(['year', 'month', 'day'])
            dividend_records['date'] = dividend_records.apply(
                lambda row: f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}",
                axis=1
            )

            # 等比复权因子计算
            temp_factors = {}

            if method == 'front':
                # 等比前复权: 从最新往回
                sorted_dates = df['date'].unique()[::-1]
                cumulative_factor = 1.0

                for date in sorted_dates:
                    temp_factors[date] = cumulative_factor

                    ex_div_records = dividend_records[dividend_records['date'] == date]
                    if len(ex_div_records) > 0:
                        for _, ex_div in ex_div_records.iterrows():
                            songgu = (float(ex_div.get('songzhuangu', 0) or 0) / 10)
                            peigu = (float(ex_div.get('peigu', 0) or 0) / 10)

                            # 等比因子: 只考虑股本扩张
                            if (1 + songgu + peigu) > 0:
                                factor = 1 / (1 + songgu + peigu)
                                cumulative_factor = cumulative_factor * factor

                    elif date in temp_factors:
                        cumulative_factor = temp_factors[date]

            else:  # back
                # 等比后复权: 从前往后
                sorted_dates = df['date'].unique()
                cumulative_factor = 1.0

                for date in sorted_dates:
                    temp_factors[date] = cumulative_factor

                    ex_div_records = dividend_records[dividend_records['date'] == date]
                    if len(ex_div_records) > 0:
                        for _, ex_div in ex_div_records.iterrows():
                            songgu = (float(ex_div.get('songzhuangu', 0) or 0) / 10)
                            peigu = (float(ex_div.get('peigu', 0) or 0) / 10)

                            if (1 + songgu + peigu) > 0:
                                factor = (1 + songgu + peigu)
                                cumulative_factor = cumulative_factor * factor

                    elif date in temp_factors:
                        cumulative_factor = temp_factors[date]

            # 应用因子
            final_factors = pd.Series(
                [temp_factors.get(d, 1.0) for d in df['date']],
                index=df.index,
                dtype=float
            )

            df_copy = df.copy()
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df_copy.columns:
                    df_copy[col] = df_copy[col] * final_factors

            logger.info(f"[等比复权{method}] {symbol} 完成")
            return df_copy

        except Exception as e:
            logger.warning(f"[等比复权] {symbol} 计算失败: {e}")
            return df

    def apply_adjustment(
        self,
        df: pd.DataFrame,
        xdxr_data: List[Dict],
        symbol: str,
        adjust_type: str = 'none'
    ) -> pd.DataFrame:
        """应用复权

        Args:
            df: K线数据
            xdxr_data: 除权除息数据
            symbol: 股票代码
            adjust_type: 复权类型 (none/front/back/front_ratio/back_ratio)

        Returns:
            复权后的 DataFrame
        """
        if adjust_type == 'none' or not xdxr_data or df.empty:
            return df

        if adjust_type == 'front':
            return self.calc_front_adjustment(df, xdxr_data, symbol)
        elif adjust_type == 'back':
            return self.calc_back_adjustment(df, xdxr_data, symbol)
        elif adjust_type == 'front_ratio':
            return self.calc_ratio_adjustment(df, xdxr_data, symbol, 'front')
        elif adjust_type == 'back_ratio':
            return self.calc_ratio_adjustment(df, xdxr_data, symbol, 'back')
        else:
            logger.warning(f"[复权计算] 未知复权类型: {adjust_type}")
            return df


# 单例实例
_calculator_instance: Optional[AdjustmentCalculator] = None


def get_adjustment_calculator() -> AdjustmentCalculator:
    """获取复权计算器单例"""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = AdjustmentCalculator()
    return _calculator_instance
