"""
性能调优模块
根据实际使用情况优化系统参数，提高投资组合管理和回测系统的性能
"""

import os
import sys
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import json
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

logger = logging.getLogger(__name__)


class OptimizationTarget(Enum):
    """优化目标"""
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    EXECUTION_SPEED = "execution_speed"
    DATA_THROUGHPUT = "data_throughput"
    STRATEGY_PERFORMANCE = "strategy_performance"


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    execution_time: float
    data_processed: int
    strategy_return: float
    sharpe_ratio: float
    max_drawdown: float


@dataclass
class OptimizationConfig:
    """优化配置"""
    # 系统资源限制
    max_memory_usage: float = 80.0  # 最大内存使用率(%)
    max_cpu_usage: float = 85.0  # 最大CPU使用率(%)
    
    # 性能目标
    target_execution_time: float = 5.0  # 目标执行时间(秒)
    target_throughput: float = 1000.0  # 目标数据处理量(条/秒)
    
    # 优化参数
    batch_size_range: Tuple[int, int] = (100, 10000)  # 批处理大小范围
    thread_pool_range: Tuple[int, int] = (1, 8)  # 线程池大小范围
    cache_size_range: Tuple[int, int] = (100, 10000)  # 缓存大小范围
    
    # 策略参数
    topk_range: Tuple[int, int] = (10, 100)  # Topk策略参数范围
    n_drop_range: Tuple[int, int] = (1, 20)  # Drop参数范围
    
    # 优化算法参数
    population_size: int = 50  # 种群大小
    generations: int = 20  # 迭代次数
    mutation_rate: float = 0.1  # 变异率
    crossover_rate: float = 0.8  # 交叉率


class PerformanceTuner:
    """
    性能调优器
    
    使用遗传算法优化系统参数，提高整体性能
    """
    
    def __init__(self, config: OptimizationConfig = None):
        """
        初始化性能调优器
        
        Args:
            config: 优化配置
        """
        self.config = config or OptimizationConfig()
        self.performance_history = []
        self.best_params = {}
        self.optimization_active = False
        self.optimization_thread = None
        
        logger.info("性能调优器初始化完成")
    
    def record_performance(self, metrics: PerformanceMetrics):
        """
        记录性能指标
        
        Args:
            metrics: 性能指标
        """
        self.performance_history.append(metrics)
        
        # 保留最近100条记录
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        logger.debug(f"记录性能指标: CPU={metrics.cpu_usage:.1f}%, "
                   f"内存={metrics.memory_usage:.1f}%, "
                   f"执行时间={metrics.execution_time:.2f}s")
    
    def auto_tune(self, target: OptimizationTarget, 
                 objective_func: Callable[[Dict[str, Any]], float] = None,
                 max_iterations: int = 50) -> Dict[str, Any]:
        """
        自动调优
        
        Args:
            target: 优化目标
            objective_func: 目标函数，接收参数字典，返回评分
            max_iterations: 最大迭代次数
            
        Returns:
            优化后的参数
        """
        if self.optimization_active:
            logger.warning("调优已在进行中")
            return self.best_params
        
        self.optimization_active = True
        
        try:
            logger.info(f"开始自动调优，目标: {target.value}")
            
            # 使用网格搜索进行初步优化
            best_params = self._grid_search(target, objective_func, max_iterations)
            
            # 使用遗传算法进行精细优化
            if len(best_params) > 0:
                best_params = self._genetic_optimization(
                    target, objective_func, best_params, max_iterations
                )
            
            self.best_params = best_params
            logger.info(f"自动调优完成，最佳参数: {best_params}")
            
            return best_params
            
        except Exception as e:
            logger.error(f"自动调优失败: {e}")
            return self.best_params
        
        finally:
            self.optimization_active = False
    
    def _grid_search(self, target: OptimizationTarget,
                   objective_func: Callable[[Dict[str, Any]], float],
                   max_iterations: int) -> Dict[str, Any]:
        """网格搜索"""
        best_params = {}
        best_score = float('-inf')
        
        # 根据目标确定搜索空间
        if target == OptimizationTarget.MEMORY_USAGE:
            search_space = {
                'batch_size': list(range(self.config.batch_size_range[0], 
                                   self.config.batch_size_range[1], 100)),
                'cache_size': list(range(self.config.cache_size_range[0], 
                                    self.config.cache_size_range[1], 100)),
                'thread_pool_size': list(range(self.config.thread_pool_range[0], 
                                         self.config.thread_pool_range[1]))
            }
        elif target == OptimizationTarget.EXECUTION_SPEED:
            search_space = {
                'batch_size': list(range(self.config.batch_size_range[0], 
                                   self.config.batch_size_range[1], 200)),
                'thread_pool_size': list(range(self.config.thread_pool_range[0], 
                                         self.config.thread_pool_range[1]))
            }
        elif target == OptimizationTarget.STRATEGY_PERFORMANCE:
            search_space = {
                'topk': list(range(self.config.topk_range[0], 
                                 self.config.topk_range[1], 5)),
                'n_drop': list(range(self.config.n_drop_range[0], 
                                   self.config.n_drop_range[1]))
            }
        else:
            search_space = {}
        
        # 网格搜索
        iterations = 0
        for params in self._generate_combinations(search_space):
            if iterations >= max_iterations:
                break
                
            try:
                score = objective_func(params)
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                
                iterations += 1
                
            except Exception as e:
                logger.warning(f"参数测试失败: {params}, 错误: {e}")
        
        logger.info(f"网格搜索完成，最佳评分: {best_score:.4f}")
        return best_params
    
    def _genetic_optimization(self, target: OptimizationTarget,
                           objective_func: Callable[[Dict[str, Any]], float],
                           initial_params: Dict[str, Any],
                           max_iterations: int) -> Dict[str, Any]:
        """遗传算法优化"""
        # 初始化种群
        population = self._initialize_population(initial_params)
        
        best_individual = None
        best_fitness = float('-inf')
        
        for generation in range(self.config.generations):
            # 评估适应度
            fitness_scores = []
            for individual in population:
                try:
                    fitness = objective_func(individual)
                    fitness_scores.append(fitness)
                    
                    if fitness > best_fitness:
                        best_fitness = fitness
                        best_individual = individual.copy()
                        
                except Exception as e:
                    logger.warning(f"个体评估失败: {individual}, 错误: {e}")
                    fitness_scores.append(float('-inf'))
            
            # 选择、交叉、变异
            population = self._evolve_population(population, fitness_scores)
            
            logger.debug(f"遗传算法第{generation+1}代，最佳适应度: {best_fitness:.4f}")
        
        logger.info(f"遗传算法优化完成，最佳适应度: {best_fitness:.4f}")
        return best_individual or initial_params
    
    def _initialize_population(self, initial_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """初始化种群"""
        population = [initial_params.copy()]
        
        for _ in range(self.config.population_size - 1):
            individual = initial_params.copy()
            
            # 随机变异
            for key, value in individual.items():
                if isinstance(value, int):
                    # 根据参数类型确定变异范围
                    if key in ['batch_size']:
                        min_val, max_val = self.config.batch_size_range
                    elif key in ['cache_size']:
                        min_val, max_val = self.config.cache_size_range
                    elif key in ['thread_pool_size']:
                        min_val, max_val = self.config.thread_pool_range
                    elif key in ['topk']:
                        min_val, max_val = self.config.topk_range
                    elif key in ['n_drop']:
                        min_val, max_val = self.config.n_drop_range
                    else:
                        min_val, max_val = 0, 1000
                    
                    # 随机变异
                    mutation = np.random.randint(-max_val//10, max_val//10)
                    individual[key] = np.clip(value + mutation, min_val, max_val)
            
            population.append(individual)
        
        return population
    
    def _evolve_population(self, population: List[Dict[str, Any]], 
                         fitness_scores: List[float]) -> List[Dict[str, Any]]:
        """进化种群"""
        # 选择（锦标赛选择）
        selected = self._tournament_selection(population, fitness_scores)
        
        # 交叉
        offspring = []
        for i in range(0, len(selected), 2):
            if i + 1 < len(selected):
                parent1, parent2 = selected[i], selected[i + 1]
                if np.random.random() < self.config.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                    offspring.extend([child1, child2])
                else:
                    offspring.extend([parent1.copy(), parent2.copy()])
        
        # 变异
        for individual in offspring:
            if np.random.random() < self.config.mutation_rate:
                self._mutate(individual)
        
        # 组合新种群
        new_population = selected + offspring
        
        # 保持种群大小
        while len(new_population) < self.config.population_size:
            new_population.append(selected[np.random.randint(0, len(selected))].copy())
        
        return new_population[:self.config.population_size]
    
    def _tournament_selection(self, population: List[Dict[str, Any]], 
                           fitness_scores: List[float], 
                           tournament_size: int = 3) -> List[Dict[str, Any]]:
        """锦标赛选择"""
        selected = []
        
        for _ in range(len(population)):
            # 随机选择锦标赛参与者
            tournament_indices = np.random.choice(
                len(population), 
                min(tournament_size, len(population)), 
                replace=False
            )
            
            # 选择最佳个体
            best_idx = max(tournament_indices, 
                          key=lambda i: fitness_scores[i])
            selected.append(population[best_idx].copy())
        
        return selected
    
    def _crossover(self, parent1: Dict[str, Any], 
                  parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """交叉操作"""
        child1, child2 = parent1.copy(), parent2.copy()
        
        # 单点交叉
        keys = list(parent1.keys())
        if len(keys) > 1:
            crossover_point = np.random.randint(1, len(keys))
            keys1, keys2 = keys[:crossover_point], keys[crossover_point:]
            
            for key in keys2:
                child1[key] = parent2[key]
            for key in keys1:
                child2[key] = parent1[key]
        
        return child1, child2
    
    def _mutate(self, individual: Dict[str, Any]):
        """变异操作"""
        for key, value in individual.items():
            if isinstance(value, int) and np.random.random() < 0.1:
                # 根据参数类型确定变异范围
                if key in ['batch_size']:
                    min_val, max_val = self.config.batch_size_range
                elif key in ['cache_size']:
                    min_val, max_val = self.config.cache_size_range
                elif key in ['thread_pool_size']:
                    min_val, max_val = self.config.thread_pool_range
                elif key in ['topk']:
                    min_val, max_val = self.config.topk_range
                elif key in ['n_drop']:
                    min_val, max_val = self.config.n_drop_range
                else:
                    min_val, max_val = 0, 1000
                
                # 随机变异
                mutation_range = (max_val - min_val) * 0.1
                individual[key] = np.clip(
                    value + np.random.randint(-mutation_range, mutation_range),
                    min_val, max_val
                )
    
    def _generate_combinations(self, search_space: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """生成参数组合"""
        if not search_space:
            return [{}]
        
        keys = list(search_space.keys())
        combinations = []
        
        def generate_recursive(index, current_combination):
            if index == len(keys):
                combinations.append(current_combination.copy())
                return
            
            key = keys[index]
            for value in search_space[key]:
                current_combination[key] = value
                generate_recursive(index + 1, current_combination)
        
        generate_recursive(0, {})
        return combinations
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Args:
            hours: 统计时间范围(小时)
            
        Returns:
            性能摘要
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.performance_history 
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        # 计算统计指标
        cpu_usage = [m.cpu_usage for m in recent_metrics]
        memory_usage = [m.memory_usage for m in recent_metrics]
        execution_time = [m.execution_time for m in recent_metrics]
        strategy_return = [m.strategy_return for m in recent_metrics]
        
        summary = {
            'performance_count': len(recent_metrics),
            'cpu_usage': {
                'average': np.mean(cpu_usage),
                'max': np.max(cpu_usage),
                'min': np.min(cpu_usage),
                'current': cpu_usage[-1] if cpu_usage else 0
            },
            'memory_usage': {
                'average': np.mean(memory_usage),
                'max': np.max(memory_usage),
                'min': np.min(memory_usage),
                'current': memory_usage[-1] if memory_usage else 0
            },
            'execution_time': {
                'average': np.mean(execution_time),
                'max': np.max(execution_time),
                'min': np.min(execution_time),
                'current': execution_time[-1] if execution_time else 0
            },
            'strategy_performance': {
                'average_return': np.mean(strategy_return),
                'max_return': np.max(strategy_return),
                'min_return': np.min(strategy_return),
                'current_return': strategy_return[-1] if strategy_return else 0
            }
        }
        
        return summary
    
    def export_optimization_results(self, filename: str):
        """
        导出优化结果
        
        Args:
            filename: 导出文件名
        """
        results = {
            'best_parameters': self.best_params,
            'optimization_config': {
                'max_memory_usage': self.config.max_memory_usage,
                'max_cpu_usage': self.config.max_cpu_usage,
                'target_execution_time': self.config.target_execution_time,
                'target_throughput': self.config.target_throughput,
                'population_size': self.config.population_size,
                'generations': self.config.generations,
                'mutation_rate': self.config.mutation_rate,
                'crossover_rate': self.config.crossover_rate
            },
            'performance_summary': self.get_performance_summary(),
            'optimization_timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"优化结果已导出到: {filename}")


# 全局性能调优器实例
_global_tuner = None


def get_performance_tuner(config: OptimizationConfig = None) -> PerformanceTuner:
    """获取全局性能调优器实例"""
    global _global_tuner
    
    if _global_tuner is None:
        _global_tuner = PerformanceTuner(config)
    
    return _global_tuner


def test_performance_tuner():
    """测试性能调优器"""
    print("=" * 70)
    print("测试性能调优器")
    print("=" * 70)
    
    try:
        # 创建调优配置
        config = OptimizationConfig(
            max_memory_usage=75.0,
            max_cpu_usage=80.0,
            target_execution_time=3.0,
            batch_size_range=(50, 500),
            thread_pool_range=(1, 4)
        )
        
        # 创建调优器
        tuner = PerformanceTuner(config)
        
        # 定义目标函数
        def objective_function(params):
            # 模拟性能评估
            batch_size = params.get('batch_size', 100)
            thread_pool_size = params.get('thread_pool_size', 2)
            
            # 简单的性能模型
            cpu_score = 100 - (thread_pool_size * 10)  # 线程越多CPU使用越高
            memory_score = 100 - (batch_size * 0.01)  # 批处理越大内存使用越高
            speed_score = min(100, batch_size / 10)  # 批处理越大速度越快
            
            # 综合评分
            score = (cpu_score + memory_score + speed_score) / 3
            return score
        
        # 记录一些测试性能数据
        now = datetime.now()
        test_metrics = PerformanceMetrics(
            timestamp=now,
            cpu_usage=65.5,
            memory_usage=70.2,
            execution_time=4.5,
            data_processed=1000,
            strategy_return=0.05,
            sharpe_ratio=1.2,
            max_drawdown=-0.08
        )
        tuner.record_performance(test_metrics)
        
        # 自动调优
        best_params = tuner.auto_tune(
            target=OptimizationTarget.EXECUTION_SPEED,
            objective_func=objective_function,
            max_iterations=10
        )
        
        print(f"🎯 最佳参数: {best_params}")
        
        # 获取性能摘要
        summary = tuner.get_performance_summary()
        print(f"📊 性能摘要: {summary}")
        
        print("✅ 性能调优器测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 性能调优器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_performance_tuner()