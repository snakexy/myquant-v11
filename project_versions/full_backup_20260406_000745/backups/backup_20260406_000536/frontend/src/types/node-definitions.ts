/**
 * 节点定义类型系统
 * 用于支持模块化节点的类型定义
 */

import { Ref } from 'vue'

// 基础节点类型
export interface BaseNode {
  id: string
  x: number
  y: number
  icon: string
  title: string
  description: string
  params?: Record<string, any>
  metadata?: Record<string, any>
  data: {
    type: 'table' | 'stats' | 'list' | 'chart' | 'custom'
    content: any
  }
}

// 节点动作定义
export interface NodeAction {
  id: string
  label: string
  icon?: string
  handler: () => void | Promise<void>
  show?: () => boolean
  disabled?: () => boolean
}

// 节点配置表单定义
export interface NodeConfigField {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'multiselect' | 'date' | 'checkbox' | 'textarea'
  placeholder?: string
  options?: Array<{ label: string; value: any }>
  default?: any
  required?: boolean
  validation?: (value: any) => string | true
}

// 节点模块接口 - 每个节点模块需要实现此接口
export interface NodeModule {
  // 节点类型ID（唯一标识）
  type: string

  // 创建默认节点实例
  createNode: (position?: { x: number; y: number }) => BaseNode

  // 节点配置表单定义
  getConfigFields?: () => NodeConfigField[]

  // 节点动作定义
  getActions?: (node: BaseNode, context: NodeContext) => NodeAction[]

  // 自定义渲染组件（可选）
  renderComponent?: any

  // 节点数据更新逻辑
  updateNodeData?: (node: BaseNode, context: NodeContext) => void | Promise<void>

  // 节点参数验证
  validateParams?: (params: Record<string, any>) => { valid: boolean; errors?: string[] }

  // 节点执行逻辑
  execute?: (node: BaseNode, context: NodeContext) => Promise<NodeExecutionResult>
}

// 节点执行上下文
export interface NodeContext {
  // 所有节点引用
  nodes: Ref<BaseNode[]>
  // 连线引用
  connections: Ref<Connection[]>
  // 获取上游节点
  getUpstreamNodes: (nodeId: string) => BaseNode[]
  // 获取下游节点
  getDownstreamNodes: (nodeId: string) => BaseNode[]
  // 全局状态
  globalState: Record<string, any>
  // API服务
  api: {
    getStockHistory: any
    getBatchStockNames: any
    // ... 其他API方法
  }
}

// 节点执行结果
export interface NodeExecutionResult {
  success: boolean
  data?: any
  errors?: string[]
  warnings?: string[]
}

// 连线类型
export interface Connection {
  from: string
  to: string
  id?: string
}

// 节点分类
export type NodeCategory =
  | 'data-acquisition'  // 数据获取
  | 'data-processing'   // 数据处理
  | 'feature-engineering' // 特征工程
  | 'analysis'          // 分析
  | 'backtest'          // 回测
  | 'trading'           // 交易
  | 'output'            // 输出
  | 'utility'           // 工具

// 节点注册表项
export interface NodeRegistryItem {
  type: string
  category: NodeCategory
  module: NodeModule
  icon: string
  title: string
  description: string
  tags?: string[]
}
