<template>
  <n-card class="system-monitor-card" hoverable>
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <span class="card-icon">📊</span>
          <span>系统监控</span>
        </div>
        <div class="card-actions">
          <n-dropdown trigger="hover" placement="bottom-end">
            <template #trigger>
              <n-button circle size="small" quaternary>
                <template #icon>
                  <n-icon><EllipsisVertical /></n-icon>
                </template>
              </n-button>
            </template>
            <template #dropdown>
              <n-doption @click="toggleLayout">
                <template #icon>
                  <n-icon><Grid /></n-icon>
                </template>
                切换布局
              </n-doption>
              <n-doption @click="exportData">
                <template #icon>
                  <n-icon><Download /></n-icon>
                </template>
                导出数据
              </n-doption>
            </template>
          </n-dropdown>
        </div>
      </div>
    </template>
    
    <div class="card-content">
      <!-- 布局选择 -->
      <div class="layout-selector">
        <n-tabs v-model:value="layoutType" type="segment" size="small">
          <n-tab-pane name="2x2" tab="2×2布局" />
          <n-tab-pane name="3x3" tab="3×3布局" />
          <n-tab-pane name="4x4" tab="4×4布局" />
          <n-tab-pane name="6x1" tab="6×1布局" />
          <n-tab-pane name="full" tab="全屏" />
        </n-tabs>
      </div>
      
      <!-- 股票监控网格 -->
      <div class="monitor-grid" :class="`layout-${layoutType}`">
        <div
          v-for="stock in monitorStocks"
          :key="stock.symbol"
          class="stock-monitor"
          @click="selectStock(stock)"
          :class="{ active: selectedStock?.symbol === stock.symbol }"
        >
          <div class="stock-header">
            <div class="stock-info">
              <div class="stock-symbol">{{ stock.symbol }}</div>
              <div class="stock-name">{{ stock.name }}</div>
            </div>
            <div class="stock-price" :class="getPriceChangeClass(stock.changePercent)">
              <div class="current-price">{{ stock.currentPrice.toFixed(2) }}</div>
              <div class="price-change">
                <span class="change-amount">{{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}</span>
                <span class="change-percent">({{ stock.changePercent >= 0 ? '+' : '' }}{{ (stock.changePercent * 100).toFixed(2) }}%)</span>
              </div>
            </div>
          </div>
          
          <!-- K线图 -->
          <div class="stock-chart">
            <TradingViewKLineUnified
              :symbol="stock.symbol"
              :stock-name="stock.name"
              :period="mapTimeframeToPeriod(selectedTimeframe)"
              :initial-data="stock.chartData"
              height="120px"
              :show-volume="false"
              :indicators="['ma5', 'ma10', 'ma20']"
            />
          </div>
          
          <!-- 技术指标 -->
          <div class="stock-indicators">
            <div class="indicator-item">
              <span class="indicator-label">MA5</span>
              <span class="indicator-value">{{ stock.ma5.toFixed(2) }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">MA10</span>
              <span class="indicator-value">{{ stock.ma10.toFixed(2) }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">MA20</span>
              <span class="indicator-value">{{ stock.ma20.toFixed(2) }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">RSI</span>
              <span class="indicator-value" :class="getRSIClass(stock.rsi)">{{ stock.rsi.toFixed(1) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 阶段走势分析 -->
      <div class="stage-analysis" v-if="selectedStock">
        <div class="analysis-header">
          <h4>{{ selectedStock.name }} 阶段走势分析</h4>
          <n-select
            v-model:value="selectedTimeframe"
            :options="timeframeOptions"
            size="small"
            style="width: 120px;"
          />
        </div>
        
        <div class="stage-tabs">
          <n-tabs v-model:value="analysisTab" type="card">
            <n-tab-pane name="trend" tab="趋势分析">
              <div class="trend-analysis">
                <div class="trend-item">
                  <div class="trend-label">短期趋势</div>
                  <div class="trend-value" :class="getTrendClass(selectedStock.shortTrend)">
                    {{ getTrendText(selectedStock.shortTrend) }}
                  </div>
                </div>
                <div class="trend-item">
                  <div class="trend-label">中期趋势</div>
                  <div class="trend-value" :class="getTrendClass(selectedStock.mediumTrend)">
                    {{ getTrendText(selectedStock.mediumTrend) }}
                  </div>
                </div>
                <div class="trend-item">
                  <div class="trend-label">长期趋势</div>
                  <div class="trend-value" :class="getTrendClass(selectedStock.longTrend)">
                    {{ getTrendText(selectedStock.longTrend) }}
                  </div>
                </div>
              </div>
            </n-tab-pane>
            
            <n-tab-pane name="support" tab="支撑阻力">
              <div class="support-resistance">
                <div class="level-item">
                  <div class="level-label">第一支撑</div>
                  <div class="level-value">{{ selectedStock.support1.toFixed(2) }}</div>
                </div>
                <div class="level-item">
                  <div class="level-label">第二支撑</div>
                  <div class="level-value">{{ selectedStock.support2.toFixed(2) }}</div>
                </div>
                <div class="level-item">
                  <div class="level-label">第一阻力</div>
                  <div class="level-value">{{ selectedStock.resistance1.toFixed(2) }}</div>
                </div>
                <div class="level-item">
                  <div class="level-label">第二阻力</div>
                  <div class="level-value">{{ selectedStock.resistance2.toFixed(2) }}</div>
                </div>
              </div>
            </n-tab-pane>
            
            <n-tab-pane name="volume" tab="量能分析">
              <div class="volume-analysis">
                <div class="volume-chart">
                  <BaseChart
                    :option="volumeChartOption"
                    height="200px"
                    width="100%"
                  />
                </div>
                <div class="volume-stats">
                  <div class="stat-item">
                    <div class="stat-label">平均量</div>
                    <div class="stat-value">{{ formatNumber(selectedStock.avgVolume) }}</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-label">量比</div>
                    <div class="stat-value" :class="getVolumeRatioClass(selectedStock.volumeRatio)">
                      {{ selectedStock.volumeRatio.toFixed(2) }}
                    </div>
                  </div>
                </div>
              </div>
            </n-tab-pane>
          </n-tabs>
        </div>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NIcon, NButton, NDropdown, NDropdownOption, NTabs, NTabPane, NSelect } from 'naive-ui'
import { EllipsisVertical, Download, Grid } from '@vicons/ionicons5'
import TradingViewKLineUnified from '../charts/TradingViewKLineUnified.vue'
import BaseChart from '../charts/BaseChart.vue'
import { formatNumber } from '@/utils/format'

interface StockData {
  symbol: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  chartData: any[]
  ma5: number
  ma10: number
  ma20: number
  rsi: number
  shortTrend: 'up' | 'down' | 'sideways'
  mediumTrend: 'up' | 'down' | 'sideways'
  longTrend: 'up' | 'down' | 'sideways'
  support1: number
  support2: number
  resistance1: number
  resistance2: number
  avgVolume: number
  volumeRatio: number
}

interface Props {
  onToggleLayout?: () => void
  onExportData?: () => void
  onSelectStock?: (stock: StockData) => void
}

const props = defineProps<Props>()

// 状态管理
const layoutType = ref('2x2')
const selectedStock = ref<StockData | null>(null)
const selectedTimeframe = ref('1d')
const analysisTab = ref('trend')

// 模拟股票数据
const monitorStocks = ref<StockData[]>([
  {
    symbol: '000001.SZ',
    name: '平安银行',
    currentPrice: 12.35,
    change: 0.15,
    changePercent: 0.0122,
    chartData: [],
    ma5: 12.28,
    ma10: 12.18,
    ma20: 12.05,
    rsi: 58.5,
    shortTrend: 'up',
    mediumTrend: 'up',
    longTrend: 'sideways',
    support1: 12.10,
    support2: 11.85,
    resistance1: 12.50,
    resistance2: 12.80,
    avgVolume: 12500000,
    volumeRatio: 1.2
  },
  {
    symbol: '600519.SH',
    name: '贵州茅台',
    currentPrice: 1825.00,
    change: -15.50,
    changePercent: -0.0084,
    chartData: [],
    ma5: 1835.20,
    ma10: 1838.50,
    ma20: 1842.30,
    rsi: 42.3,
    shortTrend: 'down',
    mediumTrend: 'down',
    longTrend: 'down',
    support1: 1810.00,
    support2: 1795.50,
    resistance1: 1840.00,
    resistance2: 1855.00,
    avgVolume: 8500000,
    volumeRatio: 0.8
  },
  {
    symbol: '000002.SZ',
    name: '万科A',
    currentPrice: 18.65,
    change: 0.35,
    changePercent: 0.0192,
    chartData: [],
    ma5: 18.52,
    ma10: 18.38,
    ma20: 18.15,
    rsi: 65.2,
    shortTrend: 'up',
    mediumTrend: 'up',
    longTrend: 'up',
    support1: 18.30,
    support2: 18.10,
    resistance1: 18.80,
    resistance2: 19.20,
    avgVolume: 21000000,
    volumeRatio: 1.5
  },
  {
    symbol: '600036.SH',
    name: '招商银行',
    currentPrice: 35.28,
    change: -0.72,
    changePercent: -0.0200,
    chartData: [],
    ma5: 35.65,
    ma10: 35.42,
    ma20: 35.18,
    rsi: 48.7,
    shortTrend: 'down',
    mediumTrend: 'sideways',
    longTrend: 'down',
    support1: 34.80,
    support2: 34.20,
    resistance1: 35.80,
    resistance2: 36.50,
    avgVolume: 18500000,
    volumeRatio: 0.9
  }
])

// 配置选项
const timeframeOptions = [
  { label: '1分钟', value: '1m' },
  { label: '5分钟', value: '5m' },
  { label: '15分钟', value: '15m' },
  { label: '30分钟', value: '30m' },
  { label: '1小时', value: '1h' },
  { label: '4小时', value: '4h' },
  { label: '日线', value: '1d' }
]

// 计算属性
const volumeChartOption = computed(() => {
  if (!selectedStock.value) return {}
  
  return {
    title: { text: '量能分析' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'time' },
    yAxis: { type: 'value' },
    series: [
      {
        name: '成交量',
        type: 'bar',
        data: selectedStock.value.chartData.map((item: any) => ({
          value: item.volume,
          itemStyle: {
            color: item.volume > selectedStock.value.avgVolume ? '#ef4444' : '#10b981'
          }
        }))
      }
    ]
  }
})

// 方法
const getPriceChangeClass = (changePercent: number) => {
  return changePercent > 0 ? 'positive' : 'negative'
}

const getRSIClass = (rsi: number) => {
  if (rsi < 30) return 'oversold'
  if (rsi > 70) return 'overbought'
  return 'normal'
}

const getTrendClass = (trend: string) => {
  return trend === 'up' ? 'trend-up' : trend === 'down' ? 'trend-down' : 'trend-sideways'
}

const getTrendText = (trend: string) => {
  const trendMap: Record<string, string> = {
    up: '上升趋势',
    down: '下降趋势',
    sideways: '横盘整理'
  }
  return trendMap[trend] || '未知'
}

const getVolumeRatioClass = (ratio: number) => {
  if (ratio > 1.2) return 'high'
  if (ratio < 0.8) return 'low'
  return 'normal'
}

const toggleLayout = () => {
  if (props.onToggleLayout) {
    props.onToggleLayout()
  }
}

const exportData = () => {
  if (props.onExportData) {
    props.onExportData()
  }
}

const selectStock = (stock: StockData) => {
  selectedStock.value = stock
  if (props.onSelectStock) {
    props.onSelectStock(stock)
  }
}

// 映射timeframe到period
const mapTimeframeToPeriod = (timeframe: string) => {
  const timeframeMap: Record<string, string> = {
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m',
    '1h': '60m',
    '4h': '240m',
    '1d': 'day'
  }
  return timeframeMap[timeframe] || 'day'
}

onMounted(() => {
  // 组件初始化
})
</script>

<style lang="scss" scoped>
.system-monitor-card {
  @include card-style;
  height: 700px;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .card-header {
    @include card-header;
    flex-shrink: 0;

    .card-title {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);

      .card-icon {
        font-size: var(--font-size-lg);
      }
    }

    .card-actions {
      margin-left: auto;
    }
  }

  .card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: var(--spacing-4);
    gap: var(--spacing-4);

    .layout-selector {
      margin-bottom: var(--spacing-4);
    }

    .monitor-grid {
      flex: 1;
      display: grid;
      gap: var(--spacing-2);
      overflow: auto;
      
      &.layout-2x2 {
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(2, 1fr);
      }
      
      &.layout-3x3 {
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: repeat(3, 1fr);
      }
      
      &.layout-4x4 {
        grid-template-columns: repeat(4, 1fr);
        grid-template-rows: repeat(4, 1fr);
      }
      
      &.layout-6x1 {
        grid-template-columns: repeat(6, 1fr);
        grid-template-rows: repeat(1, 1fr);
      }
      
      &.layout-full {
        grid-template-columns: 1fr;
        grid-template-rows: 1fr;
      }

      .stock-monitor {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: var(--border-radius-medium);
        padding: var(--spacing-3);
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        flex-direction: column;
        overflow: hidden;

        &:hover {
          background: rgba(15, 23, 42, 0.6);
          transform: translateY(-2px);
        }

        &.active {
          border-color: var(--primary-color);
          box-shadow: 0 0 0 2px rgba(var(--primary-color), 0.3);
        }

        .stock-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-2);

          .stock-info {
            .stock-symbol {
              font-weight: 600;
              color: var(--text-primary);
            }

            .stock-name {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
            }
          }

          .stock-price {
            text-align: right;

            .current-price {
              font-size: var(--font-size-lg);
              font-weight: 600;
              color: var(--text-primary);
            }

            .price-change {
              margin-top: var(--spacing-1);

              .change-amount {
                font-size: var(--font-size-sm);
                
                &.positive {
                  color: var(--success-color);
                }
                
                &.negative {
                  color: $error-color;
                }
              }

              .change-percent {
                font-size: var(--font-size-xs);
                color: var(--text-secondary);
                margin-left: var(--spacing-1);
              }
            }
          }
        }

        .stock-chart {
          flex: 1;
          min-height: 120px;
        }

        .stock-indicators {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--spacing-1);
          margin-top: var(--spacing-2);

          .indicator-item {
            display: flex;
            justify-content: space-between;
            padding: var(--spacing-1);
            background: rgba(0, 0, 0, 0.1);
            border-radius: var(--border-radius-sm)all;

            .indicator-label {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
            }

            .indicator-value {
              font-weight: 600;
              
              &.oversold {
                color: var(--success-color);
              }
              
              &.overbought {
                color: $error-color;
              }
              
              &.normal {
                color: var(--text-primary);
              }
            }
          }
        }
      }
    }

    .stage-analysis {
      margin-top: var(--spacing-4);
      padding: var(--spacing-3);
      background: rgba(15, 23, 42, 0.4);
      border-radius: var(--border-radius-medium);
      border: 1px solid rgba(148, 163, 184, 0.1);

      .analysis-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-3);

        h4 {
          margin: 0;
          color: var(--text-primary);
        }
      }

      .stage-tabs {
        .trend-analysis {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: var(--spacing-3);

          .trend-item {
            text-align: center;
            padding: var(--spacing-2);
            background: rgba(0, 0, 0, 0.1);
            border-radius: var(--border-radius-sm)all;

            .trend-label {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
              margin-bottom: var(--spacing-1);
            }

            .trend-value {
              font-weight: 600;
              
              &.trend-up {
                color: var(--success-color);
              }
              
              &.trend-down {
                color: $error-color;
              }
              
              &.trend-sideways {
                color: var(--warning-color);
              }
            }
          }
        }

        .support-resistance {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--spacing-3);

          .level-item {
            display: flex;
            justify-content: space-between;
            padding: var(--spacing-2);
            background: rgba(0, 0, 0, 0.1);
            border-radius: var(--border-radius-sm)all;

            .level-label {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
            }

            .level-value {
              font-weight: 600;
              color: var(--text-primary);
            }
          }
        }

        .volume-analysis {
          .volume-chart {
            margin-bottom: var(--spacing-3);
          }

          .volume-stats {
            display: flex;
            gap: var(--spacing-3);

            .stat-item {
              flex: 1;
              text-align: center;
              padding: var(--spacing-2);
              background: rgba(0, 0, 0, 0.1);
              border-radius: var(--border-radius-sm)all;

              .stat-label {
                font-size: var(--font-size-xs);
                color: var(--text-secondary);
                margin-bottom: var(--spacing-1);
              }

              .stat-value {
                font-weight: 600;
                
                &.high {
                  color: var(--success-color);
                }
                
                &.low {
                  color: $error-color;
                }
                
                &.normal {
                  color: var(--text-primary);
                }
              }
            }
          }
        }
      }
    }
  }
}
</style>