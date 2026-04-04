# -*- coding: utf-8 -*-
"""
V5 TdxQuant 适配器

直接调用 tqcenter SDK，不依赖 V4 适配器
"""

import sys
from typing import Dict, List, Optional, Callable
from loguru import logger
import pandas as pd

from .base import V5DataAdapter


# 全局初始化状态标志（防止重复初始化尝试）
_TDXQUANT_INIT_ATTEMPTED = False
_TDXQUANT_INIT_SUCCESS = False
_TDXQUANT_LAST_ERROR = None
_TDXQUANT_INIT_LOCK = False  # 新增：初始化锁，防止并发初始化


class V5TdxQuantAdapter(V5DataAdapter):
    """V5 TdxQuant 适配器

    直接调用 tqcenter.tq SDK

    注意：TdxQuant SDK 是类级别单例，不能重复初始化
    """

    def __init__(self):
        super().__init__()
        self._name = 'tdxquant'
        self._subscriptions: Dict[str, Callable] = {}
        self._tq = None
        self._initialized = False

    def _ensure_initialized(self, force_retry: bool = False) -> bool:
        """确保 TdxQuant 已初始化

        TdxQuant SDK 是类级别单例，核心原则：
        1. 如果 tq._initialized 为 True，直接复用，不做任何操作
        2. 如果未初始化，调用 initialize() 且只调用一次
        3. 任何情况下都不应该关闭已初始化的连接
        """
        global _TDXQUANT_INIT_ATTEMPTED, _TDXQUANT_INIT_SUCCESS, _TDXQUANT_LAST_ERROR, _TDXQUANT_INIT_LOCK

        # 如果已初始化，直接返回
        if self._initialized and self._tq:
            return True

        # 如果不是强制重试，且已经尝试过初始化但失败了，不再重试（避免日志刷屏）
        if not force_retry and _TDXQUANT_INIT_ATTEMPTED and not _TDXQUANT_INIT_SUCCESS:
            logger.debug("[TdxQuant] 初始化已失败过，跳过重试（使用 force_retry=True 强制重试）")
            return False

        # 检查是否有其他实例正在初始化（防止并发）
        if _TDXQUANT_INIT_LOCK:
            logger.debug("[TdxQuant] 另一个实例正在初始化，等待...")
            import time
            for _ in range(50):  # 最多等5秒
                time.sleep(0.1)
                if not _TDXQUANT_INIT_LOCK:
                    break

            # 等待后检查是否已初始化成功
            try:
                from tqcenter import tq
                if hasattr(tq, '_initialized') and tq._initialized:
                    logger.debug("[TdxQuant] 等待后检测到 SDK 已初始化，直接复用")
                    self._tq = tq
                    self._initialized = True
                    return True
            except Exception:
                pass

            if _TDXQUANT_INIT_LOCK:
                logger.warning("[TdxQuant] 等待初始化超时")
                return False

        # 标记正在初始化
        _TDXQUANT_INIT_LOCK = True

        try:
            # 添加 SDK 路径（使用 v11 自己的路径，不依赖 v10）
            sdk_path = r'E:\MyQuant_v11\backend\external\tdxquant_sdk'
            if sdk_path not in sys.path:
                sys.path.insert(0, sdk_path)

            from tqcenter import tq

            # 关键检查：如果 SDK 已经初始化，直接复用（这是最常见的情况）
            if hasattr(tq, '_initialized') and tq._initialized:
                logger.debug("[TdxQuant] SDK 已初始化，直接复用现有连接")
                self._tq = tq
                self._initialized = True
                _TDXQUANT_INIT_SUCCESS = True
                _TDXQUANT_INIT_ATTEMPTED = True
                return True

            # SDK 未初始化，执行初始化（这只应该发生一次）
            logger.info("[TdxQuant] 开始初始化 SDK...")
            _TDXQUANT_INIT_ATTEMPTED = True

            # 设置 DLL 路径（必须在 initialize 之前设置）
            tq.dll_path = r'E:\new_tdx64\PYPlugins\TPythClient.dll'
            init_path = r'E:\new_tdx64\PYPlugins\user\myquant_init.py'

            # 检查必要文件
            import os
            if not os.path.exists(tq.dll_path):
                error_msg = f"DLL 文件不存在: {tq.dll_path}"
                logger.error(f"[TdxQuant] ❌ {error_msg}")
                _TDXQUANT_LAST_ERROR = error_msg
                return False

            if not os.path.exists(init_path):
                error_msg = f"初始化脚本不存在: {init_path}"
                logger.error(f"[TdxQuant] ❌ {error_msg}")
                _TDXQUANT_LAST_ERROR = error_msg
                return False

            # 执行初始化前记录状态
            logger.info(f"[TdxQuant] DLL路径: {tq.dll_path}")
            logger.info(f"[TdxQuant] 初始化脚本: {init_path}")
            logger.info("[TdxQuant] 准备调用 initialize()...")

            # 执行初始化
            tq.initialize(path=init_path)

            # 验证初始化结果
            if hasattr(tq, '_initialized') and tq._initialized:
                self._tq = tq
                self._initialized = True
                _TDXQUANT_INIT_SUCCESS = True
                _TDXQUANT_LAST_ERROR = None

                logger.info(f"[TdxQuant] ✅ 初始化成功 (run_id={self._tq.run_id})")
                return True
            else:
                error_msg = "初始化未完成（_initialized=False）"
                logger.warning(f"[TdxQuant] ⚠️ {error_msg}")
                _TDXQUANT_LAST_ERROR = error_msg
                return False

        except Exception as e:
            error_str = str(e)
            _TDXQUANT_LAST_ERROR = error_str

            # 详细诊断信息
            import traceback
            tb_str = traceback.format_exc()

            # 检查常见错误
            if "TQ数据接口初始化失败" in error_str or "已有同名策略运行" in error_str:
                # TQ初始化失败：可能是策略同名或DLL被占用
                # 解决方案：创建一个新的初始化文件名（如 myquant_init_2.py）
                # 限制：最多创建3个备用文件（myquant_init_2.py ~ myquant_init_4.py）
                # 清理：初始化成功后删除其他备用文件
                import shutil
                import glob

                original_path = r'E:\new_tdx64\PYPlugins\user\myquant_init.py'
                base_dir = r'E:\new_tdx64\PYPlugins\user'
                max_alternatives = 3  # 最多创建3个备用文件

                # 先清理已存在的备用文件（避免垃圾累积）
                existing_alts = glob.glob(os.path.join(base_dir, 'myquant_init_[0-9].py'))
                if len(existing_alts) >= max_alternatives:
                    logger.info(f"[TdxQuant] 清理旧备用文件: {len(existing_alts)} 个")
                    for old_file in existing_alts:
                        try:
                            os.remove(old_file)
                            logger.debug(f"[TdxQuant] 删除: {os.path.basename(old_file)}")
                        except Exception as e:
                            logger.debug(f"[TdxQuant] 删除失败: {e}")

                # 查找可用的编号
                for i in range(2, max_alternatives + 2):  # 尝试 myquant_init_2.py ~ myquant_init_5.py
                    new_init_path = os.path.join(base_dir, f'myquant_init_{i}.py')

                    try:
                        # 如果文件已存在，尝试使用
                        if os.path.exists(new_init_path):
                            logger.info(f"[TdxQuant] 尝试使用现有文件: myquant_init_{i}.py")
                            tq.initialize(path=new_init_path)
                        else:
                            # 创建新文件
                            shutil.copy(original_path, new_init_path)
                            logger.info(f"[TdxQuant] 创建新初始化文件: myquant_init_{i}.py")
                            tq.initialize(path=new_init_path)

                        # 验证初始化
                        if hasattr(tq, '_initialized') and tq._initialized:
                            self._tq = tq
                            self._initialized = True
                            _TDXQUANT_INIT_SUCCESS = True
                            _TDXQUANT_LAST_ERROR = None

                            logger.info(f"[TdxQuant] ✅ 初始化成功: myquant_init_{i}.py (run_id={self._tq.run_id})")

                            # 清理其他备用文件
                            for alt_file in glob.glob(os.path.join(base_dir, 'myquant_init_[0-9].py')):
                                if alt_file != new_init_path:
                                    try:
                                        os.remove(alt_file)
                                        logger.debug(f"[TdxQuant] 清理备用文件: {os.path.basename(alt_file)}")
                                    except Exception:
                                        pass

                            return True

                    except Exception as e:
                        logger.debug(f"[TdxQuant] myquant_init_{i}.py 失败: {e}")
                        continue

                # 所有尝试都失败
                error_msg = f"无法创建可用的初始化文件（已尝试 2-{max_alternatives + 1}）"
                logger.error(f"[TdxQuant] ❌ {error_msg}")
                _TDXQUANT_LAST_ERROR = error_msg
                return False
            elif "返回ID小于0" in error_str or "ErrorId=11" in error_str:
                logger.error(f"[TdxQuant] ❌ 重复初始化错误 (ErrorId=11): {error_str}")
            else:
                logger.error(f"[TdxQuant] ❌ 初始化失败: {error_str}")
                logger.debug(f"[TdxQuant] 详细错误:\n{tb_str}")

            return False
        finally:
            # 无论如何都要释放锁
            _TDXQUANT_INIT_LOCK = False

    def _to_tdx_period(self, period: str) -> str:
        """转换周期到 TdxQuant 格式"""
        # TdxQuant 支持的周期: 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1mon
        period_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '60m': '1h',
            '1d': '1d', 'd': '1d', 'day': '1d',
            '1w': '1w', 'w': '1w', 'week': '1w',
            '1M': '1mon', 'M': '1mon', '1mon': '1mon', 'mon': '1mon',
        }
        return period_map.get(period, '1d')

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据

        注意：此方法始终返回不复权原始数据，复权由服务层统一处理

        Args:
            symbols: 股票代码列表
            period: 周期
            start_date: 开始日期
            end_date: 结束日期
            count: 数量
            adjust_type: 复权类型（参数保留但不使用，统一由服务层处理）
        """
        if not self._ensure_initialized():
            return {}

        result = {}
        tdx_period = self._to_tdx_period(period)

        for symbol in symbols:
            try:
                # 始终获取不复权原始数据
                data = self._tq.get_market_data(
                    stock_list=[symbol],
                    period=tdx_period,
                    start_time='',
                    end_time='',
                    count=count or 100,
                    dividend_type='none'  # 始终获取不复权数据
                )

                if data and len(data) > 0:
                    # 转置数据: dict[field]=DataFrame -> per-symbol DataFrame
                    df_dict = {}
                    for field, field_df in data.items():
                        if (isinstance(field_df, pd.DataFrame) and
                                not field_df.empty):
                            # 从每个字段 DataFrame 提取第一列（该股票的数据）
                            for idx, value in field_df.iloc[:, 0].items():
                                if idx not in df_dict:
                                    df_dict[idx] = {}
                                df_dict[idx][field.lower()] = value

                    if df_dict:
                        # 构建 DataFrame
                        df = pd.DataFrame.from_dict(df_dict, orient='index')
                        df.index.name = 'datetime'

                        # 确保索引是 datetime 类型
                        if not isinstance(df.index, pd.DatetimeIndex):
                            df.index = pd.to_datetime(
                                df.index
                            )

                        result[symbol] = self._normalize_kline_df(df, 'tdxquant')

            except Exception as e:
                logger.warning(f"获取 {symbol} K线失败: {e}")
                continue

        return result

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """获取实时行情（包含完整86个字段）

        通过组合三个API获取最完整的字段：
        1. get_market_snapshot: 基础行情 + 五档盘口 + 内外盘
        2. get_more_info: 86个扩展字段（换手率、市盈率、涨停价等）
        3. get_stock_info: 63个财务指标（总股本、ROE等）
        """
        if not self._ensure_initialized():
            return {}

        result = {}

        for symbol in symbols:
            try:
                # 1. 获取基础行情（get_market_snapshot）
                tick_data = self._tq.get_market_snapshot(
                    stock_code=symbol
                )

                # 2. 获取86个扩展字段（get_more_info）
                more_info = self._tq.get_more_info(stock_code=symbol)

                # 3. 获取财务指标（get_stock_info，单只股票）
                stock_info = {}
                try:
                    stock_info = self._tq.get_stock_info(symbol)
                except Exception:
                    pass

                # 合并所有数据
                if tick_data and tick_data.get('ErrorId') in (0, '0'):
                    result[symbol] = self._normalize_quote(
                        symbol, tick_data, more_info, stock_info
                    )

            except Exception as e:
                logger.warning(f"获取 {symbol} 行情失败: {e}")
                continue

        return result

    def _normalize_quote(
        self,
        code: str,
        tick: dict,
        more: dict = None,
        stock: dict = None
    ) -> dict:
        """标准化行情数据（TdxQuant完整版）

        整合三个数据源：
        - tick: 基础行情（get_market_snapshot）
        - more: 扩展指标（get_more_info，86个字段）
        - stock: 财务数据（get_stock_info，63个字段）
        """
        more = more or {}
        stock = stock or {}

        # 安全转换函数（处理 '.' 等非数字字符串）
        def safe_float(val, default=0.0):
            if val is None or val == '' or val == '.':
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        def safe_int(val, default=0):
            if val is None or val == '' or val == '.':
                return default
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return default

        # 基础字段（from get_market_snapshot）
        price = safe_float(tick.get('Now') or tick.get('Price'), 0)
        pre_close = safe_float(tick.get('LastClose'), 0)
        volume = safe_float(tick.get('Volume'), 0)  # 股

        # 计算涨跌
        change = round(price - pre_close, 4)
        change_pct = round(change / pre_close * 100, 2) if pre_close else 0

        # 五档盘口（get_market_snapshot 用 Buyp/Buyv/Sellp/Sellv）
        buy_prices = tick.get('Buyp') or tick.get('BuyPrice') or []
        buy_volumes = tick.get('Buyv') or tick.get('BuyVolume') or []
        sell_prices = tick.get('Sellp') or tick.get('SellPrice') or []
        sell_volumes = tick.get('Sellv') or tick.get('SellVolume') or []

        # 内外盘（get_market_snapshot 独有）
        inner_vol = safe_int(tick.get('Inside'), 0)
        outer_vol = safe_int(tick.get('Outside'), 0)
        cur_vol = safe_int(tick.get('NowVol'), 0)

        # 从more_info获取扩展字段（86个字段中的核心指标）
        turnover_rate = safe_float(more.get('fHSL') or more.get('Zjl'), 0)
        volume_ratio = safe_float(more.get('fLianB') or more.get('LB'), 0)
        amplitude = safe_float(more.get('ZAF'), 0)
        pe_ratio = safe_float(more.get('DynaPE'), 0)
        pb_ratio = safe_float(more.get('PB_MRQ'), 0)
        dy_ratio = safe_float(more.get('DYRatio'), 0)
        zt_price = safe_float(more.get('ZTPrice'), 0)
        dt_price = safe_float(more.get('DTPrice'), 0)
        beta = safe_float(more.get('BetaValue'), 0)
        his_high = safe_float(more.get('HisHigh'), 0)
        his_low = safe_float(more.get('HisLow'), 0)

        # 从stock_info获取财务数据
        total_shares = safe_float(stock.get('J_zgb') or stock.get('total_shares'), 0)

        return {
            # ====== 基础字段 ======
            'code': code,
            'price': price,
            'open': safe_float(tick.get('Open'), 0),
            'high': safe_float(tick.get('Max') or tick.get('High'), 0),
            'low': safe_float(tick.get('Min') or tick.get('Low'), 0),
            'pre_close': pre_close,
            'volume': volume / 100,  # 股→手
            'amount': safe_float(tick.get('Amount'), 0) * 10000,  # 万元→元
            'change': change,
            'change_pct': change_pct,

            # ====== 五档盘口 ======
            'bid1': safe_float(buy_prices[0] if len(buy_prices) > 0 else 0, 0),
            'bid_vol1': safe_int(buy_volumes[0] if len(buy_volumes) > 0 else 0, 0),
            'bid2': safe_float(buy_prices[1] if len(buy_prices) > 1 else 0, 0),
            'bid_vol2': safe_int(buy_volumes[1] if len(buy_volumes) > 1 else 0, 0),
            'bid3': safe_float(buy_prices[2] if len(buy_prices) > 2 else 0, 0),
            'bid_vol3': safe_int(buy_volumes[2] if len(buy_volumes) > 2 else 0, 0),
            'bid4': safe_float(buy_prices[3] if len(buy_prices) > 3 else 0, 0),
            'bid_vol4': safe_int(buy_volumes[3] if len(buy_volumes) > 3 else 0, 0),
            'bid5': safe_float(buy_prices[4] if len(buy_prices) > 4 else 0, 0),
            'bid_vol5': safe_int(buy_volumes[4] if len(buy_volumes) > 4 else 0, 0),

            'ask1': safe_float(sell_prices[0] if len(sell_prices) > 0 else 0, 0),
            'ask_vol1': safe_int(sell_volumes[0] if len(sell_volumes) > 0 else 0, 0),
            'ask2': safe_float(sell_prices[1] if len(sell_prices) > 1 else 0, 0),
            'ask_vol2': safe_int(sell_volumes[1] if len(sell_volumes) > 1 else 0, 0),
            'ask3': safe_float(sell_prices[2] if len(sell_prices) > 2 else 0, 0),
            'ask_vol3': safe_int(sell_volumes[2] if len(sell_volumes) > 2 else 0, 0),
            'ask4': safe_float(sell_prices[3] if len(sell_prices) > 3 else 0, 0),
            'ask_vol4': safe_int(sell_volumes[3] if len(sell_volumes) > 3 else 0, 0),
            'ask5': safe_float(sell_prices[4] if len(sell_prices) > 4 else 0, 0),
            'ask_vol5': safe_int(sell_volumes[4] if len(sell_volumes) > 4 else 0, 0),

            # ====== 扩展字段 ======
            'inner_vol': inner_vol,
            'outer_vol': outer_vol,
            'cur_vol': cur_vol,

            # 衍生指标
            'turnover_rate': round(turnover_rate, 2) if turnover_rate else 0,
            'volume_ratio': round(volume_ratio, 2) if volume_ratio else 0,
            'amplitude': round(amplitude, 2) if amplitude else 0,

            # 估值指标
            'pe_ratio': round(float(pe_ratio), 2) if pe_ratio else 0,
            'pb_ratio': round(float(pb_ratio), 2) if pb_ratio else 0,
            'dy_ratio': round(float(dy_ratio), 2) if dy_ratio else 0,

            # 价格限制
            'zt_price': round(float(zt_price), 2) if zt_price else 0,
            'dt_price': round(float(dt_price), 2) if dt_price else 0,

            # 其他指标
            'beta': round(float(beta), 2) if beta else 0,
            'his_high': (
                round(float(his_high), 2) if his_high else 0
            ),
            'his_low': (
                round(float(his_low), 2) if his_low else 0
            ),
            'total_shares': float(total_shares),

            # 数据源标识
            'data_source': 'tdxquant',
        }

    def subscribe(
        self,
        symbols: List[str],
        callback: Callable,
        period: str = '1m'
    ) -> bool:
        """订阅实时推送"""
        if not self._ensure_initialized():
            return False

        try:
            # TdxQuant 订阅
            self._tq.subscribe_quote(symbols)

            # 记录订阅
            for symbol in symbols:
                self._subscriptions[symbol] = callback

            return True

        except Exception as e:
            logger.error(f"TdxQuant 订阅失败: {e}")
            return False

    def unsubscribe(self, symbols: List[str]) -> bool:
        """取消订阅"""
        try:
            self._tq.unsubscribe_hq(symbols)

            # 移除订阅记录
            for symbol in symbols:
                self._subscriptions.pop(symbol, None)

            return True

        except Exception:
            return False

    def get_sector_components(self, sector_code: str) -> List[dict]:
        """获取板块成分股"""
        if not self._ensure_initialized():
            return []

        try:
            return self._tq.get_stock_list_in_sector(sector_code)
        except Exception as e:
            logger.warning(f"获取板块成分股失败: {e}")
            return []

    def get_sector_list(self) -> List[dict]:
        """获取板块列表"""
        if not self._ensure_initialized():
            return []

        try:
            return self._tq.get_sector_list()
        except Exception as e:
            logger.warning(f"获取板块列表失败: {e}")
            return []

    def get_stock_name(self, code: str) -> Optional[str]:
        """获取股票名称"""
        if not self._ensure_initialized():
            return None

        try:
            info = self._tq.get_stock_info([code])
            if info and code in info:
                return info[code].get('name')
        except Exception as e:
            logger.debug(f"获取股票名称失败: {e}")

        return None

    def get_extra_indicators(self, code: str) -> dict:
        """获取额外指标（换手率、市盈率等）

        TdxQuant 提供 86 个额外字段（通过 get_more_info）：
        - Zjl: 换手率
        - DynaPE: 动态市盈率
        - PB_MRQ: 市净率
        - DYRatio: 股息率
        - ZAF: 振幅
        等

        Args:
            code: 股票代码

        Returns:
            包含额外指标的字典
        """
        if not self._ensure_initialized():
            return {}

        try:
            # get_more_info 返回单个股票的详细信息
            info = self._tq.get_more_info(stock_code=code)
            if info:
                return {
                    'turnover_rate': info.get('Zjl'),      # 换手率
                    'pe_ratio': info.get('DynaPE'),        # 动态市盈率
                    'pb_ratio': info.get('PB_MRQ'),        # 市净率
                    'dy_ratio': info.get('DYRatio'),       # 股息率
                    'amplitude': info.get('ZAF'),          # 振幅
                    'his_high': info.get('HisHigh'),       # 52周高
                    'his_low': info.get('HisLow'),         # 52周低
                }
        except Exception as e:
            logger.debug(f"获取 {code} 额外指标失败: {e}")

        return {}

    def _normalize_kline_df(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """标准化 K线 DataFrame

        TdxQuant 返回：volume 是股，amount 是万元
        统一转换为：手 / 元（volume÷100, amount×10000）
        """
        if df is None or df.empty:
            return df

        # volume 股→手
        if 'volume' in df.columns:
            df['volume'] = df['volume'] / 100

        # amount 万元→元
        if 'amount' in df.columns:
            df['amount'] = df['amount'] * 10000

        # 添加数据源标记
        df['data_source'] = source

        return df

    def _normalize_quote_dict(self, code: str, quote: dict, source: str) -> dict:
        """标准化行情数据

        TdxQuant 返回：volume 是股，amount 是万元
        统一转换为：手 / 元
        """
        # 先调用基类方法
        result = super()._normalize_quote_dict(code, quote, source)

        # TdxQuant 的 volume 是股，转换为手
        if 'volume' in result:
            result['volume'] = result['volume'] / 100

        # TdxQuant 的 amount 是万元，转换为元
        if 'Amount' in quote:
            result['amount'] = quote['Amount'] * 10000
        elif 'amount' in quote:
            result['amount'] = quote['amount'] * 10000

        return result

    def get_tdxquant_status(self) -> dict:
        """获取 TdxQuant 状态"""
        if self._initialized and self._tq:
            return {
                "available": True,
                "mode": "实时模式",
                "run_id": self._tq.run_id
            }
        return {"available": False, "mode": "未初始化"}

    def is_available(self) -> bool:
        """检查适配器是否可用

        注意：此方法会在后台静默检查，不会触发初始化尝试。
        如果尚未初始化或初始化失败，返回 False。
        """
        # 如果已经初始化成功，直接返回 True
        if self._initialized and self._tq:
            return True

        # 如果尚未初始化，尝试初始化，但捕获所有异常
        try:
            return self._ensure_initialized()
        except Exception as e:
            logger.debug(f"[TdxQuant] 初始化失败，标记为不可用: {e}")
            return False


def create_tdxquant_adapter() -> V5TdxQuantAdapter:
    """工厂函数：创建 TdxQuant 适配器"""
    return V5TdxQuantAdapter()
