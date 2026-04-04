# -*- coding: utf-8 -*-
"""
MyQuant v10.0.0 - 统一配置管理
==================================

整合所有配置类别：
1. DataSourceConfig - 数据源配置
2. APIConfig - API配置
3. CacheConfig - 缓存配置
4. QLibConfig - QLib配置
5. ThreeStageConfig - 三阶段配置

作者: MyQuant v10.0.0 Team
创建时间: 2026-02-04
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


# ============================================================================
# 1. 数据源配置
# ============================================================================

class XtQuantConfig(BaseSettings):
    """XtQuant数据源配置"""

    enabled: bool = Field(default=False, description="启用XtQuant数据源")
    account: Optional[str] = Field(default=None, description="XtQuant账号")
    password: Optional[str] = Field(default=None, description="XtQuant密码")
    session_id: int = Field(default=1, description="会话ID（支持多实例）")
    host: str = Field(default="127.0.0.1", description="XtQuant服务器地址")
    port: int = Field(default=55505, description="XtQuant服务器端口")
    timeout: int = Field(default=10, description="连接超时时间(秒)")

    class Config:
        env_prefix = "XTQUANT_"


class PyTdxConfig(BaseSettings):
    """通达信(PyTdx)数据源配置"""

    enabled: bool = Field(default=True, description="启用通达信数据源")
    local_data_path: str = Field(
        default="E:/zd_zsone",
        description="本地通达信数据路径"
    )
    enable_remote: bool = Field(default=True, description="启用远程通达信数据")
    server: str = Field(default="119.147.212.81", description="远程服务器地址")
    port: int = Field(default=7709, description="远程服务器端口")
    timeout: int = Field(default=10, description="连接超时时间(秒)")

    class Config:
        env_prefix = "PYTDX_"


class LocalDBConfig(BaseSettings):
    """本地数据库配置"""

    enabled: bool = Field(default=True, description="启用本地数据库")
    db_path: str = Field(default="data/myquant.db", description="数据库路径")
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="最大溢出连接数")

    class Config:
        env_prefix = "LOCALDB_"


class DataSourceConfig(BaseSettings):
    """数据源统一配置"""

    # 数据源优先级（数字越小优先级越高）
    priority: Dict[str, int] = Field(
        default={
            "xtquant": 1,
            "pytdx": 2,
            "localdb": 3,
        },
        description="数据源优先级"
    )

    # 子配置
    xtquant: XtQuantConfig = Field(default_factory=XtQuantConfig)
    pytdx: PyTdxConfig = Field(default_factory=PyTdxConfig)
    localdb: LocalDBConfig = Field(default_factory=LocalDBConfig)

    # 自动切换配置
    auto_switch: bool = Field(default=True, description="数据源故障时自动切换")
    retry_times: int = Field(default=3, description="重试次数")
    health_check_interval: int = Field(default=60, description="健康检查间隔(秒)")

    class Config:
        env_prefix = "DATASOURCE_"


# ============================================================================
# 2. API配置
# ============================================================================

class FastAPIConfig(BaseSettings):
    """FastAPI服务配置"""

    app_name: str = Field(default="MyQuant_v10.0.0", description="应用名称")
    app_version: str = Field(default="10.0.0", description="应用版本")
    host: str = Field(default="0.0.0.0", description="服务器地址")
    port: int = Field(default=8002, description="服务器端口")
    workers: int = Field(default=4, description="工作进程数")
    debug: bool = Field(default=False, description="调试模式")
    reload: bool = Field(default=False, description="自动重载")

    class Config:
        env_prefix = "API_"


class CORSConfig(BaseSettings):
    """跨域配置"""

    enabled: bool = Field(default=True, description="启用CORS")
    origins: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8080"
        ],
        description="允许的源"
    )
    allow_credentials: bool = Field(default=True, description="允许携带凭证")
    allow_methods: List[str] = Field(default=["*"], description="允许的方法")
    allow_headers: List[str] = Field(default=["*"], description="允许的请求头")

    class Config:
        env_prefix = "CORS_"


class APIConfig(BaseSettings):
    """API统一配置"""

    fastapi: FastAPIConfig = Field(default_factory=FastAPIConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)

    # API文档配置
    docs_enabled: bool = Field(default=True, description="启用API文档")
    docs_url: str = Field(default="/docs", description="Swagger UI路径")
    redoc_url: str = Field(default="/redoc", description="ReDoc路径")

    # 请求限流
    rate_limit_enabled: bool = Field(default=False, description="启用请求限流")
    rate_limit_times: int = Field(default=100, description="每分钟请求次数限制")

    # 请求日志
    log_requests: bool = Field(default=True, description="记录请求日志")
    log_level: str = Field(default="INFO", description="API日志级别")

    class Config:
        env_prefix = "API_"


# ============================================================================
# 3. 缓存配置
# ============================================================================

class RedisConfig(BaseSettings):
    """Redis缓存配置"""

    enabled: bool = Field(default=False, description="启用Redis")
    host: str = Field(default="localhost", description="Redis主机")
    port: int = Field(default=6379, description="Redis端口")
    db: int = Field(default=0, description="Redis数据库编号")
    password: Optional[str] = Field(default=None, description="Redis密码")
    max_connections: int = Field(default=10, description="最大连接数")
    socket_timeout: int = Field(default=5, description="Socket超时时间")
    socket_connect_timeout: int = Field(default=5, description="连接超时时间")

    class Config:
        env_prefix = "REDIS_"


class MemoryCacheConfig(BaseSettings):
    """内存缓存配置"""

    enabled: bool = Field(default=True, description="启用内存缓存")
    max_size: int = Field(default=1000, description="最大缓存条目数")
    ttl: int = Field(default=300, description="默认过期时间(秒)")

    class Config:
        env_prefix = "MEMCACHE_"


class CacheConfig(BaseSettings):
    """缓存统一配置"""

    # 缓存策略（"redis", "memory", "both"）
    strategy: str = Field(default="memory", description="缓存策略")

    # 子配置
    redis: RedisConfig = Field(default_factory=RedisConfig)
    memory: MemoryCacheConfig = Field(default_factory=MemoryCacheConfig)

    # 缓存时间配置（秒）
    quote_ttl: int = Field(default=3, description="行情缓存时间")
    kline_ttl: int = Field(default=60, description="K线缓存时间")
    sector_ttl: int = Field(default=300, description="板块缓存时间")
    factor_ttl: int = Field(default=1800, description="因子缓存时间")

    # 缓存键前缀
    key_prefix: str = Field(default="myquant:", description="缓存键前缀")

    class Config:
        env_prefix = "CACHE_"


# ============================================================================
# 4. QLib配置
# ============================================================================

class QLibConfig(BaseSettings):
    """QLib量化框架配置"""

    # 数据路径
    provider_uri: str = Field(default="data/qlib", description="QLib数据源URI")
    region_name: str = Field(default="cn", description="QLib区域名称")
    log_level: str = Field(default="INFO", description="QLib日志级别")

    # 性能配置
    enable_cache: bool = Field(default=True, description="启用QLib缓存")
    max_threads: int = Field(default=4, description="最大线程数")

    # 数据特征
    calendars_path: Optional[str] = Field(
        default=None,
        description="自定义交易日历路径"
    )

    # 特征配置
    feature_columns: List[str] = Field(
        default=[
            "$open", "$high", "$low", "$close", "$volume", "$vwap",
            "Ref($close, 1)", "Mean($close, 5)", "Mean($close, 20)"
        ],
        description="默认特征列"
    )

    class Config:
        env_prefix = "QLIB_"


# ============================================================================
# 5. 三阶段配置
# ============================================================================

class ResearchStageConfig(BaseSettings):
    """Research阶段配置"""

    enabled: bool = Field(default=True, description="启用Research阶段")

    # 因子计算
    max_parallel_factor_calculations: int = Field(
        default=5,
        description="最大并行因子计算数"
    )
    factor_calculation_timeout: int = Field(
        default=600,
        description="因子计算超时时间(秒)"
    )

    # 数据缓存
    enable_result_cache: bool = Field(default=True, description="启用结果缓存")

    class Config:
        env_prefix = "RESEARCH_"


class ValidationStageConfig(BaseSettings):
    """Validation阶段配置"""

    enabled: bool = Field(default=True, description="启用Validation阶段")

    # 回测配置
    backtest_executor_type: str = Field(
        default="port_analysis",
        description="回测执行器类型"
    )
    backtest_start_date: str = Field(
        default="2020-01-01",
        description="默认回测开始日期"
    )
    backtest_end_date: str = Field(
        default="2023-12-31",
        description="默认回测结束日期"
    )

    # 模拟实盘
    simulation_enabled: bool = Field(default=True, description="启用模拟实盘")
    simulation_initial_capital: float = Field(
        default=1000000.0,
        description="模拟初始资金"
    )

    class Config:
        env_prefix = "VALIDATION_"


class ProductionStageConfig(BaseSettings):
    """Production阶段配置"""

    enabled: bool = Field(default=False, description="启用Production阶段")

    # 实盘交易
    trading_enabled: bool = Field(default=False, description="启用实盘交易")
    broker_type: str = Field(default="simulated", description="券商类型")

    # 仓位管理
    max_position_ratio: float = Field(
        default=0.95,
        description="最大仓位比例"
    )
    max_single_stock_ratio: float = Field(
        default=0.3,
        description="单股最大仓位比例"
    )

    # 风险控制
    stop_loss_ratio: float = Field(default=0.08, description="止损比例")
    take_profit_ratio: float = Field(default=0.15, description="止盈比例")
    max_drawdown_ratio: float = Field(default=0.20, description="最大回撤比例")

    # 交易限制
    max_orders_per_day: int = Field(default=100, description="每日最大订单数")
    trading_hours_only: bool = Field(default=True, description="仅交易时间下单")

    class Config:
        env_prefix = "PRODUCTION_"


class ThreeStageConfig(BaseSettings):
    """三阶段工作流配置"""

    research: ResearchStageConfig = Field(default_factory=ResearchStageConfig)
    validation: ValidationStageConfig = Field(default_factory=ValidationStageConfig)
    production: ProductionStageConfig = Field(default_factory=ProductionStageConfig)

    # 工作流配置
    auto_transition: bool = Field(default=False, description="自动阶段转换")
    strict_validation: bool = Field(default=True, description="严格验证模式")

    class Config:
        env_prefix = "THREESTAGE_"


# ============================================================================
# 6. 全局应用配置
# ============================================================================

class AppConfig(BaseSettings):
    """MyQuant v10.0.0 全局配置"""

    # 应用基础信息
    project_name: str = Field(default="MyQuant", description="项目名称")
    version: str = Field(default="10.0.0", description="版本号")
    environment: str = Field(default="development", description="运行环境")

    # 配置类别
    datasource: DataSourceConfig = Field(default_factory=DataSourceConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    qlib: QLibConfig = Field(default_factory=QLibConfig)
    threestage: ThreeStageConfig = Field(default_factory=ThreeStageConfig)

    # WebSocket配置
    ws_heartbeat_interval: int = Field(default=30, description="WebSocket心跳间隔(秒)")
    ws_max_connections: int = Field(default=100, description="WebSocket最大连接数")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_dir: str = Field(default="logs", description="日志目录")
    log_max_bytes: int = Field(default=10485760, description="单个日志文件最大大小(10MB)")
    log_backup_count: int = Field(default=5, description="日志备份数量")

    # 特性开关
    feature_multi_stock_monitor: bool = Field(default=True, description="多股同列监控")
    feature_sector_rotation: bool = Field(default=True, description="板块轮动")
    feature_ai_assistant: bool = Field(default=True, description="AI助手")
    feature_backtest: bool = Field(default=True, description="回测功能")
    feature_live_trading: bool = Field(default=False, description="实盘交易")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    # ========================================================================
    # 属性访问器
    # ========================================================================

    @property
    def base_dir(self) -> Path:
        """项目根目录"""
        return Path(__file__).parent.parent.parent

    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self.base_dir / "data"

    @property
    def backend_dir(self) -> Path:
        """后端目录"""
        return self.base_dir / "backend"

    @property
    def qlib_dir(self) -> Path:
        """QLib数据目录"""
        return Path(self.qlib.provider_uri)

    @property
    def log_dir_path(self) -> Path:
        """日志目录路径"""
        return self.base_dir / self.log_dir

    # ========================================================================
    # 验证方法
    # ========================================================================

    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        valid_environments = ['development', 'testing', 'staging', 'production']
        if v not in valid_environments:
            raise ValueError(f'Invalid environment: {v}. Must be one of {valid_environments}')
        return v

    @field_validator('datasource')
    @classmethod
    def validate_datasource(cls, v: DataSourceConfig) -> DataSourceConfig:
        """验证数据源配置"""
        enabled_count = sum([
            v.xtquant.enabled,
            v.pytdx.enabled,
            v.localdb.enabled
        ])
        if enabled_count == 0:
            raise ValueError('At least one data source must be enabled')
        return v


# ============================================================================
# 全局配置实例
# ============================================================================

# 创建全局配置实例
config = AppConfig()


def get_config() -> AppConfig:
    """
    获取全局配置实例

    Returns:
        AppConfig: 全局配置对象
    """
    return config


def reload_config() -> AppConfig:
    """
    重新加载配置

    Returns:
        AppConfig: 新的配置对象
    """
    global config
    config = AppConfig()
    return config


# ============================================================================
# 配置辅助函数
# ============================================================================

def is_production() -> bool:
    """判断是否为生产环境"""
    return config.environment == 'production'


def is_development() -> bool:
    """判断是否为开发环境"""
    return config.environment == 'development'


def get_data_source_priority() -> List[tuple]:
    """
    获取数据源优先级列表

    Returns:
        List[tuple]: [(source_name, priority), ...] 按优先级排序
    """
    priority_dict = config.datasource.priority
    return sorted(priority_dict.items(), key=lambda x: x[1])


def get_enabled_data_sources() -> List[str]:
    """
    获取启用的数据源列表

    Returns:
        List[str]: 启用的数据源名称列表
    """
    enabled = []
    if config.datasource.xtquant.enabled:
        enabled.append('xtquant')
    if config.datasource.pytdx.enabled:
        enabled.append('pytdx')
    if config.datasource.localdb.enabled:
        enabled.append('localdb')
    return enabled


def get_active_stage() -> str:
    """
    获取当前激活的阶段

    Returns:
        str: 'research', 'validation', 或 'production'
    """
    if config.threestage.production.enabled:
        return 'production'
    elif config.threestage.validation.enabled:
        return 'validation'
    else:
        return 'research'


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    # 全局配置
    'config',
    'get_config',
    'reload_config',

    # 配置类
    'AppConfig',

    # 数据源配置
    'DataSourceConfig',
    'XtQuantConfig',
    'PyTdxConfig',
    'LocalDBConfig',

    # API配置
    'APIConfig',
    'FastAPIConfig',
    'CORSConfig',

    # 缓存配置
    'CacheConfig',
    'RedisConfig',
    'MemoryCacheConfig',

    # QLib配置
    'QLibConfig',

    # 三阶段配置
    'ThreeStageConfig',
    'ResearchStageConfig',
    'ValidationStageConfig',
    'ProductionStageConfig',

    # 辅助函数
    'is_production',
    'is_development',
    'get_data_source_priority',
    'get_enabled_data_sources',
    'get_active_stage',
]
