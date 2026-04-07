/**
 * 因子计算引擎节点模块
 *
 * 核心共享组件，支持双输入端：
 * - 数据驱动输入端：接收来自数据清洗的数据
 * - AI助手输入端：接收来自AI助手策略构思的数据
 */

import type { NodeModule } from '../base/BaseNode'
import { factorEngineConfig } from './config'
import { updateFactorEngineDisplay, calculateFactors, validateParams, toggleInputPort } from './data'

/**
 * 因子计算引擎节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const FactorEngineNode: NodeModule = {
  // 节点类型标识
  type: 'factor-engine',

  // 基础配置
  ...factorEngineConfig,

  // 节点处理器
  updateDisplay: updateFactorEngineDisplay,
  fetchData: calculateFactors,
  validateParams: validateParams,

  // 自定义方法：切换输入端口
  toggleInputPort: toggleInputPort,

  // 执行方法（默认使用 calculateFactors）
  execute: async (node: any, context: any) => {
    return await calculateFactors(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { factorEngineConfig } from './config'
export { updateFactorEngineDisplay, calculateFactors, validateParams, toggleInputPort } from './data'
