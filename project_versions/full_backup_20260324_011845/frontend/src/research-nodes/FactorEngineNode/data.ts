/**
 * 因子计算引擎节点数据处理逻辑
 *
 * 核心共享组件，支持双输入端：
 * - 数据驱动输入端：接收来自数据清洗的数据
 * - AI助手输入端：接收来自AI助手策略构思的数据
 */

import { ElMessage } from 'element-plus'
import type { NodeContext, NodeExecutionResult } from '../../base/BaseNode'

/**
 * 更新因子计算引擎节点显示
 */
export async function updateFactorEngineDisplay(node: any, context: NodeContext) {
  const nodeConfig = node

  // 检查输入端口状态
  const dataDrivenActive = node.inputs?.find((i: any) => i.id === 'data-driven')?.active ?? true
  const aiDrivenActive = node.inputs?.find((i: any) => i.id === 'ai-driven')?.active ?? true

  // 获取上游节点
  const upstreamNodes = context.getUpstreamNodes(node.id)

  // 统计激活的输入数量
  const activeInputs = upstreamNodes.filter(n => {
    if (n.id === 'data-cleaning') return dataDrivenActive
    if (n.id === 'ai-assistant' || n.id === 'strategy-conception') return aiDrivenActive
    return false
  })

  // 更新节点描述
  const inputLabels = activeInputs.map(n => n.title).join(' + ')
  node.description = inputLabels ? `因子计算 (${inputLabels})` : '因子计算引擎'

  // 更新显示内容
  if (activeInputs.length === 0) {
    node.data.content = {
      totalFactors: 0,
      calculatedFactors: ['等待输入数据...'],
      calculationTime: '--',
      inputStatus: '未连接数据源'
    }
  } else {
    node.data.content = {
      totalFactors: node.params?.alpha158 ? 158 : (node.params?.alpha360 ? 360 : 0),
      calculatedFactors: activeInputs.map((n: any) => n.title),
      calculationTime: '--',
      inputStatus: `${activeInputs.length} 个数据源已连接`
    }
  }
}

/**
 * 计算因子
 */
export async function calculateFactors(node: any, context: NodeContext): Promise<NodeExecutionResult> {
  try {
    const nodeConfig = node

    // 检查输入端口状态
    const dataDrivenActive = node.inputs?.find((i: any) => i.id === 'data-driven')?.active ?? true
    const aiDrivenActive = node.inputs?.find((i: any) => i.id === 'ai-driven')?.active ?? true

    // 获取上游节点
    const upstreamNodes = context.getUpstreamNodes(node.id)

    // 筛选激活的输入节点
    const activeInputs = upstreamNodes.filter(n => {
      if (n.id === 'data-cleaning') return dataDrivenActive
      if (n.id === 'ai-assistant' || n.id === 'strategy-conception') return aiDrivenActive
      return false
    })

    if (activeInputs.length === 0) {
      return {
        success: false,
        errors: ['没有激活的输入数据源，请先连接数据清洗节点或AI助手节点']
      }
    }

    // 显示计算中状态
    node.data.content = {
      totalFactors: '--',
      calculatedFactors: ['计算中...'],
      calculationTime: '计算中...',
      inputStatus: `${activeInputs.length} 个数据源`
    }

    // 确定要计算的因子数量
    let totalFactors = 0
    if (node.params?.alpha158) totalFactors += 158
    if (node.params?.alpha360) totalFactors += 360
    if (node.params?.customFactors && Array.isArray(node.params.customFactors)) {
      totalFactors += node.params.customFactors.length
    }

    if (totalFactors === 0) {
      return {
        success: false,
        errors: ['请选择至少一个因子模板或输入自定义因子']
      }
    }

    // 调用后端因子计算API
    const startTime = Date.now()

    const api_endpoint = node.metadata?.api_endpoint || 'http://localhost:8000/api/v1/factor_engine/calculate_factors'

    // 获取上游股票列表
    const dataCleaningNode = activeInputs.find((n: any) => n.id === 'data-cleaning')
    const symbols = dataCleaningNode?.data?.data?.symbols || ['000001.SZ', '600000.SH']

    // 确定日期范围
    const start_date = dataCleaningNode?.data?.data?.start_date || '2024-01-01'
    const end_date = dataCleaningNode?.data?.data?.end_date || new Date().toISOString().split('T')[0]

    // 确定因子类型
    const factor_types: string[] = []
    if (node.params?.alpha158) factor_types.push('alpha158')
    if (node.params?.alpha360) factor_types.push('alpha360')
    if (node.params?.customFactors && node.params.customFactors.length > 0) {
      factor_types.push('custom')
    }

    const request_params = {
      symbols: symbols,
      start_date: start_date,
      end_date: end_date,
      factor_types: factor_types.length > 0 ? factor_types : ['basic'],
      config: {
        normalize: node.params?.normalize ?? true,
        neutralize: node.params?.neutralize ?? true,
        custom_factors: node.params?.customFactors || [],
        frequency: node.params?.frequency || 'daily'
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
      throw new Error(result.detail || result.message || '因子计算失败')
    }

    const calculationTime = Date.now() - startTime

    // 从API响应获取计算结果
    const calculatedFactors: string[] = []
    if (node.params?.alpha158) calculatedFactors.push('Alpha158')
    if (node.params?.alpha360) calculatedFactors.push('Alpha360')
    if (node.params?.customFactors && node.params.customFactors.length > 0) {
      calculatedFactors.push(`自定义(${node.params.customFactors.length}个)`)
    }

    // 更新计算结果
    const resultData = result.data || {}

    node.data.content = {
      totalFactors,
      calculatedFactors,
      calculationTime: `${calculationTime}ms`,
      inputStatus: `${activeInputs.length} 个数据源已完成`
    }

    return {
      success: true,
      data: {
        factors: calculatedFactors,
        totalFactors,
        calculationTime,
        inputSources: activeInputs.map((n: any) => n.id),
        factor_data: resultData.factors || {},
        factor_stats: resultData.stats || {}
      },
      message: `成功计算 ${totalFactors} 个因子，耗时 ${calculationTime}ms`
    }
  } catch (error) {
    console.error('[FactorEngineNode] 因子计算失败:', error)

    node.data.content = {
      totalFactors: 0,
      calculatedFactors: ['计算失败'],
      calculationTime: '--',
      inputStatus: '错误'
    }

    return {
      success: false,
      errors: [error.message]
    }
  }
}

/**
 * 验证参数
 */
export function validateParams(params: Record<string, any>): { valid: boolean; errors?: string[] } {
  const errors: string[] = []

  const hasAlpha158 = params.alpha158
  const hasAlpha360 = params.alpha360
  const hasCustomFactors = params.customFactors && params.customFactors.length > 0

  if (!hasAlpha158 && !hasAlpha360 && !hasCustomFactors) {
    errors.push('请至少选择一个因子模板或输入自定义因子')
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
