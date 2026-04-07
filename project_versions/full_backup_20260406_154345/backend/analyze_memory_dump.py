"""内存分析工具 - dump 内存对象到文件进行分析"""
import gc
import sys
import pickle
from pathlib import Path
from typing import Any, Dict, List
from collections import Counter
import pandas as pd

def get_object_info(obj: Any, obj_id: int = None) -> Dict:
    """获取对象信息"""
    if obj_id is None:
        obj_id = id(obj)

    obj_type = type(obj).__name__
    size = sys.getsizeof(obj)

    info = {
        'id': obj_id,
        'type': obj_type,
        'size': size,
        'size_mb': size / 1024 / 1024,
    }

    # 额外信息
    if isinstance(obj, pd.DataFrame):
        info.update({
            'dataframe_rows': len(obj),
            'dataframe_cols': len(obj.columns),
            'dataframe_columns': list(obj.columns),
            'dataframe_memory_mb': obj.memory_usage(deep=True).sum() / 1024 / 1024,
        })
    elif isinstance(obj, pd.Series):
        info.update({
            'series_length': len(obj),
            'series_dtype': str(obj.dtype),
        })
    elif isinstance(obj, dict):
        info.update({
            'dict_keys': list(obj.keys())[:20],  # 只保存前20个
            'dict_length': len(obj),
        })
    elif isinstance(obj, (list, tuple)):
        info.update({
            'list_length': len(obj),
            'list_first_items': str(obj[:5]) if len(obj) > 0 else 'empty',
        })
    elif isinstance(obj, str):
        info.update({
            'str_length': len(obj),
            'str_preview': obj[:100],
        })

    return info


def analyze_big_objects(min_size_mb: float = 0.1) -> List[Dict]:
    """找出所有大对象"""
    gc.collect()

    big_objects = []
    seen = set()

    for obj in gc.get_objects():
        obj_id = id(obj)
        if obj_id in seen:
            continue
        seen.add(obj_id)

        try:
            size = sys.getsizeof(obj)
            if size >= min_size_mb * 1024 * 1024:
                info = get_object_info(obj, obj_id)
                big_objects.append(info)
        except:
            pass

    # 按大小排序
    big_objects.sort(key=lambda x: x['size'], reverse=True)
    return big_objects


def analyze_dataframes() -> List[Dict]:
    """找出所有 DataFrame"""
    gc.collect()

    dataframes = []
    seen = set()

    for obj in gc.get_objects():
        obj_id = id(obj)
        if obj_id in seen:
            continue
        seen.add(obj_id)

        if isinstance(obj, pd.DataFrame):
            try:
                info = get_object_info(obj, obj_id)
                dataframes.append(info)
            except:
                pass

    dataframes.sort(key=lambda x: x['size'], reverse=True)
    return dataframes


def save_to_file(data: List[Dict], filename: str):
    """保存到文件"""
    output_path = Path(__file__).parent / filename

    # 使用普通格式保存（避免pickle问题）
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(str(item) + '\n')
            f.write('-' * 80 + '\n')

    print(f"已保存到: {output_path}")


def main():
    """主函数"""
    print("=" * 80)
    print("内存分析工具")
    print("=" * 80)

    # 分析大对象
    print("\n1. 分析大对象 (>0.1 MB)...")
    big_objects = analyze_big_objects(min_size_mb=0.1)
    print(f"   找到 {len(big_objects)} 个大对象")

    if big_objects:
        print("\n   最大的 10 个对象:")
        for i, obj in enumerate(big_objects[:10], 1):
            print(f"   {i}. {obj['type']} - {obj['size_mb']:.2f} MB")
            if 'dataframe_rows' in obj:
                print(f"      DataFrame: {obj['dataframe_rows']} 行 x {obj['dataframe_cols']} 列")
                print(f"      内存: {obj['dataframe_memory_mb']:.2f} MB")
                print(f"      列: {obj['dataframe_columns']}")

        save_to_file(big_objects, 'memory_big_objects.txt')

    # 分析 DataFrame
    print("\n2. 分析 DataFrame...")
    dataframes = analyze_dataframes()
    print(f"   找到 {len(dataframes)} 个 DataFrame")

    if dataframes:
        print("\n   DataFrame 详情:")
        total_memory = 0
        for i, df in enumerate(dataframes, 1):
            memory_mb = df.get('dataframe_memory_mb', df['size_mb'])
            total_memory += memory_mb
            print(f"   {i}. {memory_mb:.2f} MB - {df['dataframe_rows']} 行 x {df['dataframe_cols']} 列")
            print(f"      列: {df['dataframe_columns']}")

        print(f"\n   DataFrame 总内存: {total_memory:.2f} MB")
        save_to_file(dataframes, 'memory_dataframes.txt')

    # 统计对象类型
    print("\n3. 统计对象类型...")
    type_counter = Counter()
    for obj in gc.get_objects():
        try:
            type_counter[type(obj).__name__] += 1
        except:
            pass

    print("   对象数量排名:")
    for obj_type, count in type_counter.most_common(20):
        print(f"   {obj_type}: {count} 个")

    print("\n" + "=" * 80)
    print(f"进程总内存: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB")
    print("=" * 80)


if __name__ == "__main__":
    import psutil
    main()
