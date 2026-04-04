#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复QLib数据路径问题
确保QLib使用项目路径而不是默认用户目录
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


def fix_qlib_data_path():
    """
    修复QLib数据路径问题
    
    确保QLib使用项目路径而不是默认用户目录
    """
    try:
        # 设置项目数据路径
        project_data_dir = project_root / "data" / "qlib_data"
        
        # 确保目录存在
        project_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置环境变量，强制QLib使用我们的路径
        os.environ["QLIB_DATA_DIR"] = str(project_data_dir)
        os.environ["QLIB_PROVIDER_URI"] = str(project_data_dir)
        
        # 创建QLib配置文件
        qlib_config_dir = project_data_dir / ".qlib"
        qlib_config_dir.mkdir(exist_ok=True)
        
        # 创建配置文件
        config_file = qlib_config_dir / "config.yaml"
        config_content = f"""# QLib配置文件
provider_uri: {project_data_dir}
region: cn
flg: day
"""
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        logger.info(f"QLib数据路径已修复为: {project_data_dir}")
        return True
        
    except Exception as e:
        logger.error(f"修复QLib数据路径失败: {e}")
        return False


def initialize_qlib_with_project_path():
    """
    使用项目路径初始化QLib
    
    Returns:
        是否初始化成功
    """
    try:
        # 首先修复数据路径
        if not fix_qlib_data_path():
            return False
        
        # 然后初始化QLib
        import qlib
        from qlib.constant import REG_CN
        
        # 使用项目路径初始化
        project_data_dir = project_root / "data" / "qlib_data"
        
        qlib.init(
            provider_uri=str(project_data_dir),
            region=REG_CN
        )
        
        # 验证路径是否正确
        from qlib.config import C
        actual_provider_uri = C.get("provider_uri", None)
        
        if actual_provider_uri and str(project_data_dir) in actual_provider_uri:
            logger.info(f"✅ QLib使用正确的项目路径: {actual_provider_uri}")
            return True
        else:
            logger.warning(f"⚠️ QLib可能仍在使用默认路径: {actual_provider_uri}")
            return False
            
    except Exception as e:
        logger.error(f"初始化QLib失败: {e}")
        return False


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("修复QLib数据路径问题")
    print("=" * 70)
    
    # 修复路径
    success = fix_qlib_data_path()
    
    if success:
        print("✅ QLib数据路径修复成功")
        
        # 尝试初始化QLib
        print("\n尝试初始化QLib...")
        init_success = initialize_qlib_with_project_path()
        
        if init_success:
            print("✅ QLib初始化成功，使用项目路径")
        else:
            print("❌ QLib初始化失败")
    else:
        print("❌ QLib数据路径修复失败")
    
    print("\n" + "=" * 70)