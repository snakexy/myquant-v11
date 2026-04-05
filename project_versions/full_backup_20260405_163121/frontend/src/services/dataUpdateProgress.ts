/**
 * 数据更新进度管理服务
 * 提供全局的数据更新进度显示功能
 */

import { ref } from 'vue'

export interface UpdateTask {
  symbol: string
  period: string
  status: 'pending' | 'downloading' | 'processing' | 'completed' | 'failed'
  progress: number
  message?: string
}

class DataUpdateProgressService {
  private listeners: Set<(task: UpdateTask) => void> = new Set()
  private currentTask: UpdateTask | null = null

  // 开始更新任务
  startUpdate(symbol: string, period: string, message?: string) {
    this.currentTask = {
      symbol,
      period,
      status: 'downloading',
      progress: 0,
      message
    }
    this.notify()
  }

  // 更新进度
  updateProgress(progress: number, message?: string) {
    if (this.currentTask) {
      this.currentTask.progress = progress
      if (message) this.currentTask.message = message
      this.notify()
    }
  }

  // 设置状态
  setStatus(status: UpdateTask['status'], message?: string) {
    if (this.currentTask) {
      this.currentTask.status = status
      if (status === 'completed') this.currentTask.progress = 100
      if (message) this.currentTask.message = message
      this.notify()
    }
  }

  // 完成任务
  complete() {
    if (this.currentTask) {
      this.currentTask.status = 'completed'
      this.currentTask.progress = 100
      this.notify()

      // 2秒后清除
      setTimeout(() => {
        this.currentTask = null
        this.notify()
      }, 2000)
    }
  }

  // 失败
  fail(message: string) {
    if (this.currentTask) {
      this.currentTask.status = 'failed'
      this.currentTask.message = message
      this.notify()
    }
  }

  // 获取当前任务
  getCurrentTask(): UpdateTask | null {
    return this.currentTask
  }

  // 订阅更新
  subscribe(callback: (task: UpdateTask | null) => void) {
    this.listeners.add(callback)
    return () => this.listeners.delete(callback)
  }

  // 通知所有订阅者
  private notify() {
    this.listeners.forEach(callback => callback(this.currentTask))
  }
}

// 单例实例
export const dataUpdateProgress = new DataUpdateProgressService()

// 挂载到 window（开发环境调试用）
if (import.meta.env.DEV) {
  (window as any).__dataUpdateProgress = dataUpdateProgress
}
