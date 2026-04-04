# QLib工作流配置解析器

import os
import json
import yaml
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigParser:
    """
    QLib工作流配置解析器
    
    该类实现了QLib标准的配置文件解析功能，包括：
    - YAML配置文件解析
    - JSON配置文件解析
    - 配置验证和默认值处理
    - 环境变量替换
    """
    
    def __init__(self):
        """初始化配置解析器"""
        self.supported_formats = ['.yaml', '.yml', '.json']
        self.default_config = self._get_default_config()
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析配置文件
        
        Args:
            file_path: 配置文件路径
            
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
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_ext in ['.yaml', '.yml']:
                    config = yaml.safe_load(f)
                else:  # JSON
                    config = json.load(f)
                    
            # 环境变量替换
            config = self._replace_env_vars(config)
            
            # 配置验证和默认值合并
            config = self._validate_and_merge(config)
            
            logger.info(f"成功解析配置文件: {file_path}")
            return config
            
        except Exception as e:
            logger.error(f"解析配置文件失败: {file_path}, 错误: {str(e)}")
            raise ValueError(f"配置文件解析失败: {str(e)}")
    
    def parse_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析配置字典
        
        Args:
            config_dict: 配置字典
            
        Returns:
            验证和合并后的配置字典
        """
        # 环境变量替换
        config = self._replace_env_vars(config_dict)
        
        # 配置验证和默认值合并
        config = self._validate_and_merge(config)
        
        return config
    
    def _replace_env_vars(self, obj: Any) -> Any:
        """
        递归替换环境变量
        
        Args:
            obj: 要处理的对象
            
        Returns:
            替换环境变量后的对象
        """
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
    
    def _validate_and_merge(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证配置并合并默认值
        
        Args:
            config: 用户配置
            
        Returns:
            验证和合并后的配置
        """
        # 深度合并默认配置
        merged_config = self._deep_merge(self.default_config, config)
        
        # 验证必需字段
        self._validate_required_fields(merged_config)
        
        # 验证字段值
        self._validate_field_values(merged_config)
        
        return merged_config
    
    def _deep_merge(
        self,
        default: Dict[str, Any],
        user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        深度合并两个字典
        
        Args:
            default: 默认配置
            user: 用户配置
            
        Returns:
            合并后的配置
        """
        result = default.copy()
        
        for key, value in user.items():
            if (
                key in result and
                isinstance(result[key], dict) and
                isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _validate_required_fields(self, config: Dict[str, Any]):
        """
        验证必需字段
        
        Args:
            config: 配置字典
            
        Raises:
            ValueError: 缺少必需字段
        """
        required_fields = [
            'workflow',
            'data',
            'model',
            'strategy',
            'backtest'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
                
        if missing_fields:
            raise ValueError(f"缺少必需的配置字段: {missing_fields}")
    
    def _validate_field_values(self, config: Dict[str, Any]):
        """
        验证字段值
        
        Args:
            config: 配置字典
            
        Raises:
            ValueError: 字段值无效
        """
        # 验证工作流配置
        if 'workflow' in config:
            workflow = config['workflow']
            if 'name' not in workflow:
                raise ValueError("工作流配置缺少 'name' 字段")
                
        # 验证数据配置
        if 'data' in config:
            data = config['data']
            if 'start_time' not in data or 'end_time' not in data:
                raise ValueError("数据配置缺少 'start_time' 或 'end_time' 字段")
                
        # 验证模型配置
        if 'model' in config:
            model = config['model']
            if 'type' not in model:
                raise ValueError("模型配置缺少 'type' 字段")
                
        # 验证策略配置
        if 'strategy' in config:
            strategy = config['strategy']
            if 'type' not in strategy:
                raise ValueError("策略配置缺少 'type' 字段")
                
        # 验证回测配置
        if 'backtest' in config:
            backtest = config['backtest']
            if 'account' not in backtest:
                raise ValueError("回测配置缺少 'account' 字段")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "workflow": {
                "name": "qlib_workflow",
                "description": "QLib标准工作流",
                "version": "1.0.0"
            },
            "data": {
                "provider": "qlib",
                "market": "csi300",
                "start_time": "2017-01-01",
                "end_time": "2020-08-01",
                "features": ["Alpha158"],
                "instruments": "all"
            },
            "model": {
                "type": "lgb",
                "loss": "mse",
                "learning_rate": 0.1,
                "num_leaves": 31,
                "num_threads": 8
            },
            "strategy": {
                "type": "topk_dropout",
                "topk": 50,
                "n_drop": 5
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
                    "max_drawdown"
                ],
                "save_results": True,
                "output_dir": "results"
            }
        }
    
    def save_config(self, config: Dict[str, Any], file_path: str):
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            file_path: 保存路径
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的配置文件格式: {file_ext}")
            
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_ext in ['.yaml', '.yml']:
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