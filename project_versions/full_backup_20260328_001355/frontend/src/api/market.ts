/**
 * MyQuant v9.0.0 - Market API
 * 市场行情API
 */

import { http } from './request'

/**
 * 获取市场状态
 */
export const getMarketStatus = () => {
  return http.get('/market/status')
}

/**
 * 获取实时行情
 * @param symbols 股票代码列表，逗号分隔
 * @param useCache 是否使用缓存
 */
export const getQuotes = (symbols: string, useCache = true) => {
  return http.get('/market/quotes', {
    params: { symbols, use_cache: useCache }
  })
}

/**
 * 获取指数行情
 * @param symbols 指数代码列表，逗号分隔
 */
export const getIndexQuotes = (symbols: string) => {
  return http.get('/market/index_quotes', {
    params: { symbols }
  })
}

/**
 * 获取股票列表
 * @param market 市场代码
 */
export const getStockList = (market?: string) => {
  return http.get('/market/stock_list', {
    params: { market }
  })
}

/**
 * 搜索股票
 * @param keyword 搜索关键词
 * @param limit 返回数量限制
 */
export const searchStocks = (keyword: string, limit = 10) => {
  return http.get('/market/search', {
    params: { keyword, limit }
  })
}

/**
 * 获取热门股票
 * @param limit 返回数量限制
 */
export const getHotStocks = (limit = 20) => {
  return http.get('/market/hot_stocks', {
    params: { limit }
  })
}

/**
 * 获取市场概览
 */
export const getMarketOverview = () => {
  return http.get('/market/market_overview')
}

// ==================== 板块指数API ====================

/**
 * 获取板块列表
 * @param category 板块分类 (可选) - 如: '一级行业', '二级行业', '概念板块'
 * @param hasData 是否只返回有数据的板块 (可选)
 */
export const getBoardList = (category?: string, hasData?: boolean) => {
  return http.get('/market/boards/list', {
    params: { category, has_data: hasData }
  })
}

/**
 * 获取板块K线数据
 * @param code 板块代码 (如: 880001)
 * @param startDate 开始日期 (可选) - 格式: YYYY-MM-DD
 * @param endDate 结束日期 (可选) - 格式: YYYY-MM-DD
 * @param limit 返回记录数限制 (可选) - 默认100，最大1000
 */
export const getBoardKline = (
  code: string,
  startDate?: string,
  endDate?: string,
  limit?: number
) => {
  return http.get(`/market/boards/kline/${code}`, {
    params: {
      start_date: startDate,
      end_date: endDate,
      limit
    }
  })
}

/**
 * 获取板块实时行情
 * @param code 板块代码
 */
export const getBoardQuote = (code: string) => {
  return http.get(`/market/boards/quote/${code}`)
}

/**
 * 搜索板块
 * @param keyword 搜索关键词
 * @param limit 返回数量限制
 */
export const searchBoards = (keyword: string, limit = 20) => {
  return http.get('/market/boards/search', {
    params: { keyword, limit }
  })
}

/**
 * 获取板块成分股
 * @param code 板块代码
 * @param limit 返回成分股数量限制
 */
export const getBoardComponents = (code: string, limit = 50) => {
  return http.get(`/market/boards/components/${code}`, {
    params: { limit }
  })
}

/**
 * 获取热门板块
 * @param limit 返回数量限制
 * @param sortBy 排序字段 (change_percent/volume/amount)
 */
export const getHotBoards = (limit = 10, sortBy = 'change_percent') => {
  return http.get('/market/boards/hot', {
    params: { limit, sort_by: sortBy }
  })
}

// ==================== 股票K线API ====================

/**
 * 获取股票K线数据（通过SmartSourceManager）
 * 集成了刷新控制和智能补全策略
 *
 * @param symbol 股票代码
 * @param startDate 开始日期 (YYYY-MM-DD)
 * @param endDate 结束日期 (YYYY-MM-DD)
 * @param frequency 数据频率 (day/week/month)
 * @param forceRefresh 强制刷新（忽略缓存）
 */
export const getStockKline = (
  symbol: string,
  startDate: string,
  endDate: string,
  frequency: 'day' | 'week' | 'month' = 'day',
  forceRefresh = false
) => {
  return http.get(`/market/stock/${symbol}/kline`, {
    params: {
      start_date: startDate,
      end_date: endDate,
      frequency,
      force_refresh: forceRefresh
    }
  })
}

// ==================== 新K线API（基于XtQuant） ====================

/**
 * 导出新的高性能K线API
 *
 * > 创建日期: 2026-02-05
 * > 特性:
 * > - 纯在线获取，性能9-36ms
 * > - 支持所有K线周期（月K、周K、日K、分钟K）
 * > - 支持最大10000条数据
 *
 * 使用示例:
 * ```ts
 * import { getKlineData, getDailyKline } from '@/api/market'
 *
 * // 方式1：使用通用API
 * const data = await getKlineData('600519.SH', '1d', 250)
 *
 * // 方式2：使用便捷函数
 * const daily = await getDailyKline('600519.SH', 250)
 * const weekly = await getWeeklyKline('600519.SH', 120)
 * const monthly = await getMonthlyKline('600519.SH', 60)
 * ```
 */
export * from './kline'
