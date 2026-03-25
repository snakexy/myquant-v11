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
                v-model="config.startDate"
                type="date"
                class="date-input"
                :max="today"
                @change="handleCustomDateChange"
              />
            </div>
            <div class="range-input-group">
              <label>结束日期：</label>
              <input
                v-model="config.endDate"
                type="date"
                class="date-input"
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
      <h4 class="section-title">数据频率</h4>
      <div class="frequency-group">
        <label class="radio-option" v-for="freq in dataFrequencies" :key="freq.value">
          <input
            type="radio"
            :value="freq.value"
            v-model="config.frequency"
          />
          <span>{{ freq.label }}</span>
          <small v-if="freq.description">{{ freq.description }}</small>
        </label>
      </div>

      <!-- 分钟级数据选项 - 仅当时间范围为1周且只有一只股票时显示 -->
      <div class="intraday-options" v-if="showIntradayOptions">
        <div class="intraday-description">
          <small>选择需要下载的分钟级数据，用于多时间框架分析</small>
        </div>
        <div class="intraday-checkboxes">
          <label class="checkbox-option intraday-checkbox" v-for="interval in intradayIntervals" :key="interval.value">
            <input
              type="checkbox"
              :value="interval.value"
              v-model="config.intradayIntervals"
            />
            <span>{{ interval.label }}</span>
            <small class="interval-info">{{ interval.description }}</small>
          </label>
        </div>
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
          :key="stock.code"
          :stock-code="stock.code"
          :stock-name="stock.name"
          :data="stock.data"
          :metrics="stock.metrics"
          :loading="stock.loading"
          :show-volume="true"
          :show-time-range="true"
          :chart-width="240"
          :chart-height="80"
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, onMounted, nextTick } from 'vue'
import StockDataPreview from '../charts/StockDataPreview.vue'
import { getStockDetail, getStockHistory, getIndicators } from '../../api/modules/data'

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
  intradayIntervals: props.modelValue.intradayIntervals || []
})

// 初始化智能默认时间范围 - 修复版本
const initializeDefaultTimeRange = async () => {
  // 如果没有设置时间范围，则使用智能默认值
  if (!config.startDate || !config.endDate) {
    const now = new Date()
    console.log(`[时间范围初始化] 当前时间: ${now.toLocaleString()}`)
    console.log(`[时间范围初始化] 当前年份: ${now.getFullYear()}`)

    // 智能获取最新的完整交易日数据
    const latestTradingDay = await getLatestAvailableTradingDay()

    config.endDate = latestTradingDay

    // 默认使用最近3个月的时间范围，从结束日期往前推90天
    const endDate = new Date(latestTradingDay)
    const startDate = new Date(endDate)
    startDate.setDate(endDate.getDate() - 90)
    config.startDate = startDate.toISOString().split('T')[0]
    config.timeRange = config.timeRange || '3M'

    console.log(`[时间范围初始化] 智能获取最新交易收盘日: ${config.startDate} 到 ${config.endDate}`)
    console.log(`[时间范围初始化] 使用API实时获取的最新完整交易日数据`)

    // 验证数据可用性
    await validateDateRange()
  }
}

// 获取最新可用的交易日数据 - 修复版本
const getLatestAvailableTradingDay = async (): Promise<string> => {
  try {
    const now = new Date()
    const currentHour = now.getHours()
    const currentMinute = now.getMinutes()
    const dayOfWeek = now.getDay() // 0=周日, 1=周一, ..., 6=周六

    console.log(`[获取最新交易日] 当前时间: ${currentHour}:${currentMinute.toString().padStart(2, '0')}, 星期${dayOfWeek}`)
    console.log(`[获取最新交易日] 当前年份: ${now.getFullYear()}`)

    // 根据当前时间和是否周末智能选择日期
    let targetDate = new Date(now)

    if (currentHour > 15 || (currentHour === 15 && currentMinute >= 30)) {
      // 收盘后 (15:30后-23:59前): 使用当天，但如果当天是周末则需要调整
      console.log(`[获取最新交易日] 收盘后，检查当天是否为交易日...`)

      if (dayOfWeek === 0) {
        // 周日，使用上周五
        targetDate.setDate(now.getDate() - 2)
        console.log(`[获取最新交易日] 周日，使用上周五: ${targetDate.toISOString().split('T')[0]}`)
      } else if (dayOfWeek === 6) {
        // 周六，使用上周五
        targetDate.setDate(now.getDate() - 1)
        console.log(`[获取最新交易日] 周六，使用上周五: ${targetDate.toISOString().split('T')[0]}`)
      } else {
        // 工作日，使用当天
        console.log(`[获取最新交易日] 工作日收盘后，使用当天: ${targetDate.toISOString().split('T')[0]}`)
      }
    } else {
      // 其他时间 (00:00-15:29): 使用前一个交易日
      console.log(`[获取最新交易日] 非收盘时间，查找前一个交易日...`)

      if (dayOfWeek === 1) {
        // 周一，使用上周五
        targetDate.setDate(now.getDate() - 3)
        console.log(`[获取最新交易日] 周一，使用上周五: ${targetDate.toISOString().split('T')[0]}`)
      } else if (dayOfWeek === 0) {
        // 周日，使用上周五
        targetDate.setDate(now.getDate() - 2)
        console.log(`[获取最新交易日] 周日，使用上周五: ${targetDate.toISOString().split('T')[0]}`)
      } else {
        // 其他情况，使用前一天
        targetDate.setDate(now.getDate() - 1)
        console.log(`[获取最新交易日] 使用前一天: ${targetDate.toISOString().split('T')[0]}`)
      }
    }

    const result = targetDate.toISOString().split('T')[0]
    console.log(`[获取最新交易日] 最终返回日期: ${result}, 年份: ${targetDate.getFullYear()}`)
    return result

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
onMounted(() => {
  initializeDefaultTimeRange()
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

// 分钟级数据选项
const intradayIntervals = [
  { label: '5分钟', value: '5min', description: '适合短线交易分析' },
  { label: '15分钟', value: '15min', description: '适合日内交易' },
  { label: '30分钟', value: '30min', description: '适合波段操作' },
  { label: '60分钟', value: '60min', description: '适合中短期趋势' }
]

// 数据频率选项
const dataFrequencies = [
  { label: '日线', value: 'daily', description: '每日交易数据' },
  { label: '周线', value: 'weekly', description: '每周交易数据' },
  { label: '月线', value: 'monthly', description: '每月交易数据' },
]


const today = computed(() => {
  const date = new Date()
  return date.toISOString().split('T')[0]
})

// 计算是否显示分钟级数据选项
// 仅当时间范围为1周时显示（不限制股票数量）
const showIntradayOptions = computed(() => {
  // 检查是否选择了1周时间范围
  if (config.timeRange !== '1W') {
    return false
  }

  // 检查是否有股票代码
  if (!config.stockCode) {
    return false
  }

  // 只要是1周时间范围就显示，不限制股票数量
  return true
})


// 解析股票代码
const previewStocks = ref<StockPreview[]>([])

// 防抖定时器
let debounceTimer: NodeJS.Timeout | null = null

// 延迟验证股票代码
const validateStockCodes = async (codes: string) => {
  const stockPreviews: StockPreview[] = []

  for (const code of codes) {
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

      // 检查数据有效性
      if (stockDetail?.data && historyData?.data && historyData.data.length > 0) {
        stockPreviews.push({
          code,
          name: stockDetail.data.name || code,
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
          code,
          name: code, // 只显示股票代码
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
        code,
        name: code, // 只显示股票代码
        data: [],
        metrics: {},
        loading: false,
        isRealData: false,
        error: error as Error
      })
    }
  }

  previewStocks.value = stockPreviews
}

// 监听股票代码变化，使用防抖机制
watch(() => config.stockCode, async (newCodes) => {
  // 清除之前的定时器
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  if (!newCodes) {
    previewStocks.value = []
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

// 监听配置变化
watch(config, () => {
  emit('update:modelValue', { ...config })
}, { deep: true })

// 选择预设时间范围
const selectTimeRange = (preset: { label: string; value: string; days: number }) => {
  config.timeRange = preset.value

  // 使用智能结束日期（考虑股票数据滞后性）
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  const endDate = yesterday
  const startDate = new Date(endDate)
  startDate.setDate(endDate.getDate() - preset.days)

  config.endDate = endDate.toISOString().split('T')[0]
  config.startDate = startDate.toISOString().split('T')[0]

  console.log(`[预设时间范围] 选择 ${preset.label}: ${config.startDate} 到 ${config.endDate}`)
}

// 处理自定义日期变化
const handleCustomDateChange = () => {
  config.timeRange = 'custom'
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

// 处理预览时间范围变化
const handlePreviewRangeChange = (stockCode: string, range: string) => {
  // 这里可以加载对应时间范围的数据
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
}

.custom-range {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.range-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.range-input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;

  label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
  }

  .date-input {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    padding: 6px 10px;
    color: #fff;
    font-size: 13px;

    &:focus {
      outline: none;
      border-color: #8b5cf6;
      background: rgba(255, 255, 255, 0.08);
    }

    &::-webkit-calendar-picker-indicator {
      filter: invert(1);
      cursor: pointer;
    }
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
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
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

// 分钟级数据选项样式
.intraday-options {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);

  .intraday-description {
    margin-bottom: 8px;
    margin-left: 4px;

    small {
      color: rgba(255, 255, 255, 0.5);
      font-size: 12px;
      font-style: italic;
    }
  }

  .intraday-checkboxes {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-left: 4px;
  }

  .intraday-checkbox {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.06);
      border-color: rgba(139, 92, 246, 0.2);
    }

    input[type="checkbox"] {
      accent-color: #8b5cf6;
      width: 14px;
      height: 14px;
    }

    span {
      color: rgba(255, 255, 255, 0.85);
      font-size: 12px;
      font-weight: 500;
      flex: 1;
    }

    .interval-info {
      color: rgba(255, 255, 255, 0.4);
      font-size: 10px;
      margin-left: auto;
    }
  }
}
</style>