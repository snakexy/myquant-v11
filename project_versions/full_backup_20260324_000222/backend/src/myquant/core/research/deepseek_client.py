# -*- coding: utf-8 -*-
"""
DeepSeek API客户端
================================
职责：
- 封装DeepSeek Chat Completions API
- 支持流式响应
- 自动重试和错误处理
- Token计数

版本: v1.0
创建日期: 2026-02-11
"""

import httpx
import os
import json
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from dataclasses import dataclass, field


# ==================== 配置 ====================

@dataclass
class DeepSeekMessage:
    """聊天消息"""
    role: str
    content: str

    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content}


@dataclass
class DeepSeekResponse:
    """API响应"""
    content: str
    role: str
    finish_reason: Optional[str] = None
    usage: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "content": self.content,
            "role": self.role
        }
        if self.finish_reason:
            result["finish_reason"] = self.finish_reason
        if self.usage:
            result.update(self.usage)
        return result


@dataclass
class ChatContext:
    """对话上下文"""
    messages: List[DeepSeekMessage] = field(default_factory=list)
    max_tokens: int = 6000  # 上下文最大Token数
    total_tokens: int = 0

    def add_tokens(self, tokens: int):
        """添加Token计数"""
        self.total_tokens += tokens

    def can_add_message(self, tokens: int) -> bool:
        """检查是否可以添加消息（考虑上下文限制）"""
        return (self.total_tokens + tokens) <= self.max_tokens

    def to_list(self) -> List[Dict[str, Any]]:
        """转换为API格式"""
        return [msg.to_dict() for msg in self.messages]


class DeepSeekAPIClient:
    """
    DeepSeek API客户端

    核心功能：
    1. 流式聊天补全
    2. 自动上下文管理
    3. Token计数和限制
    4. 错误处理和重试
    """

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        """
        初始化DeepSeek API客户端

        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url

        # 配置请求头
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _create_client(self) -> httpx.AsyncClient:
        """创建HTTP客户端"""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=120.0
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.TimeoutException)
    )
    async def _make_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        stream: bool = False
    ) -> Any:
        """
        发送API请求（带重试）

        Args:
            endpoint: API端点
            payload: 请求数据
            stream: 是否流式响应

        Returns:
            API响应
        """
        client = self._create_client()
        url = f"{self.base_url}/{endpoint}"

        try:
            if stream:
                # 流式请求
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data:'):
                            json_str = line_text[5:]
                            yield json.loads(json_str)
                        else:
                            yield line_text
            else:
                # 普通请求
                response = await client.post("POST", url, json=payload, timeout=120.0)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API请求失败: {e}")
            raise

    async def chat_completions(
        self,
        messages: List[DeepSeekMessage],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> DeepSeekResponse:
        """
        聊天补全API（Chat Completions）

        Args:
            messages: 对话消息列表
            model: 模型名称
            temperature: 温度参数（0-7，越高越随机）
            max_tokens: 最大Token数
            stream: 是否流式响应

        Returns:
            DeepSeekResponse对象
        """
        logger.info(f"DeepSeek API请求: {len(messages)}条消息")

        payload = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        response = await self._make_request(
            endpoint="chat/completions",
            payload=payload,
            stream=stream
        )

        # 解析响应
        if isinstance(response, dict):
            return DeepSeekResponse(**response)
        else:
            # 流式响应
            return DeepSeekResponse(
                content="",
                role="assistant",
                finish_reason="stream"
            )

    async def chat_completions_stream(
        self,
        messages: List[DeepSeekMessage],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[Dict[str, Any]]:
        """
        流式聊天补全API

        Args:
            messages: 对话消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大Token数

        Yields:
            响应数据块
        """
        logger.info(f"DeepSeek API流式请求: {len(messages)}条消息")

        payload = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        client = self._create_client()
        url = f"{self.base_url}/chat/completions"

        try:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    line_text = line.decode('utf-8')

                    if not line_text.strip():
                        continue

                    # SSE格式：data: JSON
                    if line_text.startswith('data:'):
                        json_str = line_text[5:]
                        try:
                            json_data = json.loads(json_str)
                            yield {
                                "type": "data",
                                "data": json_data
                            }
                        except json.JSONDecodeError:
                            logger.warning(f"JSON解析失败: {json_str}")
                    else:
                        yield {
                            "type": "text",
                            "data": line_text
                        }

        except Exception as e:
            logger.error(f"DeepSeek API流式请求失败: {e}")
            raise


# ==================== 单例 ====================

_client_instance: Optional[DeepSeekAPIClient] = None


def get_deepseek_client(api_key: Optional[str] = None) -> DeepSeekAPIClient:
    """
    获取DeepSeek API客户端单例

    Args:
        api_key: API密钥（如果为None则从环境变量或配置读取）

    Returns:
        DeepSeekAPIClient实例
    """
    global _client_instance

    if _client_instance is None:
        # 优先级：环境变量 → 配置文件 → 默认值
        key = api_key or os.getenv("DEEPSEEK_API_KEY")

        if not key:
            logger.warning("⚠️ DeepSeek API密钥未配置，使用默认值（可能导致API调用失败）")
            key = "sk-placeholder"

        # 获取base_url（如果需要自定义）
        base_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")

        _client_instance = DeepSeekAPIClient(api_key=key, base_url=base_url)
        logger.info(f"✅ DeepSeek API客户端创建完成")

    return _client_instance


# ==================== 工具函数 ====================

def estimate_tokens(text: str) -> int:
    """
    估算Token数量（粗略估计：中文约2字节/token，英文约1字节/token）

    Args:
        text: 文本内容

    Returns:
        估算的Token数
    """
    # 简单估算：平均每字符1.5字节（混合中英文）
    return int(len(text) * 1.5)


async def count_tokens_async(text: str) -> int:
    """
    使用DeepSeek API计算Token数（更准确）

    Args:
        text: 文本内容

    Returns:
        Token数
    """
    client = get_deepseek_client()

    try:
        # 调用tokenizer API
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": text}]
        }

        response = await client._make_request(
            endpoint="chat/completions",
            payload=payload,
            stream=False
        )

        if response and "usage" in response:
            return response["usage"].get("total_tokens", len(text))
        else:
            # 降级到估算
            logger.warning("Token计数API失败，使用估算")
            return estimate_tokens(text)

    except Exception as e:
        logger.error(f"Token计数失败: {e}")
        return estimate_tokens(text)
