# -*- coding: utf-8 -*-
"""
HotDB 污染数据清理工具

检测并清理 HotDB 中异常时间的 K 线数据
"""

import os
import struct
import shutil
from datetime import datetime, time
from pathlib import Path
from loguru import logger


class HotDBCleaner:
    """HotDB 数据清理工具"""

    def __init__(self, hotdb_path: str):
        self.hotdb_path = Path(hotdb_path)

    def is_valid_trading_time(self, hour: int, minute: int) -> bool:
        """检查是否是有效的交易时间"""
        # A股交易时间：9:30-11:30, 13:00-15:00
        if (hour == 9 and minute >= 30) or (10 <= hour < 12) or (hour == 11 and minute <= 30):
            return True
        if hour == 13 or hour == 14 or (hour == 15 and minute == 0):
            return True
        return False

    def check_minute_file(self, filepath: Path) -> dict:
        """
        检查分钟线文件中的污染数据

        Tdx 分钟线格式（每条记录 32 字节）：
        - 日期(4) + 时间(4) + 开(4) + 高(4) + 低(4) + 收(4) + 成交额(4) + 成交量(4)
        """
        result = {
            'total': 0,
            'abnormal': 0,
            'abnormal_list': []
        }

        try:
            with open(filepath, 'rb') as f:
                record_size = 32
                record_idx = 0

                while True:
                    data = f.read(record_size)
                    if len(data) < record_size:
                        break

                    # 解析日期和时间
                    date_int = struct.unpack('i', data[0:4])[0]
                    time_int = struct.unpack('i', data[4:8])[0]

                    if date_int <= 0:
                        continue

                    result['total'] += 1

                    # 解析时间 (格式: HHMM)
                    hour = time_int // 100
                    minute = time_int % 100

                    # 检查是否是有效交易时间
                    if not self.is_valid_trading_time(hour, minute):
                        result['abnormal'] += 1
                        result['abnormal_list'].append({
                            'index': record_idx,
                            'date': str(date_int),
                            'time': f'{hour:02d}:{minute:02d}'
                        })

                    record_idx += 1

        except Exception as e:
            logger.error(f"检查文件失败 {filepath}: {e}")

        return result

    def clean_minute_file(self, filepath: Path, backup: bool = True) -> bool:
        """清理分钟线文件中的污染数据"""
        # 备份原文件
        if backup:
            backup_path = filepath.with_suffix('.bak')
            shutil.copy2(filepath, backup_path)
            logger.info(f"已备份: {backup_path}")

        try:
            # 读取所有记录
            clean_records = []
            abnormal_count = 0

            with open(filepath, 'rb') as f:
                record_size = 32

                while True:
                    data = f.read(record_size)
                    if len(data) < record_size:
                        break

                    date_int = struct.unpack('i', data[0:4])[0]
                    time_int = struct.unpack('i', data[4:8])[0]

                    if date_int <= 0:
                        continue

                    hour = time_int // 100
                    minute = time_int % 100

                    # 只保留有效交易时间的记录
                    if self.is_valid_trading_time(hour, minute):
                        clean_records.append(data)
                    else:
                        abnormal_count += 1

            # 重写文件
            with open(filepath, 'wb') as f:
                for record in clean_records:
                    f.write(record)

            logger.info(f"清理完成: {filepath.name}, 原有 {len(clean_records) + abnormal_count} 条, 清理 {abnormal_count} 条, 保留 {len(clean_records)} 条")
            return True

        except Exception as e:
            logger.error(f"清理失败 {filepath}: {e}")
            # 恢复备份
            if backup and backup_path.exists():
                shutil.copy2(backup_path, filepath)
                logger.info(f"已恢复备份")
            return False

    def scan_all(self, period: str = 'min60') -> dict:
        """扫描所有股票的指定周期数据"""
        results = {}
        abnormal_files = []

        # 遍历 sz 和 sh 目录
        for market in ['sz', 'sh']:
            period_dir = self.hotdb_path / market / period
            if not period_dir.exists():
                continue

            for filepath in period_dir.glob('*'):
                if filepath.is_file():
                    result = self.check_minute_file(filepath)
                    if result['abnormal'] > 0:
                        abnormal_files.append({
                            'file': str(filepath),
                            'symbol': filepath.name,
                            'total': result['total'],
                            'abnormal': result['abnormal'],
                            'abnormal_list': result['abnormal_list'][:5]  # 只显示前5条
                        })

        return {
            'scanned_files': sum(1 for _ in Path(self.hotdb_path).glob(f'*/{period}/*')),
            'abnormal_files': abnormal_files
        }

    def clean_all(self, period: str = 'min60', backup: bool = True) -> dict:
        """清理所有股票的指定周期数据"""
        cleaned = 0
        failed = 0

        for market in ['sz', 'sh']:
            period_dir = self.hotdb_path / market / period
            if not period_dir.exists():
                continue

            for filepath in period_dir.glob('*'):
                if filepath.is_file():
                    # 先检查是否有污染
                    result = self.check_minute_file(filepath)
                    if result['abnormal'] > 0:
                        if self.clean_minute_file(filepath, backup):
                            cleaned += 1
                        else:
                            failed += 1

        return {'cleaned': cleaned, 'failed': failed}


def main():
    """主函数"""
    import sys

    hotdb_path = 'E:/MyQuant_v11/data/hotdata'
    cleaner = HotDBCleaner(hotdb_path)

    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        # 清理模式
        logger.info("开始清理 HotDB 污染数据...")
        result = cleaner.clean_all(period='min60', backup=True)
        logger.info(f"清理完成: 清理 {result['cleaned']} 个文件, 失败 {result['failed']} 个")
    else:
        # 扫描模式（默认）
        logger.info("扫描 HotDB 污染数据...")
        result = cleaner.scan_all(period='min60')

        logger.info(f"\n扫描结果:")
        logger.info(f"  扫描文件数: {result['scanned_files']}")
        logger.info(f"  发现污染文件: {len(result['abnormal_files'])}")

        if result['abnormal_files']:
            logger.info(f"\n污染文件详情:")
            for item in result['abnormal_files'][:10]:
                logger.info(f"  {item['symbol']}: 总计 {item['total']} 条, 污染 {item['abnormal']} 条")
                for abnormal in item['abnormal_list']:
                    logger.info(f"    - {abnormal['date']} {abnormal['time']}")

            logger.info(f"\n清理方法:")
            logger.info(f"  python backend/src/myquant/core/market/utils/hotdb_cleaner.py clean")
        else:
            logger.info("  未发现污染数据 ✅")


if __name__ == '__main__':
    main()
