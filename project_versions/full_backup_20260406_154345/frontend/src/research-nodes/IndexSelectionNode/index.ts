/**
 * 指数选择节点模块
 *
 * 负责指数选择和数据获取功能
 */

import type { NodeModule } from '../base/BaseNode'
import { indexSelectionConfig } from './config'
import { updateIndexNodeDisplay, fetchIndexData, validateParams } from './data'

/**
 * 指数选择节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const IndexSelectionNode: NodeModule = {
  // 节点类型标识
  type: 'index-selection',

  // 基础配置
  ...indexSelectionConfig,

  // 节点处理器
  updateDisplay: updateIndexNodeDisplay,
  fetchData: fetchIndexData,
  validateParams: validateParams,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchIndexData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { indexSelectionConfig } from './config'
export { updateIndexNodeDisplay, fetchIndexData, validateParams } from './data'
export {
  extractCount,
  extractUnit,
  getStatusTagClass,
  getStatusShortLabel,
  getIndexCountFromTable,
  formatDataCount,
  formatDateRange,
  getFrequencyFromParams,
  miniReportConfig
} from './utils'
