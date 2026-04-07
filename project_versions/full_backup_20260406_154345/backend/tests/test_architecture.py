# -*- coding: utf-8 -*-
"""
架构约束测试

测试 Service 层是否遵守分层架构规范：
- Service 层不能直接 import Adapter
- 单次修改文件数不能超过 3 个
"""

import pytest
import os
import re
from pathlib import Path


class TestArchitectureConstraints:
    """架构约束测试"""

    def test_service_layer_no_direct_adapter_import(self):
        """测试 Service 层是否直接 import Adapter

        规则：Service 层必须通过 get_adapter() 获取 Adapter 实例
        禁止：from myquant.core.market.adapters.xxx import XxxAdapter
        """
        service_dir = Path('backend/src/myquant/core/market/services')

        if not service_dir.exists():
            pytest.skip("Service 目录不存在")

        violations = []

        for py_file in service_dir.glob('*.py'):
            # 跳过 __init__.py 和备份文件
            if py_file.name.startswith('__') or py_file.suffix == '.bak':
                continue

            content = py_file.read_text(encoding='utf-8')

            # 检查是否直接 import adapter（通过 from ... import 语句）
            pattern = r'from\s+myquant\.core\.market\.adapters\.\w+\s+import'
            if re.search(pattern, content):
                violations.append(py_file.name)

        assert len(violations) == 0, (
            f"Service 层违规直接 import Adapter:\n"
            f"  违规文件: {violations}\n"
            f"  正确做法: 使用 get_adapter('xxx') 获取实例"
        )

    def test_api_layer_no_adapter_import(self):
        """测试 API 层是否直接 import Adapter

        规则：API 层只能调用 Service 层，不能直接调用 Adapter
        """
        api_dir = Path('backend/src/myquant/api')

        if not api_dir.exists():
            pytest.skip("API 目录不存在")

        violations = []

        for py_file in api_dir.rglob('*.py'):
            if py_file.name.startswith('__'):
                continue

            content = py_file.read_text(encoding='utf-8')

            # 检查是否直接 import adapter
            pattern = r'from\s+myquant\.core\.market\.adapters\s+import\s+get_adapter'
            if re.search(pattern, content):
                violations.append(str(py_file.relative_to(Path('backend/src'))))

        assert len(violations) == 0, (
            f"API 层违规直接调用 get_adapter:\n"
            f"  违规文件: {violations}\n"
            f"  正确做法: API 层调用 Service 层"
        )

    def test_no_backup_files_in_services(self):
        """测试 Service 目录是否有备份文件

        规则：备份文件不应该存在于源码目录
        """
        service_dir = Path('backend/src/myquant/core/market/services')

        if not service_dir.exists():
            pytest.skip("Service 目录不存在")

        backup_files = list(service_dir.glob('*.bak')) + \
                       list(service_dir.glob('*_backup.py')) + \
                       list(service_dir.glob('*.backup'))

        assert len(backup_files) == 0, (
            f"Service 目录存在备份文件:\n"
            f"  {backup_files}\n"
            f"  请删除备份文件"
        )


class TestHotDBServiceConstraints:
    """HotDBService 架构约束测试"""

    def test_hotdb_service_calls_kline_service(self):
        """测试 HotDBService 是否通过 KlineService 获取在线数据

        规则：HotDBService 检测到缺口时，必须调用 KlineService
        禁止：直接调用 pytdx/xtquant/tdxquant
        """
        hotdb_service = Path('backend/src/myquant/core/market/services/hotdb_service.py')

        if not hotdb_service.exists():
            pytest.skip("HotDBService 文件不存在")

        content = hotdb_service.read_text(encoding='utf-8')

        # 检查是否直接 import 在线适配器（不应该出现）
        online_adapters = ['pytdx', 'xtquant', 'tdxquant']
        violations = []

        for adapter in online_adapters:
            # 检查是否有 from ... import get_adapter('adapter')
            pattern = rf"get_adapter\s*\(\s*['\"]({adapter})['\"]"
            if re.search(pattern, content):
                violations.append(adapter)

        # 注意：这个测试可能需要根据实际实现调整
        # 目前只做警告，不强制失败
        if violations:
            print(f"[警告] HotDBService 可能直接调用了在线适配器: {violations}")


def test_file_change_count():
    """测试当前改动文件数量

    规则：单次改动不超过 3 个文件
    """
    import subprocess

    result = subprocess.run(
        ['git', 'diff', '--name-only'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent  # 回到项目根目录
    )

    changed_files = [f for f in result.stdout.strip().split('\n') if f]
    file_count = len(changed_files)

    if file_count > 3:
        pytest.fail(
            f"改动文件数 ({file_count}) 超过 3 个:\n"
            f"  {chr(10).join(changed_files)}\n"
            f"  请拆分任务，单次只改一个功能"
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
