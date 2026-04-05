"""
数据库连接管理

配置来源：config/settings.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from myquant.config.settings import DATABASE_URL

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,  # 设为 True 可查看 SQL 语句
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()


def get_db():
    """获取数据库会话（用于 FastAPI 依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    # 导入所有模型以确保注册
    from . import models
    Base.metadata.create_all(bind=engine)
