"""清理 HotDB 错误数据并重新预热"""
import sys
import shutil
from pathlib import Path

sys.path.insert(0, 'E:/MyQuant_v11/backend')

# HotDB 数据目录
hotdb_dir = Path('E:/MyQuant_v11/data/hotdata')

print("=" * 70)
print("清理 HotDB 错误数据")
print("=" * 70)

if hotdb_dir.exists():
    # 备份到旧版本目录
    from datetime import datetime
    backup_name = f"hotdb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path = Path('E:/MyQuant_v11/project_versions') / backup_name

    print(f"\n备份 HotDB 到: {backup_path}")
    shutil.copytree(hotdb_dir, backup_path)
    print("备份完成")

    # 删除 HotDB 数据
    print(f"\n删除 HotDB 数据: {hotdb_dir}")
    shutil.rmtree(hotdb_dir)
    print("删除完成")

    # 重新创建目录
    hotdb_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n重建 HotDB 目录: {hotdb_dir}")

print("\n" + "=" * 70)
print("HotDB 已清空，接下来重新预热...")
print("=" * 70)

# 重新预热（从 LocalDB）
from myquant.core.market.services.hotdb_service import get_hotdb_service

service = get_hotdb_service()

# 预热台基股份
symbol = "300046.SZ"
periods = ['1d', '5m']

print(f"\n预热 {symbol} {periods}...")
result = service.preheat(symbols=[symbol], periods=periods)

print(f"\n预热结果: {result}")

# 验证预热后的数据
from myquant.core.market.adapters import get_adapter

hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    print("\n" + "=" * 70)
    print("验证预热后的数据:")
    print("=" * 70)

    for period in periods:
        df_dict = hotdb.get_kline(symbols=[symbol], period=period, count=3)
        if symbol in df_dict and not df_dict[symbol].empty:
            df = df_dict[symbol].sort_values('datetime', ascending=False).head(3)
            print(f"\n[HotDB] {period} 最新3条:")
            for _, row in df.iterrows():
                print(f"  {row['datetime']}  volume={int(row['volume']):>10} 手")

print("\n" + "=" * 70)
print("完成！")
print("=" * 70)
