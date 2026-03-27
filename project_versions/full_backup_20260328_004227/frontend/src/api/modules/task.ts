/**
 * MyQuant v10.0.0 - Task Management API
 * Task任务管理API接口封装
 * 批量管理多个任务（滚动训练、多模型对比）
 */

import { http } from '../request'

// ==================== 类型定义 ====================

export type TaskGenType = 'rolling' | 'multi_loss' | 'optuna' | 'custom'
export type TaskPoolStatus = 'waiting' | 'running' | 'done' | 'failed' | 'part_done'

export interface TaskPool {
  name: string
  description: string
  created_at: string
  total_tasks: number
  completed_tasks: number
}

export interface TaskPoolStats {
  total: number
  waiting: number
  running: number
  done: number
  failed: number
  part_done: number
}

export interface TaskConfig {
  model: Record<string, any>
  dataset: Record<string, any>
  record: Array<Record<string, any>>
}

export interface GenerateTasksRequest {
  taskTemplate: TaskConfig
  genType: TaskGenType
  genConfig?: Record<string, any>
  // 滚动任务
  rollSteps?: string[][]
  // 多损失函数
  losses?: string[]
  // 超参搜索
  searchSpace?: Record<string, any>
  nTrials?: number
}

export interface TaskResult {
  taskId: string
  status: string
  config: Record<string, any>
  result?: Record<string, any>
  completedAt?: string
}

export interface TaskTemplate {
  id: string
  name: string
  description: string
  genType: TaskGenType
  template?: TaskConfig
  losses?: string[]
  searchSpace?: Record<string, any>
}

// ==================== API方法 ====================

export const taskApi = {
  /**
   * 获取任务池列表
   * GET /api/v1/task/pools
   */
  getPools(): Promise<{ code: number; data: TaskPool[]; message: string }> {
    return http.get('/v1/task/pools')
  },

  /**
   * 创建任务池
   * POST /api/v1/task/pools
   */
  createPool(data: {
    name: string
    description?: string
    config?: Record<string, any>
  }): Promise<{ code: number; data: { name: string }; message: string }> {
    return http.post('/v1/task/pools', data)
  },

  /**
   * 获取任务池统计
   * GET /api/v1/task/pools/{pool_name}/stats
   */
  getPoolStats(poolName: string): Promise<{ code: number; data: TaskPoolStats; message: string }> {
    return http.get(`/v1/task/pools/${poolName}/stats`)
  },

  /**
   * 生成任务
   * POST /api/v1/task/pools/{pool_name}/tasks
   */
  generateTasks(poolName: string, request: GenerateTasksRequest): Promise<{
    code: number
    data: {
      taskIds: string[]
      count: number
      genType: string
    }
    message: string
  }> {
    return http.post(`/v1/task/pools/${poolName}/tasks`, request)
  },

  /**
   * 启动训练
   * POST /api/v1/task/pools/{pool_name}/start
   */
  startTraining(poolName: string, options?: {
    parallelWorkers?: number
    delayTraining?: boolean
  }): Promise<{
    code: number
    data: {
      executionId: string
      poolName: string
      waitingTasks: number
    }
    message: string
  }> {
    return http.post(`/v1/task/pools/${poolName}/start`, options || {})
  },

  /**
   * 获取收集结果
   * GET /api/v1/task/pools/{pool_name}/results
   */
  getResults(poolName: string): Promise<{
    code: number
    data: {
      poolName: string
      results: TaskResult[]
      total: number
    }
    message: string
  }> {
    return http.get(`/v1/task/pools/${poolName}/results`)
  },

  /**
   * 重置任务池
   * POST /api/v1/task/pools/{pool_name}/reset
   */
  resetPool(poolName: string): Promise<{ code: number; data: { resetCount: number }; message: string }> {
    return http.post(`/v1/task/pools/${poolName}/reset`)
  },

  /**
   * 删除任务池
   * DELETE /api/v1/task/pools/{pool_name}
   */
  deletePool(poolName: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.delete(`/v1/task/pools/${poolName}`)
  },

  /**
   * 获取任务模板列表
   * GET /api/v1/task/templates
   */
  getTemplates(): Promise<{ code: number; data: TaskTemplate[]; message: string }> {
    return http.get('/v1/task/templates')
  }
}

export default taskApi
