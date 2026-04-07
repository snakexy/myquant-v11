"""
QLib增强任务调度器

该模块实现了增强的任务调度功能，包括：
- 高级任务依赖管理
- 动态资源分配
- 任务优先级调度
- 分布式任务执行
- 任务重试和容错
"""

import logging
import threading
import time
import queue
from typing import Dict, Any, List, Callable, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class ResourceRequirement:
    """资源需求"""
    cpu_cores: int = 1
    memory_mb: int = 512
    gpu_count: int = 0
    disk_space_mb: int = 100


@dataclass
class RetryPolicy:
    """重试策略"""
    max_retries: int = 3
    retry_delay: timedelta = timedelta(seconds=5)
    exponential_backoff: bool = True
    retry_on_exceptions: List[type] = field(default_factory=list)


@dataclass
class Task:
    """增强任务数据类"""
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
    dependencies: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    resource_requirements: ResourceRequirement = field(default_factory=ResourceRequirement)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    retry_count: int = 0
    tags: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class EnhancedTaskScheduler:
    """
    增强任务调度器
    
    该类扩展了基础任务调度器，添加了更多高级功能：
    - 任务优先级调度
    - 资源感知调度
    - 智能重试机制
    - 任务标签和分组
    - 性能监控和统计
    """
    
    def __init__(
        self, 
        max_workers: int = 4,
        enable_resource_monitoring: bool = True,
        enable_priority_scheduling: bool = True
    ):
        """
        初始化增强任务调度器
        
        Args:
            max_workers: 最大工作线程数
            enable_resource_monitoring: 启用资源监控
            enable_priority_scheduling: 启用优先级调度
        """
        self.max_workers = max_workers
        self.enable_resource_monitoring = enable_resource_monitoring
        self.enable_priority_scheduling = enable_priority_scheduling
        
        # 任务管理
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Set[str] = set()
        
        # 执行器
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: Dict[str, Future] = {}
        
        # 资源管理
        self.resource_pool = {
            'cpu_cores': max_workers,
            'memory_mb': max_workers * 1024,  # 假设每个线程1GB
            'gpu_count': 0,
            'disk_space_mb': 10240  # 10GB
        }
        self.used_resources = {
            'cpu_cores': 0,
            'memory_mb': 0,
            'gpu_count': 0,
            'disk_space_mb': 0
        }
        
        # 统计信息
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'cancelled_tasks': 0,
            'total_execution_time': timedelta(0),
            'average_execution_time': timedelta(0)
        }
        
        # 线程安全
        self.lock = threading.RLock()
        self.resource_lock = threading.RLock()
        
        logger.info(f"增强任务调度器初始化完成，最大工作线程数: {max_workers}")
    
    def add_task(
        self, 
        task_id: str, 
        name: str, 
        func: Callable, 
        args: tuple = (), 
        kwargs: dict = None,
        dependencies: List[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        resource_requirements: Optional[ResourceRequirement] = None,
        retry_policy: Optional[RetryPolicy] = None,
        tags: Optional[Dict[str, str]] = None
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
            priority: 任务优先级
            resource_requirements: 资源需求
            retry_policy: 重试策略
            tags: 任务标签
            
        Returns:
            创建的任务对象
        """
        if kwargs is None:
            kwargs = {}
        if dependencies is None:
            dependencies = []
        if resource_requirements is None:
            resource_requirements = ResourceRequirement()
        if retry_policy is None:
            retry_policy = RetryPolicy()
        if tags is None:
            tags = {}
        
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            dependencies=dependencies,
            priority=priority,
            resource_requirements=resource_requirements,
            retry_policy=retry_policy,
            tags=tags
        )
        
        with self.lock:
            self.tasks[task_id] = task
            if self.enable_priority_scheduling:
                # 使用优先级队列，优先级值越小优先级越高
                priority_value = 5 - priority.value
                self.task_queue.put((priority_value, time.time(), task))
            else:
                self.task_queue.put((0, time.time(), task))
            
            self.stats['total_tasks'] += 1
        
        logger.info(f"添加任务: {name} (ID: {task_id}, 优先级: {priority.name})")
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
        
        # 检查资源可用性
        if self.enable_resource_monitoring:
            if not self._check_resource_availability(task.resource_requirements):
                logger.warning(f"资源不足，任务 {task_id} 等待中")
                # 等待资源可用
                self._wait_for_resources(task.resource_requirements)
        
        # 执行任务
        return self._execute_task_with_retry(task)
    
    def run_workflow(self, task_ids: List[str] = None) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            task_ids: 要运行的任务ID列表，None表示运行所有任务
            
        Returns:
            所有任务的执行结果
        """
        if task_ids is None:
            with self.lock:
                task_ids = list(self.tasks.keys())
        
        logger.info(f"开始运行工作流，任务数量: {len(task_ids)}")
        
        # 按依赖关系和优先级排序任务
        sorted_tasks = self._sort_tasks_by_dependencies_and_priority(task_ids)
        
        results = {}
        
        # 启动工作线程来处理任务队列
        self._start_queue_processor()
        
        # 等待所有任务完成
        self._wait_for_completion(task_ids)
        
        # 收集结果
        with self.lock:
            for task_id in task_ids:
                if task_id in self.tasks:
                    results[task_id] = self.tasks[task_id].result
        
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
    
    def get_tasks_by_tag(self, tag_key: str, tag_value: str) -> List[Task]:
        """
        按标签获取任务
        
        Args:
            tag_key: 标签键
            tag_value: 标签值
            
        Returns:
            匹配的任务列表
        """
        with self.lock:
            return [
                task for task in self.tasks.values()
                if task.tags.get(tag_key) == tag_value
            ]
    
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
                    self.stats['cancelled_tasks'] += 1
                    logger.info(f"任务已取消: {task_id}")
                    return True
            
            # 取消待执行的任务
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                self.stats['cancelled_tasks'] += 1
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
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """
        获取调度器统计信息
        
        Returns:
            统计信息字典
        """
        with self.lock:
            stats = self.stats.copy()
            stats['pending_tasks'] = sum(
                1 for task in self.tasks.values()
                if task.status == TaskStatus.PENDING
            )
            stats['running_tasks'] = len(self.running_tasks)
            stats['resource_utilization'] = {
                resource: used / self.resource_pool[resource] * 100
                for resource, used in self.used_resources.items()
            }
            
            return stats
    
    def shutdown(self, wait: bool = True):
        """
        关闭任务调度器
        
        Args:
            wait: 是否等待所有任务完成
        """
        logger.info("关闭增强任务调度器")
        self.executor.shutdown(wait=wait)
    
    def _start_queue_processor(self):
        """启动队列处理器"""
        def process_queue():
            while True:
                try:
                    # 获取任务，设置超时避免永久阻塞
                    priority, timestamp, task = self.task_queue.get(timeout=1)
                    
                    # 检查任务是否已被取消
                    if task.status == TaskStatus.CANCELLED:
                        continue
                    
                    # 提交任务执行
                    with self.lock:
                        if task.id not in self.running_tasks:
                            self.running_tasks.add(task.id)
                            future = self.executor.submit(
                                self._execute_task_with_retry, task
                            )
                            self.futures[task.id] = future
                            
                            logger.info(f"开始执行任务: {task.name}")
                
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"队列处理器错误: {e}")
        
        # 启动队列处理线程
        queue_thread = threading.Thread(target=process_queue, daemon=True)
        queue_thread.start()
    
    def _wait_for_completion(self, task_ids: List[str]):
        """等待任务完成"""
        while True:
            with self.lock:
                completed = all(
                    self.tasks.get(task_id).status in [
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                        TaskStatus.CANCELLED
                    ]
                    for task_id in task_ids
                    if task_id in self.tasks
                )
                
                if completed:
                    break
                
                # 从运行任务集合中移除已完成的任务
                self.running_tasks = {
                    task_id for task_id in self.running_tasks
                    if task_id in self.tasks and
                    self.tasks[task_id].status == TaskStatus.RUNNING
                }
            
            time.sleep(0.1)  # 短暂休眠避免忙等待
    
    def _check_resource_availability(
        self, 
        requirements: ResourceRequirement
    ) -> bool:
        """检查资源可用性"""
        with self.resource_lock:
            return (
                self.used_resources['cpu_cores'] + requirements.cpu_cores <= 
                self.resource_pool['cpu_cores'] and
                self.used_resources['memory_mb'] + requirements.memory_mb <= 
                self.resource_pool['memory_mb'] and
                self.used_resources['gpu_count'] + requirements.gpu_count <= 
                self.resource_pool['gpu_count']
            )
    
    def _wait_for_resources(self, requirements: ResourceRequirement):
        """等待资源可用"""
        while not self._check_resource_availability(requirements):
            time.sleep(0.5)
    
    def _execute_task_with_retry(self, task: Task) -> Any:
        """带重试机制的任务执行"""
        with self.lock:
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            
            # 更新资源使用情况
            if self.enable_resource_monitoring:
                self.used_resources['cpu_cores'] += task.resource_requirements.cpu_cores
                self.used_resources['memory_mb'] += task.resource_requirements.memory_mb
                self.used_resources['gpu_count'] += task.resource_requirements.gpu_count
        
        try:
            logger.info(f"开始执行任务: {task.name}")
            result = task.func(*task.args, **task.kwargs)
            
            with self.lock:
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.end_time = datetime.now()
                self.stats['completed_tasks'] += 1
                
                # 更新执行时间统计
                execution_time = task.end_time - task.start_time
                self.stats['total_execution_time'] += execution_time
                total_completed = self.stats['completed_tasks']
                self.stats['average_execution_time'] = (
                    self.stats['total_execution_time'] / total_completed
                )
            
            logger.info(f"任务执行成功: {task.name}")
            return result
            
        except Exception as e:
            with self.lock:
                task.error = e
                task.end_time = datetime.now()
                
                # 检查是否需要重试
                should_retry = (
                    task.retry_count < task.retry_policy.max_retries and
                    (not task.retry_policy.retry_on_exceptions or
                     any(isinstance(e, exc_type) for exc_type in task.retry_policy.retry_on_exceptions))
                )
                
                if should_retry:
                    task.retry_count += 1
                    task.status = TaskStatus.RETRYING
                    
                    # 计算重试延迟
                    if task.retry_policy.exponential_backoff:
                        delay = task.retry_policy.retry_delay * (2 ** (task.retry_count - 1))
                    else:
                        delay = task.retry_policy.retry_delay
                    
                    logger.warning(
                        f"任务失败，{delay.total_seconds()}秒后重试: {task.name}, 错误: {str(e)}"
                    )
                    
                    # 等待重试
                    time.sleep(delay.total_seconds())
                    
                    # 递归重试
                    return self._execute_task_with_retry(task)
                else:
                    task.status = TaskStatus.FAILED
                    self.stats['failed_tasks'] += 1
                    logger.error(f"任务执行失败: {task.name}, 错误: {str(e)}")
            
            raise
        
        finally:
            # 释放资源
            with self.lock and self.resource_lock:
                if task.id in self.running_tasks:
                    self.running_tasks.remove(task.id)
                
                if self.enable_resource_monitoring:
                    self.used_resources['cpu_cores'] -= task.resource_requirements.cpu_cores
                    self.used_resources['memory_mb'] -= task.resource_requirements.memory_mb
                    self.used_resources['gpu_count'] -= task.resource_requirements.gpu_count
    
    def _sort_tasks_by_dependencies_and_priority(
        self, task_ids: List[str]
    ) -> List[str]:
        """
        按依赖关系和优先级对任务进行排序
        
        Args:
            task_ids: 任务ID列表
            
        Returns:
            排序后的任务ID列表
        """
        # 首先按依赖关系进行拓扑排序
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
            
            # 按优先级排序就绪任务
            ready_tasks.sort(
                key=lambda tid: self.tasks[tid].priority.value,
                reverse=True  # 高优先级在前
            )
            
            # 添加就绪任务到结果中
            for task_id in ready_tasks:
                sorted_tasks.append(task_id)
                remaining_tasks.remove(task_id)
        
        return sorted_tasks


# 导出主要类
__all__ = [
    'EnhancedTaskScheduler',
    'Task',
    'TaskPriority',
    'TaskStatus',
    'ResourceRequirement',
    'RetryPolicy'
]