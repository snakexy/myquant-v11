<template>
  <div class="index-selection-config">
    <!-- 指数代码输入 -->
    <div class="config-section">
      <h4 class="section-title">指数代码</h4>
      <div class="code-input-group">
        <textarea
          v-model="config.indexCode"
          placeholder="请输入指数代码，用逗号或换行分隔&#10;常用指数：&#10;• 000001.SH - 上证指数&#10;• 399001.SZ - 深证成指&#10;• 000300.SH - 沪深300&#10;• 000905.SH - 中证500&#10;• 399006.SZ - 创业板指"
          class="code-textarea"
          rows="5"
          @input="onCodeInput"
        ></textarea>

        <!-- 常用指数快捷选择 -->
        <div class="quick-select">
          <span class="quick-label">快捷选择：</span>
          <button
            v-for="preset in commonIndexes"
            :key="preset.code"
            class="quick-btn"
            :class="{ selected: isIndexSelected(preset.code) }"
            @click="toggleIndex(preset.code)"
            :title="preset.name"
          >
            {{ preset.label }}
          </button>
        </div>
      </div>

      <!-- 预览选中的指数 -->
      <div v-if="selectedIndexes.length > 0" class="selected-preview">
        <div class="preview-header">
          <span>已选择 {{ selectedIndexes.length }} 个指数</span>
          <button class="clear-btn" @click="clearIndexes">清空</button>
        </div>
        <div class="preview-list">
          <div v-for="idx in selectedIndexes" :key="idx.code" class="preview-item">
            <span class="index-code">{{ idx.code }}</span>
            <span class="index-name">{{ idx.name || '加载中...' }}</span>
            <button class="remove-btn" @click="removeIndex(idx.code)">×</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 指数预览卡片（类似股票选择节点） -->
    <div class="config-section" v-if="previewIndexes.length > 0">
      <h4 class="section-title">指数行情预览</h4>
      <div class="index-preview-grid">
        <div v-for="index in previewIndexes.slice(0, 5)" :key="index.code" class="index-preview-card">
          <div class="index-info">
            <h5 class="index-name">{{ index.name }}</h5>
            <span class="index-code">{{ index.code }}</span>
          </div>
          <div v-if="index.latestPrice" class="index-price">
            <span class="price" :class="{ positive: index.change >= 0, negative: index.change < 0 }">
              {{ index.latestPrice }}
            </span>
            <span class="change" :class="{ positive: index.change >= 0, negative: index.change < 0 }">
              {{ index.change >= 0 ? '+' : '' }}{{ index.change }}%
            </span>
          </div>
          <div v-else class="loading-placeholder">
            数据加载中...
          </div>
        </div>
      </div>
    </div>

    <!-- 时间范围 -->
    <div class="config-section">
      <h4 class="section-title">时间范围</h4>
      <div class="time-presets">
        <button
          v-for="preset in timePresets"
          :key="preset.value"
          class="preset-btn"
          :class="{ active: config.timeRange === preset.value }"
          @click="selectTimeRange(preset)"
        >
          {{ preset.label }}
        </button>
      </div>
      <div class="custom-range">
        <div class="range-inputs">
          <div class="range-input-group">
            <label>开始日期：</label>
            <input
              type="date"
              v-model="config.startDate"
              class="date-input"
              :max="config.endDate || today"
            />
          </div>
          <div class="range-input-group">
            <label>结束日期：</label>
            <input
              type="date"
              v-model="config.endDate"
              class="date-input"
              :min="config.startDate"
              :max="today"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 数据频率 -->
    <div class="config-section">
      <h4 class="section-title">数据频率 (支持多选)</h4>
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

    <!-- 数据获取进度 -->
    <div class="config-section" v-if="isLoadingData">
      <h4 class="section-title">数据获取中...</h4>
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="progress-text">
          正在获取 {{ loadingCurrent }}/{{ loadingTotal }} 个指数的数据
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
            <font-awesome-icon icon="chart-area" />
          </div>
          <div class="report-content">
            <div class="report-label">指数数量</div>
            <div class="report-value">{{ dataReport.totalIndexes }}</div>
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
            <div class="report-value">{{ dataReport.successCount }}/{{ dataReport.totalIndexes }} 成功</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { timeRangeSyncService, timeRangeSyncState, formatDateToLocal, calculateDateFromRange } from '../../utils/timeRangeSync'
import { getBatchStockNames } from '../../api/modules/data'
import { ElMessage } from 'element-plus'

// 常用指数预设
const commonIndexes = [
  { code: '000001.SH', label: '上证指数', name: '上证指数' },
  { code: '399001.SZ', label: '深证成指', name: '深证成指' },
  { code: '000300.SH', label: '沪深300', name: '沪深300' },
  { code: '000905.SH', label: '中证500', name: '中证500' },
  { code: '000852.SH', label: '中证1000', name: '中证1000' },
  { code: '399006.SZ', label: '创业板指', name: '创业板指' },
  { code: '399102.SZ', label: '创业板综', name: '创业板综' },
  { code: '000016.SH', label: '上证180', name: '上证180' },
  { code: '000688.SH', label: '上证380', name: '上证380' },
  { code: '399303.SZ', label: '国证1000', name: '国证1000' }
]

// 时间范围预设
const timePresets = [
  { label: '近1周', value: '1W', days: 7 },
  { label: '近1个月', value: '1M', days: 30 },
  { label: '近3个月', value: '3M', days: 90 },
  { label: '近6个月', value: '6M', days: 180 },
  { label: '近1年', value: '1Y', days: 365 },
  { label: '近2年', value: '2Y', days: 730 }
]

// 数据频率选项（包含分钟级数据）
const dataFrequencies = [
  { label: '5分钟', value: '5min', description: '短线交易分析，最多1周数据', intraday: true },
  { label: '15分钟', value: '15min', description: '适合日内交易，最多1个月数据', intraday: true },
  { label: '30分钟', value: '30min', description: '适合波段操作，最多2个月数据', intraday: true },
  { label: '60分钟', value: '60min', description: '适合中短期趋势，最多半年数据', intraday: true },
  { label: '日线', value: 'daily', description: '每日交易数据', intraday: false },
  { label: '周线', value: 'weekly', description: '每周交易数据', intraday: false },
  { label: '月线', value: 'monthly', description: '每月交易数据', intraday: false }
]

// 频率时间范围限制（天数）
const frequencyMaxDays: Record<string, number> = {
  '5min': 7,      // 1周
  '15min': 30,    // 1个月
  '30min': 60,    // 2个月
  '60min': 180,   // 半年
}

interface IndexInfo {
  code: string
  name: string
}

const props = defineProps<{
  modelValue: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
}>()

const config = reactive({
  ...props.modelValue,
  indexCode: props.modelValue?.indexCode || '',
  startDate: props.modelValue?.startDate || '',
  endDate: props.modelValue?.endDate || '',
  timeRange: props.modelValue?.timeRange || '1Y',  // 默认近1年
  frequency: props.modelValue?.frequency || 'daily',
  // 兼容旧的单频率配置,转换为数组
  frequencies: props.modelValue?.frequencies || (props.modelValue?.frequency ? [props.modelValue.frequency] : ['daily'])
})

// 多频率选择的响应式数组
const selectedFrequencies = ref<string[]>(config.frequencies || ['daily'])

// 计算是否选中了分钟级频率
const hasIntradayFrequency = computed(() => {
  return selectedFrequencies.value.some(freq =>
    freq === '5min' || freq === '15min' || freq === '30min' || freq === '60min'
  )
})

// 监听频率选择变化,同步到config
watch(selectedFrequencies, (newFrequencies, oldFrequencies) => {
  console.log(`[指数选择节点] selectedFrequencies 变化:`, newFrequencies)
  config.frequencies = newFrequencies
  // 为了向后兼容,同时更新frequency字段(使用第一个选中的频率)
  config.frequency = newFrequencies.length > 0 ? newFrequencies[0] : 'daily'

  // 同步频率到联动服务
  if (isInitialized) {
    console.log(`[指数选择节点] 频率变化,同步到联动服务:`, newFrequencies)
    timeRangeSyncService.updateIndexFrequencies(newFrequencies)
  }
  // 注意：不需要手动 emit，watch(config, ...) 会自动触发

  // 检查是否从非分钟级切换到分钟级，自动调整时间范围
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

// 时间范围联动状态
const syncState = timeRangeSyncState
let unsubscribeSync: (() => void) | null = null
let unsubscribeFrequencySync: (() => void) | null = null
let isInitialized = false  // 标记是否已完成初始化

// 处理时间范围变化（同步到联动服务）
const handleTimeRangeChange = () => {
  // 只在初始化完成后才同步
  if (!isInitialized) return

  // 更新联动服务中的指数节点时间范围
  timeRangeSyncService.updateIndexTimeRange({
    timeRange: config.timeRange,
    startDate: config.startDate,
    endDate: config.endDate
  })
}

// 选中的指数列表
const selectedIndexes = ref<IndexInfo[]>([])

// 指数预览数据（类似股票选择节点的 previewStocks）
const previewIndexes = ref<any[]>([])

// 数据加载状态 - 必须在计算属性之前定义
const isLoadingData = ref(false)
const loadingProgress = ref(0)
const loadingCurrent = ref(0)
const loadingTotal = ref(0)

// 数据报告 - 使用独立响应式变量以确保计算属性能正确追踪
const totalIndexes = ref(0)
const totalDataPoints = ref(0)
const successCount = ref(0)
const allSuccess = ref(false)

// 计算属性：是否显示数据报告
const showDataReport = computed(() => {
  const shouldShow = !isLoadingData.value && totalIndexes.value > 0
  console.log('[IndexSelectionNode] showDataReport:', {
    isLoadingData: isLoadingData.value,
    totalIndexes: totalIndexes.value,
    shouldShow
  })
  return shouldShow
})

// 为了兼容模板，保留 dataReport 作为计算属性
const dataReport = computed(() => ({
  totalIndexes: totalIndexes.value,
  totalDataPoints: totalDataPoints.value,
  successCount: successCount.value,
  allSuccess: allSuccess.value
}))

// 解析指数代码
const parseIndexCodes = (codes: string): string[] => {
  if (!codes) return []
  return codes
    .split(/[,，\n]/)
    .map(code => code.trim())
    .filter(code => code)
}

// 检查指数是否已选中
const isIndexSelected = (code: string): boolean => {
  const codes = parseIndexCodes(config.indexCode)
  return codes.includes(code)
}

// 切换指数选择状态
const toggleIndex = (code: string) => {
  const codes = parseIndexCodes(config.indexCode)
  const index = codes.indexOf(code)

  if (index >= 0) {
    // 已选中，移除
    codes.splice(index, 1)
  } else {
    // 未选中，添加
    codes.push(code)
  }

  config.indexCode = codes.join(',')
  updateSelectedIndexes()
}

// 移除指数
const removeIndex = (code: string) => {
  const codes = parseIndexCodes(config.indexCode)
  const index = codes.indexOf(code)
  if (index >= 0) {
    codes.splice(index, 1)
    config.indexCode = codes.join(',')
    updateSelectedIndexes()
  }
}

// 清空所有指数
const clearIndexes = () => {
  config.indexCode = ''
  selectedIndexes.value = []
}

// 更新选中的指数列表（获取名称）
const updateSelectedIndexes = async () => {
  const codes = parseIndexCodes(config.indexCode)

  if (codes.length === 0) {
    selectedIndexes.value = []
    return
  }

  // 从预设列表中获取名称
  const results: IndexInfo[] = []
  for (const code of codes) {
    const preset = commonIndexes.find(idx => idx.code === code)
    results.push({
      code,
      name: preset?.name || code
    })
  }

  selectedIndexes.value = results
}

// 选择时间范围
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

  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(endDate.getDate() - preset.days)

  config.endDate = formatDateToLocal(endDate)
  config.startDate = formatDateToLocal(startDate)

  // 同步到联动服务
  handleTimeRangeChange()
}

// 🔧 新增：格式化日期范围显示（只显示日期部分）
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

// 今天日期
const today = computed(() => {
  const date = new Date()
  return formatDateToLocal(date)
})

// 代码输入处理
const onCodeInput = () => {
  updateSelectedIndexes()
}

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
  console.log('[IndexSelectionNode] updateDataReport, previewIndexes:', previewIndexes.value.length)

  if (previewIndexes.value.length === 0) {
    totalIndexes.value = 0
    totalDataPoints.value = 0
    successCount.value = 0
    allSuccess.value = false
    return
  }

  const indexesCount = previewIndexes.value.length
  let dataPoints = 0
  let successes = 0

  previewIndexes.value.forEach(index => {
    if (index.data && index.data.length > 0) {
      dataPoints += index.data.length
      successes++
    }
  })

  totalIndexes.value = indexesCount
  totalDataPoints.value = dataPoints
  successCount.value = successes
  allSuccess.value = successes === indexesCount

  console.log('[IndexSelectionNode] 数据报告已更新:', {
    totalIndexes: totalIndexes.value,
    totalDataPoints: totalDataPoints.value,
    showDataReport: showDataReport.value
  })
}

/**
 * 添加市场后缀
 */
const addMarketSuffix = (code: string): string => {
  if (code.endsWith('.SZ') || code.endsWith('.SH')) {
    return code
  }
  if (code.startsWith('6') || code.startsWith('000') || code.startsWith('001')) {
    return `${code}.SH`
  } else if (code.startsWith('399') || code.startsWith('200')) {
    return `${code}.SZ`
  }
  return code
}

/**
 * 获取指数数据（类似股票选择节点的 validateStockCodes）
 */
const fetchIndexDataForPreview = async () => {
  const indexCodes = parseIndexCodes(config.indexCode)

  if (indexCodes.length === 0) {
    previewIndexes.value = []
    updateDataReport()
    return
  }

  // 显示加载状态
  isLoadingData.value = true
  loadingCurrent.value = 0
  loadingTotal.value = indexCodes.length
  loadingProgress.value = 0

  // 格式化指数代码，添加市场后缀
  const formattedCodes = indexCodes.map(addMarketSuffix)

  try {
    // 获取指数名称
    let nameMap: Record<string, string> = {}
    try {
      const nameResponse = await getBatchStockNames(formattedCodes)
      nameMap = nameResponse.success ? nameResponse.data : {}
    } catch (error) {
      console.warn('[IndexSelectionNode] 获取指数名称失败:', error)
    }

    // 准备API请求参数
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8010/api/v1'
    const startDate = config.startDate || (() => {
      const date = new Date()
      date.setFullYear(date.getFullYear() - 1)
      return date.toISOString().split('T')[0]
    })()
    const endDate = config.endDate || new Date().toISOString().split('T')[0]

    // 关键修复：优先使用多频率配置的第一个频率，向后兼容单频率配置
    let frequency = 'daily'
    if (config.frequencies && Array.isArray(config.frequencies) && config.frequencies.length > 0) {
      frequency = config.frequencies[0]
      console.log('[IndexSelectionNode] Config.vue 预览使用多频率配置的第一个频率:', frequency)
    } else if (config.frequency) {
      frequency = config.frequency
      console.log('[IndexSelectionNode] Config.vue 预览使用单频率配置:', frequency)
    } else {
      console.log('[IndexSelectionNode] Config.vue 预览没有频率信息，使用默认值 daily')
    }
    console.log('[IndexSelectionNode] Config.vue 预览最终使用的频率:', frequency)

    const url = `${baseURL}/data/query`
    const requestParams = {
      symbols: formattedCodes,
      fields: ['open', 'high', 'low', 'close', 'volume'],
      start_date: startDate,
      end_date: endDate,
      frequency: frequency
    }

    // 构建URL查询参数
    const queryParams = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      frequency: frequency
    })
    const fullUrl = `${url}?${queryParams.toString()}`

    // 发送API请求
    const response = await fetch(fullUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestParams),
      signal: AbortSignal.timeout(30000)
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const result = await response.json()

    if (!result.success) {
      throw new Error(result.error || result.detail || result.message || 'API返回失败')
    }

    // 处理返回的数据
    const results: any[] = []
    for (let i = 0; i < indexCodes.length; i++) {
      const originalCode = indexCodes[i]
      const formattedCode = formattedCodes[i]
      const indexData = result.data?.[formattedCode]

      loadingCurrent.value = i + 1
      loadingProgress.value = Math.round(((i + 1) / indexCodes.length) * 100)

      const indexName = nameMap[formattedCode] || commonIndexes.find(idx => idx.code === originalCode)?.name || originalCode

      if (indexData && indexData.dates && indexData.dates.length > 0) {
        const fields = indexData.fields || {}
        const closePrices = fields.close || []

        // 获取最新价格和涨跌幅
        let latestPrice = '--'
        let change = 0

        if (closePrices.length > 0) {
          latestPrice = parseFloat(closePrices[closePrices.length - 1]).toFixed(2)

          if (closePrices.length > 1) {
            const previousClose = parseFloat(closePrices[closePrices.length - 2])
            const currentPrice = parseFloat(latestPrice)
            change = ((currentPrice - previousClose) / previousClose) * 100
          }
        }

        results.push({
          code: originalCode,
          name: indexName,
          latestPrice: latestPrice !== '--' ? parseFloat(latestPrice) : null,
          change: parseFloat(change.toFixed(2)),
          data: indexData.dates, // 保存日期数据
          dataLength: indexData.dates.length
        })
      } else {
        // 数据获取失败
        results.push({
          code: originalCode,
          name: indexName,
          latestPrice: null,
          change: 0,
          data: [],
          dataLength: 0
        })
      }
    }

    // 更新预览数据
    previewIndexes.value = results

    // 显示成功消息
    const successCount = results.filter(r => r.data && r.data.length > 0).length
    if (successCount > 0) {
      ElMessage({
        message: `成功获取 ${successCount}/${indexCodes.length} 个指数的数据`,
        type: 'success',
        duration: 3000
      })
    } else {
      ElMessage({
        message: '未能获取指数数据，请检查指数代码',
        type: 'warning',
        duration: 3000
      })
    }
  } catch (error) {
    console.error('[IndexSelectionNode] 获取指数数据失败:', error)
    ElMessage({
      message: `获取指数数据失败: ${(error as Error).message}`,
      type: 'error',
      duration: 3000
    })

    // 设置空数据
    previewIndexes.value = indexCodes.map(code => ({
      code,
      name: commonIndexes.find(idx => idx.code === code)?.name || code,
      latestPrice: null,
      change: 0,
      data: [],
      dataLength: 0
    }))

  } finally {
    isLoadingData.value = false
    // 在加载完成后更新数据报告
    updateDataReport()
  }
}

// 防抖函数，避免频繁请求
let debounceTimer: ReturnType<typeof setTimeout> | null = null
const debouncedFetchIndexData = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  debounceTimer = setTimeout(() => {
    fetchIndexDataForPreview()
  }, 800) // 800ms延迟
}

// 监听配置变化
watch(config, () => {
  emit('update:modelValue', { ...config })
}, { deep: true })

// 监听指数代码变化，触发数据获取
watch(() => config.indexCode, (newCode, oldCode) => {
  if (newCode !== oldCode && newCode) {
    console.log('[IndexSelectionNode] 指数代码变化，触发数据获取:', newCode)
    debouncedFetchIndexData()
  } else if (!newCode) {
    // 清空时也要清除预览数据
    previewIndexes.value = []
    updateDataReport()
  }
})

// 监听时间范围或频率变化，重新获取数据
watch([() => config.startDate, () => config.endDate, () => config.frequency], () => {
  if (config.indexCode && config.startDate && config.endDate) {
    console.log('[IndexSelectionNode] 时间范围或频率变化，重新获取数据')
    debouncedFetchIndexData()
  }
})

// 初始化
onMounted(() => {
  // 如果没有预选指数，默认只选中上证指数
  if (!config.indexCode || config.indexCode.trim() === '') {
    config.indexCode = '000001.SH'
  }

  // 解析已有代码
  updateSelectedIndexes()

  // 初始化时获取指数数据
  if (config.indexCode) {
    console.log('[IndexSelectionNode] 初始化，获取指数数据')
    fetchIndexDataForPreview()
  }

  // 订阅时间范围联动
  unsubscribeSync = timeRangeSyncService.subscribe((syncedConfig) => {
    console.log(`[指数选择节点] 收到时间范围同步通知:`, syncedConfig)
    console.log(`[指数选择节点] 主节点: ${syncState.masterNode}, isInitialized: ${isInitialized}`)
    // 只有当主节点是股票节点时才应用同步的配置
    // 避免循环更新
    if (syncState.masterNode === 'stock' && isInitialized) {
      console.log(`[指数选择节点] 应用同步的时间范围`)
      // 更新本地配置
      config.timeRange = syncedConfig.timeRange
      config.startDate = syncedConfig.startDate
      config.endDate = syncedConfig.endDate

      // 立即触发emit,让父组件知道配置已更新
      emit('update:modelValue', { ...config })
    } else {
      console.log(`[指数选择节点] 跳过同步 (主节点: ${syncState.masterNode}, isInitialized: ${isInitialized})`)
    }
  })

  // 订阅频率联动
  unsubscribeFrequencySync = timeRangeSyncService.subscribeFrequencies((syncedFrequencies) => {
    console.log(`[指数选择节点] 收到频率同步通知:`, syncedFrequencies)
    console.log(`[指数选择节点] 主节点: ${syncState.masterNode}, isInitialized: ${isInitialized}`)
    // 只有当主节点是股票节点时才应用同步的频率
    if (syncState.masterNode === 'stock' && isInitialized) {
      console.log(`[指数选择节点] 应用同步的频率`)
      // 更新本地配置
      selectedFrequencies.value = [...syncedFrequencies]
      config.frequencies = [...syncedFrequencies]
      config.frequency = syncedFrequencies.length > 0 ? syncedFrequencies[0] : 'daily'
      emit('update:modelValue', { ...config })
    } else {
      console.log(`[指数选择节点] 跳过频率同步 (主节点: ${syncState.masterNode}, isInitialized: ${isInitialized})`)
    }
  })

  // 检查是否需要应用联动的时间范围
  // 如果股票节点已经设置了时间范围,应用它
  const state = timeRangeSyncService.getState()
  if (state.masterNode === 'stock' && state.syncedTimeRange.startDate) {
    config.timeRange = state.syncedTimeRange.timeRange
    config.startDate = state.syncedTimeRange.startDate
    config.endDate = state.syncedTimeRange.endDate
  } else if (!config.startDate || !config.endDate) {
    // 只有在没有设置时间范围时才使用默认值
    // 检查是否选择了分钟级频率，如果有，使用更短的默认时间范围
    const initialFrequencies = selectedFrequencies.value
    const hasInitialMinuteFrequency = initialFrequencies.some(f =>
      f === '5min' || f === '15min' || f === '30min' || f === '60min'
    )

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
          selectTimeRange(matchingPreset)
          console.log(`[指数选择节点] 初始化检测到分钟级频率，使用预设时间范围: ${matchingPreset.label}`)
        } else {
          // 使用自定义范围
          const endDate = new Date()
          const startDate = new Date(endDate)
          startDate.setDate(endDate.getDate() - minMaxDays)
          config.timeRange = 'custom'
          config.startDate = formatDateToLocal(startDate)
          config.endDate = formatDateToLocal(endDate)
          console.log(`[指数选择节点] 初始化检测到分钟级频率，使用自定义时间范围: ${minMaxDays}天`)
        }
      } else {
        // 没有找到限制，使用默认1年
        selectTimeRange(timePresets.find(p => p.value === '1Y') || timePresets[4])
      }
    } else {
      // 非分钟级频率，使用默认1年
      selectTimeRange(timePresets.find(p => p.value === '1Y') || timePresets[4])
    }
  }

  // 检查是否需要应用联动的频率
  if (state.masterNode === 'stock' && state.syncedFrequencies) {
    console.log(`[指数选择节点] 检测到股票节点已设置频率,应用联动:`, state.syncedFrequencies)
    selectedFrequencies.value = [...state.syncedFrequencies]
    config.frequencies = [...state.syncedFrequencies]
    config.frequency = state.syncedFrequencies.length > 0 ? state.syncedFrequencies[0] : 'daily'
  }

  // 标记初始化完成
  isInitialized = true

  // 初始化时,同步当前配置到联动服务
  if (config.startDate && config.endDate) {
    timeRangeSyncService.updateIndexTimeRange({
      timeRange: config.timeRange,
      startDate: config.startDate,
      endDate: config.endDate
    })
  }

  // 初始化时,同步频率到联动服务
  if (selectedFrequencies.value) {
    console.log(`[指数选择节点] 初始化频率同步:`, selectedFrequencies.value)
    timeRangeSyncService.updateIndexFrequencies(selectedFrequencies.value)
  }
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
</script>

<style lang="scss" scoped>
.index-selection-config {
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
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: 8px;
}

.code-input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.code-textarea {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  resize: vertical;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #8b5cf6;
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
}

.quick-select {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.quick-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.quick-btn {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.9);
  }

  &.selected {
    background: rgba(139, 92, 246, 0.2);
    border-color: #8b5cf6;
    color: #8b5cf6;
  }
}

.selected-preview {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 10px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.clear-btn {
  padding: 2px 8px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.5);
    color: #ef4444;
  }
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 150px;
  overflow-y: auto;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  font-size: 12px;
}

.index-code {
  font-family: 'Consolas', 'Monaco', monospace;
  color: #8b5cf6;
  font-weight: 500;
}

.index-name {
  color: rgba(255, 255, 255, 0.7);
  flex: 1;
}

.remove-btn {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  transition: all 0.2s;

  &:hover {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }
}

.time-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-btn {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.9);
  }

  &.active {
    background: #8b5cf6;
    border-color: #8b5cf6;
    color: #fff;
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

  small {
    margin-left: auto;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
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

// 复选框选项样式
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

  small {
    margin-left: auto;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
  }
}

// 指数预览卡片样式
.index-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.index-preview-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(139, 92, 246, 0.3);
  }

  .index-info {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .index-name {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.9);
    }

    .index-code {
      font-size: 12px;
      color: #8b5cf6;
      font-family: 'Consolas', 'Monaco', monospace;
    }
  }

  .index-price {
    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: flex-end;

    .price {
      font-size: 16px;
      font-weight: 600;

      &.positive {
        color: #ef4444;
      }

      &.negative {
        color: #22c55e;
      }
    }

    .change {
      font-size: 12px;

      &.positive {
        color: #ef4444;
      }

      &.negative {
        color: #22c55e;
      }
    }
  }

  .loading-placeholder {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    text-align: center;
    padding: 8px 0;
  }
}
</style>
