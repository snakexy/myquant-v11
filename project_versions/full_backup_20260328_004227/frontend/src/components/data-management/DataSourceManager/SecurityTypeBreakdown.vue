<template>
  <div class="security-type-breakdown">
    <div class="breakdown-header">
      <h4>📊 按证券类型分类</h4>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在分析...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <font-awesome-icon icon="exclamation-triangle" />
      <span>{{ error }}</span>
    </div>

    <!-- 分类数据卡片 -->
    <div v-else class="type-cards">
      <div
        v-for="(typeData, typeKey) in typeStats"
        :key="typeKey"
        :class="['type-card', typeKey]"
      >
        <div class="type-header">
          <div class="type-icon">
            <font-awesome-icon :icon="typeData.icon" />
          </div>
          <div class="type-info">
            <div class="type-label">{{ typeData.label }}</div>
            <div class="type-count">{{ formatNumber(typeData.total_count) }} 个</div>
          </div>
        </div>

        <!-- 多频率时间线 -->
        <div class="frequency-timelines">
          <div
            v-for="freq in ['day', '5min']"
            :key="freq"
            class="timeline-item"
          >
            <div class="timeline-header">
              <span class="timeline-label">{{ freq === 'day' ? '日线' : '5分钟' }}</span>
              <span class="timeline-completeness" :style="{ color: getCompletenessColor(typeData[freq]?.completeness || 0) }">
                {{ typeData[freq]?.completeness || 0 }}%
              </span>
            </div>

            <!-- 时间刻度和数据段 -->
            <div class="timeline-section">
              <div class="timeline-scale">
                <div class="scale-marks">
                  <div
                    v-for="mark in getTimeMarks(typeKey, freq)"
                    :key="mark.label"
                    :class="['scale-mark', mark.type]"
                    :style="{ left: mark.position + '%' }"
                  >
                    {{ mark.label }}
                  </div>
                </div>
              </div>

              <!-- 数据段可视化 -->
              <div class="data-segments">
                <div
                  v-for="(segment, idx) in getDataSegments(typeKey, freq)"
                  :key="idx"
                  :class="['data-segment', { 'has-data': segment.hasData, 'gap': !segment.hasData }]"
                  :style="{
                    left: segment.left + '%',
                    width: segment.width + '%'
                  }"
                  :title="`${segment.label} (${formatDate(segment.startDate)} ~ ${formatDate(segment.endDate)})`"
                ></div>
              </div>

              <div class="timeline-range">{{ typeData[freq]?.date_range || '-' }}</div>
            </div>
          </div>
        </div>

        <!-- 汇总指标 -->
        <div class="summary-metrics">
          <div class="metric-item">
            <span class="metric-label">日线完整度</span>
            <span class="metric-value" :style="{ color: getCompletenessColor(typeData.day?.completeness || 0) }">
              {{ typeData.day?.completeness || 0 }}%
            </span>
          </div>
          <div class="metric-item">
            <span class="metric-label">5分钟完整度</span>
            <span class="metric-value" :style="{ color: getCompletenessColor(typeData['5min']?.completeness || 0) }">
              {{ typeData['5min']?.completeness || 0 }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 汇总统计 -->
    <div class="summary-stats">
      <div class="summary-item">
        <span class="summary-label">证券总数</span>
        <span class="summary-value">{{ formatNumber(totalSecurities) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">平均完整度</span>
        <span class="summary-value" :style="{ color: getCompletenessColor(avgCompleteness) }">
          {{ avgCompleteness.toFixed(1) }}%
        </span>
      </div>
      <div class="summary-item">
        <span class="summary-label">数据类型</span>
        <span class="summary-value">{{ Object.keys(typeStats).length }} 种</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

interface FrequencyData {
  label: string
  completeness: number
  date_range: string
  data_points: number
  segments?: DataSegmentRaw[]
}

interface SecurityTypeData {
  label: string
  icon: string
  total_count: number
  day: FrequencyData
  '5min': FrequencyData
}

interface DataSegmentRaw {
  start_date: string
  end_date: string
  has_data: boolean
}

interface DataSegment {
  left: number
  width: number
  hasData: boolean
  label: string
  startDate: Date
  endDate: Date
}

interface Props {
  tdxPath?: string
  tdxInfo?: any
}

const props = defineProps<Props>()

const loading = ref(false)
const error = ref('')
const typeStats = ref<Record<string, SecurityTypeData>>({})

// 从实际数据动态计算时间轴范围
const timelineRange = computed(() => {
  const types = Object.values(typeStats.value)
  if (types.length === 0) {
    return {
      start: new Date(2025, 0, 1),
      end: new Date(2026, 0, 1)
    }
  }

  let earliestDate: Date | null = null
  let latestDate: Date | null = null

  // 遍历所有类型和频率的数据
  for (const typeData of types) {
    for (const freq of ['day', '5min'] as const) {
      const freqData = typeData[freq]
      if (!freqData) continue

      const match = freqData.date_range.match(/(\d{4})-(\d{2})-(\d{2})\s*~\s*(\d{4})-(\d{2})-(\d{2})/)
      if (match) {
        const startDate = new Date(parseInt(match[1]), parseInt(match[2]) - 1, parseInt(match[3]))
        const endDate = new Date(parseInt(match[4]), parseInt(match[5]) - 1, parseInt(match[6]))

        if (!earliestDate || startDate.getTime() < earliestDate.getTime()) {
          earliestDate = startDate
        }
        if (!latestDate || endDate.getTime() > latestDate.getTime()) {
          latestDate = endDate
        }
      }
    }
  }

  if (!earliestDate || !latestDate) {
    return {
      start: new Date(2025, 0, 1),
      end: new Date(2026, 0, 1)
    }
  }

  // 添加10%的边距
  const rangeMs = latestDate.getTime() - earliestDate.getTime()
  const paddingMs = rangeMs * 0.1

  return {
    start: new Date(earliestDate.getTime() - paddingMs),
    end: new Date(latestDate.getTime() + paddingMs)
  }
})

// 计算汇总统计
const totalSecurities = computed(() => {
  return Object.values(typeStats.value).reduce((sum, type) => sum + type.total_count, 0)
})

const avgCompleteness = computed(() => {
  const values = Object.values(typeStats.value)
  if (values.length === 0) return 0

  let totalCompleteness = 0
  let count = 0

  for (const type of values) {
    for (const freq of ['day', '5min'] as const) {
      if (type[freq]?.completeness) {
        totalCompleteness += type[freq].completeness
        count++
      }
    }
  }

  return count > 0 ? totalCompleteness / count : 0
})

// 获取所有频率的数据（从 tdxInfo 构建，不需要额外 API 调用）
const fetchTypeData = async () => {
  if (!props.tdxInfo) {
    error.value = '未提供数据信息'
    return
  }

  loading.value = true
  error.value = ''

  try {
    // 直接从 tdxInfo 构建数据
    const merged: Record<string, SecurityTypeData> = {}

    const typeKeys = ['stock', 'fund', 'index', 'other'] as const
    const typeLabels: Record<string, string> = {
      stock: '股票',
      fund: '基金',
      index: '指数',
      other: '债券、回购'
    }

    const iconMap: Record<string, string> = {
      stock: 'chart-line',
      fund: 'piggy-bank',
      index: 'chart-area',
      other: 'money-bill-wave'
    }

    for (const key of typeKeys) {
      const dayCount = props.tdxInfo?.[`${key}Counts`]?.day || 0
      const min5Count = props.tdxInfo?.[`${key}Counts`]?.['5min'] || 0

      merged[key] = {
        label: typeLabels[key],
        icon: iconMap[key] || 'database',
        total_count: dayCount,
        day: {
          label: '日线',
          completeness: 0,
          date_range: props.tdxInfo?.dateRange || '-',
          data_points: dayCount * 250,
          segments: []
        },
        '5min': {
          label: '5分钟',
          completeness: 0,
          date_range: props.tdxInfo?.dateRange || '-',
          data_points: min5Count * 12000,
          segments: []
        }
      }
    }

    typeStats.value = merged
  } catch (err: any) {
    console.error('构建类型数据失败:', err)
    error.value = err.message || '构建数据失败'
  } finally {
    loading.value = false
  }
}

// 获取时间刻度
const getTimeMarks = (typeKey: string, freq: 'day' | '5min') => {
  const marks = []
  const { start: startDate, end: endDate } = timelineRange.value
  const rangeMs = endDate.getTime() - startDate.getTime()
  const rangeMonths = (endDate.getFullYear() - startDate.getFullYear()) * 12 +
                     (endDate.getMonth() - startDate.getMonth())

  // 根据时间范围决定刻度间隔
  if (rangeMonths <= 12) {
    // 1年以内：显示月份刻度
    let current = new Date(startDate)
    while (current <= endDate) {
      const position = ((current.getTime() - startDate.getTime()) / rangeMs) * 100
      marks.push({
        label: `${current.getMonth() + 1}月`,
        position: Math.min(100, Math.max(0, position)),
        type: 'month'
      })
      current.setMonth(current.getMonth() + 1)
    }
  } else {
    // 超过1年：显示季度刻度
    let current = new Date(startDate)
    while (current <= endDate) {
      const position = ((current.getTime() - startDate.getTime()) / rangeMs) * 100
      marks.push({
        label: `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2, '0')}`,
        position: Math.min(100, Math.max(0, position)),
        type: 'quarter'
      })
      current.setMonth(current.getMonth() + 3)
    }
  }

  return marks
}

// 获取数据段
const getDataSegments = (typeKey: string, freq: 'day' | '5min'): DataSegment[] => {
  const typeData = typeStats.value[typeKey]
  if (!typeData) return []

  const freqData = typeData[freq]
  if (!freqData || freqData.completeness === 0) return []

  // 如果API返回了真实的segments数据，使用它
  if (freqData.segments && freqData.segments.length > 0) {
    const { start: displayStart, end: displayEnd } = timelineRange.value
    const displayRangeMs = displayEnd.getTime() - displayStart.getTime()

    return freqData.segments.map(segment => {
      const startDate = new Date(segment.start_date)
      const endDate = new Date(segment.end_date)

      const left = Math.max(0, ((startDate.getTime() - displayStart.getTime()) / displayRangeMs) * 100)
      const right = Math.min(100, ((endDate.getTime() - displayStart.getTime()) / displayRangeMs) * 100)
      const width = Math.max(0.5, right - left)

      return {
        left,
        width,
        hasData: segment.has_data,
        label: segment.has_data ? freqData.label : '缺失',
        startDate,
        endDate
      }
    })
  }

  // 从date_range解析日期（fallback逻辑）
  const dateRange = freqData.date_range
  const match = dateRange.match(/(\d{4})-(\d{2})-(\d{2})\s*~\s*(\d{4})-(\d{2})-(\d{2})/)

  if (!match) {
    return []
  }

  const startDate = new Date(parseInt(match[1]), parseInt(match[2]) - 1, parseInt(match[3]))
  const endDate = new Date(parseInt(match[4]), parseInt(match[5]) - 1, parseInt(match[6]))

  const { start: displayStart, end: displayEnd } = timelineRange.value
  const displayRangeMs = displayEnd.getTime() - displayStart.getTime()

  const left = Math.max(0, ((startDate.getTime() - displayStart.getTime()) / displayRangeMs) * 100)
  const right = Math.min(100, ((endDate.getTime() - displayStart.getTime()) / displayRangeMs) * 100)
  const width = right - left

  return [{
    left,
    width,
    hasData: true,
    label: freqData.label,
    startDate,
    endDate
  }]
}

// 格式化数字
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

// 格式化日期
const formatDate = (date: Date): string => {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 获取完整度颜色
const getCompletenessColor = (percent: number): string => {
  if (percent >= 90) return '#10b981'
  if (percent >= 70) return '#f59e0b'
  return '#ef4444'
}

// 组件挂载时获取数据
onMounted(() => {
  fetchTypeData()
})

// 监听 tdxInfo 变化，自动构建数据
watch(() => props.tdxInfo, (newTdxInfo) => {
  if (newTdxInfo) {
    fetchTypeData()
  }
}, { immediate: true, deep: true })

// 暴露刷新方法
defineExpose({
  refresh: fetchTypeData
})
</script>

<style scoped>
.security-type-breakdown {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 20px;
}

.breakdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.breakdown-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.loading-state,
.error-state {
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

.type-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.type-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.type-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.type-card.stock {
  border-color: rgba(102, 126, 234, 0.3);
}

.type-card.fund {
  border-color: rgba(16, 185, 129, 0.3);
}

.type-card.index {
  border-color: rgba(245, 158, 11, 0.3);
}

.type-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.type-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.15);
  border-radius: 12px;
  font-size: 20px;
  color: #2962ff;
  flex-shrink: 0;
}

.type-card.fund .type-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.type-card.index .type-icon {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.type-info {
  flex: 1;
  min-width: 0;
}

.type-label {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.type-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.type-completeness {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  min-width: 80px;
}

.completeness-value {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}

.completeness-bar-mini {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.completeness-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

/* 时间线部分 */
.timeline-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.timeline-range {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-family: 'Consolas', 'Monaco', monospace;
}

.timeline-scale {
  position: relative;
  height: 20px;
  margin-bottom: 4px;
}

.scale-marks {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-end;
}

.scale-mark {
  position: absolute;
  bottom: 2px;
  transform: translateX(-50%);
  font-size: 9px;
  color: rgba(255, 255, 255, 0.35);
  white-space: nowrap;
}

.scale-mark.month {
  font-weight: 500;
}

.scale-mark.quarter {
  font-size: 8px;
  font-weight: 500;
}

.data-segments {
  position: relative;
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: visible;
}

.data-segment {
  position: absolute;
  height: 100%;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.data-segment.has-data {
  background: rgba(16, 185, 129, 0.6);
  box-shadow: 0 0 4px rgba(16, 185, 129, 0.3);
}

.data-segment.gap {
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.1),
    rgba(255, 255, 255, 0.1) 2px,
    rgba(255, 255, 255, 0.15) 2px,
    rgba(255, 255, 255, 0.15) 4px
  );
}

.type-card:hover .data-segment.has-data {
  filter: brightness(1.1);
}

.type-card:hover .data-segment.gap {
  background: repeating-linear-gradient(
    90deg,
    rgba(239, 68, 68, 0.2),
    rgba(239, 68, 68, 0.2) 2px,
    rgba(239, 68, 68, 0.3) 2px,
    rgba(239, 68, 68, 0.3) 4px
  );
}

.type-metrics {
  display: flex;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.metric-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.metric-value.text {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
}

/* 汇总统计 */
.summary-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .type-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .type-cards {
    grid-template-columns: 1fr;
  }

  .breakdown-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .summary-stats {
    flex-direction: column;
    gap: 16px;
  }

  .type-header {
    flex-wrap: wrap;
  }

  .type-completeness {
    min-width: 60px;
  }
}
</style>

