"""
板块数据模型

定义板块相关的数据格式
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from .base import BaseModel


class SectorType(str, Enum):
    """板块类型"""
    INDUSTRY = "industry"      # 行业板块
    CONCEPT = "concept"        # 概念板块
    REGION = "region"          # 地域板块


@dataclass
class SectorData(BaseModel):
    """板块数据

    板块指数和成分股统计信息
    """
    code: str
    name: str
    sector_type: str          # 板块类型
    index: float              # 板块指数
    change_pct: float         # 涨跌幅 (%)
    up_count: int             # 上涨家数
    down_count: int           # 下跌家数
    component_count: int      # 成分股数量
    amount: float = 0.0       # 成交额
    volume_ratio: float = 0.0 # 量比
    turnover_rate: float = 0.0  # 换手率(%)
    amplitude: float = 0.0    # 振幅(%)
    pe_ratio: float = 0.0     # 市盈率
    pb_ratio: float = 0.0     # 市净率
    timestamp: Optional[str] = None

    @property
    def is_hot(self) -> bool:
        """是否热点板块（涨跌幅 > 0）"""
        return self.change_pct > 0

    @property
    def breadth_ratio(self) -> float:
        """涨跌比（上涨家数 / 总家数）"""
        if self.component_count == 0:
            return 0.0
        return self.up_count / self.component_count

    @property
    def strength(self) -> float:
        """板块强度（综合涨跌幅和涨跌比）"""
        return self.change_pct * self.breadth_ratio


@dataclass
class SectorComponent(BaseModel):
    """板块成分股"""
    code: str
    name: str
    price: float = 0.0
    change_pct: float = 0.0
    volume: float = 0.0
    amount: float = 0.0
    weight: float = 0.0        # 在板块中的权重
