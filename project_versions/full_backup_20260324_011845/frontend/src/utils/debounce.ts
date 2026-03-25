/**
 * MyQuant v9.0.0 - Request Debounce Utility
 * 请求防抖工具 - 减少不必要的API调用
 */

export interface DebounceConfig {
  delay: number // 延迟时间(ms)
  maxWait: number // 最大等待时间(ms)
  leading: boolean // 是否在开始时立即执行
  trailing: boolean // 是否在结束时执行
}

export interface ThrottleConfig {
  delay: number // 延迟时间(ms)
  leading: boolean // 是否在开始时立即执行
  trailing: boolean // 是否在结束时执行
}

/**
 * 防抖函数 - 延迟执行，在等待时间内多次调用只执行最后一次
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  config: number | DebounceConfig = 300
): (...args: Parameters<T>) => void {
  const options: DebounceConfig = typeof config === 'number'
    ? { delay: config, maxWait: 0, leading: false, trailing: true }
    : config

  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let lastCallTime = 0
  let lastArgs: Parameters<T> | null = null
  let result: any

  const invokeFunc = (time: number) => {
    const args = lastArgs!
    lastArgs = null
    result = func(...args)
    return result
  }

  const startTimer = (pendingFunc: () => void, wait: number) => {
    return setTimeout(pendingFunc, wait)
  }

  const shouldInvoke = (time: number) => {
    const timeSinceLastCall = time - lastCallTime
    return lastCallTime === 0 || timeSinceLastCall >= options.delay
  }

  const trailingEdge = (time: number) => {
    timeoutId = null

    if (options.trailing && lastArgs) {
      return invokeFunc(time)
    }

    lastArgs = null
    return result
  }

  const timerExpired = () => {
    const time = Date.now()
    if (shouldInvoke(time)) {
      return trailingEdge(time)
    }

    // 重启计时器
    const remaining = options.delay - (time - lastCallTime)
    timeoutId = startTimer(timerExpired, remaining)
  }

  const debounced = (...args: Parameters<T>) => {
    const time = Date.now()
    const isInvoking = shouldInvoke(time)

    lastArgs = args
    lastCallTime = time

    if (isInvoking) {
      if (timeoutId === null) {
        if (options.leading) {
          return invokeFunc(time)
        }
      } else {
        clearTimeout(timeoutId!)
      }

      timeoutId = startTimer(timerExpired, options.delay)
    }

    if (isInvoking && options.leading) {
      return result
    }

    return result
  }

  return debounced
}

/**
 * 节流函数 - 限制执行频率
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  config: number | ThrottleConfig = 300
): (...args: Parameters<T>) => void {
  const options: ThrottleConfig = typeof config === 'number'
    ? { delay: config, leading: true, trailing: true }
    : config

  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let lastCallTime = 0
  let lastArgs: Parameters<T> | null = null
  let result: any

  const invokeFunc = (time: number) => {
    const args = lastArgs!
    lastArgs = null
    lastCallTime = time
    result = func(...args)
    return result
  }

  const startTimer = (pendingFunc: () => void, wait: number) => {
    return setTimeout(pendingFunc, wait)
  }

  const trailingEdge = (time: number) => {
    timeoutId = null

    if (options.trailing && lastArgs) {
      return invokeFunc(time)
    }

    lastArgs = null
    return result
  }

  const remainingWait = (time: number) => {
    const timeSinceLastCall = time - lastCallTime
    return options.delay - timeSinceLastCall
  }

  const shouldInvoke = (time: number) => {
    const timeSinceLastCall = time - lastCallTime
    return lastCallTime === 0 || timeSinceLastCall >= options.delay
  }

  const timerExpired = () => {
    const time = Date.now()
    if (shouldInvoke(time)) {
      return trailingEdge(time)
    }

    timeoutId = startTimer(timerExpired, remainingWait(time))
  }

  const throttled = (...args: Parameters<T>) => {
    const time = Date.now()
    const isInvoking = shouldInvoke(time)

    lastArgs = args

    if (timeoutId === null) {
      if (isInvoking && options.leading) {
        return invokeFunc(time)
      }

      timeoutId = startTimer(timerExpired, options.delay)
    } else if (isInvoking) {
      clearTimeout(timeoutId!)
      timeoutId = startTimer(timerExpired, options.delay)
    }

    return result
  }

  return throttled
}

/**
 * 请求防抖管理器 - 用于管理API请求防抖
 */
export class RequestDebouncer {
  private debounceMap: Map<string, ReturnType<typeof debounce>> = new Map()
  private throttleMap: Map<string, ReturnType<typeof throttle>> = new Map()
  private delayMap: Map<string, number> = new Map()

  /**
   * 设置请求延迟
   */
  setDelay(key: string, delay: number): void {
    this.delayMap.set(key, delay)
  }

  /**
   * 获取请求延迟
   */
  getDelay(key: string, defaultDelay: number = 300): number {
    return this.delayMap.get(key) || defaultDelay
  }

  /**
   * 防抖执行
   */
  debounce<T extends (...args: any[]) => any>(
    key: string,
    func: T,
    customDelay?: number
  ): (...args: Parameters<T>) => void {
    const delay = customDelay ?? this.getDelay(key)

    if (!this.debounceMap.has(key)) {
      this.debounceMap.set(key, debounce(func, { delay, leading: false, trailing: true }))
    }

    return this.debounceMap.get(key)!(...arguments)
  }

  /**
   * 节流执行
   */
  throttle<T extends (...args: any[]) => any>(
    key: string,
    func: T,
    customDelay?: number
  ): (...args: Parameters<T>) => void {
    const delay = customDelay ?? this.getDelay(key, 100)

    if (!this.throttleMap.has(key)) {
      this.throttleMap.set(key, throttle(func, { delay, leading: true, trailing: true }))
    }

    return this.throttleMap.get(key)!(...arguments)
  }

  /**
   * 清除所有防抖/节流
   */
  clear(): void {
    this.debounceMap.clear()
    this.throttleMap.clear()
    this.delayMap.clear()
  }

  /**
   * 清除特定key
   */
  delete(key: string): void {
    this.debounceMap.delete(key)
    this.throttleMap.delete(key)
    this.delayMap.delete(key)
  }
}

/**
 * 预定义的常用请求延迟配置
 */
export const REQUEST_DELAYS = {
  MARKET_QUOTE: 1000, // 行情刷新
  KLINE_UPDATE: 500, // K线更新
  STOCK_SEARCH: 300, // 股票搜索
  SECTOR_REFRESH: 2000, // 板块刷新
  CHART_RESIZE: 200, // 图表调整
  SCROLL_EVENT: 100, // 滚动事件
  INPUT_CHANGE: 300 // 输入变化
} as const

/**
 * 全局请求防抖管理器
 */
export const globalDebouncer = new RequestDebouncer()

// 初始化默认延迟
Object.entries(REQUEST_DELAYS).forEach(([key, delay]) => {
  globalDebouncer.setDelay(key, delay)
})

/**
 * 防抖装饰器（用于类方法）
 */
export function Debounce(delay: number = 300) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value
    const key = `${target.constructor.name}_${propertyKey}`

    descriptor.value = function (...args: any[]) {
      return globalDebouncer.debounce(key, originalMethod.bind(this), delay)(...args)
    }

    return descriptor
  }
}

/**
 * 节流装饰器（用于类方法）
 */
export function Throttle(delay: number = 300) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value
    const key = `${target.constructor.name}_${propertyKey}`

    descriptor.value = function (...args: any[]) {
      return globalDebouncer.throttle(key, originalMethod.bind(this), delay)(...args)
    }

    return descriptor
  }
}
