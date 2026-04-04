"""
并行计算优化模块

提供高性能并行计算功能，优化多核CPU利用率
"""

import os
import time
import logging
import threading
import multiprocessing as mp
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from queue import Queue, Empty
import numpy as np
import pandas as pd
from functools import partial, wraps


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        self.max_workers = max_workers or mp.cpu_count()
        self.use_processes = use_processes
        self.logger = logging.getLogger(__name__)
        self._task_queue = Queue()
        self._result_queue = Queue()
        self._workers = []
        self._shutdown = False
    
    def submit_task(self, func: Callable, *args, **kwargs) -> Any:
        """提交任务"""
        task = {
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'id': id(func) + time.time()
        }
        self._task_queue.put(task)
        return task['id']
    
    def get_result(self, timeout: Optional[float] = None) -> Any:
        """获取结果"""
        try:
            return self._result_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def start_workers(self):
        """启动工作线程"""
        if self._workers:
            return
        
        for _ in range(self.max_workers):
            if self.use_processes:
                worker = mp.Process(target=self._worker_loop)
            else:
                worker = threading.Thread(target=self._worker_loop)
            
            worker.start()
            self._workers.append(worker)
        
        self.logger.info(f"已启动 {self.max_workers} 个工作线程")
    
    def shutdown(self):
        """关闭调度器"""
        self._shutdown = True
        
        # 等待所有任务完成
        while not self._task_queue.empty():
            time.sleep(0.1)
        
        # 关闭工作线程
        for worker in self._workers:
            if self.use_processes:
                worker.terminate()
            else:
                worker.join(timeout=1)
        
        self._workers = []
        self.logger.info("任务调度器已关闭")
    
    def _worker_loop(self):
        """工作线程循环"""
        while not self._shutdown:
            try:
                task = self._task_queue.get(timeout=0.1)
                func = task['func']
                args = task['args']
                kwargs = task['kwargs']
                
                try:
                    result = func(*args, **kwargs)
                    self._result_queue.put({
                        'id': task['id'],
                        'result': result,
                        'error': None
                    })
                except Exception as e:
                    self._result_queue.put({
                        'id': task['id'],
                        'result': None,
                        'error': str(e)
                    })
                    
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"工作线程错误: {e}")


class ParallelProcessor:
    """并行处理器"""
    
    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        self.max_workers = max_workers or mp.cpu_count()
        self.use_processes = use_processes
        self.logger = logging.getLogger(__name__)
    
    def map_reduce(self, data: List[Any], map_func: Callable, 
                   reduce_func: Optional[Callable] = None,
                   chunk_size: Optional[int] = None) -> Any:
        """Map-Reduce并行处理"""
        if not data:
            return None
        
        # Map阶段
        if self.use_processes:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                if chunk_size:
                    map_results = list(executor.map(map_func, data, chunksize=chunk_size))
                else:
                    map_results = list(executor.map(map_func, data))
        else:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                if chunk_size:
                    map_results = list(executor.map(map_func, data, chunksize=chunk_size))
                else:
                    map_results = list(executor.map(map_func, data))
        
        # Reduce阶段
        if reduce_func:
            return reduce_func(map_results)
        else:
            return map_results
    
    def parallel_for(self, func: Callable, iterable: List[Any],
                     progress_callback: Optional[Callable] = None) -> List[Any]:
        """并行for循环"""
        results = [None] * len(iterable)
        
        if self.use_processes:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(func, item): i for i, item in enumerate(iterable)}
                
                for future in as_completed(futures):
                    index = futures[future]
                    try:
                        results[index] = future.result()
                        if progress_callback:
                            progress_callback(index + 1, len(iterable))
                    except Exception as e:
                        self.logger.error(f"任务 {index} 执行失败: {e}")
                        results[index] = None
        else:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(func, item): i for i, item in enumerate(iterable)}
                
                for future in as_completed(futures):
                    index = futures[future]
                    try:
                        results[index] = future.result()
                        if progress_callback:
                            progress_callback(index + 1, len(iterable))
                    except Exception as e:
                        self.logger.error(f"任务 {index} 执行失败: {e}")
                        results[index] = None
        
        return results
    
    def batch_process(self, data: List[Any], batch_size: int,
                     process_func: Callable) -> List[Any]:
        """批量并行处理"""
        if not data:
            return []
        
        # 分批
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
        
        # 并行处理每个批次
        def process_batch(batch):
            return [process_func(item) for item in batch]
        
        return self.map_reduce(batches, process_batch, lambda x: [item for sublist in x for item in sublist])


class DataFrameParallelProcessor:
    """DataFrame并行处理器"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.processor = ParallelProcessor(max_workers=max_workers)
        self.logger = logging.getLogger(__name__)
    
    def parallel_apply(self, df: pd.DataFrame, func: Callable, axis: int = 0,
                      partitions: Optional[int] = None) -> Union[pd.DataFrame, pd.Series]:
        """并行应用函数到DataFrame"""
        if partitions is None:
            partitions = self.max_workers
        
        if axis == 0:
            # 按列并行处理
            columns = [col for col in df.columns]
            
            def process_column(col_name):
                return func(df[col_name])
            
            results = self.processor.parallel_for(process_column, columns)
            return pd.Series(results, index=columns)
        
        elif axis == 1:
            # 按行并行处理
            # 分割DataFrame
            row_partitions = np.array_split(df, partitions)
            
            def process_partition(partition):
                return partition.apply(func, axis=1)
            
            results = self.processor.map_reduce(row_partitions, process_partition)
            return pd.concat(results, ignore_index=True)
        
        else:
            raise ValueError("axis参数必须为0或1")
    
    def parallel_groupby_apply(self, df: pd.DataFrame, groupby_cols: List[str],
                               func: Callable) -> pd.DataFrame:
        """并行分组应用函数"""
        grouped = df.groupby(groupby_cols)
        groups = [group for name, group in grouped]
        
        def process_group(group):
            return func(group)
        
        results = self.processor.parallel_for(process_group, groups)
        return pd.concat(results, ignore_index=True)
    
    def parallel_merge(self, dfs: List[pd.DataFrame], **kwargs) -> pd.DataFrame:
        """并行合并多个DataFrame"""
        if len(dfs) < 2:
            return dfs[0] if dfs else pd.DataFrame()
        
        # 两两合并
        while len(dfs) > 1:
            pairs = [(dfs[i], dfs[i+1]) for i in range(0, len(dfs)-1, 2)]
            
            def merge_pair(pair):
                return pd.merge(pair[0], pair[1], **kwargs)
            
            new_dfs = self.processor.parallel_for(merge_pair, pairs)
            
            # 处理奇数个DataFrame的情况
            if len(dfs) % 2 == 1:
                new_dfs.append(dfs[-1])
            
            dfs = new_dfs
        
        return dfs[0]


class NumpyParallelProcessor:
    """NumPy并行处理器"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.processor = ParallelProcessor(max_workers=max_workers)
        self.logger = logging.getLogger(__name__)
    
    def parallel_matrix_operations(self, matrices: List[np.ndarray],
                                  operation: str) -> List[np.ndarray]:
        """并行矩阵操作"""
        def matrix_op(matrix):
            if operation == 'transpose':
                return matrix.T
            elif operation == 'inverse':
                return np.linalg.inv(matrix)
            elif operation == 'eig':
                return np.linalg.eig(matrix)[0]  # 返回特征值
            elif operation == 'svd':
                return np.linalg.svd(matrix)[0]  # 返回U矩阵
            else:
                raise ValueError(f"不支持的操作: {operation}")
        
        return self.processor.parallel_for(matrix_op, matrices)
    
    def parallel_elementwise_operation(self, arrays: List[np.ndarray],
                                      operation: Callable) -> List[np.ndarray]:
        """并行元素级操作"""
        return self.processor.parallel_for(operation, arrays)
    
    def parallel_reduction(self, arrays: List[np.ndarray],
                          axis: Optional[int] = None,
                          operation: str = 'sum') -> List[Any]:
        """并行归约操作"""
        def reduce_op(arr):
            if operation == 'sum':
                return np.sum(arr, axis=axis)
            elif operation == 'mean':
                return np.mean(arr, axis=axis)
            elif operation == 'std':
                return np.std(arr, axis=axis)
            elif operation == 'max':
                return np.max(arr, axis=axis)
            elif operation == 'min':
                return np.min(arr, axis=axis)
            else:
                raise ValueError(f"不支持的操作: {operation}")
        
        return self.processor.parallel_for(reduce_op, arrays)


def parallel_decorator(max_workers: Optional[int] = None, use_processes: bool = False):
    """并行装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            processor = ParallelProcessor(max_workers, use_processes)
            
            # 检查第一个参数是否是可迭代对象
            if args and isinstance(args[0], (list, tuple, np.ndarray)):
                data = args[0]
                # 创建部分函数，固定除第一个参数外的其他参数
                partial_func = partial(func, *args[1:], **kwargs)
                return processor.parallel_for(partial_func, list(data))
            else:
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {}
    
    def monitor_function(self, func_name: str, func: Callable, *args, **kwargs):
        """监控函数执行性能"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory
        
        # 记录性能指标
        self.metrics[func_name] = {
            'execution_time': execution_time,
            'memory_delta': memory_delta,
            'success': success,
            'error': error,
            'timestamp': time.time()
        }
        
        self.logger.info(f"函数 {func_name} 执行时间: {execution_time:.4f}s, "
                        f"内存变化: {memory_delta:.2f}MB")
        
        return result
    
    def _get_memory_usage(self) -> float:
        """获取当前内存使用量(MB)"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """获取性能指标"""
        return self.metrics.copy()
    
    def clear_metrics(self):
        """清除性能指标"""
        self.metrics.clear()


# 全局并行处理器实例
parallel_processor = ParallelProcessor()
dataframe_processor = DataFrameParallelProcessor()
numpy_processor = NumpyParallelProcessor()
performance_monitor = PerformanceMonitor()