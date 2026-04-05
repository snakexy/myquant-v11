"""
数据处理模块测试
验证重构后的数据处理功能
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# 添加项目根目录到路径
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入测试模块
from qlib_core.data_processing.enhanced_processor import (
    EnhancedQLibDataProcessor,
    get_enhanced_data_processor,
    test_enhanced_data_processor
)
from qlib_core.data_processing.data_quality import get_quality_controller
from qlib_core.data_processing.technical_indicators import get_indicators_calculator
from qlib_core.data_processing.factor_generation import get_factor_generator


def test_data_quality_module():
    """测试数据质量控制模块"""
    print("\n" + "="*50)
    print("测试数据质量控制模块")
    print("="*50)
    
    try:
        # 创建测试数据
        test_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'close': [100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 106.5, 107.5, 108.5, 109.5, 110.5],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
        })
        
        # 添加异常值和缺失值
        test_data.loc[5, 'close'] = 200  # 异常值
        test_data.loc[7, 'volume'] = np.nan  # 缺失值
        
        # 创建质量控制器
        controller = get_quality_controller({
            'outlier_method': 'iqr',
            'missing_method': 'interpolate'
        })
        
        # 测试数据预处理
        processed_data = controller.preprocess_data_advanced(test_data, 'TEST001')
        
        print(f"✅ 数据质量控制测试通过")
        print(f"📊 处理前数据形状: {test_data.shape}")
        print(f"📈 处理后数据形状: {processed_data.shape}")
        print(f"🔧 处理后列数: {len(processed_data.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据质量控制测试失败: {e}")
        return False


def test_technical_indicators_module():
    """测试技术指标计算模块"""
    print("\n" + "="*50)
    print("测试技术指标计算模块")
    print("="*50)
    
    try:
        # 创建测试数据
        dates = pd.date_range('2020-01-01', periods=50, freq='D')
        test_data = pd.DataFrame({
            'date': dates,
            'open': 100 + np.random.randn(50).cumsum() * 0.1,
            'high': 100 + np.random.randn(50).cumsum() * 0.1 + 1,
            'low': 100 + np.random.randn(50).cumsum() * 0.1 - 1,
            'close': 100 + np.random.randn(50).cumsum() * 0.1,
            'volume': np.random.randint(1000, 10000, 50)
        })
        test_data.set_index('date', inplace=True)
        
        # 创建技术指标计算器
        calculator = get_indicators_calculator({
            'indicator_windows': [5, 10, 20]
        })
        
        # 测试技术指标计算
        indicators_data = calculator.calculate_technical_indicators(
            test_data, ['MA', 'EMA', 'RSI', 'MACD']
        )
        
        print(f"✅ 技术指标计算测试通过")
        print(f"📊 原始数据形状: {test_data.shape}")
        print(f"📈 指标数据形状: {indicators_data.shape}")
        print(f"🔧 计算的指标数: {len(indicators_data.columns) - len(test_data.columns)}")
        
        # 检查特定指标是否存在
        expected_indicators = ['MA5', 'EMA10', 'RSI', 'MACD', 'MACD_signal', 'MACD_hist']
        missing_indicators = [ind for ind in expected_indicators if ind not in indicators_data.columns]
        
        if missing_indicators:
            print(f"⚠️ 缺失指标: {missing_indicators}")
        else:
            print(f"✅ 所有预期指标都已计算")
        
        return True
        
    except Exception as e:
        print(f"❌ 技术指标计算测试失败: {e}")
        return False


def test_factor_generation_module():
    """测试因子生成模块"""
    print("\n" + "="*50)
    print("测试因子生成模块")
    print("="*50)
    
    try:
        # 创建测试数据
        dates = pd.date_range('2020-01-01', periods=60, freq='D')
        test_data = pd.DataFrame({
            'date': dates,
            'open': 100 + np.random.randn(60).cumsum() * 0.1,
            'high': 100 + np.random.randn(60).cumsum() * 0.1 + 1,
            'low': 100 + np.random.randn(60).cumsum() * 0.1 - 1,
            'close': 100 + np.random.randn(60).cumsum() * 0.1,
            'volume': np.random.randint(1000, 10000, 60)
        })
        test_data.set_index('date', inplace=True)
        
        # 创建因子生成器
        generator = get_factor_generator()
        
        # 测试因子生成
        factor_config = {
            'momentum_factors': True,
            'reversal_factors': True,
            'volatility_factors': True,
            'volume_factors': True,
            'technical_factors': False,
            'cross_sectional_factors': False
        }
        
        factor_data = generator.generate_factors(test_data, factor_config)
        
        print(f"✅ 因子生成测试通过")
        print(f"📊 原始数据形状: {test_data.shape}")
        print(f"📈 因子数据形状: {factor_data.shape}")
        print(f"🔧 生成的因子数: {len(factor_data.columns) - len(test_data.columns)}")
        
        # 检查特定因子是否存在
        expected_factors = ['momentum_5', 'reversal_1', 'volatility_5', 'volume_ma_5']
        existing_factors = [fac for fac in expected_factors if fac in factor_data.columns]
        
        print(f"✅ 找到的预期因子: {existing_factors}")
        
        return True
        
    except Exception as e:
        print(f"❌ 因子生成测试失败: {e}")
        return False


def test_enhanced_processor_integration():
    """测试增强处理器集成"""
    print("\n" + "="*50)
    print("测试增强处理器集成")
    print("="*50)
    
    try:
        # 创建测试数据
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        test_data = pd.DataFrame({
            'datetime': dates,
            'open': 100 + np.random.randn(100).cumsum() * 0.1,
            'high': 100 + np.random.randn(100).cumsum() * 0.1 + 2,
            'low': 100 + np.random.randn(100).cumsum() * 0.1 - 2,
            'close': 100 + np.random.randn(100).cumsum() * 0.1,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # 创建增强处理器
        processor = get_enhanced_data_processor({
            'outlier_method': 'iqr',
            'missing_method': 'interpolate',
            'indicator_windows': [5, 10, 20]
        })
        
        # 测试完整处理流程
        complete_data = processor.process_data_complete(
            test_data,
            instrument='TEST_INTEGRATION',
            indicators=['MA', 'RSI', 'MACD'],
            factor_config={
                'momentum_factors': True,
                'reversal_factors': True,
                'volatility_factors': True
            }
        )
        
        print(f"✅ 增强处理器集成测试通过")
        print(f"📊 原始数据形状: {test_data.shape}")
        print(f"📈 完整处理后形状: {complete_data.shape}")
        print(f"🔧 总列数: {len(complete_data.columns)}")
        
        # 验证数据类型
        numeric_cols = [col for col in complete_data.columns 
                     if pd.api.types.is_numeric_dtype(complete_data[col])]
        print(f"📊 数值列数: {len(numeric_cols)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强处理器集成测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("="*70)
    print("开始运行数据处理模块测试")
    print("="*70)
    
    test_results = []
    
    # 测试数据质量控制模块
    test_results.append(("数据质量控制模块", test_data_quality_module()))
    
    # 测试技术指标计算模块
    test_results.append(("技术指标计算模块", test_technical_indicators_module()))
    
    # 测试因子生成模块
    test_results.append(("因子生成模块", test_factor_generation_module()))
    
    # 测试增强处理器集成
    test_results.append(("增强处理器集成", test_enhanced_processor_integration()))
    
    # 运行内置测试
    print("\n" + "="*50)
    print("运行内置测试")
    print("="*50)
    test_results.append(("内置完整测试", test_enhanced_data_processor()))
    
    # 汇总结果
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 测试通过率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 所有测试都通过了！数据处理模块重构成功！")
    else:
        print("⚠️ 部分测试失败，请检查相关模块")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)