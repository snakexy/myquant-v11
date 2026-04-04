# MyQuant V5 代码风格规范

## Python 后端规范

### 缩进与格式
- 缩进：**4个空格**（不是Tab）
- 最大行宽：**120字符**
- 引号：优先单引号 `'string'`，字符串内包含引号时用双引号
- 末尾分号：**不加**

### 命名规范
```python
# ✅ 变量：snake_case
user_count = 100
kline_data = []

# ✅ 函数：snake_case，动词开头
def get_kline_data(symbol: str) -> dict:
    pass

def calculate_average(prices: list) -> float:
    pass

# ✅ 类：大驼峰
class KlineService:
    pass

class HotDBAdapter:
    pass

# ✅ 常量：全大写，下划线分隔
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# ✅ 私有方法：单下划线前缀
def _fetch_from_online(self, symbol: str):
    pass

# ❌ 禁止：匈牙利命名法
# ❌ strName, intCount, lstData
```

### 注释规范
```python
# ✅ 注释解释"为什么"，而非"做了什么"
# 原因：pytdx2 的 get_security_bars 没有 fq_type 参数
if period in ('1m', '5m', '15m', '30m', '60m'):
    df['volume'] = df['volume'] / 100

# ❌ 错误：只说"做了什么"
# 将 volume 除以 100
df['volume'] = df['volume'] / 100

# ✅ TODO 格式
# TODO [责任人]: [描述]
# TODO [Claude]: 添加缓存机制减少重复查询
```

### 类型注解（强制）
```python
# ✅ 必须添加类型注解
def get_historical_kline(
    symbol: str,
    period: str,
    count: int = 500
) -> pd.DataFrame:
    pass

# ✅ 复杂类型用 typing
from typing import Optional, Dict, List

def smart_update(
    symbol: str,
    period: str
) -> Dict[str, Any]:
    pass
```

### 错误处理
```python
# ✅ 使用 loguru 记录错误
from loguru import logger

try:
    data = adapter.get_kline(symbol)
except Exception as e:
    logger.error(f"获取K线失败: {symbol}, 错误: {e}")
    return None

# ❌ 禁止静默失败
try:
    data = adapter.get_kline(symbol)
except:
    pass  # ❌ 错误！吞掉异常
```

## Vue3 + TypeScript 前端规范

### 缩进与格式
- 缩进：**2个空格**
- 最大行宽：**100字符**
- 引号：优先单引号
- 末尾分号：**不加**

### 命名规范
```typescript
// ✅ 变量：camelCase
const klineData = ref<KlineData[]>([])
const isLoading = ref(false)

// ✅ 函数：camelCase，动词开头
const loadKlineData = async () => {}
const switchSymbol = (symbol: string) => {}

// ✅ 组件：大驼峰
RealtimeQuotes.vue
TradingViewKLine.vue

// ✅ Composable：use 前缀
useKlineData.ts
useWebSocket.ts

// ✅ 接口：I 前缀（可选）或直接名词
interface KlineData {}
interface UseKlineDataOptions {}
```

### 组合式API规范
```vue
<script setup lang="ts">
// ✅ 正确顺序
import { ref, onMounted } from 'vue'

// 1. Props
const props = defineProps<{
  symbol: string
}>()

// 2. 响应式状态
const loading = ref(false)
const data = ref<KlineData[]>([])

// 3. 计算属性
const filteredData = computed(() => data.value.filter(...))

// 4. 方法
const loadData = async () => {}

// 5. 生命周期
onMounted(() => {
  loadData()
})
</script>
```

### 禁止的写法
```vue
<!-- ❌ 禁止：直接在模板中写复杂逻辑 -->
<div v-if="data.filter(item => item.close > 100).length > 0">

<!-- ✅ 正确：使用计算属性 -->
<div v-if="hasHighPriceItems">

<script setup lang="ts">
const hasHighPriceItems = computed(() => 
  data.value.filter(item => item.close > 100).length > 0
)
</script>
```

## 通用规范

### 文件头注释
```python
# -*- coding: utf-8 -*-
"""
K线数据服务

提供历史K线和实时K线的无缝拼接
"""
```

```typescript
/**
 * useKlineData - K线数据管理 Composable
 *
 * 统一封装：HTTP 加载 + WebSocket 实时更新
 */
```

### 导入顺序
```python
# 1. 标准库
import os
import time
from datetime import datetime

# 2. 第三方库
import pandas as pd
from loguru import logger

# 3. 本地模块
from myquant.core.market.adapters import get_adapter
from myquant.config.settings import settings
```

```typescript
// 1. Vue
import { ref, onMounted } from 'vue'

// 2. 第三方库
import axios from 'axios'

// 3. 本地模块
import { fetchKline } from '@/api/modules/quotes'
```
