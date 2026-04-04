// 通用工具函数库
import type { 
  DebounceConfig, 
  ThrottleConfig, 
  DeepCompareConfig,
  CacheConfig,
  CacheItem,
  StorageConfig,
  ArrayUtilsConfig,
  ObjectUtilsConfig,
  StringUtilsConfig,
  DeviceInfo,
  EnvironmentConfig
} from './types'

/**
 * 防抖函数
 * @param func 要防抖的函数
 * @param config 防抖配置
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  config: DebounceConfig | number
): T {
  const { delay, immediate = false, maxWait } = typeof config === 'number' 
    ? { delay: config } 
    : config

  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let lastCallTime = 0
  let maxTimeoutId: ReturnType<typeof setTimeout> | null = null

  const debounced = function (this: any, ...args: Parameters<T>) {
    const currentTime = Date.now()
    const shouldCallImmediately = immediate && !timeoutId

    if (maxWait && currentTime - lastCallTime >= maxWait) {
      if (maxTimeoutId) {
        clearTimeout(maxTimeoutId)
        maxTimeoutId = null
      }
      func.apply(this, args)
      lastCallTime = currentTime
      return
    }

    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      if (!immediate) {
        func.apply(this, args)
      }
      timeoutId = null
      lastCallTime = Date.now()
    }, delay)

    if (shouldCallImmediately) {
      func.apply(this, args)
    }
  } as T & { cancel: () => void }

  ;(debounced as any).cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
    if (maxTimeoutId) {
      clearTimeout(maxTimeoutId)
      maxTimeoutId = null
    }
  }

  return debounced
}

/**
 * 节流函数
 * @param func 要节流的函数
 * @param config 节流配置
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  config: ThrottleConfig | number
): T {
  const { delay, leading = true, trailing = true } = typeof config === 'number' 
    ? { delay: config } 
    : config

  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let lastCallTime = 0

  const throttled = function (this: any, ...args: Parameters<T>) {
    const currentTime = Date.now()

    if (leading && currentTime - lastCallTime >= delay) {
      func.apply(this, args)
      lastCallTime = currentTime
      return
    }

    if (trailing && !timeoutId) {
      timeoutId = setTimeout(() => {
        func.apply(this, args)
        lastCallTime = Date.now()
        timeoutId = null
      }, delay - (currentTime - lastCallTime))
    }
  } as T & { cancel: () => void }

  ;(throttled as any).cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  return throttled
}

/**
 * 深度比较两个值是否相等
 * @param obj1 第一个值
 * @param obj2 第二个值
 * @param config 比较配置
 * @returns 是否相等
 */
export function deepEqual(obj1: any, obj2: any, config: DeepCompareConfig = {}): boolean {
  const {
    ignoreCase = false,
    ignoreWhitespace = false,
    ignoreUndefined = false,
    ignoreNull = false,
    ignoreEmptyString = false,
    ignoreEmptyArray = false,
    ignoreEmptyObject = false
  } = config

  // 处理字符串比较
  if (typeof obj1 === 'string' && typeof obj2 === 'string') {
    let str1 = obj1
    let str2 = obj2

    if (ignoreCase) {
      str1 = str1.toLowerCase()
      str2 = str2.toLowerCase()
    }

    if (ignoreWhitespace) {
      str1 = str1.trim()
      str2 = str2.trim()
    }

    return str1 === str2
  }

  // 处理忽略值的逻辑
  const shouldIgnore = (value: any) => {
    if (ignoreUndefined && value === undefined) return true
    if (ignoreNull && value === null) return true
    if (ignoreEmptyString && value === '') return true
    if (ignoreEmptyArray && Array.isArray(value) && value.length === 0) return true
    if (ignoreEmptyObject && typeof value === 'object' && value !== null && !Array.isArray(value) && Object.keys(value).length === 0) return true
    return false
  }

  if (shouldIgnore(obj1) && shouldIgnore(obj2)) return true
  if (shouldIgnore(obj1) !== shouldIgnore(obj2)) return false

  // 严格相等比较
  if (obj1 === obj2) return true

  // 类型不同
  if (typeof obj1 !== typeof obj2) return false

  // 处理数组
  if (Array.isArray(obj1) && Array.isArray(obj2)) {
    if (obj1.length !== obj2.length) return false
    for (let i = 0; i < obj1.length; i++) {
      if (!deepEqual(obj1[i], obj2[i], config)) return false
    }
    return true
  }

  // 处理对象
  if (typeof obj1 === 'object' && obj1 !== null && obj2 !== null) {
    const keys1 = Object.keys(obj1)
    const keys2 = Object.keys(obj2)

    if (keys1.length !== keys2.length) return false

    for (const key of keys1) {
      if (!keys2.includes(key)) return false
      if (!deepEqual(obj1[key], obj2[key], config)) return false
    }

    return true
  }

  return false
}

/**
 * 深度克隆对象
 * @param obj 要克隆的对象
 * @returns 克隆后的对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime()) as T
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as T
  if (typeof obj === 'object') {
    const cloned = {} as T
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key])
      }
    }
    return cloned
  }
  return obj
}

/**
 * 生成唯一ID
 * @param prefix 前缀
 * @param length 长度
 * @returns 唯一ID
 */
export function generateId(prefix = '', length = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return prefix ? `${prefix}_${result}` : result
}

/**
 * 简单缓存类
 */
export class SimpleCache<T = any> {
  private cache = new Map<string, CacheItem<T>>()
  private maxSize: number
  private defaultTtl: number

  constructor(config: CacheConfig = {}) {
    this.maxSize = config.maxSize || 100
    this.defaultTtl = config.ttl || 5 * 60 * 1000 // 5分钟
  }

  set(key: string, value: T, ttl?: number): void {
    const item: CacheItem<T> = {
      value,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTtl,
      expires: Date.now() + (ttl || this.defaultTtl)
    }

    // 如果缓存已满，删除最旧的项
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const oldestKey = this.getOldestKey()
      if (oldestKey) {
        this.cache.delete(oldestKey)
      }
    }

    this.cache.set(key, item)
  }

  get(key: string): T | null {
    const item = this.cache.get(key)
    if (!item) return null

    // 检查是否过期
    if (item.expires && Date.now() > item.expires) {
      this.cache.delete(key)
      return null
    }

    return item.value
  }

  has(key: string): boolean {
    const item = this.cache.get(key)
    if (!item) return false

    // 检查是否过期
    if (item.expires && Date.now() > item.expires) {
      this.cache.delete(key)
      return false
    }

    return true
  }

  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  clear(): void {
    this.cache.clear()
  }

  size(): number {
    return this.cache.size
  }

  private getOldestKey(): string | null {
    let oldestKey: string | null = null
    let oldestTime = Date.now()

    for (const [key, item] of this.cache) {
      if (item.timestamp < oldestTime) {
        oldestTime = item.timestamp
        oldestKey = key
      }
    }

    return oldestKey
  }
}

/**
 * 本地存储工具
 */
export class StorageHelper {
  private config: StorageConfig

  constructor(config: StorageConfig = {}) {
    this.config = {
      prefix: '',
      driver: 'localStorage',
      ...config
    }
  }

  private getKey(key: string): string {
    return this.config.prefix ? `${this.config.prefix}_${key}` : key
  }

  private getDriver(): Storage {
    if (this.config.driver === 'sessionStorage') {
      return sessionStorage
    } else if (this.config.driver === 'memory') {
      return memoryStorage
    } else {
      return localStorage
    }
  }

  set(key: string, value: any, ttl?: number): void {
    const driver = this.getDriver()
    const item = {
      value,
      timestamp: Date.now(),
      ttl: ttl || this.config.ttl,
      expires: ttl ? Date.now() + ttl : null
    }

    const serializedValue = this.config.serializer 
      ? this.config.serializer(JSON.stringify(item))
      : JSON.stringify(item)

    driver.setItem(this.getKey(key), serializedValue)
  }

  get(key: string): any {
    const driver = this.getDriver()
    const serializedValue = driver.getItem(this.getKey(key))
    
    if (!serializedValue) return null

    try {
      const item = this.config.deserializer 
        ? this.config.deserializer(serializedValue)
        : JSON.parse(serializedValue)

      // 检查是否过期
      if (item.expires && Date.now() > item.expires) {
        this.delete(key)
        return null
      }

      return item.value
    } catch (error) {
      console.error('Storage parse error:', error)
      return null
    }
  }

  has(key: string): boolean {
    return this.get(key) !== null
  }

  delete(key: string): void {
    const driver = this.getDriver()
    driver.removeItem(this.getKey(key))
  }

  clear(): void {
    const driver = this.getDriver()
    if (this.config.prefix) {
      // 只删除带前缀的项
      const keys = Object.keys(driver)
      keys.forEach(key => {
        if (key.startsWith(this.config.prefix!)) {
          driver.removeItem(key)
        }
      })
    } else {
      driver.clear()
    }
  }
}

// 内存存储实现
const memoryStorage: Storage = {
  data: {} as Record<string, string>,
  getItem(key: string): string | null {
    return this.data[key] || null
  },
  setItem(key: string, value: string): void {
    this.data[key] = value
  },
  removeItem(key: string): void {
    delete this.data[key]
  },
  clear(): void {
    this.data = {}
  },
  get length(): number {
    return Object.keys(this.data).length
  },
  key(index: number): string | null {
    const keys = Object.keys(this.data)
    return keys[index] || null
  }
}

/**
 * 数组工具函数
 */
export class ArrayUtils {
  /**
   * 数组去重
   * @param array 数组
   * @param config 配置
   * @returns 去重后的数组
   */
  static unique<T>(array: T[], config: ArrayUtilsConfig = {}): T[] {
    const { uniqueKey } = config

    if (!uniqueKey) {
      return [...new Set(array)]
    }

    const seen = new Set()
    return array.filter(item => {
      const key = typeof uniqueKey === 'function' ? uniqueKey(item) : item[uniqueKey]
      if (seen.has(key)) {
        return false
      }
      seen.add(key)
      return true
    })
  }

  /**
   * 数组排序
   * @param array 数组
   * @param config 配置
   * @returns 排序后的数组
   */
  static sort<T>(array: T[], config: ArrayUtilsConfig): T[] {
    const { sortBy, compareFn } = config

    if (compareFn) {
      return [...array].sort(compareFn)
    }

    if (sortBy) {
      const key = typeof sortBy === 'function' ? sortBy : (item: T) => item[sortBy as keyof T]
      return [...array].sort((a, b) => {
        const valA = key(a)
        const valB = key(b)
        if (valA < valB) return -1
        if (valA > valB) return 1
        return 0
      })
    }

    return [...array]
  }

  /**
   * 数组分组
   * @param array 数组
   * @param config 配置
   * @returns 分组后的对象
   */
  static groupBy<T>(array: T[], config: ArrayUtilsConfig): Record<string, T[]> {
    const { groupBy } = config

    if (!groupBy) {
      throw new Error('groupBy is required')
    }

    const key = typeof groupBy === 'function' ? groupBy : (item: T) => item[groupBy as keyof T]
    return array.reduce((groups, item) => {
      const groupKey = String(key(item))
      if (!groups[groupKey]) {
        groups[groupKey] = []
      }
      groups[groupKey].push(item)
      return groups
    }, {} as Record<string, T[]>)
  }

  /**
   * 数组分块
   * @param array 数组
   * @param size 块大小
   * @returns 分块后的二维数组
   */
  static chunk<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = []
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size))
    }
    return chunks
  }

  /**
   * 数组扁平化
   * @param array 数组
   * @param depth 扁平化深度
   * @returns 扁平化后的数组
   */
  static flatten<T>(array: any[], depth = 1): T[] {
    return depth > 0 
      ? array.reduce((acc, val) => acc.concat(Array.isArray(val) ? ArrayUtils.flatten(val, depth - 1) : val), [])
      : array.slice()
  }
}

/**
 * 对象工具函数
 */
export class ObjectUtils {
  /**
   * 深度合并对象
   * @param target 目标对象
   * @param sources 源对象
   * @returns 合并后的对象
   */
  static merge<T extends Record<string, any>>(target: T, ...sources: Partial<T>[]): T {
    if (!sources.length) return target
    const source = sources.shift()

    if (isObject(target) && isObject(source)) {
      for (const key in source) {
        if (isObject(source[key])) {
          if (!target[key]) Object.assign(target, { [key]: {} })
          ObjectUtils.merge(target[key], source[key])
        } else {
          Object.assign(target, { [key]: source[key] })
        }
      }
    }

    return ObjectUtils.merge(target, ...sources)
  }

  /**
   * 选择对象的指定属性
   * @param obj 对象
   * @param keys 属性键数组
   * @returns 新对象
   */
  static pick<T extends Record<string, any>, K extends keyof T>(
    obj: T, 
    keys: K[]
  ): Pick<T, K> {
    const result = {} as Pick<T, K>
    keys.forEach(key => {
      if (key in obj) {
        result[key] = obj[key]
      }
    })
    return result
  }

  /**
   * 排除对象的指定属性
   * @param obj 对象
   * @param keys 属性键数组
   * @returns 新对象
   */
  static omit<T extends Record<string, any>, K extends keyof T>(
    obj: T, 
    keys: K[]
  ): Omit<T, K> {
    const result = { ...obj }
    keys.forEach(key => {
      delete result[key]
    })
    return result
  }

  /**
   * 过滤对象属性
   * @param obj 对象
   * @param config 配置
   * @returns 过滤后的对象
   */
  static filter<T extends Record<string, any>>(
    obj: T, 
    config: ObjectUtilsConfig = {}
  ): Partial<T> {
    const { 
      deep = false, 
      omitNull = false, 
      omitUndefined = false, 
      omitEmpty = false,
      customFilter 
    } = config

    const filterValue = (value: any, key: string): boolean => {
      if (customFilter && !customFilter(key, value)) return false
      if (omitNull && value === null) return false
      if (omitUndefined && value === undefined) return false
      if (omitEmpty && value === '') return false
      return true
    }

    if (deep) {
      const result: any = {}
      for (const [key, value] of Object.entries(obj)) {
        if (filterValue(value, key)) {
          if (isObject(value) && !Array.isArray(value)) {
            result[key] = ObjectUtils.filter(value, config)
          } else {
            result[key] = value
          }
        }
      }
      return result
    } else {
      const result: any = {}
      for (const [key, value] of Object.entries(obj)) {
        if (filterValue(value, key)) {
          result[key] = value
        }
      }
      return result
    }
  }
}

/**
 * 字符串工具函数
 */
export class StringUtils {
  /**
   * 驼峰命名转换
   * @param str 字符串
   * @returns 驼峰命名字符串
   */
  static toCamelCase(str: string): string {
    return str.replace(/[-_\s]+(.)?/g, (_, c) => c ? c.toUpperCase() : '')
  }

  /**
   * 短横线命名转换
   * @param str 字符串
   * @returns 短横线命名字符串
   */
  static toKebabCase(str: string): string {
    return str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase()
  }

  /**
   * 下划线命名转换
   * @param str 字符串
   * @returns 下划线命名字符串
   */
  static toSnakeCase(str: string): string {
    return str.replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase()
  }

  /**
   * 首字母大写
   * @param str 字符串
   * @returns 首字母大写的字符串
   */
  static capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1)
  }

  /**
   * 截断字符串
   * @param str 字符串
   * @param length 最大长度
   * @param suffix 后缀
   * @returns 截断后的字符串
   */
  static truncate(str: string, length: number, suffix = '...'): string {
    if (str.length <= length) return str
    return str.substring(0, length - suffix.length) + suffix
  }

  /**
   * 转换为模板字符串
   * @param template 模板
   * @param data 数据
   * @returns 替换后的字符串
   */
  static template(template: string, data: Record<string, any>): string {
    return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return data[key] !== undefined ? String(data[key]) : match
    })
  }
}

/**
 * 获取设备信息
 * @returns 设备信息
 */
export function getDeviceInfo(): DeviceInfo {
  const userAgent = navigator.userAgent
  const platform = navigator.platform

  // 检测浏览器
  let browser = 'Unknown'
  let browserVersion = 'Unknown'
  
  if (userAgent.indexOf('Chrome') > -1) {
    browser = 'Chrome'
    const match = userAgent.match(/Chrome\/(\d+)/)
    if (match) browserVersion = match[1]
  } else if (userAgent.indexOf('Firefox') > -1) {
    browser = 'Firefox'
    const match = userAgent.match(/Firefox\/(\d+)/)
    if (match) browserVersion = match[1]
  } else if (userAgent.indexOf('Safari') > -1) {
    browser = 'Safari'
    const match = userAgent.match(/Version\/(\d+)/)
    if (match) browserVersion = match[1]
  } else if (userAgent.indexOf('Edge') > -1) {
    browser = 'Edge'
    const match = userAgent.match(/Edge\/(\d+)/)
    if (match) browserVersion = match[1]
  }

  // 检测操作系统
  let os = 'Unknown'
  let osVersion = 'Unknown'
  
  if (platform.indexOf('Win') > -1) {
    os = 'Windows'
    const match = userAgent.match(/Windows NT (\d+\.\d+)/)
    if (match) osVersion = match[1]
  } else if (platform.indexOf('Mac') > -1) {
    os = 'macOS'
    const match = userAgent.match(/Mac OS X (\d+[._]\d+)/)
    if (match) osVersion = match[1].replace('_', '.')
  } else if (platform.indexOf('Linux') > -1) {
    os = 'Linux'
  }

  // 检测设备类型
  const mobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent)
  const tablet = /iPad|Android(?!.*Mobile)|Tablet/i.test(userAgent)
  const desktop = !mobile && !tablet

  // 屏幕信息
  const screen = {
    width: window.screen.width,
    height: window.screen.height,
    colorDepth: window.screen.colorDepth,
    pixelRatio: window.devicePixelRatio || 1
  }

  // 视口信息
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight
  }

  // 功能检测
  const features = {
    webgl: !!window.WebGLRenderingContext,
    webgl2: !!window.WebGL2RenderingContext,
    canvas: !!document.createElement('canvas').getContext,
    svg: !!document.createElementNS && !!document.createElementNS('http://www.w3.org/2000/svg', 'svg').createSVGRect,
    audio: !!window.Audio,
    video: !!document.createElement('video').canPlayType,
    localStorage: !!window.localStorage,
    sessionStorage: !!window.sessionStorage,
    webWorkers: !!window.Worker,
    touch: 'ontouchstart' in window,
    geolocation: !!navigator.geolocation,
    notification: !!window.Notification
  }

  return {
    userAgent,
    platform,
    browser,
    browserVersion,
    mobile,
    tablet,
    desktop,
    os,
    osVersion,
    screen,
    viewport,
    features
  }
}

/**
 * 获取环境信息
 * @returns 环境信息
 */
export function getEnvironmentInfo(): EnvironmentConfig {
  const env = import.meta.env as any
  return {
    development: env.MODE === 'development',
    production: env.MODE === 'production',
    test: env.MODE === 'test',
    staging: env.MODE === 'staging',
    version: env.VITE_APP_VERSION || '1.0.0',
    buildTime: env.VITE_BUILD_TIME || new Date().toISOString(),
    commit: env.VITE_GIT_COMMIT || 'unknown',
    branch: env.VITE_GIT_BRANCH || 'main'
  }
}

/**
 * 下载文件
 * @param url 文件URL
 * @param filename 文件名
 */
export function downloadFile(url: string, filename?: string): void {
  const link = document.createElement('a')
  link.href = url
  if (filename) {
    link.download = filename
  }
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 复制到剪贴板
 * @param text 要复制的文本
 * @returns 是否成功
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      // 降级方案
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      const result = document.execCommand('copy')
      document.body.removeChild(textArea)
      return result
    }
  } catch (error) {
    console.error('Copy to clipboard failed:', error)
    return false
  }
}

/**
 * 获取URL参数
 * @param url URL字符串
 * @returns 参数对象
 */
export function getUrlParams(url?: string): Record<string, string> {
  const urlObj = new URL(url || window.location.href)
  const params: Record<string, string> = {}
  
  urlObj.searchParams.forEach((value, key) => {
    params[key] = value
  })
  
  return params
}

/**
 * 构建URL
 * @param config URL配置
 * @returns 构建的URL
 */
export function buildUrl(config: {
  baseUrl?: string
  path?: string
  query?: Record<string, any>
  hash?: string
}): string {
  const { baseUrl = '', path = '', query = {}, hash = '' } = config
  
  let url = baseUrl
  if (path) {
    url += url.endsWith('/') ? path.substring(1) : path
  }
  
  const queryString = Object.entries(query)
    .filter(([, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join('&')
  
  if (queryString) {
    url += (url.includes('?') ? '&' : '?') + queryString
  }
  
  if (hash) {
    url += hash.startsWith('#') ? hash : `#${hash}`
  }
  
  return url
}

/**
 * 延迟执行
 * @param ms 延迟毫秒数
 * @returns Promise
 */
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 重试执行
 * @param fn 要执行的函数
 * @param times 重试次数
 * @param delay 延迟时间
 * @returns Promise
 */
export async function retry<T>(
  fn: () => Promise<T>,
  times = 3,
  delayMs = 1000
): Promise<T> {
  let lastError: Error
  
  for (let i = 0; i < times; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      if (i < times - 1) {
        await delay(delayMs)
      }
    }
  }
  
  throw lastError!
}

// 辅助函数
function isObject(value: any): boolean {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}