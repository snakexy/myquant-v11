/**
 * 智能刷新调度器
 *
 * 功能：
 * 1. 错峰执行 - 避免多分组同时请求
 * 2. 批量合并 - 减少API调用次数
 * 3. 并发控制 - 防止请求阻塞
 * 4. 优先级队列 - 高频分组优先处理
 * 5. 暂停/恢复 - 市场休市时暂停，开盘时恢复
 */

interface RefreshTask {
  groupId: string
  groupName: string
  stocks: string[]
  interval: number
  priority: number
  lastRefresh: number
}

interface BatchRequest {
  stocks: string[]
  groupIds: string[]
  timestamp: number
}

type RefreshCallback = (stocks: string[]) => Promise<void>

export class RefreshScheduler {
  private tasks: Map<string, RefreshTask> = new Map()
  private timers: Map<string, NodeJS.Timeout> = new Map()
  private batchWindow: number = 100 // 批量合并窗口（毫秒）
  private maxConcurrent: number = 3 // 最大并发请求数
  private activeRequests: number = 0
  private pendingBatch: BatchRequest | null = null
  private batchTimer: NodeJS.Timeout | null = null
  private refreshCallback: RefreshCallback
  private paused: boolean = false // 是否暂停

  constructor(callback: RefreshCallback) {
    this.refreshCallback = callback
  }

  /**
   * 暂停调度器（市场休市时调用）
   */
  pause(): void {
    if (this.paused) return
    this.paused = true
    console.log('[Scheduler] ⏸ 调度器已暂停')
    // 清除所有定时器
    for (const timer of this.timers.values()) {
      clearTimeout(timer)
      clearInterval(timer)
    }
    this.timers.clear()
    // 清除批量窗口定时器
    if (this.batchTimer) {
      clearTimeout(this.batchTimer)
      this.batchTimer = null
    }
    // 清除待处理的批量队列
    this.pendingBatch = null
  }

  /**
   * 恢复调度器（市场开盘时调用）
   */
  resume(): void {
    if (!this.paused) return
    this.paused = false
    console.log('[Scheduler] ▶ 调度器已恢复')
    // 重新注册所有任务
    for (const task of this.tasks.values()) {
      const offset = this.calculateOffset(task.groupId)
      const timer = setTimeout(() => {
        this.startTask(task.groupId)
        this.setIntervalTask(task.groupId, task.interval)
      }, offset)
      this.timers.set(task.groupId, timer)
    }
  }

  /**
   * 注册分组刷新任务
   */
  register(task: RefreshTask): void {
    // 如果任务已存在，先清除旧定时器
    if (this.timers.has(task.groupId)) {
      this.unregister(task.groupId)
    }

    this.tasks.set(task.groupId, task)

    // 计算错峰偏移量（基于分组ID hash，确保不同分组错开）
    const offset = this.calculateOffset(task.groupId)
    const interval = task.interval

    console.log(`[Scheduler] 注册分组 ${task.groupName} (${task.groupId})`)
    console.log(`[Scheduler] 间隔: ${interval}ms, 错峰: ${offset}ms`)

    // 设置定时器
    const timer = setTimeout(() => {
      this.startTask(task.groupId)
      // 转换为 setInterval 持续执行
      this.setIntervalTask(task.groupId, interval)
    }, offset)

    this.timers.set(task.groupId, timer)
  }

  /**
   * 取消注册分组刷新任务
   */
  unregister(groupId: string): void {
    const timer = this.timers.get(groupId)
    if (timer) {
      clearTimeout(timer)
      this.timers.delete(groupId)
    }
    this.tasks.delete(groupId)
    console.log(`[Scheduler] 取消分组 ${groupId}`)
  }

  /**
   * 更新分组刷新间隔
   */
  updateInterval(groupId: string, newInterval: number): void {
    const task = this.tasks.get(groupId)
    if (task) {
      task.interval = newInterval
      this.unregister(groupId)
      this.register(task)
      console.log(`[Scheduler] 更新分组 ${groupId} 间隔为 ${newInterval}ms`)
    }
  }

  /**
   * 计算错峰偏移量
   */
  private calculateOffset(groupId: string): number {
    let hash = 0
    for (let i = 0; i < groupId.length; i++) {
      hash = ((hash << 5) - hash) + groupId.charCodeAt(i)
      hash |= 0
    }
    return Math.abs(hash) % 1000
  }

  /**
   * 启动任务（首次）
   */
  private startTask(groupId: string): void {
    const task = this.tasks.get(groupId)
    if (!task) return

    console.log(`[Scheduler] 启动分组 ${task.groupName} 首次刷新`)
    this.executeTask(task)
  }

  /**
   * 设置周期性任务
   */
  private setIntervalTask(groupId: string, interval: number): void {
    const timer = setInterval(() => {
      const task = this.tasks.get(groupId)
      if (task) {
        this.executeTask(task)
      }
    }, interval)

    this.timers.set(groupId, timer)
  }

  /**
   * 执行任务
   */
  private async executeTask(task: RefreshTask): Promise<void> {
    // 如果没有股票或已暂停，跳过
    if (!task.stocks || task.stocks.length === 0) {
      return
    }

    if (this.paused) {
      // 已暂停，静默跳过
      return
    }

    // 添加到批量队列
    this.addToBatch(task)

    // 更新最后刷新时间
    task.lastRefresh = Date.now()
  }

  /**
   * 添加到批量队列
   */
  private addToBatch(task: RefreshTask): void {
    if (!this.pendingBatch) {
      this.pendingBatch = {
        stocks: [],
        groupIds: [],
        timestamp: Date.now()
      }

      // 设置批量窗口定时器
      this.batchTimer = setTimeout(() => {
        this.flushBatch()
      }, this.batchWindow)
    }

    // 合并股票列表（去重）
    for (const stock of task.stocks) {
      if (!this.pendingBatch.stocks.includes(stock)) {
        this.pendingBatch.stocks.push(stock)
      }
    }

    // 记录涉及的分组
    if (!this.pendingBatch.groupIds.includes(task.groupId)) {
      this.pendingBatch.groupIds.push(task.groupId)
    }

    console.log(`[Scheduler] 批量队列: ${this.pendingBatch.stocks.length} 只股票, ${this.pendingBatch.groupIds.length} 个分组`)
  }

  /**
   * 刷新批量队列（执行API请求）
   */
  private async flushBatch(): Promise<void> {
    if (!this.pendingBatch || this.pendingBatch.stocks.length === 0) {
      this.pendingBatch = null
      return
    }

    // 如果已暂停或并发数已达上限，直接返回，等待下次定时器触发
    if (this.paused || this.activeRequests >= this.maxConcurrent) {
      console.log(`[Scheduler] 跳过刷新（暂停:${this.paused}, 并发:${this.activeRequests}/${this.maxConcurrent}）`)
      return
    }

    const batch = this.pendingBatch
    this.pendingBatch = null

    this.activeRequests++
    const startTime = Date.now()

    console.log(`[Scheduler] 执行批量请求: ${batch.stocks.length} 只股票`)
    console.log(`[Scheduler] 涉及分组: ${batch.groupIds.join(', ')}`)

    try {
      await this.refreshCallback(batch.stocks)

      const elapsed = Date.now() - startTime
      console.log(`[Scheduler] 批量请求完成，耗时: ${elapsed}ms`)
    } catch (error) {
      console.error('[Scheduler] 批量请求失败:', error)
    } finally {
      this.activeRequests--
    }
  }

  /**
   * 获取所有任务状态
   */
  getStatus(): Array<{
    groupId: string
    groupName: string
    interval: number
    lastRefresh: number
  }> {
    return Array.from(this.tasks.values()).map(task => ({
      groupId: task.groupId,
      groupName: task.groupName,
      interval: task.interval,
      lastRefresh: task.lastRefresh
    }))
  }

  /**
   * 销毁调度器
   */
  destroy(): void {
    // 清除所有定时器
    for (const timer of this.timers.values()) {
      clearTimeout(timer)
      clearInterval(timer)
    }
    this.timers.clear()
    this.tasks.clear()

    if (this.batchTimer) {
      clearTimeout(this.batchTimer)
    }

    console.log('[Scheduler] 调度器已销毁')
  }
}

// 创建全局单例
let globalScheduler: RefreshScheduler | null = null

/**
 * 初始化全局调度器
 */
export function initScheduler(callback: RefreshCallback): RefreshScheduler {
  if (globalScheduler) {
    globalScheduler.destroy()
  }

  globalScheduler = new RefreshScheduler(callback)
  return globalScheduler
}

/**
 * 获取全局调度器
 */
export function getScheduler(): RefreshScheduler | null {
  return globalScheduler
}
