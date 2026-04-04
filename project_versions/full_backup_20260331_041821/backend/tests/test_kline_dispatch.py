"""测试 KlineService V5 双层路由（直接调用）"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from myquant.core.market.services.kline_service import get_kline_service


def test_dispatch_kline():
    """测试 _dispatch_kline 方法"""
    print("=" * 60)
    print("KlineService V5 双层路由测试")
    print("=" * 60)

    service = get_kline_service()
    symbol = "000001.SZ"

    print("")
    print("[测试] 获取 %s 1分钟数据" % symbol)
    print("-" * 40)

    # 调用 _dispatch_kline
    dataset = service._dispatch_kline(symbol, '1m', 10)

    if dataset is None:
        print("[结果] 失败 - 所有数据源均失败")
    else:
        bars = dataset.to_dict_list()
        print("[结果] 成功 - 来源: %s" % dataset.adapter)
        print("        数据条数: %d" % len(bars))
        if bars:
            latest_close = bars[-1].get('close', 'N/A')
            print("        最新价格: %s" % latest_close)
        print("")
        print("[OK] V5 双层路由工作正常！")

    print("")
    print("=" * 60)


if __name__ == "__main__":
    test_dispatch_kline()
