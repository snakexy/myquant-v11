# QLib工作流任务调度器

import logging
import threading
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务数据类"""
    id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class TaskScheduler:
    """
    QLib工作流任务调度器
    
    该类实现了QLib标准的任务调度功能，包括：
    - 任务依赖管理
    - 并行任务执行
    - 任务状态跟踪
    - 错误处理和重试
    """
    
    def __init__(self, max_workers: int = 4):
        """
        初始化任务调度器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: Dict[str, Future] = {}
        self.lock = threading.Lock()
        
        logger.info(f"任务调度器初始化完成，最大工作线程数: {max_workers}")
    
    def add_task(
        self, 
        task_id: str, 
        name: str, 
        func: Callable, 
        args: tuple = (), 
        kwargs: dict = None,
        dependencies: List[str] = None
    ) -> Task:
        """
        添加任务
        
        Args:
            task_id: 任务ID
            name: 任务名称
            func: 任务函数
            args: 位置参数
            kwargs: 关键字参数
            dependencies: 依赖任务ID列表
            
        Returns:
            创建的任务对象
        """
        if kwargs is None:
            kwargs = {}
            
        if dependencies is None:
            dependencies = []
            
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            dependencies=dependencies
        )
        
        with self.lock:
            self.tasks[task_id] = task
            
        logger.info(f"添加任务: {name} (ID: {task_id})")
        return task
    
    def run_task(self, task_id: str) -> Any:
        """
        运行单个任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务执行结果
            
        Raises:
            ValueError: 任务不存在
            RuntimeError: 任务依赖未满足
        """
        with self.lock:
            if task_id not in self.tasks:
                raise ValueError(f"任务不存在: {task_id}")
                
            task = self.tasks[task_id]
            
            # 检查依赖
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    raise RuntimeError(f"任务依赖未满足: {task_id} -> {dep_id}")
        
        # 执行任务
        return self._execute_task(task)
    
    def run_workflow(self, task_ids: List[str] = None) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            task_ids: 要运行的任务ID列表，None表示运行所有任务
            
        Returns:
            所有任务的执行结果
        """
        if task_ids is None:
            task_ids = list(self.tasks.keys())
            
        logger.info(f"开始运行工作流，任务数量: {len(task_ids)}")
        
        # 按依赖关系排序任务
        sorted_tasks = self._sort_tasks_by_dependencies(task_ids)
        
        results = {}
        
        # 按批次执行任务
        for batch in self._group_tasks_by_dependencies(sorted_tasks):
            batch_futures = {}
            
            # 提交批次中的所有任务
            for task_id in batch:
                task = self.tasks[task_id]
                future = self.executor.submit(self._execute_task, task)
                batch_futures[task_id] = future
                self.futures[task_id] = future
                
                logger.info(f"提交任务: {task.name} (ID: {task_id})")
            
            # 等待批次完成
            for task_id, future in batch_futures.items():
                try:
                    result = future.result()
                    results[task_id] = result
                    logger.info(f"任务完成: {task_id}")
                except Exception as e:
                    logger.error(f"任务失败: {task_id}, 错误: {str(e)}")
                    results[task_id] = None
        
        logger.info("工作流执行完成")
        return results
    
    def get_task_status(self, task_id: str) -> TaskStatus:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态
        """
        with self.lock:
            if task_id not in self.tasks:
                raise ValueError(f"任务不存在: {task_id}")
            return self.tasks[task_id].status
    
    def get_all_tasks(self) -> Dict[str, Task]:
        """
        获取所有任务
        
        Returns:
            所有任务的字典
        """
        with self.lock:
            return self.tasks.copy()
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
                
            task = self.tasks[task_id]
            
            # 取消正在运行的任务
            if task_id in self.futures:
                future = self.futures[task_id]
                if future.cancel():
                    task.status = TaskStatus.CANCELLED
                    logger.info(f"任务已取消: {task_id}")
                    return True
            
            # 取消待执行的任务
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                logger.info(f"任务已取消: {task_id}")
                return True
                
            return False
    
    def clear_completed_tasks(self):
        """清除已完成的任务"""
        with self.lock:
            completed_ids = [
                task_id for task_id, task in self.tasks.items()
                if task.status in [
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.CANCELLED
                ]
            ]
            
            for task_id in completed_ids:
                del self.tasks[task_id]
                if task_id in self.futures:
                    del self.futures[task_id]
                    
            logger.info(f"清除已完成任务: {len(completed_ids)}个")
    
    def shutdown(self, wait: bool = True):
        """
        关闭任务调度器
        
        Args:
            wait: 是否等待所有任务完成
        """
        logger.info("关闭任务调度器")
        self.executor.shutdown(wait=wait)
    
    def _execute_task(self, task: Task) -> Any:
        """
        执行单个任务
        
        Args:
            task: 任务对象
            
        Returns:
            任务执行结果
        """
        with self.lock:
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            
        try:
            logger.info(f"开始执行任务: {task.name}")
            result = task.func(*task.args, **task.kwargs)
            
            with self.lock:
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.end_time = datetime.now()
                
            logger.info(f"任务执行成功: {task.name}")
            return result
            
        except Exception as e:
            with self.lock:
                task.status = TaskStatus.FAILED
                task.error = e
                task.end_time = datetime.now()
                
            logger.error(f"任务执行失败: {task.name}, 错误: {str(e)}")
            raise
    
    def _sort_tasks_by_dependencies(self, task_ids: List[str]) -> List[str]:
        """
        按依赖关系对任务进行拓扑排序
        
        Args:
            task_ids: 任务ID列表
            
        Returns:
            排序后的任务ID列表
        """
        # 简单的拓扑排序实现
        sorted_tasks = []
        remaining_tasks = task_ids.copy()
        
        while remaining_tasks:
            # 找到没有未完成依赖的任务
            ready_tasks = []
            for task_id in remaining_tasks:
                task = self.tasks[task_id]
                if all(
                    dep_id not in remaining_tasks 
                    for dep_id in task.dependencies
                ):
                    ready_tasks.append(task_id)
            
            if not ready_tasks:
                raise ValueError("存在循环依赖或依赖任务不存在")
            
            # 添加就绪任务到结果中
            for task_id in ready_tasks:
                sorted_tasks.append(task_id)
                remaining_tasks.remove(task_id)
        
        return sorted_tasks
    
    def _group_tasks_by_dependencies(
        self, sorted_tasks: List[str]
    ) -> List[List[str]]:
        """
        将任务按依赖关系分组，同一组的任务可以并行执行
        
        Args:
            sorted_tasks: 已排序的任务ID列表
            
        Returns:
            分组后的任务列表
        """
        groups = []
        remaining_tasks = sorted_tasks.copy()
        
        while remaining_tasks:
            current_group = []
            next_tasks = []
            
            for task_id in remaining_tasks:
                task = self.tasks[task_id]
                
                # 检查是否所有依赖都已完成
                if all(
                    dep_id not in remaining_tasks 
                    for dep_id in task.dependencies
                ):
                    current_group.append(task_id)
                else:
                    next_tasks.append(task_id)
            
            if not current_group:
                raise ValueError("存在循环依赖")
            
            groups.append(current_group)
            remaining_tasks = next_tasks
        
        return groups
    
    def get_workflow_progress(self) -> Dict[str, Any]:
        """
        获取工作流进度
        
        Returns:
            工作流进度信息
        """
        with self.lock:
            total_tasks = len(self.tasks)
            completed_tasks = sum(
                1 for task in self.tasks.values()
                if task.status == TaskStatus.COMPLETED
            )
            failed_tasks = sum(
                1 for task in self.tasks.values()
                if task.status == TaskStatus.FAILED
            )
            running_tasks = sum(
                1 for task in self.tasks.values()
                if task.status == TaskStatus.RUNNING
            )
            
            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "running_tasks": running_tasks,
                "progress_percentage": (
                    completed_tasks / total_tasks * 100
                ) if total_tasks > 0 else 0,
                "tasks": {
                    task_id: {
                        "name": task.name,
                        "status": task.status.value,
                        "start_time": (
                            task.start_time.isoformat()
                            if task.start_time else None
                        ),
                        "end_time": (
                            task.end_time.isoformat()
                            if task.end_time else None
                        ),
                        "error": str(task.error) if task.error else None
                    }
                    for task_id, task in self.tasks.items()
                }
            }