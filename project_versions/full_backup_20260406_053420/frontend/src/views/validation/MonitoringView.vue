<template>
  <div class="monitoring-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">📡 实时监控</h1>
        <p class="page-subtitle">实时监控策略运行状态和风险指标</p>
      </div>
      <div class="header-right">
        <el-badge :value="alertCount" :hidden="alertCount === 0" class="item">
          <el-button @click="showAlerts = true">
            <el-icon><Bell /></el-icon>
            预警消息
          </el-button>
        </el-badge>
        <el-button @click="handleRefresh" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="handleBack">返回</el-button>
      </div>
    </div>

    <!-- 概览卡片 -->
    <OverviewCards v-if="overviewMetrics" :metrics="overviewMetrics" />

    <!-- 实时图表和风险指标 -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="16">
        <RealtimeChart />
      </el-col>

      <el-col :span="8">
        <RiskIndicatorPanel />
      </el-col>
    </el-row>

    <!-- 持仓和交易记录 -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card class="positions-card" shadow="never">
          <template #header>
            <span class="card-title">💼 当前持仓</span>
          </template>

          <el-table :data="positions" style="width: 100%" max-height="300">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="price" label="成本" width="80">
              <template #default="scope">
                ¥{{ scope.row.price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="currentPrice" label="现价" width="80">
              <template #default="scope">
                ¥{{ scope.row.currentPrice.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="profit" label="盈亏" width="100">
              <template #default="scope">
                <span :class="scope.row.profit >= 0 ? 'positive' : 'negative'">
                  {{ scope.row.profit >= 0 ? '+' : '' }}{{ scope.row.profit.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="trades-card" shadow="never">
          <template #header>
            <span class="card-title">📝 今日交易</span>
          </template>

          <el-table :data="trades" style="width: 100%" max-height="300">
            <el-table-column prop="time" label="时间" width="80" />
            <el-table-column prop="symbol" label="代码" width="80" />
            <el-table-column prop="type" label="类型" width="60">
              <template #default="scope">
                <el-tag :type="scope.row.type === '买入' ? 'success' : 'danger'" size="small">
                  {{ scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="price" label="价格" width="80">
              <template #default="scope">
                ¥{{ scope.row.price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="100">
              <template #default="scope">
                ¥{{ scope.row.amount.toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预警消息抽屉 -->
    <el-drawer v-model="showAlerts" title="预警消息" size="400px">
      <div class="alert-list">
        <div
          v-for="alert in alertList"
          :key="alert.id"
          class="alert-item"
          :class="'alert-' + alert.type"
        >
          <div class="alert-icon">
            <el-icon v-if="alert.type === 'warning'"><Warning /></el-icon>
            <el-icon v-else-if="alert.type === 'error'"><CircleClose /></el-icon>
            <el-icon v-else><InfoFilled /></el-icon>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-message">{{ alert.message }}</div>
            <div class="alert-time">{{ alert.time }}</div>
          </div>
          <el-button size="small" text @click="dismissAlert(alert.id)">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>

        <el-empty v-if="alertList.length === 0" description="暂无预警消息" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Bell, Refresh, Top, Bottom, Minus,
  TrendCharts, Money, DataLine, Warning,
  InfoFilled, CircleClose, Close
} from '@element-plus/icons-vue'
import { monitoringApi } from '@/api/modules/monitoring'
import type { OverviewMetrics, RiskMetrics, Position, Trade, AlertMessage, TimePeriod } from '@/api/modules/monitoring'
import OverviewCards from '@/components/validation/monitoring/OverviewCards.vue'
import RealtimeChart from '@/components/validation/monitoring/RealtimeChart.vue'
import RiskIndicatorPanel from '@/components/validation/monitoring/RiskIndicatorPanel.vue'

const router = useRouter()
const showAlerts = ref(false)
const refreshing = ref(false)

// 概览指标数据
const overviewMetrics = ref<OverviewMetrics | null>(null)

// 持仓数据
const positions = ref<Position[]>([])

// 交易记录
const trades = ref<Trade[]>([])

// 预警消息列表
const alertList = ref<AlertMessage[]>([])

let refreshInterval: number | null = null

// 加载概览指标
const loadOverview = async () => {
  try {
    const response = await monitoringApi.getOverview()
    if (response.code === 200) {
      overviewMetrics.value = response.data
    }
  } catch (error) {
    console.error('加载概览指标失败:', error)
    // 降级方案：使用默认值
    overviewMetrics.value = {
      currentAssets: 1000000,
      totalReturn: 0,
      totalReturnRate: 0,
      maxDrawdown: 0,
      sharpeRatio: 0,
      updateTime: new Date().toISOString(),
      trends: {
        assets: 'flat',
        return: 'flat',
        drawdown: 'flat',
        sharpe: 'flat'
      }
    }
  }
}

// 加载持仓数据
const loadPositions = async () => {
  try {
    const response = await monitoringApi.getPositions()
    if (response.code === 200) {
      positions.value = response.data
    }
  } catch (error) {
    console.error('加载持仓数据失败:', error)
    // 降级方案：使用默认持仓数据
    positions.value = []
  }
}

// 加载交易记录
const loadTrades = async () => {
  try {
    const response = await monitoringApi.getTrades(50)
    if (response.code === 200) {
      trades.value = response.data.map(trade => ({
        ...trade,
        time: new Date(trade.time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      }))
    }
  } catch (error) {
    console.error('加载交易记录失败:', error)
    // 降级方案
    trades.value = []
  }
}

// 加载预警消息
const loadAlerts = async () => {
  try {
    const response = await monitoringApi.getAlerts(false)
    if (response.code === 200) {
      alertList.value = response.data.map(alert => ({
        ...alert,
        time: formatTimeAgo(alert.time)
      }))
    }
  } catch (error) {
    console.error('加载预警消息失败:', error)
    // 降级方案
    alertList.value = []
  }
}

// 格式化时间为"XX前"格式
const formatTimeAgo = (time: string): string => {
  const now = Date.now()
  const past = new Date(time).getTime()
  const diff = now - past

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

// 刷新所有数据
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      loadOverview(),
      loadPositions(),
      loadTrades(),
      loadAlerts()
    ])
    ElMessage.success('数据已刷新')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 关闭/删除预警
const dismissAlert = async (id: string | number) => {
  try {
    const response = await monitoringApi.deleteAlert(String(id))
    if (response.code === 200) {
      alertList.value = alertList.value.filter(alert => alert.id !== id)
      ElMessage.success('预警已删除')
    }
  } catch (error) {
    console.error('删除预警失败:', error)
    ElMessage.error('删除失败')
  }
}

// 返回
const handleBack = () => {
  router.back()
}

// 实时数据更新
const startRealtimeUpdate = () => {
  refreshInterval = window.setInterval(async () => {
    try {
      // 只更新持仓价格，不重新加载整个列表
      const response = await monitoringApi.getPositions()
      if (response.code === 200) {
        const updatedPositions = response.data
        positions.value.forEach(pos => {
          const updated = updatedPositions.find(p => p.symbol === pos.symbol)
          if (updated) {
            pos.currentPrice = updated.currentPrice
            pos.profit = updated.profit
            pos.profitRate = updated.profitRate
          }
        })
      }
    } catch (error) {
      console.error('实时更新失败:', error)
    }
  }, 5000) // 每5秒更新一次
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadOverview(),
    loadPositions(),
    loadTrades(),
    loadAlerts()
  ])
  startRealtimeUpdate()
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped lang="scss">
.monitoring-view {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      .page-title {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 8px 0;
      }

      .page-subtitle {
        font-size: 14px;
        color: #909399;
        margin: 0;
      }
    }

    .header-right {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .chart-card,
  .risk-card,
  .positions-card,
  .trades-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .chart-card {
    .return-chart-container {
      .chart-placeholder {
        padding: 20px;
        background: linear-gradient(180deg, rgba(64, 158, 255, 0.05) 0%, rgba(64, 158, 255, 0.02) 100%);
        border-radius: 8px;

        .chart-metrics {
          display: flex;
          justify-content: space-around;
          margin-bottom: 20px;

          .metric-item {
            text-align: center;

            .metric-label {
              font-size: 12px;
              color: #909399;
              display: block;
              margin-bottom: 4px;
            }

            .metric-value {
              font-size: 16px;
              font-weight: 600;

              &.positive {
                color: #f56c6c;
              }

              &.negative {
                color: #67c23a;
              }
            }
          }
        }

        .chart-visual {
          position: relative;
          height: 200px;
          margin: 20px 0;

          .chart-line {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 100%;
            background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
            clip-path: polygon(
              0% 80%, 10% 75%, 20% 78%, 30% 70%, 40% 72%, 50% 65%,
              60% 68%, 70% 60%, 80% 55%, 90% 50%, 100% 45%, 100% 100%, 0% 100%
            );
            opacity: 0.3;
          }

          .chart-area {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 100%;
            border-left: 2px solid #409eff;
            border-bottom: 2px solid #409eff;
          }
        }

        .chart-time {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .risk-card {
    .risk-indicators {
      .risk-item {
        margin-bottom: 20px;

        &:last-child {
          margin-bottom: 0;
        }

        .risk-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .risk-label {
            font-size: 14px;
            color: #606266;
            font-weight: 500;
          }
        }

        .risk-value {
          font-size: 18px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 8px;

          .risk-threshold {
            font-size: 12px;
            color: #909399;
            font-weight: normal;
            margin-left: 8px;
          }

          &.positive {
            color: #f56c6c;
          }

          &.negative {
            color: #67c23a;
          }

          &.warning {
            color: #e6a23c;
          }
        }
      }
    }
  }

  .alert-list {
    .alert-item {
      display: flex;
      gap: 12px;
      padding: 16px;
      background-color: #f5f7fa;
      border-radius: 8px;
      margin-bottom: 12px;

      &.alert-warning {
        background-color: #fdf6ec;
        border-left: 4px solid #e6a23c;
      }

      &.alert-error {
        background-color: #fef0f0;
        border-left: 4px solid #f56c6c;
      }

      &.alert-info {
        background-color: #f4f4f5;
        border-left: 4px solid #909399;
      }

      .alert-icon {
        font-size: 24px;

        .alert-warning & {
          color: #e6a23c;
        }

        .alert-error & {
          color: #f56c6c;
        }

        .alert-info & {
          color: #909399;
        }
      }

      .alert-content {
        flex: 1;

        .alert-title {
          font-size: 14px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 4px;
        }

        .alert-message {
          font-size: 12px;
          color: #606266;
          margin-bottom: 8px;
        }

        .alert-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}

.positive {
  color: #f56c6c !important;
}

.negative {
  color: #67c23a !important;
}

.warning {
  color: #e6a23c !important;
}
</style>
