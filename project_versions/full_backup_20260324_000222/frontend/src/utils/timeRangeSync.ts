/**
 * 时间范围联动服务
 *
 * 用于在股票选择节点和指数选择节点之间同步时间范围和频率配置,
 * 确保数据清洗节点能够正常处理相同时段的数据。
 */

import { reactive } from 'vue'

export interface TimeRangeConfig {
  timeRange: string      // 预设时间范围，如 '1W', '3M', '1Y'
  startDate: string      // 开始日期 YYYY-MM-DD
  endDate: string        // 结束日期 YYYY-MM-DD
  frequencies?: string[] // 数据频率，如 ['daily', '60min']
}

export interface TimeRangeSyncState {
  enabled: boolean       // 是否启用联动
  masterNode: 'stock' | 'index' | null  // 主节点，null表示自动
  stockTimeRange: TimeRangeConfig
  indexTimeRange: TimeRangeConfig
  syncedTimeRange: TimeRangeConfig  // 联动后的统一时间范围
  stockFrequencies: string[]         // 股票节点的频率
  indexFrequencies: string[]         // 指数节点的频率
  syncedFrequencies: string[]        // 联动后的统一频率
}

// 创建全局响应式状态
const syncState = reactive<TimeRangeSyncState>({
  enabled: true,  // 默认启用联动
  masterNode: null,  // 自动选择主节点(最后修改的节点为主节点)
  stockTimeRange: {
    timeRange: '3M',
    startDate: '',
    endDate: ''
  },
  indexTimeRange: {
    timeRange: '3M',
    startDate: '',
    endDate: ''
  },
  syncedTimeRange: {
    timeRange: '3M',
    startDate: '',
    endDate: ''
  },
  stockFrequencies: ['daily'],
  indexFrequencies: ['daily'],
  syncedFrequencies: ['daily']
})

// 监听器集合
const listeners: Set<(config: TimeRangeConfig) => void> = new Set()
const frequencyListeners: Set<(frequencies: string[]) => void> = new Set()

/**
 * 时间范围联动服务类
 */
class TimeRangeSyncService {
  /**
   * 更新股票节点的时间范围
   */
  updateStockTimeRange(config: TimeRangeConfig) {
    console.log(`[TimeRangeSync] updateStockTimeRange 被调用:`, config)
    syncState.stockTimeRange = { ...config }

    // 如果包含频率信息,同步频率
    if (config.frequencies) {
      this.updateStockFrequencies(config.frequencies)
    }

    if (syncState.enabled) {
      // 设置为主节点
      syncState.masterNode = 'stock'
      // 同步到统一时间范围
      syncState.syncedTimeRange = { ...config }
      // 同步到指数节点
      syncState.indexTimeRange = { ...config }
      // 通知所有监听器
      console.log(`[TimeRangeSync] 当前监听器数量: ${listeners.size}`)
      this.notifyListeners('stock', config)
    } else {
      console.log(`[TimeRangeSync] 联动已禁用,跳过同步`)
    }
  }

  /**
   * 更新指数节点的时间范围
   */
  updateIndexTimeRange(config: TimeRangeConfig) {
    syncState.indexTimeRange = { ...config }

    // 如果包含频率信息,同步频率
    if (config.frequencies) {
      this.updateIndexFrequencies(config.frequencies)
    }

    if (syncState.enabled) {
      // 设置为主节点
      syncState.masterNode = 'index'
      // 同步到统一时间范围
      syncState.syncedTimeRange = { ...config }
      // 同步到股票节点
      syncState.stockTimeRange = { ...config }
      // 通知所有监听器
      this.notifyListeners('index', config)
    }
  }

  /**
   * 更新股票节点的频率
   */
  updateStockFrequencies(frequencies: string[]) {
    console.log(`[TimeRangeSync] updateStockFrequencies 被调用:`, frequencies)
    syncState.stockFrequencies = [...frequencies]

    if (syncState.enabled) {
      // 设置为主节点
      syncState.masterNode = 'stock'
      // 同步到统一频率
      syncState.syncedFrequencies = [...frequencies]
      // 同步到指数节点
      syncState.indexFrequencies = [...frequencies]
      // 通知所有频率监听器
      console.log(`[TimeRangeSync] 当前频率监听器数量: ${frequencyListeners.size}`)
      this.notifyFrequencyListeners('stock', frequencies)
    }
  }

  /**
   * 更新指数节点的频率
   */
  updateIndexFrequencies(frequencies: string[]) {
    console.log(`[TimeRangeSync] updateIndexFrequencies 被调用:`, frequencies)
    syncState.indexFrequencies = [...frequencies]

    if (syncState.enabled) {
      // 设置为主节点
      syncState.masterNode = 'index'
      // 同步到统一频率
      syncState.syncedFrequencies = [...frequencies]
      // 同步到股票节点
      syncState.stockFrequencies = [...frequencies]
      // 通知所有频率监听器
      this.notifyFrequencyListeners('index', frequencies)
    }
  }

  /**
   * 通知所有监听器
   */
  private notifyListeners(_source: 'stock' | 'index', config: TimeRangeConfig) {
    listeners.forEach(listener => {
      try {
        listener(config)
      } catch (error) {
        console.error('[TimeRangeSync] 监听器执行失败:', error)
      }
    })
  }

  /**
   * 通知所有频率监听器
   */
  private notifyFrequencyListeners(_source: 'stock' | 'index', frequencies: string[]) {
    frequencyListeners.forEach(listener => {
      try {
        listener(frequencies)
      } catch (error) {
        console.error('[TimeRangeSync] 频率监听器执行失败:', error)
      }
    })
  }

  /**
   * 订阅时间范围变化
   * @param callback 回调函数，接收新的时间范围配置
   * @returns 取消订阅的函数
   */
  subscribe(callback: (config: TimeRangeConfig) => void): () => void {
    listeners.add(callback)

    // 返回取消订阅函数
    return () => {
      listeners.delete(callback)
    }
  }

  /**
   * 订阅频率变化
   * @param callback 回调函数，接收新的频率数组
   * @returns 取消订阅的函数
   */
  subscribeFrequencies(callback: (frequencies: string[]) => void): () => void {
    frequencyListeners.add(callback)

    // 返回取消订阅函数
    return () => {
      frequencyListeners.delete(callback)
    }
  }

  /**
   * 启用或禁用联动
   */
  setEnabled(enabled: boolean) {
    syncState.enabled = enabled

    if (enabled) {
      // 启用联动时，使用当前主节点的配置
      const masterConfig = syncState.masterNode === 'stock'
        ? syncState.stockTimeRange
        : syncState.indexTimeRange

      syncState.syncedTimeRange = { ...masterConfig }

      // 如果没有明确的主节点，使用股票节点的配置
      if (!syncState.masterNode) {
        syncState.masterNode = 'stock'
        syncState.syncedTimeRange = { ...syncState.stockTimeRange }
        syncState.indexTimeRange = { ...syncState.stockTimeRange }
      } else if (syncState.masterNode === 'stock') {
        syncState.indexTimeRange = { ...syncState.stockTimeRange }
      } else {
        syncState.stockTimeRange = { ...syncState.indexTimeRange }
      }
    }
  }

  /**
   * 设置主节点
   */
  setMasterNode(node: 'stock' | 'index' | null) {
    syncState.masterNode = node

    if (syncState.enabled && node) {
      const config = node === 'stock'
        ? syncState.stockTimeRange
        : syncState.indexTimeRange

      syncState.syncedTimeRange = { ...config }

      // 同步到另一个节点
      if (node === 'stock') {
        syncState.indexTimeRange = { ...config }
      } else {
        syncState.stockTimeRange = { ...config }
      }
    }
  }

  /**
   * 获取当前同步状态
   */
  getState(): TimeRangeSyncState {
    return { ...syncState }
  }

  /**
   * 获取股票节点应该使用的时间范围
   */
  getStockTimeRange(): TimeRangeConfig {
    return syncState.enabled ? syncState.syncedTimeRange : syncState.stockTimeRange
  }

  /**
   * 获取指数节点应该使用的时间范围
   */
  getIndexTimeRange(): TimeRangeConfig {
    return syncState.enabled ? syncState.syncedTimeRange : syncState.indexTimeRange
  }

  /**
   * 重置所有配置
   */
  reset() {
    syncState.enabled = true
    syncState.masterNode = null
    syncState.stockTimeRange = {
      timeRange: '3M',
      startDate: '',
      endDate: ''
    }
    syncState.indexTimeRange = {
      timeRange: '3M',
      startDate: '',
      endDate: ''
    }
    syncState.syncedTimeRange = {
      timeRange: '3M',
      startDate: '',
      endDate: ''
    }
    syncState.stockFrequencies = ['daily']
    syncState.indexFrequencies = ['daily']
    syncState.syncedFrequencies = ['daily']
  }
}

// 导出单例实例
export const timeRangeSyncService = new TimeRangeSyncService()

// 导出响应式状态，用于在Vue组件中直接访问
export { syncState as timeRangeSyncState }

// 格式化日期为本地日期字符串（YYYY-MM-DD）
export function formatDateToLocal(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 根据时间范围预设计算日期
export function calculateDateFromRange(timeRange: string): { startDate: string; endDate: string } {
  const endDate = new Date()
  const startDate = new Date(endDate)

  // 解析时间范围 (如 1W, 3M, 1Y)
  const match = timeRange.match(/^(\d+)([WMY])$/)
  if (match) {
    const value = parseInt(match[1])
    const unit = match[2]

    switch (unit) {
      case 'W':  // 周
        startDate.setDate(endDate.getDate() - value * 7)
        break
      case 'M':  // 月
        startDate.setMonth(endDate.getMonth() - value)
        break
      case 'Y':  // 年
        startDate.setFullYear(endDate.getFullYear() - value)
        break
    }
  } else {
    // 默认3个月
    startDate.setMonth(endDate.getMonth() - 3)
  }

  return {
    startDate: formatDateToLocal(startDate),
    endDate: formatDateToLocal(endDate)
  }
}
