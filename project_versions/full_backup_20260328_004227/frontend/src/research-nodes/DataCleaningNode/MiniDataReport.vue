<template>
  <div class="data-cleaning-mini-report">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在连接数据库...</div>
    </div>

    <!-- 数据内容 -->
    <div v-else class="data-content">
      <!-- 圆形进度条显示数据新鲜度 -->
      <div class="freshness-progress-section">
        <CircularProgress
          :value="freshnessScore"
          :size="60"
          :stroke-width="6"
          label="数据新鲜度"
          :show-label="true"
        />
        <div class="freshness-info">
          <div class="freshness-label">数据新鲜度</div>
          <div class="freshness-score">{{ freshnessScore }}%</div>
          <div class="freshness-status" :class="freshnessStatusClass">
            {{ freshnessStatusText }}
          </div>
        </div>
      </div>

      <!-- 其他数据指标 -->
      <div class="data-metrics-grid">
        <div class="data-metric">
          <div class="metric-icon success-gradient">
            <font-awesome-icon icon="database" />
          </div>
          <div class="metric-content">
            <div class="metric-label">数据库标的</div>
            <div class="metric-value">{{ stockCount }}个</div>
          </div>
        </div>

        <div class="data-metric">
          <div class="metric-icon purple-gradient">
            <font-awesome-icon icon="chart-bar" />
          </div>
          <div class="metric-content">
            <div class="metric-label">数据频率</div>
            <div class="metric-value">{{ dataFrequency }}</div>
          </div>
        </div>

        <div class="data-metric">
          <div class="metric-icon info-gradient">
            <font-awesome-icon icon="calendar-alt" />
          </div>
          <div class="metric-content">
            <div class="metric-label">时间范围</div>
            <div class="metric-value">{{ dateRange }}</div>
          </div>
        </div>

        <div class="data-metric">
          <div class="metric-icon warning-gradient">
            <font-awesome-icon icon="check-circle" />
          </div>
          <div class="metric-content">
            <div class="metric-label">已选标的</div>
            <div class="metric-value">{{ selectedStocks }}个</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import CircularProgress from '../../components/ui/CircularProgress.vue'
import { formatDataCount } from './utils'
import * as databaseApi from '../../api/modules/database'

interface Props {
  metadata?: {
    overall_quality_score?: number
    qualityScore?: number
    data_quality_score?: number
    stockCount?: number
    selectedStocks?: number
    totalCount?: number
    totalRecords?: number
    totalDataPoints?: number
    startDate?: string
    endDate?: string
    dateRange?: string
    lastUpdated?: string
    storage_info?: {
      data_storage?: {
        total_records?: number
        daily_records?: number
        intraday_records?: number
        last_updated?: string
      }
    }
    data_overview?: {
      stock_count?: number
      data_time_range?: string
      total_records?: number
      instrument_stats?: {
        total?: number
        stocks?: number
        indexes?: number
      }
    }
    [key: string]: any
  }
  nodeId?: string
}

const props = withDefaults(defineProps<Props>(), {
  metadata: () => ({}),
  nodeId: 'data-cleaning'
})

const isLoading = ref(false)
const qualityReport = ref<any>(null)
const isInitialLoad = ref(true)  // 🔧 标记是否为初始加载
const lastRefreshTime = ref(0)  // 🔧 记录上次刷新时间（用于防抖）

// 🔧 计算数据新鲜度（从数据新鲜度 API 获取）
const freshnessScore = computed(() => {
  // 优先使用数据新鲜度 API 的 overallScore
  if (qualityReport.value?.freshness_data?.overallScore) {
    return qualityReport.value.freshness_data.overallScore
  }

  // 回退：使用 freshnessDetails 的平均分
  if (qualityReport.value?.freshness_data?.freshnessDetails && qualityReport.value.freshness_data.freshnessDetails.length > 0) {
    const scores = qualityReport.value.freshness_data.freshnessDetails.map((detail: any) => detail.score || 0)
    const avgScore = scores.reduce((a: number, b: number) => a + b, 0) / scores.length
    return Math.round(avgScore)
  }

  // 回退：使用 storage_info 中的最后更新时间计算
  const lastUpdated = qualityReport.value?.storage_info?.data_storage?.last_updated ||
                      props.metadata?.storage_info?.data_storage?.last_updated

  if (!lastUpdated || lastUpdated === '--') {
    // 🔧 如果没有最后更新时间，但有数据，默认给个较高的分数
    if (totalRecords.value > 0) {
      return 100 // 假设有数据就是新鲜的
    }
    return 0
  }

  try {
    const lastUpdateTime = new Date(lastUpdated).getTime()
    const now = Date.now()
    const hoursDiff = (now - lastUpdateTime) / (1000 * 60 * 60)

    // 数据新鲜度评分（基于数据年龄）
    // 0-24小时：100分
    // 24-48小时：80分
    // 48-72小时：60分
    // 72-168小时（7天）：40分
    // 超过7天：20分
    if (hoursDiff < 24) return 100
    if (hoursDiff < 48) return 80
    if (hoursDiff < 72) return 60
    if (hoursDiff < 168) return 40
    return 20
  } catch (error) {
    console.error('[MiniDataReport] 解析最后更新时间失败:', lastUpdated, error)
    // 如果解析失败，但有数据，默认给个较高的分数
    if (totalRecords.value > 0) {
      return 90
    }
    return 0
  }
})

const freshnessStatusClass = computed(() => {
  const score = freshnessScore.value
  if (score >= 90) return 'status-excellent'
  if (score >= 70) return 'status-good'
  if (score >= 50) return 'status-fair'
  return 'status-poor'
})

const freshnessStatusText = computed(() => {
  const score = freshnessScore.value
  if (score >= 90) return '优秀'
  if (score >= 70) return '良好'
  if (score >= 50) return '一般'
  return '较差'
})

// 🔧 从质量报告或 props 获取数据质量分数
const qualityScore = computed(() => {
  // 优先使用质量报告的数据
  if (qualityReport.value?.overall_quality_score) {
    return Math.round(qualityReport.value.overall_quality_score * 100)
  }

  // 回退到 props 数据
  if (props.metadata?.overall_quality_score) {
    return Math.round(props.metadata.overall_quality_score * 100)
  }

  return props.metadata?.qualityScore || props.metadata?.data_quality_score || 0
})

const qualityStatusClass = computed(() => {
  const score = qualityScore.value
  if (score >= 90) return 'status-excellent'
  if (score >= 70) return 'status-good'
  if (score >= 50) return 'status-fair'
  return 'status-poor'
})

const qualityStatusText = computed(() => {
  const score = qualityScore.value
  if (score >= 90) return '优秀'
  if (score >= 70) return '良好'
  if (score >= 50) return '一般'
  return '较差'
})

// 🔧 从 QLib 数据库统计获取股票数量
const stockCount = computed(() => {
  // 优先使用 data_overview 中的 stock_count
  if (qualityReport.value?.data_overview?.stock_count) {
    console.log('[MiniDataReport] stockCount 从 qualityReport.data_overview.stock_count 获取:', qualityReport.value.data_overview.stock_count)
    return qualityReport.value.data_overview.stock_count
  }

  if (props.metadata?.data_overview?.stock_count) {
    console.log('[MiniDataReport] stockCount 从 props.metadata.data_overview.stock_count 获取:', props.metadata.data_overview.stock_count)
    return props.metadata.data_overview.stock_count
  }

  // 回退到 props 中的 stockCount
  const fallbackCount = props.metadata?.stockCount || props.metadata?.totalCount || 0
  console.log('[MiniDataReport] stockCount 使用回退值:', fallbackCount)
  return fallbackCount
})

// 🔧 从质量报告获取已选标的数量（股票数量，不包括指数）
const selectedStocks = computed(() => {
  // 优先使用节点配置中的选中标的数量（来自数据库管理界面的复选框）
  if (props.metadata?.selectedStockCount !== undefined) {
    return props.metadata.selectedStockCount
  }

  // 回退：使用 data_overview.instrument_stats.stocks
  if (qualityReport.value?.data_overview?.instrument_stats?.stocks) {
    return qualityReport.value.data_overview.instrument_stats.stocks
  }

  if (props.metadata?.data_overview?.instrument_stats?.stocks) {
    return props.metadata.data_overview.instrument_stats.stocks
  }

  // 回退：如果没有 stocks 字段，使用 total
  if (qualityReport.value?.data_overview?.instrument_stats?.total) {
    return qualityReport.value.data_overview.instrument_stats.total
  }

  if (props.metadata?.data_overview?.instrument_stats?.total) {
    return props.metadata.data_overview.instrument_stats.total
  }

  return props.metadata?.selectedStocks || stockCount.value
})

// 🔧 数据频率（显示当前使用的数据频率）
const dataFrequency = computed(() => {
  // 优先使用 props 中的频率配置
  if (props.metadata?.frequencies && Array.isArray(props.metadata.frequencies) && props.metadata.frequencies.length > 0) {
    const freqMap: Record<string, string> = {
      'daily': '日线',
      '60min': '60分钟',
      '30min': '30分钟',
      '15min': '15分钟',
      '5min': '5分钟',
      '1min': '1分钟'
    }
    const labels = props.metadata.frequencies.map((f: string) => freqMap[f] || f)
    return labels.join(' + ')
  }

  if (props.metadata?.frequency) {
    const freqMap: Record<string, string> = {
      'daily': '日线',
      '60min': '60分钟',
      '30min': '30分钟',
      '15min': '15分钟',
      '5min': '5分钟',
      '1min': '1分钟'
    }
    return freqMap[props.metadata.frequency] || props.metadata.frequency
  }

  // 默认显示日线
  return '日线'
})

// 🔧 从 QLib 数据库统计获取总记录数
const totalRecords = computed(() => {
  // 优先使用 storage_info 中的总记录数
  if (qualityReport.value?.storage_info?.data_storage?.total_records) {
    return qualityReport.value.storage_info.data_storage.total_records
  }

  if (props.metadata?.storage_info?.data_storage?.total_records) {
    return props.metadata.storage_info.data_storage.total_records
  }

  // 回退到 data_overview 中的 total_records
  if (qualityReport.value?.data_overview?.total_records) {
    return qualityReport.value.data_overview.total_records
  }

  if (props.metadata?.data_overview?.total_records) {
    return props.metadata.data_overview.total_records
  }

  return props.metadata?.totalRecords || props.metadata?.totalDataPoints || 0
})

// 🔧 从 QLib 数据库统计获取时间范围
const dateRange = computed(() => {
  // 优先使用 data_overview 中的时间范围
  if (qualityReport.value?.data_overview?.data_time_range) {
    const range = qualityReport.value.data_overview.data_time_range
    // 🔧 如果已经是 "XXXX-XX-XX 至 XXXX-XX-XX" 格式，直接返回
    if (range.includes(' 至 ') && range.match(/^\d{4}-\d{2}-\d{2}/)) {
      return range
    }
    // 🔧 如果是简化格式 "XX-XX ~ XX-XX"，保持原样
    if (range.includes(' ~ ')) {
      return range
    }
    // 🔧 其他格式，尝试解析
    if (range.includes(' 至 ')) {
      const parts = range.split(' 至 ')
      if (parts.length === 2) {
        const simplifyDate = (dateStr: string) => {
          // 提取日期部分，忽略时间
          const tIndex = dateStr.indexOf('T')
          if (tIndex !== -1) {
            dateStr = dateStr.substring(0, tIndex)
          }
          const spaceIndex = dateStr.indexOf(' ')
          if (spaceIndex !== -1) {
            dateStr = dateStr.substring(0, spaceIndex)
          }
          // 如果已经是完整日期格式，保持不变
          if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
            return dateStr
          }
          // 只显示月日（对于旧格式）
          return dateStr.split('-').slice(1).join('-')
        }
        return `${simplifyDate(parts[0])} 至 ${simplifyDate(parts[1])}`
      }
    }
    return range
  }

  if (props.metadata?.data_overview?.data_time_range) {
    return props.metadata.data_overview.data_time_range
  }

  // 回退到 props 中的 dateRange
  if (props.metadata?.dateRange && props.metadata.dateRange !== '未配置' && props.metadata.dateRange !== '未设置') {
    return props.metadata.dateRange
  }

  return '未设置'
})

// 🔧 刷新报告（可以被父组件调用来重新生成报告）
const refreshReport = async (forceRefresh = true) => {
  console.log('[MiniDataReport] 刷新报告, forceRefresh:', forceRefresh)
  await loadDatabaseData(forceRefresh)
}

// 🔧 加载数据库数据
const loadDatabaseData = async (forceRefresh = false) => {
  try {
    console.log('[MiniDataReport] 开始调用数据库扫描API, forceRefresh:', forceRefresh)
    lastRefreshTime.value = Date.now()  // 🔧 更新刷新时间
    const dbResponse = await databaseApi.scanDatabase(forceRefresh, ['daily'])

    if (dbResponse.code === 200 && dbResponse.data) {
      console.log('[MiniDataReport] 数据库扫描API返回成功:', dbResponse.data)

      if (!qualityReport.value) {
        qualityReport.value = {}
      }

      // 🔧 构建数据库概览数据（使用API返回的真实数据，覆盖props.metadata中的旧数据）
      qualityReport.value.data_overview = {
        stock_count: dbResponse.data.total_stocks || 0,
        total_records: dbResponse.data.total_records || 0,
        data_time_range: `${dbResponse.data.date_range?.earliest || '--'} 至 ${dbResponse.data.date_range?.latest || '--'}`,
        instrument_stats: {
          total: dbResponse.data.total_stocks || 0,
          stocks: dbResponse.data.total_stocks || 0,
          indexes: 0
        }
      }

      // 🔧 保留 props.metadata 中的 storage_info（如果有的话）
      if (props.metadata?.storage_info) {
        qualityReport.value.storage_info = props.metadata.storage_info
      }

      console.log('[MiniDataReport] 数据库概览数据已更新:', qualityReport.value.data_overview)
    } else {
      console.warn('[MiniDataReport] 数据库扫描API返回失败:', dbResponse)
    }
  } catch (e: any) {
    console.warn('[MiniDataReport] 调用数据库扫描API失败:', e.message)
  }
}

// 🔧 加载数据（从数据库扫描API获取数据库标的和时间范围）
onMounted(async () => {
  console.log('[MiniDataReport] 开始加载数据...')
  console.log('[MiniDataReport] props.metadata:', props.metadata)

  try {
    isLoading.value = true

    // 🔧 调用数据库扫描API获取真实的数据库标的和时间范围（强制刷新，确保获取最新数据）
    await loadDatabaseData(true)

    // 🔧 尝试获取数据新鲜度（带超时保护，但不阻塞显示）
    try {
      const freshnessTimeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('数据新鲜度请求超时')), 3000) // 3秒超时
      })

      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
      const freshnessPromise = fetch(`${apiBase}/data-management/freshness/status`)
      const freshnessResponse = await Promise.race([freshnessPromise, freshnessTimeoutPromise]) as Response

      if (freshnessResponse.ok) {
        const result = await freshnessResponse.json()
        if (result.success && result.data) {
          if (!qualityReport.value) {
            qualityReport.value = {}
          }
          qualityReport.value.freshness_data = result.data
          console.log('[MiniDataReport] 数据新鲜度加载成功:', result.data)
        }
      }
    } catch (e: any) {
      console.warn('[MiniDataReport] 获取数据新鲜度失败，忽略:', e.message)
    }

  } catch (error: any) {
    console.error('[MiniDataReport] 加载数据失败:', error.message)
  } finally {
    isLoading.value = false
    isInitialLoad.value = false  // 🔧 标记初始加载完成
    console.log('[MiniDataReport] 数据加载完成, isLoading:', isLoading.value)
  }
})

// 🔧 监听 props.metadata 的变化，当 DatabaseManager 刷新后同步更新
watch(() => props.metadata?.data_overview, async (newData) => {
  // 🔧 跳过初始加载（避免在 onMounted 时触发重复刷新）
  if (isInitialLoad.value) {
    console.log('[MiniDataReport] 初始加载，跳过 watch 触发')
    isInitialLoad.value = false
    return
  }

  if (newData && newData.data_time_range) {
    // 🔧 防抖：5秒内不重复刷新
    const now = Date.now()
    const debounceMs = 5000
    if (now - lastRefreshTime.value < debounceMs) {
      console.log('[MiniDataReport] 防抖：距离上次刷新不足5秒，跳过')
      return
    }

    console.log('[MiniDataReport] 检测到 metadata.data_overview 变化:', newData)

    // 🔧 检查是否真的需要刷新：比较新旧数据的时间范围
    const currentRange = qualityReport.value?.data_overview?.data_time_range
    const newRange = newData.data_time_range
    if (currentRange === newRange) {
      console.log('[MiniDataReport] 数据时间范围未变化，跳过刷新')
      return
    }

    // 🔧 当检测到 DatabaseManager 刷新后，重新调用数据库扫描API获取最新数据
    // 这样可以确保显示的是数据库中的真实数据，而不是传递过来的可能过时的数据
    console.log('[MiniDataReport] 重新调用数据库扫描API获取最新数据...')
    lastRefreshTime.value = now
    await loadDatabaseData(true)  // 强制刷新
  }
}, { deep: true })

// 🔧 暴露 refreshReport 方法给父组件
defineExpose({
  refreshReport
})

</script>

<style scoped>
.data-cleaning-mini-report {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 14px;
  background: rgba(26, 26, 46, 0.9);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 200px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 140px;
  gap: 12px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid #2962ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 数据内容 */
.data-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.freshness-progress-section {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 10px;
  background: transparent;
  border-radius: 6px;
}

.freshness-info {
  flex: 1;
}

.freshness-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 5px;
}

.freshness-score {
  font-size: 26px;
  font-weight: 700;
  color: white;
  margin-bottom: 5px;
}

.freshness-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.freshness-status.status-excellent {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.freshness-status.status-good {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.freshness-status.status-fair {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.freshness-status.status-poor {
  background: rgba(107, 114, 128, 0.2);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.3);
}

.data-metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  min-width: 0;
}

.data-metric {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(26, 26, 46, 0.9);
  border-radius: 6px;
  transition: all 0.2s ease;
  min-height: 44px;
  min-width: 0;
  overflow: hidden;
}

/* 时间范围卡片允许自适应高度 */
.data-metric:nth-child(3) {
  align-items: flex-start;
  min-height: 54px;
}

/* 时间范围卡片的图标顶部对齐 */
.data-metric:nth-child(3) .metric-icon {
  margin-top: 2px;
}

.data-metric:hover {
  background: rgba(26, 26, 46, 1);
  transform: translateY(-1px);
}

.metric-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  border-radius: 5px;
  font-size: 13px;
  color: white;
  flex-shrink: 0;
}

/* 图标渐变色 - 与 IndexSelectionNode 保持一致 */
.metric-icon.primary-gradient {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
}

.metric-icon.success-gradient {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.metric-icon.purple-gradient {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.metric-icon.info-gradient {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.metric-icon.warning-gradient {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.metric-icon.danger-gradient {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.metric-icon :deep(svg) {
  color: white;
}

.metric-content {
  flex: 1;
  min-width: 0;
}

.metric-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: white;
  line-height: 1.3;
  word-break: break-word;
  overflow-wrap: break-word;
}

/* 时间范围特殊处理：允许换行显示 */
.data-metric:nth-child(3) .metric-value {
  white-space: normal;
  word-break: break-all;
  line-height: 1.4;
}

.metric-value.status-latest {
  color: #10b981;
}

.metric-value.status-recent {
  color: #f59e0b;
}

.metric-value.status-pending {
  color: #ef4444;
}

.metric-value.status-outdated {
  color: #ef4444;
  opacity: 0.7;
}
</style>
