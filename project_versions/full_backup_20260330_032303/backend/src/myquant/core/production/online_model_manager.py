# -*- coding: utf-8 -*-
"""
Production阶段 - 在线模型管理服务
================================
职责：
- 模型版本管理（v1.0, v1.1, v2.0...）
- 模型热加载（不中断服务）
- 模型A/B测试
- 模型回滚

QLib集成：
- 集成QLib Workflow的R对象进行模型管理
- 支持QLib训练的模型格式

架构层次：
- Production阶段：生产级模型管理
- P0核心功能
"""

from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import threading
import json
import os

try:
    from qlib.workflow import R
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False
    logger.warning("QLib未安装，OnlineModelManager将使用模拟模式")


class ModelStatus(Enum):
    """模型状态"""
    REGISTERED = "registered"     # 已注册
    LOADING = "loading"           # 加载中
    READY = "ready"               # 就绪
    ACTIVE = "active"             # 活跃（正在使用）
    DEPRECATED = "deprecated"     # 已废弃
    ERROR = "error"               # 错误


class ABTestStatus(Enum):
    """A/B测试状态"""
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ModelVersion:
    """模型版本信息"""
    model_id: str                          # 模型ID (如 xgb_v1.1)
    model_name: str                        # 模型名称 (如 xgb_classification)
    version: str                           # 版本号 (如 1.1)
    model_path: str                        # 模型文件路径
    status: ModelStatus = ModelStatus.REGISTERED
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    loaded_at: Optional[datetime] = None
    load_time_ms: float = 0.0
    model_object: Any = None               # 实际加载的模型对象
    ic_score: float = 0.0                  # IC评分
    prediction_count: int = 0              # 预测次数


@dataclass
class ABTestConfig:
    """A/B测试配置"""
    test_id: str                           # 测试ID
    model_a_id: str                        # A模型ID
    model_b_id: str                        # B模型ID
    traffic_split: float = 0.5             # 流量分配 (0.0-1.0)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: ABTestStatus = ABTestStatus.RUNNING
    metrics_a: Dict[str, float] = field(default_factory=dict)
    metrics_b: Dict[str, float] = field(default_factory=dict)


class OnlineModelManager:
    """
    在线模型管理器

    功能：
    - 模型版本管理
    - 模型热加载（不中断服务）
    - 模型A/B测试
    - 模型回滚

    性能要求：
    - 热加载时间 < 100ms
    - 支持多模型并行运行
    """

    def __init__(self, models_dir: str = "models"):
        """
        初始化在线模型管理器

        Args:
            models_dir: 模型存储目录
        """
        self.models_dir = models_dir

        # 模型版本注册表 {model_name: {version: ModelVersion}}
        self._versions: Dict[str, Dict[str, ModelVersion]] = {}

        # 当前活跃模型 {model_name: model_id}
        self._active_models: Dict[str, str] = {}

        # A/B测试配置 {test_id: ABTestConfig}
        self._ab_tests: Dict[str, ABTestConfig] = {}

        # 模型锁（确保线程安全）
        self._lock = threading.RLock()

        # 历史记录
        self._switch_history: List[Dict[str, Any]] = []

        logger.info("✅ OnlineModelManager初始化完成")

    # ==================== 模型注册 ====================

    def register_model(
        self,
        model_name: str,
        model_id: str,
        model_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ModelVersion:
        """
        注册模型版本

        Args:
            model_name: 模型名称
            model_id: 模型ID (如 xgb_v1.1)
            model_path: 模型文件路径
            metadata: 模型元数据

        Returns:
            ModelVersion对象
        """
        with self._lock:
            # 解析版本号
            version = self._parse_version(model_id)

            # 创建版本对象
            model_version = ModelVersion(
                model_id=model_id,
                model_name=model_name,
                version=version,
                model_path=model_path,
                metadata=metadata or {}
            )

            # 注册到版本表
            if model_name not in self._versions:
                self._versions[model_name] = {}
            self._versions[model_name][version] = model_version

            logger.info(f"模型注册成功: {model_id}, 版本: {version}")

            return model_version

    def _parse_version(self, model_id: str) -> str:
        """从model_id解析版本号"""
        # 假设格式为 name_vX.X 或 name vX.X
        parts = model_id.split('_v')
        if len(parts) > 1:
            return f"v{parts[-1]}"
        parts = model_id.split(' v')
        if len(parts) > 1:
            return f"v{parts[-1]}"
        return "v1.0"

    # ==================== 模型加载 ====================

    def load_model(
        self,
        model_name: str,
        target_version: Optional[str] = None
    ) -> bool:
        """
        热加载模型

        Args:
            model_name: 模型名称
            target_version: 目标版本（None则加载最新版本）

        Returns:
            是否加载成功
        """
        with self._lock:
            start_time = datetime.now()

            # 获取目标版本
            if target_version is None:
                target_version = self._get_latest_version(model_name)
                if target_version is None:
                    logger.error(f"未找到模型: {model_name}")
                    return False

            # 获取版本对象
            version_obj = self._get_version(model_name, target_version)
            if version_obj is None:
                logger.error(f"未找到版本: {model_name}/{target_version}")
                return False

            try:
                version_obj.status = ModelStatus.LOADING

                # 加载模型
                model_object = self._load_model_file(version_obj.model_path)

                if model_object is not None:
                    version_obj.model_object = model_object
                    version_obj.status = ModelStatus.READY
                    version_obj.loaded_at = datetime.now()

                    load_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                    version_obj.load_time_ms = load_time_ms

                    logger.info(f"模型加载成功: {version_obj.model_id}, 耗时: {load_time_ms:.1f}ms")
                    return True
                else:
                    version_obj.status = ModelStatus.ERROR
                    logger.error(f"模型加载失败: {version_obj.model_path}")
                    return False

            except Exception as e:
                version_obj.status = ModelStatus.ERROR
                logger.error(f"模型加载异常: {e}")
                return False

    def _load_model_file(self, model_path: str) -> Any:
        """
        加载模型文件

        Args:
            model_path: 模型文件路径

        Returns:
            模型对象
        """
        try:
            if QLIB_AVAILABLE:
                # 尝试使用QLib加载
                import pickle
                full_path = os.path.join(self.models_dir, model_path)
                if os.path.exists(full_path):
                    with open(full_path, 'rb') as f:
                        return pickle.load(f)

            # 模拟加载
            logger.warning(f"使用模拟模式加载模型: {model_path}")
            return {"model_path": model_path, "type": "mock"}

        except Exception as e:
            logger.error(f"加载模型文件失败: {e}")
            return None

    def _get_latest_version(self, model_name: str) -> Optional[str]:
        """获取最新版本"""
        if model_name not in self._versions:
            return None

        versions = list(self._versions[model_name].keys())
        if not versions:
            return None

        # 按版本号排序，返回最新
        versions.sort(key=self._version_key, reverse=True)
        return versions[0]

    def _version_key(self, version: str) -> tuple:
        """版本号排序键"""
        # 解析 vX.Y 格式
        try:
            parts = version.replace('v', '').split('.')
            return tuple(int(p) for p in parts)
        except:
            return (0, 0)

    def _get_version(self, model_name: str, version: str) -> Optional[ModelVersion]:
        """获取版本对象"""
        return self._versions.get(model_name, {}).get(version)

    # ==================== 模型切换 ====================

    def switch_model(
        self,
        model_name: str,
        target_version: str,
        auto_load: bool = True
    ) -> bool:
        """
        切换活跃模型

        Args:
            model_name: 模型名称
            target_version: 目标版本
            auto_load: 是否自动加载（如果未加载）

        Returns:
            是否切换成功
        """
        with self._lock:
            version_obj = self._get_version(model_name, target_version)
            if version_obj is None:
                logger.error(f"未找到版本: {model_name}/{target_version}")
                return False

            # 如果模型未加载，尝试加载
            if version_obj.status != ModelStatus.READY:
                if auto_load:
                    if not self.load_model(model_name, target_version):
                        return False
                else:
                    logger.error(f"模型未加载: {version_obj.model_id}")
                    return False

            # 记录旧版本
            old_model_id = self._active_models.get(model_name)

            # 切换活跃模型
            self._active_models[model_name] = version_obj.model_id
            version_obj.status = ModelStatus.ACTIVE

            # 将旧模型设为就绪状态
            if old_model_id:
                old_version = self._get_version(model_name, self._parse_version(old_model_id))
                if old_version and old_version != version_obj:
                    old_version.status = ModelStatus.READY

            # 记录历史
            self._switch_history.append({
                "model_name": model_name,
                "from_version": old_model_id,
                "to_version": version_obj.model_id,
                "timestamp": datetime.now().isoformat()
            })

            logger.info(f"模型切换成功: {old_model_id} -> {version_obj.model_id}")
            return True

    def rollback_model(self, model_name: str) -> bool:
        """
        回滚到上一版本

        Args:
            model_name: 模型名称

        Returns:
            是否回滚成功
        """
        # 查找最近的切换记录
        for record in reversed(self._switch_history):
            if record["model_name"] == model_name and record["from_version"]:
                return self.switch_model(
                    model_name,
                    self._parse_version(record["from_version"])
                )

        logger.error(f"未找到可回滚的版本: {model_name}")
        return False

    # ==================== A/B测试 ====================

    def start_ab_test(
        self,
        model_name: str,
        model_a_version: str,
        model_b_version: str,
        traffic_split: float = 0.5
    ) -> Optional[str]:
        """
        启动A/B测试

        Args:
            model_name: 模型名称
            model_a_version: A模型版本
            model_b_version: B模型版本
            traffic_split: 流量分配 (0.0-1.0, A模型占比)

        Returns:
            测试ID
        """
        with self._lock:
            # 确保两个模型都已加载
            if not self.load_model(model_name, model_a_version):
                logger.error(f"A模型加载失败: {model_a_version}")
                return None
            if not self.load_model(model_name, model_b_version):
                logger.error(f"B模型加载失败: {model_b_version}")
                return None

            # 生成测试ID
            test_id = f"ab_{model_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # 创建测试配置
            ab_test = ABTestConfig(
                test_id=test_id,
                model_a_id=f"{model_name}_{model_a_version}",
                model_b_id=f"{model_name}_{model_b_version}",
                traffic_split=traffic_split
            )

            self._ab_tests[test_id] = ab_test

            logger.info(f"A/B测试启动: {test_id}, A:{model_a_version}, B:{model_b_version}")
            return test_id

    def get_ab_test_model(self, test_id: str) -> Optional[str]:
        """
        根据A/B测试配置返回模型ID

        Args:
            test_id: 测试ID

        Returns:
            模型ID
        """
        ab_test = self._ab_tests.get(test_id)
        if ab_test is None or ab_test.status != ABTestStatus.RUNNING:
            return None

        # 根据流量分配决定使用哪个模型
        import random
        if random.random() < ab_test.traffic_split:
            return ab_test.model_a_id
        else:
            return ab_test.model_b_id

    def stop_ab_test(self, test_id: str) -> bool:
        """
        停止A/B测试

        Args:
            test_id: 测试ID

        Returns:
            是否停止成功
        """
        ab_test = self._ab_tests.get(test_id)
        if ab_test is None:
            return False

        ab_test.status = ABTestStatus.COMPLETED
        ab_test.end_time = datetime.now()
        logger.info(f"A/B测试停止: {test_id}")
        return True

    # ==================== 查询方法 ====================

    def get_model_versions(self, model_name: str) -> List[ModelVersion]:
        """
        获取模型的所有版本

        Args:
            model_name: 模型名称

        Returns:
            版本列表
        """
        return list(self._versions.get(model_name, {}).values())

    def get_active_model(self, model_name: str) -> Optional[ModelVersion]:
        """
        获取当前活跃模型

        Args:
            model_name: 模型名称

        Returns:
            ModelVersion对象
        """
        model_id = self._active_models.get(model_name)
        if model_id is None:
            return None

        version = self._parse_version(model_id)
        return self._get_version(model_name, version)

    def get_model_object(self, model_name: str) -> Any:
        """
        获取模型对象（用于预测）

        Args:
            model_name: 模型名称

        Returns:
            模型对象
        """
        version_obj = self.get_active_model(model_name)
        if version_obj is None:
            # 尝试加载最新版本
            latest = self._get_latest_version(model_name)
            if latest and self.load_model(model_name, latest):
                self.switch_model(model_name, latest)
                version_obj = self.get_active_model(model_name)

        return version_obj.model_object if version_obj else None

    def get_switch_history(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取切换历史

        Args:
            model_name: 模型名称（None返回全部）

        Returns:
            切换历史列表
        """
        if model_name is None:
            return self._switch_history

        return [h for h in self._switch_history if h["model_name"] == model_name]


# ==================== 单例模式 ====================

_model_manager_instance: Optional[OnlineModelManager] = None


def get_model_manager() -> OnlineModelManager:
    """获取OnlineModelManager单例"""
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = OnlineModelManager()
    return _model_manager_instance
