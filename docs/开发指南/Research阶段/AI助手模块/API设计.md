# AI助手模块 - API设计 v2.0

> **阶段**: Research阶段
> **版本**: v2.0
> **状态**: ⏸️ 代码已编写，待测试验证
> **最后更新**: 2026-02-11

---

## 📡 API端点列表

### 路由前缀
`/api/v1/research/ai`

### 10个RESTful端点

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/sessions/create` | POST | 创建对话会话 | ⏸️ 待测试 |
| `/sessions/{id}/messages` | POST | 添加消息 | ⏸️ 待测试 |
| `/sessions/{id}/history` | GET | 获取历史 | ⏸️ 待测试 |
| `/sessions` | GET | 会话列表 | ⏸️ 待测试 |
| `/factor/generate` | POST | AI生成因子 | ⏸️ 待测试 |
| `/factor/save` | POST | 保存因子 | ⏸️ 待测试 |
| `/config/save` | POST | 保存配置 | ⏸️ 待测试 |
| `/config/{key}` | GET | 获取配置 | ⏸️ 待测试 |
| `/health` | GET | 健康检查 | ⏸️ 待测试 |

---

## 🔧 详细端点规范

### 1. 创建对话会话

**端点**: `POST /sessions/create`

**功能**: 创建新的AI对话会话

**请求体**:
```json
{
  "title": "AI助手对话",
  "user_goal": "生成动量因子"
}
```

**响应**:
```json
{
  "success": true,
  "session_id": "uuid-string",
  "title": "AI助手对话",
  "user_goal": "生成动量因子",
  "message": "会话创建成功"
}
```

**错误响应**:
```json
{
  "detail": "创建会话失败: <错误信息>"
}
```

---

### 2. 添加消息

**端点**: `POST /sessions/{session_id}/messages`

**功能**: 向会话添加消息

**路径参数**:
- `session_id`: 会话ID

**请求体**:
```json
{
  "message": "帮我生成一个动量因子",
  "role": "user",
  "tokens": null
}
```

**响应**:
```json
{
  "success": true,
  "message": "消息已添加"
}
```

**角色类型**:
- `user`: 用户消息
- `assistant`: AI回复
- `system`: 系统消息

---

### 3. 获取会话历史

**端点**: `GET /sessions/{session_id}/history`

**功能**: 获取会话历史消息

**路径参数**:
- `session_id`: 会话ID

**查询参数**:
- `limit`: 返回条数（默认50）

**响应**:
```json
{
  "success": true,
  "session_id": "uuid-string",
  "messages": [
    {
      "role": "user",
      "content": "帮我生成一个动量因子",
      "tokens": 15
    },
    {
      "role": "assistant",
      "content": "好的，我来帮你生成...",
      "tokens": 120
    }
  ]
}
```

---

### 4. 获取会话列表

**端点**: `GET /sessions`

**功能**: 获取所有会话列表

**响应**:
```json
{
  "sessions": [
    {
      "session_id": "uuid-string",
      "title": "AI助手对话",
      "user_goal": "生成动量因子",
      "status": "active",
      "message_count": 5,
      "created_at": "2026-02-11T10:00:00",
      "last_activity": "2026-02-11T10:30:00"
    }
  ],
  "active_session": "uuid-string",
  "total_sessions": 1
}
```

---

### 5. AI生成因子

**端点**: `POST /factor/generate`

**功能**: 使用AI生成因子

**请求体**:
```json
{
  "prompt": "生成一个基于成交量的动量因子",
  "factor_type": "momentum",
  "stock_pool": ["000001.SZ", "000002.SZ"],
  "time_range": "2024-01-01 to 2024-12-31",
  "session_id": "uuid-string"
}
```

**响应**:
```json
{
  "success": true,
  "factor_code": "volume_momentum_5d",
  "expression": "$volume / Ref($volume, 5) - 1",
  "description": "基于5日成交量的动量因子，当值为正表示成交量增加，负值表示减少",
  "model": "deepseek-chat",
  "tokens_used": 350,
  "message": "因子生成成功"
}
```

**因子类型**:
- `momentum`: 动量因子
- `reversal`: 反转因子
- `volatility`: 波动率因子
- `volume`: 成交量因子
- `custom`: 自定义因子

**错误响应**:
```json
{
  "success": false,
  "error": "DeepSeek API调用失败: <错误信息>"
}
```

---

### 6. 保存AI生成因子

**端点**: `POST /factor/save`

**功能**: 保存AI生成的因子到数据库

**请求体**:
```json
{
  "factor_code": "volume_momentum_5d",
  "expression": "$volume / Ref($volume, 5) - 1",
  "description": "基于5日成交量的动量因子",
  "generation_method": "ai",
  "source_conversation_id": 123,
  "is_saved": true,
  "category": "momentum",
  "tags": ["volume", "momentum", "5d"]
}
```

**响应**:
```json
{
  "success": true,
  "factor_id": "ai_factor_001",
  "message": "因子保存成功"
}
```

---

### 7. 保存配置

**端点**: `POST /config/save`

**功能**: 保存AI配置到数据库

**请求体**:
```json
{
  "config_key": "deepseek_api_key",
  "config_value": "sk-xxxxxxxxxxxxxxxxxxxx",
  "config_type": "api_key"
}
```

**配置类型**:
- `api_key`: API密钥
- `model`: 模型名称
- `temperature`: 温度参数
- `max_tokens`: 最大Token数
- `system`: 系统配置

**响应**:
```json
{
  "success": true,
  "message": "配置保存成功",
  "data": {
    "config_key": "deepseek_api_key",
    "config_value": "sk-xxxxxxxxxxxxxxxxxxxx",
    "config_type": "api_key",
    "is_encrypted": true
  }
}
```

---

### 8. 获取配置

**端点**: `GET /config/{config_key}`

**功能**: 获取配置值

**路径参数**:
- `config_key`: 配置键

**响应**:
```json
{
  "success": true,
  "message": "配置获取成功",
  "data": {
    "config_key": "deepseek_api_key",
    "config_value": "sk-xxxxxxxxxxxxxxxxxxxx",
    "config_type": "api_key",
    "is_encrypted": true,
    "updated_at": "2026-02-11T10:00:00"
  }
}
```

---

### 9. 健康检查

**端点**: `GET /health`

**功能**: 检查服务健康状态

**响应**:
```json
{
  "status": "healthy",
  "service": "ai_assistant_v2",
  "version": "2.0",
  "timestamp": "2026-02-11T10:00:00.000000",
  "dependencies": {
    "deepseek_api": "available",
    "database": "connected",
    "context_manager": "available"
  }
}
```

---

## 🔐 认证与授权

### 认证方式
当前版本暂未实现认证，所有端点公开访问。

### 计划中的认证
- JWT Token认证
- API密钥认证
- 用户会话管理

---

## 📊 数据格式

### 统一响应格式

**成功响应**:
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误描述",
  "detail": "详细错误信息"
}
```

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 🧪 测试示例

### 使用curl测试

```bash
# 1. 健康检查
curl http://localhost:8000/api/v1/research/ai/health

# 2. 创建会话
curl -X POST http://localhost:8000/api/v1/research/ai/sessions/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试会话",
    "user_goal": "生成动量因子"
  }'

# 3. 生成因子
curl -X POST http://localhost:8000/api/v1/research/ai/factor/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "生成一个动量因子",
    "factor_type": "momentum"
  }'

# 4. 获取会话历史
curl http://localhost:8000/api/v1/research/ai/sessions/{session_id}/history?limit=10
```

### 使用Python测试

```python
import httpx

base_url = "http://localhost:8000/api/v1/research/ai"

# 1. 健康检查
response = httpx.get(f"{base_url}/health")
print(response.json())

# 2. 创建会话
response = httpx.post(f"{base_url}/sessions/create", json={
    "title": "测试会话",
    "user_goal": "生成动量因子"
})
session_id = response.json()["session_id"]

# 3. 添加消息
response = httpx.post(f"{base_url}/sessions/{session_id}/messages", json={
    "message": "帮我生成一个动量因子",
    "role": "user"
})

# 4. 生成因子
response = httpx.post(f"{base_url}/factor/generate", json={
    "prompt": "生成一个动量因子",
    "factor_type": "momentum",
    "session_id": session_id
})
print(response.json())
```

---

## 📝 实现文件

**后端路由**: [backend/api/routers/domain_ai_assistant_v2.py](../../../../../backend/api/routers/domain_ai_assistant_v2.py) (560行)

**后端服务**: [backend/services/research/ai_assistant_service_v2.py](../../../../../backend/services/research/ai_assistant_service_v2.py) (680行)

**Pydantic模型**: 在domain_ai_assistant_v2.py中定义

---

## 🔗 相关文档

- [概述](./概述.md) - 模块概述
- [数据模型](./数据模型.md) - 数据表结构
- [前端组件](./前端组件.md) - 前端UI组件
- [实施记录](./实施记录.md) - v2.0实施记录

---

**创建时间**: 2026-02-11
**v2.0更新**: 2026-02-11
**状态**: ⏸️ 代码已编写，待测试验证
**维护者**: Claude (AI Assistant Service)
