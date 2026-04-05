"""
模型管道管理器

提供完整的模型训练、评估和部署管道
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .model_registry import ModelRegistry, ModelMetadata


class PipelineStep(Enum):
    """管道步骤枚举"""
    DATA_PREPARATION = "data_preparation"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_DEPLOYMENT = "model_deployment"
    MONITORING = "monitoring"


@dataclass
class PipelineConfig:
    """管道配置"""
    name: str
    description: str
    steps: List[str]
    parameters: Dict[str, Any]
    dependencies: List[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineConfig':
        """从字典创建"""
        return cls(**data)


@dataclass
class PipelineResult:
    """管道执行结果"""
    pipeline_name: str
    status: str
    start_time: str
    end_time: str
    duration: float
    steps_results: Dict[str, Any]
    artifacts: Dict[str, str]
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineResult':
        """从字典创建"""
        return cls(**data)


class ModelPipeline:
    """
    模型管道管理器

    负责管理模型的完整生命周期，包括数据准备、特征工程、
    模型训练、验证、部署和监控
    """

    def __init__(self,
                 registry: ModelRegistry,
                 pipeline_dir: str = "pipelines"):
        """
        初始化模型管道

        Parameters
        ----------
        registry : ModelRegistry
            模型注册表
        pipeline_dir : str
            管道配置目录
        """
        self.registry = registry
        self.pipeline_dir = pipeline_dir
        self.logger = logging.getLogger(__name__)
        self._pipelines: Dict[str, PipelineConfig] = {}
        self._step_handlers: Dict[str, Callable] = {}
        self._results: Dict[str, PipelineResult] = {}

        # 注册默认步骤处理器
        self._register_default_handlers()

        # 加载管道配置
        self._load_pipelines()

        self.logger.info(f"模型管道管理器初始化完成，目录: {pipeline_dir}")

    def register_step_handler(self,
                              step_name: str,
                              handler: Callable) -> None:
        """
        注册步骤处理器

        Parameters
        ----------
        step_name : str
            步骤名称
        handler : Callable
            处理函数
        """
        self._step_handlers[step_name] = handler
        self.logger.info(f"注册步骤处理器: {step_name}")

    def create_pipeline(self,
                        name: str,
                        description: str = "",
                        steps: List[str] = None,
                        parameters: Dict[str, Any] = None,
                        dependencies: List[str] = None) -> None:
        """
        创建管道

        Parameters
        ----------
        name : str
            管道名称
        description : str
            管道描述
        steps : List[str]
            管道步骤
        parameters : Dict[str, Any]
            管道参数
        dependencies : List[str]
            依赖项
        """
        config = PipelineConfig(
            name=name,
            description=description,
            steps=steps or [],
            parameters=parameters or {},
            dependencies=dependencies or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        self._pipelines[name] = config
        self._save_pipelines()

        self.logger.info(f"创建管道: {name}")

    def get_pipeline(self, name: str) -> Optional[PipelineConfig]:
        """
        获取管道配置

        Parameters
        ----------
        name : str
            管道名称

        Returns
        -------
        Optional[PipelineConfig]
            管道配置
        """
        return self._pipelines.get(name)

    def list_pipelines(self) -> List[Dict[str, Any]]:
        """
        列出所有管道

        Returns
        -------
        List[Dict[str, Any]]
            管道列表
        """
        return [config.to_dict() for config in self._pipelines.values()]

    def execute_pipeline(self,
                         name: str,
                         context: Dict[str, Any] = None) -> PipelineResult:
        """
        执行管道

        Parameters
        ----------
        name : str
            管道名称
        context : Dict[str, Any]
            执行上下文

        Returns
        -------
        PipelineResult
            执行结果
        """
        config = self.get_pipeline(name)
        if not config:
            raise ValueError(f"管道不存在: {name}")

        self.logger.info(f"开始执行管道: {name}")

        # 创建执行结果
        result = PipelineResult(
            pipeline_name=name,
            status="running",
            start_time=datetime.now().isoformat(),
            end_time="",
            duration=0.0,
            steps_results={},
            artifacts={},
            errors=[]
        )

        try:
            # 执行各个步骤
            for step in config.steps:
                if step not in self._step_handlers:
                    error_msg = f"步骤处理器不存在: {step}"
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)
                    continue

                try:
                    self.logger.info(f"执行步骤: {step}")
                    step_result = self._step_handlers[step](
                        context=context,
                        parameters=config.parameters.get(step, {}),
                        artifacts=result.artifacts
                    )
                    result.steps_results[step] = step_result

                    # 更新上下文
                    if isinstance(step_result, dict):
                        context.update(step_result)

                except Exception as e:
                    error_msg = f"步骤执行失败 {step}: {str(e)}"
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)

            # 设置最终状态
            result.status = "completed" if not result.errors else "failed"

        except Exception as e:
            result.status = "failed"
            result.errors.append(f"管道执行失败: {str(e)}")
            self.logger.error(f"管道执行失败: {e}")

        finally:
            result.end_time = datetime.now().isoformat()
            start = datetime.fromisoformat(result.start_time)
            end = datetime.fromisoformat(result.end_time)
            result.duration = (end - start).total_seconds()

            # 保存结果
            self._results[name] = result
            self._save_results()

        self.logger.info(f"管道执行完成: {name}, 状态: {result.status}")
        return result

    def get_pipeline_result(self, name: str) -> Optional[PipelineResult]:
        """
        获取管道执行结果

        Parameters
        ----------
        name : str
            管道名称

        Returns
        -------
        Optional[PipelineResult]
            执行结果
        """
        return self._results.get(name)

    def delete_pipeline(self, name: str) -> bool:
        """
        删除管道

        Parameters
        ----------
        name : str
            管道名称

        Returns
        -------
        bool
            是否删除成功
        """
        if name not in self._pipelines:
            return False

        del self._pipelines[name]

        # 删除相关结果
        if name in self._results:
            del self._results[name]

        self._save_pipelines()
        self._save_results()

        self.logger.info(f"删除管道: {name}")
        return True

    def _register_default_handlers(self) -> None:
        """注册默认步骤处理器"""
        # 数据准备处理器
        self._step_handlers[PipelineStep.DATA_PREPARATION.value] = \
            self._handle_data_preparation

        # 特征工程处理器
        self._step_handlers[PipelineStep.FEATURE_ENGINEERING.value] = \
            self._handle_feature_engineering

        # 模型训练处理器
        self._step_handlers[PipelineStep.MODEL_TRAINING.value] = \
            self._handle_model_training

        # 模型验证处理器
        self._step_handlers[PipelineStep.MODEL_VALIDATION.value] = \
            self._handle_model_validation

        # 模型部署处理器
        self._step_handlers[PipelineStep.MODEL_DEPLOYMENT.value] = \
            self._handle_model_deployment

        # 监控处理器
        self._step_handlers[PipelineStep.MONITORING.value] = \
            self._handle_monitoring

    def _handle_data_preparation(self,
                                 context: Dict[str, Any],
                                 parameters: Dict[str, Any],
                                 artifacts: Dict[str, str]) -> Dict[str, Any]:
        """处理数据准备步骤"""
        self.logger.info("执行数据准备")

        # 这里可以实现具体的数据准备逻辑
        # 例如：数据加载、清洗、分割等

        return {
            "data_prepared": True,
            "data_shape": "(1000, 10)",
            "train_size": 800,
            "test_size": 200
        }

    def _handle_feature_engineering(self,
                                    context: Dict[str, Any],
                                    parameters: Dict[str, Any],
                                    artifacts: Dict[str, str]) -> Dict[str, Any]:
        """处理特征工程步骤"""
        self.logger.info("执行特征工程")

        # 这里可以实现具体的特征工程逻辑
        # 例如：特征选择、特征变换、特征生成等

        return {
            "features_engineered": True,
            "feature_count": 20,
            "feature_names": ["feature_1", "feature_2", "..."]
        }

    def _handle_model_training(self,
                               context: Dict[str, Any],
                               parameters: Dict[str, Any],
                               artifacts: Dict[str, str]) -> Dict[str, Any]:
        """处理模型训练步骤"""
        self.logger.info("执行模型训练")

        # 这里可以实现具体的模型训练逻辑
        # 例如：模型选择、超参数调优、训练等

        return {
            "model_trained": True,
            "model_type": parameters.get("model_type", "LinearRegression"),
            "training_score": 0.85,
            "model_path": "models/trained_model.pkl"
        }

    def _handle_model_validation(self,
                                 context: Dict[str, Any],
                                 parameters: Dict[str, Any],
                                 artifacts: Dict[str, str]) -> Dict[str, Any]:
        """处理模型验证步骤"""
        self.logger.info("执行模型验证")

        # 这里可以实现具体的模型验证逻辑
        # 例如：交叉验证、性能评估、鲁棒性测试等

        return {
            "model_validated": True,
            "validation_score": 0.82,
            "test_score": 0.80,
            "metrics": {
                "mse": 0.15,
                "mae": 0.30,
                "r2": 0.80
            }
        }

    def _handle_model_deployment(self,
                                 context: Dict[str, Any],
                                 parameters: Dict[str, Any],
                                 artifacts: Dict[str, str]) -> Dict[str, Any]:
        """处理模型部署步骤"""
        self.logger.info("执行模型部署")

        # 这里可以实现具体的模型部署逻辑
        # 例如：模型打包、服务部署、版本管理等

        return {
            "model_deployed": True,
            "deployment_url": "http://api.example.com/model",
            "deployment_version": "1.0.0",
            "deployment_time": datetime.now().isoformat()
        }

    def _handle_monitoring(self,
                           context: Dict[str, Any],
                           parameters: Dict[str, Any],
                           artifacts: Dict[str, str]) -> Dict[str, Any]:
        """处理监控步骤"""
        self.logger.info("执行监控设置")

        # 这里可以实现具体的监控逻辑
        # 例如：性能监控、数据漂移检测、告警设置等

        return {
            "monitoring_setup": True,
            "monitoring_dashboard": "http://dashboard.example.com",
            "alert_rules": ["performance_drop", "data_drift"],
            "monitoring_interval": "1h"
        }

    def _load_pipelines(self) -> None:
        """加载管道配置"""
        try:
            pipeline_file = os.path.join(self.pipeline_dir, "pipelines.json")
            if os.path.exists(pipeline_file):
                with open(pipeline_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, config_dict in data.items():
                        self._pipelines[name] = PipelineConfig.from_dict(
                            config_dict)
        except Exception as e:
            self.logger.error(f"加载管道配置失败: {e}")

    def _save_pipelines(self) -> None:
        """保存管道配置"""
        try:
            os.makedirs(self.pipeline_dir, exist_ok=True)
            pipeline_file = os.path.join(self.pipeline_dir, "pipelines.json")

            data = {name: config.to_dict()
                    for name, config in self._pipelines.items()}
            with open(pipeline_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存管道配置失败: {e}")

    def _load_results(self) -> None:
        """加载执行结果"""
        try:
            results_file = os.path.join(self.pipeline_dir, "results.json")
            if os.path.exists(results_file):
                with open(results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, result_dict in data.items():
                        self._results[name] = PipelineResult.from_dict(
                            result_dict)
        except Exception as e:
            self.logger.error(f"加载执行结果失败: {e}")

    def _save_results(self) -> None:
        """保存执行结果"""
        try:
            os.makedirs(self.pipeline_dir, exist_ok=True)
            results_file = os.path.join(self.pipeline_dir, "results.json")

            data = {name: result.to_dict()
                    for name, result in self._results.items()}
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存执行结果失败: {e}")


# 全局模型管道实例
_global_model_pipeline = None


def create_model_pipeline(
    registry: ModelRegistry = None,
    pipeline_dir: str = "pipelines"
) -> ModelPipeline:
    """
    获取全局模型管道实例
    
    Args:
        registry: 模型注册表实例
        pipeline_dir: 管道配置目录
        
    Returns:
        ModelPipeline实例
    """
    global _global_model_pipeline
    
    if _global_model_pipeline is None:
        if registry is None:
            from .model_registry import get_model_registry
            registry = get_model_registry()
        
        _global_model_pipeline = ModelPipeline(registry, pipeline_dir)
    
    return _global_model_pipeline


def get_model_pipeline(
    registry: ModelRegistry = None,
    pipeline_dir: str = "pipelines"
) -> ModelPipeline:
    """
    获取模型管道实例（别名函数）
    
    Args:
        registry: 模型注册表实例
        pipeline_dir: 管道配置目录
        
    Returns:
        ModelPipeline实例
    """
    return create_model_pipeline(registry, pipeline_dir)
