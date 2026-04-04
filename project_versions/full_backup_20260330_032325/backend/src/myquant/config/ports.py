#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一端口配置 - MyQuant v10.0.0

> 创建日期: 2026-02-06
> 版本: v10.0.0
> 目的: 消除端口硬编码，集中管理所有服务端口

使用方式:
    from backend.config.ports import PortConfig
    api_port = PortConfig.API_PORT
    ws_port = PortConfig.WS_PORT
"""

import os
from typing import Dict


class PortConfig:
    """
    统一端口配置

    所有服务端口的单一真实来源（SSOT）
    支持通过环境变量覆盖
    """

    # ===== 核心服务端口 =====

    # 主API服务端口
    API_PORT: int = int(os.getenv('MYQUANT_API_PORT', '8000'))

    # WebSocket服务端口
    WS_PORT: int = int(os.getenv('MYQUANT_WS_PORT', '8765'))

    # Data Hub服务端口（备用）
    DATA_HUB_PORT: int = int(os.getenv('MYQUANT_DATA_HUB_PORT', '8001'))

    # Qlib服务端口（备用）
    QLIB_PORT: int = int(os.getenv('MYQUANT_QLIB_PORT', '8002'))

    # AI引擎服务端口（备用）
    AI_ENGINE_PORT: int = int(os.getenv('MYQUANT_AI_ENGINE_PORT', '8003'))

    # 风险管理服务端口（备用）
    RISK_PORT: int = int(os.getenv('MYQUANT_RISK_PORT', '8004'))

    # 交易执行服务端口（备用）
    TRADING_PORT: int = int(os.getenv('MYQUANT_TRADING_PORT', '8005'))

    # ===== 基础设施端口 =====

    # Redis端口
    REDIS_PORT: int = int(os.getenv('MYQUANT_REDIS_PORT', '6379'))

    # PostgreSQL端口
    POSTGRES_PORT: int = int(os.getenv('MYQUANT_POSTGRES_PORT', '5432'))

    # MLflow端口
    MLFLOW_PORT: int = int(os.getenv('MYQUANT_MLFLOW_PORT', '5000'))

    # MinIO端口
    MINIO_PORT: int = int(os.getenv('MYQUANT_MINIO_PORT', '9000'))
    MINIO_CONSOLE_PORT: int = int(os.getenv('MYQUANT_MINIO_CONSOLE_PORT', '9001'))

    # Prometheus端口
    PROMETHEUS_PORT: int = int(os.getenv('MYQUANT_PROMETHEUS_PORT', '9090'))

    # Grafana端口
    GRAFANA_PORT: int = int(os.getenv('MYQUANT_GRAFANA_PORT', '3000'))

    # ===== 主机配置 =====

    # 默认主机
    API_HOST: str = os.getenv('MYQUANT_API_HOST', '0.0.0.0')
    WS_HOST: str = os.getenv('MYQUANT_WS_HOST', '0.0.0.0')

    # Redis主机
    REDIS_HOST: str = os.getenv('MYQUANT_REDIS_HOST', 'localhost')

    # PostgreSQL主机
    POSTGRES_HOST: str = os.getenv('MYQUANT_POSTGRES_HOST', 'localhost')

    # ===== URL生成方法 =====

    @classmethod
    def get_api_url(cls, path: str = "") -> str:
        """获取API完整URL"""
        return f"http://{cls.API_HOST}:{cls.API_PORT}{path}"

    @classmethod
    def get_ws_url(cls, path: str = "") -> str:
        """获取WebSocket完整URL"""
        return f"ws://{cls.WS_HOST}:{cls.WS_PORT}{path}"

    @classmethod
    def get_redis_url(cls, db: int = 0) -> str:
        """获取Redis连接URL"""
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{db}"

    @classmethod
    def get_postgres_url(cls, database: str = "myquant") -> str:
        """获取PostgreSQL连接URL"""
        return f"postgresql://{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{database}"

    @classmethod
    def get_mlflow_url(cls, path: str = "") -> str:
        """获取MLflow URL"""
        return f"http://localhost:{cls.MLFLOW_PORT}{path}"

    @classmethod
    def get_data_hub_url(cls, path: str = "") -> str:
        """获取Data Hub服务URL"""
        return f"http://localhost:{cls.DATA_HUB_PORT}{path}"

    @classmethod
    def get_qlib_url(cls, path: str = "") -> str:
        """获取QLib服务URL"""
        return f"http://localhost:{cls.QLIB_PORT}{path}"

    @classmethod
    def get_ai_engine_url(cls, path: str = "") -> str:
        """获取AI引擎服务URL"""
        return f"http://localhost:{cls.AI_ENGINE_PORT}{path}"

    @classmethod
    def get_risk_url(cls, path: str = "") -> str:
        """获取风险管理服务URL"""
        return f"http://localhost:{cls.RISK_PORT}{path}"

    @classmethod
    def get_trading_url(cls, path: str = "") -> str:
        """获取交易执行服务URL"""
        return f"http://localhost:{cls.TRADING_PORT}{path}"

    @classmethod
    def get_all_ports(cls) -> Dict[str, int]:
        """获取所有端口配置（用于调试和文档）"""
        return {
            'API服务': cls.API_PORT,
            'WebSocket服务': cls.WS_PORT,
            'Data Hub': cls.DATA_HUB_PORT,
            'QLib服务': cls.QLIB_PORT,
            'AI引擎服务': cls.AI_ENGINE_PORT,
            '风险管理服务': cls.RISK_PORT,
            '交易执行服务': cls.TRADING_PORT,
            'Redis': cls.REDIS_PORT,
            'PostgreSQL': cls.POSTGRES_PORT,
            'MLflow': cls.MLFLOW_PORT,
            'MinIO': cls.MINIO_PORT,
            'MinIO Console': cls.MINIO_CONSOLE_PORT,
            'Prometheus': cls.PROMETHEUS_PORT,
            'Grafana': cls.GRAFANA_PORT,
        }

    @classmethod
    def print_port_config(cls):
        """打印端口配置（用于启动日志）"""
        print("=" * 60)
        print("MyQuant v10.0.0 - 端口配置")
        print("=" * 60)
        for name, port in cls.get_all_ports().items():
            print(f"  {name:20s}: {port}")
        print("=" * 60)


# ===== 便捷导出 =====

# 仅导出常量，不导出类（避免实例化）
__all__ = [
    'PortConfig',
    'get_api_url',
    'get_ws_url',
    'get_redis_url',
    'get_postgres_url',
]


# ===== 使用示例 =====

if __name__ == "__main__":
    # 打印端口配置
    PortConfig.print_port_config()

    # 生成URL示例
    print("\nURL示例:")
    print(f"  API URL: {PortConfig.get_api_url('/api/v1/health')}")
    print(f"  WS URL:  {PortConfig.get_ws_url('/ws/quotes')}")
    print(f"  Redis:   {PortConfig.get_redis_url(0)}")
    print(f"  MLflow:  {PortConfig.get_mlflow_url()}")
