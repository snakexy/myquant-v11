# -*- coding: utf-8 -*-
"""
配置兼容层
==========

提供向后兼容的API，平滑迁移到新配置系统

作者: MyQuant v10.0.0 Team
创建时间: 2026-02-04
"""

from typing import List, Dict, Any, Optional
from backend.config.app_config import config


# ============================================================================
# 1. XtQuant多实例配置兼容
# ============================================================================

def get_xtquant_instances() -> List[Dict[str, Any]]:
    """
    获取XtQuant实例列表（兼容旧格式）

    Returns:
        实例配置列表
    """
    if not hasattr(config.datasource.xtquant, 'instances') or not config.datasource.xtquant.instances:
        # 如果新配置没有实例，使用默认配置
        return []

    return [
        {
            "name": inst.name,
            "account": inst.account,
            "enabled": inst.enabled,
            "market": inst.market,
            "max_subscriptions": inst.max_subscriptions,
            "install_path": inst.install_path,
            "data_path": inst.data_path,
            "executable": inst.executable,
            "can_trade": inst.can_trade,
            "is_vip": inst.is_vip,
        }
        for inst in config.datasource.xtquant.instances
    ]


def get_enable_multi_instance() -> bool:
    """获取是否启用多实例模式"""
    if hasattr(config.datasource.xtquant, 'enable_multi_instance'):
        return config.datasource.xtquant.enable_multi_instance
    return False


# 向后兼容导出
ENABLE_MULTI_INSTANCE = get_enable_multi_instance()
XTQUANT_INSTANCES = get_xtquant_instances()


# ============================================================================
# 2. 数据源配置兼容
# ============================================================================

def get_data_source_config() -> Dict[str, List[Dict[str, Any]]]:
    """
    获取数据源分层配置（兼容旧DATA_SOURCE_CONFIG格式）

    Returns:
        分层数据源配置
    """
    # 简化的分层配置，从新配置系统映射
    config_map = {
        'L0': [  # 订阅缓存
            {
                'name': 'xtquant_dual',
                'priority': 1,
                'enabled': config.datasource.xtquant.enabled,
                'speed': '<1ms (订阅缓存)',
                'availability': '交易时间',
                'description': 'XtQuant订阅缓存'
            }
        ],
        'L1': [  # 实时快照
            {
                'name': 'xtquant_dual',
                'priority': 1,
                'enabled': config.datasource.xtquant.enabled,
                'speed': '<1ms',
                'availability': '24/7',
                'description': 'XtQuant实时快照'
            },
            {
                'name': 'pytdx_server1',
                'priority': 2,
                'enabled': config.datasource.pytdx.enabled,
                'speed': '~10ms',
                'availability': '24/7',
                'description': 'PyTdx批量API'
            },
            {
                'name': 'local_db',
                'priority': 3,
                'enabled': config.datasource.localdb.enabled,
                'speed': '10-100ms',
                'availability': '离线可用',
                'description': '本地数据库'
            }
        ],
        'L2': [  # 历史K线（短期）
            {
                'name': 'local_db',
                'priority': 1,
                'enabled': config.datasource.localdb.enabled,
                'speed': '7ms',
                'availability': '离线可用',
                'description': '本地数据库'
            }
        ],
        'L3': [  # 历史K线（长期）
            {
                'name': 'local_db',
                'priority': 1,
                'enabled': config.datasource.localdb.enabled,
                'speed': '5ms',
                'availability': '离线可用',
                'description': '本地数据库'
            }
        ]
    }

    return config_map


# 向后兼容导出
DATA_SOURCE_CONFIG = get_data_source_config()


# ============================================================================
# 3. 默认配置兼容
# ============================================================================

def get_default_config() -> Dict[str, Any]:
    """获取默认配置"""
    return {
        'enable_auto_fallback': config.datasource.auto_switch,
        'load_balancing_ratio': 0.97,  # 默认值
        'enable_cache': True,  # 从config.cache.strategy读取
        'cache_ttl': config.cache.quote_ttl,
        'enable_stock_name_service': True,
        'use_unified_format': True,
        'filter_futures_fields': True,
    }


DEFAULT_CONFIG = get_default_config()


# ============================================================================
# 4. 辅助函数兼容
# ============================================================================

def get_enabled_sources(data_type: str) -> List[Dict[str, Any]]:
    """
    获取指定数据类型的已启用数据源（兼容旧API）

    Args:
        data_type: L0/L1/L2/L3

    Returns:
        已启用数据源列表
    """
    sources = DATA_SOURCE_CONFIG.get(data_type, [])
    return [s for s in sources if s.get('enabled', False)]


def get_source_by_name(data_type: str, source_name: str) -> Optional[Dict[str, Any]]:
    """
    根据名称获取数据源配置（兼容旧API）

    Args:
        data_type: L0/L1/L2/L3
        source_name: 数据源名称

    Returns:
        数据源配置，如果未找到返回None
    """
    sources = DATA_SOURCE_CONFIG.get(data_type, [])
    for source in sources:
        if source['name'] == source_name:
            return source
    return None


def get_priority_order(data_type: str) -> List[str]:
    """
    获取数据源优先级顺序（从高到低）（兼容旧API）

    Args:
        data_type: L0/L1/L2/L3

    Returns:
        数据源名称列表（按优先级从高到低）
    """
    enabled = get_enabled_sources(data_type)
    return [s['name'] for s in sorted(enabled, key=lambda x: x['priority'])]


def is_source_enabled(data_type: str, source_name: str) -> bool:
    """
    检查数据源是否启用（兼容旧API）

    Args:
        data_type: L0/L1/L2/L3
        source_name: 数据源名称

    Returns:
        是否启用
    """
    source = get_source_by_name(data_type, source_name)
    return source is not None and source.get('enabled', False)


def disable_source(data_type: str, source_name: str):
    """
    禁用数据源（运行时修改）（兼容旧API）

    Args:
        data_type: L0/L1/L2/L3
        source_name: 数据源名称

    注意：这是兼容函数，实际修改需要重新加载配置
    """
    # TODO: 实现运行时禁用逻辑
    pass


def enable_source(data_type: str, source_name: str):
    """
    启用数据源（运行时修改）（兼容旧API）

    Args:
        data_type: L0/L1/L2/L3
        source_name: 数据源名称

    注意：这是兼容函数，实际修改需要重新加载配置
    """
    # TODO: 实现运行时启用逻辑
    pass


def get_config(key: str, default=None):
    """
    获取配置项（兼容旧API）

    Args:
        key: 配置键
        default: 默认值

    Returns:
        配置值
    """
    return DEFAULT_CONFIG.get(key, default)


def set_config(key: str, value: Any):
    """
    设置配置项（运行时修改）（兼容旧API）

    Args:
        key: 配置键
        value: 配置值

    注意：这是兼容函数，实际修改需要重新加载配置
    """
    DEFAULT_CONFIG[key] = value


# ============================================================================
# 5. 配置同步函数
# ============================================================================

def sync_config_from_legacy():
    """
    从旧配置文件同步到新配置系统

    在应用启动时调用此函数，确保新旧配置一致
    """
    global ENABLE_MULTI_INSTANCE, XTQUANT_INSTANCES, DATA_SOURCE_CONFIG

    # 重新读取配置
    ENABLE_MULTI_INSTANCE = get_enable_multi_instance()
    XTQUANT_INSTANCES = get_xtquant_instances()
    DATA_SOURCE_CONFIG = get_data_source_config()


# ============================================================================
# 导出所有兼容API
# ============================================================================

__all__ = [
    # XtQuant配置
    'ENABLE_MULTI_INSTANCE',
    'XTQUANT_INSTANCES',
    'get_xtquant_instances',
    'get_enable_multi_instance',

    # 数据源配置
    'DATA_SOURCE_CONFIG',
    'DEFAULT_CONFIG',
    'get_data_source_config',
    'get_default_config',

    # 辅助函数
    'get_enabled_sources',
    'get_source_by_name',
    'get_priority_order',
    'is_source_enabled',
    'disable_source',
    'enable_source',
    'get_config',
    'set_config',

    # 配置同步
    'sync_config_from_legacy',
]
