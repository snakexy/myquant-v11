/**
 * 模型训练节点数据处理逻辑
 *
 * 核心任务：机器学习模型训练和评估
 * 支持双输入：特征输入 + AI分析输入
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'

/**
 * 更新模型训练节点显示
 */
export async function updateModelTrainingDisplay(node: any, context: NodeContext) {
  console.log('[ModelTrainingNode] updateDisplay')

  // 检查输入端口状态
  const featuresActive = node.inputs?.find((i: any) => i.id === 'features')?.active ?? true
  const aiInsightsActive = node.inputs?.find((i: any) => i.id === 'ai-insights')?.active ?? true

  // 获取上游节点
  const upstreamNodes = context.getUpstreamNodes(node.id)

  // 统计激活的输入数量
  const activeInputs = upstreamNodes.filter(n => {
    if (n.id === 'feature-engineering') return featuresActive
    if (n.id === 'ai-analysis') return aiInsightsActive
    return false
  })

  // 更新节点描述
  node.description = activeInputs.length > 0
    ? `模型训练 (${activeInputs.map(n => n.title).join(' + ')})`
    : '模型训练'

  // 检查是否已经训练过
  if (node.data?.content?.trainingStatus === 'completed') {
    node.description = `${node.data.content.modelName} - 准确率: ${node.data.content.accuracy}`
    return
  }

  // 显示待训练状态
  node.data.content = {
    modelName: node.params?.modelType || '--',
    trainingStatus: activeInputs.length > 0 ? 'pending' : 'waiting',
    accuracy: '--',
    sharpe: '--'
  }
}

/**
 * 训练模型
 */
export async function trainModel(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    // 检查输入端口状态
    const featuresActive = node.inputs?.find((i: any) => i.id === 'features')?.active ?? true
    const aiInsightsActive = node.inputs?.find((i: any) => i.id === 'ai-insights')?.active ?? true

    // 获取上游节点
    const upstreamNodes = context.getUpstreamNodes(node.id)

    // 筛选激活的输入节点
    const activeInputs = upstreamNodes.filter(n => {
      if (n.id === 'feature-engineering') return featuresActive
      if (n.id === 'ai-analysis') return aiInsightsActive
      return false
    })

    if (activeInputs.length === 0) {
      return {
        success: false,
        errors: ['没有激活的输入数据源，请先连接特征工程节点或AI分析节点']
      }
    }

    const featureNode = activeInputs.find(n => n.id === 'feature-engineering')
    const aiAnalysisNode = activeInputs.find(n => n.id === 'ai-analysis')

    if (!featureNode) {
      return { success: false, errors: ['需要连接特征工程节点'] }
    }

    // 更新状态为训练中
    node.data.content = {
      modelName: node.params?.modelType || '--',
      trainingStatus: 'training',
      accuracy: '训练中...',
      sharpe: '--'
    }
    node.description = '模型训练中...'

    const api_endpoint = node.metadata?.api_endpoint || 'http://localhost:8000/api/v1/models/train'

    const request_params = {
      model_type: node.params?.modelType || 'xgboost',
      feature_data: featureNode.data?.data || {},
      ai_insights: aiAnalysisNode?.data?.data || {},
      train_params: node.params?.trainParams || {},
      feature_columns: node.params?.featureColumns || [],
      target_column: node.params?.targetColumn || 'return',
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
      throw new Error(result.detail || result.message || '模型训练失败')
    }

    // 获取训练结果
    const metrics = result.data?.metrics || {}
    const accuracy = metrics.accuracy || metrics.sharpe || '--'
    const sharpe = metrics.sharpe || '--'

    // 更新显示内容
    node.data.content = {
      modelName: node.params?.modelType || '--',
      trainingStatus: 'completed',
      accuracy: typeof accuracy === 'number' ? (accuracy * 100).toFixed(2) + '%' : accuracy,
      sharpe: typeof sharpe === 'number' ? sharpe.toFixed(2) : sharpe
    }

    node.description = `${node.params?.modelType} - 准确率: ${node.data.content.accuracy}`

    return {
      success: true,
      data: {
        model: result.data?.model || {},
        metrics: metrics,
        model_id: result.data?.model_id
      },
      message: '模型训练完成'
    }
  } catch (error) {
    console.error('[ModelTrainingNode] 模型训练失败:', error)

    node.data.content.trainingStatus = 'failed'

    return {
      success: false,
      errors: [error.message]
    }
  }
}

/**
 * 获取数据（训练模型）
 */
export async function fetchData(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  return await trainModel(node, context)
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  const validModelTypes = ['xgboost', 'lightgbm', 'lstm', 'transformer', 'linear', 'random-forest']
  if (!validModelTypes.includes(params.modelType)) {
    errors.push('请选择有效的模型类型')
  }

  if (params.trainParams?.testSize !== undefined) {
    const testSize = parseFloat(params.trainParams.testSize)
    if (isNaN(testSize) || testSize <= 0 || testSize >= 1) {
      errors.push('测试集比例必须在0-1之间')
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  }
}

/**
 * 切换输入端口状态
 */
export function toggleInputPort(node: any, inputId: string): void {
  if (node.inputs) {
    const input = node.inputs.find((i: any) => i.id === inputId)
    if (input) {
      input.active = !input.active
    }
  }
}
