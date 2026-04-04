<template>
  <div class="monitor">
    <h1>实时监控</h1>
    <div class="monitor-container">
      <MultiStockMonitor />
    </div>
  </div>
</template>

<script setup lang="ts">
import MultiStockMonitor from '../components/cards/MultiStockMonitor.vue'
</script>

<style lang="scss" scoped>
.monitor {
  padding: 24px;
  height: calc(100vh - 120px);
  
  h1 {
    margin: 0 0 24px 0;
    color: var(--text-primary);
  }
  
  .monitor-container {
    height: 100%;
  }
}
</style>