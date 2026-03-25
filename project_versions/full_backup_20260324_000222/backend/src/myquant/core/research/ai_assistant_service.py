# -*- coding: utf-8 -*-
"""
Research阶段 - AI助手服务
================================
职责：
- DeepSeek API集成
- AI生成因子代码
- 因子解释和建议
- API配置管理
- 生成历史记录

版本: v1.0
创建日期: 2026-02-11
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from loguru import logger
from datetime import datetime
import uuid
import json
import hashlib
import base64
from pathlib import Path
import os
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@dataclass
class AIConfig:
    """AI配置"""
    is_configured: bool = False
    model: str = "deepseek-chat"
    api_key: str = ""
    last_tested: Optional[datetime] = None
    test_result: str = ""


@dataclass
class GeneratedFactor:
    """生成的因子"""
    factor_name: str
    expression: str
    description: str
    code: str
    suggestions: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HistoryItem:
    """历史记录项"""
    factor_id: str
    factor_name: str
    prompt: str
    expression: str
    description: str
    created_at: datetime


@dataclass
class HistoryResult:
    """历史记录结果"""
    total: int
    page: int
    page_size: int
    items: List[HistoryItem]


class AIAssistantService:
    """
    AI助手服务

    核心职责：
    1. API配置管理 - 保存和查询DeepSeek API密钥
    2. AI生成因子 - 使用AI生成因子代码和表达式
    3. 保存生成因子 - 将AI生成的因子保存到数据库
    4. 查询历史记录 - 获取因子生成历史
    """

    def __init__(self):
        """初始化AI助手服务"""
        self.config: AIConfig = AIConfig()
        self.history: List[HistoryItem] = []

        # 配置文件路径
        self.config_dir = Path(__file__).parent.parent.parent / "config" / "ai"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "deepseek_config.json"

        # 尝试从文件加载配置
        self._load_config_from_file()

        logger.info("✅ AIAssistantService初始化完成")

    # ==================== 配置文件辅助方法 ====================

    def _load_config_from_file(self):
        """从配置文件加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    encrypted_data = json.load(f)

                # 解密API密钥
                if encrypted_data.get('api_key'):
                    encrypted_data['api_key'] = self._decrypt(encrypted_data['api_key'])

                self.config = AIConfig(**encrypted_data)
                logger.info("从配置文件加载AI配置")
        except Exception as e:
            logger.warning(f"加载配置文件失败: {e}")

    def _save_config_to_file(self):
        """保存配置到文件"""
        try:
            config_data = {
                "is_configured": self.config.is_configured,
                "model": self.config.model,
                "api_key": self._encrypt(self.config.api_key) if self.config.api_key else "",
                "last_tested": self.config.last_tested.isoformat() if self.config.last_tested else None,
                "test_result": self.config.test_result
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            logger.info("配置已保存到文件")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise

    def _encrypt(self, text: str) -> str:
        """简单加密（base64 + hash）"""
        # 注意：这只是基础混淆，生产环境应使用proper加密
        encoded = base64.b64encode(text.encode()).decode()
        return encoded

    def _decrypt(self, encrypted: str) -> str:
        """解密"""
        try:
            decoded = base64.b64decode(encrypted.encode()).decode()
            return decoded
        except Exception as e:
            logger.warning(f"解密失败: {e}")
            return ""

    # ==================== API配置管理 ====================

    def save_config(self, api_key: str, model: str = "deepseek-chat") -> Dict[str, Any]:
        """
        保存API配置

        Args:
            api_key: DeepSeek API密钥
            model: 模型名称

        Returns:
            配置状态

        实现说明：
            - 当前实现：加密保存到本地配置文件
            - 未来改进：保存到数据库ai_configurations表
            - 安全措施：API密钥经过base64编码存储
        """
        logger.info("保存API配置")

        self.config = AIConfig(
            is_configured=True,
            model=model,
            api_key=api_key,
            last_tested=datetime.now(),
            test_result="configured"
        )

        # 保存到文件
        self._save_config_to_file()

        # TODO: 未来集成数据库操作
        # db.execute("""
        #     INSERT INTO ai_configurations (model, api_key_encrypted, created_at)
        #     VALUES (?, ?, ?)
        # """, (model, self._encrypt(api_key), datetime.now()))

        return {
            "status": "configured",
            "model": model,
            "message": "API密钥已保存",
            "last_tested": self.config.last_tested.isoformat()
        }

    def get_config(self) -> Dict[str, Any]:
        """
        获取API配置

        Returns:
            配置信息

        实现说明：
            - 当前实现：从内存配置对象返回（已从文件加载）
            - 未来改进：从数据库ai_configurations表查询最新配置
        """
        logger.info("获取API配置")

        # TODO: 未来集成数据库查询
        # config = db.query_one("SELECT * FROM ai_configurations ORDER BY created_at DESC LIMIT 1")

        return {
            "is_configured": self.config.is_configured,
            "model": self.config.model,
            "last_tested": self.config.last_tested.isoformat() if self.config.last_tested else None,
            "test_result": self.config.test_result,
            # 不返回API密钥本身，只返回是否配置
            "has_api_key": bool(self.config.api_key)
        }

    def test_api_connection(self) -> Dict[str, Any]:
        """
        测试API连接

        Returns:
            测试结果

        实现说明：
            - 发送简单的测试请求验证API密钥是否有效
            - 返回连接状态和响应时间
        """
        logger.info("测试DeepSeek API连接")

        if not self.config.api_key:
            return {
                "success": False,
                "message": "API密钥未配置",
                "status": "not_configured"
            }

        try:
            import time

            api_url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }

            # 发送简单的测试请求
            test_payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "user", "content": "Hi"}
                ],
                "max_tokens": 10
            }

            start_time = time.time()
            response = requests.post(
                api_url,
                headers=headers,
                json=test_payload,
                timeout=10
            )
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                # 更新配置
                self.config.last_tested = datetime.now()
                self.config.test_result = "success"
                self._save_config_to_file()

                return {
                    "success": True,
                    "message": "API连接成功",
                    "status": "connected",
                    "response_time": round(elapsed_time * 1000, 2),  # 毫秒
                    "model": self.config.model
                }
            elif response.status_code == 401:
                self.config.test_result = "invalid_key"
                self._save_config_to_file()
                return {
                    "success": False,
                    "message": "API密钥无效",
                    "status": "invalid_key"
                }
            else:
                self.config.test_result = f"error_{response.status_code}"
                self._save_config_to_file()
                return {
                    "success": False,
                    "message": f"API返回错误: {response.status_code}",
                    "status": "error"
                }

        except requests.exceptions.Timeout:
            self.config.test_result = "timeout"
            self._save_config_to_file()
            return {
                "success": False,
                "message": "API请求超时",
                "status": "timeout"
            }
        except requests.exceptions.RequestException as e:
            self.config.test_result = "connection_error"
            self._save_config_to_file()
            return {
                "success": False,
                "message": f"网络连接失败: {str(e)}",
                "status": "network_error"
            }

    # ==================== AI生成因子 ====================

    def generate_factor(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        AI生成因子

        Args:
            prompt: 提示词
            context: 上下文信息（market, frequency, etc.）

        Returns:
            生成的因子信息

        实现说明：
            - 当前实现：基于关键词的智能模板生成
            - 未来改进：调用DeepSeek API进行真实AI生成
            - DeepSeek API: https://api.deepseek.com/v1/chat/completions
        """
        logger.info(f"AI生成因子: {prompt}")

        # 检查API配置
        if not self.config.api_key:
            logger.warning("API密钥未配置，使用模板生成")
            use_real_api = False
        else:
            use_real_api = True

        try:
            if use_real_api:
                # 调用真实DeepSeek API
                generated = self._call_deepseek_api(prompt, context or {})
            else:
                # 使用智能模板生成（回退方案）
                generated = self._simulate_ai_generation(prompt, context or {})

            # 构建前端需要的响应格式
            return {
                "success": True,
                "factor_name": generated.factor_name,
                "expression": generated.expression,
                "description": generated.description,
                "code": generated.code,
                "suggestions": generated.suggestions,
                "parameters": generated.parameters,
                # 前端需要的额外字段
                "reply": self._generate_reply(prompt, generated),
                "strategy": {
                    "name": generated.factor_name,
                    "parameters": generated.parameters
                },
                "description_full": {
                    "overview": generated.description,
                    "logic": f"核心逻辑：{generated.expression}",
                    "scenarios": generated.suggestions,
                    "risk": "请注意：AI生成的因子需要经过充分回测验证后才能使用"
                }
            }

        except Exception as e:
            logger.error(f"AI生成因子失败: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
    )
    def _call_deepseek_api(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> GeneratedFactor:
        """
        调用DeepSeek API生成因子

        Args:
            prompt: 用户提示词
            context: 上下文信息

        Returns:
            生成的因子信息

        Raises:
            requests.exceptions.RequestException: API调用失败
            ValueError: API响应格式错误
        """
        logger.info("调用DeepSeek API生成因子")

        # 构建系统提示词
        system_prompt = self._build_system_prompt(context)

        # 构建请求
        api_url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}  # 要求返回JSON格式
        }

        try:
            # 发送请求
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            # 解析响应
            result = response.json()

            # 提取AI生成的内容
            if "choices" not in result or len(result["choices"]) == 0:
                raise ValueError("API返回格式错误: 无choices")

            content = result["choices"][0]["message"]["content"]

            # 解析JSON内容
            try:
                factor_data = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(f"AI返回的不是有效JSON，使用模板解析: {content[:200]}")
                # 回退到模板生成
                return self._simulate_ai_generation(prompt, context)

            # 验证必要字段
            required_fields = ["factor_name", "expression", "description", "code"]
            missing_fields = [f for f in required_fields if f not in factor_data]
            if missing_fields:
                logger.warning(f"AI返回缺少字段: {missing_fields}，使用模板生成")
                return self._simulate_ai_generation(prompt, context)

            # 构建GeneratedFactor对象
            return GeneratedFactor(
                factor_name=factor_data.get("factor_name", "ai_generated_factor"),
                expression=factor_data.get("expression", ""),
                description=factor_data.get("description", ""),
                code=factor_data.get("code", ""),
                suggestions=factor_data.get("suggestions", []),
                parameters=factor_data.get("parameters", {
                    "market": context.get("market", "A股"),
                    "frequency": context.get("frequency", "1d")
                }),
                created_at=datetime.now()
            )

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("DeepSeek API密钥无效")
                raise ValueError("API密钥无效，请检查配置") from e
            elif e.response.status_code == 429:
                logger.error("DeepSeek API请求频率超限")
                raise ValueError("API请求频率超限，请稍后再试") from e
            else:
                logger.error(f"DeepSeek API请求失败: {e}")
                raise
        except requests.exceptions.Timeout:
            logger.error("DeepSeek API请求超时")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API请求异常: {e}")
            raise

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """构建系统提示词"""
        market = context.get("market", "A股")
        frequency = context.get("frequency", "1d")

        return f"""你是一个专业的量化因子生成助手，专门为{market}市场设计因子。

你的任务是：根据用户的需求，生成有效的量化因子表达式。

返回格式必须是JSON，包含以下字段：
{{
    "factor_name": "因子名称（使用snake_case命名）",
    "expression": "因子表达式（使用QLib格式，如$close, Ref($close, 5), Mean($volume, 20)等）",
    "description": "因子描述（简要说明因子的逻辑和用途）",
    "code": "Python代码（完整的因子计算函数，使用pandas DataFrame）",
    "suggestions": ["优化建议1", "优化建议2", "优化建议3"],
    "parameters": {{"period": 周期, "market": "{market}", "frequency": "{frequency}"}}
}}

QLib表达式说明：
- $open, $high, $low, $close, $volume, $amount: 基础数据
- Ref($expr, n): 引用n期前的值
- Mean($expr, n): n期均值
- Std($expr, n): n期标准差
- Max($expr, n), Min($expr, n): n期最大/最小值
- Sum($expr, n): n期求和

注意事项：
1. 因子表达式必须使用QLib格式
2. Python代码要实用pandas DataFrame
3. 提供具体的参数值和优化建议
4. 考虑因子的经济学逻辑和实际可操作性
5. 返回的JSON必须格式正确且完整

请只返回JSON，不要包含其他说明文字。"""

    def _simulate_ai_generation(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> GeneratedFactor:
        """模拟AI生成因子"""
        # 根据提示词生成不同的因子
        if "成交量" in prompt or "volume" in prompt.lower():
            return GeneratedFactor(
                factor_name="ai_generated_volume_momentum",
                expression="$volume / Ref($volume, 5) - 1",
                description="基于5日成交量的动量因子，衡量成交量变化趋势",
                code="def calculate(df):\n    \"\"\"计算成交量动量因子\"\"\"\n    return df['volume'] / df['volume'].shift(5) - 1",
                suggestions=[
                    "建议使用10日或20日作为参数进行回测",
                    "可以考虑加入成交量波动率的调整",
                    "适用于捕捉资金流入流出的信号"
                ],
                parameters={
                    "period": 5,
                    "threshold": 0.2,
                    "market": context.get("market", "A股"),
                    "frequency": context.get("frequency", "1d")
                }
            )
        elif "均线" in prompt or "ma" in prompt.lower() or "momentum" in prompt.lower():
            return GeneratedFactor(
                factor_name="ai_generated_ma_momentum",
                expression="($close - Ref($close, 20)) / Ref($close, 20)",
                description="基于20日收盘价的动量因子",
                code="def calculate(df):\n    \"\"\"计算价格动量因子\"\"\"\n    return (df['close'] - df['close'].shift(20)) / df['close'].shift(20)",
                suggestions=[
                    "可以尝试10日、60日等不同周期",
                    "建议配合成交量指标一起使用",
                    "适合趋势明显的市场环境"
                ],
                parameters={
                    "period": 20,
                    "threshold": 0.05,
                    "market": context.get("market", "A股")
                }
            )
        elif "波动" in prompt or "volatility" in prompt.lower() or "bollinger" in prompt.lower():
            return GeneratedFactor(
                factor_name="ai_generated_volatility_factor",
                expression="Std($close, 20) / Mean($close, 20)",
                description="基于20日价格波动率的因子",
                code="def calculate(df):\n    \"\"\"计算波动率因子\"\"\"\n    return df['close'].rolling(20).std() / df['close'].rolling(20).mean()",
                suggestions=[
                    "可以结合ATR指标增强效果",
                    "高波动时降低仓位，低波动时增加仓位",
                    "适用于市场择时策略"
                ],
                parameters={
                    "period": 20,
                    "threshold": 0.03
                }
            )
        else:
            # 默认生成一个通用因子
            return GeneratedFactor(
                factor_name=f"ai_generated_{uuid.uuid4().hex[:8]}",
                expression="($close - $open) / $open",
                description="AI生成的日内收益率因子",
                code="def calculate(df):\n    \"\"\"计算日内收益率因子\"\"\"\n    return (df['close'] - df['open']) / df['open']",
                suggestions=[
                    "建议结合其他指标一起使用",
                    "可以通过调整参数优化效果",
                    "需要在不同市场环境下验证"
                ],
                parameters={
                    "market": context.get("market", "A股"),
                    "frequency": context.get("frequency", "1d")
                }
            )

    def _generate_reply(self, prompt: str, generated: GeneratedFactor) -> str:
        """生成AI回复文本"""
        return f"""根据您的要求，我已生成一个因子：

**因子名称**: {generated.factor_name}

**因子表达式**: `{generated.expression}`

**因子说明**: {generated.description}

**代码实现**:
```python
{generated.code}
```

**优化建议**:
{chr(10).join(f"- {s}" for s in generated.suggestions)}

**注意事项**:
- AI生成的因子需要经过充分回测验证
- 建议在不同市场环境下测试
- 注意因子之间的相关性，避免多重共线性

您可以：
1. 点击"保存策略"将此因子保存到数据库
2. 点击"去回测"进入回测页面验证因子效果
3. 继续提问让我优化因子或生成新因子
"""

    # ==================== 保存生成因子 ====================

    def save_factor(
        self,
        factor_name: str,
        expression: str,
        description: str,
        code: str,
        prompt: str = "",
        source: str = "ai_generated"
    ) -> Dict[str, Any]:
        """
        保存生成的因子

        Args:
            factor_name: 因子名称
            expression: 因子表达式
            description: 因子描述
            code: 因子代码
            prompt: 生成因子的提示词
            source: 来源

        Returns:
            保存结果

        实现说明：
            - 当前实现：保存到内存历史记录
            - 未来改进：保存到数据库ai_generated_factors表
        """
        logger.info(f"保存因子: {factor_name}")

        factor_id = f"ai_factor_{uuid.uuid4().hex[:8]}"

        # 添加到历史记录（内存）
        history_item = HistoryItem(
            factor_id=factor_id,
            factor_name=factor_name,
            expression=expression,
            description=description,
            prompt=prompt,
            created_at=datetime.now()
        )
        self.history.append(history_item)

        # TODO: 未来集成数据库操作
        # db.execute("""
        #     INSERT INTO ai_generated_factors
        #     (factor_id, factor_name, expression, description, code, prompt, source, created_at)
        #     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        # """, (factor_id, factor_name, expression, description, code, prompt, source, datetime.now()))

        # 同时保存到本地备份文件
        self._save_factor_backup(factor_id, {
            "factor_id": factor_id,
            "factor_name": factor_name,
            "expression": expression,
            "description": description,
            "code": code,
            "prompt": prompt,
            "source": source,
            "created_at": datetime.now().isoformat()
        })

        return {
            "factor_id": factor_id,
            "saved": True,
            "message": "因子已保存",
            "created_at": datetime.now().isoformat()
        }

    def _save_factor_backup(self, factor_id: str, factor_data: Dict[str, Any]):
        """保存因子备份到本地文件"""
        try:
            backup_dir = self.config_dir / "generated_factors"
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / f"{factor_id}.json"

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(factor_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"因子备份已保存: {backup_file}")
        except Exception as e:
            logger.warning(f"保存因子备份失败: {e}")

    # ==================== 查询历史记录 ====================

    def get_history(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> HistoryResult:
        """
        获取历史记录

        Args:
            page: 页码
            page_size: 每页数量

        Returns:
            历史记录

        实现说明：
            - 当前实现：从内存历史记录分页
            - 未来改进：从数据库ai_generated_factors表查询
        """
        logger.info(f"获取历史记录: page={page}, page_size={page_size}")

        # TODO: 未来集成数据库查询
        # results = db.query("""
        #     SELECT * FROM ai_generated_factors
        #     ORDER BY created_at DESC
        #     LIMIT ? OFFSET ?
        # """, (page_size, (page - 1) * page_size))

        # 当前使用内存数据
        total = len(self.history)
        start = (page - 1) * page_size
        end = start + page_size
        items = list(reversed(self.history))[start:end]  # 最新的在前

        return HistoryResult(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )

    # ==================== 清空历史 ====================

    def clear_history(self) -> Dict[str, Any]:
        """清空历史记录"""
        logger.info("清空历史记录")
        self.history.clear()
        return {
            "success": True,
            "message": "历史记录已清空"
        }
