/**
 * 节点注册中心
 *
 * 统一导出所有节点模块，提供节点注册和获取功能
 */

import type { NodeModule } from './base/BaseNode'
import { StockSelectionNode } from './StockSelectionNode'
import { IndexSelectionNode } from './IndexSelectionNode'
import { DataCleaningNode } from './DataCleaningNode'
import { FactorEngineNode } from './FactorEngineNode'
import { FeatureEngineeringNode } from './FeatureEngineeringNode'
import { SignalEngineNode } from './SignalEngineNode'
import { AIAnalysisNode } from './AIAnalysisNode'
import { AIStrategyAssistantNode } from './AIStrategyAssistantNode'
import { ModelTrainingNode } from './ModelTrainingNode'
import { PreliminaryValidationNode } from './PreliminaryValidationNode'

/**
 * 节点注册表
 * 存储所有可用的节点模块
 */
const nodeRegistry: Record<string, NodeModule> = {
  'stock-selection': StockSelectionNode,
  'index-selection': IndexSelectionNode,
  'data-cleaning': DataCleaningNode,
  'factor-engine': FactorEngineNode,
  'feature-engineering': FeatureEngineeringNode,
  'signal-engine': SignalEngineNode,
  'ai-analysis': AIAnalysisNode,
  'ai-strategy-assistant': AIStrategyAssistantNode,
  'model-training': ModelTrainingNode,
  'preliminary-validation': PreliminaryValidationNode
}

/**
 * 获取节点模块
 * @param nodeId 节点ID
 * @returns 节点模块，如果不存在则返回 undefined
 */
export function getNodeModule(nodeId: string): NodeModule | undefined {
  return nodeRegistry[nodeId]
}

/**
 * 注册节点模块
 * @param nodeModule 节点模块
 */
export function registerNodeModule(nodeModule: NodeModule): void {
  nodeRegistry[nodeModule.type || nodeModule.id] = nodeModule
}

/**
 * 获取所有已注册的节点模块
 * @returns 节点模块列表
 */
export function getAllNodeModules(): NodeModule[] {
  return Object.values(nodeRegistry)
}

/**
 * 获取所有已注册的节点ID
 * @returns 节点ID列表
 */
export function getAllNodeIds(): string[] {
  return Object.keys(nodeRegistry)
}

/**
 * 检查节点是否已注册
 * @param nodeId 节点ID
 * @returns 是否已注册
 */
export function isNodeRegistered(nodeId: string): boolean {
  return nodeId in nodeRegistry
}

// 导出所有节点模块
export {
  StockSelectionNode,
  IndexSelectionNode,
  DataCleaningNode,
  FactorEngineNode,
  FeatureEngineeringNode,
  SignalEngineNode,
  AIAnalysisNode,
  AIStrategyAssistantNode,
  ModelTrainingNode,
  PreliminaryValidationNode
}

// 导出基础类型和工具
export * from './base/BaseNode'
