/**
 * AI助手策略构思节点模块
 *
 * 核心任务：AI生成交易策略因子
 * 独立起点节点，输出到因子计算引擎节点的AI驱动输入端口
 */

import type { NodeModule } from '../base/BaseNode'
import { aiStrategyAssistantConfig } from './config'
import { updateAIStrategyAssistantDisplay, generateStrategy, fetchData, validateParams } from './data'

/**
 * AI助手策略构思节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const AIStrategyAssistantNode: NodeModule = {
  // 节点类型标识
  type: 'ai-strategy-assistant',

  // 基础配置
  ...aiStrategyAssistantConfig,

  // 节点处理器
  updateDisplay: updateAIStrategyAssistantDisplay,
  fetchData: fetchData,
  generateStrategy: generateStrategy,
  validateParams: validateParams,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { aiStrategyAssistantConfig } from './config'
export { updateAIStrategyAssistantDisplay, generateStrategy, fetchData, validateParams } from './data'
