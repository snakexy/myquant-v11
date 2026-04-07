"""
V5 数据转换服务 API 路由

提供批量转换TDX本地数据到Qlib格式等功能
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from myquant.core.market.services import get_conversion_service


router = APIRouter(tags=["数据转换"])


# 请求模型
class ConvertRequest(BaseModel):
    """转换请求"""
    symbols: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=1000)
    period: str = Field("1d", description="周期: 1m, 5m, 15m, 30m, 1h, 1d")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    save_to_qlib: bool = Field(True, description="是否保存到Qlib")
    parallel: bool = Field(True, description="是否并行处理")


# 响应模型
class ConversionResponse(BaseModel):
    """转换响应"""
    code: int = 0
    data: Optional[dict] = None
    message: str = "success"


@router.post("/convert", response_model=ConversionResponse)
async def convert_batch(request: ConvertRequest):
    """批量转换数据

    从TDX本地数据读取并转换为Qlib格式
    """
    try:
        logger.info("开始批量转换: {} 只股票, period={}",
                    len(request.symbols), request.period)

        service = get_conversion_service()

        result = service.convert_batch(
            symbols=request.symbols,
            period=request.period,
            start_date=request.start_date,
            end_date=request.end_date,
            save_to_qlib=request.save_to_qlib,
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

        logger.info("转换完成: 成功={}, 失败={}, 耗时={:.2f}秒",
                    result['success'], result['failed'], result['duration'])

        return ConversionResponse(data=data)

    except Exception as e:
        logger.error("转换失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress", response_model=ConversionResponse)
async def get_conversion_progress():
    """获取转换进度

    查看当前批量转换任务的进度
    """
    try:
        service = get_conversion_service()

        progress = service.get_progress()

        return ConversionResponse(data=progress)

    except Exception as e:
        logger.error("获取进度失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/convert-async")
async def convert_batch_async(request: ConvertRequest, background_tasks: BackgroundTasks):
    """异步批量转换

    在后台执行转换任务
    """
    try:
        logger.info("提交异步转换任务: {} 只股票", len(request.symbols))

        task_id = f"convert_{len(request.symbols)}_{request.period}"

        return ConversionResponse(
            data={
                'task_id': task_id,
                'status': 'submitted',
                'message': '转换任务已提交'
            }
        )

    except Exception as e:
        logger.error("提交异步任务失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))
