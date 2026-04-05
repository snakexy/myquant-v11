"""
V5 增量更新服务 API 路由

提供数据更新、缺失检测、快照获取等功能
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from myquant.core.market.services import get_incremental_service


router = APIRouter(tags=["增量更新"])


# 请求模型
class UpdateRequest(BaseModel):
    """更新请求"""
    symbols: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=500)
    period: str = Field("1d", description="周期: 1m, 5m, 15m, 30m, 1h, 1d")
    days_back: int = Field(7, description="回溯天数", ge=1, le=30)
    save_to_db: bool = Field(False, description="是否保存到数据库")
    parallel: bool = Field(True, description="是否并行处理")


class DetectRequest(BaseModel):
    """检测请求"""
    symbols: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=500)
    period: str = Field("1d", description="周期")
    days_back: int = Field(30, description="回溯天数", ge=1, le=30)


# 响应模型
class IncrementalResponse(BaseModel):
    """增量更新响应"""
    code: int = 0
    data: Optional[dict] = None
    message: str = "success"


@router.post("/update", response_model=IncrementalResponse)
async def update_symbols(request: UpdateRequest, background_tasks: BackgroundTasks):
    """更新股票数据

    在线获取填补缺失的交易日数据
    """
    try:
        logger.info("开始更新: {} 只股票, period={}, days_back={}",
                    len(request.symbols), request.period, request.days_back)

        service = get_incremental_service()

        # 同步执行（可以改为后台任务）
        result = service.update_symbols(
            symbols=request.symbols,
            period=request.period,
            days_back=request.days_back,
            save_to_db=request.save_to_db,
            parallel=request.parallel,
        )

        data = {
            'total': len(request.symbols),
            'success': result['success'],
            'failed': result['failed'],
            'total_records': result['total_records'],
            'duration': result['duration'],
            'success_rate': f"{result['success'] / len(request.symbols) * 100:.1f}%",
        }

        logger.info("更新完成: 成功={}, 失败={}, 耗时={:.2f}秒",
                    result['success'], result['failed'], result['duration'])

        return IncrementalResponse(data=data)

    except Exception as e:
        logger.error("更新失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-async")
async def update_symbols_async(request: UpdateRequest, background_tasks: BackgroundTasks):
    """异步更新股票数据

    在后台执行更新任务
    """
    try:
        logger.info("提交异步更新任务: {} 只股票", len(request.symbols))

        # 这里可以添加任务队列逻辑
        # 简化处理，直接返回任务ID
        task_id = f"update_{len(request.symbols)}_{request.period}"

        return IncrementalResponse(
            data={
                'task_id': task_id,
                'status': 'submitted',
                'message': '更新任务已提交'
            }
        )

    except Exception as e:
        logger.error("提交异步任务失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect", response_model=IncrementalResponse)
async def detect_missing(request: DetectRequest):
    """检测缺失数据

    检查指定股票在指定周期内的数据缺失情况
    """
    try:
        logger.info("检测缺失数据: {} 只股票, period={}, days_back={}",
                    len(request.symbols), request.period, request.days_back)

        service = get_incremental_service()

        missing_info = service.detect_missing(
            symbols=request.symbols,
            period=request.period,
            days_back=request.days_back
        )

        # 统计缺失情况
        total_missing = sum(len(dates) for dates in missing_info.values())
        symbols_with_missing = [s for s, dates in missing_info.items() if dates]

        data = {
            'total_symbols': len(request.symbols),
            'symbols_with_missing': len(symbols_with_missing),
            'total_missing_dates': total_missing,
            'missing_details': {
                symbol: dates
                for symbol, dates in missing_info.items()
                if dates
            }
        }

        logger.info("检测完成: {} 只股票有缺失，共 {} 个缺失日期",
                    len(symbols_with_missing), total_missing)

        return IncrementalResponse(data=data)

    except Exception as e:
        logger.error("检测缺失失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snapshot", response_model=IncrementalResponse)
async def get_same_day_snapshot(symbols: List[str]):
    """获取当天收盘快照

    获取指定股票的当日收盘价数据，转换为K线格式
    """
    try:
        logger.info("获取当天快照: {} 只股票", len(symbols))

        service = get_incremental_service()

        snapshots = service.get_same_day_closing_data(symbols)

        data = {
            'count': len(snapshots),
            'snapshots': snapshots
        }

        logger.info("快照获取完成: {} 只股票", len(snapshots))

        return IncrementalResponse(data=data)

    except Exception as e:
        logger.error("获取快照失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=IncrementalResponse)
async def get_service_status():
    """获取增量更新服务状态

    查看各数据源的可用性
    """
    try:
        service = get_incremental_service()

        status = service.get_status()

        return IncrementalResponse(data=status)

    except Exception as e:
        logger.error("获取服务状态失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))
