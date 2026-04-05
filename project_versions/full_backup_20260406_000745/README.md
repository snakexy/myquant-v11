# MyQuant v11 - 量化投研平台

## 项目结构

```
MyQuant_v11/
├── backend/src/myquant/              ← 后端核心代码
│   ├── api/                  ← API 网关层
│   │   ├── domain/           ← 业务领域 API
│   │   │   ├── research.py   ← 研究
│   │   │   ├── backtest.py   ← 回测
│   │   │   ├── validation.py ← 验证
│   │   │   └── production.py ← 生产交易
│   │   └── data/             ← 数据服务 API
│   │       ├── quotes.py     ← 行情（K线/快照）
│   │       ├── monitoring.py ← 实时监控
│   │       ├── incremental.py← 增量更新
│   │       └── conversion.py ← 数据转换
│   │
│   ├── core/                 ← 核心业务层
│   │   ├── market/           ← 行情核心
│   │   │   ├── adapters/     ← 数据源适配器
│   │   │   └── services/     ← 场景服务
│   │   ├── research/         ← 研究核心
│   │   ├── backtest/         ← 回测核心
│   │   └── production/       ← 生产核心
│   │
│   ├── infrastructure/       ← 基础设施层
│   │   ├── persistence/      ← 数据库访问层 (SQLAlchemy/ORM)
│   │   ├── qlib/             ← Qlib 引擎
│   │   ├── messaging/        ← 消息队列 (预留)
│   │   └── external/         ← 第三方SDK封装
│   │
│   └── config/               ← 配置管理
│
├── data/                       ← 数据文件 (程序代码外)
│   ├── cache/                  ← 运行时缓存
│   ├── db/                     ← SQLite数据库文件
│   ├── qlib/                   ← Qlib数据目录
│   ├── tdx/                    ← 通达信数据文件
│   └── logs/                   ← 日志文件
│   │
│   ├── interfaces/           ← 接口适配层
│   │   └── websocket/        ← WebSocket服务
│   │
│   └── config/               ← 配置管理
│
├── frontend/                 ← 前端代码
│   └── src/
│       ├── api/              ← API调用
│       ├── components/       ← 组件
│       ├── views/            ← 页面
│       ├── stores/           ← 状态管理
│       └── utils/            ← 工具函数
│
├── docs/                     ← 文档
│   ├── 数据源能力研究/
│   ├── 项目设计/数据架构V5/
│   └── 开发指南/
│
└── .claude/skills/           ← AI开发规范
    ├── architecture.md
    ├── backend.md
    └── project-context.md
```

## 前端模块对应

| 前端模块 | 后端对应 | 状态 |
|---------|---------|------|
| RealtimeQuotes (行情) | `api/data/quotes.py` | ✅ 已迁移 |
| ResearchMain (研究) | `api/domain/research.py` | ✅ 已迁移 |
| BacktestView (回测) | `api/domain/backtest.py` | ✅ 已迁移 |
| ValidationMain (验证) | `api/domain/validation.py` | ✅ 已迁移 |
| ProductionMain (生产) | `api/domain/production.py` | ✅ 已迁移 |
| DataManagement (数据) | `api/data/incremental.py` | ✅ 已迁移 |

## API 路由

```
/api/quotes/{symbol}        ← 行情K线
/api/monitoring/hot-sectors ← 热点板块
/api/incremental/update     ← 增量更新
/api/conversion/convert     ← 数据转换
```

## 启动命令

**后端：**
```bash
cd E:/MyQuant_v11
pip install -r requirements.txt
uvicorn backend.src.myquant.main:app --reload --port 8000
```

**前端：**
```bash
cd E:/MyQuant_v11/frontend
npm install
npm run dev
```

## 与原项目关系

- **E:/MyQuant_v10.0.0v2/** - 原项目，保留作为参考
- **E:/MyQuant_v11/** - 新版本，干净架构，从此处继续开发

## 详细结构

完整目录结构说明见 [STRUCTURE.md](./STRUCTURE.md)

## 开发规范

详见 `.claude/skills/` 目录下技能文件。
