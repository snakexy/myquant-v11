"""
数据库访问层 (Persistence Layer)

职责：
    - 定义数据库表结构 (models/)
    - 提供数据操作方法 (repositories/)
    - 管理数据库连接 (connection.py)

使用示例：
    from myquant.infrastructure.persistence import get_db
    from myquant.infrastructure.persistence.models import User

    db = get_db()
    user = db.query(User).filter_by(id=1).first()
"""

# 延迟导入，避免循环依赖
def get_db():
    """获取数据库会话"""
    from .connection import SessionLocal
    return SessionLocal()


__all__ = ["get_db"]
