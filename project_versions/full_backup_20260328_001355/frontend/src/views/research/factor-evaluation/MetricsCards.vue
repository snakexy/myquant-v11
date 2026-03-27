<template>
  <div class="metrics-cards">
    <div
      v-for="metric in metrics"
      :key="metric.key"
      class="metric-card"
    >
      <div class="metric-icon" :style="{ color: metric.iconColor }">
        <component :is="metric.icon" v-if="typeof metric.icon === 'object'" />
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" v-html="metric.icon" />
      </div>
      <div class="metric-label">{{ metric.label }}</div>
      <div class="metric-value" :class="metric.valueClass">
        {{ metric.value }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface MetricCard {
  key: string
  label: string
  value: string
  icon: string | object
  valueClass?: string
  iconColor?: string
}

interface Props {
  metrics: MetricCard[]
}

defineProps<Props>()
</script>

<style scoped lang="scss">
.metrics-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.metric-icon {
  width: 28px;
  height: 28px;
  color: var(--text-secondary);
}

.metric-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-align: center;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);

  &.excellent {
    color: var(--accent-blue);
  }

  &.good {
    color: var(--accent-green);
  }

  &.average {
    color: var(--accent-orange);
  }

  &.poor {
    color: var(--accent-red);
  }
}
</style>
