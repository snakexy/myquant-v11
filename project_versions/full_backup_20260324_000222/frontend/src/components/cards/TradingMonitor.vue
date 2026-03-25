<template>
  <n-card class="trading-monitor-card" hoverable>
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <span class="card-icon">📈</span>
          <span>实盘交易监控</span>
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
              <n-doption @click="exportTradingLog">
                <template #icon>
                  <n-icon><Download /></n-icon>
                </template>
                导出交易记录
              </n-doption>
              <n-doption @click="refreshData">
                <template #icon>
                  <n-icon><Refresh /></n-icon>
                </template>
                刷新数据
              </n-doption>
            </template>
          </n-dropdown>
        </div>
      </div>
    </template>
    
    <div class="card-content">
      <!-- 交易概览 -->
      <div class="trading-overview">
        <div class="overview-item">
          <div class="item-label">今日盈亏</div>
          <div class="item-value" :class="getPNLClass(tradingOverview.todayPNL)">
            {{ formatCurrency(tradingOverview.todayPNL) }}
          </div>
        </div>
        <div class="overview-item">
          <div class="item-label">总盈亏</div>
          <div class="item-value" :class="getPNLClass(tradingOverview.totalPNL)">
            {{ formatCurrency(tradingOverview.totalPNL) }}
          </div>
        </div>
        <div class="overview-item">
          <div class="item-label">胜率</div>
          <div class="item-value">{{ (tradingOverview.winRate * 100).toFixed(1) }}%</div>
        </div>
        <div class="overview-item">
          <div class="item-label">交易次数</div>
          <div class="item-value">{{ tradingOverview.totalTrades }}</div>
        </div>
      </div>
      
      <!-- 时间框架选择 -->
      <div class="timeframe-selector">
        <n-tabs v-model:value="selectedTimeframe" type="segment" size="small">
          <n-tab-pane name="1m" tab="1分钟" />
          <n-tab-pane name="5m" tab="5分钟" />
          <n-tab-pane name="15m" tab="15分钟" />
          <n-tab-pane name="30m" tab="30分钟" />
          <n-tab-pane name="1h" tab="1小时" />
          <n-tab-pane name="4h" tab="4小时" />
          <n-tab-pane name="1d" tab="日线" />
        </n-tabs>
      </div>
      
      <!-- 预警系统 -->
      <div class="alert-system">
        <div class="alert-header">
          <h4>预警系统</h4>
          <n-button @click="showAlertConfig = true" size="small" type="primary">
            <template #icon>
              <n-icon><Settings /></n-icon>
            </template>
            配置预警
          </n-button>
        </div>
        <div class="alert-list">
          <div
            v-for="alert in activeAlerts"
            :key="alert.id"
            class="alert-item"
            :class="alert.level"
          >
            <div class="alert-icon">
              <n-icon :component="getAlertIcon(alert.type)" />
            </div>
            <div class="alert-content">
              <div class="alert-title">{{ alert.title }}</div>
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
            </div>
            <div class="alert-actions">
              <n-button @click="dismissAlert(alert.id)" size="tiny" quaternary>
                <template #icon>
                  <n-icon><Close /></n-icon>
                </template>
              </n-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 实时持仓 -->
      <div class="positions-section">
        <div class="section-header">
          <h4>实时持仓</h4>
          <n-button @click="refreshPositions" size="small" quaternary>
            <template #icon>
              <n-icon><Refresh /></n-icon>
            </template>
            刷新
          </n-button>
        </div>
        <div class="positions-grid">
          <div
            v-for="position in positions"
            :key="position.symbol"
            class="position-card"
          >
            <div class="position-header">
              <div class="symbol">{{ position.symbol }}</div>
              <div class="position-size">{{ position.size }}股</div>
            </div>
            <div class="position-details">
              <div class="detail-item">
                <span class="label">成本价:</span>
                <span class="value">{{ formatCurrency(position.avgCost) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">现价:</span>
                <span class="value" :class="getPriceChangeClass(position.currentPrice, position.avgCost)">
                  {{ formatCurrency(position.currentPrice) }}
                </span>
              </div>
              <div class="detail-item">
                <span class="label">盈亏:</span>
                <span class="value" :class="getPNLClass(position.pnl)">
                  {{ formatCurrency(position.pnl) }} ({{ (position.pnlPercent * 100).toFixed(2) }}%)
                </span>
              </div>
            </div>
            <div class="position-actions">
              <n-button @click="closePosition(position)" size="small" type="error">
                平仓
              </n-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 交易记录 -->
      <div class="trading-history">
        <div class="section-header">
          <h4>交易记录</h4>
          <n-button @click="showHistoryFilter = true" size="small" quaternary>
            <template #icon>
              <n-icon><Filter /></n-icon>
            </template>
            筛选
          </n-button>
        </div>
        <div class="history-table">
          <n-data-table
            :columns="historyColumns"
            :data="tradingHistory"
            :pagination="historyPagination"
            size="small"
            striped
            @update:page="handlePageChange"
          />
        </div>
      </div>
    </div>
    
    <!-- 预警配置弹窗 -->
    <n-modal v-model:show="showAlertConfig" preset="card" style="max-width: 600px;" title="预警配置">
      <div class="alert-config">
        <div class="config-section">
          <h4>价格预警</h4>
          <div class="config-item">
            <n-checkbox v-model:checked="alertConfig.priceAlert.enabled">
              启用价格预警
            </n-checkbox>
            <div v-if="alertConfig.priceAlert.enabled" class="price-settings">
              <div class="setting-item">
                <n-label>上涨幅度</n-label>
                <n-input-number
                  v-model:value="alertConfig.priceAlert.upPercent"
                  :min="0.1"
                  :max="50"
                  :step="0.1"
                  :precision="1"
                  suffix="%"
                />
              </div>
              <div class="setting-item">
                <n-label>下跌幅度</n-label>
                <n-input-number
                  v-model:value="alertConfig.priceAlert.downPercent"
                  :min="0.1"
                  :max="50"
                  :step="0.1"
                  :precision="1"
                  suffix="%"
                />
              </div>
            </div>
          </div>
        </div>
        
        <div class="config-section">
          <h4>技术指标预警</h4>
          <div class="config-item">
            <n-checkbox v-model:checked="alertConfig.indicatorAlert.enabled">
              启用技术指标预警
            </n-checkbox>
            <div v-if="alertConfig.indicatorAlert.enabled" class="indicator-settings">
              <div class="setting-item">
                <n-label>RSI超买</n-label>
                <n-input-number
                  v-model:value="alertConfig.indicatorAlert.rsiOversold"
                  :min="10"
                  :max="40"
                  :step="1"
                />
              </div>
              <div class="setting-item">
                <n-label>RSI超买</n-label>
                <n-input-number
                  v-model:value="alertConfig.indicatorAlert.rsiOverbought"
                  :min="60"
                  :max="90"
                  :step="1"
                />
              </div>
            </div>
          </div>
        </div>
        
        <div class="config-section">
          <h4>风险管理</h4>
          <div class="config-item">
            <n-checkbox v-model:checked="alertConfig.riskAlert.enabled">
              启用风险预警
            </n-checkbox>
            <div v-if="alertConfig.riskAlert.enabled" class="risk-settings">
              <div class="setting-item">
                <n-label>单日最大亏损</n-label>
                <n-input-number
                  v-model:value="alertConfig.riskAlert.maxDailyLoss"
                  :min="100"
                  :max="10000"
                  :step="100"
                  :precision="0"
                  prefix="¥"
                />
              </div>
              <div class="setting-item">
                <n-label>最大回撤</n-label>
                <n-input-number
                  v-model:value="alertConfig.riskAlert.maxDrawdown"
                  :min="0.05"
                  :max="0.5"
                  :step="0.01"
                  :precision="2"
                  suffix="%"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAlertConfig = false">取消</n-button>
          <n-button type="primary" @click="saveAlertConfig">保存配置</n-button>
        </n-space>
      </template>
    </n-modal>
    
    <!-- 历史记录筛选弹窗 -->
    <n-modal v-model:show="showHistoryFilter" preset="card" style="max-width: 500px;" title="交易记录筛选">
      <div class="history-filter">
        <div class="filter-item">
          <n-label>交易日期</n-label>
          <n-date-picker
            v-model:value="historyFilter.dateRange"
            type="daterange"
            clearable
          />
        </div>
        <div class="filter-item">
          <n-label>交易类型</n-label>
          <n-select
            v-model:value="historyFilter.tradeType"
            :options="tradeTypeOptions"
            clearable
          />
        </div>
        <div class="filter-item">
          <n-label>股票代码</n-label>
          <n-input
            v-model:value="historyFilter.symbol"
            placeholder="输入股票代码"
          />
        </div>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="resetFilter">重置</n-button>
          <n-button type="primary" @click="applyFilter">应用筛选</n-button>
        </n-space>
      </template>
    </n-modal>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NIcon, NButton, NDropdown, NDropdownOption, NTabs, NTabPane, NDataTable, NModal, NCheckbox, NLabel, NInputNumber, NDatePicker, NSelect, NInput, NSpace } from 'naive-ui'
import { EllipsisVertical, Download, Refresh, Settings, Close, Filter } from '@vicons/ionicons5'
import { formatCurrency, formatTime } from '@/utils/format'

interface TradingOverview {
  todayPNL: number
  totalPNL: number
  winRate: number
  totalTrades: number
}

interface Position {
  symbol: string
  size: number
  avgCost: number
  currentPrice: number
  pnl: number
  pnlPercent: number
}

interface Trade {
  id: string
  symbol: string
  type: 'buy' | 'sell'
  price: number
  quantity: number
  timestamp: Date
  pnl?: number
}

interface Alert {
  id: string
  type: 'price' | 'indicator' | 'risk'
  level: 'info' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
}

interface Props {
  onExportTradingLog?: () => void
  onRefreshData?: () => void
  onClosePosition?: (position: Position) => void
}

const props = defineProps<Props>()

// 状态管理
const selectedTimeframe = ref('1h')
const showAlertConfig = ref(false)
const showHistoryFilter = ref(false)
const tradingOverview = ref<TradingOverview>({
  todayPNL: 1250.50,
  totalPNL: 15420.30,
  winRate: 0.65,
  totalTrades: 42
})
const positions = ref<Position[]>([
  {
    symbol: '000001.SZ',
    size: 1000,
    avgCost: 12.50,
    currentPrice: 13.20,
    pnl: 700.00,
    pnlPercent: 0.056
  },
  {
    symbol: '600519.SH',
    size: 500,
    avgCost: 185.60,
    currentPrice: 182.30,
    pnl: -1650.00,
    pnlPercent: -0.089
  }
])
const activeAlerts = ref<Alert[]>([
  {
    id: '1',
    type: 'price',
    level: 'warning',
    title: '价格预警',
    message: '000001.SZ 上涨超过5%',
    timestamp: new Date(Date.now() - 10 * 60 * 1000)
  },
  {
    id: '2',
    type: 'indicator',
    level: 'info',
    title: '技术指标预警',
    message: '600519.SH RSI指标进入超买区域',
    timestamp: new Date(Date.now() - 30 * 60 * 1000)
  }
])
const tradingHistory = ref<Trade[]>([
  {
    id: '1',
    symbol: '000001.SZ',
    type: 'buy',
    price: 12.35,
    quantity: 1000,
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    pnl: 850.00
  },
  {
    id: '2',
    symbol: '600519.SH',
    type: 'sell',
    price: 188.50,
    quantity: 500,
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
    pnl: 1450.00
  }
])
const alertConfig = ref({
  priceAlert: {
    enabled: true,
    upPercent: 5.0,
    downPercent: 3.0
  },
  indicatorAlert: {
    enabled: true,
    rsiOversold: 30,
    rsiOverbought: 70
  },
  riskAlert: {
    enabled: true,
    maxDailyLoss: 2000,
    maxDrawdown: 0.15
  }
})
const historyFilter = ref({
  dateRange: null,
  tradeType: '',
  symbol: ''
})

// 配置选项
const tradeTypeOptions = [
  { label: '买入', value: 'buy' },
  { label: '卖出', value: 'sell' }
]

// 表格列配置
const historyColumns = computed(() => [
  { title: '股票代码', key: 'symbol', width: 100 },
  { title: '类型', key: 'type', width: 80, render: (row: Trade) => row.type === 'buy' ? '买入' : '卖出' },
  { title: '价格', key: 'price', width: 100, render: (row: Trade) => `¥${row.price.toFixed(2)}` },
  { title: '数量', key: 'quantity', width: 80 },
  { title: '盈亏', key: 'pnl', width: 100, render: (row: Trade) => row.pnl ? `¥${row.pnl.toFixed(2)}` : '-' },
  { title: '时间', key: 'timestamp', width: 150, render: (row: Trade) => formatTime(row.timestamp) }
])

const historyPagination = ref({
  page: 1,
  pageSize: 10,
  itemCount: 2,
  showSizePicker: true,
  pageSizes: [10, 20, 50]
})

// 方法
const getPNLClass = (pnl: number) => {
  return pnl > 0 ? 'positive' : 'negative'
}

const getPriceChangeClass = (current: number, cost: number) => {
  const change = (current - cost) / cost
  return change > 0 ? 'positive' : 'negative'
}

const getAlertIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    price: 'TrendingUpOutline',
    indicator: 'AnalyticsOutline',
    risk: 'WarningOutline'
  }
  return iconMap[type] || 'InformationCircleOutline'
}

const refreshData = () => {
  if (props.onRefreshData) {
    props.onRefreshData()
  }
}

const exportTradingLog = () => {
  if (props.onExportTradingLog) {
    props.onExportTradingLog()
  }
}

const closePosition = (position: Position) => {
  if (props.onClosePosition) {
    props.onClosePosition(position)
  }
}

const refreshPositions = () => {
  // 刷新持仓数据
}

const dismissAlert = (alertId: string) => {
  const index = activeAlerts.value.findIndex(alert => alert.id === alertId)
  if (index > -1) {
    activeAlerts.value.splice(index, 1)
  }
}

const saveAlertConfig = () => {
  // 保存预警配置
  showAlertConfig.value = false
}

const resetFilter = () => {
  historyFilter.value = {
    dateRange: null,
    tradeType: '',
    symbol: ''
  }
}

const applyFilter = () => {
  // 应用筛选条件
  showHistoryFilter.value = false
}

const handlePageChange = (page: number) => {
  historyPagination.value.page = page
}

onMounted(() => {
  // 组件初始化
})
</script>

<style lang="scss" scoped>
.trading-monitor-card {
  @include card-style;
  height: 600px;
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

    .trading-overview {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: var(--spacing-3);
      padding: var(--spacing-3);
      background: rgba(15, 23, 42, 0.4);
      border-radius: var(--border-radius-medium);
      margin-bottom: var(--spacing-4);

      .overview-item {
        text-align: center;

        .item-label {
          font-size: var(--font-size-xs);
          color: var(--text-secondary);
          margin-bottom: var(--spacing-1);
        }

        .item-value {
          font-size: var(--font-size-lg);
          font-weight: 600;
          
          &.positive {
            color: var(--success-color);
          }
          
          &.negative {
            color: $error-color;
          }
        }
      }
    }

    .timeframe-selector {
      margin-bottom: var(--spacing-4);
    }

    .alert-system {
      margin-bottom: var(--spacing-4);

      .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-3);

        h4 {
          margin: 0;
          color: var(--text-primary);
        }
      }

      .alert-list {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-2);

        .alert-item {
          display: flex;
          align-items: center;
          padding: var(--spacing-3);
          border-radius: var(--border-radius-medium);
          border-left: 4px solid;

          &.info {
            background: rgba(59, 130, 246, 0.1);
            border-left-color: var(--info-color);
          }

          &.warning {
            background: rgba(245, 158, 11, 0.1);
            border-left-color: var(--warning-color);
          }

          &.error {
            background: rgba(239, 68, 68, 0.1);
            border-left-color: $error-color;
          }

          .alert-icon {
            margin-right: var(--spacing-2);
            color: var(--warning-color);
          }

          .alert-content {
            flex: 1;

            .alert-title {
              font-weight: 600;
              margin-bottom: var(--spacing-1);
            }

            .alert-message {
              font-size: var(--font-size-sm);
              color: var(--text-secondary);
            }

            .alert-time {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
              margin-top: var(--spacing-1);
            }
          }

          .alert-actions {
            margin-left: var(--spacing-2);
          }
        }
      }
    }

    .positions-section {
      margin-bottom: var(--spacing-4);

      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-3);

        h4 {
          margin: 0;
          color: var(--text-primary);
        }
      }

      .positions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--spacing-3);

        .position-card {
          padding: var(--spacing-3);
          background: rgba(15, 23, 42, 0.4);
          border-radius: var(--border-radius-medium);
          border: 1px solid rgba(148, 163, 184, 0.1);

          .position-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-2);

            .symbol {
              font-weight: 600;
              color: var(--text-primary);
            }

            .position-size {
              font-size: var(--font-size-sm);
              color: var(--text-secondary);
            }
          }

          .position-details {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--spacing-2);
            margin-bottom: var(--spacing-2);

            .detail-item {
              display: flex;
              flex-direction: column;

              .label {
                font-size: var(--font-size-xs);
                color: var(--text-secondary);
                margin-bottom: var(--spacing-1);
              }

              .value {
                font-weight: 600;
                
                &.positive {
                  color: var(--success-color);
                }
                
                &.negative {
                  color: $error-color;
                }
              }
            }
          }

          .position-actions {
            display: flex;
            justify-content: flex-end;
          }
        }
      }
    }

    .trading-history {
      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-3);

        h4 {
          margin: 0;
          color: var(--text-primary);
        }
      }

      .history-table {
        border-radius: var(--border-radius-medium);
        overflow: hidden;
      }
    }
  }
}

.alert-config {
  .config-section {
    margin-bottom: var(--spacing-4);

    h4 {
      margin-bottom: var(--spacing-2);
      color: var(--text-primary);
    }

    .config-item {
      margin-bottom: var(--spacing-3);

      .price-settings,
      .indicator-settings,
      .risk-settings {
        margin-top: var(--spacing-2);
        padding-left: var(--spacing-4);
      }

      .setting-item {
        display: flex;
        align-items: center;
        margin-bottom: var(--spacing-2);
        gap: var(--spacing-2);

        .n-label {
          min-width: 100px;
        }
      }
    }
  }
}

.history-filter {
  .filter-item {
    margin-bottom: var(--spacing-3);

    .n-label {
      margin-bottom: var(--spacing-1);
    }
  }
}
</style>