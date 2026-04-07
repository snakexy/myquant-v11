/**
 * 指数选择节点数据处理逻辑
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'
import { getBatchStockNames } from '../../api/modules/data'

/**
 * 更新指数节点显示
 */
export async function updateIndexNodeDisplay(node: any, context: NodeContext) {
  const indexCodes = node.params?.indexCode
    ? node.params.indexCode.split(/[,，\n]/)
        .map((code: string) => code.trim())
        .filter((code: string) => code)
    : []

  console.log('[IndexSelectionNode] updateDisplay, indexCodes:', indexCodes)

  // 始终显示汇总报告样式（类似数据清洗节点）
  node.data.type = 'stats'

  if (indexCodes.length > 0) {
    // 添加市场后缀
    const addMarketSuffix = (code: string): string => {
      if (code.endsWith('.SZ') || code.endsWith('.SH')) {
        return code
      }
      if (code.startsWith('6') || code.startsWith('000') || code.startsWith('001')) {
        return `${code}.SH`
      } else if (code.startsWith('399') || code.startsWith('200')) {
        return `${code}.SZ`
      }
      return code
    }

    const indexCodesWithSuffix = indexCodes.map(addMarketSuffix)

    // 批量获取指数名称
    try {
      const nameResponse = await getBatchStockNames(indexCodesWithSuffix)
      const nameMap = nameResponse.success ? nameResponse.data : {}

      // 显示配置汇总报告（未获取数据状态）
      const frequency = node.params?.frequency || 'daily'
      const timeRange = node.params?.timeRange || '1Y'

      node.data.content = {
        '指数数量': `${indexCodes.length} 个`,
        '配置状态': '✓ 已配置',
        '时间范围': timeRange,
        '数据频率': frequency === 'daily' ? '日线' : frequency === 'weekly' ? '周线' : '月线',
        '数据状态': '待获取'
      }

      // 更新节点描述
      node.description = `已配置 ${indexCodes.length} 个指数`
    } catch (error) {
      console.error('[IndexSelectionNode] 获取指数名称失败:', error)

      const frequency = node.params?.frequency || 'daily'
      const timeRange = node.params?.timeRange || '1Y'

      node.data.content = {
        '指数数量': `${indexCodes.length} 个`,
        '配置状态': '✓ 已配置',
        '时间范围': timeRange,
        '数据频率': frequency === 'daily' ? '日线' : frequency === 'weekly' ? '周线' : '月线',
        '数据状态': '待获取'
      }

      node.description = `已配置 ${indexCodes.length} 个指数`
    }
  } else {
    // 显示默认状态
    const timeRange = node.params?.timeRange || '1Y'
    node.data.content = {
      '指数数量': '0 个',
      '配置状态': '未配置',
      '时间范围': timeRange,
      '数据频率': '--',
      '数据状态': '请配置指数代码'
    }
    node.description = '选择指数并获取数据'
  }
}

/**
 * 获取指数数据（支持多频率）
 */
export async function fetchIndexData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    const indexCodes: string[] = node.params?.indexCode
      ? node.params.indexCode.split(/[,，\n]/)
          .map((code: string) => code.trim())
          .filter((code: string) => code)
      : []

    if (indexCodes.length === 0) {
      ElMessage({
        message: '请先配置指数代码',
        type: 'warning',
        duration: 3000
      })
      return { success: false, errors: ['请先配置指数代码'] }
    }

    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8010/api/v1'

    // 🔧 修复：添加和股票选择节点一样的时间范围计算逻辑
    // 如果用户选择了timeRange(如1Y、3M等),计算出startDate和endDate
    // 如果用户直接输入了startDate和endDate,则使用用户输入的值
    const calculateDateRange = (timeRange: string, startDate: string, endDate: string) => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)

      // 如果用户提供了开始和结束日期,直接使用
      if (startDate && endDate) {
        return {
          start: startDate,
          end: endDate || today.toISOString().split('T')[0]
        }
      }

      // 根据timeRange计算日期范围
      if (!timeRange || timeRange === '1Y') {
        // 默认1年
        const lastYear = new Date(today)
        lastYear.setFullYear(today.getFullYear() - 1)
        return {
          start: lastYear.toISOString().split('T')[0],
          end: today.toISOString().split('T')[0]
        }
      }

      // 解析timeRange
      const match = timeRange.match(/^(\d+)([WMY])$/)  // 1W, 3M, 2Y等
      if (!match) {
        // 默认1年
        const lastYear = new Date(today)
        lastYear.setFullYear(today.getFullYear() - 1)
        return {
          start: lastYear.toISOString().split('T')[0],
          end: today.toISOString().split('T')[0]
        }
      }

      const value = parseInt(match[1])
      const unit = match[2]

      const startDate_obj = new Date(today)

      switch (unit) {
        case 'W':  // 周
          startDate_obj.setDate(today.getDate() - value * 7)
          break
        case 'M':  // 月
          startDate_obj.setMonth(today.getMonth() - value)
          break
        case 'Y':  // 年
          startDate_obj.setFullYear(today.getFullYear() - value)
          break
        default:
          startDate_obj.setFullYear(today.getFullYear() - 1)
      }

      return {
        start: startDate_obj.toISOString().split('T')[0],
        end: today.toISOString().split('T')[0]
      }
    }

    const dateRange = calculateDateRange(
      node.params.timeRange || '',
      node.params.startDate || '',
      node.params.endDate || ''
    )

    let final_start_date = dateRange.start
    let final_end_date = dateRange.end

    // 🔍 添加日志：打印时间范围计算结果
    const startDateObj = new Date(final_start_date)
    const endDateObj = new Date(final_end_date)
    const daysDiff = Math.floor((endDateObj.getTime() - startDateObj.getTime()) / (1000 * 60 * 60 * 24))

    console.log('[IndexSelectionNode] 时间范围计算结果:', {
      timeRange: node.params.timeRange,
      startDate: node.params.startDate,
      endDate: node.params.endDate,
      calculatedStart: final_start_date,
      calculatedEnd: final_end_date,
      daysDiff: daysDiff
    })

    // 支持多频率：使用 frequencies 参数
    const frequencies = node.params.frequencies || [node.params.frequency || 'daily']
    console.log('[IndexSelectionNode] 获取多频率数据:', frequencies)

    // 格式化所有指数代码：添加市场后缀
    const addMarketSuffix = (code: string): string => {
      if (code.endsWith('.SZ') || code.endsWith('.SH')) {
        return code
      }
      if (code.startsWith('6') || code.startsWith('000') || code.startsWith('001')) {
        return `${code}.SH`
      } else if (code.startsWith('399') || code.startsWith('200')) {
        return `${code}.SZ`
      }
      return code
    }

    const formattedSymbols = indexCodes.map(addMarketSuffix)

    // 为每个频率获取数据
    const allResults = []
    let totalDataPoints = 0
    let success_count = 0

    for (const freq of frequencies) {
      console.log(`[IndexSelectionNode] 获取频率 ${freq} 的数据...`)

      // 使用数据中枢后端API批量查询接口
      const url = `${baseURL}/data/query`

      const request_params = {
        symbols: formattedSymbols,
        fields: ['open', 'high', 'low', 'close', 'volume'],
        start_date: final_start_date,
        end_date: final_end_date,
        frequency: freq
      }

      // 重试函数
      const fetchWithRetry = async (maxRetries = 2, timeout = 30000) => {
        for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
          try {
            // 构建URL查询参数
            const queryParams = new URLSearchParams({
              start_date: final_start_date,
              end_date: final_end_date,
              frequency: freq
            })
            const fullUrl = `${url}?${queryParams.toString()}`

            const response = await fetch(fullUrl, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(request_params),
              signal: AbortSignal.timeout(timeout)
            })

            if (!response.ok) {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }

            const result = await response.json()

            if (!result.success) {
              throw new Error(result.error || result.detail || result.message || 'API返回失败')
            }

            return result
          } catch (error) {
            if (attempt === maxRetries + 1) throw error

            const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000)
            await new Promise(resolve => setTimeout(resolve, delay))
          }
        }
      }

      let api_result
      try {
        api_result = await fetchWithRetry()
      } catch (error) {
        console.error(`[IndexSelectionNode] 获取频率 ${freq} 的指数数据失败:`, error)
        continue
      }

      // 处理该频率的数据
      for (const originalSymbol of indexCodes) {
        const formattedSymbol = addMarketSuffix(originalSymbol)
        const stockData = api_result.data?.[formattedSymbol]

        let latest_price = '--'
        let latest_change = '--'
        let latest_change_percent = '--'
        let latest_volume = '--'
        let success = false
        let data = null

        if (stockData && stockData.dates && stockData.dates.length > 0) {
          success = true
          data = { ...stockData, frequency: freq }  // 添加频率标识

          const dates = stockData.dates
          const fields = stockData.fields || {}
          const close_prices = fields.close || []
          const volumes = fields.volume || []

          if (close_prices.length > 0) {
            latest_price = parseFloat(close_prices[close_prices.length - 1]).toFixed(2)

            if (close_prices.length > 1) {
              const previous_close = parseFloat(close_prices[close_prices.length - 2])
              const current_price = parseFloat(latest_price)
              const change = current_price - previous_close
              const change_percent = (change / previous_close) * 100
              latest_change = change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2)
              latest_change_percent = change_percent >= 0 ? `+${change_percent.toFixed(2)}%` : `${change_percent.toFixed(2)}%`
            } else {
              latest_change = '0.00'
              latest_change_percent = '0.00%'
            }
          }

          if (volumes.length > 0) {
            latest_volume = volumes[volumes.length - 1]
          }
        }

        // 查找是否已有该指数的结果
        let existingResult = allResults.find(r => r.symbol === originalSymbol)
        if (!existingResult) {
          existingResult = {
            symbol: originalSymbol,
            success: false,
            data: null,
            display_data: null,
            frequencies: {}  // 存储各频率的数据
          }
          allResults.push(existingResult)
        }

        // 更新该频率的数据
        if (success) {
          existingResult.frequencies[freq] = data
          // 如果还没有主数据显示，使用第一个成功频率的数据
          if (!existingResult.success) {
            existingResult.success = true
            existingResult.data = data
            existingResult.display_data = {
              symbol: originalSymbol,
              close_price: latest_price,
              change: latest_change,
              change_percent: latest_change_percent,
              volume: latest_volume
            }
          }
          // 如果是日线，优先使用日线数据显示
          if (freq === 'daily' || freq === 'day') {
            existingResult.display_data = {
              symbol: originalSymbol,
              close_price: latest_price,
              change: latest_change,
              change_percent: latest_change_percent,
              volume: latest_volume
            }
          }
        }
      }
    }

    // 计算成功数量
    const successful_results = allResults.filter(r => r.success)
    success_count = successful_results.length
    const total_count = allResults.length

    // 批量获取指数名称
    const indexCodesWithSuffix = indexCodes.map(addMarketSuffix)
    let nameMap: Record<string, string> = {}

    try {
      const nameResponse = await getBatchStockNames(indexCodesWithSuffix)
      nameMap = nameResponse.success ? nameResponse.data : {}
    } catch (error) {
      console.warn('[IndexSelectionNode] 获取指数名称失败:', error)
    }

    // 更新节点显示数据
    const tableContent = allResults.map(result => {
      const suffixedCode = addMarketSuffix(result.symbol)
      const indexName = nameMap[suffixedCode]

      if (result.success && result.display_data) {
        return {
          '指数代码': result.display_data.symbol,
          '指数名称': indexName && indexName !== suffixedCode ? indexName : '--',
          '收盘点位': result.display_data.close_price,
          '涨跌幅': result.display_data.change_percent,
          '成交量': result.display_data.volume
        }
      } else {
        return {
          '指数代码': result.symbol,
          '指数名称': indexName && indexName !== suffixedCode ? indexName : '--',
          '收盘点位': '获取失败',
          '涨跌幅': '--',
          '成交量': '--'
        }
      }
    })

    // 根据指数数量决定显示方式
    const displayContent = indexCodes.length > 3 ? tableContent.slice(0, 3) : tableContent

    // 计算总数据点数（所有频率的总和）
    for (const result of successful_results) {
      for (const freq of frequencies) {
        if (result.frequencies && result.frequencies[freq]) {
          totalDataPoints += result.frequencies[freq].dates?.length || 0
        }
      }
    }

    // 获取日期范围
    let startDate = '--'
    let endDate = '--'
    if (successful_results.length > 0 && successful_results[0].data) {
      const firstSuccess = successful_results[0]
      if (firstSuccess.data.dates && firstSuccess.data.dates.length > 0) {
        // 🔧 修复：只提取日期部分，去掉时间
        const extractDate = (dateStr: string) => {
          // 处理 ISO 格式 (如 "2025-07-07T10:30:00")
          if (dateStr.includes('T')) {
            return dateStr.split('T')[0]
          }
          // 处理空格分隔格式 (如 "2025-07-07 10:30:00")
          if (dateStr.includes(' ')) {
            return dateStr.split(' ')[0]
          }
          return dateStr
        }
        startDate = extractDate(firstSuccess.data.dates[0])
        endDate = extractDate(firstSuccess.data.dates[firstSuccess.data.dates.length - 1])
      }
    }

    // 显示表格数据（同时保存到 fullData）
    node.data.type = 'table'
    node.data.content = displayContent
    node.data.fullData = tableContent

    // 🔧 新增：生成频率显示标签
    const freqLabels: Record<string, string> = {
      'day': '日线',
      'daily': '日线',
      '1min': '1分钟',
      '5min': '5分钟',
      '15min': '15分钟',
      '30min': '30分钟',
      '60min': '60分钟'
    }
    const frequenciesLabel = frequencies.map((f: string) => freqLabels[f] || f).join('+')

    node.data.metadata = {
      totalDataPoints,
      startDate,
      endDate,
      successCount: success_count,
      totalCount: total_count,
      frequencies: frequencies,  // 保存频率列表
      frequenciesLabel: frequenciesLabel  // 🔧 新增：频率显示标签
    }

    // 添加汇总信息到描述
    const freqLabel = frequencies.map(f => {
      if (f === 'daily' || f === 'day') return '日线'
      if (f === '60min') return '60分钟'
      return f
    }).join('、')

    if (indexCodes.length > 3) {
      node.description = `已获取 ${success_count}/${total_count} 个指数（${freqLabel}）`
    } else {
      node.description = `已获取 ${success_count}/${total_count} 个指数数据（${freqLabel}）`
    }

    // 构建返回数据，合并所有频率的数据并添加frequency列
    const mergedResults = allResults.map(result => {
      // 如果只有一个频率，直接返回该频率的数据
      if (frequencies.length === 1 && result.frequencies && result.frequencies[frequencies[0]]) {
        const singleFreqData = result.frequencies[frequencies[0]]
        return {
          symbol: result.symbol,
          success: result.success,
          data: singleFreqData,
          display_data: result.display_data
        }
      }

      // 多频率：合并所有频率的数据，添加frequency列
      const allDates = []
      const allFields = {
        open: [],
        high: [],
        low: [],
        close: [],
        volume: []
      }
      const frequencyList = []

      for (const freq of frequencies) {
        if (result.frequencies && result.frequencies[freq]) {
          const freqData = result.frequencies[freq]
          if (freqData.dates) {
            allDates.push(...freqData.dates)
            // 为每个日期添加频率标识
            for (let i = 0; i < freqData.dates.length; i++) {
              frequencyList.push(freq)
            }
          }
          if (freqData.fields) {
            allFields.open.push(...(freqData.fields.open || []))
            allFields.high.push(...(freqData.fields.high || []))
            allFields.low.push(...(freqData.fields.low || []))
            allFields.close.push(...(freqData.fields.close || []))
            allFields.volume.push(...(freqData.fields.volume || []))
          }
        }
      }

      // 构建合并后的数据，包含frequency列
      const mergedData = {
        dates: allDates,
        fields: {
          ...allFields,
          frequency: frequencyList  // 添加frequency列
        }
      }

      return {
        symbol: result.symbol,
        success: result.success,
        data: mergedData,
        display_data: result.display_data
      }
    })

    // 保存实际数据到 node.data.data 供下游节点使用
    node.data.data = mergedResults

    return {
      success: true,
      data: mergedResults,
      message: `通过数据中枢API成功获取 ${success_count}/${total_count} 个指数数据（${freqLabel}）`
    }
  } catch (error) {
    console.error('[IndexSelectionNode] 获取指数数据失败:', error)

    node.data.content = [{
      '指数代码': '系统错误',
      '指数名称': '--',
      '收盘点位': `获取失败: ${(error as Error).message}`,
      '涨跌幅': '--',
      '成交量': '--'
    }]

    return {
      success: false,
      errors: [(error as Error).message]
    }
  }
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  if (!params.indexCode) {
    errors.push('请输入指数代码')
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}
