/**
 * 初步验证节点模块
 *
 * 核心任务：模型性能初步验证
 * 终点节点
 */

import type { NodeModule } from '../base/BaseNode'
import { preliminaryValidationConfig } from './config'
import { updatePreliminaryValidationDisplay, runBacktest, fetchData, validateParams } from './data'

/**
 * 初步验证节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const PreliminaryValidationNode: NodeModule = {
  // 节点类型标识
  type: 'preliminary-validation',

  // 基础配置
  ...preliminaryValidationConfig,

  // 节点处理器
  updateDisplay: updatePreliminaryValidationDisplay,
  fetchData: fetchData,
  runBacktest: runBacktest,
  validateParams: validateParams,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { preliminaryValidationConfig } from './config'
export { updatePreliminaryValidationDisplay, runBacktest, fetchData, validateParams } from './data'
