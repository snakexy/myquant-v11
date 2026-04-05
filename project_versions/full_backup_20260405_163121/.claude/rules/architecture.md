# MyQuant V5 架构约束（不可违反）

## 分层架构铁律

### ✅ 允许的调用链
```
前端 → /api/* → Service层 → Adapter层 → 数据源
```

### ❌ 禁止的跳层调用
```python
# ❌ 错误：API层直接调用Adapter
from myquant.core.market.adapters import get_adapter
def get_kline_api():
    adapter = get_adapter('hotdb')  # 违规！

# ✅ 正确：API层调用Service层
from myquant.core.market.services import get_kline_service
def get_kline_api():
    service = get_kline_service()  # 正确
    return service.get_historical_kline(...)
```

### ❌ 禁止的跨层依赖
```python
# ❌ Service层直接import Adapter（错误）
from myquant.core.market.adapters.hotdb_adapter import V5HotDBAdapter

# ✅ Service层通过工厂获取Adapter（正确）
from myquant.core.market.adapters import get_adapter
hotdb = get_adapter('hotdb')
```

## 数据流规范

### 前端数据流
```
RealtimeQuotes.vue
    → useKlineData.ts（Composable统一入口）
    → /api/v5/kline/realtime/{symbol}（HTTP）
    → /ws/kline/{symbol}（WebSocket，只推1分钟线）
```

**禁止**：
- ❌ 组件直接调用 `fetchKline()`
- ❌ 组件自己管理 WebSocket 连接

### 后端数据流
```
API路由层（api/dataget/）
    → SeamlessKlineService.get_kline()
    → KlineService.get_historical_kline()
    → HotDBAdapter/LocalDBAdapter/在线Adapter
```

**禁止**：
- ❌ HotDBService 直接调用 `pytdx/xtquant` 在线源
- ❌ API层包含业务逻辑（只能调用Service层）

## HotDB 智能补全规范

### ✅ 正确的补全流程
```python
# HotDBService检测到缺口
if gap_detected:
    # 调用 KlineService 获取在线数据
    online_data = self._kline_service._fetch_from_online(...)
    # 保存到 HotDB
    self._hotdb_adapter.save_kline(online_data)
```

### ❌ 禁止的直接调用
```python
# ❌ HotDBService 直接调用在线源（违规）
from myquant.core.market.adapters import get_adapter
pytdx = get_adapter('pytdx')
pytdx.get_kline(...)  # 架构违规！
```

## 文件修改范围约束

### 单次任务限制
- 最多修改 **1 个功能**
- 最多修改 **3 个文件**
- 超过必须拆分任务

### 禁止的"顺手改"
- ❌ 任务是改 A 文件，顺手改 B、C 文件
- ❌ 修bug时顺便"优化"周围代码
- ❌ 加功能时顺便重构组件结构

## 验证方法

每次改文件后，自动运行：
```bash
# 检查架构违规
grep -r "from.*adapter import" backend/src/myquant/core/market/services/
# 如果有输出 → Service层直接import Adapter → 违规

# 检查文件修改数量
git diff --stat | wc -l
# 如果 > 3 → 可能违反"单次只改1个功能"
```
