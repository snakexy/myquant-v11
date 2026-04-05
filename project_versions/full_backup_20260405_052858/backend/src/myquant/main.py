"""
MyQuant v11 - FastAPI 入口

启动命令:
    uvicorn backend.src.myquant.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from myquant.api.dataget import (
    quotes_router,
    monitoring_router,
    incremental_router,
    conversion_router,
    market_router,
)
from myquant.api.dataget.kline_ws import router as ws_kline_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("MyQuant v11 starting...")
    yield
    # 关闭时
    print("MyQuant v11 stopped")


app = FastAPI(
    title="MyQuant v11 API",
    description="量化投研平台 - 场景化服务 API",
    version="11.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载数据服务路由（原 V5）
app.include_router(quotes_router,      prefix="/api/quotes",      tags=["行情"])
app.include_router(market_router,      prefix="/api/market",      tags=["市场"])
app.include_router(monitoring_router,  prefix="/api/monitoring",  tags=["监控"])
app.include_router(incremental_router, prefix="/api/incremental", tags=["增量更新"])
app.include_router(conversion_router,  prefix="/api/conversion",  tags=["数据转换"])

# 前端兼容路由别名
app.include_router(quotes_router,      prefix="/api/v5",          tags=["行情(v5别名)"])
app.include_router(market_router,      prefix="/api/v1/quotes",   tags=["市场(v1别名)"])

# WebSocket 路由
app.include_router(ws_kline_router, prefix="/ws")


@app.get("/", tags=["根"])
async def root():
    """API 根路径"""
    return {
        "name": "MyQuant v11 API",
        "version": "11.0.0",
        "docs": "/docs",
        "endpoints": {
            "quotes": "/api/quotes",
            "market": "/api/market",
            "monitoring": "/api/monitoring",
            "incremental": "/api/incremental",
            "conversion": "/api/conversion",
        }
    }


@app.get("/health", tags=["健康"])
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "11.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
