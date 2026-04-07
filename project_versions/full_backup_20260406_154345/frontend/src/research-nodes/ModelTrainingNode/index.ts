/**
 * 模型训练节点模块
 *
 * 核心任务：机器学习模型训练和评估
 * 支持双输入：特征输入 + AI分析输入
 */

import type { NodeModule } from '../base/BaseNode'
import { modelTrainingConfig } from './config'
import { updateModelTrainingDisplay, trainModel, fetchData, validateParams, toggleInputPort } from './data'

/**
 * 模型训练节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const ModelTrainingNode: NodeModule = {
  // 节点类型标识
  type: 'model-training',

  // 基础配置
  ...modelTrainingConfig,

  // 节点处理器
  updateDisplay: updateModelTrainingDisplay,
  fetchData: fetchData,
  trainModel: trainModel,
  validateParams: validateParams,
  toggleInputPort: toggleInputPort,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { modelTrainingConfig } from './config'
export { updateModelTrainingDisplay, trainModel, fetchData, validateParams, toggleInputPort } from './data'
