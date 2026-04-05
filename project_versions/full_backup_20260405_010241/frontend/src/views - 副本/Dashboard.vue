<template>
  <div class="dashboard-container">
    <div class="function-cards">
      <!-- 功能卡片容器 -->
      <div class="function-card">
        <h3>数据概览</h3>
        <p>查看数据库统计、数据新鲜度、股票数量</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Dashboard页面逻辑
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.dashboard-container {
  width: 100%;
  height: 100%;
  background: var(--bg-deep);
  padding: var(--spacing-4);
  position: relative;
  z-index: 1;
}

.function-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-4);
}

.function-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-4);
  transition: all var(--transition-duration-base) var(--transition-timing-function-base);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
  
  h3 {
    margin: 0 0 var(--spacing-2) 0;
    color: var(--text-primary);
  }
  
  p {
    margin: 0;
    color: var(--text-secondary);
  }
}
</style>