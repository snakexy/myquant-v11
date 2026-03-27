"""
GPU加速模块 - 修复版本

提供GPU设备管理、内存优化和并行计算功能
"""

import os
import logging
import warnings
from typing import Dict, List, Optional, Union, Any, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
import numpy as np
import pandas as pd

# 尝试导入GPU相关库
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

try:
    import numba
    from numba import cuda, jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


class GPUManager:
    """GPU设备管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._gpu_available = self._check_gpu_availability()
        self._device_count = 0
        self._current_device = 0
        self._device_info = {}
        
        if self._gpu_available:
            self._initialize_gpu_devices()
    
    def _check_gpu_availability(self) -> bool:
        """检查GPU是否可用"""
        # 检查PyTorch
        if TORCH_AVAILABLE and torch.cuda.is_available():
            return True
        
        # 检查CuPy
        if CUPY_AVAILABLE and cp.cuda.is_available():
            return True
        
        # 检查Numba CUDA
        if NUMBA_AVAILABLE and cuda.is_available():
            return True
        
        return False
    
    def _initialize_gpu_devices(self):
        """初始化GPU设备信息"""
        try:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                self._device_count = torch.cuda.device_count()
                for i in range(self._device_count):
                    props = torch.cuda.get_device_properties(i)
                    self._device_info[i] = {
                        'name': props.name,
                        'total_memory': props.total_memory,
                        'compute_capability': f"{props.major}.{props.minor}",
                        'multiprocessor_count': props.multi_processor_count
                    }
            
            elif CUPY_AVAILABLE and cp.cuda.is_available():
                self._device_count = cp.cuda.runtime.getDeviceCount()
                for i in range(self._device_count):
                    with cp.cuda.Device(i):
                        meminfo = cp.cuda.runtime.memGetInfo()
                        self._device_info[i] = {
                            'name': cp.cuda.runtime.getDeviceProperties(i)['name'].decode(),
                            'total_memory': meminfo[1],
                            'free_memory': meminfo[0],
                            'compute_capability': cp.cuda.runtime.getDeviceProperties(i)['computeCapability']
                        }
            
            elif NUMBA_AVAILABLE and cuda.is_available():
                self._device_count = len(cuda.gpus)
                for i in range(self._device_count):
                    with cuda.gpus[i]:
                        device = cuda.get_current_device()
                        self._device_info[i] = {
                            'name': device.name.decode(),
                            'compute_capability': f"{device.compute_capability[0]}.{device.compute_capability[1]}",
                            'multiprocessor_count': device.MULTIPROCESSOR_COUNT,
                            'max_threads_per_block': device.MAX_THREADS_PER_BLOCK,
                            'max_block_dim': device.MAX_BLOCK_DIM,
                            'max_grid_dim': device.MAX_GRID_DIM
                        }
            
            self.logger.info(f"已初始化 {self._device_count} 个GPU设备")
            
        except Exception as e:
            self.logger.error(f"初始化GPU设备失败: {e}")
            self._gpu_available = False
    
    @property
    def gpu_available(self) -> bool:
        """GPU是否可用"""
        return self._gpu_available
    
    @property
    def device_count(self) -> int:
        """GPU设备数量"""
        return self._device_count
    
    def get_device_info(self, device_id: Optional[int] = None) -> Dict[str, Any]:
        """获取GPU设备信息"""
        if not self._gpu_available:
            return {}
        
        if device_id is None:
            device_id = self._current_device
        
        return self._device_info.get(device_id, {})
    
    def set_device(self, device_id: int):
        """设置当前使用的GPU设备"""
        if not self._gpu_available:
            self.logger.warning("GPU不可用，无法设置设备")
            return
        
        if device_id >= self._device_count:
            raise ValueError(f"设备ID {device_id} 超出范围，总设备数: {self._device_count}")
        
        try:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                torch.cuda.set_device(device_id)
            
            elif CUPY_AVAILABLE and cp.cuda.is_available():
                cp.cuda.Device(device_id).use()
            
            elif NUMBA_AVAILABLE and cuda.is_available():
                cuda.set_device(device_id)
            
            self._current_device = device_id
            self.logger.info(f"已切换到GPU设备 {device_id}")
            
        except Exception as e:
            self.logger.error(f"设置GPU设备 {device_id} 失败: {e}")
    
    def get_memory_info(self, device_id: Optional[int] = None) -> Dict[str, int]:
        """获取GPU内存信息"""
        if not self._gpu_available:
            return {}
        
        if device_id is None:
            device_id = self._current_device
        
        try:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                with torch.cuda.device(device_id):
                    total = torch.cuda.get_device_properties(device_id).total_memory
                    allocated = torch.cuda.memory_allocated(device_id)
                    cached = torch.cuda.memory_reserved(device_id)
                    free = total - allocated
                    
                    return {
                        'total': total,
                        'allocated': allocated,
                        'cached': cached,
                        'free': free
                    }
            
            elif CUPY_AVAILABLE and cp.cuda.is_available():
                with cp.cuda.Device(device_id):
                    meminfo = cp.cuda.runtime.memGetInfo()
                    return {
                        'total': meminfo[1],
                        'free': meminfo[0],
                        'used': meminfo[1] - meminfo[0]
                    }
            
            elif NUMBA_AVAILABLE and cuda.is_available():
                with cuda.gpus[device_id]:
                    # Numba不直接提供内存信息，使用PyTorch或CuPy的方法
                    if TORCH_AVAILABLE and torch.cuda.is_available():
                        with torch.cuda.device(device_id):
                            total = torch.cuda.get_device_properties(device_id).total_memory
                            allocated = torch.cuda.memory_allocated(device_id)
                            return {
                                'total': total,
                                'allocated': allocated,
                                'free': total - allocated
                            }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"获取GPU内存信息失败: {e}")
            return {}
    
    def clear_cache(self, device_id: Optional[int] = None):
        """清理GPU缓存"""
        if not self._gpu_available:
            return
        
        if device_id is None:
            device_id = self._current_device
        
        try:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                with torch.cuda.device(device_id):
                    torch.cuda.empty_cache()
            
            elif CUPY_AVAILABLE and cp.cuda.is_available():
                with cp.cuda.Device(device_id):
                    cp.get_default_memory_pool().free_all_blocks()
                    cp.get_default_pinned_memory_pool().free_all_blocks()
            
            self.logger.info(f"已清理GPU设备 {device_id} 的缓存")
            
        except Exception as e:
            self.logger.error(f"清理GPU缓存失败: {e}")


class GPUMemoryManager:
    """GPU内存管理器"""
    
    def __init__(self, gpu_manager: GPUManager):
        self.gpu_manager = gpu_manager
        self.logger = logging.getLogger(__name__)
        self._allocated_tensors = {}
        self._memory_pools = {}
    
    def allocate_tensor(self, shape: tuple, dtype: str = 'float32', 
                       device_id: Optional[int] = None) -> Union[Any, None]:
        """分配GPU张量"""
        if not self.gpu_manager.gpu_available:
            self.logger.warning("GPU不可用，返回None")
            return None
        
        if device_id is None:
            device_id = self.gpu_manager._current_device
        
        try:
            # 使用PyTorch
            if TORCH_AVAILABLE and torch.cuda.is_available():
                with torch.cuda.device(device_id):
                    tensor = torch.empty(shape, dtype=getattr(torch, dtype), device='cuda')
                    return tensor
            
            # 使用CuPy
            elif CUPY_AVAILABLE and cp.cuda.is_available():
                with cp.cuda.Device(device_id):
                    tensor = cp.empty(shape, dtype=getattr(cp, dtype))
                    return tensor
            
            return None
            
        except Exception as e:
            self.logger.error(f"分配GPU张量失败: {e}")
            return None
    
    def copy_to_gpu(self, data: Union[np.ndarray, pd.DataFrame], 
                   device_id: Optional[int] = None) -> Union[Any, None]:
        """将数据复制到GPU"""
        if not self.gpu_manager.gpu_available:
            return None
        
        if device_id is None:
            device_id = self.gpu_manager._current_device
        
        try:
            # 转换pandas DataFrame为numpy数组
            if isinstance(data, pd.DataFrame):
                data = data.values
            
            # 使用PyTorch
            if TORCH_AVAILABLE and torch.cuda.is_available():
                with torch.cuda.device(device_id):
                    tensor = torch.from_numpy(data).cuda()
                    return tensor
            
            # 使用CuPy
            elif CUPY_AVAILABLE and cp.cuda.is_available():
                with cp.cuda.Device(device_id):
                    tensor = cp.asarray(data)
                    return tensor
            
            return None
            
        except Exception as e:
            self.logger.error(f"复制数据到GPU失败: {e}")
            return None
    
    def copy_from_gpu(self, gpu_data: Any) -> Union[np.ndarray, None]:
        """从GPU复制数据到CPU"""
        if not self.gpu_manager.gpu_available:
            return None
        
        try:
            # 使用PyTorch
            if TORCH_AVAILABLE and isinstance(gpu_data, torch.Tensor):
                return gpu_data.cpu().numpy()
            
            # 使用CuPy
            elif CUPY_AVAILABLE and isinstance(gpu_data, cp.ndarray):
                return cp.asnumpy(gpu_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"从GPU复制数据失败: {e}")
            return None
    
    def optimize_memory_layout(self, tensor: Any) -> Any:
        """优化内存布局"""
        if not self.gpu_manager.gpu_available:
            return tensor
        
        try:
            # 使用PyTorch
            if TORCH_AVAILABLE and isinstance(tensor, torch.Tensor):
                # 确保张量是连续的
                if not tensor.is_contiguous():
                    tensor = tensor.contiguous()
                
                # 尝试转换为更节省内存的格式
                if tensor.dtype == torch.float64 and tensor.device.type == 'cuda':
                    tensor = tensor.float()  # 转换为float32
                
                return tensor
            
            # 使用CuPy
            elif CUPY_AVAILABLE and isinstance(tensor, cp.ndarray):
                # 确保数组是连续的
                if not tensor.flags.c_contiguous:
                    tensor = cp.ascontiguousarray(tensor)
                
                return tensor
            
            return tensor
            
        except Exception as e:
            self.logger.error(f"优化内存布局失败: {e}")
            return tensor


class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        self.max_workers = max_workers or mp.cpu_count()
        self.use_processes = use_processes
        self.logger = logging.getLogger(__name__)
    
    def execute_parallel(self, func: Callable, tasks: List[Any], 
                         chunk_size: Optional[int] = None) -> List[Any]:
        """并行执行任务"""
        if not tasks:
            return []
        
        try:
            if self.use_processes:
                # 使用进程池
                with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                    if chunk_size:
                        map_results = list(executor.map(func, tasks, chunksize=chunk_size))
                    else:
                        map_results = list(executor.map(func, tasks))
            else:
                # 使用线程池
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    if chunk_size:
                        map_results = list(executor.map(func, tasks, chunksize=chunk_size))
                    else:
                        map_results = list(executor.map(func, tasks))
            
            return map_results
            
        except Exception as e:
            self.logger.error(f"并行执行失败: {e}")
            # 回退到串行执行
            return [func(task) for task in tasks]
    
    def execute_parallel_with_args(self, func: Callable, args_list: List[tuple]) -> List[Any]:
        """并行执行带参数的任务"""
        if not args_list:
            return []
        
        try:
            if self.use_processes:
                with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(func, *args) for args in args_list]
                    results = [future.result() for future in futures]
            else:
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(func, *args) for args in args_list]
                    results = [future.result() for future in futures]
            
            return results
            
        except Exception as e:
            self.logger.error(f"并行执行失败: {e}")
            # 回退到串行执行
            return [func(*args) for args in args_list]


class GPUAccelerator:
    """GPU加速器主类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gpu_manager = GPUManager()
        self.memory_manager = GPUMemoryManager(self.gpu_manager)
        self.parallel_executor = ParallelExecutor()
        
        # 检查可用的后端
        self._check_available_backends()
    
    def _check_available_backends(self):
        """检查可用的GPU后端"""
        backends = []
        
        if TORCH_AVAILABLE and torch.cuda.is_available():
            backends.append('PyTorch')
        
        if CUPY_AVAILABLE and cp.cuda.is_available():
            backends.append('CuPy')
        
        if NUMBA_AVAILABLE and cuda.is_available():
            backends.append('Numba')
        
        if backends:
            self.logger.info(f"可用的GPU后端: {', '.join(backends)}")
        else:
            self.logger.warning("没有可用的GPU后端")
    
    def accelerate_numpy_operations(self, func: Callable) -> Callable:
        """为numpy操作添加GPU加速装饰器"""
        def wrapper(*args, **kwargs):
            if not self.gpu_manager.gpu_available:
                return func(*args, **kwargs)
            
            try:
                # 尝试将参数转换为GPU张量
                gpu_args = []
                for arg in args:
                    if isinstance(arg, np.ndarray):
                        gpu_arg = self.memory_manager.copy_to_gpu(arg)
                        if gpu_arg is not None:
                            gpu_args.append(gpu_arg)
                        else:
                            gpu_args.append(arg)
                    else:
                        gpu_args.append(arg)
                
                # 执行函数
                result = func(*gpu_args, **kwargs)
                
                # 将结果转换回CPU
                if isinstance(result, (torch.Tensor, 'cp.ndarray' if 'cp' in globals() else type(None))):
                    return self.memory_manager.copy_from_gpu(result)
                else:
                    return result
                    
            except Exception as e:
                self.logger.error(f"GPU加速执行失败: {e}")
                # 回退到CPU执行
                return func(*args, **kwargs)
        
        return wrapper
    
    def batch_matrix_multiply(self, matrices_a: List[np.ndarray], 
                             matrices_b: List[np.ndarray]) -> List[np.ndarray]:
        """批量矩阵乘法"""
        if not self.gpu_manager.gpu_available:
            # CPU实现
            return [np.dot(a, b) for a, b in zip(matrices_a, matrices_b)]
        
        try:
            # GPU实现
            gpu_matrices_a = [self.memory_manager.copy_to_gpu(a) for a in matrices_a]
            gpu_matrices_b = [self.memory_manager.copy_to_gpu(b) for b in matrices_b]
            
            if TORCH_AVAILABLE and torch.cuda.is_available():
                # 使用PyTorch
                gpu_results = [torch.matmul(a, b) for a, b in zip(gpu_matrices_a, gpu_matrices_b)]
                return [self.memory_manager.copy_from_gpu(r) for r in gpu_results]
            
            elif CUPY_AVAILABLE and cp.cuda.is_available():
                # 使用CuPy
                gpu_results = [cp.dot(a, b) for a, b in zip(gpu_matrices_a, gpu_matrices_b)]
                return [self.memory_manager.copy_from_gpu(r) for r in gpu_results]
            
            else:
                # 回退到CPU
                return [np.dot(a, b) for a, b in zip(matrices_a, matrices_b)]
                
        except Exception as e:
            self.logger.error(f"批量矩阵乘法失败: {e}")
            return [np.dot(a, b) for a, b in zip(matrices_a, matrices_b)]
    
    def parallel_apply(self, data: Union[np.ndarray, pd.DataFrame], 
                      func: Callable, axis: int = 0) -> Union[np.ndarray, pd.DataFrame]:
        """并行应用函数"""
        if isinstance(data, pd.DataFrame):
            if axis == 0:
                # 按列并行处理
                columns = [col for col in data.columns]
                
                def process_column(col_name):
                    return func(data[col_name])
                
                results = self.parallel_executor.execute_parallel(process_column, columns)
                return pd.Series(results, index=columns, name=data.index.name)
            
            elif axis == 1:
                # 按行并行处理
                # 分割DataFrame
                row_partitions = np.array_split(data, self.parallel_executor.max_workers)
                
                def process_partition(partition):
                    return partition.apply(func, axis=1)
                
                results = self.parallel_executor.execute_parallel(process_partition, row_partitions)
                return pd.concat(results, ignore_index=True)
        
        elif isinstance(data, np.ndarray):
            if axis == 0:
                # 按列并行处理
                def process_column(i):
                    return func(data[:, i])
                
                results = self.parallel_executor.execute_parallel(process_column, list(range(data.shape[1])))
                return np.column_stack(results)
            
            else:
                # 按行并行处理
                def process_row(i):
                    return func(data[i])
                
                results = self.parallel_executor.execute_parallel(process_row, list(range(data.shape[0])))
                return np.vstack(results)
        
        else:
            return func(data)
    
    def get_accelerator_info(self) -> Dict[str, Any]:
        """获取加速器信息"""
        info = {
            'gpu_available': self.gpu_manager.gpu_available,
            'device_count': self.gpu_manager.device_count,
            'max_workers': self.parallel_executor.max_workers,
            'use_processes': self.parallel_executor.use_processes
        }
        
        if self.gpu_manager.gpu_available:
            info['current_device'] = self.gpu_manager._current_device
            info['device_info'] = self.gpu_manager.get_device_info()
            info['memory_info'] = self.gpu_manager.get_memory_info()
        
        return info


# 全局GPU加速器实例
gpu_accelerator = GPUAccelerator()