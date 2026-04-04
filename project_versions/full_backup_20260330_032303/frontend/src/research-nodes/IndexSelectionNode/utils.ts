/**
 * 指数选择节点辅助函数
 *
 * 提供数据格式化和状态判断的工具函数
 */

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
 * 从表格数据获取指数数量
 */
export function getIndexCountFromTable(tableData: any[]): string {
  return String(tableData?.length || 0)
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
 * 🔧 重构：将小组件显示逻辑回归到节点组件中
 */
export const miniReportConfig = {
  cards: [
    {
      key: 'index-count',
      label: '指数数量',
      icon: 'chart-line',
      iconClass: 'primary-gradient',
      cardClass: 'highlight',
      getValue: (metadata: any, content: any) => {
        // 从表格内容获取指数数量
        const count = Array.isArray(content) ? content.length : 0
        return `${count}个`
      }
    },
    {
      key: 'total-data',
      label: '总数据量',
      icon: 'database',
      iconClass: 'success-gradient',
      getValue: (metadata: any) => {
        return formatDataCount(metadata?.totalDataPoints || 0)
      }
    },
    {
      key: 'frequency',
      label: '数据频率',
      icon: 'chart-bar',
      iconClass: 'purple-gradient',
      getValue: (metadata: any, content: any, params: any) => {
        // 优先使用 metadata.frequenciesLabel（已获取数据）
        if (metadata?.frequenciesLabel) {
          return metadata.frequenciesLabel
        }

        // 其次使用 metadata.frequency（已获取数据，旧格式）
        if (metadata?.frequency) {
          const freqMap: Record<string, string> = {
            'daily': '日线',
            'day': '日线',
            '60min': '60分钟',
            '30min': '30分钟',
            '15min': '15分钟',
            '5min': '5分钟',
            '1min': '1分钟'
          }
          return freqMap[metadata.frequency] || metadata.frequency
        }

        // 最后使用 params.frequencies 或 params.frequency（未获取数据时的配置）
        const freqMap: Record<string, string> = {
          'daily': '日线',
          'day': '日线',
          '60min': '60分钟',
          '30min': '30分钟',
          '15min': '15分钟',
          '5min': '5分钟',
          '1min': '1分钟'
        }

        // 多频率
        if (params?.frequencies && Array.isArray(params.frequencies)) {
          return params.frequencies.map((f: string) => freqMap[f] || f).join('+')
        }

        // 单频率
        if (params?.frequency) {
          return freqMap[params.frequency] || params.frequency
        }

        return '--'
      }
    },
    {
      key: 'status',
      label: '获取状态',
      icon: 'clock',  // 默认图标（未获取数据时）
      iconClass: (metadata: any) => {
        const success = metadata?.successCount || 0
        const total = metadata?.totalCount || 0
        // 未获取数据（totalCount === 0）时显示黄色警告
        if (total === 0) return 'warning-gradient'
        // 全部成功显示绿色
        if (success === total) return 'success-gradient'
        // 部分失败显示红色
        return 'danger-gradient'
      },
      cardClass: (metadata: any) => {
        const success = metadata?.successCount || 0
        const total = metadata?.totalCount || 0
        if (total === 0) return 'warning'
        if (success === total) return 'success'
        return 'danger'
      },
      getValue: (metadata: any) => {
        const success = metadata?.successCount || 0
        const total = metadata?.totalCount || 0
        if (total === 0) return '待获取'
        return `${success}/${total}`
      }
    },
    {
      key: 'date-range',
      label: '时间范围',
      icon: 'calendar-alt',
      iconClass: 'info-gradient',
      getValue: (metadata: any) => {
        return formatDateRange(metadata?.startDate, metadata?.endDate)
      }
    }
  ]
}
