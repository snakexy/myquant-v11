/**
 * AI助手策略构思节点数据处理逻辑
 *
 * 核心任务：AI生成交易策略因子
 * 独立起点节点，输出到因子计算引擎节点的AI驱动输入端口
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'

/**
 * 更新AI助手策略构思节点显示
 */
export async function updateAIStrategyAssistantDisplay(node: any, context: NodeContext) {
  console.log('[AIStrategyAssistantNode] updateDisplay')

  // 检查是否已经生成过
  if (node.data?.content && typeof node.data.content === 'string' && node.data.content.includes('因子表达式')) {
    const lines = node.data.content.split('\n')
    node.description = lines[0].substring(0, 25) + '...'
    return
  }

  // 显示待生成状态
  node.data.content = '等待生成策略...\n请描述您的策略想法'
  node.description = '等待生成策略'
}

/**
 * 生成策略
 */
export async function generateStrategy(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    // 更新状态为生成中
    node.data.content = 'AI正在生成策略...'
    node.description = '策略生成中...'

    const api_endpoint = node.metadata?.api_endpoint || 'http://localhost:8000/api/v1/research/ai/factor/generate'

    const request_params = {
      name: `${node.params?.strategyType || 'trend-following'}策略`,
      description: node.params?.description || '',
      strategy_type: node.params?.strategyType || 'trend-following',
      risk_management: {
        risk_level: node.params?.riskLevel || 'moderate',
        include_stop_loss: node.params?.includeStopLoss ?? true,
        include_take_profit: node.params?.includeTakeProfit ?? true
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
      throw new Error(result.detail || result.message || '策略生成失败')
    }

    // 更新显示内容
    const strategy = result.data?.strategy || {}
    const factorExpression = strategy.factor_expression || '--'
    const description = strategy.description || '策略已生成'

    node.data.content = `${description}\n\n因子表达式:\n${factorExpression}`

    if (strategy.stop_loss) {
      node.data.content += `\n\n止损: ${strategy.stop_loss}`
    }
    if (strategy.take_profit) {
      node.data.content += `\n\n止盈: ${strategy.take_profit}`
    }

    node.description = description.substring(0, 25) + '...'

    return {
      success: true,
      data: {
        strategy: strategy,
        factor_expression: factorExpression,
        description: description
      },
      message: '策略生成成功'
    }
  } catch (error) {
    console.error('[AIStrategyAssistantNode] 策略生成失败:', error)

    node.data.content = `策略生成失败: ${error.message}`

    return {
      success: false,
      errors: [error.message]
    }
  }
}

/**
 * 获取数据（生成策略）
 */
export async function fetchData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  return await generateStrategy(node, context)
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  const validStrategyTypes = ['trend-following', 'mean-reversion', 'momentum', 'custom']
  if (!validStrategyTypes.includes(params.strategyType)) {
    errors.push('请选择有效的策略类型')
  }

  const validRiskLevels = ['conservative', 'moderate', 'aggressive']
  if (!validRiskLevels.includes(params.riskLevel)) {
    errors.push('请选择有效的风险偏好')
  }

  if (params.strategyType === 'custom' && !params.description) {
    errors.push('自定义策略需要提供策略描述')
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}
