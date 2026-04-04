<template>
  <div class="overview-cards">
    <!-- 总资产卡片 -->
    <div class="metric-card">
      <div class="card-header">
        <el-icon class="card-icon" color="#409EFF"><Wallet /></el-icon>
        <span class="card-label">总资产</span>
      </div>
      <div class="card-value">
        ¥{{ formatNumber(metrics.currentAssets) }}
      </div>
      <div :class="['card-trend', getTrendClass(metrics.trends.assets)]">
        <el-icon>
          <Top v-if="metrics.trends.assets === 'up'" />
          <Bottom v-else-if="metrics.trends.assets === 'down'" />
          <Minus v-else />
        </el-icon>
        <span>{{ getTrendText(metrics.trends.assets) }}</span>
      </div>
    </div>

    <!-- 总收益率卡片 -->
    <div class="metric-card">
      <div class="card-header">
        <el-icon class="card-icon" color="#67C23A"><TrendCharts /></el-icon>
        <span class="card-label">总收益率</span>
      </div>
      <div :class="['card-value', getValueClass(metrics.totalReturnRate)]">
        {{ metrics.totalReturnRate >= 0 ? '+' : '' }}{{ metrics.totalReturnRate.toFixed(2) }}%
      </div>
      <div :class="['card-trend', getTrendClass(metrics.trends.return)]">
        <el-icon>
          <Top v-if="metrics.trends.return === 'up'" />
          <Bottom v-else-if="metrics.trends.return === 'down'" />
          <Minus v-else />
        </el-icon>
        <span>{{ getTrendText(metrics.trends.return) }}</span>
      </div>
    </div>

    <!-- 最大回撤卡片 -->
    <div class="metric-card">
      <div class="card-header">
        <el-icon class="card-icon" color="#F56C6C"><DataLine /></el-icon>
        <span class="card-label">最大回撤</span>
      </div>
      <div class="card-value negative">
        {{ metrics.maxDrawdown.toFixed(2) }}%
      </div>
      <div :class="['card-trend', getTrendClass(metrics.trends.drawdown, true)]">
        <el-icon>
          <Top v-if="metrics.trends.drawdown === 'up'" />
          <Bottom v-else-if="metrics.trends.drawdown === 'down'" />
          <Minus v-else />
        </el-icon>
        <span>{{ getTrendText(metrics.trends.drawdown, true) }}</span>
      </div>
    </div>

    <!-- 夏普比率卡片 -->
    <div class="metric-card">
      <div class="card-header">
        <el-icon class="card-icon" color="#E6A23C"><Odometer /></el-icon>
        <span class="card-label">夏普比率</span>
      </div>
      <div :class="['card-value', getSharpeClass(metrics.sharpeRatio)]">
        {{ metrics.sharpeRatio.toFixed(2) }}
      </div>
      <div :class="['card-trend', getTrendClass(metrics.trends.sharpe)]">
        <el-icon>
          <Top v-if="metrics.trends.sharpe === 'up'" />
          <Bottom v-else-if="metrics.trends.sharpe === 'down'" />
          <Minus v-else />
        </el-icon>
        <span>{{ getTrendText(metrics.trends.sharpe) }}</span>
      </div>
    </div>

    <!-- 更新时间 -->
    <div class="update-time">
      <el-icon><Clock /></el-icon>
      <span>更新于 {{ formatRelativeTime(metrics.updateTime) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Wallet, TrendCharts, DataLine, Odometer, Top, Bottom, Minus, Clock } from '@element-plus/icons-vue'
import type { OverviewMetrics } from '@/api/modules/monitoring'

// Props
interface Props {
  metrics: OverviewMetrics
}

const props = defineProps<Props>()

// 格式化数字
const formatNumber = (num: number) => {
  return Math.floor(num).toLocaleString('en-US')
}

// 获取趋势样式类
const getTrendClass = (trend: 'up' | 'down' | 'flat', inverse = false) => {
  if (trend === 'flat') return 'flat'
  if (inverse) {
    // 对于回撤等反向指标，上涨是坏事，下跌是好事
    return trend === 'up' ? 'negative' : 'positive'
  }
  return trend === 'up' ? 'positive' : 'negative'
}

// 获取数值样式类（收益率）
const getValueClass = (value: number) => {
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return ''
}

// 获取夏普比率样式类
const getSharpeClass = (value: number) => {
  if (value >= 1) return 'positive'
  if (value >= 0.5) return 'neutral'
  return 'negative'
}

// 获取趋势文本
const getTrendText = (trend: 'up' | 'down' | 'flat', inverse = false) => {
  if (trend === 'flat') return '持平'
  if (inverse) {
    return trend === 'up' ? '上升' : '下降'
  }
  return trend === 'up' ? '上升' : '下降'
}

// 格式化相对时间
const formatRelativeTime = (timeStr: string) => {
  const now = new Date()
  const time = new Date(timeStr)
  const diffMs = now.getTime() - time.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}小时前`

  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}天前`
}
</script>

<style scoped lang="scss">
.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;

  .metric-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;

    &:hover {
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      transform: translateY(-2px);
    }

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    &:hover::before {
      opacity: 1;
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;

      .card-icon {
        font-size: 24px;
      }

      .card-label {
        font-size: 14px;
        color: #909399;
        font-weight: 500;
      }
    }

    .card-value {
      font-size: 28px;
      font-weight: 700;
      color: #303133;
      font-family: 'Consolas', 'Monaco', monospace;
      margin-bottom: 8px;

      &.positive {
        color: #f56c6c; // 红色表示盈利
      }

      &.negative {
        color: #67c23a; // 绿色表示亏损
      }

      &.neutral {
        color: #E6A23C;
      }
    }

    .card-trend {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      font-weight: 500;

      &.positive {
        color: #f56c6c;
      }

      &.negative {
        color: #67c23a;
      }

      &.flat {
        color: #909399;
      }

      .el-icon {
        font-size: 16px;
      }
    }
  }

  .update-time {
    grid-column: 1 / -1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px;
    font-size: 13px;
    color: #909399;
    background-color: #f5f7fa;
    border-radius: 6px;

    .el-icon {
      font-size: 14px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: 1fr;
  }
}
</style>
