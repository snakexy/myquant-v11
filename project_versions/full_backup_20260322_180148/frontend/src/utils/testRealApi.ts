/**
 * 测试真实API连接的工具函数
 */

import { getStockDetail, getStockHistory, getRealtimeData } from '../api/modules/data'

/**
 * 测试获取真实股票数据
 */
export async function testRealStockData() {
  console.log('🧪 开始测试真实API数据获取...')

  try {
    const stockCode = '000001.SZ'  // 使用完整的股票代码格式

    // 测试获取股票详情
    console.log('1. 测试获取股票详情...')
    const detailResult = await getStockDetail(stockCode)
    console.log('股票详情结果:', detailResult)

    // 测试获取历史数据 - 使用更短的时间范围
    console.log('\n2. 测试获取历史数据...')
    const endDate = '2025-12-17'
    const startDate = '2025-12-10'

    const historyResult = await getStockHistory(stockCode, {
      startDate: startDate,
      endDate: endDate,
      frequency: 'daily'
    })
    console.log('历史数据结果:', historyResult)

    // 测试获取实时数据
    console.log('\n3. 测试获取实时数据...')
    const realtimeResult = await getRealtimeData([stockCode])
    console.log('实时数据结果:', realtimeResult)

    return {
      success: true,
      stockCode,
      hasDetail: !!detailResult.data,
      hasHistory: !!historyResult.data,
      hasRealtime: !!realtimeResult.data
    }

  } catch (error: any) {
    console.error('API测试失败:', error)
    return {
      success: false,
      error: error.message,
      stockCode: '000001'
    }
  }
}

/**
 * 检查是否正在使用Mock数据
 */
export function checkMockMode() {
  const isMockMode = import.meta.env.VITE_ENABLE_MOCK === 'true'
  console.log('\n📊 当前Mock模式状态:', isMockMode ? '启用' : '禁用')

  if (isMockMode) {
    console.log('💡 提示：要使用真实API数据，请设置 VITE_ENABLE_MOCK=false')
  } else {
    console.log('✅ 已配置使用真实API数据')
  }

  return isMockMode
}

// 自动执行测试
if (import.meta.env.DEV) {
  setTimeout(async () => {
    console.log('\n=========================================')
    console.log('🔍 MyQuant API数据源验证')
    console.log('=========================================')

    checkMockMode()
    await testRealStockData()

    console.log('\n=========================================')
    console.log('✅ API验证完成')
    console.log('=========================================')
  }, 3000)
}