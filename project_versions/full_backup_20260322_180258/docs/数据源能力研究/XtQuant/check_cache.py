# -*- coding: utf-8 -*-
"""
检查XtQuant缓存目录
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import os

# 获取数据目录
print("XtQuant数据目录检查")
print("="*80)

# 方法1: 通过连接信息获取
try:
    # 连接后会显示数据目录路径
    print("\n尝试连接获取数据路径...")
    # 这个方法可能不会直接返回路径
except:
    pass

# 方法2: 常见路径
common_paths = [
    r"E:\迅投QMT交易终端 正在使用版\userdata_mini\datadir",
    r"E:\迅投QMT交易终端 正在使用版\userdata\datadir",
    r"C:\userdata_mini\datadir",
    r"C:\userdata\datadir",
]

print("\n检查常见路径:")
for path in common_paths:
    if os.path.exists(path):
        print("  [存在] %s" % path)

        # 列出子目录
        try:
            subdirs = os.listdir(path)
            print("    子目录: %s" % str(subdirs[:10]))
        except:
            pass
    else:
        print("  [不存在] %s" % path)

# 方法3: 检查分钟线缓存
print("\n检查分钟线数据缓存:")

# 搜索可能包含分钟线数据的目录
for base_path in common_paths:
    if os.path.exists(base_path):
        for root, dirs, files in os.walk(base_path):
            # 查找包含分钟线的文件
            for file in files:
                if '5m' in file or '1m' in file or 'min' in file.lower():
                    rel_path = os.path.relpath(os.path.join(root, file), base_path)
                    print("  找到: %s" % rel_path)
                    if len(rel_path.split('\\')) < 3:  # 只显示前几层
                        break
            break

print("\n提示: 如需清理缓存，请手动删除datadir目录下的相应文件")
