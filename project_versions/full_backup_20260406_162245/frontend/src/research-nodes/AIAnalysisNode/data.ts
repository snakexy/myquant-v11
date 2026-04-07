/**
 * AI智能分析节点数据处理逻辑
 *
 * 核心任务：AI驱动的市场分析和策略建议
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'

/**
 * 更新AI智能分析节点显示
 */
export async function updateAIAnalysisDisplay(node: any, context: NodeContext) {
  console.log('[AIAnalysisNode] updateDisplay')

  // 检查上游节点
  const upstreamNodes = context.getUpstreamNodes(node.id)
  const hasUpstreamData = upstreamNodes.length > 0

  if (!hasUpstreamData) {
    node.data.content = '等待上游信号数据...\n请连接智能信号引擎节点'
    node.description = '等待上游信号数据'
    return
  }

  // 检查是否已经分析过
  if (node.data?.content && typeof node.data.content === 'string' && node.data.content.includes('分析摘要')) {
    // 已有分析结果
    const summary = node.data.content.split('\n')[0]
    node.description = summary.substring(0, 30) + '...'
    return
  }

  // 显示待分析状态
  node.data.content = '等待执行AI分析...\n请配置分析参数后执行'
  node.description = '等待执行AI分析'
}

/**
 * 执行AI分析
 */
export async function analyzeWithAI(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    const upstreamNodes = context.getUpstreamNodes(node.id)
    const hasUpstreamData = upstreamNodes.length > 0

    if (!hasUpstreamData) {
      ElMessage({
        message: '请先连接上游智能信号引擎节点',
        type: 'warning',
        duration: 3000
      })
      return { success: false, errors: ['请先连接上游智能信号引擎节点'] }
    }

    // 获取上游信号数据
    const signalNode = upstreamNodes.find(n => n.id === 'signal-engine')

    if (!signalNode) {
      return { success: false, errors: ['上游没有智能信号引擎节点'] }
    }

    // 更新状态为分析中
    node.data.content = 'AI分析中...'
    node.description = 'AI分析中...'

    const api_endpoint = node.metadata?.api_endpoint || 'http://localhost:8000/api/v1/ai_assistant/market-analysis'

    const request_params = {
      signal_data: signalNode.data?.data || {},
      analysis_type: node.params?.analysisType || 'market-trend',
      depth: node.params?.depth || 'standard',
      output_format: node.params?.outputFormat || 'detailed',
      include_charts: node.params?.includeCharts ?? true,
      include_risk: node.params?.includeRisk ?? true
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
      throw new Error(result.detail || result.message || 'AI分析失败')
    }

    // 更新显示内容
    const analysis = result.data?.analysis || '分析完成'
    const summary = result.data?.summary || '分析已完成'

    node.data.content = `分析摘要: ${summary}\n\n${analysis}`
    node.description = summary.substring(0, 30) + '...'

    return {
      success: true,
      data: {
        analysis: analysis,
        summary: summary,
        charts: result.data?.charts || [],
        risk_assessment: result.data?.risk_assessment || {}
      },
      message: 'AI分析完成'
    }
  } catch (error) {
    console.error('[AIAnalysisNode] AI分析失败:', error)

    node.data.content = `AI分析失败: ${error.message}`

    return {
      success: false,
      errors: [error.message]
    }
  }
}

/**
 * 获取数据（执行AI分析）
 */
export async function fetchData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  return await analyzeWithAI(node, context)
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  const validAnalysisTypes = ['market-trend', 'individual-stock', 'portfolio']
  if (!validAnalysisTypes.includes(params.analysisType)) {
    errors.push('请选择有效的分析类型')
  }

  const validDepths = ['basic', 'standard', 'comprehensive']
  if (!validDepths.includes(params.depth)) {
    errors.push('请选择有效的分析深度')
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}
