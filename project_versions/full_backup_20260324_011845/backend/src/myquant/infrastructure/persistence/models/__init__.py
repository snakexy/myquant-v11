"""
数据库模型定义

所有 SQLAlchemy ORM 模型放在这里，自动注册到 Base。

添加新模型：
    1. 创建新文件，如 user.py
    2. 在这里导入：from .user import User
"""

# 基类导入
from myquant.infrastructure.persistence.connection import Base

# 模型导入（后续添加）
# from .user import User
# from .strategy import Strategy

__all__ = ["Base"]
