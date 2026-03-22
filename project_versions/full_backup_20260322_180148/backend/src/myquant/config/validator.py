# -*- coding: utf-8 -*-
"""
配置验证模块 - MyQuant v10.0.0

> 创建日期: 2026-02-06
> 目的: 提供启动时配置验证，防止运行时错误
>
> 功能:
> 1. 验证端口范围和可用性
> 2. 验证环境配置
> 3. 验证数据源配置
> 4. 验证路径和权限
> 5. 提供友好的错误提示
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

# 尝试导入配置
try:
    from .ports import PortConfig
    from .app_config import AppConfig
except ImportError:
    PortConfig = None
    AppConfig = None


class ConfigValidationError(Exception):
    """配置验证错误"""

    def __init__(self, message: str, config_name: str = "", details: Dict[str, Any] = None):
        """
        初始化配置验证错误

        Args:
            message: 错误消息
            config_name: 配置名称
            details: 错误详情
        """
        self.message = message
        self.config_name = config_name
        self.details = details or {}
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """格式化错误消息"""
        msg = f"❌ 配置验证失败"
        if self.config_name:
            msg += f" [{self.config_name}]"
        msg += f": {self.message}"

        if self.details:
            msg += "\n📋 详情:"
            for key, value in self.details.items():
                msg += f"\n   - {key}: {value}"

        return msg


class ConfigValidator:
    """配置验证器"""

    def __init__(self):
        """初始化验证器"""
        self.errors: List[ConfigValidationError] = []
        self.warnings: List[str] = []

    # ==================== 端口验证 ====================

    def validate_port_range(
        self,
        port: int,
        config_name: str = "端口"
    ) -> bool:
        """
        验证端口范围

        Args:
            port: 端口号
            config_name: 配置名称

        Returns:
            是否有效
        """
        if not isinstance(port, int):
            self.errors.append(ConfigValidationError(
                f"端口必须是整数，当前类型: {type(port).__name__}",
                config_name,
                {"当前值": port, "期望类型": "int"}
            ))
            return False

        if not 1024 <= port <= 65535:
            self.errors.append(ConfigValidationError(
                f"端口必须在有效范围内 (1024-65535)",
                config_name,
                {"当前端口": port, "有效范围": "1024-65535"}
            ))
            return False

        return True

    def validate_all_ports(self) -> bool:
        """验证所有端口配置"""
        if PortConfig is None:
            logger.warning("⚠️ PortConfig未导入，跳过端口验证")
            return True

        logger.info("🔍 验证端口配置...")

        valid = True

        # 验证所有核心端口
        ports_to_check = {
            "API_PORT": PortConfig.API_PORT,
            "WS_PORT": PortConfig.WS_PORT,
            "DATA_HUB_PORT": PortConfig.DATA_HUB_PORT,
            "QLIB_PORT": PortConfig.QLIB_PORT,
            "AI_ENGINE_PORT": PortConfig.AI_ENGINE_PORT,
            "RISK_PORT": PortConfig.RISK_PORT,
            "TRADING_PORT": PortConfig.TRADING_PORT,
            "REDIS_PORT": PortConfig.REDIS_PORT,
        }

        for name, port in ports_to_check.items():
            if not self.validate_port_range(port, name):
                valid = False

        # 检查端口冲突
        port_values = list(ports_to_check.values())
        if len(port_values) != len(set(port_values)):
            # 找出重复的端口
            from collections import Counter
            duplicates = [port for port, count in Counter(port_values).items() if count > 1]
            self.errors.append(ConfigValidationError(
                f"检测到端口冲突",
                "端口配置",
                {"重复端口": duplicates}
            ))
            valid = False

        return valid

    # ==================== 主机验证 ====================

    def validate_host(self, host: str, config_name: str = "主机") -> bool:
        """
        验证主机配置

        Args:
            host: 主机地址
            config_name: 配置名称

        Returns:
            是否有效
        """
        if not host:
            self.errors.append(ConfigValidationError(
                "主机地址不能为空",
                config_name
            ))
            return False

        # 检查是否为有效的主机格式
        valid_patterns = ["0.0.0.0", "localhost", "127.0.0.1"]
        if host not in valid_patterns and not host.startswith(("192.168.", "10.", "172.")):
            self.warnings.append(f"⚠️ 非标准主机地址: {host} ({config_name})")

        return True

    def validate_all_hosts(self) -> bool:
        """验证所有主机配置"""
        if PortConfig is None:
            return True

        logger.info("🔍 验证主机配置...")

        valid = True

        hosts_to_check = {
            "API_HOST": PortConfig.API_HOST,
            "WS_HOST": PortConfig.WS_HOST,
            "REDIS_HOST": PortConfig.REDIS_HOST,
        }

        for name, host in hosts_to_check.items():
            if not self.validate_host(host, name):
                valid = False

        return valid

    # ==================== 数据源验证 ====================

    def validate_datasource(self) -> bool:
        """验证数据源配置"""
        if AppConfig is None:
            logger.warning("⚠️ AppConfig未导入，跳过数据源验证")
            return True

        logger.info("🔍 验证数据源配置...")

        try:
            config = AppConfig()

            # 检查是否至少启用一个数据源
            enabled_count = sum([
                config.datasource.xtquant.enabled,
                config.datasource.pytdx.enabled,
                config.datasource.localdb.enabled
            ])

            if enabled_count == 0:
                self.errors.append(ConfigValidationError(
                    "至少需要启用一个数据源",
                    "数据源配置",
                    {
                        "XtQuant": config.datasource.xtquant.enabled,
                        "PyTdx": config.datasource.pytdx.enabled,
                        "LocalDB": config.datasource.localdb.enabled
                    }
                ))
                return False

            # 检查XtQuant配置
            if config.datasource.xtquant.enabled:
                if not config.datasource.xtquant.account:
                    self.warnings.append("⚠️ XtQuant已启用但未配置账号")
                if not config.datasource.xtquant.password:
                    self.warnings.append("⚠️ XtQuant已启用但未配置密码")

            # 检查PyTdx路径
            if config.datasource.pytdx.enabled:
                tdx_path = Path(config.datasource.pytdx.local_data_path)
                if not tdx_path.exists():
                    self.warnings.append(f"⚠️ PyTdx路径不存在: {tdx_path}")

            # 检查LocalDB路径
            if config.datasource.localdb.enabled:
                db_path = Path(config.datasource.localdb.db_path)
                db_dir = db_path.parent
                if not db_dir.exists():
                    self.warnings.append(f"⚠️ LocalDB目录不存在: {db_dir}")

            return True

        except Exception as e:
            self.errors.append(ConfigValidationError(
                f"数据源配置验证异常: {str(e)}",
                "数据源配置"
            ))
            return False

    # ==================== 环境验证 ====================

    def validate_environment(self) -> bool:
        """验证环境配置"""
        if AppConfig is None:
            return True

        logger.info("🔍 验证环境配置...")

        try:
            config = AppConfig()

            valid_environments = ['development', 'testing', 'staging', 'production']
            if config.environment not in valid_environments:
                self.errors.append(ConfigValidationError(
                    f"无效的环境配置",
                    "环境配置",
                    {
                        "当前值": config.environment,
                        "有效值": valid_environments
                    }
                ))
                return False

            # 生产环境警告
            if config.environment == 'production':
                if config.api.fastapi.debug:
                    self.warnings.append("⚠️ 生产环境不建议启用debug模式")
                if config.api.fastapi.reload:
                    self.warnings.append("⚠️ 生产环境不建议启用自动重载")

            return True

        except Exception as e:
            self.errors.append(ConfigValidationError(
                f"环境配置验证异常: {str(e)}",
                "环境配置"
            ))
            return False

    # ==================== 路径验证 ====================

    def validate_paths(self) -> bool:
        """验证路径配置"""
        if AppConfig is None:
            return True

        logger.info("🔍 验证路径配置...")

        try:
            config = AppConfig()

            # 检查关键目录
            critical_paths = {
                "数据目录": config.data_dir,
                "后端目录": config.backend_dir,
                "日志目录": config.log_dir_path,
            }

            all_valid = True
            for name, path in critical_paths.items():
                if not path.exists():
                    # 尝试创建目录
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                        logger.info(f"✅ 已创建目录: {name} - {path}")
                    except Exception as e:
                        self.errors.append(ConfigValidationError(
                            f"无法创建目录",
                            name,
                            {"路径": str(path), "错误": str(e)}
                        ))
                        all_valid = False
                elif not path.is_dir():
                    self.errors.append(ConfigValidationError(
                        "路径存在但不是目录",
                        name,
                        {"路径": str(path)}
                    ))
                    all_valid = False

            return all_valid

        except Exception as e:
            self.errors.append(ConfigValidationError(
                f"路径验证异常: {str(e)}",
                "路径配置"
            ))
            return False

    # ==================== 综合验证 ====================

    def validate_all(
        self,
        check_ports: bool = True,
        check_hosts: bool = True,
        check_datasource: bool = True,
        check_environment: bool = True,
        check_paths: bool = True,
        auto_fix: bool = False
    ) -> bool:
        """
        执行所有配置验证

        Args:
            check_ports: 是否检查端口
            check_hosts: 是否检查主机
            check_datasource: 是否检查数据源
            check_environment: 是否检查环境
            check_paths: 是否检查路径
            auto_fix: 是否自动修复问题

        Returns:
            是否全部通过验证
        """
        logger.info("=" * 60)
        logger.info("🚀 开始配置验证 (MyQuant v10.0.0)")
        logger.info("=" * 60)

        self.errors.clear()
        self.warnings.clear()

        # 执行各项验证
        if check_ports:
            self.validate_all_ports()

        if check_hosts:
            self.validate_all_hosts()

        if check_datasource:
            self.validate_datasource()

        if check_environment:
            self.validate_environment()

        if check_paths:
            self.validate_paths()

        # 输出结果
        logger.info("\n" + "=" * 60)
        logger.info("📊 验证结果")
        logger.info("=" * 60)

        # 输出警告
        if self.warnings:
            logger.warning(f"⚠️ 发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                logger.warning(f"   {warning}")

        # 输出错误
        if self.errors:
            logger.error(f"❌ 发现 {len(self.errors)} 个错误:")
            for error in self.errors:
                logger.error(str(error))

            logger.info("\n" + "=" * 60)
            logger.error("❌ 配置验证失败！请修复上述错误后重试。")
            logger.info("=" * 60)
            return False

        logger.info("✅ 所有配置验证通过！")
        logger.info("=" * 60)

        return True


# ==================== 便捷函数 ====================

def validate_config(
    check_ports: bool = True,
    check_hosts: bool = True,
    check_datasource: bool = True,
    check_environment: bool = True,
    check_paths: bool = True,
    auto_fix: bool = False,
    exit_on_error: bool = False
) -> bool:
    """
    验证所有配置（便捷函数）

    Args:
        check_ports: 是否检查端口
        check_hosts: 是否检查主机
        check_datasource: 是否检查数据源
        check_environment: 是否检查环境
        check_paths: 是否检查路径
        auto_fix: 是否自动修复问题
        exit_on_error: 验证失败时是否退出程序

    Returns:
        是否全部通过验证
    """
    validator = ConfigValidator()
    result = validator.validate_all(
        check_ports=check_ports,
        check_hosts=check_hosts,
        check_datasource=check_datasource,
        check_environment=check_environment,
        check_paths=check_paths,
        auto_fix=auto_fix
    )

    if not result and exit_on_error:
        logger.error("❌ 配置验证失败，程序退出！")
        sys.exit(1)

    return result


__all__ = [
    'ConfigValidator',
    'ConfigValidationError',
    'validate_config',
]
