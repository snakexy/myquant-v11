"""
财务数据模型

定义上市公司财务数据格式
"""

from dataclasses import dataclass
from typing import Optional

from .base import BaseModel


@dataclass
class FinancialData(BaseModel):
    """财务数据

    上市公司关键财务指标
    """
    code: str
    report_date: str         # 报告期 (YYYYMMDD 格式)
    revenue: float = 0.0     # 营业收入（万元）
    net_profit: float = 0.0  # 净利润（万元）
    eps: float = 0.0         # 每股收益（元）
    bvps: float = 0.0        # 每股净资产（元）
    roe: float = 0.0         # 净资产收益率（%）
    total_assets: float = 0.0      # 总资产（万元）
    total_liabilities: float = 0.0 # 总负债（万元）
    total_shares: float = 0.0      # 总股本（万股）
    circulating_shares: float = 0.0 # 流通股本（万股）
    pe_ttm: float = 0.0      # 市盈率 TTM
    pb: float = 0.0          # 市净率
    ps_ttm: float = 0.0      # 市销率 TTM
    pcf: float = 0.0         # 市现率

    @property
    def is_profitable(self) -> bool:
        """是否盈利"""
        return self.net_profit > 0

    @property
    def is_quality(self) -> bool:
        """是否优质（ROE > 15%）"""
        return self.roe > 15.0

    @property
    def debt_ratio(self) -> float:
        """资产负债率"""
        if self.total_assets == 0:
            return 0.0
        return self.total_liabilities / self.total_assets * 100

    @property
    def margin(self) -> float:
        """净利率"""
        if self.revenue == 0:
            return 0.0
        return self.net_profit / self.revenue * 100
