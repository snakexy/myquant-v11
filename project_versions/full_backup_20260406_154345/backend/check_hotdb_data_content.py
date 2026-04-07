"""
检查 HotDB 数据内容
"""
import struct
import os
from pathlib import Path
from datetime import datetime

def read_dates(filepath):
    """读取日期文件"""
    dates = []
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(4)
            if not data:
                break
            # 4字节整数 YYYYMMDD
            date_int = struct.unpack('<i', data)[0]
            if date_int == 0:
                continue
            # 转换为日期字符串
            date_str = str(date_int)
            if len(date_str) == 8:
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                dates.append((year, month, day))
    return dates

def main():
    hotdata_dir = Path("E:/MyQuant_v11/data/hotdata")

    # 检查 sh600536 的日线数据
    symbol_dir = hotdata_dir / "sh/day/sh600536"
    if symbol_dir.exists():
        date_file = symbol_dir / "date.day.bin"
        close_file = symbol_dir / "close.day.bin"

        if date_file.exists():
            dates = read_dates(date_file)
            print(f"sh600536 日线数据: {len(dates)} 条")
            if dates:
                print(f"  最早: {dates[0][0]}-{dates[0][1]:02d}-{dates[0][2]:02d}")
                print(f"  最新: {dates[-1][0]}-{dates[-1][1]:02d}-{dates[-1][2]:02d}")

                # 检查是否有2025年4月之前的数据
                cutoff = (2025, 4, 1)
                old_data = [d for d in dates if d < cutoff]
                print(f"  2025年4月之前: {len(old_data)} 条")
    else:
        print("sh600536 数据不存在")

    # 检查 sh600519 (茅台)
    symbol_dir = hotdata_dir / "sh/day/sh600519"
    if symbol_dir.exists():
        print("\nsh600519 数据存在")
    else:
        print("\nsh600519 数据不存在 (需要预热)")

if __name__ == "__main__":
    main()
