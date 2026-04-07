/**
 * 数据管理模块 - API 调用封装
 */

import type {
  ApiResponse,
  StockDetailInfo,
  DatabaseStats,
  FilterOptions,
  TDXInfo,
  ConversionProgress,
  SectorNode,
  KlineData,
  StockPrice
} from './types'
import { API_ENDPOINTS } from './constants'
import { API_BASE_URL } from '@/config/api'
import { getBoardList, getBoardComponents, getBoardKline } from '@/api/market'

// ==================== 基础请求函数 ====================

/**
 * 发送 GET 请求
 */
async function get<T = any>(url: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
  const query = params ? '?' + new URLSearchParams(params).toString() : ''
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`
  const response = await fetch(fullUrl + query)

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

/**
 * 发送 POST 请求
 */
async function post<T = any>(url: string, body?: any): Promise<ApiResponse<T>> {
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`
  const response = await fetch(fullUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

/**
 * 发送 DELETE 请求
 */
async function del<T = any>(url: string): Promise<ApiResponse<T>> {
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`
  const response = await fetch(fullUrl, {
    method: 'DELETE'
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// ==================== 数据库管理 API ====================

/**
 * 扫描数据库
 */
export async function scanDatabase(
  forceRefresh?: boolean,
  frequencies?: string[] | string
) {
  // 确保 frequencies 是数组
  const freqArray = Array.isArray(frequencies) ? frequencies : (frequencies ? [frequencies] : undefined)
  return get<any>(API_ENDPOINTS.DATABASE_SCAN, {
    force_refresh: forceRefresh ? 'true' : 'false',
    frequencies: freqArray?.join(',')
  })
}

/**
 * 获取数据库统计信息
 */
export async function getDatabaseStats(): Promise<ApiResponse<DatabaseStats>> {
  return get<DatabaseStats>(API_ENDPOINTS.DATABASE_STATS)
}

/**
 * 获取股票列表
 */
export async function getStockList(filters?: FilterOptions, page = 1, pageSize = 50) {
  return get(API_ENDPOINTS.STOCK_LIST, {
    ...filters,
    page,
    pageSize
  })
}

/**
 * 获取股票详情
 */
export async function getStockDetail(code: string): Promise<ApiResponse<StockDetailInfo>> {
  return get<StockDetailInfo>(`${API_ENDPOINTS.STOCK_DETAIL}/${code}`)
}

/**
 * 更新股票数据
 */
export async function updateStockData(
  stockCodes: string[],
  startDate?: string,
  endDate?: string
) {
  return post(API_ENDPOINTS.STOCK_UPDATE, {
    stock_codes: stockCodes,
    start_date: startDate,
    end_date: endDate
  })
}

/**
 * 删除股票数据
 */
export async function deleteStockData(code: string, frequency?: string) {
  const url = frequency
    ? `${API_ENDPOINTS.STOCK_DELETE}/${code}?frequency=${frequency}`
    : `${API_ENDPOINTS.STOCK_DELETE}/${code}`

  return del(url)
}

// ==================== 数据源管理 API ====================

/**
 * 获取数据源列表
 */
export async function getDataSources() {
  return get(API_ENDPOINTS.DATA_SOURCES)
}

/**
 * 测试数据源连接
 */
export async function testConnection(sourceId: string) {
  return post(`${API_ENDPOINTS.TEST_CONNECTION}/${sourceId}/test`)
}

/**
 * 检测通达信数据
 */
export async function detectTDX(tdxPath: string): Promise<ApiResponse<TDXInfo>> {
  return post<TDXInfo>(API_ENDPOINTS.TDX_DETECT, { tdx_path: tdxPath })
}

/**
 * 开始转换数据
 */
export async function startConversion(
  tdxPath: string,
  frequencies: string[],
  options: {
    forwardFill: boolean
    handleOutliers: boolean
    normalize: boolean
  }
) {
  return post<{ taskId: string }>(API_ENDPOINTS.TDX_CONVERT, {
    tdx_path: tdxPath,
    frequencies,
    options
  })
}

/**
 * 获取转换进度
 */
export async function getConversionProgress(taskId: string): Promise<ApiResponse<ConversionProgress>> {
  return get<ConversionProgress>(`/api/data-management/convert/${taskId}/progress`)
}

// ==================== 板块管理 API ====================

/**
 * @deprecated ⚠️ 请使用 getBoardList 替代
 * 获取板块列表
 *
 * @see 从 @/api/market 导入 getBoardList
 * @example
 * import { getBoardList } from '@/api/market'
 * const boards = await getBoardList('一级行业', true)
 */
export async function fetchSectorList(): Promise<ApiResponse<any>> {
  // 使用静态导入的 getBoardList
  try {
    return await getBoardList()
  } catch (error) {
    console.warn('建议使用 @/api/market 的 getBoardList 替代 fetchSectorList')
    return get<any>('/sector/list')
  }
}

/**
 * 获取板块成分股列表
 *
 * @see 从 @/api/market 导入 getBoardComponents
 * @example
 * import { getBoardComponents } from '@/api/market'
 * const components = await getBoardComponents('880001', 50)
 */
export async function fetchSectorStocks(
  sectorName: string
): Promise<ApiResponse<any>> {
  // 使用静态导入的 getBoardComponents
  try {
    return await getBoardComponents(sectorName, 100)
  } catch (error) {
    return post<any>('/sector/stocks', {
      sector_name: sectorName
    })
  }
}

/**
 * 获取板块基本信息
 */
export async function fetchSectorInfo(
  sectorName: string
): Promise<ApiResponse<any>> {
  return get<any>('/sector/info', {
    sector_name: sectorName
  })
}

/**
 * 获取板块树
 */
export async function getSectorTree(category: string): Promise<ApiResponse<SectorNode[]>> {
  return get<SectorNode[]>(`${API_ENDPOINTS.SECTORS}/${category}`)
}

/**
 * 获取板块股票列表
 */
export async function getSectorStocks(sectorId: string): Promise<ApiResponse<string[]>> {
  return get<string[]>(`${API_ENDPOINTS.SECTOR_STOCKS}/${sectorId}`)
}

/**
 * 批量获取股票信息
 */
export async function getStocksInfo(stockCodes: string[]): Promise<ApiResponse<any[]>> {
  return post('/api/data-management/stocks/info', { stock_codes: stockCodes })
}

// ==================== 股票详情 API ====================

/**
 * 获取股票价格
 */
export async function getStockPrice(code: string): Promise<ApiResponse<StockPrice>> {
  return get<StockPrice>(`/api/market/stock/${code}/price`)
}

/**
 * @deprecated ⚠️ 请使用 getBoardKline 替代（针对板块指数）
 * 获取 K 线数据
 *
 * @notice 支持8开头的板块代码
 * @example
 * // 板块指数K线（推荐）
 * import { getBoardKline } from '@/api/market'
 * const kline = await getBoardKline('880001', '2024-01-01', '2024-12-31', 100)
 *
 * // 股票K线（需要后端实现新端点）
 * // 目前仍使用旧版API
 */
export async function getKlineData(
  code: string,
  period: string,
  startDate?: string,
  endDate?: string
): Promise<ApiResponse<KlineData[]>> {
  // 检测是否为板块代码（8开头）
  if (code.startsWith('8')) {
    try {
      // 使用静态导入的 getBoardKline
      const response = await getBoardKline(code, startDate, endDate, 500)

      // 转换返回格式
      if (response && response.data) {
        const klineData: KlineData[] = response.data.map((item: any) => ({
          timestamp: new Date(item.date).getTime(),
          date: item.date,
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
          volume: item.volume
        }))

        return {
          code: 200,
          message: 'success',
          data: klineData
        }
      }
    } catch (error) {
      console.warn('板块K线获取失败，尝试使用旧版API:', error)
    }
  }

  // 使用旧版API（股票数据或降级方案）
  return get<KlineData[]>(`/api/market/stock/${code}/kline`, {
    period,
    start_date: startDate,
    end_date: endDate
  })
}

/**
 * 获取股票统计数据
 */
export async function getStockStats(code: string): Promise<ApiResponse<any>> {
  return get(`/api/database/stocks/${code}/stats`)
}

// ==================== 统一数据中枢实时行情 API ====================

/**
 * 获取QMT实时行情
 * @param symbols 股票代码列表 (如: ['600000', '000001'])
 */
export async function getQMTRealtimeQuote(symbols: string[]): Promise<ApiResponse<any>> {
  return post('/qmt-realtime/get_realtime_quote', {
    symbols
  })
}

/**
 * 获取板块成分股的实时行情（通过统一数据中枢）
 * 优先级: QMT > mootdx
 * @param stockCodes 股票代码列表 (QLib格式: ['sh600000', 'sz000001'])
 */
export async function getSectorStocksRealtime(stockCodes: string[]): Promise<ApiResponse<any>> {
  // 将QLib格式转换为纯数字格式 (sh600000 -> 600000)
  const qmtCodes = stockCodes.map(code => {
    if (code.startsWith('sh') || code.startsWith('sz') || code.startsWith('bj')) {
      return code.substring(2)
    }
    return code
  })

  // 数据源列表（按优先级排序）
  const dataSources = [
    { name: 'QMT', fetcher: () => getQMTRealtimeQuote(qmtCodes) },
    { name: 'mootdx', fetcher: () => getMootdxRealtimeQuote(qmtCodes) }
  ]

  // 依次尝试各个数据源
  for (const source of dataSources) {
    try {
      const response = await source.fetcher() as ApiResponse<any>
      // 检查响应是否成功 (code === 200 表示成功)
      if (response && response.code === 200 && response.data) {
        console.log(`✅ 使用 ${source.name} 数据源获取实时行情成功`)
        return response
      }
    } catch (error: any) {
      console.warn(`⚠️ ${source.name} 数据源获取失败:`, error?.message || error)
      continue
    }
  }

  // 所有数据源都失败
  console.error('❌ 所有实时行情数据源均不可用')
  return {
    code: 503,
    message: '无法获取实时行情，请确保QMT或mootdx数据源可用',
    data: null
  }
}

/**
 * 获取mootdx实时行情（降级数据源）
 * @param symbols 股票代码列表
 */
export async function getMootdxRealtimeQuote(symbols: string[]): Promise<ApiResponse<any>> {
  // 通过统一数据中枢获取mootdx实时行情
  return post('/unified_data/realtime/quote', {
    symbols
  })
}

// ==================== 导出 API ====================

/**
 * 导出数据
 */
export async function exportData(
  types: string[],
  format: string,
  timeRange: string,
  customDateRange?: { start: string; end: string }
) {
  return post(API_ENDPOINTS.EXPORT, {
    types,
    format,
    time_range: timeRange,
    custom_date_range: customDateRange
  })
}

// ==================== 工具函数 ====================

/**
 * 处理 API 错误
 */
export function handleApiError(error: any): string {
  if (error.response) {
    return error.response.data?.message || '请求失败'
  }
  if (error.request) {
    return '网络错误，请检查连接'
  }
  return error.message || '未知错误'
}

/**
 * 显示成功消息
 */
export function showSuccessMessage(message: string): void {
  // 可以集成 Element Plus 的 ElMessage
  console.log('Success:', message)
}

/**
 * 显示错误消息
 */
export function showErrorMessage(message: string): void {
  // 可以集成 Element Plus 的 ElMessage
  console.error('Error:', message)
}
