/**
 * MyQuant v9.0.0 - Frontend Data Cache Manager
 * 前端数据缓存管理器 - 提高性能和减少网络请求
 */

interface CacheItem<T = any> {
  data: T
  timestamp: number
  expires: number
}

interface CacheConfig {
  ttl: number  // Time to live in milliseconds
  maxSize: number  // Maximum cache size
}

class DataCacheManager {
  private cache: Map<string, CacheItem>
  private maxSize: number
  private defaultTTL: number

  constructor() {
    this.cache = new Map()
    this.maxSize = 100  // 默认最大缓存100项
    this.defaultTTL = 5 * 60 * 1000  // 默认5分钟过期

    // 从localStorage恢复缓存
    this.loadFromStorage()

    // 定期清理过期数据
    setInterval(() => this.cleanup(), 60 * 1000)  // 每分钟清理一次
  }

  /**
   * 生成缓存键
   */
  private generateKey(prefix: string, params: Record<string, any>): string {
    const sortedParams = Object.keys(params).sort()
    const paramString = sortedParams.map(key => `${key}=${params[key]}`).join('&')
    return `${prefix}:${paramString}`
  }

  /**
   * 设置缓存
   */
  set<T>(key: string, data: T, ttl?: number): void {
    // 检查缓存大小
    if (this.cache.size >= this.maxSize) {
      // 删除最旧的缓存项
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }

    const expires = Date.now() + (ttl || this.defaultTTL)

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      expires
    })

    // 持久化到localStorage
    this.saveToStorage()
  }

  /**
   * 获取缓存
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key)

    if (!item) {
      return null
    }

    // 检查是否过期
    if (Date.now() > item.expires) {
      this.cache.delete(key)
      return null
    }

    return item.data as T
  }

  /**
   * 删除缓存
   */
  delete(key: string): void {
    this.cache.delete(key)
    this.saveToStorage()
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear()
    this.saveToStorage()
  }

  /**
   * 清理过期缓存
   */
  private cleanup(): void {
    const now = Date.now()
    let cleaned = 0

    for (const [key, item] of this.cache.entries()) {
      if (now > item.expires) {
        this.cache.delete(key)
        cleaned++
      }
    }

    if (cleaned > 0) {
      console.log(`[Cache] Cleaned up ${cleaned} expired items`)
      this.saveToStorage()
    }
  }

  /**
   * 保存到localStorage
   */
  private saveToStorage(): void {
    try {
      const serialized = JSON.stringify(Array.from(this.cache.entries()))
      localStorage.setItem('myquant_cache', serialized)
    } catch (e) {
      console.warn('[Cache] Failed to save to localStorage:', e)
    }
  }

  /**
   * 从localStorage恢复
   */
  private loadFromStorage(): void {
    try {
      const serialized = localStorage.getItem('myquant_cache')
      if (serialized) {
        const entries = JSON.parse(serialized)
        this.cache = new Map(entries)
      }
    } catch (e) {
      console.warn('[Cache] Failed to load from localStorage:', e)
    }
  }

  /**
   * 获取缓存统计
   */
  getStats(): {
    size: number
    keys: string[]
    totalMemory: number
  } {
    const keys = Array.from(this.cache.keys())
    const serialized = JSON.stringify(Array.from(this.cache.entries()))

    return {
      size: this.cache.size,
      keys,
      totalMemory: new Blob([serialized]).size
    }
  }
}

// 全局缓存实例
const cacheManager = new DataCacheManager()

/**
 * 带缓存的fetch封装
 */
export async function cachedFetch<T = any>(
  key: string,
  fetcher: () => Promise<T>,
  ttl?: number
): Promise<T> {
  // 尝试从缓存获取
  const cached = cacheManager.get<T>(key)
  if (cached !== null) {
    console.log(`[Cache] Hit: ${key}`)
    return cached
  }

  // 缓存未命中，执行fetch
  console.log(`[Cache] Miss: ${key}`)
  const data = await fetcher()

  // 存入缓存
  cacheManager.set(key, data, ttl)

  return data
}

/**
 * K线数据缓存
 */
export function fetchKlineWithCache(symbol: string, period: string, count: number = 100) {
  const key = cacheManager.generateKey('kline', { symbol, period, count })
  const ttl = 60 * 1000  // K线数据缓存1分钟

  return cachedFetch(key, async () => {
    const response = await fetch(
      `/api/stock/${symbol}/kline?period=${period}&count=${count}`
    )
    const result = await response.json()
    return result
  }, ttl)
}

/**
 * 技术指标缓存
 */
export function fetchIndicatorsWithCache(
  symbol: string,
  period: string,
  indicators: string[],
  params?: Record<string, any>
) {
  const key = cacheManager.generateKey('indicators', {
    symbol,
    period,
    indicators: indicators.sort().join(','),
    ...params
  })
  const ttl = 60 * 1000  // 指标数据缓存1分钟

  return cachedFetch(key, async () => {
    const queryString = new URLSearchParams({
      symbol,
      period,
      indicators: indicators.join(','),
      ...params
    })

    const response = await fetch(`/api/indicators/all?${queryString}`)
    const result = await response.json()
    return result
  }, ttl)
}

/**
 * 板块数据缓存
 */
export function fetchSectorWithCache(endpoint: string, params?: Record<string, any>) {
  const key = cacheManager.generateKey(`sector_${endpoint}`, params || {})
  const ttl = 30 * 1000  // 板块数据缓存30秒

  return cachedFetch(key, async () => {
    const queryString = new URLSearchParams(params || {})
    const response = await fetch(`/api/sector/${endpoint}?${queryString}`)
    const result = await response.json()
    return result
  }, ttl)
}

/**
 * 板块历史数据缓存
 */
export function fetchSectorHistoryWithCache(
  sectorCode: string,
  days: number = 30
) {
  const key = cacheManager.generateKey('sector_history', { sectorCode, days })
  const ttl = 5 * 60 * 1000  // 历史数据缓存5分钟

  return cachedFetch(key, async () => {
    const response = await fetch(
      `/api/sector/history/${sectorCode}?days=${days}`
    )
    const result = await response.json()
    return result
  }, ttl)
}

/**
 * 清除特定类型的缓存
 */
export function clearCacheByPrefix(prefix: string): void {
  const stats = cacheManager.getStats()
  const keysToDelete = stats.keys.filter(key => key.startsWith(prefix))

  keysToDelete.forEach(key => cacheManager.delete(key))

  console.log(`[Cache] Cleared ${keysToDelete.length} items with prefix "${prefix}"`)
}

/**
 * 清除所有缓存
 */
export function clearAllCache(): void {
  cacheManager.clear()
  console.log('[Cache] Cleared all cache')
}

/**
 * 获取缓存统计
 */
export function getCacheStats() {
  return cacheManager.getStats()
}

export default cacheManager
