#!/usr/bin/env python3
"""
完整项目备份脚本
备份整个项目的当前状态，排除不必要的文件
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

# Windows 特殊文件名（无法复制）
windows_special_files = {
    "nul", "con", "prn", "aux", "com1", "com2", "com3", "com4",
    "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2",
    "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"
}


def safe_copytree(src, dst, ignore=None):
    """安全复制目录，跳过无法复制的文件"""
    if ignore is None:
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*.log", "*.tmp")

    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        # 跳过 Windows 特殊文件
        if item.name.lower() in windows_special_files:
            continue

        if item.is_dir():
            # 递归复制子目录
            if not ignore(item.name, []):
                safe_copytree(item, dst / item.name, ignore)
        elif item.is_file():
            # 复制文件
            try:
                shutil.copy2(item, dst / item.name)
            except Exception as e:
                print(f"[WARNING] 跳过文件: {item.name} ({e})")


def create_full_backup():
    """创建完整的项目备份"""
    print("=" * 60)
    print("MyQuant v9.0.0 - 完整项目备份工具")
    print("=" * 60)

    # 项目根目录
    project_root = Path(".")
    project_root = Path("E:\\MyQuant_v9.0.0")  # 明确指定项目路径

    # 备份目录
    backup_dir = project_root / "project_versions"
    backup_dir.mkdir(exist_ok=True)

    # 生成备份名称
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"full_backup_{timestamp}"
    backup_path = backup_dir / backup_name
    backup_path.mkdir(exist_ok=True)

    # 排除的目录
    exclude_dirs = {
        ".git", "__pycache__", ".pytest_cache", ".venv",
        "node_modules", ".idea", ".vscode", "logs", "data_cache",
        "project_versions", "MyQuant.egg-info"
    }

    # 排除的文件类型
    exclude_extensions = {
        ".pyc", ".pyo", ".pyd", ".log", ".tmp", ".bak"
    }

    # 排除的特定文件
    exclude_files = {
        "backup_current_progress.py"
    }

    print(f"正在创建完整备份到: {backup_path}")
    print()

    files_backed_up = 0
    dirs_backed_up = 0
    total_size = 0

    # 遍历项目目录
    for item in project_root.iterdir():
        # 跳过备份目录本身
        if item.name == "project_versions":
            continue

        # 跳过排除的目录
        if item.is_dir() and item.name in exclude_dirs:
            continue

        # 备份目录
        if item.is_dir():
            dest_path = backup_path / item.name
            try:
                print(f"[DIR] 备份目录: {item.name}")
            except UnicodeEncodeError:
                print(f"[DIR] 备份目录: (无法显示名称)")

            # 使用安全复制函数
            safe_copytree(item, dest_path)

            # 统计文件和大小
            for file_path in item.rglob("*"):
                if file_path.is_file():
                    # 跳过Windows特殊文件
                    if file_path.name.lower() in windows_special_files:
                        continue
                    files_backed_up += 1
                    try:
                        total_size += file_path.stat().st_size
                    except Exception:
                        pass

            dirs_backed_up += 1

        # 备份文件
        elif item.is_file():
            # 跳过排除的文件
            if (item.name in exclude_files or
                any(item.name.endswith(ext) for ext in exclude_extensions)):
                continue

            dest_path = backup_path / item.name
            try:
                print(f"[FILE] 备份文件: {item.name}")
            except UnicodeEncodeError:
                print(f"[FILE] 备份文件: (无法显示名称)")
            shutil.copy2(item, dest_path)
            files_backed_up += 1
            try:
                total_size += item.stat().st_size
            except Exception:
                pass

    # 创建备份信息文件
    backup_info = {
        "backup_name": backup_name,
        "created_at": datetime.now().isoformat(),
        "description": "完整项目备份 - Python 3.11 + TA-Lib 0.6.7 + XtQuant",
        "stats": {
            "files_backed_up": files_backed_up,
            "dirs_backed_up": dirs_backed_up,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        },
        "exclude_dirs": list(exclude_dirs),
        "exclude_extensions": list(exclude_extensions),
        "exclude_files": list(exclude_files)
    }

    info_file = backup_path / "backup_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)

    # 更新版本配置
    config_file = project_root / "version_manager" / "project_version_config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {"versions": {}}
    else:
        config = {"versions": {}}

    # 添加新版本信息
    config["versions"][backup_name] = {
        "name": backup_name,
        "description": backup_info["description"],
        "tags": ["full_backup", "auto", "python3.11", "talib"],
        "created_at": backup_info["created_at"],
        "files": [{"path": "full_project", "type": "directory", "file_count": files_backed_up}],
        "files_count": files_backed_up
    }
    config["current_version"] = backup_name

    # 保存配置
    config_file.parent.mkdir(exist_ok=True)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print()
    print("[SUCCESS] 备份完成!")
    print(f"[INFO] 备份位置: {backup_path}")
    print("[STATS] 备份统计:")
    print(f"   - 文件数: {files_backed_up}")
    print(f"   - 目录数: {dirs_backed_up}")
    print(f"   - 总大小: {backup_info['stats']['total_size_mb']} MB")
    print(f"[NAME] 备份名称: {backup_name}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        create_full_backup()
    except KeyboardInterrupt:
        print("\n备份操作被用户中断")
    except Exception as e:
        print(f"\n备份过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
