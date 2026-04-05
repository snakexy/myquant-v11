# MyQuant V5 测试规范

## 测试范围

### 必须测试的场景
1. **数据获取** - 每个Adapter的 `get_kline()` 方法
2. **数据拼接** - SeamlessKlineService 的历史+实时拼接
3. **架构约束** - Service层不能直接import Adapter
4. **成交量单位** - 在线源返回的是"股"，需转换为"手"（÷100）

### 测试文件位置
```
backend/tests/
├── test_adapters.py          # 测试所有Adapter
├── test_seamless_service.py  # 测试拼接服务
├── test_architecture.py      # 测试架构约束
└── test_volume_unit.py       # 测试成交量单位
```

## 测试用例模板

### Adapter 测试
```python
import pytest
from myquant.core.market.adapters import get_adapter

def test_pytdx_adapter_get_kline():
    """测试 PyTdx Adapter 获取K线"""
    adapter = get_adapter('pytdx')
    
    # 测试正常情况
    data = adapter.get_kline(['000001.SZ'], period='1d', count=10)
    assert data is not None
    assert '000001.SZ' in data
    assert len(data['000001.SZ']) == 10
    
    # 测试成交量单位（应该是"手"，不是"股"）
    df = data['000001.SZ']
    avg_volume = df['volume'].mean()
    assert avg_volume < 100000  # 日线成交量通常 < 10万手
    
    # 测试数据完整性
    assert df['close'].notna().all()
    assert df['high'].max() >= df['close'].max()
    assert df['low'].min() <= df['close'].min()
```

### 架构约束测试
```python
import pytest
import os
import re

def test_service_layer_no_direct_adapter_import():
    """测试 Service 层是否直接 import Adapter"""
    service_dir = 'backend/src/myquant/core/market/services/'
    
    violations = []
    for filename in os.listdir(service_dir):
        if not filename.endswith('.py'):
            continue
        
        filepath = os.path.join(service_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查是否直接 import adapter
            if re.search(r'from\s+myquant\.core\.market\.adapters\.\w+\s+import', content):
                violations.append(filename)
    
    assert len(violations) == 0, f"Service层违规直接import Adapter: {violations}"
```

### 成交量单位测试
```python
def test_volume_unit_consistency():
    """测试成交量单位一致性"""
    symbol = '000001.SZ'
    
    # 从在线源获取数据
    pytdx = get_adapter('pytdx')
    online_data = pytdx.get_kline([symbol], period='60m', count=100)
    
    # 从 HotDB 获取数据
    hotdb = get_adapter('hotdb')
    cached_data = hotdb.get_kline([symbol], period='60m', count=100)
    
    # 对比成交量单位（应该一致）
    online_avg = online_data[symbol]['volume'].mean()
    cached_avg = cached_data[symbol]['volume'].mean()
    
    # 允许10%误差
    assert abs(online_avg - cached_avg) / online_avg < 0.1, \
        f"成交量单位不一致: 在线={online_avg}, 缓存={cached_avg}"
```

## 运行测试

### 手动测试
```bash
# 运行所有测试
pytest backend/tests/

# 运行单个测试文件
pytest backend/tests/test_volume_unit.py

# 运行特定测试用例
pytest backend/tests/test_volume_unit.py::test_volume_unit_consistency

# 显示print输出
pytest -s backend/tests/test_volume_unit.py
```

### 自动测试（Hook）
配置 `.claude/settings.json`：
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "pytest backend/tests/ -v --tb=short"
          }
        ]
      }
    ]
  }
}
```

## 测试失败处理

### 如果测试失败
1. **不要跳过测试** - 修复代码，不是注释测试
2. **查看错误信息** - `pytest -v` 显示详细错误
3. **验证修复** - 重新运行测试直到通过

### 禁止的行为
- ❌ `@pytest.mark.skip` 跳过失败的测试
- ❌ 修改测试用例让错误的代码通过
- ❌ 提交代码前不运行测试
