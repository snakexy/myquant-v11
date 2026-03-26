"""
MyQuant v11 - FastAPI 入口

启动命令:
    uvicorn backend.src.myquant.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from loguru import logger

from myquant.api.dataget import (
    quotes_router,
    monitoring_router,
    incremental_router,
    conversion_router,
    market_router,
    hotdata_router,
)
from myquant.api.dataget.kline_ws import router as ws_kline_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("MyQuant v11 starting...")

    # 启动后预热 HotDB
    asyncio.create_task(preheat_hotdb())

    yield

    # 关闭时
    print("MyQuant v11 stopped")


async def preheat_hotdb():
    """预热 HotDB（后台任务）"""
    await asyncio.sleep(1)  # 等待服务完全启动

    try:
        from myquant.core.market.services.hotdb_service import get_hotdb_service

        hotdb_service = get_hotdb_service()

        # 默认预热股票列表
        default_symbols = [
            '600000.SH', '000001.SZ', '601628.SH',  # 主要指数股
            '510300.SH', '159919.SZ',  # ETF
        ]

        # 预热周期
        periods = ['1d', '5m', '15m']

        logger.info(f"[预热] 开始预热 HotDB: {len(default_symbols)} 只股票 x {len(periods)} 周期")

        result = hotdb_service.preheat(
            symbols=default_symbols,
            periods=periods
        )

        if result.get('success'):
            logger.info(
                f"[预热] 完成: 成功 {result['saved_count']}, "
                f"跳过 {result['skipped_count']}, "
                f"失败 {result['failed_count']}"
            )
        else:
            logger.warning(f"[预热] 失败: {result.get('error')}")

    except Exception as e:
        logger.warning(f"[预热] 预热任务失败: {e}")


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
app.include_router(hotdata_router,     prefix="/api/hotdb",       tags=["热数据库"])

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
            "hotdb": "/api/hotdb",
        }
    }


@app.get("/health", tags=["健康"])
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "11.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
