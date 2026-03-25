"""
任务调度器详细测试

测试QLib工作流管理器的任务调度器，支持高效的任务调度和执行
"""

import os
import sys
import time
import threading
import unittest

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_scheduler import TaskScheduler, TaskStatus


class TestTaskSchedulerDetailed(unittest.TestCase):
    """任务调度器详细测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.scheduler = TaskScheduler(max_workers=2)
        
        # 定义测试函数
        def simple_task(x, y):
            """简单测试任务"""
            time.sleep(0.1)  # 模拟耗时操作
            return x + y
        
        def failing_task():
            """失败任务"""
            raise ValueError("测试任务失败")
        
        def long_running_task(duration):
            """长时间运行任务"""
            time.sleep(duration)
            return f"任务完成，耗时{duration}秒"
        
        self.simple_task = simple_task
        self.failing_task = failing_task
        self.long_running_task = long_running_task
    
    def tearDown(self):
        """测试后清理"""
        self.scheduler.shutdown(wait=False)
    
    def test_scheduler_initialization(self):
        """测试调度器初始化"""
        # 验证初始状态
        self.assertEqual(self.scheduler.max_workers, 2)
        self.assertEqual(len(self.scheduler.tasks), 0)
        self.assertEqual(len(self.scheduler.futures), 0)
        
        # 测试自定义工作线程数
        custom_scheduler = TaskScheduler(max_workers=4)
        self.assertEqual(custom_scheduler.max_workers, 4)
        custom_scheduler.shutdown(wait=False)
    
    def test_add_task(self):
        """测试添加任务"""
        # 添加简单任务
        task = self.scheduler.add_task(
            task_id="task1",
            name="简单任务",
            func=self.simple_task,
            args=(1, 2)
        )
        
        # 验证任务添加
        self.assertIn("task1", self.scheduler.tasks)
        self.assertEqual(task.id, "task1")
        self.assertEqual(task.name, "简单任务")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.args, (1, 2))
        self.assertEqual(task.kwargs, {})
        self.assertEqual(task.dependencies, [])
        
        # 添加带参数的任务
        task2 = self.scheduler.add_task(
            task_id="task2",
            name="参数任务",
            func=self.simple_task,
            args=(3, 4),
            kwargs={"delay": 0.1},
            dependencies=["task1"]
        )
        
        # 验证参数
        self.assertEqual(task2.args, (3, 4))
        self.assertEqual(task2.kwargs, {"delay": 0.1})
        self.assertEqual(task2.dependencies, ["task1"])
    
    def test_run_single_task(self):
        """测试运行单个任务"""
        # 添加并运行任务
        self.scheduler.add_task(
            task_id="single_task",
            name="单个任务",
            func=self.simple_task,
            args=(5, 3)
        )
        
        # 运行任务
        result = self.scheduler.run_task("single_task")
        
        # 验证结果
        self.assertEqual(result, 8)
        
        # 验证任务状态
        task = self.scheduler.tasks["single_task"]
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result, 8)
        self.assertIsNotNone(task.start_time)
        self.assertIsNotNone(task.end_time)
    
    def test_run_task_with_dependencies(self):
        """测试运行带依赖的任务"""
        # 添加依赖任务
        self.scheduler.add_task(
            task_id="dep_task",
            name="依赖任务",
            func=self.simple_task,
            args=(1, 1)
        )
        
        # 添加主任务
        self.scheduler.add_task(
            task_id="main_task",
            name="主任务",
            func=self.simple_task,
            args=(2, 2),
            dependencies=["dep_task"]
        )
        
        # 先运行依赖任务
        dep_result = self.scheduler.run_task("dep_task")
        self.assertEqual(dep_result, 2)
        
        # 再运行主任务
        main_result = self.scheduler.run_task("main_task")
        self.assertEqual(main_result, 4)
        
        # 验证状态
        dep_task = self.scheduler.tasks["dep_task"]
        main_task = self.scheduler.tasks["main_task"]
        self.assertEqual(dep_task.status, TaskStatus.COMPLETED)
        self.assertEqual(main_task.status, TaskStatus.COMPLETED)
    
    def test_dependency_validation(self):
        """测试依赖验证"""
        # 添加带未完成依赖的任务
        self.scheduler.add_task(
            task_id="task_with_dep",
            name="带依赖任务",
            func=self.simple_task,
            args=(1, 2),
            dependencies=["nonexistent_dep"]
        )
        
        # 应该抛出依赖未满足异常
        with self.assertRaises(RuntimeError):
            self.scheduler.run_task("task_with_dep")
    
    def test_failing_task(self):
        """测试失败任务"""
        # 添加失败任务
        self.scheduler.add_task(
            task_id="failing_task",
            name="失败任务",
            func=self.failing_task
        )
        
        # 运行任务应该抛出异常
        with self.assertRaises(ValueError):
            self.scheduler.run_task("failing_task")
        
        # 验证任务状态
        task = self.scheduler.tasks["failing_task"]
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertIsInstance(task.error, ValueError)
        self.assertIsNotNone(task.start_time)
        self.assertIsNotNone(task.end_time)
    
    def test_workflow_execution(self):
        """测试工作流执行"""
        # 添加多个任务
        self.scheduler.add_task(
            task_id="task1",
            name="任务1",
            func=self.simple_task,
            args=(1, 1)
        )
        
        self.scheduler.add_task(
            task_id="task2",
            name="任务2",
            func=self.simple_task,
            args=(2, 2)
        )
        
        self.scheduler.add_task(
            task_id="task3",
            name="任务3",
            func=self.simple_task,
            args=(3, 3),
            dependencies=["task1", "task2"]
        )
        
        # 运行工作流
        results = self.scheduler.run_workflow()
        
        # 验证结果
        self.assertEqual(len(results), 3)
        self.assertEqual(results["task1"], 2)
        self.assertEqual(results["task2"], 4)
        self.assertEqual(results["task3"], 6)
        
        # 验证任务状态
        for task_id in ["task1", "task2", "task3"]:
            task = self.scheduler.tasks[task_id]
            self.assertEqual(task.status, TaskStatus.COMPLETED)
    
    def test_partial_workflow_execution(self):
        """测试部分工作流执行"""
        # 添加多个任务
        self.scheduler.add_task(
            task_id="task1",
            name="任务1",
            func=self.simple_task,
            args=(1, 1)
        )
        
        self.scheduler.add_task(
            task_id="task2",
            name="任务2",
            func=self.simple_task,
            args=(2, 2)
        )
        
        self.scheduler.add_task(
            task_id="task3",
            name="任务3",
            func=self.simple_task,
            args=(3, 3)
        )
        
        # 只运行部分任务
        results = self.scheduler.run_workflow(["task1", "task3"])
        
        # 验证结果
        self.assertEqual(len(results), 2)
        self.assertEqual(results["task1"], 2)
        self.assertEqual(results["task3"], 6)
        
        # 验证task2未运行
        task2 = self.scheduler.tasks["task2"]
        self.assertEqual(task2.status, TaskStatus.PENDING)
    
    def test_task_cancellation(self):
        """测试任务取消"""
        # 添加长时间运行任务
        self.scheduler.add_task(
            task_id="long_task",
            name="长时间任务",
            func=self.long_running_task,
            args=(5)  # 5秒任务
        )
        
        # 启动任务但不等待完成
        self.scheduler.executor.submit(
            self.scheduler.run_task, "long_task"
        )
        
        # 等待任务开始
        time.sleep(0.1)
        
        # 取消任务
        cancelled = self.scheduler.cancel_task("long_task")
        
        # 验证取消结果
        self.assertTrue(cancelled)
        
        # 验证任务状态
        task = self.scheduler.tasks["long_task"]
        self.assertEqual(task.status, TaskStatus.CANCELLED)
    
    def test_pending_task_cancellation(self):
        """测试待执行任务取消"""
        # 添加任务
        self.scheduler.add_task(
            task_id="pending_task",
            name="待执行任务",
            func=self.simple_task,
            args=(1, 1)
        )
        
        # 取消待执行任务
        cancelled = self.scheduler.cancel_task("pending_task")
        
        # 验证取消结果
        self.assertTrue(cancelled)
        
        # 验证任务状态
        task = self.scheduler.tasks["pending_task"]
        self.assertEqual(task.status, TaskStatus.CANCELLED)
    
    def test_task_status_tracking(self):
        """测试任务状态跟踪"""
        # 添加任务
        self.scheduler.add_task(
            task_id="status_task",
            name="状态测试任务",
            func=self.simple_task,
            args=(1, 2)
        )
        
        # 验证初始状态
        status = self.scheduler.get_task_status("status_task")
        self.assertEqual(status, TaskStatus.PENDING)
        
        # 运行任务
        self.scheduler.run_task("status_task")
        
        # 验证完成状态
        status = self.scheduler.get_task_status("status_task")
        self.assertEqual(status, TaskStatus.COMPLETED)
        
        # 测试不存在的任务
        with self.assertRaises(ValueError):
            self.scheduler.get_task_status("nonexistent_task")
    
    def test_clear_completed_tasks(self):
        """测试清除已完成任务"""
        # 添加并完成任务
        self.scheduler.add_task(
            task_id="completed_task",
            name="已完成任务",
            func=self.simple_task,
            args=(1, 1)
        )
        
        self.scheduler.run_task("completed_task")
        
        # 添加失败任务
        self.scheduler.add_task(
            task_id="failed_task",
            name="失败任务",
            func=self.failing_task
        )
        
        try:
            self.scheduler.run_task("failed_task")
        except ValueError:
            pass  # 预期的异常
        
        # 添加待执行任务
        self.scheduler.add_task(
            task_id="pending_task",
            name="待执行任务",
            func=self.simple_task,
            args=(2, 2)
        )
        
        # 清除已完成任务
        self.scheduler.clear_completed_tasks()
        
        # 验证清除结果
        self.assertNotIn("completed_task", self.scheduler.tasks)
        self.assertNotIn("failed_task", self.scheduler.tasks)
        self.assertIn("pending_task", self.scheduler.tasks)
        
        # 验证待执行任务状态
        pending_task = self.scheduler.tasks["pending_task"]
        self.assertEqual(pending_task.status, TaskStatus.PENDING)
    
    def test_workflow_progress(self):
        """测试工作流进度"""
        # 添加任务
        self.scheduler.add_task(
            task_id="progress_task1",
            name="进度任务1",
            func=self.simple_task,
            args=(1, 1)
        )
        
        self.scheduler.add_task(
            task_id="progress_task2",
            name="进度任务2",
            func=self.simple_task,
            args=(2, 2)
        )
        
        # 获取初始进度
        progress = self.scheduler.get_workflow_progress()
        self.assertEqual(progress["total_tasks"], 2)
        self.assertEqual(progress["completed_tasks"], 0)
        self.assertEqual(progress["failed_tasks"], 0)
        self.assertEqual(progress["running_tasks"], 0)
        self.assertEqual(progress["progress_percentage"], 0)
        
        # 完成一个任务
        self.scheduler.run_task("progress_task1")
        
        # 获取更新后的进度
        progress = self.scheduler.get_workflow_progress()
        self.assertEqual(progress["total_tasks"], 2)
        self.assertEqual(progress["completed_tasks"], 1)
        self.assertEqual(progress["failed_tasks"], 0)
        self.assertEqual(progress["running_tasks"], 0)
        self.assertEqual(progress["progress_percentage"], 50)
        
        # 验证任务详情
        tasks = progress["tasks"]
        self.assertIn("progress_task1", tasks)
        self.assertEqual(tasks["progress_task1"]["status"], "completed")
        self.assertIsNotNone(tasks["progress_task1"]["start_time"])
        self.assertIsNotNone(tasks["progress_task1"]["end_time"])
        self.assertIsNone(tasks["progress_task1"]["error"])
        
        self.assertIn("progress_task2", tasks)
        self.assertEqual(tasks["progress_task2"]["status"], "pending")
        self.assertIsNone(tasks["progress_task2"]["start_time"])
        self.assertIsNone(tasks["progress_task2"]["end_time"])
    
    def test_concurrent_task_execution(self):
        """测试并发任务执行"""
        # 添加多个独立任务
        for i in range(4):
            self.scheduler.add_task(
                task_id=f"concurrent_task_{i}",
                name=f"并发任务{i}",
                func=self.simple_task,
                args=(i, i+1)
            )
        
        # 记录开始时间
        start_time = time.time()
        
        # 运行工作流
        results = self.scheduler.run_workflow()
        
        # 记录结束时间
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证结果
        self.assertEqual(len(results), 4)
        for i in range(4):
            task_id = f"concurrent_task_{i}"
            self.assertEqual(results[task_id], i + (i+1))
        
        # 验证并发执行（应该比串行执行快）
        # 串行执行需要约0.4秒（4个任务×0.1秒），并发执行应该更快
        self.assertLess(execution_time, 0.3)
    
    def test_complex_dependency_graph(self):
        """测试复杂依赖图"""
        # 创建复杂依赖图：
        # task1 -> task3 -> task5
        # task2 -> task3 -> task6
        # task4 -> task6
        self.scheduler.add_task("task1", "任务1", self.simple_task, (1, 1))
        self.scheduler.add_task("task2", "任务2", self.simple_task, (2, 2))
        self.scheduler.add_task("task4", "任务4", self.simple_task, (4, 4))
        
        self.scheduler.add_task(
            "task3", "任务3", self.simple_task, (3, 3),
            dependencies=["task1", "task2"]
        )
        
        self.scheduler.add_task(
            "task5", "任务5", self.simple_task, (5, 5),
            dependencies=["task3"]
        )
        
        self.scheduler.add_task(
            "task6", "任务6", self.simple_task, (6, 6),
            dependencies=["task3", "task4"]
        )
        
        # 运行工作流
        results = self.scheduler.run_workflow()
        
        # 验证结果
        self.assertEqual(len(results), 6)
        self.assertEqual(results["task1"], 2)
        self.assertEqual(results["task2"], 4)
        self.assertEqual(results["task3"], 6)
        self.assertEqual(results["task4"], 8)
        self.assertEqual(results["task5"], 10)
        self.assertEqual(results["task6"], 12)
        
        # 验证执行顺序
        task1 = self.scheduler.tasks["task1"]
        task2 = self.scheduler.tasks["task2"]
        task3 = self.scheduler.tasks["task3"]
        task4 = self.scheduler.tasks["task4"]
        task5 = self.scheduler.tasks["task5"]
        task6 = self.scheduler.tasks["task6"]
        
        # task1和task2应该在task3之前完成
        self.assertLess(task1.end_time, task3.start_time)
        self.assertLess(task2.end_time, task3.start_time)
        
        # task3应该在task5和task6之前完成
        self.assertLess(task3.end_time, task5.start_time)
        self.assertLess(task3.end_time, task6.start_time)
        
        # task4应该在task6之前完成
        self.assertLess(task4.end_time, task6.start_time)
    
    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""
        # 创建循环依赖：task1 -> task2 -> task3 -> task1
        self.scheduler.add_task("task1", "任务1", self.simple_task, (1, 1))
        self.scheduler.add_task(
            "task2", "任务2", self.simple_task, (2, 2),
            dependencies=["task1"]
        )
        self.scheduler.add_task(
            "task3", "任务3", self.simple_task, (3, 3),
            dependencies=["task2"]
        )
        self.scheduler.add_task(
            "task1_circular", "任务1循环", self.simple_task, (1, 1),
            dependencies=["task3"]
        )
        
        # 应该检测到循环依赖
        with self.assertRaises(ValueError):
            self.scheduler.run_workflow()
    
    def test_error_handling_in_workflow(self):
        """测试工作流中的错误处理"""
        # 添加正常任务
        self.scheduler.add_task(
            "normal_task", "正常任务", self.simple_task, (1, 1)
        )
        
        # 添加失败任务
        self.scheduler.add_task(
            "failing_task", "失败任务", self.failing_task
        )
        
        # 添加依赖失败任务的任务
        self.scheduler.add_task(
            "dependent_task", "依赖任务", self.simple_task, (2, 2),
            dependencies=["failing_task"]
        )
        
        # 运行工作流
        results = self.scheduler.run_workflow()
        
        # 验证结果
        self.assertEqual(results["normal_task"], 2)
        self.assertIsNone(results["failing_task"])
        self.assertIsNone(results["dependent_task"])
        
        # 验证状态
        normal_task = self.scheduler.tasks["normal_task"]
        failing_task = self.scheduler.tasks["failing_task"]
        dependent_task = self.scheduler.tasks["dependent_task"]
        
        self.assertEqual(normal_task.status, TaskStatus.COMPLETED)
        self.assertEqual(failing_task.status, TaskStatus.FAILED)
        self.assertEqual(dependent_task.status, TaskStatus.PENDING)
    
    def test_performance_with_many_tasks(self):
        """测试大量任务的性能"""
        # 添加大量任务
        num_tasks = 100
        for i in range(num_tasks):
            self.scheduler.add_task(
                f"perf_task_{i}", f"性能任务{i}", self.simple_task, (i, i+1)
            )
        
        # 测量执行时间
        start_time = time.time()
        results = self.scheduler.run_workflow()
        end_time = time.time()
        
        # 验证结果
        self.assertEqual(len(results), num_tasks)
        for i in range(num_tasks):
            task_id = f"perf_task_{i}"
            self.assertEqual(results[task_id], i + (i+1))
        
        # 验证性能（应该比串行执行快）
        execution_time = end_time - start_time
        serial_time = num_tasks * 0.1  # 串行执行时间
        self.assertLess(execution_time, serial_time * 0.5)  # 至少快50%
    
    def test_thread_safety(self):
        """测试线程安全性"""
        results = []
        errors = []
        
        def add_and_run_task(task_id, value):
            """添加并运行任务的线程函数"""
            try:
                self.scheduler.add_task(
                    task_id, f"线程任务{task_id}", self.simple_task, (value, value)
                )
                result = self.scheduler.run_task(task_id)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # 创建多个线程同时添加和运行任务
        threads = []
        for i in range(10):
            thread = threading.Thread(
                target=add_and_run_task, args=(f"thread_task_{i}", i)
            )
            threads.append(thread)
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertEqual(len(errors), 0, f"线程安全错误: {errors}")
        self.assertEqual(len(results), 10)
        for i in range(10):
            self.assertIn(i * 2, results)


if __name__ == '__main__':
    unittest.main()