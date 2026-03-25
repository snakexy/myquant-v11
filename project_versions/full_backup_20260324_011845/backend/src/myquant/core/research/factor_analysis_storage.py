# -*- coding: utf-8 -*-
"""
因子分析结果存储管理器
Factor Analysis Result Storage Manager

职责：使用.pkl文件格式存储因子分析结果
- IC/IR分析结果
- 因子分布统计
- 因子相关性矩阵

存储路径：backend/data/factor_analysis/
"""

import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger


class FactorAnalysisStorage:
    """因子分析结果存储管理器"""

    def __init__(self, storage_dir: str = None):
        """
        初始化存储管理器

        Args:
            storage_dir: 存储目录路径
        """
        if storage_dir is None:
            # 默认路径：backend/data/factor_analysis/
            project_root = Path(__file__).parent.parent.parent
            storage_dir = project_root / "backend" / "data" / "factor_analysis"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 创建子目录
        (self.storage_dir / "ic_ir").mkdir(exist_ok=True)
        (self.storage_dir / "distribution").mkdir(exist_ok=True)
        (self.storage_dir / "correlation").mkdir(exist_ok=True)

        logger.info(f"✅ FactorAnalysisStorage初始化完成: {self.storage_dir}")

    # ==================== IC/IR分析结果 ====================

    def save_ic_ir_result(
        self,
        factor_name: str,
        result: Dict[str, Any],
        analysis_date: Optional[str] = None
    ) -> bool:
        """
        保存IC/IR分析结果

        Args:
            factor_name: 因子名称
            result: 分析结果字典
                {
                    "factor_name": str,
                    "start_date": str,
                    "end_date": str,
                    "ic_mean": float,
                    "ic_std": float,
                    "ic_min": float,
                    "ic_max": float,
                    "ir": float,
                    "ic_positive_ratio": float,
                    "t_stat": float,
                    "p_value": float,
                    "ic_series": List[Dict],
                }
            analysis_date: 分析日期 (YYYY-MM-DD)

        Returns:
            是否保存成功
        """
        try:
            # 文件名：factor_name_YYYY-MM-DD.pkl
            if analysis_date is None:
                analysis_date = datetime.now().strftime("%Y-%m-%d")

            filename = f"{factor_name}_{analysis_date}.pkl"
            filepath = self.storage_dir / "ic_ir" / filename

            # 保存为pkl文件
            with open(filepath, 'wb') as f:
                pickle.dump(result, f)

            logger.debug(f"💾 保存IC/IR结果: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ 保存IC/IR结果失败: {e}")
            return False

    def load_ic_ir_result(
        self,
        factor_name: str,
        analysis_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        加载IC/IR分析结果

        Args:
            factor_name: 因子名称
            analysis_date: 分析日期 (YYYY-MM-DD)

        Returns:
            分析结果字典，不存在返回None
        """
        try:
            if analysis_date is None:
                # 查找最新的分析结果
                return self._load_latest_ic_ir_result(factor_name)

            filename = f"{factor_name}_{analysis_date}.pkl"
            filepath = self.storage_dir / "ic_ir" / filename

            if not filepath.exists():
                logger.warning(f"⚠️ IC/IR结果不存在: {filename}")
                return None

            with open(filepath, 'rb') as f:
                result = pickle.load(f)

            logger.debug(f"📖 加载IC/IR结果: {filename}")
            return result

        except Exception as e:
            logger.error(f"❌ 加载IC/IR结果失败: {e}")
            return None

    def _load_latest_ic_ir_result(self, factor_name: str) -> Optional[Dict[str, Any]]:
        """加载最新的IC/IR分析结果"""
        try:
            # 列出所有该因子的分析结果文件
            pattern = f"{factor_name}_*.pkl"
            files = list((self.storage_dir / "ic_ir").glob(pattern))

            if not files:
                return None

            # 按修改时间排序，取最新的
            latest_file = max(files, key=lambda f: f.stat().st_mtime)

            with open(latest_file, 'rb') as f:
                result = pickle.load(f)

            logger.debug(f"📖 加载最新IC/IR结果: {latest_file.name}")
            return result

        except Exception as e:
            logger.error(f"❌ 加载最新IC/IR结果失败: {e}")
            return None

    def list_ic_ir_results(self, factor_name: Optional[str] = None) -> List[str]:
        """
        列出IC/IR分析结果文件

        Args:
            factor_name: 因子名称（可选）

        Returns:
            文件名列表
        """
        try:
            if factor_name:
                pattern = f"{factor_name}_*.pkl"
            else:
                pattern = "*.pkl"

            files = list((self.storage_dir / "ic_ir").glob(pattern))
            return [f.name for f in files]

        except Exception as e:
            logger.error(f"❌ 列出IC/IR结果失败: {e}")
            return []

    # ==================== 因子分布统计 ====================

    def save_distribution_stats(
        self,
        factor_name: str,
        result: Dict[str, Any],
        analysis_date: Optional[str] = None
    ) -> bool:
        """
        保存因子分布统计

        Args:
            factor_name: 因子名称
            result: 分布统计结果
            analysis_date: 分析日期

        Returns:
            是否保存成功
        """
        try:
            if analysis_date is None:
                analysis_date = datetime.now().strftime("%Y-%m-%d")

            filename = f"{factor_name}_{analysis_date}.pkl"
            filepath = self.storage_dir / "distribution" / filename

            with open(filepath, 'wb') as f:
                pickle.dump(result, f)

            logger.debug(f"💾 保存分布统计: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ 保存分布统计失败: {e}")
            return False

    def load_distribution_stats(
        self,
        factor_name: str,
        analysis_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        加载因子分布统计

        Args:
            factor_name: 因子名称
            analysis_date: 分析日期

        Returns:
            分布统计结果，不存在返回None
        """
        try:
            if analysis_date is None:
                return self._load_latest_distribution_stats(factor_name)

            filename = f"{factor_name}_{analysis_date}.pkl"
            filepath = self.storage_dir / "distribution" / filename

            if not filepath.exists():
                return None

            with open(filepath, 'rb') as f:
                result = pickle.load(f)

            logger.debug(f"📖 加载分布统计: {filename}")
            return result

        except Exception as e:
            logger.error(f"❌ 加载分布统计失败: {e}")
            return None

    def _load_latest_distribution_stats(self, factor_name: str) -> Optional[Dict[str, Any]]:
        """加载最新的分布统计"""
        try:
            pattern = f"{factor_name}_*.pkl"
            files = list((self.storage_dir / "distribution").glob(pattern))

            if not files:
                return None

            latest_file = max(files, key=lambda f: f.stat().st_mtime)

            with open(latest_file, 'rb') as f:
                result = pickle.load(f)

            logger.debug(f"📖 加载最新分布统计: {latest_file.name}")
            return result

        except Exception as e:
            logger.error(f"❌ 加载最新分布统计失败: {e}")
            return None

    # ==================== 因子相关性矩阵 ====================

    def save_correlation_matrix(
        self,
        result: Dict[str, Any],
        analysis_id: Optional[str] = None
    ) -> bool:
        """
        保存因子相关性矩阵

        Args:
            result: 相关性矩阵结果
            analysis_id: 分析ID

        Returns:
            是否保存成功
        """
        try:
            if analysis_id is None:
                analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S")

            filename = f"correlation_{analysis_id}.pkl"
            filepath = self.storage_dir / "correlation" / filename

            with open(filepath, 'wb') as f:
                pickle.dump(result, f)

            logger.debug(f"💾 保存相关性矩阵: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ 保存相关性矩阵失败: {e}")
            return False

    def load_correlation_matrix(
        self,
        analysis_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        加载因子相关性矩阵

        Args:
            analysis_id: 分析ID

        Returns:
            相关性矩阵结果，不存在返回None
        """
        try:
            filename = f"correlation_{analysis_id}.pkl"
            filepath = self.storage_dir / "correlation" / filename

            if not filepath.exists():
                return None

            with open(filepath, 'rb') as f:
                result = pickle.load(f)

            logger.debug(f"📖 加载相关性矩阵: {filename}")
            return result

        except Exception as e:
            logger.error(f"❌ 加载相关性矩阵失败: {e}")
            return None

    # ==================== 工具方法 ====================

    def get_storage_stats(self) -> Dict[str, int]:
        """
        获取存储统计信息

        Returns:
            统计信息字典
        """
        try:
            ic_ir_count = len(list((self.storage_dir / "ic_ir").glob("*.pkl")))
            distribution_count = len(list((self.storage_dir / "distribution").glob("*.pkl")))
            correlation_count = len(list((self.storage_dir / "correlation").glob("*.pkl")))

            return {
                "ic_ir_results": ic_ir_count,
                "distribution_stats": distribution_count,
                "correlation_matrix": correlation_count,
                "total": ic_ir_count + distribution_count + correlation_count
            }

        except Exception as e:
            logger.error(f"❌ 获取存储统计失败: {e}")
            return {
                "ic_ir_results": 0,
                "distribution_stats": 0,
                "correlation_matrix": 0,
                "total": 0
            }

    def clear_old_results(self, days: int = 30) -> int:
        """
        清理旧的分析结果

        Args:
            days: 保留天数

        Returns:
            删除的文件数量
        """
        try:
            from datetime import timedelta

            cutoff_time = datetime.now() - timedelta(days=days)
            deleted_count = 0

            # 清理IC/IR结果
            for filepath in (self.storage_dir / "ic_ir").glob("*.pkl"):
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_time:
                    filepath.unlink()
                    deleted_count += 1

            # 清理分布统计
            for filepath in (self.storage_dir / "distribution").glob("*.pkl"):
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_time:
                    filepath.unlink()
                    deleted_count += 1

            # 清理相关性矩阵
            for filepath in (self.storage_dir / "correlation").glob("*.pkl"):
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_time:
                    filepath.unlink()
                    deleted_count += 1

            logger.info(f"🗑️ 已清理 {deleted_count} 个旧分析结果（{days}天前）")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ 清理旧结果失败: {e}")
            return 0


# 全局存储实例
_factor_analysis_storage = None


def get_factor_analysis_storage() -> FactorAnalysisStorage:
    """获取因子分析存储管理器实例"""
    global _factor_analysis_storage
    if _factor_analysis_storage is None:
        _factor_analysis_storage = FactorAnalysisStorage()
    return _factor_analysis_storage
