/**
 * IndexedDB K线缓存服务
 *
 * 功能：
 * - 持久化缓存自选股K线数据
 * - 支持增量恢复（记录 last_time）
 * - LRU清理 + 过期自动删除
 * - 容量限制（最多500条记录 ≈ 5MB）
 */

const DB_NAME = 'MyQuantKlineDB'
const DB_VERSION = 1
const STORE_KLINE = 'kline_data'
const STORE_META = 'metadata'

const MAX_RECORDS = 500    // 最多缓存500条记录
const EXPIRY_DAYS = 7      // 7天过期
const MAX_SYMBOLS = 100    // 最多100只股票

/** K线数据存储格式 */
export interface IDBKlineRecord {
  id: string               // key: "symbol:period" 如 "600519.SH:1d"
  symbol: string
  period: string
  data: Array<{
    time: number
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>
  meta: {
    lastTime: number       // 最后数据时间戳
    count: number          // 总条数
    dataSource: string     // 数据来源
    updatedAt: number      // 更新时间
  }
  accessedAt: number       // 最后访问时间（用于LRU）
}

/** 股票元数据 */
export interface IDBStockMeta {
  symbol: string
  periods: string[]        // 已缓存的周期列表
  lastAccessAt: number     // 最后访问时间
  totalRecords: number     // 该股票总记录数
}

/** 缓存统计 */
export interface IDBCacheStats {
  totalRecords: number
  totalSymbols: number
  totalSize: number        // 估算大小（MB）
  oldestRecord: number     // 最旧记录时间
}

let db: IDBDatabase | null = null

/**
 * 初始化 IndexedDB
 */
export async function initKlineDB(): Promise<IDBDatabase> {
  if (db) return db

  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onerror = () => reject(request.error)
    request.onsuccess = () => {
      db = request.result
      console.log('[IDB] 数据库初始化成功')
      resolve(db)
    }

    request.onupgradeneeded = (event) => {
      const database = (event.target as IDBOpenDBRequest).result

      // K线数据存储
      if (!database.objectStoreNames.contains(STORE_KLINE)) {
        const store = database.createObjectStore(STORE_KLINE, { keyPath: 'id' })
        store.createIndex('by_symbol', 'symbol', { unique: false })
        store.createIndex('by_period', 'period', { unique: false })
        store.createIndex('by_accessed', 'accessedAt', { unique: false })
        console.log('[IDB] 创建 kline_data 存储')
      }

      // 元数据存储
      if (!database.objectStoreNames.contains(STORE_META)) {
        const store = database.createObjectStore(STORE_META, { keyPath: 'symbol' })
        store.createIndex('by_access', 'lastAccessAt', { unique: false })
        console.log('[IDB] 创建 metadata 存储')
      }
    }
  })
}

/**
 * 保存K线数据
 */
export async function saveKlineData(
  symbol: string,
  period: string,
  data: IDBKlineRecord['data'],
  meta: IDBKlineRecord['meta']
): Promise<void> {
  const database = await initKlineDB()

  // 检查容量，必要时清理
  await checkAndCleanup(database)

  // 将 Proxy 对象转换为普通对象（避免 DataCloneError）
  const plainData = JSON.parse(JSON.stringify(data))

  const record: IDBKlineRecord = {
    id: `${symbol}:${period}`,
    symbol,
    period,
    data: plainData,
    meta,
    accessedAt: Date.now()
  }

  return new Promise((resolve, reject) => {
    const tx = database.transaction([STORE_KLINE, STORE_META], 'readwrite')

    // 保存K线数据
    const klineStore = tx.objectStore(STORE_KLINE)
    klineStore.put(record)

    // 更新元数据
    const metaStore = tx.objectStore(STORE_META)
    const metaRequest = metaStore.get(symbol)

    metaRequest.onsuccess = () => {
      const existing: IDBStockMeta | undefined = metaRequest.result
      const periods = existing ? [...new Set([...existing.periods, period])] : [period]

      metaStore.put({
        symbol,
        periods,
        lastAccessAt: Date.now(),
        totalRecords: periods.length
      })
    }

    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * 获取K线数据
 */
export async function getKlineData(
  symbol: string,
  period: string
): Promise<IDBKlineRecord | null> {
  const database = await initKlineDB()

  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_KLINE, 'readwrite')
    const store = tx.objectStore(STORE_KLINE)
    const request = store.get(`${symbol}:${period}`)

    request.onsuccess = () => {
      const record: IDBKlineRecord | undefined = request.result

      if (record) {
        // 更新访问时间（LRU）
        record.accessedAt = Date.now()
        store.put(record)

        // 检查是否过期
        const daysSinceUpdate = (Date.now() - record.meta.updatedAt) / (1000 * 60 * 60 * 24)
        if (daysSinceUpdate > EXPIRY_DAYS) {
          console.log(`[IDB] 数据已过期: ${symbol}:${period}`)
          resolve(null)
          return
        }
      }

      resolve(record || null)
    }
    request.onerror = () => reject(request.error)
  })
}

/**
 * 检查并清理缓存
 */
async function checkAndCleanup(database: IDBDatabase): Promise<void> {
  const tx = database.transaction(STORE_KLINE, 'readonly')
  const store = tx.objectStore(STORE_KLINE)
  const countRequest = store.count()

  return new Promise((resolve, reject) => {
    countRequest.onsuccess = async () => {
      const count = countRequest.result

      if (count >= MAX_RECORDS) {
        console.log(`[IDB] 缓存已满 (${count}/${MAX_RECORDS})，开始清理`)
        await performCleanup(database)
      }

      // 同时检查过期数据
      await cleanupExpired(database)

      resolve()
    }
    countRequest.onerror = () => reject(countRequest.error)
  })
}

/**
 * LRU清理：删除最久未访问的记录
 */
async function performCleanup(database: IDBDatabase): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_KLINE, 'readwrite')
    const store = tx.objectStore(STORE_KLINE)
    const index = store.index('by_accessed')

    // 获取最旧访问的记录
    const request = index.openCursor()
    let deleted = 0
    const toDelete = Math.floor(MAX_RECORDS * 0.2)  // 删除20%

    request.onsuccess = (event) => {
      const cursor = (event.target as IDBRequest).result
      if (cursor && deleted < toDelete) {
        store.delete(cursor.primaryKey)
        deleted++
        cursor.continue()
      }
    }

    tx.oncomplete = () => {
      console.log(`[IDB] LRU清理完成，删除 ${deleted} 条记录`)
      resolve()
    }
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * 清理过期数据
 */
async function cleanupExpired(database: IDBDatabase): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_KLINE, 'readwrite')
    const store = tx.objectStore(STORE_KLINE)
    const request = store.openCursor()
    const expiryTime = Date.now() - EXPIRY_DAYS * 24 * 60 * 60 * 1000
    let deleted = 0

    request.onsuccess = (event) => {
      const cursor = (event.target as IDBRequest).result
      if (cursor) {
        const record: IDBKlineRecord = cursor.value
        if (record.meta.updatedAt < expiryTime) {
          store.delete(cursor.primaryKey)
          deleted++
        }
        cursor.continue()
      }
    }

    tx.oncomplete = () => {
      if (deleted > 0) {
        console.log(`[IDB] 清理过期数据 ${deleted} 条`)
      }
      resolve()
    }
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * 删除指定股票的缓存
 */
export async function deleteSymbolCache(symbol: string): Promise<void> {
  const database = await initKlineDB()

  return new Promise((resolve, reject) => {
    const tx = database.transaction([STORE_KLINE, STORE_META], 'readwrite')

    // 获取元数据
    const metaStore = tx.objectStore(STORE_META)
    const metaRequest = metaStore.get(symbol)

    metaRequest.onsuccess = () => {
      const meta: IDBStockMeta | undefined = metaRequest.result
      if (meta) {
        // 删除所有周期的数据
        const klineStore = tx.objectStore(STORE_KLINE)
        meta.periods.forEach(period => {
          klineStore.delete(`${symbol}:${period}`)
        })
        // 删除元数据
        metaStore.delete(symbol)
      }
    }

    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * 清空所有缓存
 */
export async function clearAllCache(): Promise<void> {
  const database = await initKlineDB()

  return new Promise((resolve, reject) => {
    const tx = database.transaction([STORE_KLINE, STORE_META], 'readwrite')
    tx.objectStore(STORE_KLINE).clear()
    tx.objectStore(STORE_META).clear()

    tx.oncomplete = () => {
      console.log('[IDB] 所有缓存已清空')
      resolve()
    }
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * 获取缓存统计
 */
export async function getCacheStats(): Promise<IDBCacheStats> {
  const database = await initKlineDB()

  return new Promise((resolve, reject) => {
    const tx = database.transaction([STORE_KLINE, STORE_META], 'readonly')

    const klineCountReq = tx.objectStore(STORE_KLINE).count()
    const metaCountReq = tx.objectStore(STORE_META).count()

    let totalRecords = 0
    let totalSymbols = 0
    let oldestRecord = Date.now()

    klineCountReq.onsuccess = () => { totalRecords = klineCountReq.result }
    metaCountReq.onsuccess = () => { totalSymbols = metaCountReq.result }

    // 获取最旧记录时间
    const index = tx.objectStore(STORE_KLINE).index('by_accessed')
    const cursorReq = index.openCursor()

    cursorReq.onsuccess = (event) => {
      const cursor = (event.target as IDBRequest).result
      if (cursor) {
        const record: IDBKlineRecord = cursor.value
        oldestRecord = Math.min(oldestRecord, record.accessedAt)
      }
    }

    tx.oncomplete = () => {
      // 估算大小：每条记录约10KB
      const totalSize = (totalRecords * 10) / 1024

      resolve({
        totalRecords,
        totalSymbols,
        totalSize: Math.round(totalSize * 100) / 100,
        oldestRecord
      })
    }
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * 预加载自选股列表到缓存
 */
export async function preloadWatchlistToCache(
  symbols: string[],
  periods: string[] = ['1d', '5m']
): Promise<void> {
  console.log(`[IDB] 预加载 ${symbols.length} 只股票到缓存`)

  // 限制数量
  const limitedSymbols = symbols.slice(0, MAX_SYMBOLS)

  for (const symbol of limitedSymbols) {
    for (const period of periods) {
      // 检查是否已缓存
      const existing = await getKlineData(symbol, period)
      if (!existing) {
        // 标记为需要加载（下次请求时会从API获取并缓存）
        console.log(`[IDB] ${symbol}:${period} 待加载`)
      }
    }
  }
}
