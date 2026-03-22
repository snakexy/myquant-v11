# RL策略优化模块 - API设计

> **阶段**: Research阶段
> **状态**: ✅ 核心功能实现完成
> **最后更新**: 2026-02-11

---

## 🎯 模块定位

基于QLib Reinforcement Learning框架的RL策略优化服务。

**核心功能**:
- RL策略训练（DQN/PPO/A2C）
- 策略超参数优化
- 模型管理和查询
- 训练历史管理

**应用场景**:
1. **Order Execution（订单执行优化）**: 单资产/多资产订单执行优化
2. **Portfolio Construction（投资组合构建）**: 资产配置优化

---

## 📡 API端点列表

### 1. 训练RL策略
`POST /api/v1/research/rl/train`

训练DQN/PPO/A2C策略。

**请求**:
```json
{
  "algorithm": "PPO",           // DQN, PPO, A2C
  "scenario": "order_execution", // order_execution, portfolio_construction
  "max_episodes": 1000,
  "max_steps_per_episode": 100,
  "hidden_size": 128,
  "num_layers": 2,
  "learning_rate": 0.0003,
  "state_dim": 10,
  "action_dim": 3,
  "gamma": 0.99,
  "buffer_size": 10000,
  "batch_size": 64,
  "clip_param": 0.2,            // PPO特定参数
  "entropy_coef": 0.01,         // PPO特定参数
  "epsilon_start": 1.0,         // DQN特定参数
  "epsilon_end": 0.01,          // DQN特定参数
  "env_data": null              // 可选：环境数据
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "training_id": "ppo_order_execution_xxx",
    "algorithm": "PPO",
    "scenario": "order_execution",
    "total_episodes": 1000,
    "final_reward": 0.85,
    "average_reward": 0.72,
    "best_reward": 0.91,
    "rewards_summary": {
      "min": 0.45,
      "max": 0.91,
      "mean": 0.72,
      "std": 0.12
    },
    "training_history": [...],
    "created_at": "2026-02-11T10:30:00",
    "training_duration": 123.45,
    "status": "completed",
    "model_saved": true
  },
  "timestamp": "2026-02-11T10:32:00"
}
```

---

### 2. 优化策略超参数
`POST /api/v1/research/rl/optimize`

使用网格搜索优化策略超参数。

**请求**:
```json
{
  "algorithm": "PPO",
  "scenario": "order_execution",
  "param_grid": {
    "learning_rate": [0.001, 0.0003, 0.0001],
    "hidden_size": [64, 128, 256],
    "gamma": [0.95, 0.99, 0.995]
  },
  "n_trials": 10
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "optimization_id": "opt_ppo_xxx",
    "algorithm": "PPO",
    "scenario": "order_execution",
    "best_params": {
      "learning_rate": 0.0003,
      "hidden_size": 128,
      "gamma": 0.99
    },
    "best_metrics": {
      "best_reward": 0.91,
      "n_trials": 10
    },
    "all_trials": [
      {
        "trial_id": "opt_ppo_xxx_trial_0",
        "params": {...},
        "score": 0.85,
        "final_reward": 0.83,
        "average_reward": 0.76
      },
      ...
    ],
    "created_at": "2026-02-11T10:00:00",
    "trial_count": 10
  },
  "timestamp": "2026-02-11T10:05:00"
}
```

---

### 3. 列出所有模型
`GET /api/v1/research/rl/models?limit=20`

列出所有训练好的模型。

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 5,
    "models": [
      {
        "training_id": "ppo_order_execution_xxx",
        "algorithm": "PPO",
        "scenario": "order_execution",
        "best_reward": 0.91,
        "created_at": "2026-02-11T10:30:00",
        "model_path": "backend/data/rl_strategy/models/ppo_order_execution_xxx.pkl"
      },
      ...
    ]
  },
  "timestamp": "2026-02-11T11:00:00"
}
```

---

### 4. 获取模型详情
`GET /api/v1/research/rl/models/{training_id}`

获取指定模型的详细信息。

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "training_id": "ppo_order_execution_xxx",
    "algorithm": "PPO",
    "scenario": "order_execution",
    "config": {
      "algorithm": "PPO",
      "scenario": "order_execution",
      "max_episodes": 1000,
      ...
    },
    "total_episodes": 1000,
    "final_reward": 0.85,
    "average_reward": 0.72,
    "best_reward": 0.91,
    "rewards_summary": {...},
    "training_history": [...],
    "created_at": "2026-02-11T10:30:00",
    "training_duration": 123.45,
    "status": "completed",
    "model_saved": true
  },
  "timestamp": "2026-02-11T11:00:00"
}
```

**错误响应** (404):
```json
{
  "code": 404,
  "message": "模型不存在: xxx",
  "timestamp": "2026-02-11T11:00:00"
}
```

---

### 5. 保存模型
`POST /api/v1/research/rl/models/{training_id}/save?model_path=xxx`

保存训练好的模型到文件。

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "training_id": "ppo_order_execution_xxx",
    "saved": true
  },
  "timestamp": "2026-02-11T11:00:00"
}
```

---

### 6. 获取训练历史
`GET /api/v1/research/rl/history?algorithm=PPO&scenario=order_execution&limit=20`

获取训练历史记录。

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "history": [
      {
        "training_id": "ppo_order_execution_xxx",
        "algorithm": "PPO",
        "scenario": "order_execution",
        "total_episodes": 1000,
        "final_reward": 0.85,
        ...
      },
      ...
    ]
  },
  "timestamp": "2026-02-11T11:00:00"
}
```

---

### 7. 获取统计信息
`GET /api/v1/research/rl/statistics`

获取RL策略优化统计信息。

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_trainings": 15,
    "total_models": 15,
    "by_algorithm": {
      "PPO": 8,
      "DQN": 5,
      "A2C": 2
    },
    "by_scenario": {
      "order_execution": 10,
      "portfolio_construction": 5
    },
    "dependencies": {
      "tianshou": true,
      "torch": true,
      "numpy": true
    }
  },
  "timestamp": "2026-02-11T11:00:00"
}
```

---

### 8. 健康检查
`GET /api/v1/research/rl/health`

检查服务状态。

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "service": "RL策略优化模块",
    "status": "healthy",
    "dependencies": {
      "tianshou": true,
      "torch": true,
      "numpy": true
    }
  },
  "timestamp": "2026-02-11T11:00:00"
}
```

---

## 🔄 交互流程

### 训练流程

```
客户端 → POST /api/v1/research/rl/train
       ↓
   API路由层 (rl_router.py)
       ↓
   Service层 (rl_strategy_service.py)
       ↓
   RL训练 (DQN/PPO/A2C)
       ↓
   保存结果 (.pkl)
       ↓
   返回训练结果
```

### 优化流程

```
客户端 → POST /api/v1/research/rl/optimize
       ↓
   API路由层 (rl_router.py)
       ↓
   Service层 (rl_strategy_service.py)
       ↓
   多次训练 (n_trials)
       ↓
   选择最佳参数
       ↓
   保存优化结果 (.pkl)
       ↓
   返回优化结果
```

---

## 📝 数据模型

### 请求模型

```python
class RLTrainingRequest(BaseModel):
    algorithm: str = "PPO"          # DQN, PPO, A2C
    scenario: str = "order_execution"
    max_episodes: int = 1000
    max_steps_per_episode: int = 100
    hidden_size: int = 128
    num_layers: int = 2
    learning_rate: float = 3e-4
    state_dim: int = 10
    action_dim: int = 3
    gamma: float = 0.99
    buffer_size: int = 10000
    batch_size: int = 64
    clip_param: float = 0.2         # PPO
    entropy_coef: float = 0.01      # PPO
    epsilon_start: float = 1.0      # DQN
    epsilon_end: float = 0.01       # DQN
    env_data: Optional[Dict[str, Any]] = None

class RLOptimizationRequest(BaseModel):
    algorithm: str
    scenario: str = "order_execution"
    param_grid: Dict[str, List[Any]]
    n_trials: int = 10
```

### 响应模型

```python
class RLTrainingResult(BaseModel):
    training_id: str
    algorithm: str
    scenario: str
    config: Dict[str, Any]
    total_episodes: int
    total_rewards: List[float]
    final_reward: float
    average_reward: float
    best_reward: float
    rewards_summary: Dict[str, float]
    training_history: List[Dict[str, Any]]
    created_at: str
    training_duration: Optional[float]
    status: str
    model_saved: bool

class RLOptimizationResult(BaseModel):
    optimization_id: str
    algorithm: str
    scenario: str
    best_params: Dict[str, Any]
    best_metrics: Dict[str, float]
    all_trials: List[Dict[str, Any]]
    created_at: str
    trial_count: int
```

---

## 🔐 安全机制

### 认证方式
- 使用FastAPI内置认证机制
- 支持API Token认证

### 权限控制
- 所有端点需要认证
- 管理员端点需要特殊权限

---

## 📊 统一响应格式

所有API端点使用统一的响应格式：

```json
{
  "code": 200,           // HTTP状态码
  "message": "success",  // 响应消息
  "data": {...},         // 响应数据
  "timestamp": "..."     // 时间戳
}
```

**错误响应**:
```json
{
  "code": 500,
  "message": "训练失败: ...",
  "timestamp": "..."
}
```

---

## 🚀 使用示例

### 示例1: 训练PPO策略

```bash
curl -X POST "http://localhost:8000/api/v1/research/rl/train" \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "PPO",
    "scenario": "order_execution",
    "max_episodes": 1000,
    "hidden_size": 128,
    "learning_rate": 0.0003
  }'
```

### 示例2: 优化超参数

```bash
curl -X POST "http://localhost:8000/api/v1/research/rl/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "PPO",
    "scenario": "order_execution",
    "param_grid": {
      "learning_rate": [0.001, 0.0003, 0.0001],
      "hidden_size": [64, 128, 256]
    },
    "n_trials": 10
  }'
```

### 示例3: 获取模型列表

```bash
curl -X GET "http://localhost:8000/api/v1/research/rl/models?limit=10"
```

### 示例4: 获取模型详情

```bash
curl -X GET "http://localhost:8000/api/v1/research/rl/models/ppo_order_execution_xxx"
```

---

## 📚 相关文档

- [概述](./概述.md)
- [数据模型](./数据模型.md)
- [前端组件](./前端组件.md)
- [实施记录](./实施记录.md)

---

**创建时间**: 2026-02-11
**最后更新**: 2026-02-11
**状态**: ✅ 核心功能实现完成
**优先级**: P2
