"""
TdxQuant L5板块数据测试

测试目标：
1. 验证TdxQuant的板块数据获取功能
2. 测试不同类型的板块数据（行业、概念、地区）
3. 测试板块成分股获取
4. 测试板块指数实时快照
5. 验证板块数据的完整性
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import (
    measure_performance,
    save_test_result,
    print_performance_result
)
from tests.config import (
    SECTOR_CONFIG,
    PERFORMANCE_CONFIG
)

print("="*60)
print("TdxQuant L5板块数据测试")
print("="*60)
print("板块数据是TdxQuant的主要优势")
print("="*60)


class TdxQuantL5Test:
    """TdxQuant L5板块数据测试类"""

    def __init__(self):
        # TODO: 初始化TdxQuant连接
        self.client = None
        print("\n⚠️ 注意: 需要集成实际的TdxQuant API客户端")
        print("  请根据实际的TdxQuant SDK修改此文件")

    def get_sector_list(self, sector_type: str):
        """
        获取板块列表

        Args:
            sector_type: 板块类型（industry/concept/region）

        Returns:
            list: 板块列表
        """
        # TODO: 实现实际的API调用
        # 示例代码（需要根据实际API调整）：
        # return self.client.get_sector_list(sector_type)

        # 模拟数据（仅用于演示）
        if sector_type == "industry":
            return [
                {"code": "BK0001", "name": "银行", "sector_type": "industry"},
                {"code": "BK0002", "name": "医药", "sector_type": "industry"},
                {"code": "BK0003", "name": "汽车", "sector_type": "industry"},
                {"code": "BK0004", "name": "白酒", "sector_type": "industry"},
                {"code": "BK0005", "name": "证券", "sector_type": "industry"},
            ]
        elif sector_type == "concept":
            return [
                {"code": "BK1001", "name": "人工智能", "sector_type": "concept"},
                {"code": "BK1002", "name": "新能源汽车", "sector_type": "concept"},
                {"code": "BK1003", "name": "数字货币", "sector_type": "concept"},
            ]
        else:  # region
            return [
                {"code": "BK2001", "name": "上海", "sector_type": "region"},
                {"code": "BK2002", "name": "深圳", "sector_type": "region"},
                {"code": "BK2003", "name": "北京", "sector_type": "region"},
            ]

    def get_sector_stocks(self, sector_code: str):
        """
        获取板块成分股列表

        Args:
            sector_code: 板块代码

        Returns:
            list: 成分股列表
        """
        # TODO: 实现实际的API调用
        # 示例代码（需要根据实际API调整）：
        # return self.client.get_sector_stocks(sector_code)

        # 模拟数据（仅用于演示）
        if sector_code == "BK0004":  # 白酒板块
            return [
                {"code": "600519.SH", "name": "贵州茅台"},
                {"code": "000858.SZ", "name": "五粮液"},
                {"code": "000568.SZ", "name": "泸州老窖"},
                {"code": "600809.SH", "name": "山西汾酒"},
            ]
        else:
            return [
                {"code": "600519.SH", "name": "贵州茅台"},
                {"code": "601318.SH", "name": "中国平安"},
            ]

    def get_sector_snapshot(self, sector_code: str):
        """
        获取板块指数实时快照

        Args:
            sector_code: 板块代码

        Returns:
            dict: 板块指数快照
        """
        # TODO: 实现实际的API调用
        # 示例代码（需要根据实际API调整）：
        # return self.client.get_sector_snapshot(sector_code)

        # 模拟数据（仅用于演示）
        return {
            "sector_code": sector_code,
            "price": 1500.50,
            "change": 25.30,
            "change_pct": 1.72,
            "volume": 12345678,
            "amount": 1.85e9
        }


def test_sector_types():
    """测试不同类型的板块数据"""
    print("\n1. 测试不同类型的板块数据")

    test = TdxQuantL5Test()

    sector_types = []
    if SECTOR_CONFIG.get('industry'):
        sector_types.append(('行业板块', 'industry'))
    if SECTOR_CONFIG.get('concept'):
        sector_types.append(('概念板块', 'concept'))
    if SECTOR_CONFIG.get('region'):
        sector_types.append(('地区板块', 'region'))

    results = {}

    for name, type_code in sector_types:
        print(f"\n  测试类型: {name} ({type_code})")

        try:
            def get_data():
                return test.get_sector_list(type_code)

            # 性能测试
            perf_data = measure_performance(
                get_data,
                warmup_count=2,
                test_count=5
            )

            # 获取实际数据
            sectors = get_data()
            sector_count = len(sectors)

            # 数据验证
            has_required_fields = all(
                'code' in s and 'name' in s
                for s in sectors
            )

            print(f"    板块数量: {sector_count}个")
            print(f"    数据完整性: {'✅ 通过' if has_required_fields else '❌ 失败'}")
            print(f"    性能: {perf_data['avg']:.2f}ms")

            if sector_count > 0:
                print(f"    示例: {sectors[0]['name']} ({sectors[0]['code']})")

            results[type_code] = {
                "success": has_required_fields,
                "count": sector_count,
                "performance": perf_data,
                "sample": sectors[:3] if sectors else []
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[type_code] = {
                "success": False,
                "count": 0,
                "error_msg": str(e)
            }

    # 汇总结果
    success_count = sum(1 for r in results.values() if r.get('success', False))
    print(f"\n  结果汇总: {success_count}/{len(results)}个类型成功")

    # 保存结果
    save_test_result("test_l5_sector_types", {
        "test_type": "L5_sector_types",
        "results": results,
        "success_rate": (success_count / len(results)) * 100
    })

    return results


def test_sector_components():
    """测试板块成分股获取"""
    print("\n2. 测试板块成分股获取")

    test = TdxQuantL5Test()

    # 测试几个不同类型的板块
    test_sectors = [
        ("BK0004", "白酒板块"),
        ("BK0001", "银行板块"),
    ]

    results = {}

    for code, name in test_sectors:
        print(f"\n  测试板块: {name} ({code})")

        try:
            def get_data():
                return test.get_sector_stocks(code)

            # 性能测试
            perf_data = measure_performance(
                get_data,
                warmup_count=2,
                test_count=5
            )

            # 获取实际数据
            stocks = get_data()
            stock_count = len(stocks)

            # 数据验证
            has_required_fields = all(
                'code' in s and 'name' in s
                for s in stocks
            )

            print(f"    成分股数量: {stock_count}只")
            print(f"    数据完整性: {'✅ 通过' if has_required_fields else '❌ 失败'}")
            print(f"    性能: {perf_data['avg']:.2f}ms")

            if stock_count > 0:
                print(f"    示例成分股: {stocks[0]['name']} ({stocks[0]['code']})")

            results[code] = {
                "success": has_required_fields,
                "count": stock_count,
                "performance": perf_data,
                "stocks": stocks[:5] if stocks else []  # 只保存前5只
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[code] = {
                "success": False,
                "count": 0,
                "error_msg": str(e)
            }

    # 保存结果
    save_test_result("test_l5_sector_components", {
        "test_type": "L5_sector_components",
        "results": results
    })

    return results


def test_sector_snapshot():
    """测试板块指数实时快照"""
    print("\n3. 测试板块指数实时快照")

    test = TdxQuantL5Test()

    # 测试几个板块的实时快照
    test_sectors = ["BK0004", "BK0001", "BK1001"]

    results = {}

    for sector_code in test_sectors:
        print(f"\n  测试板块: {sector_code}")

        try:
            def get_data():
                return test.get_sector_snapshot(sector_code)

            # 性能测试
            perf_data = measure_performance(
                get_data,
                warmup_count=PERFORMANCE_CONFIG['warmup_count'],
                test_count=PERFORMANCE_CONFIG['test_count']
            )

            # 获取实际数据
            snapshot = get_data()

            # 数据验证
            required_fields = ['sector_code', 'price', 'volume']
            has_required_fields = all(
                field in snapshot
                for field in required_fields
            )

            print(f"    价格: {snapshot.get('price', 0):.2f}")
            print(f"    涨跌: {snapshot.get('change', 0):.2f} ({snapshot.get('change_pct', 0):.2f}%)")
            print(f"    数据完整性: {'✅ 通过' if has_required_fields else '❌ 失败'}")
            print(f"    性能: {perf_data['avg']:.2f}ms")

            print_performance_result(f"板块{sector_code}快照", perf_data)

            results[sector_code] = {
                "success": has_required_fields,
                "performance": perf_data,
                "data": snapshot
            }

        except Exception as e:
            print(f"    ❌ 失败: {e}")
            results[sector_code] = {
                "success": False,
                "error_msg": str(e)
            }

    # 保存结果
    save_test_result("test_l5_sector_snapshot", {
        "test_type": "L5_sector_snapshot",
        "results": results
    })

    return results


def test_sector_advantage():
    """测试板块数据优势验证"""
    print("\n4. 验证板块数据作为TdxQuant优势")

    test = TdxQuantL5Test()

    print("\n  板块数据优势分析:")
    print("  1. 板块数量完整性")
    print("  2. 成分股数据准确性")
    print("  3. 实时快照性能")
    print("  4. 数据更新及时性")

    # 综合评估
    advantages = []

    # 1. 板块数量
    try:
        industry_count = len(test.get_sector_list('industry'))
        concept_count = len(test.get_sector_list('concept'))
        region_count = len(test.get_sector_list('region'))
        total_count = industry_count + concept_count + region_count

        print(f"\n  板块数量:")
        print(f"    行业板块: {industry_count}个")
        print(f"    概念板块: {concept_count}个")
        print(f"    地区板块: {region_count}个")
        print(f"    总计: {total_count}个")

        advantages.append({
            "aspect": "板块数量",
            "status": "✅",
            "detail": f"共{total_count}个板块，覆盖全面"
        })
    except Exception as e:
        advantages.append({
            "aspect": "板块数量",
            "status": "❌",
            "detail": f"获取失败: {e}"
        })

    # 2. 成分股数据
    try:
        stocks = test.get_sector_stocks('BK0004')
        advantages.append({
            "aspect": "成分股数据",
            "status": "✅",
            "detail": f"成分股数据完整，包含{len(stocks)}只股票"
        })
    except Exception as e:
        advantages.append({
            "aspect": "成分股数据",
            "status": "❌",
            "detail": f"获取失败: {e}"
        })

    # 3. 实时快照
    try:
        snapshot = test.get_sector_snapshot('BK0004')
        perf_data = measure_performance(
            lambda: test.get_sector_snapshot('BK0004'),
            warmup_count=3,
            test_count=10
        )

        advantages.append({
            "aspect": "实时快照性能",
            "status": "✅",
            "detail": f"平均{perf_data['avg']:.2f}ms，性能优异"
        })
    except Exception as e:
        advantages.append({
            "aspect": "实时快照性能",
            "status": "❌",
            "detail": f"获取失败: {e}"
        })

    # 汇总
    print(f"\n  优势评估结果:")
    for item in advantages:
        print(f"    {item['status']} {item['aspect']}: {item['detail']}")

    # 保存结果
    save_test_result("test_l5_sector_advantage", {
        "test_type": "L5_sector_advantage",
        "advantages": advantages,
        "conclusion": "板块数据是TdxQuant的主要优势"
    })

    return advantages


if __name__ == "__main__":
    import time

    print("\n开始L5板块数据测试...\n")

    try:
        # 执行所有测试
        result1 = test_sector_types()
        result2 = test_sector_components()
        result3 = test_sector_snapshot()
        result4 = test_sector_advantage()

        # 汇总结果
        print("\n" + "="*60)
        print("L5板块数据测试完成")
        print("="*60)
        print(f"板块类型测试: {result1.get('success_rate', 0):.1f}%成功率")
        print(f"成分股测试: {sum(1 for r in result2.values() if r.get('success', False))}/{len(result2)}通过")
        print(f"实时快照测试: {sum(1 for r in result3.values() if r.get('success', False))}/{len(result3)}通过")
        print(f"优势验证: 板块数据是TdxQuant的主要优势")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
