"""
代码执行追踪和性能分析日志系统

提供详细的函数调用追踪、性能计时和执行路径记录
"""

import functools
import time
import logging
from contextlib import contextmanager
from typing import Optional, Callable, Any
from loguru import logger


# 创建TRACE级别（比DEBUG更详细）
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


def trace_performance(func: Callable) -> Callable:
    """
    性能追踪装饰器

    记录函数执行时间、调用参数和返回结果

    使用示例:
    @trace_performance
    def get_historical_kline(self, symbol, period):
        ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 获取函数信息
        func_name = func.__name__
        module_name = func.__module__

        # 记录开始
        start_time = time.perf_counter()
        start_ns = time.perf_counter_ns()

        # 格式化参数（保护敏感信息）
        args_repr = [repr(a) if len(repr(a)) < 100 else f"{type(a).__name__}(...large...)" for a in args[1:]]  # 排除self
        kwargs_repr = [f"{k}={v!r}" if len(repr(v)) < 100 else f"{k}={type(v).__name__}(...large...)" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        if len(signature) > 500:
            signature = signature[:500] + "... [truncated]"

        logger.opt(depth=1).trace(f"[TRACE] ▶️  {func_name}({signature})")

        try:
            # 执行函数
            result = func(*args, **kwargs)

            # 计算耗时
            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000
            elapsed_ns = time.perf_counter_ns() - start_ns

            # 格式化结果
            if result is not None:
                if hasattr(result, '__len__'):
                    result_str = f"{type(result).__name__}(len={len(result)})"
                elif hasattr(result, 'shape'):
                    result_str = f"{type(result).__name__}(shape={result.shape})"
                else:
                    result_str = f"{type(result).__name__}"
            else:
                result_str = "None"

            logger.opt(depth=1).trace(
                f"[TRACE] ✅ {func_name} | "
                f"耗时: {elapsed_ms:.2f}ms ({elapsed_ns}ns) | "
                f"返回: {result_str}"
            )

            return result

        except Exception as e:
            # 计算耗时（即使出错）
            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000

            logger.opt(depth=1).trace(
                f"[TRACE] ❌ {func_name} | "
                f"耗时: {elapsed_ms:.2f}ms | "
                f"异常: {type(e).__name__}: {str(e)[:100]}"
            )
            raise

    return wrapper


@contextmanager
def trace_block(block_name: str, extra_info: Optional[dict] = None):
    """
    代码块追踪上下文管理器

    用于追踪任意代码块的执行时间

    使用示例:
    with trace_block("数据聚合", {"symbol": symbol, "period": period}):
        df = aggregate_data(raw_data)
    """
    start_time = time.perf_counter()
    extra_str = f" | {extra_info}" if extra_info else ""

    logger.trace(f"[TRACE] ▶️  开始: {block_name}{extra_str}")

    try:
        yield

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.trace(f"[TRACE] ✅ 完成: {block_name} | 耗时: {elapsed_ms:.2f}ms")

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.trace(f"[TRACE] ❌ 失败: {block_name} | 耗时: {elapsed_ms:.2f}ms | 异常: {type(e).__name__}")
        raise


class TraceContext:
    """
    追踪上下文

    用于追踪跨多个函数的完整操作链路
    """

    def __init__(self, operation_name: str, **context_vars):
        self.operation_name = operation_name
        self.context_vars = context_vars
        self.start_time = None
        self.end_time = None
        self.steps = []

    def __enter__(self):
        self.start_time = time.perf_counter()
        context_str = ", ".join([f"{k}={v}" for k, v in self.context_vars.items()])
        logger.trace(f"[TRACE] 🚀 开始操作: {self.operation_name} | {context_str}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        elapsed_ms = (self.end_time - self.start_time) * 1000

        if exc_type is None:
            logger.trace(f"[TRACE] 🏁 完成操作: {self.operation_name} | 总耗时: {elapsed_ms:.2f}ms | 步骤: {len(self.steps)}")
        else:
            logger.trace(f"[TRACE] 💥 操作失败: {self.operation_name} | 总耗时: {elapsed_ms:.2f}ms | 异常: {exc_type.__name__}")

        return False  # 不吞异常

    def add_step(self, step_name: str, **step_info):
        """添加步骤记录"""
        step_time = time.perf_counter()
        if self.start_time:
            elapsed_since_start = (step_time - self.start_time) * 1000
        else:
            elapsed_since_start = 0

        info_str = ", ".join([f"{k}={v}" for k, v in step_info.items()]) if step_info else ""
        self.steps.append({
            "name": step_name,
            "time": step_time,
            "elapsed_ms": elapsed_since_start
        })

        logger.trace(f"[TRACE] 📍 步骤: {self.operation_name}.{step_name} | 已耗时: {elapsed_since_start:.2f}ms | {info_str}")


def log_variable(name: str, value: Any, max_length: int = 200):
    """
    记录变量值

    用于追踪关键变量的变化
    """
    value_str = repr(value)
    if len(value_str) > max_length:
        value_str = value_str[:max_length] + f"... [truncated, total {len(value_str)} chars]"

    logger.trace(f"[TRACE] 📊 变量 {name} = {value_str}")


# 性能计数器
class PerformanceCounter:
    """
    性能计数器

    统计函数调用次数和平均耗时
    """

    def __init__(self):
        self.stats = {}

    def record(self, func_name: str, elapsed_ms: float):
        """记录一次调用"""
        if func_name not in self.stats:
            self.stats[func_name] = {
                "count": 0,
                "total_ms": 0,
                "min_ms": float('inf'),
                "max_ms": 0
            }

        stat = self.stats[func_name]
        stat["count"] += 1
        stat["total_ms"] += elapsed_ms
        stat["min_ms"] = min(stat["min_ms"], elapsed_ms)
        stat["max_ms"] = max(stat["max_ms"], elapsed_ms)

    def report(self):
        """生成性能报告"""
        logger.trace("[TRACE] 📈 性能统计报告:")
        for func_name, stat in sorted(self.stats.items(), key=lambda x: x[1]["total_ms"], reverse=True):
            avg_ms = stat["total_ms"] / stat["count"] if stat["count"] > 0 else 0
            logger.trace(
                f"[TRACE]   {func_name}: "
                f"调用{stat['count']}次 | "
                f"平均{avg_ms:.2f}ms | "
                f"最小{stat['min_ms']:.2f}ms | "
                f"最大{stat['max_ms']:.2f}ms | "
                f"总计{stat['total_ms']:.2f}ms"
            )


# 全局性能计数器
perf_counter = PerformanceCounter()


def trace_with_counter(func: Callable) -> Callable:
    """
    带性能统计的追踪装饰器
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        func_name = func.__name__

        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            perf_counter.record(func_name, elapsed_ms)
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            perf_counter.record(func_name, elapsed_ms)
            raise

    return wrapper
