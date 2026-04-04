<template>
  <div class="time-range-mini-view">
    <div class="mini-view-header">
      <div class="header-title">📅 数据时间范围详情</div>
      <el-button
        size="small"
        text
        @click="$emit('show-detail')"
        class="detail-btn"
      >
        <font-awesome-icon icon="expand-alt" />
        查看完整时间线
      </el-button>
    </div>

    <div v-loading="loading" class="mini-view-content">
      <div
        v-for="freq in frequencyRanges"
        :key="freq.frequency"
        :class="['freq-timeline-row', { 'no-data': !freq.hasData }]"
      >
        <div class="freq-label">
          <font-awesome-icon :icon="freq.icon" />
          <span>{{ freq.frequencyLabel }}</span>
        </div>

        <div class="timeline-wrapper">
          <div v-if="freq.hasData" class="timeline-track">
            <div
              v-for="(segment, index) in freq.segments"
              :key="index"
              :class="['timeline-segment', { 'has-data': segment.hasData, 'no-data': !segment.hasData }]"
              :style="{ left: segment.left + '%', width: segment.width + '%' }"
              @mouseenter="showTooltip($event, segment, freq.frequencyLabel)"
              @mouseleave="hideTooltip"
            >
            </div>
          </div>

          <div v-else class="timeline-track empty">
            <div class="empty-text">无数据</div>
          </div>

          <div v-if="freq.hasData" class="timeline-info">
            <span class="date-range">{{ formatDateShort(freq.startDate)}} ~ {{ formatDateShort(freq.endDate) }}</span>
            <span :class="['coverage-percent', getCoverageClass(freq.coverage)]">
              {{ freq.coverage.toFixed(0) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 悬浮提示 -->
    <div
      v-if="tooltipVisible"
      class="mini-tooltip"
      :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
    >
      <div class="tooltip-freq">{{ tooltipData?.freqLabel }}</div>
      <div class="tooltip-content">
        <div>{{ tooltipData?.segment.hasData ? '✓' : '✗' }} {{ tooltipData?.segment.label || (tooltipData?.segment.hasData ? '有数据' : '数据缺失') }}</div>
        <div class="tooltip-dates">
          {{ formatDate(tooltipData?.segment.startDate) }} ~ {{ formatDate(tooltipData?.segment.endDate) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getDataTimeRangeDetail, type FrequencyTimeRange, type DateRangeSegment } from '@/api/dataManagement'
import { AVAILABLE_FREQUENCIES } from '@/components/data-management/shared/constants'

interface Props {
  tdxInfo?: any
}

const props = defineProps<Props>()

defineEmits<{
  'show-detail': []
}>()

const loading = ref(false)
const frequencyRanges = ref<Array<{
  frequency: string
  frequencyLabel: string
  icon: string
  hasData: boolean
  segments?: Array<DateRangeSegment & { left: number; width: number }>
  coverage: number
  gaps: number
}>>([])

const tooltipVisible = ref(false)
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipData = ref<{ segment: DateRangeSegment; freqLabel: string } | null>(null)

// 格式化日期
const formatDate = (dateStr?: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 格式化短日期（只显示年月）
const formatDateShort = (dateStr?: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

// 获取覆盖率样式类
const getCoverageClass = (coverage: number): string => {
  if (coverage >= 90) return 'success'
  if (coverage >= 70) return 'warning'
  return 'danger'
}

// 显示悬浮提示
const showTooltip = (event: MouseEvent, segment: DateRangeSegment, freqLabel: string) => {
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  tooltipX.value = rect.left + rect.width / 2
  tooltipY.value = rect.top
  tooltipData.value = { segment, freqLabel }
  tooltipVisible.value = true
}

// 隐藏悬浮提示
const hideTooltip = () => {
  tooltipVisible.value = false
  tooltipData.value = null
}

// 加载时间范围数据
const loadData = async () => {
  loading.value = true
  try {
    const result = await getDataTimeRangeDetail({
      sourcePath: props.tdxInfo?.path
    })

    // 处理数据，计算位置和宽度
    const availableFreqs = props.tdxInfo?.availableFrequencies || []

    const processedRanges = AVAILABLE_FREQUENCIES
      .filter(freq => availableFreqs.includes(freq.value))
      .map(freq => {
        const rangeData = result.frequencyRanges.find(r => r.frequency === freq.value)

        if (!rangeData || !rangeData.segments || rangeData.segments.length === 0) {
          return {
            frequency: freq.value,
            frequencyLabel: freq.label,
            icon: freq.icon,
            hasData: false,
            coverage: 0,
            gaps: 0
          }
        }

        const start = new Date(rangeData.startDate).getTime()
        const end = new Date(rangeData.endDate).getTime()
        const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24))

        const segmentsWithPos = rangeData.segments.map(segment => {
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
          frequency: freq.value,
          frequencyLabel: freq.label,
          icon: freq.icon,
          hasData: true,
          segments: segmentsWithPos,
          coverage: rangeData.coverage,
          gaps: rangeData.gaps
        }
      })

    frequencyRanges.value = processedRanges
  } catch (error) {
    console.error('加载时间范围数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})

// 暴露刷新方法
defineExpose({
  refresh: loadData
})
</script>

<style scoped>
.time-range-mini-view {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: 20px;
}

.mini-view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.detail-btn {
  font-size: 12px;
  color: #2962ff;
  padding: 4px 12px;
}

.detail-btn:hover {
  background: rgba(102, 126, 234, 0.1);
}

.mini-view-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.freq-timeline-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  transition: background 0.2s ease;
}

.freq-timeline-row:hover {
  background: rgba(255, 255, 255, 0.04);
}

.freq-timeline-row.no-data {
  opacity: 0.5;
}

.freq-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.freq-label font-awesome-icon {
  font-size: 12px;
}

.timeline-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.timeline-track {
  position: relative;
  height: 24px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.timeline-track.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
}

.empty-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
}

.timeline-segment {
  position: absolute;
  height: 100%;
  transition: all 0.2s ease;
  cursor: pointer;
  min-width: 2px;
  top: 0;
}

.timeline-segment.has-data {
  background: linear-gradient(180deg, #10b981 0%, #059669 100%);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.timeline-segment.has-data:hover {
  filter: brightness(1.15);
  z-index: 10;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4);
}

.timeline-segment.no-data {
  background: rgba(255, 255, 255, 0.15);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.timeline-segment.no-data:hover {
  background: rgba(239, 68, 68, 0.25);
  z-index: 10;
}

.timeline-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.date-range {
  color: rgba(255, 255, 255, 0.5);
  font-family: 'Consolas', 'Monaco', monospace;
}

.coverage-info {
  display: flex;
  justify-content: flex-end;
}

.coverage-percent {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 3px;
}

.coverage-percent.success {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.coverage-percent.warning {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.coverage-percent.danger {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* 悬浮提示 */
.mini-tooltip {
  position: fixed;
  padding: 8px 12px;
  background: rgba(17, 24, 39, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  pointer-events: none;
  z-index: 10000;
  transform: translate(-50%, -100%);
  margin-top: -8px;
  min-width: 140px;
}

.tooltip-freq {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tooltip-content {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
}

.tooltip-dates {
  margin-top: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .freq-timeline-row {
    grid-template-columns: 60px 1fr 40px;
    gap: 8px;
  }

  .freq-label {
    font-size: 11px;
  }

  .timeline-track {
    height: 16px;
  }
}
</style>
