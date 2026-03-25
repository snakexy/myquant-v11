/**
 * 数据管理API测试脚本
 * 用于验证API返回数据而不依赖前端页面
 */

// API基础URL - 根据实际部署情况调整
const API_BASE_URL = 'http://localhost:8000/api/v1/data-management'

// 测试用的数据获取函数
async function testAPI(endpoint, description) {
  console.log(`\n=== 测试: ${description} ===`)
  console.log(`端点: ${endpoint}`)
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    
    console.log('✅ 请求成功')
    console.log('响应数据:', JSON.stringify(data, null, 2))
    
    // 验证数据结构
    if (data.success && data.data) {
      console.log('✅ 数据结构正确')
      return data.data
    } else {
      console.log('⚠️ 数据结构异常')
      return null
    }
  } catch (error) {
    console.error('❌ 请求失败:', error.message)
    return null
  }
}

// 主测试函数
async function runDataAPITests() {
  console.log('🚀 开始数据管理API测试')
  console.log(`API服务器: ${API_BASE_URL}`)
  console.log('测试时间:', new Date().toISOString())
  
  const tests = [
    {
      endpoint: '/database/stats',
      description: '数据库统计信息',
      expectedFields: ['totalStocks', 'totalRecords', 'dataSize', 'tableStats']
    },
    {
      endpoint: '/freshness/status',
      description: '数据新鲜度状态',
      expectedFields: ['overallScore', 'freshnessDetails', 'heatmapData']
    },
    {
      endpoint: '/categories/stats',
      description: '股票分类统计',
      expectedFields: ['id', 'name', 'count', 'marketCap']
    },
    {
      endpoint: '/sources/list',
      description: '数据源配置列表',
      expectedFields: ['id', 'name', 'enabled', 'status']
    },
    {
      endpoint: '/schedules/list',
      description: '数据更新计划',
      expectedFields: ['id', 'name', 'schedule', 'status']
    }
  ]
  
  const results = {}
  
  for (const test of tests) {
    const data = await testAPI(test.endpoint, test.description)
    results[test.endpoint] = {
      success: data !== null,
      data: data,
      timestamp: new Date().toISOString()
    }
    
    // 验证预期字段
    if (data && test.expectedFields) {
      const missingFields = test.expectedFields.filter(field => 
        !(field in data) && !(field in data[0]) // 检查对象或数组中的对象
      )
      if (missingFields.length > 0) {
        console.log(`⚠️ 缺少字段: ${missingFields.join(', ')}`)
      } else {
        console.log('✅ 所有必要字段都存在')
      }
    }
    
    // 添加延迟避免请求过快
    await new Promise(resolve => setTimeout(resolve, 500))
  }
  
  // 生成测试报告
  console.log('\n📊 测试报告摘要:')
  console.log('================')
  
  const successCount = Object.values(results).filter(r => r.success).length
  const totalCount = Object.keys(results).length
  
  console.log(`总测试数: ${totalCount}`)
  console.log(`成功数: ${successCount}`)
  console.log(`失败数: ${totalCount - successCount}`)
  console.log(`成功率: ${((successCount / totalCount) * 100).toFixed(1)}%`)
  
  // 检查是否为模拟数据
  console.log('\n🔍 模拟数据检测:')
  console.log('================')
  
  const dbStats = results['/database/stats']?.data
  if (dbStats) {
    const isSimulated = 
      dbStats.totalStocks === 4856 ||
      dbStats.totalRecords === '12.5M' ||
      dbStats.dataSize === '8.2GB'
    
    console.log(`数据库统计: ${isSimulated ? '❌ 模拟数据' : '✅ 真实数据'}`)
  }
  
  const freshness = results['/freshness/status']?.data
  if (freshness) {
    const isSimulated = freshness.overallScore === 94
    console.log(`数据新鲜度: ${isSimulated ? '❌ 模拟数据' : '✅ 真实数据'}`)
  }
  
  // 保存测试结果到文件（如果在Node.js环境中）
  if (typeof require !== 'undefined') {
    const fs = require('fs')
    const reportPath = './api_test_results.json'
    fs.writeFileSync(reportPath, JSON.stringify({
      testTime: new Date().toISOString(),
      apiBaseUrl: API_BASE_URL,
      results,
      summary: {
        total: totalCount,
        success: successCount,
        failed: totalCount - successCount,
        successRate: ((successCount / totalCount) * 100).toFixed(1)
      }
    }, null, 2))
    console.log(`\n📄 详细报告已保存到: ${reportPath}`)
  }
  
  return results
}

// 如果直接运行此脚本
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { runDataAPITests, testAPI }
}

// 如果在浏览器中运行
if (typeof window !== 'undefined') {
  window.runDataAPITests = runDataAPITests
  window.testAPI = testAPI
  
  // 自动运行测试
  console.log('🌐 在浏览器环境中，将在2秒后自动运行测试...')
  setTimeout(runDataAPITests, 2000)
}