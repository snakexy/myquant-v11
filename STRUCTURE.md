# MyQuant v11 完整目录结构

```
MyQuant_v11/
│
├── backend/                          ← 后端代码
│   └── src/myquant/
│       │
│       ├── api/                      ← API 网关层
│       │   ├── __init__.py
│       │   ├── domain/               ← 业务领域 API
│       │   │   ├── __init__.py
│       │   │   ├── research.py       ← 研究 API
│       │   │   ├── backtest.py       ← 回测 API
│       │   │   ├── validation.py     ← 验证 API
│       │   │   └── production.py     ← 生产 API
│       │   │
│       │   └── dataget/              ← 数据获取 API（行情/监控/增量/转换）
│       │       ├── __init__.py
│       │       ├── quotes.py         ← 行情 K线/快照
│       │       ├── market.py         ← 市场数据
│       │       ├── monitoring.py     ← 实时监控
│       │       ├── incremental.py    ← 增量更新
│       │       └── conversion.py     ← 数据转换
│       ├── core/                     ← 核心业务层
│       │   ├── __init__.py
│       │   ├── market/               ← 行情核心
│       │   │   ├── __init__.py
│       │   │   ├── adapters/         ← 数据源适配器
│       │   │   │   ├── __init__.py
│       │   │   │   ├── base.py
│       │   │   │   ├── pytdx_adapter.py
│       │   │   │   ├── xtquant_adapter.py
│       │   │   │   ├── tdxquant_adapter.py
│       │   │   │   ├── localdb_adapter.py
│       │   │   │   └── tdxlocal_adapter.py
│       │   │   │
│       │   │   ├── services/         ← 场景服务
│       │   │   │   ├── kline/
│       │   │   │   ├── monitoring/
│       │   │   │   ├── incremental/
│       │   │   │   ├── conversion/
│       │   │   │   └── realtime_market/
│       │   │   │
│       │   │   ├── models/           ← 数据模型
│       │   │   ├── routing/          ← 路由逻辑
│       │   │   └── utils/            ← 工具函数
│       │   │
│       │   ├── research/             ← 研究核心
│       │   ├── backtest/             ← 回测核心
│       │   └── production/           ← 生产核心
│       │
│       ├── infrastructure/           ← 基础设施层
│       │   ├── persistence/          ← 数据库访问层
│       │   │   ├── models/           ← SQLAlchemy 表结构定义
│       │   │   ├── repositories/     ← 数据操作方法
│       │   │   └── connection.py     ← 数据库连接管理
│       │   ├── qlib/                 ← Qlib 引擎
│       │   ├── messaging/            ← 消息队列
│       │   └── external/             ← 第三方 SDK
│       │
│       ├── interfaces/               ← 接口适配层
│       │   └── websocket/            ← WebSocket 服务
│       │
│       ├── config/                   ← 配置管理
│       │   ├── __init__.py
│       │   ├── settings.py           ← 核心配置
│       │   └── ports.py              ← 端口配置
│       │
│       └── main.py                   ← FastAPI 入口
│
├── frontend/                         ← 前端代码
│   └── src/
│       ├── api/                      ← API 调用
│       ├── components/               ← 组件
│       ├── views/                    ← 页面
│       ├── stores/                   ← 状态管理
│       ├── utils/                    ← 工具函数
│       └── main.ts                   ← 入口
│
├── data/                             ← 数据文件 (程序代码外)
│   ├── cache/                        ← 运行时缓存
│   ├── db/                           ← SQLite 数据库
│   ├── qlib/                         ← Qlib 数据
│   ├── tdx/                          ← 通达信数据
│   └── logs/                         ← 日志文件
│
├── docs/                             ← 文档
│   ├── 数据源能力研究/
│   ├── 项目设计/
│   └── 开发指南/
│
├── tests/                            ← 测试
│   ├── unit/
│   └── integration/
│
├── scripts/                          ← 运维脚本
├── .claude/skills/                   ← AI 开发规范
│   ├── architecture.md
│   ├── backend.md
│   └── project-context.md
│
├── README.md                         ← 项目说明
└── STRUCTURE.md                      ← 本文件
```

## 目录职责说明

### backend/src/myquant/

| 目录 | 职责 | 禁止 |
|------|------|------|
| `api/` | 路由定义、参数校验、序列化 | 禁止直接调用 infrastructure |
| `core/` | 业务逻辑、领域模型 | 禁止直接操作数据库/文件 |
| `infrastructure/` | 数据库、缓存、第三方SDK | 禁止包含业务逻辑 |
| `interfaces/` | WebSocket、CLI 等接口适配 | 禁止包含业务逻辑 |
| `config/` | 配置管理 | 禁止硬编码配置 |

### data/

| 目录 | 用途 | 说明 |
|------|------|------|
| `cache/` | 运行时缓存 | 可随时删除 |
| `db/` | SQLite 数据库 | 持久化存储 |
| `qlib/` | Qlib 数据目录 | 二进制格式 |
| `tdx/` | 通达信数据 | 本地 .day 文件 |
| `logs/` | 日志文件 | 按日期轮转 |

### 代码 vs 数据分离原则

```
# 代码（在 backend/src/ 下，随版本控制）
backend/src/myquant/infrastructure/persistence/  ← 怎么读写数据库
├── models/user.py                                 用户表结构定义
├── repositories/user_repository.py                查询/保存用户的方法
└── connection.py                                  数据库连接池

# 数据（在 data/ 下，不进入 git，运行时生成）
data/                                              ← 实际存数据的地方
├── db/myquant.db                                  SQLite 数据库文件
├── cache/xxx.tmp                                  运行时缓存
└── logs/2024-03-22.log                            日志文件
```

**关键区别：**
- `persistence/` 是**代码**，告诉程序怎么访问数据库
- `data/db/` 是**文件**，实际存放数据内容
- 删除 `data/` 只丢数据，删除 `persistence/` 程序无法运行

## 分层调用规则

```
api/ → core/ → infrastructure/
            ↘ interfaces/
```

- **同层之间**可以调用
- **禁止跨层**调用（如 api 直接调 infrastructure）
- **禁止反向**调用（如 infrastructure 调 core）

## 文件命名规范

- **适配器**: `{source}_adapter.py` (如 `pytdx_adapter.py`, `xtquant_adapter.py`)
- **服务**: `{scene}_service.py` (如 `seamless_service.py`, `realtime_service.py`)
- **路由**: `{name}.py` (如 `quotes.py`, `market.py`)
- **模型**: `{entity}.py` (如 `kline.py`)
