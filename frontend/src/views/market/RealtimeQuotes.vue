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
              <div class="toolbar-divider-v"></div>
              <!-- 指标选择器 -->
              <IndicatorSelector
                v-model:active="activeIndicators"
                v-model:overlay="overlayIndicators"
                @settings="openIndicatorSettings"
              />
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
            <div v-if="showContextMenu" class="context-menu-overlay" @click="closeContextMenu"></div>
          </teleport>

          <!-- 价格预警面板 -->
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
                  <div class="label-menu-row">
                    <label>目标价格：</label>
                    <input
                      v-model.number="labelContextMenu.currentPrice"
                      type="number"
                      step="0.01"
                      class="label-menu-input"
                    />
                  </div>
                  <div class="label-menu-row">
                    <label>标签名称：</label>
                    <input
                      v-model="labelContextMenu.currentTitle"
                      type="text"
                      class="label-menu-input"
                      placeholder="留空显示价格"
                    />
                  </div>
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
            <span>{{ isZh ? '行情详情' : 'Quote' }}</span>
            <div class="stock-info-header">
              <span class="stock-name-header">{{ currentStockNameForPanel }}</span>
              <span class="stock-code-header">{{ selectedStock }}</span>
            </div>
          </div>

          <div class="trade-section">
            <div class="price-display">
              <div :class="['current-price', realtimeQuote.quote.value.change >= 0 ? 'positive' : 'negative']">
                {{ realtimeQuote.quote.value.price || '--' }}
              </div>
              <div :class="['price-change', realtimeQuote.quote.value.change >= 0 ? 'positive' : 'negative']">
                {{ realtimeQuote.quote.value.change >= 0 ? '+' : '' }}{{ realtimeQuote.quote.value.change }}
                ({{ realtimeQuote.quote.value.change_percent >= 0 ? '+' : '' }}{{ realtimeQuote.quote.value.change_percent }}%)
              </div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">{{ isZh ? '五档盘口' : 'Order Book' }}</div>
            <div class="order-book">
              <div class="order-column">
                <div v-for="(ask, i) in realtimeQuote.asks.value.slice().reverse()" :key="'ask'+i" class="order-row sell">
                  <span>{{ isZh ? '卖' : 'Sell' }} {{ i + 1 }}</span>
                  <span class="order-price">{{ ask.price }}</span>
                  <span class="order-size">
                    <span class="size-bar" :style="{ width: getSizePercent(ask.size) + '%' }"></span>
                    {{ formatOrderSize(ask.size) }}
                  </span>
                </div>
              </div>
              <div class="order-column">
                <div v-for="(bid, i) in realtimeQuote.bids.value" :key="'bid'+i" class="order-row buy">
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
                <div class="info-value">{{ realtimeQuote.quote.value.open || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '最高' : 'High' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.high || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '最低' : 'Low' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.low || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '昨收' : 'Prev' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.prev_close || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '成交量' : 'Volume' }}</div>
                <div class="info-value">{{ formatVolume(realtimeQuote.quote.value.volume) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '成交额' : 'Amount' }}</div>
                <div class="info-value">{{ formatAmount(realtimeQuote.quote.value.amount) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '换手率' : 'Turnover' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.turnover_rate ? realtimeQuote.quote.value.turnover_rate + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '总量' : 'Volume' }}</div>
                <div class="info-value">{{ formatVolume(realtimeQuote.quote.value.volume) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '振幅' : 'Amplitude' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.amplitude ? realtimeQuote.quote.value.amplitude + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '量比' : 'Vol Ratio' }}</div>
                <div class="info-value" :class="realtimeQuote.quote.value.volume_ratio > 1 ? 'positive' : realtimeQuote.quote.value.volume_ratio < 1 ? 'negative' : ''">{{ realtimeQuote.quote.value.volume_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '外盘' : 'Outer' }}</div>
                <div class="info-value positive">{{ formatVol(realtimeQuote.quote.value.outer_vol) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '内盘' : 'Inner' }}</div>
                <div class="info-value negative">{{ formatVol(realtimeQuote.quote.value.inner_vol) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '市盈率' : 'P/E' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.pe_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '市净率' : 'P/B' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.pb_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '股息率' : 'Div Yield' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.dy_ratio ? realtimeQuote.quote.value.dy_ratio + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '涨停价' : 'Limit Up' }}</div>
                <div class="info-value positive">{{ realtimeQuote.quote.value.zt_price || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '跌停价' : 'Limit Down' }}</div>
                <div class="info-value negative">{{ realtimeQuote.quote.value.dt_price || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '贝塔系数' : 'Beta' }}</div>
                <div class="info-value">{{ realtimeQuote.quote.value.beta || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '总股本' : 'Shares' }}</div>
                <div class="info-value">{{ formatShares(realtimeQuote.quote.value.total_shares) }}</div>
              </div>
              <div class="info-item" style="grid-column: 1 / -1;">
                <div class="data-source-info">
                  <span class="data-source-label">{{ isZh ? '数据源' : 'Source' }}</span>
                  <span class="data-source-value">{{ realtimeQuote.quote.value.data_source }}</span>
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
          <span>{{ isZh ? '成交' : 'Vol' }}: {{ formatAmount(realtimeQuote.quote.value.amount) }}</span>
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
          <span style="margin-left: auto; color: #4a4f60;">{{ statusbarText }}</span>
        </div>
      </div>
    </div>

    <!-- 指标参数设置弹窗 -->
    <IndicatorSettings
      v-model:visible="showIndicatorSettings"
      :indicator-id="settingsIndicatorId"
      :current-params="settingsParams"
      @confirm="handleSettingsConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue'
import { createChart, CrosshairMode, CandlestickSeries, HistogramSeries, LineSeries, AreaSeries } from 'lightweight-charts'
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
import { initScheduler, getScheduler, type RefreshScheduler } from '@/utils/refreshScheduler'
import { useKlineData } from '@/composables/useKlineData'
import { useKlineBatch } from '@/composables/useKlineBatch'
import { useMiniCharts, generateSparklinePoints } from '@/composables/useMiniCharts'
import { useRealtimeQuote, type QuoteData } from '@/composables/useRealtimeQuote'
import { UserPriceAlerts } from '@/components/charts/plugins'
import IndicatorSelector from '@/components/charts/IndicatorSelector.vue'
import IndicatorSettings from '@/components/charts/IndicatorSettings.vue'
	import { getIndicatorSettings, saveIndicatorSettings as saveIndicatorSettingsApi } from '@/api/modules/settings'

// 类型定义
type ChartApi = any
type SeriesApi = any

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

// 状态
const selectedStock = ref('')  // 初始为空，在 onMounted 中从分组获取
const currentTimeframe = ref('1d')
const appStore = useAppStore()
const dataStore = useDataStore()
const isZh = computed(() => appStore.language === 'zh')

// ========== useKlineData: K线数据管理（新增，与现有逻辑并存）==========
const {
  bars: klineBars,
  loading: klineLoading,
  isConnected: klineWsConnected,
  loadHistory: loadKlineHistory,
  switchSymbol: switchKlineSymbol,
  switchTimeframe: switchKlineTimeframe,
  connect: connectKlineWsNew,
  disconnect: disconnectKlineWsNew
} = useKlineData(selectedStock, currentTimeframe, {
  initialCount: 800,
  adjustType: 'none',
  enableWebSocket: true,
  autoLoad: false
})

// ========== Composables: 统一数据管理 ==========
// 实时行情数据（五档盘口 + 统计数据）
const realtimeQuote = useRealtimeQuote(selectedStock)

// 批量预加载（用于缓存其他股票的其他周期）
const klineBatch = useKlineBatch()

// 迷你图数据（自选股列表的分时图）
const miniCharts = useMiniCharts()

// 转换 Map 为 Record 格式（兼容 WatchlistPanel）
const miniChartsData = computed(() => {
  const result: Record<string, Array<{time: Date, close: number}>> = {}
  for (const [symbol, data] of miniCharts.data.value.entries()) {
    result[symbol] = data
  }
  return result
})

// 智能刷新调度器
let scheduler: RefreshScheduler | null = null

const loading = ref(false)
const adjustType = ref('qfq')

// 沪深指数
const indices = ref([
  { code: '000001.SH', name: '上证', price: '--', change: 0 },
  { code: '399001.SZ', name: '深证', price: '--', change: 0 },
  { code: '399006.SZ', name: '创业板', price: '--', change: 0 },
])

// 自选股列表现在使用 DataStore (dataStore.watchlist)

// 图表实例
const chartContainer = ref<HTMLElement>()
let chart: ChartApi | null = null
let candleSeries: SeriesApi | null = null
let volumeSeries: SeriesApi | null = null
let statusTimer: number | null = null
let chartResizeObserver: ResizeObserver | null = null

// ========== 技术指标相关 ==========
// 指标窗口显示状态
const showIndicatorPanel = ref(false)
// ========== 指标状态存储 ==========
const INDICATOR_STORAGE_KEY = 'myquant_indicator_settings'

// 从localStorage加载保存的指标设置
function loadSavedIndicators(): {
  activeIndicators: string[]
  overlayIndicators: string[]
  indicatorParams: Record<string, any>
  paneHeights: Record<string, number>
} {
  try {
    const saved = localStorage.getItem(INDICATOR_STORAGE_KEY)
    console.log('[指标] 读取localStorage:', saved)
    if (saved) {
      const parsed = JSON.parse(saved)
      console.log('[指标] 解析结果:', parsed)
      return {
        activeIndicators: parsed.activeIndicators || ['MACD'],
        overlayIndicators: parsed.overlayIndicators || [],
        indicatorParams: parsed.indicatorParams || {},
        paneHeights: parsed.paneHeights || {}
      }
    }
  } catch (e) {
    console.warn('[指标] 加载存储设置失败:', e)
  }
  console.log('[指标] 使用默认设置')
  return { activeIndicators: ['MACD'], overlayIndicators: [], indicatorParams: {}, paneHeights: {} }
}

const savedSettings = loadSavedIndicators()

const activeIndicators = ref<string[]>(savedSettings.activeIndicators)  // 独立指标
const overlayIndicators = ref<string[]>(savedSettings.overlayIndicators)  // 主图叠加指标(MA/BOLL)
const indicatorParams = ref<Record<string, any>>(savedSettings.indicatorParams)  // 指标参数缓存
const indicatorPaneHeights = ref<Record<string, number>>(savedSettings.paneHeights)  // 指标pane高度缓存

// 保存指标设置到localStorage
function saveIndicatorSettings() {
  const settings = {
    activeIndicators: activeIndicators.value,
    overlayIndicators: overlayIndicators.value,
    indicatorParams: indicatorParams.value,
    paneHeights: indicatorPaneHeights.value
  }
  localStorage.setItem(INDICATOR_STORAGE_KEY, JSON.stringify(settings))
  console.log('[指标] 保存设置:', settings)
}

// 监听指标变化，自动保存
watch([activeIndicators, overlayIndicators, indicatorParams, indicatorPaneHeights], () => {
  saveIndicatorSettings()
}, { deep: true })

// 主图叠加指标series存储
const overlaySeriesMap = new Map<string, Record<string, SeriesApi>>()

// SMC 专用 Canvas 叠加层
let smcCanvas: HTMLCanvasElement | null = null
let smcCtx: CanvasRenderingContext2D | null = null
let smcLastDpr: number = 0  // 记录上次设备像素比
const smcDataRef = ref<any>(null)  // 缓存 SMC 数据用于重绘
const smcSeriesRef = ref<SeriesApi[]>([])  // SMC LineSeries 引用
const chartDataRef = ref<any[]>([])  // K线数据缓存，用于 Canvas 重绘

// ========== 多指标管理 ==========
import {
  INDICATOR_REGISTRY,
  getIndicatorConfig,
  type IndicatorConfig,
  type SeriesConfig
} from '@/components/charts/indicator-registry'

// ========== 多指标Pane管理 ==========
// 指标系列存储（每个指标的多个series）
const indicatorSeriesMap = new Map<string, Record<string, SeriesApi>>()

// 指标警戒线存储（KDJ等指标的水平警戒线）
const indicatorAlertLinesMap = new Map<string, SeriesApi[]>()

// 指标数据缓存（后端返回的原始数据）
const indicatorDataCache = ref<Record<string, any>>({})

// 当前指标pane数量（用于动态分配索引）
let currentIndicatorPaneCount = 0

/**
 * 清除所有指标pane和series
 */
const clearAllIndicatorPanes = () => {
  // 清除 SMC Canvas
  destroySMCCanvas()

  // 清除所有警戒线
  indicatorAlertLinesMap.forEach(lines => {
    lines.forEach(line => {
      try {
        line.setData([])
      } catch (e) {}
    })
  })
  indicatorAlertLinesMap.clear()

  // 清除所有series数据
  indicatorSeriesMap.forEach(seriesMap => {
    Object.values(seriesMap).forEach(series => {
      series?.setData([])
    })
  })
  indicatorSeriesMap.clear()
  indicatorPaneIndexMap.clear()

  // 移除所有指标pane（从后往前移除，避免索引变化）
  const paneCount = chart?.panes().length || 0
  for (let i = paneCount - 1; i >= 1; i--) {
    try {
      chart?.removePane(i)
    } catch (e) {}
  }
  currentIndicatorPaneCount = 0
  console.log('[指标] 已清除所有指标pane')
}

/**
 * 为指标分配pane索引（动态分配，从1开始连续）
 */
const allocatePaneIndex = (): number => {
  return ++currentIndicatorPaneCount
}

/**
 * 获取指标的pane索引
 */
const getIndicatorPaneIndex = (indicatorId: string): number => {
  return indicatorPaneIndexMap.get(indicatorId) || 0
}

// ========== 价格预警相关 ==========
let userPriceAlerts: UserPriceAlerts | null = null
const showPriceAlertPanel = ref(false)
const priceAlertInput = ref<number | null>(null)
const priceLineToolActive = ref(false)
const isDragging = ref(false)
const draggedAlertId = ref<string | null>(null)
const draggedAlertTempPrice = ref<number | null>(null)
const editingAlertId = ref<string | null>(null)
const editingAlertPrice = ref<string>('')
const editingInput = ref<HTMLInputElement | null>(null)
const priceAlertsList = ref<any[]>([])
const priceAlertsKey = ref(0)
const showContextMenu = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const labelContextMenu = ref({
  show: false,
  alertId: '',
  x: 0,
  y: 0,
  currentPrice: 0,
  currentTitle: '',
  currentColor: '',
  enableAlert: false,
})
const triggeredAlerts = ref<Set<string>>(new Set())
const flashingAlerts = ref<Set<string>>(new Set())
let priceAlertRafId: number | null = null

// WebSocket 实例（1分钟线实时推送）
let klineWs: any = null  // KlineWebSocket
let aggregator: any = null  // Kline聚合器（所有周期都用WS，前端聚合）
const wsConnected = ref(false)

// 十字光标悬停的 bar 数据
const hoverBar = ref<{ time: string; open: number; high: number; low: number; close: number; volume: number } | null>(null)

// 当前股票名称
const currentStockName = computed(() => {
  const stock = dataStore.watchlist.find(s => s.symbol === selectedStock.value)
  return stock ? `${stock.name} (${stock.symbol})` : selectedStock.value
})

// 当前股票名称（用于面板标题，响应式）
const currentStockNameForPanel = computed(() => {
  // 优先从 watchlist 获取
  const stock = dataStore.watchlist.find(s => s.symbol === selectedStock.value)
  if (stock) return stock.name

  // 从所有分组中查找
  for (const group of dataStore.watchlistGroups) {
    const groupStock = group.stocks.find(s => s.symbol === selectedStock.value)
    if (groupStock) return groupStock.name
  }

  // 其次从实时行情获取
  const quote = dataStore.quotes[selectedStock.value]
  if (quote && quote.name) return quote.name

  // 最后返回代码
  return selectedStock.value
})

// 状态栏文字（直接显示市场状态）
const statusbarText = computed(() => {
  const status = marketStatusCache.value
  if (!status) return '行情'

  // 直接显示市场状态：交易中 / 休市
  return status.status || '行情'
})

// 格式化成交量
const formatVolume = (vol: number): string => {
  if (!vol) return '--'
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toString()
}

// 将带时间戳的价格数组转为 SVG polyline points 字符串
// X轴：按交易分钟数映射（A股240个交易分钟）
// Y轴：价格映射（已移至 useMiniCharts.generateSparklinePoints）

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
      mode: CrosshairMode.Normal,
      vertLine: {
        width: 1,
        color: '#758696',
        style: 2, // 虚线
      },
      horzLine: {
        width: 1,
        color: '#758696',
        style: 2, // 虚线
      },
    },
    rightPriceScale: {
      borderColor: 'transparent',
      autoScale: false,
      visible: true,
    },
    leftPriceScale: {
      borderColor: 'transparent',
      visible: false,
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
      borderColor: 'rgba(42, 46, 57, 0.25)',
      timeVisible: true,
      secondsVisible: false,
      minBarSpacing: 0.5,
      rightOffset: 10,
      fixLeftEdge: true,
      fixRightEdge: false,
      tickMarkFormatter: (timestamp: number, tickMarkType: number) => {
        // 只在A股交易时间段显示时间标签
        const date = new Date(timestamp * 1000)
        const hours = date.getHours()
        const minutes = date.getMinutes()
        const timeValue = hours * 100 + minutes

        // A股交易时间：9:30-11:30, 13:00-15:00
        const isTradingTime = (timeValue >= 930 && timeValue <= 1130) ||
                              (timeValue >= 1300 && timeValue <= 1500)

        // 日线/周线不限制，分钟线只在交易时间显示标签
        const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
        if (isDaily || isTradingTime) {
          const month = String(date.getMonth() + 1).padStart(2, '0')
          const day = String(date.getDate()).padStart(2, '0')
          const h = String(hours).padStart(2, '0')
          const m = String(minutes).padStart(2, '0')
          return isDaily ? `${month}-${day}` : `${h}:${m}`
        }
        // 非交易时间返回空，不显示刻度标签
        return ''
      }
    },
    // 时间轴配置
    localization: {
      dateFormat: 'yyyy-MM-dd',
      timeFormatter: (timestamp: number) => {
        const date = new Date(timestamp * 1000)
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
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
    crosshairMarkerRadius: 2,  // 缩小十字光标标记点（默认6）
    crosshairMarkerBorderWidth: 1,  // 缩小标记点边框（默认2）
  })

  // 创建成交量系列
  volumeSeries = chart.addSeries(HistogramSeries, {
    color: '#26a69a',
    priceFormat: {
      type: 'volume'
    },
    crosshairMarkerRadius: 3,  // 缩小十字光标标记点
    priceScaleId: 'volume'
  })

  chart.priceScale('volume').applyOptions({
    scaleMargins: {
      top: 0.8,
      bottom: 0
    }
  })

  // 指标pane将在用户选择指标时动态创建

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

  // 监听鼠标释放事件，保存pane高度
  chartContainer.value.addEventListener('mouseup', () => {
    // 延迟保存，确保pane高度已更新
    setTimeout(() => {
      saveCurrentPaneHeights()
    }, 100)
  })

  // 初始化价格预警插件
  if (!userPriceAlerts && candleSeries) {
    userPriceAlerts = new UserPriceAlerts({
      color: '#2196F3',
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: true,
    })
    userPriceAlerts.attach(chart, candleSeries)
    if (selectedStock.value) {
      userPriceAlerts.loadFromStorage(selectedStock.value)
      refreshPriceAlertsList()
    }
  }

  // 点击图表 → 添加价格线或执行其他操作
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
      refreshPriceAlertsList()

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
      refreshPriceAlertsList()

      // 保存到本地存储
      if (selectedStock.value && userPriceAlerts) {
        userPriceAlerts.saveToStorage(selectedStock.value)
      }

      console.log(`[价格预警] 已添加价格线: ${price.toFixed(2)}`)
    }
  })

  // 使用 requestAnimationFrame 实时更新标签位置
  let lastUpdateTime = 0
  const updateLabels = () => {
    const now = performance.now()
    if (now - lastUpdateTime > 16) {
      if (priceAlertsList.value.length > 0) {
        priceAlertsKey.value++
      }
      lastUpdateTime = now
    }
    priceAlertRafId = requestAnimationFrame(updateLabels)
  }
  priceAlertRafId = requestAnimationFrame(updateLabels)

  // 十字光标移动 → 更新 hoverBar
  chart.subscribeCrosshairMove((param: any) => {
    if (!param.time || !candleSeries) {
      hoverBar.value = null
      return
    }
    const bar = param.seriesData.get(candleSeries) as any
    const volBar = param.seriesData.get(volumeSeries) as any
    if (bar) {
      const ts = Number(param.time) * 1000
      const dt = new Date(ts)
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const timeStr = isDaily
        ? `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}`
        : `${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
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
}

// ========== 技术指标功能 ==========

// 指标到pane索引的映射（动态分配）
const indicatorPaneIndexMap = new Map<string, number>()

/**
 * 初始化指标Pane（动态分配索引）
 */
const initIndicatorPane = (indicatorId: string): number => {
  if (!chart) return 0

  const config = getIndicatorConfig(indicatorId)
  if (!config) {
    console.warn(`[指标] 未找到配置: ${indicatorId}`)
    return 0
  }

  // 已存在则返回已有索引
  if (indicatorSeriesMap.has(indicatorId)) {
    return indicatorPaneIndexMap.get(indicatorId) || 0
  }

  // 分配新的pane索引
  const paneIndex = allocatePaneIndex()
  indicatorPaneIndexMap.set(indicatorId, paneIndex)

  try {
    // 确保pane存在
    while (chart.panes().length <= paneIndex) {
      console.log(`[指标] 创建pane ${chart.panes().length}`)
      chart.addPane()
    }

    // 设置pane边框颜色（更灰）
    try {
      const pane = chart.panes()[paneIndex]
      if (pane) {
        // 通过DOM操作设置边框颜色
        setTimeout(() => {
          const paneElements = document.querySelectorAll('.pane')
          if (paneElements[paneIndex]) {
            (paneElements[paneIndex] as HTMLElement).style.borderTop = '1px solid rgba(60, 65, 75, 0.4)'
          }
        }, 0)
      }
    } catch (e) {}

    console.log(`[指标] 初始化 ${indicatorId}, pane: ${paneIndex}`)

    // 获取用户自定义参数
    const customParams = indicatorParams.value[indicatorId] || {}

    // 创建series
    const seriesMap: Record<string, SeriesApi> = {}

    config.series.forEach(s => {
      // 获取该线条的自定义设置
      const lineParams = customParams[s.key] || {}

      const seriesOptions: any = {
        color: lineParams.color || s.color,
        lineWidth: lineParams.lineWidth || s.lineWidth || 2,
        lineStyle: lineParams.lineStyle ?? 0,
        title: s.label,
        lastValueVisible: true,
        priceLineVisible: false,
        crosshairMarkerRadius: 2,  // 缩小十字光标标记点（默认6）
    crosshairMarkerBorderWidth: 1,  // 缩小标记点边框（默认2）（默认6）
      }

      // OBV 特殊处理：使用大数值格式（M表示百万）
      if (indicatorId === 'OBV') {
        seriesOptions.priceFormat = {
          type: 'custom',
          minMove: 0.01,
          formatter: (price: number) => {
            if (Math.abs(price) >= 1000000) {
              return (price / 1000000).toFixed(2) + 'M'
            } else if (Math.abs(price) >= 1000) {
              return (price / 1000).toFixed(1) + 'K'
            }
            return price.toFixed(0)
          }
        }
      }

      if (s.type === 'histogram') {
        seriesOptions.priceFormat = { type: 'price', precision: 2 }
        seriesMap[s.key] = chart.addSeries(HistogramSeries, seriesOptions, paneIndex)
      } else {
        seriesMap[s.key] = chart.addSeries(LineSeries, seriesOptions, paneIndex)
      }
    })

    indicatorSeriesMap.set(indicatorId, seriesMap)

    // 设置pane伸展因子（从保存的设置恢复）
    const pane = chart.panes()[paneIndex]
    if (pane) {
      const savedHeight = indicatorPaneHeights.value[indicatorId]
      console.log(`[指标] ${indicatorId} 准备设置高度, savedHeight:`, savedHeight, 'indicatorPaneHeights:', JSON.stringify(indicatorPaneHeights.value))
      if (savedHeight && savedHeight !== 1) {
        pane.setStretchFactor(savedHeight)
        console.log(`[指标] ${indicatorId} 已应用保存的高度: ${savedHeight}`)
      } else {
        pane.setStretchFactor(1)
        console.log(`[指标] ${indicatorId} 使用默认高度: 1`)
      }
    }

    // 配置price scale
    try {
      chart?.priceScale('right', paneIndex).applyOptions({
        visible: true,
        autoScale: true,
        borderVisible: true,
        borderColor: 'rgba(42, 46, 57, 0.25)',
        scaleMargins: { top: 0.1, bottom: 0.1 }
      })
    } catch (e) {
      console.log(`[指标] ${indicatorId} price scale配置失败:`, e)
    }

    console.log(`[指标] ${indicatorId} pane初始化完成`)

    // 触发resize
    if (chartContainer.value) {
      const rect = chartContainer.value.getBoundingClientRect()
      chart.resize(rect.width, rect.height)
    }
  } catch (e) {
    console.error(`[指标] ${indicatorId} pane初始化失败:`, e)
  }
}

/**
 * 更新指标数据（通用版本）
 */
const updateIndicatorData = (indicatorId: string, klineData: any[]) => {
  const seriesMap = indicatorSeriesMap.get(indicatorId)
  if (!seriesMap) {
    console.log(`[指标] ${indicatorId} series未初始化`)
    return
  }

  const indicatorData = indicatorDataCache.value[indicatorId]
  if (!indicatorData) {
    console.log(`[指标] 无${indicatorId}数据`)
    return
  }

  const config = getIndicatorConfig(indicatorId)
  if (!config) return

  const datetime = indicatorData.datetime
  if (!datetime) return

  // 构建时间戳映射
  const timeMap = new Map<number, number>()
  klineData.forEach((bar, index) => {
    if (datetime[index]) {
      const ts = new Date(datetime[index]).getTime() / 1000
      timeMap.set(index, ts)
    }
  })

  // 为每个series准备数据
  config.series.forEach(s => {
    const values = indicatorData[s.key]
    if (!values || !seriesMap[s.key]) return

    const data: any[] = []
    for (let i = 0; i < values.length; i++) {
      const time = timeMap.get(i)
      const value = values[i]
      if (!time || value === null || isNaN(value)) continue

      if (s.type === 'histogram') {
        data.push({ time, value, color: value >= 0 ? '#ef4444' : '#10b981' })
      } else {
        data.push({ time, value })
      }
    }

    seriesMap[s.key]?.setData(data)
    console.log(`[指标] ${indicatorId}.${s.key} 设置 ${data.length} 条数据`)
  })

  // 确保price scale可见
  const paneIndex = getIndicatorPaneIndex(indicatorId)
  try {
    chart?.priceScale('right', paneIndex).applyOptions({
      visible: true,
      autoScale: true
    })
  } catch (e) {}

  // KDJ 特殊处理：创建/更新警戒线（80超买、10超卖）
  if (indicatorId === 'KDJ') {
    try {
      const times = Array.from(timeMap.values()).filter(t => t && t > 0)
      if (times.length >= 2) {
        const firstTime = times[0]
        const lastTime = times[times.length - 1]
        const paneIndex = getIndicatorPaneIndex(indicatorId)

        // 检查警戒线是否已存在
        let alertLines = indicatorAlertLinesMap.get(indicatorId)

        if (!alertLines) {
          // 首次创建警戒线
          console.log('[指标] KDJ 首次创建警戒线')

          // 创建80警戒线（超买）
          const overboughtLine = chart.addSeries(LineSeries, {
            color: '#FF6B6B',
            lineWidth: 1,
            lineStyle: 1, // 虚线
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,  // 隐藏十字光标标记点
          }, paneIndex)

          // 创建10警戒线（超卖）
          const oversoldLine = chart.addSeries(LineSeries, {
            color: '#26A69A',
            lineWidth: 1,
            lineStyle: 1, // 虚线
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,  // 隐藏十字光标标记点
          }, paneIndex)

          alertLines = [overboughtLine, oversoldLine]
          indicatorAlertLinesMap.set(indicatorId, alertLines)
        }

        // 更新警戒线数据
        alertLines[0]?.setData([
          { time: firstTime, value: 80 },
          { time: lastTime, value: 80 }
        ])

        alertLines[1]?.setData([
          { time: firstTime, value: 10 },
          { time: lastTime, value: 10 }
        ])

        console.log('[指标] KDJ 警戒线已更新:', firstTime, '-', lastTime)
      } else {
        console.log('[指标] KDJ 时间数据不足:', times.length)
      }
    } catch (e) {
      console.error('[指标] KDJ 警戒线处理失败:', e)
    }
  }

  // RSI 特殊处理：创建/更新警戒线（70超买、30超卖）
  if (indicatorId === 'RSI') {
    try {
      const times = Array.from(timeMap.values()).filter(t => t && t > 0)
      if (times.length >= 2) {
        const firstTime = times[0]
        const lastTime = times[times.length - 1]
        const paneIndex = getIndicatorPaneIndex(indicatorId)

        let alertLines = indicatorAlertLinesMap.get(indicatorId)

        if (!alertLines) {
          console.log('[指标] RSI 首次创建警戒线')

          // 创建70警戒线（超买）
          const overboughtLine = chart.addSeries(LineSeries, {
            color: '#FF6B6B',
            lineWidth: 1,
            lineStyle: 1,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          // 创建30警戒线（超卖）
          const oversoldLine = chart.addSeries(LineSeries, {
            color: '#26A69A',
            lineWidth: 1,
            lineStyle: 1,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          alertLines = [overboughtLine, oversoldLine]
          indicatorAlertLinesMap.set(indicatorId, alertLines)
        }

        alertLines[0]?.setData([
          { time: firstTime, value: 70 },
          { time: lastTime, value: 70 }
        ])

        alertLines[1]?.setData([
          { time: firstTime, value: 30 },
          { time: lastTime, value: 30 }
        ])

        console.log('[指标] RSI 警戒线已更新:', firstTime, '-', lastTime)
      } else {
        console.log('[指标] RSI 时间数据不足:', times.length)
      }
    } catch (e) {
      console.error('[指标] RSI 警戒线处理失败:', e)
    }
  }

  // CCI 特殊处理：创建/更新警戒线（+200极端超买、+100超买、-100超卖、-200极端超卖）
  if (indicatorId === 'CCI') {
    try {
      const times = Array.from(timeMap.values()).filter(t => t && t > 0)
      if (times.length >= 2) {
        const firstTime = times[0]
        const lastTime = times[times.length - 1]
        const paneIndex = getIndicatorPaneIndex(indicatorId)

        let alertLines = indicatorAlertLinesMap.get(indicatorId)

        if (!alertLines) {
          console.log('[指标] CCI 首次创建警戒线')

          // 创建+200警戒线（极端超买）
          const extremeOverboughtLine = chart.addSeries(LineSeries, {
            color: '#FFD700',
            lineWidth: 1,
            lineStyle: 2,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          // 创建+100警戒线（超买）
          const overboughtLine = chart.addSeries(LineSeries, {
            color: '#FF6B6B',
            lineWidth: 1,
            lineStyle: 1,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          // 创建-100警戒线（超卖）
          const oversoldLine = chart.addSeries(LineSeries, {
            color: '#26A69A',
            lineWidth: 1,
            lineStyle: 1,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          // 创建-200警戒线（极端超卖）
          const extremeOversoldLine = chart.addSeries(LineSeries, {
            color: '#4CAF50',
            lineWidth: 1,
            lineStyle: 2,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          alertLines = [extremeOverboughtLine, overboughtLine, oversoldLine, extremeOversoldLine]
          indicatorAlertLinesMap.set(indicatorId, alertLines)
        }

        alertLines[0]?.setData([
          { time: firstTime, value: 200 },
          { time: lastTime, value: 200 }
        ])

        alertLines[1]?.setData([
          { time: firstTime, value: 100 },
          { time: lastTime, value: 100 }
        ])

        alertLines[2]?.setData([
          { time: firstTime, value: -100 },
          { time: lastTime, value: -100 }
        ])

        alertLines[3]?.setData([
          { time: firstTime, value: -200 },
          { time: lastTime, value: -200 }
        ])

        console.log('[指标] CCI 警戒线已更新:', firstTime, '-', lastTime)
      } else {
        console.log('[指标] CCI 时间数据不足:', times.length)
      }
    } catch (e) {
      console.error('[指标] CCI 警戒线处理失败:', e)
    }
  }

  // WR 特殊处理：创建/更新警戒线（80超买、20超卖）
  if (indicatorId === 'WR') {
    try {
      const times = Array.from(timeMap.values()).filter(t => t && t > 0)
      if (times.length >= 2) {
        const firstTime = times[0]
        const lastTime = times[times.length - 1]
        const paneIndex = getIndicatorPaneIndex(indicatorId)

        let alertLines = indicatorAlertLinesMap.get(indicatorId)

        if (!alertLines) {
          console.log('[指标] WR 首次创建警戒线')

          // 创建80警戒线（超买）
          const overboughtLine = chart.addSeries(LineSeries, {
            color: '#FF6B6B',
            lineWidth: 1,
            lineStyle: 1,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          // 创建20警戒线（超卖）
          const oversoldLine = chart.addSeries(LineSeries, {
            color: '#26A69A',
            lineWidth: 1,
            lineStyle: 1,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          alertLines = [overboughtLine, oversoldLine]
          indicatorAlertLinesMap.set(indicatorId, alertLines)
        }

        alertLines[0]?.setData([
          { time: firstTime, value: 80 },
          { time: lastTime, value: 80 }
        ])

        alertLines[1]?.setData([
          { time: firstTime, value: 20 },
          { time: lastTime, value: 20 }
        ])

        console.log('[指标] WR 警戒线已更新:', firstTime, '-', lastTime)
      } else {
        console.log('[指标] WR 时间数据不足:', times.length)
      }
    } catch (e) {
      console.error('[指标] WR 警戒线处理失败:', e)
    }
  }

  // BIAS 特殊处理：创建/更新警戒线（3超买、-3超卖）
  if (indicatorId === 'BIAS') {
    try {
      const times = Array.from(timeMap.values()).filter(t => t && t > 0)
      if (times.length >= 2) {
        const firstTime = times[0]
        const lastTime = times[times.length - 1]
        const paneIndex = getIndicatorPaneIndex(indicatorId)

        let alertLines = indicatorAlertLinesMap.get(indicatorId)

        if (!alertLines) {
          console.log('[指标] BIAS 首次创建警戒线')

          // 创建3警戒线（超买）
          const overboughtLine = chart.addSeries(LineSeries, {
            color: '#FF6B6B',
            lineWidth: 1,
            lineStyle: 1,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          // 创建-3警戒线（超卖）
          const oversoldLine = chart.addSeries(LineSeries, {
            color: '#26A69A',
            lineWidth: 1,
            lineStyle: 1,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          alertLines = [overboughtLine, oversoldLine]
          indicatorAlertLinesMap.set(indicatorId, alertLines)
        }

        alertLines[0]?.setData([
          { time: firstTime, value: 3 },
          { time: lastTime, value: 3 }
        ])

        alertLines[1]?.setData([
          { time: firstTime, value: -3 },
          { time: lastTime, value: -3 }
        ])

        console.log('[指标] BIAS 警戒线已更新:', firstTime, '-', lastTime)
      } else {
        console.log('[指标] BIAS 时间数据不足:', times.length)
      }
    } catch (e) {
      console.error('[指标] BIAS 警戒线处理失败:', e)
    }
  }

  // TOPBOTTOM 顶底背离指标特殊处理
  if (indicatorId === 'TOPBOTTOM') {
    try {
      const times = Array.from(timeMap.values()).filter(t => t && t > 0)
      if (times.length >= 2) {
        const firstTime = times[0]
        const lastTime = times[times.length - 1]
        const paneIndex = getIndicatorPaneIndex(indicatorId)

        let alertLines = indicatorAlertLinesMap.get(indicatorId)

        if (!alertLines) {
          console.log('[指标] TOPBOTTOM 首次创建警戒线')

          // 创建80超买警戒线
          const overboughtLine = chart.addSeries(LineSeries, {
            color: 'rgba(244, 67, 54, 0.6)',
            lineWidth: 1,
            lineStyle: 2,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          // 创建20超卖警戒线
          const oversoldLine = chart.addSeries(LineSeries, {
            color: 'rgba(76, 175, 80, 0.6)',
            lineWidth: 1,
            lineStyle: 2,
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }, paneIndex)

          alertLines = [overboughtLine, oversoldLine]
          indicatorAlertLinesMap.set(indicatorId, alertLines)
        }

        alertLines[0]?.setData([
          { time: firstTime, value: 80 },
          { time: lastTime, value: 80 }
        ])

        alertLines[1]?.setData([
          { time: firstTime, value: 20 },
          { time: lastTime, value: 20 }
        ])

        console.log('[指标] TOPBOTTOM 警戒线已更新:', firstTime, '-', lastTime)
      } else {
        console.log('[指标] TOPBOTTOM 时间数据不足:', times.length)
      }
    } catch (e) {
      console.error('[指标] TOPBOTTOM 警戒线处理失败:', e)
    }
  }
}

// ========== 主图叠加指标 ==========

/**
 * 初始化主图叠加指标
 */
const initOverlayIndicator = (indicatorId: string) => {
  if (!chart) return

  const config = getIndicatorConfig(indicatorId)
  if (!config) return

  // 已存在则跳过
  if (overlaySeriesMap.has(indicatorId)) {
    console.log(`[叠加指标] ${indicatorId} series已存在`)
    return
  }

  console.log(`[叠加指标] 初始化 ${indicatorId}`)

  // 获取用户自定义参数
  const customParams = indicatorParams.value[indicatorId] || {}

  // 创建series（pane 0 = 主图）
  const seriesMap: Record<string, SeriesApi> = {}

  config.series.forEach(s => {
    // MA/BOLL指标：检查是否在可见列表中
    if (customParams.visibleLines) {
      if (!customParams.visibleLines.includes(s.key)) {
        console.log(`[叠加指标] ${indicatorId} ${s.key} 未勾选，跳过`)
        return
      }
    }

    // 获取该线条的自定义设置
    const lineParams = customParams[s.key] || {}
    const lineColor = lineParams.color || s.color
    const lineWidth = parseInt(lineParams.lineWidth) || s.lineWidth || 1
    const lineStyle = parseInt(lineParams.lineStyle) || 0

    const seriesOptions: any = {
      color: lineColor,
      lineWidth: lineWidth,
      lineStyle: lineStyle,
      title: s.label,
      lastValueVisible: true,
      priceLineVisible: false,
      crosshairMarkerRadius: 2,  // 缩小十字光标标记点（默认6）
    crosshairMarkerBorderWidth: 1,  // 缩小标记点边框（默认2）
    }

    console.log(`[叠加指标] ${indicatorId}.${s.key} 选项:`, { color: lineColor, lineWidth, lineStyle })

    seriesMap[s.key] = chart.addSeries(LineSeries, seriesOptions, 0)
  })

  overlaySeriesMap.set(indicatorId, seriesMap)
  console.log(`[叠加指标] ${indicatorId} 初始化完成, 创建了 ${Object.keys(seriesMap).length} 条线`)
}

/**
 * 更新主图叠加指标数据
 */
const updateOverlayData = (indicatorId: string, klineData: any[]) => {
  const seriesMap = overlaySeriesMap.get(indicatorId)
  console.log(`[叠加指标] updateOverlayData: ${indicatorId}`, {
    hasSeriesMap: !!seriesMap,
    cachedKeys: indicatorDataCache.value[indicatorId] ? Object.keys(indicatorDataCache.value[indicatorId]) : '无缓存'
  })
  if (!seriesMap) return

  const indicatorData = indicatorDataCache.value[indicatorId]
  console.log(`[叠加指标] ${indicatorId} 数据检查:`, indicatorData ? Object.keys(indicatorData) : '无数据')
  if (!indicatorData) {
    console.log(`[叠加指标] 无${indicatorId}数据, cache内容:`, Object.keys(indicatorDataCache.value))
    return
  }

  const config = getIndicatorConfig(indicatorId)
  if (!config) return

  // SMC 指标特殊处理
  if (indicatorId === 'SMC') {
    updateSMCIndicator(indicatorData, klineData)
    return
  }

  // 构建时间戳映射
  const timeMap = new Map<number, number>()
  klineData.forEach((bar, index) => {
    timeMap.set(index, bar.time)
  })

  // 为每个series准备数据
  config.series.forEach(s => {
    const values = indicatorData[s.key]
    if (!values || !seriesMap[s.key]) return

    const data: any[] = []
    for (let i = 0; i < values.length; i++) {
      const time = timeMap.get(i)
      const value = values[i]
      if (!time || value === null || isNaN(value)) continue
      data.push({ time, value })
    }

    seriesMap[s.key]?.setData(data)
    console.log(`[叠加指标] ${indicatorId}.${s.key} 设置 ${data.length} 条数据`)
  })
}

/**
 * 创建 SMC Canvas 叠加层
 */
const createSMCCanvas = () => {
  console.log('[SMC Canvas] createSMCCanvas 调用', { hasChart: !!chart, hasCanvas: !!smcCanvas })
  if (!chart || smcCanvas) return

  // 使用 chartElement() - 这是图表的内部容器，坐标系统与它对齐
  const chartElement = chart.chartElement()
  console.log('[SMC Canvas] chartElement:', chartElement)
  if (!chartElement) {
    console.log('[SMC Canvas] chartElement 不存在，尝试使用 container')
    // 备选方案：使用 container
    const container = chartContainer.value
    if (!container) {
      console.log('[SMC Canvas] container 也不存在，退出')
      return
    }
  }

  const targetElement = chartElement || chartContainer.value
  if (!targetElement) return

  // 确保父元素有 relative 定位
  const parentStyle = window.getComputedStyle(targetElement)
  if (parentStyle.position === 'static') {
    (targetElement as HTMLElement).style.position = 'relative'
  }

  // 检查是否已存在
  const existing = document.getElementById('smc-overlay-canvas')
  if (existing) {
    console.log('[SMC Canvas] Canvas 已存在，复用')
    smcCanvas = existing as HTMLCanvasElement
    smcCtx = smcCanvas.getContext('2d')
    return
  }

  smcCanvas = document.createElement('canvas')
  smcCanvas.id = 'smc-overlay-canvas'
  smcCanvas.style.position = 'absolute'
  smcCanvas.style.top = '0'
  smcCanvas.style.left = '0'
  smcCanvas.style.pointerEvents = 'none'
  smcCanvas.style.zIndex = '100'  // 高 z-index 确保可见
  targetElement.appendChild(smcCanvas)

  smcCtx = smcCanvas.getContext('2d')

  console.log('[SMC Canvas] Canvas 创建完成', {
    parentTag: targetElement.tagName,
    parentRect: targetElement.getBoundingClientRect(),
    canvasRect: smcCanvas.getBoundingClientRect()
  })

  // 监听图表大小变化
  chart.timeScale().subscribeVisibleLogicalRangeChange(() => {
    requestAnimationFrame(drawSMCCanvas)
  })
  chart.subscribeCrosshairMove(() => {
    // 十字光标移动时不需要重绘
  })
}

/**
 * 销毁 SMC Canvas
 */
const destroySMCCanvas = () => {
  if (smcCanvas) {
    smcCanvas.remove()
    smcCanvas = null
    smcCtx = null
  }
}

// 线条样式转换为 Canvas lineDash
const getLineDash = (style: number): number[] => {
  switch (style) {
    case 0: return []          // 实线
    case 1: return [6, 4]      // 虚线
    case 2: return [2, 2]      // 点线
    case 3: return [4, 2, 1, 2] // 点虚线
    default: return [6, 4]
  }
}

/**
 * 绘制 SMC V2 Canvas (改进版，更接近 TradingView 效果)
 *
 * V2 改进:
 * 1. BMS/CHoCH 使用方框+文字标签
 * 2. 摆动点使用圆角矩形背景
 * 3. 供需区域使用渐变填充
 * 4. 整体配色更接近 TradingView
 */
const drawSMCCanvas = () => {
  if (!chart || !smcCanvas || !smcCtx || !candleSeries) return

  const smcData = smcDataRef.value
  const klineData = chartDataRef.value || []

  if (!smcData || klineData.length === 0) return

  const chartElement = chart.chartElement()
  const rect = chartElement ? chartElement.getBoundingClientRect() : smcCanvas.getBoundingClientRect()

  // 更新 canvas 大小
  const dpr = window.devicePixelRatio || 1
  const canvasWidth = Math.floor(rect.width * dpr)
  const canvasHeight = Math.floor(rect.height * dpr)

  if (smcCanvas.width !== canvasWidth || smcCanvas.height !== canvasHeight || smcLastDpr !== dpr) {
    smcCanvas.width = canvasWidth
    smcCanvas.height = canvasHeight
    smcCanvas.style.width = rect.width + 'px'
    smcCanvas.style.height = rect.height + 'px'
    smcCtx!.setTransform(dpr, 0, 0, dpr, 0, 0)
    smcLastDpr = dpr
  }

  // 清除画布
  smcCtx.clearRect(0, 0, rect.width, rect.height)

  const timeScale = chart.timeScale()
  const lastTime = klineData[klineData.length - 1].time
  const params = indicatorParams.value['SMC'] || {}

  // ==================== 从设置读取颜色配置 ====================
  const hexToRgba = (hex: string, opacity: number): string => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    if (!result) return `rgba(128, 128, 128, ${opacity / 100})`
    return `rgba(${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}, ${opacity / 100})`
  }

  // 从 params 读取颜色，使用默认值作为回退
  const colors = {
    // 摆动点
    swingHigh: params.swing_high_color || '#00D9FF',
    swingLow: params.swing_low_color || '#FF61D2',

    // BMS (Break of Market Structure)
    bms: params.bms_color || '#FFD700',

    // CHoCH
    choch: params.choch_color || '#9C27B0',

    // Order Blocks - 从设置读取颜色和透明度
    obBullish: hexToRgba(params.ob_bullish || '#00D9FF', params.ob_opacity || 15),
    obBearish: hexToRgba(params.ob_bearish || '#FF61D2', params.ob_opacity || 15),
    obBorderBullish: params.ob_bullish || '#00D9FF',
    obBorderBearish: params.ob_bearish || '#FF61D2',

    // FVG - 从设置读取颜色和透明度
    fvgBullish: hexToRgba(params.fvg_bullish || '#4CAF50', params.fvg_opacity || 12),
    fvgBearish: hexToRgba(params.fvg_bearish || '#F44336', params.fvg_opacity || 12),
    fvgBorderBullish: params.fvg_bullish || '#4CAF50',
    fvgBorderBearish: params.fvg_bearish || '#F44336',
  }

  // 辅助函数：绘制圆角矩形
  const drawRoundedRect = (x: number, y: number, width: number, height: number, radius: number) => {
    smcCtx!.beginPath()
    smcCtx!.moveTo(x + radius, y)
    smcCtx!.lineTo(x + width - radius, y)
    smcCtx!.quadraticCurveTo(x + width, y, x + width, y + radius)
    smcCtx!.lineTo(x + width, y + height - radius)
    smcCtx!.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
    smcCtx!.lineTo(x + radius, y + height)
    smcCtx!.quadraticCurveTo(x, y + height, x, y + height - radius)
    smcCtx!.lineTo(x, y + radius)
    smcCtx!.quadraticCurveTo(x, y, x + radius, y)
    smcCtx!.closePath()
  }

  // 辅助函数：绘制线条（支持多种样式）
  // lineStyle: 0=实线, 1=虚线, 2=点线, 3=点虚线
  const drawStyledLine = (
    x1: number, y1: number, x2: number, y2: number,
    color: string, width: number = 1, lineStyle: number = 1, opacity: number = 100
  ) => {
    smcCtx!.beginPath()

    // 根据线条样式设置虚线模式
    const dashPattern: number[] = {
      0: [],           // 实线
      1: [4, 4],       // 虚线
      2: [2, 2],       // 点线
      3: [2, 2, 4, 2]  // 点虚线
    }[lineStyle] || [4, 4]

    // 应用透明度
    const finalColor = opacity < 100 ? hexToRgba(color, opacity) : color

    smcCtx!.setLineDash(dashPattern)
    smcCtx!.moveTo(x1, y1)
    smcCtx!.lineTo(x2, y2)
    smcCtx!.strokeStyle = finalColor
    smcCtx!.lineWidth = width
    smcCtx!.stroke()
    smcCtx!.setLineDash([])
  }

  // ==================== 1. FVG 区域 (最底层) ====================
  if (params.show_fvg !== false && smcData.fvg_type) {
    const fvgCount = params.fvg_count || 5
    const fvgList: any[] = []

    smcData.fvg_type?.forEach((type: number, index: number) => {
      if (type === 0) return
      const top = smcData.fvg_top?.[index]
      const bottom = smcData.fvg_bottom?.[index]
      const time = klineData[index]?.time
      if (top === null || bottom === null || !time) return
      fvgList.push({ type, top, bottom, time })
    })

    const recentFVGs = fvgList.slice(-fvgCount)

    recentFVGs.forEach(fvg => {
      const isBullish = fvg.type > 0
      const x1 = timeScale.timeToCoordinate(fvg.time)
      const x2 = timeScale.timeToCoordinate(lastTime)
      const y1 = candleSeries.priceToCoordinate(fvg.top)
      const y2 = candleSeries.priceToCoordinate(fvg.bottom)

      if (x1 === null || x2 === null || y1 === null || y2 === null) return

      const height = Math.abs(y2 - y1)
      if (height < 2) return

      // 填充区域
      smcCtx!.fillStyle = isBullish ? colors.fvgBullish : colors.fvgBearish
      smcCtx!.fillRect(x1, Math.min(y1, y2), x2 - x1, height)

      // 绘制上下边框（使用配置的边框样式）
      const fvgLineStyle = params.fvg_line_style ?? 1
      const fvgLineWidth = params.fvg_line_width ?? 1
      const fvgBorderOpacity = params.fvg_border_opacity ?? 100
      const borderColor = isBullish ? colors.fvgBorderBullish : colors.fvgBorderBearish
      drawStyledLine(x1, y1, x2, y1, borderColor, fvgLineWidth, fvgLineStyle, fvgBorderOpacity)
      drawStyledLine(x1, y2, x2, y2, borderColor, fvgLineWidth, fvgLineStyle, fvgBorderOpacity)
    })
  }

  // ==================== 2. Order Blocks (中间层) ====================
  if (params.show_ob !== false && smcData.ob_type) {
    const obCount = params.ob_count || 5
    const obList: any[] = []

    smcData.ob_type?.forEach((type: number, index: number) => {
      if (type === 0) return
      const top = smcData.ob_top?.[index]
      const bottom = smcData.ob_bottom?.[index]
      const time = klineData[index]?.time
      if (top === null || bottom === null || !time) return
      obList.push({ type, top, bottom, time })
    })

    const recentOBs = obList.slice(-obCount)

    recentOBs.forEach(ob => {
      const isBullish = ob.type > 0
      const x1 = timeScale.timeToCoordinate(ob.time)
      const x2 = timeScale.timeToCoordinate(lastTime)
      const y1 = candleSeries.priceToCoordinate(ob.top)
      const y2 = candleSeries.priceToCoordinate(ob.bottom)

      if (x1 === null || x2 === null || y1 === null || y2 === null) return

      const height = Math.abs(y2 - y1)
      if (height < 3) return

      // 填充区域
      smcCtx!.fillStyle = isBullish ? colors.obBullish : colors.obBearish
      smcCtx!.fillRect(x1, Math.min(y1, y2), x2 - x1, height)

      // 实线边框 (右侧)
      const obLineStyle = params.ob_line_style ?? 0
      const obLineWidth = params.ob_border_width ?? 2
      const obBorderOpacity = params.ob_border_opacity ?? 100
      const borderColor = isBullish ? colors.obBorderBullish : colors.obBorderBearish
      const finalBorderColor = obBorderOpacity < 100 ? hexToRgba(borderColor, obBorderOpacity) : borderColor

      smcCtx!.strokeStyle = finalBorderColor
      smcCtx!.lineWidth = obLineWidth

      // 根据线条样式设置虚线模式
      const obDashPattern: number[] = {
        0: [],           // 实线
        1: [4, 4],       // 虚线
        2: [2, 2],       // 点线
        3: [2, 2, 4, 2]  // 点虚线
      }[obLineStyle] || []
      smcCtx!.setLineDash(obDashPattern)
      smcCtx!.strokeRect(x1, Math.min(y1, y2), x2 - x1, height)
      smcCtx!.setLineDash([])

      // 左侧小标签
      const labelY = (y1 + y2) / 2
      smcCtx!.fillStyle = finalBorderColor
      smcCtx!.font = 'bold 9px sans-serif'
      smcCtx!.textAlign = 'right'
      smcCtx!.fillText(isBullish ? 'OB+' : 'OB-', x1 - 4, labelY + 3)
    })
  }

  // ==================== 3. 摆动点 (HH/HL/LL/LH) ====================
  if (params.show_swing_points !== false) {
    // 收集所有摆动点
    const swingPoints: any[] = []

    smcData.swing_highs?.forEach((price: number | null, index: number) => {
      if (price === null || !klineData[index]) return
      const label = smcData.swing_labels?.[index] || 'HH'
      swingPoints.push({ index, price, label, type: 'high' })
    })

    smcData.swing_lows?.forEach((price: number | null, index: number) => {
      if (price === null || !klineData[index]) return
      const label = smcData.swing_labels?.[index] || 'LL'
      swingPoints.push({ index, price, label, type: 'low' })
    })

    // 绘制每个摆动点
    swingPoints.forEach(sp => {
      const time = klineData[sp.index].time
      const x = timeScale.timeToCoordinate(time)
      const y = candleSeries.priceToCoordinate(sp.price)

      if (x === null || y === null) return

      const isHigh = sp.type === 'high'
      const color = isHigh ? colors.swingHigh : colors.swingLow

      // 小圆点 (中心)
      smcCtx!.beginPath()
      smcCtx!.arc(x, y, 3, 0, Math.PI * 2)
      smcCtx!.fillStyle = color
      smcCtx!.fill()

      // 标签背景 (圆角矩形)
      const label = sp.label
      smcCtx!.font = 'bold 10px sans-serif'
      const textWidth = smcCtx!.measureText(label).width
      const padding = 4
      const boxWidth = textWidth + padding * 2
      const boxHeight = 14

      const boxX = x - boxWidth / 2
      const boxY = isHigh ? y - boxHeight - 8 : y + 8

      // 绘制标签背景
      smcCtx!.fillStyle = 'rgba(19, 23, 34, 0.85)'
      drawRoundedRect(boxX, boxY, boxWidth, boxHeight, 3)
      smcCtx!.fill()

      // 绘制标签文字
      smcCtx!.fillStyle = color
      smcCtx!.textAlign = 'center'
      smcCtx!.textBaseline = 'middle'
      smcCtx!.fillText(label, x, boxY + boxHeight / 2)
    })
  }

  // 绘制参考线（最近 N 根K线的最高/最低）- 独立于摆动点显示
  console.log('[SMC Canvas] ====== 参考线检查 ======')
  console.log('[SMC Canvas] smcData 所有键:', Object.keys(smcData))
  console.log('[SMC Canvas] 参考线参数:', {
    show_reference: params.show_reference,
    reference_high: smcData.reference_high,
    reference_low: smcData.reference_low
  })
  if (params.show_reference !== false && smcData.reference_high !== undefined) {
    console.log('[SMC Canvas] 参考线条件满足，开始绘制')
    const lastBarIndex = klineData.length - 1
    const lastBarTime = klineData[lastBarIndex]?.time
    const x2 = lastBarTime ? timeScale.timeToCoordinate(lastBarTime) : null

    if (x2 !== null) {
      const refLineColor = params.reference_color || '#FFD700'
      const refLineStyle = params.reference_line_style ?? 2
      const refLineWidth = params.reference_line_width ?? 1
      const refLineOpacity = params.reference_opacity ?? 80

      // 绘制最高点参考线
      const highIndex = smcData.reference_high_index
      const lowIndex = smcData.reference_low_index
      console.log('[SMC Canvas] 索引检查:', {
        highIndex,
        lowIndex,
        klineDataLength: klineData.length,
        highIndexValid: highIndex !== undefined && highIndex >= 0 && highIndex < klineData.length,
        lowIndexValid: lowIndex !== undefined && lowIndex >= 0 && lowIndex < klineData.length
      })

      // 使用有效索引绘制
      const validHighIndex = (highIndex !== undefined && highIndex >= 0 && highIndex < klineData.length) ? highIndex : null
      const validLowIndex = (lowIndex !== undefined && lowIndex >= 0 && lowIndex < klineData.length) ? lowIndex : null

      if (validHighIndex !== null) {
        const highTime = klineData[validHighIndex]?.time
        if (highTime) {
          const x1 = timeScale.timeToCoordinate(highTime)
          const y = candleSeries.priceToCoordinate(smcData.reference_high)
          console.log('[SMC Canvas] 最高点坐标:', { x1, y, x2 })
          if (x1 !== null && y !== null) {
            drawStyledLine(x1, y, x2, y, refLineColor, refLineWidth, refLineStyle, refLineOpacity)
            console.log('[SMC Canvas] 最高点线已绘制')
          }
        } else {
          console.log('[SMC Canvas] 最高点无时间数据')
        }
      } else {
        console.log('[SMC Canvas] 最高点索引无效')
      }

      // 绘制最低点参考线
      if (validLowIndex !== null) {
        const lowTime = klineData[validLowIndex]?.time
        if (lowTime) {
          const x1 = timeScale.timeToCoordinate(lowTime)
          const y = candleSeries.priceToCoordinate(smcData.reference_low)
          console.log('[SMC Canvas] 最低点坐标:', { x1, y, x2 })
          if (x1 !== null && y !== null) {
            drawStyledLine(x1, y, x2, y, refLineColor, refLineWidth, refLineStyle, refLineOpacity)
            console.log('[SMC Canvas] 最低点线已绘制')
          }
        } else {
          console.log('[SMC Canvas] 最低点无时间数据')
        }
      } else {
        console.log('[SMC Canvas] 最低点索引无效')
      }
    }
  } else {
    console.log('[SMC Canvas] 参考线未绘制:', {
      show_reference: params.show_reference,
      has_reference_high: smcData.reference_high !== undefined,
      reference_high_value: smcData.reference_high
    })
  }

  // ==================== 4. BMS (Break of Market Structure) ====================
  console.log('[SMC Canvas] BMS 数据:', {
    bms: smcData.bms?.slice(-10),
    bms_levels: smcData.bms_levels?.slice(-10),
    bms_end_index: smcData.bms_end_index?.slice(-10)
  })

  if (params.show_bms !== false && smcData.bms) {
    const bmsCount = params.bms_count || 5
    const bmsList: any[] = []

    smcData.bms?.forEach((type: number, index: number) => {
      if (type === 0) return
      const level = smcData.bms_levels?.[index]
      const endIndex = smcData.bms_end_index?.[index]
      if (level === null || level === undefined || endIndex === undefined) {
        console.log(`[SMC Canvas] BMS ${index} 数据不完整:`, { type, level, endIndex })
        return
      }

      bmsList.push({
        index,     // 被突破的摆动点索引（起点）
        endIndex,  // 突破发生的 K 线索引（终点）
        level,     // 被突破的摆动点价格
        isBullish: type > 0
      })
    })

    console.log(`[SMC Canvas] 找到 ${bmsList.length} 个 BMS:`, bmsList)

    const recentBMS = bmsList.slice(-bmsCount)

    recentBMS.forEach((bms, i) => {
      // 起点：被突破的摆动点
      const startTime = klineData[bms.index]?.time
      // 终点：突破发生的 K 线
      const endTime = klineData[bms.endIndex]?.time
      if (!startTime || !endTime) return

      const x1 = timeScale.timeToCoordinate(startTime)
      const x2 = timeScale.timeToCoordinate(endTime)
      const y = candleSeries.priceToCoordinate(bms.level)

      if (x1 === null || x2 === null || y === null) return

      const color = colors.bms
      const label = 'BMS'

      // 水平线从被突破点画到突破发生的 K 线
      const bmsLineStyle = params.bms_line_style ?? 1
      const bmsOpacity = params.bms_opacity ?? 100
      drawStyledLine(x1, y, x2, y, color, params.bms_line_width || 1, bmsLineStyle, bmsOpacity)

      // 小方块标记在起点（被突破点）
      const boxSize = params.bms_box_size || 8
      smcCtx!.fillStyle = color
      smcCtx!.fillRect(x1 - boxSize/2, y - boxSize/2, boxSize, boxSize)

      // 白色边框
      smcCtx!.strokeStyle = '#FFFFFF'
      smcCtx!.lineWidth = 1
      smcCtx!.strokeRect(x1 - boxSize/2, y - boxSize/2, boxSize, boxSize)

      // 标签
      smcCtx!.fillStyle = color
      smcCtx!.font = 'bold 9px sans-serif'
      smcCtx!.textAlign = 'left'
      smcCtx!.textBaseline = 'middle'
      smcCtx!.fillText(label, x1 + boxSize/2 + 4, y)
    })
  }

  // ==================== 5. CHoCH (Change of Character) ====================
  if (params.show_choch !== false && smcData.choch) {
    const chochCount = params.choch_count || 5
    const chochList: any[] = []

    smcData.choch?.forEach((type: number, index: number) => {
      if (type === 0) return
      const level = smcData.choch_levels?.[index]
      const endIndex = smcData.choch_end_index?.[index]
      if (level === null || level === undefined || endIndex === undefined) return

      chochList.push({
        index,     // 被突破的摆动点索引（起点）
        endIndex,  // 突破发生的 K 线索引（终点）
        level,     // 被突破的摆动点价格
        isBullish: type > 0
      })
    })

    const recentChoCH = chochList.slice(-chochCount)

    recentChoCH.forEach(choch => {
      // 起点：被突破的摆动点
      const startTime = klineData[choch.index]?.time
      // 终点：突破发生的 K 线
      const endTime = klineData[choch.endIndex]?.time
      if (!startTime || !endTime) return

      const x1 = timeScale.timeToCoordinate(startTime)
      const x2 = timeScale.timeToCoordinate(endTime)
      const y = candleSeries.priceToCoordinate(choch.level)

      if (x1 === null || x2 === null || y === null) return

      const color = colors.choch
      const label = 'CHoCH'

      // 水平线从被突破点画到突破发生的 K 线
      const chochLineStyle = params.choch_line_style ?? 1
      const chochOpacity = params.choch_opacity ?? 100
      drawStyledLine(x1, y, x2, y, color, params.choch_line_width || 1, chochLineStyle, chochOpacity)

      // 菱形标记在起点（被突破点）
      const size = params.choch_diamond_size || 6
      smcCtx!.beginPath()
      smcCtx!.moveTo(x1, y - size)
      smcCtx!.lineTo(x1 + size, y)
      smcCtx!.lineTo(x1, y + size)
      smcCtx!.lineTo(x1 - size, y)
      smcCtx!.closePath()
      smcCtx!.fillStyle = color
      smcCtx!.fill()

      // 白色边框
      smcCtx!.strokeStyle = '#FFFFFF'
      smcCtx!.lineWidth = 1
      smcCtx!.stroke()

      // 标签
      smcCtx!.fillStyle = color
      smcCtx!.font = 'bold 9px sans-serif'
      smcCtx!.textAlign = 'left'
      smcCtx!.textBaseline = 'middle'
      smcCtx!.fillText(label, x1 + size + 4, y)
    })
  }
}

/**
 * 更新 SMC 指标显示
 * SMC 渲染规则：
 * 1. 使用 Canvas 叠加层绘制矩形区域
 * 2. 摆动点/BOS/CHoCH 仍然用 LineSeries
 */
const updateSMCIndicator = (smcData: any, klineData: any[]) => {
  console.log('[SMC] updateSMCIndicator 调用', {
    hasChart: !!chart,
    smcDataKeys: smcData ? Object.keys(smcData) : null,
    klineCount: klineData.length
  })
  if (!chart || !smcData) return

  console.log('[SMC] 开始渲染')

  // 缓存数据用于 Canvas 重绘（同时缓存 K 线数据！）
  smcDataRef.value = smcData
  chartDataRef.value = klineData  // 关键：缓存 K 线数据

  // 清除旧的 SMC series
  clearSMCSeries()

  // 创建 Canvas（如果还没有）
  if (!smcCanvas) {
    createSMCCanvas()
  }

  // 绘制 Canvas
  drawSMCCanvas()

  const customParams = indicatorParams.value['SMC'] || {}
  const showSwingPoints = customParams.show_swing_points !== false
  const showBMS = customParams.show_bms !== false
  const showCHoCH = customParams.show_choch !== false

  // 构建 K线数据索引映射
  const klineDataByTime = new Map<number, any>()
  klineData.forEach((bar: any) => {
    klineDataByTime.set(bar.time, bar)
  })

  // 所有 SMC 元素都通过 Canvas 绘制
  // 只需要保存数据并触发重绘
  smcSeriesRef.value = []  // 不再使用 LineSeries

  // 触发 Canvas 重绘
  requestAnimationFrame(drawSMCCanvas)

  console.log(`[SMC] 渲染完成 (Canvas模式)`)
}

/**
 * 清除 SMC Canvas 和 series
 */
const clearSMCSeries = () => {
  // 清除所有 LineSeries
  smcSeriesRef.value.forEach(series => {
    try {
      series?.setData([])
    } catch (e) {
      // 忽略错误
    }
  })
  smcSeriesRef.value = []

  // 清除 Canvas
  if (smcCtx && smcCanvas) {
    smcCtx.clearRect(0, 0, smcCanvas.width, smcCanvas.height)
  }
}

/**
 * 清除主图叠加指标
 */
const clearOverlayIndicator = (indicatorId: string) => {
  const seriesMap = overlaySeriesMap.get(indicatorId)
  if (!seriesMap) return

  // 清除所有series数据
  Object.values(seriesMap).forEach(series => {
    series?.setData([])
  })

  overlaySeriesMap.delete(indicatorId)
  console.log(`[叠加指标] ${indicatorId} 已清除`)
}

/**
 * 隐藏指标Pane
 */
const hideIndicatorPane = (indicatorId: string) => {
  const seriesMap = indicatorSeriesMap.get(indicatorId)

  if (!seriesMap) return

  // 清除所有series数据
  Object.values(seriesMap).forEach(series => {
    series?.setData([])
  })

  // 从map中移除
  indicatorSeriesMap.delete(indicatorId)

  // 移除对应的pane
  const paneIndex = getIndicatorPaneIndex(indicatorId)
  try {
    chart?.removePane(paneIndex)
    console.log(`[指标] ${indicatorId} pane ${paneIndex} 已移除`)
  } catch (e) {
    console.log(`[指标] ${indicatorId} pane ${paneIndex} 移除失败:`, e)
  }
}

/**
 * 切换指标显示
 */
const toggleIndicator = (indicator: string) => {
  const index = activeIndicators.value.indexOf(indicator)
  if (index > -1) {
    activeIndicators.value.splice(index, 1)
  } else {
    activeIndicators.value.push(indicator)
  }
  // 重新加载数据以获取指标
  loadKlineData()
}

/**
 * 打开指标参数设置
 */
const openIndicatorSettings = (indicatorId: string) => {
  console.log('[指标设置] 打开设置:', indicatorId)
  settingsIndicatorId.value = indicatorId
  // 获取当前参数（如果有）
  settingsParams.value = indicatorParams.value[indicatorId] ||
    getIndicatorConfig(indicatorId)?.defaultParams || {}
  showIndicatorSettings.value = true
}

/**
 * 确认指标参数设置
 */
const handleSettingsConfirm = (params: Record<string, any>) => {
  console.log('[指标设置] 确认参数:', settingsIndicatorId.value, params)
  const indicatorId = settingsIndicatorId.value
  const config = getIndicatorConfig(indicatorId)

  // 保存参数
  indicatorParams.value[indicatorId] = params

  // 如果是叠加指标（MA/BOLL），需要清除并重新初始化 series
  if (config && config.type === 'overlay') {
    console.log(`[指标设置] ${indicatorId} 是叠加指标，清除并重新初始化`)
    clearOverlayIndicator(indicatorId)
  }

  // 重新加载数据
  loadKlineData()
}

// 指标参数设置状态
const showIndicatorSettings = ref(false)
const settingsIndicatorId = ref('')
const settingsParams = ref<Record<string, any>>({})

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
 * 删除价格预警
 */
const removePriceAlert = (id: string) => {
  if (!userPriceAlerts) return

  userPriceAlerts.removeAlert(id)
  refreshPriceAlertsList()

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
  const currentQuote = dataStore.quotes[selectedStock.value]

  if (!currentQuote) return

  const currentPrice = realtimeQuote.quote.value.close || realtimeQuote.quote.value.price || 0
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
  refreshPriceAlertsList()

  // 清除本地存储
  if (selectedStock.value) {
    localStorage.removeItem(`price_alerts_${selectedStock.value}`)
  }
}

// 加载K线数据（优化版：优先加载K线，其他数据延后）
const isInitialLoad = ref(true)  // 标记是否为初始加载

const loadKlineData = async () => {
  if (!selectedStock.value) return

  loading.value = true
  let lastBarsCount = 0  // 记录本次加载的 bar 数量，供 setVisibleLogicalRange 使用

  try {
    // 确定需要请求的指标（合并独立指标和叠加指标）
    const allIndicators = [...activeIndicators.value, ...overlayIndicators.value]
    const indicatorsToFetch = allIndicators.length > 0 ? allIndicators : undefined
    console.log('[指标] 请求指标:', allIndicators)
    console.log('[SMC] overlayIndicators 包含 SMC:', overlayIndicators.value.includes('SMC'))

    // 准备指标参数配置
    const indicatorParamsConfig: Record<string, any> = {}

    // 遍历所有启用的指标，构建参数配置
    for (const indId of allIndicators) {
      const indParams = indicatorParams.value[indId] || {}

      // SKDJ 参数映射
      if (indId === 'SKDJ') {
        indicatorParamsConfig['SKDJ'] = {
          fastk_period: indParams.fastk_period ?? 9,
          slowk_period: indParams.slowk_period ?? 3,
          slowd_period: indParams.slowd_period ?? 3
        }
      }
      // KDJ 参数映射
      else if (indId === 'KDJ') {
        indicatorParamsConfig['KDJ'] = {
          fastk_period: indParams.kPeriod ?? 9,
          slowk_period: indParams.dPeriod ?? 3,
          slowd_period: indParams.jPeriod ?? 3
        }
      }
      // MACD 参数映射
      else if (indId === 'MACD') {
        indicatorParamsConfig['MACD'] = {
          fast_period: indParams.fast ?? 12,
          slow_period: indParams.slow ?? 26,
          signal_period: indParams.signal ?? 9
        }
      }
      // SMC 参数映射
      else if (indId === 'SMC') {
        indicatorParamsConfig['SMC'] = {
          swing_length: indParams.swing_length ?? 5,
          close_break: indParams.close_break ?? true,
          show_ob: indParams.show_ob ?? true,
          show_fvg: indParams.show_fvg ?? true,
          reference_period: indParams.reference_period ?? 34
        }
      }
      // TOPBOTTOM 参数映射
      else if (indId === 'TOPBOTTOM') {
        indicatorParamsConfig['TOPBOTTOM'] = {
          fastk_period: indParams.fastk_period ?? 9,
          slowk_period: indParams.slowk_period ?? 3,
          slowd_period: indParams.slowd_period ?? 3,
          rsi_period: indParams.rsi_period ?? 14,
          macd_fast: indParams.macd_fast ?? 12,
          macd_slow: indParams.macd_slow ?? 26,
          macd_signal: indParams.macd_signal ?? 9
        }
      }
    }

    console.log('[指标] 传递参数配置:', indicatorParamsConfig)

    // 第一步：优先只加载K线数据（最核心的）- 同时请求指标
    const klineRes = await fetchKline(
      selectedStock.value,
      currentTimeframe.value,
      800,
      adjustType.value,
      indicatorsToFetch,
      indicatorParamsConfig
    )

    // 保存指标数据
    if (klineRes.indicators) {
      // 转换扁平结构为嵌套结构（兼容后端返回的扁平格式）
      const indicators = klineRes.indicators
      const nestedIndicators: Record<string, any> = {}

      // 定义需要嵌套的指标组
      const indicatorGroups: Record<string, string[]> = {
        'SKDJ': ['sk', 'sd'],  // 通达信SKDJ没有SJ
        'KDJ': ['k', 'd', 'j'],
        'MACD': ['macd', 'signal', 'histogram'],
        'BOLL': ['upper', 'middle', 'lower'],
        'TOPBOTTOM': ['risk_value_34', 'risk_value_170', 'buy_signal', 'sell_signal']
      }

      // 检查是否为扁平结构（包含sk/sd/sj等键）
      const isFlatStructure = Object.keys(indicators).some(key =>
        ['sk', 'sd', 'sj', 'k', 'd', 'j'].includes(key.toLowerCase())
      )

      if (isFlatStructure) {
        // 扁平结构，需要转换为嵌套结构
        for (const [indicatorName, keys] of Object.entries(indicatorGroups)) {
          // 检查是否所有需要的键都存在
          if (keys.every(key => key in indicators)) {
            // 创建嵌套结构
            nestedIndicators[indicatorName] = {}
            keys.forEach(key => {
              nestedIndicators[indicatorName][key] = indicators[key]
            })
            // 从原始数据中移除已处理的键
            keys.forEach(key => delete indicators[key])
          }
        }
        // 合并剩余的指标（MA、RSI等已经是正确格式的）
        Object.assign(nestedIndicators, indicators)
        indicatorDataCache.value = nestedIndicators
      } else {
        // 已经是嵌套结构，直接使用
        indicatorDataCache.value = indicators
      }

      console.log('[指标] 收到指标数据:', Object.keys(indicatorDataCache.value))
      console.log('[指标] MA数据:', indicatorDataCache.value['MA'])
      console.log('[指标] SKDJ数据:', indicatorDataCache.value['SKDJ'])
    }

    // 处理K线数据
    if (klineRes.data && klineRes.data.length > 0) {
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const klineDataWithSeconds = klineRes.data
        .map((item: KlineItem) => {
          const ts = Number(item.time)
          const timeValue = Math.floor(ts / 1000)

          return {
            time: timeValue,
            open: Number(item.open),
            high: Number(item.high),
            low: Number(item.low),
            close: Number(item.close),
            volume: Number(item.volume)
          }
        })
        .filter((item): item is { time: number; open: number; high: number; low: number; close: number; volume: number } => item !== null)

      // 日线去重：同一天可能有本地(00:00 CST)和在线(15:00 CST)两条，保留后一条
      // 按日期去重（去掉时间部分）
      const deduped = isDaily
        ? Array.from(
            klineDataWithSeconds.reduce((map, item) => {
              // 将时间戳转换为当天的00:00:00作为key
              const dayKey = Math.floor(item.time / 86400) * 86400
              map.set(dayKey, item)  // 同一天后面覆盖前面
              return map
            }, new Map<number, typeof klineDataWithSeconds[0]>()).values()
          ).sort((a, b) => a.time - b.time)
        : klineDataWithSeconds.sort((a, b) => (a.time as number) - (b.time as number))

      candleSeries?.setData(deduped)
      lastBarsCount = deduped.length

      // 成交量数据与 deduped K线保持一致的时间戳
      const volumeData = deduped.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#ef535080' : '#26a69a80'
      }))
      volumeSeries?.setData(volumeData)

      // 先清除所有指标pane，再按需重建
      clearAllIndicatorPanes()

      // 处理所有独立指标（按顺序创建）
      activeIndicators.value.forEach(indicatorId => {
        const config = getIndicatorConfig(indicatorId)
        if (!config || config.type === 'overlay') return  // 跳过主图叠加指标

        // 保存指标数据
        if (klineRes.indicators?.[indicatorId]) {
          indicatorDataCache.value[indicatorId] = klineRes.indicators[indicatorId]
        }

        // 初始化pane并更新数据
        initIndicatorPane(indicatorId)
        updateIndicatorData(indicatorId, deduped)
      })

      // 处理主图叠加指标（MA/BOLL）
      overlayIndicators.value.forEach(indicatorId => {
        const config = getIndicatorConfig(indicatorId)
        if (!config || config.type !== 'overlay') return

        // 保存指标数据到缓存
        if (klineRes.indicators?.[indicatorId]) {
          indicatorDataCache.value[indicatorId] = klineRes.indicators[indicatorId]
        }

        // 初始化并更新数据
        initOverlayIndicator(indicatorId)
        updateOverlayData(indicatorId, deduped)
      })

      // 清除未选中的叠加指标
      overlaySeriesMap.forEach((_, indicatorId) => {
        if (!overlayIndicators.value.includes(indicatorId)) {
          clearOverlayIndicator(indicatorId)
        }
      })

      // K线加载完成，立即结束loading
      loading.value = false

      // 统一设置所有指标pane的高度（需要在所有pane创建完成后统一设置）
      const panes = chart?.panes()
      if (panes && panes.length > 1) {
        // 设置主图pane
        const mainPane = panes[0]
        mainPane.setStretchFactor(3)  // 主图占3份

        // 设置指标pane
        for (let i = 1; i < panes.length; i++) {
          const indicatorId = activeIndicators.value[i - 1]
          const savedHeight = indicatorPaneHeights.value[indicatorId]
          if (savedHeight) {
            panes[i].setStretchFactor(savedHeight)
            console.log(`[指标] 统一设置 ${indicatorId} pane高度: ${savedHeight}`)
          } else {
            panes[i].setStretchFactor(1)
          }
        }
      }

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
        const allSymbols = dataStore.watchlist.map(s => s.symbol)
        const indexSymbols = indices.value.map(i => i.code)

        // 并行加载快照、自选股、指数
        const [snapshotRes, batchRes, indexRes] = await Promise.all([
          fetchSnapshot(selectedStock.value),
          fetchSnapshotBatch(allSymbols),
          fetchSnapshotBatch(indexSymbols),
        ])

        // 更新当前股票快照（右侧详情面板）
        if (snapshotRes.data) {
          realtimeQuote.updateFromSnapshot(snapshotRes.data)
        }

        // 批量更新所有自选股的价格到 DataStore
        if (batchRes.data && batchRes.data.length > 0) {
          // 转换 QuoteSnapshot 到 Quote 格式，处理后端 change_pct 字段
          const quotes = batchRes.data.map((q: any) => {
            const symbol = q.symbol || q.code
            // 后端返回的字段是 change_pct，前端需要 change_percent
            const changePercent = q.change_percent !== undefined ? q.change_percent : q.change_pct
            return {
              symbol: symbol,
              name: q.name,
              price: q.price,
              change: q.change,
              change_percent: changePercent,
              open: q.open,
              high: q.high,
              low: q.low,
              close: q.prev_close,
              volume: q.volume,
              amount: q.amount,
              timestamp: q.timestamp || Date.now()
            }
          })
          console.log('[RealtimeQuotes] Updating DataStore quotes:', quotes)
          dataStore.updateQuotes(quotes)
          console.log('[RealtimeQuotes] After update, dataStore.quotes:', Object.keys(dataStore.quotes))
        }

        // 更新指数
        if (indexRes.data && indexRes.data.length > 0) {
          const indexMap = new Map(indexRes.data.map((q: any) => [q.symbol || q.code, q]))
          for (const idx of indices.value) {
            const q = indexMap.get(idx.code)
            if (q) {
              idx.price = q.price ? Number(q.price).toFixed(2) : '--'
              // 内联 getChangePct 实现
              idx.change = parseFloat(Number(q.change_pct ?? q.change_percent ?? 0).toFixed(2))
            }
          }
        }

        // 第三步：后台预加载其他自选股K线
        const otherStocks = dataStore.watchlist.filter(s => s.symbol !== selectedStock.value)
        if (otherStocks.length > 0) {
          const periodsToPreload = Array.from(new Set([
            currentTimeframe.value,
            '1m', '5m', '1d'  // 常用周期
          ]))
          const tasks = otherStocks.flatMap(stock =>
            periodsToPreload.map(period => ({
              symbol: stock.symbol,
              period,
              count: 300,
              adjustType: adjustType.value
            }))
          )
          klineBatch.preload(tasks, {
            concurrency: 3,
            delay: 100
          })
        }
      } catch (error) {
        console.error('后台加载数据失败:', error)
      }
    }, 100)  // 延迟100ms，让K线先渲染

  } catch (error) {
    console.error('加载K线失败:', error)
    loading.value = false
  }
}

// 监听指标变化，重新加载数据
watch(activeIndicators, (newVal, oldVal) => {
  const removed = oldVal.filter(id => !newVal.includes(id))
  const added = newVal.filter(id => !oldVal.includes(id))

  if (removed.length > 0 || added.length > 0) {
    // 先隐藏被移除的指标
    removed.forEach(id => hideIndicatorPane(id))
    // 重新加载数据
    loadKlineData()
  }
}, { deep: true })

// 监听主图叠加指标变化
watch(overlayIndicators, (newVal, oldVal) => {
  const removed = oldVal.filter(id => !newVal.includes(id))
  const added = newVal.filter(id => !oldVal.includes(id))

  if (removed.length > 0 || added.length > 0) {
    // 先清除被移除的叠加指标
    removed.forEach(id => clearOverlayIndicator(id))
    // 重新加载数据
    loadKlineData()
  }
}, { deep: true })

// ─────────────────────────────────────────────
// watch: 使用 useKlineData 的数据更新图表（新逻辑）
// ─────────────────────────────────────────────
watch(klineBars, (bars) => {
  if (!bars || bars.length === 0 || !candleSeries || !volumeSeries) return

  // 转换数据格式
  const chartData = bars.map(bar => ({
    time: bar.time,
    open: bar.open,
    high: bar.high,
    low: bar.low,
    close: bar.close,
    volume: bar.volume
  }))

  // 更新图表
  candleSeries.setData(chartData)
  chartDataRef.value = chartData  // 缓存 K 线数据用于 SMC Canvas 重绘

  // 成交量
  const volumeData = chartData.map(d => ({
    time: d.time,
    value: d.volume,
    color: d.close >= d.open ? '#ef535080' : '#26a69a80'
  }))
  volumeSeries.setData(volumeData)

  // 首次加载时设置显示范围
  if (isInitialLoad.value && chartData.length > 0) {
    const total = chartData.length
    chart?.timeScale().setVisibleLogicalRange({
      from: Math.max(0, total - 200),
      to: total - 1 + 10,
    })
    chart?.priceScale('right').applyOptions({ autoScale: true })
    setTimeout(() => {
      chart?.priceScale('right').applyOptions({ autoScale: false })
    }, 200)
    isInitialLoad.value = false
  }

  console.log('[RealtimeQuotes] useKlineData 更新图表:', bars.length, '根')

  // 更新所有已启用的指标
  activeIndicators.value.forEach(indicatorId => {
    const config = getIndicatorConfig(indicatorId)
    if (config && config.type !== 'overlay') {
      updateIndicatorData(indicatorId, chartData)
    }
  })
}, { deep: true })

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

/** 刷新快照数据：当前股票快照 + 自选股批量快照 + 指数（不含 K线） */
const refreshSnapshots = async () => {
  if (!selectedStock.value) return

  try {
    // 获取所有分组的所有股票（热数据库：所有列表里的股票都在后台更新）
    const allSymbols = dataStore.watchlistGroups.flatMap(g => g.stocks.map(s => s.symbol))

    // 确保当前选中的股票也在获取列表中
    if (selectedStock.value && !allSymbols.includes(selectedStock.value)) {
      allSymbols.unshift(selectedStock.value)
    }
    const indexSymbols = indices.value.map(i => i.code)
    console.log('[RealtimeQuotes] Fetching snapshots for allSymbols:', allSymbols)
    const [snapshotRes, batchRes, indexRes] = await Promise.all([
      fetchSnapshot(selectedStock.value),
      fetchSnapshotBatch(allSymbols),
      fetchSnapshotBatch(indexSymbols),
    ])

    console.log('[RealtimeQuotes] batchRes:', batchRes)
    console.log('[RealtimeQuotes] batchRes.data:', batchRes.data)
    console.log('[RealtimeQuotes] batchRes.data length:', batchRes.data?.length)

    // 更新当前股票快照（使用 realtimeQuote composable）
    if (snapshotRes.data) {
      realtimeQuote.updateFromSnapshot(snapshotRes.data)
    }

    // 批量更新所有自选股的价格到 DataStore
    if (batchRes.data && batchRes.data.length > 0) {
      // 转换 QuoteSnapshot 到 Quote 格式
      const quotes = batchRes.data.map((q: any) => {
        const symbol = q.symbol || q.code
        // 后端返回的字段是 change_pct，前端需要 change_percent
        const changePercent = q.change_percent !== undefined ? q.change_percent : q.change_pct
        console.log(`[RealtimeQuotes] 处理 quote: symbol=${symbol}, code=${q.code}, price=${q.price}, change_pct=${q.change_pct}, changePercent=${changePercent}`)
        return {
          symbol: symbol,
          name: q.name,
          price: q.price,
          change: q.change,
          change_percent: changePercent,
          open: q.open,
          high: q.high,
          low: q.low,
          close: q.prev_close,
          volume: q.volume,
          amount: q.amount,
          timestamp: q.timestamp || Date.now()
        }
      })
      console.log('[RealtimeQuotes] Updating DataStore quotes:', quotes)
      dataStore.updateQuotes(quotes)
      console.log('[RealtimeQuotes] After update, dataStore.quotes keys:', Object.keys(dataStore.quotes))
    }

    // 更新指数
    if (indexRes.data && indexRes.data.length > 0) {
      const indexMap = new Map(indexRes.data.map((q: any) => [q.symbol || q.code, q]))
      for (const idx of indices.value) {
        const q = indexMap.get(idx.code)
        if (q) {
          idx.price = q.price ? Number(q.price).toFixed(2) : '--'
          // 内联 getChangePct 实现
          idx.change = parseFloat(Number(q.change_pct ?? q.change_percent ?? 0).toFixed(2))
        }
      }
    }
  } catch (error) {
    console.error('刷新快照失败:', error)
    checkPriceAlerts()
  }
}

// 计算最大订单数量（用于进度条基准）
const maxOrderSize = computed(() => {
  const allSizes = [...realtimeQuote.asks.value, ...realtimeQuote.bids.value].map(item => item.size)
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

// 保存当前指标pane高度
function saveCurrentPaneHeights() {
  if (!chart) return

  const panes = chart.panes()
  if (panes.length <= 1) return  // 只有主图，无需保存

  // 遍历所有pane，从pane 1开始（pane 0是主图）
  const newHeights: Record<string, number> = { ...indicatorPaneHeights.value }
  let changed = false

  for (let i = 1; i < panes.length; i++) {
    const pane = panes[i]
    const indicatorId = activeIndicators.value[i - 1]  // 对应的指标
    if (pane && indicatorId) {
      try {
        const stretchFactor = pane.getStretchFactor()
        if (newHeights[indicatorId] !== stretchFactor) {
          newHeights[indicatorId] = stretchFactor
          changed = true
          console.log(`[指标] ${indicatorId} pane ${i} stretchFactor: ${stretchFactor}`)
        }
      } catch (e) {
        console.warn(`[指标] 获取pane ${i} 高度失败:`, e)
      }
    }
  }

  if (changed) {
    indicatorPaneHeights.value = newHeights  // 触发响应式更新
    console.log('[指标] pane高度已更新:', JSON.stringify(indicatorPaneHeights.value))
  }
}

const selectStock = (code: string) => {
  // 切换前保存当前pane高度
  saveCurrentPaneHeights()

  selectedStock.value = code
  isInitialLoad.value = true  // 切换股票时重新适应显示范围
  // 切换价格预警：清除旧的，加载新的
  if (userPriceAlerts) {
    userPriceAlerts.clearAll()
    userPriceAlerts.loadFromStorage(code)
    refreshPriceAlertsList()
  }

  // 加载快照数据
  realtimeQuote.fetchSnapshot(code)

  // 切换 WebSocket 连接到新股票
  connectKlineWs()

  // 立即加载新股票的历史数据（HTTP兜底，确保数据即时显示正确的周期）
  loadKlineData()
}

// 切换周期
const changeTimeframe = (tf: string) => {
  if (currentTimeframe.value === tf) return  // 周期没变，不处理

  // 切换前保存当前pane高度
  saveCurrentPaneHeights()

  console.log('[RealtimeQuotes] 切换周期:', currentTimeframe.value, '->', tf)
  currentTimeframe.value = tf
  isInitialLoad.value = true  // 切换周期时重新适应显示范围

  // 清空旧聚合器，创建新聚合器（确保干净的聚合状态）
  if (aggregator) {
    aggregator.clear()
  }
  aggregator = createKlineAggregator(tf as Timeframe)
  console.log('[RealtimeQuotes] 新建聚合器:', tf)

  // 切换周期时，用 HTTP API 加载历史数据（WebSocket 只推1分钟线，需要聚合）
  console.log('[RealtimeQuotes] 切换周期，加载历史数据:', tf)
  loadKlineData()

  // WebSocket 保持连接（始终推1分钟线），无需重连
  // 聚合器会自动将1分钟线聚合到目标周期
}

// 切换复权类型
const changeAdjustType = (type: string) => {
  adjustType.value = type
  isInitialLoad.value = true
  loadKlineData()
}

// 添加股票
// 市场状态缓存
const marketStatusCache = ref<MarketStatus | null>(null)

// 实时更新（根据市场状态动态调整刷新间隔）
const startRealtimeUpdate = async () => {
  const getStatus = async (): Promise<MarketStatus | null> => {
    try { return await fetchMarketStatus() } catch { return null }
  }

  const updateStatus = async () => {
    const status = await getStatus()
    marketStatusCache.value = status

    // 根据市场状态控制调度器
    if (scheduler) {
      if (status?.is_open) {
        scheduler.resume()
      } else {
        scheduler.pause()
      }
    }
  }

  // 初始获取状态
  await updateStatus()

  // 每30秒更新一次市场状态
  statusTimer = window.setInterval(updateStatus, 30000)

  // 初始化智能刷新调度器
  scheduler = initScheduler(async (stocks: string[]) => {
    // 批量刷新指定股票的快照数据
    if (stocks.length > 0) {
      try {
        const batchRes = await fetchSnapshotBatch(stocks)
        if (batchRes.data && batchRes.data.length > 0) {
          // 处理后端 change_pct 字段
          const quotes = batchRes.data.map((q: any) => {
            const symbol = q.symbol || q.code
            const changePercent = q.change_percent !== undefined ? q.change_percent : q.change_pct
            return {
              symbol: symbol,
              name: q.name,
              price: q.price,
              change: q.change,
              change_percent: changePercent,
              open: q.open,
              high: q.high,
              low: q.low,
              close: q.prev_close,
              volume: q.volume,
              amount: q.amount,
              timestamp: q.timestamp || Date.now()
            }
          })
          dataStore.updateQuotes(quotes)
        }
      } catch (error) {
        console.error('[RealtimeQuotes] 调度器刷新失败:', error)
      }
    }
  })

  // 调度器初始化后，根据当前市场状态暂停/恢复
  const currentStatus = marketStatusCache.value
  if (currentStatus && !currentStatus.is_open) {
    scheduler.pause()
  }

  // 为每个分组注册刷新任务
  const registerGroups = () => {
    if (!scheduler) return

    // 清除旧任务
    for (const group of dataStore.watchlistGroups) {
      scheduler.unregister(group.id)
    }

    // 注册新任务
    for (const group of dataStore.watchlistGroups) {
      if (group.stocks.length > 0) {
        // 如果 refreshInterval 未定义，使用默认值 3000ms
        const interval = group.refreshInterval ?? 3000
        scheduler.register({
          groupId: group.id,
          groupName: group.name,
          stocks: group.stocks.map(s => s.symbol),
          interval: interval,
          priority: interval < 5000 ? 1 : 2,
          lastRefresh: 0
        })
      }
    }

    console.log(`[RealtimeQuotes] 已注册 ${dataStore.watchlistGroups.length} 个分组到调度器`)
  }

  // 初始注册
  registerGroups()

  // 监听分组变化，重新注册刷新任务并加载迷你图
  watch(() => dataStore.watchlistGroups, () => {
    registerGroups()
    // 重新加载迷你图数据（支持新添加股票后自动加载）
    const allSymbols = dataStore.watchlistGroups.flatMap(g => g.stocks.map(s => s.symbol))
    miniCharts.loadMiniCharts(allSymbols)
  }, { deep: true })
}

onMounted(() => {
  nextTick(() => {
    initChart()

    // 加载迷你图数据（从所有分组收集股票）
    const allSymbols = dataStore.watchlistGroups.flatMap(g => g.stocks.map(s => s.symbol))
    miniCharts.loadMiniCharts(allSymbols)

    // 数据预热：启动时预加载标记为预热的分组数据
    dataStore.preheatData(async (symbols) => {
      if (symbols.length > 0) {
        try {
          const batchRes = await fetchSnapshotBatch(symbols)
          if (batchRes.data && batchRes.data.length > 0) {
            // 处理后端 change_pct 字段
            const quotes = batchRes.data.map((q: any) => {
              const symbol = q.symbol || q.code
              const changePercent = q.change_percent !== undefined ? q.change_percent : q.change_pct
              return {
                symbol: symbol,
                name: q.name,
                price: q.price,
                change: q.change,
                change_percent: changePercent,
                open: q.open,
                high: q.high,
                low: q.low,
                close: q.prev_close,
                volume: q.volume,
                amount: q.amount,
                timestamp: q.timestamp || Date.now()
              }
            })
            dataStore.updateQuotes(quotes)
            console.log(`[RealtimeQuotes] 预热完成: ${symbols.length} 只股票`)
          }
        } catch (error) {
          console.error('[RealtimeQuotes] 预热失败:', error)
        }
      }
    })

    startRealtimeUpdate()

    // 连接 WebSocket 并加载历史数据（所有周期：HTTP加载历史，WS实时更新）
    connectKlineWs()

    // 等待数据加载后，初始化选中股票
    setTimeout(() => {
      if (!selectedStock.value) {
        const activeGroup = dataStore.activeGroup
        let targetSymbol = ''

        if (activeGroup && activeGroup.stocks.length > 0) {
          targetSymbol = activeGroup.stocks[0].symbol
        } else if (dataStore.watchlistGroups.length > 0 && dataStore.watchlistGroups[0].stocks.length > 0) {
          targetSymbol = dataStore.watchlistGroups[0].stocks[0].symbol
        }

        if (targetSymbol) {
          console.log('[RealtimeQuotes] 初始化选中股票:', targetSymbol)
          selectStock(targetSymbol)
          // 选中股票后立即刷新快照数据
          setTimeout(() => refreshSnapshots(), 100)
        }
      }
    }, 200)
  })
})

onBeforeUnmount(() => {
  // 保存指标pane高度
  saveCurrentPaneHeights()

  if (statusTimer) clearInterval(statusTimer)
  if (scheduler) {
    scheduler.destroy()
    scheduler = null
  }
  disconnectKlineWs()  // 断开 WebSocket
  chartResizeObserver?.disconnect()
  if (priceAlertRafId !== null) {
    cancelAnimationFrame(priceAlertRafId)
  }
  // 清理指标系列
  indicatorSeriesMap.clear()
  overlaySeriesMap.clear()
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
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #d1d4dc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #2a2e39;
}

.stock-info-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stock-name-header {
  font-size: 13px;
  font-weight: 500;
  color: #d1d4dc;
}

.stock-code-header {
  font-size: 11px;
  font-weight: 400;
  color: #787b86;
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
  pointer-events: none;
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
  background: #1976D2;
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

/* 修改 lightweight-charts 窗口分割线颜色 - 使用全局样式 */
</style>

<style>
/* 修改 lightweight-charts 窗口分割线颜色 - 非scoped */
.pane {
  border-top: 1px solid rgba(42, 46, 57, 0.6) !important;
}

.pane:first-child {
  border-top: none !important;
}

/* 针对不同可能的类名 */
[class*="pane"] {
  border-top: 1px solid rgba(42, 46, 57, 0.6) !important;
}

[class*="pane"]:first-child {
  border-top: none !important;
}
</style>
