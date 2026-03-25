/**
 * MyQuant v9.0.0 - Data Preloader
 * 数据预加载工具 - 提升用户体验
 */

import { apiClient } from '@/api/client'

export interface PreloadConfig {
  enable: boolean
  maxCacheSize: number // 最大缓存数量
  preloadCount: number // 预加载数量
  preloadTimeout: number // 预加载超时时间(ms)
}

export interface PreloadItem {
  symbol: string
  period: string
  timestamp: number
  data?: any
  status: 'pending' | 'loading' | 'success' | 'failed'
}

class DataPreloader {
  private cache: Map<string, PreloadItem> = new Map()
  private config: PreloadConfig = {
    enable: true,
    maxCacheSize: 50,
    preloadCount: 10,
    preloadTimeout: 5000
  }

  private pendingRequests: Set<string> = new Set()

  constructor() {
    this.loadFromStorage()
  }

  /**
   * 生成缓存键
   */
  private generateKey(symbol: string, period: string): string {
    return `${symbol}_${period}`
  }

  /**
   * 从本地存储加载配置
   */
  private loadFromStorage(): void {
    try {
      const saved = localStorage.getItem('data_preloader_config')
      if (saved) {
        this.config = { ...this.config, ...JSON.parse(saved) }
      }
    } catch (error) {
      console.warn('[DataPreloader] Failed to load config from storage:', error)
    }
  }

  /**
   * 保存配置到本地存储
   */
  private saveToStorage(): void {
    try {
      localStorage.setItem('data_preloader_config', JSON.stringify(this.config))
    } catch (error) {
      console.warn('[DataPreloader] Failed to save config to storage:', error)
    }
  }

  /**
   * 更新配置
   */
  updateConfig(config: Partial<PreloadConfig>): void {
    this.config = { ...this.config, ...config }
    this.saveToStorage()
  }

  /**
   * 获取缓存
   */
  get(symbol: string, period: string): PreloadItem | undefined {
    const key = this.generateKey(symbol, period)
    return this.cache.get(key)
  }

  /**
   * 检查是否已缓存
   */
  has(symbol: string, period: string): boolean {
    const key = this.generateKey(symbol, period)
    return this.cache.has(key)
  }

  /**
   * 添加到预加载队列
   */
  async preload(symbols: string[], period: string = 'day'): Promise<void> {
    if (!this.config.enable) {
      return
    }

    // 清理过期缓存
    this.cleanup()

    // 限制预加载数量
    const toPreload = symbols.slice(0, this.config.preloadCount)

    for (const symbol of toPreload) {
      const key = this.generateKey(symbol, period)

      // 跳过已缓存或正在加载的
      if (this.cache.has(key) || this.pendingRequests.has(key)) {
        continue
      }

      // 标记为待加载
      this.cache.set(key, {
        symbol,
        period,
        timestamp: Date.now(),
        status: 'pending'
      })

      // 异步加载
      this.loadSymbolData(symbol, period)
    }
  }

  /**
   * 加载单个股票数据
   */
  private async loadSymbolData(symbol: string, period: string): Promise<void> {
    const key = this.generateKey(symbol, period)

    // 防止重复请求
    if (this.pendingRequests.has(key)) {
      return
    }

    this.pendingRequests.add(key)

    // 更新状态为加载中
    const item = this.cache.get(key)
    if (item) {
      item.status = 'loading'
    }

    try {
      // 设置超时
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Preload timeout')), this.config.preloadTimeout)
      })

      // 请求数据
      const dataPromise = apiClient.get(`/api/stocks/${symbol}/kline?period=${period}&count=100`)

      const response = await Promise.race([dataPromise, timeoutPromise]) as any

      // 更新缓存
      if (item && response.data) {
        item.data = response.data
        item.status = 'success'
        item.timestamp = Date.now()
      }
    } catch (error) {
      console.warn(`[DataPreloader] Failed to preload ${symbol}:`, error)
      if (item) {
        item.status = 'failed'
      }
    } finally {
      this.pendingRequests.delete(key)

      // 清理缓存（如果超过最大数量）
      this.cleanup()
    }
  }

  /**
   * 清理过期缓存
   */
  private cleanup(): void {
    const now = Date.now()
    const maxAge = 5 * 60 * 1000 // 5分钟过期

    // 删除过期数据
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > maxAge) {
        this.cache.delete(key)
      }
    }

    // 如果缓存数量超过限制，删除最旧的
    if (this.cache.size > this.config.maxCacheSize) {
      const entries = Array.from(this.cache.entries())
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp)

      const toDelete = entries.slice(0, this.cache.size - this.config.maxCacheSize)
      for (const [key] of toDelete) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear()
    this.pendingRequests.clear()
  }

  /**
   * 获取缓存统计
   */
  getStats(): { total: number; success: number; failed: number; loading: number; pending: number } {
    const stats = {
      total: this.cache.size,
      success: 0,
      failed: 0,
      loading: 0,
      pending: 0
    }

    for (const item of this.cache.values()) {
      stats[item.status]++
    }

    return stats
  }

  /**
   * 预加载热门股票
   */
  async preloadHotStocks(): Promise<void> {
    const hotStocks = [
      '600519', // 贵州茅台
      '000858', // 五粮液
      '600036', // 招商银行
      '000001', // 平安银行
      '601318', // 中国平安
      '000333', // 美的集团
      '600276', // 恒瑞医药
      '300750', // 宁德时代
      '601012', // 隆基绿能
      '600900'  // 长江电力
    ]

    await this.preload(hotStocks, 'day')
  }

  /**
   * 预加载指数
   */
  async preloadIndices(): Promise<void> {
    const indices = [
      '000001', // 上证指数
      '399001', // 深证成指
      '399006', // 创业板指
      '000300', // 沪深300
      '000016', // 上证50
      '399905'  // 中证500
    ]

    await this.preload(indices, 'day')
  }

  /**
   * 智能预加载 - 根据用户行为预测
   */
  async smartPreload(currentSymbol: string, allSymbols: string[]): Promise<void> {
    if (!this.config.enable) {
      return
    }

    // 找到当前股票在列表中的位置
    const currentIndex = allSymbols.findIndex(s => s === currentSymbol)
    if (currentIndex === -1) {
      return
    }

    // 预加载前后各2只股票
    const toPreload: string[] = []
    for (let i = 1; i <= 2; i++) {
      if (currentIndex - i >= 0) {
        toPreload.push(allSymbols[currentIndex - i])
      }
      if (currentIndex + i < allSymbols.length) {
        toPreload.push(allSymbols[currentIndex + i])
      }
    }

    await this.preload(toPreload, 'day')
  }
}

// 创建单例
export const dataPreloader = new DataPreloader()

// 导出类型
export type { PreloadConfig, PreloadItem }
