<template>
  <div class="chart-card">
    <div class="chart-header">
      <div class="chart-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="16"></line>
          <line x1="8" y1="12" x2="16" y2="12"></line>
        </svg>
        {{ title }}
      </div>
    </div>
    <div class="chart-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
}

withDefaults(defineProps<Props>(), {
  title: '因子权重'
})
</script>

<style lang="scss" scoped>
.chart-card {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.chart-header {
  flex-shrink: 0;
  padding-bottom: 12px;
}

.chart-title {
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-md {
  width: 18px;
  height: 18px;
  color: #ff9800;
}

.chart-content {
  flex: 1;
  min-height: 120px;
}
</style>
