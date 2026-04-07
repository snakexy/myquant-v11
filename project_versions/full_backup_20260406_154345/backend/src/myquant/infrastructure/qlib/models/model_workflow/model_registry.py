"""
模型注册机制

提供模型的注册、发现和管理功能
"""

import logging
import json
import os
import time
from typing import Dict, List, Optional, Any, Callable, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ModelMetadata:
    """模型元数据"""
    name: str
    version: str
    description: str
    model_type: str
    created_at: str
    updated_at: str
    author: str
    tags: List[str]
    hyperparameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    file_path: str
    dependencies: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelMetadata':
        """从字典创建"""
        return cls(**data)


class ModelRegistry:
    """
    模型注册表

    负责模型的注册、发现、版本管理和元数据维护
    """

    def __init__(self, registry_path: str = "model_registry.json"):
        """
        初始化模型注册表

        Parameters
        ----------
        registry_path : str
            注册表文件路径
        """
        self.registry_path = registry_path
        self.logger = logging.getLogger(__name__)
        self._models: Dict[str, Dict[str, ModelMetadata]] = {}
        self._model_classes: Dict[str, Type] = {}
        self._model_factories: Dict[str, Callable] = {}

        self._load_registry()

        self.logger.info(f"模型注册表初始化完成，路径: {registry_path}")

    def register_model_class(self,
                             name: str,
                             model_class: Type,
                             description: str = "",
                             tags: List[str] = None) -> None:
        """
        注册模型类

        Parameters
        ----------
        name : str
            模型名称
        model_class : Type
            模型类
        description : str
            模型描述
        tags : List[str]
            模型标签
        """
        self._model_classes[name] = model_class

        self.logger.info(f"注册模型类: {name} - {description}")

    def register_model_factory(self,
                               name: str,
                               factory_func: Callable,
                               description: str = "",
                               tags: List[str] = None) -> None:
        """
        注册模型工厂函数

        Parameters
        ----------
        name : str
            模型名称
        factory_func : Callable
            工厂函数
        description : str
            模型描述
        tags : List[str]
            模型标签
        """
        self._model_factories[name] = factory_func

        self.logger.info(f"注册模型工厂: {name} - {description}")

    def register_model_instance(self,
                                name: str,
                                version: str,
                                model_instance: Any,
                                description: str = "",
                                author: str = "",
                                tags: List[str] = None,
                                hyperparameters: Dict[str, Any] = None,
                                performance_metrics: Dict[str, float] = None,
                                dependencies: List[str] = None) -> None:
        """
        注册模型实例

        Parameters
        ----------
        name : str
            模型名称
        version : str
            模型版本
        model_instance : Any
            模型实例
        description : str
            模型描述
        author : str
            作者
        tags : List[str]
            标签
        hyperparameters : Dict[str, Any]
            超参数
        performance_metrics : Dict[str, float]
            性能指标
        dependencies : List[str]
            依赖项
        """
        # 生成文件路径
        file_path = f"models/{name}_{version}.pkl"

        # 保存模型实例
        self._save_model_instance(model_instance, file_path)

        # 创建元数据
        metadata = ModelMetadata(
            name=name,
            version=version,
            description=description,
            model_type=type(model_instance).__name__,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author=author,
            tags=tags or [],
            hyperparameters=hyperparameters or {},
            performance_metrics=performance_metrics or {},
            file_path=file_path,
            dependencies=dependencies or []
        )

        # 注册到注册表
        if name not in self._models:
            self._models[name] = {}

        self._models[name][version] = metadata

        # 保存注册表
        self._save_registry()

        self.logger.info(f"注册模型实例: {name} v{version}")

    def get_model_class(self, name: str) -> Optional[Type]:
        """
        获取模型类

        Parameters
        ----------
        name : str
            模型名称

        Returns
        -------
        Optional[Type]
            模型类
        """
        return self._model_classes.get(name)

    def get_model_factory(self, name: str) -> Optional[Callable]:
        """
        获取模型工厂函数

        Parameters
        ----------
        name : str
            模型名称

        Returns
        -------
        Optional[Callable]
            工厂函数
        """
        return self._model_factories.get(name)

    def get_model_metadata(
            self,
            name: str,
            version: str = "latest") -> Optional[ModelMetadata]:
        """
        获取模型元数据

        Parameters
        ----------
        name : str
            模型名称
        version : str
            版本，默认为最新版本

        Returns
        -------
        Optional[ModelMetadata]
            模型元数据
        """
        if name not in self._models:
            return None

        if version == "latest":
            # 获取最新版本
            versions = list(self._models[name].keys())
            if not versions:
                return None
            version = max(versions)

        return self._models[name].get(version)

    def get_model_instance(
            self,
            name: str,
            version: str = "latest") -> Optional[Any]:
        """
        获取模型实例

        Parameters
        ----------
        name : str
            模型名称
        version : str
            版本，默认为最新版本

        Returns
        -------
        Optional[Any]
            模型实例
        """
        metadata = self.get_model_metadata(name, version)
        if not metadata:
            return None

        return self._load_model_instance(metadata.file_path)

    def list_models(self, model_type: str = None,
                    tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有模型

        Parameters
        ----------
        model_type : str
            模型类型过滤
        tags : List[str]
            标签过滤

        Returns
        -------
        List[Dict[str, Any]]
            模型列表
        """
        models = []

        for name, versions in self._models.items():
            for version, metadata in versions.items():
                # 应用过滤条件
                if model_type and metadata.model_type != model_type:
                    continue

                if tags and not any(tag in metadata.tags for tag in tags):
                    continue

                models.append(metadata.to_dict())

        return models

    def get_model_versions(self, name: str) -> List[str]:
        """
        获取模型的所有版本

        Parameters
        ----------
        name : str
            模型名称

        Returns
        -------
        List[str]
            版本列表
        """
        if name not in self._models:
            return []

        return list(self._models[name].keys())

    def delete_model(self, name: str, version: str = None) -> bool:
        """
        删除模型

        Parameters
        ----------
        name : str
            模型名称
        version : str
            版本，如果为None则删除所有版本

        Returns
        -------
        bool
            是否删除成功
        """
        if name not in self._models:
            return False

        if version is None:
            # 删除所有版本
            for metadata in self._models[name].values():
                self._delete_model_file(metadata.file_path)
            del self._models[name]
        else:
            # 删除指定版本
            if version not in self._models[name]:
                return False

            metadata = self._models[name][version]
            self._delete_model_file(metadata.file_path)
            del self._models[name][version]

            # 如果没有版本了，删除模型条目
            if not self._models[name]:
                del self._models[name]

        self._save_registry()
        self.logger.info(f"删除模型: {name} v{version}")
        return True

    def _save_model_instance(
            self,
            model_instance: Any,
            file_path: str) -> None:
        """保存模型实例"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            import pickle
            with open(file_path, 'wb') as f:
                pickle.dump(model_instance, f)
        except Exception as e:
            self.logger.error(f"保存模型实例失败: {e}")
            raise

    def _load_model_instance(self, file_path: str) -> Optional[Any]:
        """加载模型实例"""
        try:
            import pickle
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            self.logger.error(f"加载模型实例失败: {e}")
            return None

    def _delete_model_file(self, file_path: str) -> None:
        """删除模型文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            self.logger.error(f"删除模型文件失败: {e}")

    def _load_registry(self) -> None:
        """加载注册表"""
        try:
            if os.path.exists(self.registry_path):
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    for name, versions in data.items():
                        self._models[name] = {}
                        for version, metadata_dict in versions.items():
                            self._models[name][version] = ModelMetadata.from_dict(
                                metadata_dict)
        except Exception as e:
            self.logger.error(f"加载注册表失败: {e}")

    def _save_registry(self) -> None:
        """保存注册表"""
        try:
            data = {}
            for name, versions in self._models.items():
                data[name] = {}
                for version, metadata in versions.items():
                    data[name][version] = metadata.to_dict()

            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存注册表失败: {e}")


# 全局模型注册表实例
_global_model_registry = None


def get_model_registry(registry_path: str = "model_registry.json") -> ModelRegistry:
    """
    获取全局模型注册表实例
    
    Args:
        registry_path: 注册表文件路径
        
    Returns:
        ModelRegistry实例
    """
    global _global_model_registry
    
    if _global_model_registry is None:
        _global_model_registry = ModelRegistry(registry_path)
    
    return _global_model_registry
