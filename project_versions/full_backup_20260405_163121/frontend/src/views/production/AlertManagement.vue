<template>
  <div class="alert-management">
    <!-- 告警统计卡片 -->
    <div class="alert-stats">
      <div class="stat-card" :class="{ active: filterLevel === 'all' }" @click="filterLevel = 'all'">
        <div class="stat-icon total">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ alertStats.total }}</div>
          <div class="stat-label">{{ t.totalAlerts }}</div>
        </div>
      </div>
      <div class="stat-card critical" :class="{ active: filterLevel === 'critical' }" @click="filterLevel = 'critical'">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ alertStats.critical }}</div>
          <div class="stat-label">{{ t.critical }}</div>
        </div>
      </div>
      <div class="stat-card warning" :class="{ active: filterLevel === 'warning' }" @click="filterLevel = 'warning'">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 8v4m0 4h.01"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ alertStats.warning }}</div>
          <div class="stat-label">{{ t.warning }}</div>
        </div>
      </div>
      <div class="stat-card info" :class="{ active: filterLevel === 'info' }" @click="filterLevel = 'info'">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4m0-4h.01"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ alertStats.info }}</div>
          <div class="stat-label">{{ t.info }}</div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：告警列表 -->
      <div class="alert-list-section">
        <div class="section-header">
          <h3>{{ t.alertList }}</h3>
          <div class="header-actions">
            <el-select v-model="filterType" size="small" :placeholder="t.filterByType" style="width: 140px;">
              <el-option :label="t.allTypes" value="all" />
              <el-option :label="t.positionAlert" value="position" />
              <el-option :label="t.riskAlert" value="risk" />
              <el-option :label="t.tradeAlert" value="trade" />
              <el-option :label="t.systemAlert" value="system" />
            </el-select>
            <el-button size="small" @click="clearReadAlerts" :disabled="!hasReadAlerts">
              <el-icon><Delete /></el-icon>
              {{ t.clearRead }}
            </el-button>
          </div>
        </div>

        <div class="alert-list" v-loading="loading">
          <div
            v-for="alert in filteredAlerts"
            :key="alert.id"
            class="alert-item"
            :class="[alert.level, { read: alert.read }]"
            @click="selectAlert(alert)"
          >
            <div class="alert-icon" :class="alert.level">
              <svg v-if="alert.level === 'critical'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <svg v-else-if="alert.level === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 8v4m0 4h.01"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 16v-4m0-4h.01"/>
              </svg>
            </div>
            <div class="alert-content">
              <div class="alert-header">
                <span class="alert-type">{{ getAlertTypeText(alert.type) }}</span>
                <span class="alert-time">{{ formatTime(alert.timestamp) }}</span>
              </div>
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-source" v-if="alert.source">{{ t.source }}: {{ alert.source }}</div>
            </div>
            <div class="alert-actions">
              <el-button
                v-if="!alert.read"
                link
                type="primary"
                size="small"
                @click.stop="markAsRead(alert)"
              >
                {{ t.markRead }}
              </el-button>
              <el-icon v-else class="read-icon"><Check /></el-icon>
            </div>
          </div>

          <el-empty v-if="filteredAlerts.length === 0" :description="t.noAlerts" />
        </div>
      </div>

      <!-- 右侧：告警详情与配置 -->
      <div class="alert-detail-section">
        <!-- 告警详情 -->
        <div class="detail-card" v-if="selectedAlert">
          <div class="section-header">
            <h3>{{ t.alertDetail }}</h3>
            <el-tag :type="getLevelType(selectedAlert.level)" size="small">
              {{ getLevelText(selectedAlert.level) }}
            </el-tag>
          </div>
          <div class="detail-content">
            <div class="detail-row">
              <span class="detail-label">{{ t.alertId }}</span>
              <span class="detail-value">{{ selectedAlert.id }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">{{ t.alertType }}</span>
              <span class="detail-value">{{ getAlertTypeText(selectedAlert.type) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">{{ t.time }}</span>
              <span class="detail-value">{{ formatDateTime(selectedAlert.timestamp) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">{{ t.source }}</span>
              <span class="detail-value">{{ selectedAlert.source || '-' }}</span>
            </div>
            <div class="detail-row full">
              <span class="detail-label">{{ t.message }}</span>
              <span class="detail-value message">{{ selectedAlert.message }}</span>
            </div>
            <div class="detail-row full" v-if="selectedAlert.details">
              <span class="detail-label">{{ t.details }}</span>
              <pre class="detail-value details">{{ JSON.stringify(selectedAlert.details, null, 2) }}</pre>
            </div>
          </div>
          <div class="detail-actions">
            <el-button type="primary" size="small" @click="handleAlert(selectedAlert)">
              {{ t.handle }}
            </el-button>
            <el-button size="small" @click="ignoreAlert(selectedAlert)">
              {{ t.ignore }}
            </el-button>
          </div>
        </div>

        <!-- 告警规则配置 -->
        <div class="rules-card">
          <div class="section-header">
            <h3>{{ t.alertRules }}</h3>
            <el-button type="primary" size="small" @click="showAddRuleDialog = true">
              <el-icon><Plus /></el-icon>
              {{ t.addRule }}
            </el-button>
          </div>
          <div class="rules-list">
            <div v-for="rule in alertRules" :key="rule.id" class="rule-item">
              <div class="rule-info">
                <span class="rule-name">{{ rule.name }}</span>
                <span class="rule-condition">{{ rule.condition }}</span>
              </div>
              <el-switch v-model="rule.enabled" size="small" @change="toggleRule(rule)" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加规则对话框 -->
    <el-dialog v-model="showAddRuleDialog" :title="t.addRule" width="500px">
      <el-form :model="ruleForm" label-width="100px">
        <el-form-item :label="t.ruleName">
          <el-input v-model="ruleForm.name" :placeholder="t.ruleNamePlaceholder" />
        </el-form-item>
        <el-form-item :label="t.alertType">
          <el-select v-model="ruleForm.type" style="width: 100%;">
            <el-option :label="t.positionAlert" value="position" />
            <el-option :label="t.riskAlert" value="risk" />
            <el-option :label="t.tradeAlert" value="trade" />
            <el-option :label="t.systemAlert" value="system" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t.condition">
          <el-input v-model="ruleForm.condition" :placeholder="t.conditionPlaceholder" />
        </el-form-item>
        <el-form-item :label="t.alertLevel">
          <el-select v-model="ruleForm.level" style="width: 100%;">
            <el-option :label="t.critical" value="critical" />
            <el-option :label="t.warning" value="warning" />
            <el-option :label="t.info" value="info" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddRuleDialog = false">{{ t.cancel }}</el-button>
        <el-button type="primary" @click="addRule">{{ t.confirm }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Check, Plus } from '@element-plus/icons-vue'

// Props
interface Props {
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isZh: true
})

// 多语言文本
const t = computed(() => ({
  totalAlerts: props.isZh ? '总告警' : 'Total Alerts',
  critical: props.isZh ? '严重' : 'Critical',
  warning: props.isZh ? '警告' : 'Warning',
  info: props.isZh ? '信息' : 'Info',
  alertList: props.isZh ? '告警列表' : 'Alert List',
  filterByType: props.isZh ? '按类型筛选' : 'Filter by Type',
  allTypes: props.isZh ? '全部类型' : 'All Types',
  positionAlert: props.isZh ? '仓位告警' : 'Position',
  riskAlert: props.isZh ? '风险告警' : 'Risk',
  tradeAlert: props.isZh ? '交易告警' : 'Trade',
  systemAlert: props.isZh ? '系统告警' : 'System',
  clearRead: props.isZh ? '清除已读' : 'Clear Read',
  markRead: props.isZh ? '标记已读' : 'Mark Read',
  noAlerts: props.isZh ? '暂无告警' : 'No Alerts',
  alertDetail: props.isZh ? '告警详情' : 'Alert Detail',
  alertId: props.isZh ? '告警ID' : 'Alert ID',
  alertType: props.isZh ? '告警类型' : 'Alert Type',
  time: props.isZh ? '时间' : 'Time',
  source: props.isZh ? '来源' : 'Source',
  message: props.isZh ? '消息' : 'Message',
  details: props.isZh ? '详情' : 'Details',
  handle: props.isZh ? '处理' : 'Handle',
  ignore: props.isZh ? '忽略' : 'Ignore',
  alertRules: props.isZh ? '告警规则' : 'Alert Rules',
  addRule: props.isZh ? '添加规则' : 'Add Rule',
  ruleName: props.isZh ? '规则名称' : 'Rule Name',
  ruleNamePlaceholder: props.isZh ? '请输入规则名称' : 'Enter rule name',
  condition: props.isZh ? '触发条件' : 'Condition',
  conditionPlaceholder: props.isZh ? '例如: position_ratio > 0.8' : 'e.g. position_ratio > 0.8',
  alertLevel: props.isZh ? '告警级别' : 'Alert Level',
  cancel: props.isZh ? '取消' : 'Cancel',
  confirm: props.isZh ? '确定' : 'Confirm'
}))

// 状态
const loading = ref(false)
const filterLevel = ref('all')
const filterType = ref('all')
const selectedAlert = ref<Alert | null>(null)
const showAddRuleDialog = ref(false)

// 告警接口
interface Alert {
  id: string
  type: 'position' | 'risk' | 'trade' | 'system'
  level: 'critical' | 'warning' | 'info'
  message: string
  source?: string
  timestamp: string
  read: boolean
  details?: any
}

// 告警统计
const alertStats = ref({
  total: 12,
  critical: 2,
  warning: 5,
  info: 5
})

// 告警列表
const alerts = ref<Alert[]>([
  { id: 'ALT-001', type: 'risk', level: 'critical', message: '组合VaR超过阈值限制(5.2% > 5.0%)', source: '风险引擎', timestamp: '2024-01-15T14:30:00', read: false, details: { var_value: 0.052, threshold: 0.05 } },
  { id: 'ALT-002', type: 'position', level: 'critical', message: '单一持仓超过限额: 600519贵州茅台持仓比例达到12.5%', source: '仓位监控', timestamp: '2024-01-15T14:25:00', read: false },
  { id: 'ALT-003', type: 'trade', level: 'warning', message: '订单执行延迟超过3秒: 订单号#20240115001', source: '交易系统', timestamp: '2024-01-15T14:20:00', read: false },
  { id: 'ALT-004', type: 'risk', level: 'warning', message: '组合回撤接近止损线: 当前回撤-7.8%, 止损线-10%', source: '风险引擎', timestamp: '2024-01-15T14:15:00', read: true },
  { id: 'ALT-005', type: 'system', level: 'info', message: '行情数据源切换: 主数据源恢复,已切换回主数据源', source: '系统', timestamp: '2024-01-15T14:10:00', read: true },
  { id: 'ALT-006', type: 'position', level: 'warning', message: '持仓集中度过高: 前5大持仓占比85%', source: '仓位监控', timestamp: '2024-01-15T14:00:00', read: false },
  { id: 'ALT-007', type: 'risk', level: 'warning', message: '流动性风险预警: 部分持仓换手率过低', source: '风险引擎', timestamp: '2024-01-15T13:50:00', read: true },
  { id: 'ALT-008', type: 'system', level: 'info', message: '策略参数更新: 动量策略参数已更新', source: '策略引擎', timestamp: '2024-01-15T13:40:00', read: true }
])

// 告警规则
const alertRules = ref([
  { id: 1, name: 'VaR超限告警', condition: 'var > 0.05', enabled: true },
  { id: 2, name: '单一持仓限制', condition: 'single_position > 0.10', enabled: true },
  { id: 3, name: '回撤预警', condition: 'drawdown < -0.08', enabled: true },
  { id: 4, name: '持仓集中度', condition: 'concentration > 0.80', enabled: false }
])

// 规则表单
const ruleForm = ref({
  name: '',
  type: 'risk',
  condition: '',
  level: 'warning'
})

// 过滤后的告警列表
const filteredAlerts = computed(() => {
  let result = alerts.value
  if (filterLevel.value !== 'all') {
    result = result.filter(a => a.level === filterLevel.value)
  }
  if (filterType.value !== 'all') {
    result = result.filter(a => a.type === filterType.value)
  }
  return result
})

// 是否有已读告警
const hasReadAlerts = computed(() => alerts.value.some(a => a.read))

// 格式化函数
const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)

  if (minutes < 60) {
    return props.isZh ? `${minutes}分钟前` : `${minutes}m ago`
  } else if (minutes < 1440) {
    const hours = Math.floor(minutes / 60)
    return props.isZh ? `${hours}小时前` : `${hours}h ago`
  } else {
    return date.toLocaleTimeString(props.isZh ? 'zh-CN' : 'en-US', { hour: '2-digit', minute: '2-digit' })
  }
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString(props.isZh ? 'zh-CN' : 'en-US')
}

const getAlertTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    position: t.value.positionAlert,
    risk: t.value.riskAlert,
    trade: t.value.tradeAlert,
    system: t.value.systemAlert
  }
  return typeMap[type] || type
}

const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    critical: t.value.critical,
    warning: t.value.warning,
    info: t.value.info
  }
  return levelMap[level] || level
}

const getLevelType = (level: string) => {
  const typeMap: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return typeMap[level] || 'info'
}

// 操作函数
const selectAlert = (alert: Alert) => {
  selectedAlert.value = alert
}

const markAsRead = (alert: Alert) => {
  alert.read = true
  ElMessage.success(props.isZh ? '已标记为已读' : 'Marked as read')
}

const clearReadAlerts = () => {
  alerts.value = alerts.value.filter(a => !a.read)
  ElMessage.success(props.isZh ? '已清除已读告警' : 'Cleared read alerts')
}

const handleAlert = (alert: Alert) => {
  ElMessage.success(props.isZh ? `正在处理告警: ${alert.id}` : `Handling alert: ${alert.id}`)
}

const ignoreAlert = (alert: Alert) => {
  alert.read = true
  ElMessage.info(props.isZh ? '告警已忽略' : 'Alert ignored')
}

const toggleRule = (rule: any) => {
  ElMessage.success(props.isZh
    ? `规则"${rule.name}"已${rule.enabled ? '启用' : '禁用'}`
    : `Rule "${rule.name}" ${rule.enabled ? 'enabled' : 'disabled'}`
  )
}

const addRule = () => {
  if (!ruleForm.value.name || !ruleForm.value.condition) {
    ElMessage.warning(props.isZh ? '请填写完整信息' : 'Please fill in all fields')
    return
  }

  alertRules.value.push({
    id: Date.now(),
    name: ruleForm.value.name,
    condition: ruleForm.value.condition,
    enabled: true
  })

  showAddRuleDialog.value = false
  ruleForm.value = { name: '', type: 'risk', condition: '', level: 'warning' }
  ElMessage.success(props.isZh ? '规则添加成功' : 'Rule added successfully')
}

// 生命周期
onMounted(() => {
  // 加载告警数据
})
</script>

<style scoped lang="scss">
.alert-management {
  padding: 20px;
  background: var(--bg-primary, #131722);
  border-radius: 8px;

  // 使用全局统一样式，el-select、el-input-number等已统一

  :deep(.el-button) {
    --el-button-bg-color: var(--bg-secondary, #1e222d);
    --el-button-border-color: var(--border-color, #2a2e39);
    --el-button-text-color: var(--text-primary, #d1d4dc);
  }

  :deep(.el-button--primary) {
    --el-button-bg-color: var(--accent-blue, #2962ff);
    --el-button-border-color: var(--accent-blue, #2962ff);
  }

  :deep(.el-tag) {
    --el-tag-bg-color: var(--bg-secondary, #1e222d);
    --el-tag-border-color: var(--border-color, #2a2e39);
    --el-tag-text-color: var(--text-primary, #d1d4dc);
  }

  :deep(.el-empty__description) {
    color: var(--text-secondary, #787b86);
  }
}

// 告警统计
.alert-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg-secondary, #1e222d);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #2a2e39);
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover, &.active {
    border-color: var(--accent-blue, #2962ff);
  }

  &.critical .stat-icon { color: #ef5350; }
  &.warning .stat-icon { color: #f7931a; }
  &.info .stat-icon { color: #2962ff; }

  .stat-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary, #787b86);

    svg {
      width: 24px;
      height: 24px;
    }

    &.total {
      color: var(--text-primary, #d1d4dc);
    }
  }

  .stat-content {
    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
    }

    .stat-label {
      font-size: 11px;
      color: var(--text-secondary, #787b86);
    }
  }
}

// 主要内容
.main-content {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 16px;
}

// 告警列表
.alert-list-section {
  background: var(--bg-secondary, #1e222d);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #2a2e39);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;

  h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary, #d1d4dc);
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.alert-list {
  max-height: 500px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  background: var(--bg-primary, #131722);
  border-left: 3px solid transparent;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(41, 98, 255, 0.1);
  }

  &.critical { border-left-color: #ef5350; }
  &.warning { border-left-color: #f7931a; }
  &.info { border-left-color: #2962ff; }

  &.read {
    opacity: 0.6;
  }

  .alert-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    &.critical { background: rgba(239, 83, 80, 0.2); color: #ef5350; }
    &.warning { background: rgba(247, 147, 26, 0.2); color: #f7931a; }
    &.info { background: rgba(41, 98, 255, 0.2); color: #2962ff; }

    svg {
      width: 16px;
      height: 16px;
    }
  }

  .alert-content {
    flex: 1;
    min-width: 0;

    .alert-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;

      .alert-type {
        font-size: 11px;
        color: var(--text-secondary, #787b86);
      }

      .alert-time {
        font-size: 11px;
        color: var(--text-secondary, #787b86);
      }
    }

    .alert-message {
      font-size: 13px;
      color: var(--text-primary, #d1d4dc);
      line-height: 1.4;
    }

    .alert-source {
      font-size: 11px;
      color: var(--text-secondary, #787b86);
      margin-top: 4px;
    }
  }

  .alert-actions {
    .read-icon {
      color: #26a69a;
    }
  }
}

// 告警详情区域
.alert-detail-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-card,
.rules-card {
  background: var(--bg-secondary, #1e222d);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #2a2e39);
}

.detail-content {
  .detail-row {
    display: flex;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color, #2a2e39);

    &:last-child {
      border-bottom: none;
    }

    &.full {
      flex-direction: column;
      gap: 4px;
    }

    .detail-label {
      font-size: 12px;
      color: var(--text-secondary, #787b86);
      width: 80px;
      flex-shrink: 0;
    }

    .detail-value {
      font-size: 13px;
      color: var(--text-primary, #d1d4dc);
      flex: 1;

      &.message {
        line-height: 1.5;
      }

      &.details {
        background: var(--bg-primary, #131722);
        padding: 8px;
        border-radius: 4px;
        font-size: 11px;
        overflow-x: auto;
      }
    }
  }
}

.detail-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

// 规则列表
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--bg-primary, #131722);
  border-radius: 6px;

  .rule-info {
    .rule-name {
      font-size: 13px;
      color: var(--text-primary, #d1d4dc);
      display: block;
    }

    .rule-condition {
      font-size: 11px;
      color: var(--text-secondary, #787b86);
      font-family: monospace;
    }
  }
}

@media (max-width: 1200px) {
  .alert-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>
