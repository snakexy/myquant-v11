/**
 * 股票选择节点模块
 *
 * 负责股票选择和数据获取功能
 */

import type { NodeModule } from '../base/BaseNode'
import { stockSelectionConfig } from './config'
import { updateStockNodeDisplay, fetchStockData, validateParams } from './data'

/**
 * 股票选择节点模块
 * 合并配置和处理器，提供完整的节点功能
 */
export const StockSelectionNode: NodeModule = {
  // 节点类型标识
  type: 'stock-selection',

  // 基础配置
  ...stockSelectionConfig,

  // 节点处理器
  updateDisplay: updateStockNodeDisplay,
  fetchData: fetchStockData,
  validateParams: validateParams,

  // 执行方法（默认使用 fetchData）
  execute: async (node: any, context: any) => {
    return await fetchStockData(node, context)
  }
}

// 导出配置和处理器，供外部单独使用
export { stockSelectionConfig } from './config'
export { updateStockNodeDisplay, fetchStockData, validateParams } from './data'
export {
  extractCount,
  extractUnit,
  getStatusTagClass,
  getStatusShortLabel,
  getStockCountFromTable,
  formatDataCount,
  formatDateRange,
  getFrequencyFromParams,
  miniReportConfig
} from './utils'
