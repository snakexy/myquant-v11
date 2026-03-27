<template>
  <el-card class="risk-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="card-title">⚠️ 风险指标</span>
        <el-button size="small" @click="handleRefresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </template>

    <div v-if="loading && !riskMetrics" class="risk-loading">
      <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    <div v-else-if="error" class="risk-error">
      <el-icon :size="24"><WarningFilled /></el-icon>
      <span>{{ error }}</span>
    </div>
    <div v-else class="risk-indicators">
      <!-- 最大回撤 -->
      <div class="risk-item">
        <div class="risk-header">
          <span class="risk-label">最大回撤</span>
          <el-tag :type="getDrawdownLevel(riskMetrics!.maxDrawdown)" size="small">
            {{ getDrawdownLevelText(riskMetrics!.maxDrawdown) }}
          </el-tag>
        </div>
        <div class="risk-value" :class="getDrawdownValueClass(riskMetrics!.maxDrawdown)">
          -{{ riskMetrics!.maxDrawdown.toFixed(2) }}%
          <span class="risk-threshold">/ 阈值: -5.00%</span>
        </div>
        <el-progress
          :percentage="getDrawdownPercentage(riskMetrics!.maxDrawdown)"
          :color="getDrawdownColor(riskMetrics!.maxDrawdown)"
          :show-text="false"
          size="small"
        />
      </div>

      <el-divider style="margin: 16px 0;" />

      <!-- 杠杆率 -->
      <div class="risk-item">
        <div class="risk-header">
          <span class="risk-label">杠杆率</span>
          <el-tag :type="getLeverageLevel(riskMetrics!.leverage)" size="small">
            {{ getLeverageLevelText(riskMetrics!.leverage) }}
          </el-tag>
        </div>
        <div class="risk-value">
          {{ riskMetrics!.leverage.toFixed(2) }}
          <span class="risk-threshold">/ 阈值: 2.0</span>
        </div>
        <el-progress
          :percentage="getLeveragePercentage(riskMetrics!.leverage)"
          :color="getLeverageColor(riskMetrics!.leverage)"
          :show-text="false"
          size="small"
        />
      </div>

      <el-divider style="margin: 16px 0;" />

      <!-- 集中度 -->
      <div class="risk-item">
        <div class="risk-header">
          <span class="risk-label">集中度</span>
          <el-tag :type="getConcentrationLevel(riskMetrics!.concentration)" size="small">
            {{ getConcentrationLevelText(riskMetrics!.concentration) }}
          </el-tag>
        </div>
        <div class="risk-value" :class="getConcentrationValueClass(riskMetrics!.concentration)">
          {{ riskMetrics!.concentration.toFixed(0) }}%
          <span class="risk-threshold">/ 阈值: 50%</span>
        </div>
        <el-progress
          :percentage="riskMetrics!.concentration"
          :color="getConcentrationColor(riskMetrics!.concentration)"
          :show-text="false"
          size="small"
        />
      </div>

      <el-divider style="margin: 16px 0;" />

      <!-- 波动率 -->
      <div class="risk-item">
        <div class="risk-header">
          <span class="risk-label">波动率</span>
          <el-tag :type="getVolatilityLevel(riskMetrics!.volatility)" size="small">
            {{ getVolatilityLevelText(riskMetrics!.volatility) }}
          </el-tag>
        </div>
        <div class="risk-value">
          {{ riskMetrics!.volatility.toFixed(1) }}%
          <span class="risk-threshold">/ 阈值: 20%</span>
        </div>
        <el-progress
          :percentage="getVolatilityPercentage(riskMetrics!.volatility)"
          :color="getVolatilityColor(riskMetrics!.volatility)"
          :show-text="false"
          size="small"
        />
      </div>

      <!-- 整体风险状态 -->
      <div class="risk-status">
        <div class="status-label">整体风险</div>
        <div :class="['status-value', getStatusClass(riskMetrics!.status)]">
          {{ getStatusText(riskMetrics!.status) }}
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Loading, WarningFilled } from '@element-plus/icons-vue'
import { monitoringApi } from '@/api/modules/monitoring'
import type { RiskMetrics } from '@/api/modules/monitoring'

// Props
interface Props {
  autoRefresh?: boolean
  refreshInterval?: number // 秒
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: false,
  refreshInterval: 60
})

// Emits
const emit = defineEmits<{
  dataLoaded: [data: RiskMetrics]
  statusChange: [status: 'normal' | 'attention' | 'warning']
}>()

// State
const riskMetrics = ref<RiskMetrics | null>(null)
const loading = ref(false)
const error = ref('')

let refreshTimer: number | null = null

// 加载风险指标
const loadRiskMetrics = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await monitoringApi.getRiskMetrics()
    if (response.code === 200) {
      riskMetrics.value = response.data
      emit('dataLoaded', response.data)
      emit('statusChange', response.data.status)
    } else {
      error.value = '加载失败'
      ElMessage.error('加载风险指标失败')
    }
  } catch (err) {
    console.error('加载风险指标失败:', err)
    error.value = '加载失败'
    // 使用模拟数据作为降级方案
    riskMetrics.value = generateMockData()
    emit('dataLoaded', riskMetrics.value)
    ElMessage.warning('使用模拟数据')
  } finally {
    loading.value = false
  }
}

// 生成模拟数据
const generateMockData = (): RiskMetrics => {
  return {
    maxDrawdown: 2.5 + Math.random() * 3, // 2.5-5.5%
    leverage: 0.8 + Math.random() * 0.8, // 0.8-1.6
    concentration: 30 + Math.random() * 40, // 30-70%
    volatility: 10 + Math.random() * 15, // 10-25%
    status: 'normal'
  }
}

// 最大回撤相关方法
const getDrawdownLevel = (value: number) => {
  if (value < 3) return 'success'
  if (value < 4) return 'warning'
  return 'danger'
}

const getDrawdownLevelText = (value: number) => {
  if (value < 3) return '正常'
  if (value < 4) return '注意'
  return '警告'
}

const getDrawdownValueClass = (value: number) => {
  if (value >= 3) return 'negative'
  return ''
}

const getDrawdownPercentage = (value: number) => {
  return Math.min((value / 5) * 100, 100)
}

const getDrawdownColor = (value: number) => {
  if (value < 3) return '#67c23a'
  if (value < 4) return '#e6a23c'
  return '#f56c6c'
}

// 杠杆率相关方法
const getLeverageLevel = (value: number) => {
  if (value < 1.5) return 'success'
  if (value < 1.8) return 'warning'
  return 'danger'
}

const getLeverageLevelText = (value: number) => {
  if (value < 1.5) return '正常'
  if (value < 1.8) return '注意'
  return '警告'
}

const getLeveragePercentage = (value: number) => {
  return Math.min((value / 2) * 100, 100)
}

const getLeverageColor = (value: number) => {
  if (value < 1.5) return '#67c23a'
  if (value < 1.8) return '#e6a23c'
  return '#f56c6c'
}

// 集中度相关方法
const getConcentrationLevel = (value: number) => {
  if (value < 40) return 'success'
  if (value < 50) return 'warning'
  return 'danger'
}

const getConcentrationLevelText = (value: number) => {
  if (value < 40) return '正常'
  if (value < 50) return '注意'
  return '警告'
}

const getConcentrationValueClass = (value: number) => {
  if (value >= 40) return 'warning'
  return ''
}

const getConcentrationColor = (value: number) => {
  if (value < 40) return '#67c23a'
  if (value < 50) return '#e6a23c'
  return '#f56c6c'
}

// 波动率相关方法
const getVolatilityLevel = (value: number) => {
  if (value < 15) return 'success'
  if (value < 18) return 'warning'
  return 'danger'
}

const getVolatilityLevelText = (value: number) => {
  if (value < 15) return '正常'
  if (value < 18) return '注意'
  return '警告'
}

const getVolatilityPercentage = (value: number) => {
  return Math.min((value / 20) * 100, 100)
}

const getVolatilityColor = (value: number) => {
  if (value < 15) return '#67c23a'
  if (value < 18) return '#e6a23c'
  return '#f56c6c'
}

// 整体状态相关方法
const getStatusClass = (status: 'normal' | 'attention' | 'warning') => {
  if (status === 'normal') return 'status-normal'
  if (status === 'attention') return 'status-attention'
  return 'status-warning'
}

const getStatusText = (status: 'normal' | 'attention' | 'warning') => {
  if (status === 'normal') return '正常'
  if (status === 'attention') return '注意'
  return '警告'
}

// 刷新
const handleRefresh = () => {
  loadRiskMetrics()
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (!props.autoRefresh) return

  refreshTimer = window.setInterval(() => {
    loadRiskMetrics()
  }, props.refreshInterval * 1000)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  loadRiskMetrics()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

// 暴露方法给父组件
defineExpose({
  refresh: loadRiskMetrics,
  getData: () => riskMetrics.value
})
</script>

<style scoped lang="scss">
.risk-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .risk-loading,
  .risk-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 40px 20px;
    color: #909399;

    .el-icon {
      font-size: 24px;
    }

    span {
      font-size: 14px;
    }
  }

  .risk-indicators {
    .risk-item {
      margin-bottom: 4px;

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
        font-family: 'Consolas', 'Monaco', monospace;

        .risk-threshold {
          font-size: 12px;
          color: #909399;
          font-weight: normal;
          margin-left: 8px;
        }

        &.negative {
          color: #67c23a;
        }

        &.warning {
          color: #e6a23c;
        }
      }
    }

    .risk-status {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px;
      margin-top: 16px;
      background-color: #f5f7fa;
      border-radius: 6px;

      .status-label {
        font-size: 14px;
        color: #606266;
        font-weight: 500;
      }

      .status-value {
        font-size: 16px;
        font-weight: 600;

        &.status-normal {
          color: #67c23a;
        }

        &.status-attention {
          color: #e6a23c;
        }

        &.status-warning {
          color: #f56c6c;
        }
      }
    }
  }
}
</style>
