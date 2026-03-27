<template>
  <div class="stats-info-container">
    <div class="stats-grid">
      <div class="stat-card primary">
        <div class="stat-icon">
          <font-awesome-icon icon="database" />
        </div>
        <div class="stat-content">
          <div class="stat-label">数据记录</div>
          <div class="stat-value">{{ formatNumber(stats.recordCount) }}</div>
        </div>
      </div>

      <div class="stat-card success">
        <div class="stat-icon">
          <font-awesome-icon icon="calendar-alt" />
        </div>
        <div class="stat-content">
          <div class="stat-label">时间范围</div>
          <div class="stat-value text-small">{{ stats.dateRange }}</div>
        </div>
      </div>

      <div class="stat-card" :class="getCompletenessClass(stats.completeness)">
        <div class="stat-icon">
          <font-awesome-icon icon="check-circle" />
        </div>
        <div class="stat-content">
          <div class="stat-label">数据完整度</div>
          <div class="stat-value">{{ stats.completeness }}%</div>
        </div>
      </div>

      <div class="stat-card warning">
        <div class="stat-icon">
          <font-awesome-icon icon="clock" />
        </div>
        <div class="stat-content">
          <div class="stat-label">最新更新</div>
          <div class="stat-value text-small">{{ stats.lastUpdate }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatNumber } from '@/components/data-management/shared/utils'

interface StockStats {
  recordCount: number
  dateRange: string
  completeness: number
  lastUpdate: string
}

interface Props {
  stats: StockStats
}

defineProps<Props>()

// 获取完整度样式类
const getCompletenessClass = (completeness: number) => {
  if (completeness >= 95) return 'success'
  if (completeness >= 80) return 'warning'
  return 'danger'
}
</script>

<style scoped>
.stats-info-container {
  padding: 16px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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

.stat-card.danger {
  border-left: 4px solid #ef4444;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.15);
  border-radius: 8px;
  font-size: 20px;
  color: #2962ff;
}

.stat-card.success .stat-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.stat-card.warning .stat-icon {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.stat-card.danger .stat-icon {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}

.stat-value.text-small {
  font-size: 13px;
  font-weight: 500;
}

.stat-card.success .stat-value {
  color: #10b981;
}

.stat-card.warning .stat-value {
  color: #f59e0b;
}

.stat-card.danger .stat-value {
  color: #ef4444;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
