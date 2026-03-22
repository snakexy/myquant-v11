# MyQuant v11 项目上下文

## 版本
- **Version**: 11.0.0
- **架构**: V5 场景化服务
- **Python**: 3.11+

## 核心依赖
- FastAPI - Web框架
- Pandas - 数据处理
- Loguru - 日志
- PyTdx2 - 通达信数据
- XtQuant - QMT接口

## 前端对应
- **RealtimeQuotes.vue** → `/api/v5/kline/realtime/{symbol}`
- **ResearchMain.vue** → `/api/v1/research/*`
- **BacktestView.vue** → `/api/v1/backtest/*`
- **ProductionMain.vue** → `/api/v1/production/*`

## 数据源配置
- PyTdx: `E:/new_tdx64`
- XtQuant: `127.0.0.1:58610`
- TdxQuant: `E:/new_tdx64/PYPlugins`

## 启动命令
```bash
cd E:/MyQuant_v11
uvicorn src.myquant.main:app --reload --port 8000
```
