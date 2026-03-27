/**
 * MyQuant v10.0.0 - Online Learning API
 * 在线滚动训练相关API
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 学习配置
export interface LearningConfig {
  modelId: string
  learningFrequency: number // 学习频率（秒）
  windowSize: number // 时间窗口大小
  retrainThreshold: number // 重训练阈值
  autoRetrain: boolean // 是否自动重训练
}

// 模型版本信息
export interface ModelVersion {
  versionId: string
  modelId: string
  versionNumber: number
  createdAt: string
  performanceMetrics: PerformanceMetrics
  isCurrent: boolean
}

// 性能指标
export interface PerformanceMetrics {
  sharpeRatio: number
  totalReturn: number
  totalReturnRate: number
  maxDrawdown: number
  winRate: number
  profitLossRatio: number
  volatility: number
}

// 训练进度
export interface TrainingProgress {
  isTraining: boolean
  currentEpoch: number
  totalEpochs: number
  progress: number // 0-100
  loss: number
  accuracy?: number
  startTime: string
  estimatedEndTime?: string
}

// 学习统计
export interface LearningStatistics {
  modelId: string
  totalVersions: number
  currentVersion: number
  isDegraded: boolean
  lastUpdateTime: string
  trainingHistory: TrainingHistoryItem[]
}

// 训练历史项
export interface TrainingHistoryItem {
  versionId: string
  versionNumber: number
  timestamp: string
  sharpeRatio: number
  isCurrentVersion: boolean
}

// 性能对比
export interface PerformanceComparison {
  currentVersion: ModelVersion
  previousVersion?: ModelVersion
  baselineVersion?: ModelVersion
  comparison: {
    sharpeRatioChange: number
    totalReturnChange: number
    maxDrawdownChange: number
  }
}

// 更新请求
export interface UpdateModelRequest {
  newData: any[] // 新数据
  incremental?: boolean // 是否增量学习
}

// 评估响应
export interface EvaluateResponse {
  modelId: string
  versionId: string
  metrics: PerformanceMetrics
  isDegraded: boolean
  degradationReason?: string
}

// 回滚响应
export interface RollbackResponse {
  success: boolean
  previousVersionId: string
  currentVersionId: string
  message: string
}

// ==================== API方法 ====================

export const learningApi = {
  /**
   * 启动在线学习
   * POST /api/v1/validation/learning/start
   * @param config 学习配置
   */
  startLearning(config: LearningConfig): Promise<{ code: number; data: { success: boolean; sessionId: string }; message: string }> {
    return http.post('/v1/validation/learning/start', config)
  },

  /**
   * 更新模型
   * POST /api/v1/validation/learning/update
   * @param request 更新请求
   */
  updateModel(request: UpdateModelRequest): Promise<{ code: number; data: { success: boolean; versionId: string }; message: string }> {
    return http.post('/v1/validation/learning/update', request)
  },

  /**
   * 评估性能
   * GET /api/v1/validation/learning/evaluate
   * @param modelId 模型ID
   */
  evaluatePerformance(modelId: string): Promise<{ code: number; data: EvaluateResponse; message: string }> {
    return http.get('/v1/validation/learning/evaluate', { params: { model_id: modelId } })
  },

  /**
   * 回滚模型
   * POST /api/v1/validation/learning/rollback
   * @param modelId 模型ID
   * @param targetVersionId 目标版本ID（可选，默认回滚到上一版本）
   */
  rollbackModel(modelId: string, targetVersionId?: string): Promise<{ code: number; data: RollbackResponse; message: string }> {
    return http.post('/v1/validation/learning/rollback', { modelId, targetVersionId })
  },

  /**
   * 获取学习统计
   * GET /api/v1/validation/learning/statistics
   * @param modelId 模型ID
   */
  getStatistics(modelId: string): Promise<{ code: number; data: LearningStatistics; message: string }> {
    return http.get('/v1/validation/learning/statistics', { params: { model_id: modelId } })
  },

  /**
   * 检查性能退化
   * POST /api/v1/validation/learning/check-performance
   * @param modelId 模型ID
   * @param currentMetrics 当前性能指标
   */
  checkPerformanceDegradation(modelId: string, currentMetrics: PerformanceMetrics): Promise<{ code: number; data: { isDegraded: boolean; reason?: string }; message: string }> {
    return http.post('/v1/validation/learning/check-performance', { modelId, currentMetrics })
  },

  /**
   * 获取训练进度
   * GET /api/v1/validation/learning/progress
   * @param modelId 模型ID
   */
  getTrainingProgress(modelId: string): Promise<{ code: number; data: TrainingProgress; message: string }> {
    return http.get('/v1/validation/learning/progress', { params: { model_id: modelId } })
  },

  /**
   * 获取模型版本列表
   * GET /api/v1/validation/learning/versions
   * @param modelId 模型ID
   * @param limit 返回数量限制
   */
  getModelVersions(modelId: string, limit: number = 10): Promise<{ code: number; data: ModelVersion[]; message: string }> {
    return http.get('/v1/validation/learning/versions', { params: { model_id: modelId, limit } })
  },

  /**
   * 获取性能对比
   * GET /api/v1/validation/learning/comparison
   * @param modelId 模型ID
   */
  getPerformanceComparison(modelId: string): Promise<{ code: number; data: PerformanceComparison; message: string }> {
    return http.get('/v1/validation/learning/comparison', { params: { model_id: modelId } })
  },

  /**
   * 停止训练
   * POST /api/v1/validation/learning/stop
   * @param modelId 模型ID
   */
  stopTraining(modelId?: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/v1/validation/learning/stop', { modelId })
  },

  /**
   * 开始训练（旧接口兼容）
   * POST /api/v1/validation/learning/start
   * @param modelId 模型ID
   */
  startTraining(modelId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/v1/validation/learning/start', { modelId })
  },

  /**
   * 获取通用进度（旧接口兼容）
   * GET /api/v1/validation/learning/progress
   */
  getProgress(): Promise<{ code: number; data: { progress: number; currentEpoch: number; remainingTime: number }; message: string }> {
    return http.get('/v1/validation/learning/progress')
  },

  /**
   * 首次训练（新接口 - OnlineManager）
   * POST /api/v1/validation/learning/first-train
   * @param modelId 模型ID
   */
  firstTrain(modelId: string): Promise<{ code: number; data: any; message: string }> {
    return http.post('/v1/validation/learning/first-train', { model_id: modelId })
  },

  /**
   * 获取训练进度v2（新接口 - OnlineManager）
   * GET /api/v1/validation/learning/progress/v2
   * @param modelId 模型ID
   */
  getProgressV2(modelId: string): Promise<{ code: number; data: { modelId: string; isRunning: boolean; currentOnlineModel: string | null; lastRoutineTime: string | null; totalRoutines: number; latestSignals: any }; message: string }> {
    return http.get('/v1/validation/learning/progress/v2', { params: { model_id: modelId } })
  },

  /**
   * 手动触发例行更新（新接口 - OnlineManager）
   * POST /api/v1/validation/learning/routine
   * @param modelId 模型ID
   * @param curTime 当前时间
   */
  routine(modelId: string, curTime?: string): Promise<{ code: number; data: any; message: string }> {
    return http.post('/v1/validation/learning/routine', { model_id: modelId, cur_time: curTime })
  },

  /**
   * 获取交易信号
   * GET /api/v1/validation/learning/signals
   * @param modelId 模型ID
   */
  getSignals(modelId: string): Promise<{ code: number; data: { buy: string[]; sell: string[]; timestamp: string; confidence: number; models_used: number }; message: string }> {
    return http.get('/v1/validation/learning/signals', { params: { model_id: modelId } })
  },

  /**
   * 启动定时调度 ⭐ 新增
   * POST /api/v1/validation/learning/schedule/start
   * @param modelId 模型ID
   * @param hour 小时（默认15）
   * @param minute 分钟（默认0）
   */
  startSchedule(modelId: string, hour: number = 15, minute: number = 0): Promise<{ code: number; data: { model_id: string; schedule: string; status: string; enabled: boolean }; message: string }> {
    return http.post('/v1/validation/learning/schedule/start', { model_id: modelId, hour, minute })
  },

  /**
   * 获取调度状态 ⭐ 新增
   * GET /api/v1/validation/learning/schedule/status
   * @param modelId 模型ID
   */
  getScheduleStatus(modelId: string): Promise<{ code: number; data: { model_id: string; scheduled: boolean; enabled: boolean; schedule_time: string; is_running: boolean }; message: string }> {
    return http.get('/v1/validation/learning/schedule/status', { params: { model_id: modelId } })
  },

  /**
   * 停止调度 ⭐ 新增
   * POST /api/v1/validation/learning/schedule/stop
   * @param modelId 模型ID
   */
  stopSchedule(modelId: string): Promise<{ code: number; data: { model_id: string; status: string; enabled: boolean }; message: string }> {
    return http.post('/v1/validation/learning/schedule/stop', { model_id: modelId })
  },

  /**
   * 切换模型（旧接口兼容）
   * POST /api/v1/validation/learning/switch
   * @param modelId 模型ID
   */
  switchModel(modelId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/v1/validation/learning/switch', { modelId })
  }
}

export default learningApi
