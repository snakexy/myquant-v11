/**
 * 数据清洗节点数据处理逻辑
 *
 * 核心任务：将数据中枢的股票数据转换为QLib可用的数据格式
 * 保存路径：项目根目录 \data\qlib_data
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'
import { timeRangeSyncState } from '@/utils/timeRangeSync'

/**
 * 将上游节点数据转换为后端期望的 DataRecord 格式
 * 上游数据格式: { symbol, success, data: { dates, fields } }
 * 后端期望格式: { stock, date, open, high, low, close, volume, frequency? }
 */
function convertToDataRecords(upstreamData: any[]): any[] {
  const records: any[] = []

  console.log(`[convertToDataRecords] 输入数据: ${upstreamData.length} 个标的`)

  for (const item of upstreamData) {
    if (!item.success || !item.data) {
      console.warn(`[convertToDataRecords] 跳过无效数据:`, item)
      continue
    }

    const symbol = item.symbol
    const data = item.data

    // 检查数据格式
    if (!data.dates || !data.fields) {
      console.warn(`[convertToDataRecords] 跳过无效数据（缺少dates或fields）: ${symbol}`)
      continue
    }

    const dates = data.dates
    const fields = data.fields
    const open = fields.open || []
    const high = fields.high || []
    const low = fields.low || []
    const close = fields.close || []
    const volume = fields.volume || []
    // 🔧 移除 frequency 字段 - 这是数据中枢的内部字段，不应该传递给清洗节点

    // 转换每条记录
    for (let i = 0; i < dates.length; i++) {
      const record: any = {
        stock: symbol,
        date: dates[i],
        open: open[i] !== null && open[i] !== undefined ? parseFloat(open[i]) : null,
        high: high[i] !== null && high[i] !== undefined ? parseFloat(high[i]) : null,
        low: low[i] !== null && low[i] !== undefined ? parseFloat(low[i]) : null,
        close: close[i] !== null && close[i] !== undefined ? parseFloat(close[i]) : null,
        volume: volume[i] !== null && volume[i] !== undefined ? parseFloat(volume[i]) : null
      }

      records.push(record)
    }
  }

  // 统计各频率的数量
  const freqCount: Record<string, number> = {}
  for (const r of records) {
    if (r.frequency) {
      freqCount[r.frequency] = (freqCount[r.frequency] || 0) + 1
    }
  }

  // 🔧 调试：检查成交量为0的数据
  const zeroVolumeRecords = records.filter(r => r.volume === 0)
  const zeroVolumeWithPrice = zeroVolumeRecords.filter(r => r.close > 0)
  console.log(`[convertToDataRecords] 转换完成: ${upstreamData.length} 个标的 -> ${records.length} 条记录`)
  console.log(`[convertToDataRecords] 频率统计:`, freqCount)
  console.log(`[convertToDataRecords] 成交量为0的记录: ${zeroVolumeRecords.length} 条`)
  console.log(`[convertToDataRecords] 成交量为0但有价格的记录: ${zeroVolumeWithPrice.length} 条`)
  if (zeroVolumeWithPrice.length > 0) {
    console.log(`[convertToDataRecords] 成交量为0但有价格的记录示例:`, zeroVolumeWithPrice.slice(0, 3))
  }
  return records
}

/**
 * 默认显示内容
 */
const defaultDisplayContent = {
  // 数据质量分数
  qualityScore: 0,
  // 进度指标
  completeness: 0,
  accuracy: 0,
  consistency: 0,
  // 问题计数
  missingCount: 0,
  duplicateCount: 0,
  outlierCount: 0,
  // 转换状态
  conversionStatus: 'pending', // pending, converting, completed, failed
  // 数据统计
  stockCount: 0,
  dateRange: '',
  dataPath: ''
}

/**
 * 更新数据清洗节点显示
 */
export async function updateDataCleaningNodeDisplay(node: any, context: NodeContext) {
  console.log('[DataCleaningNode] updateDisplay')

  // 检查上游节点
  const upstreamNodes = context.getUpstreamNodes(node.id)
  const hasUpstreamData = upstreamNodes.length > 0

  if (!hasUpstreamData) {
    // 没有上游数据，显示默认状态
    node.data.content = {
      qualityScore: 0,
      completeness: 0,
      accuracy: 0,
      consistency: 0,
      missingCount: 0,
      duplicateCount: 0,
      outlierCount: 0,
      conversionStatus: 'pending',
      stockCount: 0,
      dateRange: '未配置',
      dataPath: node.params?.qlibDataPath || 'E:\\MyQuant_v8.0.1\\data\\qlib_data'
    }
    node.description = '等待上游数据'
    return
  }

  // 从上游节点获取数据
  const stockNode = upstreamNodes.find(n => n.id === 'stock-selection')
  const indexNode = upstreamNodes.find(n => n.id === 'index-selection')

  let stockCodes: string[] = []
  let indexCodes: string[] = []

  if (stockNode) {
    stockCodes = stockNode.params?.symbols && Array.isArray(stockNode.params.symbols)
      ? stockNode.params.symbols
      : (stockNode.params?.stockCode || '').split(/[,，\n]/).map((c: string) => c.trim()).filter((c: string) => c)
  }

  if (indexNode) {
    indexCodes = (indexNode.params?.indexCode || '').split(/[,，\n]/).map((c: string) => c.trim()).filter((c: string) => c)
  }

  const totalCount = stockCodes.length + indexCodes.length

  if (totalCount === 0) {
    node.data.content = {
      ...defaultDisplayContent,
      dataPath: node.params?.qlibDataPath || 'E:\\MyQuant_v8.0.1\\data\\qlib_data'
    }
    node.description = '上游无数据'
    return
  }

  // 检查是否已经转换过
  const savedStatus = node.data?.content?.conversionStatus
  if (savedStatus === 'completed') {
    // 已完成，保持现有显示
    node.description = `已转换 ${node.data.content.stockCount} 只标的`
    return
  }

  // 从上游节点获取日期范围
  let dateRange = '未设置'
  if (stockNode?.params) {
    const startDate = stockNode.params.startDate || stockNode.params.start_date
    const endDate = stockNode.params.endDate || stockNode.params.end_date

    if (startDate && endDate) {
      dateRange = `${startDate} ~ ${endDate}`
    } else if (stockNode.params.timeRange) {
      // 如果使用timeRange,显示相对时间
      const timeRangeMap: Record<string, string> = {
        '1W': '近1周',
        '1M': '近1个月',
        '3M': '近3个月',
        '6M': '近6个月',
        '1Y': '近1年',
        '2Y': '近2年'
      }
      dateRange = timeRangeMap[stockNode.params.timeRange] || stockNode.params.timeRange
    }
  }

  // 显示待转换状态
  node.data.content = {
    ...defaultDisplayContent,
    stockCount: totalCount,
    dateRange: dateRange,
    dataPath: node.params?.qlibDataPath || 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
    conversionStatus: 'pending'
  }

  node.description = `待转换 ${totalCount} 只标的`
}

/**
 * 执行数据转换为QLib格式
 */
export async function convertToQLibFormat(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    const upstreamNodes = context.getUpstreamNodes(node.id)
    const hasUpstreamData = upstreamNodes.length > 0

    if (!hasUpstreamData) {
      ElMessage({
        message: '请先连接上游数据节点',
        type: 'warning',
        duration: 3000
      })
      return { success: false, errors: ['请先连接上游数据节点'] }
    }

    // 获取上游数据
    const stockNode = upstreamNodes.find((n: any) => n.id === 'stock-selection')
    const indexNode = upstreamNodes.find((n: any) => n.id === 'index-selection')

    let symbols: string[] = []
    let upstreamDataList: any[] = []  // 🔧 修复：重命名以避免与后面的 responseData 冲突
    let frequencies: string[] = []

    console.log('[DataCleaningNode] 上游节点检查:', {
      stockNode: stockNode ? '存在' : '不存在',
      indexNode: indexNode ? '存在' : '不存在',
      stockNodeData: stockNode?.data,
      indexNodeData: indexNode?.data
    })

    // 详细打印上游节点的完整数据结构
    if (stockNode) {
      console.log('[DataCleaningNode] 股票节点完整结构:', {
        id: stockNode.id,
        data: stockNode.data,
        dataKeys: stockNode.data ? Object.keys(stockNode.data) : 'no data',
        dataContent: stockNode.data?.content,
        dataType: stockNode.data?.type,
        dataData: stockNode.data?.data
      })
    }

    if (indexNode) {
      console.log('[DataCleaningNode] 指数节点完整结构:', {
        id: indexNode.id,
        data: indexNode.data,
        dataKeys: indexNode.data ? Object.keys(indexNode.data) : 'no data',
        dataContent: indexNode.data?.content,
        dataType: indexNode.data?.type,
        dataData: indexNode.data?.data
      })
    }

    if (stockNode && stockNode.data?.data) {
      const stockData = stockNode.data.data
      console.log('[DataCleaningNode] 股票节点数据:', stockData)

      // stockData 可能是数组或对象
      if (Array.isArray(stockData)) {
        // 转换为后端期望的格式
        const convertedData = convertToDataRecords(stockData)
        upstreamDataList.push(...convertedData)
        symbols.push(...stockData.map((d: any) => d.symbol || d.symbol))
      } else if (stockData.symbols) {
        const convertedData = convertToDataRecords([stockData])
        upstreamDataList.push(...convertedData)
        symbols.push(...stockData.symbols)
      } else {
        // 如果data是一个对象，尝试直接使用
        console.log('[DataCleaningNode] stockData是对象，尝试直接使用:', stockData)
        const convertedData = convertToDataRecords([stockData])
        upstreamDataList.push(...convertedData)
        if (stockData.symbol) {
          symbols.push(stockData.symbol)
        }
      }

      // 获取上游节点的频率信息
      if (stockNode.data?.metadata?.frequencies) {
        console.log('[DataCleaningNode] 从metadata获取频率:', stockNode.data.metadata.frequencies)
        frequencies.push(...stockNode.data.metadata.frequencies)
      } else if (stockNode.params?.frequencies) {
        console.log('[DataCleaningNode] 从params获取频率:', stockNode.params.frequencies)
        frequencies.push(...stockNode.params.frequencies)
      } else if (stockNode.params?.frequency) {
        frequencies.push(stockNode.params.frequency)
      }
    }

    // 总是尝试获取指数节点数据（不再检查 includeIndex）
    if (indexNode && indexNode.data?.data) {
      const indexData = indexNode.data.data
      console.log('[DataCleaningNode] 指数节点数据:', indexData)

      // indexData 可能是数组或对象
      if (Array.isArray(indexData)) {
        // 转换为后端期望的格式
        const convertedData = convertToDataRecords(indexData)
        upstreamDataList.push(...convertedData)
        symbols.push(...indexData.map((d: any) => d.symbol || d.symbol))
      } else if (indexData.symbols) {
        const convertedData = convertToDataRecords([indexData])
        upstreamDataList.push(...convertedData)
        symbols.push(...indexData.symbols)
      } else {
        // 如果data是一个对象，尝试直接使用
        console.log('[DataCleaningNode] indexData是对象，尝试直接使用:', indexData)
        const convertedData = convertToDataRecords([indexData])
        upstreamDataList.push(...convertedData)
        if (indexData.symbol) {
          symbols.push(indexData.symbol)
        }
      }

      // 获取上游节点的频率信息
      if (indexNode.data?.metadata?.frequencies) {
        console.log('[DataCleaningNode] 从指数节点metadata获取频率:', indexNode.data.metadata.frequencies)
        frequencies.push(...indexNode.data.metadata.frequencies)
      } else if (indexNode.params?.frequencies) {
        console.log('[DataCleaningNode] 从指数节点params获取频率:', indexNode.params.frequencies)
        frequencies.push(...indexNode.params.frequencies)
      } else if (indexNode.params?.frequency) {
        frequencies.push(indexNode.params.frequency)
      }
    }

    // 去重频率列表
    frequencies = [...new Set(frequencies)]
    console.log('[DataCleaningNode] 检测到的上游频率:', frequencies)
    console.log('[DataCleaningNode] 获取到的symbols:', symbols)
    console.log('[DataCleaningNode] 获取到的data数量:', upstreamDataList.length)

    if (symbols.length === 0) {
      return { success: false, errors: ['上游节点没有数据'] }
    }

    // 更新状态为转换中
    node.data.content.conversionStatus = 'converting'
    node.data.content.stockCount = symbols.length

    // 🔧 修复：使用时间同步服务中的日期范围
    const syncedStartDate = timeRangeSyncState.syncedTimeRange?.startDate || node.params?.startDate
    const syncedEndDate = timeRangeSyncState.syncedTimeRange?.endDate || node.params?.endDate

    console.log(`[DataCleaningNode] 使用同步的日期范围: ${syncedStartDate} 至 ${syncedEndDate}`)

    const api_endpoint = node.metadata?.api_endpoint || `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8010/api/v1'}/data-cleaning/clean`

    // 构建请求参数 - 传递上游的数据，让后端从数据中提取frequency列
    const request_params: any = {
      node_id: node.id || 'data-cleaning',
      data: upstreamDataList,  // 🔧 修复：传递上游数据（包含多频率信息）
      stock_codes: symbols,
      start_date: syncedStartDate,
      end_date: syncedEndDate,
      // 如果上游没有频率信息，使用本地配置
      frequency: frequencies.length > 0 ? undefined : (node.params?.frequency || 'daily'),
      frequencies: frequencies.length > 0 ? frequencies : undefined,
      config: {
        quality_assessment: {
          enabled: true,
          completeness_threshold: 1 - (node.params?.maxMissingRatio ?? 0.3),
          accuracy_threshold: 0.98,
          consistency_threshold: 0.90,
          timeliness_threshold: 0.85
        },
        data_cleaning: {
          remove_duplicates: true,
          handle_missing: {
            strategy: 'interpolate',  // 🔧 修复：默认使用插值，不要删除数据
            threshold: node.params?.maxMissingRatio ?? 0.3
          },
          outlier_detection: {
            method: 'percentage_change',  // 🔧 使用涨跌幅百分比方法，只有超过20%才算异常
            threshold: 0.20,  // 20%阈值
            action: 'cap'
          },
          data_normalization: {
            method: node.params?.normalize ? 'z_score' : 'none',
            features: ['price', 'volume', 'returns']
          }
        }
      }
    }

    const response = await fetch(api_endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request_params)
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const result = await response.json()

    // 后端返回格式: { code: 200, message: "...", data: {...} }
    // 兼容处理: 支持 code: 200 或 success: true
    const isSuccess = result.success === true || result.code === 200

    if (!isSuccess) {
      throw new Error(result.detail || result.message || '转换失败')
    }

    // 🔧 修复：解析"转换后的数据库报告"
    // 后端返回的是清洗后保存到数据库的数据统计
    const responseData = result.data || result
    const databaseReport = (responseData as any).database_report || {}
    const statistics = (responseData as any).statistics || {}

    // 🔧 调试：详细打印后端返回的数据结构
    console.log('[DataCleaningNode] ===== 后端返回数据结构 =====')
    console.log('[DataCleaningNode] responseData 键:', Object.keys(responseData))
    console.log('[DataCleaningNode] quality_report 存在:', 'quality_report' in responseData)
    console.log('[DataCleaningNode] issue_analysis 存在:', 'issue_analysis' in responseData)

    const qualityReport = (responseData as any).quality_report
    if (qualityReport) {
      console.log('[DataCleaningNode] quality_report 类型:', typeof qualityReport)
      console.log('[DataCleaningNode] quality_report 键:', Object.keys(qualityReport))
      console.log('[DataCleaningNode] quality_report.issue_analysis 存在:', 'issue_analysis' in qualityReport)

      if (qualityReport.issue_analysis) {
        console.log('[DataCleaningNode] issue_analysis.missing_values 存在:', 'missing_values' in qualityReport.issue_analysis)
        if (qualityReport.issue_analysis.missing_values) {
          const byColumn = qualityReport.issue_analysis.missing_values.by_column
          console.log('[DataCleaningNode] by_column 值:', byColumn)
          console.log('[DataCleaningNode] by_column 类型:', typeof byColumn)
          console.log('[DataCleaningNode] by_column 长度/大小:', byColumn ? Object.keys(byColumn).length : 0)
        }
      }
    }

    console.log('[DataCleaningNode] 后端返回的数据库报告:', databaseReport)
    console.log('[DataCleaningNode] 后端返回的统计信息:', statistics)
    console.log('[DataCleaningNode] ================================')

    // 🔧 修复：使用 overall_quality_score（综合质量评分）而不是 statistics.quality_score（数据保留率）
    // overall_quality_score 是小数形式（0.995），需要转换为百分比（99.5）
    // databaseReport.quality_score 是百分比值（100），表示数据保留率
    const overallScore = (responseData as any).overall_quality_score ||
                        (responseData as any).quality_report?.overall_quality_score
    const dataRetentionScore = databaseReport.quality_score || statistics.quality_score

    // 优先使用综合质量评分（小数形式），如果没有则使用数据保留率（百分比值/100）
    const qualityScoreValue = overallScore !== undefined ? overallScore : (dataRetentionScore !== undefined ? dataRetentionScore / 100 : 0.95)

    // 更新显示内容 - 使用"转换后的数据库报告"
    node.data.content = {
      conversionStatus: 'completed',

      // 🔧 修复：使用计算后的质量评分
      qualityScore: qualityScoreValue,

      completeness: (responseData as any).completeness || 95,
      accuracy: (responseData as any).accuracy || 98,
      consistency: (responseData as any).consistency || 92,

      // 🔧 使用统计信息中的实际数值
      originalRows: databaseReport.original_rows || statistics.original_rows || (responseData as any).original_rows || 0,
      cleanedRows: databaseReport.cleaned_rows || statistics.cleaned_rows || (responseData as any).cleaned_rows || 0,
      originalColumns: databaseReport.original_columns || statistics.original_columns || (responseData as any).original_columns || 8,

      // 🔧 清洗过程中处理的问题数量
      missingCount: databaseReport.handled_missing || statistics.handled_missing || (responseData as any).missing_count || 0,
      duplicateCount: databaseReport.removed_duplicates || statistics.removed_duplicates || (responseData as any).duplicate_count || 0,
      outlierCount: databaseReport.handled_outliers || statistics.handled_outliers || (responseData as any).outlier_count || 0,
      removedInvalid: databaseReport.removed_invalid || statistics.removed_invalid || 0,

      // 其他信息
      stockCount: symbols.length,
      indexCount: indexNode ? (indexNode.params?.indexCode || '').split(/[,，\n]/).length : 0,
      dateRange: (responseData as any).date_range || `${syncedStartDate} ~ ${syncedEndDate}`,
      dataPath: node.params?.qlibDataPath || 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
      storageSize: (responseData as any).storage_size || 0,
      storageTime: (responseData as any).storage_time || new Date().toISOString(),

      // 🔧 新增：保存完整的质量报告，包括各列的缺失值统计
      qualityReport: (responseData as any).quality_report || null
    }

    node.description = `已转换 ${symbols.length} 只标的`

    console.log('[DataCleaningNode] 节点内容已更新:', node.data.content)

    return {
      success: true,
      data: {
        qlib_data_path: node.params?.qlibDataPath,
        symbols: symbols,
        quality_report: (responseData as any).quality_report,
        database_report: databaseReport,
        statistics: statistics
      },
      message: `成功转换 ${symbols.length} 只标的为QLib格式`
    }
  } catch (error: any) {
    console.error('[DataCleaningNode] 转换失败:', error)

    node.data.content.conversionStatus = 'failed'

    return {
      success: false,
      errors: [error.message]
    }
  }
}

/**
 * 获取数据（执行转换）
 */
export async function fetchData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  return await convertToQLibFormat(node, context)
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  if (!params.qlibDataPath) {
    errors.push('请设置QLib数据保存路径')
  }

  if (params.maxMissingRatio !== undefined) {
    const ratio = parseFloat(params.maxMissingRatio)
    if (isNaN(ratio) || ratio < 0 || ratio > 1) {
      errors.push('最大缺失比例必须在0-1之间')
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}
