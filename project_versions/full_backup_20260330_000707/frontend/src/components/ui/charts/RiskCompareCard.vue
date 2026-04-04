<template>
  <div class="chart-card">
    <div class="chart-header">
      <div class="chart-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
          <path d="M2 17l10 5 10-5"></path>
          <path d="M2 12l10 5 10-5"></path>
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
  title: '风险指标对比'
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
