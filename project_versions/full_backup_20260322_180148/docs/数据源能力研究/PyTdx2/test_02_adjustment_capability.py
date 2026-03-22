# -*- coding: utf-8 -*-
"""
PyTdx2 复权功能完整测试

验证 PyTdx2 的 get_xdxr_info() API 和复权计算功能
"""

import time
from pytdx2.hq import TdxHq_API
from pytdx2.params import TDXParams
import pandas as pd


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_xdxr_info_api():
    """测试除权除息信息API"""
    print_section("1. 除权除息信息API测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            # 测试一只股票的除权信息
            symbol = "600000"  # 浦发银行
            market = 1

            start = time.time()
            xdxr_data = api.get_xdxr_info(market, symbol)
            elapsed = (time.time() - start) * 1000

            print(f"股票: {symbol}")
            print(f"耗时: {elapsed:.2f}ms")
            print(f"记录数: {len(xdxr_data)}")

            if xdxr_data:
                df = pd.DataFrame(xdxr_data)
                print(f"\n字段: {list(df.columns)}")
                print(f"\n最近3条记录:")
                print(df[['year', 'month', 'day', 'category', 'name',
                         'fenhong', 'songzhuangu', 'peigu', 'peigujia']].tail(3).to_string())

                # 统计各类别
                category_counts = df['category'].value_counts()
                print(f"\n类别统计:")
                for cat, count in category_counts.items():
                    cat_name = df[df['category'] == cat]['name'].iloc[0] if len(df) > 0 else str(cat)
                    print(f"  {cat_name}: {count}条")

                return xdxr_data
            else:
                print("没有除权除息记录")
                return []

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        api.disconnect()


def test_dividend_types():
    """测试不同类型的除权除息"""
    print_section("2. 不同类别除权除息测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            # 测试多只股票
            test_symbols = [
                (1, "600000"),  # 浦发银行
                (0, "000001"),  # 平安银行
                (1, "600036"),  # 招商银行
                (0, "000002"),  # 万科A
            ]

            for market, symbol in test_symbols:
                xdxr_data = api.get_xdxr_info(market, symbol)

                if xdxr_data:
                    df = pd.DataFrame(xdxr_data)

                    # 统计
                    total = len(df)
                    category_1 = len(df[df['category'] == 1])  # 除权除息

                    print(f"\n{symbol}:")
                    print(f"  总记录: {total}")
                    print(f"  除权除息(category=1): {category_1}")
                    if category_1 > 0:
                        recent = df[df['category'] == 1].tail(1)
                        print(f"  最近除权: {int(recent.iloc[0]['year'])}-{int(recent.iloc[0]['month']):02d}")
                        print(f"    分红: {recent.iloc[0]['fenhong']}")
                        print(f"    送股: {recent.iloc[0]['songzhuangu']}")
                else:
                    print(f"\n{symbol}: 无除权除息记录")

    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        api.disconnect()


def test_adjustment_factors():
    """测试复权因子计算"""
    print_section("3. 复权因子计算测试")

    api = TdxHq_API()

    try:
        if api.connect('180.153.18.172', 80):
            symbol = "600000"
            market = 1

            # 获取除权信息
            xdxr_data = api.get_xdxr_info(market, symbol)

            if not xdxr_data:
                print("无除权除息记录")
                return

            df = pd.DataFrame(xdxr_data)
            dividend_records = df[df['category'] == 1].copy()

            if len(dividend_records) == 0:
                print("无除权除息记录")
                return

            print(f"找到{len(dividend_records)}条除权除息记录")

            # 获取K线数据
            kline_data = api.get_security_bars(
                category=TDXParams.KLINE_TYPE_RI_K,
                market=market,
                code=symbol,
                start=0,
                count=500
            )

            if not kline_data:
                print("无法获取K线数据")
                return

            kline_df = pd.DataFrame(kline_data)
            kline_df['date'] = kline_df.apply(
                lambda row: f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}",
                axis=1
            )

            print(f"获取{len(kline_df)}条K线数据")

            # 计算复权因子
            dividend_records['date'] = dividend_records.apply(
                lambda row: f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}",
                axis=1
            )

            # 从最新日期开始计算
            temp_factors = {}
            cumulative_factor = 1.0

            sorted_dates = sorted(kline_df['date'].unique(), reverse=True)

            for date in sorted_dates[:10]:  # 只显示最近10个
                temp_factors[date] = cumulative_factor

                ex_div_records = dividend_records[dividend_records['date'] == date]

                if len(ex_div_records) > 0:
                    before_ex_data = kline_df[kline_df['date'] < date]

                    if len(before_ex_data) > 0:
                        last_close = float(before_ex_data.iloc[-1]['close'])

                        for _, ex_div in ex_div_records.iterrows():
                            fenhong = float(ex_div.get('fenhong', 0) or 0) / 10
                            songgu = float(ex_div.get('songzhuangu', 0) or 0) / 10
                            peigu = float(ex_div.get('peigu', 0) or 0) / 10
                            peigujia = float(ex_div.get('peigujia', 0) or 0)

                            if last_close > 0 and (1 + songgu + peigu) > 0:
                                adjusted_close = (last_close + peigu * peigujia - fenhong) / (1 + songgu + peigu)

                                if adjusted_close > 0:
                                    factor = adjusted_close / last_close
                                    cumulative_factor = cumulative_factor * factor

                                    print(f"\n日期: {date}")
                                    print(f"  除权前收盘: {last_close:.2f}")
                                    print(f"  分红: {fenhong:.2f}, 送股: {songgu:.2f}, 配股: {peigu:.2f}, 配股价: {peigujia:.2f}")
                                    print(f"  理论除权价: {adjusted_close:.2f}")
                                    print(f"  复权因子: {factor:.6f}")
                                    print(f"  累积因子: {cumulative_factor:.6f}")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        api.disconnect()


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  PyTdx2 复权功能完整测试")
    print("=" * 60)

    # 1. API测试
    test_xdxr_info_api()

    # 2. 不同类别测试
    test_dividend_types()

    # 3. 复权因子计算测试
    test_adjustment_factors()

    print("\n" + "=" * 60)
    print("  测试完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
