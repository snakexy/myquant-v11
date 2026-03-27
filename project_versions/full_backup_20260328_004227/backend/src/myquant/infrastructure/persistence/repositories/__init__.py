"""
数据仓库模式

提供各类实体的数据操作方法，隔离业务层和数据库细节。

使用示例：
    from myquant.infrastructure.persistence.repositories import UserRepository

    repo = UserRepository(db)
    user = repo.get_by_id(1)
    users = repo.get_all()
"""

# 后续添加：
# from .user_repository import UserRepository

__all__ = []
