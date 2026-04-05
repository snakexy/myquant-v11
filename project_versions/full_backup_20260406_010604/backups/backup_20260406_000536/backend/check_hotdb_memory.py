"""
检查 HotDB Adapter 内存使用情况
"""
import json
import requests

def check_memory():
    """检查内存缓存状态"""
    try:
        resp = requests.get("http://localhost:8000/api/debug/hotdb-memory", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print("=" * 60)
            print("HotDB 内存缓存状态:")
            print("=" * 60)

            stats = data.get("stats", {})
            print(f"缓存项数: {stats.get('count', 0)} / {stats.get('max_count', 50)}")
            print(f"总内存: {stats.get('total_cached_mb', 0)} MB / {stats.get('max_cached_mb', 0)} MB")
            print(f"总字节: {stats.get('total_cached_bytes', 0)}")

            details = data.get("details", [])
            if details:
                print(f"\n前10个缓存项:")
                for item in details[:10]:
                    print(f"  - {item.get('key')}: {item.get('rows')} 行, {item.get('size_kb')} KB")

            # 检查异常
            if stats.get('total_cached_mb', 0) > 20:
                print("\n⚠️ 警告: 缓存内存超过 20MB!")
            if stats.get('count', 0) > 45:
                print("\n⚠️ 警告: 缓存项数接近上限!")

            print("=" * 60)
        else:
            print(f"请求失败: {resp.status_code}")
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_memory()
