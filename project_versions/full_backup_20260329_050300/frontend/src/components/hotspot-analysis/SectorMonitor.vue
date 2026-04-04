<template>
  <div class="sector-monitor">
    <div class="panel-header">
      <h2>板块监控</h2>
      <div class="controls">
        <!-- 大小滑块 -->
        <div class="size-slider">
          <i class="fas fa-compress-alt"></i>
          <input
            type="range"
            v-model.number="cardSize"
            min="1"
            max="5"
            step="0.1"
            class="slider"
            title="调整卡片大小"
          />
          <i class="fas fa-expand-alt"></i>
          <span class="size-label">{{ getSizeLabel() }}</span>
        </div>
        <!-- 视图切换按钮 -->
        <div class="view-toggle">
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
            title="网格视图"
          >
            <i class="fas fa-th"></i>
          </button>
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
            title="列表视图"
          >
            <i class="fas fa-list"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="panel-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 网格视图 -->
      <div v-else-if="viewMode === 'grid'" class="sectors-grid" :style="gridStyle">
        <div
          v-for="sector in displayedSectors"
          :key="sector.id"
          v-memo="[sector.id, sector.changePercent, sector.stockCount]"
          class="sector-card"
          :class="`size-${Math.floor(cardSize)}`"
          :style="cardStyle"
          @click="$emit('sectorClick', sector)"
        >
          <!-- 最小尺寸：紧凑横向布局（显示名称+涨幅，横向排列） -->
          <template v-if="cardSize < 2">
            <div class="sector-compact">
              <div class="compact-info">
                <span class="compact-name">{{ sector.name }}</span>
                <span class="compact-divider">|</span>
                <span class="compact-stat">{{ sector.stockCount }}只</span>
              </div>
              <div class="compact-change" :class="getChangeClass(sector.changePercent)">
                <i class="fas" :class="sector.changePercent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'"></i>
                <span>{{ sector.changePercent }}%</span>
              </div>
            </div>
          </template>

          <!-- 小尺寸：名称、涨幅、股票数 -->
          <template v-else-if="cardSize < 3">
            <div class="sector-small">
              <div class="small-header">
                <h3 class="sector-name">{{ sector.name }}</h3>
                <div class="sector-change" :class="getChangeClass(sector.changePercent)">
                  {{ sector.changePercent }}%
                </div>
              </div>
              <div class="sector-stats">
                <span class="stat">{{ sector.stockCount }}只</span>
              </div>
            </div>
          </template>

          <!-- 中等尺寸：基本信息 + 龙头股 -->
          <template v-else-if="cardSize < 4">
            <div class="sector-medium">
              <div class="sector-header">
                <h3 class="sector-name">{{ sector.name }}</h3>
                <div class="sector-change" :class="getChangeClass(sector.changePercent)">
                  {{ sector.changePercent }}%
                </div>
              </div>
              <div class="sector-stats">
                <div class="stat-item">
                  <span class="stat-label">股票</span>
                  <span class="stat-value">{{ sector.stockCount }}</span>
                </div>
                <div class="stat-item" v-if="sector.amount">
                  <span class="stat-label">成交额</span>
                  <span class="stat-value">{{ formatAmount(sector.amount) }}亿</span>
                </div>
              </div>
              <div class="sector-stocks" v-if="sector.topStocks && sector.topStocks.length > 0">
                <div class="stocks-label">龙头股</div>
                <div class="top-stocks-list">
                  <div
                    v-for="(stock, index) in sector.topStocks.slice(0, 3)"
                    :key="stock.code"
                    class="top-stock-item"
                  >
                    <span class="stock-rank">{{ index + 1 }}</span>
                    <span class="stock-name">{{ stock.name }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 大尺寸：完整信息 + 更多龙头股 -->
          <template v-else-if="cardSize < 5">
            <div class="sector-large">
              <div class="sector-header">
                <h3 class="sector-name">{{ sector.name }}</h3>
                <div class="sector-change" :class="getChangeClass(sector.changePercent)">
                  {{ sector.changePercent }}%
                </div>
              </div>
              <div class="sector-stats">
                <div class="stat-item">
                  <span class="stat-label">股票数</span>
                  <span class="stat-value">{{ sector.stockCount }}</span>
                </div>
                <div class="stat-item" v-if="sector.amount">
                  <span class="stat-label">成交额</span>
                  <span class="stat-value">{{ formatAmount(sector.amount) }}亿</span>
                </div>
                <div class="stat-item" v-if="sector.price">
                  <span class="stat-label">指数</span>
                  <span class="stat-value">{{ sector.price.toFixed(0) }}</span>
                </div>
              </div>
              <div class="sector-stocks" v-if="sector.topStocks && sector.topStocks.length > 0">
                <div class="stocks-label">龙头股 TOP5</div>
                <div class="top-stocks-list">
                  <div
                    v-for="(stock, index) in sector.topStocks.slice(0, 5)"
                    :key="stock.code"
                    class="top-stock-item"
                  >
                    <span class="stock-rank">{{ index + 1 }}</span>
                    <span class="stock-name">{{ stock.name }}</span>
                    <span
                      class="stock-change"
                      :class="getChangeClass(stock.changePercent)"
                    >
                      {{ stock.changePercent }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 超大尺寸：完整信息 + 分时图 -->
          <template v-else>
            <div class="sector-extra-large">
              <div class="sector-header">
                <h3 class="sector-name">{{ sector.name }}</h3>
                <div class="sector-change" :class="getChangeClass(sector.changePercent)">
                  {{ sector.changePercent }}%
                </div>
              </div>
              <div class="sector-stats">
                <div class="stat-item">
                  <span class="stat-label">股票</span>
                  <span class="stat-value">{{ sector.stockCount }}</span>
                </div>
                <div class="stat-item" v-if="sector.amount">
                  <span class="stat-label">成交额</span>
                  <span class="stat-value">{{ formatAmount(sector.amount) }}亿</span>
                </div>
                <div class="stat-item" v-if="sector.price">
                  <span class="stat-label">指数</span>
                  <span class="stat-value">{{ sector.price.toFixed(0) }}</span>
                </div>
              </div>


              <!-- 走势图区域 -->
              <div class="sector-chart">
                <!-- 图表切换按钮 -->
                <div class="chart-toggle">
                  <button
                    class="chart-toggle-btn"
                    :class="{ active: chartType === 'daily' }"
                    @click.stop="chartType = 'daily'"
                  >
                    <i class="fas fa-chart-bar"></i>
                    日线
                  </button>
                  <button
                    class="chart-toggle-btn"
                    :class="{ active: chartType === 'minute' }"
                    @click.stop="chartType = 'minute'"
                  >
                    <i class="fas fa-chart-line"></i>
                    分时
                  </button>
                </div>

                <!-- 图表占位符 -->
                <div class="chart-placeholder">
                  <i class="fas fa-chart-area"></i>
                  <span>{{ chartType === 'daily' ? '日线走势图' : '分时走势图' }}</span>
                  <small>（图表组件开发中）</small>
                </div>
              </div>

              <div class="sector-stocks" v-if="sector.topStocks && sector.topStocks.length > 0">
                <div class="stocks-label">龙头股 TOP5</div>
                <div class="top-stocks-list">
                  <div
                    v-for="(stock, index) in sector.topStocks.slice(0, 5)"
                    :key="stock.code"
                    class="top-stock-item detailed"
                  >
                    <span class="stock-rank">{{ index + 1 }}</span>
                    <span class="stock-name">{{ stock.name }}</span>
                    <span
                      class="stock-change"
                      :class="getChangeClass(stock.changePercent)"
                    >
                      {{ stock.changePercent }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- 列表视图（保持原有功能） -->
      <div v-else class="sectors-list">
        <div
          v-for="sector in sectors"
          :key="sector.id"
          class="sector-list-item"
          @click="$emit('sectorClick', sector)"
        >
          <div class="sector-info">
            <h3 class="sector-name">{{ sector.name }}</h3>
            <div class="sector-meta">
              <span>{{ sector.stockCount }}只股票</span>
            </div>
          </div>

          <div class="sector-performance">
            <div
              class="sector-change"
              :class="getChangeClass(sector.changePercent)"
            >
              {{ sector.changePercent }}%
            </div>
          </div>

          <div class="sector-top-stocks">
            <div
              v-for="stock in sector.topStocks.slice(0, 3)"
              :key="stock.code"
              class="mini-stock"
            >
              {{ stock.name }}
            </div>
          </div>

          <div class="sector-action">
            <button class="expand-btn">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>

      <div v-if="!loading && sectors.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <p>暂无板块数据</p>
      </div>
    </div>

    <!-- 显示数量提示 -->
    <div class="display-info" v-if="viewMode === 'grid' && !loading">
      显示 {{ displayedSectors.length }} / {{ sectors.length }} 个板块
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Stock {
  code: string
  name: string
  changePercent: number
}

interface Sector {
  id: string
  name: string
  changePercent: number
  stockCount: number
  amount?: number
  price?: number
  topStocks: Stock[]
}

interface Props {
  sectors: Sector[]
  loading: boolean
}

const props = defineProps<Props>()

defineEmits<{
  sectorClick: [sector: Sector]
}>()

// 视图模式
const viewMode = ref<'grid' | 'list'>('grid')

// 卡片大小（1-5）
const cardSize = ref(2)
const chartType = ref<'daily' | 'minute'>('daily')  // 默认显示日线图

// 根据卡片大小计算显示的板块数量
const displayedSectors = computed(() => {
  const size = cardSize.value
  if (size < 2) {
    // 最小：显示50个
    return props.sectors.slice(0, 50)
  } else if (size < 3) {
    // 小：显示30个
    return props.sectors.slice(0, 30)
  } else if (size < 4) {
    // 中：显示20个
    return props.sectors.slice(0, 20)
  } else if (size < 5) {
    // 大：显示12个
    return props.sectors.slice(0, 12)
  } else {
    // 超大：显示8个
    return props.sectors.slice(0, 8)
  }
})

// 计算网格样式
const gridStyle = computed(() => {
  const size = cardSize.value
  let columns = 10

  if (size < 2) columns = 10  // 最小：10列
  else if (size < 3) columns = 6  // 小：6列
  else if (size < 4) columns = 5  // 中：5列
  else if (size < 5) columns = 4  // 大：4列
  else columns = 2  // 超大：2列

  return {
    'grid-template-columns': `repeat(${columns}, 1fr)`
  }
})

// 计算卡片样式
const cardStyle = computed(() => {
  const size = cardSize.value
  const baseHeight = 80
  const height = baseHeight * (0.8 + size * 0.4)

  return {
    'min-height': `${height}px`
  }
})

// 获取尺寸标签
const getSizeLabel = () => {
  const size = cardSize.value
  if (size < 2) return '紧凑'
  if (size < 3) return '小'
  if (size < 4) return '中'
  if (size < 5) return '大'
  return '详细'
}

// 格式化成交额
const formatAmount = (amount: number) => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2)
  }
  return amount.toFixed(2)
}

const getChangeClass = (change: number) => {
  if (change > 0) return 'rise'
  if (change < 0) return 'fall'
  return 'flat'
}
</script>

<style scoped>
.sector-monitor {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.panel-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 大小滑块 */
.size-slider {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: var(--bg-primary);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.size-slider i {
  font-size: 14px;
  color: var(--text-secondary);
}

.size-slider .slider {
  width: 150px;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}

.size-slider .slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  border: 2px solid #3b82f6;
}

.size-slider .slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 8px rgba(59, 130, 246, 0.4);
}

.size-slider .slider::-webkit-slider-thumb:active {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.size-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
  min-width: 40px;
  text-align: center;
  padding: 2px 8px;
  background: var(--bg-surface);
  border-radius: 8px;
}

/* Firefox slider thumb */
.size-slider .slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  border: 2px solid #3b82f6;
}

.size-slider .slider::-moz-range-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 8px rgba(59, 130, 246, 0.4);
}

/* 视图切换按钮 */
.view-toggle {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--bg-primary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.toggle-btn {
  padding: 6px 10px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.toggle-btn:hover {
  background: var(--bg-hover);
}

.toggle-btn.active {
  background: var(--primary-color);
  color: white;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 网格视图 */
.sectors-grid {
  display: grid;
  gap: 12px;
  padding-bottom: 40px;
}

.sector-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.sector-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

/* 最小尺寸 */
.sector-mini {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

/* 紧凑横向布局（最小尺寸） */
.sector-compact {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 10px;
}

.compact-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.compact-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.compact-divider {
  color: var(--border-color);
  font-size: 10px;
}

.compact-stat {
  font-size: 11px;
  color: var(--text-secondary);
}

.compact-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
  justify-content: center;
}

.compact-change i {
  font-size: 10px;
}

.mini-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-change {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

/* 小尺寸 */
.sector-small {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.small-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sector-name {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.sector-change {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
}

.sector-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.stat {
  font-size: 12px;
}

/* 中等尺寸 */
.sector-medium {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.sector-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.sector-stocks {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stocks-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.top-stocks-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.top-stock-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px;
  background: var(--bg-primary);
  border-radius: 4px;
}

.stock-rank {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 600;
}

.stock-name {
  flex: 1;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-change {
  font-weight: 600;
  font-size: 11px;
}

/* 大尺寸 */
.sector-large {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 超大尺寸 */
.sector-extra-large {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sector-chart {
  height: 140px;
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 8px;
  display: flex;
  flex-direction: column;
}

.chart-toggle {
  display: flex;
  gap: 4px;
  padding: 3px;
  background: var(--bg-surface);
  border-radius: 6px;
  margin-bottom: 8px;
  align-self: center;
}

.chart-toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 11px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.chart-toggle-btn:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.chart-toggle-btn.active {
  background: var(--primary-color);
  color: white;
}

.chart-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-secondary);
  background: var(--bg-surface);
  border-radius: 6px;
  border: 1px dashed var(--border-color);
}

.chart-placeholder i {
  font-size: 32px;
  opacity: 0.5;
}

.chart-placeholder small {
  font-size: 11px;
  opacity: 0.7;
}

.top-stock-item.detailed {
  padding: 6px 8px;
  font-size: 13px;
}

/* 列表视图 */
.sectors-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sector-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid var(--border-color);
}

.sector-list-item:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sector-info {
  flex: 1;
}

.sector-meta {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.sector-performance {
  text-align: right;
}

.sector-top-stocks {
  display: flex;
  gap: 8px;
}

.mini-stock {
  padding: 4px 8px;
  background: var(--bg-primary);
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.sector-action button {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--bg-primary);
  color: var(--text-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.sector-action button:hover {
  background: var(--primary-color);
  color: white;
}

/* 涨跌颜色 */
.rise {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}

.fall {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.flat {
  color: var(--text-secondary);
  background: var(--bg-hover);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 16px;
  color: var(--text-secondary);
}

.empty-state i {
  font-size: 48px;
  opacity: 0.5;
}

/* 显示信息 */
.display-info {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

/* 滚动条样式 */
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

.panel-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
