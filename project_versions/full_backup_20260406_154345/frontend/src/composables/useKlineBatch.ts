/**
 * useKlineBatch - 批量K线数据加载 Composable
 *
 * 用于预加载多只股票的多个周期数据，填充缓存但不显示
 * 符合 V5 架构：通过 useKlineData 统一接口获取数据
 */

import { ref } from 'vue'
import { fetchKline, type KlineItem } from '@/api/modules/quotes'

export interface BatchLoadOptions {
  /** 加载超时时间（毫秒，默认30000） */
  timeout?: number
  /** 并发请求数（默认3） */
  concurrency?: number
  /** 每个请求之间的延迟（毫秒，默认100） */
  delay?: number
  /** 进度回调 */
  onProgress?: (completed: number, total: number) => void
}

export interface BatchLoadTask {
  symbol: string
  period: string
  count: number
  adjustType: string
}

export interface BatchLoadResult {
  success: boolean
  completed: number
  total: number
  failed: number
  details: Array<{
    symbol: string
    period: string
    success: boolean
    error?: string
  }>
}

/**
 * 批量加载K线数据（用于预加载缓存）
 *
 * @param tasks - 加载任务列表
 * @param options - 配置选项
 *
 * @example
 * const { preload, loading, result } = useKlineBatch()
 *
 * // 预加载其他股票的其他周期
 * const tasks = otherStocks.flatMap(stock =>
 *   periods.map(period => ({
 *     symbol: stock.symbol,
 *     period,
 *     count: 300,
 *     adjustType: 'qfq'
 *   }))
 * )
 *
 * await preload(tasks, {
 *   concurrency: 3,
 *   delay: 100,
 *   onProgress: (c, t) => console.log(`进度: ${c}/${t}`)
 * })
 */
export function useKlineBatch() {
  const loading = ref(false)
  const result = ref<BatchLoadResult | null>(null)

  /**
   * 批量预加载K线数据
   *
   * 特点：
   * - 低优先级，静默失败不影响主流程
   * - 延迟执行，避免阻塞主线程
   * - 并发控制，避免突发请求
   */
  const preload = async (
    tasks: BatchLoadTask[],
    options: BatchLoadOptions = {}
  ): Promise<BatchLoadResult> => {
    const {
      timeout = 30000,
      concurrency = 3,
      delay = 100,
      onProgress
    } = options

    loading.value = true
    result.value = null

    const total = tasks.length
    let completed = 0
    let failed = 0
    const details: BatchLoadResult['details'] = []

    // 分批执行（并发控制）
    for (let i = 0; i < tasks.length; i += concurrency) {
      const batch = tasks.slice(i, i + concurrency)

      await Promise.all(
        batch.map(async (task) => {
          try {
            // 延迟执行，避免突发请求
            await new Promise(resolve => setTimeout(resolve, delay))

            // 调用 API（数据会被中间件缓存）
            await fetchKline(task.symbol, task.period, task.count, task.adjustType)

            completed++
            details.push({
              symbol: task.symbol,
              period: task.period,
              success: true
            })

            // 进度回调
            if (onProgress && (completed % 5 === 0 || completed === total)) {
              onProgress(completed, total)
            }
          } catch (error) {
            failed++
            details.push({
              symbol: task.symbol,
              period: task.period,
              success: false,
              error: error instanceof Error ? error.message : String(error)
            })
            // 静默失败，不影响用户体验
            console.debug(`[useKlineBatch] ${task.symbol} ${task.period} 预加载失败`)
          }
        })
      )
    }

    const batchResult: BatchLoadResult = {
      success: failed === 0,
      completed,
      total,
      failed,
      details
    }

    result.value = batchResult
    loading.value = false

    console.log(`[useKlineBatch] 预加载完成: ${completed}/${total} 成功, ${failed} 失败`)

    return batchResult
  }

  /**
   * 取消当前的预加载任务
   */
  const cancel = (): void => {
    loading.value = false
    console.log('[useKlineBatch] 预加载已取消')
  }

  return {
    loading,
    result,
    preload,
    cancel
  }
}
