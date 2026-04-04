# -*- coding: utf-8 -*-
"""
自选股管理 API 路由

提供自选股分组的增删改查功能，数据持久化到 data/watchlist.json
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from loguru import logger
from pathlib import Path
import json
from datetime import datetime

router = APIRouter(tags=["自选股管理"])


# 数据文件路径：项目根目录的 data 文件夹
# watchlist.py 位置: backend/src/myquant/api/dataget/watchlist.py
# 项目根目录: 向上 6 层
DATA_FILE = Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "watchlist.json"


# ─── 请求模型 ───────────────────────────────────────────────────────────────

class CreateGroupRequest(BaseModel):
    """创建分组请求"""
    name: str = Field(..., description="分组名称", min_length=1, max_length=50)


class RenameGroupRequest(BaseModel):
    """重命名分组请求"""
    group_id: str = Field(..., description="分组ID")
    name: str = Field(..., description="新分组名称", min_length=1, max_length=50)


class AddStockRequest(BaseModel):
    """添加股票请求"""
    group_id: str = Field(..., description="分组ID")
    symbol: str = Field(..., description="股票代码（如 600519.SH）")
    name: str = Field(..., description="股票名称")


class RemoveStockRequest(BaseModel):
    """删除股票请求"""
    group_id: str = Field(..., description="分组ID")
    symbol: str = Field(..., description="股票代码")


class SetRefreshIntervalRequest(BaseModel):
    """设置刷新频率请求"""
    group_id: str = Field(..., description="分组ID")
    interval: int = Field(..., description="刷新间隔（毫秒）", ge=1000, le=60000)


class TogglePreheatRequest(BaseModel):
    """切换预热状态请求"""
    group_id: str = Field(..., description="分组ID")


class SetActiveGroupRequest(BaseModel):
    """设置激活分组请求"""
    group_id: str = Field(..., description="分组ID")


# ─── 响应模型 ───────────────────────────────────────────────────────────────

class WatchlistResponse(BaseModel):
    """自选股列表响应"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class GroupResponse(BaseModel):
    """分组操作响应"""
    success: bool
    group: Optional[dict] = None
    error: Optional[str] = None


# ─── 工具函数 ───────────────────────────────────────────────────────────────

def _load_data() -> dict:
    """加载自选股数据"""
    try:
        if not DATA_FILE.exists():
            logger.warning(f"[自选股API] 数据文件不存在，创建默认数据: {DATA_FILE}")
            default_data = {
                "version": "1.0",
                "last_updated": None,
                "groups": [
                    {
                        "id": "default",
                        "name": "默认分组",
                        "stocks": [],
                        "refreshInterval": 5000,
                        "preheat": False,
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            _save_data(default_data)
            return default_data

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"[自选股API] 加载数据成功: {len(data.get('groups', []))} 个分组")
            return data

    except json.JSONDecodeError as e:
        logger.error(f"[自选股API] JSON 解析失败: {e}")
        raise HTTPException(status_code=500, detail=f"数据文件格式错误: {e}")
    except Exception as e:
        logger.error(f"[自选股API] 加载数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"加载数据失败: {e}")


def _save_data(data: dict) -> None:
    """保存自选股数据"""
    try:
        # 确保目录存在
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        # 更新时间戳
        data["last_updated"] = datetime.now().isoformat()

        # 保存到文件
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.debug(f"[自选股API] 保存数据成功: {len(data.get('groups', []))} 个分组")

    except Exception as e:
        logger.error(f"[自选股API] 保存数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存数据失败: {e}")


# ─── API 端点 ───────────────────────────────────────────────────────────────

@router.get("/", response_model=WatchlistResponse, summary="获取自选股列表")
async def get_watchlist():
    """获取所有自选股分组数据"""
    try:
        data = _load_data()
        return WatchlistResponse(success=True, data=data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[自选股API] 获取自选股列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/groups", response_model=GroupResponse, summary="创建分组")
async def create_group(request: CreateGroupRequest):
    """创建新的自选股分组"""
    try:
        data = _load_data()

        # 生成唯一ID
        group_id = f"group_{int(datetime.now().timestamp() * 1000)}"

        # 创建新分组
        new_group = {
            "id": group_id,
            "name": request.name,
            "stocks": [],
            "refreshInterval": 5000,
            "preheat": False,
            "created_at": datetime.now().isoformat()
        }

        data["groups"].append(new_group)
        _save_data(data)

        logger.info(f"[自选股API] 创建分组成功: {group_id} - {request.name}")
        return GroupResponse(success=True, group=new_group)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[自选股API] 创建分组失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/groups/{group_id}", response_model=GroupResponse, summary="删除分组")
async def delete_group(group_id: str):
    """删除指定的自选股分组"""
    try:
        data = _load_data()

        if len(data["groups"]) <= 1:
            raise HTTPException(status_code=400, detail="至少保留一个分组")

        groups = data["groups"]
        group_index = next((i for i, g in enumerate(groups) if g["id"] == group_id), None)

        if group_index is None:
            raise HTTPException(status_code=404, detail=f"分组不存在: {group_id}")

        deleted_group = groups.pop(group_index)
        _save_data(data)

        logger.info(f"[自选股API] 删除分组成功: {group_id} - {deleted_group['name']}")
        return GroupResponse(success=True, group=deleted_group)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[自选股API] 删除分组失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/groups/rename", response_model=GroupResponse, summary="重命名分组")
async def rename_group(request: RenameGroupRequest):
    """重命名指定的自选股分组"""
    try:
        data = _load_data()

        group = next((g for g in data["groups"] if g["id"] == request.group_id), None)
        if not group:
            raise HTTPException(status_code=404, detail=f"分组不存在: {request.group_id}")

        old_name = group["name"]
        group["name"] = request.name
        _save_data(data)

        logger.info(f"[自选股API] 重命名分组成功: {request.group_id} {old_name} -> {request.name}")
        return GroupResponse(success=True, group=group)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[自选股API] 重命名分组失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/groups/add-stock", response_model=GroupResponse, summary="添加股票到分组")
async def add_stock(request: AddStockRequest):
    """添加股票到指定分组"""
    try:
        data = _load_data()

        group = next((g for g in data["groups"] if g["id"] == request.group_id), None)
        if not group:
            raise HTTPException(status_code=404, detail=f"分组不存在: {request.group_id}")

        # 检查是否已存在
        if any(s["symbol"] == request.symbol for s in group["stocks"]):
            logger.info(f"[自选股API] 股票已存在: {request.symbol} in {request.group_id}")
            return GroupResponse(success=True, group=group)

        # 添加股票
        group["stocks"].append({
            "symbol": request.symbol,
            "name": request.name
        })
        _save_data(data)

        logger.info(f"[自选股API] 添加股票成功: {request.symbol} to {request.group_id}")
        return GroupResponse(success=True, group=group)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[自选股API] 添加股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/groups/remove-stock", response_model=GroupResponse, summary="从分组删除股票")
async def remove_stock(request: RemoveStockRequest):
    """从指定分组删除股票"""
    try:
        data = _load_data()

        group = next((g for g in data["groups"] if g["id"] == request.group_id), None)
        if not group:
            raise HTTPException(status_code=404, detail=f"分组不存在: {request.group_id}")

        # 删除股票
        original_count = len(group["stocks"])
        group["stocks"] = [s for s in group["stocks"] if s["symbol"] != request.symbol]

        if len(group["stocks"]) == original_count:
            logger.info(f"[自选股API] 股票不存在: {request.symbol} in {request.group_id}")
        else:
            _save_data(data)
            logger.info(f"[自选股API] 删除股票成功: {request.symbol} from {request.group_id}")

        return GroupResponse(success=True, group=group)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[自选股API] 删除股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/groups/refresh-interval", response_model=GroupResponse, summary="设置刷新频率")
async def set_refresh_interval(request: SetRefreshIntervalRequest):
    """设置分组的刷新频率"""
    try:
        data = _load_data()

        group = next((g for g in data["groups"] if g["id"] == request.group_id), None)
        if not group:
            raise HTTPException(status_code=404, detail=f"分组不存在: {request.group_id}")

        group["refreshInterval"] = request.interval
        _save_data(data)

        logger.info(f"[自选股API] 设置刷新频率成功: {request.group_id} -> {request.interval}ms")
        return GroupResponse(success=True, group=group)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[自选股API] 设置刷新频率失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/groups/toggle-preheat", response_model=GroupResponse, summary="切换预热状态")
async def toggle_preheat(request: TogglePreheatRequest):
    """切换分组的预热状态"""
    try:
        data = _load_data()

        group = next((g for g in data["groups"] if g["id"] == request.group_id), None)
        if not group:
            raise HTTPException(status_code=404, detail=f"分组不存在: {request.group_id}")

        group["preheat"] = not group["preheat"]
        _save_data(data)

        logger.info(f"[自选股API] 切换预热状态成功: {request.group_id} -> {group['preheat']}")
        return GroupResponse(success=True, group=group)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[自选股API] 切换预热状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
