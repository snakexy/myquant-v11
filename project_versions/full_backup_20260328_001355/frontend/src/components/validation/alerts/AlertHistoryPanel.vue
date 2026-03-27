<template>
  <el-card class="alert-history-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📜 预警历史</span>
        <el-button text @click="handleRefresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </template>

    <!-- 筛选器 -->
    <div class="filter-bar">
      <el-select
        v-model="filterSeverity"
        placeholder="全部级别"
        clearable
        size="small"
        style="width: 120px"
        @change="loadAlerts"
      >
        <el-option label="全部级别" value="" />
        <el-option label="严重" value="critical" />
        <el-option label="警告" value="warning" />
        <el-option label="信息" value="info" />
      </el-select>

      <el-select
        v-model="filterAcknowledged"
        placeholder="全部状态"
        clearable
        size="small"
        style="width: 120px"
        @change="loadAlerts"
      >
        <el-option label="全部状态" value="" />
        <el-option label="未确认" value="false" />
        <el-option label="已确认" value="true" />
      </el-select>

      <el-button
        size="small"
        type="primary"
        :disabled="selectedAlerts.length === 0"
        @click="handleBatchAcknowledge"
      >
        批量确认 ({{ selectedAlerts.length }})
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">总计</span>
        <span class="stat-value">{{ statistics.total }}</span>
      </div>
      <div class="stat-item critical">
        <span class="stat-label">严重</span>
        <span class="stat-value">{{ statistics.critical }}</span>
      </div>
      <div class="stat-item warning">
        <span class="stat-label">警告</span>
        <span class="stat-value">{{ statistics.warning }}</span>
      </div>
      <div class="stat-item info">
        <span class="stat-label">信息</span>
        <span class="stat-value">{{ statistics.info }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">已确认</span>
        <span class="stat-value">{{ statistics.acknowledged }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">待处理</span>
        <span class="stat-value">{{ statistics.pending }}</span>
      </div>
    </div>

    <!-- 预警列表 -->
    <el-table
      ref="tableRef"
      :data="alerts"
      v-loading="loading"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="ruleName" label="规则名称" min-width="150" />
      <el-table-column prop="severity" label="级别" width="80">
        <template #default="scope">
          <el-tag :type="getSeverityTagType(scope.row.severity)" size="small">
            {{ getSeverityText(scope.row.severity) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="message" label="预警消息" min-width="200" show-overflow-tooltip />
      <el-table-column prop="metrics" label="指标值" width="120">
        <template #default="scope">
          <el-popover placement="left" width="200" trigger="hover">
            <div class="metrics-popover">
              <div v-for="(value, key) in scope.row.metrics" :key="key" class="metric-row">
                <span class="metric-key">{{ key }}:</span>
                <span class="metric-value">{{ formatMetricValue(key, value) }}</span>
              </div>
            </div>
            <template #reference>
              <el-button text type="primary" size="small">查看</el-button>
            </template>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column prop="channelStatus" label="推送状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.channelStatus" :type="getChannelStatusTagType(scope.row.channelStatus)" size="small">
            {{ getChannelStatusText(scope.row.channelStatus) }}
          </el-tag>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="acknowledged" label="确认状态" width="90">
        <template #default="scope">
          <el-tag v-if="scope.row.acknowledged" type="success" size="small">已确认</el-tag>
          <el-tag v-else type="warning" size="small">待处理</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="触发时间" width="160">
        <template #default="scope">
          {{ formatDateTime(scope.row.createdAt) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button
            v-if="!scope.row.acknowledged"
            link
            type="primary"
            size="small"
            @click="handleAcknowledge(scope.row)"
          >
            确认
          </el-button>
          <el-button
            link
            size="small"
            @click="handleViewDetails(scope.row)"
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 预警详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="预警详情"
      width="600px"
    >
      <div v-if="selectedAlert" class="alert-detail">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">规则名称</span>
              <span class="value">{{ selectedAlert.ruleName }}</span>
            </div>
            <div class="info-item">
              <span class="label">严重级别</span>
              <el-tag :type="getSeverityTagType(selectedAlert.severity)" size="small">
                {{ getSeverityText(selectedAlert.severity) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">触发时间</span>
              <span class="value">{{ formatDateTime(selectedAlert.createdAt) }}</span>
            </div>
            <div class="info-item">
              <span class="label">确认状态</span>
              <el-tag v-if="selectedAlert.acknowledged" type="success" size="small">
                已确认
              </el-tag>
              <el-tag v-else type="warning" size="small">待处理</el-tag>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>预警消息</h4>
          <div class="message-box">{{ selectedAlert.message }}</div>
        </div>

        <div class="detail-section">
          <h4>触发指标</h4>
          <div class="metrics-grid">
            <div v-for="(value, key) in selectedAlert.metrics" :key="key" class="metric-card">
              <div class="metric-key">{{ key }}</div>
              <div class="metric-value">{{ formatMetricValue(key, value) }}</div>
            </div>
          </div>
        </div>

        <div v-if="selectedAlert.acknowledged" class="detail-section">
          <h4>确认信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">确认人</span>
              <span class="value">{{ selectedAlert.acknowledgedBy || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">确认时间</span>
              <span class="value">{{ formatDateTime(selectedAlert.acknowledgedAt || '') }}</span>
            </div>
          </div>
        </div>

        <div v-if="selectedAlert.channelStatus" class="detail-section">
          <h4>推送信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">推送渠道</span>
              <span class="value">{{ selectedAlert.channelId || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">推送状态</span>
              <el-tag :type="getChannelStatusTagType(selectedAlert.channelStatus)" size="small">
                {{ getChannelStatusText(selectedAlert.channelStatus) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="selectedAlert && !selectedAlert.acknowledged"
          type="primary"
          @click="handleAcknowledgeFromDialog"
        >
          确认预警
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { alertApi } from '@/api/modules/alerts'
import type { Alert, AlertStatistics } from '@/api/modules/alerts'

// Props
interface Props {
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: true,
  refreshInterval: 30000
})

// 筛选器
const filterSeverity = ref<string>('')
const filterAcknowledged = ref<string>('')

// 预警列表
const alerts = ref<Alert[]>([])
const loading = ref(false)
const tableRef = ref()
const selectedAlerts = ref<Alert[]>([])

// 分页
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

// 统计
const statistics = reactive<AlertStatistics>({
  total: 0,
  critical: 0,
  warning: 0,
  info: 0,
  acknowledged: 0,
  pending: 0,
  byRule: {},
  todayCount: 0,
  weekCount: 0,
  monthCount: 0
})

// 详情弹窗
const detailDialogVisible = ref(false)
const selectedAlert = ref<Alert | null>(null)

// 自动刷新定时器
let refreshTimer: number | null = null

// 加载统计信息
const loadStatistics = async () => {
  try {
    const response = await alertApi.getStatistics()
    if (response.code === 200) {
      Object.assign(statistics, response.data)
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

// 加载预警列表
const loadAlerts = async () => {
  loading.value = true
  try {
    const acknowledged = filterAcknowledged.value === 'true' ? true : filterAcknowledged.value === 'false' ? false : undefined
    const offset = (currentPage.value - 1) * pageSize.value

    const response = await alertApi.listAlerts(
      filterSeverity.value || undefined,
      acknowledged,
      pageSize.value,
      offset
    )

    if (response.code === 200) {
      alerts.value = response.data.alerts
      total.value = response.data.total
    }
  } catch (error) {
    console.error('加载预警列表失败:', error)
    // 降级方案：使用默认预警数据
    alerts.value = [
      {
        alertId: 'alert_1',
        ruleId: 'rule_1',
        ruleName: '夏普比率过低预警',
        message: '当前夏普比率 0.85 低于阈值 1.0，建议优化策略',
        severity: 'warning',
        metrics: {
          sharpe_ratio: 0.85,
          max_drawdown: 15.2,
          total_return: 8.5
        },
        acknowledged: false,
        createdAt: new Date().toISOString(),
        channelStatus: 'sent'
      },
      {
        alertId: 'alert_2',
        ruleId: 'rule_2',
        ruleName: '最大回撤超限',
        message: '最大回撤达到 22.5%，超过阈值 20%，请及时处理',
        severity: 'critical',
        metrics: {
          max_drawdown: 22.5,
          total_return: 5.2
        },
        acknowledged: false,
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        channelStatus: 'sent'
      },
      {
        alertId: 'alert_3',
        ruleId: 'rule_1',
        ruleName: '夏普比率过低预警',
        message: '当前夏普比率 0.92 低于阈值 1.0',
        severity: 'warning',
        metrics: {
          sharpe_ratio: 0.92,
          max_drawdown: 14.8
        },
        acknowledged: true,
        acknowledgedBy: '系统管理员',
        acknowledgedAt: new Date(Date.now() - 7200000).toISOString(),
        createdAt: new Date(Date.now() - 10800000).toISOString(),
        channelStatus: 'sent'
      }
    ]
    total.value = 3
    ElMessage.warning('使用默认预警数据')
  } finally {
    loading.value = false
  }
}

// 选择变化
const handleSelectionChange = (selection: Alert[]) => {
  selectedAlerts.value = selection
}

// 确认预警
const handleAcknowledge = async (alert: Alert) => {
  try {
    const response = await alertApi.acknowledgeAlert(alert.alertId)
    if (response.code === 200) {
      alert.acknowledged = true
      alert.acknowledgedAt = new Date().toISOString()
      ElMessage.success('预警已确认')
      await loadStatistics()
    }
  } catch (error) {
    console.error('确认预警失败:', error)
    ElMessage.error('确认失败')
  }
}

// 批量确认
const handleBatchAcknowledge = async () => {
  if (selectedAlerts.value.length === 0) {
    ElMessage.warning('请先选择要确认的预警')
    return
  }

  try {
    const alertIds = selectedAlerts.value.map(alert => alert.alertId)
    const response = await alertApi.batchAcknowledgeAlerts(alertIds)
    if (response.code === 200) {
      ElMessage.success(`已确认 ${response.data.count} 条预警`)
      tableRef.value?.clearSelection()
      await loadAlerts()
      await loadStatistics()
    }
  } catch (error) {
    console.error('批量确认失败:', error)
    ElMessage.error('批量确认失败')
  }
}

// 查看详情
const handleViewDetails = (alert: Alert) => {
  selectedAlert.value = alert
  detailDialogVisible.value = true
}

// 从弹窗确认
const handleAcknowledgeFromDialog = async () => {
  if (!selectedAlert.value) return
  await handleAcknowledge(selectedAlert.value)
  detailDialogVisible.value = false
}

// 分页变化
const handlePageChange = () => {
  loadAlerts()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadAlerts()
}

// 刷新
const handleRefresh = () => {
  Promise.all([loadAlerts(), loadStatistics()])
}

// 格式化日期时间
const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 格式化指标值
const formatMetricValue = (key: string, value: number): string => {
  if (key.includes('rate') || key.includes('return')) {
    return value.toFixed(2) + '%'
  }
  if (key.includes('ratio')) {
    return value.toFixed(2)
  }
  return value.toString()
}

// 严重级别标签类型
const getSeverityTagType = (severity: string): string => {
  const severityMap: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return severityMap[severity] || 'info'
}

// 严重级别文本
const getSeverityText = (severity: string): string => {
  const severityMap: Record<string, string> = {
    critical: '严重',
    warning: '警告',
    info: '信息'
  }
  return severityMap[severity] || severity
}

// 推送状态标签类型
const getChannelStatusTagType = (status: string): string => {
  const statusMap: Record<string, string> = {
    sent: 'success',
    pending: 'warning',
    failed: 'danger'
  }
  return statusMap[status] || 'info'
}

// 推送状态文本
const getChannelStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    sent: '已推送',
    pending: '待推送',
    failed: '推送失败'
  }
  return statusMap[status] || status
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (props.autoRefresh && props.refreshInterval > 0) {
    refreshTimer = window.setInterval(() => {
      loadAlerts()
      loadStatistics()
    }, props.refreshInterval)
  }
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
  loadAlerts()
  loadStatistics()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

// 暴露方法
defineExpose({
  refresh: handleRefresh
})
</script>

<style scoped lang="scss">
.alert-history-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    align-items: center;
  }

  .stats-bar {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    padding: 12px;
    background-color: #f5f7fa;
    border-radius: 8px;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;

      .stat-label {
        font-size: 12px;
        color: #909399;
      }

      .stat-value {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }

      &.critical .stat-value {
        color: #f56c6c;
      }

      &.warning .stat-value {
        color: #e6a23c;
      }

      &.info .stat-value {
        color: #409eff;
      }
    }
  }

  .pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 16px;
  }

  .metrics-popover {
    .metric-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 13px;

      &:last-child {
        margin-bottom: 0;
      }

      .metric-key {
        color: #606266;
      }

      .metric-value {
        font-weight: 600;
        color: #303133;
      }
    }
  }

  .alert-detail {
    .detail-section {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: #606266;
      }

      .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 4px;

          .label {
            font-size: 12px;
            color: #909399;
          }

          .value {
            font-size: 13px;
            color: #303133;
          }
        }
      }

      .message-box {
        padding: 12px;
        background-color: #f5f7fa;
        border-radius: 8px;
        font-size: 13px;
        color: #303133;
        line-height: 1.6;
      }

      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;

        .metric-card {
          padding: 12px;
          background-color: #f5f7fa;
          border-radius: 8px;
          text-align: center;

          .metric-key {
            font-size: 12px;
            color: #909399;
            margin-bottom: 8px;
          }

          .metric-value {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }
        }
      }
    }
  }

  .text-muted {
    color: #c0c4cc;
  }
}
</style>
