// 简单的API测试，不依赖TypeScript
import { apiRequest } from './index'

// 测试数据库统计API
export const testDatabaseStats = async () => {
  try {
    console.log('测试数据库统计API...')
    const response = await apiRequest.get('/data-management/database/stats')
    console.log('API响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应数据:', response.data)
    return response
  } catch (error) {
    console.error('API错误:', error)
    throw error
  }
}

// 测试数据新鲜度API
export const testDataFreshness = async () => {
  try {
    console.log('测试数据新鲜度API...')
    const response = await apiRequest.get('/data-management/freshness/status')
    console.log('API响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应数据:', response.data)
    return response
  } catch (error) {
    console.error('API错误:', error)
    throw error
  }
}

// 测试股票分类API
export const testStockCategories = async () => {
  try {
    console.log('测试股票分类API...')
    const response = await apiRequest.get('/data-management/categories/stats')
    console.log('API响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应数据:', response.data)
    return response
  } catch (error) {
    console.error('API错误:', error)
    throw error
  }
}

// 测试数据源API
export const testDataSources = async () => {
  try {
    console.log('测试数据源API...')
    const response = await apiRequest.get('/data-management/sources/list')
    console.log('API响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应数据:', response.data)
    return response
  } catch (error) {
    console.error('API错误:', error)
    throw error
  }
}

// 测试更新计划API
export const testUpdateSchedules = async () => {
  try {
    console.log('测试更新计划API...')
    const response = await apiRequest.get('/data-management/schedules/list')
    console.log('API响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应数据:', response.data)
    return response
  } catch (error) {
    console.error('API错误:', error)
    throw error
  }
}