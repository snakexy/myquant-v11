/**
 * 智能信号引擎节点模块
 *
 * 核心任务：技术分析和模式识别
 */

import type { NodeModule } from '../base/BaseNode'
import { signalEngineConfig } from './config'
import { updateSignalEngineDisplay, detectSignals, fetchData, validateParams } from './data'

/**
 * 智能信号引擎节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const SignalEngineNode: NodeModule = {
  // 节点类型标识
  type: 'signal-engine',

  // 基础配置
  ...signalEngineConfig,

  // 节点处理器
  updateDisplay: updateSignalEngineDisplay,
  fetchData: fetchData,
  detectSignals: detectSignals,
  validateParams: validateParams,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { signalEngineConfig } from './config'
export { updateSignalEngineDisplay, detectSignals, fetchData, validateParams } from './data'
