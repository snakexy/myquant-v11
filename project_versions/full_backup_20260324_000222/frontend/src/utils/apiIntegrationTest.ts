/**
 * API集成测试工具
 * 用于验证研究阶段所需的API连接
 */

import { getStockList, getRealtimeData, getDataQuality } from '../api/modules/data'
import { judgeStockType, detectAIInput, getRecommendations } from '../api/modules/intelligent'
import { getWorkflows, createWorkflow } from '../api/modules/workflow'

export interface ApiTestResult {
  name: string
  status: 'success' | 'error' | 'warning'
  message: string
  responseTime?: number
  details?: any
}

export class ApiIntegrationTester {
  private results: ApiTestResult[] = []

  /**
   * 运行所有API测试
   */
  async runAllTests(): Promise<ApiTestResult[]> {
    this.results = []
    console.log('🚀 开始API集成测试...')

    // 数据API测试
    await this.testDataApis()

    // 智能判断API测试
    await this.testIntelligentApis()

    // 工作流程API测试
    await this.testWorkflowApis()

    this.generateReport()
    return this.results
  }

  /**
   * 测试数据相关API
   */
  private async testDataApis(): Promise<void> {
    console.log('📊 测试数据API...')

    // 测试股票列表API
    await this.testApi(
      'getStockList',
      () => getStockList({ page: 1, size: 10 }),
      '获取股票列表'
    )

    // 测试实时数据API
    await this.testApi(
      'getRealtimeData',
      () => getRealtimeData(['000001', '000002']),
      '获取实时股票数据'
    )

    // 测试数据质量API
    await this.testApi(
      'getDataQuality',
      () => getDataQuality(),
      '获取数据质量指标'
    )
  }

  /**
   * 测试智能判断API
   */
  private async testIntelligentApis(): Promise<void> {
    console.log('🧠 测试智能判断API...')

    // 测试股票类型判断
    await this.testApi(
      'judgeStockType',
      () => judgeStockType({
        code: '000001',
        name: '平安银行',
        market: 'SZ'
      }),
      '股票类型判断'
    )

    // 测试AI输入检测
    await this.testApi(
      'detectAIInput',
      () => detectAIInput({
        input: '分析平安银行的技术指标',
        type: 'analysis'
      }),
      'AI输入检测'
    )

    // 测试智能推荐
    await this.testApi(
      'getRecommendations',
      () => getRecommendations({
        type: 'stocks',
        limit: 5
      }),
      '获取智能推荐'
    )
  }

  /**
   * 测试工作流程API
   */
  private async testWorkflowApis(): Promise<void> {
    console.log('⚙️ 测试工作流程API...')

    // 测试获取工作流列表
    await this.testApi(
      'getWorkflows',
      () => getWorkflows(1, 5),
      '获取工作流列表'
    )

    // 测试创建工作流
    await this.testApi(
      'createWorkflow',
      () => createWorkflow({
        name: '测试工作流',
        description: 'API测试创建的工作流',
        type: 'analysis' as any,
        status: 'pending' as any,
        nodes: [],
        connections: []
      }),
      '创建工作流'
    )
  }

  /**
   * 执行单个API测试
   */
  private async testApi(
    name: string,
    apiCall: () => Promise<any>,
    description: string
  ): Promise<void> {
    const startTime = Date.now()

    try {
      const response = await apiCall()
      const responseTime = Date.now() - startTime

      // 检查响应格式
      const isValid = this.validateApiResponse(response)

      this.results.push({
        name,
        status: isValid ? 'success' : 'warning',
        message: `${description} - ${isValid ? '成功' : '响应格式异常'}`,
        responseTime,
        details: {
          response: isValid ? 'Valid response' : 'Invalid response format',
          dataKeys: response ? Object.keys(response) : []
        }
      })

      console.log(`✅ ${name}: ${description} - ${responseTime}ms`)
    } catch (error: any) {
      const responseTime = Date.now() - startTime

      this.results.push({
        name,
        status: 'error',
        message: `${description} - 失败: ${error.message}`,
        responseTime,
        details: {
          error: error.message,
          code: error.code || 'UNKNOWN',
          stack: error.stack
        }
      })

      console.log(`❌ ${name}: ${description} - ${error.message}`)
    }
  }

  /**
   * 验证API响应格式
   */
  private validateApiResponse(response: any): boolean {
    if (!response) return false

    // 检查标准API响应格式
    if (typeof response === 'object' && 'code' in response && 'data' in response) {
      return response.code === 200 || response.success === true
    }

    // 检查直接数据响应
    if (Array.isArray(response) || (typeof response === 'object' && !('code' in response))) {
      return true
    }

    return false
  }

  /**
   * 生成测试报告
   */
  private generateReport(): void {
    const total = this.results.length
    const success = this.results.filter(r => r.status === 'success').length
    const errors = this.results.filter(r => r.status === 'error').length
    const warnings = this.results.filter(r => r.status === 'warning').length
    const avgResponseTime = this.results
      .filter(r => r.responseTime)
      .reduce((sum, r) => sum + (r.responseTime || 0), 0) / total

    console.log('\n📋 API集成测试报告')
    console.log('='.repeat(50))
    console.log(`总测试数: ${total}`)
    console.log(`成功: ${success} ✅`)
    console.log(`失败: ${errors} ❌`)
    console.log(`警告: ${warnings} ⚠️`)
    console.log(`平均响应时间: ${avgResponseTime.toFixed(2)}ms`)

    if (errors > 0) {
      console.log('\n❌ 失败的API:')
      this.results
        .filter(r => r.status === 'error')
        .forEach(r => {
          console.log(`  - ${r.name}: ${r.message}`)
        })
    }

    if (warnings > 0) {
      console.log('\n⚠️ 警告的API:')
      this.results
        .filter(r => r.status === 'warning')
        .forEach(r => {
          console.log(`  - ${r.name}: ${r.message}`)
        })
    }

    console.log('\n✅ 成功的API:')
    this.results
      .filter(r => r.status === 'success')
      .forEach(r => {
        console.log(`  - ${r.name}: ${r.message} (${r.responseTime}ms)`)
      })
  }

  /**
   * 获取测试结果摘要
   */
  getSummary(): {
    total: number
    success: number
    errors: number
    warnings: number
    successRate: number
    avgResponseTime: number
  } {
    const total = this.results.length
    const success = this.results.filter(r => r.status === 'success').length
    const errors = this.results.filter(r => r.status === 'error').length
    const warnings = this.results.filter(r => r.status === 'warning').length
    const avgResponseTime = this.results
      .filter(r => r.responseTime)
      .reduce((sum, r) => sum + (r.responseTime || 0), 0) / total || 0

    return {
      total,
      success,
      errors,
      warnings,
      successRate: total > 0 ? (success / total) * 100 : 0,
      avgResponseTime
    }
  }

  /**
   * 导出测试结果为JSON
   */
  exportResults(): string {
    const summary = this.getSummary()
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      summary,
      results: this.results
    }, null, 2)
  }

  /**
   * 保存测试结果到文件
   */
  async saveResultsToFile(filename?: string): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const defaultFilename = `api-test-results-${timestamp}.json`
    const finalFilename = filename || defaultFilename

    const results = this.exportResults()
    const blob = new Blob([results], { type: 'application/json' })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.download = finalFilename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
}

// 创建全局测试器实例
export const apiIntegrationTester = new ApiIntegrationTester()

// 快速测试函数
export const quickApiTest = async (): Promise<void> => {
  await apiIntegrationTester.runAllTests()
}

// 在开发环境下自动运行测试
if (import.meta.env.DEV) {
  // 延迟执行，确保应用初始化完成
  setTimeout(async () => {
    console.log('🔍 开始自动API集成测试...')
    try {
      await quickApiTest()
    } catch (error) {
      console.error('API测试执行失败:', error)
    }
  }, 3000)
}