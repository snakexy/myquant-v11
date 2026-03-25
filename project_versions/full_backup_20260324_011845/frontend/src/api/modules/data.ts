import { apiRequest } from '../index'

// 数据相关API接口
// 修复说明：
// 1. 使用正确的后端API端点
// 2. 端口从8004改为8001
// 3. 使用统一数据API路径 /unified_data/ 和 /data/

// 获取股票列表 - 暂不支持，返回空列表
export const getStockList = async (params?: {
  page?: number
  size?: number
  market?: string
  sector?: string
}) => {
  // 开发环境且启用Mock时使用Mock数据
  if (import.meta.env.DEV && import.meta.env.VITE_ENABLE_MOCK === 'true') {
    const { mockService } = await import('../mockService')
    return mockService.getStockList(params)
  }

  // 当前后端暂不支持股票列表API，返回空列表
  return {
    success: true,
    data: {
      stocks: [],
      total: 0,
      page: params?.page || 1,
      size: params?.size || 10
    },
    message: '股票列表功能暂未实现'
  }
}

// 获取股票详情 - 使用统一数据API
export const getStockDetail = async (code: string) => {
  // 开发环境且启用Mock时使用Mock数据
  if (import.meta.env.DEV && import.meta.env.VITE_ENABLE_MOCK === 'true') {
    const { mockService } = await import('../mockService')
    return mockService.getStockDetail(code)
  }

  try {
    // 确保股票代码格式正确
    let formattedCode = code
    if (!code.endsWith('.SZ') && !code.endsWith('.SH')) {
      if (code.startsWith('6')) {
        formattedCode = `${code}.SH`
      } else {
        formattedCode = `${code}.SZ`
      }
    }

    // 使用统一数据API获取最新一天的数据作为详情
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

    const response = await apiRequest.get(`/unified_data/stock/${formattedCode}`, {
      params: {
        start_date: startDate,
        end_date: endDate,
        frequency: 'day',
        format: 'dataframe',
        forward_adjust: false
      }
    })

    if (response.success && response.data && !response.data.empty) {
      // 从返回的数据中提取最新的股票信息
      const dates = response.data.dates || []
      const values = response.data.values || []
      const columns = response.data.columns || []

      if (dates.length > 0 && values.length > 0) {
        const lastIndex = values.length - 1
        const latestRow = values[lastIndex]

        // 找到各列的索引
        const openIdx = columns.indexOf('open')
        const highIdx = columns.indexOf('high')
        const lowIdx = columns.indexOf('low')
        const closeIdx = columns.indexOf('close')
        const volumeIdx = columns.indexOf('volume')

        return {
          success: true,
          data: {
            code: formattedCode,
            name: formattedCode, // 后端暂未返回名称
            market: formattedCode.endsWith('.SH') ? 'SH' : 'SZ',
            sector: '未知',
            industry: '未知',
            currentPrice: closeIdx >= 0 ? latestRow[closeIdx] : 0,
            changePercent: 0, // 需要计算
            open: openIdx >= 0 ? latestRow[openIdx] : 0,
            high: highIdx >= 0 ? latestRow[highIdx] : 0,
            low: lowIdx >= 0 ? latestRow[lowIdx] : 0,
            close: closeIdx >= 0 ? latestRow[closeIdx] : 0,
            volume: volumeIdx >= 0 ? latestRow[volumeIdx] : 0,
            date: dates[lastIndex],
            lastUpdate: new Date().toISOString()
          }
        }
      }
    }

    return {
      success: false,
      message: '无法获取股票详情',
      data: null
    }
  } catch (error) {
    return {
      success: false,
      message: '获取股票详情失败',
      data: null
    }
  }
}

// 获取股票历史数据 - 使用统一数据API
export const getStockHistory = async (code: string, params: {
  startDate: string
  endDate: string
  frequency: 'daily' | 'weekly' | 'monthly'
}, timeout?: number) => {
  // 开发环境且启用Mock时使用Mock数据
  if (import.meta.env.DEV && import.meta.env.VITE_ENABLE_MOCK === 'true') {
    const { mockService } = await import('../mockService')
    return mockService.getStockHistory(code, params)
  }

  try {
    // ✅ 使用新的统一K线API（集成SmartSourceManager）
    const { getStockKline } = await import('../market')

    const frequencyMap = {
      daily: 'day',
      weekly: 'week',
      monthly: 'month'
    }

    const response = await getStockKline(
      code,
      params.startDate,
      params.endDate,
      frequencyMap[params.frequency] as 'day' | 'week' | 'month'
    )

    if (response && response.data && response.data.length > 0) {
      // 转换为前端期望的格式
      const historyData = response.data.map((item: any) => ({
        timestamp: item.timestamp,
        date: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }))

      return {
        success: true,
        data: historyData
      }
    } else {
      return {
        success: false,
        message: '获取历史数据失败：返回数据为空',
        data: []
      }
    }
  } catch (error) {
    console.error('获取股票历史数据失败:', error)

    // 降级到旧版API
    try {
      let formattedCode = code
      if (!code.endsWith('.SZ') && !code.endsWith('.SH')) {
        if (code.startsWith('6')) {
          formattedCode = `${code}.SH`
        } else {
          formattedCode = `${code}.SZ`
        }
      }

      const response = await apiRequest.get(`/unified_data/stock/${formattedCode}`, {
        params: {
          start_date: params.startDate,
          end_date: params.endDate,
          frequency: params.frequency === 'daily' ? 'day' :
                    params.frequency === 'weekly' ? 'week' : 'month',
          format: 'dataframe',
          forward_adjust: false
        },
        timeout: timeout || 15000
      })

      if (response.success && response.data && !response.data.empty) {
        const values = response.data.values || []
        const columns = response.data.columns || []
        const dates = response.data.dates || []

        const openIdx = columns.indexOf('open')
        const highIdx = columns.indexOf('high')
        const lowIdx = columns.indexOf('low')
        const closeIdx = columns.indexOf('close')
        const volumeIdx = columns.indexOf('volume')

        const historyData = values.map((row: any, idx: number) => ({
          timestamp: new Date(dates[idx]).getTime(),
          date: dates[idx],
          open: openIdx >= 0 ? row[openIdx] : null,
          high: highIdx >= 0 ? row[highIdx] : null,
          low: lowIdx >= 0 ? row[lowIdx] : null,
          close: closeIdx >= 0 ? row[closeIdx] : null,
          volume: volumeIdx >= 0 ? row[volumeIdx] : 0
        }))

        return {
          success: true,
          data: historyData
        }
      } else {
        return {
          success: false,
          message: '获取历史数据失败：返回数据为空',
          data: []
        }
      }
    } catch (fallbackError) {
      console.error('降级API也失败:', fallbackError)
      return {
        success: false,
        message: '获取历史数据失败',
        data: []
      }
    }
  }
}


// 获取实时股票数据 - 使用统一实时数据API
export const getRealtimeData = async (codes: string[], timeout?: number) => {
  console.log('[getRealtimeData] 开始获取实时数据:', codes)

  // 开发环境且启用Mock时使用Mock数据
  if (import.meta.env.DEV && import.meta.env.VITE_ENABLE_MOCK === 'true') {
    console.log('[getRealtimeData] 使用Mock数据')
    const { mockService } = await import('../mockService')
    return mockService.getRealtimeData(codes)
  }

  try {
    console.log('[getRealtimeData] 调用统一实时API: /unified_data/realtime/quote')

    // 使用统一实时数据API
    const response = await apiRequest.post('/unified_data/realtime/quote', {
      symbols: codes,
      use_cache: true,
      preferred_source: 'qmt'
    }, {
      timeout: timeout || 30000  // 增加默认超时时间到30秒
    })

    console.log('[getRealtimeData] API响应:', response)

    if (response.success && response.data) {
      const quotes = response.data.quotes || {}
      const realtimeData: RealtimeData[] = []

      for (const [code, quote] of Object.entries(quotes)) {
        const q = quote as any
        realtimeData.push({
          code: q.symbol || code,
          name: q.symbol || code,
          price: q.last_price || 0,
          change: 0, // 需要计算
          changePercent: 0, // 需要计算
          volume: q.volume || 0,
          timestamp: q.datetime || new Date().toISOString()
        })
      }

      return {
        success: true,
        data: realtimeData,
        message: response.message || '获取实时数据成功',
        source: response.data.source
      }
    }

    return {
      success: false,
      data: [],
      message: response.message || '获取实时数据失败'
    }
  } catch (error) {
    console.error('获取实时股票数据失败:', error)
    return {
      success: false,
      data: [],
      message: '获取实时数据失败'
    }
  }
}

// 获取技术指标 - 暂不支持
export const getIndicators = async (code: string, indicators: string[], timeout?: number) => {
  // 开发环境且启用Mock时使用Mock数据
  if (import.meta.env.DEV && import.meta.env.VITE_ENABLE_MOCK === 'true') {
    const { mockService } = await import('../mockService')
    return mockService.getIndicators(code, indicators)
  }

  // 当前后端暂不支持技术指标API
  return {
    success: false,
    message: '技术指标功能暂未实现',
    data: {}
  }
}

// 批量获取股票历史数据 - 使用正确的数据查询API
export const getBatchStockHistory = async (
  symbols: string[],
  fields: string[],
  startDate: string,
  endDate: string,
  frequency: 'daily' | 'weekly' | 'monthly' = 'daily',
  timeout?: number
) => {
  try {
    // 调用数据查询API
    const response = await apiRequest.post('/data/query', {
      symbols: symbols,
      fields: fields,
      start_date: startDate,
      end_date: endDate,
      frequency: frequency
    }, {
      timeout: timeout || 30000
    })

    return response
  } catch (error) {
    console.error('批量获取股票历史数据失败:', error)
    return {
      success: false,
      message: '批量获取历史数据失败',
      data: {}
    }
  }
}

// 获取股票筛选结果 - 暂不支持
export const filterStocks = (filters: {
  indicators?: Record<string, any>
  sector?: string[]
  market?: string[]
  priceRange?: {
    min: number
    max: number
  }
  marketCapRange?: {
    min: number
    max: number
  }
}, timeout?: number) => {
  // 当前后端暂不支持股票筛选API
  return Promise.resolve({
    success: false,
    message: '股票筛选功能暂未实现',
    data: []
  })
}

// 获取板块信息 - 暂不支持
export const getSectors = () => {
  // 当前后端暂不支持板块信息API
  return Promise.resolve({
    success: false,
    message: '板块信息功能暂未实现',
    data: []
  })
}

// 获取热门股票 - 暂不支持
export const getHotStocks = (limit?: number) => {
  // 当前后端暂不支持热门股票API
  return Promise.resolve({
    success: false,
    message: '热门股票功能暂未实现',
    data: []
  })
}

// 获取股票搜索结果 - 暂不支持
export const searchStocks = (keyword: string, limit?: number) => {
  // 当前后端暂不支持股票搜索API
  return Promise.resolve({
    success: false,
    message: '股票搜索功能暂未实现',
    data: []
  })
}

// 获取数据质量指标 - 使用数据管理API
export const getDataQuality = () => {
  return apiRequest.get('/data/overview')
}

// 获取数据源状态 - 使用数据管理API
export const getDataSources = () => {
  return apiRequest.get('/data-management/sources/list')
}

// 同步数据 - 使用数据管理API
export const syncData = (source: string, params?: {
  symbols?: string[]
  startDate?: string
  endDate?: string
}, timeout?: number) => {
  return apiRequest.post(`/data-management/sync/${source}`, params, {
    timeout: timeout || 60000
  })
}

// 导出数据 - 使用数据管理API
export const exportData = (params: {
  codes: string[]
  fields: string[]
  format: 'csv' | 'excel' | 'json'
  startDate?: string
  endDate?: string
}) => {
  return apiRequest.post('/data-management/export/start', params)
}

// 批量获取股票名称 - 使用高级数据服务API（通过股票名称服务）
export const getBatchStockNames = async (codes: string[]) => {
  try {
    // 直接使用axios调用，跳过apiRequest的响应拦截器
    // 因为后端返回的是直接的Pydantic模型，不是标准ApiResponse格式
    const axios = (await import('axios')).default
    const response = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8010/api/v1'}/advanced-data-services/get-batch-stock-names`,
      {
        symbols: codes,
        use_cache: true
      },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 15000
      }
    )

    console.log('[getBatchStockNames] API响应:', response.data)

    // 后端直接返回BatchStockNameResponse格式
    const batchResponse = response.data
    const results = batchResponse.results || []

    console.log('[getBatchStockNames] 解析的results:', results)

    if (results && results.length > 0) {
      // 构建代码到名称的映射
      const nameMap: Record<string, string> = {}
      for (const result of results) {
        // 总是记录返回的股票名称，即使它和symbol看起来相同
        // 这样可以确保后端返回的所有名称都被正确映射
        if (result.stock_name) {
          nameMap[result.symbol] = result.stock_name
        }
      }
      console.log('[getBatchStockNames] 构建的名称映射:', nameMap)
      return {
        success: true,
        data: nameMap
      }
    }

    return {
      success: false,
      data: {}
    }
  } catch (error) {
    console.error('[getBatchStockNames] 批量获取股票名称失败:', error)
    return {
      success: false,
      data: {}
    }
  }
}

// 类型定义
export interface StockInfo {
  code: string
  name: string
  market: 'SZ' | 'SH'
  sector: string
  industry: string
  currentPrice: number
  changePercent: number
  open?: number
  high?: number
  low?: number
  close?: number
  volume: number
  marketCap?: number
  pe?: number
  pb?: number
  roe?: number
  lastUpdate: string
  date?: string
}

export interface IndicatorData {
  code: string
  name: string
  values: Record<string, number>
  timestamp: string
}

export interface RealtimeData {
  code: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: string
}

export interface DataQuality {
  completeness: number
  accuracy: number
  timeliness: number
  consistency: number
  lastUpdate: string
}

export interface DataSource {
  id: string
  name: string
  status: 'connected' | 'disconnected' | 'error'
  lastUpdate: string | null
  latency?: number
  errorCount?: number
}
