# -*- coding: utf-8 -*-
"""
Backend配置模块

解决config目录与config.py文件的冲突问题
"""

import sys
from pathlib import Path

# 导入xtquant配置（TdxQuant已移除）
from .xtquant_multi_instance import *

# 导入配置验证器（新增）
try:
    from .validator import ConfigValidator, validate_config, ConfigValidationError
    __all__ = ['ConfigValidator', 'validate_config', 'ConfigValidationError']
except ImportError:
    pass  # 配置验证器是可选的

# 从父目录的config.py导入settings
config_file_path = Path(__file__).parent.parent / 'config.py'
if config_file_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("config_settings", config_file_path)
    config_settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_settings)
    settings = config_settings.settings
    get_settings = config_settings.get_settings
else:
    # 如果config.py不存在，尝试创建默认settings
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        PROJECT_NAME: str = "MyQuant"
        VERSION: str = "9.0.0"
        HOST: str = "0.0.0.0"
        PORT: int = 8002
        DEBUG: bool = False

        class Config:
            env_file = ".env"
            case_sensitive = True
            extra = "ignore"

    settings = Settings()

    def get_settings():
        return settings
