<template>
  <div class="dashboard-view">
    <div class="main-container">
      <div class="content-area">
        <!-- 左侧股票列表 -->
        <div class="panel watchlist-panel">
          <div class="panel-header">
            <span>{{ isZh ? '自选列表' : 'Watchlist' }}</span>
            <div class="panel-actions">
              <button class="panel-btn">+</button>
              <button class="panel-btn">⚙</button>
            </div>
          </div>
          <div class="stock-list">
            <div
              v-for="stock in watchlist"
              :key="stock.code"
              :class="['stock-item', { selected: selectedStock === stock.code }]"
              @click="selectStock(stock.code)"
            >
              <div class="stock-info">
                <div class="stock-code">{{ stock.code }}</div>
                <div class="stock-name">{{ isZh ? stock.nameZh : stock.name }}</div>
              </div>
              <div :class="['stock-price', stock.change >= 0 ? 'positive' : 'negative']">
                {{ stock.price.toFixed(2) }}
              </div>
              <div :class="['stock-change', stock.change >= 0 ? 'positive' : 'negative']">
                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
              </div>
            </div>
          </div>
        </div>

        <!-- 中间图表区域 -->
        <div class="chart-area">
          <div class="chart-toolbar">
            <button
              v-for="tf in timeframes"
              :key="tf"
              :class="['timeframe-btn', { active: currentTimeframe === tf }]"
              @click="currentTimeframe = tf"
            >
              {{ tf }}
            </button>
            <div class="chart-indicator">
              <button class="indicator-btn">MA</button>
              <button class="indicator-btn">EMA</button>
              <button class="indicator-btn">RSI</button>
              <button class="indicator-btn">MACD</button>
            </div>
          </div>
          <div class="chart-container">
            <!-- SVG 图表演示 -->
            <svg viewBox="0 0 800 400" class="chart-svg">
              <defs>
                <pattern id="grid" width="100" height="50" patternUnits="userSpaceOnUse">
                  <path d="M 100 0 L 0 0 0 50" fill="none" stroke="var(--tv-border)" stroke-width="1"/>
                </pattern>
              </defs>
              <rect width="800" height="400" fill="url(#grid)" />

              <!-- 价格线 -->
              <polyline fill="none" stroke="var(--tv-rise)" stroke-width="2"
                points="50,300 120,280 190,290 260,250 330,260 400,220 470,200 540,210 610,170 680,160 750,140"/>

              <!-- 填充区域 -->
              <polygon fill="rgba(38, 166, 154, 0.1)"
                points="50,400 50,300 120,280 190,290 260,250 330,260 400,220 470,200 540,210 610,170 680,160 750,140 750,400"/>

              <!-- MA线 -->
              <polyline fill="none" stroke="var(--tv-brand)" stroke-width="1.5" stroke-dasharray="5,5"
                points="50,310 120,295 190,285 260,270 330,275 400,250 470,240 540,230 610,200 680,190 750,180"/>

              <!-- 当前价格线 -->
              <line x1="50" y1="140" x2="780" y2="140" stroke="var(--tv-rise)" stroke-width="1" stroke-dasharray="4,4" opacity="0.5"/>
              <rect x="710" y="128" width="70" height="24" fill="var(--tv-rise)" rx="3"/>
              <text x="745" y="145" fill="white" font-size="12" text-anchor="middle" font-weight="600">1860.00</text>

              <!-- 坐标轴 -->
              <text x="15" y="300" fill="var(--tv-text-secondary)" font-size="10">1840</text>
              <text x="15" y="220" fill="var(--tv-text-secondary)" font-size="10">1850</text>
              <text x="15" y="140" fill="var(--tv-text-secondary)" font-size="10">1860</text>
              <text x="100" y="390" fill="var(--tv-text-secondary)" font-size="10">09:30</text>
              <text x="300" y="390" fill="var(--tv-text-secondary)" font-size="10">11:30</text>
              <text x="500" y="390" fill="var(--tv-text-secondary)" font-size="10">13:30</text>
              <text x="700" y="390" fill="var(--tv-text-secondary)" font-size="10">15:00</text>
            </svg>
          </div>
        </div>

        <!-- 右侧交易面板 -->
        <div class="panel trade-panel">
          <div class="panel-header">
            <span>{{ isZh ? '交易' : 'Trade' }}</span>
            <div class="panel-actions">
              <button class="panel-btn">📊</button>
            </div>
          </div>

          <div class="trade-section">
            <div class="price-display">
              <div class="current-price">1850.00</div>
              <div class="price-change">+42.50 (+2.35%)</div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">{{ isZh ? '五档盘口' : 'Order Book' }}</div>
            <div class="order-book">
              <div class="order-column">
                <div v-for="(ask, i) in asks" :key="'ask'+i" class="order-row sell">
                  <span>{{ isZh ? '卖' : 'Ask' }} {{ 5 - i }}</span>
                  <span class="order-price">{{ ask.price }}</span>
                  <span class="order-size">{{ ask.size }}</span>
                </div>
              </div>
              <div class="order-column">
                <div v-for="(bid, i) in bids" :key="'bid'+i" class="order-row buy">
                  <span>{{ isZh ? '买' : 'Bid' }} {{ i + 1 }}</span>
                  <span class="order-price">{{ bid.price }}</span>
                  <span class="order-size">{{ bid.size }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">{{ isZh ? '统计数据' : 'Statistics' }}</div>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">{{ isZh ? '成交量' : 'Volume' }}</div>
                <div class="info-value">3.2M</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '成交额' : 'Turnover' }}</div>
                <div class="info-value">5.9B</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '最高' : 'High' }}</div>
                <div class="info-value">1865.00</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '最低' : 'Low' }}</div>
                <div class="info-value">1820.00</div>
              </div>
            </div>
          </div>

          <div class="action-buttons">
            <button class="trade-btn buy">{{ isZh ? '买入' : 'BUY' }}</button>
            <button class="trade-btn sell">{{ isZh ? '卖出' : 'SELL' }}</button>
          </div>
        </div>
      </div>

      <!-- 底部状态栏 -->
      <div class="statusbar">
        <div class="statusbar-section">
          <span class="stock-name-display">贵州茅台 (600519)</span>
          <div class="statusbar-divider"></div>
          <div class="index-item">
            <span>{{ isZh ? '上证' : 'SSE' }}</span>
            <span class="index-value">3,245.67</span>
            <span class="index-change positive">+0.35%</span>
          </div>
          <div class="index-item">
            <span>{{ isZh ? '深证' : 'SZSE' }}</span>
            <span class="index-value">11,678.23</span>
            <span class="index-change negative">-0.12%</span>
          </div>
          <div class="statusbar-divider"></div>
          <span>{{ isZh ? '成交' : 'Vol' }}: 45.6B</span>
          <span style="margin-left: auto;">{{ isZh ? '实时行情' : 'Real-time' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/core/AppStore'

const appStore = useAppStore()
const isZh = computed(() => appStore.language === 'zh')

// 自选股列表
const watchlist = ref([
  { code: '600519', name: 'Kweichow Moutai', nameZh: '贵州茅台', price: 1850.00, change: 2.35 },
  { code: '000858', name: 'Wuliangye', nameZh: '五粮液', price: 152.80, change: 1.12 },
  { code: '600036', name: 'China Merchants Bank', nameZh: '招商银行', price: 35.60, change: -0.45 },
  { code: '000001', name: 'Ping An Bank', nameZh: '平安银行', price: 12.35, change: 0.65 },
  { code: '600276', name: 'Hengrui Medicine', nameZh: '恒瑞医药', price: 46.50, change: 1.53 },
  { code: '000333', name: 'Midea Group', nameZh: '美的集团', price: 57.80, change: -0.21 },
  { code: '601318', name: 'Ping An Insurance', nameZh: '中国平安', price: 49.20, change: 0.82 }
])

const selectedStock = ref('600519')

const selectStock = (code: string) => {
  selectedStock.value = code
}

const timeframes = ['1m', '5m', '15m', '1H', '4H', '1D', '1W']
const currentTimeframe = ref('4H')

const asks = ref([
  { price: '1852.00', size: 23 },
  { price: '1851.50', size: 45 },
  { price: '1851.00', size: 67 },
  { price: '1850.50', size: 89 },
  { price: '1850.00', size: 156 }
])

const bids = ref([
  { price: '1849.50', size: 203 },
  { price: '1849.00', size: 178 },
  { price: '1848.50', size: 145 },
  { price: '1848.00', size: 98 },
  { price: '1847.50', size: 56 }
])
</script>

<style scoped>
/* 使用全局配色 */
.dashboard-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  font-size: 13px;
  overflow: hidden;
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
  background: var(--border-color);
  overflow: hidden;
}

/* 面板 */
.panel {
  background: var(--bg-primary);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  background: var(--bg-secondary);
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
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
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.panel-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* 股票列表 */
.stock-list {
  flex: 1;
  overflow-y: auto;
}

.stock-item {
  display: grid;
  grid-template-columns: 1fr 70px 60px;
  gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.15s;
}

.stock-item:hover {
  background: var(--bg-secondary);
}

.stock-item.selected {
  background: var(--bg-tertiary);
  border-left: 2px solid var(--tv-brand);
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-code {
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
}

.stock-name {
  color: var(--text-secondary);
  font-size: 11px;
}

.stock-price {
  text-align: right;
  font-weight: 600;
  font-size: 13px;
}

.stock-price.positive { color: var(--tv-rise); }
.stock-price.negative { color: var(--tv-fall); }

.stock-change {
  text-align: right;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.stock-change.positive {
  background: rgba(38, 166, 154, 0.15);
  color: var(--tv-rise);
}

.stock-change.negative {
  background: rgba(239, 83, 80, 0.15);
  color: var(--tv-fall);
}

/* 图表区域 */
.chart-area {
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.chart-toolbar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 8px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.timeframe-btn {
  padding: 5px 10px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  border-radius: 3px;
  transition: all 0.15s;
}

.timeframe-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.timeframe-btn.active {
  color: var(--tv-brand);
  border-color: var(--tv-brand);
  background: rgba(41, 98, 255, 0.1);
}

.chart-indicator {
  margin-left: auto;
  display: flex;
  gap: 6px;
}

.indicator-btn {
  padding: 5px 10px;
  background: var(--bg-tertiary);
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 11px;
  border-radius: 3px;
  font-weight: 600;
}

.indicator-btn:hover {
  background: var(--tv-bg-hover);
}

.chart-container {
  flex: 1;
  position: relative;
  background: var(--bg-primary);
}

.chart-svg {
  width: 100%;
  height: 100%;
}

/* 交易面板 */
.trade-panel {
  display: flex;
  flex-direction: column;
}

.trade-section {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  font-size: 11px;
  color: var(--text-secondary);
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
  color: var(--tv-rise);
  line-height: 1;
}

.price-change {
  font-size: 13px;
  color: var(--tv-rise);
  margin-top: 4px;
  font-weight: 600;
}

.order-book {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.order-column {
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.order-row {
  display: grid;
  grid-template-columns: 1fr 1fr 45px;
  gap: 4px;
  padding: 6px 8px;
  font-size: 11px;
  border-bottom: 1px solid var(--border-color);
}

.order-row:last-child {
  border-bottom: none;
}

.order-row.buy { color: var(--tv-rise); }
.order-row.sell { color: var(--tv-fall); }

.order-price {
  text-align: right;
  font-weight: 600;
}

.order-size {
  text-align: right;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-item {
  background: var(--bg-secondary);
  padding: 10px 12px;
  border-radius: 4px;
}

.info-label {
  font-size: 10px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 16px;
}

.trade-btn {
  padding: 14px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}

.trade-btn.buy {
  background: var(--tv-rise);
  color: white;
}

.trade-btn.buy:hover {
  background: var(--success);
}

.trade-btn.sell {
  background: var(--tv-fall);
  color: white;
}

.trade-btn.sell:hover {
  background: var(--danger);
}

/* 底部状态栏 */
.statusbar {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 0 16px;
  display: flex;
  align-items: center;
  font-size: 11px;
  color: var(--text-secondary);
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
  background: var(--border-color);
}

.stock-name-display {
  color: var(--text-primary);
  font-weight: 600;
}

.index-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.index-value {
  color: var(--text-primary);
  font-weight: 600;
}

.index-change {
  font-weight: 600;
}

.index-change.positive { color: var(--tv-rise); }
.index-change.negative { color: var(--tv-fall); }

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
  background: var(--tv-bg-hover);
}
</style>
