/**
 * 数据管理模块 - 工具函数
 */

import type { MarketType, FrequencyType, DataStatus } from './types'
import { MARKET_CONFIG, FREQUENCY_CONFIG, DATA_STATUS_CONFIG } from './constants'

// ==================== 格式化函数 ====================

/**
 * 格式化数字为带千分位的字符串
 */
export function formatNumber(num: number): string {
  return num.toLocaleString()
}

/**
 * 格式化成交量
 */
export function formatVolume(volume: number): string {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

/**
 * 格式化成交额
 */
export function formatAmount(amount: number): string {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toString()
}

/**
 * 格式化时间秒数为可读字符串
 */
export function formatElapsedTime(seconds: number): string {
  if (seconds < 60) {
    return `${Math.floor(seconds)}秒`
  }
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${minutes}分${secs}秒`
}

/**
 * 格式化日期范围
 */
export function formatDateRange(start: string, end: string): string {
  return `${start} ~ ${end}`
}

// ==================== 数据转换函数 ====================

/**
 * 根据数据年龄计算状态
 */
export function calculateStatus(dataAgeDays: number): DataStatus {
  if (dataAgeDays === 0) return 'complete'
  if (dataAgeDays <= 3) return 'incomplete'
  return 'need_update'
}

/**
 * 根据完整度获取样式类
 */
export function getCompletenessClass(completeness: number): string {
  if (completeness >= 95) return 'success'
  if (completeness >= 80) return 'warning'
  return 'danger'
}

/**
 * 根据涨跌幅获取样式类
 */
export function getPriceChangeClass(changePercent: number): string {
  if (changePercent > 0) return 'up'
  if (changePercent < 0) return 'down'
  return 'neutral'
}

// ==================== 配置获取函数 ====================

/**
 * 获取市场类型配置
 */
export function getMarketConfig(market: MarketType) {
  return MARKET_CONFIG[market] || { label: market, tagType: '' }
}

/**
 * 获取频率标签
 */
export function getFrequencyLabel(freq: FrequencyType): string {
  return FREQUENCY_CONFIG[freq]?.label || freq
}

/**
 * 获取频率图标
 */
export function getFrequencyIcon(freq: FrequencyType): string {
  return FREQUENCY_CONFIG[freq]?.icon || 'clock'
}

/**
 * 获取数据状态标签
 */
export function getStatusLabel(status: DataStatus): string {
  return DATA_STATUS_CONFIG[status]?.label || status
}

/**
 * 获取数据状态类型
 */
export function getStatusType(status: DataStatus): string {
  return DATA_STATUS_CONFIG[status]?.type || ''
}

// ==================== 验证函数 ====================

/**
 * 验证股票代码格式
 */
export function validateStockCode(code: string): boolean {
  // A股股票代码：6位数字
  return /^\d{6}$/.test(code)
}

/**
 * 验证日期格式 (YYYY-MM-DD)
 */
export function validateDateFormat(date: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(date)
}

/**
 * 验证路径格式
 */
export function validatePath(path: string): boolean {
  // Windows 路径或 Unix 路径
  return /^[a-zA-Z]:\\|^[a-zA-Z]:\//.test(path) || path.startsWith('/')
}

// ==================== 数据处理函数 ====================

/**
 * 计算移动平均值
 */
export function calculateMA(data: number[], period: number): number[] {
  const result: number[] = []
  for (let i = period - 1; i < data.length; i++) {
    const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
    result.push(sum / period)
  }
  return result
}

/**
 * 计算涨跌幅
 */
export function calculateChangePercent(current: number, previous: number): number {
  if (previous === 0) return 0
  return ((current - previous) / previous) * 100
}

/**
 * 计算标准差
 */
export function calculateStdDev(data: number[]): number {
  const mean = data.reduce((sum, val) => sum + val, 0) / data.length
  const squareDiffs = data.map(val => Math.pow(val - mean, 2))
  return Math.sqrt(squareDiffs.reduce((sum, val) => sum + val, 0) / data.length)
}

/**
 * 计算健康度分数（基于数据完整性和新鲜度）
 */
export function calculateHealthScore(stock: any): number {
  let score = 100

  // 数据年龄扣分
  const age = stock.data_age_days || 0
  if (age > 30) {
    score -= 40
  } else if (age > 14) {
    score -= 20
  } else if (age > 7) {
    score -= 10
  }

  // 记录数扣分（少于100条认为不完整）
  const count = stock.record_count || 0
  if (count < 100) {
    score -= 30
  } else if (count < 500) {
    score -= 10
  }

  return Math.max(score, 0)
}

// ==================== 字符串处理函数 ====================

/**
 * 截断字符串
 */
export function truncateString(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength) + '...'
}

/**
 * 高亮搜索关键词
 */
export function highlightKeyword(text: string, keyword: string): string {
  if (!keyword) return text
  const regex = new RegExp(`(${keyword})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

// ==================== 数组处理函数 ====================

/**
 * 数组去重
 */
export function uniqueArray<T>(arr: T[]): T[] {
  return Array.from(new Set(arr))
}

/**
 * 数组分组
 */
export function groupBy<T>(arr: T[], key: keyof T): Record<string, T[]> {
  return arr.reduce((result, item) => {
    const groupKey = String(item[key])
    if (!result[groupKey]) {
      result[groupKey] = []
    }
    result[groupKey].push(item)
    return result
  }, {} as Record<string, T[]>)
}

/**
 * 数组排序
 */
export function sortBy<T>(arr: T[], key: keyof T, order: 'asc' | 'desc' = 'asc'): T[] {
  return [...arr].sort((a, b) => {
    const valA = a[key]
    const valB = b[key]
    if (valA < valB) return order === 'asc' ? -1 : 1
    if (valA > valB) return order === 'asc' ? 1 : -1
    return 0
  })
}

// ==================== 导出函数 ====================

/**
 * 导出数据为 CSV
 */
export function exportToCSV(data: any[], filename: string): void {
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(header => row[header]).join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}

/**
 * 导出数据为 JSON
 */
export function exportToJSON(data: any[], filename: string): void {
  const jsonContent = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.json`
  link.click()
  URL.revokeObjectURL(link.href)
}

// ==================== 防抖和节流 ====================

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return function(this: any, ...args: Parameters<T>) {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func.apply(this, args), wait)
  }
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let lastTime = 0
  return function(this: any, ...args: Parameters<T>) {
    const now = Date.now()
    if (now - lastTime >= wait) {
      lastTime = now
      func.apply(this, args)
    }
  }
}
