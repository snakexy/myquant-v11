/**
 * 初步验证节点数据处理逻辑
 *
 * 核心任务：模型性能初步验证
 * 终点节点
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'

/**
 * 更新初步验证节点显示
 */
export async function updatePreliminaryValidationDisplay(node: any, context: NodeContext) {
  console.log('[PreliminaryValidationNode] updateDisplay')

  // 检查上游节点
  const upstreamNodes = context.getUpstreamNodes(node.id)
  const hasUpstreamData = upstreamNodes.length > 0

  if (!hasUpstreamData) {
    node.data.content = {
      validationStatus: 'waiting',
      totalReturn: '--',
      sharpeRatio: '--',
      maxDrawdown: '--',
      winRate: '--'
    }
    node.description = '等待上游模型'
    return
  }

  // 检查是否已经验证过
  if (node.data?.content?.validationStatus === 'completed') {
    node.description = `收益率: ${node.data.content.totalReturn}, 夏普: ${node.data.content.sharpeRatio}`
    return
  }

  // 显示待验证状态
  node.data.content = {
    validationStatus: 'pending',
    totalReturn: '--',
    sharpeRatio: '--',
    maxDrawdown: '--',
    winRate: '--'
  }
  node.description = '待执行回测验证'
}

/**
 * 执行回测验证
 */
export async function runBacktest(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    const upstreamNodes = context.getUpstreamNodes(node.id)
    const hasUpstreamData = upstreamNodes.length > 0

    if (!hasUpstreamData) {
      ElMessage({
        message: '请先连接上游模型训练节点',
        type: 'warning',
        duration: 3000
      })
      return { success: false, errors: ['请先连接上游模型训练节点'] }
    }

    // 获取上游模型数据
    const modelNode = upstreamNodes.find(n => n.id === 'model-training')

    if (!modelNode) {
      return { success: false, errors: ['上游没有模型训练节点'] }
    }

    if (modelNode.data?.content?.trainingStatus !== 'completed') {
      return { success: false, errors: ['上游模型尚未训练完成'] }
    }

    // 更新状态为验证中
    node.data.content.validationStatus = 'validating'
    node.description = '回测验证中...'

    const api_endpoint = node.metadata?.api_endpoint || 'http://localhost:8000/api/v1/backtest/run'

    const request_params = {
      model: modelNode.data?.data?.model || {},
      model_id: modelNode.data?.data?.model_id,
      backtest_period: node.params?.backtestPeriod || {},
      initial_capital: node.params?.initialCapital || 100000,
      commission: node.params?.commission || 0.0003,
      slippage: node.params?.slippage || 0.0001,
      metrics: node.params?.metrics || []
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
      throw new Error(result.detail || result.message || '回测验证失败')
    }

    // 获取验证结果
    const metrics = result.data?.metrics || {}
    const totalReturn = metrics.total_return || metrics.return || '--'
    const sharpeRatio = metrics.sharpe || metrics.sharpe_ratio || '--'
    const maxDrawdown = metrics.max_drawdown || '--'
    const winRate = metrics.win_rate || '--'

    // 更新显示内容
    node.data.content = {
      validationStatus: 'completed',
      totalReturn: typeof totalReturn === 'number' ? (totalReturn * 100).toFixed(2) + '%' : totalReturn,
      sharpeRatio: typeof sharpeRatio === 'number' ? sharpeRatio.toFixed(2) : sharpeRatio,
      maxDrawdown: typeof maxDrawdown === 'number' ? (maxDrawdown * 100).toFixed(2) + '%' : maxDrawdown,
      winRate: typeof winRate === 'number' ? (winRate * 100).toFixed(2) + '%' : winRate
    }

    node.description = `收益率: ${node.data.content.totalReturn}, 夏普: ${node.data.content.sharpeRatio}`

    return {
      success: true,
      data: {
        backtest_report: result.data?.report || {},
        metrics: metrics,
        trades: result.data?.trades || []
      },
      message: '回测验证完成'
    }
  } catch (error) {
    console.error('[PreliminaryValidationNode] 回测验证失败:', error)

    node.data.content.validationStatus = 'failed'

    return {
      success: false,
      errors: [error.message]
    }
  }
}

/**
 * 获取数据（执行回测验证）
 */
export async function fetchData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  return await runBacktest(node, context)
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  if (params.initialCapital !== undefined) {
    const capital = parseFloat(params.initialCapital)
    if (isNaN(capital) || capital <= 0) {
      errors.push('初始资金必须大于0')
    }
  }

  if (params.commission !== undefined) {
    const commission = parseFloat(params.commission)
    if (isNaN(commission) || commission < 0 || commission > 0.01) {
      errors.push('手续费率必须在0-0.01之间')
    }
  }

  if (params.slippage !== undefined) {
    const slippage = parseFloat(params.slippage)
    if (isNaN(slippage) || slippage < 0 || slippage > 0.01) {
      errors.push('滑点率必须在0-0.01之间')
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}
