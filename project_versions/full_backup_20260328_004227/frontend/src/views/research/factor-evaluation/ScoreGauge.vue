<template>
  <div class="score-gauge">
    <div class="gauge-container">
      <div
        v-for="(gauge, index) in gauges"
        :key="index"
        class="gauge-item"
      >
        <el-progress
          type="dashboard"
          :percentage="gauge.percentage"
          :width="gauge.width || 120"
          :color="getGaugeColor(gauge.percentage)"
        />
        <span class="gauge-label">{{ gauge.label }}</span>
        <span class="gauge-value">{{ gauge.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getFactorScoreColor } from '@/utils/colors'

export interface GaugeData {
  label: string
  percentage: number
  value: string
  width?: number
}

interface Props {
  gauges: GaugeData[]
}

defineProps<Props>()

// 使用统一的颜色工具函数
const getGaugeColor = getFactorScoreColor
</script>

<style scoped lang="scss">
.score-gauge {
  width: 100%;
}

.gauge-container {
  display: flex;
  justify-content: center;
  gap: 40px;
  flex-wrap: wrap;
}

.gauge-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.gauge-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.gauge-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
