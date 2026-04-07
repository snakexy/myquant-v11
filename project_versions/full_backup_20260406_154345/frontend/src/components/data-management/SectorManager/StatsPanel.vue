<template>
  <div class="stats-panel">
    <div class="stat-card primary">
      <div class="stat-icon">
        <font-awesome-icon icon="layer-group" />
      </div>
      <div class="stat-content">
        <div class="stat-value">{{ formatNumber(totalSectors) }}</div>
        <div class="stat-label">总板块数</div>
      </div>
    </div>

    <div class="stat-card success">
      <div class="stat-icon">
        <font-awesome-icon icon="check-square" />
      </div>
      <div class="stat-content">
        <div class="stat-value">{{ formatNumber(selectedCount) }}</div>
        <div class="stat-label">已选股票</div>
      </div>
    </div>

    <div class="stat-card warning">
      <div class="stat-icon">
        <font-awesome-icon icon="database" />
      </div>
      <div class="stat-content">
        <div class="stat-value">{{ formatNumber(totalStocks) }}</div>
        <div class="stat-label">覆盖股票</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatNumber } from '@/components/data-management/shared/utils'

interface Props {
  totalSectors: number
  selectedCount: number
  totalStocks: number
}

defineProps<Props>()
</script>

<style scoped>
.stats-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
}

.stat-card.primary {
  border-left: 4px solid #2962ff;
}

.stat-card.success {
  border-left: 4px solid #10b981;
}

.stat-card.warning {
  border-left: 4px solid #f59e0b;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 20px;
  color: white;
}

.stat-card.primary .stat-icon {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
}

.stat-card.success .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-card.warning .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-panel {
    grid-template-columns: 1fr;
  }
}
</style>
