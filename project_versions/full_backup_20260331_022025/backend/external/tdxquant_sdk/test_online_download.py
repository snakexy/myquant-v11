# -*- coding: utf-8 -*-
"""
TdxQuant 在线下载功能验证测试
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# 添加适配器路径
adapter_dir = Path(__file__).parent
sys.path.insert(0, str(adapter_dir))

from tqcenter import tq


def check_tdx_running():
    """检查通达信是否运行"""
    try:
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq tdxw.exe'],
                              capture_output=True, text=True)
        if 'tdxw.exe' in result.stdout:
            return True, 'tdxw.exe'
    except:
        pass
    return False, None


def get_local_file_mtime(stock_code):
    """检查通达信本地文件的修改时间"""
    result = {}
    if stock_code.endswith('.SH'):
        market = 'sh'
        code = stock_code.replace('.SH', '')
    elif stock_code.endswith('.SZ'):
        market = 'sz'
        code = stock_code.replace('.SZ', '')
    else:
        return result

    tdx_base = Path(r'E:\new_tdx64')
    if not tdx_base.exists():
        return result

    vipdoc_path = tdx_base / 'vipdoc' / market.upper() / 'minline' / f'{code}.day'
    if vipdoc_path.exists():
        result[str(vipdoc_path)] = vipdoc_path.stat().st_mtime

    return result


def main():
    print("=" * 60)
    print("TdxQuant 在线下载功能验证测试")
    print("=" * 60)

    # 1. 检查通达信
    print("\n[步骤1] 检查通达信状态...")
    running, proc_name = check_tdx_running()
    if running:
        print(f"[OK] 通达信运行中: {proc_name}")
    else:
        print("[WARN] 通达信未运行")

    # 2. 初始化
    print("\n[步骤2] 初始化TdxQuant...")
    try:
        tq_path = r'E:\new_tdx64\PYPlugins\user\script.py'
        dll_path = r'E:\new_tdx64\PYPlugins\TPythClient.dll'
        tq.initialize(path=tq_path, dll_path=dll_path)
        print("[OK] TdxQuant 初始化成功")
    except Exception as e:
        print(f"[FAIL] 初始化失败: {e}")
        return

    # 3. 测试股票
    test_stock = '600519.SH'
    print(f"\n[步骤3] 测试股票: {test_stock}")

    # 4. 获取初始数据
    print("\n[步骤4] 获取初始K线数据...")
    try:
        initial_data = tq.get_market_data(
            stock_list=[test_stock],
            period='1d',
            count=10
        )

        if 'Close' in initial_data and test_stock in initial_data['Close'].columns:
            close_data = initial_data['Close'][test_stock]
            initial_count = len(close_data)
            initial_dates = list(close_data.index)
            latest_date = initial_dates[-1] if initial_dates else None
            print(f"[OK] 初始: {initial_count}根, 最新: {latest_date}")
        else:
            print("[FAIL] 未获取到数据")
            return
    except Exception as e:
        print(f"[FAIL] 获取数据失败: {e}")
        return

    # 5. 记录本地文件时间
    print("\n[步骤5] 记录本地文件时间...")
    initial_files = get_local_file_mtime(test_stock)
    if initial_files:
        for fp, mtime in initial_files.items():
            mtime_str = datetime.fromtimestamp(mtime).strftime('%H:%M:%S')
            print(f"  {Path(fp).name}: {mtime_str}")

    # 6. 调用刷新
    print("\n[步骤6] 调用 refresh_kline()...")
    time.sleep(2)
    try:
        refresh_result = tq.refresh_kline(stock_list=[test_stock], period='1d')
        print("[OK] 刷新调用完成")
        if refresh_result:
            try:
                result_json = json.loads(refresh_result)
                error_id = result_json.get('ErrorId', '')
                error_msg = result_json.get('Error', '')
                print(f"  ErrorId: {error_id}, Error: {error_msg}")
            except:
                print(f"  返回: {refresh_result}")
    except Exception as e:
        print(f"[FAIL] 刷新失败: {e}")
        return

    # 7. 等待
    print("\n[步骤7] 等待下载... (5秒)")
    time.sleep(5)

    # 8. 再次获取数据
    print("\n[步骤8] 再次获取数据对比...")
    try:
        after_data = tq.get_market_data(
            stock_list=[test_stock],
            period='1d',
            count=10
        )

        if 'Close' in after_data and test_stock in after_data['Close'].columns:
            close_data = after_data['Close'][test_stock]
            after_count = len(close_data)
            after_dates = list(close_data.index)
            after_latest = after_dates[-1] if after_dates else None

            print(f"[OK] 刷新后: {after_count}根, 最新: {after_latest}")

            # 对比
            changed = False
            if after_count > initial_count:
                print(f"[CHANGE] 数据增加: +{after_count - initial_count}根")
                changed = True
            elif after_latest and latest_date and after_latest > latest_date:
                print(f"[CHANGE] 日期更新: {latest_date} -> {after_latest}")
                changed = True
            else:
                print("[NO CHANGE] 数据无变化")
        else:
            print("[FAIL] 刷新后未获取到数据")
    except Exception as e:
        print(f"[FAIL] 获取刷新后数据失败: {e}")

    # 9. 检查本地文件变化
    print("\n[步骤9] 检查本地文件变化...")
    after_files = get_local_file_mtime(test_stock)
    for fp, after_mtime in after_files.items():
        if fp in initial_files:
            initial_mtime = initial_files[fp]
            if after_mtime > initial_mtime:
                diff = after_mtime - initial_mtime
                print(f"[CHANGE] 文件已更新 (+{diff:.1f}秒)")
            else:
                print(f"[NO CHANGE] 文件无变化")

    # 10. 结论
    print("\n" + "=" * 60)
    print("结论")
    print("=" * 60)

    file_changed = any(
        after_mtime > initial_files.get(fp, 0)
        for fp, after_mtime in after_files.items()
    )

    if file_changed:
        print("[SUCCESS] refresh_kline() 触发了本地文件更新!")
        print("  TdxQuant 可以触发通达信在线更新数据")
    elif changed:
        print("[SUCCESS] 数据有更新")
        print("  TdxQuant 获取到了更新的数据")
    else:
        print("[NO CHANGE] 数据无变化")
        print("  可能原因:")
        print("  1. 通达信未在线")
        print("  2. 当前已是最新数据")

    tq.close()


if __name__ == '__main__':
    main()
