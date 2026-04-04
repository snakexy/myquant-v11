/**
 * MyQuant v9.0.0 - Performance Optimization Composable
 * 性能优化组合式函数
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { dataPreloader, type PreloadConfig } from '@/utils/dataPreloader'
import { wsReconnection, type ReconnectionConfig } from '@/utils/websocketReconnection'
import { globalDebouncer, REQUEST_DELAYS, debounce, throttle } from '@/utils/debounce'

export interface PerformanceConfig {
  preloader: PreloadConfig
  reconnection: ReconnectionConfig
  enable: boolean
}

export interface PerformanceStats {
  preloader: {
    total: number
    success: number
    failed: number
    loading: number
    pending: number
  }
  reconnection: {
    attempt: number
    isRetrying: boolean
    timeUntilNext: number
    successRate: number
  }
}

export function usePerformance() {
  const enabled = ref(true)
  const stats = ref<PerformanceStats | null>(null)

  let updateInterval: ReturnType<typeof setInterval> | null = null

  /**
   * 更新统计信息
   */
  const updateStats = () => {
    if (!enabled.value) {
      return
    }

    stats.value = {
      preloader: dataPreloader.getStats(),
      reconnection: wsReconnection.getStats()
    }
  }

  /**
   * 启用性能优化
   */
  const enable = () => {
    enabled.value = true
    dataPreloader.updateConfig({ enable: true })
    wsReconnection.updateConfig({ enable: true })
  }

  /**
   * 禁用性能优化
   */
  const disable = () => {
    enabled.value = false
    dataPreloader.updateConfig({ enable: false })
    wsReconnection.updateConfig({ enable: false })
  }

  /**
   * 预加载数据
   */
  const preload = async (symbols: string[], period: string = 'day') => {
    if (!enabled.value) {
      return
    }

    return await dataPreloader.preload(symbols, period)
  }

  /**
   * 智能预加载
   */
  const smartPreload = async (currentSymbol: string, allSymbols: string[]) => {
    if (!enabled.value) {
      return
    }

    return await dataPreloader.smartPreload(currentSymbol, allSymbols)
  }

  /**
   * 预加载热门股票
   */
  const preloadHotStocks = async () => {
    if (!enabled.value) {
      return
    }

    return await dataPreloader.preloadHotStocks()
  }

  /**
   * 预加载指数
   */
  const preloadIndices = async () => {
    if (!enabled.value) {
      return
    }

    return await dataPreloader.preloadIndices()
  }

  /**
   * 获取缓存数据
   */
  const getCachedData = (symbol: string, period: string = 'day') => {
    return dataPreloader.get(symbol, period)
  }

  /**
   * 检查是否已缓存
   */
  const hasCachedData = (symbol: string, period: string = 'day'): boolean => {
    return dataPreloader.has(symbol, period)
  }

  /**
   * 清空缓存
   */
  const clearCache = () => {
    dataPreloader.clear()
    updateStats()
  }

  /**
   * 更新配置
   */
  const updateConfig = (config: Partial<PerformanceConfig>) => {
    if (config.preloader) {
      dataPreloader.updateConfig(config.preloader)
    }

    if (config.reconnection) {
      wsReconnection.updateConfig(config.reconnection)
    }

    if (config.enable !== undefined) {
      enabled.value = config.enable
      dataPreloader.updateConfig({ enable: config.enable })
      wsReconnection.updateConfig({ enable: config.enable })
    }
  }

  /**
   * 防抖执行
   */
  const debounceCall = <T extends (...args: any[]) => ReturnType<T>>(
    key: string,
    func: T,
    delay?: number
  ): ((...args: Parameters<T>) => ReturnType<T>) => {
    return debounce(func, delay ?? globalDebouncer.getDelay(key))
  }

  /**
   * 节流执行
   */
  const throttleCall = <T extends (...args: any[]) => ReturnType<T>>(
    key: string,
    func: T,
    delay?: number
  ): ((...args: Parameters<T>) => ReturnType<T>) => {
    return throttle(func, delay ?? globalDebouncer.getDelay(key))
  }

  /**
   * WebSocket重连
   */
  const scheduleReconnect = () => {
    if (!enabled.value) {
      return Promise.reject(new Error('Performance optimization disabled'))
    }

    return wsReconnection.scheduleReconnect()
  }

  /**
   * 重置重连状态
   */
  const resetReconnection = () => {
    wsReconnection.reset()
    updateStats()
  }

  /**
   * 获取性能建议
   */
  const getPerformanceTips = (): string[] => {
    const tips: string[] = []
    const currentStats = stats.value

    if (!currentStats) {
      return ['性能统计尚未初始化']
    }

    // 预加载建议
    if (currentStats.preloader.failed > currentStats.preloader.success * 0.5) {
      tips.push('预加载失败率较高，建议检查网络连接或减少预加载数量')
    }

    if (currentStats.preloader.total < 10) {
      tips.push('缓存数据较少，建议启用智能预加载以提升浏览体验')
    }

    // WebSocket建议
    if (currentStats.reconnection.attempt > 5) {
      tips.push('WebSocket重连次数较多，建议检查网络稳定性')
    }

    if (currentStats.reconnection.isRetrying) {
      tips.push(`WebSocket正在尝试重连，预计 ${Math.ceil(currentStats.reconnection.timeUntilNext / 1000)} 秒后完成`)
    }

    if (tips.length === 0) {
      tips.push('性能状态良好，无需优化')
    }

    return tips
  }

  // 生命周期钩子
  onMounted(() => {
    // 定期更新统计信息
    updateInterval = setInterval(updateStats, 5000)

    // 立即更新一次
    updateStats()
  })

  onUnmounted(() => {
    if (updateInterval) {
      clearInterval(updateInterval)
      updateInterval = null
    }
  })

  return {
    // 状态
    enabled,
    stats,

    // 配置
    enable,
    disable,
    updateConfig,

    // 预加载
    preload,
    smartPreload,
    preloadHotStocks,
    preloadIndices,

    // 缓存
    getCachedData,
    hasCachedData,
    clearCache,

    // 防抖/节流
    debounceCall,
    throttleCall,

    // WebSocket重连
    scheduleReconnect,
    resetReconnection,

    // 工具
    getPerformanceTips
  }
}

// 导出工具类和常量
export { dataPreloader, wsReconnection, globalDebouncer, REQUEST_DELAYS }
export type { PreloadConfig, ReconnectionConfig }
