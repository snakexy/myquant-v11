<template>
  <div class="production-detail-view">
    <GlobalNavBar />

    <!-- 任务头部信息 -->
    <div class="task-header-bar">
      <div class="task-title-row">
        <h1 class="task-title">{{ isZh ? currentTask.titleZh : currentTask.title }}</h1>
        <span class="task-id-badge">#{{ currentTask.id }}</span>
      </div>
      <div class="task-config-info" v-if="currentTask.stockPool || currentTask.factors">
        <div class="config-item" v-if="currentTask.stockPool">
          <span class="config-label">{{ isZh ? '股票池' : 'Stock Pool' }}</span>
          <span class="config-value">{{ isZh ? currentTask.stockPoolZh : currentTask.stockPool }}</span>
        </div>
        <div class="config-item" v-if="currentTask.factors">
          <span class="config-label">{{ isZh ? '因子' : 'Factors' }}</span>
          <span class="config-value">{{ isZh ? currentTask.factorsZh : currentTask.factors }}</span>
        </div>
        <div class="config-item" v-if="currentTask.model">
          <span class="config-label">{{ isZh ? '模型' : 'Model' }}</span>
          <span class="config-value">{{ currentTask.model }}</span>
        </div>
      </div>
    </div>

    <!-- Dashboard指标区域 -->
    <div class="dashboard-panel">
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">{{ isZh ? '总资产' : 'Total Assets' }}</div>
          <div class="metric-value">¥{{ formatAssets(dashboard.totalAssets) }}</div>
          <div :class="['metric-change', dashboard.assetsTrend]">
            {{ getTrendIcon(dashboard.assetsTrend) }} {{ dashboard.assetsChange > 0 ? '+' : '' }}{{ dashboard.assetsChange.toFixed(1) }}%
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ isZh ? '今日盈亏' : "Today's P&L" }}</div>
          <div :class="['metric-value', { positive: dashboard.todayPnL > 0, negative: dashboard.todayPnL < 0 }]">
            {{ dashboard.todayPnL >= 0 ? '+' : '' }}¥{{ formatNumber(dashboard.todayPnL) }}
          </div>
          <div :class="['metric-change', dashboard.pnlTrend]">
            {{ getTrendIcon(dashboard.pnlTrend) }} {{ dashboard.pnlChange > 0 ? '+' : '' }}{{ dashboard.pnlChange.toFixed(1) }}%
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ isZh ? '仓位' : 'Positions' }}</div>
          <div class="metric-value">{{ dashboard.positionRate }}%</div>
          <div :class="['metric-change', dashboard.positionTrend]">
            {{ getTrendIcon(dashboard.positionTrend) }} {{ Math.abs(dashboard.positionChange) }}%
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ isZh ? '最大回撤' : 'Max Drawdown' }}</div>
          <div :class="['metric-value', { negative: dashboard.maxDrawdown > 0 }]">
            -{{ dashboard.maxDrawdown.toFixed(1) }}%
          </div>
          <div :class="['metric-change', dashboard.drawdownTrend]">
            {{ getTrendIcon(dashboard.drawdownTrend) }} {{ Math.abs(dashboard.drawdownChange).toFixed(1) }}%
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ isZh ? '夏普比率' : 'Sharpe Ratio' }}</div>
          <div :class="['metric-value', { positive: dashboard.sharpeRatio > 1 }]">
            {{ dashboard.sharpeRatio.toFixed(2) }}
          </div>
          <div class="metric-change stable">
            → {{ isZh ? '稳定' : 'Stable' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 主交易区域 -->
    <div class="main-container">
      <!-- ===== 实盘交易模块 ===== -->
      <template v-if="currentStageModule === 'trading'">
        <!-- 左侧：持仓列表 -->
        <aside class="panel position-panel">
          <div class="panel-header">
            <span class="panel-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <path d="M3 9h18M9 21V9"/>
              </svg>
              {{ isZh ? '当前持仓' : 'Current Positions' }}
            </span>
            <span class="position-count">{{ positions.length }} {{ isZh ? '只' : 'stocks' }}</span>
          </div>
          <table class="position-table">
            <thead>
              <tr>
                <th>{{ isZh ? '代码' : 'Symbol' }}</th>
                <th>{{ isZh ? '数量' : 'Qty' }}</th>
                <th>{{ isZh ? '成本' : 'Cost' }}</th>
                <th>{{ isZh ? '现价' : 'Current' }}</th>
                <th>{{ isZh ? '盈亏' : 'P&L' }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pos in positions" :key="pos.symbol" @click="selectPosition(pos)">
                <td>
                  <span class="symbol">{{ pos.symbol }}</span>
                </td>
                <td>{{ pos.quantity }}</td>
                <td>¥{{ pos.costPrice.toFixed(2) }}</td>
                <td>¥{{ pos.currentPrice.toFixed(2) }}</td>
                <td :class="['pnl', { positive: pos.pnlRate > 0, negative: pos.pnlRate < 0 }]">
                  {{ pos.pnlRate >= 0 ? '+' : '' }}{{ pos.pnlRate.toFixed(1) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </aside>

        <!-- 中间：TradingView K线图 -->
        <main class="panel chart-panel">
          <div class="panel-header">
            <span class="panel-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3v18h18"/>
                <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
              </svg>
              {{ isZh ? 'K线图' : 'K-Line Chart' }}
              <span v-if="selectedPosition" class="chart-stock-name">
                - {{ selectedPosition.name }} ({{ selectedPosition.symbol }})
              </span>
            </span>
            <div class="timeframe-buttons">
              <button
                v-for="tf in timeframes"
                :key="tf.id"
                :class="['tf-btn', { active: currentTimeframe === tf.id }]"
                @click="changeTimeframe(tf.id)"
              >
                {{ tf.label }}
              </button>
            </div>
          </div>
          <div class="chart-body">
            <!-- TradingView K线图组件 - 使用key强制周期切换时重新渲染 -->
            <TradingViewKLineUnified
              v-if="chartSymbol"
              :key="`${chartSymbol}-${currentTimeframe}`"
              :symbol="chartSymbol"
              :stock-name="selectedPosition?.name || ''"
              :stock-code="selectedPosition?.symbol || ''"
              :period="currentTimeframe"
              height="100%"
              :show-toolbar="false"
              :show-legend="true"
              theme="dark"
              :enable-realtime="true"
              @chart-ready="onChartReady"
              @period-change="onPeriodChange"
            />
            <!-- 无持仓选中时的提示 -->
            <div v-else class="chart-placeholder">
              <svg class="placeholder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 3v18h18"/>
                <path d="M7 16l4-4 4 4 5-6"/>
              </svg>
              <p class="placeholder-text">{{ isZh ? '请从左侧选择持仓股票查看K线图' : 'Select a position to view K-line chart' }}</p>
            </div>
          </div>
        </main>

        <!-- 右侧：交易面板 -->
        <aside class="panel trade-panel">
          <div class="panel-header">
            <span class="panel-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
              {{ isZh ? '快速交易' : 'Quick Trade' }}
            </span>
          </div>

          <div class="trade-content">
            <!-- 价格显示 -->
            <div class="price-display">
              <div :class="['current-price', selectedPosition?.pnlRate >= 0 ? 'up' : 'down']">
                {{ selectedPosition?.currentPrice.toFixed(2) || '1850.00' }}
              </div>
              <div :class="['price-change', selectedPosition?.pnlRate >= 0 ? 'up' : 'down']">
                {{ selectedPosition?.pnlRate >= 0 ? '+' : '' }}{{ selectedPosition?.currentPrice && selectedPosition?.costPrice ?
                  ((selectedPosition.currentPrice - selectedPosition.costPrice).toFixed(2)) : '+42.50' }}
                ({{ selectedPosition?.pnlRate >= 0 ? '+' : '' }}{{ selectedPosition?.pnlRate.toFixed(2) || '+2.35' }}%)
              </div>
            </div>

            <!-- 五档行情 -->
            <div class="order-book">
              <div class="order-column">
                <div class="order-row sell" v-for="(ask, idx) in askOrders" :key="'ask'+idx">
                  <span class="order-label">{{ isZh ? '卖' : 'Ask' }} {{ 5 - idx }}</span>
                  <span class="order-price">{{ ask.price }}</span>
                  <span class="order-size">{{ ask.size }}</span>
                </div>
              </div>
              <div class="order-column">
                <div class="order-row buy" v-for="(bid, idx) in bidOrders" :key="'bid'+idx">
                  <span class="order-label">{{ isZh ? '买' : 'Bid' }} {{ idx + 1 }}</span>
                  <span class="order-price">{{ bid.price }}</span>
                  <span class="order-size">{{ bid.size }}</span>
                </div>
              </div>
            </div>

            <!-- 交易按钮 -->
            <div class="action-buttons">
              <button class="trade-btn buy" @click="placeOrder('buy')">
                {{ isZh ? '买入' : 'BUY' }}
              </button>
              <button class="trade-btn sell" @click="placeOrder('sell')">
                {{ isZh ? '卖出' : 'SELL' }}
              </button>
            </div>
          </div>
        </aside>
      </template>

      <!-- ===== ML信号模块 ===== -->
      <template v-else-if="currentStageModule === 'ml-signal'">
        <div class="module-content">
          <h2 class="module-title">{{ isZh ? 'ML交易信号' : 'ML Trading Signals' }}</h2>
          <p class="module-subtitle">{{ isZh ? '基于机器学习模型生成的交易信号' : 'Trading signals generated by ML models' }}</p>

          <!-- ML信号统计 -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">{{ isZh ? '今日信号' : 'Today Signals' }}</div>
              <div class="stat-value positive">{{ mlStats.todaySignals }}</div>
              <div class="stat-change">{{ isZh ? '个股票' : 'stocks' }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">{{ isZh ? '买入信号' : 'Buy Signals' }}</div>
              <div class="stat-value positive">{{ mlStats.buySignals }}</div>
              <div class="stat-change">{{ isZh ? '看涨' : 'Bullish' }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">{{ isZh ? '卖出信号' : 'Sell Signals' }}</div>
              <div class="stat-value negative">{{ mlStats.sellSignals }}</div>
              <div class="stat-change">{{ isZh ? '看跌' : 'Bearish' }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">{{ isZh ? '模型准确率' : 'Model Accuracy' }}</div>
              <div :class="['stat-value', { positive: mlStats.accuracy > 60 }]">
                {{ mlStats.accuracy.toFixed(1) }}%
              </div>
              <div class="stat-change">{{ isZh ? '近30天' : 'Last 30 days' }}</div>
            </div>
          </div>

          <!-- 信号列表 -->
          <div class="signal-list-container">
            <h3 class="section-title">{{ isZh ? '最新ML信号' : 'Latest ML Signals' }}</h3>
            <table class="signal-table">
              <thead>
                <tr>
                  <th>{{ isZh ? '股票代码' : 'Symbol' }}</th>
                  <th>{{ isZh ? '股票名称' : 'Name' }}</th>
                  <th>{{ isZh ? '信号类型' : 'Signal' }}</th>
                  <th>{{ isZh ? '置信度' : 'Confidence' }}</th>
                  <th>{{ isZh ? '模型版本' : 'Model' }}</th>
                  <th>{{ isZh ? '生成时间' : 'Time' }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="signal in mlSignals" :key="signal.code">
                  <td class="symbol">{{ signal.code }}</td>
                  <td>{{ signal.name }}</td>
                  <td>
                    <span :class="['signal-badge', signal.type]">
                      {{ signal.type === 'buy' ? (isZh ? '买入' : 'Buy') : (isZh ? '卖出' : 'Sell') }}
                    </span>
                  </td>
                  <td :class="['confidence', { high: signal.confidence > 0.8 }]">
                    {{ (signal.confidence * 100).toFixed(0) }}%
                  </td>
                  <td class="model-version">{{ signal.model }}</td>
                  <td class="time">{{ signal.time }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button class="btn btn-primary" @click="refreshMLSignals">
              {{ isZh ? '刷新信号' : 'Refresh Signals' }}
            </button>
            <button class="btn btn-secondary" @click="exportMLSignals">
              {{ isZh ? '导出信号' : 'Export Signals' }}
            </button>
          </div>
        </div>
      </template>

      <!-- ===== 风险监控模块 ===== -->
      <template v-else-if="currentStageModule === 'risk'">
        <RiskMonitorChart
          :task-id="taskId"
          :is-zh="isZh"
          ref="riskMonitorRef"
          style="grid-column: 1 / -1; width: 100%;"
        />
      </template>

      <!-- ===== 告警管理模块 ===== -->
      <template v-else-if="currentStageModule === 'alerts'">
        <div class="module-content">
          <h2 class="module-title">{{ isZh ? '告警管理' : 'Alert Management' }}</h2>
          <p class="module-subtitle">{{ isZh ? '查看和管理系统告警' : 'View and manage system alerts' }}</p>

          <!-- 告警统计 -->
          <div class="alert-summary">
            <div class="alert-stat critical">
              <span class="count">{{ alertStats.critical }}</span>
              <span class="label">{{ isZh ? '严重' : 'Critical' }}</span>
            </div>
            <div class="alert-stat warning">
              <span class="count">{{ alertStats.warning }}</span>
              <span class="label">{{ isZh ? '警告' : 'Warning' }}</span>
            </div>
            <div class="alert-stat info">
              <span class="count">{{ alertStats.info }}</span>
              <span class="label">{{ isZh ? '信息' : 'Info' }}</span>
            </div>
          </div>

          <!-- 告警列表 -->
          <div class="alert-list">
            <div :class="['alert-item', alert.level]" v-for="alert in alerts" :key="alert.id">
              <div class="alert-icon">{{ getAlertIcon(alert.level) }}</div>
              <div class="alert-content">
                <div class="alert-message">{{ isZh ? alert.messageZh : alert.message }}</div>
                <div class="alert-meta">
                  <span class="alert-time">{{ alert.time }}</span>
                  <span class="alert-source">{{ alert.source }}</span>
                </div>
              </div>
              <button class="btn-dismiss" @click="dismissAlert(alert.id)">
                {{ isZh ? '忽略' : 'Dismiss' }}
              </button>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button class="btn btn-primary" @click="refreshAlerts">
              {{ isZh ? '刷新告警' : 'Refresh Alerts' }}
            </button>
            <button class="btn btn-secondary" @click="clearAllAlerts">
              {{ isZh ? '清除所有' : 'Clear All' }}
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- 底部面板 - 仅交易模块显示 -->
    <div v-if="currentStageModule === 'trading'" class="bottom-panel">
      <!-- 今日委托 -->
      <div class="panel orders-panel">
        <div class="panel-header">
          <span class="panel-title">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            {{ isZh ? '今日委托' : "Today's Orders" }}
          </span>
          <span class="order-count">{{ todayOrders.length }} {{ isZh ? '笔' : 'orders' }}</span>
        </div>
        <div class="orders-list">
          <div class="order-item" v-for="order in todayOrders" :key="order.id">
            <span class="order-time">{{ order.time }}</span>
            <span :class="['order-type', order.side]">{{ order.side === 'buy' ? (isZh ? '买入' : 'BUY') : (isZh ? '卖出' : 'SELL') }}</span>
            <span class="order-symbol">{{ order.symbol }} {{ order.name }}</span>
            <span class="order-qty">{{ order.quantity }}{{ isZh ? '股' : 'shares' }}</span>
            <span :class="['order-pnl', { positive: order.pnl > 0, negative: order.pnl < 0 }]">
              {{ order.pnl >= 0 ? '+' : '' }}{{ order.pnl.toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- 风险监控 -->
      <div class="panel risk-panel">
        <div class="panel-header">
          <span class="panel-title">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            {{ isZh ? '风险监控' : 'Risk Monitor' }}
          </span>
          <span :class="['risk-status', riskStatus]">{{ getRiskStatusText(riskStatus) }}</span>
        </div>
        <div class="risk-content">
          <div class="risk-item" v-for="risk in riskMetrics" :key="risk.id">
            <div class="risk-header">
              <span class="risk-label">{{ isZh ? risk.labelZh : risk.label }}</span>
              <span :class="['risk-value', risk.level]">
                {{ risk.current }}% ({{ isZh ? '限制' : 'limit' }} {{ risk.limit }}%)
              </span>
            </div>
            <div class="risk-bar">
              <div
                :class="['risk-bar-fill', risk.level]"
                :style="{ width: `${(risk.current / risk.limit) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import TradingViewKLineUnified from '@/components/charts/TradingViewKLineUnified.vue'
import RiskMonitorChart from './RiskMonitorChart.vue'
import { useAppStore } from '@/stores/core/AppStore'
import GlobalNavBar from '@/components/GlobalNavBar.vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

// 组件引用
const riskMonitorRef = ref<InstanceType<typeof RiskMonitorChart> | null>(null)

// 获取URL中的taskId参数
const taskId = computed(() => route.query.taskId as string || 'default')

// 任务配置存储
interface TaskConfig {
  id: string
  title: string
  titleZh: string
  stockPool?: string
  stockPoolZh?: string
  factors?: string
  factorsZh?: string
  model?: string
  progress: number
  status: string
}

const taskStore: Record<string, TaskConfig> = {
  'PRD-2024-001': {
    id: 'PRD-2024-001',
    title: 'Alpha158 Live Trading',
    titleZh: 'Alpha158实盘交易',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    factors: 'Alpha158',
    factorsZh: 'Alpha158因子集',
    model: 'LightGBM',
    progress: 85,
    status: 'running'
  },
  'PRD-2024-002': {
    id: 'PRD-2024-002',
    title: 'ML Signal Generation Service',
    titleZh: 'ML信号生成服务',
    stockPool: 'All A-shares',
    stockPoolZh: '全A股',
    factors: 'ML Features',
    factorsZh: 'ML特征',
    model: 'Ensemble',
    progress: 92,
    status: 'running'
  },
  'PRD-2024-003': {
    id: 'PRD-2024-003',
    title: 'Risk Monitor - Portfolio Exposure',
    titleZh: '风险监控 - 组合敞口',
    stockPool: 'CSI300+CSI500',
    stockPoolZh: '沪深300+中证500',
    progress: 100,
    status: 'running'
  },
  'PRD-2024-004': {
    id: 'PRD-2024-004',
    title: 'Alert System - Drawdown Warning',
    titleZh: '预警系统 - 回撤预警',
    stockPool: 'All Positions',
    stockPoolZh: '全部持仓',
    progress: 100,
    status: 'running'
  },
  'default': {
    id: 'PRD-DEFAULT',
    title: 'Production Task',
    titleZh: '实盘任务',
    progress: 80,
    status: 'running'
  }
}

const currentTask = computed(() => taskStore[taskId.value] || taskStore['default'])

// 导航相关
const isZh = computed(() => appStore.language === 'zh')

// 阶段模块导航
const currentStageModule = ref('trading')

const switchStageModule = (module: string) => {
  currentStageModule.value = module
  console.log('Switching to module:', module)
}

const goBack = () => {
  router.push('/workflow')
}

// 仪表盘指标
const dashboard = reactive({
  totalAssets: 1230000,
  assetsChange: 0.5,
  assetsTrend: 'up' as 'up' | 'down' | 'stable',
  todayPnL: 12000,
  pnlChange: 0.8,
  pnlTrend: 'up' as 'up' | 'down' | 'stable',
  positionRate: 65,
  positionChange: -2,
  positionTrend: 'down' as 'up' | 'down' | 'stable',
  maxDrawdown: 3.2,
  drawdownChange: 0.1,
  drawdownTrend: 'down' as 'up' | 'down' | 'stable',
  sharpeRatio: 1.85
})

const formatAssets = (val: number) => {
  if (val >= 1000000) {
    return (val / 1000000).toFixed(2) + 'M'
  }
  return val.toLocaleString('zh-CN')
}

const formatNumber = (val: number) => {
  if (val >= 1000) {
    return (val / 1000).toFixed(0) + 'K'
  }
  return val.toLocaleString('zh-CN')
}

const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
  const icons = {
    up: '▲',
    down: '▼',
    stable: '→'
  }
  return icons[trend]
}

// 持仓
interface Position {
  symbol: string
  name: string
  quantity: number
  costPrice: number
  currentPrice: number
  pnlRate: number
}

const positions = ref<Position[]>([
  { symbol: '600519', name: '贵州茅台', quantity: 100, costPrice: 1800.00, currentPrice: 1850.00, pnlRate: 2.8 },
  { symbol: '000858', name: '五粮液', quantity: 50, costPrice: 150.00, currentPrice: 152.00, pnlRate: 1.3 },
  { symbol: '600036', name: '招商银行', quantity: 200, costPrice: 35.00, currentPrice: 35.60, pnlRate: 1.7 },
  { symbol: '000001', name: '平安银行', quantity: 300, costPrice: 12.50, currentPrice: 12.35, pnlRate: -1.2 },
  { symbol: '600276', name: '恒瑞医药', quantity: 150, costPrice: 45.00, currentPrice: 46.50, pnlRate: 3.3 }
])

const selectedPosition = ref<Position | null>(positions.value[0])

const selectPosition = (pos: Position) => {
  selectedPosition.value = pos
}

// K线图相关
const chartSymbol = computed(() => {
  if (!selectedPosition.value) return ''
  // 转换股票代码格式: 600519 -> 600519.SH (上证) 或 000001 -> 000001.SZ (深证)
  const code = selectedPosition.value.symbol
  if (code.startsWith('6')) {
    return `${code}.SH`
  } else {
    return `${code}.SZ`
  }
})

const onChartReady = () => {
  console.log('[ProductionDetailView] K线图已加载:', chartSymbol.value)
}

const onPeriodChange = (period: string) => {
  currentTimeframe.value = period
  console.log('[ProductionDetailView] 周期切换:', period)
}

// 时间周期 - 支持8种周期
const timeframes = [
  { id: '1m', label: '1分' },
  { id: '5m', label: '5分' },
  { id: '15m', label: '15分' },
  { id: '30m', label: '30分' },
  { id: '60m', label: '60分' },
  { id: 'day', label: '日线' },
  { id: 'week', label: '周线' },
  { id: 'month', label: '月线' }
]

const currentTimeframe = ref('day')

const changeTimeframe = (tf: string) => {
  console.log('[ProductionDetailView] 切换周期:', tf)
  currentTimeframe.value = tf
}

// 五档行情
const askOrders = ref([
  { price: '1852.00', size: 23 },
  { price: '1851.50', size: 45 },
  { price: '1851.00', size: 67 },
  { price: '1850.50', size: 89 },
  { price: '1850.00', size: 156 }
])

const bidOrders = ref([
  { price: '1849.50', size: 203 },
  { price: '1849.00', size: 178 },
  { price: '1848.50', size: 145 },
  { price: '1848.00', size: 98 },
  { price: '1847.50', size: 56 }
])

const placeOrder = (side: 'buy' | 'sell') => {
  console.log(`Placing ${side} order for`, selectedPosition.value?.symbol)
}

// 今日委托
interface Order {
  id: string
  time: string
  side: 'buy' | 'sell'
  symbol: string
  name: string
  quantity: number
  pnl: number
}

const todayOrders = ref<Order[]>([
  { id: '1', time: '09:31:25', side: 'buy', symbol: '600519', name: '贵州茅台', quantity: 100, pnl: 1.2 },
  { id: '2', time: '09:32:10', side: 'sell', symbol: '000858', name: '五粮液', quantity: 50, pnl: 0.8 },
  { id: '3', time: '09:33:05', side: 'buy', symbol: '600036', name: '招商银行', quantity: 200, pnl: -0.3 }
])

// 风险指标
interface RiskMetric {
  id: string
  label: string
  labelZh: string
  current: number
  limit: number
  level: 'safe' | 'warning' | 'danger'
}

const riskMetrics = ref<RiskMetric[]>([
  { id: 'single', label: 'Single Position', labelZh: '单只持仓', current: 15, limit: 20, level: 'safe' },
  { id: 'sector', label: 'Sector Concentration', labelZh: '行业集中度', current: 35, limit: 40, level: 'warning' },
  { id: 'drawdown', label: 'Current Drawdown', labelZh: '当前回撤', current: 3.2, limit: 15, level: 'safe' },
  { id: 'dailyLoss', label: 'Daily Loss', labelZh: '日内亏损', current: 0.8, limit: 5, level: 'safe' },
  { id: 'volatility', label: 'Volatility', labelZh: '波动率', current: 18, limit: 20, level: 'safe' }
])

const riskStatus = computed(() => {
  const hasDanger = riskMetrics.value.some(r => r.level === 'danger')
  const hasWarning = riskMetrics.value.some(r => r.level === 'warning')
  if (hasDanger) return 'danger'
  if (hasWarning) return 'warning'
  return 'safe'
})

const getRiskStatusText = (status: string) => {
  const statusMapZh: Record<string, string> = {
    safe: '安全',
    warning: '警告',
    danger: '危险'
  }
  const statusMapEn: Record<string, string> = {
    safe: 'Safe',
    warning: 'Warning',
    danger: 'Danger'
  }
  return isZh.value ? statusMapZh[status] : statusMapEn[status]
}

const getRiskLevelText = (level: string) => {
  const levelMapZh: Record<string, string> = {
    safe: '安全',
    warning: '警告',
    danger: '危险'
  }
  const levelMapEn: Record<string, string> = {
    safe: 'Safe',
    warning: 'Warning',
    danger: 'Danger'
  }
  return isZh.value ? levelMapZh[level] : levelMapEn[level]
}

// ========== ML信号模块数据 ==========
const mlStats = reactive({
  todaySignals: 18,
  buySignals: 12,
  sellSignals: 6,
  accuracy: 68.5
})

interface MLSignal {
  code: string
  name: string
  type: 'buy' | 'sell'
  confidence: number
  model: string
  time: string
}

const mlSignals = ref<MLSignal[]>([
  { code: '600519', name: '贵州茅台', type: 'buy', confidence: 0.85, model: 'v1.2.0', time: '09:31:12' },
  { code: '000858', name: '五粮液', type: 'buy', confidence: 0.78, model: 'v1.2.0', time: '09:35:08' },
  { code: '600036', name: '招商银行', type: 'sell', confidence: 0.72, model: 'v1.2.0', time: '09:42:33' },
  { code: '000001', name: '平安银行', type: 'buy', confidence: 0.68, model: 'v1.2.0', time: '10:15:45' },
  { code: '601318', name: '中国平安', type: 'sell', confidence: 0.65, model: 'v1.2.0', time: '10:28:22' },
  { code: '600276', name: '恒瑞医药', type: 'buy', confidence: 0.82, model: 'v1.2.0', time: '10:45:15' }
])

const refreshMLSignals = () => {
  console.log('Refreshing ML signals...')
}

const exportMLSignals = () => {
  console.log('Exporting ML signals...')
}

const refreshRiskMetrics = () => {
  riskMonitorRef.value?.refresh()
  console.log('Refreshing risk metrics...')
}

const exportRiskReport = () => {
  console.log('Exporting risk report...')
}

// ========== 告警管理模块数据 ==========
const alertStats = reactive({
  critical: 2,
  warning: 5,
  info: 12
})

interface SystemAlert {
  id: string
  level: 'critical' | 'warning' | 'info'
  message: string
  messageZh: string
  time: string
  source: string
}

const alerts = ref<SystemAlert[]>([
  { id: '1', level: 'critical', message: 'Position limit exceeded for 600519', messageZh: '600519持仓超限', time: '10:30:15', source: 'Risk Engine' },
  { id: '2', level: 'critical', message: 'Daily loss limit approaching', messageZh: '日内亏损接近限制', time: '10:25:42', source: 'Risk Engine' },
  { id: '3', level: 'warning', message: 'Sector concentration high in consumer', messageZh: '消费行业集中度过高', time: '10:20:33', source: 'Risk Engine' },
  { id: '4', level: 'warning', message: 'Model signal delay detected', messageZh: '检测到模型信号延迟', time: '10:15:18', source: 'ML Pipeline' },
  { id: '5', level: 'info', message: 'Model retraining scheduled', messageZh: '模型重训练已安排', time: '09:00:00', source: 'System' }
])

const getAlertIcon = (level: string) => {
  const icons: Record<string, string> = {
    critical: '🔴',
    warning: '⚠️',
    info: 'ℹ️'
  }
  return icons[level] || 'ℹ️'
}

const dismissAlert = (id: string) => {
  alerts.value = alerts.value.filter(a => a.id !== id)
  console.log('Dismissed alert:', id)
}

const refreshAlerts = () => {
  console.log('Refreshing alerts...')
}

const clearAllAlerts = () => {
  alerts.value = []
  console.log('Cleared all alerts')
}

// 生命周期
let refreshInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  console.log('ProductionDetailView mounted')
  // 可以添加定时刷新逻辑
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
/* 主容器 */
.production-detail-view {
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  /* A股颜色规则：红涨绿跌 */
  --color-up: #ef5350;      /* 红色 - 上涨/正面 */
  --color-down: #26a69a;    /* 绿色 - 下跌/负面 */
  --accent-red: #ef5350;
  --accent-green: #26a69a;
  --accent-orange: #ff9800;
  --border-color: #2a2e39;

  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  background: #131722;
  color: #d1d4dc;
  font-size: 13px;
  overflow: hidden;
}

/* 任务头部信息栏 */
.task-header-bar {
  padding: 12px 24px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.task-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.task-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.task-id-badge {
  padding: 4px 10px;
  background: rgba(38, 166, 154, 0.15);
  border: 1px solid rgba(38, 166, 154, 0.3);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-green);
  font-family: monospace;
}

.task-config-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.config-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Dashboard面板 */
.dashboard-panel {
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.metric-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 14px;
}

.metric-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 6px;
}

.metric-value.positive {
  color: var(--color-up);
}

.metric-value.negative {
  color: var(--color-down);
}

.metric-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.metric-change.up {
  color: var(--color-up);
}

.metric-change.down {
  color: var(--color-down);
}

.metric-change.stable {
  color: var(--text-secondary);
}

/* 主容器布局 */
.main-container {
  display: grid;
  grid-template-columns: 300px 1fr 320px;
  flex: 1;
  gap: 1px;
  background: var(--border-color);
  min-height: 0;
}

/* 面板通用样式 */
.panel {
  background: var(--bg-primary);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  background: var(--bg-secondary);
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 持仓表格 */
.position-count {
  font-size: 11px;
  color: var(--text-secondary);
}

.position-table {
  width: 100%;
  border-collapse: collapse;
}

.position-table th {
  background: var(--bg-tertiary);
  padding: 10px 12px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border-color);
}

.position-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  color: var(--text-primary);
}

.position-table tr {
  cursor: pointer;
  transition: background 0.15s;
}

.position-table tr:hover {
  background: var(--bg-secondary);
}

.symbol {
  font-weight: 600;
  color: var(--accent-blue);
}

.pnl {
  font-weight: 600;
}

.pnl.positive {
  color: var(--color-up);
}

.pnl.negative {
  color: var(--color-down);
}

/* 图表面板 */
.timeframe-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.chart-stock-name {
  font-size: 12px;
  color: var(--text-secondary);
  margin-left: 8px;
}

.tf-btn {
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border: none;
  color: var(--text-primary);
  font-size: 11px;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.tf-btn:hover {
  background: var(--accent-blue);
  color: white;
}

.tf-btn.active {
  background: var(--accent-blue);
  color: white;
}

.chart-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  position: relative;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  text-align: center;
  padding: 40px;
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.placeholder-text {
  font-size: 14px;
  max-width: 200px;
}

.price-chart {
  width: 100%;
  height: 100%;
}

/* 交易面板 */
.trade-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.price-display {
  text-align: center;
  margin-bottom: 20px;
}

.current-price {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.current-price.up {
  color: var(--color-up);
}

.current-price.down {
  color: var(--color-down);
}

.price-change {
  font-size: 13px;
}

.price-change.up {
  color: var(--color-up);
}

.price-change.down {
  color: var(--color-down);
}

/* 五档行情 */
.order-book {
  flex: 1;
}

.order-column {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.order-row {
  display: grid;
  grid-template-columns: 50px 1fr 50px;
  gap: 6px;
  padding: 6px 8px;
  font-size: 11px;
  border-radius: 3px;
}

.order-row.sell {
  background: rgba(38, 166, 154, 0.1);
  color: var(--color-down);
}

.order-row.buy {
  background: rgba(239, 83, 80, 0.1);
  color: var(--color-up);
}

.order-label {
  color: var(--text-secondary);
}

.order-price {
  text-align: right;
  font-weight: 600;
}

.order-size {
  text-align: right;
}

/* 交易按钮 */
.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: auto;
}

.trade-btn {
  padding: 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 0.5px;
  transition: all 0.15s;
}

.trade-btn.buy {
  background: var(--color-up);
  color: white;
}

.trade-btn.buy:hover {
  opacity: 0.9;
}

.trade-btn.sell {
  background: var(--color-down);
  color: white;
}

.trade-btn.sell:hover {
  opacity: 0.9;
}

/* 底部面板 */
.bottom-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: 200px;
  gap: 1px;
  background: var(--border-color);
}

/* 委托列表 */
.order-count {
  font-size: 11px;
  color: var(--text-secondary);
}

.orders-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.order-item {
  display: grid;
  grid-template-columns: 70px 50px 1fr 60px 60px;
  gap: 10px;
  padding: 8px 0;
  font-size: 12px;
  border-bottom: 1px solid var(--border-color);
  align-items: center;
}

.order-time {
  color: var(--text-secondary);
}

.order-type {
  font-weight: 600;
}

.order-type.buy {
  color: var(--color-up);
}

.order-type.sell {
  color: var(--color-down);
}

.order-pnl {
  font-weight: 600;
}

.order-pnl.positive {
  color: var(--color-up);
}

.order-pnl.negative {
  color: var(--color-down);
}

/* 风险面板 */
.risk-panel .panel-header {
  gap: 12px;
}

.risk-status {
  padding: 4px 10px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.risk-status.safe {
  background: rgba(239, 83, 80, 0.2);
  color: var(--color-up);
}

.risk-status.warning {
  background: rgba(255, 152, 0, 0.2);
  color: var(--accent-orange);
}

.risk-status.danger {
  background: rgba(38, 166, 154, 0.2);
  color: var(--color-down);
}

.risk-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.risk-item {
  margin-bottom: 12px;
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 12px;
}

.risk-label {
  font-weight: 600;
  color: var(--text-primary);
}

.risk-value {
  font-size: 11px;
}

.risk-value.safe {
  color: var(--color-up);
}

.risk-value.warning {
  color: var(--accent-orange);
}

.risk-value.danger {
  color: var(--color-down);
}

.risk-bar {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.risk-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.risk-bar-fill.safe {
  background: var(--color-up);
}

.risk-bar-fill.warning {
  background: var(--accent-orange);
}

.risk-bar-fill.danger {
  background: var(--color-down);
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #363a45;
}

/* 模块内容通用样式 */
.module-content {
  padding: 24px;
  overflow-y: auto;
  background: var(--bg-primary);
  flex: 1;
}

.module-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.module-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.positive {
  color: var(--color-up);
}

.stat-value.negative {
  color: var(--color-down);
}

.stat-change {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* 信号表格 */
.signal-list-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.signal-table {
  width: 100%;
  border-collapse: collapse;
}

.signal-table th {
  text-align: left;
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-color);
}

.signal-table td {
  padding: 12px;
  font-size: 13px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.signal-badge {
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.signal-badge.buy {
  background: rgba(239, 83, 80, 0.2);
  color: var(--color-up);
}

.signal-badge.sell {
  background: rgba(38, 166, 154, 0.2);
  color: var(--color-down);
}

.confidence.high {
  color: var(--color-up);
  font-weight: 600;
}

.model-version {
  color: var(--text-secondary);
  font-size: 12px;
}

.time {
  color: var(--text-secondary);
}

/* 风险仪表盘 */
.risk-dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.risk-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
}

.risk-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.risk-level {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
}

.risk-level.safe {
  background: rgba(239, 83, 80, 0.2);
  color: var(--color-up);
}

.risk-level.warning {
  background: rgba(255, 152, 0, 0.2);
  color: var(--accent-orange);
}

.risk-level.danger {
  background: rgba(38, 166, 154, 0.2);
  color: var(--color-down);
}

.risk-progress {
  margin-top: 12px;
}

.risk-bar-bg {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.risk-values {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 12px;
}

.current {
  font-weight: 600;
  color: var(--text-primary);
}

.limit {
  color: var(--text-secondary);
}

/* 告警统计 */
.alert-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.alert-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 32px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.alert-stat .count {
  font-size: 32px;
  font-weight: 700;
}

.alert-stat .label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.alert-stat.critical .count {
  color: var(--color-down);
}

.alert-stat.warning .count {
  color: var(--accent-orange);
}

.alert-stat.info .count {
  color: var(--accent-blue);
}

/* 告警列表 */
.alert-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.alert-item.critical {
  border-left: 3px solid var(--color-down);
}

.alert-item.warning {
  border-left: 3px solid var(--accent-orange);
}

.alert-item.info {
  border-left: 3px solid var(--accent-blue);
}

.alert-icon {
  font-size: 20px;
}

.alert-content {
  flex: 1;
}

.alert-message {
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.alert-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--text-secondary);
}

.btn-dismiss {
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border: none;
  color: var(--text-secondary);
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-dismiss:hover {
  background: var(--border-color);
  color: var(--text-primary);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover {
  background: #1e4bd8;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: #363a45;
}
</style>
