"""
股票相关数据模型

定义资产类型、股票信息等
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from .base import BaseModel


class AssetType(str, Enum):
    """资产类型"""
    STOCK = "stock"              # 股票
    INDEX = "index"              # 指数
    SECTOR_BLOCK = "sector"      # 板块
    ETF = "etf"                  # ETF
    FUND = "fund"                # 基金
    BOND = "bond"                # 债券


class MarketType(str, Enum):
    """市场类型"""
    SH = "sh"        # 上海证券交易所
    SZ = "sz"        # 深圳证券交易所
    BJ = "bj"        # 北京证券交易所


class ListStatus(str, Enum):
    """上市状态"""
    LISTED = "listed"          # 正常上市
    SUSPENDED = "suspended"    # 停牌
    DELISTED = "delisted"      # 退市
    IPO = "ipo"                # 新股发行


@dataclass
class StockInfo(BaseModel):
    """股票基本信息"""
    code: str
    name: str
    market: MarketType
    asset_type: AssetType
    list_status: ListStatus = ListStatus.LISTED
    ipo_date: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    total_shares: float = 0.0
    circulating_shares: float = 0.0

    @property
    def full_code(self) -> str:
        """完整代码（带市场后缀）"""
        return f"{self.code}.{self.market.value.upper()}"

    @property
    def is_listed(self) -> bool:
        """是否正常上市"""
        return self.list_status == ListStatus.LISTED


@dataclass
class StockListResult(BaseModel):
    """股票列表查询结果"""
    stocks: List[StockInfo]
    total: int = 0
    page: int = 1
    page_size: int = 100

    @classmethod
    def empty(cls) -> 'StockListResult':
        """创建空结果"""
        return cls(stocks=[], total=0)


def parse_market_type(code: str) -> MarketType:
    """根据代码前缀判断市场类型

    Args:
        code: 股票代码（6位数字）

    Returns:
        MarketType
    """
    if not code:
        return MarketType.SH

    # 6, 5, 9 开头为上海
    if code[0] in ['6', '5', '9']:
        return MarketType.SH
    # 0, 2, 3 开头为深圳
    elif code[0] in ['0', '2', '3']:
        return MarketType.SZ
    # 4, 8 开头为北京
    elif code[0] in ['4', '8']:
        return MarketType.BJ

    return MarketType.SH


def parse_asset_type(code: str) -> AssetType:
    """根据代码判断资产类型

    Args:
        code: 代码

    Returns:
        AssetType
    """
    if not code:
        return AssetType.STOCK

    # 88 开头为板块
    if code.startswith('88') or code.startswith('BK'):
        return AssetType.SECTOR_BLOCK
    # 5 开头为 ETF/基金
    elif code.startswith('5') or code.startswith('15'):
        return AssetType.ETF
    # 指数代码 (000001.SH, 399001.SZ 等)
    elif code.startswith('000') or code.startswith('399') or code.startswith('000'):
        return AssetType.INDEX

    return AssetType.STOCK


def normalize_stock_code(code: str) -> str:
    """标准化股票代码

    将 600000.SH 或 600000 转换为 600000

    Args:
        code: 股票代码（可能带市场后缀）

    Returns:
        标准化后的6位代码
    """
    if not code:
        return code

    # 移除市场后缀
    for market in ['SH', 'SZ', 'BJ', 'sh', 'sz', 'bj']:
        if code.endswith(f'.{market}'):
            return code.split('.')[0]

    return code
