"""
MyQuant v11 - FastAPI 入口

启动命令:
    uvicorn backend.src.myquant.main:app --reload --port 8000
"""

# HotDB 预热功能已集成

import sys
from pathlib import Path

# 确保 src 目录在 Python 路径中（修复 uvicorn.exe 启动时的路径问题）
_current_file = Path(__file__).resolve()
src_dir = _current_file.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
    print(f"[DEBUG] Added to sys.path: {src_dir}")

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
from myquant.api.hotdb import router as hotdb_router
from myquant.api.dataget import hotdata_router
from myquant.api.dataget import watchlist_router
from myquant.api.dataget import unified_router
from myquant.api.dataget import system_router
from myquant.api.dataget.kline_ws import router as ws_kline_router
from myquant.api.dataget.batch_update_ws import router as ws_batch_update_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("MyQuant v11 starting...")
    # 调试：检查适配器注册
    from myquant.core.market.adapters import AdapterFactory
    print(f"已注册适配器: {AdapterFactory.list_adapters()}")
    from myquant.core.market.adapters import get_adapter
    hotdb = get_adapter('hotdb')
    print(f"HotDB 适配器: {hotdb}")
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
app.include_router(hotdb_router,       prefix="/api/hotdb",      tags=["HotDB管理"])
app.include_router(hotdata_router,     prefix="/api/v5/hotdata", tags=["热数据库"])
app.include_router(watchlist_router,   prefix="/api/v5/watchlist", tags=["自选股管理"])
app.include_router(system_router,      prefix="/api/v5/system",   tags=["系统监控"])
# 前端兼容路由别名
app.include_router(quotes_router,      prefix="/api/v5",          tags=["行情(v5别名)"])
app.include_router(market_router,      prefix="/api/v1/quotes",   tags=["市场(v1别名)"])
app.include_router(unified_router,     prefix="/api/v1",          tags=["统一数据"])

# WebSocket 路由
app.include_router(ws_kline_router, prefix="/ws")
app.include_router(ws_batch_update_router, prefix="/ws")


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


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("MyQuant 后端服务启动中...")

    # 启动自动检查调度器
    try:
        from myquant.core.market.services.auto_check_scheduler import get_auto_check_scheduler
        scheduler = get_auto_check_scheduler()
        scheduler.start()
        logger.info("[Startup] 自动检查调度器已启动")
    except Exception as e:
        logger.warning(f"[Startup] 启动调度器失败: {e}")

    # 启动后自动检查今天的数据状态（后台运行）
    try:
        from myquant.core.market.services.hotdb_service import get_hotdb_service
        from myquant.api.dataget.watchlist import load_watchlist_data

        hotdb_service = get_hotdb_service()
        watchlist = load_watchlist_data()

        all_symbols = []
        for group in watchlist.get('groups', []):
            for stock in group.get('stocks', []):
                all_symbols.append(stock['symbol'])

        # 异步执行检查，不阻塞启动
        import threading
        check_thread = threading.Thread(
            target=hotdb_service.auto_check_and_fill_today,
            args=(all_symbols,),
            daemon=True
        )
        check_thread.start()
        logger.info("[Startup] 已触发自动数据检查（后台运行）")

    except Exception as e:
        logger.warning(f"[Startup] 自动数据检查触发失败: {e}")

    logger.info("MyQuant 后端服务启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("MyQuant 后端服务关闭中...")

    # 停止调度器
    try:
        from myquant.core.market.services.auto_check_scheduler import get_auto_check_scheduler
        scheduler = get_auto_check_scheduler()
        scheduler.stop()
        logger.info("[Shutdown] 自动检查调度器已停止")
    except Exception:
        pass

    logger.info("MyQuant 后端服务已关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
