"""
模型工作流模块测试

测试模型注册、管道管理、工作流管理和版本控制功能
"""

import unittest
import tempfile
import os
import shutil
from datetime import datetime

from .model_registry import ModelRegistry, ModelMetadata
from .model_pipeline import ModelPipeline, PipelineStep
from .workflow_manager import WorkflowManager, WorkflowStatus
from .version_control import ModelVersionControl, VersionStatus


class TestModelRegistry(unittest.TestCase):
    """测试模型注册表"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = ModelRegistry(
            registry_path=os.path.join(self.temp_dir, "registry.json")
        )

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_register_model_class(self):
        """测试注册模型类"""
        class TestModel:
            pass

        self.registry.register_model_class(
            "test_model", TestModel, "测试模型"
        )

        model_class = self.registry.get_model_class("test_model")
        self.assertEqual(model_class, TestModel)

    def test_register_model_instance(self):
        """测试注册模型实例"""
        class TestModel:
            def __init__(self):
                self.coef_ = [1.0, 2.0]
                self.intercept_ = 0.5

        model = TestModel()
        self.registry.register_model_instance(
            "test_model", "1.0", model,
            description="测试模型实例",
            author="test_author",
            tags=["test"],
            hyperparameters={"learning_rate": 0.01},
            performance_metrics={"accuracy": 0.85}
        )

        metadata = self.registry.get_model_metadata("test_model", "1.0")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.name, "test_model")
        self.assertEqual(metadata.version, "1.0")
        self.assertEqual(metadata.author, "test_author")
        self.assertEqual(metadata.tags, ["test"])

    def test_list_models(self):
        """测试列出模型"""
        class TestModel:
            def __init__(self):
                self.coef_ = [1.0, 2.0]
                self.intercept_ = 0.5

        model = TestModel()
        self.registry.register_model_instance(
            "test_model", "1.0", model,
            tags=["test"]
        )

        models = self.registry.list_models()
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]["name"], "test_model")
        self.assertEqual(models[0]["version"], "1.0")


class TestModelPipeline(unittest.TestCase):
    """测试模型管道"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = ModelRegistry(
            registry_path=os.path.join(self.temp_dir, "registry.json")
        )
        self.pipeline = ModelPipeline(
            self.registry,
            pipeline_dir=self.temp_dir
        )

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_pipeline(self):
        """测试创建管道"""
        self.pipeline.create_pipeline(
            "test_pipeline",
            description="测试管道",
            steps=[
                PipelineStep.DATA_PREPARATION.value,
                PipelineStep.MODEL_TRAINING.value,
                PipelineStep.MODEL_VALIDATION.value
            ],
            parameters={"model_type": "LinearRegression"}
        )

        config = self.pipeline.get_pipeline("test_pipeline")
        self.assertIsNotNone(config)
        self.assertEqual(config.name, "test_pipeline")
        self.assertEqual(len(config.steps), 3)
        self.assertEqual(config.parameters["model_type"], "LinearRegression")

    def test_execute_pipeline(self):
        """测试执行管道"""
        self.pipeline.create_pipeline(
            "test_pipeline",
            steps=[
                PipelineStep.DATA_PREPARATION.value,
                PipelineStep.MODEL_TRAINING.value,
                PipelineStep.MODEL_VALIDATION.value
            ]
        )

        result = self.pipeline.execute_pipeline("test_pipeline")

        self.assertIsNotNone(result)
        self.assertEqual(result.pipeline_name, "test_pipeline")
        self.assertIn("data_preparation", result.steps_results)
        self.assertIn("model_training", result.steps_results)
        self.assertIn("model_validation", result.steps_results)

    def test_list_pipelines(self):
        """测试列出管道"""
        self.pipeline.create_pipeline("test_pipeline1")
        self.pipeline.create_pipeline("test_pipeline2")

        pipelines = self.pipeline.list_pipelines()
        self.assertEqual(len(pipelines), 2)

        names = [p["name"] for p in pipelines]
        self.assertIn("test_pipeline1", names)
        self.assertIn("test_pipeline2", names)


class TestWorkflowManager(unittest.TestCase):
    """测试工作流管理器"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = ModelRegistry(
            registry_path=os.path.join(self.temp_dir, "registry.json")
        )
        self.pipeline = ModelPipeline(
            self.registry,
            pipeline_dir=self.temp_dir
        )
        self.manager = WorkflowManager(
            self.registry,
            self.pipeline,
            workflow_dir=self.temp_dir
        )

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_workflow(self):
        """测试创建工作流"""
        tasks = [
            {
                "name": "数据准备",
                "type": "data_processing",
                "parameters": {"source": "test_data.csv"}
            },
            {
                "name": "模型训练",
                "type": "model_training",
                "parameters": {"model_type": "LinearRegression"},
                "dependencies": ["数据准备"]
            },
            {
                "name": "模型评估",
                "type": "model_evaluation",
                "parameters": {"test_data": "test.csv"},
                "dependencies": ["模型训练"]
            }
        ]

        workflow_id = self.manager.create_workflow(
            "test_workflow",
            description="测试工作流",
            tasks=tasks
        )

        self.assertIsNotNone(workflow_id)
        self.assertTrue(workflow_id.startswith("workflow_"))

        workflow = self.manager.get_workflow(workflow_id)
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(len(workflow.tasks), 3)

    def test_execute_workflow(self):
        """测试执行工作流"""
        tasks = [
            {
                "name": "数据处理",
                "type": "data_processing",
                "parameters": {"source": "test_data.csv"}
            },
            {
                "name": "模型训练",
                "type": "model_training",
                "parameters": {"model_name": "test_model"},
                "dependencies": ["数据处理"]
            }
        ]

        workflow_id = self.manager.create_workflow(
            "test_workflow",
            tasks=tasks
        )

        # 执行工作流
        success = self.manager.execute_workflow(workflow_id)
        self.assertTrue(success)

        # 等待执行完成
        import time
        time.sleep(2)

        workflow = self.manager.get_workflow(workflow_id)
        self.assertIn(workflow.status, [
            WorkflowStatus.COMPLETED.value,
            WorkflowStatus.FAILED.value
        ])

    def test_list_workflows(self):
        """测试列出工作流"""
        self.manager.create_workflow("test_workflow1")
        self.manager.create_workflow("test_workflow2")

        workflows = self.manager.list_workflows()
        self.assertEqual(len(workflows), 2)

        names = [w["name"] for w in workflows]
        self.assertIn("test_workflow1", names)
        self.assertIn("test_workflow2", names)


class TestModelVersionControl(unittest.TestCase):
    """测试模型版本控制"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.version_control = ModelVersionControl(
            registry_path=os.path.join(self.temp_dir, "versions"),
            storage_path=os.path.join(self.temp_dir, "storage")
        )

        # 创建测试模型元数据
        self.test_metadata = ModelMetadata(
            name="test_model",
            version="1.0",
            description="测试模型",
            model_type="TestModel",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author="test_author",
            tags=["test"],
            hyperparameters={"learning_rate": 0.01},
            performance_metrics={"accuracy": 0.85},
            file_path=os.path.join(self.temp_dir, "test_model.pkl"),
            dependencies=[]
        )

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_version(self):
        """测试创建版本"""
        # 创建测试模型文件
        model_file = os.path.join(self.temp_dir, "test_model.pkl")
        with open(model_file, 'w') as f:
            f.write("test_model_data")

        success = self.version_control.create_version(
            "test_model",
            "1.0",
            self.test_metadata,
            changelog="初始版本",
            tags=["initial"],
            status=VersionStatus.DEVELOPMENT.value
        )

        self.assertTrue(success)

        version_info = self.version_control.get_version_info(
            "test_model", "1.0")
        self.assertIsNotNone(version_info)
        self.assertEqual(version_info.version, "1.0")
        self.assertEqual(version_info.status, VersionStatus.DEVELOPMENT.value)
        self.assertEqual(version_info.changelog, "初始版本")

    def test_list_versions(self):
        """测试列出版本"""
        # 创建测试模型文件
        model_file = os.path.join(self.temp_dir, "test_model.pkl")
        with open(model_file, 'w') as f:
            f.write("test_model_data")

        # 创建多个版本
        self.version_control.create_version(
            "test_model", "1.0", self.test_metadata)
        self.version_control.create_version(
            "test_model", "1.1", self.test_metadata)
        self.version_control.create_version(
            "test_model", "2.0", self.test_metadata)

        versions = self.version_control.list_versions("test_model")
        self.assertEqual(len(versions), 3)

        version_numbers = [v["version"] for v in versions]
        self.assertIn("1.0", version_numbers)
        self.assertIn("1.1", version_numbers)
        self.assertIn("2.0", version_numbers)

    def test_compare_versions(self):
        """测试版本比较"""
        # 创建测试模型文件
        model_file = os.path.join(self.temp_dir, "test_model.pkl")
        with open(model_file, 'w') as f:
            f.write("test_model_data")

        # 创建两个版本
        metadata1 = ModelMetadata(
            name="test_model",
            version="1.0",
            description="测试模型1",
            model_type="TestModel",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author="test_author",
            tags=["test"],
            hyperparameters={"learning_rate": 0.01},
            performance_metrics={"accuracy": 0.85},
            file_path=model_file,
            dependencies=[]
        )

        metadata2 = ModelMetadata(
            name="test_model",
            version="1.1",
            description="测试模型2",
            model_type="TestModel",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author="test_author",
            tags=["test"],
            hyperparameters={"learning_rate": 0.02},
            performance_metrics={"accuracy": 0.87},
            file_path=model_file,
            dependencies=[]
        )

        self.version_control.create_version("test_model", "1.0", metadata1)
        self.version_control.create_version("test_model", "1.1", metadata2)

        comparison = self.version_control.compare_versions(
            "test_model", "1.0", "1.1"
        )

        self.assertIsNotNone(comparison)
        self.assertEqual(comparison.version1, "1.0")
        self.assertEqual(comparison.version2, "1.1")
        self.assertIn("accuracy", comparison.performance_diff)
        self.assertIn("learning_rate", comparison.parameter_diff)

    def test_update_version_status(self):
        """测试更新版本状态"""
        # 创建测试模型文件
        model_file = os.path.join(self.temp_dir, "test_model.pkl")
        with open(model_file, 'w') as f:
            f.write("test_model_data")

        self.version_control.create_version(
            "test_model", "1.0", self.test_metadata)

        success = self.version_control.update_version_status(
            "test_model", "1.0", VersionStatus.PRODUCTION.value
        )

        self.assertTrue(success)

        version_info = self.version_control.get_version_info(
            "test_model", "1.0")
        self.assertEqual(version_info.status, VersionStatus.PRODUCTION.value)


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)
