# 数据管理模块 - API设计

> **阶段**: Research阶段
> **模块**: 数据管理
> **状态**: ✅ 已实现
> **版本**: v3.0 (实际实现版本)
> **最后更新**: 2026-02-11

> **说明**: 本文档反映实际代码实现，与实施记录.md同步

---

## 🎯 模块定位

数据管理模块是Research阶段的基础设施，负责：
- 数据库统计信息查询
- 分类统计查询
- 数据导出（CSV/Excel/Parquet/JSON）
- 数据预处理（缺失值填充、异常值处理）
- 数据质量检查
- 股票列表和详情查询
- 服务状态监控

---

## 📡 API端点列表

### 1. 数据库统计信息

**端点**: `GET /api/v1/research/data/database/stats`

**描述**: 获取数据库统计信息，包括股票数量、记录数、数据大小等

**请求参数**: 无

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_stocks": 5234,
    "daily_records": 12567890,
    "minute_records": 45234567,
    "data_size_mb": 856.5,
    "last_update": "2026-02-11 15:30:00",
    "data_sources": {
      "redis": {"status": "connected", "records": 1523},
      "qlib": {"status": "connected", "records": 12456},
      "tdx": {"status": "connected", "records": 5234}
    }
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 2. 分类统计信息

**端点**: `GET /api/v1/research/data/category/stats`

**描述**: 获取分类统计信息（行业、板块、市场等）

**请求参数**:
- `category` (query, optional): 分类类型 (industry/sector/market)

---

### 3. 数据导出

**端点**: `POST /api/v1/research/data/export`

**描述**: 导出数据到文件（CSV/Excel/Parquet/JSON）

**请求参数**:
```json
{
  "data": [...],
  "export_type": "csv",
  "filename": "stocks"
}
```

---

### 4. 数据预处理

**端点**: `POST /api/v1/research/data/preprocess`

**描述**: 数据预处理（缺失值填充、异常值处理）

---

### 5. 数据质量检查

**端点**: `POST /api/v1/research/data/quality/check`

**描述**: 检查数据质量（缺失值、异常值、重复值）

---

### 6. 股票列表查询

**端点**: `GET /api/v1/research/data/stocks/list`

**描述**: 查询股票列表（支持筛选、搜索、分页）

**请求参数**:
- `category` (query): 分类筛选
- `market` (query): 市场筛选 (SZ/SH)
- `search` (query): 搜索关键词
- `page` (query): 页码
- `page_size` (query): 每页数量

---

### 7. 股票详情查询

**端点**: `GET /api/v1/research/data/stocks/{symbol}`

**描述**: 查询单个股票详细信息

---

### 8. 服务状态统计

**端点**: `GET /api/v1/research/data/service/stats`

**描述**: 获取服务运行状态和性能统计

---

### 9. 健康检查

**端点**: `GET /api/v1/research/data/health`

**描述**: 服务健康检查

---

## 🔄 前后端交互流程

### 系统架构图

```
┌─────────────────────────────────────────────────┐
│                  前端层 (Vue 3)                 │
│  DataManagementView.vue                        │
│  ├─ 数据源状态卡片                              │
│  ├─ 缓存统计面板                                │
│  └─ 数据导出组件                                │
└───────────────┬─────────────────────────────────┘
                │ HTTP/REST API
                ↓
┌─────────────────────────────────────────────────┐
│              API层 (FastAPI)                    │
│  /api/v1/research/data/router.py                 │
│  ├─ GET  /database/stats                        │
│  ├─ GET  /category/stats                        │
│  ├─ POST /export                                 │
│  ├─ POST /preprocess                             │
│  └─ POST /quality/check                          │
└───────────────┬─────────────────────────────────┘
                │ 调用
                ↓
┌─────────────────────────────────────────────────┐
│           Service层 (Python)                     │
│  DataManagementService                           │
│  ├─ get_database_stats()                        │
│  ├─ get_category_stats()                        │
│  ├─ export_data()                               │
│  ├─ preprocess_data()                            │
│  └─ check_data_quality()                         │
└───────────────┬─────────────────────────────────┘
                │ 访问
                ↓
┌─────────────────────────────────────────────────┐
│              数据层                              │
│  ┌─────────┬─────────┬─────────┐                │
│  │  Redis  │  QLib   │   TDX   │                │
│  └─────────┴─────────┴─────────┘                │
└─────────────────────────────────────────────────┘
```

### 数据库统计查询时序图

```
前端          API            Service          数据源
 │             │                │                 │
 │ GET /database/stats              │                 │
 │────────────>│                 │                 │
 │             │                 │                 │
 │             │ 调用get_database_stats()  │                 │
 │             │────────────────>│                 │
 │             │                 │ 扫描数据目录      │
 │             │                 │────────────────>│
 │             │                 │                 │
 │             │                 │ Redis/QLib/TDX   │
 │             │                 │<────────────────│
 │             │                 │                 │
 │             │ 返回统计信息    │                 │
 │             │<────────────────│                 │
 │             │                 │                 │
 │ 响应JSON      │                 │                 │
 │<────────────│                 │                 │
 │             │                 │                 │
```

### 数据导出流程图

```
┌──────────┐
│ 前端     │
└─────┬────┘
     │
     │ 1. 用户选择导出格式和数据
     │
     ↓
┌──────────────────┐
│  POST /export     │
│  {                │
│    data: [...],   │
│    export_type:   │
│    "csv"          │
│  }                │
└─────┬────────────┘
     │
     │ 2. API接收请求
     │
     ↓
┌──────────────────────┐
│ Service.export_data() │
│                      │
│ ┌──────────────────┐ │
│ │ 根据export_type   │ │
│ │ 选择导出器         │ │
│ └──────────────────┘ │
│                      │
│ CSV/Excel/Parquet/    │
└─────┬────────────────┘
     │
     │ 3. 生成文件
     │
     ↓
┌──────────────┐
│  文件系统     │
│  /exports/   │
└─────┬────────┘
     │
     │ 4. 返回下载链接
     │
     ↓
┌──────────────────┐
│ 前端下载文件      │
└──────────────────┘
```

### 数据预处理流程图

```
输入数据
   │
   ├─> 缺失值检测 ──> ────────────┐
   │                          │
   ├─> 异常值检测 ──> ────────────┤
   │                          │
   └─> 类型转换 ──> ──────────────┤
                              │
                              ▼
                    ┌─────────────────┐
                    │   预处理操作     │
                    │                  │
                    ├─ forward填充     │
                    ├─ backward填充     │
                    ├─ mean填充        │
                    ├─ IQR异常值处理   │
                    └─ Z-score异常值处理│
                    └─────────────────┘
                              │
                              ▼
                        输出：清洗后的数据
```

### 前端数据请求流程

```
Vue组件
   │
   ├─> Pinia Store (状态管理)
   │   │
   │   ├─> API客户端封装
   │   │   │
   │   │   └─> axios发送HTTP请求
   │   │       │
   │   │       ├─> GET /api/v1/research/data/xxx
   │   │       │
   │   │       └─> 等待响应
   │   │           │
   │   │           ├─> 200 OK: 返回数据
   │   │           │      └─> 更新Store状态
   │   │           │
   │   │           └─> 4xx/5xx: 错误处理
   │   │                   └─> 显示错误信息
   │   │
   │   └─> Vue响应式更新UI
   │
   └─> 用户看到最新数据
```

---

## 🔐 安全机制

---

## 📝 数据模型

### ExportRequest
```python
class ExportRequest(BaseModel):
    data: Any
    export_type: str = "csv"
    filename: Optional[str] = None
```

### PreprocessRequest
```python
class PreprocessRequest(BaseModel):
    data: Any
    operations: Optional[List[str]] = None
```

### QualityCheckRequest
```python
class QualityCheckRequest(BaseModel):
    data: Any
    data_type: str = "kline"
```

---

## 🔐 安全机制

- Pydantic模型验证
- 防止SQL注入
- 限制导出数据大小

---

## 📊 性能优化

- 统计信息缓存（5分钟 TTL）
- 分页支持（默认50条/页）
- 批量操作支持

---

## 📚 相关文档

- [概述](./概述.md)
- [前端组件](./前端组件.md)
- [数据模型](./数据模型.md)
- [实施记录](./实施记录.md)

---

**代码位置**: `backend/api/v1/research/data_router.py`
**状态**: ✅ 已实现（9个端点）
