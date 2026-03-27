<template>
  <div v-if="visible" class="scheduler-monitor-overlay" @click="closePanel">
    <div class="scheduler-monitor-panel" @click.stop>
      <!-- 头部 -->
      <div class="panel-header">
        <span class="panel-title">📊 {{ isZh ? '调度器监控面板' : 'Scheduler Monitor' }}</span>
        <button class="close-btn" @click="closePanel">×</button>
      </div>

      <!-- 内容区 -->
      <div class="panel-content">
        <!-- 全局统计 -->
        <div class="section">
          <h3>{{ isZh ? '全局统计' : 'Global Statistics' }}</h3>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-value">{{ stats.activeTasks }}</div>
              <div class="stat-label">{{ isZh ? '活跃任务' : 'Active Tasks' }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ stats.totalRequests }}</div>
              <div class="stat-label">{{ isZh ? '总请求数' : 'Total Requests' }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ stats.avgResponseTime }}ms</div>
              <div class="stat-label">{{ isZh ? '平均响应' : 'Avg Response' }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" :class="{ error: stats.errorRate > 5 }">{{ stats.errorRate }}%</div>
              <div class="stat-label">{{ isZh ? '错误率' : 'Error Rate' }}</div>
            </div>
          </div>
        </div>

        <!-- 分组刷新配置 -->
        <div class="section">
          <h3>{{ isZh ? '分组刷新配置' : 'Group Refresh Config' }}</h3>
          <div class="groups-list">
            <div
              v-for="group in (dataStore.watchlistGroups || [])"
              :key="group.id"
              class="group-item"
            >
              <div class="group-info">
                <span class="group-name">{{ group.name }}</span>
                <span class="group-count">({{ group.stocks.length }})</span>
                <span v-if="group.preheat" class="preheat-tag" title="启动时预加载">⚡</span>
              </div>

              <div class="group-config">
                <!-- 刷新频率选择 -->
                <select
                  :value="group.refreshInterval"
                  @change="updateGroupInterval(group.id, $event)"
                  class="interval-select"
                >
                  <option :value="3000">{{ isZh ? '3秒 (高频)' : '3s (High)' }}</option>
                  <option :value="5000">{{ isZh ? '5秒 (中频)' : '5s (Medium)' }}</option>
                  <option :value="10000">{{ isZh ? '10秒 (低频)' : '10s (Low)' }}</option>
                  <option :value="30000">{{ isZh ? '30秒 (超低)' : '30s (Ultra)' }}</option>
                </select>

                <!-- 状态指示 -->
                <div class="status-indicator">
                  <div
                    :class="[
                      'status-dot',
                      {
                        active: isGroupActive(group.id),
                        pending: isGroupPending(group.id)
                      }
                    ]"
                  ></div>
                  <span class="status-text">
                    {{ getStatusText(group.id) }}
                  </span>
                </div>

                <!-- 下次刷新倒计时 -->
                <div class="next-refresh">
                  <span class="refresh-label">{{ isZh ? '下次:' : 'Next:' }}</span>
                  <span class="refresh-countdown">{{ getNextRefreshTime(group.id) }}</span>
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-if="(dataStore.watchlistGroups?.length ?? 0) === 0" class="empty-state">
              {{ isZh ? '暂无分组' : 'No groups' }}
            </div>
          </div>
        </div>

        <!-- 实时日志 -->
        <div class="section">
          <h3>{{ isZh ? '实时日志' : 'Real-time Logs' }}</h3>
          <div class="logs-container">
            <div
              v-for="(log, index) in logs.slice(-10).reverse()"
              :key="index"
              :class="['log-item', log.level]"
            >
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="logs.length === 0" class="empty-logs">
              {{ isZh ? '暂无日志' : 'No logs' }}
            </div>
          </div>
        </div>

        <!-- 性能图表 -->
        <div class="section">
          <h3>{{ isZh ? 'API调用频率' : 'API Call Frequency' }}</h3>
          <div class="chart-container">
            <canvas ref="chartCanvas" class="frequency-chart"></canvas>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <div class="legend-color" style="background: #ef5350;"></div>
              <span>{{ isZh ? '请求数' : 'Requests' }}</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: #10b981;"></div>
              <span>{{ isZh ? '成功' : 'Success' }}</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: #f59e0b;"></div>
              <span>{{ isZh ? '失败' : 'Failed' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="panel-footer">
        <button class="footer-btn" @click="refreshStats">
          {{ isZh ? '刷新统计' : 'Refresh' }}
        </button>
        <button class="footer-btn danger" @click="clearLogs">
          {{ isZh ? '清空日志' : 'Clear Logs' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useDataStore } from '@/stores/core/DataStore'

interface LogEntry {
  timestamp: number
  level: 'info' | 'success' | 'warning' | 'error'
  message: string
}

interface GroupStatus {
  lastRefresh: number
  nextRefresh: number
  isActive: boolean
}

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const dataStore = useDataStore()
const isZh = ref(navigator.language === 'zh-CN')

// 统计数据
const stats = ref({
  activeTasks: 0,
  totalRequests: 0,
  avgResponseTime: 0,
  errorRate: 0
})

// 日志
const logs = ref<LogEntry[]>([])

// 分组状态
const groupStatus = ref<Map<string, GroupStatus>>(new Map())

// 图表相关
const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInterval: number | null = null

// 判断分组是否活跃
const isGroupActive = (groupId: string): boolean => {
  const status = groupStatus.value.get(groupId)
  return status?.isActive || false
}

// 判断分组是否等待中
const isGroupPending = (groupId: string): boolean => {
  const status = groupStatus.value.get(groupId)
  if (!status) return false
  const now = Date.now()
  return now < status.nextRefresh
}

// 获取状态文本
const getStatusText = (groupId: string): string => {
  if (isGroupActive(groupId)) return isZh.value ? '刷新中' : 'Refreshing'
  if (isGroupPending(groupId)) return isZh.value ? '等待中' : 'Pending'
  return isZh.value ? '空闲' : 'Idle'
}

// 获取下次刷新时间
const getNextRefreshTime = (groupId: string): string => {
  const status = groupStatus.value.get(groupId)
  if (!status) return '--'

  const now = Date.now()
  const diff = status.nextRefresh - now

  if (diff <= 0) return isZh.value ? '即将刷新' : 'Soon'

  const seconds = Math.ceil(diff / 1000)
  return `${seconds}s`
}

// 格式化时间
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour12: false })
}

// 更新分组刷新间隔
const updateGroupInterval = (groupId: string, event: Event) => {
  const target = event.target as HTMLSelectElement
  const interval = parseInt(target.value)
  dataStore.setGroupRefreshInterval(groupId, interval)
  const groupName = dataStore.watchlistGroups?.find(g => g.id === groupId)?.name
  addLog('info', `分组 ${groupName || groupId} 刷新间隔设置为 ${interval}ms`)
}

// 添加日志
const addLog = (level: LogEntry['level'], message: string) => {
  logs.value.push({
    timestamp: Date.now(),
    level,
    message
  })

  // 只保留最近50条
  if (logs.value.length > 50) {
    logs.value = logs.value.slice(-50)
  }
}

// 刷新统计
const refreshStats = () => {
  const groups = dataStore.watchlistGroups || []
  // 模拟统计数据（实际应从调度器获取）
  stats.value = {
    activeTasks: groups.filter(g => g.stocks.length > 0).length,
    totalRequests: Math.floor(Math.random() * 1000) + 500,
    avgResponseTime: Math.floor(Math.random() * 200) + 50,
    errorRate: (Math.random() * 2).toFixed(1)
  }

  // 更新分组状态
  const now = Date.now()
  for (const group of groups) {
    const lastRefresh = now - Math.random() * group.refreshInterval
    const nextRefresh = lastRefresh + group.refreshInterval

    groupStatus.value.set(group.id, {
      lastRefresh,
      nextRefresh,
      isActive: Math.random() > 0.8 // 20%概率刷新中
    })
  }

  addLog('info', isZh.value ? '统计数据已刷新' : 'Stats refreshed')
}

// 清空日志
const clearLogs = () => {
  logs.value = []
}

// 关闭面板
const closePanel = () => {
  emit('close')
}

// 绘制图表
const drawChart = () => {
  if (!chartCanvas.value) return

  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // 设置画布尺寸
  const rect = canvas.getBoundingClientRect()
  canvas.width = rect.width * 2
  canvas.height = 150 * 2
  ctx.scale(2, 2)

  const width = rect.width
  const height = 150

  // 清空画布
  ctx.clearRect(0, 0, width, height)

  // 生成模拟数据（最近60秒，每秒一个点）
  const dataPoints = 60
  const requests = Array.from({ length: dataPoints }, () => Math.floor(Math.random() * 20) + 5)
  const success = requests.map(r => Math.floor(r * (0.9 + Math.random() * 0.1)))
  const failed = requests.map((r, i) => r - success[i])

  // 绘制网格
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
  ctx.lineWidth = 1
  for (let i = 0; i <= 4; i++) {
    const y = (height / 4) * i
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }

  // 绘制请求数（红色）
  ctx.strokeStyle = '#ef5350'
  ctx.lineWidth = 2
  ctx.beginPath()
  requests.forEach((value, index) => {
    const x = (width / (dataPoints - 1)) * index
    const y = height - (value / 25) * height
    if (index === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.stroke()

  // 绘制成功数（绿色）
  ctx.strokeStyle = '#10b981'
  ctx.lineWidth = 2
  ctx.beginPath()
  success.forEach((value, index) => {
    const x = (width / (dataPoints - 1)) * index
    const y = height - (value / 25) * height
    if (index === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.stroke()

  // 绘制失败数（黄色）
  ctx.strokeStyle = '#f59e0b'
  ctx.lineWidth = 1
  ctx.beginPath()
  failed.forEach((value, index) => {
    const x = (width / (dataPoints - 1)) * index
    const y = height - (value / 25) * height
    if (index === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.stroke()
}

// 定时更新
onMounted(() => {
  refreshStats()
  addLog('info', isZh.value ? '监控面板已启动' : 'Monitor panel started')

  // 每秒刷新一次
  chartInterval = window.setInterval(() => {
    refreshStats()
    drawChart()
  }, 1000)

  nextTick(() => {
    drawChart()
  })
})

onUnmounted(() => {
  if (chartInterval) {
    clearInterval(chartInterval)
  }
})
</script>

<style scoped>
.scheduler-monitor-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.scheduler-monitor-panel {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 12px;
  width: 800px;
  max-height: 85vh;
  max-width: 95vw;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #2a2e39;
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: #d1d4dc;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #787b86;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(239, 83, 80, 0.1);
  color: #ef5350;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.section {
  margin-bottom: 24px;
}

.section:last-child {
  margin-bottom: 0;
}

.section h3 {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
  margin-bottom: 12px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  background: rgba(30, 30, 60, 0.6);
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #ef5350;
  margin-bottom: 4px;
}

.stat-value.error {
  color: #f59e0b;
}

.stat-label {
  font-size: 12px;
  color: #787b86;
}

/* 分组列表 */
.groups-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.group-item {
  background: rgba(30, 30, 60, 0.6);
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.group-info {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.group-name {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
}

.group-count {
  font-size: 12px;
  color: #787b86;
}

.preheat-tag {
  font-size: 12px;
  background: rgba(239, 83, 80, 0.2);
  color: #ef5350;
  padding: 2px 6px;
  border-radius: 4px;
}

.group-config {
  display: flex;
  align-items: center;
  gap: 12px;
}

.interval-select {
  background: #131722;
  border: 1px solid #2a2e39;
  border-radius: 4px;
  padding: 6px 10px;
  color: #d1d4dc;
  font-size: 12px;
  cursor: pointer;
}

.interval-select:focus {
  outline: none;
  border-color: #ef5350;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #787b86;
}

.status-dot.active {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-dot.pending {
  background: #f59e0b;
}

.status-text {
  font-size: 11px;
  color: #787b86;
  min-width: 50px;
}

.next-refresh {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #787b86;
}

.refresh-countdown {
  font-weight: 600;
  color: #d1d4dc;
}

/* 日志 */
.logs-container {
  background: rgba(30, 30, 60, 0.6);
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 8px;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid rgba(42, 46, 57, 0.5);
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #787b86;
  min-width: 70px;
}

.log-message {
  color: #d1d4dc;
}

.log-item.info .log-message {
  color: #60a5fa;
}

.log-item.success .log-message {
  color: #10b981;
}

.log-item.warning .log-message {
  color: #f59e0b;
}

.log-item.error .log-message {
  color: #ef5350;
}

.empty-logs, .empty-state {
  text-align: center;
  color: #787b86;
  font-size: 13px;
  padding: 20px;
}

/* 图表 */
.chart-container {
  background: rgba(30, 30, 60, 0.6);
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.frequency-chart {
  width: 100%;
  height: 150px;
  display: block;
}

.chart-legend {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #787b86;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

/* 底部按钮 */
.panel-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #2a2e39;
  justify-content: flex-end;
}

.footer-btn {
  padding: 8px 16px;
  background: #2a2e39;
  border: none;
  border-radius: 6px;
  color: #d1d4dc;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.footer-btn:hover {
  background: #363a45;
}

.footer-btn.danger {
  background: rgba(239, 83, 80, 0.1);
  color: #ef5350;
}

.footer-btn.danger:hover {
  background: rgba(239, 83, 80, 0.2);
}
</style>
