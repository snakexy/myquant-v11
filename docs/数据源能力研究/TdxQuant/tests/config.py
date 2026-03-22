"""
TdxQuant测试配置文件
"""

# 测试股票代码（用于各项测试）
TEST_STOCKS = {
    "贵州茅台": "600519.SH",
    "中国平安": "601318.SH",
    "招商银行": "600036.SH",
    "比亚迪": "002594.SZ",
    "宁德时代": "300750.SZ"
}

# 默认测试股票
DEFAULT_STOCK = "600519.SH"

# 性能测试配置
PERFORMANCE_CONFIG = {
    "warmup_count": 3,        # 预热次数
    "test_count": 10,          # 测试次数
    "batch_size": 10,          # 批量测试数量
}

# K线数据配置
KLINE_CONFIG = {
    "periods": ["1m", "5m", "15m", "30m", "60m", "1d", "1w", "1M"],
    "default_period": "1d",
    "default_count": 100,
}

# 板块数据配置
SECTOR_CONFIG = {
    "industry": True,     # 测试行业板块
    "concept": True,      # 测试概念板块
    "region": True,       # 测试地区板块
}

# 测试结果输出配置
OUTPUT_CONFIG = {
    "save_results": True,
    "results_dir": "../test_results",
    "detailed_log": True,
}

# 数据源配置
DATASOURCE_CONFIG = {
    "type": "TdxQuant",
    "connection_timeout": 10,
    "retry_count": 3,
}
