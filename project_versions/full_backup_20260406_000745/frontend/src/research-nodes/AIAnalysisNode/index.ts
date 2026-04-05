/**
 * AI智能分析节点模块
 *
 * 核心任务：AI驱动的市场分析和策略建议
 */

import type { NodeModule } from '../base/BaseNode'
import { aiAnalysisConfig } from './config'
import { updateAIAnalysisDisplay, analyzeWithAI, fetchData, validateParams } from './data'

/**
 * AI智能分析节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const AIAnalysisNode: NodeModule = {
  // 节点类型标识
  type: 'ai-analysis',

  // 基础配置
  ...aiAnalysisConfig,

  // 节点处理器
  updateDisplay: updateAIAnalysisDisplay,
  fetchData: fetchData,
  analyzeWithAI: analyzeWithAI,
  validateParams: validateParams,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { aiAnalysisConfig } from './config'
export { updateAIAnalysisDisplay, analyzeWithAI, fetchData, validateParams } from './data'
