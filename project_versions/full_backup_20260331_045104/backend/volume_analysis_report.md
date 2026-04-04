# 成交量单位问题分析报告

## 问题描述
用户报告：5分钟线成交量从47万变成了2.3万（约÷20）。

## 发现的问题

### 1. 单位转换不一致

**TdxQuant 适配器** (`tdxquant_adapter.py` 第580-581行):
- TdxQuant 返回的 volume 是 **股(shares)**
- 适配器会 **÷100** 转换为 **手(lots)**
```python
if 'volume' in df.columns:
    df['volume'] = df['volume'] / 100  # 股→手
```

**PyTdx 适配器** (`pytdx_pool_adapter.py` 第378-379行):
- PyTdx 返回的分钟线 vol 是 **股(shares)**
- 适配器会 **÷100** 转换为 **手(lots)**
```python
if not is_daily and 'vol' in df.columns:
    df['vol'] = df['vol'] / 100  # 股→手
```

**LocalDB 适配器**:
- 读取数据时 **不做任何单位转换**
- 数据以原始格式（股）存储和返回

**HotDB 适配器**:
- 读取数据时 **不做任何单位转换**
- 直接返回存储的原始值

### 2. 数据流分析

**预热流程** (`hotdb_service.py` 第97-107行):
1. 从 LocalDB 读取数据（原始股，未转换）
2. 直接保存到 HotDB（仍然是股）
3. 通过 HotDB 适配器读取时，不做转换

**在线获取流程** (通过 TdxQuant/PyTdx):
1. 从 TdxQuant/PyTdx 获取数据（股）
2. 通过适配器标准化时 **÷100**（转为手）
3. 保存到 HotDB（手）
4. 从 HotDB 读取（手）

## 根本原因

**数据来源不一致导致的单位混乱：**

- **预热数据**（LocalDB → HotDB）：单位是 **股**
- **在线数据**（TdxQuant → HotDB）：单位是 **手**

当用户查看数据时，如果数据来自预热（LocalDB），显示的是股；如果来自在线获取（TdxQuant），显示的是手。

这解释了为什么用户看到 470k → 23k：
- 470,000 股 = 4,700 手（接近用户说的 23k 的 1/5）
- 但如果数据被二次处理（比如从股→手→股→手），可能会出现任意数值

## 验证数据

运行检查脚本显示：

```
TdxQuant原始数据: Volume = 1,275,200 (股)
TdxQuant标准化后: volume = 12,752 (手，已÷100)
HotDB存储的数据: volume = 1,275,200 (股，未转换！)
```

**确认：HotDB中存储的是原始股数据，没有经过单位转换。**

## 解决方案

需要在数据写入 HotDB 时统一单位。有两个选择：

### 方案1：HotDB 统一存储为股（推荐）
- 修改 TdxQuant/PyTdx 适配器：读取时不转换（保持股）
- 或者：在保存到 HotDB 前，将手转回股（×100）
- 优点：保持原始数据精度，后续处理灵活
- 缺点：需要修改多个适配器

### 方案2：HotDB 统一存储为手
- 修改 LocalDB 适配器：读取时转换为手（÷100）
- 修改 HotDB 写入逻辑：保存前转换单位
- 优点：存储空间小，符合交易习惯
- 缺点：丢失精度（1手=100股）

### 方案3：在 Service 层统一转换
- 在 `hotdb_service.py` 的预热逻辑中，添加单位转换
- 确保 LocalDB → HotDB 时，分钟线 volume ÷100
- 优点：改动范围小，集中处理
- 缺点：需要在服务层维护单位转换逻辑

## 建议

采用 **方案3（Service层统一转换）**，因为：
1. 改动范围最小，风险可控
2. 只在预热流程中添加转换逻辑
3. 不影响其他使用 LocalDB 的代码
4. 可以精确控制哪些周期需要转换（分钟线÷100，日线保持）

## 修复代码位置

文件：`backend/src/myquant/core/market/services/hotdb_service.py`
行数：第103-107行（预热保存逻辑）

需要在保存到 HotDB 之前，检查数据单位并转换：
```python
# 从 LocalDB 读取的数据是股，需要转换为手（÷100）
if period in ['1m', '5m', '15m', '30m', '1h'] and 'volume' in df.columns:
    df['volume'] = df['volume'] / 100
```
