/**
 * MyQuant v10.0.0 - RL Strategy API
 * RL策略优化API调用封装
 * 包含：RL模型训练、策略优化、模型管理、自动算法选择
 */

import { http } from './request'

// ==================== 类型定义 ====================

/**
 * RL训练请求参数
 */
export interface RLTrainingRequest {
  /** 算法选择 */
  algorithm?: 'DQN' | 'PPO' | 'A2C' | 'AUTO'
  /** 应用场景 */
  scenario?: 'order_execution' | 'portfolio_construction'
  /** 训练参数 */
  max_episodes?: number
  max_steps_per_episode?: number
  /** 网络参数 */
  hidden_size?: number
  num_layers?: number
  learning_rate?: number
  /** 环境参数 */
  state_dim?: number
  action_dim?: number
  /** RL特定参数 */
  gamma?: number
  buffer_size?: number
  batch_size?: number
  /** PPO特定参数 */
  clip_param?: number
  entropy_coef?: number
  /** 设备选择 */
  device?: 'auto' | 'cuda' | 'cpu'
}

/**
 * 自动算法选择请求参数
 */
export interface RLAutoSelectionRequest {
  /** 应用场景 */
  scenario?: 'order_execution' | 'portfolio_construction'
  /** 要测试的算法列表（可选，默认测试所有） */
  algorithms?: ('DQN' | 'PPO' | 'A2C')[]
  /** 每个算法的最大训练轮数 */
  max_episodes?: number
  /** 是否并行训练（当前版本不支持） */
  parallel?: boolean
  /** 设备选择 */
  device?: 'auto' | 'cuda' | 'cpu'
  /** 环境数据（可选） */
  env_data?: Record<string, any>
}

/**
 * 自动算法选择结果
 */
export interface RLAutoSelectionResult {
  selection_id: string
  scenario: string
  algorithms_tried: string[]
  results_by_algorithm: Record<string, {
    training_id?: string
    algorithm: string
    best_reward: number
    average_reward?: number
    final_reward?: number
    total_episodes?: number
    training_duration?: number
    status: string
    error?: string
  }>
  best_algorithm: string
  best_training_id: string
  best_reward: number
  training_duration: number
  created_at: string
}

/**
 * RL模型信息
 */
export interface RLModel {
  training_id: string
  algorithm: string
  scenario: string
  status: 'training' | 'completed' | 'failed'
  episode: number
  total_episodes?: number
  total_reward: number
  final_reward?: number
  avg_reward: number
  average_reward?: number
  best_reward?: number
  created_at: string
  updated_at?: string
  config: Record<string, any>
  rewards_summary?: {
    min: number
    max: number
    mean: number
    std: number
  }
  training_duration?: number
  training_history?: Array<{
    episode: number
    reward: number
    timestamp: string
  }>
}

/**
 * RL训练结果
 */
export interface RLTrainingResult {
  training_id: string
  status: string
  episode: number
  total_episodes: number
  reward: number
  avg_reward: number
  best_avg_reward: number
  model_path?: string
}

/**
 * API响应基础结构
 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  timestamp: string
}

// ==================== RL Strategy API ====================

// RL训练需要较长时间，使用更长的超时时间（5分钟）
const RL_TRAINING_TIMEOUT = 5 * 60 * 1000

// SSE 训练进度事件类型
export interface RLTrainingProgressEvent {
  training_id: string
  progress: number
  status: 'initializing' | 'training' | 'completed' | 'error'
  algorithm: string
  reward: number
  episode: number
  total_episodes: number
  result?: RLTrainingResult
  error?: string
  timestamp: string
}

// SSE 自动选择进度事件类型
export interface RLAutoSelectProgressEvent {
  selection_id: string
  progress: number
  status: 'initializing' | 'training' | 'completed' | 'error'
  current_algorithm: string
  algorithms: string[]
  results: Record<string, {
    training_id: string
    algorithm: string
    best_reward: number
    average_reward: number
    total_episodes: number
    status: string
  }>
  best_algorithm?: string
  best_reward?: number
  algorithm_progress?: number
  algorithm_status?: string
  episode?: number
  reward?: number
  error?: string
  timestamp: string
}

export const rlStrategyAPI = {
  /**
   * 健康检查
   */
  healthCheck: () => {
    return http.get<ApiResponse<{ service: string; status: string }>>(
      '/v1/research/rl/health'
    )
  },

  /**
   * 使用 SSE 流式训练 - 返回真实进度
   * @param request 训练请求
   * @param onProgress 进度回调
   * @param onComplete 完成回调
   * @param onError 错误回调
   * @returns 返回一个取消函数
   */
  trainStream: (
    request: RLTrainingRequest,
    onProgress: (event: RLTrainingProgressEvent) => void,
    onComplete?: (result: RLTrainingResult) => void,
    onError?: (error: string) => void
  ): (() => void) => {
    // EventSource 只支持 GET，所以使用 fetch + POST 实现 SSE
    let aborted = false
    const controller = new AbortController()

    const startStream = async () => {
      try {
        const response = await fetch('/api/v1/research/rl/train-stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
          signal: controller.signal
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) throw new Error('No reader available')

        const decoder = new TextDecoder()
        let buffer = ''

        while (!aborted) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6)) as RLTrainingProgressEvent
                onProgress(data)

                if (data.status === 'completed') {
                  onComplete?.(data.result || {
                    training_id: data.training_id,
                    status: 'completed',
                    episode: data.episode,
                    total_episodes: data.total_episodes,
                    reward: data.reward,
                    avg_reward: data.reward,
                    best_avg_reward: data.reward
                  } as any)
                } else if (data.status === 'error') {
                  onError?.(data.error || 'Training failed')
                }
              } catch (e) {
                console.warn('Failed to parse SSE data:', line)
              }
            }
          }
        }
      } catch (error: any) {
        if (!aborted) {
          onError?.(error.message || 'Connection failed')
        }
      }
    }

    startStream()

    return () => {
      aborted = true
      controller.abort()
    }
  },

  /**
   * 使用 SSE 流式自动选择 - 返回真实进度
   */
  autoSelectStream: (
    request: RLAutoSelectionRequest,
    onProgress: (event: RLAutoSelectProgressEvent) => void,
    onComplete?: (result: RLAutoSelectionResult) => void,
    onError?: (error: string) => void
  ): (() => void) => {
    let aborted = false
    const controller = new AbortController()

    const startStream = async () => {
      try {
        const response = await fetch('/api/v1/research/rl/auto-select-stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
          signal: controller.signal
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) throw new Error('No reader available')

        const decoder = new TextDecoder()
        let buffer = ''

        while (!aborted) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6)) as RLAutoSelectProgressEvent
                onProgress(data)

                if (data.status === 'completed' && data.best_algorithm) {
                  onComplete?.({
                    selection_id: data.selection_id,
                    scenario: '',
                    algorithms_tried: data.algorithms,
                    results_by_algorithm: data.results,
                    best_algorithm: data.best_algorithm,
                    best_training_id: data.results[data.best_algorithm]?.training_id || '',
                    best_reward: data.best_reward || 0,
                    training_duration: 0,
                    created_at: data.timestamp
                  })
                } else if (data.status === 'error') {
                  onError?.(data.error || 'Auto selection failed')
                }
              } catch (e) {
                console.warn('Failed to parse SSE data:', line)
              }
            }
          }
        }
      } catch (error: any) {
        if (!aborted) {
          onError?.(error.message || 'Connection failed')
        }
      }
    }

    startStream()

    return () => {
      aborted = true
      controller.abort()
    }
  },

  /**
   * 训练RL模型（传统方式，无实时进度）
   */
  train: (request: RLTrainingRequest) => {
    return http.post<ApiResponse<RLTrainingResult>>(
      '/v1/research/rl/train',
      request,
      { timeout: RL_TRAINING_TIMEOUT }
    )
  },

  /**
   * 自动选择最优算法（传统方式，无实时进度）
   * 训练多个算法（DQN、PPO、A2C）并自动选择表现最好的
   */
  autoSelect: (request: RLAutoSelectionRequest = {}) => {
    return http.post<ApiResponse<RLAutoSelectionResult>>(
      '/v1/research/rl/auto-select',
      request,
      { timeout: RL_TRAINING_TIMEOUT }
    )
  },

  /**
   * 优化策略
   */
  optimize: (trainingId: string, params: Record<string, any> = {}) => {
    return http.post<ApiResponse<any>>('/v1/research/rl/optimize', {
      training_id: trainingId,
      ...params
    }, { timeout: RL_TRAINING_TIMEOUT })
  },

  /**
   * 获取模型列表
   */
  getModels: () => {
    return http.get<ApiResponse<{ total: number; models: RLModel[] }>>(
      '/v1/research/rl/models',
      { timeout: RL_TRAINING_TIMEOUT }
    )
  },

  /**
   * 获取模型详情
   */
  getModel: (trainingId: string) => {
    return http.get<ApiResponse<RLModel>>(
      `/v1/research/rl/models/${trainingId}`,
      { timeout: RL_TRAINING_TIMEOUT }
    )
  },

  /**
   * 获取训练历史
   */
  getHistory: (limit: number = 20, offset: number = 0) => {
    return http.get<ApiResponse<any>>(
      `/v1/research/rl/history?limit=${limit}&offset=${offset}`,
      { timeout: RL_TRAINING_TIMEOUT }
    )
  },

  /**
   * 保存模型
   */
  saveModel: (trainingId: string, name?: string) => {
    return http.post<ApiResponse<any>>(
      `/v1/research/rl/models/${trainingId}/save`,
      { name },
      { timeout: RL_TRAINING_TIMEOUT }
    )
  },

  /**
   * 获取统计信息
   */
  getStatistics: () => {
    return http.get<ApiResponse<any>>('/v1/research/rl/statistics')
  }
}

export default rlStrategyAPI
