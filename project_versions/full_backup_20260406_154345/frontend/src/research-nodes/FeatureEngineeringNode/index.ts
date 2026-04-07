/**
 * 特征工程节点模块
 *
 * 核心任务：特征选择、转换和组合
 */

import type { NodeModule } from '../base/BaseNode'
import { featureEngineeringConfig } from './config'
import { updateFeatureEngineeringDisplay, processFeatures, fetchData, validateParams } from './data'

/**
 * 特征工程节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const FeatureEngineeringNode: NodeModule = {
  // 节点类型标识
  type: 'feature-engineering',

  // 基础配置
  ...featureEngineeringConfig,

  // 节点处理器
  updateDisplay: updateFeatureEngineeringDisplay,
  fetchData: fetchData,
  processFeatures: processFeatures,
  validateParams: validateParams,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { featureEngineeringConfig } from './config'
export { updateFeatureEngineeringDisplay, processFeatures, fetchData, validateParams } from './data'
