<template>
  <div class="database-overview">
    <div class="overview-header">
      <h3>数据库概览</h3>
      <el-button
        size="small"
        @click="$emit('refresh')"
        :loading="loading"
        type="primary"
      >
        <font-awesome-icon icon="sync-alt" :spin="loading" />
        刷新
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div v-if="stats" class="stats-grid">
      <div class="stat-card primary">
        <div class="stat-icon">
          <font-awesome-icon icon="database" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(stats.totalStocks) }}</div>
          <div class="stat-label">总股票数</div>
        </div>
      </div>

      <div class="stat-card warning">
        <div class="stat-icon">
          <font-awesome-icon icon="exclamation-triangle" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(stats.needsUpdate) }}</div>
          <div class="stat-label">需要更新</div>
        </div>
      </div>

      <div class="stat-card success">
        <div class="stat-icon">
          <font-awesome-icon icon="check-circle" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(stats.healthyStocks) }}</div>
          <div class="stat-label">数据健康</div>
        </div>
      </div>

      <div class="stat-card info">
        <div class="stat-icon">
          <font-awesome-icon icon="calendar-alt" />
        </div>
        <div class="stat-content">
          <div class="stat-value text-small">{{ formatDateRange(stats.dateRange) }}</div>
          <div class="stat-label">数据范围</div>
        </div>
      </div>
    </div>

    <!-- 空状态提示 -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <font-awesome-icon icon="database" size="3x" />
      </div>
      <div class="empty-text">
        <h4>暂无数据库信息</h4>
        <p>点击"刷新"按钮扫描数据库</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatNumber } from '@/components/data-management/shared/utils'

interface DatabaseStats {
  totalStocks: number
  needsUpdate: number
  healthyStocks: number
  dateRange: {
    start: string
    end: string
  }
}

interface Props {
  stats?: DatabaseStats | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  stats: null,
  loading: false
})

defineEmits<{
  refresh: []
}>()

// 格式化日期范围
const formatDateRange = (range: any) => {
  if (!range) return '暂无数据'

  // 支持多种格式：
  // 1. {start: '2020-01-01', end: '2025-01-09'}
  // 2. {earliest: '2020-01-01', latest: '2025-01-09'}
  // 3. 字符串 "2020-01-01 至 2025-01-09"

  // 如果已经是格式化的字符串，直接返回
  if (typeof range === 'string') {
    return range.includes(' 至 ') ? range : range
  }

  // 提取开始和结束日期
  const start = range.start || range.earliest || null
  const end = range.end || range.latest || null

  // 如果都没有，返回占位符
  if (!start && !end) {
    return '暂无数据'
  }

  // 格式化单个日期
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '未知'
    if (dateStr === 'N/A' || dateStr === '~' || dateStr === '-') return '未知'

    // 如果日期包含时间部分，只显示日期
    if (dateStr.includes(' ')) {
      return dateStr.split(' ')[0]
    }

    return dateStr
  }

  const startClean = formatDate(start)
  const endClean = formatDate(end)

  return `${startClean} 至 ${endClean}`
}
</script>

<style scoped>
.database-overview {
  margin-bottom: 20px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.overview-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
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
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card.primary {
  border-left: 4px solid #2962ff;
}

.stat-card.warning {
  border-left: 4px solid #f59e0b;
}

.stat-card.success {
  border-left: 4px solid #10b981;
}

.stat-card.info {
  border-left: 4px solid #3b82f6;
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

.stat-card.warning .stat-icon {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.stat-card.success .stat-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.stat-card.info .stat-icon {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
}

.stat-value.text-small {
  font-size: 14px;
  font-weight: 500;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  color: rgba(255, 255, 255, 0.2);
  margin-bottom: 16px;
}

.empty-text h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.empty-text p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
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

  .overview-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
