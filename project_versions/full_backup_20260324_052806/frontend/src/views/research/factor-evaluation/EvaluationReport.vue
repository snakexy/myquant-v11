<template>
  <div class="evaluation-report">
    <div class="report-header">
      <svg class="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
        <polyline points="10 9 9 9 8 9"/>
      </svg>
      <h3 class="header-title">{{ title }}</h3>
    </div>

    <div v-if="data" class="report-content">
      <div class="report-summary">
        <div
          v-for="item in summaryItems"
          :key="item.key"
          class="summary-item"
        >
          <span class="summary-label">{{ item.label }}:</span>
          <span :class="['summary-value', item.valueClass]">
            {{ item.value }}
          </span>
        </div>
      </div>

      <div v-if="data.details" class="report-details">
        <h4 class="details-title">{{ detailsTitle }}</h4>
        <p class="details-text">{{ data.details }}</p>
      </div>
    </div>

    <div v-else class="report-placeholder">
      <div class="placeholder-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="12" y1="18" x2="12" y2="12"/>
          <line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
      </div>
      <p>{{ placeholderText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface ReportData {
  completed: boolean
  status: string
  evaluatedAt: string
  totalFactors: number
  qualifiedFactors: number
  details: string
}

interface SummaryItem {
  key: string
  label: string
  value: string
  valueClass?: string
}

interface Props {
  data: ReportData | null
  isZh?: boolean
  title?: string
  detailsTitle?: string
  placeholderText?: string
}

const props = withDefaults(defineProps<Props>(), {
  isZh: true,
  title: '',
  detailsTitle: '',
  placeholderText: ''
})

const title = computed(() => props.title || (props.isZh ? '评估报告' : 'Evaluation Report'))
const detailsTitle = computed(() => props.detailsTitle || (props.isZh ? '详细说明' : 'Details'))
const placeholderText = computed(() => props.placeholderText || (props.isZh ? '点击下方按钮开始评估' : 'Click the button below to start evaluation'))

const summaryItems = computed((): SummaryItem[] => {
  if (!props.data) return []

  const statusText = props.data.status === 'pass'
    ? (props.isZh ? '通过' : 'Pass')
    : (props.isZh ? '未通过' : 'Fail')

  return [
    {
      key: 'status',
      label: props.isZh ? '评估状态' : 'Status',
      value: statusText,
      valueClass: props.data.status
    },
    {
      key: 'evaluatedAt',
      label: props.isZh ? '评估时间' : 'Evaluated At',
      value: props.data.evaluatedAt
    },
    {
      key: 'totalFactors',
      label: props.isZh ? '评估因子数' : 'Factors Evaluated',
      value: String(props.data.totalFactors)
    },
    {
      key: 'qualifiedFactors',
      label: props.isZh ? '合格因子数' : 'Qualified Factors',
      value: String(props.data.qualifiedFactors)
    }
  ]
})
</script>

<style scoped lang="scss">
.evaluation-report {
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  padding: 16px;
}

.report-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.header-icon {
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
}

.header-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.report-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
}

.summary-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.summary-value {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 600;

  &.pass {
    color: var(--accent-green);
  }

  &.fail {
    color: var(--accent-red);
  }
}

.report-details {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.details-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.details-text {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.report-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-secondary);
}

.placeholder-icon {
  width: 48px;
  height: 48px;
  opacity: 0.5;
}

.report-placeholder p {
  font-size: 13px;
  margin: 0;
}
</style>
