# TdxQuant 测试套件

## 📋 概述

这是TdxQuant数据源的完整测试套件，旨在验证TdxQuant的L0-L5各层级能力，并与文档中的测试结果进行对比。

## 🎯 测试目标

1. **验证功能完整性** - 测试TdxQuant各层级的数据获取能力
2. **性能基准测试** - 测量各项操作的性能并与文档对比
3. **限制验证** - 验证数据获取的限制和边界条件
4. **数据质量** - 验证返回数据的格式和准确性
5. **优势确认** - 验证TdxQuant的主要优势领域

## 📁 文件结构

```
tests/
├── config.py                 # 测试配置
├── test_utils.py            # 测试工具函数
├── run_all_tests.py         # 运行所有测试
├── test_l1_snapshot.py      # L1实时快照测试
├── test_l3_kline.py        # L3 K线数据测试
├── test_l5_sector.py       # L5板块数据测试
├── test_performance.py      # 性能对比测试
└── test_limits.py          # 限制测试
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 确保Python环境已配置
python --version

# 安装必要的依赖（如果有的话）
pip install -r requirements.txt
```

### 2. 集成TdxQuant API

⚠️ **重要**: 当前测试框架使用模拟数据，需要集成实际的TdxQuant SDK才能运行真实测试。

#### 集成步骤：

1. **获取TdxQuant SDK**
   - 从官方渠道获取TdxQuant Python SDK
   - 或从项目中的适配器代码中引用

2. **修改测试类初始化**

在每个测试文件中，找到类似这样的代码：

```python
class TdxQuantL1Test:
    def __init__(self):
        # TODO: 初始化TdxQuant连接
        self.client = None
```

替换为实际的初始化代码：

```python
from tdxquant_sdk import TdxQuantClient  # 根据实际SDK调整

class TdxQuantL1Test:
    def __init__(self):
        # 初始化TdxQuant连接
        self.client = TdxQuantClient(
            host="localhost",  # 根据实际配置调整
            port=7709
        )
        print("✅ TdxQuant客户端已连接")
```

3. **实现API调用方法**

将所有`TODO`标记的API调用方法替换为实际代码。

示例（test_l1_snapshot.py）：

```python
# 原始代码（模拟数据）
def get_single_snapshot(self, symbol: str):
    return {
        "symbol": symbol,
        "price": 1850.00,
        "volume": 123456
    }

# 替换为实际代码
def get_single_snapshot(self, symbol: str):
    try:
        result = self.client.get_snapshot(symbol)
        return {
            "symbol": symbol,
            "price": result["price"],
            "volume": result["volume"],
            "amount": result.get("amount", 0),
            "bid1": result.get("bid1", 0),
            "ask1": result.get("ask1", 0),
            "timestamp": result.get("time", "")
        }
    except Exception as e:
        print(f"获取快照失败: {e}")
        raise
```

### 3. 运行测试

#### 运行单个测试

```bash
# 运行L1实时快照测试
python tests/test_l1_snapshot.py

# 运行L3 K线数据测试
python tests/test_l3_kline.py

# 运行L5板块数据测试
python tests/test_l5_sector.py
```

#### 运行所有测试

```bash
# 运行完整测试套件
python tests/run_all_tests.py
```

## 📊 测试结果

### 结果文件位置

测试结果会保存在 `../test_results/` 目录下：

```
test_results/
├── test_l1_single_snapshot_20260304_150000.json
├── test_l1_batch_snapshot_20260304_150005.json
├── test_l3_kline_periods_20260304_150010.json
├── test_l5_sector_types_20260304_150015.json
└── ...
```

### 结果格式

每个测试结果JSON文件包含：

```json
{
  "timestamp": "20260304_150000",
  "test_name": "test_l1_single_snapshot",
  "test_type": "L1_single_snapshot",
  "success": true,
  "performance": {
    "avg": 0.62,
    "min": 0.58,
    "max": 0.71,
    "count": 10,
    "errors": 0,
    "success_rate": 100.0
  },
  "document_time": 0.60,
  "diff_percentage": 3.33
}
```

## 📈 测试覆盖

### L0-L5层级测试

| 层级 | 测试文件 | 测试内容 | 状态 |
|------|----------|----------|------|
| L1 | test_l1_snapshot.py | 实时快照、批量快照 | ✅ 已创建 |
| L2 | - | 历史快照 | ⏳ 待创建 |
| L3 | test_l3_kline.py | K线数据、数量限制 | ✅ 已创建 |
| L3 | - | 分笔数据 | ⏳ 待创建 |
| L4 | - | 财务数据 | ⏳ 待创建 |
| L5 | test_l5_sector.py | 板块数据、成分股 | ✅ 已创建 |

### 专项测试

| 测试类型 | 测试文件 | 状态 |
|----------|----------|------|
| 性能测试 | test_performance.py | ✅ 已创建 |
| 限制测试 | test_limits.py | ✅ 已创建 |
| 边界测试 | - | ⏳ 待创建 |

## 🔧 配置说明

### 测试配置 (config.py)

```python
# 测试股票代码
TEST_STOCKS = {
    "贵州茅台": "600519.SH",
    "中国平安": "601318.SH",
    ...
}

# 性能测试配置
PERFORMANCE_CONFIG = {
    "warmup_count": 3,        # 预热次数
    "test_count": 10,          # 测试次数
    "batch_size": 10,          # 批量大小
}

# K线数据配置
KLINE_CONFIG = {
    "periods": ["1m", "5m", "15m", "30m", "60m", "1d", "1w", "1M"],
    "default_period": "1d",
}
```

可以根据需要修改这些配置参数。

## 📝 测试模板

如果需要添加新的测试文件，可以参考以下模板：

```python
"""
测试描述

测试目标：
1. 目标1
2. 目标2
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import (
    measure_performance,
    save_test_result,
    print_performance_result
)
from tests.config import (
    DEFAULT_STOCK,
    PERFORMANCE_CONFIG
)

class MyTestClass:
    def __init__(self):
        # 初始化TdxQuant连接
        self.client = None
        print("\n⚠️ 注意: 需要集成实际的TdxQuant API客户端")

    def my_test_method(self, param):
        """测试方法"""
        # TODO: 实现实际API调用
        pass

def test_my_test():
    """测试函数"""
    print("\n测试开始")

    test = MyTestClass()

    # 测试代码
    result = {}

    # 保存结果
    save_test_result("test_my_test", {
        "test_type": "my_test",
        "success": True,
        "results": result
    })

    return result

if __name__ == "__main__":
    test_my_test()
```

## 📚 参考资料

- [TdxQuant API文档](../../TdxQuant/README.md)
- [L0-L5能力矩阵测试](../01-L0-L5能力矩阵测试.md)
- [文件夹结构对比分析](../文件夹结构对比分析.md)

## ⚠️ 注意事项

1. **API集成**: 当前测试使用模拟数据，必须集成实际SDK才能获得有意义的结果

2. **测试环境**: 建议在测试环境中运行，避免影响生产数据

3. **性能差异**: 测试结果可能因网络、硬件等因素而有所不同

4. **数据限制**: 某些测试（如K线数量限制）需要请求大量数据，注意API限制

5. **错误处理**: 所有测试都应正确处理异常，避免程序崩溃

## 🎯 下一步计划

1. ✅ 创建基础测试框架
2. ⏳ 集成实际TdxQuant API
3. ⏳ 补充L0、L2、L4测试
4. ⏳ 添加边界和错误处理测试
5. ⏳ 生成完整对比报告
6. ⏳ 创建最佳实践指南

## 📞 支持

如有问题或建议，请参考：
- 主项目文档
- 测试结果文件
- TdxQuant官方文档
