"""
V5 适配器工厂

提供统一的适配器创建接口
"""

from typing import Optional
import logging

from .base import DataAdapter, V5DataAdapter
from .pytdx_adapter import V5PyTdxAdapter, create_pytdx_adapter
from .pytdx_pool_adapter import V5PyTdxPoolAdapter, create_pytdx_pool_adapter
from .xtquant_adapter import V5XtQuantAdapter, create_xtquant_adapter
from .tdxquant_adapter import V5TdxQuantAdapter, create_tdxquant_adapter
from .localdb_adapter import V5LocalDBAdapter, create_localdb_adapter
from .tdxlocal_adapter import V5TdxLocalAdapter, create_tdxlocal_adapter
from .hotdb_adapter import V5HotDBAdapter, create_hotdb_adapter

logger = logging.getLogger(__name__)


class AdapterFactory:
    """适配器工厂

    根据名称创建对应的 V5 适配器实例，每个适配器名称只创建一个实例（单例缓存）
    """

    _registry = {
        'pytdx': create_pytdx_pool_adapter,  # 默认：连接池版（M+H+P架构，高可用）
        'pytdx_simple': create_pytdx_adapter,  # 简单版（无连接池，兼容回退）
        'xtquant': create_xtquant_adapter,
        'tdxquant': create_tdxquant_adapter,
        'localdb': create_localdb_adapter,
        'tdxlocal': create_tdxlocal_adapter,
        'hotdb': create_hotdb_adapter,  # 热数据库
    }

    # 单例缓存：每个 name 只创建一次实例
    _instances: dict = {}

    @classmethod
    def create(cls, name: str) -> Optional[DataAdapter]:
        """获取适配器实例（已存在则复用，否则创建）

        Args:
            name: 适配器名称 (pytdx/xtquant/tdxquant/localdb/tdxlocal)

        Returns:
            适配器实例，如果名称不支持则返回 None
        """
        key = name.lower()

        # 已有实例直接返回
        if key in cls._instances:
            return cls._instances[key]

        factory = cls._registry.get(key)
        if factory is None:
            logger.warning(f"Unknown adapter name: {name}")
            return None

        try:
            instance = factory()
            cls._instances[key] = instance
            return instance
        except Exception as e:
            logger.error(f"Failed to create adapter {name}: {e}")
            return None

    @classmethod
    def register(cls, name: str, factory) -> None:
        """注册新的适配器工厂

        Args:
            name: 适配器名称
            factory: 工厂函数
        """
        cls._registry[name.lower()] = factory

    @classmethod
    def list_adapters(cls) -> list:
        """列出所有已注册的适配器"""
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """检查适配器是否已注册"""
        return name.lower() in cls._registry


def get_v5_adapter(name: str) -> Optional[DataAdapter]:
    """获取 V5 适配器实例（便捷函数）

    Args:
        name: 适配器名称

    Returns:
        适配器实例
    """
    return AdapterFactory.create(name)


# 别名，保持兼容性
get_adapter = get_v5_adapter


# 注册到全局适配器注册表
from .base import register_adapter
for adapter_name in AdapterFactory.list_adapters():
    register_adapter(
        adapter_name,
        lambda name=adapter_name: get_v5_adapter(name)
    )
