# MyQuant v11 项目上下文
> 每次新对话开始必读，保持最新状态

## 当前状态（2026-03-22）
- **后端**: ✅ 运行中 http://localhost:8000
- **前端**: ✅ 运行中 http://localhost:5174（v10 frontend 代理到 v11 backend）
- **数据源**: ✅ pytdx2 联网行情已通，K线/快照/市场状态均正常

## 项目结构
```
E:/MyQuant_v11/          ← 主项目根目录（有git）
├── backend/             ← Python FastAPI 后端
│   ├── .venv/           ← Python 3.11.8 虚拟环境（勿提交）
│   ├── src/myquant/     ← 主包
│   │   ├── main.py      ← FastAPI 入口
│   │   ├── api/data/    ← 路由层
│   │   └── core/market/ ← 业务逻辑层
│   ├── external/pytdx2/ ← pytdx2 本地包（非pip安装）
│   └── pyproject.toml   ← 包配置（where=["src","external"]）
├── frontend/src/        ← 前端源码（无构建配置，用v10跑）
└── version_manager/     ← 本地备份工具（已在.gitignore）

E:/MyQuant_v10.0.0/frontend/  ← 当前运行的前端（vite dev server）
├── vite.config.ts       ← 代理 /api → localhost:8000
└── src/
    ├── components/GlobalNavBar.vue  ← 公共导航栏（今天新建）
    ├── views/market/RealtimeQuotes.vue ← 实时行情主页
    └── router/index.ts  ← /RealtimeQuotes 路由已配置
```

## 启动命令
```bash
# 后端（必须在 backend 目录）
cd E:/MyQuant_v11/backend
E:/MyQuant_v11/.venv/Scripts/uvicorn.exe myquant.main:app --reload --port 8000

# 前端
cd E:/MyQuant_v10.0.0/frontend
npm run dev   # 运行在 localhost:5174
```

## API 路由（已验证可用）
| 路径 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /api/market/status` | 市场状态 |
| `POST /api/market/quotes` | 实时行情（body: ["000001","600000"]） |
| `GET /api/quotes/kline/realtime/{symbol}` | K线数据 |
| `GET /api/v5/kline/realtime/{symbol}` | 同上（前端别名） |
| `GET /api/v1/quotes/status` | 市场状态（前端别名） |
| `GET /docs` | Swagger UI |

## 已解决的关键问题（避免重复踩坑）
1. **pytdx2 参数错误**: `get_security_bars` 只有5个参数，不能传 `fq_type`
2. **缺少方法**: `_normalize_quote_dict` 需在 `pytdx_adapter.py` 手动实现
3. **路由重复前缀**: router 自带 prefix，main.py 挂载时不要重复加
4. **requirements.txt 编码**: 原文件含中文注释导致 GBK 报错，已清理为纯 ASCII
5. **pytz 未安装**: quotes.py 用到 pytz，需单独 pip install
6. **uvicorn reload 不可靠**: 改代码后建议手动重启，不要依赖热重载
7. **API 返回元组**: `get_realtime_quotes` 返回 `(dict, source)` 元组，API层需解包

## 前端导航栏说明
- **公共导航栏**: `E:/MyQuant_v10.0.0/frontend/src/components/GlobalNavBar.vue`
- 已应用到: RealtimeQuotes、Monitoring、RiskControlView、MLModelManagement、ResearchDetailViewSplit、StrategyManagement、WorkflowManager
- 工作流子页面（研究/验证/实盘）**不需要**公共导航栏
- 导航菜单: 实时行情→工作流→监控→风险管理→策略→ML模型

## 数据源架构（V5，详细文档见 docs/项目设计/数据架构V5/）
| 数据源 | 最擅长 | 可用时间 | 当前状态 |
|--------|--------|----------|---------|
| **TdxQuant** | L1快照(0.60ms) + 板块(6.99ms, 586板块) | 仅交易时间 | ✅ 可用（需通达信终端运行） |
| **XtQuant** | 当天分钟线(0.90ms) + 订阅(300股) | 交易+盘后 | ❌ 未安装（需要QMT） |
| **PyTdx2** | 24/7兜底 | 24/7 | ✅ 可用（本地包 external/pytdx2） |
| **QLib** | 历史K线本地库(7-10ms) | 24/7 | ❓ 未验证 |

**关键限制**：TdxQuant 不支持当天分钟线；XtQuant 不支持板块数据

## Git 状态
- v11 已初始化 git，在 `E:/MyQuant_v11`
- v10 有 git，分支 `feature/research-detail-refactor-v2`（不管它）
- .gitignore 已排除: `.venv/`, `__pycache__/`, `version_manager/`, `data/`
