"""
工作流管理器

提供统一的工作流管理和协调功能
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future

from .model_registry import ModelRegistry
from .model_pipeline import ModelPipeline


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowTask:
    """工作流任务"""
    id: str
    name: str
    type: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    status: str
    created_at: str
    started_at: str = ""
    completed_at: str = ""
    result: Any = None
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowTask':
        """从字典创建"""
        return cls(**data)


@dataclass
class Workflow:
    """工作流"""
    id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    status: str
    created_at: str
    started_at: str = ""
    completed_at: str = ""
    parameters: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """从字典创建"""
        return cls(**data)


class WorkflowManager:
    """
    工作流管理器

    负责管理和协调复杂的工作流，包括任务调度、依赖管理和执行监控
    """

    def __init__(self,
                 registry: ModelRegistry,
                 pipeline: ModelPipeline,
                 workflow_dir: str = "workflows"):
        """
        初始化工作流管理器

        Parameters
        ----------
        registry : ModelRegistry
            模型注册表
        pipeline : ModelPipeline
            模型管道
        workflow_dir : str
            工作流配置目录
        """
        self.registry = registry
        self.pipeline = pipeline
        self.workflow_dir = workflow_dir
        self.logger = logging.getLogger(__name__)
        self._workflows: Dict[str, Workflow] = {}
        self._task_handlers: Dict[str, Callable] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._running_tasks: Dict[str, Future] = {}

        # 注册默认任务处理器
        self._register_default_handlers()

        # 加载工作流配置
        self._load_workflows()

        self.logger.info(f"工作流管理器初始化完成，目录: {workflow_dir}")

    def register_task_handler(self,
                              task_type: str,
                              handler: Callable) -> None:
        """
        注册任务处理器

        Parameters
        ----------
        task_type : str
            任务类型
        handler : Callable
            处理函数
        """
        self._task_handlers[task_type] = handler
        self.logger.info(f"注册任务处理器: {task_type}")

    def create_workflow(self,
                        name: str,
                        description: str = "",
                        tasks: List[Dict[str, Any]] = None,
                        parameters: Dict[str, Any] = None) -> str:
        """
        创建工作流

        Parameters
        ----------
        name : str
            工作流名称
        description : str
            工作流描述
        tasks : List[Dict[str, Any]]
            任务列表
        parameters : Dict[str, Any]
            工作流参数

        Returns
        -------
        str
            工作流ID
        """
        workflow_id = f"workflow_{int(datetime.now().timestamp())}"

        # 创建任务对象
        workflow_tasks = []
        for i, task_config in enumerate(tasks or []):
            task = WorkflowTask(
                id=f"task_{workflow_id}_{i}",
                name=task_config.get("name", f"Task_{i}"),
                type=task_config.get("type", "default"),
                parameters=task_config.get("parameters", {}),
                dependencies=task_config.get("dependencies", []),
                status=WorkflowStatus.PENDING.value,
                created_at=datetime.now().isoformat()
            )
            workflow_tasks.append(task)

        # 创建工作流
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            tasks=workflow_tasks,
            status=WorkflowStatus.PENDING.value,
            created_at=datetime.now().isoformat(),
            parameters=parameters or {}
        )

        self._workflows[workflow_id] = workflow
        self._save_workflows()

        self.logger.info(f"创建工作流: {name} (ID: {workflow_id})")
        return workflow_id

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        获取工作流

        Parameters
        ----------
        workflow_id : str
            工作流ID

        Returns
        -------
        Optional[Workflow]
            工作流对象
        """
        return self._workflows.get(workflow_id)

    def list_workflows(self, status: str = None) -> List[Dict[str, Any]]:
        """
        列出所有工作流

        Parameters
        ----------
        status : str
            状态过滤

        Returns
        -------
        List[Dict[str, Any]]
            工作流列表
        """
        workflows = []
        for workflow in self._workflows.values():
            if status and workflow.status != status:
                continue
            workflows.append(workflow.to_dict())
        return workflows

    def execute_workflow(self, workflow_id: str) -> bool:
        """
        执行工作流

        Parameters
        ----------
        workflow_id : str
            工作流ID

        Returns
        -------
        bool
            是否成功开始执行
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            self.logger.error(f"工作流不存在: {workflow_id}")
            return False

        if workflow.status != WorkflowStatus.PENDING.value:
            self.logger.error(f"工作流状态不正确: {workflow.status}")
            return False

        self.logger.info(f"开始执行工作流: {workflow.name} (ID: {workflow_id})")

        # 更新工作流状态
        workflow.status = WorkflowStatus.RUNNING.value
        workflow.started_at = datetime.now().isoformat()

        # 提交工作流执行任务
        future = self._executor.submit(
            self._execute_workflow_internal, workflow)
        self._running_tasks[workflow_id] = future

        self._save_workflows()
        return True

    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        取消工作流

        Parameters
        ----------
        workflow_id : str
            工作流ID

        Returns
        -------
        bool
            是否成功取消
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False

        if workflow.status not in [WorkflowStatus.PENDING.value,
                                   WorkflowStatus.RUNNING.value]:
            return False

        # 取消正在运行的任务
        if workflow_id in self._running_tasks:
            future = self._running_tasks[workflow_id]
            future.cancel()
            del self._running_tasks[workflow_id]

        # 更新工作流状态
        workflow.status = WorkflowStatus.CANCELLED.value
        workflow.completed_at = datetime.now().isoformat()

        # 更新任务状态
        for task in workflow.tasks:
            if task.status in [WorkflowStatus.PENDING.value,
                               WorkflowStatus.RUNNING.value]:
                task.status = WorkflowStatus.CANCELLED.value
                task.completed_at = datetime.now().isoformat()

        self._save_workflows()
        self.logger.info(f"取消工作流: {workflow_id}")
        return True

    def get_workflow_status(self, workflow_id: str) -> Optional[str]:
        """
        获取工作流状态

        Parameters
        ----------
        workflow_id : str
            工作流ID

        Returns
        -------
        Optional[str]
            工作流状态
        """
        workflow = self.get_workflow(workflow_id)
        return workflow.status if workflow else None

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        删除工作流

        Parameters
        ----------
        workflow_id : str
            工作流ID

        Returns
        -------
        bool
            是否删除成功
        """
        if workflow_id not in self._workflows:
            return False

        # 取消正在运行的工作流
        if workflow_id in self._running_tasks:
            self.cancel_workflow(workflow_id)

        del self._workflows[workflow_id]
        self._save_workflows()

        self.logger.info(f"删除工作流: {workflow_id}")
        return True

    def _execute_workflow_internal(self, workflow: Workflow) -> None:
        """内部工作流执行逻辑"""
        try:
            # 按依赖关系执行任务
            completed_tasks = set()
            failed_tasks = set()

            while len(completed_tasks) + \
                    len(failed_tasks) < len(workflow.tasks):
                # 找到可以执行的任务
                ready_tasks = []
                for task in workflow.tasks:
                    if (task.id not in completed_tasks and
                        task.id not in failed_tasks and
                            task.status == WorkflowStatus.PENDING.value):

                        # 检查依赖是否完成
                        deps_completed = all(
                            dep in completed_tasks for dep in task.dependencies
                        )
                        if deps_completed:
                            ready_tasks.append(task)

                if not ready_tasks:
                    # 没有可执行的任务，检查是否有失败的任务
                    if failed_tasks:
                        break
                    # 否则等待
                    continue

                # 并行执行准备好的任务
                task_futures = {}
                for task in ready_tasks:
                    task.status = WorkflowStatus.RUNNING.value
                    task.started_at = datetime.now().isoformat()

                    if task.type in self._task_handlers:
                        future = self._executor.submit(
                            self._execute_task, task, workflow.parameters
                        )
                        task_futures[task.id] = future
                    else:
                        error_msg = f"任务处理器不存在: {task.type}"
                        task.status = WorkflowStatus.FAILED.value
                        task.completed_at = datetime.now().isoformat()
                        task.error = error_msg
                        failed_tasks.add(task.id)
                        self.logger.error(error_msg)

                # 等待任务完成
                for task_id, future in task_futures.items():
                    try:
                        result = future.result()
                        task = next(
                            t for t in workflow.tasks if t.id == task_id)
                        task.result = result
                        task.status = WorkflowStatus.COMPLETED.value
                        task.completed_at = datetime.now().isoformat()
                        completed_tasks.add(task_id)
                    except Exception as e:
                        task = next(
                            t for t in workflow.tasks if t.id == task_id)
                        task.status = WorkflowStatus.FAILED.value
                        task.completed_at = datetime.now().isoformat()
                        task.error = str(e)
                        failed_tasks.add(task_id)
                        self.logger.error(f"任务执行失败 {task_id}: {e}")

            # 更新工作流状态
            if failed_tasks:
                workflow.status = WorkflowStatus.FAILED.value
            else:
                workflow.status = WorkflowStatus.COMPLETED.value

            workflow.completed_at = datetime.now().isoformat()

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED.value
            workflow.completed_at = datetime.now().isoformat()
            self.logger.error(f"工作流执行失败: {e}")

        finally:
            # 清理运行任务记录
            if workflow.id in self._running_tasks:
                del self._running_tasks[workflow.id]

            self._save_workflows()

    def _execute_task(self, task: WorkflowTask,
                      workflow_params: Dict[str, Any]) -> Any:
        """执行单个任务"""
        handler = self._task_handlers[task.type]

        # 合并任务参数和工作流参数
        parameters = {**workflow_params, **task.parameters}

        return handler(parameters)

    def _register_default_handlers(self) -> None:
        """注册默认任务处理器"""
        # 模型训练任务处理器
        self._task_handlers["model_training"] = self._handle_model_training

        # 模型评估任务处理器
        self._task_handlers["model_evaluation"] = self._handle_model_evaluation

        # 模型部署任务处理器
        self._task_handlers["model_deployment"] = self._handle_model_deployment

        # 数据处理任务处理器
        self._task_handlers["data_processing"] = self._handle_data_processing

        # 报告生成任务处理器
        self._task_handlers["report_generation"] = self._handle_report_generation

    def _handle_model_training(
            self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理模型训练任务"""
        self.logger.info("执行模型训练任务")

        # 这里可以实现具体的模型训练逻辑
        model_name = parameters.get("model_name", "default_model")
        training_data = parameters.get("training_data", {})

        return {
            "status": "completed",
            "model_name": model_name,
            "training_score": 0.85,
            "model_path": f"models/{model_name}_trained.pkl"
        }

    def _handle_model_evaluation(
            self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理模型评估任务"""
        self.logger.info("执行模型评估任务")

        # 这里可以实现具体的模型评估逻辑
        model_path = parameters.get("model_path", "")
        test_data = parameters.get("test_data", {})

        return {
            "status": "completed",
            "evaluation_score": 0.82,
            "metrics": {
                "accuracy": 0.82,
                "precision": 0.80,
                "recall": 0.84
            }
        }

    def _handle_model_deployment(
            self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理模型部署任务"""
        self.logger.info("执行模型部署任务")

        # 这里可以实现具体的模型部署逻辑
        model_path = parameters.get("model_path", "")
        deployment_config = parameters.get("deployment_config", {})

        return {
            "status": "completed",
            "deployment_url": "http://api.example.com/model",
            "deployment_version": "1.0.0"
        }

    def _handle_data_processing(
            self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据处理任务"""
        self.logger.info("执行数据处理任务")

        # 这里可以实现具体的数据处理逻辑
        data_source = parameters.get("data_source", "")
        processing_config = parameters.get("processing_config", {})

        return {
            "status": "completed",
            "processed_data_path": "data/processed_data.csv",
            "record_count": 10000
        }

    def _handle_report_generation(
            self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理报告生成任务"""
        self.logger.info("执行报告生成任务")

        # 这里可以实现具体的报告生成逻辑
        report_type = parameters.get("report_type", "summary")
        data_sources = parameters.get("data_sources", [])

        return {
            "status": "completed",
            "report_path": f"reports/{report_type}_report.pdf",
            "generated_at": datetime.now().isoformat()
        }

    def _load_workflows(self) -> None:
        """加载工作流配置"""
        try:
            workflow_file = os.path.join(self.workflow_dir, "workflows.json")
            if os.path.exists(workflow_file):
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for workflow_id, workflow_dict in data.items():
                        tasks = [
                            WorkflowTask.from_dict(task_dict)
                            for task_dict in workflow_dict.get("tasks", [])
                        ]
                        workflow_dict["tasks"] = tasks
                        self._workflows[workflow_id] = Workflow.from_dict(
                            workflow_dict)
        except Exception as e:
            self.logger.error(f"加载工作流配置失败: {e}")

    def _save_workflows(self) -> None:
        """保存工作流配置"""
        try:
            os.makedirs(self.workflow_dir, exist_ok=True)
            workflow_file = os.path.join(self.workflow_dir, "workflows.json")

            data = {
                workflow_id: workflow.to_dict()
                for workflow_id, workflow in self._workflows.items()
            }
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存工作流配置失败: {e}")


# 全局工作流管理器实例
_global_workflow_manager_instance = None


def create_workflow_manager(
    registry: ModelRegistry = None,
    pipeline: ModelPipeline = None,
    workflow_dir: str = "workflows"
) -> WorkflowManager:
    """
    获取全局工作流管理器实例
    
    Args:
        registry: 模型注册表实例
        pipeline: 模型管道实例
        workflow_dir: 工作流配置目录
        
    Returns:
        WorkflowManager实例
    """
    global _global_workflow_manager_instance
    
    if _global_workflow_manager_instance is None:
        if registry is None:
            from .model_registry import get_model_registry
            registry = get_model_registry()
        
        if pipeline is None:
            from .model_pipeline import get_model_pipeline
            pipeline = get_model_pipeline(registry)
        
        _global_workflow_manager_instance = WorkflowManager(registry, pipeline, workflow_dir)
    
    return _global_workflow_manager_instance
