# -*- coding: utf-8 -*-
"""
用户配置 API 路由

提供用户配置的持久化存储：
- 指标配置（启用哪些指标、参数、高度等）
- 图表布局配置
- 个性化设置
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from loguru import logger
import json
from pathlib import Path
import os

router = APIRouter(prefix="/settings", tags=["用户配置"])


# ==================== 配置文件存储 ====================

CONFIG_DIR = Path("data/config")
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_user_config_path(user_id: str, setting_type: str = "general") -> Path:
    """获取用户配置文件路径"""
    return CONFIG_DIR / f"{user_id}_{setting_type}.json"


def load_config_from_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """从文件加载配置"""
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[Settings] 读取配置文件失败 {file_path}: {e}")
    return None


def save_config_to_file(file_path: Path, data: Dict[str, Any]) -> bool:
    """保存配置到文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"[Settings] 配置已保存到 {file_path}")
        return True
    except Exception as e:
        logger.error(f"[Settings] 保存配置文件失败 {file_path}: {e}")
        return False


# ==================== 请求模型 ====================

class UserSettings(BaseModel):
    """用户配置"""
    userId: str = Field(default="default", description="用户ID")
    settings: Dict[str, Any] = Field(default={}, description="配置数据")


class IndicatorSettings(BaseModel):
    """指标配置"""
    userId: str = Field(default="default", description="用户ID")
    activeIndicators: list[str] = Field(default=["MACD"], description="启用的指标")
    overlayIndicators: list[str] = Field(default=[], description="主图叠加指标")
    indicatorParams: Dict[str, Any] = Field(default={}, description="指标参数")
    paneHeights: Dict[str, int] = Field(default={}, description="指标pane高度")


# ==================== API 端点 ====================

@router.get("/indicators/{user_id}")
async def get_indicator_settings(user_id: str = "default") -> Dict[str, Any]:
    """获取指标配置

    Args:
        user_id: 用户ID

    Returns:
        {
            'activeIndicators': [...],
            'overlayIndicators': [...],
            'indicatorParams': {...},
            'paneHeights': {...}
        }
    """
    try:
        config_path = get_user_config_path(user_id, "indicators")
        data = load_config_from_file(config_path)

        if data:
            return data
        else:
            # 返回默认配置
            return {
                'activeIndicators': ['MACD'],
                'overlayIndicators': [],
                'indicatorParams': {},
                'paneHeights': {}
            }

    except Exception as e:
        logger.error(f"[Settings API] 获取指标配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/indicators")
async def save_indicator_settings(data: IndicatorSettings) -> Dict[str, str]:
    """保存指标配置

    Args:
        data: 指标配置数据

    Returns:
        {'status': 'success', 'message': '配置已保存'}
    """
    try:
        config_path = get_user_config_path(data.userId, "indicators")
        config_data = {
            'activeIndicators': data.activeIndicators,
            'overlayIndicators': data.overlayIndicators,
            'indicatorParams': data.indicatorParams,
            'paneHeights': data.paneHeights
        }

        if save_config_to_file(config_path, config_data):
            logger.info(f"[Settings API] 已保存用户 {data.userId} 的指标配置")
            return {'status': 'success', 'message': '配置已保存'}
        else:
            raise HTTPException(status_code=500, detail="保存配置失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Settings API] 保存指标配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/general/{user_id}")
async def get_general_settings(user_id: str = "default") -> Dict[str, Any]:
    """获取通用配置

    Args:
        user_id: 用户ID

    Returns:
        用户配置数据
    """
    try:
        config_path = get_user_config_path(user_id, "general")
        data = load_config_from_file(config_path)
        return data or {}

    except Exception as e:
        logger.error(f"[Settings API] 获取通用配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/general")
async def save_general_settings(data: UserSettings) -> Dict[str, str]:
    """保存通用配置

    Args:
        data: 配置数据

    Returns:
        {'status': 'success', 'message': '配置已保存'}
    """
    try:
        config_path = get_user_config_path(data.userId, "general")

        if save_config_to_file(config_path, data.settings):
            logger.info(f"[Settings API] 已保存用户 {data.userId} 的通用配置")
            return {'status': 'success', 'message': '配置已保存'}
        else:
            raise HTTPException(status_code=500, detail="保存配置失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Settings API] 保存通用配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
