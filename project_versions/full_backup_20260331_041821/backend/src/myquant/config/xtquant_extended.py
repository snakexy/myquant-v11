# -*- coding: utf-8 -*-
"""
XtQuant多实例配置扩展
====================

扩展XtQuantConfig以支持多实例模式
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class XtQuantInstanceConfig(BaseSettings):
    """XtQuant单个实例配置"""

    name: str = Field(default="instance1", description="实例名称")
    account: str = Field(default="", description="账号（仅标识）")
    enabled: bool = Field(default=True, description="是否启用")
    market: str = Field(default="SH", description="负责市场（SH/SZ）")
    max_subscriptions: int = Field(default=300, description="最大订阅数（非VIP 300，VIP 500）")
    install_path: str = Field(default="", description="MiniQMT安装路径")
    data_path: str = Field(default="", description="MiniQMT本地数据路径")
    executable: str = Field(default="XtItClient.exe", description="可执行文件名")
    can_trade: bool = Field(default=False, description="是否可交易")
    is_vip: bool = Field(default=False, description="是否VIP用户")

    class Config:
        env_prefix = "XTQUANT_INSTANCE_"


class XtQuantMultiInstanceConfig(BaseSettings):
    """XtQuant多实例配置"""

    # 是否启用多实例模式
    enable_multi_instance: bool = Field(default=True, description="启用多实例模式")

    # 实例配置列表
    instances: List[XtQuantInstanceConfig] = Field(
        default_factory=lambda: [
            XtQuantInstanceConfig(
                name="instance1",
                account="8887080618",
                enabled=True,
                market="SH",
                max_subscriptions=300,
                install_path=r"E:\GJZQQMT\bin.x64",
                data_path=r"E:\迅投xt量化交易终端 miniQMT独立版\userdata_mini\datadir",  # 共享数据目录
                executable="XtItClient.exe",
                can_trade=True,
                is_vip=False
            ),
            XtQuantInstanceConfig(
                name="instance2",
                account="18049905250",
                enabled=True,
                market="SZ",
                max_subscriptions=300,
                install_path=r"E:\迅投极速交易终端 睿智融科版\bin.x64",
                data_path=r"E:\迅投xt量化交易终端 miniQMT独立版\userdata_mini\datadir",  # 共享数据目录
                executable="XtItClient.exe",
                can_trade=False,
                is_vip=False
            )
        ]
    )

    # 自动按市场分配
    auto_market_routing: bool = Field(
        default=True,
        description="自动按市场分配实例（SH→instance1, SZ→instance2）"
    )

    # 健康检查
    health_check_enabled: bool = Field(default=True, description="启用健康检查")
    health_check_interval: int = Field(default=60, description="健康检查间隔(秒)")

    @property
    def total_subscriptions(self) -> int:
        """总订阅能力（所有实例之和）"""
        return sum(
            inst.max_subscriptions for inst in self.instances if inst.enabled
        )

    @property
    def tradable_instances(self) -> List[XtQuantInstanceConfig]:
        """可交易的实例列表"""
        return [inst for inst in self.instances if inst.enabled and inst.can_trade]

    @property
    def data_instances(self) -> List[XtQuantInstanceConfig]:
        """可获取数据的实例列表"""
        return [inst for inst in self.instances if inst.enabled]

    def get_instance_by_market(self, market: str) -> XtQuantInstanceConfig:
        """
        根据市场获取实例

        Args:
            market: SH（上海）或 SZ（深圳）

        Returns:
            对应的实例配置
        """
        if self.auto_market_routing:
            for inst in self.instances:
                if inst.enabled and inst.market == market:
                    return inst

        # 如果未找到或未启用路由，返回第一个可用实例
        for inst in self.instances:
            if inst.enabled:
                return inst

        # 如果都没有，返回第一个（即使未启用）
        return self.instances[0] if self.instances else XtQuantInstanceConfig()


# 导出默认配置（向后兼容）
ENABLE_MULTI_INSTANCE = True  # 将从配置读取
XTQUANT_INSTANCES = []  # 将从配置读取
