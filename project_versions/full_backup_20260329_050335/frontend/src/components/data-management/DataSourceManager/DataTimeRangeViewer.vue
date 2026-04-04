<template>
  <el-dialog
    v-model="dialogVisible"
    title="数据时间范围详情"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
    class="time-range-viewer-dialog"
  >
    <div class="time-range-viewer" v-loading="loading">
      <!-- 频率选择器 -->
      <div class="frequency-selector">
        <div class="selector-label">选择数据频率：</div>
        <div class="frequency-tabs">
          <div
            v-for="freq in availableFrequencies"
            :key="freq.frequency"
            :class="['frequency-tab', { active: selectedFrequency === freq.frequency }]"
            @click="selectFrequency(freq.frequency)"
          >
            <font-awesome-icon :icon="freq.icon" />
            <span>{{ freq.frequencyLabel }}</span>
            <span v-if="freq.segments && freq.segments.length > 0" class="coverage-badge">
              {{ freq.coverage.toFixed(1) }}%
            </span>
            <span v-else class="no-data-badge">无数据</span>
          </div>
        </div>
      </div>

      <!-- 时间范围统计 -->
      <div v-if="currentRange" class="range-stats">
        <div class="stat-item">
          <span class="stat-label">数据起始：</span>
          <span class="stat-value">{{ formatDate(currentRange.startDate) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">数据结束：</span>
          <span class="stat-value">{{ formatDate(currentRange.endDate) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">数据覆盖率：</span>
          <span :class="['stat-value', getCoverageClass(currentRange.coverage)]">
            {{ currentRange.coverage.toFixed(1) }}%
          </span>
        </div>
        <div class="stat-item" v-if="currentRange.gaps > 0">
          <span class="stat-label">数据断档：</span>
          <span class="stat-value warning">{{ currentRange.gaps }} 处</span>
        </div>
      </div>

      <!-- 时间条可视化 -->
      <div v-if="currentRange && currentRange.segments && currentRange.segments.length > 0" class="timeline-container">
        <div class="timeline-header">
          <div class="header-title">数据覆盖时间线（精确到日）</div>
          <div class="header-legend">
            <div class="legend-item">
              <div class="legend-color has-data"></div>
              <span>有数据</span>
            </div>
            <div class="legend-item">
              <div class="legend-color no-data"></div>
              <span>数据缺失</span>
            </div>
          </div>
        </div>

        <div class="timeline-wrapper">
          <!-- 时间刻度 -->
          <div class="timeline-scale">
            <div
              v-for="(tick, index) in timeTicks"
              :key="index"
              :class="['scale-tick', { major: tick.major }]"
              :style="{ left: tick.position + '%' }"
            >
              <div class="tick-line"></div>
              <div v-if="tick.major" class="tick-label">{{ tick.label }}</div>
            </div>
          </div>

          <!-- 时间条 -->
          <div class="timeline-bar">
            <div
              v-for="(segment, index) in currentRange.segments"
              :key="index"
              :class="['time-segment', { 'has-data': segment.hasData, 'no-data': !segment.hasData }]"
              :style="{ left: segment.left + '%', width: segment.width + '%' }"
              @mouseenter="showTooltip($event, segment)"
              @mouseleave="hideTooltip"
            >
              <div v-if="segment.hasData" class="segment-pattern"></div>
            </div>
          </div>
        </div>

        <!-- 时间段详情列表 -->
        <div class="segments-list">
          <div class="list-title">时间段详情</div>
          <div class="segments-table">
            <div class="table-header">
              <div class="header-cell">开始日期</div>
              <div class="header-cell">结束日期</div>
              <div class="header-cell">状态</div>
              <div class="header-cell">说明</div>
            </div>
            <div class="table-body">
              <div
                v-for="(segment, index) in currentRange.segments"
                :key="index"
                :class="['table-row', { 'data-gap': !segment.hasData }]"
              >
                <div class="table-cell">{{ formatDate(segment.startDate) }}</div>
                <div class="table-cell">{{ formatDate(segment.endDate) }}</div>
                <div class="table-cell">
                  <span :class="['status-badge', segment.hasData ? 'has-data' : 'no-data']">
                    {{ segment.hasData ? '有数据' : '缺失' }}
                  </span>
                </div>
                <div class="table-cell">{{ segment.label || '-' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 无数据提示 -->
      <div v-else class="no-data-message">
        <font-awesome-icon icon="database" size="3x" style="color: rgba(255, 255, 255, 0.2);" />
        <p>当前频率暂无数据</p>
      </div>
    </div>

    <!-- 悬浮提示框 -->
    <div
      v-if="tooltipVisible"
      :class="['custom-tooltip', { 'no-data': !tooltipData?.hasData }]"
      :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
    >
      <div class="tooltip-title">{{ tooltipData?.hasData ? '数据段' : '数据缺失' }}</div>
      <div class="tooltip-content">
        <div>开始：{{ formatDate(tooltipData?.startDate) }}</div>
        <div>结束：{{ formatDate(tooltipData?.endDate) }}</div>
        <div v-if="tooltipData?.label">{{ tooltipData.label }}</div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getDataTimeRangeDetail, type FrequencyTimeRange, type DateRangeSegment } from '@/api/dataManagement'
import { AVAILABLE_FREQUENCIES } from '@/components/data-management/shared/constants'

interface Props {
  visible: boolean
  tdxInfo?: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const loading = ref(false)
const selectedFrequency = ref('day')
const timeRangeData = ref<FrequencyTimeRange[]>([])
const tooltipVisible = ref(false)
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipData = ref<DateRangeSegment | null>(null)

// 可用频率列表（带图标）
const availableFrequencies = computed(() => {
  const availableFreqs = props.tdxInfo?.availableFrequencies || []
  return AVAILABLE_FREQUENCIES
    .filter(freq => availableFreqs.includes(freq.value))
    .map(freq => {
      const rangeData = timeRangeData.value.find(r => r.frequency === freq.value)
      return {
        frequency: freq.value,
        frequencyLabel: freq.label,
        icon: freq.icon,
        ...rangeData
      }
    })
})

// 当前选中频率的数据
const currentRange = computed(() => {
  return timeRangeData.value.find(r => r.frequency === selectedFrequency.value)
})

// 时间刻度
const timeTicks = computed(() => {
  if (!currentRange.value || currentRange.value.segments.length === 0) return []

  const start = new Date(currentRange.value.startDate).getTime()
  const end = new Date(currentRange.value.endDate).getTime()
  const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24))

  // 生成刻度
  const ticks: Array<{ position: number; label: string; major: boolean }> = []

  // 起始刻度
  ticks.push({
    position: 0,
    label: formatYearMonth(new Date(start)),
    major: true
  })

  // 中间刻度（按月）
  const current = new Date(start)
  current.setDate(1) // 设置到月初
  current.setMonth(current.getMonth() + 1)

  while (current.getTime() < end) {
    const daysFromStart = Math.ceil((current.getTime() - start) / (1000 * 60 * 60 * 24))
    const position = (daysFromStart / totalDays) * 100

    ticks.push({
      position: Math.min(position, 100),
      label: formatYearMonth(current),
      major: true
    })

    current.setMonth(current.getMonth() + 1)
  }

  // 结束刻度
  ticks.push({
    position: 100,
    label: formatYearMonth(new Date(end)),
    major: true
  })

  return ticks
})

// 格式化年月
const formatYearMonth = (date: Date): string => {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

// 格式化日期
const formatDate = (dateStr?: string): string => {
  if (!dateStr) return '-'
  return dateStr
}

// 选择频率
const selectFrequency = (frequency: string) => {
  selectedFrequency.value = frequency
}

// 获取覆盖率样式类
const getCoverageClass = (coverage: number): string => {
  if (coverage >= 90) return 'success'
  if (coverage >= 70) return 'warning'
  return 'danger'
}

// 显示悬浮提示
const showTooltip = (event: MouseEvent, segment: DateRangeSegment) => {
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  tooltipX.value = rect.left + rect.width / 2
  tooltipY.value = rect.top - 10
  tooltipData.value = segment
  tooltipVisible.value = true
}

// 隐藏悬浮提示
const hideTooltip = () => {
  tooltipVisible.value = false
  tooltipData.value = null
}

// 加载时间范围数据
const loadTimeRangeData = async () => {
  loading.value = true
  try {
    const result = await getDataTimeRangeDetail({
      sourcePath: props.tdxInfo?.path
    })

    // 计算每个segment的位置和宽度
    const rangesWithPositions = result.frequencyRanges.map(range => {
      if (!range.segments || range.segments.length === 0) return range

      const start = new Date(range.startDate).getTime()
      const end = new Date(range.endDate).getTime()
      const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24))

      const segmentsWithPos = range.segments.map(segment => {
        const segStart = new Date(segment.startDate).getTime()
        const segEnd = new Date(segment.endDate).getTime()
        const segDays = Math.ceil((segEnd - segStart) / (1000 * 60 * 60 * 24)) + 1

        const left = ((segStart - start) / (1000 * 60 * 60 * 24) / totalDays) * 100
        const width = (segDays / totalDays) * 100

        return {
          ...segment,
          left: Math.max(0, left),
          width: Math.min(width, 100 - left)
        }
      })

      return {
        ...range,
        segments: segmentsWithPos
      }
    })

    timeRangeData.value = rangesWithPositions

    // 设置默认选中第一个有数据的频率
    const firstWithData = rangesWithPositions.find(r => r.segments && r.segments.length > 0)
    if (firstWithData) {
      selectedFrequency.value = firstWithData.frequency
    }
  } catch (error) {
    console.error('加载时间范围数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}

// 监听对话框显示
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadTimeRangeData()
  }
})
</script>

<style scoped>
.time-range-viewer {
  padding: 0;
}

.frequency-selector {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.selector-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 12px;
}

.frequency-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.frequency-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.frequency-tab:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.frequency-tab.active {
  background: rgba(102, 126, 234, 0.2);
  border-color: #2962ff;
  color: #ffffff;
}

.coverage-badge {
  padding: 2px 8px;
  background: rgba(16, 185, 129, 0.2);
  border-radius: 4px;
  font-size: 12px;
  color: #10b981;
}

.no-data-badge {
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.range-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.stat-value.success {
  color: #10b981;
}

.stat-value.warning {
  color: #f59e0b;
}

.stat-value.danger {
  color: #ef4444;
}

.timeline-container {
  margin-top: 24px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.header-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 3px;
}

.legend-color.has-data {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.legend-color.no-data {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
  opacity: 0.3;
}

.timeline-wrapper {
  position: relative;
  margin-bottom: 24px;
}

.timeline-scale {
  position: relative;
  height: 30px;
  margin-bottom: 8px;
}

.scale-tick {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
}

.tick-line {
  width: 1px;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  margin: 0 auto;
}

.scale-tick.major .tick-line {
  height: 16px;
  background: rgba(255, 255, 255, 0.5);
}

.tick-label {
  margin-top: 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  text-align: center;
}

.timeline-bar {
  position: relative;
  height: 60px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.time-segment {
  position: absolute;
  height: 100%;
  transition: all 0.2s ease;
  cursor: pointer;
}

.time-segment.has-data {
  background: linear-gradient(180deg, #10b981 0%, #059669 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.time-segment.has-data:hover {
  filter: brightness(1.1);
  transform: scaleY(1.05);
  transform-origin: center;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.time-segment.no-data {
  background: repeating-linear-gradient(
    45deg,
    rgba(239, 68, 68, 0.15),
    rgba(239, 68, 68, 0.15) 5px,
    rgba(239, 68, 68, 0.25) 5px,
    rgba(239, 68, 68, 0.25) 10px
  );
  border-right: 1px solid rgba(239, 68, 68, 0.2);
}

.time-segment.no-data:hover {
  background: repeating-linear-gradient(
    45deg,
    rgba(239, 68, 68, 0.25),
    rgba(239, 68, 68, 0.25) 5px,
    rgba(239, 68, 68, 0.35) 5px,
    rgba(239, 68, 68, 0.35) 10px
  );
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.segment-pattern {
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 2px,
    rgba(255, 255, 255, 0.1) 2px,
    rgba(255, 255, 255, 0.1) 4px
  );
}

.segments-list {
  margin-top: 32px;
}

.list-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

.segments-table {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 100px 1fr;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-cell {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.table-body {
  max-height: 300px;
  overflow-y: auto;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 100px 1fr;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background 0.2s ease;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.table-row.data-gap {
  background: rgba(239, 68, 68, 0.05);
}

.table-row.data-gap:hover {
  background: rgba(239, 68, 68, 0.08);
}

.table-cell {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.has-data {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.status-badge.no-data {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.no-data-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.4);
}

.no-data-message p {
  margin-top: 16px;
  font-size: 14px;
}

/* 自定义悬浮提示 */
.custom-tooltip {
  position: fixed;
  padding: 10px 14px;
  background: rgba(17, 24, 39, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  pointer-events: none;
  z-index: 10000;
  transform: translate(-50%, -100%);
  margin-top: -8px;
  min-width: 150px;
}

.custom-tooltip.no-data {
  border-color: rgba(239, 68, 68, 0.3);
}

.tooltip-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tooltip-content {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

/* 对话框样式 */
:deep(.time-range-viewer-dialog) {
  background: rgba(17, 24, 39, 0.95);
}

:deep(.time-range-viewer-dialog .el-dialog__header) {
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px 24px;
}

:deep(.time-range-viewer-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

:deep(.time-range-viewer-dialog .el-dialog__body) {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.time-range-viewer-dialog .el-dialog__footer) {
  background: rgba(255, 255, 255, 0.03);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 24px;
}

/* 滚动条样式 */
:deep(.table-body)::-webkit-scrollbar {
  width: 6px;
}

:deep(.table-body)::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

:deep(.table-body)::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

:deep(.table-body)::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .frequency-tabs {
    flex-direction: column;
  }

  .frequency-tab {
    width: 100%;
  }

  .range-stats {
    flex-direction: column;
    gap: 12px;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr 1fr 80px;
  }

  .table-header .header-cell:last-child,
  .table-row .table-cell:last-child {
    display: none;
  }
}
</style>
