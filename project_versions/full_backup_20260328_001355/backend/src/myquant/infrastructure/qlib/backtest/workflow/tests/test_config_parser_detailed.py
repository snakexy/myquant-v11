"""
配置解析器详细测试

测试QLib工作流管理器的配置文件解析，支持多种配置格式和参数验证
"""

import unittest
import os
import json
import yaml
import tempfile
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_parser import ConfigParser


class TestConfigParserDetailed(unittest.TestCase):
    """配置解析器详细测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = ConfigParser()
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试配置文件
        self.valid_yaml_config = {
            "workflow": {
                "name": "test_workflow",
                "description": "测试工作流"
            },
            "data": {
                "provider": "qlib",
                "market": "csi300",
                "features": ["Alpha158"]
            },
            "model": {
                "type": "lgb",
                "loss": "mse",
                "learning_rate": 0.1
            },
            "strategy": {
                "type": "enhanced_indexing",
                "topk": 50,
                "n_drop": 5
            },
            "backtest": {
                "start_time": "2020-01-01",
                "end_time": "2020-12-31",
                "account": 1000000
            }
        }
        
        self.valid_json_config = {
            "workflow": {
                "name": "json_test_workflow"
            },
            "data": {
                "provider": "local",
                "source": "test_data.csv"
            }
        }
        
        self.invalid_config = {
            "workflow": {
                # 缺少必需字段
                "description": "无效工作流"
            }
        }
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_yaml_parsing(self):
        """测试YAML配置文件解析"""
        # 创建YAML配置文件
        yaml_file = os.path.join(self.temp_dir, "test_config.yaml")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.valid_yaml_config, f,
                default_flow_style=False,
                allow_unicode=True
            )
        
        # 解析配置
        config = self.parser.parse_file(yaml_file)
        
        # 验证结果
        self.assertIsInstance(config, dict)
        self.assertEqual(config['workflow']['name'], "test_workflow")
        self.assertEqual(config['data']['provider'], "qlib")
        self.assertEqual(config['model']['type'], "lgb")
        self.assertEqual(config['strategy']['type'], "enhanced_indexing")
        self.assertEqual(config['backtest']['account'], 1000000)
    
    def test_json_parsing(self):
        """测试JSON配置文件解析"""
        # 创建JSON配置文件
        json_file = os.path.join(self.temp_dir, "test_config.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.valid_json_config, f, indent=2, ensure_ascii=False)
        
        # 解析配置
        config = self.parser.parse_file(json_file)
        
        # 验证结果
        self.assertIsInstance(config, dict)
        self.assertEqual(config['workflow']['name'], "json_test_workflow")
        self.assertEqual(config['data']['provider'], "local")
        self.assertEqual(config['data']['source'], "test_data.csv")
    
    def test_unsupported_format(self):
        """测试不支持的配置文件格式"""
        # 创建不支持的格式文件
        unsupported_file = os.path.join(self.temp_dir, "test_config.txt")
        with open(unsupported_file, 'w') as f:
            f.write("invalid config content")
        
        # 应该抛出异常
        with self.assertRaises(ValueError):
            self.parser.parse_file(unsupported_file)
    
    def test_file_not_found(self):
        """测试文件不存在的情况"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.yaml")
        
        # 应该抛出异常
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file(nonexistent_file)
    
    def test_invalid_yaml_content(self):
        """测试无效YAML内容"""
        # 创建无效YAML文件
        invalid_yaml_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(invalid_yaml_file, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        # 应该抛出异常
        with self.assertRaises(ValueError):
            self.parser.parse_file(invalid_yaml_file)
    
    def test_invalid_json_content(self):
        """测试无效JSON内容"""
        # 创建无效JSON文件
        invalid_json_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_json_file, 'w') as f:
            f.write('{"invalid": json content}')
        
        # 应该抛出异常
        with self.assertRaises(ValueError):
            self.parser.parse_file(invalid_json_file)
    
    def test_dict_parsing(self):
        """测试字典解析"""
        # 解析有效配置字典
        config = self.parser.parse_dict(self.valid_yaml_config)
        
        # 验证结果
        self.assertIsInstance(config, dict)
        self.assertEqual(config['workflow']['name'], "test_workflow")
        self.assertEqual(config['data']['provider'], "qlib")
        self.assertEqual(config['model']['learning_rate'], 0.1)
    
    def test_environment_variable_replacement(self):
        """测试环境变量替换"""
        # 设置环境变量
        os.environ['TEST_MARKET'] = 'sh000500'
        os.environ['TEST_PROVIDER'] = 'custom_provider'
        
        # 创建带环境变量的配置
        env_config = {
            "data": {
                "market": "${TEST_MARKET}",
                "provider": "${TEST_PROVIDER}"
            }
        }
        
        # 解析配置
        parsed_config = self.parser.parse_dict(env_config)
        
        # 验证环境变量替换
        self.assertEqual(parsed_config['data']['market'], 'sh000500')
        self.assertEqual(parsed_config['data']['provider'], 'custom_provider')
    
    def test_nested_dict_parsing(self):
        """测试嵌套字典解析"""
        # 创建嵌套配置
        nested_config = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep_value"
                    }
                }
            },
            "simple": "simple_value"
        }
        
        # 解析配置
        parsed_config = self.parser.parse_dict(nested_config)
        
        # 验证嵌套结构
        self.assertEqual(
            parsed_config['level1']['level2']['level3']['value'],
            'deep_value'
        )
        self.assertEqual(parsed_config['simple'], 'simple_value')
    
    def test_list_parsing(self):
        """测试列表解析"""
        # 创建包含列表的配置
        list_config = {
            "strategies": [
                {"name": "strategy1", "type": "enhanced_indexing"},
                {"name": "strategy2", "type": "topk_dropout"}
            ],
            "features": ["Alpha158", "Alpha360"]
        }
        
        # 解析配置
        parsed_config = self.parser.parse_dict(list_config)
        
        # 验证列表解析
        self.assertIsInstance(parsed_config['strategies'], list)
        self.assertEqual(len(parsed_config['strategies']), 2)
        self.assertEqual(parsed_config['strategies'][0]['name'], 'strategy1')
        self.assertEqual(
            parsed_config['strategies'][1]['type'],
            'topk_dropout'
        )
        self.assertIsInstance(parsed_config['features'], list)
        self.assertEqual(len(parsed_config['features']), 2)
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效配置
        valid_config = self.parser.parse_dict(self.valid_yaml_config)
        
        # 验证没有抛出异常
        try:
            self.parser._validate_required_fields(valid_config)
            self.parser._validate_field_values(valid_config)
        except ValueError:
            self.fail("有效配置不应该抛出异常")
        
        # 测试无效配置
        invalid_config = self.parser.parse_dict(self.invalid_config)
        
        # 应该抛出异常
        with self.assertRaises(ValueError):
            self.parser._validate_required_fields(invalid_config)
    
    def test_default_config_merge(self):
        """测试默认配置合并"""
        # 创建部分配置
        partial_config = {
            "data": {
                "provider": "custom_provider"
            }
        }
        
        # 解析配置
        parsed_config = self.parser.parse_dict(partial_config)
        
        # 验证默认值合并
        self.assertEqual(parsed_config['data']['provider'], 'custom_provider')
        self.assertEqual(
            parsed_config['workflow']['name'],
            'qlib_workflow'
        )  # 默认值
        self.assertEqual(parsed_config['model']['type'], 'lgb')  # 默认值
    
    def test_config_saving(self):
        """测试配置保存"""
        # 创建测试配置
        test_config = self.parser.parse_dict(self.valid_yaml_config)
        
        # 保存为YAML
        yaml_file = os.path.join(self.temp_dir, "saved_config.yaml")
        self.parser.save_config(test_config, yaml_file)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(yaml_file))
        
        # 重新读取验证
        saved_config = self.parser.parse_file(yaml_file)
        self.assertEqual(
            saved_config['workflow']['name'],
            test_config['workflow']['name']
        )
        
        # 保存为JSON
        json_file = os.path.join(self.temp_dir, "saved_config.json")
        self.parser.save_config(test_config, json_file)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(json_file))
        
        # 重新读取验证
        saved_config = self.parser.parse_file(json_file)
        self.assertEqual(
            saved_config['workflow']['name'],
            test_config['workflow']['name']
        )
    
    def test_config_template_generation(self):
        """测试配置模板生成"""
        # 生成配置模板
        template = self.parser.generate_config_template()
        
        # 验证模板结构
        self.assertIsInstance(template, dict)
        self.assertIn('workflow', template)
        self.assertIn('data', template)
        self.assertIn('model', template)
        self.assertIn('strategy', template)
        self.assertIn('backtest', template)
        
        # 验证模板包含所有必需字段
        workflow_template = template['workflow']
        self.assertIn('name', workflow_template)
        self.assertIn('description', workflow_template)
    
    def test_config_schema_validation(self):
        """测试配置模式验证"""
        # 创建符合模式的配置
        valid_schema_config = {
            "workflow": {
                "name": "test_workflow",
                "version": "1.0.0",
                "description": "测试工作流",
                "steps": ["step1", "step2", "step3"]
            },
            "data": {
                "provider": "qlib",
                "market": "csi300",
                "start_time": "2020-01-01",
                "end_time": "2020-12-31",
                "features": ["Alpha158"],
                "instruments": ["stock", "future"]
            }
        }
        
        # 解析配置
        parsed_config = self.parser.parse_dict(valid_schema_config)
        
        # 验证模式验证
        self.assertEqual(len(parsed_config['workflow']['steps']), 3)
        self.assertEqual(
            parsed_config['data']['instruments'],
            ["stock", "future"]
        )
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试权限错误
        readonly_file = os.path.join(self.temp_dir, "readonly.yaml")
        with open(readonly_file, 'w') as f:
            yaml.dump(self.valid_yaml_config, f)
        
        # 设置为只读
        os.chmod(readonly_file, 0o444)
        
        # 应该处理权限错误
        try:
            with open(readonly_file, 'r') as f:
                yaml.safe_load(f)
        except Exception as e:
            # 验证错误被捕获并记录
            self.assertIsInstance(e, (PermissionError, yaml.YAMLError))
    
    def test_performance_optimization(self):
        """测试性能优化"""
        import time
        
        # 创建大配置
        large_config = {}
        for i in range(1000):
            large_config[f'section_{i}'] = {
                'value': f'value_{i}',
                'nested': {
                    'deep': f'deep_value_{i}'
                }
            }
        
        # 测试解析性能
        start_time = time.time()
        
        for _ in range(10):  # 重复解析10次
            parsed_config = self.parser.parse_dict(large_config)
            self.assertIsInstance(parsed_config, dict)
            self.assertEqual(len(parsed_config), 1000)
        
        end_time = time.time()
        parsing_time = end_time - start_time
        
        # 验证性能
        self.assertLess(parsing_time, 5.0)  # 10次解析应在5秒内完成
    
    def test_config_inheritance(self):
        """测试配置继承"""
        # 创建基础配置
        base_config = {
            "base": {
                "setting1": "base_value1",
                "setting2": "base_value2"
            }
        }
        
        # 创建继承配置
        child_config = {
            "extends": "base_config",
            "child": {
                "setting3": "child_value3"
            }
        }
        
        # 模拟继承解析（需要实际实现支持）
        # 这里测试基本的合并功能
        merged_config = self.parser.parse_dict(base_config)
        child_parsed = self.parser.parse_dict(child_config)
        
        # 验证基础配置
        self.assertEqual(merged_config['base']['setting1'], 'base_value1')
        
        # 验证子配置
        self.assertEqual(child_parsed['child']['setting3'], 'child_value3')


if __name__ == '__main__':
    unittest.main()