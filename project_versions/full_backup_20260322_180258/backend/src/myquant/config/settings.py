"""
MyQuant v11 配置

数据目录结构：
    MyQuant_v11/
    ├── data/
    │   ├── cache/      ← 运行时缓存
    │   ├── db/         ← SQLite数据库
    │   ├── qlib/       ← Qlib数据
    │   ├── tdx/        ← 通达信数据
    │   └── logs/       ← 日志文件
    └── ...
"""

from pathlib import Path

# 项目根目录 (MyQuant_v11/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
DB_DIR = DATA_DIR / "db"
QLIB_DIR = DATA_DIR / "qlib"
TDX_DIR = DATA_DIR / "tdx"
LOGS_DIR = DATA_DIR / "logs"

# 确保目录存在
for d in [DATA_DIR, CACHE_DIR, DB_DIR, QLIB_DIR, TDX_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 数据库配置
DATABASE_URL = f"sqlite:///{DB_DIR}/myquant.db"

# Qlib配置
QLIB_DATA_PATH = str(QLIB_DIR)

# 通达信配置
TDX_DATA_PATH = str(TDX_DIR)

# 日志配置
LOG_PATH = str(LOGS_DIR)

# API配置
API_HOST = "0.0.0.0"
API_PORT = 8000
API_PREFIX = "/api"

# CORS配置
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
]
