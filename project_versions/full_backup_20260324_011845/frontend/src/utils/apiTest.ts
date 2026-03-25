// API测试工具
import { apiRequest } from '@/api'
import { getStockList, getRealtimeData } from '@/api/modules/data'

export interface TestResult {
  name: string
  status: 'pass' | 'fail' | 'skip'
  message: string
  duration?: number
}

export class APITester {
  private results: TestResult[] = []

  // 记录测试结果
  private addResult(name: string, status: TestResult['status'], message: string, duration?: number) {
    this.results.push({
      name,
      status,
      message,
      duration
    })
    console.log(`[API Test] ${name}: ${status.toUpperCase()} - ${message}`)
  }

  // 测试API连接
  async testConnection() {
    const start = Date.now()
    try {
      const response = await apiRequest.get('/health', { showError: false })
      this.addResult(
        'API连接测试',
        'pass',
        `连接成功，耗时 ${Date.now() - start}ms`,
        Date.now() - start
      )
    } catch (error: any) {
      this.addResult(
        'API连接测试',
        'fail',
        `连接失败: ${error.message}`,
        Date.now() - start
      )
    }
  }

  // 测试获取股票列表
  async testGetStockList() {
    const start = Date.now()
    try {
      const response = await getStockList({ page: 1, size: 10 })
      if (response.success && Array.isArray(response.data)) {
        this.addResult(
          '获取股票列表',
          'pass',
          `成功获取 ${response.data.length} 条股票数据`,
          Date.now() - start
        )
      } else {
        this.addResult('获取股票列表', 'fail', '返回数据格式错误')
      }
    } catch (error: any) {
      this.addResult('获取股票列表', 'fail', `请求失败: ${error.message}`)
    }
  }

  // 测试获取实时数据
  async testGetRealtimeData() {
    const start = Date.now()
    try {
      const response = await getRealtimeData(['000001', '000002'])
      if (response.success && Array.isArray(response.data)) {
        this.addResult(
          '获取实时数据',
          'pass',
          `成功获取 ${response.data.length} 只股票实时数据`,
          Date.now() - start
        )
      } else {
        this.addResult('获取实时数据', 'fail', '返回数据格式错误')
      }
    } catch (error: any) {
      this.addResult('获取实时数据', 'fail', `请求失败: ${error.message}`)
    }
  }

  // 测试错误处理
  async testErrorHandling() {
    const start = Date.now()
    try {
      await apiRequest.get('/non-existent-endpoint', { showError: false })
      this.addResult('错误处理测试', 'fail', '应该返回404错误')
    } catch (error: any) {
      this.addResult(
        '错误处理测试',
        'pass',
        `正确处理错误: ${error.message}`,
        Date.now() - start
      )
    }
  }

  // 测试并发请求
  async testConcurrentRequests() {
    const start = Date.now()
    try {
      const requests = Array(5).fill(null).map(() =>
        getStockList({ page: 1, size: 5 })
      )
      const results = await Promise.all(requests)
      const allSuccess = results.every(r => r.success)

      if (allSuccess) {
        this.addResult(
          '并发请求测试',
          'pass',
          `5个并发请求全部成功，耗时 ${Date.now() - start}ms`,
          Date.now() - start
        )
      } else {
        this.addResult('并发请求测试', 'fail', '部分请求失败')
      }
    } catch (error: any) {
      this.addResult('并发请求测试', 'fail', `并发请求失败: ${error.message}`)
    }
  }

  // 测试请求超时
  async testTimeout() {
    const start = Date.now()
    try {
      // 假设有一个慢速接口
      await apiRequest.get('/slow-endpoint', {
        timeout: 2000,
        showError: false
      })
      this.addResult('请求超时测试', 'fail', '应该触发超时')
    } catch (error: any) {
      if (error.message.includes('timeout')) {
        this.addResult(
          '请求超时测试',
          'pass',
          '正确处理超时错误',
          Date.now() - start
        )
      } else {
        this.addResult('请求超时测试', 'fail', `未预期的错误: ${error.message}`)
      }
    }
  }

  // 测试Token认证
  async testAuthentication() {
    // 先清除token
    localStorage.removeItem('token')

    const start = Date.now()
    try {
      await apiRequest.get('/protected-endpoint', { showError: false })
      this.addResult('Token认证测试', 'fail', '未认证的请求应该被拒绝')
    } catch (error: any) {
      if (error.response?.status === 401) {
        this.addResult(
          'Token认证测试',
          'pass',
          '正确拒绝未认证请求',
          Date.now() - start
        )
      } else {
        this.addResult('Token认证测试', 'fail', `未预期的错误: ${error.message}`)
      }
    }
  }

  // 运行所有测试
  async runAllTests() {
    console.log('开始API测试...')
    this.results = []

    await this.testConnection()
    await this.testGetStockList()
    await this.testGetRealtimeData()
    await this.testErrorHandling()
    await this.testConcurrentRequests()
    await this.testTimeout()
    await this.testAuthentication()

    return this.getTestReport()
  }

  // 获取测试报告
  getTestReport() {
    const total = this.results.length
    const passed = this.results.filter(r => r.status === 'pass').length
    const failed = this.results.filter(r => r.status === 'fail').length
    const skipped = this.results.filter(r => r.status === 'skip').length

    const avgDuration = this.results
      .filter(r => r.duration)
      .reduce((acc, r) => acc + (r.duration || 0), 0) /
      this.results.filter(r => r.duration).length

    return {
      summary: {
        total,
        passed,
        failed,
        skipped,
        passRate: Math.round((passed / total) * 100),
        avgDuration: Math.round(avgDuration)
      },
      details: this.results
    }
  }

  // 打印测试报告
  printReport() {
    const report = this.getTestReport()

    console.log('\n========== API测试报告 ==========')
    console.log(`总测试数: ${report.summary.total}`)
    console.log(`通过: ${report.summary.passed}`)
    console.log(`失败: ${report.summary.failed}`)
    console.log(`跳过: ${report.summary.skipped}`)
    console.log(`通过率: ${report.summary.passRate}%`)
    console.log(`平均耗时: ${report.summary.avgDuration}ms`)

    console.log('\n---------- 详细结果 ----------')
    report.details.forEach(result => {
      const icon = result.status === 'pass' ? '✓' : result.status === 'fail' ? '✗' : '-'
      console.log(`${icon} ${result.name}: ${result.message}`)
    })

    console.log('=================================\n')

    return report
  }
}

// 导出测试实例
export const apiTester = new APITester()

// 开发环境下自动运行测试
if (import.meta.env.DEV && import.meta.env.VITE_ENABLE_API_TEST === 'true') {
  // 延迟执行，确保应用已加载
  setTimeout(() => {
    apiTester.runAllTests().then(() => {
      apiTester.printReport()
    })
  }, 2000)
}