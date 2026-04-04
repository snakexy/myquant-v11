<template>
  <div class="realtime-quotes-view">
    <GlobalNavBar />

    <div class="main-container">
      <div class="content-area">
        <!-- 左侧股票列表 -->
        <WatchlistPanel
          :selected-stock="selectedStock"
          :mini-charts-data="miniChartsData"
          @select-stock="selectStock"
        />

        <!-- 中间图表区域 -->
        <div class="chart-area">
          <div class="chart-toolbar">
            <span class="current-stock-name">{{ currentStockName }}</span>
            <div class="toolbar-right">
              <button
                v-for="tf in timeframes"
                :key="tf.value"
                :class="['timeframe-btn', { active: currentTimeframe === tf.value }]"
                @click="changeTimeframe(tf.value)"
              >
                {{ tf.label }}
              </button>
              <div class="toolbar-divider-v"></div>
              <button
                :class="['timeframe-btn', { active: adjustType === 'none' }]"
                @click="changeAdjustType('none')"
              >
                {{ isZh ? '不复权' : 'Raw' }}
              </button>
              <button
                :class="['timeframe-btn', { active: adjustType === 'qfq' }]"
                @click="changeAdjustType('qfq')"
              >
                {{ isZh ? '前复权' : 'Adj' }}
              </button>
              <div class="toolbar-divider-v"></div>
              <!-- 价格预警工具按钮 -->
              <button
                :class="['timeframe-btn', { active: priceLineToolActive }]"
                @click="togglePriceLineTool"
                @contextmenu="showPriceLineContextMenu"
                :title="priceLineToolActive ? '点击图表添加价格线（再次按钮退出）' : '左键：画线工具 / 右键：管理价格线'"
              >
                ✏️
              </button>
            </div>
          </div>

          <!-- 价格线右键菜单 -->
          <teleport to="body">
            <div
              v-if="showContextMenu"
              class="price-line-context-menu"
              :style="{ left: contextMenuPosition.x + 'px', top: contextMenuPosition.y + 'px' }"
              @click.stop
            >
              <div class="context-menu-header">价格线管理</div>
              <div class="context-menu-content">
                <div class="price-alert-input-row">
                  <input
                    v-model.number="priceAlertInput"
                    type="number"
                    step="0.01"
                    placeholder="输入目标价格"
                    class="price-alert-input"
                    @keyup.enter="addPriceAlertFromMenu"
                  />
                  <button class="price-alert-add-btn" @click="addPriceAlertFromMenu">添加</button>
                </div>
                <div class="price-alert-list">
                  <div
                    v-for="alert in getPriceAlerts()"
                    :key="alert.id"
                    class="price-alert-item"
                  >
                    <span class="price-alert-price">{{ alert.price.toFixed(2) }}</span>
                    <button class="price-alert-remove-btn" @click="removePriceAlert(alert.id); closeContextMenu()">&times;</button>
                  </div>
                  <div v-if="getPriceAlerts().length === 0" class="price-alert-empty">
                    暂无价格提醒
                  </div>
                </div>
                <button v-if="getPriceAlerts().length > 0" class="price-alert-clear-btn" @click="clearAllPriceAlerts(); closeContextMenu()">
                  清除全部
                </button>
              </div>
            </div>
            <!-- 点击外部关闭菜单的遮罩 -->
            <div v-if="showContextMenu" class="context-menu-overlay" @click="closeContextMenu"></div>
          </teleport>

          <!-- 价格预警面板（保留，可通过按钮打开） -->
          <div v-if="showPriceAlertPanel" class="price-alert-panel">
            <div class="price-alert-header">
              <span>价格提醒</span>
              <button class="price-alert-close" @click="showPriceAlertPanel = false">&times;</button>
            </div>
            <div class="price-alert-content">
              <div class="price-alert-input-row">
                <input
                  v-model.number="priceAlertInput"
                  type="number"
                  step="0.01"
                  placeholder="输入目标价格"
                  class="price-alert-input"
                  @keyup.enter="addPriceAlert"
                />
                <button class="price-alert-add-btn" @click="addPriceAlert">添加</button>
              </div>
              <div class="price-alert-list">
                <div
                  v-for="alert in getPriceAlerts()"
                  :key="alert.id"
                  class="price-alert-item"
                >
                  <span class="price-alert-price">{{ alert.price.toFixed(2) }}</span>
                  <button class="price-alert-remove-btn" @click="removePriceAlert(alert.id)">&times;</button>
                </div>
                <div v-if="getPriceAlerts().length === 0" class="price-alert-empty">
                  暂无价格提醒
                </div>
              </div>
              <button v-if="getPriceAlerts().length > 0" class="price-alert-clear-btn" @click="clearAllPriceAlerts">
                清除全部
              </button>
            </div>
          </div>

          <!-- K线图容器（副图指标通过 chart.addPane() 在同一实例内开） -->
          <div class="chart-container">
            <div ref="chartContainer" class="kline-chart"></div>

            <!-- 价格标签交互层（覆盖在原生标签上） -->
            <div class="price-labels-left" :key="priceAlertsKey">
              <div
                v-for="alert in getPriceAlerts()"
                :key="alert.id"
                class="price-label-left"
                :style="{ top: getAlertLabelPosition(alert.price) + 'px', background: alert.color }"
                :class="{
                  dragging: isDragging && draggedAlertId === alert.id,
                  editing: editingAlertId === alert.id,
                  'alert-flash': flashingAlerts.has(alert.id)
                }"
                :data-alert-id="alert.id"
                @dblclick="startEditPriceAlert(alert.id, alert.price)"
                @contextmenu.prevent="showLabelContextMenu(alert, $event)"
                @mousedown="startDragAlert(alert.id, $event)"
                @touchstart.prevent="startDragAlert(alert.id, $event)"
              >
                <input
                  v-if="editingAlertId === alert.id"
                  :ref="el => editingAlertId === alert.id && (editingInput = el)"
                  v-model="editingAlertPrice"
                  type="number"
                  step="0.01"
                  class="price-label-input"
                  @blur="finishEditPriceAlert(alert.id)"
                  @keyup.enter="finishEditPriceAlert(alert.id)"
                  @keyup.esc="cancelEditPriceAlert"
                  @mousedown.stop
                />
                <span v-else class="label-text">{{ alert.price.toFixed(2) }}</span>
              </div>
            </div>

            <!-- 标签右键菜单 -->
            <teleport to="body">
              <div
                v-if="labelContextMenu.show"
                class="label-context-menu"
                :style="{ left: labelContextMenu.x + 'px', top: labelContextMenu.y + 'px' }"
                @click.stop
              >
                <div class="label-menu-header">价格线设置</div>
                <div class="label-menu-content">
                  <!-- 价格 -->
                  <div class="label-menu-row">
                    <label>目标价格：</label>
                    <input
                      v-model.number="labelContextMenu.currentPrice"
                      type="number"
                      step="0.01"
                      class="label-menu-input"
                    />
                  </div>
                  <!-- 标签名称 -->
                  <div class="label-menu-row">
                    <label>标签名称：</label>
                    <input
                      v-model="labelContextMenu.currentTitle"
                      type="text"
                      class="label-menu-input"
                      placeholder="留空显示价格"
                    />
                  </div>
                  <!-- 颜色选择 -->
                  <div class="label-menu-row">
                    <label>线条颜色：</label>
                    <div class="color-picker">
                      <div
                        v-for="color in presetColors"
                        :key="color"
                        class="color-option"
                        :class="{ active: labelContextMenu.currentColor === color }"
                        :style="{ background: color }"
                        @click="labelContextMenu.currentColor = color"
                      ></div>
                    </div>
                  </div>
                  <!-- 启用提醒 -->
                  <div class="label-menu-row">
                    <label class="checkbox-label">
                      <input
                        v-model="labelContextMenu.enableAlert"
                        type="checkbox"
                        class="checkbox-input"
                      />
                      <span>价格到达时闪烁提醒</span>
                    </label>
                  </div>
                  <!-- 操作按钮 -->
                  <div class="label-menu-actions">
                    <button class="label-menu-btn cancel" @click="closeLabelContextMenu">取消</button>
                    <button class="label-menu-btn confirm" @click="applyLabelSettings">确定</button>
                  </div>
                </div>
              </div>
              <div v-if="labelContextMenu.show" class="context-menu-overlay" @click="closeLabelContextMenu"></div>
            </teleport>

            <!-- OHLCV legend 悬浮在图表左上角 -->
            <div v-if="hoverBar" class="chart-legend-overlay">
              <span class="legend-time">{{ hoverBar.time }}</span>
              <span class="legend-item">O <em :class="hoverBar.close>=hoverBar.open?'positive':'negative'">{{ hoverBar.open?.toFixed(2) }}</em></span>
              <span class="legend-item">H <em :class="hoverBar.close>=hoverBar.open?'positive':'negative'">{{ hoverBar.high?.toFixed(2) }}</em></span>
              <span class="legend-item">L <em :class="hoverBar.close>=hoverBar.open?'positive':'negative'">{{ hoverBar.low?.toFixed(2) }}</em></span>
              <span class="legend-item">C <em :class="hoverBar.close>=hoverBar.open?'positive':'negative'">{{ hoverBar.close?.toFixed(2) }}</em></span>
              <span class="legend-item">V <em>{{ formatVolume(hoverBar.volume) }}</em></span>
            </div>

            <!-- 加载状态 -->
            <div v-if="loading" class="chart-loading">
              <div class="spinner"></div>
              <span>加载中...</span>
            </div>
          </div>
        </div>

        <!-- 右侧信息面板 -->
        <div class="panel info-panel">
          <div class="panel-header">
            <div class="stock-info-header">
              <div class="stock-name-large">{{ currentStockName || '--' }}</div>
              <div class="stock-code-small">{{ selectedStock || '--' }}</div>
            </div>
          </div>

          <div class="trade-section">
            <div class="price-display">
              <div :class="['current-price', currentQuote.change >= 0 ? 'positive' : 'negative']">
                {{ currentQuote.price || '--' }}
              </div>
              <div :class="['price-change', currentQuote.change >= 0 ? 'positive' : 'negative']">
                {{ currentQuote.change >= 0 ? '+' : '' }}{{ currentQuote.change }}
                ({{ currentQuote.change_percent >= 0 ? '+' : '' }}{{ currentQuote.change_percent }}%)
              </div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">{{ isZh ? '五档盘口' : 'Order Book' }}</div>
            <div class="order-book">
              <div class="order-column">
                <div v-for="(ask, i) in asks.slice().reverse()" :key="'ask'+i" class="order-row sell">
                  <span>{{ isZh ? '卖' : 'Sell' }} {{ i + 1 }}</span>
                  <span class="order-price">{{ ask.price }}</span>
                  <span class="order-size">
                    <span class="size-bar" :style="{ width: getSizePercent(ask.size) + '%' }"></span>
                    {{ formatOrderSize(ask.size) }}
                  </span>
                </div>
              </div>
              <div class="order-column">
                <div v-for="(bid, i) in bids" :key="'bid'+i" class="order-row buy">
                  <span>{{ isZh ? '买' : 'Buy' }} {{ i + 1 }}</span>
                  <span class="order-price">{{ bid.price }}</span>
                  <span class="order-size">
                    <span class="size-bar" :style="{ width: getSizePercent(bid.size) + '%' }"></span>
                    {{ formatOrderSize(bid.size) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">{{ isZh ? '统计数据' : 'Stats' }}</div>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">{{ isZh ? '开盘' : 'Open' }}</div>
                <div class="info-value">{{ currentQuote.open || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '最高' : 'High' }}</div>
                <div class="info-value">{{ currentQuote.high || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '最低' : 'Low' }}</div>
                <div class="info-value">{{ currentQuote.low || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '昨收' : 'Prev' }}</div>
                <div class="info-value">{{ currentQuote.prev_close || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '成交量' : 'Volume' }}</div>
                <div class="info-value">{{ formatVolume(currentQuote.volume) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '成交额' : 'Amount' }}</div>
                <div class="info-value">{{ formatAmount(currentQuote.amount) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '换手率' : 'Turnover' }}</div>
                <div class="info-value">{{ currentQuote.turnover_rate ? currentQuote.turnover_rate + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '总量' : 'Volume' }}</div>
                <div class="info-value">{{ formatVolume(currentQuote.volume) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '振幅' : 'Amplitude' }}</div>
                <div class="info-value">{{ currentQuote.amplitude ? currentQuote.amplitude + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '量比' : 'Vol Ratio' }}</div>
                <div class="info-value" :class="currentQuote.volume_ratio > 1 ? 'positive' : currentQuote.volume_ratio < 1 ? 'negative' : ''">{{ currentQuote.volume_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '外盘' : 'Outer' }}</div>
                <div class="info-value positive">{{ formatVol(currentQuote.outer_vol) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '内盘' : 'Inner' }}</div>
                <div class="info-value negative">{{ formatVol(currentQuote.inner_vol) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '市盈率' : 'P/E' }}</div>
                <div class="info-value">{{ currentQuote.pe_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '市净率' : 'P/B' }}</div>
                <div class="info-value">{{ currentQuote.pb_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '股息率' : 'Div Yield' }}</div>
                <div class="info-value">{{ currentQuote.dy_ratio ? currentQuote.dy_ratio + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '涨停价' : 'Limit Up' }}</div>
                <div class="info-value positive">{{ currentQuote.zt_price || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '跌停价' : 'Limit Down' }}</div>
                <div class="info-value negative">{{ currentQuote.dt_price || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '贝塔系数' : 'Beta' }}</div>
                <div class="info-value">{{ currentQuote.beta || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '总股本' : 'Shares' }}</div>
                <div class="info-value">{{ formatShares(currentQuote.total_shares) }}</div>
              </div>
              <div class="info-item" style="grid-column: 1 / -1;">
                <div class="data-source-info">
                  <span class="data-source-label">{{ isZh ? '数据源' : 'Source' }}</span>
                  <span class="data-source-value">{{ currentQuote.data_source }}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- 底部状态栏 -->
      <div class="statusbar">
        <div class="statusbar-section">
          <span class="stock-name-display">{{ currentStockName }}</span>
          <div class="statusbar-divider"></div>
          <span>{{ isZh ? '成交' : 'Vol' }}: {{ formatAmount(currentQuote.amount) }}</span>
          <div class="statusbar-divider"></div>
          <template v-for="idx in indices" :key="idx.code">
            <span class="index-item">
              <span class="index-name">{{ idx.name }}</span>
              <span :class="['index-price', idx.change >= 0 ? 'positive' : 'negative']">{{ idx.price }}</span>
              <span :class="['index-change', idx.change >= 0 ? 'positive' : 'negative']">
                {{ idx.change >= 0 ? '+' : '' }}{{ idx.change }}%
              </span>
            </span>
            <div class="statusbar-divider"></div>
          </template>
          <span style="margin-left: auto; color: #4a4f60;">实时行情</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { createChart, CrosshairMode, CandlestickSeries, HistogramSeries } from 'lightweight-charts'
import GlobalNavBar from '@/components/GlobalNavBar.vue'
import WatchlistPanel from '@/components/watchlist/WatchlistPanel.vue'
import { useAppStore } from '@/stores/core/AppStore'
import { useDataStore } from '@/stores/core/DataStore'
import {
  fetchKline,
  fetchSnapshot,
  fetchSnapshotBatch,
  fetchMarketStatus,
  type KlineItem,
  type QuoteSnapshot,
  type MarketStatus
} from '@/api/modules/quotes'
import { createKlineWebSocket, type KlineBar } from '@/services/klineWebSocket'
import { createKlineAggregator, type Timeframe } from '@/services/klineAggregator'
import { UserPriceAlerts } from '@/components/charts/plugins'

// 类型定义
type ChartApi = any
type SeriesApi = any

interface QuoteData {
  price: string | number
  change: number
  change_percent: number
  open: string | number
  high: string | number
  low: string | number
  prev_close: string | number
  volume: number
  amount: number
  turnover_rate: number
  amplitude: number
  volume_ratio: number
  outer_vol: number
  inner_vol: number
  pe_ratio: number
  pb_ratio: number
  dy_ratio: number
  zt_price: string | number
  dt_price: string | number
  beta: number
  total_shares: number
  data_source: string
}

// 周期选项（响应语言切换）
const timeframes = computed(() => [
  { label: isZh.value ? '分时' : '1m',   value: '1m' },
  { label: isZh.value ? '5分' : '5m',    value: '5m' },
  { label: isZh.value ? '15分' : '15m',  value: '15m' },
  { label: isZh.value ? '30分' : '30m',  value: '30m' },
  { label: isZh.value ? '60分' : '1h',   value: '1h' },
  { label: isZh.value ? '日K' : 'Day',   value: '1d' },
  { label: isZh.value ? '周K' : 'Week',  value: '1w' },
  { label: isZh.value ? '月K' : 'Month', value: '1M' },
])

// 从 localStorage 恢复上次选中的股票和周期
const getLastSelectedStock = (): string => {
  try {
    const saved = localStorage.getItem('realtime_quotes_last_stock')
    // 检查值是否有效（非空、不是 "undefined" 字符串）
    if (saved && saved !== 'undefined' && saved.trim()) {
      return saved
    }
  } catch (e) {}
  return ''
}

const getLastTimeframe = (): string => {
  try {
    const saved = localStorage.getItem('realtime_quotes_last_timeframe')
    // 检查值是否有效
    if (saved && saved !== 'undefined' && saved.trim()) {
      return saved
    }
  } catch (e) {}
  return '1d'  // 默认日线
}

const selectedStock = ref(getLastSelectedStock())
const currentTimeframe = ref(getLastTimeframe())
const appStore = useAppStore()
const dataStore = useDataStore()
const isZh = computed(() => appStore.language === 'zh')

const loading = ref(false)
const adjustType = ref('qfq')

// 滚动加载状态
const isLoadingMore = ref(false)           // 是否正在加载更多数据
const totalLoadedCount = ref(200)          // 已加载的总条数
const hasMoreHistory = ref(true)           // 是否还有更多历史数据
const klineData = ref<any[]>([])           // K线数据存储

// 后端 change_pct 字段兼容工具（pytdx 返回 change_pct，部分接口返回 change_percent）
const getChangePct = (q: any): number => parseFloat(Number(q.change_pct ?? q.change_percent ?? 0).toFixed(2))

// miniCharts removed, using miniChartsData with time-based X-axis instead

// 沪深指数
const indices = ref([
  { code: '000001.SH', name: '上证', price: '--', change: 0 },
  { code: '399001.SZ', name: '深证', price: '--', change: 0 },
  { code: '399006.SZ', name: '创业板', price: '--', change: 0 },
])

// 当前行情数据
const currentQuote = ref<QuoteData>({
  price: '--',
  change: 0,
  change_percent: 0,
  open: '--',
  high: '--',
  low: '--',
  prev_close: '--',
  volume: 0,
  amount: 0,
  turnover_rate: 0,
  amplitude: 0,
  volume_ratio: 0,
  outer_vol: 0,
  inner_vol: 0,
  pe_ratio: 0,
  pb_ratio: 0,
  dy_ratio: 0,
  zt_price: '--',
  dt_price: '--',
  beta: 0,
  total_shares: 0,
  data_source: 'unknown'
})

// 五档盘口数据（从API获取）
const asks = ref([
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 }
])

const bids = ref([
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 }
])

// 图表实例
const chartContainer = ref<HTMLElement>()
let chart: ChartApi | null = null
let candleSeries: SeriesApi | null = null
let volumeSeries: SeriesApi | null = null
let updateTimer: number | null = null
let statusTimer: number | null = null
let chartResizeObserver: ResizeObserver | null = null

// WebSocket 实例（1分钟线实时推送）
let klineWs: any = null  // KlineWebSocket
let aggregator: any = null  // Kline聚合器（所有周期都用WS，前端聚合）
const wsConnected = ref(false)

// 十字光标悬停的 bar 数据
const hoverBar = ref<{ time: string; open: number; high: number; low: number; close: number; volume: number } | null>(null)

// 当前股票名称（从行情数据获取）
const currentStockName = ref('')

// 价格预警相关
let userPriceAlerts: UserPriceAlerts | null = null
const showPriceAlertPanel = ref(false)
const priceAlertInput = ref<number | null>(null)
const priceLineToolActive = ref(false)  // 价格线工具激活状态
const isDragging = ref(false)  // 是否正在拖动
const draggedAlertId = ref<string | null>(null)  // 正在拖动的价格线ID
const draggedAlertTempPrice = ref<number | null>(null)  // 拖动时的临时价格（用于平滑显示）
const editingAlertId = ref<string | null>(null)  // 正在编辑的价格线ID
const editingAlertPrice = ref<string>('')  // 正在编辑的价格值
const editingInput = ref<HTMLInputElement | null>(null)  // 编辑输入框引用
const priceAlertsList = ref<any[]>([])  // 响应式价格线列表
const priceAlertsKey = ref(0)  // 强制刷新 key
const showContextMenu = ref(false)  // 右键菜单显示状态
const contextMenuPosition = ref({ x: 0, y: 0 })  // 右键菜单位置
// 标签右键菜单状态
const labelContextMenu = ref({
  show: false,
  alertId: '',
  x: 0,
  y: 0,
  currentPrice: 0,
  currentTitle: '',
  currentColor: '',
  enableAlert: false,  // 是否启用提醒
})

// 价格提醒状态（记录已提醒过的价格线）
const triggeredAlerts = ref<Set<string>>(new Set())
// 当前正在闪烁的标签ID
const flashingAlerts = ref<Set<string>>(new Set())

// 格式化成交量
const formatVolume = (vol: number): string => {
  if (!vol) return '--'
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toString()
}

// 迷你折线图数据：存储带时间戳的K线 {time: Date, close: number}
const miniChartsData = ref<Record<string, Array<{time: Date, close: number}>>>({})

// 后台预加载自选股列表的K线数据（无感缓存）
let preloadAbortController: AbortController | null = null

const preloadWatchlistKlines = async () => {
  const currentStocks = dataStore.activeGroup?.stocks || []
  const otherStocks = currentStocks.filter((s: any) => s.symbol !== selectedStock.value)
  if (otherStocks.length === 0) return

  // 要预加载的周期（当前周期 + 常用周期）
  const periodsToPreload = Array.from(new Set([
    currentTimeframe.value,
    '1m', '5m', '1d'  // 常用周期
  ]))

  console.log('[Preload] 开始后台预加载', otherStocks.length, '只自选股，周期:', periodsToPreload)

  // 取消之前的预加载任务
  if (preloadAbortController) {
    preloadAbortController.abort()
  }
  preloadAbortController = new AbortController()
  const signal = preloadAbortController.signal

  let completed = 0
  const total = otherStocks.length * periodsToPreload.length

  for (const stock of otherStocks) {
    for (const period of periodsToPreload) {
      // 检查是否被取消
      if (signal.aborted) return

      // 验证股票代码有效性
      const code = stock.code || stock.symbol
      if (!code || code === 'undefined' || !code.trim()) {
        console.warn('[Preload] 跳过无效股票:', stock)
        continue
      }

      // 延迟执行，避免阻塞主线程和突发请求
      await new Promise(resolve => setTimeout(resolve, 100))

      try {
        // 低优先级获取，只缓存不显示（count=300足够近期使用）
        await fetchKline(code, period, 300, adjustType.value)
        completed++

        // 每完成5个打印一次日志
        if (completed % 5 === 0 || completed === total) {
          console.log(`[Preload] 进度: ${completed}/${total}`)
        }
      } catch (e) {
        // 静默失败，不影响用户体验
        console.debug(`[Preload] ${code} ${period} 预加载失败`)
      }
    }
  }

  console.log('[Preload] 预加载完成，已缓存', completed, '条数据')
}

// 迷你折线图定时刷新器
let miniChartsTimer: number | null = null

// 迷你折线图：获取自选股的当天 1 分钟收盘价
const loadMiniCharts = async () => {
  const currentStocks = dataStore.activeGroup?.stocks || []
  console.log('[loadMiniCharts] 开始加载，股票数量:', currentStocks.length)
  const tasks = currentStocks.map(async (stock: any) => {
    try {
      // 兼容 symbol 和 code 字段
      const symbol = stock.symbol || stock.code
      // 更严格的检查：排除空值、undefined、"undefined" 字符串
      if (!symbol || symbol === 'undefined' || !symbol.trim()) {
        console.warn('[loadMiniCharts] 跳过无效股票:', stock)
        return
      }
      console.log(`[loadMiniCharts] 正在加载 ${symbol}...`)
      const res = await fetchKline(symbol, '1m', 240, 'none')  // 1分钟，全天240根
      if (res.data && res.data.length >= 5) {
        // 转换为带时间戳的数据，并按时间排序
        const barsWithTime = res.data
          .map((b: KlineItem) => ({
            time: new Date(Number(b.time)),
            close: Number(b.close)
          }))
          .sort((a, b) => a.time.getTime() - b.time.getTime())

        // 找到最新一天的开盘时间
        const latestTime = barsWithTime[barsWithTime.length - 1].time
        const dayOpen = new Date(latestTime)
        dayOpen.setHours(9, 30, 0, 0)

        // 只保留当天开盘之后的数据
        const todayBars = barsWithTime.filter(b => b.time >= dayOpen)
        console.log(`[loadMiniCharts] ${symbol} 成功，数据点数:`, todayBars.length)
        miniChartsData.value[symbol] = todayBars
      } else {
        console.log(`[loadMiniCharts] ${symbol} 数据不足，res.data.length:`, res.data?.length)
        miniChartsData.value[symbol] = []
      }
    } catch (e) {
      console.error(`[loadMiniCharts] ${stock.symbol || stock.code} 加载失败:`, e)
      const symbol = stock.symbol || stock.code
      if (symbol) miniChartsData.value[symbol] = []
    }
  })
  await Promise.all(tasks)
  console.log('[loadMiniCharts] 加载完成，miniChartsData:', Object.keys(miniChartsData.value))
}

// 将带时间戳的价格数组转为 SVG polyline points 字符串
// X轴：按交易分钟数映射（A股240个交易分钟）
// Y轴：价格映射
const sparklinePoints = (data: Array<{time: Date, close: number}>): string => {
  if (!data || data.length < 2) return ''
  const W = 120, H = 28

  // A股交易时间：240个1分钟K线
  // 上午：9:30-11:30（120分钟）
  // 下午：13:00-15:00（120分钟）
  const TOTAL_TRADING_MINUTES = 240

  const prices = data.map(d => d.close)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1

  return data.map((d) => {
    const hour = d.time.getHours()
    const minute = d.time.getMinutes()

    // 计算交易分钟数（从0开始）
    // 北京时间：上午 9:30-11:30，下午 13:00-15:00
    let tradingMinutes = (hour - 9) * 60 + (minute - 30)

    // 下午时段减去中午休市的90分钟（11:30-13:00）
    if (hour >= 13) {
      tradingMinutes -= 90
    }

    // 计算在240个交易分钟中的位置（0-1）
    const position = tradingMinutes / TOTAL_TRADING_MINUTES

    // 限制在 0-1 范围内
    const clampedPos = Math.max(0, Math.min(1, position))
    const x = clampedPos * W
    const y = H - ((d.close - min) / range) * (H - 4) - 2
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}

const sparklineColor = (data: Array<{time: Date, close: number}>): string => {
  if (!data || data.length < 2) return '#4a4f60'
  return data[data.length - 1].close >= data[0].close ? '#ef5350' : '#26a69a'
}

// 格式化成交额
const formatAmount = (amt: number): string => {
  if (!amt) return '--'
  if (amt >= 100000000) return (amt / 100000000).toFixed(2) + '亿'
  if (amt >= 10000) return (amt / 10000).toFixed(2) + '万'
  return amt.toString()
}

// 格式化股本（总股本）
const formatShares = (shares: number): string => {
  if (!shares) return '--'
  if (shares >= 100000000) return (shares / 100000000).toFixed(2) + '亿'
  if (shares >= 10000) return (shares / 10000).toFixed(2) + '万'
  return shares.toLocaleString()
}

// 格式化内外盘（股）
const formatVol = (vol: number): string => {
  if (!vol) return '--'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toLocaleString()
}

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return

  // 创建主图表（先用 fallback 尺寸，之后通过轮询拿到真实高度）
  const w = chartContainer.value.clientWidth || 600
  const h = chartContainer.value.clientHeight
         || (window.innerHeight - 56 - 42 - 28 - 100) // nav+toolbar+status+volume
  chart = createChart(chartContainer.value, {
    width: w,
    height: h,
    layout: {
      background: { color: '#131722' },
      textColor: '#d1d4dc'
    },
    grid: {
      vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
      horzLines: { color: 'rgba(42, 46, 57, 0.5)' }
    },
    crosshair: {
      mode: CrosshairMode.Normal
    },
    rightPriceScale: {
      borderColor: 'transparent',
      autoScale: false,
    },
    handleScroll: {
      mouseWheel: true,
      pressedMouseMove: true,
      horzTouchDrag: true,
      vertTouchDrag: true,
    },
    handleScale: {
      axisPressedMouseMove: {
        time: true,
        price: true,
      },
    },
    timeScale: {
      borderColor: 'rgba(42, 46, 57, 0.8)',
      timeVisible: true,
      secondsVisible: false,
      minBarSpacing: 0.5,
      rightOffset: 10,
      fixLeftEdge: true,
      fixRightEdge: false
    },
    // 时间轴配置
    localization: {
      dateFormat: 'yyyy-MM-dd',
      timeFormatter: (timestamp: number) => {
        const date = new Date(timestamp * 1000)
        const year = date.getUTCFullYear()
        const month = String(date.getUTCMonth() + 1).padStart(2, '0')
        const day = String(date.getUTCDate()).padStart(2, '0')
        const hours = String(date.getUTCHours()).padStart(2, '0')
        const minutes = String(date.getUTCMinutes()).padStart(2, '0')
        // 日线/周线只显示日期，分钟线显示日期+时间
        const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
        return isDaily
          ? `${year}-${month}-${day}`
          : `${year}-${month}-${day} ${hours}:${minutes}`
      }
    }
  })

  // 创建K线系列（中国股市：红涨绿跌）
  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#ef5350',        // 上涨红色（默认）
    downColor: '#26a69a',      // 下跌绿色（默认）
    borderVisible: false,
    wickUpColor: '#ef5350',    // 上影线红色
    wickDownColor: '#26a69a',   // 下影线绿色
    // 使用自定义颜色对象，根据API返回的color字段设置每根K线的颜色
    // 注意：需要将数据格式转换为lightweight-charts支持的格式
  })

  // 创建成交量系列
  volumeSeries = chart.addSeries(HistogramSeries, {
    color: '#26a69a',
    priceFormat: {
      type: 'volume'
    },
    priceScaleId: 'volume'
  })

  chart.priceScale('volume').applyOptions({
    scaleMargins: {
      top: 0.8,
      bottom: 0
    }
  })

  // 从 chart-area 反算正确高度（避免 canvas 干扰 clientHeight 读取）
  let retries = 0
  const syncSize = () => {
    if (!chart || !chartContainer.value) return
    const chartArea = chartContainer.value.closest('.chart-area') as HTMLElement
    if (chartArea) {
      const areaH = chartArea.getBoundingClientRect().height
      const toolbar = chartArea.querySelector('.chart-toolbar') as HTMLElement
      const toolbarH = toolbar?.getBoundingClientRect().height || 42
      const targetH = areaH - toolbarH
      const targetW = chartContainer.value.getBoundingClientRect().width
      if (targetH > 50 && targetW > 0) {
        chart.resize(targetW, targetH)
        return
      }
    }
    if (retries++ < 30) requestAnimationFrame(syncSize)
  }
  requestAnimationFrame(syncSize)

  // ResizeObserver 持续同步宽高
  chartResizeObserver = new ResizeObserver(() => {
    if (chart && chartContainer.value) {
      const rect = chartContainer.value.getBoundingClientRect()
      if (rect.width > 0 && rect.height > 0) {
        chart.resize(rect.width, rect.height)
      }
    }
  })
  chartResizeObserver.observe(chartContainer.value)

  // 初始化价格预警插件
  if (!userPriceAlerts && candleSeries) {
    userPriceAlerts = new UserPriceAlerts({
      color: '#2196F3',
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: true,
    })
    userPriceAlerts.attach(chart, candleSeries)
    // 加载已保存的价格线
    if (selectedStock.value) {
      userPriceAlerts.loadFromStorage(selectedStock.value)
      refreshPriceAlertsList()  // 刷新响应式列表
    }
  }

  // 十字光标移动 → 更新 hoverBar
  chart.subscribeClick((param: any) => {
    if (!param.point || !candleSeries || !chart) return

    // 工具激活模式：直接添加价格线
    if (priceLineToolActive.value) {
      // 优先使用十字光标位置的K线收盘价
      const bar = param.seriesData.get(candleSeries) as any
      let price: number | null = null

      if (bar && bar.close) {
        // 检查鼠标Y坐标是否接近收盘价
        const closeCoord = candleSeries.priceToCoordinate(bar.close)
        const yDiff = Math.abs(closeCoord - param.point.y)

        // 10像素内直接使用收盘价
        if (yDiff < 10) {
          price = parseFloat(bar.close.toFixed(2))
        }
      }

      // 如果没有命中收盘价，使用精确计算
      if (price === null) {
        price = getPriceFromYCoordinate(param.point.y)
      }

      if (price === null) return

      userPriceAlerts?.addAlert(price, {
        title: `目标: ${price.toFixed(2)}`,
      })
      refreshPriceAlertsList()  // 刷新响应式列表

      // 保存到本地存储
      if (selectedStock.value && userPriceAlerts) {
        userPriceAlerts.saveToStorage(selectedStock.value)
      }

      console.log(`[价格预警] 已添加价格线: ${price.toFixed(2)}`)

      // 添加后自动退出工具模式
      priceLineToolActive.value = false
      if (chartContainer.value) {
        chartContainer.value.style.cursor = 'default'
      }
      return
    }

    // 普通 Shift+点击 添加价格线
    if (param.shiftKey) {
      const bar = param.seriesData.get(candleSeries) as any
      let price: number | null = null

      if (bar && bar.close) {
        const closeCoord = candleSeries.priceToCoordinate(bar.close)
        const yDiff = Math.abs(closeCoord - param.point.y)

        if (yDiff < 10) {
          price = parseFloat(bar.close.toFixed(2))
        }
      }

      if (price === null) {
        price = getPriceFromYCoordinate(param.point.y)
      }

      if (price === null) return

      userPriceAlerts?.addAlert(price, {
        title: `目标: ${price.toFixed(2)}`,
      })
      refreshPriceAlertsList()  // 刷新响应式列表

      // 保存到本地存储
      if (selectedStock.value && userPriceAlerts) {
        userPriceAlerts.saveToStorage(selectedStock.value)
      }

      console.log(`[价格预警] 已添加价格线: ${price.toFixed(2)}`)
    }
  })

  chart.subscribeCrosshairMove((param: any) => {
    if (!param.time || !candleSeries) {
      hoverBar.value = null
      return
    }
    const bar = param.seriesData.get(candleSeries) as any
    const volBar = param.seriesData.get(volumeSeries) as any
    if (bar) {
      const ts = Number(param.time) * 1000
      // 修改版插件已处理时区，不加偏移
      const dt = new Date(ts)
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const timeStr = isDaily
        ? `${dt.getUTCFullYear()}-${String(dt.getUTCMonth()+1).padStart(2,'0')}-${String(dt.getUTCDate()).padStart(2,'0')}`
        : `${String(dt.getUTCMonth()+1).padStart(2,'0')}-${String(dt.getUTCDate()).padStart(2,'0')} ${String(dt.getUTCHours()).padStart(2,'0')}:${String(dt.getUTCMinutes()).padStart(2,'0')}`
      hoverBar.value = {
        time: timeStr,
        open: bar.open,
        high: bar.high,
        low: bar.low,
        close: bar.close,
        volume: volBar?.value ?? 0,
      }
    } else {
      hoverBar.value = null
    }
  })

  // 监听可见范围变化，实现滚动加载
  const checkAndLoadMore = () => {
    if (!candleSeries || isLoadingMore.value || !hasMoreHistory.value) return
    const currentData = klineData.value
    if (!currentData || currentData.length === 0) return

    const visibleRange = chart.timeScale().getVisibleLogicalRange()
    if (!visibleRange) return

    console.log('[滚动加载] 可见范围:', visibleRange.from, '-', visibleRange.to, '总数据:', currentData.length)

    // 检测是否滚动到数据边界（前 20 条）
    if (visibleRange.from < 20) {
      console.log('[滚动加载] 触发加载更多数据')
      loadMoreHistoryData()
    }
  }

  chart.timeScale().subscribeVisibleLogicalRangeChange(checkAndLoadMore)

  // 使用 requestAnimationFrame 实时更新标签位置
  let rafId: number | null = null
  let lastUpdateTime = 0
  const updateLabels = () => {
    const now = performance.now()
    if (now - lastUpdateTime > 16) {  // 限制 ~60fps
      if (priceAlertsList.value.length > 0) {
        priceAlertsKey.value++
      }
      lastUpdateTime = now
    }
    rafId = requestAnimationFrame(updateLabels)
  }
  rafId = requestAnimationFrame(updateLabels)

  // 组件卸载时清理
  onBeforeUnmount(() => {
    if (rafId !== null) {
      cancelAnimationFrame(rafId)
    }
  })
}

// ==================== 价格预警功能 ====================

/**
 * 显示价格线右键菜单
 */
const showPriceLineContextMenu = (e: MouseEvent) => {
  e.preventDefault()
  contextMenuPosition.value = { x: e.clientX, y: e.clientY }
  showContextMenu.value = true
}

/**
 * 关闭右键菜单
 */
const closeContextMenu = () => {
  showContextMenu.value = false
}

/**
 * 切换价格线工具模式
 */
const togglePriceLineTool = () => {
  priceLineToolActive.value = !priceLineToolActive.value

  // 更新鼠标样式
  if (chartContainer.value) {
    chartContainer.value.style.cursor = priceLineToolActive.value ? 'crosshair' : 'default'
  }
}

/**
 * 切换价格预警面板显示
 */
const togglePriceAlertPanel = () => {
  showPriceAlertPanel.value = !showPriceAlertPanel.value
}

/**
 * 添加价格预警（从右键菜单）
 */
const addPriceAlertFromMenu = () => {
  if (!userPriceAlerts || !priceAlertInput.value) return

  const price = Number(priceAlertInput.value)
  if (isNaN(price) || price <= 0) {
    alert('请输入有效的价格')
    return
  }

  userPriceAlerts.addAlert(price, {
    title: `目标: ${price.toFixed(2)}`,
  })

  // 保存到本地存储
  if (selectedStock.value) {
    userPriceAlerts.saveToStorage(selectedStock.value)
  }

  priceAlertInput.value = null
}

/**
 * 添加价格预警
 */
const addPriceAlert = () => {
  if (!userPriceAlerts || !priceAlertInput.value) return

  const price = Number(priceAlertInput.value)
  if (isNaN(price) || price <= 0) {
    alert('请输入有效的价格')
    return
  }

  userPriceAlerts.addAlert(price, {
    title: `目标: ${price.toFixed(2)}`,
  })

  // 保存到本地存储
  if (selectedStock.value) {
    userPriceAlerts.saveToStorage(selectedStock.value)
  }

  priceAlertInput.value = null
}

/**
 * 获取价格线标签的位置（相对于图表顶部）
 */
const getAlertLabelPosition = (price: number): number => {
  if (!chart || !candleSeries) return 0

  try {
    const coord = candleSeries.priceToCoordinate(price)
    if (coord === null || coord === undefined) return 0

    return Math.max(0, coord)
  } catch (e) {
    return 0
  }
}

/**
 * 从鼠标Y坐标计算价格（使用 priceToCoordinate 反向计算）
 * 支持K线价格吸附（优先级：收盘 > 开盘 > 最高/最低）
 */
const getPriceFromYCoordinate = (y: number): number | null => {
  if (!chart || !candleSeries) return null

  try {
    // 获取系列数据
    const data = candleSeries.data()
    if (!data || data.length === 0) return null

    // 获取时间轴的可见范围
    const timeScale = chart.timeScale()
    const visibleLogicalRange = timeScale.getVisibleLogicalRange()
    if (!visibleLogicalRange) return null

    // 获取可见范围内的数据
    const from = Math.max(0, Math.floor(visibleLogicalRange.from))
    const to = Math.min(data.length - 1, Math.ceil(visibleLogicalRange.to))

    if (from > to) return null

    // 吸附功能：找到最近的K线价格
    let bestPrice = null
    let minDiff = Infinity
    const SNAP_THRESHOLD = 20  // 20像素内吸附

    for (let i = from; i <= to; i++) {
      const bar = data[i] as any
      if (!bar) continue

      // 尝试吸附到这些价格点
      const pricePoints = [
        { price: bar.close, priority: 1 },    // 收盘价（最优先）
        { price: bar.open, priority: 2 },
        { price: bar.high, priority: 3 },
        { price: bar.low, priority: 3 }
      ]

      for (const point of pricePoints) {
        try {
          const coord = candleSeries.priceToCoordinate(point.price)
          if (coord !== null) {
            const diff = Math.abs(coord - y)

            // 在吸附范围内，优先吸附到收盘价
            if (diff < SNAP_THRESHOLD) {
              // 收盘价优先级更高，权重加倍
              const weightedDiff = diff / (point.priority === 1 ? 2 : 1)
              if (weightedDiff < minDiff) {
                minDiff = weightedDiff
                bestPrice = point.price
              }
            }
          }
        } catch (e) {
          continue
        }
      }
    }

    // 如果找到吸附的价格，直接返回
    if (bestPrice !== null && minDiff < SNAP_THRESHOLD) {
      return parseFloat(bestPrice.toFixed(2))
    }

    // 没有吸附到K线，使用精确计算
    // 二分查找方法
    let minPrice = Infinity
    let maxPrice = -Infinity

    for (let i = from; i <= to; i++) {
      const bar = data[i] as any
      if (bar) {
        minPrice = Math.min(minPrice, bar.low)
        maxPrice = Math.max(maxPrice, bar.high)
      }
    }

    if (minPrice === Infinity || maxPrice === -Infinity) return null

    // 扩展价格范围
    const priceRange = maxPrice - minPrice
    minPrice -= priceRange * 0.2
    maxPrice += priceRange * 0.2

    // 二分查找
    bestPrice = (minPrice + maxPrice) / 2
    minDiff = Infinity

    for (let i = 0; i < 50; i++) {
      const midPrice = (minPrice + maxPrice) / 2

      try {
        const coord = candleSeries.priceToCoordinate(midPrice)
        if (coord === null) break

        const diff = coord - y

        if (Math.abs(diff) < minDiff) {
          minDiff = Math.abs(diff)
          bestPrice = midPrice
        }

        if (Math.abs(diff) < 0.1) break

        if (diff > 0) {
          maxPrice = midPrice
        } else {
          minPrice = midPrice
        }
      } catch (e) {
        break
      }
    }

    return parseFloat(bestPrice.toFixed(2))
  } catch (e) {
    console.error('[getPriceFromYCoordinate] Error:', e)
    return null
  }
}

/**
 * 处理标签鼠标按下（检测是否真正拖动）
 */
const handleLabelMouseDown = (alertId: string, event: MouseEvent) => {
  // 如果正在编辑，不处理
  if (editingAlertId.value === alertId) {
    event.preventDefault()
    return
  }

  const startY = event.clientY
  const MOVE_THRESHOLD = 5
  let moved = false

  const onMouseMove = (e: MouseEvent) => {
    const dy = Math.abs(e.clientY - startY)
    if (dy > MOVE_THRESHOLD && !moved && !isDragging.value) {
      moved = true
      // 真正开始拖动
      const mockEvent = { ...event, clientY: e.clientY, preventDefault: () => {}, stopPropagation: () => {} }
      startDragAlert(alertId, mockEvent as MouseEvent)
    }

    // 如果已经开始拖动，继续处理移动
    if (isDragging.value && draggedAlertId.value) {
      const clientY = e.clientY
      const chartRect = chartContainer.value?.getBoundingClientRect()
      if (!chartRect) return

      const y = clientY - chartRect.top
      const price = getPriceFromYCoordinate(y)

      if (price) {
        userPriceAlerts?.updateAlertPrice(draggedAlertId.value, price)
        const alert = priceAlertsList.value.find(a => a.id === draggedAlertId.value)
        if (alert) {
          alert.price = price
        }
      }
    }
  }

  const onMouseUp = () => {
    window.removeEventListener('mousemove', onMouseMove)
    window.removeEventListener('mouseup', onMouseUp)

    // 如果正在拖动，结束拖动
    if (isDragging.value && draggedAlertId.value) {
      refreshPriceAlertsList()
      if (selectedStock.value && userPriceAlerts) {
        userPriceAlerts.saveToStorage(selectedStock.value)
      }
      isDragging.value = false
      draggedAlertId.value = null
    }
  }

  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

/**
 * 处理标签点击
 */
const handleLabelClick = (alertId: string) => {
  // 这个函数现在不再使用，改用原生 dblclick
}

/**
 * 开始拖动价格线标签
 */
const startDragAlert = (alertId: string, event: MouseEvent | TouchEvent) => {
  event.preventDefault()
  event.stopPropagation()

  isDragging.value = true
  draggedAlertId.value = alertId

  console.log(`[价格预警] 开始拖动价格线标签`)

  const onMove = (e: MouseEvent | TouchEvent) => {
    if (!isDragging.value || !draggedAlertId.value) return

    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY
    const chartRect = chartContainer.value?.getBoundingClientRect()
    if (!chartRect) return

    const y = clientY - chartRect.top
    const price = getPriceFromYCoordinate(y)

    // 实时更新价格线位置
    if (price) {
      userPriceAlerts?.updateAlertPrice(draggedAlertId.value, price)
      // 直接更新列表中对应项的价格，避免等待响应式更新
      const alert = priceAlertsList.value.find(a => a.id === draggedAlertId.value)
      if (alert) {
        alert.price = price
      }
    }
  }

  const onEnd = () => {
    if (isDragging.value && draggedAlertId.value) {
      // 拖动结束时刷新列表并保存
      refreshPriceAlertsList()
      if (selectedStock.value && userPriceAlerts) {
        userPriceAlerts.saveToStorage(selectedStock.value)
      }
      console.log(`[价格预警] 价格线已更新`)
    }

    isDragging.value = false
    draggedAlertId.value = null
    draggedAlertTempPrice.value = null

    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onEnd)
    window.removeEventListener('touchmove', onMove)
    window.removeEventListener('touchend', onEnd)
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onEnd)
  window.addEventListener('touchmove', onMove, { passive: false })
  window.addEventListener('touchend', onEnd)
}

/**
 * 删除价格预警（重构命名）
 */
const removePriceAlert = (id: string) => {
  if (!userPriceAlerts) return

  userPriceAlerts.removeAlert(id)
  refreshPriceAlertsList()  // 刷新响应式列表

  // 更新本地存储
  if (selectedStock.value) {
    userPriceAlerts.saveToStorage(selectedStock.value)
  }
}

/**
 * 双击开始编辑价格预警
 */
const startEditPriceAlert = (id: string, currentPrice: number) => {
  editingAlertId.value = id
  editingAlertPrice.value = currentPrice.toFixed(2)

  // 聚焦输入框
  nextTick(() => {
    if (editingInput.value) {
      editingInput.value.focus()
      editingInput.value.select()
    }
  })
}

/**
 * 完成编辑价格预警
 */
const finishEditPriceAlert = (id: string) => {
  if (!editingAlertId.value) return

  const newPrice = parseFloat(editingAlertPrice.value)
  if (isNaN(newPrice) || newPrice <= 0) {
    // 无效价格，恢复原值
    cancelEditPriceAlert()
    return
  }

  // 更新价格线
  userPriceAlerts?.updateAlertPrice(id, newPrice)
  refreshPriceAlertsList()

  // 保存到本地存储
  if (selectedStock.value && userPriceAlerts) {
    userPriceAlerts.saveToStorage(selectedStock.value)
  }

  console.log(`[价格预警] 已编辑价格线: ${newPrice.toFixed(2)}`)

  // 清理编辑状态
  editingAlertId.value = null
  editingAlertPrice.value = ''
}

/**
 * 取消编辑价格预警
 */
const cancelEditPriceAlert = () => {
  editingAlertId.value = null
  editingAlertPrice.value = ''
}

// 预置颜色列表
const presetColors = [
  '#2196F3',  // 蓝色
  '#4CAF50',  // 绿色
  '#FF9800',  // 橙色
  '#F44336',  // 红色
  '#9C27B0',  // 紫色
  '#FFEB3B',  // 黄色
  '#00BCD4',  // 青色
  '#FF5722',  // 深橙色
]

/**
 * 显示标签右键菜单
 */
const showLabelContextMenu = (alert: any, event: MouseEvent) => {
  event.preventDefault()
  event.stopPropagation()

  labelContextMenu.value = {
    show: true,
    alertId: alert.id,
    x: event.clientX,
    y: event.clientY,
    currentPrice: alert.price,
    currentTitle: alert.title || '',
    currentColor: alert.color || '#2196F3',
    enableAlert: alert.enableAlert || false,
  }
}

/**
 * 关闭标签右键菜单
 */
const closeLabelContextMenu = () => {
  labelContextMenu.value.show = false
}

/**
 * 应用标签设置
 */
const applyLabelSettings = () => {
  if (!userPriceAlerts || !labelContextMenu.value.alertId) return

  const { alertId, currentPrice, currentTitle, currentColor, enableAlert } = labelContextMenu.value

  // 如果价格改变了，先更新价格
  const alert = priceAlertsList.value.find(a => a.id === alertId)
  if (alert && currentPrice !== undefined && currentPrice !== alert.price) {
    userPriceAlerts.updateAlertPrice(alertId, currentPrice)
  }

  // 更新价格线样式（标题、颜色、提醒开关）
  userPriceAlerts.updateAlert(alertId, {
    title: currentTitle,
    color: currentColor,
    enableAlert: enableAlert,
  })

  // 清除此价格线的提醒记录（重新设置）
  if (!enableAlert) {
    triggeredAlerts.value.delete(alertId)
  }

  refreshPriceAlertsList()
  priceAlertsKey.value++  // 强制重新渲染整个标签容器

  // 保存到本地存储
  if (selectedStock.value) {
    userPriceAlerts.saveToStorage(selectedStock.value)
  }

  console.log(`[价格预警] 已更新标签设置: 价格=${currentPrice}, 标题=${currentTitle || '(无)'}, 颜色=${currentColor}, 提醒=${enableAlert}`)

  closeLabelContextMenu()
}

/**
 * 检查价格提醒（在行情更新时调用）
 */
const checkPriceAlerts = () => {
  if (!userPriceAlerts || !selectedStock.value) return

  const alerts = userPriceAlerts.getAlerts()
  const currentQuote = quotes.value[selectedStock.value]

  if (!currentQuote) return

  const currentPrice = currentQuote.close || currentQuote.price || 0
  if (!currentPrice) return

  // 检查每个启用了提醒的价格线
  alerts.forEach(alert => {
    if (!alert.enableAlert) return

    const { price, id, title } = alert
    const threshold = 0.01  // 0.01% 容差

    // 检查是否到达目标价格
    const triggered = (currentPrice >= price * (1 - threshold) && currentPrice <= price * (1 + threshold))

    if (triggered && !triggeredAlerts.value.has(id)) {
      // 第一次触发，记录并闪烁
      triggeredAlerts.value.add(id)
      triggerAlertFlash(id)
      console.log(`[价格预警] ${title || price.toFixed(2)} 到达目标价! 当前价格: ${currentPrice.toFixed(2)}`)
    } else if (!triggered) {
      // 价格远离目标价格，清除触发记录
      triggeredAlerts.value.delete(id)
    }
  })
}

/**
 * 触发价格提醒闪烁
 */
const triggerAlertFlash = (alertId: string) => {
  // 标记该标签需要闪烁
  flashingAlerts.value.add(alertId)
  priceAlertsKey.value++
  console.log(`[价格预警] 触发闪烁: ${alertId}`)

  // 3秒后停止闪烁（动画总时长 = 0.5s × 3次 = 1.5s，留余量3秒）
  setTimeout(() => {
    flashingAlerts.value.delete(alertId)
    priceAlertsKey.value++
  }, 3000)
}

/**
 * 获取所有价格预警（返回响应式列表）
 */
const getPriceAlerts = () => {
  return priceAlertsList.value
}

/**
 * 刷新价格预警列表（保持响应式）
 */
const refreshPriceAlertsList = () => {
  if (!userPriceAlerts) {
    priceAlertsList.value = []
    return
  }
  // 创建新数组触发 Vue 响应式更新
  priceAlertsList.value = [...userPriceAlerts.getAlerts()]
}

/**
 * 清除所有价格预警
 */
const clearAllPriceAlerts = () => {
  if (!userPriceAlerts) return

  userPriceAlerts.clearAll()
  refreshPriceAlertsList()  // 刷新响应式列表

  // 清除本地存储
  if (selectedStock.value) {
    localStorage.removeItem(`price_alerts_${selectedStock.value}`)
  }
}

// 加载K线数据（优化版：优先加载K线，其他数据延后）
const isInitialLoad = ref(true)  // 标记是否为初始加载

// 启动迷你折线图定时刷新
const startMiniChartsRefresh = () => {
  // 清除旧定时器
  if (miniChartsTimer) {
    clearInterval(miniChartsTimer)
    miniChartsTimer = null
  }

  // 每分钟刷新一次分时图
  miniChartsTimer = window.setInterval(() => {
    const now = new Date()
    const hour = now.getHours()
    const minute = now.getMinutes()

    // 只在交易时间内刷新（9:30 - 15:00）
    const isInTradingTime = (hour > 9 || (hour === 9 && minute >= 30)) && hour < 15

    if (isInTradingTime) {
      loadMiniCharts()
    }
  }, 60000)  // 60秒刷新一次
}

// 加载更多历史数据
const loadMoreHistoryData = async () => {
  if (isLoadingMore.value || !hasMoreHistory.value || !selectedStock.value) return

  isLoadingMore.value = true

  try {
    const oldLength = klineData.value.length
    console.log('[loadMoreHistoryData] 开始加载, 当前数据量:', oldLength)

    // 新请求的 count 增加 200 条
    const newCount = totalLoadedCount.value + 200
    const klineRes = await fetchKline(
      selectedStock.value,
      currentTimeframe.value,
      newCount,
      adjustType.value
    )

    if (klineRes.data && klineRes.data.length > 0) {
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const newDataWithSeconds = klineRes.data
        .map((item: KlineItem) => {
          let timeValue: number
          if (typeof item.time === 'string') {
            timeValue = Math.floor(new Date(item.time).getTime() / 1000)
          } else {
            const numTime = Number(item.time)
            timeValue = numTime > 100000000000 ? Math.floor(numTime / 1000) : numTime
          }
          return {
            time: timeValue + 8 * 3600,
            open: Number(item.open),
            high: Number(item.high),
            low: Number(item.low),
            close: Number(item.close),
            volume: Number(item.volume)
          }
        })
        .sort((a, b) => a.time - b.time)

      // 日线去重
      const deduped = isDaily
        ? Array.from(
            newDataWithSeconds.reduce((map, item) => {
              map.set(item.time, item)
              return map
            }, new Map<number, typeof newDataWithSeconds[0]>()).values()
          ).sort((a, b) => a.time - b.time)
        : newDataWithSeconds

      // 检查是否有更多历史数据
      if (deduped.length <= oldLength) {
        hasMoreHistory.value = false
        console.log('[loadMoreHistoryData] 数据量未增加，无更多历史数据')
      }

      // 更新数据
      totalLoadedCount.value = newCount
      klineData.value = deduped

      // 更新图表
      candleSeries.setData(deduped)
      volumeSeries.setData(deduped.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#ef535080' : '#26a69a80'
      })))

      console.log('[loadMoreHistoryData] 加载完成, 新数据量:', deduped.length)
    } else {
      hasMoreHistory.value = false
      console.log('[loadMoreHistoryData] API 返回空数据')
    }
  } catch (error) {
    console.error('加载更多历史数据失败:', error)
  } finally {
    isLoadingMore.value = false
  }
}

const loadKlineData = async () => {
  if (!selectedStock.value) return

  loading.value = true
  let lastBarsCount = 0  // 记录本次加载的 bar 数量，供 setVisibleLogicalRange 使用

  // 重置滚动加载状态
  totalLoadedCount.value = 200
  hasMoreHistory.value = true
  isLoadingMore.value = false

  try {
    // 第一步：优先只加载K线数据（最核心的）
    const klineRes = await fetchKline(selectedStock.value, currentTimeframe.value, 200, adjustType.value)

    // 处理K线数据
    if (klineRes.data && klineRes.data.length > 0) {
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const klineDataWithSeconds = klineRes.data
        .map((item: KlineItem) => {
          // 后端返回毫秒时间戳（UTC时间）
          // 需要加8小时偏移才能显示北京时间
          let timeValue: number
          if (typeof item.time === 'string') {
            timeValue = Math.floor(new Date(item.time).getTime() / 1000)
          } else {
            const numTime = Number(item.time)
            // 判断是毫秒还是秒：毫秒时间戳 > 1e11
            timeValue = numTime > 100000000000 ? Math.floor(numTime / 1000) : numTime
          }

          // 前端传北京时间戳（+8小时），插件不加偏移
          const beijingTime = timeValue + 8 * 3600
          return {
            time: beijingTime,
            open: Number(item.open),
            high: Number(item.high),
            low: Number(item.low),
            close: Number(item.close),
            volume: Number(item.volume)
          }
        })
        .filter((item): item is { time: number; open: number; high: number; low: number; close: number; volume: number } => item !== null)

      // 日线去重：同一天可能有本地(00:00 CST)和在线(15:00 CST)两条，保留后一条
      const deduped = isDaily
        ? Array.from(
            klineDataWithSeconds.reduce((map, item) => {
              map.set(item.time, item)  // 相同时间戳后面覆盖前面
              return map
            }, new Map<number, typeof klineDataWithSeconds[0]>()).values()
          ).sort((a, b) => a.time - b.time)
        : klineDataWithSeconds.sort((a, b) => (a.time as number) - (b.time as number))

      candleSeries?.setData(deduped)
      lastBarsCount = deduped.length

      // 保存数据供滚动加载使用
      klineData.value = deduped

      // 成交量数据与 deduped K线保持一致的时间戳
      const volumeData = deduped.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#ef535080' : '#26a69a80'
      }))
      volumeSeries?.setData(volumeData)

      // K线加载完成，立即结束loading（提升用户体验）
      loading.value = false

      // 设置图表显示范围
      if (isInitialLoad.value) {
        const total = lastBarsCount
        if (total > 0) {
          chart?.timeScale().setVisibleLogicalRange({
            from: Math.max(0, total - 200),
            to: total - 1 + 10,
          })
        }
        chart?.priceScale('right').applyOptions({ autoScale: true })
        setTimeout(() => {
          chart?.priceScale('right').applyOptions({ autoScale: false })
        }, 200)
        isInitialLoad.value = false
      }
    }

    // 第二步：后台加载其他数据（不阻塞K线显示）
    setTimeout(async () => {
      try {
        const currentStocks = dataStore.activeGroup?.stocks || []
        const allSymbols = currentStocks.map((s: any) => s.symbol)
        const indexSymbols = indices.value.map(i => i.code)

        // 并行加载快照、自选股、指数
        const [snapshotRes, batchRes, indexRes] = await Promise.all([
          fetchSnapshot(selectedStock.value),
          fetchSnapshotBatch(allSymbols),
          fetchSnapshotBatch(indexSymbols),
        ])

        // 更新当前股票快照（右侧详情面板）
        updateQuoteFromSnapshot(snapshotRes)

        // 批量更新所有自选股的价格
        if (batchRes.data && batchRes.data.length > 0) {
          const quoteMap = new Map(batchRes.data.map((q: any) => [q.symbol || q.code, q]))
          const currentStocks = dataStore.activeGroup?.stocks || []
          for (const stock of currentStocks) {
            const quote = quoteMap.get(stock.symbol)
            if (quote) {
              dataStore.updateQuote(quote)
            }
          }
        }

        // 更新指数
        if (indexRes.data && indexRes.data.length > 0) {
          const indexMap = new Map(indexRes.data.map((q: any) => [q.symbol || q.code, q]))
          for (const idx of indices.value) {
            const q = indexMap.get(idx.code)
            if (q) {
              idx.price = q.price ? Number(q.price).toFixed(2) : '--'
              idx.change = getChangePct(q)
            }
          }
        }

        // 第三步：后台预加载其他自选股K线
        preloadWatchlistKlines()
      } catch (error) {
        console.error('后台加载数据失败:', error)
      }
    }, 100)  // 延迟100ms，让K线先渲染

  } catch (error) {
    console.error('加载K线失败:', error)
    loading.value = false
  }
}

// ─────────────────────────────────────────────
// WebSocket 消息处理函数
// ─────────────────────────────────────────────

/** 将后端 bar 格式转换为 lightweight-charts 格式 */
const convertBarForChart = (bar: any): { time: number; open: number; high: number; low: number; close: number; volume: number } => {
  // 后端格式：{time: "2026-03-24 09:31:00", open, high, low, close, volume}
  // 需转换为：{time: Unix秒, open, high, low, close, volume}
  const timestamp = bar.time instanceof Date ? bar.time.getTime() : Date.parse(String(bar.time))
  return {
    time: Math.floor(timestamp / 1000),
    open: Number(bar.open),
    high: Number(bar.high),
    low: Number(bar.low),
    close: Number(bar.close),
    volume: Number(bar.volume)
  }
}

/** 处理 WebSocket 历史数据消息（已弃用：所有周期都用HTTP加载历史数据） */
const onWsHistory = (bars: KlineBar[]) => {
  // 不再使用WebSocket历史数据，所有周期都通过HTTP API加载历史数据
  console.log('[RealtimeQuotes] 收到WS历史数据（忽略）:', bars.length, '根')
  // 只用于初始化聚合器，不设置图表数据
  if (aggregator && bars.length > 0) {
    const convertedBars = bars.map(bar => {
      const timeField = (bar as any).datetime || bar.time
      const timestamp = new Date(timeField).getTime() / 1000
      return { time: timestamp, open: Number(bar.open), high: Number(bar.high), low: Number(bar.low), close: Number(bar.close), volume: Number(bar.volume) }
    }).filter(bar => !isNaN(bar.time))
    aggregator.setHistory(convertedBars)
  }
}

/** 处理 WebSocket bar_update 消息（更新最后一根 K线） */
const onWsBarUpdate = (bar: KlineBar) => {
  if (!candleSeries || !volumeSeries || !aggregator) return

  // 日线及以上周期：检查是否是当天数据
  const isDailyOrAbove = ['1d', '1w', '1M'].includes(currentTimeframe.value)

  // 转换后端数据格式
  const timeField = (bar as any).datetime || bar.time
  const timestamp = new Date(timeField).getTime() / 1000
  if (isNaN(timestamp)) return

  // 日线周期：只更新当天的最后一根K线，不处理历史数据
  if (isDailyOrAbove) {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000

    // 只处理当天的数据（用于更新最后一根K线的收盘价）
    if (timestamp >= today) {
      const chartBar = {
        time: today,
        open: Number(bar.open),
        high: Number(bar.high),
        low: Number(bar.low),
        close: Number(bar.close),
        volume: Number(bar.volume)
      }
      candleSeries.update(chartBar)
      volumeSeries.update({
        time: today,
        value: chartBar.volume,
        color: chartBar.close >= chartBar.open ? '#ef535080' : '#26a69a80'
      })
      console.log('[RealtimeQuotes] 日线更新:', chartBar)
    }
    return
  }

  // 分钟线周期：正常聚合
  const convertedBar: KlineBar = {
    time: timestamp,
    open: Number(bar.open),
    high: Number(bar.high),
    low: Number(bar.low),
    close: Number(bar.close),
    volume: Number(bar.volume)
  }

  const result = aggregator.aggregateBar(convertedBar, true)

  // 更新图表
  if (result.update) {
    const chartBar = result.update
    candleSeries.update(chartBar)
    volumeSeries.update({
      time: chartBar.time,
      value: chartBar.volume,
      color: chartBar.close >= chartBar.open ? '#ef535080' : '#26a69a80'
    })
    console.log('[RealtimeQuotes] K线更新:', chartBar)
  }
}

/** 处理 WebSocket bar_close 消息（上一根收线，新一根开始） */
const onWsBarClose = (bar: KlineBar) => {
  if (!candleSeries || !volumeSeries) return

  // 日线及以上周期：不处理收线消息（因为历史数据已通过HTTP加载）
  const isDailyOrAbove = ['1d', '1w', '1M'].includes(currentTimeframe.value)
  if (isDailyOrAbove) {
    return
  }

  // 分钟线周期：正常处理
  if (!aggregator) return

  // 转换后端数据格式
  const timeField = (bar as any).datetime || bar.time
  const timestamp = new Date(timeField).getTime() / 1000
  if (isNaN(timestamp)) return

  const convertedBar: KlineBar = {
    time: timestamp,
    open: Number(bar.open),
    high: Number(bar.high),
    low: Number(bar.low),
    close: Number(bar.close),
    volume: Number(bar.volume)
  }

  const result = aggregator.aggregateBar(convertedBar, true)

  // 如果有新bar收线，更新图表
  if (result.close) {
    const chartBar = result.close
    candleSeries.update(chartBar)
    volumeSeries.update({
      time: chartBar.time,
      value: chartBar.volume,
      color: chartBar.close >= chartBar.open ? '#ef535080' : '#26a69a80'
    })
    console.log('[RealtimeQuotes] 新K线收线:', chartBar)
  }

  // 更新当前正在形成的bar
  if (result.update) {
    const chartBar = result.update
    candleSeries.update(chartBar)
    volumeSeries.update({
      time: chartBar.time,
      value: chartBar.volume,
      color: chartBar.close >= chartBar.open ? '#ef535080' : '#26a69a80'
    })
    console.log('[RealtimeQuotes] 新K线开始:', chartBar)
  }
}

// ─────────────────────────────────────────────
// 从快照数据更新当前行情和五档盘口
// ─────────────────────────────────────────────
const updateQuoteFromSnapshot = (quote: any) => {
  console.log('[updateQuoteFromSnapshot] quote keys:', Object.keys(quote))
  console.log('[updateQuoteFromSnapshot] quote.name:', quote.name)

  const price = Number(quote.price) || 0
  const prevClose = Number(quote.pre_close ?? quote.prev_close ?? quote.last_close) || 0
  const changeAmt = Number(quote.change ?? (price - prevClose))

  // 更新股票名称（优先从快照数据，如果没有则从自选股列表查找）
  if (quote.name && quote.name !== '--') {
    currentStockName.value = quote.name
    console.log('[updateQuoteFromSnapshot] 更新股票名称（来自快照）:', quote.name)
  } else {
    // 从自选股列表中查找股票名称
    const stockInWatchlist = dataStore.activeGroup?.stocks?.find((s: any) =>
      s.symbol === selectedStock.value || s.code === selectedStock.value
    )
    if (stockInWatchlist?.name) {
      currentStockName.value = stockInWatchlist.name
      console.log('[updateQuoteFromSnapshot] 更新股票名称（来自自选股列表）:', stockInWatchlist.name)
    }
  }

  currentQuote.value = {
    price: price ? price.toFixed(2) : '--',
    change: parseFloat(changeAmt.toFixed(2)),
    change_percent: getChangePct(quote),
    open: quote.open ? Number(quote.open).toFixed(2) : '--',
    high: quote.high ? Number(quote.high).toFixed(2) : '--',
    low: quote.low ? Number(quote.low).toFixed(2) : '--',
    prev_close: prevClose ? prevClose.toFixed(2) : '--',
    volume: quote.volume || 0,
    amount: quote.amount || 0,
    // 新增扩展指标
    turnover_rate: quote.turnover_rate || quote.turnover || 0,
    volume_ratio: quote.volume_ratio || quote.LB || 0,
    amplitude: quote.amplitude || quote.ZAF || 0,
    pe_ratio: quote.pe_ratio || quote.dyna_pe || 0,
    pb_ratio: quote.pb_ratio || quote.pb_mrq || 0,
    dy_ratio: quote.dy_ratio || quote.dyr || 0,
    zt_price: quote.zt_price ? Number(quote.zt_price).toFixed(2) : '--',
    dt_price: quote.dt_price ? Number(quote.dt_price).toFixed(2) : '--',
    beta: quote.beta || quote.BetaValue || 0,
    total_shares: quote.total_shares || quote.J_zgb || 0,
    inner_vol: quote.inner_vol || 0,
    outer_vol: quote.outer_vol || 0,
    data_source: quote.data_source || 'unknown'
  }
  updateOrderBookFromSnapshot(quote)
}

// 从快照数据更新五档盘口
const updateOrderBookFromSnapshot = (quote: QuoteSnapshot) => {
  // 卖盘（价格从高到低：ask5 → ask1）
  // 注意：0 是有效值（无挂单），只有 null/undefined 才显示 '--'
  asks.value = [
    { price: quote.ask5 != null ? Number(quote.ask5).toFixed(2) : '--', size: quote.ask_vol5 ?? 0 },
    { price: quote.ask4 != null ? Number(quote.ask4).toFixed(2) : '--', size: quote.ask_vol4 ?? 0 },
    { price: quote.ask3 != null ? Number(quote.ask3).toFixed(2) : '--', size: quote.ask_vol3 ?? 0 },
    { price: quote.ask2 != null ? Number(quote.ask2).toFixed(2) : '--', size: quote.ask_vol2 ?? 0 },
    { price: quote.ask1 != null ? Number(quote.ask1).toFixed(2) : '--', size: quote.ask_vol1 ?? 0 }
  ]

  // 买盘（价格从低到高：bid1 → bid5）
  bids.value = [
    { price: quote.bid1 != null ? Number(quote.bid1).toFixed(2) : '--', size: quote.bid_vol1 ?? 0 },
    { price: quote.bid2 != null ? Number(quote.bid2).toFixed(2) : '--', size: quote.bid_vol2 ?? 0 },
    { price: quote.bid3 != null ? Number(quote.bid3).toFixed(2) : '--', size: quote.bid_vol3 ?? 0 },
    { price: quote.bid4 != null ? Number(quote.bid4).toFixed(2) : '--', size: quote.bid_vol4 ?? 0 },
    { price: quote.bid5 != null ? Number(quote.bid5).toFixed(2) : '--', size: quote.bid_vol5 ?? 0 }
  ]
}

/** 刷新快照数据：当前股票快照 + 自选股批量快照 + 指数（不含 K线） */
const refreshSnapshots = async () => {
  console.log('[refreshSnapshots] 开始执行')
  if (!selectedStock.value) {
    console.log('[refreshSnapshots] 没有选中股票，返回')
    return
  }

  try {
    const currentStocks = dataStore.activeGroup?.stocks || []
    const allSymbols = currentStocks.map((s: any) => s.symbol)
    console.log('[refreshSnapshots] 当前自选股:', allSymbols)
    const indexSymbols = indices.value.map(i => i.code)
    const [snapshotRes, batchRes, indexRes] = await Promise.all([
      fetchSnapshot(selectedStock.value),
      fetchSnapshotBatch(allSymbols),
      fetchSnapshotBatch(indexSymbols),
    ])

    console.log('[refreshSnapshots] batchRes:', batchRes)

    // 更新当前股票快照（API 直接返回 QuoteSnapshot，无需解包）
    updateQuoteFromSnapshot(snapshotRes)

    // 批量更新所有自选股的价格
    if (batchRes.data && batchRes.data.length > 0) {
      console.log('[refreshSnapshots] batchRes.data:', batchRes.data)
      const quoteMap = new Map(batchRes.data.map((q: any) => [q.symbol || q.code, q]))
      console.log('[refreshSnapshots] quoteMap keys:', Array.from(quoteMap.keys()))
      const currentStocks = dataStore.activeGroup?.stocks || []
      for (const stock of currentStocks) {
        const quote = quoteMap.get(stock.symbol)
        console.log(`[refreshSnapshots] ${stock.symbol}:`, quote ? '找到' : '未找到')
        if (quote) {
          dataStore.updateQuote(quote)
          console.log(`[refreshSnapshots] 已更新 ${stock.symbol}:`, quote)
        }
      }
    } else {
      console.log('[refreshSnapshots] batchRes.data 为空或不存在')
    }

    // 更新指数
    if (indexRes.data && indexRes.data.length > 0) {
      const indexMap = new Map(indexRes.data.map((q: any) => [q.symbol || q.code, q]))
      for (const idx of indices.value) {
        const q = indexMap.get(idx.code)
        if (q) {
          idx.price = q.price ? Number(q.price).toFixed(2) : '--'
          idx.change = getChangePct(q)
        }
      }
    }
  } catch (error) {
    console.error('刷新快照失败:', error)
  }

  // 检查价格提醒
  checkPriceAlerts()
}

// 计算最大订单数量（用于进度条基准）
const maxOrderSize = computed(() => {
  const allSizes = [...asks.value, ...bids.value].map(item => item.size)
  return Math.max(...allSizes, 1) // 至少为1，避免除以0
})

// 获取数量百分比（用于进度条宽度）
const getSizePercent = (size: number) => {
  if (!size || maxOrderSize.value === 0) return 0
  // 最小保留15%宽度，确保小数字也能看到进度条
  const percent = (size / maxOrderSize.value) * 100
  return Math.max(percent, 15)
}

// 格式化盘口数量（转为"手"）
const formatOrderSize = (size: number): string => {
  if (!size) return '0'
  // 后端返回的已经是手，无需再转换
  if (size >= 10000) {
    return (size / 10000).toFixed(1) + '万'
  }
  return Math.floor(size).toLocaleString()
}

// ─────────────────────────────────────────────
// WebSocket 连接管理
// ─────────────────────────────────────────────

/** 连接 K线 WebSocket（所有周期：HTTP加载历史，WS更新最后一根） */
const connectKlineWs = () => {
  if (!selectedStock.value) return

  // 如果已连接且股票没变，只更新聚合器周期
  if (klineWs && klineWs.isConnected() && selectedStock.value === (klineWs as any).symbol) {
    console.log('[RealtimeQuotes] WS 已连接，更新聚合器周期:', currentTimeframe.value)
    if (aggregator) {
      aggregator.setTimeframe(currentTimeframe.value as Timeframe)
    } else {
      aggregator = createKlineAggregator(currentTimeframe.value as Timeframe)
    }
    return
  }

  disconnectKlineWs()  // 先断开旧连接

  console.log('[RealtimeQuotes] 连接 WS:', selectedStock.value, '周期:', currentTimeframe.value)

  // 初始化聚合器
  aggregator = createKlineAggregator(currentTimeframe.value as Timeframe)

  klineWs = createKlineWebSocket(selectedStock.value, {
    onConnected: () => {
      wsConnected.value = true
      console.log('[RealtimeQuotes] WS 已连接')
    },
    onDisconnected: () => {
      wsConnected.value = false
      console.log('[RealtimeQuotes] WS 已断开')
    },
    onHistory: onWsHistory,  // 所有周期都不用WS历史数据，只用于初始化聚合器
    onBarUpdate: onWsBarUpdate,
    onBarClose: onWsBarClose,
    onError: (msg) => {
      console.error('[RealtimeQuotes] WS 错误:', msg)
    }
  })
  klineWs.connect()

  // 注意：loadKlineData 由调用方（如 selectStock）负责调用，避免重复请求
}

/** 断开 K线 WebSocket */
const disconnectKlineWs = () => {
  if (klineWs) {
    console.log('[RealtimeQuotes] 断开 WS')
    klineWs.disconnect()
    klineWs = null
    wsConnected.value = false
  }
  // 清空聚合器
  aggregator?.clear()
  aggregator = null
}

// ─────────────────────────────────────────────
// 选择股票
const selectStock = (code: string) => {
  if (!code || code === 'undefined') {
    console.warn('[selectStock] 无效的股票代码:', code)
    return
  }

  selectedStock.value = code

  // 保存到 localStorage（只保存有效值）
  try {
    localStorage.setItem('realtime_quotes_last_stock', code)
  } catch (e) {
    console.error('[selectStock] 保存失败:', e)
  }

  // 切换价格预警：清除旧的，加载新的
  if (userPriceAlerts) {
    userPriceAlerts.clearAll()
    userPriceAlerts.loadFromStorage(code)
  }

  isInitialLoad.value = true  // 切换股票时重新适应显示范围

  // 取消之前的预加载任务
  if (preloadAbortController) {
    preloadAbortController.abort()
    preloadAbortController = null
  }

  // 切换 WebSocket 连接到新股票
  connectKlineWs()

  // 立即加载新股票的历史数据（HTTP兜底，确保数据即时显示正确的周期）
  loadKlineData()
}

// 切换周期（先加载数据，避免图表闪空白）
const changeTimeframe = async (tf: string) => {
  if (currentTimeframe.value === tf) return  // 周期没变，不处理

  if (!tf || tf === 'undefined') {
    console.warn('[changeTimeframe] 无效的周期:', tf)
    return
  }

  console.log('[RealtimeQuotes] 切换周期:', currentTimeframe.value, '->', tf)
  currentTimeframe.value = tf

  // 保存到 localStorage（只保存有效值）
  try {
    localStorage.setItem('realtime_quotes_last_timeframe', tf)
  } catch (e) {
    console.error('[changeTimeframe] 保存失败:', e)
  }

  isInitialLoad.value = true

  // 先加载数据（利用TTL缓存，瞬间完成）
  console.log('[RealtimeQuotes] 切换周期，加载历史数据:', tf)
  await loadKlineData()

  // 数据加载完成后再切换聚合器（避免图表闪空白）
  if (aggregator) {
    aggregator.clear()
  }
  aggregator = createKlineAggregator(tf as Timeframe)
  console.log('[RealtimeQuotes] 聚合器已切换:', tf)

  // WebSocket 保持连接（始终推1分钟线），无需重连
  // 聚合器会自动将1分钟线聚合到目标周期
}

// 切换复权类型
const changeAdjustType = (type: string) => {
  adjustType.value = type
  isInitialLoad.value = true
  loadKlineData()
}

// 市场状态缓存
const marketStatusCache = ref<MarketStatus | null>(null)

// 实时更新（根据市场状态动态调整刷新间隔）
const startRealtimeUpdate = async () => {
  const getStatus = async (): Promise<MarketStatus | null> => {
    try { return await fetchMarketStatus() } catch { return null }
  }

  const updateStatus = async () => {
    marketStatusCache.value = await getStatus()
  }

  // 初始获取状态
  await updateStatus()

  // 每30秒更新一次市场状态
  statusTimer = window.setInterval(updateStatus, 30000)

  // 主刷新循环
  updateTimer = window.setInterval(async () => {
    if (!selectedStock.value) return

    const status = marketStatusCache.value
    const isOpen = status?.is_open ?? false

    // 收盘后不刷新
    if (!isOpen) {
      return
    }

    // 始终刷新快照（包含自选股列表的价格）
    refreshSnapshots()

    // 交易中：根据连接状态决定是否加载K线
    if (!wsConnected.value) {
      // WebSocket 未连接：用 HTTP 加载当前股票K线
      loadKlineData()
    }
    // WebSocket 已连接：K线由 WS 推送，不需要 HTTP 加载
  }, 5000)  // 固定5秒检查一次，实际是否刷新由市场状态决定
}

onMounted(() => {
  nextTick(() => {
    // 先设置选中的股票，再初始化其他功能
    if (!selectedStock.value) {
      const firstStock = dataStore.activeGroup?.stocks?.[0]
      if (firstStock) {
        selectedStock.value = firstStock.symbol || firstStock.code
        console.log('[onMounted] 使用列表第一只股票:', selectedStock.value)
      } else {
        // 如果列表也是空的，使用默认值
        selectedStock.value = '600000.SH'
        console.log('[onMounted] 使用默认股票:', selectedStock.value)
      }
    }

    // 确保 selectedStock 已设置后再初始化
    console.log('[onMounted] 当前选中股票:', selectedStock.value)

    initChart()
    loadMiniCharts()
    startMiniChartsRefresh()  // 启动分时图定时刷新
    refreshSnapshots()  // 立即加载一次快照数据
    startRealtimeUpdate()
    // 连接 WebSocket 并加载历史数据（所有周期：HTTP加载历史，WS实时更新）
    connectKlineWs()
  })
})

onBeforeUnmount(() => {
  if (updateTimer) clearInterval(updateTimer)
  if (statusTimer) clearInterval(statusTimer)
  if (miniChartsTimer) clearInterval(miniChartsTimer)  // 清理分时图定时器
  disconnectKlineWs()  // 断开 WebSocket
  chartResizeObserver?.disconnect()
  if (chart) chart.remove()
})
</script>

<style scoped>
/* 使用全局配色 - TradingView 风格 */
.realtime-quotes-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #131722;
  color: #d1d4dc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 主容器 */
.main-container {
  display: grid;
  grid-template-rows: 1fr 28px;
  flex: 1;
  min-height: 0;
}

.content-area {
  display: grid;
  grid-template-columns: 260px 1fr 280px;
  gap: 1px;
  background: #2a2e39;
  overflow: hidden;
  min-height: 0;
}

/* 面板 */
.panel {
  background: #131722;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  background: #1e222d;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #d1d4dc;
  border-bottom: 1px solid #2a2e39;
}

.stock-info-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-name-large {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
}

.stock-code-small {
  font-size: 11px;
  font-weight: 400;
  color: #787b86;
  font-family: 'Courier New', monospace;
}

.panel-actions {
  display: flex;
  gap: 4px;
}

.panel-btn {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  color: #787b86;
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.panel-btn:hover {
  background: #2a2e39;
  color: #d1d4dc;
}

/* 搜索区域 */
.search-section {
  padding: 10px;
  display: flex;
  gap: 6px;
  border-bottom: 1px solid #2a2e39;
}

.search-input {
  flex: 1;
  padding: 6px 10px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 12px;
}

.search-input:focus {
  outline: none;
  border-color: #ef5350;  /* 红色边框 */
}

.add-btn {
  padding: 6px 12px;
  background: #ef5350;  /* 红色按钮 */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.add-btn:hover {
  background: #e53935;  /* 深红色 */
}

/* 股票列表 */
.stock-list {
  flex: 1;
  overflow-y: auto;
}

.stock-item {
  display: grid;
  grid-template-columns: 1fr 80px 52px;
  gap: 6px;
  padding: 8px 14px;
  border-bottom: 1px solid #2a2e39;
  cursor: pointer;
  transition: background 0.15s;
  align-items: center;
}

.mini-chart {
  width: 80px;
  height: 28px;
  opacity: 0.9;
}

.stock-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.stock-row1, .stock-row2, .mini-chart-placeholder { display: none; }

.stock-item:hover {
  background: #1e222d;
}

.stock-item.selected {
  background: #2a2e39;
  border-left: 2px solid #ef5350;  /* 红色左边框 */
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-code {
  color: #d1d4dc;
  font-size: 13px;
  font-weight: 600;
}

.stock-name {
  color: #787b86;
  font-size: 11px;
}

.stock-price {
  text-align: right;
  font-weight: 600;
  font-size: 13px;
}

/* 中国股市：红涨绿跌 */
.stock-price.positive { color: #ef5350; }  /* 上涨红色 */
.stock-price.negative { color: #26a69a; }  /* 下跌绿色 */

.stock-change {
  text-align: right;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.stock-change.positive {
  background: rgba(239, 83, 80, 0.15);
  color: #ef5350;
}

.stock-change.negative {
  background: rgba(38, 166, 154, 0.15);
  color: #26a69a;
}

/* 图表区域 */
.chart-area {
  display: flex;
  flex-direction: column;
  background: #131722;
  flex: 1;
  min-height: 0;
}

.chart-toolbar {
  background: #1e222d;
  border-bottom: 1px solid #2a2e39;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.current-stock-name {
  color: #d1d4dc;
  font-weight: 600;
  font-size: 14px;
}

.chart-legend-overlay {
  position: absolute;
  top: 8px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #d1d4dc;
  pointer-events: none;
  z-index: 10;
  background: rgba(19, 23, 34, 0.75);
  padding: 4px 12px;
  border-radius: 4px;
}
.chart-legend-overlay .legend-time { color: #9ca3af; margin-right: 4px; }
.chart-legend-overlay .legend-item { display: flex; align-items: center; gap: 4px; }
.chart-legend-overlay .legend-item em { font-style: normal; font-weight: 600; font-size: 13px; color: #e6edf3; }

.toolbar-right {
  display: flex;
  gap: 4px;
}

.toolbar-divider-v {
  width: 1px;
  height: 20px;
  background: #363a45;
  margin: 0 6px;
  align-self: center;
}

.timeframe-btn {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #363a45;
  color: #d1d4dc;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
  transition: all 0.2s;
}

.timeframe-btn:hover {
  background: #2a2e39;
}

.timeframe-btn.active {
  background: #ef5350;  /* 激活状态红色 */
  border-color: #ef5350;
  color: white;
}

.chart-container {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  position: relative;
}

.kline-chart {
  flex: 1;
  min-height: 0;
}

.volume-chart {
  display: none;
}

.chart-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #d1d4dc;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #363a45;
  border-top-color: #ef5350;  /* 红色 spinner */
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 信息面板 */
.info-panel {
  display: flex;
  flex-direction: column;
}

.trade-section {
  padding: 16px;
  border-bottom: 1px solid #2a2e39;
}

.section-title {
  font-size: 11px;
  color: #787b86;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.price-display {
  text-align: center;
}

.current-price {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.current-price.positive { color: #ef5350; }  /* 上涨红色 */
.current-price.negative { color: #26a69a; }  /* 下跌绿色 */

.price-change {
  font-size: 14px;
  margin-top: 6px;
  font-weight: 600;
}

.price-change.positive { color: #ef5350; }  /* 上涨红色 */
.price-change.negative { color: #26a69a; }  /* 下跌绿色 */

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.info-item {
  background: #1e222d;
  padding: 8px 10px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.info-label {
  font-size: 10px;
  color: #787b86;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
}
.info-value.positive { color: #ef5350; }
.info-value.negative { color: #26a69a; }

.data-source-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.data-source-label {
  color: #787b86;
  font-size: 10px;
  text-transform: uppercase;
}

.data-source-value {
  color: #4caf50;
  font-weight: 600;
  font-size: 12px;
}

.update-time {
  color: #787b86;
  font-size: 11px;
}

/* 五档盘口 */
.order-book {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.order-column {
  background: #1e222d;
  border-radius: 4px;
  overflow: hidden;
}

.order-row {
  display: grid;
  grid-template-columns: 1fr 1fr 45px;
  gap: 4px;
  padding: 6px 8px;
  font-size: 11px;
  border-bottom: 1px solid #2a2e39;
  min-height: 24px;
  align-items: center;
  white-space: nowrap;
}

.order-row:last-child {
  border-bottom: none;
}

.order-row.buy { color: #ef5350; }  /* 买盘红色（主动买入） */
.order-row.sell { color: #26a69a; }  /* 卖盘绿色（主动卖出） */

.order-price {
  text-align: right;
  font-weight: 600;
}

.order-size {
  text-align: right;
  position: relative;
  z-index: 1;
}

/* 盘口数量进度条 */
.size-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 0;
  transition: width 0.3s ease;
}

/* 买盘红色背景条 */
.order-row.buy .size-bar {
  background: rgba(239, 83, 80, 0.45);
}

/* 卖盘绿色背景条 */
.order-row.sell .size-bar {
  background: rgba(38, 166, 154, 0.45);
}

/* 底部状态栏 */
.statusbar {
  background: #1e222d;
  border-top: 1px solid #2a2e39;
  padding: 0 16px;
  display: flex;
  align-items: center;
  font-size: 11px;
  color: #787b86;
}

.statusbar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 6px 0;
  width: 100%;
}

.statusbar-divider {
  width: 1px;
  height: 14px;
  background: #2a2e39;
}

.stock-name-display {
  color: #d1d4dc;
  font-weight: 600;
}

.index-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.index-name { color: #6e7681; }
.index-price { color: #d1d4dc; font-weight: 600; }
.index-change { font-size: 10px; }
.index-price.positive, .index-change.positive { color: #ef5350; }
.index-price.negative, .index-change.negative { color: #26a69a; }

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #131722;
}

::-webkit-scrollbar-thumb {
  background: #363a45;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #434651;
}

/* ==================== 价格预警面板 ==================== */
.price-alert-panel {
  position: absolute;
  top: 52px;
  right: 14px;
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 100;
  min-width: 240px;
}

/* ==================== 价格线右键菜单 ==================== */
.price-line-context-menu {
  position: fixed;
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  z-index: 1000;
  min-width: 260px;
  max-width: 320px;
}

.context-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.context-menu-header {
  padding: 10px 14px;
  border-bottom: 1px solid #2a2e39;
  font-size: 13px;
  font-weight: 600;
  color: #d1d4dc;
}

.context-menu-content {
  padding: 12px;
}

.price-alert-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid #2a2e39;
  font-size: 13px;
  font-weight: 600;
  color: #d1d4dc;
}

.price-alert-close {
  background: transparent;
  border: none;
  color: #787b86;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.price-alert-close:hover {
  background: #2a2e39;
  color: #d1d4dc;
}

.price-alert-content {
  padding: 12px;
}

.price-alert-input-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.price-alert-input {
  flex: 1;
  background: #131722;
  border: 1px solid #363a45;
  border-radius: 4px;
  padding: 8px 10px;
  color: #d1d4dc;
  font-size: 13px;
  outline: none;
}

.price-alert-input:focus {
  border-color: #2196F3;
}

.price-alert-input::placeholder {
  color: #787b86;
}

.price-alert-add-btn {
  background: #2196F3;
  border: none;
  border-radius: 4px;
  padding: 8px 14px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.price-alert-add-btn:hover {
  background: #1976D2;
}

.price-alert-list {
  max-height: 180px;
  overflow-y: auto;
  margin-bottom: 8px;
}

.price-alert-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  background: #131722;
  border-radius: 4px;
  margin-bottom: 6px;
}

.price-alert-price {
  color: #d1d4dc;
  font-size: 13px;
  font-weight: 600;
}

.price-alert-remove-btn {
  background: transparent;
  border: none;
  color: #787b86;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.price-alert-remove-btn:hover {
  background: #2a2e39;
  color: #ef5350;
}

.price-alert-empty {
  text-align: center;
  padding: 20px 10px;
  color: #787b86;
  font-size: 12px;
}

.price-alert-clear-btn {
  width: 100%;
  background: transparent;
  border: 1px solid #363a45;
  border-radius: 4px;
  padding: 8px;
  color: #787b86;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.price-alert-clear-btn:hover {
  background: #2a2e39;
  border-color: #ef5350;
  color: #ef5350;
}

/* ==================== 价格标签交互层 ==================== */
.price-labels-left {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;  /* 容器不拦截事件 */
  z-index: 50;
}

.price-label-left {
  position: absolute;
  right: 65px;
  transform: translateY(-50%);
  border: none;
  color: #d1d4dc;
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 11px;
  font-weight: 400;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  pointer-events: auto;
  cursor: ns-resize;
  user-select: none;
  white-space: nowrap;
}

.price-label-left:hover {
  opacity: 0.9;
}

.price-label-left.dragging {
  background: #FF9800 !important;
}

/* 价格提醒闪烁动画 */
.price-label-left.alert-flash {
  animation: flash 0.5s ease-in-out 3;
}

@keyframes flash {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; box-shadow: 0 0 10px 2px rgba(255, 152, 0, 0.8); }
}

.price-label-left .label-text {
  display: block;
}

.price-label-left.editing {
  background: #1976D2;  /* 编辑时深蓝色 */
  padding: 0;
}

.price-label-input {
  width: 70px;
  height: 20px;
  background: #ffffff;
  border: none;
  border-radius: 2px;
  color: #131722;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  outline: none;
}

/* ==================== 标签右键菜单 ==================== */
.label-context-menu {
  position: fixed;
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  z-index: 1001;
  min-width: 240px;
}

.label-menu-header {
  padding: 10px 14px;
  border-bottom: 1px solid #2a2e39;
  font-size: 13px;
  font-weight: 600;
  color: #d1d4dc;
}

.label-menu-content {
  padding: 12px;
}

.label-menu-row {
  margin-bottom: 12px;
}

.label-menu-row label {
  display: block;
  font-size: 11px;
  color: #787b86;
  margin-bottom: 6px;
}

.label-menu-input {
  width: 100%;
  background: #131722;
  border: 1px solid #363a45;
  border-radius: 4px;
  padding: 6px 10px;
  color: #d1d4dc;
  font-size: 12px;
  outline: none;
}

.label-menu-input:focus {
  border-color: #2196F3;
}

.color-picker {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.color-option {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.15s;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.active {
  border-color: #ffffff;
  box-shadow: 0 0 0 2px #2196F3;
}

.label-menu-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.label-menu-btn {
  flex: 1;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.label-menu-btn.cancel {
  background: #2a2e39;
  color: #d1d4dc;
}

.label-menu-btn.cancel:hover {
  background: #363a45;
}

.label-menu-btn.confirm {
  background: #2196F3;
  color: white;
}

.label-menu-btn.confirm:hover {
  background: #1976D2;
}

</style>
