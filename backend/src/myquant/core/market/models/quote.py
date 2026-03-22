"""
行情数据模型

定义实时行情快照的数据格式
"""

from dataclasses import dataclass
from typing import Optional

from .base import BaseModel


@dataclass
class QuoteData(BaseModel):
    """实时行情数据

    标准化的 L1 行情快照
    """
    code: str
    name: str
    price: float
    change: float
    change_pct: float
    volume: float
    amount: float = 0.0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    last_close: float = 0.0
    bid1: float = 0.0
    bid2: float = 0.0
    bid3: float = 0.0
    bid4: float = 0.0
    bid5: float = 0.0
    bid_vol1: float = 0.0
    bid_vol2: float = 0.0
    bid_vol3: float = 0.0
    bid_vol4: float = 0.0
    bid_vol5: float = 0.0
    ask1: float = 0.0
    ask2: float = 0.0
    ask3: float = 0.0
    ask4: float = 0.0
    ask5: float = 0.0
    ask_vol1: float = 0.0
    ask_vol2: float = 0.0
    ask_vol3: float = 0.0
    ask_vol4: float = 0.0
    ask_vol5: float = 0.0
    timestamp: Optional[str] = None
    turnover: float = 0.0

    @property
    def is_up(self) -> bool:
        """是否上涨"""
        return self.change_pct > 0

    @property
    def is_down(self) -> bool:
        """是否下跌"""
        return self.change_pct < 0

    @property
    def is_limit_up(self) -> bool:
        """是否涨停（简化判断，涨跌幅 >= 9.9%）"""
        return self.change_pct >= 9.9

    @property
    def is_limit_down(self) -> bool:
        """是否跌停（简化判断，涨跌幅 <= -9.9%）"""
        return self.change_pct <= -9.9

    @property
    def amplitude(self) -> float:
        """振幅 (%)"""
        if self.last_close == 0 or self.high == 0 or self.low == 0:
            return 0.0
        return (self.high - self.low) / self.last_close * 100

    @property
    def bid_volume_total(self) -> float:
        """买盘总量（五档合计）"""
        return sum([
            self.bid_vol1, self.bid_vol2, self.bid_vol3,
            self.bid_vol4, self.bid_vol5
        ])

    @property
    def ask_volume_total(self) -> float:
        """卖盘总量（五档合计）"""
        return sum([
            self.ask_vol1, self.ask_vol2, self.ask_vol3,
            self.ask_vol4, self.ask_vol5
        ])
