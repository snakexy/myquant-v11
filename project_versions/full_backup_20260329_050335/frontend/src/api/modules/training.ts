/**
 * MyQuant v10.0.0 - Training API
 * 在线滚动训练相关API
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 模型信息
export interface Model {
  id: string
  name: string
  version: string
  type: 'lstm' | 'transformer' | 'gru' | 'topk_dropout'
  status: 'idle' | 'training' | 'completed' | 'failed'
  description?: string
}

// 训练状态
export type TrainingStatus = 'idle' | 'running' | 'paused' | 'completed' | 'failed'

// 训练参数
export interface TrainingParams {
  trainingWindow: number  // 训练窗口（天数）
  rebalanceFrequency: number  // 滚动周期（天数）
  minReturnRate: number  // 最小收益率（%）
  batchSize?: number  // 批次大小
  learningRate?: number  // 学习率
  epochs?: number  // 训练轮数
}

// 训练进度
export interface TrainingProgress {
  progress: number  // 进度百分比 (0-100)
  currentEpoch: number  // 当前轮数
  totalEpochs: number  // 总轮数
  remainingTime: number  // 剩余时间（秒）
  loss: number  // 当前损失
  accuracy?: number  // 准确率
}

// 训练历史记录
export interface TrainingHistory {
  id: string
  modelId: string
  modelName: string
  status: TrainingStatus
  startTime: string
  endTime?: string
  duration?: number  // 训练时长（秒）
  finalAccuracy?: number
  finalLoss?: number
  params: TrainingParams
  result?: {
    totalReturn: number
    sharpeRatio: number
    maxDrawdown: number
  }
}

// 训练详细信息
export interface TrainingDetail {
  modelId: string
  modelName: string
  modelVersion: string
  status: TrainingStatus
  progress: TrainingProgress
  params: TrainingParams
  startTime?: string
  endTime?: string
}

// ==================== API方法 ====================

export const trainingApi = {
  /**
   * 获取所有可用模型列表
   * GET /api/v1/validation/training/models
   */
  getModels(): Promise<{ code: number; data: Model[]; message: string }> {
    return http.get('/validation/training/models')
  },

  /**
   * 获取当前训练状态
   * GET /api/v1/validation/training/status
   */
  getStatus(): Promise<{ code: number; data: TrainingDetail; message: string }> {
    return http.get('/validation/training/status')
  },

  /**
   * 获取训练参数配置
   * GET /api/v1/validation/training/params
   */
  getParams(): Promise<{ code: number; data: TrainingParams; message: string }> {
    return http.get('/validation/training/params')
  },

  /**
   * 更新训练参数
   * PUT /api/v1/validation/training/params
   * @param params 训练参数
   */
  updateParams(params: TrainingParams): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put('/validation/training/params', params)
  },

  /**
   * 开始训练
   * POST /api/v1/validation/training/start
   * @param modelId 模型ID
   */
  startTraining(modelId: string): Promise<{ code: number; data: TrainingDetail; message: string }> {
    return http.post('/validation/training/start', { modelId })
  },

  /**
   * 暂停训练
   * POST /api/v1/validation/training/pause
   */
  pauseTraining(): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/training/pause')
  },

  /**
   * 恢复训练
   * POST /api/v1/validation/training/resume
   */
  resumeTraining(): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/training/resume')
  },

  /**
   * 停止训练
   * POST /api/v1/validation/training/stop
   */
  stopTraining(): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/training/stop')
  },

  /**
   * 获取训练进度
   * GET /api/v1/validation/training/progress
   */
  getProgress(): Promise<{ code: number; data: TrainingProgress; message: string }> {
    return http.get('/validation/training/progress')
  },

  /**
   * 获取训练历史记录
   * GET /api/v1/validation/training/history
   * @param limit 返回记录数量限制
   */
  getHistory(limit: number = 10): Promise<{ code: number; data: TrainingHistory[]; message: string }> {
    return http.get('/validation/training/history', { params: { limit } })
  },

  /**
   * 切换模型
   * POST /api/v1/validation/training/switch-model
   * @param modelId 新模型ID
   */
  switchModel(modelId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/training/switch-model', { modelId })
  }
}

export default trainingApi
