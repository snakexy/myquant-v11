# -*- coding: utf-8 -*-
"""
LocalDB → HotDB 复制与聚合测试

不启动后端服务，直接测试数据流转逻辑：
1. 检查 LocalDB 数据
2. 读取 LocalDB 数据（1d, 5m）
3. 聚合 5m → 15m/30m/1h（含速度测试）
4. 保存到 HotDB 格式
"""

import sys
from pathlib import Path
import time
import struct

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import pandas as pd
import numpy as np
from loguru import logger


class LocalDBToHotDBTester:
    """LocalDB → HotDB 测试工具"""

    def __init__(self):
        self.localdb_dir = Path("E:/MyQuant_v11/data/qlib_data/stock")
        self.hotdb_dir = Path("E:/MyQuant_v11/data/hotdata")
        self.hotdb_dir.mkdir(parents=True, exist_ok=True)

    def read_bin_file(self, filepath: Path) -> list:
        """读取 bin 文件"""
        if not filepath.exists():
            return []

        with open(filepath, 'rb') as f:
            if 'float' in str(filepath):
                data = np.frombuffer(f.read(), dtype=np.float32)
            else:
                data = np.frombuffer(f.read(), dtype=np.int32)
        return data.tolist()

    def check_localdb_data(self, symbol: str, exchange: str = "sh") -> dict:
        """检查 LocalDB 数据

        Returns:
            数据状态字典
        """
        result = {
            "symbol": symbol,
            "exchange": exchange,
            "1d": {"exists": False, "count": 0},
            "5m": {"exists": False, "count": 0},
        }

        # 检查日线 (qlib_data/{exchange}/day/{symbol}/)
        day_dir = self.localdb_dir / exchange / "day" / symbol
        if day_dir.exists():
            day_file = day_dir / "date.day.bin"
            if day_file.exists():
                dates = self.read_bin_file(day_file)
                result["1d"]["exists"] = True
                result["1d"]["count"] = len(dates)
                logger.info(f"[LocalDB] {symbol} 日线: {len(dates)} 条")

        # 检查5分钟线 (qlib_data/{exchange}/min5/{symbol}/)
        min5_dir = self.localdb_dir / exchange / "min5" / symbol
        if min5_dir.exists():
            min5_file = min5_dir / "date.min5.bin"
            if min5_file.exists():
                dates = self.read_bin_file(min5_file)
                result["5m"]["exists"] = True
                result["5m"]["count"] = len(dates)
                logger.info(f"[LocalDB] {symbol} 5分钟: {len(dates)} 条")

        result["exists"] = result["1d"]["exists"] or result["5m"]["exists"]
        return result

    def read_localdb_kline(
        self, symbol: str, period: str, exchange: str = "sh",
        limit: int = 100
    ) -> pd.DataFrame:
        """读取 LocalDB K线数据

        Args:
            symbol: 股票代码（QLib格式：sh600000）
            period: 周期 (1d/5m)
            exchange: 交易所 (sh/sz)
            limit: 读取条数

        Returns:
            DataFrame with columns: datetime, open, high, low, close, volume
        """
        # 日线在 day 目录，分钟线在 min5 目录
        if period == "1d":
            data_dir = self.localdb_dir / exchange / "day" / symbol
            suffix = "day"
        else:  # 5m
            data_dir = self.localdb_dir / exchange / "min5" / symbol
            suffix = "min5"

        # 读取文件
        date_file = data_dir / f"date.{suffix}.bin"
        open_file = data_dir / f"open.{suffix}.bin"
        high_file = data_dir / f"high.{suffix}.bin"
        low_file = data_dir / f"low.{suffix}.bin"
        close_file = data_dir / f"close.{suffix}.bin"
        vol_file = data_dir / f"volume.{suffix}.bin"
        amount_file = data_dir / f"amount.{suffix}.bin"

        if not date_file.exists():
            logger.warning(f"[LocalDB] {symbol} {period} 数据不存在")
            return pd.DataFrame()

        dates = self.read_bin_file(date_file)[-limit:]
        opens = self.read_bin_file(open_file)[-limit:]
        highs = self.read_bin_file(high_file)[-limit:]
        lows = self.read_bin_file(low_file)[-limit:]
        closes = self.read_bin_file(close_file)[-limit:]
        volumes = self.read_bin_file(vol_file)[-limit:]

        if amount_file.exists():
            amounts_list = self.read_bin_file(amount_file)[-limit:]
            amounts = [float(x) if x != 0 else 0.0 for x in amounts_list]
        else:
            amounts = [0.0] * len(dates)

        # 确保 dates 也是列表
        if not isinstance(dates, list):
            dates = list(dates)
        if not isinstance(opens, list):
            opens = list(opens)
        if not isinstance(highs, list):
            highs = list(highs)
        if not isinstance(lows, list):
            lows = list(lows)
        if not isinstance(closes, list):
            closes = list(closes)
        if not isinstance(volumes, list):
            volumes = list(volumes)

        # 构造 DataFrame
        df = pd.DataFrame({
            "datetime": pd.to_datetime([str(d) for d in dates], format="%Y%m%d"),
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
            "amount": amounts
        })

        logger.info(f"[LocalDB] 读取 {symbol} {period}: {len(df)} 条")
        return df

    def aggregate_5m_to_period(
        self, df_5m: pd.DataFrame, target_period: str
    ) -> pd.DataFrame:
        """将5分钟数据聚合到目标周期（含速度测试）

        Args:
            df_5m: 5分钟K线数据
            target_period: 目标周期 (15m/30m/1h)

        Returns:
            聚合后的K线数据
        """
        if df_5m.empty:
            return pd.DataFrame()

        # 计算聚合倍数
        mapping = {"15m": 3, "30m": 6, "1h": 12}
        n = mapping.get(target_period)

        if n is None:
            logger.error(f"[聚合] 不支持的周期: {target_period}")
            return pd.DataFrame()

        # 测试聚合速度
        start_time = time.time()

        # 确保时间戳是索引且已排序
        df = df_5m.copy().reset_index(drop=True)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime").reset_index(drop=True)

        # 创建周期分组键（每 n 根K线一组）
        group_keys = (df.index // n)

        # 聚合
        agg_df = df.groupby(group_keys).agg({
            "datetime": "first",
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "amount": "sum"
        }).reset_index(drop=True)

        elapsed = (time.time() - start_time) * 1000  # 转换为毫秒

        logger.info(
            f"[聚合] 5m → {target_period}: "
            f"{len(df_5m)} 根 → {len(agg_df)} 根 "
            f"(耗时: {elapsed:.2f}ms)"
        )

        return agg_df

    def save_to_hotdb_format(
        self, df: pd.DataFrame, symbol: str, period: str
    ) -> bool:
        """保存到 HotDB 格式

        Args:
            df: K线数据
            symbol: 股票代码
            period: 周期

        Returns:
            是否成功
        """
        if df.empty:
            logger.warning(f"[HotDB] 数据为空，跳过保存")
            return False

        try:
            # 创建股票目录
            stock_dir = self.hotdb_dir / symbol
            stock_dir.mkdir(parents=True, exist_ok=True)

            # 周期后缀
            suffix_map = {
                "1d": "day", "1w": "week", "1mon": "mon",
                "1m": "1m", "5m": "5m", "15m": "15m",
                "30m": "30m", "1h": "60m"
            }
            suffix = suffix_map.get(period, period)

            # 转换数据
            dates = df["datetime"].dt.strftime("%Y%m%d").astype(int).tolist()
            opens = df["open"].astype(float).tolist()
            highs = df["high"].astype(float).tolist()
            lows = df["low"].astype(float).tolist()
            closes = df["close"].astype(float).tolist()
            volumes = df["volume"].astype(float).tolist()

            if "amount" in df.columns:
                amounts = df["amount"].astype(float).tolist()
            else:
                amounts = [0.0] * len(dates)

            # 写入 bin 文件（格式：int32 count + 数据数组）
            def write_bin(filepath, data, dtype):
                with open(filepath, 'wb') as f:
                    # 先写入 count（int32）
                    f.write(struct.pack('<i', len(data)))
                    # 再写入数据数组
                    if dtype == 'int':
                        f.write(np.array(data, dtype=np.int32).tobytes())
                    else:
                        f.write(np.array(data, dtype=np.float32).tobytes())

            write_bin(stock_dir / f"date.{suffix}.bin", dates, 'int')
            write_bin(stock_dir / f"open.{suffix}.bin", opens, 'float')
            write_bin(stock_dir / f"high.{suffix}.bin", highs, 'float')
            write_bin(stock_dir / f"low.{suffix}.bin", lows, 'float')
            write_bin(stock_dir / f"close.{suffix}.bin", closes, 'float')
            write_bin(stock_dir / f"volume.{suffix}.bin", volumes, 'float')
            write_bin(stock_dir / f"amount.{suffix}.bin", amounts, 'float')

            logger.info(f"[HotDB] 保存 {symbol} {period}: {len(df)} 条")
            return True

        except Exception as e:
            logger.error(f"[HotDB] 保存失败: {e}")
            return False

    def test_copy_and_aggregate(
        self, symbol: str = "sh600000", exchange: str = "sh"
    ) -> dict:
        """测试完整的复制和聚合流程

        Args:
            symbol: 股票代码（QLib格式：sh600000）
            exchange: 交易所

        Returns:
            测试结果
        """
        logger.info("=" * 60)
        logger.info(f"开始测试: {symbol}")
        logger.info("=" * 60)

        results = {
            "symbol": symbol,
            "steps": []
        }

        # 步骤1：检查 LocalDB 数据
        logger.info("")
        logger.info("[步骤1] 检查 LocalDB 数据")
        localdb_status = self.check_localdb_data(symbol, exchange)
        results["steps"].append({
            "step": "检查 LocalDB",
            "result": localdb_status
        })

        if not localdb_status["1d"]["exists"] \
                and not localdb_status["5m"]["exists"]:
            logger.warning(f"LocalDB 中 {symbol} 没有数据，测试终止")
            results["success"] = False
            results["error"] = "LocalDB 无数据"
            return results

        # 步骤2：读取 1d 数据并保存到 HotDB
        if localdb_status["1d"]["exists"]:
            logger.info("")
            logger.info("[步骤2] 读取 1d 数据 → HotDB")
            df_1d = self.read_localdb_kline(symbol, "1d", exchange, limit=100)
            if not df_1d.empty:
                success = self.save_to_hotdb_format(df_1d, symbol, "1d")
                results["steps"].append({
                    "step": "1d → HotDB",
                    "success": success,
                    "count": len(df_1d)
                })

        # 步骤3：读取 5m 数据
        if not localdb_status["5m"]["exists"]:
            logger.warning(f"LocalDB 中 {symbol} 没有 5m 数据，跳过聚合测试")
            results["success"] = True
            return results

        logger.info("")
        logger.info("[步骤3] 读取 5m 数据")
        df_5m = self.read_localdb_kline(symbol, "5m", exchange, limit=500)

        if df_5m.empty:
            logger.warning(f"5m 数据为空，跳过聚合测试")
            results["success"] = True
            return results

        # 步骤4：保存 5m 到 HotDB
        logger.info("")
        logger.info("[步骤4] 保存 5m → HotDB")
        success_5m = self.save_to_hotdb_format(df_5m, symbol, "5m")
        results["steps"].append({
            "step": "5m → HotDB",
            "success": success_5m,
            "count": len(df_5m)
        })

        # 步骤5：聚合到 15m/30m/1h（含速度测试）
        for target_period in ["15m", "30m", "1h"]:
            logger.info("")
            logger.info(f"[步骤5.{target_period}] 聚合 5m → {target_period}")
            df_agg = self.aggregate_5m_to_period(df_5m, target_period)

            if not df_agg.empty:
                success_agg = self.save_to_hotdb_format(
                    df_agg, symbol, target_period
                )
                results["steps"].append({
                    "step": f"5m → {target_period}",
                    "success": success_agg,
                    "count": len(df_agg)
                })

        logger.info("")
        logger.info("=" * 60)
        logger.info("测试完成!")
        logger.info("=" * 60)

        results["success"] = True
        return results


def main():
    """主测试函数"""
    tester = LocalDBToHotDBTester()

    # 测试列表（使用 QLib 格式的股票代码）
    test_symbols = [
        ("sh600000", "sh"),  # 浦发银行
        ("sz000001", "sz"),  # 平安银行
        ("sh601628", "sh"),  # 中国人寿
    ]

    all_results = []
    perf_stats = []

    for symbol, exchange in test_symbols:
        try:
            result = tester.test_copy_and_aggregate(symbol, exchange)
            all_results.append(result)
        except Exception as e:
            logger.error(f"测试 {symbol} 失败: {e}")
            all_results.append({
                "symbol": symbol,
                "success": False,
                "error": str(e)
            })

    # 汇总结果
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试汇总")
    logger.info("=" * 60)

    for r in all_results:
        status = "成功" if r.get("success") else "失败"
        logger.info(f"{r['symbol']}: {status}")
        if "error" in r:
            logger.info(f"  错误: {r['error']}")

    # 统计
    success_count = sum(1 for r in all_results if r.get("success"))
    logger.info("")
    logger.info(f"总计: {success_count}/{len(all_results)} 成功")

    # 检查 HotDB 目录
    logger.info("")
    logger.info(f"HotDB 数据目录: {tester.hotdb_dir}")
    if tester.hotdb_dir.exists():
        stock_count = len(list(tester.hotdb_dir.iterdir()))
        logger.info(f"已创建 {stock_count} 只股票的 HotDB 数据")

    # 验证读取：测试第一只股票的 1d 数据是否能被正确读取
    logger.info("")
    logger.info("=" * 60)
    logger.info("验证读取：测试 HotDB 适配器能否正确读取")
    logger.info("=" * 60)

    try:
        # 导入 HotDB 适配器
        from myquant.core.market.adapters import get_adapter

        hotdb = get_adapter('hotdb')
        if hotdb and hotdb.is_available():
            # 读取第一只测试股票的 1d 数据
            test_symbol = test_symbols[0][0].replace('sh', '.SH').replace('sz', '.SZ')
            results = hotdb.get_kline(symbols=[test_symbol], period='1d', count=10)

            if test_symbol in results and not results[test_symbol].empty:
                df = results[test_symbol]
                logger.info(f"[验证] 成功读取 {test_symbol} 1d: {len(df)} 条")
                logger.info(f"[验证] 数据预览: {df.head(2).to_dict('records')}")
            else:
                logger.warning(f"[验证] 读取 {test_symbol} 1d 失败或无数据")
        else:
            logger.warning("[验证] HotDB 适配器不可用")
    except Exception as e:
        logger.warning(f"[验证] 读取测试失败: {e}")


if __name__ == "__main__":
    main()
