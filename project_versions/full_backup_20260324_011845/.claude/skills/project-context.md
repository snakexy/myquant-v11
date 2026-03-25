# MyQuant v11 项目上下文
> 每次新对话开始必读，保持最新状态

## 当前状态（2026-03-23）
- **后端**: ✅ 运行中 http://localhost:8000
- **前端**: ✅ 已迁移到 v11，运行在 http://localhost:5174
- **数据源**: ✅ pytdx2 联网行情已通，K线/快照/市场状态均正常

## 项目结构
→ 详见 `E:/MyQuant_v11/STRUCTURE.md`（代码放哪里、各层职责、命名规范）

**v11 特殊说明（STRUCTURE.md 未覆盖的）：**
- `backend/.venv/` — Python 3.11.8 虚拟环境（勿提交）
- `backend/external/pytdx2/` — pytdx2 本地包（非 pip 安装）
- `frontend/` — 完整前端工程（已从 v10 迁移，有 package.json + node_modules）

## 启动命令
```bash
# 后端（必须在 backend 目录）
cd E:/MyQuant_v11/backend
E:/MyQuant_v11/.venv/Scripts/uvicorn.exe myquant.main:app --reload --port 8000

# 前端（已迁移到 v11）
cd E:/MyQuant_v11/frontend
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

## 已解决的关键问题
→ 详见 `.claude/skills/` 下的 skill 文件，遇到相关问题直接查阅：
- `pytdx2-api-differences` — get_security_bars 参数、返回 None
- `uvicorn-windows-reload` — 热重载不可靠，需手动重启
- `fastapi-frontend-alias-routes` — 前后端路径不匹配
- `windows-pip-encoding` — requirements.txt GBK 报错
- `_normalize_quote_dict` 需在 pytdx_adapter.py 手动实现

### 2026-03-23 修复内容
- **format_converter.py**: XtQuant datetime +8h 还原 CST 日期（修复日线日期偏移一天）
- **seamless_service.py**: keep='last' 优先在线数据；非交易时间不触发 TdxQuant 查询
- **pytdx_adapter.py + pytdx_pool_adapter.py**: 分钟线 vol÷100 股→手；intraday bar high/low 异常值截断（1%阈值）
- **intraday_service.py**: 非交易时间直接用 pytdx 避免 TdxQuant 初始化报错
- **RealtimeQuotes.vue**: 日线去重；成交量颜色修复；timeFormatter 日线只显日期
- **quotes.ts**: _base 修复双重 /api/ 前缀
- **market.py**: 新增 GET /snapshot/{symbol} 和 GET /snapshot/ 端点

**2026-03-23 前端修复（RealtimeQuotes.vue）**：
- K线图贴底：从chart-area计算高度，排除toolbar，移除空volumeContainer
- 十字光标OHLCV legend：悬浮在图表左上角，成交量从volumeSeries读取
- 价格颜色修复：pre_close字段名不一致导致change计算错误，直接用后端change字段
- 左侧列表：迷你折线图(5分钟线)、所有股票价格正确更新
- 状态栏：沪深指数(上证/深证/创业板)，市场代码后缀判断修复上证指数
- 垂直拖动：autoScale:false + 临时开启autoScale自适应初始价格范围
- App.vue：height:100%+overflow:hidden修复height链
- quotes.ts：修复双重/api/前缀

## 前端导航栏说明
- **公共导航栏**: `E:/MyQuant_v10.0.0/frontend/src/components/GlobalNavBar.vue`
- 已应用到: RealtimeQuotes、Monitoring、RiskControlView、MLModelManagement、ResearchDetailViewSplit、StrategyManagement、WorkflowManager
- 工作流子页面（研究/验证/实盘）**不需要**公共导航栏
- 导航菜单: 实时行情→工作流→监控→风险管理→策略→ML模型

## 数据源架构（V5，详细文档见 docs/项目设计/数据架构V5/）
| 数据源 | 最擅长 | 可用时间 | 当前状态 |
|--------|--------|----------|---------|
| **TdxQuant** | L1快照(0.60ms) + 板块(6.99ms, 586板块) | 仅交易时间 | ✅ 可用（需通达信终端运行） |
| **XtQuant** | 当天分钟线(13ms首次/4ms后续) + 后台下载完整历史 | 交易+盘后 | ✅ 可用（pip install xtquant） |
| **PyTdx2** | 24/7在线多周期K线(13ms) **连接池版(M+H+P)** | 24/7 | ✅ 可用（默认连接池版） |
| **QLib** | 历史K线本地库(7-10ms) | 24/7 | ❓ 未验证 |

**关键限制**：
- TdxQuant：仅交易时间可用（需通达信终端运行），不支持盘后的当天分钟线历史
- XtQuant：依赖 QMT 运行，周末/节假日如 QMT 服务器连接正常仍可用；首次调用约600ms（下载），后续约4-5ms
- PyTdx2：24/7 在线，不支持订阅推送

**2026-03-22 测试结论**：
1. PyTdx2 分钟线性能优异（13ms），可作为默认在线数据源
2. XtQuant 实现三层加载策略（本地→在线→后台下载），适合需要完整历史的场景
3. TdxQuant 单例重复初始化问题已修复（AdapterFactory 缓存实例）

## Git 状态
- v11 已初始化 git，在 `E:/MyQuant_v11`
- v10 有 git，分支 `feature/research-detail-refactor-v2`（不管它）
- .gitignore 已排除: `.venv/`, `__pycache__/`, `version_manager/`, `data/`
