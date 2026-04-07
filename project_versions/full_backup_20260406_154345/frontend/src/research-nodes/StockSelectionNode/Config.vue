<template>
  <div class="stock-selection-config">
    <!-- 股票代码输入 -->
    <div class="config-section">
      <h4 class="section-title">股票代码</h4>
      <div class="stock-input-group">
        <input
          v-model="config.stockCode"
          class="stock-input"
          placeholder="请输入股票代码，多个代码用逗号分隔"
          @input="handleStockCodeChange"
        />
              </div>
    </div>

    <!-- 时间范围选择 -->
    <div class="config-section">
      <h4 class="section-title">时间范围</h4>
      <div class="time-range-notice" v-if="config.stockCode">
        <small class="notice-text">
          ⚠️ 数据说明：当前数据最新至2025-12-19。2025-12-18为交易日但数据源暂缺该日数据，系统会自动补全。您可以选择包含任意交易日的范围。
        </small>
      </div>
      <div class="time-range-group">
        <div class="time-presets">
          <button
            v-for="preset in timePresets"
            :key="preset.value"
            class="preset-btn"
            :class="{
              active: config.timeRange === preset.value,
              disabled: isTimeRangeDisabled(preset)
            }"
            @click="!isTimeRangeDisabled(preset) && selectTimeRange(preset)"
            :disabled="isTimeRangeDisabled(preset)"
            :title="isTimeRangeDisabled(preset) ? '该时间范围超出选中的分钟级频率限制' : preset.label"
          >
            {{ preset.label }}
          </button>
        </div>
        <div class="custom-range">
          <div class="range-inputs">
            <div class="range-input-group">
              <label>开始日期：</label>
              <input
                v-model="config.startDate"
                type="date"
                class="date-input"
                :max="config.endDate || today"
                @change="handleCustomDateChange"
              />
            </div>
            <div class="range-input-group">
              <label>结束日期：</label>
              <input
                v-model="config.endDate"
                type="date"
                class="date-input"
                :min="config.startDate"
                :max="today"
                @change="handleCustomDateChange"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据频率 -->
    <div class="config-section">
      <h4 class="section-title">数据频率 (支持多选)</h4>
      <div class="frequency-description" v-if="hasIntradayFrequency">
        <small class="notice-text">
          ⚠️ 分钟级数据有时间范围限制：5分钟最多1周，15分钟最多1个月，30分钟最多2个月，60分钟最多半年
        </small>
      </div>
      <div class="frequency-group">
        <label class="checkbox-option" v-for="freq in dataFrequencies" :key="freq.value">
          <input
            type="checkbox"
            :value="freq.value"
            v-model="selectedFrequencies"
          />
          <span>{{ freq.label }}</span>
          <small v-if="freq.description">{{ freq.description }}</small>
        </label>
      </div>
    </div>

    <!-- 其他选项 -->
    <div class="config-section">
      <h4 class="section-title">其他选项</h4>
      <div class="other-options">
        <label class="checkbox-option">
          <input
            type="checkbox"
            v-model="config.includeDividends"
          />
          <span>包含除权除息数据</span>
        </label>
        <label class="checkbox-option">
          <input
            type="checkbox"
            v-model="config.adjustPrices"
          />
          <span>价格复权处理</span>
        </label>
        <label class="checkbox-option">
          <input
            type="checkbox"
            v-model="config.includeVolume"
          />
          <span>包含成交量数据</span>
        </label>
      </div>
    </div>

    <!-- 股票筛选 -->
    <div class="config-section">
      <h4 class="section-title">股票筛选</h4>
      <div class="filter-options">
        <div class="filter-group">
          <label>市场类型：</label>
          <select v-model="config.marketType" class="filter-select">
            <option value="A股">A股</option>
            <option value="港股">港股</option>
            <option value="美股">美股</option>
            <option value="全部">全部市场</option>
          </select>
        </div>
        <div class="filter-group">
          <label>股票类型：</label>
          <select v-model="config.stockType" class="filter-select">
            <option value="all">全部</option>
            <option value="stock">个股</option>
            <option value="index">指数</option>
            <option value="etf">ETF</option>
          </select>
        </div>
        <div class="filter-group">
          <label>排序方式：</label>
          <select v-model="config.sortBy" class="filter-select">
            <option value="code">股票代码</option>
            <option value="name">股票名称</option>
            <option value="price">价格</option>
            <option value="change">涨跌幅</option>
          </select>
        </div>
        <div class="filter-group">
          <label>最大数量：</label>
          <input
            v-model.number="config.maxStocks"
            type="number"
            min="1"
            max="100"
            class="filter-input"
          />
        </div>
      </div>
    </div>

    <!-- 股票预览 -->
    <div class="config-section" v-if="previewStocks.length > 0">
      <h4 class="section-title">股票行情预览（前5只）</h4>
      <div class="stock-preview-grid">
        <StockDataPreview
          v-for="stock in previewStocks.slice(0, 5)"
          :key="`${stock.code}-${previewDefaultRange}`"
          :stock-code="stock.code"
          :stock-name="stock.name"
          :data="stock.data"
          :metrics="stock.metrics"
          :loading="stock.loading"
          :show-volume="true"
          :show-time-range="true"
          :default-range="previewDefaultRange"
          :chart-width="340"
          :chart-height="100"
          @range-change="handlePreviewRangeChange(stock.code, $event)"
        />
      </div>
    </div>

    <!-- 已选择的股票列表 -->
    <div class="config-section" v-if="previewStocks.length > 5">
      <h4 class="section-title">已选择的股票（{{ previewStocks.length }}只）</h4>
      <div class="selected-stocks">
        <div v-for="(stock, index) in previewStocks" :key="index" class="stock-tag">
          <span class="stock-code">{{ stock.code }}</span>
          <span class="stock-name">{{ stock.name }}</span>
          <button class="remove-btn" @click="removeStock(index)">×</button>
        </div>
      </div>
    </div>

    <!-- 数据获取进度 -->
    <div class="config-section" v-if="isLoadingData">
      <h4 class="section-title">数据获取中...</h4>
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="progress-text">
          正在获取 {{ loadingCurrent }}/{{ loadingTotal }} 只股票的数据
        </div>
      </div>
    </div>

    <!-- 数据报告 -->
    <div class="config-section" v-if="showDataReport">
      <h4 class="section-title">
        <font-awesome-icon icon="chart-pie" />
        数据报告
      </h4>
      <div class="data-report-grid">
        <div class="data-report-card highlight">
          <div class="report-icon">
            <font-awesome-icon icon="chart-line" />
          </div>
          <div class="report-content">
            <div class="report-label">股票数量</div>
            <div class="report-value">{{ dataReport.totalStocks }}</div>
          </div>
        </div>
        <div class="data-report-card">
          <div class="report-icon success">
            <font-awesome-icon icon="database" />
          </div>
          <div class="report-content">
            <div class="report-label">总数据量</div>
            <div class="report-value">{{ formatNumber(dataReport.totalDataPoints) }} 条</div>
          </div>
        </div>
        <div class="data-report-card">
          <div class="report-icon info">
            <font-awesome-icon icon="calendar-alt" />
          </div>
          <div class="report-content">
            <div class="report-label">时间范围</div>
            <div class="report-value-small">{{ formatDateRangeDisplay(config.startDate, config.endDate) }}</div>
          </div>
        </div>
        <div class="data-report-card" :class="dataReport.allSuccess ? 'success' : 'warning'">
          <div class="report-icon" :class="dataReport.allSuccess ? 'success-bg' : 'warning-bg'">
            <font-awesome-icon :icon="dataReport.allSuccess ? 'check-circle' : 'exclamation-triangle'" />
          </div>
          <div class="report-content">
            <div class="report-label">获取状态</div>
            <div class="report-value">{{ dataReport.successCount }}/{{ dataReport.totalStocks }} 成功</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import StockDataPreview from '../../components/charts/StockDataPreview.vue'
import { getStockDetail, getStockHistory, getIndicators } from '../../api/modules/data'
import { timeRangeSyncService, timeRangeSyncState, formatDateToLocal, calculateDateFromRange } from '../../utils/timeRangeSync'

interface StockData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface StockMetrics {
  ma5?: number
  ma10?: number
  ma20?: number
  ma60?: number
  rsi?: number
  macd?: number
  kdj?: {
    k?: number
    d?: number
    j?: number
  }
  pe?: number
  pb?: number
}

interface StockPreview {
  code: string
  name: string
  data: StockData[]
  metrics: StockMetrics
  loading: boolean
  isRealData?: boolean
  error?: Error
}

interface StockConfig {
  stockCode: string
  timeRange: string
  startDate: string
  endDate: string
  frequency: string
  frequencies?: string[]  // 多频率选择,新增字段
  includeDividends: boolean
  adjustPrices: boolean
  includeVolume: boolean
  marketType: string
  stockType: string
  sortBy: string
  maxStocks: number
  intradayIntervals: string[]
}

const props = defineProps<{
  modelValue: StockConfig
}>()

const emit = defineEmits<{
  'update:modelValue': [value: StockConfig]
}>()

const config = reactive({
  ...props.modelValue,
  intradayIntervals: props.modelValue.intradayIntervals || [],
  // 兼容旧的单频率配置,转换为数组
  frequencies: props.modelValue?.frequencies || (props.modelValue?.frequency ? [props.modelValue.frequency] : ['daily'])
})

// 多频率选择的响应式数组
const selectedFrequencies = ref<string[]>(config.frequencies || ['daily'])

// 监听频率选择变化,同步到config
watch(selectedFrequencies, (newFrequencies) => {
  config.frequencies = newFrequencies
  // 为了向后兼容,同时更新frequency字段(使用第一个选中的频率)
  config.frequency = newFrequencies.length > 0 ? newFrequencies[0] : 'daily'

  // 同步频率到联动服务
  if (isInitialized) {
    console.log(`[股票选择节点] 频率变化,同步到联动服务:`, newFrequencies)
    timeRangeSyncService.updateStockFrequencies(newFrequencies)
  }
}, { deep: true })

// 计算是否选中了分钟级频率
const hasIntradayFrequency = computed(() => {
  return selectedFrequencies.value.some(freq =>
    freq === '5min' || freq === '15min' || freq === '30min' || freq === '60min'
  )
})

// 保留原有的计算属性用于向后兼容
const isIntradayFrequency = computed(() => {
  const freq = config.frequency
  return freq === '5min' || freq === '15min' || freq === '30min' || freq === '60min'
})

// 时间范围联动状态
const syncState = timeRangeSyncState
let unsubscribeSync: (() => void) | null = null
let unsubscribeFrequencySync: (() => void) | null = null
let isInitialized = false  // 标记是否已完成初始化

// 处理时间范围变化（同步到联动服务）
const handleTimeRangeChange = () => {
  // 只在初始化完成后才同步
  if (!isInitialized) {
    console.log('[股票选择节点] handleTimeRangeChange: 未初始化,跳过同步')
    return
  }

  console.log(`[股票选择节点] handleTimeRangeChange: 同步时间范围 ${config.timeRange} (${config.startDate} 到 ${config.endDate})`)

  // 更新联动服务中的股票节点时间范围
  timeRangeSyncService.updateStockTimeRange({
    timeRange: config.timeRange,
    startDate: config.startDate,
    endDate: config.endDate
  })
}

// 初始化智能默认时间范围
const initializeDefaultTimeRange = async () => {
  // 只在日期完全为空时才设置默认值（不覆盖用户已有的设置）
  // 检查 props.modelValue 中的原始值，而不是 reactive config
  const hasUserSetStartDate = props.modelValue?.startDate && props.modelValue?.startDate.trim() !== ''
  const hasUserSetEndDate = props.modelValue?.endDate && props.modelValue?.endDate.trim() !== ''
  const hasUserSetTimeRange = props.modelValue?.timeRange && props.modelValue?.timeRange.trim() !== ''

  if (!hasUserSetStartDate || !hasUserSetEndDate) {
    const now = new Date()
    console.log(`[时间范围初始化] 当前时间: ${now.toLocaleString()}`)
    console.log(`[时间范围初始化] 用户未设置完整日期，使用智能默认值`)

    // 智能获取最新的完整交易日数据
    const latestTradingDay = await getLatestAvailableTradingDay()

    // 检查是否选择了分钟级频率，如果有，使用更短的默认时间范围
    const initialFrequencies = selectedFrequencies.value
    const hasInitialMinuteFrequency = initialFrequencies.some(f =>
      f === '5min' || f === '15min' || f === '30min' || f === '60min'
    )

    let defaultDays = 365  // 默认1年
    let defaultTimeRange = '1Y'

    if (hasInitialMinuteFrequency) {
      // 找出最小的天数限制
      let minMaxDays = Infinity
      for (const freq of initialFrequencies) {
        if (frequencyMaxDays[freq] !== undefined) {
          minMaxDays = Math.min(minMaxDays, frequencyMaxDays[freq])
        }
      }

      if (minMaxDays !== Infinity) {
        // 尝试匹配预设时间范围
        const matchingPreset = timePresets.find(p => p.days === minMaxDays)
        if (matchingPreset) {
          defaultDays = minMaxDays
          defaultTimeRange = matchingPreset.value
          console.log(`[时间范围初始化] 检测到分钟级频率，使用预设时间范围: ${matchingPreset.label}`)
        } else {
          defaultDays = minMaxDays
          defaultTimeRange = 'custom'
          console.log(`[时间范围初始化] 检测到分钟级频率，使用自定义时间范围: ${minMaxDays}天`)
        }
      }
    }

    // 只更新空的日期，保留用户已有的设置
    if (!hasUserSetEndDate) {
      config.endDate = latestTradingDay
    }
    if (!hasUserSetStartDate) {
      // 使用计算出的默认天数，从结束日期往前推
      const endDate = new Date(config.endDate || latestTradingDay)
      const startDate = new Date(endDate)
      startDate.setDate(endDate.getDate() - defaultDays)
      config.startDate = formatDateToLocal(startDate)
    }
    // 设置默认的 timeRange
    if (!hasUserSetTimeRange) {
      config.timeRange = defaultTimeRange
    }

    console.log(`[时间范围初始化] 智能获取最新交易收盘日: ${config.startDate} 到 ${config.endDate}`)
    console.log(`[时间范围初始化] 默认时间范围: ${config.timeRange}`)
    console.log(`[时间范围初始化] 使用API实时获取的最新完整交易日数据`)

    // 验证数据可用性
    await validateDateRange()
  } else {
    console.log(`[时间范围初始化] 用户已设置日期: ${config.startDate} 到 ${config.endDate}，跳过初始化`)
  }
}

// 格式化日期为本地日期字符串（YYYY-MM-DD）
function formatDateToLocal(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 获取最新可用的交易日数据 - 包含周末逻辑版本
const getLatestAvailableTradingDay = async (): Promise<string> => {
  try {
    const now = new Date()
    const currentHour = now.getHours()
    const currentMinute = now.getMinutes()
    const dayOfWeek = now.getDay() // 0=周日, 1=周一, ..., 6=周六

    console.log(`[获取最新交易日] 当前时间: ${currentHour}:${currentMinute.toString().padStart(2, '0')}, 星期${dayOfWeek}`)

    // 根据当前时间和是否周末智能选择日期
    let targetDate = new Date(now)

    if (currentHour > 15 || (currentHour === 15 && currentMinute >= 30)) {
      // 收盘后 (15:30后-23:59前): 使用当天，但如果当天是周末则需要调整
      console.log(`[获取最新交易日] 收盘后，检查当天是否为交易日...`)

      if (dayOfWeek === 0) {
        // 周日，使用上周五
        targetDate.setDate(now.getDate() - 2)
        console.log(`[获取最新交易日] 周日，使用上周五: ${formatDateToLocal(targetDate)}`)
      } else if (dayOfWeek === 6) {
        // 周六，使用上周五
        targetDate.setDate(now.getDate() - 1)
        console.log(`[获取最新交易日] 周六，使用上周五: ${formatDateToLocal(targetDate)}`)
      } else {
        // 工作日，使用当天
        console.log(`[获取最新交易日] 工作日收盘后，使用当天: ${formatDateToLocal(targetDate)}`)
      }
    } else {
      // 其他时间 (00:00-15:29): 使用前一个交易日
      console.log(`[获取最新交易日] 非收盘时间，查找前一个交易日...`)

      if (dayOfWeek === 1) {
        // 周一，使用上周五
        targetDate.setDate(now.getDate() - 3)
        console.log(`[获取最新交易日] 周一，使用上周五: ${formatDateToLocal(targetDate)}`)
      } else if (dayOfWeek === 0) {
        // 周日，使用上周五
        targetDate.setDate(now.getDate() - 2)
        console.log(`[获取最新交易日] 周日，使用上周五: ${formatDateToLocal(targetDate)}`)
      } else {
        // 其他情况，使用前一天
        targetDate.setDate(now.getDate() - 1)
        console.log(`[获取最新交易日] 使用前一天: ${formatDateToLocal(targetDate)}`)
      }
    }

    return formatDateToLocal(targetDate)

  } catch (error) {
    console.warn(`[获取最新交易日] 获取失败: ${error}, 使用默认日期`)
    return '2025-12-10'
  }
}

// 验证时间范围内的数据可用性
const validateDateRange = async () => {
  if (!config.stockCode || !config.startDate || !config.endDate) {
    return
  }

  try {
    // 取第一个股票代码进行验证
    const firstSymbol = config.stockCode.split(/[,，]/)[0].trim()
    if (!firstSymbol) return

    console.log(`[时间范围验证] 验证 ${firstSymbol} 在 ${config.startDate} 到 ${config.endDate} 的数据可用性`)

    // 这里可以添加API调用来验证数据可用性
    // 由于复杂性，暂时使用日志提示

  } catch (error) {
    console.warn('[时间范围验证] 验证失败:', error)
  }
}

// 组件挂载时初始化
onMounted(async () => {
  await initializeDefaultTimeRange()

  // 订阅时间范围联动
  unsubscribeSync = timeRangeSyncService.subscribe((syncedConfig) => {
    // 只有当主节点是指数节点时才应用同步的配置
    // 避免循环更新
    if (syncState.masterNode === 'index' && isInitialized) {
      // 更新本地配置
      config.timeRange = syncedConfig.timeRange
      config.startDate = syncedConfig.startDate
      config.endDate = syncedConfig.endDate

      // 立即触发emit,让父组件知道配置已更新
      emit('update:modelValue', { ...config })
    }
  })

  // 订阅频率联动
  unsubscribeFrequencySync = timeRangeSyncService.subscribeFrequencies((syncedFrequencies) => {
    // 只有当主节点是指数节点时才应用同步的频率
    if (syncState.masterNode === 'index' && isInitialized) {
      console.log(`[股票选择节点] 收到频率同步通知:`, syncedFrequencies)
      // 更新本地配置
      selectedFrequencies.value = [...syncedFrequencies]
      config.frequencies = [...syncedFrequencies]
      config.frequency = syncedFrequencies.length > 0 ? syncedFrequencies[0] : 'daily'
      emit('update:modelValue', { ...config })
    }
  })

  // 检查是否需要应用联动的时间范围
  // 如果指数节点已经设置了时间范围,应用它
  const state = timeRangeSyncService.getState()
  if (state.masterNode === 'index' && state.syncedTimeRange.startDate) {
    config.timeRange = state.syncedTimeRange.timeRange
    config.startDate = state.syncedTimeRange.startDate
    config.endDate = state.syncedTimeRange.endDate
  }

  // 检查是否需要应用联动的频率
  if (state.masterNode === 'index' && state.syncedFrequencies) {
    console.log(`[股票选择节点] 检测到指数节点已设置频率,应用联动:`, state.syncedFrequencies)
    selectedFrequencies.value = [...state.syncedFrequencies]
    config.frequencies = [...state.syncedFrequencies]
    config.frequency = state.syncedFrequencies.length > 0 ? state.syncedFrequencies[0] : 'daily'
  }

  // 标记初始化完成
  isInitialized = true

  // 初始化时,同步当前配置到联动服务
  // 这样可以让另一个节点知道当前节点的配置
  if (config.startDate && config.endDate) {
    timeRangeSyncService.updateStockTimeRange({
      timeRange: config.timeRange,
      startDate: config.startDate,
      endDate: config.endDate
    })
  }

  // 初始化时,同步频率到联动服务
  if (selectedFrequencies.value) {
    console.log(`[股票选择节点] 初始化频率同步:`, selectedFrequencies.value)
    timeRangeSyncService.updateStockFrequencies(selectedFrequencies.value)
  }

  // 🔧 修复：禁用初始化时自动获取股票数据预览
  // 用户应该手动点击"获取数据"按钮来触发数据获取
  // if (config.stockCode && config.stockCode.trim()) {
  //   console.log('[股票选择节点] 初始化时获取股票数据预览')
  //   const codes = config.stockCode.split(/[,，]/).map(code => code.trim()).filter(code => code)
  //   if (codes.length > 0) {
  //     validateStockCodes(codes)
  //   }
  // }
})

// 组件卸载时取消订阅
onUnmounted(() => {
  if (unsubscribeSync) {
    unsubscribeSync()
  }
  if (unsubscribeFrequencySync) {
    unsubscribeFrequencySync()
  }
})

// 预设时间范围选项
const timePresets = [
  { label: '近1周', value: '1W', days: 7 },
  { label: '近1个月', value: '1M', days: 30 },
  { label: '近3个月', value: '3M', days: 90 },
  { label: '近6个月', value: '6M', days: 180 },
  { label: '近1年', value: '1Y', days: 365 },
  { label: '近2年', value: '2Y', days: 730 },
]

// 分钟级数据选项（现在是主要的数据频率选项）
const intradayIntervals = [
  { label: '1分钟', value: '1min', description: '超短线，适合高频分析' },
  { label: '5分钟', value: '5min', description: '短线交易分析' },
  { label: '15分钟', value: '15min', description: '适合日内交易' },
  { label: '30分钟', value: '30min', description: '适合波段操作' },
  { label: '60分钟', value: '60min', description: '适合中短期趋势' }
]

// 数据频率选项（整合了分钟级、日线、周线、月线）
const dataFrequencies = [
  { label: '5分钟', value: '5min', description: '短线交易分析，最多1周数据', intraday: true },
  { label: '15分钟', value: '15min', description: '适合日内交易，最多1个月数据', intraday: true },
  { label: '30分钟', value: '30min', description: '适合波段操作，最多2个月数据', intraday: true },
  { label: '60分钟', value: '60min', description: '适合中短期趋势，最多半年数据', intraday: true },
  { label: '日线', value: 'daily', description: '每日交易数据', intraday: false },
  { label: '周线', value: 'weekly', description: '每周交易数据', intraday: false },
  { label: '月线', value: 'monthly', description: '每月交易数据', intraday: false },
]

// 频率时间范围限制（天数）
const frequencyMaxDays: Record<string, number> = {
  '5min': 7,      // 1周
  '15min': 30,    // 1个月
  '30min': 60,    // 2个月
  '60min': 180,   // 半年
}


const today = computed(() => {
  const date = new Date()
  return formatDateToLocal(date)
})

// 计算时间范围选项是否应该被禁用
// 根据选中的频率判断允许的最大天数
const isTimeRangeDisabled = (preset: { label: string; value: string; days: number }) => {
  if (!hasIntradayFrequency.value) {
    return false // 非分钟级数据，不限制
  }

  // 获取所有选中频率中最小的限制天数
  let minMaxDays = Infinity
  for (const freq of selectedFrequencies.value) {
    if (frequencyMaxDays[freq] !== undefined) {
      minMaxDays = Math.min(minMaxDays, frequencyMaxDays[freq])
    }
  }

  // 如果有分钟级频率，检查是否超过限制
  if (minMaxDays !== Infinity) {
    return preset.days > minMaxDays
  }

  return false
}

// 计算是否显示分钟级数据选项（已废弃，现在分钟级是主要频率选项）
const showIntradayOptions = computed(() => {
  // 不再需要单独的分钟级选项区域
  return false
})

// 监听频率变化，自动调整时间范围
watch(() => config.frequency, (newFreq, oldFreq) => {
  if (newFreq === oldFreq) return

  // 检查是否切换到分钟级频率
  const wasIntraday = oldFreq === '5min' || oldFreq === '15min' || oldFreq === '30min' || oldFreq === '60min'
  const isIntraday = newFreq === '5min' || newFreq === '15min' || newFreq === '30min' || newFreq === '60min'

  if (isIntraday && !wasIntraday) {
    // 切换到分钟级数据，根据频率调整时间范围
    const maxDays = frequencyMaxDays[newFreq] || 30
    const currentDays = Math.ceil((new Date(config.endDate || today.value).getTime() -
                                   new Date(config.startDate).getTime()) / (1000 * 60 * 60 * 24))

    if (currentDays > maxDays) {
      // 如果当前时间范围超过限制，自动调整
      const endDate = new Date()
      const startDate = new Date(endDate)
      startDate.setDate(endDate.getDate() - maxDays)

      config.timeRange = 'custom'
      config.startDate = formatDateToLocal(startDate)
      config.endDate = formatDateToLocal(endDate)
      console.log(`[频率切换] 分钟级数据自动调整为${maxDays}天: ${config.startDate} 到 ${config.endDate}`)
    }
  }
})

// 监听多频率选择变化
watch(selectedFrequencies, (newFrequencies, oldFrequencies) => {
  if (!oldFrequencies || oldFrequencies.length === 0) return

  const hadIntraday = oldFrequencies.some(f =>
    f === '5min' || f === '15min' || f === '30min' || f === '60min'
  )
  const hasIntraday = newFrequencies.some(f =>
    f === '5min' || f === '15min' || f === '30min' || f === '60min'
  )

  // 如果从非分钟级切换到包含分钟级,自动调整时间范围
  if (hasIntraday && !hadIntraday) {
    // 获取最严格的限制（最小天数）
    let minMaxDays = Infinity
    for (const freq of newFrequencies) {
      if (frequencyMaxDays[freq] !== undefined) {
        minMaxDays = Math.min(minMaxDays, frequencyMaxDays[freq])
      }
    }

    if (minMaxDays !== Infinity) {
      // 找到对应的预设时间范围
      const matchingPreset = timePresets.find(p => p.days === minMaxDays)
      if (matchingPreset) {
        // 使用预设的 selectTimeRange 函数来设置时间范围
        selectTimeRange(matchingPreset)
        console.log(`[多频率选择] 检测到分钟级数据,自动调整为预设时间范围: ${matchingPreset.label}`)
      } else {
        // 如果没有完全匹配的预设，使用自定义范围
        const endDate = new Date()
        const startDate = new Date(endDate)
        startDate.setDate(endDate.getDate() - minMaxDays)

        config.timeRange = 'custom'
        config.startDate = formatDateToLocal(startDate)
        config.endDate = formatDateToLocal(endDate)
        console.log(`[多频率选择] 检测到分钟级数据,自动调整为自定义范围(${minMaxDays}天): ${config.startDate} 到 ${config.endDate}`)
      }
    }
  }
}, { deep: true })


// 解析股票代码
const previewStocks = ref<StockPreview[]>([])

// 数据加载状态 - 必须在计算属性之前定义
const isLoadingData = ref(false)
const loadingProgress = ref(0)
const loadingCurrent = ref(0)
const loadingTotal = ref(0)

// 数据报告 - 使用独立响应式变量以确保计算属性能正确追踪
const totalStocks = ref(0)
const totalDataPoints = ref(0)
const successCount = ref(0)
const allSuccess = ref(false)

// 计算属性：是否显示数据报告
const showDataReport = computed(() => {
  const shouldShow = !isLoadingData.value && totalStocks.value > 0
  console.log('[showDataReport] 计算属性:', {
    isLoadingData: isLoadingData.value,
    totalStocks: totalStocks.value,
    shouldShow
  })
  return shouldShow
})

// 监听 showDataReport 的变化
watch(showDataReport, (newVal) => {
  console.log('[showDataReport] 值变化:', newVal)
})

// 为了兼容模板，保留 dataReport 作为计算属性
const dataReport = computed(() => ({
  totalStocks: totalStocks.value,
  totalDataPoints: totalDataPoints.value,
  successCount: successCount.value,
  allSuccess: allSuccess.value
}))

// 防抖定时器
let debounceTimer: NodeJS.Timeout | null = null

// 延迟验证股票代码
const validateStockCodes = async (codes: string) => {
  const stockPreviews: StockPreview[] = []

  // 初始化加载状态
  isLoadingData.value = true
  loadingTotal.value = codes.length
  loadingCurrent.value = 0
  loadingProgress.value = 0

  for (const code of codes) {
    // 更新加载进度
    loadingCurrent.value++
    loadingProgress.value = Math.round((loadingCurrent.value / loadingTotal.value) * 100)
    try {
      // 尝试获取真实股票数据
      const stockDetail = await getStockDetail(code)
      const historyData = await getStockHistory(code, {
        startDate: config.startDate,
        endDate: config.endDate,
        frequency: 'daily'
      })

      // 注意：智能数据补全现在由后端QuantDataHub处理
      // 后端会自动分析数据完整性并进行智能补全

      const indicators = await getIndicators(code, ['ma5', 'ma20', 'rsi'])

      console.log(`[validateStockCodes] 股票 ${code} 数据检查:`, {
        hasStockDetail: !!stockDetail?.data,
        hasHistoryData: !!historyData?.data,
        historyDataLength: historyData?.data?.length || 0,
        stockDetailData: stockDetail?.data,
        historyDataData: historyData?.data
      })

      // 检查数据有效性
      if (stockDetail?.data && historyData?.data && historyData.data.length > 0) {
        console.log(`[validateStockCodes] 股票 ${code} 数据有效，添加到预览列表，数据量: ${historyData.data.length}`)
        // 使用格式化后的代码（如 000001.SZ）作为 code，这样 StockDataPreview 组件会显示完整代码
        const formattedCode = stockDetail.data.code || code
        stockPreviews.push({
          code: formattedCode,  // 使用格式化后的代码
          name: formattedCode,  // name 也使用格式化代码（因为后端暂未返回真实名称）
          data: historyData.data,
          metrics: indicators?.data || {
            ma5: historyData.data[historyData.data.length - 1]?.close || 0,
            ma20: historyData.data[historyData.data.length - 1]?.close || 0,
            rsi: 50,
            pe: 15
          },
          loading: false,
          isRealData: true
        })
      } else {
        // 数据不完整时不抛出错误，而是显示提示
        console.warn(`股票 ${code} 数据不完整或无效，将在用户完成输入后进行验证`)

        stockPreviews.push({
          code: code,  // 使用原始代码
          name: code,  // 只显示股票代码
          data: [],
          metrics: {},
          loading: false,
          isRealData: false
        })
      }

    } catch (error) {
      console.error(`获取股票 ${code} 数据失败:`, error)

      // 创建错误状态的股票预览，不使用模拟数据
      stockPreviews.push({
        code: code,  // 使用原始代码
        name: code,  // 只显示股票代码
        data: [],
        metrics: {},
        loading: false,
        isRealData: false,
        error: error as Error
      })
    }
  }

  console.log(`[validateStockCodes] 所有股票处理完成，准备设置 previewStocks，数量: ${stockPreviews.length}`)
  previewStocks.value = stockPreviews
  console.log(`[validateStockCodes] previewStocks.value 已设置，长度: ${previewStocks.value.length}`)
  console.log(`[validateStockCodes] previewStocks.value[0]:`, previewStocks.value[0])

  // 加载完成
  console.log(`[validateStockCodes] 设置 isLoadingData.value = false`)
  isLoadingData.value = false

  // 更新数据报告（在isLoadingData设置为false之后）
  await nextTick()
  console.log(`[validateStockCodes] 调用 updateDataReport()`)
  updateDataReport()
  console.log(`[validateStockCodes] updateDataReport() 调用完成，showDataReport: ${showDataReport.value}, totalStocks: ${totalStocks.value}`)
}

// 监听股票代码变化，使用防抖机制
watch(() => config.stockCode, async (newCodes) => {
  // 清除之前的定时器
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  if (!newCodes) {
    previewStocks.value = []
    // 重置数据报告
    updateDataReport()
    return
  }

  // 设置新的防抖定时器，延迟800ms后执行验证
  debounceTimer = setTimeout(async () => {
    const codes = newCodes.split(/[,，]/).map(code => code.trim()).filter(code => code)
    if (codes.length > 0) {
      await validateStockCodes(codes)
    }
  }, 800)
}, { immediate: false })

// 保留原有的计算属性作为备用（当API不可用时）
// const previewStocks = computed(() => {
//   if (!config.stockCode) return []
//
//   const codes = config.stockCode.split(/[,，]/).map(code => code.trim()).filter(code => code)
//   return codes.map(code => {
//     const example = stockExamples.find(s => s.code === code)
//     const index = stockIndexes.find(i => i.code === code)
//
//     // 为不同股票生成不同的基础价格
//     // 移除硬编码的股票价格映射，使用真实API数据
//     const basePriceMap: Record<string, number> = {
//       '000001': 12.5,
//       '000002': 18.8,
//       '601318': 45.2,
//       '600519': 1680.5,
//       '002594': 258.3,
//       'SH000001': 3080.5,
//       'SZ399001': 11250.8,
//       'SH000300': 3850.2,
//       'SH000905': 5680.5,
//       'SZ399006': 2280.3
//     }
//
//     const basePrice = basePriceMap[code] || (Math.random() * 100 + 50)
//     const data = generateMockStockData(basePrice)
//     const metrics = generateMockMetrics(data)
//
//     return {
//       code,
//       name: example?.name || index?.name || code,
//       data,
//       metrics,
//       loading: false
//     }
//   })
// })

// 监听配置变化
watch(config, () => {
  emit('update:modelValue', { ...config })
}, { deep: true })

// 选择预设时间范围
const selectTimeRange = (preset: { label: string; value: string; days: number }) => {
  // 检查是否是分钟级频率且时间范围超过限制
  if (hasIntradayFrequency.value) {
    // 获取所有选中频率中最小的限制天数
    let minMaxDays = Infinity
    for (const freq of selectedFrequencies.value) {
      if (frequencyMaxDays[freq] !== undefined) {
        minMaxDays = Math.min(minMaxDays, frequencyMaxDays[freq])
      }
    }

    if (minMaxDays !== Infinity && preset.days > minMaxDays) {
      console.warn(`[时间范围选择] 选中的分钟级频率最多只能选择${minMaxDays}天的时间范围`)
      return // 不执行切换
    }
  }

  config.timeRange = preset.value

  // 使用今天作为结束日期（与指数选择节点保持一致）
  const endDate = new Date()
  const startDate = new Date(endDate)
  startDate.setDate(endDate.getDate() - preset.days)

  config.endDate = formatDateToLocal(endDate)
  config.startDate = formatDateToLocal(startDate)

  console.log(`[预设时间范围] 选择 ${preset.label}: ${config.startDate} 到 ${config.endDate}`)

  // 同步到联动服务
  handleTimeRangeChange()
}

// 处理自定义日期变化
const handleCustomDateChange = () => {
  config.timeRange = 'custom'
  // 同步到联动服务
  handleTimeRangeChange()
}

// 移除股票
const removeStock = (index: number) => {
  const codes = config.stockCode.split(/[,，]/).map(code => code.trim()).filter(code => code)
  codes.splice(index, 1)
  config.stockCode = codes.join(', ')
}

// 处理股票代码变化
const handleStockCodeChange = () => {
  // 可以在这里添加股票代码验证逻辑
}

// 🔧 格式化日期范围显示（只显示日期部分）
const formatDateRangeDisplay = (startDate: string, endDate: string): string => {
  if (!startDate || !endDate || startDate === '--' || endDate === '--') return '--'

  // 提取日期部分，忽略时间和T
  // 支持格式: "2025-01-01T10:30:00" 或 "2025-01-01 10:30:00" 或 "2025-01-01"
  const extractDate = (dateStr: string) => {
    // 移除T或空格之后的时间部分
    const tIndex = dateStr.indexOf('T')
    if (tIndex !== -1) {
      return dateStr.substring(0, tIndex)
    }
    const spaceIndex = dateStr.indexOf(' ')
    if (spaceIndex !== -1) {
      return dateStr.substring(0, spaceIndex)
    }
    return dateStr
  }

  const startClean = extractDate(startDate)
  const endClean = extractDate(endDate)

  // 简化日期格式，只显示月日，例如 "2025-01-01" -> "01-01"
  const start = startClean.split('-').slice(1).join('-')
  const end = endClean.split('-').slice(1).join('-')
  return `${start} 至 ${end}`
}

// 处理预览时间范围变化
const handlePreviewRangeChange = (stockCode: string, range: string) => {
  // 这里可以加载对应时间范围的数据
}

// 映射配置的时间范围到预览组件的时间范围
const mapTimeRangeToPreviewRange = (timeRange: string): string => {
  const rangeMap: Record<string, string> = {
    '1W': '5D',    // 1周映射到5日
    '1M': '1M',    // 1月保持不变
    '3M': '3M',    // 3月保持不变
    '6M': '6M',    // 6月保持不变
    '1Y': '1Y',    // 1年保持不变
    '2Y': 'ALL',   // 2年映射到全部
    'custom': 'ALL' // 自定义范围映射到全部
  }
  return rangeMap[timeRange] || '1M' // 默认返回1月
}

// 计算预览组件的默认时间范围
const previewDefaultRange = computed(() => {
  return mapTimeRangeToPreviewRange(config.timeRange)
})

// 格式化数字显示
const formatNumber = (num: number): string => {
  if (num >= 100000000) {
    return (num / 100000000).toFixed(2) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(2) + '万'
  } else {
    return num.toString()
  }
}

// 格式化频率显示
const formatFrequencies = (frequencies: string[]): string => {
  const freqMap: Record<string, string> = {
    '1min': '1分钟',
    '5min': '5分钟',
    '15min': '15分钟',
    '30min': '30分钟',
    '60min': '60分钟',
    'daily': '日线',
    'weekly': '周线',
    'monthly': '月线'
  }
  return frequencies.map(f => freqMap[f] || f).join('、')
}

// 更新数据报告
const updateDataReport = () => {
  console.log('[updateDataReport] 开始更新数据报告')

  if (previewStocks.value.length === 0) {
    totalStocks.value = 0
    totalDataPoints.value = 0
    successCount.value = 0
    allSuccess.value = false
    console.log('[updateDataReport] 没有股票，重置报告')
    return
  }

  const stocksCount = previewStocks.value.length
  let dataPoints = 0
  let successes = 0

  previewStocks.value.forEach(stock => {
    if (stock.data && stock.data.length > 0) {
      dataPoints += stock.data.length
      successes++
    }
  })

  totalStocks.value = stocksCount
  totalDataPoints.value = dataPoints
  successCount.value = successes
  allSuccess.value = successes === stocksCount

  console.log('[updateDataReport] 数据报告已更新:', {
    totalStocks: totalStocks.value,
    totalDataPoints: totalDataPoints.value,
    isLoadingData: isLoadingData.value,
    showDataReport: showDataReport.value
  })
}

// 注意：智能数据补全功能已移至后端QuantDataHub统一处理
// 前端不再需要数据完整性分析和补全逻辑，由后端自动完成：
// - 热数据层：实时缓存，秒级更新
// - 温数据层：近期历史，分钟级更新
// - 冷数据层：长期历史，按需加载
// - 智能缺口检测和自动补全
</script>

<style lang="scss" scoped>
.stock-selection-config {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stock-input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stock-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 10px 12px;
  color: #fff;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #8b5cf6;
    background: rgba(255, 255, 255, 0.08);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
}

.stock-examples,
.stock-index-examples {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.example-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-right: 8px;
}

.example-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 4px 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }

  &.index-btn {
    background: rgba(139, 92, 246, 0.1);
    border-color: rgba(139, 92, 246, 0.3);

    &:hover {
      background: rgba(139, 92, 246, 0.2);
    }
  }
}

.time-range-notice {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 6px;

  .notice-text {
    color: rgba(139, 92, 246, 0.9);
    font-size: 12px;
    line-height: 1.4;
  }
}

.time-range-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.time-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 6px 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }

  &.active {
    background: #8b5cf6;
    border-color: #8b5cf6;
    color: #fff;
  }

  &.disabled {
    opacity: 0.4;
    cursor: not-allowed;
    background: rgba(255, 255, 255, 0.02);
    border-color: rgba(255, 255, 255, 0.05);

    &:hover {
      background: rgba(255, 255, 255, 0.02);
      color: rgba(255, 255, 255, 0.8);
    }
  }
}

.custom-range {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.range-inputs {
  display: flex;
  gap: 12px;
}

.range-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;

  label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    white-space: nowrap;
  }
}

.date-input {
  flex: 1;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #8b5cf6;
  }

  &::-webkit-calendar-picker-indicator {
    filter: invert(0.5);
    cursor: pointer;
  }
}

.frequency-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.frequency-description {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: rgba(251, 146, 60, 0.1);
  border: 1px solid rgba(251, 146, 60, 0.3);
  border-radius: 6px;

  .notice-text {
    color: rgba(251, 146, 60, 0.9);
    font-size: 12px;
    line-height: 1.4;
  }
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  input[type="radio"] {
    accent-color: #8b5cf6;
  }

  span {
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
  }

  small {
    color: rgba(255, 255, 255, 0.5);
    font-size: 11px;
    margin-left: auto;
  }
}

.other-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  input[type="checkbox"] {
    accent-color: #8b5cf6;
  }

  span {
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
  }
}

.selected-stocks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.stock-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: var(--spacing-3);
  max-height: 600px;
  overflow-y: auto;
  padding-right: var(--spacing-1);

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 2px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
}

.selected-stocks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.stock-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 4px;
  padding: 4px 8px;

  .stock-code {
    color: #8b5cf6;
    font-size: 12px;
    font-family: monospace;
  }

  .stock-name {
    color: rgba(255, 255, 255, 0.8);
    font-size: 12px;
  }

  .remove-btn {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    font-size: 14px;
    cursor: pointer;
    padding: 0;
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 2px;
    transition: all 0.2s;

    &:hover {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
    }
  }
}

.filter-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;

  label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
  }

  .filter-select,
  .filter-input {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    padding: 6px 10px;
    color: #fff;
    font-size: 13px;
    transition: all 0.2s ease;

    &:focus {
      outline: none;
      border-color: #8b5cf6;
      background: rgba(255, 255, 255, 0.08);
    }

    &::placeholder {
      color: rgba(255, 255, 255, 0.4);
    }
  }

  // 修复下拉框选项样式，确保与主题一致
  .filter-select {
    // 下拉框默认背景色，与输入框保持一致
    background: rgba(255, 255, 255, 0.05);

    &:hover {
      background: rgba(255, 255, 255, 0.08);
    }

    // Firefox 样式
    option {
      background: rgba(45, 55, 72, 0.95);
      color: #fff;
      padding: 8px 12px;
      border: none;
    }

    option:hover,
    option:focus {
      background: rgba(74, 85, 104, 0.95);
    }

    option:checked,
    option:selected {
      background: #8b5cf6 !important;
      color: #fff;
    }

    // Webkit 浏览器（Chrome, Safari, Edge）样式
    &::-webkit-calendar-picker-indicator {
      filter: invert(1);
      cursor: pointer;
    }
  }

  .filter-input[type="number"] {
    -moz-appearance: textfield;

    &::-webkit-inner-spin-button,
    &::-webkit-outer-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }
  }
}

// 数据报告样式
.data-report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.data-report-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--card-bg);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
}

.data-report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.data-report-card.highlight {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, var(--card-bg) 100%);
  border-color: rgba(139, 92, 246, 0.3);
}

.data-report-card.success {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, var(--card-bg) 100%);
  border-color: rgba(34, 197, 94, 0.3);
}

.data-report-card.warning {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, var(--card-bg) 100%);
  border-color: rgba(251, 191, 36, 0.3);
}

.report-icon {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, #6366f1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.report-icon.success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.report-icon.info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.report-icon.success-bg {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.report-icon.warning-bg {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.report-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.report-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.report-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.report-value-small {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

// 进度条样式
.progress-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
}
</style>