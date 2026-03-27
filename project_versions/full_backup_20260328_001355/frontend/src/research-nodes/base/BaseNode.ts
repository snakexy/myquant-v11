/**
 * 基础节点类
 * 所有节点模块的基类，提供通用的节点功能
 */

import type { Ref } from 'vue'

// 节点数据类型
export type NodeDataType = 'table' | 'stats' | 'list' | 'chart' | 'text' | 'custom'

// 节点分类
export type NodeCategory =
  | 'data-acquisition'   // 数据获取
  | 'data-processing'    // 数据处理
  | 'feature-engineering' // 特征工程
  | 'analysis'          // 分析
  | 'backtest'          // 回测
  | 'trading'           // 交易
  | 'output'            // 输出
  | 'utility'           // 工具

// 节点执行上下文
export interface NodeContext {
  // 所有节点引用
  nodes: Ref<any[]>
  // 连线引用
  connections: Ref<any[]>
  // 获取上游节点
  getUpstreamNodes: (nodeId: string) => any[]
  // 获取下游节点
  getDownstreamNodes: (nodeId: string) => any[]
  // 全局状态
  globalState: Record<string, any>
  // API服务
  api?: any
}

// 节点执行结果
export interface NodeExecutionResult {
  success: boolean
  data?: any
  errors?: string[]
  warnings?: string[]
}

// 输入端口配置接口
export interface InputPortConfig {
  id: string
  label: string
  active: boolean
  description?: string
}

// 基础节点配置接口
export interface BaseNodeConfig {
  // 节点唯一标识
  id: string

  // 节点分类
  category: NodeCategory

  // UI 配置
  icon: string
  title: string
  description: string

  // 默认位置
  x?: number
  y?: number

  // 输入端口配置
  inputs?: InputPortConfig[]

  // 默认参数
  params?: Record<string, any>

  // 元数据
  metadata?: Record<string, any>

  // 默认数据
  data?: {
    type: NodeDataType
    content: any
  }
}

// 节点操作接口
export interface NodeHandlers {
  // 更新节点显示
  updateDisplay?: (node: any, context: NodeContext) => void | Promise<void>

  // 获取数据
  fetchData?: (node: any, context: NodeContext) => Promise<NodeExecutionResult>

  // 验证参数
  validateParams?: (params: Record<string, any>) => { valid: boolean; errors?: string[] }

  // 执行节点
  execute?: (node: any, context: NodeContext) => Promise<NodeExecutionResult>

  // 处理输入数据变化
  onInputChange?: (node: any, inputNode: any, context: NodeContext) => void | Promise<void>
}

// 完整的节点模块接口
export interface NodeModule extends BaseNodeConfig, NodeHandlers {
  // 节点类型ID（与id相同）
  type: string
}

/**
 * 创建基础节点的工厂函数
 */
export function createBaseNode(config: BaseNodeConfig): any {
  return {
    id: config.id,
    x: config.x ?? 100,
    y: config.y ?? 100,
    icon: config.icon,
    title: config.title,
    description: config.description,
    inputs: config.inputs || [],
    params: config.params || {},
    metadata: config.metadata || {},
    data: config.data || {
      type: 'table' as NodeDataType,
      content: []
    }
  }
}

/**
 * 节点工具类
 */
export class NodeUtils {
  /**
   * 格式化表格值
   */
  static formatTableValue(value: any): { text: string; color: string } {
    if (typeof value === 'number') {
      if (value > 0) {
        return { text: `+${value.toFixed(2)}`, color: '#22c55e' }
      } else if (value < 0) {
        return { text: value.toFixed(2), color: '#ef4444' }
      }
      return { text: value.toFixed(2), color: '#fff' }
    }

    if (value === '--' || value === '未获取' || value === '获取失败') {
      return { text: String(value), color: 'rgba(255,255,255,0.4)' }
    }

    return { text: String(value), color: '#fff' }
  }

  /**
   * 格式化统计标签
   */
  static formatStatLabel(key: string): string {
    const labelMap: Record<string, string> = {
      'stockCode': '股票代码',
      'stockName': '股票名称',
      'closePrice': '收盘价',
      'changePercent': '涨跌幅',
      'volume': '成交量',
      'close': '收盘价',
      'change': '涨跌额'
    }
    return labelMap[key] || key
  }

  /**
   * 格式化统计值
   */
  static formatStatValue(value: any): { text: string; color: string } {
    return NodeUtils.formatTableValue(value)
  }

  /**
   * 解析股票/指数代码
   */
  static parseCodes(input: string): string[] {
    if (!input) return []
    return input
      .split(/[,，\n]/)
      .map(code => code.trim())
      .filter(code => code)
  }

  /**
   * 添加市场后缀
   */
  static addMarketSuffix(code: string): string {
    if (code.endsWith('.SZ') || code.endsWith('.SH')) {
      return code
    }
    if (code.startsWith('6')) {
      return `${code}.SH`
    } else if (code.startsWith('0') || code.startsWith('3')) {
      return `${code}.SZ`
    }
    return code
  }
}
