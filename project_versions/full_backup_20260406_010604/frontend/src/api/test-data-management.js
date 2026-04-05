// 简单的API测试脚本
import { 
  getDatabaseStats, 
  getDataFreshness, 
  getStockCategories, 
  getDataSources,
  getUpdateSchedules
} from './dataManagement.js'

// 测试所有API调用
const testAllAPIs = async () => {
  console.log('开始测试数据管理API...')
  
  try {
    console.log('\n1. 测试数据库统计API')
    const dbStats = await getDatabaseStats()
    console.log('数据库统计结果:', dbStats)
    
    console.log('\n2. 测试数据新鲜度API')
    const freshness = await getDataFreshness()
    console.log('数据新鲜度结果:', freshness)
    
    console.log('\n3. 测试股票分类API')
    const categories = await getStockCategories()
    console.log('股票分类结果:', categories)
    
    console.log('\n4. 测试数据源配置API')
    const sources = await getDataSources()
    console.log('数据源配置结果:', sources)
    
    console.log('\n5. 测试更新计划API')
    const schedules = await getUpdateSchedules()
    console.log('更新计划结果:', schedules)
    
    console.log('\n✅ 所有API测试完成')
  } catch (error) {
    console.error('❌ API测试失败:', error)
  }
}

// 导出测试函数
export { testAllAPIs }

// 如果直接运行此文件，执行测试
if (typeof window !== 'undefined') {
  // 浏览器环境
  window.testDataManagementAPI = testAllAPIs
  console.log('在浏览器控制台中运行 testDataManagementAPI() 来测试API')
} else {
  // Node.js环境
  testAllAPIs()
}