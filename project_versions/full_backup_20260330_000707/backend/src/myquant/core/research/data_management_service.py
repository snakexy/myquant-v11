# -*- coding: utf-8 -*-
"""
Research阶段 - 数据管理服务
================================
职责：
- 数据库统计信息
- 分类统计
- 数据导出
- 数据预处理
- 数据质量检查

版本: v1.0
创建日期: 2026-02-11

整合模块：
- data_service: 统一数据获取（L0-L5分层数据访问）
- stock_service: 股票信息和列表管理
- data_cleaning_service: 数据清洗和质量检查
"""

from typing import Dict, List, Optional, Any, Tuple
from loguru import logger
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd
import numpy as np


@dataclass
class DatabaseStats:
    """数据库统计信息"""
    total_stocks: int = 0
    daily_records: int = 0
    minute_records: int = 0
    data_size_mb: float = 0.0
    last_update: Optional[str] = None
    data_sources: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CategoryStats:
    """分类统计信息"""
    category: str = ""
    count: int = 0
    subcategories: Dict[str, int] = field(default_factory=dict)


@dataclass
class DataQualityReport:
    """数据质量报告"""
    total_rows: int = 0
    missing_values: int = 0
    missing_percentage: float = 0.0
    duplicate_rows: int = 0
    outliers_detected: int = 0
    quality_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ExportResult:
    """数据导出结果"""
    file_path: str = ""
    rows_exported: int = 0
    file_size_kb: float = 0.0
    export_time: float = 0.0


class DataManagementService:
    """
    数据管理服务

    核心职责：
    1. 数据库统计 - 获取数据统计信息
    2. 分类统计 - 按行业/板块/市场统计
    3. 数据导出 - 导出为CSV/Excel/Parquet
    4. 数据预处理 - 清洗、填充、标准化
    5. 数据质量检查 - 评估数据质量

    整合来源：
    - services.research.data_service
    - services.research.stock_service
    - services.research.data_cleaning_service
    """

    def __init__(self):
        """初始化数据管理服务"""
        # 初始化子服务
        self._init_subservices()

        # 数据路径配置
        self.data_paths = {
            "qlib": Path(r"E:\zd_zsone\qlib_data"),
            "tdx": Path(r"E:\zd_zsone\vipdoc"),
            "export": Path(r"E:\MyQuant_v10.0.0\data\exports")
        }

        # 确保导出目录存在
        self.data_paths["export"].mkdir(parents=True, exist_ok=True)

        logger.info("✅ DataManagementService初始化完成")

    def _init_subservices(self):
        """初始化子服务"""
        try:
            from myquant.core.research.data_service import get_research_data_service
            self.data_service = get_research_data_service()
            logger.debug("✅ 数据服务依赖已加载")
        except Exception as e:
            logger.warning(f"⚠️ 数据服务依赖加载失败: {e}")
            self.data_service = None

        try:
            from myquant.core.research.stock_service import get_research_stock_service
            self.stock_service = get_research_stock_service()
            logger.debug("✅ 股票服务依赖已加载")
        except Exception as e:
            logger.warning(f"⚠️ 股票服务依赖加载失败: {e}")
            self.stock_service = None

        try:
            from myquant.core.research.data_cleaning_service import get_data_cleaning_service
            self.cleaning_service = get_data_cleaning_service()
            logger.debug("✅ 数据清洗服务依赖已加载")
        except Exception as e:
            logger.warning(f"⚠️ 数据清洗服务依赖加载失败: {e}")
            self.cleaning_service = None

        # 初始化缓存服务
        try:
            from myquant.core.research.data_cache_service import get_data_cache_service
            self.cache_service = get_data_cache_service()
            logger.debug("✅ 缓存服务依赖已加载")
        except Exception as e:
            logger.warning(f"⚠️ 缓存服务依赖加载失败: {e}")
            self.cache_service = None

    # ==================== 数据库统计 ====================

    def get_database_stats(self) -> DatabaseStats:
        """
        获取数据库统计信息

        Returns:
            DatabaseStats对象

        实现说明：
            - 集成data_service和stock_service的统计信息
            - 扫描数据目录获取文件大小和记录数
            - 当data_service可用时，使用其统计信息
        """
        logger.info("获取数据库统计信息")

        stats = DatabaseStats(
            total_stocks=0,
            daily_records=0,
            minute_records=0,
            data_size_mb=0.0,
            last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_sources={}
        )

        # 1. 尝试从data_service获取统计信息
        if self.data_service:
            try:
                service_stats = self.data_service.get_stats()
                stats.data_sources["data_service"] = {
                    "status": "available",
                    "stats": service_stats
                }
            except Exception as e:
                logger.warning(f"获取data_service统计失败: {e}")

        # 2. 扫描QLib数据目录
        try:
            qlib_path = self.data_paths["qlib"]
            if qlib_path.exists():
                # 计算QLib数据大小
                import os
                total_size = 0
                file_count = 0
                for dirpath, dirnames, filenames in os.walk(qlib_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.isfile(filepath):
                            total_size += os.path.getsize(filepath)
                            file_count += 1

                stats.data_sources["qlib"] = {
                    "status": "available",
                    "path": str(qlib_path),
                    "size_mb": round(total_size / (1024 * 1024), 2),
                    "files": file_count
                }
                stats.data_size_mb += round(total_size / (1024 * 1024), 2)
                logger.debug(f"QLib数据: {file_count}文件, {stats.data_size_mb:.2f}MB")
        except Exception as e:
            logger.warning(f"扫描QLib数据目录失败: {e}")
            stats.data_sources["qlib"] = {"status": "error", "error": str(e)}

        # 3. 扫描TDX数据目录
        try:
            tdx_path = self.data_paths["tdx"]
            if tdx_path.exists():
                import os
                total_size = 0
                file_count = 0
                for dirpath, dirnames, filenames in os.walk(tdx_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.isfile(filepath):
                            total_size += os.path.getsize(filepath)
                            file_count += 1

                stats.data_sources["tdx"] = {
                    "status": "available",
                    "path": str(tdx_path),
                    "size_mb": round(total_size / (1024 * 1024), 2),
                    "files": file_count
                }
                stats.data_size_mb += round(total_size / (1024 * 1024), 2)
                logger.debug(f"TDX数据: {file_count}文件, {total_size / (1024 * 1024):.2f}MB")
        except Exception as e:
            logger.warning(f"扫描TDX数据目录失败: {e}")
            stats.data_sources["tdx"] = {"status": "error", "error": str(e)}

        # 4. 尝试从stock_service获取股票数量
        if self.stock_service:
            try:
                # 获取第一页数据来估算总数
                stock_list = self.stock_service.get_stock_list(page=1, size=1)
                if stock_list and "total" in stock_list:
                    stats.total_stocks = stock_list["total"]
                    logger.debug(f"股票总数: {stats.total_stocks}")
            except Exception as e:
                logger.warning(f"获取股票数量失败: {e}")

        # 5. 如果无法获取真实数据，使用估算值
        if stats.total_stocks == 0:
            stats.total_stocks = 5000  # 估算值
            logger.info("使用估算的股票数量")

        return stats

    def get_category_stats(
        self,
        category: str = "industry"
    ) -> List[CategoryStats]:
        """
        获取分类统计信息

        Args:
            category: 分类类型（industry/sector/market）

        Returns:
            分类统计列表

        实现说明：
            - 当stock_service可用时，尝试从其获取分类统计
            - 根据category类型聚合数据
            - 当前返回估算数据，待数据库完善后替换
        """
        logger.info(f"获取分类统计: {category}")

        # 尝试从stock_service获取股票列表来统计分类
        if self.stock_service:
            try:
                # TODO: 从stock_service获取所有股票的分类信息进行统计
                # stock_list = await self.stock_service.get_stock_list(page=1, size=10000)
                # 然后按industry/sector/market聚合

                # 当前实现：由于stock_service也是模拟数据，保留原有逻辑
                pass
            except Exception as e:
                logger.warning(f"从stock_service获取分类统计失败: {e}")

        # 返回基于配置的分类统计（待数据库完善后替换为真实查询）
        if category == "industry":
            return [
                CategoryStats(category="银行", count=42, subcategories={"国有银行": 5, "股份制银行": 12, "城商行": 25}),
                CategoryStats(category="医药", count=156, subcategories={"化学制药": 45, "生物制药": 38, "中药": 35, "医疗器械": 38}),
                CategoryStats(category="科技", count=234, subcategories={"半导体": 28, "软件": 89, "通信": 45, "电子": 72}),
                CategoryStats(category="消费", count=189, subcategories={"食品饮料": 56, "家电": 34, "纺织服装": 23, "商贸零售": 76}),
                CategoryStats(category="工业", count=312, subcategories={"机械": 98, "电力设备": 76, "军工": 45, "建材": 93}),
            ]
        elif category == "sector":
            return [
                CategoryStats(category="金融", count=120, subcategories={"银行": 42, "证券": 28, "保险": 18, "信托": 12, "其他": 20}),
                CategoryStats(category="科技", count=350, subcategories={"半导体": 28, "软件": 89, "通信": 45, "电子": 72, "互联网": 116}),
                CategoryStats(category="医药", count=180, subcategories={"化学制药": 45, "生物制药": 38, "中药": 35, "医疗器械": 38, "医疗服务": 24}),
                CategoryStats(category="消费", count=245, subcategories={"可选消费": 134, "日常消费": 111}),
                CategoryStats(category="工业", count=410, subcategories={"制造业": 312, "公用事业": 52, "能源": 46}),
            ]
        elif category == "market":
            return [
                CategoryStats(category="主板", count=2234, subcategories={"上海主板": 1456, "深圳主板": 778}),
                CategoryStats(category="创业板", count=1350, subcategories={}),
                CategoryStats(category="科创板", count=560, subcategories={}),
                CategoryStats(category="北交所", count=200, subcategories={}),
            ]
        else:
            logger.warning(f"未知的分类类型: {category}")
            return []

    # ==================== 数据导出 ====================

    def export_data(
        self,
        data: Any,
        export_type: str = "csv",
        filename: Optional[str] = None
    ) -> ExportResult:
        """
        导出数据

        Args:
            data: 要导出的数据（DataFrame或dict）
            export_type: 导出类型（csv/excel/parquet/json）
            filename: 文件名（可选，默认自动生成）

        Returns:
            ExportResult对象
        """
        logger.info(f"导出数据: 类型={export_type}")

        start_time = datetime.now()

        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_export_{timestamp}.{export_type}"

        file_path = self.data_paths["export"] / filename

        try:
            # 转换为DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                raise ValueError(f"不支持的数据类型: {type(data)}")

            # 根据类型导出
            if export_type == "csv":
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
            elif export_type == "excel":
                df.to_excel(file_path, index=False, engine="openpyxl")
            elif export_type == "parquet":
                df.to_parquet(file_path, index=False)
            elif export_type == "json":
                df.to_json(file_path, orient="records", force_ascii=False, indent=2)
            else:
                raise ValueError(f"不支持的导出类型: {export_type}")

            # 计算文件大小和导出时间
            export_time = (datetime.now() - start_time).total_seconds()
            file_size_kb = file_path.stat().st_size / 1024

            logger.info(f"数据导出成功: {file_path} ({file_size_kb:.2f} KB)")

            return ExportResult(
                file_path=str(file_path),
                rows_exported=len(df),
                file_size_kb=file_size_kb,
                export_time=export_time
            )

        except Exception as e:
            logger.error(f"数据导出失败: {e}")
            raise

    async def export_data_async(
        self,
        data: Any,
        export_type: str = "csv",
        filename: Optional[str] = None
    ) -> ExportResult:
        """
        导出数据（异步版本）

        Args:
            data: 要导出的数据（DataFrame或dict）
            export_type: 导出类型（csv/excel/parquet/json）
            filename: 文件名（可选，默认自动生成）

        Returns:
            ExportResult对象
        """
        import asyncio

        logger.info(f"导出数据[异步]: 类型={export_type}")

        start_time = datetime.now()

        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_export_{timestamp}.{export_type}"

        file_path = self.data_paths["export"] / filename

        try:
            # 转换为DataFrame（在线程池中执行以避免阻塞）
            df = await asyncio.to_thread(self._convert_to_dataframe, data)

            # 根据类型导出（在线程池中执行）
            await asyncio.to_thread(
                self._save_dataframe_to_file,
                df, file_path, export_type
            )

            # 计算文件大小和导出时间
            export_time = (datetime.now() - start_time).total_seconds()
            file_size_kb = await asyncio.to_thread(
                lambda: file_path.stat().st_size / 1024
            )

            logger.info(f"数据导出成功[异步]: {file_path} ({file_size_kb:.2f} KB)")

            return ExportResult(
                file_path=str(file_path),
                rows_exported=len(df),
                file_size_kb=file_size_kb,
                export_time=export_time
            )

        except Exception as e:
            logger.error(f"数据导出失败[异步]: {e}")
            raise

    def _convert_to_dataframe(self, data: Any) -> pd.DataFrame:
        """
        将数据转换为DataFrame（同步辅助方法）

        Args:
            data: 输入数据

        Returns:
            DataFrame
        """
        if isinstance(data, dict):
            return pd.DataFrame(data)
        elif isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            return data
        else:
            raise ValueError(f"不支持的数据类型: {type(data)}")

    def _save_dataframe_to_file(
        self,
        df: pd.DataFrame,
        file_path: Path,
        export_type: str
    ) -> None:
        """
        保存DataFrame到文件（同步辅助方法）

        Args:
            df: DataFrame对象
            file_path: 文件路径
            export_type: 导出类型
        """
        if export_type == "csv":
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
        elif export_type == "excel":
            df.to_excel(file_path, index=False, engine="openpyxl")
        elif export_type == "parquet":
            df.to_parquet(file_path, index=False)
        elif export_type == "json":
            df.to_json(file_path, orient="records", force_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的导出类型: {export_type}")

    # ==================== 数据预处理 ====================

    def preprocess_data(
        self,
        data: Any,
        operations: List[str] = None
    ) -> Tuple[Any, Optional[DataQualityReport]]:
        """
        数据预处理

        Args:
            data: 要处理的数据
            operations: 操作列表（clean/fill_missing/remove_outliers/standardize）

        Returns:
            (处理后的数据, 质量报告)
        """
        logger.info(f"数据预处理: 操作={operations}")

        if operations is None:
            operations = ["clean", "fill_missing", "remove_outliers"]

        # 转换为DataFrame
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError(f"不支持的数据类型: {type(data)}")

        # 使用数据清洗服务
        if self.cleaning_service and "clean" in operations:
            df, quality_report = self.cleaning_service.clean_kline_data(
                df,
                report_quality=True
            )
        else:
            quality_report = None

        # 其他预处理操作
        if "fill_missing" in operations and self.cleaning_service:
            # 缺失值填充处理
            df = self._fill_missing_values(df, method="forward")
            logger.info(f"缺失值填充完成，剩余缺失值: {df.isnull().sum().sum()}")

        if "remove_outliers" in operations and self.cleaning_service:
            # 异常值检测和处理
            df, outliers_count = self._handle_outliers(df, method="iqr", threshold=3.0)
            logger.info(f"异常值处理完成，处理了 {outliers_count} 个异常值")

        if "standardize" in operations and self.cleaning_service:
            df = self.cleaning_service.standardize_features(df, method="zscore")

        return df, quality_report

    async def preprocess_data_async(
        self,
        data: Any,
        operations: List[str] = None
    ) -> Tuple[Any, Optional[DataQualityReport]]:
        """
        数据预处理（异步版本）

        Args:
            data: 要处理的数据
            operations: 操作列表（clean/fill_missing/remove_outliers/standardize）

        Returns:
            (处理后的数据, 质量报告)
        """
        import asyncio

        logger.info(f"数据预处理[异步]: 操作={operations}")

        if operations is None:
            operations = ["clean", "fill_missing", "remove_outliers"]

        # 转换为DataFrame（在线程池中执行）
        df = await asyncio.to_thread(self._convert_to_dataframe, data)

        # 使用数据清洗服务（如果包含clean操作）
        if self.cleaning_service and "clean" in operations:
            # 将同步的clean_kline_data包装为异步
            df, quality_report = await asyncio.to_thread(
                self.cleaning_service.clean_kline_data,
                df,
                report_quality=True
            )
        else:
            quality_report = None

        # 其他预处理操作（在线程池中执行）
        if "fill_missing" in operations and self.cleaning_service:
            # 缺失值填充处理
            df = await asyncio.to_thread(
                self._fill_missing_values, df, "forward"
            )
            logger.info(f"缺失值填充完成，剩余缺失值: {df.isnull().sum().sum()}")

        if "remove_outliers" in operations and self.cleaning_service:
            # 异常值检测和处理
            df, outliers_count = await asyncio.to_thread(
                self._handle_outliers, df, "iqr", 3.0
            )
            logger.info(f"异常值处理完成，处理了 {outliers_count} 个异常值")

        if "standardize" in operations and self.cleaning_service:
            df = await asyncio.to_thread(
                self.cleaning_service.standardize_features, df, "zscore"
            )

        return df, quality_report

    # ==================== 数据质量检查 ====================

    def check_data_quality(
        self,
        data: Any,
        data_type: str = "kline"
    ) -> DataQualityReport:
        """
        检查数据质量

        Args:
            data: 要检查的数据
            data_type: 数据类型（kline/financial/tick）

        Returns:
            DataQualityReport对象
        """
        logger.info(f"检查数据质量: 类型={data_type}")

        # 转换为DataFrame
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError(f"不支持的数据类型: {type(data)}")

        # 使用数据清洗服务
        if self.cleaning_service:
            return self.cleaning_service.check_quality(df, data_type=data_type)
        else:
            # 简单质量检查
            return DataQualityReport(
                total_rows=len(df),
                missing_values=df.isnull().sum().sum(),
                missing_percentage=(df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100 if len(df) > 0 else 100,
                duplicate_rows=df.duplicated().sum(),
                outliers_detected=0,
                quality_score=100.0,
                issues=[],
                warnings=[]
            )

    async def check_data_quality_async(
        self,
        data: Any,
        data_type: str = "kline"
    ) -> DataQualityReport:
        """
        检查数据质量（异步版本）

        Args:
            data: 要检查的数据
            data_type: 数据类型（kline/financial/tick）

        Returns:
            DataQualityReport对象
        """
        import asyncio

        logger.info(f"检查数据质量[异步]: 类型={data_type}")

        # 转换为DataFrame（在线程池中执行）
        df = await asyncio.to_thread(self._convert_to_dataframe, data)

        # 使用数据清洗服务
        if self.cleaning_service:
            # 将同步的check_quality包装为异步
            return await asyncio.to_thread(
                self.cleaning_service.check_quality,
                df,
                data_type=data_type
            )
        else:
            # 简单质量检查（在线程池中执行）
            return await asyncio.to_thread(
                lambda: DataQualityReport(
                    total_rows=len(df),
                    missing_values=df.isnull().sum().sum(),
                    missing_percentage=(df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100 if len(df) > 0 else 100,
                    duplicate_rows=df.duplicated().sum(),
                    outliers_detected=0,
                    quality_score=100.0,
                    issues=[],
                    warnings=[]
                )
            )

    # ==================== 数据获取 ====================

    async def get_stock_list(
        self,
        page: int = 1,
        size: int = 20,
        market: Optional[str] = None,
        industry: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取股票列表

        Args:
            page: 页码
            size: 每页大小
            market: 市场筛选
            industry: 行业筛选
            search: 搜索关键词

        Returns:
            股票列表数据
        """
        if self.stock_service:
            return await self.stock_service.get_stock_list(
                page=page,
                size=size,
                market=market,
                industry=industry,
                search=search
            )
        else:
            return {"total": 0, "page": page, "size": size, "data": []}

    async def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        获取股票信息

        Args:
            symbol: 股票代码

        Returns:
            股票信息字典
        """
        if self.stock_service:
            info = await self.stock_service.get_stock_info(symbol)
            if info:
                return {
                    "symbol": info.symbol,
                    "name": info.name,
                    "market": info.market,
                    "industry": info.industry,
                    "list_date": info.list_date,
                    "current_price": info.current_price,
                    "pre_close": info.pre_close,
                    "change": info.change,
                    "change_percent": info.change_percent,
                    "volume": info.volume,
                    "amount": info.amount,
                    "market_cap": info.market_cap,
                    "pe_ratio": info.pe_ratio,
                    "pb_ratio": info.pb_ratio
                }
        return None

    # ==================== 数据预处理辅助方法 ====================

    def _fill_missing_values(
        self,
        df: pd.DataFrame,
        method: str = "forward"
    ) -> pd.DataFrame:
        """
        填充缺失值

        Args:
            df: 数据框
            method: 填充方法
                - forward: 前向填充
                - backward: 后向填充
                - mean: 均值填充（仅数值列）
                - median: 中位数填充（仅数值列）
                - drop: 删除含缺失值的行

        Returns:
            填充后的数据框
        """
        df_copy = df.copy()

        if method == "forward":
            # 前向填充
            df_copy.fillna(method='ffill', inplace=True)
            # 如果还有缺失值，用后向填充
            df_copy.fillna(method='bfill', inplace=True)
        elif method == "backward":
            # 后向填充
            df_copy.fillna(method='bfill', inplace=True)
            df_copy.fillna(method='ffill', inplace=True)
        elif method == "mean":
            # 均值填充（仅数值列）
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            df_copy[numeric_cols] = df_copy[numeric_cols].fillna(df_copy[numeric_cols].mean())
        elif method == "median":
            # 中位数填充（仅数值列）
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            df_copy[numeric_cols] = df_copy[numeric_cols].fillna(df_copy[numeric_cols].median())
        elif method == "drop":
            # 删除含缺失值的行
            df_copy.dropna(inplace=True)
        else:
            logger.warning(f"未知的填充方法: {method}，使用前向填充")
            df_copy.fillna(method='ffill', inplace=True)
            df_copy.fillna(method='bfill', inplace=True)

        return df_copy

    def _handle_outliers(
        self,
        df: pd.DataFrame,
        method: str = "iqr",
        threshold: float = 3.0
    ) -> Tuple[pd.DataFrame, int]:
        """
        处理异常值

        Args:
            df: 数据框
            method: 检测方法
                - iqr: 四分位距法
                - zscore: Z分数法
            threshold: 阈值（IQR: 倍数, Z-score: 标准差倍数）

        Returns:
            (处理后的数据框, 处理的异常值数量)
        """
        df_copy = df.copy()
        outliers_count = 0

        # 只处理数值列
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if method == "iqr":
                # 四分位距法
                Q1 = df_copy[col].quantile(0.25)
                Q3 = df_copy[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR

                # 检测异常值
                outliers_mask = (df_copy[col] < lower_bound) | (df_copy[col] > upper_bound)
                outliers_count += outliers_mask.sum()

                # 用边界值替换异常值（钳制处理）
                df_copy.loc[df_copy[col] < lower_bound, col] = lower_bound
                df_copy.loc[df_copy[col] > upper_bound, col] = upper_bound

            elif method == "zscore":
                # Z分数法
                mean = df_copy[col].mean()
                std = df_copy[col].std()

                if std > 0:  # 避免除零
                    z_scores = np.abs((df_copy[col] - mean) / std)
                    outliers_mask = z_scores > threshold
                    outliers_count += outliers_mask.sum()

                    # 用均值替换异常值
                    df_copy.loc[outliers_mask, col] = mean

        logger.debug(f"异常值处理: method={method}, 处理了 {outliers_count} 个异常值")
        return df_copy, outliers_count

    # ==================== 服务统计 ====================

    def get_service_stats(self) -> Dict[str, Any]:
        """
        获取服务统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "data_service": self.data_service is not None,
            "stock_service": self.stock_service is not None,
            "cleaning_service": self.cleaning_service is not None,
            "data_paths": {
                "qlib": str(self.data_paths["qlib"]),
                "tdx": str(self.data_paths["tdx"]),
                "export": str(self.data_paths["export"])
            }
        }

        # 如果data_service可用，获取其统计信息
        if self.data_service:
            stats["data_service_stats"] = self.data_service.get_stats()

        return stats

    # ==================== 缓存支持方法 ====================

    async def get_database_stats_cached(self) -> DatabaseStats:
        """
        获取数据库统计信息（带缓存）

        Returns:
            DatabaseStats对象

        缓存策略:
            - TTL: 5分钟
            - 缓存键: data_mgmt:database_stats
        """
        if self.cache_service:
            from myquant.core.research.data_cache_service import DataCacheKeyType

            # 尝试从缓存获取
            cached = await self.cache_service.get(DataCacheKeyType.DATABASE_STATS)
            if cached is not None:
                logger.debug("[缓存] 数据库统计命中")
                return DatabaseStats(**cached)

        # 缓存未命中，调用原方法
        stats = self.get_database_stats()

        # 存入缓存
        if self.cache_service:
            from myquant.core.research.data_cache_service import DataCacheKeyType
            # 转换为字典以便JSON序列化
            stats_dict = {
                "total_stocks": stats.total_stocks,
                "daily_records": stats.daily_records,
                "minute_records": stats.minute_records,
                "data_size_mb": stats.data_size_mb,
                "last_update": stats.last_update,
                "data_sources": stats.data_sources
            }
            await self.cache_service.set(DataCacheKeyType.DATABASE_STATS, stats_dict)
            logger.debug("[缓存] 数据库统计已缓存")

        return stats

    async def get_category_stats_cached(
        self,
        category: str = "industry"
    ) -> List[CategoryStats]:
        """
        获取分类统计信息（带缓存）

        Args:
            category: 分类类型（industry/sector/market）

        Returns:
            分类统计列表

        缓存策略:
            - TTL: 10分钟
            - 缓存键: data_mgmt:category_stats:{category}
        """
        if self.cache_service:
            from myquant.core.research.data_cache_service import DataCacheKeyType

            # 尝试从缓存获取
            cached = await self.cache_service.get(DataCacheKeyType.CATEGORY_STATS, category)
            if cached is not None:
                logger.debug(f"[缓存] 分类统计命中: {category}")
                return [CategoryStats(**item) for item in cached]

        # 缓存未命中，调用原方法
        stats_list = self.get_category_stats(category)

        # 存入缓存
        if self.cache_service:
            from myquant.core.research.data_cache_service import DataCacheKeyType
            # 转换为字典列表
            stats_dicts = [
                {
                    "category": s.category,
                    "count": s.count,
                    "subcategories": s.subcategories
                }
                for s in stats_list
            ]
            await self.cache_service.set(DataCacheKeyType.CATEGORY_STATS, stats_dicts, category)
            logger.debug(f"[缓存] 分类统计已缓存: {category}")

        return stats_list

    async def get_service_stats_cached(self) -> Dict[str, Any]:
        """
        获取服务状态统计（带缓存）

        Returns:
            服务状态字典

        缓存策略:
            - TTL: 2分钟
            - 缓存键: data_mgmt:service_stats
        """
        if self.cache_service:
            from myquant.core.research.data_cache_service import DataCacheKeyType

            # 尝试从缓存获取
            cached = await self.cache_service.get(DataCacheKeyType.SERVICE_STATS)
            if cached is not None:
                logger.debug("[缓存] 服务统计命中")
                return cached

        # 缓存未命中，调用原方法
        stats = self.get_service_stats()

        # 存入缓存
        if self.cache_service:
            from myquant.core.research.data_cache_service import DataCacheKeyType
            await self.cache_service.set(DataCacheKeyType.SERVICE_STATS, stats)
            logger.debug("[缓存] 服务统计已缓存")

        return stats


# ==================== 全局单例 ====================

_data_management_service_instance: Optional[DataManagementService] = None


def get_data_management_service() -> DataManagementService:
    """
    获取数据管理服务单例

    Returns:
        DataManagementService实例
    """
    global _data_management_service_instance

    if _data_management_service_instance is None:
        _data_management_service_instance = DataManagementService()

    return _data_management_service_instance
