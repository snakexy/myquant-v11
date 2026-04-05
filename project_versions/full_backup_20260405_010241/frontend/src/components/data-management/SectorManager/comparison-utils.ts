/**
 * 板块对比工具函数
 */

import type { SectorNode, SectorBasicInfo } from '@/components/data-management/shared/types'

// ==================== 类型定义 ====================

export interface ComparisonMetric {
  label: string
  key: keyof SectorBasicInfo
  value: any
  formatted: string
  better: 'higher' | 'lower' | 'none'  // 值越高越好/越低越好/无差异
}

export interface SectorComparisonData {
  sector: SectorNode
  info: SectorBasicInfo
  metrics: ComparisonMetric[]
}

export interface ComparisonResult {
  sectors: SectorComparisonData[]
  timestamp: string
}

// ==================== 工具函数 ====================

/**
 * 格式化涨跌幅
 */
function formatChangePercent(value: number): string {
  if (value === undefined || value === null) return '-'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

/**
 * 格式化成交额
 */
function formatAmount(amount: string | number): string {
  if (!amount || amount === '-') return '-'
  if (typeof amount === 'string') return amount

  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toString()
}

/**
 * 创建对比指标
 */
function createComparisonMetrics(
  info: SectorBasicInfo
): ComparisonMetric[] {
  return [
    {
      label: '涨跌幅',
      key: 'changePercent',
      value: info.changePercent || 0,
      formatted: formatChangePercent(info.changePercent || 0),
      better: 'higher'
    },
    {
      label: '成分股数量',
      key: 'stockCount',
      value: info.stockCount || 0,
      formatted: `${info.stockCount || 0} 只`,
      better: 'none'
    },
    {
      label: '成交额',
      key: 'amount',
      value: info.amount || '',
      formatted: formatAmount(info.amount || ''),
      better: 'higher'
    },
    {
      label: '换手率',
      key: 'turnoverRate',
      value: info.turnoverRate || '',
      formatted: info.turnoverRate || '-',
      better: 'higher'
    }
  ]
}

/**
 * 创建板块对比数据
 */
export function createSectorComparisonData(
  sector: SectorNode,
  info: SectorBasicInfo
): SectorComparisonData {
  return {
    sector,
    info,
    metrics: createComparisonMetrics(info)
  }
}

/**
 * 对比多个板块
 */
export function compareSectors(
  sectors: Array<{ node: SectorNode; info: SectorBasicInfo }>
): ComparisonResult {
  return {
    sectors: sectors.map(({ node, info }) => createSectorComparisonData(node, info)),
    timestamp: new Date().toISOString()
  }
}

/**
 * 获取最优板块（根据某个指标）
 */
export function getBestSector(
  comparison: ComparisonResult,
  metricKey: keyof SectorBasicInfo
): SectorComparisonData | null {
  const metric = comparison.sectors[0]?.metrics.find(m => m.key === metricKey)
  if (!metric || metric.better === 'none') return null

  let best = comparison.sectors[0]

  comparison.sectors.forEach(sector => {
    const sectorMetric = sector.metrics.find(m => m.key === metricKey)
    if (!sectorMetric) return

    if (metric.better === 'higher') {
      if (sectorMetric.value > best.metrics.find(m => m.key === metricKey)!.value) {
        best = sector
      }
    } else if (metric.better === 'lower') {
      if (sectorMetric.value < best.metrics.find(m => m.key === metricKey)!.value) {
        best = sector
      }
    }
  })

  return best
}

/**
 * 获取雷达图数据
 */
export function getRadarChartData(comparison: ComparisonResult): {
  categories: string[]
  series: Array<{ name: string; value: number[] }>
} {
  if (comparison.sectors.length === 0) {
    return { categories: [], series: [] }
  }

  // 获取所有指标类别
  const categories = comparison.sectors[0].metrics.map(m => m.label)

  // 为每个板块创建数据系列
  // 需要标准化数据到0-100范围
  const allValues: Record<string, number[]> = {}

  comparison.sectors.forEach(sector => {
    const values: number[] = []

    sector.metrics.forEach((metric, index) => {
      let normalizedValue = 0

      if (metric.key === 'changePercent') {
        // 涨跌幅: -10% ~ +10% 映射到 0 ~ 100
        normalizedValue = Math.max(0, Math.min(100, (metric.value + 10) * 5))
      } else if (metric.key === 'stockCount') {
        // 成分股数量: 0 ~ 400 映射到 0 ~ 100
        normalizedValue = Math.min(100, (metric.value / 400) * 100)
      } else if (metric.key === 'amount') {
        // 成交额: 简化处理
        normalizedValue = 50  // 默认中值
      } else if (metric.key === 'turnoverRate') {
        // 换手率: 0% ~ 20% 映射到 0 ~ 100
        const rate = parseFloat(metric.value) || 0
        normalizedValue = Math.min(100, rate * 5)
      } else {
        normalizedValue = 50  // 默认中值
      }

      values.push(normalizedValue)
    })

    allValues[sector.sector.name] = values
  })

  const series = Object.entries(allValues).map(([name, value]) => ({
    name,
    value
  }))

  return { categories, series }
}

/**
 * 获取柱状图数据
 */
export function getBarChartData(
  comparison: ComparisonResult,
  metricKey: keyof SectorBasicInfo
): {
  categories: string[]
  values: number[]
  colors: string[]
} {
  const categories: string[] = []
  const values: number[] = []
  const colors: string[] = []

  comparison.sectors.forEach(sector => {
    const metric = sector.metrics.find(m => m.key === metricKey)
    if (!metric) return

    categories.push(sector.sector.name)
    values.push(metric.value as number)

    // 根据数值正负设置颜色
    if (metricKey === 'changePercent') {
      if (metric.value > 0) {
        colors.push('#f56c6c')  // 红色（涨）
      } else if (metric.value < 0) {
        colors.push('#67c23a')  // 绿色（跌）
      } else {
        colors.push('#909399')  // 灰色（平）
      }
    } else {
      colors.push('#409eff')  // 蓝色（默认）
    }
  })

  return { categories, values, colors }
}

/**
 * 验证对比数据
 */
export function validateComparisonData(
  sectors: SectorNode[],
  infos: SectorBasicInfo[]
): { valid: boolean; message: string } {
  if (sectors.length < 2) {
    return { valid: false, message: '请至少选择2个板块进行对比' }
  }

  if (sectors.length > 4) {
    return { valid: false, message: '最多支持4个板块同时对比' }
  }

  if (sectors.length !== infos.length) {
    return { valid: false, message: '板块数据不完整' }
  }

  return { valid: true, message: '' }
}
