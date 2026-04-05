#!/usr/bin/env python3
"""检查 000858.SZ 5m 数据中的 March 16-19 缺口"""
import pandas as pd
from pathlib import Path
import struct
from datetime import datetime, timedelta

hotdb_path = Path('E:/MyQuant_v11/data/hotdata/000858_SZ/5m')
date_file = hotdb_path / 'date.5m.bin'

if date_file.exists():
    with open(date_file, 'rb') as f:
        data = f.read()
    count = struct.unpack('<i', data[:4])[0]
    print(f'Total bars: {count}')

    # Read all dates
    all_dates = []
    for i in range(count):
        date_int = struct.unpack('<i', data[4 + i*4:4 + (i+1)*4])[0]
        date_str = f'{date_int}'
        all_dates.append(date_int)

    # Get unique dates
    unique_dates = sorted(set(all_dates))
    print(f'Unique dates: {len(unique_dates)}')

    # Show first 10 and last 10 unique dates
    print('First 10 unique dates:', unique_dates[:10])
    print('Last 10 unique dates:', unique_dates[-10:])

    # Check for March 16-19, 2026
    target_dates = [20260316, 20260317, 20260318, 20260319]
    found_target_dates = [d for d in target_dates if d in all_dates]
    missing_target_dates = [d for d in target_dates if d not in all_dates]

    print(f'March 16-19 found: {found_target_dates}')
    print(f'March 16-19 missing: {missing_target_dates}')

    # Check daily bar counts for March 2026
    march_dates = [d for d in unique_dates if 20260301 <= d <= 20260331]
    print(f'\nMarch 2026 unique dates ({len(march_dates)}):')
    for d in march_dates:
        count_on_date = all_dates.count(d)
        print(f'  {d}: {count_on_date} bars (expected ~48 for 5m)')
else:
    print('Date file not found')
