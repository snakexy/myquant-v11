"""
模型版本控制

提供模型的版本管理、比较和回滚功能
"""

import logging
import json
import os
import shutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .model_registry import ModelMetadata


class VersionStatus(Enum):
    """版本状态"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class VersionInfo:
    """版本信息"""
    version: str
    status: str
    created_at: str
    updated_at: str
    changelog: str
    tags: List[str]
    parent_version: str = ""
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionInfo':
        """从字典创建"""
        return cls(**data)


@dataclass
class VersionComparison:
    """版本比较结果"""
    version1: str
    version2: str
    comparison_date: str
    performance_diff: Dict[str, float]
    parameter_diff: Dict[str, Any]
    compatibility: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionComparison':
        """从字典创建"""
        return cls(**data)


class ModelVersionControl:
    """
    模型版本控制管理器

    负责模型的版本管理、比较、回滚和发布
    """

    def __init__(self,
                 registry_path: str = "model_versions",
                 storage_path: str = "model_storage"):
        """
        初始化版本控制管理器

        Parameters
        ----------
        registry_path : str
            版本注册表路径
        storage_path : str
            模型存储路径
        """
        self.registry_path = registry_path
        self.storage_path = storage_path
        self.logger = logging.getLogger(__name__)
        self._versions: Dict[str, Dict[str, VersionInfo]] = {}
        self._comparisons: Dict[str, VersionComparison] = {}

        # 创建目录
        os.makedirs(registry_path, exist_ok=True)
        os.makedirs(storage_path, exist_ok=True)

        # 加载版本信息
        self._load_versions()
        self._load_comparisons()

        self.logger.info(f"模型版本控制管理器初始化完成")

    def create_version(self,
                       model_name: str,
                       version: str,
                       model_metadata: ModelMetadata,
                       changelog: str = "",
                       tags: List[str] = None,
                       status: str = VersionStatus.DEVELOPMENT.value,
                       parent_version: str = "") -> bool:
        """
        创建新版本

        Parameters
        ----------
        model_name : str
            模型名称
        version : str
            版本号
        model_metadata : ModelMetadata
            模型元数据
        changelog : str
            更新日志
        tags : List[str]
            版本标签
        status : str
            版本状态
        parent_version : str
            父版本

        Returns
        -------
        bool
            是否创建成功
        """
        if model_name not in self._versions:
            self._versions[model_name] = {}

        if version in self._versions[model_name]:
            self.logger.error(f"版本已存在: {model_name} v{version}")
            return False

        # 复制模型文件到版本存储
        source_path = model_metadata.file_path
        target_path = os.path.join(
            self.storage_path, model_name, f"{version}.pkl"
        )
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        try:
            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)
            else:
                self.logger.warning(f"源文件不存在: {source_path}")
        except Exception as e:
            self.logger.error(f"复制模型文件失败: {e}")
            return False

        # 创建版本信息
        version_info = VersionInfo(
            version=version,
            status=status,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            changelog=changelog,
            tags=tags or [],
            parent_version=parent_version,
            metadata=model_metadata.to_dict()
        )

        self._versions[model_name][version] = version_info
        self._save_versions()

        self.logger.info(f"创建版本: {model_name} v{version}")
        return True

    def get_version_info(self,
                         model_name: str,
                         version: str = "latest") -> Optional[VersionInfo]:
        """
        获取版本信息

        Parameters
        ----------
        model_name : str
            模型名称
        version : str
            版本号，默认为最新版本

        Returns
        -------
        Optional[VersionInfo]
            版本信息
        """
        if model_name not in self._versions:
            return None

        if version == "latest":
            # 获取最新版本
            versions = list(self._versions[model_name].keys())
            if not versions:
                return None
            version = max(versions)

        return self._versions[model_name].get(version)

    def list_versions(self,
                      model_name: str,
                      status: str = None) -> List[Dict[str, Any]]:
        """
        列出模型的所有版本

        Parameters
        ----------
        model_name : str
            模型名称
        status : str
            状态过滤

        Returns
        -------
        List[Dict[str, Any]]
            版本列表
        """
        if model_name not in self._versions:
            return []

        versions = []
        for version_info in self._versions[model_name].values():
            if status and version_info.status != status:
                continue
            versions.append(version_info.to_dict())

        # 按创建时间排序
        versions.sort(key=lambda x: x['created_at'], reverse=True)
        return versions

    def update_version_status(self,
                              model_name: str,
                              version: str,
                              status: str) -> bool:
        """
        更新版本状态

        Parameters
        ----------
        model_name : str
            模型名称
        version : str
            版本号
        status : str
            新状态

        Returns
        -------
        bool
            是否更新成功
        """
        version_info = self.get_version_info(model_name, version)
        if not version_info:
            return False

        version_info.status = status
        version_info.updated_at = datetime.now().isoformat()

        self._save_versions()
        self.logger.info(f"更新版本状态: {model_name} v{version} -> {status}")
        return True

    def compare_versions(self,
                         model_name: str,
                         version1: str,
                         version2: str) -> Optional[VersionComparison]:
        """
        比较两个版本

        Parameters
        ----------
        model_name : str
            模型名称
        version1 : str
            版本1
        version2 : str
            版本2

        Returns
        -------
        Optional[VersionComparison]
            比较结果
        """
        info1 = self.get_version_info(model_name, version1)
        info2 = self.get_version_info(model_name, version2)

        if not info1 or not info2:
            return None

        # 计算性能差异
        perf_diff = {}
        if info1.metadata and info2.metadata:
            metrics1 = info1.metadata.get('performance_metrics', {})
            metrics2 = info2.metadata.get('performance_metrics', {})

            for key in set(metrics1.keys()) | set(metrics2.keys()):
                val1 = metrics1.get(key, 0)
                val2 = metrics2.get(key, 0)
                perf_diff[key] = val2 - val1

        # 计算参数差异
        param_diff = {}
        if info1.metadata and info2.metadata:
            params1 = info1.metadata.get('hyperparameters', {})
            params2 = info2.metadata.get('hyperparameters', {})

            for key in set(params1.keys()) | set(params2.keys()):
                val1 = params1.get(key)
                val2 = params2.get(key)
                if val1 != val2:
                    param_diff[key] = {'old': val1, 'new': val2}

        # 生成兼容性和建议
        compatibility = "compatible"
        recommendation = "upgrade"

        if perf_diff.get('accuracy', 0) < -0.05:
            compatibility = "degraded"
            recommendation = "keep_old"
        elif perf_diff.get('accuracy', 0) > 0.05:
            recommendation = "upgrade"

        # 创建比较结果
        comparison = VersionComparison(
            version1=version1,
            version2=version2,
            comparison_date=datetime.now().isoformat(),
            performance_diff=perf_diff,
            parameter_diff=param_diff,
            compatibility=compatibility,
            recommendation=recommendation
        )

        # 保存比较结果
        comparison_key = f"{model_name}_{version1}_{version2}"
        self._comparisons[comparison_key] = comparison
        self._save_comparisons()

        return comparison

    def get_comparison_result(self,
                              model_name: str,
                              version1: str,
                              version2: str) -> Optional[VersionComparison]:
        """
        获取比较结果

        Parameters
        ----------
        model_name : str
            模型名称
        version1 : str
            版本1
        version2 : str
            版本2

        Returns
        -------
        Optional[VersionComparison]
            比较结果
        """
        comparison_key = f"{model_name}_{version1}_{version2}"
        return self._comparisons.get(comparison_key)

    def rollback_version(self,
                         model_name: str,
                         from_version: str,
                         to_version: str) -> bool:
        """
        回滚到指定版本

        Parameters
        ----------
        model_name : str
            模型名称
        from_version : str
            当前版本
        to_version : str
            目标版本

        Returns
        -------
        bool
            是否回滚成功
        """
        from_info = self.get_version_info(model_name, from_version)
        to_info = self.get_version_info(model_name, to_version)

        if not from_info or not to_info:
            return False

        # 检查回滚路径
        current_version = from_version
        while current_version:
            if current_version == to_version:
                break
            info = self.get_version_info(model_name, current_version)
            current_version = info.parent_version if info else None

        if current_version != to_version:
            self.logger.error(f"无法回滚: 版本路径不正确")
            return False

        # 执行回滚
        try:
            # 复制目标版本文件
            source_path = os.path.join(
                self.storage_path, model_name, f"{to_version}.pkl"
            )
            target_path = os.path.join(
                self.storage_path, model_name, f"{from_version}_rollback.pkl"
            )

            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)
            else:
                self.logger.error(f"目标版本文件不存在: {source_path}")
                return False

            # 更新版本状态
            self.update_version_status(
                model_name, from_version, VersionStatus.DEPRECATED.value)
            self.update_version_status(
                model_name, to_version, VersionStatus.PRODUCTION.value)

            self.logger.info(
                f"回滚完成: {model_name} {from_version} -> {to_version}")
            return True

        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return False

    def delete_version(self,
                       model_name: str,
                       version: str) -> bool:
        """
        删除版本

        Parameters
        ----------
        model_name : str
            模型名称
        version : str
            版本号

        Returns
        -------
        bool
            是否删除成功
        """
        if model_name not in self._versions:
            return False

        if version not in self._versions[model_name]:
            return False

        # 检查是否有子版本
        has_children = any(
            info.parent_version == version
            for info in self._versions[model_name].values()
        )

        if has_children:
            self.logger.error(f"无法删除版本: 存在子版本")
            return False

        # 删除版本文件
        version_file = os.path.join(
            self.storage_path, model_name, f"{version}.pkl"
        )

        try:
            if os.path.exists(version_file):
                os.remove(version_file)
        except Exception as e:
            self.logger.error(f"删除版本文件失败: {e}")

        # 删除版本信息
        del self._versions[model_name][version]

        # 如果没有版本了，删除模型条目
        if not self._versions[model_name]:
            del self._versions[model_name]

        self._save_versions()
        self.logger.info(f"删除版本: {model_name} v{version}")
        return True

    def _load_versions(self) -> None:
        """加载版本信息"""
        try:
            versions_file = os.path.join(self.registry_path, "versions.json")
            if os.path.exists(versions_file):
                with open(versions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for model_name, versions in data.items():
                        self._versions[model_name] = {}
                        for version, version_dict in versions.items():
                            self._versions[model_name][version] = VersionInfo.from_dict(
                                version_dict)
        except Exception as e:
            self.logger.error(f"加载版本信息失败: {e}")

    def _save_versions(self) -> None:
        """保存版本信息"""
        try:
            versions_file = os.path.join(self.registry_path, "versions.json")

            data = {}
            for model_name, versions in self._versions.items():
                data[model_name] = {}
                for version, version_info in versions.items():
                    data[model_name][version] = version_info.to_dict()

            with open(versions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存版本信息失败: {e}")

    def _load_comparisons(self) -> None:
        """加载比较结果"""
        try:
            comparisons_file = os.path.join(
                self.registry_path, "comparisons.json")
            if os.path.exists(comparisons_file):
                with open(comparisons_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, comparison_dict in data.items():
                        self._comparisons[key] = VersionComparison.from_dict(
                            comparison_dict)
        except Exception as e:
            self.logger.error(f"加载比较结果失败: {e}")

    def _save_comparisons(self) -> None:
        """保存比较结果"""
        try:
            comparisons_file = os.path.join(
                self.registry_path, "comparisons.json")

            data = {
                key: comparison.to_dict()
                for key, comparison in self._comparisons.items()
            }

            with open(comparisons_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存比较结果失败: {e}")
