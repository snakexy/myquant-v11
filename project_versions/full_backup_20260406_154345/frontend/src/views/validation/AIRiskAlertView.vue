<template>
  <div class="ai-risk-alert-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">🤖 AI智能预警</h1>
        <p class="page-subtitle">基于QLib原生的AI风险监控与预测</p>
      </div>
      <div class="header-right">
        <el-button @click="handleRefresh" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="handleBack">返回</el-button>
      </div>
    </div>

    <!-- AI风险摘要卡片 -->
    <el-row :gutter="16" class="summary-cards">
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="card-content">
            <div class="card-icon anomaly">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-label">总风险信号</div>
              <div class="card-value">{{ riskSummary.total_signals }}</div>
              <div class="card-sub">24小时: {{ riskSummary.recent_signals }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="card-content">
            <div class="card-icon prediction">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-label">活跃AI模型</div>
              <div class="card-value">{{ riskSummary.active_models?.length || 0 }}</div>
              <div class="card-sub">监控中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="card-content">
            <div class="card-icon confidence">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-label">平均置信度</div>
              <div class="card-value">{{ averageConfidence }}%</div>
              <div class="card-sub">AI预测精度</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="card-content">
            <div class="card-icon symbols">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-label">监控标的</div>
              <div class="card-value">{{ riskSummary.monitored_symbols || 0 }}</div>
              <div class="card-sub">实时分析</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主内容区域 -->
    <el-row :gutter="16">
      <!-- 左侧：AI风险信号 -->
      <el-col :span="16">
        <!-- 实时风险信号 -->
        <el-card class="signals-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>🎯 实时AI风险信号</span>
              <el-radio-group v-model="signalFilter" size="small" @change="filterSignals">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="critical">严重</el-radio-button>
                <el-radio-button label="recent">最近24小时</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <div class="signals-list">
            <el-empty v-if="filteredSignals.length === 0" description="暂无风险信号" />

            <div
              v-for="signal in filteredSignals"
              :key="signal.id"
              class="signal-item"
              :class="getRiskClass(signal)"
            >
              <div class="signal-header">
                <div class="signal-type">
                  <el-tag :type="getSignalTagType(signal.risk_type)" size="small">
                    {{ getRiskTypeName(signal.risk_type) }}
                  </el-tag>
                  <el-tag
                    v-if="signal.confidence >= 0.8"
                    type="danger"
                    size="small"
                    effect="plain"
                  >
                    高置信度
                  </el-tag>
                </div>
                <div class="signal-time">{{ formatTime(signal.timestamp) }}</div>
              </div>

              <div class="signal-prediction">
                <strong>预测:</strong> {{ signal.prediction }}
              </div>

              <div class="signal-factors">
                <div class="factors-label">风险因子:</div>
                <div class="factors-list">
                  <el-tag
                    v-for="(value, key) in signal.factors"
                    :key="key"
                    size="small"
                    type="info"
                    effect="plain"
                  >
                    {{ key }}: {{ formatFactorValue(value) }}
                  </el-tag>
                </div>
              </div>

              <div class="signal-recommendation">
                <el-icon><InfoFilled /></el-icon>
                <span>AI建议: {{ signal.recommendation }}</span>
              </div>

              <div class="signal-confidence">
                <div class="confidence-label">置信度</div>
                <el-progress
                  :percentage="Math.round(signal.confidence * 100)"
                  :color="getConfidenceColor(signal.confidence)"
                  :show-text="true"
                />
              </div>
            </div>
          </div>
        </el-card>

        <!-- AI模型状态 -->
        <el-card class="models-card" shadow="never" style="margin-top: 16px">
          <template #header>
            <span>🧠 AI模型状态</span>
          </template>

          <el-table :data="aiModels" size="small">
            <el-table-column prop="name" label="模型名称" width="180">
              <template #default="{ row }">
                <strong>{{ getModelDisplayName(row.name) }}</strong>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag
                  :type="getModelStatusTagType(row.status)"
                  size="small"
                >
                  {{ getModelStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="accuracy" label="准确率" width="100">
              <template #default="{ row }">
                <span v-if="row.accuracy">{{ (row.accuracy * 100).toFixed(1) }}%</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="lastUpdate" label="最后更新">
              <template #default="{ row }">
                {{ formatTime(row.lastUpdate) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：警报配置和统计 -->
      <el-col :span="8">
        <!-- 风险类型统计 -->
        <el-card class="stats-card" shadow="never">
          <template #header>
            <span>📊 风险类型分布</span>
          </template>

          <div class="risk-stats">
            <div
              v-for="(count, type) in riskSummary.risk_type_counts"
              :key="type"
              class="stat-item"
            >
              <div class="stat-label">{{ getRiskTypeName(type as AIRiskType) }}</div>
              <div class="stat-bar">
                <div
                  class="stat-fill"
                  :style="{ width: `${getStatWidth(type, count)}%` }"
                ></div>
              </div>
              <div class="stat-count">{{ count }}</div>
            </div>
          </div>
        </el-card>

        <!-- 警报配置 -->
        <el-card class="alerts-config-card" shadow="never" style="margin-top: 16px">
          <template #header>
            <span>🔔 警报渠道配置</span>
          </template>

          <div class="alert-channels">
            <div
              v-for="config in alertConfigs"
              :key="config.channel"
              class="channel-item"
            >
              <div class="channel-info">
                <div class="channel-icon">
                  <el-icon v-if="config.channel === 'email'"><Message /></el-icon>
                  <el-icon v-else-if="config.channel === 'sms'"><Phone /></el-icon>
                  <el-icon v-else-if="config.channel === 'console'"><Monitor /></el-icon>
                  <el-icon v-else><Connection /></el-icon>
                </div>
                <div class="channel-details">
                  <div class="channel-name">{{ getChannelName(config.channel) }}</div>
                  <div class="channel-recipients" v-if="config.recipients.length > 0">
                    {{ config.recipients.join(', ') }}
                  </div>
                </div>
              </div>
              <div class="channel-control">
                <el-switch
                  v-model="config.enabled"
                  @change="toggleAlertChannel(config)"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </div>
            </div>
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card class="actions-card" shadow="never" style="margin-top: 16px">
          <template #header>
            <span>⚡ 快速操作</span>
          </template>

          <div class="quick-actions">
            <el-button type="primary" plain @click="exportSignals" style="width: 100%">
              <el-icon><Download /></el-icon>
              导出风险信号
            </el-button>
            <el-button type="warning" plain @click="cleanupOldSignals" style="width: 100%; margin-top: 8px">
              <el-icon><Delete /></el-icon>
              清理7天前的信号
            </el-button>
            <el-button type="info" plain @click="showAlertMessages" style="width: 100%; margin-top: 8px">
              <el-icon><List /></el-icon>
              查看警报历史
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Refresh, Warning, TrendCharts, DataLine, Monitor, InfoFilled,
  Message, Phone, Connection, Download, Delete, List
} from '@element-plus/icons-vue'
import { aiRiskAlertsApi, AIRiskType, RiskLevel, AlertChannel } from '@/api/modules/ai_risk_alerts'
import type { AIRiskSignal, AIRiskSummary, AIModel, AlertConfig } from '@/api/modules/ai_risk_alerts'

const router = useRouter()
const refreshing = ref(false)
const signalFilter = ref<'all' | 'critical' | 'recent'>('all')

// 数据
const riskSignals = ref<AIRiskSignal[]>([])
const riskSummary = ref<AIRiskSummary>({
  total_signals: 0,
  recent_signals: 0,
  risk_type_counts: {},
  avg_confidence: {},
  active_models: [],
  monitored_symbols: 0
})
const aiModels = ref<AIModel[]>([])
const alertConfigs = ref<AlertConfig[]>([])

let refreshInterval: number | null = null

// 计算属性
const filteredSignals = computed(() => {
  let signals = riskSignals.value

  if (signalFilter.value === 'critical') {
    signals = signals.filter(s => s.confidence >= 0.8)
  } else if (signalFilter.value === 'recent') {
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
    signals = signals.filter(s => new Date(s.timestamp) > oneDayAgo)
  }

  return signals.slice(0, 10) // 最多显示10条
})

const averageConfidence = computed(() => {
  const confidences = Object.values(riskSummary.value.avg_confidence)
  if (confidences.length === 0) return 0
  return (confidences.reduce((a, b) => a + b, 0) / confidences.length * 100).toFixed(1)
})

// 加载数据
const loadAISignals = async () => {
  try {
    const response = await aiRiskAlertsApi.getAISignals({ limit: 50 })
    if (response.code === 200) {
      riskSignals.value = response.data
    }
  } catch (error) {
    console.error('加载AI风险信号失败:', error)
    // 降级方案：使用默认数据
    riskSignals.value = [
      {
        id: '1',
        risk_type: AIRiskType.ANOMALY_DETECTION,
        confidence: 0.85,
        prediction: '市场行为异常，检测到价格波动异常',
        factors: {
          'anomaly_score': 2.3,
          'z_score_price': 3.1,
          'z_score_volume': 2.8
        },
        recommendation: '建议减少仓位，密切关注市场变化',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        symbol: '000001'
      },
      {
        id: '2',
        risk_type: AIRiskType.PREDICTIVE_RISK,
        confidence: 0.72,
        prediction: '未来24小时市场风险增加，预期波动率上升',
        factors: {
          'predicted_volatility': 0.035,
          'trend_strength': 0.025,
          'risk_score': 0.062
        },
        recommendation: '建议降低风险敞口，考虑对冲',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '3',
        risk_type: AIRiskType.REGIME_CHANGE,
        confidence: 0.88,
        prediction: '市场制度从低波动牛市转变为高波动震荡市',
        factors: {
          'old_regime': 'low_volatility_bull',
          'new_regime': 'high_volatility_sideways',
          'volatility': 0.032,
          'recent_returns': 0.008
        },
        recommendation: '建议调整策略参数，适应新市场制度',
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
      }
    ]
  }
}

const loadAISummary = async () => {
  try {
    const response = await aiRiskAlertsApi.getAISummary()
    if (response.code === 200) {
      riskSummary.value = response.data
    }
  } catch (error) {
    console.error('加载AI风险摘要失败:', error)
    // 降级方案
    riskSummary.value = {
      total_signals: 23,
      recent_signals: 5,
      risk_type_counts: {
        'anomaly_detection': 8,
        'predictive_risk': 6,
        'regime_change': 5,
        'sentiment_risk': 4
      },
      avg_confidence: {
        'anomaly_detection': 0.82,
        'predictive_risk': 0.75,
        'regime_change': 0.78,
        'sentiment_risk': 0.70
      },
      active_models: ['anomaly_detector', 'predictive_model', 'regime_detector'],
      monitored_symbols: 50
    }
  }
}

const loadAIModels = async () => {
  try {
    const response = await aiRiskAlertsApi.getAIModels()
    if (response.code === 200) {
      aiModels.value = response.data
    }
  } catch (error) {
    console.error('加载AI模型失败:', error)
    // 降级方案
    aiModels.value = [
      {
        name: 'anomaly_detector',
        type: 'Isolation Forest',
        status: 'active',
        lastUpdate: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
        accuracy: 0.85,
        config: {}
      },
      {
        name: 'predictive_model',
        type: 'LSTM',
        status: 'active',
        lastUpdate: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        accuracy: 0.78,
        config: {}
      },
      {
        name: 'regime_detector',
        type: 'Hidden Markov',
        status: 'active',
        lastUpdate: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        accuracy: 0.82,
        config: {}
      },
      {
        name: 'sentiment_analyzer',
        type: 'Transformer',
        status: 'training',
        lastUpdate: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        config: {}
      }
    ]
  }
}

const loadAlertConfigs = async () => {
  try {
    const response = await aiRiskAlertsApi.getAlertConfigs()
    if (response.code === 200) {
      alertConfigs.value = response.data
    }
  } catch (error) {
    console.error('加载警报配置失败:', error)
    // 降级方案
    alertConfigs.value = [
      {
        channel: AlertChannel.CONSOLE,
        enabled: true,
        risk_levels: [RiskLevel.HIGH, RiskLevel.CRITICAL],
        recipients: [],
        template: '',
        retry_count: 3,
        retry_interval: 60
      },
      {
        channel: AlertChannel.LOG,
        enabled: true,
        risk_levels: [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL],
        recipients: [],
        template: '',
        retry_count: 3,
        retry_interval: 60
      },
      {
        channel: AlertChannel.EMAIL,
        enabled: false,
        risk_levels: [RiskLevel.HIGH, RiskLevel.CRITICAL],
        recipients: ['admin@example.com'],
        template: '风险警报：{message}',
        retry_count: 3,
        retry_interval: 60
      }
    ]
  }
}

// 辅助函数
const getRiskClass = (signal: AIRiskSignal): string => {
  if (signal.confidence >= 0.8) return 'critical-signal'
  if (signal.confidence >= 0.6) return 'high-signal'
  return 'medium-signal'
}

const getSignalTagType = (riskType: AIRiskType): string => {
  const typeMap: Record<AIRiskType, string> = {
    [AIRiskType.ANOMALY_DETECTION]: 'danger',
    [AIRiskType.PREDICTIVE_RISK]: 'warning',
    [AIRiskType.REGIME_CHANGE]: 'warning',
    [AIRiskType.SENTIMENT_RISK]: 'info',
    [AIRiskType.CORRELATION_SHIFT]: 'info',
    [AIRiskType.LIQUIDITY_STRESS]: 'warning',
    [AIRiskType.VOLATILITY_CLUSTER]: 'danger'
  }
  return typeMap[riskType] || 'info'
}

const getRiskTypeName = (riskType: AIRiskType | string): string => {
  const nameMap: Record<string, string> = {
    'anomaly_detection': '异常检测',
    'predictive_risk': '预测性风险',
    'sentiment_risk': '情绪风险',
    'regime_change': '制度变化',
    'correlation_shift': '相关性变化',
    'liquidity_stress': '流动性压力',
    'volatility_cluster': '波动率聚集'
  }
  return nameMap[riskType] || riskType
}

const getModelDisplayName = (modelName: string): string => {
  const nameMap: Record<string, string> = {
    'anomaly_detector': '异常检测器',
    'predictive_model': '预测模型',
    'sentiment_analyzer': '情绪分析器',
    'regime_detector': '制度识别器'
  }
  return nameMap[modelName] || modelName
}

const getModelStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    'idle': '空闲',
    'training': '训练中',
    'active': '运行中',
    'error': '错误'
  }
  return statusMap[status] || status
}

const getModelStatusTagType = (status: string): string => {
  const typeMap: Record<string, string> = {
    'idle': 'info',
    'training': 'warning',
    'active': 'success',
    'error': 'danger'
  }
  return typeMap[status] || 'info'
}

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return '#f56c6c'
  if (confidence >= 0.6) return '#e6a23c'
  return '#67c23a'
}

const formatTime = (timestamp: string): string => {
  const now = Date.now()
  const past = new Date(timestamp).getTime()
  const diff = now - past

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return new Date(timestamp).toLocaleDateString('zh-CN')
}

const formatFactorValue = (value: number): string => {
  if (typeof value === 'number') {
    return value.toFixed(3)
  }
  return String(value)
}

const getStatWidth = (type: string, count: number): number => {
  const maxCount = Math.max(...Object.values(riskSummary.value.risk_type_counts))
  return (count / maxCount) * 100
}

const getChannelName = (channel: string): string => {
  const nameMap: Record<string, string> = {
    'console': '控制台',
    'log': '日志',
    'email': '邮件',
    'sms': '短信',
    'webhook': 'Webhook',
    'database': '数据库'
  }
  return nameMap[channel] || channel
}

// 事件处理
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      loadAISignals(),
      loadAISummary(),
      loadAIModels(),
      loadAlertConfigs()
    ])
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

const filterSignals = () => {
  // 触发计算属性重新计算
}

const toggleAlertChannel = async (config: AlertConfig) => {
  try {
    if (config.enabled) {
      await aiRiskAlertsApi.enableAlertChannel(config.channel as AlertChannel)
      ElMessage.success('警报渠道已启用')
    } else {
      await aiRiskAlertsApi.disableAlertChannel(config.channel as AlertChannel)
      ElMessage.success('警报渠道已禁用')
    }
  } catch (error) {
    console.error('切换警报渠道失败:', error)
    ElMessage.error('操作失败')
    // 恢复状态
    config.enabled = !config.enabled
  }
}

const exportSignals = async () => {
  try {
    const response = await aiRiskAlertsApi.exportAISignals()
    if (response.code === 200) {
      // 创建下载链接
      const blob = new Blob([response.data], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `ai_risk_signals_${Date.now()}.json`
      link.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const cleanupOldSignals = async () => {
  try {
    const response = await aiRiskAlertsApi.cleanupAISignals(7)
    if (response.code === 200) {
      ElMessage.success(`已清理 ${response.data.deleted_count} 条旧信号`)
      await loadAISignals()
    }
  } catch (error) {
    console.error('清理失败:', error)
    ElMessage.error('清理失败')
  }
}

const showAlertMessages = () => {
  ElMessage.info('警报历史功能开发中')
}

const handleBack = () => {
  router.back()
}

// 实时更新
const startRealtimeUpdate = () => {
  refreshInterval = window.setInterval(() => {
    loadAISummary()
  }, 30000) // 每30秒更新摘要
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadAISignals(),
    loadAISummary(),
    loadAIModels(),
    loadAlertConfigs()
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
.ai-risk-alert-view {
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
    }
  }

  .summary-cards {
    margin-bottom: 16px;

    .summary-card {
      .card-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .card-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;

          &.anomaly {
            background-color: #fef0f0;
            color: #f56c6c;
          }

          &.prediction {
            background-color: #fdf6ec;
            color: #e6a23c;
          }

          &.confidence {
            background-color: #e8f5e8;
            color: #67c23a;
          }

          &.symbols {
            background-color: #ecf5ff;
            color: #409eff;
          }
        }

        .card-info {
          flex: 1;

          .card-label {
            font-size: 13px;
            color: #909399;
            margin-bottom: 4px;
          }

          .card-value {
            font-size: 24px;
            font-weight: 600;
            color: #303133;
            margin-bottom: 2px;
          }

          .card-sub {
            font-size: 12px;
            color: #c0c4cc;
          }
        }
      }
    }
  }

  .signals-card {
    .signals-list {
      max-height: 600px;
      overflow-y: auto;

      .signal-item {
        padding: 16px;
        margin-bottom: 12px;
        border-radius: 8px;
        border: 1px solid #e4e7ed;
        transition: all 0.3s;

        &:hover {
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        }

        &.critical-signal {
          background-color: #fef0f0;
          border-color: #fde2e2;
        }

        &.high-signal {
          background-color: #fdf6ec;
          border-color: #faecd8;
        }

        &.medium-signal {
          background-color: #f4f4f5;
          border-color: #e9e9eb;
        }

        .signal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          .signal-type {
            display: flex;
            gap: 8px;
          }

          .signal-time {
            font-size: 12px;
            color: #909399;
          }
        }

        .signal-prediction {
          margin-bottom: 8px;
          font-size: 14px;
          color: #303133;
        }

        .signal-factors {
          margin-bottom: 8px;

          .factors-label {
            font-size: 12px;
            color: #909399;
            margin-bottom: 4px;
          }

          .factors-list {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
          }
        }

        .signal-recommendation {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          margin-bottom: 8px;
          background-color: #ecf5ff;
          border-radius: 4px;
          font-size: 13px;
          color: #409eff;
        }

        .signal-confidence {
          .confidence-label {
            font-size: 12px;
            color: #909399;
            margin-bottom: 4px;
          }
        }
      }
    }
  }

  .models-card {
    :deep(.el-table) {
      font-size: 13px;
    }
  }

  .stats-card {
    .risk-stats {
      .stat-item {
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }

        .stat-label {
          font-size: 13px;
          color: #606266;
          margin-bottom: 6px;
        }

        .stat-bar {
          width: 100%;
          height: 8px;
          background-color: #f5f7fa;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 4px;

          .stat-fill {
            height: 100%;
            background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
            transition: width 0.5s ease;
          }
        }

        .stat-count {
          font-size: 14px;
          font-weight: 600;
          color: #303133;
          text-align: right;
        }
      }
    }
  }

  .alerts-config-card {
    .alert-channels {
      .channel-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f5f7fa;

        &:last-child {
          border-bottom: none;
        }

        .channel-info {
          display: flex;
          gap: 12px;
          flex: 1;

          .channel-icon {
            font-size: 20px;
            color: #909399;
          }

          .channel-details {
            .channel-name {
              font-size: 14px;
              color: #303133;
              font-weight: 500;
            }

            .channel-recipients {
              font-size: 12px;
              color: #909399;
              margin-top: 2px;
            }
          }
        }
      }
    }
  }

  .actions-card {
    .quick-actions {
      display: flex;
      flex-direction: column;
    }
  }
}
</style>
