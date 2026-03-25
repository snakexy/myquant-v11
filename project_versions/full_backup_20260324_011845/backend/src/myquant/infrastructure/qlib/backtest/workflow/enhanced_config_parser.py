"""
QLib增强工作流配置解析器

该模块实现了增强的配置解析功能，包括：
- 高级配置验证
- 配置模板系统
- 动态配置加载
- 配置继承和覆盖
- 环境特定配置
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ConfigValidationRule:
    """配置验证规则"""
    field_path: str
    validator: callable
    required: bool = True
    default_value: Any = None
    description: str = ""


@dataclass
class ConfigTemplate:
    """配置模板"""
    name: str
    description: str
    template: Dict[str, Any]
    validation_rules: List[ConfigValidationRule] = field(default_factory=list)


class EnhancedConfigParser:
    """
    增强配置解析器
    
    该类扩展了基础配置解析器，添加了更多高级功能：
    - 配置模板系统
    - 高级验证规则
    - 配置继承和覆盖
    - 环境特定配置
    - 动态配置加载
    """
    
    def __init__(self):
        """初始化增强配置解析器"""
        self.supported_formats = ['.yaml', '.yml', '.json']
        self.templates = self._load_templates()
        self.validation_rules = self._load_validation_rules()
        self.config_cache = {}
        
        logger.info("增强配置解析器初始化完成")
    
    def parse_file(
        self, 
        file_path: str, 
        environment: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        解析配置文件
        
        Args:
            file_path: 配置文件路径
            environment: 环境名称（dev, test, prod等）
            overrides: 配置覆盖值
            
        Returns:
            解析后的配置字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 配置格式错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的配置文件格式: {file_ext}")
        
        try:
            # 加载基础配置
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_ext in ['.yaml', '.yml']:
                    config = yaml.safe_load(f)
                else:  # JSON
                    config = json.load(f)
            
            # 应用环境特定配置
            if environment:
                config = self._apply_environment_config(
                    config, environment, file_path
                )
            
            # 应用配置覆盖
            if overrides:
                config = self._apply_overrides(config, overrides)
            
            # 环境变量替换
            config = self._replace_env_vars(config)
            
            # 配置继承处理
            config = self._process_inheritance(config, file_path)
            
            # 高级验证
            config = self._validate_config(config)
            
            # 缓存配置
            cache_key = f"{file_path}_{environment}_{hash(str(overrides))}"
            self.config_cache[cache_key] = config
            
            logger.info(f"成功解析配置文件: {file_path}")
            return config
            
        except Exception as e:
            logger.error(f"解析配置文件失败: {file_path}, 错误: {str(e)}")
            raise ValueError(f"配置文件解析失败: {str(e)}")
    
    def parse_template(
        self, 
        template_name: str,
        parameters: Dict[str, Any],
        environment: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        基于模板解析配置
        
        Args:
            template_name: 模板名称
            parameters: 模板参数
            environment: 环境名称
            overrides: 配置覆盖值
            
        Returns:
            解析后的配置字典
        """
        if template_name not in self.templates:
            raise ValueError(f"未知的配置模板: {template_name}")
        
        template = self.templates[template_name]
        
        try:
            # 应用模板参数
            config = self._apply_template_parameters(
                template.template, parameters
            )
            
            # 应用环境特定配置
            if environment:
                config = self._apply_environment_config(
                    config, environment, None
                )
            
            # 应用配置覆盖
            if overrides:
                config = self._apply_overrides(config, overrides)
            
            # 环境变量替换
            config = self._replace_env_vars(config)
            
            # 验证配置
            config = self._validate_config(config)
            
            logger.info(f"成功解析配置模板: {template_name}")
            return config
            
        except Exception as e:
            logger.error(f"解析配置模板失败: {template_name}, 错误: {str(e)}")
            raise ValueError(f"配置模板解析失败: {str(e)}")
    
    def _load_templates(self) -> Dict[str, ConfigTemplate]:
        """加载配置模板"""
        return {
            "enhanced_indexing": ConfigTemplate(
                name="enhanced_indexing",
                description="增强指数策略模板",
                template={
                    "workflow": {
                        "name": "enhanced_indexing_workflow",
                        "description": "增强指数策略工作流",
                        "version": "2.0.0"
                    },
                    "data": {
                        "provider": "qlib",
                        "market": "csi500",
                        "start_time": "2017-01-01",
                        "end_time": "2020-08-01",
                        "features": ["Alpha158"],
                        "instruments": "all",
                        "risk_model_path": "${RISK_MODEL_PATH}/riskmodel"
                    },
                    "model": {
                        "type": "lgb",
                        "loss": "mse",
                        "learning_rate": 0.1,
                        "num_leaves": 31,
                        "num_threads": 8,
                        "early_stopping_rounds": 50
                    },
                    "strategy": {
                        "type": "enhanced_indexing",
                        "riskmodel_root": "${RISK_MODEL_PATH}/riskmodel",
                        "market": "csi500",
                        "turn_limit": 0.2,
                        "extended_config": {
                            "max_tracking_error": 0.02,
                            "max_sector_deviation": 0.05,
                            "enable_risk_monitoring": True,
                            "enable_sector_constraints": True
                        }
                    },
                    "backtest": {
                        "account": 100000000,
                        "benchmark": "SH000300",
                        "exchange_kwargs": {
                            "freq": "day",
                            "limit_threshold": 0.095,
                            "deal_price": "close",
                            "open_cost": 0.0005,
                            "close_cost": 0.0015,
                            "min_cost": 5
                        }
                    },
                    "evaluation": {
                        "metrics": [
                            "annualized_return",
                            "information_ratio",
                            "max_drawdown",
                            "tracking_error",
                            "sector_exposure"
                        ],
                        "save_results": True,
                        "output_dir": "results",
                        "risk_analysis": True
                    }
                },
                validation_rules=[
                    ConfigValidationRule(
                        field_path="data.risk_model_path",
                        validator=lambda x: os.path.exists(x) if x else False,
                        required=True,
                        description="风险模型路径必须存在"
                    ),
                    ConfigValidationRule(
                        field_path="strategy.extended_config.max_tracking_error",
                        validator=lambda x: 0 < x < 1,
                        required=True,
                        default_value=0.02,
                        description="最大跟踪误差必须在0到1之间"
                    )
                ]
            ),
            "high_frequency": ConfigTemplate(
                name="high_frequency",
                description="高频交易策略模板",
                template={
                    "workflow": {
                        "name": "high_frequency_workflow",
                        "description": "高频交易策略工作流",
                        "version": "2.0.0"
                    },
                    "data": {
                        "provider": "realtime",
                        "market": "all",
                        "features": ["price_features", "volume_features"],
                        "frequency": "1min",
                        "buffer_size": 1000
                    },
                    "model": {
                        "type": "online_learning",
                        "update_frequency": "5min",
                        "lookback_window": 100
                    },
                    "strategy": {
                        "type": "market_making",
                        "spread": 0.001,
                        "inventory_limit": 1000,
                        "update_frequency": "1min"
                    },
                    "backtest": {
                        "account": 1000000,
                        "exchange_kwargs": {
                            "freq": "1min",
                            "deal_price": "vwap",
                            "open_cost": 0.0001,
                            "close_cost": 0.0001,
                            "min_cost": 1
                        }
                    }
                },
                validation_rules=[
                    ConfigValidationRule(
                        field_path="data.frequency",
                        validator=lambda x: x in [
                            "1min", "5min", "15min", "1h"
                        ],
                        required=True,
                        description="数据频率必须是支持的值"
                    )
                ]
            )
        }
    
    def _load_validation_rules(self) -> List[ConfigValidationRule]:
        """加载全局验证规则"""
        return [
            ConfigValidationRule(
                field_path="workflow.name",
                validator=lambda x: isinstance(x, str) and len(x) > 0,
                required=True,
                description="工作流名称必须是非空字符串"
            ),
            ConfigValidationRule(
                field_path="data.start_time",
                validator=lambda x: self._is_valid_date(x),
                required=True,
                description="开始时间必须是有效日期"
            ),
            ConfigValidationRule(
                field_path="data.end_time",
                validator=lambda x: self._is_valid_date(x),
                required=True,
                description="结束时间必须是有效日期"
            ),
            ConfigValidationRule(
                field_path="model.learning_rate",
                validator=lambda x: isinstance(x, (int, float)) and x > 0,
                required=True,
                default_value=0.1,
                description="学习率必须是正数"
            ),
            ConfigValidationRule(
                field_path="backtest.account",
                validator=lambda x: isinstance(x, (int, float)) and x > 0,
                required=True,
                description="账户资金必须是正数"
            )
        ]
    
    def _apply_template_parameters(
        self, 
        template: Dict[str, Any], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用模板参数"""
        import copy
        config = copy.deepcopy(template)
        
        for key, value in parameters.items():
            if '.' in key:
                # 支持嵌套键，如 "model.learning_rate"
                self._set_nested_value(config, key, value)
            else:
                config[key] = value
        
        return config
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: Any):
        """设置嵌套字典值"""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _apply_environment_config(
        self, 
        config: Dict[str, Any], 
        environment: str, 
        file_path: Optional[str]
    ) -> Dict[str, Any]:
        """应用环境特定配置"""
        # 如果有文件路径，尝试加载环境特定配置文件
        if file_path:
            env_file_path = file_path.replace(
                '.yaml', f'.{environment}.yaml'
            ).replace('.yml', f'.{environment}.yml').replace(
                '.json', f'.{environment}.json'
            )
            
            if os.path.exists(env_file_path):
                try:
                    with open(env_file_path, 'r', encoding='utf-8') as f:
                        if env_file_path.endswith(('.yaml', '.yml')):
                            env_config = yaml.safe_load(f)
                        else:
                            env_config = json.load(f)
                    
                    # 深度合并环境配置
                    config = self._deep_merge(config, env_config)
                    logger.info(f"已加载环境配置: {environment}")
                except Exception as e:
                    logger.warning(f"加载环境配置失败: {e}")
        
        return config
    
    def _apply_overrides(
        self, 
        config: Dict[str, Any], 
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用配置覆盖"""
        return self._deep_merge(config, overrides)
    
    def _process_inheritance(
        self, 
        config: Dict[str, Any], 
        file_path: str
    ) -> Dict[str, Any]:
        """处理配置继承"""
        if 'inherit_from' in config:
            parent_path = config['inherit_from']
            
            # 支持相对路径
            if not os.path.isabs(parent_path):
                parent_path = os.path.join(
                    os.path.dirname(file_path), parent_path
                )
            
            try:
                parent_config = self.parse_file(parent_path)
                # 子配置覆盖父配置
                config = self._deep_merge(parent_config, config)
                logger.info(f"已继承配置: {parent_path}")
            except Exception as e:
                logger.warning(f"继承配置失败: {e}")
        
        return config
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置"""
        errors = []
        warnings = []
        
        # 应用全局验证规则
        for rule in self.validation_rules:
            try:
                value = self._get_nested_value(config, rule.field_path)
                
                if value is None:
                    if rule.required:
                        error_msg = (
                            f"缺少必需字段: {rule.field_path} - "
                            f"{rule.description}"
                        )
                        errors.append(error_msg)
                    elif rule.default_value is not None:
                        config = self._set_nested_value_safe(
                            config, rule.field_path, rule.default_value
                        )
                        warning_msg = (
                            f"使用默认值 {rule.default_value} for {rule.field_path}"
                        )
                        warnings.append(warning_msg)
                else:
                    if not rule.validator(value):
                        error_msg = (
                            f"字段验证失败: {rule.field_path} - "
                            f"{rule.description}"
                        )
                        errors.append(error_msg)
            except Exception as e:
                error_msg = f"验证字段 {rule.field_path} 时出错: {str(e)}"
                errors.append(error_msg)
        
        # 模板特定验证
        if 'workflow' in config and 'name' in config['workflow']:
            workflow_name = config['workflow']['name']
            if workflow_name in self.templates:
                template = self.templates[workflow_name]
                for rule in template.validation_rules:
                    try:
                        value = self._get_nested_value(config, rule.field_path)
                        
                        if value is None:
                            if rule.required:
                                error_msg = (
                                    f"缺少必需字段: {rule.field_path} - "
                                    f"{rule.description}"
                                )
                                errors.append(error_msg)
                            elif rule.default_value is not None:
                                config = self._set_nested_value_safe(
                                    config, rule.field_path, rule.default_value
                                )
                        else:
                            if not rule.validator(value):
                                error_msg = (
                                    f"字段验证失败: {rule.field_path} - "
                                    f"{rule.description}"
                                )
                                errors.append(error_msg)
                    except Exception as e:
                        error_msg = f"验证字段 {rule.field_path} 时出错: {str(e)}"
                        errors.append(error_msg)
        
        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if warnings:
            warning_msg = "配置警告:\n" + "\n".join(warnings)
            logger.warning(warning_msg)
        
        return config
    
    def _get_nested_value(self, config: Dict[str, Any], path: str):
        """获取嵌套字典值"""
        keys = path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _set_nested_value_safe(
        self, 
        config: Dict[str, Any], 
        path: str, 
        value: Any
    ) -> Dict[str, Any]:
        """安全设置嵌套字典值"""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return config
    
    def _deep_merge(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """深度合并两个字典"""
        import copy
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if (
                key in result and
                isinstance(result[key], dict) and
                isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _replace_env_vars(self, obj: Any) -> Any:
        """递归替换环境变量"""
        if isinstance(obj, str):
            # 查找环境变量模式 ${VAR_NAME} 或 $VAR_NAME
            import re
            
            def replace_env_var(match):
                var_name = match.group(1) or match.group(2)
                return os.getenv(var_name, match.group(0))
            
            # 匹配 ${VAR_NAME} 和 $VAR_NAME
            pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
            return re.sub(pattern, replace_env_var, obj)
        
        elif isinstance(obj, dict):
            return {
                key: self._replace_env_vars(value)
                for key, value in obj.items()
            }
        
        elif isinstance(obj, list):
            return [self._replace_env_vars(item) for item in obj]
        
        else:
            return obj
    
    def _is_valid_date(self, date_str: str) -> bool:
        """验证日期字符串"""
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except Exception:
            return False
    
    def get_template_names(self) -> List[str]:
        """获取所有可用模板名称"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """获取模板信息"""
        if template_name not in self.templates:
            raise ValueError(f"未知的配置模板: {template_name}")
        
        template = self.templates[template_name]
        return {
            "name": template.name,
            "description": template.description,
            "validation_rules": [
                {
                    "field_path": rule.field_path,
                    "required": rule.required,
                    "default_value": rule.default_value,
                    "description": rule.description
                }
                for rule in template.validation_rules
            ]
        }
    
    def save_config(
        self, 
        config: Dict[str, Any], 
        file_path: str,
        format: str = "yaml"
    ):
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            file_path: 保存路径
            format: 文件格式 (yaml 或 json)
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if format.lower() == 'yaml':
                    yaml.dump(
                        config,
                        f,
                        default_flow_style=False,
                        allow_unicode=True
                    )
                else:  # JSON
                    json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {file_path}")
        
        except Exception as e:
            logger.error(f"保存配置文件失败: {file_path}, 错误: {str(e)}")
            raise ValueError(f"配置文件保存失败: {str(e)}")


# 导出主要类
__all__ = [
    'EnhancedConfigParser',
    'ConfigTemplate',
    'ConfigValidationRule'
]