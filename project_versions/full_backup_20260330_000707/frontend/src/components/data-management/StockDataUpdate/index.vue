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
          <font-awesome-icon icon="sync-alt" />
          刷新状态
        </button>
        <button class="btn-primary" @click="showUpdateSettings = true">
          <font-awesome-icon icon="cog" />
          更新设置
        </button>
      </div>
    </div>

    <!-- 更新概览卡片 -->
    <div class="update-overview">
      <div class="overview-card">
        <div class="card-icon latest-date">
          <font-awesome-icon icon="calendar-check" />
        </div>
        <div class="card-content">
          <div class="card-label">最近收盘日</div>
          <div class="card-value">{{ latestTradingDate || '--' }}</div>
        </div>
      </div>

      <div class="overview-card">
        <div class="card-icon total">
          <font-awesome-icon icon="list" />
        </div>
        <div class="card-content">
          <div class="card-label">总股票数</div>
          <div class="card-value">{{ databaseStatus.total || 0 }}</div>
        </div>
      </div>

      <div class="overview-card">
        <div class="card-icon need-update">
          <font-awesome-icon icon="exclamation-triangle" />
        </div>
        <div class="card-content">
          <div class="card-label">需要更新</div>
          <div class="card-value">{{ databaseStatus.needs_update_count || 0 }}</div>
        </div>
      </div>

      <div class="overview-card">
        <div class="card-icon updated">
          <font-awesome-icon icon="check-circle" />
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
              <font-awesome-icon :icon="plan.icon" />
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
              :disabled="updateStatus.status === 'running' || (isUpdating && cooldownRemaining > 0)"
              @click="runQuickUpdate(plan)"
            >
              <font-awesome-icon v-if="updateStatus.task_id === plan.id && updateStatus.status === 'running'" icon="spinner" spin />
              <font-awesome-icon v-else-if="isUpdating && cooldownRemaining > 0" icon="clock" />
              <font-awesome-icon v-else icon="play" />
              {{
                updateStatus.task_id === plan.id && updateStatus.status === 'running'
                  ? '运行中...'
                  : isUpdating && cooldownRemaining > 0
                    ? `请等待 ${cooldownRemaining}s`
                    : '立即运行'
              }}
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
            <select v-model="customUpdate.mode" class="form-select" @change="onModeChange">
              <option value="incremental">增量更新（推荐）</option>
              <option value="manual">手动指定时间范围</option>
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
              <option value="auto">自动协同（QMT + Mootdx）</option>
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

        <!-- 手动时间范围选项 -->
        <div v-if="customUpdate.mode === 'manual'" class="form-row">
          <div class="form-group">
            <label>开始日期</label>
            <input
              type="date"
              v-model="customUpdate.startDate"
              class="form-input"
              :max="customUpdate.endDate || todayDate"
            />
          </div>
          <div class="form-group">
            <label>结束日期</label>
            <input
              type="date"
              v-model="customUpdate.endDate"
              class="form-input"
              :max="todayDate"
              :min="customUpdate.startDate"
            />
          </div>
        </div>

        <!-- 板块选择 -->
        <div class="form-row">
          <div class="form-group full-width">
            <label>
              <span style="display: flex; align-items: center; gap: 8px;">
                板块选择（可选）
                <span class="info-badge" title="选择板块后自动加载成分股，留空则更新所有股票">?</span>
              </span>
            </label>
            <div class="sector-selector">
              <el-select
                v-model="selectedSector"
                placeholder="选择板块快速筛选股票..."
                filterable
                clearable
                @change="handleSectorChange"
                style="width: 100%;"
              >
                <el-option-group label="主要指数">
                  <el-option
                    v-for="sector in popularSectors.index"
                    :key="sector.name"
                    :label="`${sector.display_name} (${sector.count}只)`"
                    :value="sector.name"
                  >
                    <span>{{ sector.display_name }}</span>
                    <span class="stock-count">({{ sector.count }}只)</span>
                  </el-option>
                </el-option-group>
                <el-option-group label="市场分类">
                  <el-option
                    v-for="sector in popularSectors.market"
                    :key="sector.name"
                    :label="`${sector.display_name} (${sector.count}只)`"
                    :value="sector.name"
                  >
                    <span>{{ sector.display_name }}</span>
                    <span class="stock-count">({{ sector.count }}只)</span>
                  </el-option>
                </el-option-group>
                <el-option-group label="热门行业">
                  <el-option
                    v-for="sector in popularSectors.industry"
                    :key="sector.name"
                    :label="`${sector.display_name} (${sector.count}只)`"
                    :value="sector.name"
                  >
                    <span>{{ sector.display_name }}</span>
                    <span class="stock-count">({{ sector.count }}只)</span>
                  </el-option>
                </el-option-group>
              </el-select>
            </div>
            <div v-if="selectedSector" class="sector-info">
              <font-awesome-icon icon="info-circle" />
              已选择板块: <strong>{{ getSelectedSectorDisplayName() }}</strong>
              <span v-if="sectorStockCount">({{ sectorStockCount }}只股票)</span>
              <el-button size="small" text @click="clearSector">清除</el-button>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group full-width">
            <label>股票代码（可选，留空则更新所有）</label>
            <textarea
              v-model="customUpdate.symbols"
              class="form-textarea"
              placeholder="输入股票代码，每行一个，如：600000.SH&#10;000001.SZ&#10;或使用上方板块选择功能快速筛选"
              rows="3"
              :disabled="!!selectedSector"
            ></textarea>
            <div v-if="selectedSector" class="input-hint">
              <font-awesome-icon icon="lock" />
              已锁定为板块成分股，清除板块选择后可手动输入
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button class="btn-secondary" @click="resetCustomUpdate">
            <font-awesome-icon icon="undo" />
            重置
          </button>
          <button
            class="btn-primary"
            :disabled="updateStatus.status === 'running' || (isUpdating && cooldownRemaining > 0) || !customUpdate.frequency"
            @click="runCustomUpdate"
          >
            <font-awesome-icon v-if="updateStatus.status === 'running'" icon="spinner" spin />
            <font-awesome-icon v-else-if="isUpdating && cooldownRemaining > 0" icon="clock" />
            <font-awesome-icon v-else icon="play" />
            {{
              updateStatus.status === 'running'
                ? '运行中...'
                : isUpdating && cooldownRemaining > 0
                  ? `请等待 ${cooldownRemaining}s`
                  : '开始更新'
            }}
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
            <font-awesome-icon :icon="getStatusIcon(task.status)" :spin="task.status === 'running'" />
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
          <font-awesome-icon icon="calendar-alt" size="3x" />
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
            <font-awesome-icon icon="times" />
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
    icon: 'chart-line',
    color: '#4CAF50'
  },
  {
    id: '60min',
    name: '60分钟线更新',
    description: '更新60分钟K线数据',
    frequency: '60min',
    source: 'mootdx',
    estimated_time: '10-30分钟',
    icon: 'chart-bar',
    color: '#2196F3'
  },
  {
    id: '5min',
    name: '5分钟线更新',
    description: '更新5分钟K线数据',
    frequency: '5min',
    source: 'mootdx',
    estimated_time: '20-60分钟',
    icon: 'chart-area',
    color: '#FF9800'
  }
])

// 自定义更新选项
const customUpdate = ref({
  mode: 'incremental',
  frequency: 'day',
  source: 'auto',  // 默认使用自动协同模式
  batchSize: 50,
  symbols: '',
  startDate: '',
  endDate: ''
})

// 板块选择相关
const selectedSector = ref('')
const sectorStockCount = ref(0)
const popularSectors = ref({
  index: [] as any[],
  market: [] as any[],
  industry: [] as any[]
})

// 加载常用板块列表
const loadPopularSectors = async () => {
  try {
    const response = await apiRequest.get('/sector/popular')
    if (response.success && response.data?.sectors) {
      const sectors = response.data.sectors

      // 分类整理板块
      popularSectors.value.index = sectors.filter((s: any) =>
        ['csi300', 'csi500', 'sse50', 'csi1000', 'zz1000', 'chuizhian300', 'kcb50', 'cyb50', 'shenzhen_index'].includes(s.name)
      )
      popularSectors.value.market = sectors.filter((s: any) =>
        ['all_a', 'sh_main', 'sz_main', 'cyb', 'kcb', 'bjse'].includes(s.name)
      )
      popularSectors.value.industry = sectors.filter((s: any) =>
        s.category === 'sw1_industry' || s.name.startsWith('sw1_')
      ).slice(0, 20) // 只取前20个热门行业
    }
  } catch (error) {
    console.error('加载常用板块失败:', error)
  }
}

// 处理板块选择变化
const handleSectorChange = async (sectorName: string) => {
  if (!sectorName) {
    selectedSector.value = ''
    sectorStockCount.value = 0
    customUpdate.value.symbols = ''
    return
  }

  selectedSector.value = sectorName

  try {
    // 获取板块成分股
    const response = await apiRequest.post('/sector/stocks', { sector_name: sectorName })

    if (response.success && response.data?.stocks) {
      const stocks = response.data.stocks
      sectorStockCount.value = stocks.length

      // 将股票代码列表填入 symbols 字段
      customUpdate.value.symbols = stocks.map((s: any) => s.code || s).join('\n')
    } else {
      console.error('获取板块成分股失败:', response.message)
      selectedSector.value = ''
    }
  } catch (error: any) {
    console.error('获取板块成分股失败:', error)
    selectedSector.value = ''
  }
}

// 获取选中板块的显示名称
const getSelectedSectorDisplayName = () => {
  if (!selectedSector.value) return ''

  const allSectors = [
    ...popularSectors.value.index,
    ...popularSectors.value.market,
    ...popularSectors.value.industry
  ]
  const sector = allSectors.find(s => s.name === selectedSector.value)
  return sector?.display_name || selectedSector.value
}

// 清除板块选择
const clearSector = () => {
  selectedSector.value = ''
  sectorStockCount.value = 0
  customUpdate.value.symbols = ''
}

// 今天的日期
const todayDate = new Date().toISOString().split('T')[0]

// 模式切换时的处理
const onModeChange = () => {
  if (customUpdate.value.mode === 'manual') {
    // 切换到手动模式时，默认设置最近一周的日期范围
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 7)
    customUpdate.value.endDate = end.toISOString().split('T')[0]
    customUpdate.value.startDate = start.toISOString().split('T')[0]
  }
}

// 设置
const settings = ref({
  autoUpdateEnabled: false,
  autoUpdateTime: '16:00',
  defaultSource: 'mootdx',
  defaultBatchSize: 50
})

let refreshTimer: any = null

// 防抖和冷却机制
let lastUpdateTime: number = 0  // 上次更新时间戳
const UPDATE_COOLDOWN = 3000  // 冷却时间：3秒
const isUpdating = ref(false)  // 是否正在更新（使用 ref 以便在模板中访问）
const cooldownRemaining = ref(0)  // 剩余冷却时间（秒）

// 存储数据库中的所有股票
const databaseStocks = ref<string[]>([])

// 冷却倒计时计时器
let cooldownTimer: any = null

// 更新冷却倒计时
const updateCooldownRemaining = () => {
  const now = Date.now()
  const elapsed = now - lastUpdateTime
  const remaining = Math.max(0, Math.ceil((UPDATE_COOLDOWN - elapsed) / 1000))
  cooldownRemaining.value = remaining

  if (remaining > 0 && !cooldownTimer) {
    cooldownTimer = setInterval(() => {
      const now = Date.now()
      const elapsed = now - lastUpdateTime
      const remaining = Math.max(0, Math.ceil((UPDATE_COOLDOWN - elapsed) / 1000))
      cooldownRemaining.value = remaining

      if (remaining === 0) {
        clearInterval(cooldownTimer)
        cooldownTimer = null
      }
    }, 1000)
  }
}

// 获取数据库中所有股票列表
const fetchDatabaseStocks = async () => {
  try {
    console.log('[fetchDatabaseStocks] 从数据库获取股票列表...')

    // 临时方案：直接扫描本地数据库文件
    // 因为后端API路由有问题，暂时绕过
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiBase}/stock-data-update/database-stocks`)
      const data = await response.json()

      if (data.success && data.stocks) {
        databaseStocks.value = data.stocks
        console.log(`[fetchDatabaseStocks] 从数据库获取到 ${databaseStocks.value.length} 只股票`)
        return databaseStocks.value
      }
    } catch (apiError) {
      console.warn('[fetchDatabaseStocks] API调用失败，使用默认列表:', apiError)
    }

    // 降级方案：使用默认的股票列表
    const defaultStocks = [
      '000001.SZ', '000002.SZ', '000063.SZ', '000333.SZ', '000338.SZ',
      '000651.SZ', '000725.SZ', '000858.SZ', '002415.SZ', '002594.SZ',
      '600000.SH', '600036.SH', '600519.SH', '600900.SH', '601318.SH',
      '601398.SH', '601857.SH', '601988.SH', '603259.SH'
    ]
    databaseStocks.value = defaultStocks
    console.log(`[fetchDatabaseStocks] 使用默认股票列表，共 ${databaseStocks.value.length} 只`)
    return databaseStocks.value

  } catch (error) {
    console.error('[fetchDatabaseStocks] 获取失败:', error)
    // 返回空数组时使用默认值
    const defaultStocks = [
      '000001.SZ', '000002.SZ', '000063.SZ', '000333.SZ', '000338.SZ',
      '000651.SZ', '000725.SZ', '000858.SZ', '002415.SZ', '002594.SZ',
      '600000.SH', '600036.SH', '600519.SH', '600900.SH', '601318.SH',
      '601398.SH', '601857.SH', '601988.SH', '603259.SH'
    ]
    databaseStocks.value = defaultStocks
    return databaseStocks.value
  }
}

// 刷新状态
const refreshStatus = async () => {
  try {
    console.log('[refreshStatus] 开始刷新状态...')

    // 先获取数据库股票列表
    if (databaseStocks.value.length === 0) {
      await fetchDatabaseStocks()
    }

    // 使用数据库中的股票，如果没有则使用默认的3只
    let symbols: string
    if (databaseStocks.value.length > 0) {
      // 限制前500只避免URL过长
      const checkStocks = databaseStocks.value.slice(0, 500)
      symbols = checkStocks.join(',')
      const actualCount = Math.min(databaseStocks.value.length, 500)
      console.log(`[refreshStatus] 检查 ${actualCount} 只股票状态（数据库共 ${databaseStocks.value.length} 只）`)
    } else {
      symbols = '600000.SH,000001.SZ,600036.SH'
      console.log('[refreshStatus] 使用默认股票检查')
    }

    // 获取数据库状态 - 使用 URL 查询字符串
    const statusUrl = `/stock-data-update/database-status?symbols=${symbols}&frequency=day`
    console.log('[refreshStatus] 请求 URL:', statusUrl)

    const statusResponse = await apiRequest.get(statusUrl)
    console.log('[refreshStatus] 完整响应:', statusResponse)
    console.log('[refreshStatus] 响应 code:', statusResponse.code)
    console.log('[refreshStatus] 响应 success:', statusResponse.success)
    console.log('[refreshStatus] 响应 data:', statusResponse.data)

    // 同时检查 code 和 success
    if (statusResponse && (statusResponse.code === 200 || statusResponse.success === true)) {
      // 合并状态：总股票数来自数据库扫描，其他信息来自状态检查
      const checkedCount = statusResponse.data?.total || 0
      const needsUpdateCount = statusResponse.data?.needs_update_count || 0

      // 按比例估算需要更新的数量
      const estimatedNeedsUpdate = checkedCount > 0
        ? Math.round(needsUpdateCount * (databaseStocks.value.length / checkedCount))
        : 0

      databaseStatus.value = {
        ...statusResponse.data,
        total: databaseStocks.value.length, // 使用数据库扫描的总数
        needs_update_count: estimatedNeedsUpdate
      }
      latestTradingDate.value = statusResponse.data?.latest_trading_date || '--'
      console.log('[refreshStatus] 数据库状态更新成功:', {
        databaseStatus: databaseStatus.value,
        latestTradingDate: latestTradingDate.value
      })
    } else {
      console.warn('[refreshStatus] 响应未成功:', statusResponse)
    }

    // 获取任务列表
    const tasksResponse = await apiRequest.get('/stock-data-update/tasks?limit=10')
    console.log('[refreshStatus] 任务列表响应:', tasksResponse)

    if (tasksResponse && (tasksResponse.code === 200 || tasksResponse.success === true)) {
      updateHistory.value = tasksResponse.data?.tasks || []
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
    const now = Date.now()
    const timeSinceLastUpdate = now - lastUpdateTime
    const cooldownRemaining = Math.ceil((UPDATE_COOLDOWN - timeSinceLastUpdate) / 1000)

    // 防抖检查：冷却时间内拒绝重复请求
    if (timeSinceLastUpdate < UPDATE_COOLDOWN && isUpdating.value) {
      console.warn(`[runQuickUpdate] 冷却中，请等待 ${cooldownRemaining} 秒后再试`)
      alert(`数据更新正在进行中，请等待 ${cooldownRemaining} 秒后再试`)
      return
    }

    // 检查是否有任务正在运行
    if (updateStatus.value.status === 'running') {
      console.warn('[runQuickUpdate] 有任务正在运行，拒绝启动新任务')
      alert('有更新任务正在运行中，请等待完成后再试')
      return
    }

    // 更新状态和时间戳
    isUpdating.value = true
    lastUpdateTime = now

    // 启动冷却倒计时
    updateCooldownRemaining()

    console.log('[runQuickUpdate] 开始更新:', plan)

    // 确保数据库股票列表已加载
    if (databaseStocks.value.length === 0) {
      await fetchDatabaseStocks()
    }

    console.log(`[runQuickUpdate] databaseStocks.value.length = ${databaseStocks.value.length}`)

    // 使用URL编码格式发送表单数据
    const params = new URLSearchParams()
    params.append('frequency', plan.frequency)
    params.append('source', plan.source)

    // 添加要更新的股票列表
    if (databaseStocks.value.length > 0) {
      const stocksToUpdate = databaseStocks.value // 更新所有股票
      const symbols = stocksToUpdate.join(',')
      params.append('symbols', symbols)
      console.log(`[runQuickUpdate] 将更新 ${stocksToUpdate.length} 只股票`)
      console.log(`[runQuickUpdate] symbols: ${symbols}`)
      console.log(`[runQuickUpdate] params.toString(): ${params.toString()}`)
    } else {
      console.log('[runQuickUpdate] 警告：databaseStocks 为空！')
    }

    params.append('batch_size', '50')

    console.log(`[runQuickUpdate] 发送请求参数: ${params.toString()}`)

    // 🔧 修复：使用 JSON 格式发送请求
    const jsonData = {
      symbols: params.get('symbols') ? params.get('symbols').split(',') : [],
      frequency: params.get('frequency') || 'day',
      source: params.get('source') || 'auto',
      batch_size: parseInt(params.get('batch_size') || '50')
    }

    const response = await apiRequest.post(
      '/stock-data-update/incremental-update-from-db',
      jsonData,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )

    console.log('[runQuickUpdate] 响应:', response)

    if ((response.success || response.code === 200) && response.data) {
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
    } else {
      // 请求失败，重置更新状态
      isUpdating.value = false
      console.error('[runQuickUpdate] 请求失败:', response)
      alert('启动更新失败，请稍后重试')
    }
  } catch (error) {
    // 异常捕获，重置更新状态
    isUpdating.value = false
    console.error('启动更新失败:', error)
    alert('启动更新失败，请稍后重试')
  }
}

// 运行自定义更新
const runCustomUpdate = async () => {
  try {
    const now = Date.now()
    const timeSinceLastUpdate = now - lastUpdateTime
    const cooldownRemaining = Math.ceil((UPDATE_COOLDOWN - timeSinceLastUpdate) / 1000)

    // 防抖检查：冷却时间内拒绝重复请求
    if (timeSinceLastUpdate < UPDATE_COOLDOWN && isUpdating.value) {
      console.warn(`[runCustomUpdate] 冷却中，请等待 ${cooldownRemaining} 秒后再试`)
      alert(`数据更新正在进行中，请等待 ${cooldownRemaining} 秒后再试`)
      return
    }

    // 检查是否有任务正在运行
    if (updateStatus.value.status === 'running') {
      console.warn('[runCustomUpdate] 有任务正在运行，拒绝启动新任务')
      alert('有更新任务正在运行中，请等待完成后再试')
      return
    }

    // 更新状态和时间戳
    isUpdating.value = true
    lastUpdateTime = now

    // 启动冷却倒计时
    updateCooldownRemaining()

    console.log('[runCustomUpdate] 开始自定义更新，模式:', customUpdate.value.mode)

    const symbols = customUpdate.value.symbols
      ? customUpdate.value.symbols.split('\n').map(s => s.trim()).filter(s => s)
      : []

    // 🔧 修复：使用 JSON 格式发送请求
    const jsonData: any = {
      symbols: symbols,
      frequency: customUpdate.value.frequency,
      source: customUpdate.value.source,
      batch_size: customUpdate.value.batchSize,
      force_full_update: customUpdate.value.mode === 'full'
    }

    // 手动模式：添加日期范围参数
    if (customUpdate.value.mode === 'manual') {
      if (!customUpdate.value.startDate || !customUpdate.value.endDate) {
        console.error('[runCustomUpdate] 手动模式需要指定开始和结束日期')
        return
      }
      jsonData.start_date = customUpdate.value.startDate
      jsonData.end_date = customUpdate.value.endDate
      jsonData.force_full_update = true  // 手动模式强制使用指定日期范围
      console.log(`[runCustomUpdate] 手动模式: ${customUpdate.value.startDate} 到 ${customUpdate.value.endDate}`)
    }

    console.log('[runCustomUpdate] 请求数据:', jsonData)

    const response = await apiRequest.post(
      '/stock-data-update/incremental-update-from-db',
      jsonData,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )

    console.log('[runCustomUpdate] 响应:', response)

    if ((response.success || response.code === 200) && response.data) {
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
    } else {
      // 请求失败，重置更新状态
      isUpdating.value = false
      console.error('[runCustomUpdate] 请求失败:', response)
      alert('启动更新失败，请稍后重试')
    }
  } catch (error) {
    // 异常捕获，重置更新状态
    isUpdating.value = false
    console.error('启动自定义更新失败:', error)
    alert('启动更新失败，请稍后重试')
  }
}

// 开始轮询进度
const startProgressPolling = (taskId: string) => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }

  // 🔧 修复：添加任务不存在计数器和超时机制
  let notFoundCount = 0
  const MAX_NOT_FOUND = 5  // 连续5次查询不到任务就停止轮询

  refreshTimer = setInterval(async () => {
    try {
      const response = await apiRequest.get(`/stock-data-update/tasks/${taskId}`)

      if (response.success && response.data) {
        const task = response.data

        // 重置计数器
        notFoundCount = 0

        updateStatus.value.progress = task.progress || 0
        updateStatus.value.status = task.status === 'completed' ? 'completed' :
                                   task.status === 'failed' ? 'failed' :
                                   task.status === 'not_found' ? 'not_found' : 'running'

        if (task.result) {
          updateStatus.value.updated = task.result.updated || 0
          updateStatus.value.skipped = task.result.skipped || 0
          updateStatus.value.failed = task.result.failed || 0
        }

        // 如果任务完成或不存在，停止轮询
        if (task.status === 'completed' || task.status === 'failed' || task.status === 'not_found') {
          clearInterval(refreshTimer)
          updateStatus.value.task_id = null

          // 🔧 重置更新状态，允许下次更新
          isUpdating.value = false
          console.log('[startProgressPolling] 任务完成，重置更新状态')

          // 如果任务不存在，显示提示
          if (task.status === 'not_found') {
            console.warn(`任务 ${taskId} 不存在或已过期，可能API服务已重启`)
            // 可选：显示用户友好的提示
            // showToast({ type: 'warning', message: '任务不存在或已过期，请重新开始' })
          }

          refreshStatus()
        }
      } else {
        // 响应成功但数据为空（任务不存在）
        notFoundCount++
        console.warn(`任务查询失败 (${notFoundCount}/${MAX_NOT_FOUND}): ${taskId}`)

        // 连续多次查询不到任务，停止轮询
        if (notFoundCount >= MAX_NOT_FOUND) {
          clearInterval(refreshTimer)
          updateStatus.value.task_id = null
          updateStatus.value.status = 'not_found'

          // 🔧 重置更新状态
          isUpdating.value = false
          console.error(`任务 ${taskId} 连续 ${MAX_NOT_FOUND} 次查询失败，停止轮询`)
          refreshStatus()
        }
      }
    } catch (error) {
      console.error('获取任务状态失败:', error)
      notFoundCount++

      // 网络错误也计数
      if (notFoundCount >= MAX_NOT_FOUND) {
        clearInterval(refreshTimer)
        updateStatus.value.task_id = null
        updateStatus.value.status = 'error'
        refreshStatus()
      }
    }
  }, 500) // 每0.5秒轮询一次，提高进度显示流畅度

  // 设置超时：最长轮询30分钟
  setTimeout(() => {
    if (refreshTimer && updateStatus.value.status === 'running') {
      console.warn(`任务 ${taskId} 轮询超时（30分钟），自动停止`)
      clearInterval(refreshTimer)
      updateStatus.value.task_id = null
      updateStatus.value.status = 'timeout'
      refreshStatus()
    }
  }, 30 * 60 * 1000) // 30分钟
}

// 重置自定义更新
const resetCustomUpdate = () => {
  customUpdate.value = {
    mode: 'incremental',
    frequency: 'day',
    source: 'mootdx',
    batchSize: 50,
    symbols: '',
    startDate: '',
    endDate: ''
  }
  // 同时清除板块选择
  clearSector()
}

// 保存设置
const saveSettings = () => {
  localStorage.setItem('stock-update-settings', JSON.stringify(settings.value))
  showUpdateSettings.value = false
}

// 获取状态图标
const getStatusIcon = (status: string) => {
  const icons = {
    completed: 'check',
    failed: 'times-circle',
    running: 'spinner',
    pending: 'clock'
  }
  return icons[status] || 'question'
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
  loadPopularSectors()  // 加载常用板块列表
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
  }
})
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables.scss' as *;

.stock-data-update {
  padding: var(--spacing-4);
  color: var(--text-primary);

  .update-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-4);
    padding-bottom: var(--spacing-3);
    border-bottom: 1px solid var(--border-color);

    .header-info {
      h2 {
        font-size: 24px;
        font-weight: 600;
        margin: 0 0 var(--spacing-1) 0;
        color: var(--text-primary);
        text-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
      }

      p {
        font-size: 14px;
        color: var(--text-secondary);
        margin: 0;
      }
    }

    .header-actions {
      display: flex;
      gap: var(--spacing-2);
    }
  }

  .btn-primary,
  .btn-secondary {
    padding: var(--spacing-2) var(--spacing-4);
    border-radius: var(--border-radius-base);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-1);
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    border: 1px solid transparent;

    i {
      font-size: 16px;
    }
  }

  .btn-primary {
    background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
    color: white;
    border: none;
    box-shadow: var(--shadow-md);

    &:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .btn-secondary {
    background: var(--bg-surface);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);

    &:hover {
      background: var(--bg-elevated);
      border-color: var(--border-light);
    }
  }

  .btn-run {
    background: var(--success);
    color: white;
    border: none;
    padding: var(--spacing-1) var(--spacing-3);
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-1);
    transition: all var(--transition-duration-base);
    box-shadow: var(--shadow-sm);

    &:hover:not(:disabled) {
      background: #059669;
      box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .update-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-3);
    margin-bottom: var(--spacing-6);

    .overview-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius-lg);
      padding: var(--spacing-4);
      display: flex;
      align-items: center;
      gap: var(--spacing-3);
      box-shadow: var(--shadow-md);
      transition: all var(--transition-duration-base);
      position: relative;
      overflow: hidden;

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        opacity: 0;
        transition: opacity var(--transition-duration-base);
      }

      &:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
        border-color: var(--primary);

        &::before {
          opacity: 1;
        }
      }

      .card-icon {
        width: 48px;
        height: 48px;
        border-radius: var(--border-radius-base);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;

        &.latest-date {
          background: rgba(59, 130, 246, 0.2);
          color: var(--info);
          box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
        }

        &.total {
          background: rgba(124, 58, 173, 0.2);
          color: var(--secondary);
          box-shadow: 0 0 12px rgba(124, 58, 173, 0.3);
        }

        &.need-update {
          background: rgba(245, 158, 11, 0.2);
          color: var(--warning);
          box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
        }

        &.updated {
          background: rgba(16, 185, 129, 0.2);
          color: var(--success);
          box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
        }
      }

      .card-content {
        .card-label {
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: var(--spacing-xs);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .card-value {
          font-size: 20px;
          font-weight: 600;
          color: var(--text-primary);
        }
      }
    }
  }

  .quick-update-plans,
  .custom-update-section,
  .update-history {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-5);
    margin-bottom: var(--spacing-5);
    box-shadow: var(--shadow-md);

    h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 0 0 var(--spacing-4) 0;
      color: var(--text-primary);
      text-shadow: 0 0 8px rgba(102, 126, 234, 0.2);
    }
  }

  .plans-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-3);

    .plan-card {
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius-base);
      padding: var(--spacing-4);
      background: rgba(37, 37, 48, 0.5);
      transition: all var(--transition-duration-base);
      position: relative;
      overflow: hidden;

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--plan-color, var(--primary));
        transition: all var(--transition-duration-base);
      }

      &:hover {
        border-color: var(--primary);
        box-shadow: 0 0 16px rgba(102, 126, 234, 0.3);
        transform: translateX(4px);

        &::before {
          width: 6px;
          box-shadow: 0 0 12px var(--plan-color, var(--primary));
        }
      }

      &.plan-running {
        border-color: var(--success);
        background: rgba(16, 185, 129, 0.1);

        &::before {
          background: var(--success);
        }
      }

      .plan-header {
        display: flex;
        gap: var(--spacing-2);
        margin-bottom: var(--spacing-3);

        .plan-icon {
          width: 40px;
          height: 40px;
          border-radius: var(--border-radius-sm);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 18px;
          box-shadow: 0 0 12px var(--plan-color, var(--primary));
        }

        .plan-info {
          h4 {
            font-size: 16px;
            font-weight: 600;
            margin: 0 0 var(--spacing-xs) 0;
            color: var(--text-primary);
          }

          p {
            font-size: 13px;
            color: var(--text-secondary);
            margin: 0;
          }
        }
      }

      .plan-details {
        margin-bottom: var(--spacing-3);

        .plan-detail {
          display: flex;
          justify-content: space-between;
          font-size: 13px;
          margin-bottom: var(--spacing-xs);

          .detail-label {
            color: var(--text-secondary);
          }

          .detail-value {
            color: var(--text-primary);
            font-weight: 500;
          }
        }
      }

      .plan-actions {
        text-align: right;
      }
    }
  }

  .update-progress {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
    border: 1px solid var(--primary);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-5);
    margin-bottom: var(--spacing-5);
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 24px rgba(102, 126, 234, 0.3);

    &::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
      animation: pulse 3s ease-in-out infinite;
    }

    h3 {
      color: var(--text-primary);
      margin-bottom: var(--spacing-3);
      position: relative;
      z-index: 1;
    }

    .progress-container {
      position: relative;
      z-index: 1;

      .progress-info {
        margin-bottom: var(--spacing-2);

        .progress-text {
          display: flex;
          justify-content: space-between;
          margin-bottom: var(--spacing-1);
          font-size: 14px;
          color: var(--text-primary);
        }

        .progress-stats {
          display: flex;
          gap: var(--spacing-4);
          font-size: 13px;
          color: var(--text-secondary);
        }
      }

      .progress-bar-wrapper {
        height: 8px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: var(--border-radius-sm);
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);

        .progress-bar {
          height: 100%;
          background: linear-gradient(90deg, var(--success), var(--info));
          border-radius: var(--border-radius-sm);
          transition: width 0.3s ease;
          box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        }
      }
    }
  }

  .custom-update-form {
    .form-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: var(--spacing-3);
      margin-bottom: var(--spacing-3);

      &.full-width {
        grid-template-columns: 1fr;
      }
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);

      &.full-width {
        grid-column: 1 / -1;
      }

      label {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .form-select,
      .form-textarea {
        padding: var(--spacing-1) var(--spacing-2);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-sm);
        font-size: 14px;
        font-family: inherit;
        background: var(--bg-deep);
        color: var(--text-primary);
        transition: all var(--transition-duration-base);

        &:focus {
          outline: none;
          border-color: var(--primary);
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }
      }

      .form-textarea {
        resize: vertical;
        min-height: 80px;
      }
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: var(--spacing-2);
    }
  }

  .history-list {
    .history-item {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);
      padding: var(--spacing-3);
      border-bottom: 1px solid var(--border-color);
      transition: all var(--transition-duration-base);

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background: rgba(102, 126, 234, 0.05);
      }

      .history-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;

        &.completed {
          background: rgba(16, 185, 129, 0.2);
          color: var(--success);
          box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        }

        &.failed {
          background: rgba(239, 68, 68, 0.2);
          color: var(--danger);
          box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
        }

        &.running {
          background: rgba(59, 130, 246, 0.2);
          color: var(--info);
          box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
        }
      }

      .history-content {
        flex: 1;

        .history-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: var(--spacing-xs);

          .history-title {
            font-size: 14px;
            font-weight: 500;
            color: var(--text-primary);
          }

          .history-time {
            font-size: 12px;
            color: var(--text-secondary);
          }
        }

        .history-details {
          display: flex;
          gap: var(--spacing-3);
          font-size: 12px;
          color: var(--text-secondary);
        }
      }

      .history-status {
        padding: var(--spacing-xs) var(--spacing-2);
        border-radius: var(--border-radius-base);
        font-size: 12px;
        font-weight: 500;

        &.completed {
          background: rgba(16, 185, 129, 0.2);
          color: var(--success);
          border: 1px solid var(--success);
        }

        &.failed {
          background: rgba(239, 68, 68, 0.2);
          color: var(--danger);
          border: 1px solid var(--danger);
        }
      }
    }

    .empty-history {
      text-align: center;
      padding: var(--spacing-8);
      color: var(--text-secondary);

      i {
        font-size: 48px;
        margin-bottom: var(--spacing-3);
        opacity: 0.5;
      }
    }
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg-overlay);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease;

    .modal-content {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius-lg);
      width: 90%;
      max-width: 500px;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: var(--shadow-glow);

      .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-4);
        border-bottom: 1px solid var(--border-color);

        h3 {
          font-size: 18px;
          font-weight: 600;
          margin: 0;
          color: var(--text-primary);
        }

        .modal-close {
          background: none;
          border: none;
          font-size: 20px;
          cursor: pointer;
          color: var(--text-secondary);
          transition: all var(--transition-duration-base);

          &:hover {
            color: var(--text-primary);
            transform: rotate(90deg);
          }
        }
      }

      .modal-body {
        padding: var(--spacing-4);

        .setting-section {
          margin-bottom: var(--spacing-5);

          h4 {
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 var(--spacing-2) 0;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }

          .setting-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-2);
            padding: var(--spacing-2);
            background: var(--bg-deep);
            border-radius: var(--border-radius-sm);

            label {
              font-size: 14px;
              color: var(--text-secondary);
            }

            .form-select {
              padding: var(--spacing-xs) var(--spacing-2);
              border: 1px solid var(--border-color);
              border-radius: var(--border-radius-sm);
              font-size: 14px;
              background: var(--bg-surface);
              color: var(--text-primary);
            }
          }
        }
      }

      .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: var(--spacing-2);
        padding: var(--spacing-4);
        border-top: 1px solid var(--border-color);
      }
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

// 板块选择器样式
.sector-selector {
  :deep(.el-select) {
    .el-select__wrapper {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.1);

      &:hover {
        border-color: rgba(102, 126, 234, 0.5);
      }
    }

    .el-select__placeholder {
      color: rgba(255, 255, 255, 0.4);
    }

    .el-select__selected-item {
      color: var(--text-primary);
    }

    .stock-count {
      color: rgba(255, 255, 255, 0.5);
      font-size: 12px;
      margin-left: 4px;
    }
  }
}

.sector-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  background: rgba(102, 126, 234, 0.1);
  border-radius: var(--border-radius-sm);
  font-size: 13px;
  color: var(--text-secondary);

  svg {
    color: #2962ff;
  }

  strong {
    color: var(--text-primary);
  }
}

.input-hint {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  margin-top: var(--spacing-1);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.info-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.3);
  color: #2962ff;
  font-size: 12px;
  font-weight: 600;
  cursor: help;
}
</style>
