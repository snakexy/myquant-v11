/**
 * 数据清洗节点辅助函数
 *
 * 提供数据格式化和状态判断的工具函数
 */

import { dataManagementState } from '@/services/dataManagementService'

/**
 * 提取数量（如 "5 个" -> "5"）
 */
export function extractCount(value: string): string {
  if (!value) return '0'
  const match = value.match(/^(\d+)/)
  return match ? match[1] : '0'
}

/**
 * 提取单位（如 "5 个" -> "个"）
 */
export function extractUnit(value: string): string {
  if (!value) return ''
  const match = value.match(/\s+([^\d]+)$/)
  return match ? match[1] : ''
}

/**
 * 获取状态标签的CSS类
 */
export function getStatusTagClass(status: string): string {
  if (!status) return 'tag-pending'
  const str = String(status)
  if (str.includes('待获取') || str.includes('未配置')) return 'tag-pending'
  if (str.includes('已获取') || str.includes('全部成功') || str.includes('已配置')) return 'tag-success'
  if (str.includes('部分成功')) return 'tag-warning'
  return 'tag-default'
}

/**
 * 获取短状态标签
 */
export function getStatusShortLabel(status: string): string {
  if (!status) return '待配置'
  const str = String(status)
  if (str.includes('待获取')) return '待获取'
  if (str.includes('未配置')) return '未配置'
  if (str.includes('已配置')) return '已配置'
  if (str.includes('全部成功')) return '完成'
  if (str.includes('部分成功')) return '部分成功'
  if (str.includes('已获取')) return '已获取'
  return str
}

/**
 * 格式化数据条数显示
 */
export function formatDataCount(count: number): string {
  if (!count) return '0条'
  if (count >= 100000000) return (count / 100000000).toFixed(2) + '亿条'
  if (count >= 10000) return (count / 10000).toFixed(2) + '万条'
  return count + '条'
}

/**
 * 格式化日期范围显示
 * 🔧 修复：只显示日期部分，忽略时间部分
 */
export function formatDateRange(startDate: string, endDate: string): string {
  if (!startDate || !endDate || startDate === '--' || endDate === '--') return '--'
  
  // 🔧 修复：提取日期部分，忽略时间（如 "2025-07-07 10:30:00" -> "2025-07-07"）
  const extractDate = (dateStr: string) => {
    // 如果包含空格，只取日期部分
    if (dateStr.includes(' ')) {
      return dateStr.split(' ')[0]
    }
    return dateStr
  }
  
  const startClean = extractDate(startDate)
  const endClean = extractDate(endDate)
  
  // 简化日期格式，例如 "01-01 至 12-19"
  const start = startClean.split('-').slice(1).join('-')
  const end = endClean.split('-').slice(1).join('-')
  return `${start} 至 ${end}`
}

/**
 * 从节点获取频率显示（支持多频率）
 * 优先使用 metadata.frequenciesLabel，如果没有则使用 params.frequency
 */
export function getFrequencyFromParams(node: any): string {
  // 🔧 修复：优先使用 metadata.frequenciesLabel（支持多频率显示，如"日线+60分钟"）
  if (node.data?.metadata?.frequenciesLabel) {
    return node.data.metadata.frequenciesLabel
  }
  
  // 兼容旧逻辑：使用 params.frequency（单频率）
  const frequency = node.params?.frequency || 'daily'
  if (frequency === 'daily') return '日线'
  if (frequency === 'weekly') return '周线'
  if (frequency === 'monthly') return '月线'
  
  // 如果有 frequencies 数组，尝试组合显示
  if (node.params?.frequencies && Array.isArray(node.params.frequencies)) {
    const freqMap: Record<string, string> = {
      'day': '日线',
      'daily': '日线',
      '1min': '1分钟',
      '5min': '5分钟',
      '15min': '15分钟',
      '30min': '30分钟',
      '60min': '60分钟'
    }
    return node.params.frequencies.map((f: string) => freqMap[f] || f).join('+')
  }
  
  return frequency
}

/**
 * 小组件配置
 * 🔧 使用共享数据服务获取真实数据
 */
export const miniReportConfig = {
  cards: [
    {
      key: 'database-stocks',
      label: '已选数据标的',
      icon: 'chart-pie',
      iconClass: 'primary-gradient',
      getValue: (metadata: any, content: any) => {
        // 🔧 优先使用共享数据服务的 stockCount
        const sharedStockCount = dataManagementState.stockCount.value
        if (sharedStockCount > 0) {
          return `${sharedStockCount}个`
        }
        // 回退到 metadata 或 content 中的数据
        const count = metadata?.stockCount || metadata?.totalCount || content?.stockCount || 0
        return `${count}个`
      }
    },
    {
      key: 'total-records',
      label: '总数据量',
      icon: 'database',
      iconClass: 'success-gradient',
      getValue: (metadata: any, content: any) => {
        // 🔧 优先使用共享数据服务的 totalRecords
        const sharedTotalRecords = dataManagementState.totalRecords.value
        if (sharedTotalRecords > 0) {
          return formatDataCount(sharedTotalRecords)
        }
        // 回退到 metadata 或 content 中的数据
        return formatDataCount(metadata?.totalRecords || metadata?.totalDataPoints || content?.totalRecords || 0)
      }
    },
    {
      key: 'quality-score',
      label: '数据质量',
      icon: 'check-circle',
      iconClass: (metadata: any, content: any) => {
        // 🔧 优先使用共享数据服务的 freshnessScore
        const sharedScore = dataManagementState.freshnessScore.value
        const score = sharedScore > 0 ? sharedScore : (metadata?.qualityScore || metadata?.data_quality_score || content?.qualityScore || 0)
        if (score >= 90) return 'success-gradient'
        if (score >= 70) return 'warning-gradient'
        return 'danger-gradient'
      },
      getValue: (metadata: any, content: any) => {
        // 🔧 优先使用共享数据服务的 freshnessScore
        const sharedScore = dataManagementState.freshnessScore.value
        const score = sharedScore > 0 ? sharedScore : (metadata?.qualityScore || metadata?.data_quality_score || content?.qualityScore || 0)
        return `${score}%`
      }
    },
    {
      key: 'date-range',
      label: '时间范围',
      icon: 'calendar-alt',
      iconClass: 'info-gradient',
      getValue: (metadata: any, content: any) => {
        // 🔧 优先使用共享数据服务的 dateRange
        const sharedDateRange = dataManagementState.dateRange.value
        if (sharedDateRange && sharedDateRange !== '未知') {
          return sharedDateRange
        }
        // 回退到 metadata 或 content 中的数据
        if (metadata?.dateRange && metadata.dateRange !== '未配置' && metadata.dateRange !== '未设置') {
          return metadata.dateRange
        }
        if (content?.dateRange && content.dateRange !== '未配置' && content.dateRange !== '未设置') {
          return content.dateRange
        }
        return formatDateRange(metadata?.startDate, metadata?.endDate)
      }
    }
  ]
}
