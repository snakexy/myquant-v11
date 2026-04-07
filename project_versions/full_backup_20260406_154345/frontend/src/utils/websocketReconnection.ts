/**
 * MyQuant v9.0.0 - WebSocket Reconnection Strategy
 * WebSocket重连策略优化 - 指数退避算法
 */

export interface ReconnectionConfig {
  enable: boolean
  maxRetries: number // 最大重试次数
  initialDelay: number // 初始延迟(ms)
  maxDelay: number // 最大延迟(ms)
  backoffFactor: number // 退避因子
  jitter: boolean // 是否添加随机抖动
}

export interface ReconnectionState {
  attempt: number
  lastAttempt: number
  nextAttempt: number
  isRetrying: boolean
}

class WebSocketReconnection {
  private config: ReconnectionConfig = {
    enable: true,
    maxRetries: 10,
    initialDelay: 1000, // 1秒
    maxDelay: 30000, // 30秒
    backoffFactor: 2, // 指数退避
    jitter: true // 添加随机抖动
  }

  private state: ReconnectionState = {
    attempt: 0,
    lastAttempt: 0,
    nextAttempt: 0,
    isRetrying: false
  }

  private retryTimer: ReturnType<typeof setTimeout> | null = null
  private reconnectCallbacks: Array<(attempt: number) => void> = []
  private successCallbacks: Array<() => void> = []
  private failedCallbacks: Array<() => void> = []

  constructor() {
    this.loadFromStorage()
  }

  /**
   * 从本地存储加载配置
   */
  private loadFromStorage(): void {
    try {
      const saved = localStorage.getItem('ws_reconnect_config')
      if (saved) {
        this.config = { ...this.config, ...JSON.parse(saved) }
      }
    } catch (error) {
      console.warn('[WSReconnection] Failed to load config from storage:', error)
    }
  }

  /**
   * 保存配置到本地存储
   */
  private saveToStorage(): void {
    try {
      localStorage.setItem('ws_reconnect_config', JSON.stringify(this.config))
    } catch (error) {
      console.warn('[WSReconnection] Failed to save config to storage:', error)
    }
  }

  /**
   * 更新配置
   */
  updateConfig(config: Partial<ReconnectionConfig>): void {
    this.config = { ...this.config, ...config }
    this.saveToStorage()
  }

  /**
   * 计算下次重连延迟（指数退避 + 抖动）
   */
  private calculateDelay(attempt: number): number {
    // 指数退避
    let delay = this.config.initialDelay * Math.pow(this.config.backoffFactor, attempt)

    // 限制最大延迟
    delay = Math.min(delay, this.config.maxDelay)

    // 添加随机抖动（避免多个客户端同时重连）
    if (this.config.jitter) {
      const jitterRange = delay * 0.1 // 10%的抖动
      delay = delay + (Math.random() - 0.5) * jitterRange
    }

    return Math.floor(delay)
  }

  /**
   * 安排重连
   */
  scheduleReconnect(): Promise<void> {
    return new Promise((resolve, reject) => {
      // 检查是否启用重连
      if (!this.config.enable) {
        this.state.isRetrying = false
        this.notifyFailed()
        reject(new Error('Reconnection disabled'))
        return
      }

      // 检查是否超过最大重试次数
      if (this.state.attempt >= this.config.maxRetries) {
        this.state.isRetrying = false
        this.notifyFailed()
        reject(new Error('Max reconnection attempts reached'))
        return
      }

      // 计算延迟
      const delay = this.calculateDelay(this.state.attempt)

      console.log(`[WSReconnection] Scheduling reconnection attempt ${this.state.attempt + 1}/${this.config.maxRetries} in ${Math.round(delay / 1000)}s`)

      // 安排重连
      this.retryTimer = setTimeout(() => {
        this.state.lastAttempt = Date.now()
        this.state.attempt++

        console.log(`[WSReconnection] Attempting reconnection #${this.state.attempt}`)

        // 通知重连回调
        this.notifyReconnect(this.state.attempt)

        resolve()
      }, delay)

      this.state.nextAttempt = Date.now() + delay
      this.state.isRetrying = true
    })
  }

  /**
   * 重连成功
   */
  onConnectSuccess(): void {
    console.log(`[WSReconnection] Connection successful after ${this.state.attempt} attempts`)

    // 清除重连定时器
    if (this.retryTimer) {
      clearTimeout(this.retryTimer)
      this.retryTimer = null
    }

    // 重置状态
    this.state.attempt = 0
    this.state.isRetrying = false

    // 通知成功回调
    this.notifySuccess()
  }

  /**
   * 重连失败
   */
  onConnectFailed(): void {
    console.warn('[WSReconnection] Connection failed')

    // 继续尝试重连
    this.scheduleReconnect().catch(() => {
      // 已达到最大重试次数
    })
  }

  /**
   * 取消重连
   */
  cancel(): void {
    if (this.retryTimer) {
      clearTimeout(this.retryTimer)
      this.retryTimer = null
    }

    this.state.isRetrying = false
    this.state.attempt = 0
  }

  /**
   * 重置状态
   */
  reset(): void {
    this.cancel()
    this.state = {
      attempt: 0,
      lastAttempt: 0,
      nextAttempt: 0,
      isRetrying: false
    }
  }

  /**
   * 获取当前状态
   */
  getState(): ReconnectionState {
    return { ...this.state }
  }

  /**
   * 获取下次重连时间
   */
  getNextAttemptTime(): number {
    return this.state.nextAttempt
  }

  /**
   * 获取距离下次重连的毫秒数
   */
  getTimeUntilNextAttempt(): number {
    return Math.max(0, this.state.nextAttempt - Date.now())
  }

  /**
   * 注册重连回调
   */
  onReconnect(callback: (attempt: number) => void): () => void {
    this.reconnectCallbacks.push(callback)
    return () => {
      const index = this.reconnectCallbacks.indexOf(callback)
      if (index > -1) {
        this.reconnectCallbacks.splice(index, 1)
      }
    }
  }

  /**
   * 注册成功回调
   */
  onSuccess(callback: () => void): () => void {
    this.successCallbacks.push(callback)
    return () => {
      const index = this.successCallbacks.indexOf(callback)
      if (index > -1) {
        this.successCallbacks.splice(index, 1)
      }
    }
  }

  /**
   * 注册失败回调
   */
  onFailed(callback: () => void): () => void {
    this.failedCallbacks.push(callback)
    return () => {
      const index = this.failedCallbacks.indexOf(callback)
      if (index > -1) {
        this.failedCallbacks.splice(index, 1)
      }
    }
  }

  /**
   * 通知重连回调
   */
  private notifyReconnect(attempt: number): void {
    for (const callback of this.reconnectCallbacks) {
      try {
        callback(attempt)
      } catch (error) {
        console.error('[WSReconnection] Error in reconnect callback:', error)
      }
    }
  }

  /**
   * 通知成功回调
   */
  private notifySuccess(): void {
    for (const callback of this.successCallbacks) {
      try {
        callback()
      } catch (error) {
        console.error('[WSReconnection] Error in success callback:', error)
      }
    }
  }

  /**
   * 通知失败回调
   */
  private notifyFailed(): void {
    for (const callback of this.failedCallbacks) {
      try {
        callback()
      } catch (error) {
        console.error('[WSReconnection] Error in failed callback:', error)
      }
    }
  }

  /**
   * 获取重连统计信息
   */
  getStats(): { attempt: number; isRetrying: boolean; timeUntilNext: number; successRate: number } {
    return {
      attempt: this.state.attempt,
      isRetrying: this.state.isRetrying,
      timeUntilNext: this.getTimeUntilNextAttempt(),
      successRate: this.state.attempt > 0 ? 1 / (this.state.attempt + 1) : 1
    }
  }
}

// 创建单例
export const wsReconnection = new WebSocketReconnection()

// 导出类型
export type { ReconnectionConfig, ReconnectionState }
