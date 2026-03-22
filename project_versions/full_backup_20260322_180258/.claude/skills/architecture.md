# MyQuant v11 架构规范

## 目录结构

```
src/myquant/
├── api/                    ← API 网关层
│   ├── domain/             ← 业务领域 API
│   │   ├── research.py     ← 研究
│   │   ├── backtest.py     ← 回测
│   │   ├── validation.py   ← 验证
│   │   └── production.py   ← 生产交易
│   └── data/               ← 数据服务 API
│       ├── quotes.py       ← 行情（K线/快照）
│       ├── monitoring.py   ← 实时监控
│       ├── incremental.py  ← 增量更新
│       └── conversion.py   ← 数据转换
│
├── core/                   ← 核心业务层
│   ├── market/             ← 行情核心
│   │   ├── adapters/       ← 数据源适配器
│   │   └── services/       ← 场景服务
│   ├── research/           ← 研究核心
│   ├── backtest/           ← 回测核心
│   └── production/         ← 生产核心
│
├── infrastructure/         ← 基础设施层
│   ├── persistence/        ← 数据库
│   ├── qlib/               ← Qlib 引擎
│   ├── messaging/          ← 消息队列
│   └── external/           ← 第三方SDK
│
├── interfaces/             ← 接口适配层
│   └── websocket/          ← WebSocket服务
│
└── config/                 ← 配置管理
    ├── app_config.py
    └── ports.py
```

## 路由挂载

```python
from myquant.api import (
    quotes_router,
    monitoring_router,
    incremental_router,
    conversion_router,
)

app.include_router(quotes_router,       prefix="/api/quotes")
app.include_router(monitoring_router,   prefix="/api/monitoring")
app.include_router(incremental_router,  prefix="/api/incremental")
app.include_router(conversion_router,   prefix="/api/conversion")
```

## 分层原则

**禁止跨层调用：**
- api/ 只能调用 core/
- core/ 只能调用 infrastructure/
- 各层内部通过 __init__.py 暴露接口

## 数据层级 (L0-L5)

| 层级 | 延迟 | 数据源 | 用途 |
|------|------|--------|------|
| L0 | <1ms | XtQuant订阅 | 实时推送 |
| L1 | 1-17ms | TdxQuant/XtQuant | 实时快照 |
| L2 | 7-17ms | LocalDB/XtQuant | 历史摘要 |
| L3 | 5-18ms | PyTdx/XtQuant | 完整K线 |
| L4 | 100-300ms | TdxQuant | 财务数据 |
| L5 | 10-500ms | TdxQuant/PyTdx | 板块数据 |

## 命名规范

- 适配器：`V5{Source}Adapter` (如 V5PyTdxAdapter)
- 服务：`{Scene}Service` (如 SeamlessKlineService)
- 路由：`{name}_router` (如 quotes_router)
