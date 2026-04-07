"""深度内存分析 - 找出所有持有数据的对象"""
import gc
import sys
import psutil
from collections import defaultdict

def find_all_dataframes():
    """找出所有 DataFrame 及其引用链"""
    gc.collect()

    dataframes = []
    referrers_dict = {}

    for obj in gc.get_objects():
        if isinstance(obj, pd.DataFrame):
            obj_id = id(obj)
            dataframes.append({
                'id': obj_id,
                'rows': len(obj),
                'cols': len(obj.columns),
                'columns': list(obj.columns),
                'memory_mb': obj.memory_usage(deep=True).sum() / 1024 / 1024,
            })

            # 获取谁引用了这个 DataFrame
            try:
                referrers = gc.get_referrers(obj)
                referrers_dict[obj_id] = []
                for ref in referrers[:10]:  # 只看前10个引用
                    ref_type = type(ref).__name__
                    ref_info = {'type': ref_type}

                    if ref_type == 'dict':
                        ref_info['dict_keys'] = list(ref.keys())[:5]
                    elif ref_type == 'list':
                        ref_info['list_length'] = len(ref)
                    elif ref_type == 'frame':
                        ref_info['frame_info'] = 'Python frame'

                    referrers_dict[obj_id].append(ref_info)
            except:
                pass

    return dataframes, referrers_dict


def find_large_lists(min_size=100):
    """找出所有大列表"""
    gc.collect()

    large_lists = []
    for obj in gc.get_objects():
        if isinstance(obj, list) and len(obj) >= min_size:
            large_lists.append({
                'type': type(obj[0]).__name__ if obj else 'empty',
                'length': len(obj),
                'size_mb': sys.getsizeof(obj) / 1024 / 1024,
                'sample': str(obj[:3]) if obj else 'empty',
            })

    large_lists.sort(key=lambda x: x['length'], reverse=True)
    return large_lists[:50]


def find_large_dicts(min_size=100):
    """找出所有大字典"""
    gc.collect()

    large_dicts = []
    for obj in gc.get_objects():
        if isinstance(obj, dict) and len(obj) >= min_size:
            large_dicts.append({
                'length': len(obj),
                'size_mb': sys.getsizeof(obj) / 1024 / 1024,
                'keys_sample': list(obj.keys())[:5],
            })

    large_dicts.sort(key=lambda x: x['length'], reverse=True)
    return large_dicts[:50]


def check_globals():
    """检查全局变量"""
    import myquant.core.market.services as services
    import myquant.core.market.adapters as adapters

    print("\n=== 检查服务模块全局变量 ===")

    # 检查 realtim_service
    try:
        from myquant.core.market.services.realtime_service import RealtimeMarketService
        if hasattr(RealtimeMarketService, '_instances'):
            print(f"RealtimeMarketService 实例: {len(RealtimeMarketService._instances)}")
    except:
        pass

    # 检查 kline_service
    try:
        from myquant.core.market.services.kline_service import KlineService
        if hasattr(KlineService, '_instance'):
            print(f"KlineService 实例: {KlineService._instance}")
    except:
        pass


def main():
    """主函数"""
    process = psutil.Process()
    print(f"当前进程内存: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    print("=" * 80)

    # 检查 DataFrame
    print("\n1. 检查 DataFrame...")
    dfs, refs = find_all_dataframes()
    print(f"   找到 {len(dfs)} 个 DataFrame")

    if dfs:
        total_memory = sum(df['memory_mb'] for df in dfs)
        print(f"   DataFrame 总内存: {total_memory:.2f} MB")

        for df in dfs[:10]:
            print(f"   - {df['rows']} 行 x {df['cols']} 列 = {df['memory_mb']:.2f} MB")
            if df['id'] in refs:
                print(f"     引用者: {refs[df['id']]}")

    # 检查大列表
    print("\n2. 检查大列表 (>=100 元素)...")
    lists = find_large_lists()
    print(f"   找到 {len(lists)} 个大列表")

    for lst in lists[:10]:
        print(f"   - {lst['type']} 长度={lst['length']}, 大小={lst['size_mb']:.2f} MB")
        print(f"     样本: {lst['sample']}")

    # 检查大字典
    print("\n3. 检查大字典 (>=100 键)...")
    dicts = find_large_dicts()
    print(f"   找到 {len(dicts)} 个大字典")

    for d in dicts[:10]:
        print(f"   - 长度={d['length']}, 大小={d['size_mb']:.2f} MB")
        print(f"     键样本: {d['keys_sample']}")

    # 检查全局变量
    check_globals()

    print("\n" + "=" * 80)
    print(f"进程内存: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    print(f"但 Python 对象只占: {sum(d['memory_mb'] for d in dfs):.2f} MB (DataFrame)")
    print(f"差异: {process.memory_info().rss / 1024 / 1024 - sum(d['memory_mb'] for d in dfs):.2f} MB 在 C 扩展中")


if __name__ == "__main__":
    import pandas as pd
    main()
