# -*- coding: utf-8 -*-
"""
对话上下文管理增强
================================
职责：
- 对话会话状态管理
- 上下文信息存储
- 会话切换和恢复
- 上下文相关度计算

添加到 AIAssistantService v2.0

版本: v1.0
创建日期: 2026-02-11
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from loguru import logger
from datetime import datetime


@dataclass
class ConversationMetadata:
    """对话元数据"""
    title: str  # 对话标题
    user_goal: Optional[str] = None  # 用户目标
    factor_context: List[str] = field(default_factory=list)  # 相关因子
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SessionStatus:
    """会话状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class ContextManager:
    """
    上下文管理器

    功能：
    1. 管理所有对话会话
    2. 维护对话元数据
    3. 计算上下文相关度
    4. 支持会话切换
    """

    def __init__(self):
        """初始化上下文管理器"""
        self.sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> session数据
        self.metadata: Dict[str, ConversationMetadata] = {}  # session_id -> 元数据
        self.active_session_id: Optional[str] = None  # 当前活跃会话

    def create_session(
        self,
        title: str,
        user_goal: Optional[str] = None,
        initial_context: Optional[str] = None
    ) -> str:
        """
        创建新的对话会话

        Args:
            title: 对话标题
            user_goal: 用户目标（可选）
            initial_context: 初始上下文（可选）

        Returns:
            会话ID
        """
        session_id = f"session_{datetime.now().timestamp()}"

        # 初始化会话数据
        self.sessions[session_id] = {
            "status": SessionStatus.ACTIVE,
            "created_at": datetime.now(),
            "messages": [],
            "metadata": ConversationMetadata(
                title=title,
                user_goal=user_goal
            )
        }

        # 初始化上下文
        if initial_context:
            self.sessions[session_id]["context"] = initial_context

        self.metadata[session_id] = self.sessions[session_id]["metadata"]

        # 设为活跃会话
        self.active_session_id = session_id

        logger.info(f"✅ 会话创建: {session_id} - {title}")
        return session_id

    def switch_session(self, session_id: str) -> bool:
        """
        切换到指定会话

        Args:
            session_id: 会话ID

        Returns:
            切换是否成功
        """
        if session_id not in self.sessions:
            logger.warning(f"会话不存在: {session_id}")
            return False

        self.active_session_id = session_id
        self.sessions[session_id]["status"] = SessionStatus.ACTIVE

        # 暂停之前的活跃会话
        for sid, session in self.sessions.items():
            if sid != session_id and session.get("status") == SessionStatus.ACTIVE:
                session["status"] = SessionStatus.PAUSED
                logger.info(f"会话暂停: {sid}")

        logger.info(f"✅ 切换到会话: {session_id}")
        return True

    def get_active_session(self) -> Optional[str]:
        """获取当前活跃会话ID"""
        return self.active_session_id

    def add_message_to_session(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata_update: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加消息到会话

        Args:
            session_id: 会话ID
            role: 角色（user/assistant/system）
            content: 消息内容
            metadata_update: 元数据更新

        Returns:
            是否成功
        """
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]

        # 添加消息
        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # 更新元数据
        if metadata_update:
            if "metadata" not in session:
                session["metadata"] = ConversationMetadata()
            session["metadata"].__dict__.update(metadata_update)
            self.metadata[session_id] = session["metadata"]

        logger.debug(f"消息已添加到会话 {session_id}: {role}")
        return True

    def get_session_context(self, session_id: str, max_history: int = 10) -> Dict[str, Any]:
        """
        获取会话上下文（最近N条消息）

        Args:
            session_id: 会话ID
            max_history: 历史条数限制

        Returns:
            上下文字典
        """
        if session_id not in self.sessions:
            return {
                "error": "会话不存在"
            }

        session = self.sessions[session_id]
        messages = session["messages"][-max_history:]

        # 格式化为上下文
        context = {
            "session_id": session_id,
            "status": session.get("status"),
            "title": session["metadata"].title if "metadata" in session else None,
            "user_goal": session["metadata"].user_goal if "metadata" in session else None,
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"]
                }
                for msg in messages
            ]
        }

        return context

    def calculate_context_relevance(self, session_id: str, query: str) -> float:
        """
        计算上下文相关度（简化版）

        Args:
            session_id: 会话ID
            query: 查询内容

        Returns:
            相关度分数（0-1）
        """
        if session_id not in self.sessions:
            return 0.0

        session = self.sessions[session_id]
        context_text = " ".join([msg["content"] for msg in session["messages"]])

        # 简单的关键词匹配
        query_words = set(query.lower().split())

        # 计算匹配词数
        matched_words = [word for word in query_words if word in context_text.lower()]

        if not matched_words:
            return 0.0

        # 计算相关度
        relevance = len(matched_words) / len(query_words)

        return relevance

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有会话列表

        Returns:
            会话列表
        """
        sessions_list = []

        for session_id, session in self.sessions.items():
            context = self.get_session_context(session_id)

            sessions_list.append(context)

        return {
            "sessions": sessions_list,
            "active_session": self.active_session_id,
            "total_sessions": len(self.sessions)
        }
