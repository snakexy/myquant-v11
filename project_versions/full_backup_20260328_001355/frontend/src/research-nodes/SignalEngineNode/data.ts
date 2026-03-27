/**
 * 智能信号引擎节点数据处理逻辑
 *
 * 核心任务：技术分析和模式识别
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'

/**
 * 更新智能信号引擎节点显示
 */
export async function updateSignalEngineDisplay(node: any, context: NodeContext) {
  console.log('[SignalEngineNode] updateDisplay')

  // 检查上游节点
  const upstreamNodes = context.getUpstreamNodes(node.id)
  const hasUpstreamData = upstreamNodes.length > 0

  if (!hasUpstreamData) {
    node.data.content = [
      '等待上游特征数据...',
      '请连接特征工程节点'
    ]
    node.description = '等待上游特征数据'
    return
  }

  // 检查是否已经检测过
  if (node.data?.content && node.data.content.length > 0 && typeof node.data.content[0] === 'object' && 'signal' in node.data.content[0]) {
    node.description = `检测到 ${node.data.content.length} 个信号`
    return
  }

  // 显示待检测状态
  node.data.content = [
    '等待信号检测...',
    '请配置技术指标后执行检测'
  ]
  node.description = '等待信号检测'
}

/**
 * 执行信号检测
 */
export async function detectSignals(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    const upstreamNodes = context.getUpstreamNodes(node.id)
    const hasUpstreamData = upstreamNodes.length > 0

    if (!hasUpstreamData) {
      ElMessage({
        message: '请先连接上游特征工程节点',
        type: 'warning',
        duration: 3000
      })
      return { success: false, errors: ['请先连接上游特征工程节点'] }
    }

    // 获取上游特征数据
    const featureNode = upstreamNodes.find(n => n.id === 'feature-engineering')

    if (!featureNode) {
      return { success: false, errors: ['上游没有特征工程节点'] }
    }

    // 更新状态为检测中
    node.data.content = ['信号检测中...']
    node.description = '信号检测中...'

    const api_endpoint = node.metadata?.api_endpoint || 'http://localhost:8000/api/v1/ai_realtime_processing/streams/create'

    const request_params = {
      name: '信号检测流',
      description: '技术指标信号检测',
      data_source: 'feature_data',
      symbols: [], // 从上游获取
      frequency: 'daily',
      processing_config: {
        indicators: node.params?.indicators || {},
        signal_rules: node.params?.signalRules || {},
        pattern_detection: node.params?.patternDetection ?? true,
        patterns: node.params?.patterns || []
      }
    }

    const response = await fetch(api_endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request_params)
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const result = await response.json()

    if (!result.success) {
      throw new Error(result.detail || result.message || '信号检测失败')
    }

    // 更新显示内容 - 信号列表
    const signals = result.data?.signals || []

    node.data.content = signals.map((signal: any) => ({
      signal: signal.type || signal.signal || '信号',
      strength: signal.strength || signal.confidence || '--',
      direction: signal.direction || '--',
      symbol: signal.symbol || '--',
      time: signal.time || signal.timestamp || '--'
    }))

    node.description = `检测到 ${signals.length} 个信号`

    return {
      success: true,
      data: {
        signals: signals,
        signal_count: signals.length
      },
      message: `成功检测到 ${signals.length} 个交易信号`
    }
  } catch (error) {
    console.error('[SignalEngineNode] 信号检测失败:', error)

    node.data.content = [
      '信号检测失败',
      error.message
    ]

    return {
      success: false,
      errors: [error.message]
    }
  }
}

/**
 * 获取数据（执行信号检测）
 */
export async function fetchData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  return await detectSignals(node, context)
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  // 检查是否有至少一个技术指标启用
  const hasIndicator =
    (params.indicators?.ma && params.indicators?.maPeriods?.length > 0) ||
    params.indicators?.macd ||
    params.indicators?.rsi ||
    params.indicators?.bollinger ||
    params.indicators?.kdj

  if (!hasIndicator) {
    errors.push('请至少启用一个技术指标')
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}
