<template>
  <div class="data-source-overview">
    <div class="overview-header">
      <h3>📊 数据源概览</h3>
    </div>

    <!-- 检测前提示 -->
    <div v-if="!hasDetected" class="no-data-tip">
      <font-awesome-icon icon="info-circle" size="3x" style="color: rgba(255, 255, 255, 0.3);" />
      <p>请先点击上方"检测连接"按钮扫描通达信数据源</p>
    </div>

    <!-- 统计卡片 -->
    <div v-else class="overview-cards">
      <!-- 总体统计 -->
      <div class="card-section">
        <div class="section-title">📦 数据概况</div>
        <div class="cards-grid">
          <div class="overview-card primary">
            <div class="card-icon">
              <font-awesome-icon icon="database" />
            </div>
            <div class="card-content">
              <div class="card-value">{{ formatNumber(stats.totalStocks) }}</div>
              <div class="card-label">标的总数</div>
            </div>
          </div>

          <div class="overview-card success">
            <div class="card-icon">
              <font-awesome-icon icon="calendar-alt" />
            </div>
            <div class="card-content">
              <div class="card-value">{{ stats.dateRange }}</div>
              <div class="card-label">数据时间范围</div>
            </div>
          </div>

          <div class="overview-card warning">
            <div class="card-icon">
              <font-awesome-icon icon="clock" />
            </div>
            <div class="card-content">
              <div class="card-value">{{ stats.lastUpdate }}</div>
              <div class="card-label">最后更新</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分频率统计 -->
      <div class="card-section">
        <div class="section-title">📈 各频率数据统计</div>
        <div class="frequency-cards">
          <div
            v-for="freq in frequencyStats"
            :key="freq.value"
            :class="['freq-card', {
              available: freq.available,
              'available-no-stats': freq.available && !freq.showStats
            }]"
          >
            <div class="freq-icon">
              <font-awesome-icon :icon="freq.icon" />
            </div>
            <div class="freq-info">
              <div class="freq-label">{{ freq.label }}</div>
              <div class="freq-status-wrapper">
                <div class="freq-status" :class="{ active: freq.available }">
                  <font-awesome-icon :icon="freq.available ? 'check-circle' : 'times-circle'" />
                  {{ freq.available ? '可用' : '不可用' }}
                </div>
                <div v-if="freq.available && freq.dateRange" class="freq-date-range">
                  {{ freq.dateRange }}
                </div>
              </div>
            </div>
            <div v-if="freq.showStats" class="freq-stats">
              <div class="freq-stat">
                <span class="stat-num">{{ formatNumber(freq.stockCount) }}</span>
                <span class="stat-text">只股票</span>
              </div>
              <div class="freq-stat">
                <span class="stat-num">{{ formatNumber(freq.recordCount) }}</span>
                <span class="stat-text">条记录</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据完整性 - 按证券类型分标签页 -->
      <div class="card-section">
        <div class="section-title">✅ 数据完整性</div>

        <!-- 时间范围控制栏 -->
        <div class="timeline-control-section">
          <!-- 起始日期选择器 -->
          <div class="timeline-start-picker">
            <el-date-picker
              v-model="startDatePicker"
              type="month"
              size="small"
              placeholder="开始"
              format="YYYY-MM"
              value-format="YYYY-MM"
              style="width: 100px"
              :clearable="false"
              :teleported="true"
              @change="onStartDateChange"
            />
          </div>

          <!-- 快速预设 -->
          <div class="timeline-controls">
            <el-select
              v-model="timelineRangePreset"
              size="small"
              style="width: 100px; --el-input-bg-color: rgba(102, 126, 234, 0.08); --el-input-border-color: rgba(102, 126, 234, 0.3); --el-input-text-color: rgba(255, 255, 255, 0.9);"
              popper-class="dark-select-dropdown"
              :teleported="true"
              @change="applyTimelinePreset"
            >
              <el-option label="近1年" value="1"></el-option>
              <el-option label="近3年" value="3"></el-option>
              <el-option label="近5年" value="5"></el-option>
              <el-option label="全部" value="all"></el-option>
            </el-select>
          </div>

          <!-- 结束日期选择器 -->
          <div class="timeline-end-picker">
            <el-date-picker
              v-model="endDatePicker"
              type="month"
              size="small"
              placeholder="结束"
              format="YYYY-MM"
              value-format="YYYY-MM"
              style="width: 100px"
              :clearable="false"
              :teleported="true"
              @change="onEndDateChange"
            />
          </div>
        </div>

        <!-- 标签页 -->
        <el-tabs v-model="activeSecurityType" class="security-type-tabs">
          <!-- 股票标签 -->
          <el-tab-pane label="股票" name="stock">
            <template #label>
              <span class="tab-label">
                <font-awesome-icon icon="chart-line" />
                股票
                <span class="tab-count">{{ formatNumber(tdxInfo?.stockCounts?.day || 0) }}</span>
              </span>
            </template>
            <div class="tab-content">
              <div v-if="loadingTypeData" class="loading-state">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在加载股票数据...</span>
              </div>
              <div v-else-if="typeError" class="error-state">
                <font-awesome-icon icon="exclamation-triangle" />
                <span>{{ typeError }}</span>
              </div>
              <div v-else class="type-timelines">
                <!-- 时间标尺 -->
                <div class="scale-marks-container">
                  <div class="scale-marks">
                    <div
                      v-for="mark in timelineMarks"
                      :key="mark.label"
                      :class="['scale-mark', mark.type]"
                      :style="{ left: mark.position + '%' }"
                    >
                      {{ mark.label }}
                    </div>
                  </div>
                </div>

                <!-- 日线数据时间条 -->
                <div class="timeline-row">
                  <div class="timeline-header">
                    <span class="timeline-title">日线数据</span>
                    <span class="timeline-percent" :style="{ color: getCompletenessColor(getTypeData('stock', 'day')?.completeness || 0) }">
                      {{ getTypeData('stock', 'day')?.completeness || 0 }}%
                    </span>
                  </div>
                  <div class="timeline-bar-container">
                    <div class="timeline-bar">
                      <template v-for="(segment, idx) in getTypeSegments('stock', 'day')" :key="idx">
                        <div
                          :class="['timeline-segment', { 'has-data': segment.hasData }]"
                          :style="{
                            left: segment.left + '%',
                            width: segment.width + '%'
                          }"
                          :title="`${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)}`"
                        ></div>
                      </template>
                    </div>
                    <div class="timeline-range">{{ getTypeData('stock', 'day')?.date_range || '-' }}</div>
                  </div>
                </div>

                <!-- 5分钟数据时间条 -->
                <div class="timeline-row">
                  <div class="timeline-header">
                    <span class="timeline-title">5分钟数据</span>
                    <span class="timeline-percent" :style="{ color: getCompletenessColor(getTypeData('stock', '5min')?.completeness || 0) }">
                      {{ getTypeData('stock', '5min')?.completeness || 0 }}%
                    </span>
                  </div>
                  <div class="timeline-bar-container">
                    <div class="timeline-bar">
                      <template v-for="(segment, idx) in getTypeSegments('stock', '5min')" :key="idx">
                        <div
                          :class="['timeline-segment', { 'has-data': segment.hasData, 'is-5min': true }]"
                          :style="{
                            left: segment.left + '%',
                            width: segment.width + '%'
                          }"
                          :title="`${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)}`"
                        ></div>
                      </template>
                    </div>
                    <div class="timeline-range">{{ getTypeData('stock', '5min')?.date_range || '-' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 基金标签 -->
          <el-tab-pane label="基金" name="fund">
            <template #label>
              <span class="tab-label">
                <font-awesome-icon icon="piggy-bank" />
                基金
                <span class="tab-count">{{ formatNumber(tdxInfo?.fundCounts?.day || 0) }}</span>
              </span>
            </template>
            <div class="tab-content">
              <div v-if="loadingTypeData" class="loading-state">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在加载基金数据...</span>
              </div>
              <div v-else-if="typeError" class="error-state">
                <font-awesome-icon icon="exclamation-triangle" />
                <span>{{ typeError }}</span>
              </div>
              <div v-else class="type-timelines">
                <!-- 时间标尺 -->
                <div class="scale-marks-container">
                  <div class="scale-marks">
                    <div
                      v-for="mark in timelineMarks"
                      :key="mark.label"
                      :class="['scale-mark', mark.type]"
                      :style="{ left: mark.position + '%' }"
                    >
                      {{ mark.label }}
                    </div>
                  </div>
                </div>

                <!-- 日线数据时间条 -->
                <div class="timeline-row">
                  <div class="timeline-header">
                    <span class="timeline-title">日线数据</span>
                    <span class="timeline-percent" :style="{ color: getCompletenessColor(getTypeData('fund', 'day')?.completeness || 0) }">
                      {{ getTypeData('fund', 'day')?.completeness || 0 }}%
                    </span>
                  </div>
                  <div class="timeline-bar-container">
                    <div class="timeline-bar">
                      <template v-for="(segment, idx) in getTypeSegments('fund', 'day')" :key="idx">
                        <div
                          :class="['timeline-segment', { 'has-data': segment.hasData }]"
                          :style="{
                            left: segment.left + '%',
                            width: segment.width + '%'
                          }"
                          :title="`${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)}`"
                        ></div>
                      </template>
                    </div>
                    <div class="timeline-range">{{ getTypeData('fund', 'day')?.date_range || '-' }}</div>
                  </div>
                </div>

                <!-- 5分钟数据时间条 -->
                <div class="timeline-row">
                  <div class="timeline-header">
                    <span class="timeline-title">5分钟数据</span>
                    <span class="timeline-percent" :style="{ color: getCompletenessColor(getTypeData('fund', '5min')?.completeness || 0) }">
                      {{ getTypeData('fund', '5min')?.completeness || 0 }}%
                    </span>
                  </div>
                  <div class="timeline-bar-container">
                    <div class="timeline-bar">
                      <template v-for="(segment, idx) in getTypeSegments('fund', '5min')" :key="idx">
                        <div
                          :class="['timeline-segment', { 'has-data': segment.hasData, 'is-5min': true }]"
                          :style="{
                            left: segment.left + '%',
                            width: segment.width + '%'
                          }"
                          :title="`${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)}`"
                        ></div>
                      </template>
                    </div>
                    <div class="timeline-range">{{ getTypeData('fund', '5min')?.date_range || '-' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 指数标签 -->
          <el-tab-pane label="指数" name="index">
            <template #label>
              <span class="tab-label">
                <font-awesome-icon icon="chart-area" />
                指数
                <span class="tab-count">{{ formatNumber(tdxInfo?.indexCounts?.day || 0) }}</span>
              </span>
            </template>
            <div class="tab-content">
              <div v-if="loadingTypeData" class="loading-state">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在加载指数数据...</span>
              </div>
              <div v-else-if="typeError" class="error-state">
                <font-awesome-icon icon="exclamation-triangle" />
                <span>{{ typeError }}</span>
              </div>
              <div v-else class="type-timelines">
                <!-- 时间标尺 -->
                <div class="scale-marks-container">
                  <div class="scale-marks">
                    <div
                      v-for="mark in timelineMarks"
                      :key="mark.label"
                      :class="['scale-mark', mark.type]"
                      :style="{ left: mark.position + '%' }"
                    >
                      {{ mark.label }}
                    </div>
                  </div>
                </div>

                <!-- 日线数据时间条 -->
                <div class="timeline-row">
                  <div class="timeline-header">
                    <span class="timeline-title">日线数据</span>
                    <span class="timeline-percent" :style="{ color: getCompletenessColor(getTypeData('index', 'day')?.completeness || 0) }">
                      {{ getTypeData('index', 'day')?.completeness || 0 }}%
                    </span>
                  </div>
                  <div class="timeline-bar-container">
                    <div class="timeline-bar">
                      <template v-for="(segment, idx) in getTypeSegments('index', 'day')" :key="idx">
                        <div
                          :class="['timeline-segment', { 'has-data': segment.hasData }]"
                          :style="{
                            left: segment.left + '%',
                            width: segment.width + '%'
                          }"
                          :title="`${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)}`"
                        ></div>
                      </template>
                    </div>
                    <div class="timeline-range">{{ getTypeData('index', 'day')?.date_range || '-' }}</div>
                  </div>
                </div>

                <!-- 5分钟数据时间条 -->
                <div class="timeline-row">
                  <div class="timeline-header">
                    <span class="timeline-title">5分钟数据</span>
                    <span class="timeline-percent" :style="{ color: getCompletenessColor(getTypeData('index', '5min')?.completeness || 0) }">
                      {{ getTypeData('index', '5min')?.completeness || 0 }}%
                    </span>
                  </div>
                  <div class="timeline-bar-container">
                    <div class="timeline-bar">
                      <template v-for="(segment, idx) in getTypeSegments('index', '5min')" :key="idx">
                        <div
                          :class="['timeline-segment', { 'has-data': segment.hasData, 'is-5min': true }]"
                          :style="{
                            left: segment.left + '%',
                            width: segment.width + '%'
                          }"
                          :title="`${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)}`"
                        ></div>
                      </template>
                    </div>
                    <div class="timeline-range">{{ getTypeData('index', '5min')?.date_range || '-' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 债券、回购标签 -->
          <el-tab-pane label="债券、回购" name="other">
            <template #label>
              <span class="tab-label">
                <font-awesome-icon icon="money-bill-wave" />
                债券、回购
                <span class="tab-count">{{ formatNumber(tdxInfo?.otherCounts?.day || 0) }}</span>
              </span>
            </template>
            <div class="tab-content">
              <div v-if="loadingTypeData" class="loading-state">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在加载债券、回购数据...</span>
              </div>
              <div v-else-if="typeError" class="error-state">
                <font-awesome-icon icon="exclamation-triangle" />
                <span>{{ typeError }}</span>
              </div>
              <div v-else class="type-timelines">
                <!-- 时间标尺 -->
                <div class="scale-marks-container">
                  <div class="scale-marks">
                    <div
                      v-for="mark in timelineMarks"
                      :key="mark.label"
                      :class="['scale-mark', mark.type]"
                      :style="{ left: mark.position + '%' }"
                    >
                      {{ mark.label }}
                    </div>
                  </div>
                </div>

                <!-- 日线数据时间条 -->
                <div class="timeline-row">
                  <div class="timeline-header">
                    <span class="timeline-title">日线数据</span>
                    <span class="timeline-percent" :style="{ color: getCompletenessColor(getTypeData('other', 'day')?.completeness || 0) }">
                      {{ getTypeData('other', 'day')?.completeness || 0 }}%
                    </span>
                  </div>
                  <div class="timeline-bar-container">
                    <div class="timeline-bar">
                      <template v-for="(segment, idx) in getTypeSegments('other', 'day')" :key="idx">
                        <div
                          :class="['timeline-segment', { 'has-data': segment.hasData }]"
                          :style="{
                            left: segment.left + '%',
                            width: segment.width + '%'
                          }"
                          :title="`${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)}`"
                        ></div>
                      </template>
                    </div>
                    <div class="timeline-range">{{ getTypeData('other', 'day')?.date_range || '-' }}</div>
                  </div>
                </div>

                <!-- 5分钟数据时间条 -->
                <div class="timeline-row">
                  <div class="timeline-header">
                    <span class="timeline-title">5分钟数据</span>
                    <span class="timeline-percent" :style="{ color: getCompletenessColor(getTypeData('other', '5min')?.completeness || 0) }">
                      {{ getTypeData('other', '5min')?.completeness || 0 }}%
                    </span>
                  </div>
                  <div class="timeline-bar-container">
                    <div class="timeline-bar">
                      <template v-for="(segment, idx) in getTypeSegments('other', '5min')" :key="idx">
                        <div
                          :class="['timeline-segment', { 'has-data': segment.hasData, 'is-5min': true }]"
                          :style="{
                            left: segment.left + '%',
                            width: segment.width + '%'
                          }"
                          :title="`${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)}`"
                        ></div>
                      </template>
                    </div>
                    <div class="timeline-range">{{ getTypeData('other', '5min')?.date_range || '-' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import type { FrequencyType } from '@/components/data-management/shared/types'
import { AVAILABLE_FREQUENCIES } from '@/components/data-management/shared/constants'

interface Props {
  tdxInfo: any
  loading?: boolean
  hasDetected?: boolean
  tdxPath?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  hasDetected: false,
  tdxPath: ''
})

defineEmits<{
  refresh: []
}>()

// 时间轴范围 - 支持月份级别精度
// 默认值将在 onMounted 中根据真实数据范围设置
const timelineStart = ref(2025)
const timelineEnd = ref(2026)
const timelineStartMonth = ref(1)  // 1-12
const timelineEndMonth = ref(1)    // 1-12
const timelineRangePreset = ref('all')

// 日期选择器绑定值
const startDatePicker = ref<string>('')
const endDatePicker = ref<string>('')

// 标签页状态
const activeSecurityType = ref('stock')

// 证券类型数据
const securityTypeData = ref<Record<string, any>>({})
const loadingTypeData = ref(false)
const typeError = ref('')

// 数据缺失详情对话框
const gapDetailDialogVisible = ref(false)
const currentGapDetail = ref<{
  dataType: string
  startDate: Date
  endDate: Date
  missingDays: Date[]
} | null>(null)

// 初始化日期选择器值
const initDatePickers = () => {
  startDatePicker.value = `${timelineStart.value}-${String(timelineStartMonth.value).padStart(2, '0')}`
  endDatePicker.value = `${timelineEnd.value}-${String(timelineEndMonth.value).padStart(2, '0')}`
}

// 监听时间轴变化，同步日期选择器
const syncDatePickers = () => {
  startDatePicker.value = `${timelineStart.value}-${String(timelineStartMonth.value).padStart(2, '0')}`
  endDatePicker.value = `${timelineEnd.value}-${String(timelineEndMonth.value).padStart(2, '0')}`
}

// 开始日期变化处理
const onStartDateChange = (value: string) => {
  if (!value) return

  const [year, month] = value.split('-').map(Number)

  // 验证不能晚于结束日期
  const startDate = new Date(year, month - 1)
  const endDate = new Date(timelineEnd.value, timelineEndMonth.value - 1)

  if (startDate > endDate) {
    // 如果晚于结束日期，自动调整结束日期
    const laterStart = new Date(year, month - 1)
    laterStart.setMonth(laterStart.getMonth() + 12) // 至少保持一年间隔
    timelineEnd.value = laterStart.getFullYear()
    timelineEndMonth.value = laterStart.getMonth() + 1
  }

  timelineStart.value = year
  timelineStartMonth.value = month
  timelineRangePreset.value = ''  // 清除预设
}

// 结束日期变化处理
const onEndDateChange = (value: string) => {
  if (!value) return

  const [year, month] = value.split('-').map(Number)

  // 验证不能早于开始日期
  const startDate = new Date(timelineStart.value, timelineStartMonth.value - 1)
  const endDate = new Date(year, month - 1)

  if (endDate < startDate) {
    // 如果早于开始日期，自动调整开始日期
    const earlierEnd = new Date(year, month - 1)
    earlierEnd.setMonth(earlierEnd.getMonth() - 12) // 至少保持一年间隔
    timelineStart.value = earlierEnd.getFullYear()
    timelineStartMonth.value = earlierEnd.getMonth() + 1
  }

  timelineEnd.value = year
  timelineEndMonth.value = month
  timelineRangePreset.value = ''  // 清除预设
}

// 当前年份和月份（用于精细控制）
const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1

// 时间轴刻度标记（智能自适应，始终在0-100%范围内）
const timelineMarks = computed(() => {
  const marks = []
  const startDate = new Date(timelineStart.value, timelineStartMonth.value - 1)
  const endDate = new Date(timelineEnd.value, timelineEndMonth.value - 1)
  const rangeMs = endDate.getTime() - startDate.getTime()
  const rangeMonths = (endDate.getFullYear() - startDate.getFullYear()) * 12 + (endDate.getMonth() - startDate.getMonth())

  // 根据时间范围决定刻度间隔和目标刻度数量
  let targetMarkCount = 6 // 默认显示约6个刻度
  let interval: 'year' | 'quarter' | 'month'
  let step = 1

  if (rangeMonths <= 12) {
    // 1年以内：显示月份刻度
    interval = 'month'
    targetMarkCount = Math.min(12, rangeMonths + 1)
    step = Math.max(1, Math.floor(rangeMonths / targetMarkCount))
  } else if (rangeMonths <= 36) {
    // 3年以内：显示季度刻度
    interval = 'quarter'
    targetMarkCount = Math.min(12, Math.ceil(rangeMonths / 3))
    step = Math.max(1, Math.floor(rangeMonths / 3 / targetMarkCount))
  } else {
    // 超过3年：显示年份刻度
    interval = 'year'
    targetMarkCount = Math.min(10, Math.ceil(rangeMonths / 12))
    step = Math.max(1, Math.ceil(rangeMonths / 12 / targetMarkCount))
  }

  // 生成刻度，确保刻度在0-100%范围内
  if (interval === 'month') {
    // 对于月份级别，显示所有月份
    let current = new Date(startDate)
    // 对齐到月份开始
    current.setDate(1)

    while (current.getTime() <= endDate.getTime()) {
      const position = ((current.getTime() - startDate.getTime()) / rangeMs) * 100

      marks.push({
        label: `${current.getMonth() + 1}月`,
        position: Math.min(100, Math.max(0, position)),
        type: 'mark-month'
      })

      current.setMonth(current.getMonth() + 1)
    }
  } else if (interval === 'quarter') {
    let current = new Date(startDate)
    // 对齐到季度开始
    current.setDate(1)
    while (current.getMonth() % 3 !== 0) {
      current.setMonth(current.getMonth() + 1)
    }
    let count = 0
    const maxMarks = 16

    while (current.getTime() <= endDate.getTime() && count < maxMarks) {
      const position = ((current.getTime() - startDate.getTime()) / rangeMs) * 100

      marks.push({
        label: `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2, '0')}`,
        position: Math.min(100, Math.max(0, position)),
        type: 'mark-quarter'
      })

      current.setMonth(current.getMonth() + 3 * step)
      count++
    }
  } else {
    // year interval
    let current = startDate.getFullYear()
    const endYear = endDate.getFullYear()
    let count = 0
    const maxMarks = 12

    while (current <= endYear && count < maxMarks) {
      const markDate = new Date(current, 0)
      const position = ((markDate.getTime() - startDate.getTime()) / rangeMs) * 100

      marks.push({
        label: current.toString(),
        position: Math.min(100, Math.max(0, position)),
        type: 'mark-year'
      })

      current += step
      count++
    }
  }

  // 确保起点有刻度
  if (marks.length === 0 || marks[0].position > 5) {
    marks.unshift({
      label: interval === 'year'
        ? startDate.getFullYear().toString()
        : `${startDate.getMonth() + 1}月`,
      position: 0,
      type: 'mark-edge'
    })
  }

  // 确保终点有刻度
  if (marks.length === 0 || marks[marks.length - 1].position < 95) {
    marks.push({
      label: interval === 'year'
        ? endDate.getFullYear().toString()
        : `${endDate.getMonth() + 1}月`,
      position: 100,
      type: 'mark-edge'
    })
  }

  return marks
})

// 应用时间范围预设
const applyTimelinePreset = (preset: string) => {
  const now = new Date()
  const endYear = now.getFullYear()
  const endMonth = now.getMonth() + 1

  switch (preset) {
    case '1':
      timelineStart.value = endYear - 1
      timelineStartMonth.value = endMonth
      timelineEnd.value = endYear
      timelineEndMonth.value = endMonth
      break
    case '3':
      timelineStart.value = endYear - 3
      timelineStartMonth.value = endMonth
      timelineEnd.value = endYear
      timelineEndMonth.value = endMonth
      break
    case '5':
      timelineStart.value = endYear - 5
      timelineStartMonth.value = endMonth
      timelineEnd.value = endYear
      timelineEndMonth.value = endMonth
      break
    case 'all':
      timelineStart.value = 2020
      timelineStartMonth.value = 1
      timelineEnd.value = endYear
      timelineEndMonth.value = 12
      break
  }

  // 同步日期选择器
  syncDatePickers()
}

// 获取时间范围提示
const getTimeRangeHint = (label: string): string => {
  const hints: Record<string, string> = {
    '日线数据': '',
    '5分钟数据': '',
    '1分钟数据': '',
    '30分钟数据': '无数据',
    '60分钟数据': '无数据',
    '基础信息': '完整'
  }
  return hints[label] || ''
}

// 获取时间段（用于对齐时间条）
// 基于动态时间轴范围 - 数据条会根据选择的日期范围动态缩放
const getTimeSegments = (label: string): Array<{ left: number; width: number; hasData: boolean }> => {
  // 当前选择的时间轴范围（这是用户通过日期选择器设定的范围）
  const displayStart = new Date(timelineStart.value, timelineStartMonth.value - 1)
  const displayEnd = new Date(timelineEnd.value, timelineEndMonth.value - 1)
  const displayRangeMs = displayEnd.getTime() - displayStart.getTime()

  const segments: Array<{ left: number; width: number; hasData: boolean }> = []

  // 从 tdxInfo.dateRange 解析真实数据范围
  // 格式: "2025-01-02 ~ 2026-01-06"
  const dateRange = props.tdxInfo?.dateRange || ''
  const match = dateRange.match(/(\d{4})-(\d{2})-(\d{2})\s*~\s*(\d{4})-(\d{2})-(\d{2})/)

  if (!match) {
    // 如果没有有效数据，返回空段
    return []
  }

  // 解析真实数据的开始和结束日期
  const dataStart = new Date(parseInt(match[1]), parseInt(match[2]) - 1, parseInt(match[3]))
  const dataEnd = new Date(parseInt(match[4]), parseInt(match[5]) - 1, parseInt(match[6]))

  // 计算在显示范围内的位置
  const dataStartMs = dataStart.getTime()
  const dataEndMs = dataEnd.getTime()
  const left = ((dataStartMs - displayStart.getTime()) / displayRangeMs) * 100
  const width = ((dataEndMs - dataStartMs) / displayRangeMs) * 100

  // 只添加在显示范围内的段（或与显示范围有交集的段）
  if (left < 100 && left + width > 0) {
    segments.push({
      left: Math.max(0, left),
      width: Math.min(width, 100 - Math.max(0, left)),
      hasData: true
    })
  }

  return segments
}

// 计算统计数据
const stats = computed(() => {
  if (!props.tdxInfo) {
    return {
      totalStocks: 0,
      dateRange: '-',
      lastUpdate: '-',
      completeness: 0,
      completenessDetails: []
    }
  }

  console.log('DataSourceOverview计算stats, tdxInfo:', props.tdxInfo)

  const details = props.tdxInfo.completenessDetails || []
  console.log('completenessDetails:', details)

  return {
    totalStocks: props.tdxInfo.totalStocks || 0,
    dateRange: props.tdxInfo.dateRange || '-',
    lastUpdate: props.tdxInfo.lastUpdate || new Date().toLocaleDateString(),
    completeness: props.tdxInfo.completeness || 0,
    completenessDetails: details  // 直接使用API返回的数据，不使用虚拟fallback
  }
})

// 计算频率统计 - 只显示可用的频率
const frequencyStats = computed(() => {
  const availableFreqs = props.tdxInfo?.availableFrequencies || []

  // 只返回可用的频率，过滤掉不可用的
  return AVAILABLE_FREQUENCIES
    .filter(freq => availableFreqs.includes(freq.value))
    .map(freq => {
      const available = true

      // 只对直接数据源（日线、5分钟）显示统计，合成数据不显示数量
      let stockCount = 0
      let recordCount = 0
      let showStats = false

      if (freq.value === 'day') {
        stockCount = props.tdxInfo?.dailyStocks || 0
        recordCount = stockCount * 250 // 假设一年250个交易日
        showStats = true
      } else if (freq.value === '5min') {
        stockCount = props.tdxInfo?.minute5Stocks || 0
        recordCount = stockCount * 12000 // 假设一年250天，每天48个5分钟
        showStats = true
      }
      // 其他频率（1分钟、30分钟、60分钟等）不显示统计数据

      return {
        value: freq.value,
        label: freq.label,
        icon: freq.icon,
        available,
        stockCount,
        recordCount,
        showStats,
        dateRange: available ? (props.tdxInfo?.dateRange || '-') : null
      }
    })
})

// 方法
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const getCompletenessColor = (percent: number) => {
  if (percent >= 90) return '#10b981'
  if (percent >= 70) return '#f59e0b'
  return '#ef4444'
}

// 监听时间轴变化，同步日期选择器
watch([timelineStart, timelineStartMonth, timelineEnd, timelineEndMonth], () => {
  syncDatePickers()
})

// 监听 tdxInfo 变化，自动调整时间轴范围
watch(() => props.tdxInfo?.dateRange, (newDateRange) => {
  if (newDateRange) {
    const match = newDateRange.match(/(\d{4})-(\d{2})-(\d{2})\s*~\s*(\d{4})-(\d{2})-(\d{2})/)
    if (match) {
      timelineStart.value = parseInt(match[1])
      timelineStartMonth.value = parseInt(match[2])
      timelineEnd.value = parseInt(match[4])
      timelineEndMonth.value = parseInt(match[5])
    }
  }
}, { immediate: true })

// 组件挂载时初始化日期选择器
onMounted(() => {
  initDatePickers()
})

// 格式化日期
const formatDate = (date: Date | string | undefined): string => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// 显示空缺详情
const showGapDetail = (dataType: string, segment: any) => {
  const startDate = new Date(segment.startDate)
  const endDate = new Date(segment.endDate)

  // 计算缺失的所有日期
  const missingDays: Date[] = []
  const current = new Date(startDate)

  while (current <= endDate) {
    // 排除周末（对于股票数据）
    const dayOfWeek = current.getDay()
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      missingDays.push(new Date(current))
    }
    current.setDate(current.getDate() + 1)
  }

  currentGapDetail.value = {
    dataType,
    startDate,
    endDate,
    missingDays
  }
  gapDetailDialogVisible.value = true
}

// 复制缺失日期列表
const copyMissingDates = async () => {
  if (!currentGapDetail.value) return

  const datesText = currentGapDetail.value.missingDays
    .map(date => formatDate(date))
    .join('\n')

  try {
    await navigator.clipboard.writeText(datesText)
    // 这里可以添加一个成功提示
    console.log('日期列表已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
  }
}

// 获取证券类型数据
const getTypeData = (typeKey: string, frequency: 'day' | '5min') => {
  const data = securityTypeData.value[typeKey]
  if (!data) {
    return null
  }

  // 根据频率返回对应的数据
  const freqKey = frequency === 'day' ? 'day' : '5min'
  return data[freqKey] || null
}

// 获取证券类型的时间段
const getTypeSegments = (typeKey: string, frequency: 'day' | '5min') => {
  const freqData = getTypeData(typeKey, frequency)
  if (!freqData || !freqData.date_range || freqData.date_range === '-') {
    return []
  }

  // 解析日期范围
  const match = freqData.date_range.match(/(\d{4})-(\d{2})-(\d{2})\s*~\s*(\d{4})-(\d{2})-(\d{2})/)
  if (!match) {
    return []
  }

  // 当前选择的时间轴范围
  const displayStart = new Date(timelineStart.value, timelineStartMonth.value - 1)
  const displayEnd = new Date(timelineEnd.value, timelineEndMonth.value - 1)
  const displayRangeMs = displayEnd.getTime() - displayStart.getTime()

  // 数据的实际时间范围
  const dataStart = new Date(parseInt(match[1]), parseInt(match[2]) - 1, parseInt(match[3]))
  const dataEnd = new Date(parseInt(match[4]), parseInt(match[5]) - 1, parseInt(match[6]))

  const segments: Array<{ left: number; width: number; hasData: boolean; startDate: Date; endDate: Date }> = []

  // 计算在显示范围内的位置
  const dataStartMs = dataStart.getTime()
  const dataEndMs = dataEnd.getTime()
  const left = ((dataStartMs - displayStart.getTime()) / displayRangeMs) * 100
  const width = ((dataEndMs - dataStartMs) / displayRangeMs) * 100

  // 只添加在显示范围内的段
  if (left < 100 && left + width > 0) {
    segments.push({
      left: Math.max(0, left),
      width: Math.min(width, 100 - Math.max(0, left)),
      hasData: true,
      startDate: dataStart,
      endDate: dataEnd
    })
  }

  return segments
}

// 获取证券类型图标（需要定义在 fetchSecurityTypeData 之前）
const getSecurityTypeIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    stock: 'chart-line',
    fund: 'piggy-bank',
    index: 'chart-area',
    other: 'money-bill-wave'
  }
  return iconMap[type] || 'database'
}

// 获取证券类型数据（从 tdxInfo 构建，不需要额外 API 调用）
const fetchSecurityTypeData = async () => {
  if (!props.tdxInfo) {
    return
  }

  loadingTypeData.value = true
  typeError.value = ''

  try {
    // 直接从 tdxInfo 构建数据
    const merged: Record<string, any> = {}

    const typeKeys = ['stock', 'fund', 'index', 'other'] as const
    const typeLabels: Record<string, string> = {
      stock: '股票',
      fund: '基金',
      index: '指数',
      other: '债券、回购'
    }

    for (const key of typeKeys) {
      const dayCount = props.tdxInfo?.[`${key}Counts`]?.day || 0
      const min5Count = props.tdxInfo?.[`${key}Counts`]?.['5min'] || 0

      merged[key] = {
        label: typeLabels[key],
        icon: getSecurityTypeIcon(key),
        total_count: dayCount,
        // 日线数据
        day: {
          label: '日线',
          completeness: 0, // tdxInfo 中没有完整度信息，设为 0
          date_range: props.tdxInfo?.dateRange || '-',
          data_points: dayCount * 250, // 估算：假设250个交易日
          segments: []
        },
        // 5分钟数据
        '5min': {
          label: '5分钟',
          completeness: 0,
          date_range: props.tdxInfo?.dateRange || '-',
          data_points: min5Count * 12000, // 估算：假设一年250天，每天48个5分钟
          segments: []
        }
      }
    }

    securityTypeData.value = merged
  } catch (err: any) {
    console.error('构建证券类型数据失败:', err)
    typeError.value = err.message || '构建数据失败'
  } finally {
    loadingTypeData.value = false
  }
}

// 监听 tdxInfo 变化，自动构建数据
watch(() => props.tdxInfo, (newTdxInfo) => {
  if (newTdxInfo) {
    fetchSecurityTypeData()
  }
}, { immediate: true, deep: true })
</script>

<style scoped>
.data-source-overview {
  margin-bottom: 20px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.no-data-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
}

.no-data-tip p {
  margin-top: 16px;
  font-size: 14px;
}

.overview-cards {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 16px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

.overview-card.primary {
  border-left: 4px solid #2962ff;
}

.overview-card.success {
  border-left: 4px solid #10b981;
}

.overview-card.warning {
  border-left: 4px solid #f59e0b;
}

.card-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.15);
  border-radius: 12px;
  font-size: 24px;
  color: #2962ff;
}

.overview-card.success .card-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.overview-card.warning .card-icon {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
  margin-bottom: 4px;
}

.card-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  gap: 6px;
}

.frequency-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.freq-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
}

.freq-card.available {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.2);
}

.freq-card.available-no-stats {
  background: rgba(251, 191, 36, 0.05);
  border-color: rgba(251, 191, 36, 0.2);
}

.freq-card.available-no-stats .freq-icon {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}

.freq-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.freq-icon {
  align-self: flex-start;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.5);
}

.freq-card.available .freq-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.freq-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.freq-label {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.freq-status-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.freq-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.freq-date-range {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.3);
  font-family: 'Consolas', 'Monaco', monospace;
}

.freq-status.active {
  color: #10b981;
}

.freq-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.freq-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.freq-stat .stat-num {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}

.freq-stat .stat-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.completeness-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.completeness-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.completeness-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.completeness-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-control-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 8px 12px;
  margin-bottom: 12px;
  border-radius: 6px;
}

.scale-marks-container {
  position: relative;
  width: 100%;
  margin-bottom: 8px;
  padding: 4px 0;
  border-radius: 6px;
}

.timeline-control-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.timeline-scale {
  position: relative;
  height: 32px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.timeline-start-picker,
.timeline-end-picker {
  flex-shrink: 0;
  z-index: 10;
}

.timeline-start-picker :deep(.el-date-editor),
.timeline-end-picker :deep(.el-date-editor) {
  background: transparent !important;
  border-color: rgba(102, 126, 234, 0.3) !important;
}

.timeline-start-picker :deep(.el-date-editor:hover),
.timeline-end-picker :deep(.el-date-editor:hover) {
  border-color: rgba(102, 126, 234, 0.6) !important;
}

.timeline-start-picker :deep(.el-date-editor.is-active),
.timeline-end-picker :deep(.el-date-editor.is-active) {
  border-color: #2962ff !important;
  background: rgba(102, 126, 234, 0.1) !important;
}

.timeline-start-picker :deep(.el-date-editor .el-input__wrapper),
.timeline-end-picker :deep(.el-date-editor .el-input__wrapper) {
  background: rgba(102, 126, 234, 0.08) !important;
  box-shadow: none !important;
}

.timeline-start-picker :deep(.el-date-editor .el-input__wrapper:hover),
.timeline-end-picker :deep(.el-date-editor .el-input__wrapper:hover) {
  background: rgba(102, 126, 234, 0.12) !important;
}

.timeline-start-picker :deep(.el-date-editor .el-input__wrapper.is-focus),
.timeline-end-picker :deep(.el-date-editor .el-input__wrapper.is-focus) {
  background: rgba(102, 126, 234, 0.15) !important;
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.3) !important;
}

.timeline-start-picker :deep(.el-date-editor .el-input__inner),
.timeline-end-picker :deep(.el-date-editor .el-input__inner) {
  color: rgba(255, 255, 255, 0.9) !important;
}

.timeline-controls :deep(.el-select .el-input__wrapper) {
  background: rgba(102, 126, 234, 0.08) !important;
  box-shadow: none !important;
}

.timeline-controls :deep(.el-select .el-input__wrapper:hover) {
  background: rgba(102, 126, 234, 0.12) !important;
}

.timeline-controls :deep(.el-select .el-input__wrapper.is-focus) {
  background: rgba(102, 126, 234, 0.15) !important;
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.3) !important;
}

.timeline-controls :deep(.el-select .el-input__inner) {
  color: rgba(255, 255, 255, 0.9) !important;
}

/* 针对 el-select--small 的特别覆盖 */
.timeline-controls :deep(.el-select--small) {
  color-scheme: dark !important;
}

/* 强制覆盖"全部"下拉框的白色背景 */
.timeline-controls :deep(.el-select--small .el-input__wrapper),
.timeline-controls :deep(.el-select--small .el-input__wrapper),
.timeline-controls :deep(.el-select .el-input__wrapper) {
  background-color: rgba(102, 126, 234, 0.08) !important;
  background: rgba(102, 126, 234, 0.08) !important;
  box-shadow: none !important;
  border: 1px solid rgba(102, 126, 234, 0.3) !important;
}

.timeline-controls :deep(.el-select--small .el-input__wrapper:hover) {
  background-color: rgba(102, 126, 234, 0.12) !important;
}

.timeline-controls :deep(.el-select--small .el-input__wrapper.is-focus) {
  background-color: rgba(102, 126, 234, 0.15) !important;
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.3) !important;
}

/* 针对日期选择器 small 尺寸的覆盖 */
.timeline-start-picker :deep(.el-date-editor--small),
.timeline-end-picker :deep(.el-date-editor--small) {
  color-scheme: dark !important;
}

.timeline-start-picker :deep(.el-date-editor--small .el-input__wrapper),
.timeline-end-picker :deep(.el-date-editor--small .el-input__wrapper) {
  background-color: rgba(102, 126, 234, 0.08) !important;
  box-shadow: none !important;
}

.timeline-start-picker :deep(.el-date-editor--small .el-input__wrapper:hover),
.timeline-end-picker :deep(.el-date-editor--small .el-input__wrapper:hover) {
  background-color: rgba(102, 126, 234, 0.12) !important;
}

.timeline-start-picker :deep(.el-date-editor--small .el-input__wrapper.is-focus),
.timeline-end-picker :deep(.el-date-editor--small .el-input__wrapper.is-focus) {
  background-color: rgba(102, 126, 234, 0.15) !important;
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.3) !important;
}

/* 下拉菜单弹出层深色样式 - 使用全局样式 */
:deep(.el-select-dropdown) {
  background: rgba(30, 41, 59, 0.95) !important;
  border: 1px solid rgba(102, 126, 234, 0.3) !important;
}

:deep(.el-select-dropdown .el-select-menu) {
  background: transparent;
}

:deep(.el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.85);
}

:deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.15) !important;
}

:deep(.el-select-dropdown__item.is-selected) {
  background: rgba(102, 126, 234, 0.25) !important;
  color: #ffffff;
}

/* 日期选择器弹出层深色样式 */
:deep(.el-picker-dropdown) {
  background: rgba(30, 41, 59, 0.95) !important;
  border: 1px solid rgba(102, 126, 234, 0.3) !important;
}

:deep(.el-picker-panel) {
  background: rgba(30, 41, 59, 0.95);
  border-color: rgba(102, 126, 234, 0.3);
}

:deep(.el-date-picker__header-label) {
  color: rgba(255, 255, 255, 0.9);
}

:deep(.el-date-picker__header-btn) {
  color: rgba(255, 255, 255, 0.7);
}

:deep(.el-date-picker__header-btn:hover) {
  color: #2962ff;
}

:deep(.el-month-table td .cell) {
  color: rgba(255, 255, 255, 0.85);
}

:deep(.el-month-table td .cell:hover) {
  background: rgba(102, 126, 234, 0.15);
  color: #ffffff;
}

:deep(.el-month-table td.in-range .cell),
:deep(.el-month-table td.start-range .cell),
:deep(.el-month-table td.end-range .cell) {
  background: rgba(102, 126, 234, 0.2);
  color: #ffffff;
}

:deep(.el-month-table td.current .cell) {
  background: #2962ff !important;
  color: #ffffff;
}

.scale-marks {
  position: relative;
  width: 100%;
  height: 20px;
  display: flex;
  align-items: flex-end;
}

.scale-mark {
  position: absolute;
  bottom: 2px;
  transform: translateX(-50%);
  font-size: 10px;
  color: rgba(255, 255, 255, 0.35);
  padding: 2px 4px;
  white-space: nowrap;
  transition: all 0.3s ease;
  border-radius: 3px;
  pointer-events: none;
  z-index: 1;
}

.scale-mark.mark-year {
  font-weight: 600;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.scale-mark.mark-quarter {
  font-size: 10px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.45);
}

.scale-mark.mark-month {
  font-size: 9px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
}

.scale-mark.mark-edge {
  font-weight: 700;
  font-size: 11px;
  color: rgba(102, 126, 234, 0.9);
  background: rgba(102, 126, 234, 0.15);
}

.timeline-controls {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.detail-row {
  display: grid;
  grid-template-columns: 100px 1fr 50px;
  gap: 12px;
  align-items: center;
  padding: 6px 0;
  transition: background 0.2s ease;
}

.detail-row:hover {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
}

.detail-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.detail-bar-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-bar {
  position: relative;
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: visible;
}

.detail-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  border-radius: 4px;
  transition: all 0.3s ease;
  min-width: 2px;
}

.detail-fill.time-segment {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.detail-row:hover .detail-fill.time-segment {
  filter: brightness(1.1);
}

.detail-gap {
  position: absolute;
  top: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.15);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  min-width: 2px;
}

.detail-gap.time-segment {
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.1),
    rgba(255, 255, 255, 0.1) 2px,
    rgba(255, 255, 255, 0.15) 2px,
    rgba(255, 255, 255, 0.15) 4px
  );
}

.detail-row:hover .detail-gap.time-segment {
  background: repeating-linear-gradient(
    90deg,
    rgba(239, 68, 68, 0.15),
    rgba(239, 68, 68, 0.15) 2px,
    rgba(239, 68, 68, 0.25) 2px,
    rgba(239, 68, 68, 0.25) 4px
  );
}

.detail-gap.clickable-gap {
  cursor: pointer;
  transition: all 0.2s ease;
}

.detail-gap.clickable-gap:hover {
  background: repeating-linear-gradient(
    90deg,
    rgba(239, 68, 68, 0.3),
    rgba(239, 68, 68, 0.3) 2px,
    rgba(239, 68, 68, 0.4) 2px,
    rgba(239, 68, 68, 0.4) 4px
  ) !important;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
  z-index: 10;
}

.time-range-hint {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  font-family: 'Consolas', 'Monaco', monospace;
}

/* 数据缺失详情对话框样式 */
.gap-detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.gap-detail-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gap-info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.gap-info-label {
  color: rgba(255, 255, 255, 0.6);
  min-width: 80px;
}

.gap-info-value {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-family: 'Consolas', 'Monaco', monospace;
}

.gap-info-value.highlight {
  color: #ef4444;
  font-weight: 600;
  font-size: 16px;
}

.missing-dates-list {
  max-height: 400px;
  overflow-y: auto;
}

.list-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.dates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}

.date-item {
  padding: 6px 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  font-family: 'Consolas', 'Monaco', monospace;
  text-align: center;
  transition: all 0.2s ease;
}

.date-item:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  transform: translateY(-1px);
}

.detail-percent {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  text-align: right;
}

:deep(.el-progress__text) {
  font-size: 14px !important;
  font-weight: 600;
}

/* 统一按钮风格 */
:deep(.el-button) {
  border-radius: 20px;
}

:deep(.el-button--primary) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

:deep(.el-button--primary:hover:not(:disabled)) {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--primary:active:not(:disabled)) {
  background: linear-gradient(135deg, #5568d3 0%, #643a8b 100%);
  border-color: transparent;
  color: white;
}

/* 标签页样式 */
.security-type-tabs :deep(.el-tabs__header) {
  margin: 0 0 16px 0;
}

.security-type-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.security-type-tabs :deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  padding: 0 20px;
}

.security-type-tabs :deep(.el-tabs__item:hover) {
  color: rgba(255, 255, 255, 0.9);
}

.security-type-tabs :deep(.el-tabs__item.is-active) {
  color: #2962ff;
}

.security-type-tabs :deep(.el-tabs__active-bar) {
  background-color: #2962ff;
}

.security-type-tabs :deep(.el-tabs__content) {
  overflow: visible;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-count {
  font-size: 11px;
  font-weight: 600;
  color: rgba(102, 126, 234, 0.9);
  background: rgba(102, 126, 234, 0.15);
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 24px;
  text-align: center;
}

.tab-content {
  padding: 16px 0;
}

.type-timelines {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-state, .error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.error-state {
  color: #ef4444;
}

.timeline-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.timeline-percent {
  font-size: 14px;
  font-weight: 600;
}

.timeline-bar-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.timeline-bar {
  position: relative;
  height: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 5px;
  overflow: visible;
}

.timeline-segment {
  position: absolute;
  height: 100%;
  border-radius: 5px;
  transition: all 0.3s ease;
}

.timeline-segment.has-data {
  background: rgba(16, 185, 129, 0.7);
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.4);
}

.timeline-segment.has-data.is-5min {
  background: rgba(245, 158, 11, 0.7);
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.4);
}

.timeline-segment.has-data:hover {
  filter: brightness(1.15);
}

.timeline-segment.has-data.is-5min:hover {
  filter: brightness(1.15);
}

.timeline-range {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-family: 'Consolas', 'Monaco', monospace;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .frequency-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .frequency-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .overview-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .security-type-tabs :deep(.el-tabs__item) {
    padding: 0 12px;
    font-size: 13px;
  }
}
</style>
