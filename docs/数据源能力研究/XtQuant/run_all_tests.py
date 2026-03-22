"""
XtQuant 数据能力完整测试套件

运行所有L0-L5测试，生成完整报告
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

import subprocess
import os

# 测试脚本列表
tests = [
    ('L0-订阅缓存', 'test_l0_subscription.py'),
    ('L1-实时快照', 'test_l1_snapshot.py'),
    ('L2-历史快照', 'test_l2_history.py'),
    ('L3-完整数据', 'test_l3_full.py'),
    ('L3.5-公司数据', 'test_l35_company.py'),
    ('L4-财务数据', 'test_l4_financial.py'),
]

print("="*80)
print("XtQuant 数据能力完整测试")
print("="*80)
print()
print(f"测试数量: {len(tests)}")
print(f"测试目录: {os.path.dirname(__file__)}")
print()
print("开始运行所有测试...")
print()

results = []

# 运行所有测试
for name, script in tests:
    print("="*80)
    print(f"运行: {name} ({script})")
    print("="*80)

    try:
        result = subprocess.run(
            ['python', script],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='ignore'
        )

        status = "[成功]" if result.returncode == 0 else "[失败]"
        results.append({
            'name': name,
            'script': script,
            'status': status,
            'returncode': result.returncode
        })

        print(f"{status} 返回码: {result.returncode}")

        # 打印输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("[超时] 测试运行超过60秒")
        results.append({
            'name': name,
            'script': script,
            'status': '[超时]',
            'returncode': -1
        })
    except Exception as e:
        print(f"[异常] {e}")
        results.append({
            'name': name,
            'script': script,
            'status': '[异常]',
            'returncode': -1
        })

    print()

# 生成汇总报告
print("="*80)
print("测试汇总报告")
print("="*80)
print()

success_count = sum(1 for r in results if r['returncode'] == 0)
fail_count = len(results) - success_count

print(f"总测试数: {len(results)}")
print(f"成功: {success_count}")
print(f"失败: {fail_count}")
print()

print("详细结果:")
print("-"*80)
for r in results:
    print(f"{r['status']} {r['name']:20s} ({r['script']})")

print()
print("="*80)
print("测试完成！")
print("="*80)
print()
print("下一步:")
print("1. 查看每个测试的详细输出")
print("2. 记录测试结果到文档")
print("3. 识别问题并修复")
print("4. 对比不同数据源的能力")
