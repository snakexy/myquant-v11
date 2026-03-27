<template>
  <div class="stock-data-update">
    <!-- 页面标题 -->
    <div class="update-header">
      <div class="header-info">
        <h2>股票基础数据更新</h2>
        <p>支持增量更新，从数据库最后时间自动更新到最近收盘日</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="refreshStatus">
          <i class="fas fa-sync-alt"></i>
          刷新状态
        </button>
        <button class="btn-primary" @click="showUpdateSettings = true">
          <i class="fas fa-cog"></i>
          更新设置
        </button>
      </div>
    </div>

    <!-- 更新概览卡片 -->
    <div class="update-overview">
      <div class="overview-card">
        <div class="card-icon latest-date">
          <i class="fas fa-calendar-check"></i>
        </div>
        <div class="card-content">
          <div class="card-label">最近收盘日</div>
          <div class="card-value">{{ latestTradingDate || '--' }}</div>
        </div>
      </div>

      <div class="overview-card">
        <div class="card-icon total">
          <i class="fas fa-list"></i>
        </div>
        <div class="card-content">
          <div class="card-label">总股票数</div>
          <div class="card-value">{{ databaseStatus.total || 0 }}</div>
        </div>
      </div>

      <div class="overview-card">
        <div class="card-icon need-update">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="card-content">
          <div class="card-label">需要更新</div>
          <div class="card-value">{{ databaseStatus.needs_update_count || 0 }}</div>
        </div>
      </div>

      <div class="overview-card">
        <div class="card-icon updated">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="card-content">
          <div class="card-label">数据最新</div>
          <div class="card-value">{{ databaseStatus.total ? databaseStatus.total - databaseStatus.needs_update_count : 0 }}</div>
        </div>
      </div>
    </div>

    <!-- 快速更新计划 -->
    <div class="quick-update-plans">
      <h3>快速更新</h3>
      <div class="plans-grid">
        <div
          v-for="plan in quickUpdatePlans"
          :key="plan.id"
          class="plan-card"
          :class="{ 'plan-running': updateStatus.task_id === plan.id && updateStatus.status === 'running' }"
        >
          <div class="plan-header">
            <div class="plan-icon" :style="{ backgroundColor: plan.color }">
              <i :class="plan.icon"></i>
            </div>
            <div class="plan-info">
              <h4>{{ plan.name }}</h4>
              <p>{{ plan.description }}</p>
            </div>
          </div>
          <div class="plan-details">
            <div class="plan-detail">
              <span class="detail-label">数据周期:</span>
              <span class="detail-value">{{ plan.frequency }}</span>
            </div>
            <div class="plan-detail">
              <span class="detail-label">预计耗时:</span>
              <span class="detail-value">{{ plan.estimated_time }}</span>
            </div>
            <div class="plan-detail">
              <span class="detail-label">数据源:</span>
              <span class="detail-value">{{ plan.source === 'qmt' ? 'QMT' : 'Mootdx' }}</span>
            </div>
          </div>
          <div class="plan-actions">
            <button
              class="btn-run"
              :disabled="updateStatus.status === 'running'"
              @click="runQuickUpdate(plan)"
            >
              <i v-if="updateStatus.task_id === plan.id && updateStatus.status === 'running'" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-play"></i>
              {{ updateStatus.task_id === plan.id && updateStatus.status === 'running' ? '运行中...' : '立即运行' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 更新进度 -->
    <div v-if="updateStatus.status === 'running'" class="update-progress">
      <h3>更新进度</h3>
      <div class="progress-container">
        <div class="progress-info">
          <div class="progress-text">
            <span>{{ updateStatus.task_name || '数据更新中...' }}</span>
            <span class="progress-percent">{{ updateStatus.progress || 0 }}%</span>
          </div>
          <div class="progress-stats">
            <span>已完成: {{ updateStatus.updated || 0 }}</span>
            <span>跳过: {{ updateStatus.skipped || 0 }}</span>
            <span>失败: {{ updateStatus.failed || 0 }}</span>
          </div>
        </div>
        <div class="progress-bar-wrapper">
          <div class="progress-bar" :style="{ width: (updateStatus.progress || 0) + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 自定义更新选项 -->
    <div class="custom-update-section">
      <h3>自定义更新</h3>
      <div class="custom-update-form">
        <div class="form-row">
          <div class="form-group">
            <label>更新模式</label>
            <select v-model="customUpdate.mode" class="form-select">
              <option value="incremental">增量更新（推荐）</option>
              <option value="full">全量更新</option>
            </select>
          </div>

          <div class="form-group">
            <label>数据周期</label>
            <select v-model="customUpdate.frequency" class="form-select">
              <option value="day">日线 (1d)</option>
              <option value="60min">60分钟 (60m)</option>
              <option value="30min">30分钟 (30m)</option>
              <option value="15min">15分钟 (15m)</option>
              <option value="5min">5分钟 (5m)</option>
              <option value="1min">1分钟 (1m)</option>
            </select>
          </div>

          <div class="form-group">
            <label>数据源</label>
            <select v-model="customUpdate.source" class="form-select">
              <option value="mootdx">Mootdx（在线）</option>
              <option value="qmt">QMT（本地）</option>
            </select>
          </div>

          <div class="form-group">
            <label>批量大小</label>
            <select v-model="customUpdate.batchSize" class="form-select">
              <option :value="10">10</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="200">200</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group full-width">
            <label>股票代码（可选，留空则更新所有）</label>
            <textarea
              v-model="customUpdate.symbols"
              class="form-textarea"
              placeholder="输入股票代码，每行一个，如：600000.SH&#10;000001.SZ"
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="form-actions">
          <button class="btn-secondary" @click="resetCustomUpdate">
            <i class="fas fa-undo"></i>
            重置
          </button>
          <button
            class="btn-primary"
            :disabled="updateStatus.status === 'running' || !customUpdate.frequency"
            @click="runCustomUpdate"
          >
            <i class="fas fa-play"></i>
            开始更新
          </button>
        </div>
      </div>
    </div>

    <!-- 更新历史 -->
    <div class="update-history">
      <h3>更新历史</h3>
      <div class="history-list">
        <div v-for="task in updateHistory" :key="task.id" class="history-item">
          <div class="history-icon" :class="task.status">
            <i :class="getStatusIcon(task.status)"></i>
          </div>
          <div class="history-content">
            <div class="history-header">
              <span class="history-title">{{ task.name }}</span>
              <span class="history-time">{{ formatTime(task.created_at) }}</span>
            </div>
            <div class="history-details">
              <span v-if="task.frequency">周期: {{ task.frequency }}</span>
              <span v-if="task.total">总数: {{ task.total }}</span>
              <span v-if="task.updated !== undefined">更新: {{ task.updated }}</span>
              <span v-if="task.failed !== undefined">失败: {{ task.failed }}</span>
            </div>
          </div>
          <div class="history-status" :class="task.status">
            {{ getStatusText(task.status) }}
          </div>
        </div>
        <div v-if="updateHistory.length === 0" class="empty-history">
          <i class="fas fa-history"></i>
          <p>暂无更新历史</p>
        </div>
      </div>
    </div>

    <!-- 更新设置模态框 -->
    <div v-if="showUpdateSettings" class="modal-overlay" @click.self="showUpdateSettings = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>更新设置</h3>
          <button class="modal-close" @click="showUpdateSettings = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="setting-section">
            <h4>自动更新计划</h4>
            <div class="setting-item">
              <label>启用每日自动更新</label>
              <input type="checkbox" v-model="settings.autoUpdateEnabled" />
            </div>
            <div class="setting-item" v-if="settings.autoUpdateEnabled">
              <label>更新时间</label>
              <input type="time" v-model="settings.autoUpdateTime" />
            </div>
          </div>

          <div class="setting-section">
            <h4>默认选项</h4>
            <div class="setting-item">
              <label>默认数据源</label>
              <select v-model="settings.defaultSource" class="form-select">
                <option value="mootdx">Mootdx</option>
                <option value="qmt">QMT</option>
              </select>
            </div>
            <div class="setting-item">
              <label>默认批量大小</label>
              <select v-model="settings.defaultBatchSize" class="form-select">
                <option :value="50">50</option>
                <option :value="100">100</option>
                <option :value="200">200</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showUpdateSettings = false">取消</button>
          <button class="btn-primary" @click="saveSettings">保存设置</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { apiRequest } from '@/api'

// 响应式数据
const latestTradingDate = ref('')
const databaseStatus = ref<any>({})
const updateStatus = ref<any>({
  status: 'idle', // idle, running, completed, failed
  task_id: null,
  progress: 0,
  updated: 0,
  skipped: 0,
  failed: 0,
  task_name: ''
})
const updateHistory = ref<any[]>([])
const showUpdateSettings = ref(false)

// 快速更新计划
const quickUpdatePlans = ref([
  {
    id: 'daily',
    name: '日线数据更新',
    description: '更新日线K线数据',
    frequency: 'day',
    source: 'mootdx',
    estimated_time: '5-15分钟',
    icon: 'fas fa-chart-line',
    color: '#4CAF50'
  },
  {
    id: '60min',
    name: '60分钟线更新',
    description: '更新60分钟K线数据',
    frequency: '60min',
    source: 'mootdx',
    estimated_time: '10-30分钟',
    icon: 'fas fa-chart-bar',
    color: '#2196F3'
  },
  {
    id: '5min',
    name: '5分钟线更新',
    description: '更新5分钟K线数据',
    frequency: '5min',
    source: 'mootdx',
    estimated_time: '20-60分钟',
    icon: 'fas fa-chart-area',
    color: '#FF9800'
  }
])

// 自定义更新选项
const customUpdate = ref({
  mode: 'incremental',
  frequency: 'day',
  source: 'mootdx',
  batchSize: 50,
  symbols: ''
})

// 设置
const settings = ref({
  autoUpdateEnabled: false,
  autoUpdateTime: '16:00',
  defaultSource: 'mootdx',
  defaultBatchSize: 50
})

let refreshTimer: any = null

// 刷新状态
const refreshStatus = async () => {
  try {
    // 获取数据库状态 - 使用逗号分隔的字符串
    const statusResponse = await apiRequest.get('/stock-data-update/database-status', {
      params: {
        symbols: '600000.SH,000001.SZ,600036.SH',
        frequency: 'day'
      }
    })

    if (statusResponse.success) {
      databaseStatus.value = statusResponse.data
      latestTradingDate.value = statusResponse.data.latest_trading_date
    }

    // 获取任务列表
    const tasksResponse = await apiRequest.get('/stock-data-update/tasks', {
      params: { limit: 10 }
    })

    if (tasksResponse.success) {
      updateHistory.value = tasksResponse.data.tasks || []
    }

    // 检查当前运行的任务状态
    if (updateStatus.value.task_id) {
      const taskResponse = await apiRequest.get(`/stock-data-update/tasks/${updateStatus.value.task_id}`)
      if (taskResponse.success) {
        const task = taskResponse.data
        updateStatus.value = {
          ...updateStatus.value,
          status: task.status === 'pending' ? 'running' : task.status,
          progress: task.progress || 0
        }

        if (task.result) {
          updateStatus.value.updated = task.result.updated || 0
          updateStatus.value.skipped = task.result.skipped || 0
          updateStatus.value.failed = task.result.failed || 0
        }
      }
    }
  } catch (error) {
    console.error('刷新状态失败:', error)
  }
}

// 运行快速更新
const runQuickUpdate = async (plan: any) => {
  try {
    // 使用FormData发送表单数据
    const formData = new FormData()
    formData.append('frequency', plan.frequency)
    formData.append('source', plan.source)
    formData.append('batch_size', '50')

    const response = await apiRequest.post(
      '/stock-data-update/incremental-update-from-db',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    if (response.success && response.data) {
      // 更新状态
      updateStatus.value = {
        status: 'running',
        task_id: response.data.task_id,
        task_name: plan.name,
        progress: 0,
        updated: 0,
        skipped: 0,
        failed: 0
      }

      // 开始轮询进度
      startProgressPolling(response.data.task_id)
    }
  } catch (error) {
    console.error('启动更新失败:', error)
  }
}

// 运行自定义更新
const runCustomUpdate = async () => {
  try {
    const symbols = customUpdate.value.symbols
      ? customUpdate.value.symbols.split('\n').map(s => s.trim()).filter(s => s).join(',')
      : null

    // 使用FormData发送表单数据
    const formData = new FormData()
    if (symbols) {
      formData.append('symbols', symbols)
    }
    formData.append('frequency', customUpdate.value.frequency)
    formData.append('source', customUpdate.value.source)
    formData.append('batch_size', String(customUpdate.value.batchSize))
    formData.append('force_full_update', String(customUpdate.value.mode === 'full'))

    const response = await apiRequest.post(
      '/stock-data-update/incremental-update-from-db',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    if (response.success && response.data) {
      updateStatus.value = {
        status: 'running',
        task_id: response.data.task_id,
        task_name: `自定义更新 (${customUpdate.value.frequency})`,
        progress: 0,
        updated: 0,
        skipped: 0,
        failed: 0
      }

      startProgressPolling(response.data.task_id)
    }
  } catch (error) {
    console.error('启动自定义更新失败:', error)
  }
}

// 开始轮询进度
const startProgressPolling = (taskId: string) => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }

  refreshTimer = setInterval(async () => {
    try {
      const response = await apiRequest.get(`/stock-data-update/tasks/${taskId}`)
      if (response.success) {
        const task = response.data
        updateStatus.value.progress = task.progress || 0
        updateStatus.value.status = task.status === 'completed' ? 'completed' :
                                   task.status === 'failed' ? 'failed' : 'running'

        if (task.result) {
          updateStatus.value.updated = task.result.updated || 0
          updateStatus.value.skipped = task.result.skipped || 0
          updateStatus.value.failed = task.result.failed || 0
        }

        // 如果任务完成，停止轮询
        if (task.status === 'completed' || task.status === 'failed') {
          clearInterval(refreshTimer)
          updateStatus.value.task_id = null
          refreshStatus()
        }
      }
    } catch (error) {
      console.error('获取任务状态失败:', error)
    }
  }, 2000) // 每2秒轮询一次
}

// 重置自定义更新
const resetCustomUpdate = () => {
  customUpdate.value = {
    mode: 'incremental',
    frequency: 'day',
    source: 'mootdx',
    batchSize: 50,
    symbols: ''
  }
}

// 保存设置
const saveSettings = () => {
  localStorage.setItem('stock-update-settings', JSON.stringify(settings.value))
  showUpdateSettings.value = false
}

// 获取状态图标
const getStatusIcon = (status: string) => {
  const icons = {
    completed: 'fas fa-check',
    failed: 'fas fa-times',
    running: 'fas fa-spinner fa-spin',
    pending: 'fas fa-clock'
  }
  return icons[status] || 'fas fa-question'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts = {
    completed: '已完成',
    failed: '失败',
    running: '运行中',
    pending: '等待中'
  }
  return texts[status] || '未知'
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '--'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

// 加载设置
const loadSettings = () => {
  const saved = localStorage.getItem('stock-update-settings')
  if (saved) {
    try {
      settings.value = { ...settings.value, ...JSON.parse(saved) }
    } catch (e) {
      console.error('加载设置失败:', e)
    }
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
  refreshStatus()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

