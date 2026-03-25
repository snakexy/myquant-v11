#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QLib初始化修复
彻底解决QLib使用默认用户目录的问题
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


def patch_qlib_init():
    """
    修补QLib初始化函数，强制使用项目路径
    
    这个函数会在QLib初始化之前被调用，修改其默认行为
    """
    try:
        import qlib
        
        # 保存原始的init函数
        original_init = qlib.init
        
        def patched_init(provider_uri=None, region=None, **kwargs):
            """
            修补后的QLib初始化函数
            强制使用项目路径而不是默认用户目录
            """
            # 如果没有提供provider_uri，使用项目路径
            if provider_uri is None:
                project_data_dir = project_root / "data" / "qlib_data"
                provider_uri = str(project_data_dir)
                logger.info(f"使用项目数据路径: {provider_uri}")
            
            # 设置环境变量，确保QLib使用我们的路径
            os.environ["QLIB_DATA_DIR"] = provider_uri
            os.environ["QLIB_PROVIDER_URI"] = provider_uri
            
            # 调用原始初始化函数
            return original_init(provider_uri=provider_uri, region=region, **kwargs)
        
        # 替换QLib的init函数
        qlib.init = patched_init
        
        logger.info("✅ QLib初始化函数已修补")
        return True
        
    except Exception as e:
        logger.error(f"修补QLib初始化函数失败: {e}")
        return False


def force_qlib_project_path():
    """
    强制QLib使用项目路径
    
    这个函数会设置所有相关的环境变量和配置
    """
    try:
        # 设置项目数据路径
        project_data_dir = project_root / "data" / "qlib_data"
        
        # 确保目录存在
        project_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置所有可能的环境变量
        os.environ["QLIB_DATA_DIR"] = str(project_data_dir)
        os.environ["QLIB_PROVIDER_URI"] = str(project_data_dir)
        os.environ["QLIB_MAIN_PATH"] = str(project_root)
        
        # 创建QLib配置目录
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
        
        # 尝试修补QLib初始化函数
        patch_qlib_init()
        
        logger.info(f"✅ QLib已强制使用项目路径: {project_data_dir}")
        return True
        
    except Exception as e:
        logger.error(f"强制QLib使用项目路径失败: {e}")
        return False


def verify_qlib_path():
    """
    验证QLib是否使用了正确的路径
    
    Returns:
        是否使用了项目路径
    """
    try:
        import qlib
        from qlib.config import C
        
        # 获取QLib实际使用的路径
        actual_provider_uri = C.get("provider_uri", None)
        expected_provider_uri = str(project_root / "data" / "qlib_data")
        
        if actual_provider_uri and expected_provider_uri in actual_provider_uri:
            logger.info(f"✅ QLib使用正确的项目路径: {actual_provider_uri}")
            return True
        else:
            logger.warning(f"⚠️ QLib仍在使用默认路径: {actual_provider_uri}")
            logger.warning(f"期望路径: {expected_provider_uri}")
            return False
            
    except Exception as e:
        logger.error(f"验证QLib路径失败: {e}")
        return False


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("QLib初始化修复")
    print("=" * 70)
    
    # 强制使用项目路径
    success = force_qlib_project_path()
    
    if success:
        print("✅ QLib路径强制设置成功")
        
        # 尝试初始化QLib
        print("\n尝试初始化QLib...")
        try:
            import qlib
            from qlib.constant import REG_CN
            
            # 初始化QLib（应该使用修补后的函数）
            qlib.init(region=REG_CN)
            
            # 验证路径
            print("\n验证QLib路径...")
            verify_success = verify_qlib_path()
            
            if verify_success:
                print("✅ QLib初始化成功，使用项目路径")
            else:
                print("❌ QLib仍在使用默认路径")
                
        except Exception as e:
            print(f"❌ QLib初始化失败: {e}")
    else:
        print("❌ QLib路径强制设置失败")
    
    print("\n" + "=" * 70)