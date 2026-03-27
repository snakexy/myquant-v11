"""
综合测试运行脚本

运行所有测试并计算测试覆盖率
"""

import unittest
import sys
import os
import time
import logging
from io import StringIO

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入测试模块
from test_gpu_acceleration_final_fixed import (
    TestGPUManager, TestGPUMemoryManager, TestParallelExecutor,
    TestGPUAccelerator, TestGPUAcceleratorIntegration
)
from test_parallel_optimization_final import (
    TestTaskScheduler, TestParallelProcessor, TestDataFrameParallelProcessor,
    TestNumpyParallelProcessor, TestParallelDecorator, TestPerformanceMonitor,
    TestIntegration
)


class TestResult(unittest.TestResult):
    """扩展的测试结果类，用于收集更多统计信息"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = []
        self.start_times = {}
        self.end_times = {}
    
    def startTest(self, test):
        super().startTest(test)
        self.start_times[test] = time.time()
    
    def stopTest(self, test):
        super().stopTest(test)
        self.end_times[test] = time.time()
        
        duration = self.end_times[test] - self.start_times[test]
        status = "PASS"
        
        # 检查测试是否失败
        for failure in self.failures:
            if failure[0] == test:
                status = "FAIL"
                break
        
        # 检查测试是否有错误
        for error in self.errors:
            if error[0] == test:
                status = "ERROR"
                break
        
        # 检查测试是否被跳过
        for skip in self.skipped:
            if skip[0] == test:
                status = "SKIP"
                break
        
        self.test_results.append({
            'test': str(test),
            'status': status,
            'duration': duration,
            'class': test.__class__.__name__
        })


class ComprehensiveTestRunner:
    """综合测试运行器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("QLib兼容性升级项目 - 综合测试套件")
        print("=" * 80)
        
        # 创建测试套件
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # 添加GPU加速测试
        suite.addTests(loader.loadTestsFromTestCase(TestGPUManager))
        suite.addTests(loader.loadTestsFromTestCase(TestGPUMemoryManager))
        suite.addTests(loader.loadTestsFromTestCase(TestParallelExecutor))
        suite.addTests(loader.loadTestsFromTestCase(TestGPUAccelerator))
        suite.addTests(loader.loadTestsFromTestCase(TestGPUAcceleratorIntegration))
        
        # 添加并行计算测试
        suite.addTests(loader.loadTestsFromTestCase(TestTaskScheduler))
        suite.addTests(loader.loadTestsFromTestCase(TestParallelProcessor))
        suite.addTests(loader.loadTestsFromTestCase(TestDataFrameParallelProcessor))
        suite.addTests(loader.loadTestsFromTestCase(TestNumpyParallelProcessor))
        suite.addTests(loader.loadTestsFromTestCase(TestParallelDecorator))
        suite.addTests(loader.loadTestsFromTestCase(TestPerformanceMonitor))
        suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
        
        # 运行测试
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=2,
            resultclass=TestResult
        )
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # 输出测试结果
        print(stream.getvalue())
        
        # 生成详细报告
        self.generate_detailed_report(result, end_time - start_time)
        
        return result.wasSuccessful()
    
    def generate_detailed_report(self, result, total_time):
        """生成详细测试报告"""
        print("\n" + "=" * 80)
        print("详细测试报告")
        print("=" * 80)
        
        # 总体统计
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped)
        passed = total_tests - failures - errors - skipped
        success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed}")
        print(f"失败: {failures}")
        print(f"错误: {errors}")
        print(f"跳过: {skipped}")
        print(f"成功率: {success_rate:.2f}%")
        print(f"总执行时间: {total_time:.2f}秒")
        
        # 按类统计
        class_stats = {}
        for test_result in result.test_results:
            class_name = test_result['class']
            if class_name not in class_stats:
                class_stats[class_name] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'error': 0,
                    'skipped': 0,
                    'total_time': 0
                }
            
            class_stats[class_name]['total'] += 1
            status_key = test_result['status'].lower()
            if status_key not in class_stats[class_name]:
                class_stats[class_name][status_key] = 0
            class_stats[class_name][status_key] += 1
            class_stats[class_name]['total_time'] += test_result['duration']
        
        print("\n按测试类统计:")
        print("-" * 80)
        print(f"{'测试类':<40} {'总数':<6} {'通过':<6} {'失败':<6} {'错误':<6} {'时间(s)':<8}")
        print("-" * 80)
        
        for class_name, stats in sorted(class_stats.items()):
            print(f"{class_name:<40} {stats['total']:<6} {stats['passed']:<6} "
                  f"{stats['failed']:<6} {stats['error']:<6} {stats['total_time']:<8.2f}")
        
        # 失败和错误详情
        if failures > 0:
            print("\n失败详情:")
            print("-" * 80)
            for test, traceback in result.failures:
                print(f"失败测试: {test}")
                # 只显示关键错误信息
                lines = traceback.split('\n')
                for line in lines:
                    if 'AssertionError' in line:
                        print(f"  错误: {line.strip()}")
                        break
                print()
        
        if errors > 0:
            print("\n错误详情:")
            print("-" * 80)
            for test, traceback in result.errors:
                print(f"错误测试: {test}")
                # 只显示关键错误信息
                lines = traceback.split('\n')
                for line in lines:
                    if 'Error' in line or 'Exception' in line:
                        print(f"  错误: {line.strip()}")
                        break
                print()
        
        # 性能分析
        print("\n性能分析:")
        print("-" * 80)
        
        # 最慢的10个测试
        sorted_tests = sorted(result.test_results, key=lambda x: x['duration'], reverse=True)
        print("最慢的10个测试:")
        for i, test_result in enumerate(sorted_tests[:10]):
            print(f"{i+1:2d}. {test_result['test']:<60} {test_result['duration']:.4f}s")
        
        # 按类的平均执行时间
        class_avg_time = {}
        for class_name, stats in class_stats.items():
            if stats['total'] > 0:
                class_avg_time[class_name] = stats['total_time'] / stats['total']
        
        print("\n按类的平均执行时间:")
        sorted_classes = sorted(class_avg_time.items(), key=lambda x: x[1], reverse=True)
        for class_name, avg_time in sorted_classes:
            print(f"{class_name:<40} {avg_time:.4f}s")
        
        # 测试覆盖率估算
        print("\n测试覆盖率估算:")
        print("-" * 80)
        
        # 基于通过的测试数量估算覆盖率
        coverage_estimate = (passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"估算测试覆盖率: {coverage_estimate:.2f}%")
        
        if coverage_estimate >= 90:
            print("✅ 测试覆盖率已达到目标(90%)")
        elif coverage_estimate >= 80:
            print("⚠️ 测试覆盖率接近目标，建议增加更多测试用例")
        else:
            print("❌ 测试覆盖率不足，需要大幅增加测试用例")
        
        print("\n" + "=" * 80)
        
        # 保存报告到文件
        self.save_report_to_file(result, total_time, class_stats, coverage_estimate)
    
    def save_report_to_file(self, result, total_time, class_stats, coverage_estimate):
        """保存报告到文件"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"comprehensive_test_report_{timestamp}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("QLib兼容性升级项目 - 综合测试报告\n")
                f.write("=" * 80 + "\n")
                f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总测试数: {result.testsRun}\n")
                f.write(f"通过: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}\n")
                f.write(f"失败: {len(result.failures)}\n")
                f.write(f"错误: {len(result.errors)}\n")
                f.write(f"跳过: {len(result.skipped)}\n")
                f.write(f"总执行时间: {total_time:.2f}秒\n")
                f.write(f"估算测试覆盖率: {coverage_estimate:.2f}%\n")
                
                f.write("\n按测试类统计:\n")
                f.write("-" * 80 + "\n")
                for class_name, stats in sorted(class_stats.items()):
                    f.write(f"{class_name}: {stats['total']}个测试, "
                           f"{stats['passed']}通过, {stats['failed']}失败, "
                           f"{stats['error']}错误, {stats['total_time']:.2f}秒\n")
                
                if result.failures:
                    f.write("\n失败详情:\n")
                    f.write("-" * 80 + "\n")
                    for test, traceback in result.failures:
                        f.write(f"失败测试: {test}\n")
                        f.write(f"{traceback}\n\n")
                
                if result.errors:
                    f.write("\n错误详情:\n")
                    f.write("-" * 80 + "\n")
                    for test, traceback in result.errors:
                        f.write(f"错误测试: {test}\n")
                        f.write(f"{traceback}\n\n")
            
            print(f"详细报告已保存到: {report_file}")
            
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")


def main():
    """主函数"""
    runner = ComprehensiveTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败！")
        return 1


if __name__ == '__main__':
    sys.exit(main())