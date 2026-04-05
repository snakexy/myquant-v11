/**
 * 数据库管理 API
 */

import { apiRequest } from '../index'

/**
 * 扫描数据库
 * @param forceRefresh 是否强制刷新缓存
 * @param frequencies 要扫描的频率列表，如 ['daily', '1min', '5min']。
 *                   如果不指定，则扫描所有支持的频率
 */
export async function scanDatabase(forceRefresh = false, frequencies?: string[]) {
  const params: Record<string, any> = {
    force_refresh: forceRefresh
  }

  if (frequencies && frequencies.length > 0) {
    params.frequencies = frequencies.join(',')
  }

  return apiRequest.get('/database/scan', { params })
}

/**
 * 获取股票列表
 */
export async function getStockList(filters = {}) {
  return apiRequest.post('/database/stocks/list', filters)
}

/**
 * 获取股票详情
 */
export async function getStockDetail(stockCode: string) {
  return apiRequest.get(`/database/stocks/${stockCode}`)
}

/**
 * 获取更新建议
 */
export async function getUpdateSuggestions(maxAgeDays = 7) {
  return apiRequest.get('/database/update/suggestions', {
    params: { max_age_days: maxAgeDays }
  })
}

/**
 * 获取数据库健康报告
 */
export async function getHealthReport() {
  return apiRequest.get('/database/health/report')
}

/**
 * 获取统计摘要
 */
export async function getStatisticsSummary() {
  return apiRequest.get('/database/statistics/summary')
}

/**
 * 更新股票数据
 */
export async function updateStockData(stockCodes: string[], startDate?: string, endDate?: string) {
  return apiRequest.post('/database/update/stocks', {
    stock_codes: stockCodes,
    start_date: startDate,
    end_date: endDate
  })
}

/**
 * 删除股票数据
 */
export async function deleteStockData(stockCode: string) {
  return apiRequest.delete(`/database/stocks/${stockCode}`)
}

/**
 * 导出清单
 */
export async function exportInventory(outputPath?: string) {
  return apiRequest.post('/database/export/inventory', null, {
    params: { output_path: outputPath }
  })
}

/**
 * 批量检查更新状态
 */
export async function batchUpdateCheck(stockCodes?: string[]) {
  return apiRequest.post('/database/update/check', {
    stock_codes: stockCodes
  })
}
