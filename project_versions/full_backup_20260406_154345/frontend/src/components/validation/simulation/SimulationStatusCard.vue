<template>
  <el-card class="status-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📊 模拟状态</span>
        <el-tag :type="getStatusTagType(simulationStatus)" size="small">
          {{ statusText }}
        </el-tag>
      </div>
    </template>

    <!-- 状态指示器 -->
    <div :class="['status-indicator', simulationStatus]">
      <div class="pulse-dot"></div>
      <span class="status-text">{{ statusDescription }}</span>
    </div>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-header">
          <el-icon class="metric-icon" color="#409EFF"><Money /></el-icon>
          <label class="metric-label">当前资产</label>
        </div>
        <div class="metric-value">
          ¥{{ formatNumber(metrics.currentAssets) }}
        </div>
        <div class="metric-change" :class="metrics.totalReturnRate >= 0 ? 'positive' : 'negative'">
          <el-icon><Top v-if="metrics.totalReturnRate >= 0" /><Bottom v-else /></el-icon>
          {{ metrics.totalReturnRate >= 0 ? '+' : '' }}{{ metrics.totalReturnRate.toFixed(2) }}%
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <el-icon class="metric-icon" color="#67C23A"><Wallet /></el-icon>
          <label class="metric-label">总收益</label>
        </div>
        <div class="metric-value" :class="metrics.totalReturn >= 0 ? 'positive-value' : 'negative-value'">
          {{ metrics.totalReturn >= 0 ? '+' : '' }}¥{{ formatNumber(metrics.totalReturn) }}
        </div>
        <div class="metric-desc">
          累计收益
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <el-icon class="metric-icon" color="#F56C6C"><TrendCharts /></el-icon>
          <label class="metric-label">最大回撤</label>
        </div>
        <div class="metric-value negative-value">
          {{ metrics.maxDrawdown.toFixed(2) }}%
        </div>
        <div class="metric-desc">
          历史最大
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <el-icon class="metric-icon" color="#E6A23C"><DataLine /></el-icon>
          <label class="metric-label">夏普比率</label>
        </div>
        <div class="metric-value">
          {{ metrics.sharpeRatio.toFixed(2) }}
        </div>
        <div class="metric-desc">
          风险调整收益
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <el-icon class="metric-icon" color="#909399"><Grid /></el-icon>
          <label class="metric-label">持仓数量</label>
        </div>
        <div class="metric-value">
          {{ metrics.positionCount }}
        </div>
        <div class="metric-desc">
          只股票
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <el-icon class="metric-icon" color="#909399"><Clock /></el-icon>
          <label class="metric-label">最后更新</label>
        </div>
        <div class="metric-value small">
          {{ formatTime(metrics.lastUpdateTime) }}
        </div>
        <div class="metric-desc">
          {{ formatRelativeTime(metrics.lastUpdateTime) }}
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Money, Wallet, TrendCharts, DataLine, Grid, Clock, Top, Bottom } from '@element-plus/icons-vue'
import type { SimulationMetrics, SimulationStatus } from '@/api/modules/simulation'

// Props
interface Props {
  simulationStatus: SimulationStatus
  metrics: SimulationMetrics
}

const props = withDefaults(defineProps<Props>(), {
  simulationStatus: 'stopped',
  metrics: () => ({
    currentAssets: 0,
    totalReturn: 0,
    totalReturnRate: 0,
    maxDrawdown: 0,
    sharpeRatio: 0,
    positionCount: 0,
    lastUpdateTime: ''
  })
})

// 计算状态文本
const statusText = computed(() => {
  const statusMap: Record<SimulationStatus, string> = {
    idle: '空闲',
    running: '运行中',
    paused: '已暂停',
    stopped: '已停止'
  }
  return statusMap[props.simulationStatus]
})

// 计算状态描述
const statusDescription = computed(() => {
  const descMap: Record<SimulationStatus, string> = {
    idle: '等待启动模拟',
    running: '模拟交易运行中',
    paused: '模拟已暂停',
    stopped: '模拟已停止'
  }
  return descMap[props.simulationStatus]
})

// 获取状态标签类型
const getStatusTagType = (status: SimulationStatus) => {
  const typeMap: Record<SimulationStatus, string> = {
    idle: 'info',
    running: 'success',
    paused: 'warning',
    stopped: 'danger'
  }
  return typeMap[status]
}

// 格式化数字
const formatNumber = (num: number) => {
  return Math.floor(num).toLocaleString('en-US')
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '--:--:--'
  const date = new Date(timeStr)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 格式化相对时间
const formatRelativeTime = (timeStr: string) => {
  if (!timeStr) return '未知'
  const now = Date.now()
  const time = new Date(timeStr).getTime()
  const diff = Math.floor((now - time) / 1000) // 秒

  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return `${Math.floor(diff / 86400)}天前`
}
</script>

<style scoped lang="scss">
.status-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 20px;

    &.idle {
      background-color: #f4f4f5;
      border: 1px solid #909399;

      .pulse-dot {
        background-color: #909399;
      }

      .status-text {
        color: #606266;
      }
    }

    &.running {
      background-color: #f0f9ff;
      border: 1px solid #3b82f6;

      .pulse-dot {
        background-color: #3b82f6;
        animation: pulse 2s infinite;
      }

      .status-text {
        color: #3b82f6;
        font-weight: 600;
      }
    }

    &.paused {
      background-color: #fffbeb;
      border: 1px solid #f59e0b;

      .pulse-dot {
        background-color: #f59e0b;
      }

      .status-text {
        color: #f59e0b;
        font-weight: 600;
      }
    }

    &.stopped {
      background-color: #fef2f2;
      border: 1px solid #ef4444;

      .pulse-dot {
        background-color: #ef4444;
      }

      .status-text {
        color: #ef4444;
        font-weight: 600;
      }
    }

    .pulse-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
    }

    .status-text {
      font-size: 14px;
    }
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;

    .metric-card {
      padding: 16px;
      background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
      border-radius: 8px;
      border: 1px solid #e5e7eb;

      .metric-header {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 12px;

        .metric-icon {
          font-size: 18px;
        }

        .metric-label {
          font-size: 13px;
          color: #6b7280;
          font-weight: 500;
        }
      }

      .metric-value {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        font-family: 'Consolas', 'Monaco', monospace;
        margin-bottom: 4px;

        &.small {
          font-size: 14px;
        }

        &.positive-value {
          color: #f56c6c;
        }

        &.negative-value {
          color: #67c23a;
        }
      }

      .metric-change {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Consolas', 'Monaco', monospace;

        &.positive {
          color: #f56c6c;
        }

        &.negative {
          color: #67c23a;
        }
      }

      .metric-desc {
        font-size: 12px;
        color: #9ca3af;
      }
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}
</style>
