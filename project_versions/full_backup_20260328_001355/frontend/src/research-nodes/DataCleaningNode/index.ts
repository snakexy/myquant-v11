/**
 * 数据清洗节点模块
 *
 * 核心任务：将数据中枢的股票数据转换为QLib可用的数据格式
 */

import type { NodeModule } from '../base/BaseNode'
import { dataCleaningConfig } from './config'
import { updateDataCleaningNodeDisplay, convertToQLibFormat, fetchData, validateParams } from './data'

/**
 * 数据清洗节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const DataCleaningNode: NodeModule = {
  // 节点类型标识
  type: 'data-cleaning',

  // 基础配置
  ...dataCleaningConfig,

  // 节点处理器
  updateDisplay: updateDataCleaningNodeDisplay,
  fetchData: fetchData,
  convertToQLib: convertToQLibFormat,
  validateParams: validateParams,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { dataCleaningConfig } from './config'
export { updateDataCleaningNodeDisplay, convertToQLibFormat, fetchData, validateParams } from './data'
