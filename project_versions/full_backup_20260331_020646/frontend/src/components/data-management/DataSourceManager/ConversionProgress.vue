<template>
  <div v-if="progress" class="conversion-progress">
    <div class="progress-header">
      <span class="progress-label">转换进度</span>
      <span class="progress-percent">{{ progress.percent }}%</span>
    </div>

    <el-progress
      :percentage="progress.percent"
      :status="progress.status"
      :stroke-width="20"
    />

    <div class="progress-details">
      <div class="detail-item">
        <span class="detail-label">已处理:</span>
        <span class="detail-value">{{ formatNumber(progress.processed) }} 只股票</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">总计:</span>
        <span class="detail-value">{{ formatNumber(progress.total) }} 只股票</span>
      </div>
      <div class="detail-item" v-if="progress.currentStock">
        <span class="detail-label">当前处理:</span>
        <span class="detail-value">{{ progress.currentStock }}</span>
      </div>
      <div class="detail-item" v-if="progress.currentFrequency">
        <span class="detail-label">当前频率:</span>
        <span class="detail-value">{{ getFrequencyLabel(progress.currentFrequency) }}</span>
      </div>
      <div class="detail-item" v-if="progress.elapsedTime">
        <span class="detail-label">已用时间:</span>
        <span class="detail-value">{{ progress.elapsedTime }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ConversionProgress } from '@/components/data-management/shared/types'
import { FREQUENCY_CONFIG } from '@/components/data-management/shared/constants'

interface Props {
  progress: ConversionProgress | null
}

defineProps<Props>()

const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const getFrequencyLabel = (freq: string) => {
  return FREQUENCY_CONFIG[freq as keyof typeof FREQUENCY_CONFIG]?.label || freq
}
</script>

<style scoped>
.conversion-progress {
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.progress-percent {
  font-size: 18px;
  font-weight: 700;
  color: #2962ff;
}

.progress-details {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 768px) {
  .progress-details {
    grid-template-columns: 1fr;
  }
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.detail-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.detail-value {
  font-size: 12px;
  font-weight: 600;
  color: white;
}
</style>
