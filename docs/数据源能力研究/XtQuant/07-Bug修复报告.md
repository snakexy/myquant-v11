# XtQuant 适配器Bug修复报告

> 修复日期: 2026-02-05
> 修复人员: Team Lead + 研究团队
> 严重级别: 🔴 P0 - 批量获取功能完全不可用

---

## Bug描述

### 现象
- ✅ 单个K线获取正常（`get_kline_data`）
- ❌ 批量K线获取失败（`get_kline_batch`）
- 测试脚本可以获取数据，但适配器无法获取

### 影响
- 所有批量数据获取功能不可用
- 用户无法获取多股票数据
- 数据服务API部分功能失效

---

## 根本原因

### 代码位置
**文件**: `backend/data/adapters/xtquant_dual_instance_adapter.py`

**错误行号**: 842, 918

### 错误代码

```python
# ❌ 错误：使用数字
dividend_type_map = {"none": 0, "front": 1, "back": 2}
dividend_type = dividend_type_map.get(adjust_type, 1)  # 返回数字
```

### 问题分析

**XtQuant API要求**:
- `dividend_type` 参数**必须是字符串**
- 值为: `'none'`, `'front'`, `'back'`

**错误后果**:
- 传入数字 `0`, `1`, `2` 会导致API调用失败
- 错误信息: "function not realize" 或参数类型错误

### 为什么单个获取正常？

```python
# ✅ 单个获取 (654行) - 正确
dividend_type_map = {"none": 'none', "front": 'front', "back": 'back'}
dividend_type = dividend_type_map.get(adjust_type, 'front')
```

单个获取使用了字符串，所以正常工作。

---

## 修复方案

### 修复1: 行842

```python
# ❌ 修改前
dividend_type_map = {"none": 0, "front": 1, "back": 2}
dividend_type = dividend_type_map.get(adjust_type, 1)  # 默认前复权

# ✅ 修改后
dividend_type_map = {"none": 'none', "front": 'front', "back": 'back'}
dividend_type = dividend_type_map.get(adjust_type, 'front')  # 默认前复权
```

### 修复2: 行918

```python
# ❌ 修改前
dividend_type_map = {"none": 0, "front": 1, "back": 2}
dividend_type = dividend_type_map.get(adjust_type, 1)

# ✅ 修改后
dividend_type_map = {"none": 'none', "front": 'front', "back": 'back'}
dividend_type = dividend_type_map.get(adjust_type, 'front')
```

---

## 修复验证

### 测试计划
1. ✅ 代码已修复
2. ⏳ 运行批量获取测试
3. ⏳ 验证多股票数据获取
4. ⏳ 确认所有复权类型正常

### 预期结果
- 批量获取可以正常工作
- 支持所有复权类型（不复权、前复权、后复权）
- 性能与单个获取相当

---

## 经验教训

### 1. 参数类型的重要性
**一个参数类型错误（数字 vs 字符串）导致整个功能不可用**

### 2. 代码一致性的重要性
- 单个获取使用了字符串 ✅
- 批量获取使用了数字 ❌
- **不一致导致了问题**

### 3. 测试覆盖的重要性
- 单个测试通过 ✅
- 批量测试未覆盖 ❌
- **缺少集成测试**

### 4. 官方文档的重要性
- 官方文档明确说明参数类型
- 未仔细阅读导致错误

---

## 预防措施

### 1. 代码规范
```python
# ✅ 推荐：使用常量
class DividendType:
    NONE = 'none'
    FRONT = 'front'
    BACK = 'back'

# 使用
dividend_type = DividendType.FRONT
```

### 2. 类型检查
```python
# 添加类型验证
if not isinstance(dividend_type, str):
    raise TypeError(f"dividend_type must be string, got {type(dividend_type)}")
```

### 3. 单元测试
```python
def test_dividend_type_types():
    """确保所有复权类型使用字符串"""
    adapter = XtQuantDualInstanceAdapter()

    # 测试所有类型
    for adj_type in ['none', 'front', 'back']:
        result = await adapter.get_kline_batch(
            symbols=['600519.SH'],
            period='1d',
            count=10,
            adjust_type=adj_type
        )
        assert '600519.SH' in result
```

### 4. 集成测试
```python
def test_batch_get_kline():
    """测试批量获取功能"""
    adapter = XtQuantDualInstanceAdapter()

    # 批量获取
    symbols = ['600519.SH', '000001.SZ', '600000.SH']
    result = await adapter.get_kline_batch(symbols, period='1d', count=10)

    # 验证
    assert len(result) == len(symbols)
    for symbol in symbols:
        assert symbol in result
        assert len(result[symbol]) > 0
```

---

## 相关文档

- [06-测试结果对比报告.md](06-测试结果对比报告.md)
- [01-参数实测报告.md](01-参数实测报告.md)
- [XtQuant官方文档](http://dict.thinktrader.net/nativeApi/start_now.html)

---

## 下一步行动

- [ ] 运行完整测试套件验证修复
- [ ] 更新API文档
- [ ] 添加单元测试和集成测试
- [ ] 代码Review确认无类似问题

---

**修复完成时间**: 2026-02-05
**修复状态**: ✅ 待验证
