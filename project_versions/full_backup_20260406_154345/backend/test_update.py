#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试智能更新修复"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend/src')

from myquant.core.market.services.hotdb_service import HotDBService
import inspect

# 检查_complete_from_online方法
method_source = inspect.getsource(HotDBService._complete_from_online)
if 'continue  # 继续尝试下一个数据源' in method_source:
    print('NEW CODE LOADED')
else:
    print('OLD CODE - exiting')
    sys.exit(1)

from myquant.core.market.services.hotdb_service import get_hotdb_service

service = get_hotdb_service()
print('Testing: 601939.SH 5m')
result = service.get_kline_with_auto_update('601939.SH', '5m', count=200)

if hasattr(result, 'df') and not result.df.empty:
    latest = result.df.iloc[-1]['datetime']
    count = len(result.df)
    print(f'Count: {count}, Latest: {latest}')
else:
    print('No data')
