/**
 * 特征工程节点数据处理逻辑
 *
 * 核心任务：特征选择、转换和组合
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'

/**
 * 更新特征工程节点显示
 */
export async function updateFeatureEngineeringDisplay(node: any, context: NodeContext) {
  console.log('[FeatureEngineeringNode] updateDisplay')

  // 检查上游节点
  const upstreamNodes = context.getUpstreamNodes(node.id)
  const hasUpstreamData = upstreamNodes.length > 0

  if (!hasUpstreamData) {
    node.data.content = {
      originalFeatures: 0,
      finalFeatures: 0,
      selectionRatio: 0,
      status: '等待输入'
    }
    node.description = '等待上游因子数据'
    return
  }

  // 从上游节点获取因子数据
  const factorNode = upstreamNodes.find(n => n.id === 'factor-engine')

  if (!factorNode || !factorNode.data?.content) {
    node.data.content = {
      originalFeatures: 0,
      finalFeatures: 0,
      selectionRatio: 0,
      status: '等待因子计算'
    }
    node.description = '等待因子计算完成'
    return
  }

  const totalFactors = factorNode.data.content.totalFactors || 0

  // 检查是否已经处理过
  const savedStatus = node.data?.content?.status
  if (savedStatus === 'completed') {
    node.description = `已处理 ${node.data.content.originalFeatures} 个特征`
    return
  }

  // 显示待处理状态
  node.data.content = {
    originalFeatures: totalFactors,
    finalFeatures: Math.min(totalFactors, node.params?.kBest || 50),
    selectionRatio: totalFactors > 0 ? ((Math.min(totalFactors, node.params?.kBest || 50) / totalFactors) * 100).toFixed(1) + '%' : '0%',
    status: 'pending'
  }

  node.description = `待处理 ${totalFactors} 个特征`
}

/**
 * 执行特征工程处理
 */
export async function processFeatures(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    const upstreamNodes = context.getUpstreamNodes(node.id)
    const hasUpstreamData = upstreamNodes.length > 0

    if (!hasUpstreamData) {
      ElMessage({
        message: '请先连接上游因子计算节点',
        type: 'warning',
        duration: 3000
      })
      return { success: false, errors: ['请先连接上游因子计算节点'] }
    }

    // 获取上游因子数据
    const factorNode = upstreamNodes.find(n => n.id === 'factor-engine')

    if (!factorNode) {
      return { success: false, errors: ['上游没有因子计算节点'] }
    }

    const totalFactors = factorNode.data?.content?.totalFactors || 0

    if (totalFactors === 0) {
      return { success: false, errors: ['上游节点没有计算因子'] }
    }

    // 更新状态为处理中
    node.data.content.status = 'processing'

    const api_endpoint = node.metadata?.api_endpoint || 'http://localhost:8000/api/v1/data-processors/market-data'

    const request_params = {
      processing_type: 'feature_engineering',
      input_data: factorNode.data?.data || {},
      config: {
        selection_method: node.params?.selectionMethod || 'variance-threshold',
        k_best: node.params?.kBest || 50,
        transformation: node.params?.transformation || 'none',
        pca_components: node.params?.pcaComponents || 10,
        remove_correlated: node.params?.removeCorrelated ?? false,
        correlation_threshold: node.params?.correlationThreshold ?? 0.95
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
      throw new Error(result.detail || result.message || '特征工程处理失败')
    }

    // 计算处理后的特征数量
    const originalFeatures = totalFactors
    const finalFeatures = result.data?.final_feature_count || Math.min(originalFeatures, node.params?.kBest || 50)
    const selectionRatio = originalFeatures > 0 ? ((finalFeatures / originalFeatures) * 100).toFixed(1) + '%' : '0%'

    // 更新显示内容
    node.data.content = {
      originalFeatures,
      finalFeatures,
      selectionRatio,
      status: 'completed'
    }

    node.description = `已处理 ${originalFeatures} → ${finalFeatures} 个特征`

    return {
      success: true,
      data: {
        features: result.data?.features || [],
        feature_importance: result.data?.feature_importance || {},
        original_count: originalFeatures,
        final_count: finalFeatures
      },
      message: `成功处理特征：${originalFeatures} → ${finalFeatures}`
    }
  } catch (error) {
    console.error('[FeatureEngineeringNode] 处理失败:', error)

    node.data.content.status = 'failed'

    return {
      success: false,
      errors: [error.message]
    }
  }
}

/**
 * 获取数据（执行特征工程）
 */
export async function fetchData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  return await processFeatures(node, context)
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  if (params.kBest !== undefined) {
    const k = parseInt(params.kBest)
    if (isNaN(k) || k <= 0) {
      errors.push('保留特征数量必须大于0')
    }
  }

  if (params.correlationThreshold !== undefined) {
    const threshold = parseFloat(params.correlationThreshold)
    if (isNaN(threshold) || threshold < 0 || threshold > 1) {
      errors.push('相关性阈值必须在0-1之间')
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}
