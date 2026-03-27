/**
 * 股票选择节点数据处理逻辑
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult, NodeUtils } from '../../base/BaseNode'
import { getBatchStockNames, getStockDetail, getStockHistory } from '../../api/modules/data'

/**
 * 更新股票节点显示
 */
export async function updateStockNodeDisplay(node: any, context: NodeContext) {
  // 支持两种参数格式：symbols（数组）和 stockCode（字符串）
  let stockCodes = []

  if (node.params?.symbols && Array.isArray(node.params.symbols)) {
    stockCodes = node.params.symbols
  } else if (node.params?.stockCode) {
    stockCodes = node.params.stockCode.split(/[,，]/)
      .map((code: string) => code.trim())
      .filter((code: string) => code)
  }

  console.log('[StockSelectionNode] updateDisplay, stockCodes:', stockCodes)

  // 始终显示汇总报告样式（类似数据清洗节点）
  node.data.type = 'stats'

  if (stockCodes.length > 0) {
    // 添加市场后缀
    const addMarketSuffix = (code: string): string => {
      if (code.endsWith('.SZ') || code.endsWith('.SH')) {
        return code
      }
      if (code.startsWith('6')) {
        return `${code}.SH`
      } else if (code.startsWith('0') || code.startsWith('3')) {
        return `${code}.SZ`
      }
      return code
    }

    const stockCodesWithSuffix = stockCodes.map(addMarketSuffix)

    // 批量获取股票名称
    try {
      const nameResponse = await getBatchStockNames(stockCodesWithSuffix)
      const nameMap = nameResponse.success ? nameResponse.data : {}

      // 显示配置汇总报告（未获取数据状态）
      const frequency = node.params?.frequency || 'daily'
      const timeRange = node.params?.timeRange || '1Y'

      node.data.content = {
        '股票数量': `${stockCodes.length} 只`,
        '配置状态': '✓ 已配置',
        '时间范围': timeRange,
        '数据频率': frequency === 'daily' ? '日线' : frequency === 'weekly' ? '周线' : '月线',
        '数据状态': '待获取'
      }

      // 更新节点描述
      node.description = `已配置 ${stockCodes.length} 只股票`
    } catch (error) {
      console.error('[StockSelectionNode] 获取股票名称失败:', error)

      const frequency = node.params?.frequency || 'daily'
      const timeRange = node.params?.timeRange || '1Y'

      node.data.content = {
        '股票数量': `${stockCodes.length} 只`,
        '配置状态': '✓ 已配置',
        '时间范围': timeRange,
        '数据频率': frequency === 'daily' ? '日线' : frequency === 'weekly' ? '周线' : '月线',
        '数据状态': '待获取'
      }

      node.description = `已配置 ${stockCodes.length} 只股票`
    }
  } else {
    // 显示默认状态
    node.data.content = {
      '股票数量': '0 只',
      '配置状态': '未配置',
      '时间范围': '--',
      '数据频率': '--',
      '数据状态': '请配置股票代码'
    }
    node.description = '选择股票并获取数据'
  }
}

/**
 * 获取股票数据
 */
export async function fetchStockData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    // 支持两种参数格式
    let stockCodes: string[] = []
    if (node.params?.symbols && Array.isArray(node.params.symbols)) {
      stockCodes = node.params.symbols
    } else if (node.params?.stockCode) {
      stockCodes = node.params.stockCode.split(/[,，]/)
        .map((code: string) => code.trim())
        .filter((code: string) => code)
    }

    if (stockCodes.length === 0) {
      ElMessage({
        message: '请先配置股票代码',
        type: 'warning',
        duration: 3000
      })
      return { success: false, errors: ['请先配置股票代码'] }
    }

    const api_endpoint = node.metadata?.api_endpoint || '/unified_data/stock/'
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8010/api/v1'

    // 处理时间范围
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

    console.log('[StockSelectionNode] 时间范围计算结果:', {
      timeRange: node.params.timeRange,
      startDate: node.params.startDate,
      endDate: node.params.endDate,
      calculatedStart: final_start_date,
      calculatedEnd: final_end_date,
      daysDiff: daysDiff
    })

    // 获取所有需要请求的频率
    let frequencies: string[] = ['day']
    if (node.params?.frequencies && Array.isArray(node.params.frequencies) && node.params.frequencies.length > 0) {
      frequencies = node.params.frequencies
      console.log('[StockSelectionNode] 使用多频率配置:', frequencies)
    } else if (node.params?.frequency) {
      frequencies = [node.params.frequency]
      console.log('[StockSelectionNode] 使用单频率配置:', frequencies)
    } else {
      console.log('[StockSelectionNode] node.params 中没有频率信息，使用默认值 day')
    }
    console.log('[StockSelectionNode] 将获取以下频率的数据:', frequencies)

    // 显示加载状态（带进度跟踪）
    node.data.type = 'loading'
    node.data.content = {
      total: stockCodes.length * frequencies.length,
      current: 0,
      percent: 0
    }
    if (context.updateNode) {
      context.updateNode(node.id, node)
    }

    // 计算总任务数：股票数量 × 频率数量
    const totalTasks = stockCodes.length * frequencies.length
    let completedTasks = 0

    // 格式化股票代码的辅助函数
    const formatStockCode = (code: string): string => {
      let formattedSymbol = code.trim()
      if (!formattedSymbol.endsWith('.SZ') && !formattedSymbol.endsWith('.SH')) {
        if (formattedSymbol.startsWith('6')) {
          formattedSymbol = `${formattedSymbol}.SH`
        } else if (formattedSymbol.startsWith('0') || formattedSymbol.startsWith('3')) {
          formattedSymbol = `${formattedSymbol}.SZ`
        }
      }
      return formattedSymbol
    }

    // 创建所有请求任务（股票 × 频率）
    const allTasks: Array<Promise<any>> = []

    for (const originalSymbol of stockCodes) {
      const formattedSymbol = formatStockCode(originalSymbol)

      for (const frequency of frequencies) {
        const taskPromise = (async () => {
          const request_params = new URLSearchParams({
            start_date: final_start_date,
            end_date: final_end_date,
            frequency: frequency,
            forward_adjust: 'false',
            format: 'dataframe'
          })
          const url = `${baseURL}${api_endpoint}${formattedSymbol}?${request_params.toString()}`

          // 重试函数
          const fetchWithRetry = async (maxRetries = 2, timeout = 15000) => {
            for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
              try {
                const response = await fetch(url, {
                  method: 'GET',
                  headers: { 'Content-Type': 'application/json' },
                  signal: AbortSignal.timeout(timeout)
                })

                if (!response.ok) {
                  throw new Error(`HTTP ${response.status}: ${response.statusText}`)
                }

                const result = await response.json()

                if (!result.success) {
                  throw new Error(result.detail || result.message || 'API返回失败')
                }

                return result
              } catch (error) {
                if (attempt === maxRetries + 1) throw error

                const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000)
                await new Promise(resolve => setTimeout(resolve, delay))
              }
            }
          }

          try {
            const result = await fetchWithRetry()

            // 更新进度
            completedTasks++
            const percent = Math.floor((completedTasks / totalTasks) * 100)
            node.data.content = {
              total: totalTasks,
              current: completedTasks,
              percent: percent
            }
            if (context.updateNode) {
              context.updateNode(node.id, node)
            }

            let latest_price = '--'
            let latest_change = '--'
            let latest_change_percent = '--'
            let latest_volume = '--'

            if (result.data && result.data.values && result.data.values.length > 0) {
              const values = result.data.values
              const columns = result.data.columns || []
              const latest_record = values[values.length - 1]
              const previous_record = values.length > 1 ? values[values.length - 2] : null

              const close_idx = columns.indexOf('close')
              const volume_idx = columns.indexOf('volume')

              if (close_idx !== -1 && latest_record[close_idx] !== null && latest_record[close_idx] !== undefined) {
                latest_price = parseFloat(latest_record[close_idx]).toFixed(2)

                if (previous_record && close_idx !== -1 && previous_record[close_idx] !== null && previous_record[close_idx] !== undefined) {
                  const previous_close = parseFloat(previous_record[close_idx])
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

              if (volume_idx !== -1 && latest_record[volume_idx] !== null && latest_record[volume_idx] !== undefined) {
                latest_volume = latest_record[volume_idx]
              }
            }

            // 🔧 修复：将API返回的 {values, columns} 格式转换为 {dates, fields} 格式
            // 这样后续的合并逻辑才能正确处理
            let convertedData = result.data
            if (result.data && result.data.values && result.data.columns) {
              const values = result.data.values
              const columns = result.data.columns

              const date_idx = columns.indexOf('date')
              const open_idx = columns.indexOf('open')
              const high_idx = columns.indexOf('high')
              const low_idx = columns.indexOf('low')
              const close_idx = columns.indexOf('close')
              const volume_idx = columns.indexOf('volume')

              const dates: any[] = []
              const fields: Record<string, any[]> = {
                open: [],
                high: [],
                low: [],
                close: [],
                volume: []
              }

              for (const row of values) {
                if (date_idx !== -1) dates.push(row[date_idx])
                if (open_idx !== -1) fields.open.push(row[open_idx])
                if (high_idx !== -1) fields.high.push(row[high_idx])
                if (low_idx !== -1) fields.low.push(row[low_idx])
                if (close_idx !== -1) fields.close.push(row[close_idx])
                if (volume_idx !== -1) fields.volume.push(row[volume_idx])
              }

              convertedData = { dates, fields }
            }

            return {
              symbol: formattedSymbol,  // 🔧 修复：返回带后缀的代码（如 000001.SZ）
              frequency: frequency,
              success: true,
              data: convertedData,
              display_data: {
                symbol: formattedSymbol,  // 🔧 修复：返回带后缀的代码
                close_price: latest_price,
                change: latest_change,
                change_percent: latest_change_percent,
                volume: latest_volume
              }
            }
          } catch (error) {
            // 更新进度（失败也要更新）
            completedTasks++
            const percent = Math.floor((completedTasks / totalTasks) * 100)
            node.data.content = {
              total: totalTasks,
              current: completedTasks,
              percent: percent
            }
            if (context.updateNode) {
              context.updateNode(node.id, node)
            }

            return {
              symbol: originalSymbol,
              frequency: frequency,
              success: false,
              error: (error as Error).message,
              data: null,
              display_data: {
                symbol: originalSymbol,
                close_price: '获取失败',
                change: '--',
                change_percent: '--',
                volume: '--'
              }
            }
          }
        })()

        allTasks.push(taskPromise)
      }
    }

    // 等待所有请求完成
    const allResults = await Promise.all(allTasks)

    // 按股票和频率组织数据
    // 数据结构: { symbol: { frequency: data, ... }, ... }
    const symbolDataMap: Record<string, Record<string, any>> = {}

    // 确定用于显示的优先频率（分钟级优先）
    let displayFrequency = frequencies[0]
    const minuteFrequencies = frequencies.filter(f =>
      f === '5min' || f === '15min' || f === '30min' || f === '60min'
    )
    if (minuteFrequencies.length > 0) {
      displayFrequency = minuteFrequencies[0]
      console.log('[StockSelectionNode] 检测到分钟级频率，优先使用:', displayFrequency, '进行显示')
    }

    // 用于显示的表格内容（使用优先频率的数据）
    const displayResults: any[] = []

    for (const result of allResults) {
      if (!symbolDataMap[result.symbol]) {
        symbolDataMap[result.symbol] = {}
      }
      symbolDataMap[result.symbol][result.frequency] = result.data

      // 对于显示，使用优先频率的数据
      if (result.frequency === displayFrequency) {
        displayResults.push(result)
      }
    }

    const successful_results = displayResults.filter(r => r.success)
    const success_count = successful_results.length
    const total_count = stockCodes.length

    // 批量获取股票名称
    const addMarketSuffix = (code: string): string => {
      if (code.endsWith('.SZ') || code.endsWith('.SH')) {
        return code
      }
      if (code.startsWith('6')) {
        return `${code}.SH`
      } else if (code.startsWith('0') || code.startsWith('3')) {
        return `${code}.SZ`
      }
      return code
    }

    const stockCodesWithSuffix = stockCodes.map(addMarketSuffix)
    let nameMap: Record<string, string> = {}

    try {
      const nameResponse = await getBatchStockNames(stockCodesWithSuffix)
      nameMap = nameResponse.success ? nameResponse.data : {}
    } catch (error) {
      console.warn('[StockSelectionNode] 获取股票名称失败:', error)
    }

    // 更新节点显示数据（使用第一个频率的数据）
    const tableContent = displayResults.map(result => {
      const suffixedCode = addMarketSuffix(result.symbol)
      const stockName = nameMap[suffixedCode]

      let displayName = result.symbol || '--'
      if (stockName && stockName !== suffixedCode && stockName !== result.symbol) {
        displayName = stockName
      }

      if (result.success && result.display_data) {
        return {
          '股票代码': result.display_data.symbol,
          '股票名称': displayName,
          '收盘价': result.display_data.close_price,
          '涨跌幅': result.display_data.change_percent,
          '成交量': result.display_data.volume
        }
      } else {
        return {
          '股票代码': result.symbol,
          '股票名称': displayName,
          '收盘价': '获取失败',
          '涨跌幅': '--',
          '成交量': '--'
        }
      }
    })

    // 根据股票数量决定显示方式
    const displayContent = stockCodes.length > 5 ? tableContent.slice(0, 5) : tableContent

    // 🔧 修复：计算所有频率的总数据条数（而不只是显示频率）
    let totalDataPoints = 0
    let startDate = '--'
    let endDate = '--'

    if (allResults.length > 0) {
      // 计算所有频率的数据点总数
      totalDataPoints = allResults.reduce((sum, r) => {
        return sum + (r.data?.dates?.length || 0)
      }, 0)

      // 从显示频率的结果中获取日期范围
      if (successful_results.length > 0) {
        const firstSuccess = successful_results[0]
        if (firstSuccess.data && firstSuccess.data.dates && firstSuccess.data.dates.length > 0) {
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

      console.log('[StockSelectionNode] 数据统计:', {
        总数据条数: totalDataPoints,
        按频率分解: allResults.reduce((acc, r) => {
          if (r.success && r.data?.dates) {
            acc[r.frequency] = (acc[r.frequency] || 0) + r.data.dates.length
          }
          return acc
        }, {} as Record<string, number>),
        所有频率: frequencies
      })
    }

    // 显示表格数据（同时保存到 fullData）
    node.data.type = 'table'
    node.data.content = displayContent
    node.data.fullData = tableContent

    // 保存多频率数据结构，供下游节点使用
    node.data.timeSeriesData = Object.entries(symbolDataMap).map(([symbol, freqData]) => {
      const displayResult = displayResults.find(r => r.symbol === symbol)

      return {
        symbol: symbol,
        multiFrequencyData: freqData,
        display_data: displayResult?.display_data || {}
      }
    })

    // 🔧 修复：保存所有频率信息，而不只是显示频率
    // 构建频率显示标签
    const freqLabels: Record<string, string> = {
      'day': '日线',
      'daily': '日线',
      '1min': '1分钟',
      '5min': '5分钟',
      '15min': '15分钟',
      '30min': '30分钟',
      '60min': '60分钟'
    }
    const frequenciesLabel = frequencies.map(f => freqLabels[f] || f).join('+')

    // 保存数据报告信息到 metadata
    node.data.metadata = {
      totalDataPoints,
      startDate,
      endDate,
      successCount: success_count,
      totalCount: total_count,
      frequencies: frequencies,
      frequenciesLabel: frequenciesLabel,  // 🔧 新增：频率显示标签
      frequency: displayFrequency,  // 用于表格显示的主频率（优先分钟级）
      start_date: final_start_date,
      end_date: final_end_date
    }

    // 添加汇总信息到描述
    // 显示所有获取的频率，并标注当前显示的频率
    const displayFreqLabel = displayFrequency === 'day' || displayFrequency === 'daily' ? '日线' : displayFrequency
    const freqLabel = frequencies.length > 1
      ? `${frequencies.length}种频率，显示${displayFreqLabel}`
      : displayFreqLabel

    if (stockCodes.length > 5) {
      node.description = `已获取 ${success_count}/${total_count} 只股票（${freqLabel}，显示前5只）`
    } else {
      node.description = `已获取 ${success_count}/${total_count} 只股票数据（${freqLabel}）`
    }

    // 🔧 修复：构建和IndexSelectionNode相同的数据格式
    // 合并所有频率的数据，添加frequency列（与IndexSelectionNode保持一致）
    const mergedResults = stockCodes.map(originalSymbol => {
      // 🔧 修复：需要同时匹配原始代码和带后缀的代码
      const symbolResults = allResults.filter(r =>
        r.symbol === originalSymbol ||
        r.symbol === `${originalSymbol}.SH` ||
        r.symbol === `${originalSymbol}.SZ` ||
        r.symbol === `${originalSymbol}.BJ`
      )

      if (frequencies.length === 1) {
        // 只有一个频率，需要添加frequency列！
        const singleResult = symbolResults[0] || { symbol: originalSymbol, success: false, data: null }
        const singleFreq = frequencies[0]

        // 🔧 修复：使用带后缀的symbol（优先使用formatted symbol）
        const finalSymbol = singleResult.symbol && singleResult.symbol.includes('.')
          ? singleResult.symbol
          : (originalSymbol.startsWith('6') ? `${originalSymbol}.SH` :
             originalSymbol.startsWith('0') || originalSymbol.startsWith('3') ? `${originalSymbol}.SZ` :
             originalSymbol.startsWith('8') || originalSymbol.startsWith('4') ? `${originalSymbol}.BJ` : originalSymbol)

        // 构建带frequency列的数据（与多频率分支保持一致）
        let dataWithFreq = singleResult.data
        if (singleResult.data && singleResult.data.dates) {
          const dateCount = singleResult.data.dates.length
          const frequencyList = Array(dateCount).fill(singleFreq)

          // 创建新对象，避免修改原始数据
          dataWithFreq = {
            dates: singleResult.data.dates,
            fields: {
              ...(singleResult.data.fields || {}),
              frequency: frequencyList
            }
          }

          console.log(`[StockSelectionNode] 单频率 ${singleFreq} ${originalSymbol}: 添加frequency列, dateCount=${dateCount}`)
        }

        return {
          symbol: finalSymbol,  // 🔧 修复：返回带后缀的symbol
          success: singleResult.success,
          data: dataWithFreq,
          display_data: singleResult.display_data
        }
      }

      // 多频率：合并所有频率的数据，添加frequency列
      const allDates: any[] = []
      const allFields: Record<string, any[]> = {
        open: [],
        high: [],
        low: [],
        close: [],
        volume: []
      }
      const frequencyList: any[] = []

      for (const freq of frequencies) {
        const freqResult = symbolResults.find(r => r.frequency === freq)
        if (freqResult && freqResult.data && freqResult.data.dates) {
          allDates.push(...freqResult.data.dates)
          // 为每个日期添加频率标识
          for (let i = 0; i < freqResult.data.dates.length; i++) {
            frequencyList.push(freq)
          }
          if (freqResult.data.fields) {
            allFields.open.push(...(freqResult.data.fields.open || []))
            allFields.high.push(...(freqResult.data.fields.high || []))
            allFields.low.push(...(freqResult.data.fields.low || []))
            allFields.close.push(...(freqResult.data.fields.close || []))
            allFields.volume.push(...(freqResult.data.fields.volume || []))
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

      // 使用第一个成功频率的display_data（优先使用分钟级）
      const displayResult = symbolResults.find(r => r.frequency === displayFrequency) || symbolResults[0]

      // 🔧 修复：使用带后缀的symbol（优先使用formatted symbol）
      const finalSymbol = displayResult?.symbol && displayResult.symbol.includes('.')
        ? displayResult.symbol
        : (originalSymbol.startsWith('6') ? `${originalSymbol}.SH` :
           originalSymbol.startsWith('0') || originalSymbol.startsWith('3') ? `${originalSymbol}.SZ` :
           originalSymbol.startsWith('8') || originalSymbol.startsWith('4') ? `${originalSymbol}.BJ` : originalSymbol)

      return {
        symbol: finalSymbol,  // 🔧 修复：返回带后缀的symbol
        success: symbolResults.some(r => r.success),
        data: mergedData,
        display_data: displayResult?.display_data || null
      }
    })

    // 保存实际数据到 node.data.data 供下游节点使用（使用合并后的格式）
    node.data.data = mergedResults

    return {
      success: true,
      data: mergedResults,
      message: `通过统一数据API成功获取 ${success_count}/${total_count} 只股票的 ${frequencies.length} 种频率数据`
    }
  } catch (error) {
    console.error('[StockSelectionNode] 获取股票数据失败:', error)

    node.data.content = [{
      '股票代码': '系统错误',
      '股票名称': '--',
      '收盘价': `获取失败: ${(error as Error).message}`,
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

  if (!params.symbols && !params.stockCode) {
    errors.push('请输入股票代码')
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}
