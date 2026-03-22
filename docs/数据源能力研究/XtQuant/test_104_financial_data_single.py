# -*- coding: utf-8 -*-
"""
测试财务数据获取能力（单股）

目的:
1. 验证get_financial_data()是否可用
2. 查看能获取哪些财务报表
3. 检查返回的数据字段
4. 验证是否需要VIP权限
"""

from xtquant import xtdata
import pandas as pd

def test_financial_data():
    """测试单个股票的财务数据获取"""

    print("=" * 80)
    print("测试: 财务数据获取（单股）")
    print("=" * 80)
    print()

    # 测试股票：贵州茅台
    symbol = '600519.SH'

    print(f"[测试股票] {symbol} (贵州茅台)")
    print()

    # ========== 测试1: 尝试获取财务数据 ==========
    print("[测试1] 尝试获取财务数据")
    print("-" * 80)

    try:
        # 尝试获取财务数据
        data = xtdata.get_financial_data(
            stock_list=[symbol],
            table_list=['Balance'],  # 资产负债表
            start_time='20240101',
            end_time='20241231',
            report_type='report_time'  # 按报告期筛选
        )

        if data:
            print("[OK] 成功获取财务数据")
            print()

            # 返回格式: {field, date, stock, value}
            print(f"[数据结构]")
            print(f"  - field (字段): {len(data.get('field', []))} 个")
            print(f"  - date (日期): {len(data.get('date', []))} 个")
            print(f"  - stock (股票): {len(data.get('stock', []))} 个")
            print(f"  - value (值): {len(data.get('value', []))} 行 x {len(data.get('value', [])) if isinstance(data.get('value', []), list) and len(data.get('value', [])) > 0 else 0} 列")
            print()

            # 显示字段列表（前20个）
            if 'field' in data and len(data['field']) > 0:
                print(f"[财务字段] (共{len(data['field'])}个，显示前20个)")
                for i, field in enumerate(data['field'][:20], 1):
                    print(f"  {i:2d}. {field}")
                print()

            # 显示报告期
            if 'date' in data and len(data['date']) > 0:
                print(f"[报告期] (共{len(data['date'])}个)")
                for date in data['date'][:10]:
                    print(f"  - {date}")
                print()

        else:
            print("[ERROR] 未获取到数据")
            print("  可能原因:")
            print("  1. 需要VIP权限")
            print("  2. API不可用")
            print("  3. 参数错误")
            print()

    except Exception as e:
        print(f"[ERROR] 获取失败: {e}")
        import traceback
        traceback.print_exc()
        print()

    # ========== 测试2: 尝试不同的报表类型 ==========
    print("[测试2] 尝试不同的财务报表")
    print("-" * 80)

    tables = {
        'Balance': '资产负债表',
        'Profit': '利润表',
        'CashFlow': '现金流量表',
        'Top10FlowHolder': '十大流通股东',
        'Top10Holder': '十大股东'
    }

    for table_name, table_desc in tables.items():
        try:
            print(f"[尝试] {table_desc} ({table_name})")

            data = xtdata.get_financial_data(
                stock_list=[symbol],
                table_list=[table_name],
                start_time='20240101',
                end_time='20241231',
                report_type='report_time'
            )

            if data and len(data.get('field', [])) > 0:
                print(f"  [OK] 成功 - 字段数: {len(data['field'])}, 报告期: {len(data.get('date', []))}")
            else:
                print(f"  [失败] 未获取到数据")

        except Exception as e:
            print(f"  [ERROR] {e}")

        print()

    # ========== 测试3: 查看可用的报表列表 ==========
    print("[测试3] 查看可用的财务报表类型")
    print("-" * 80)

    # 常见的财务报表
    common_tables = [
        'Balance',      # 资产负债表
        'Profit',       # 利润表
        'CashFlow',     # 现金流量表
        'Top10FlowHolder',  # 十大流通股东
        'Top10Holder',  # 十大股东
        'Capital',      # 股本结构
        'HolderNum',    # 股东人数
        'PE ratios',    # 市盈率
        'PS ratios',    # 市销率
    ]

    print("常见的财务报表类型:")
    for table in common_tables:
        print(f"  - {table}")
    print()

    # ========== 测试4: 获取最新报告期 ==========
    print("[测试4] 获取最新报告期的数据")
    print("-" * 80)

    try:
        # 不指定时间范围，获取最新的
        data = xtdata.get_financial_data(
            stock_list=[symbol],
            table_list=['Balance'],
            start_time='',  # 空字符串表示获取所有
            end_time='',
            report_type='report_time'
        )

        if data and len(data.get('field', [])) > 0:
            print(f"[OK] 获取最新财务数据成功")
            print(f"  字段数: {len(data['field'])}")
            print(f"  报告期数: {len(data.get('date', []))}")

            # 显示最新报告期
            if 'date' in data and len(data['date']) > 0:
                print(f"  最新报告期: {data['date'][-1]}")
            print()

            # 显示一些关键字段的值
            if 'value' in data and len(data['value']) > 0:
                print("[关键字段示例] (最新报告期)")
                # 找一些常见的字段
                key_fields = ['总资产', '总负债', '股东权益合计', '货币资金']
                for i, field in enumerate(key_fields):
                    if field in data.get('field', []):
                        field_idx = data['field'].index(field)
                        # 获取最新报告期的值（最后一列）
                        if len(data['value']) > field_idx:
                            value = data['value'][field_idx][-1] if len(data['value'][field_idx]) > 0 else 'N/A'
                            print(f"  {field}: {value}")
        else:
            print("[ERROR] 未获取到最新数据")
            print("  可能需要指定报告日期")
            print()

    except Exception as e:
        print(f"[ERROR] {e}")
        print()

    # ========== 总结 ==========
    print("=" * 80)
    print("[测试总结]")
    print("=" * 80)
    print()
    print("验证结果:")
    print("  [1] get_financial_data() API: " + "[OK] 可用" if 'data' in locals() and data else "[ERROR] 不可用或无权限")
    print("  [2] 财务报表种类: 待确认")
    print("  [3] 数据字段数量: 待确认")
    print("  [4] VIP权限要求: 待确认")
    print()
    print("建议:")
    print("  - 如果成功，查看返回的具体字段")
    print("  - 确认哪些报表需要VIP权限")
    print("  - 测试不同股票的数据完整性")
    print()


if __name__ == '__main__':
    try:
        test_financial_data()
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
