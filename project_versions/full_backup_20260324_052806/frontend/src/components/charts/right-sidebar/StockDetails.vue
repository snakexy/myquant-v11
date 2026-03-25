<template>
  <div class="stock-details">
    <div class="stock-header">
      <h3>{{ stockInfo.symbol }} {{ stockInfo.name }}</h3>
      <div class="current-price" :class="priceClass">
        {{ stockInfo.price.toFixed(2) }}
        <span class="price-change">{{ stockInfo.change >= 0 ? '+' : '' }}{{ stockInfo.change.toFixed(2) }}</span>
        <span class="price-percent">({{ stockInfo.changePercent >= 0 ? '+' : '' }}{{ stockInfo.changePercent.toFixed(2) }}%)</span>
      </div>
    </div>

    <div class="divider"></div>

    <div class="stock-stats">
      <div class="stat-item">
        <span class="stat-label">成交量</span>
        <span class="stat-value">{{ formatVolume(stockInfo.volume) }}</span>
      </div>

      <div class="stat-item">
        <span class="stat-label">平均成交量(30)</span>
        <span class="stat-value">{{ formatVolume(stockInfo.avgVolume30) }}</span>
      </div>

      <div class="stat-item">
        <span class="stat-label">市值</span>
        <span class="stat-value">{{ formatMarketCap(stockInfo.marketCap) }}</span>
      </div>

      <div class="stat-item expandable" @click="toggleKeyStats">
        <span class="stat-label">关键统计</span>
        <span class="expand-icon">{{ showKeyStats ? '▼' : '▶' }}</span>
      </div>

      <div v-if="showKeyStats" class="key-stats">
        <div class="key-stat-item">
          <span>下一份财报</span>
          <span>{{ stockInfo.nextEarnings }} ({{ stockInfo.daysToEarnings }}天后)</span>
        </div>
        <div class="key-stat-item">
          <span>52周最高</span>
          <span>{{ stockInfo.week52High.toFixed(2) }}</span>
        </div>
        <div class="key-stat-item">
          <span>52周最低</span>
          <span>{{ stockInfo.week52Low.toFixed(2) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface StockDetailInfo {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  avgVolume30: number
  marketCap: number
  nextEarnings: string
  daysToEarnings: number
  week52High: number
  week52Low: number
}

const props = defineProps<{
  stockInfo: StockDetailInfo
}>()

const showKeyStats = ref(false)

const priceClass = computed(() => {
  return props.stockInfo.changePercent > 0 ? 'up' :
         props.stockInfo.changePercent < 0 ? 'down' : 'flat'
})

const toggleKeyStats = () => {
  showKeyStats.value = !showKeyStats.value
}

const formatVolume = (volume: number) => {
  if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B'
  if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M'
  if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K'
  return volume.toString()
}

const formatMarketCap = (cap: number) => {
  if (cap >= 1e12) return (cap / 1e12).toFixed(2) + 'T'
  if (cap >= 1e8) return (cap / 1e8).toFixed(2) + 'B'
  return cap.toString()
}
</script>

<style scoped lang="scss">
.stock-details {
  width: 280px;
  height: 50%;
  background: #1e222d;
  border-left: 1px solid #2a2e39;
  border-top: 1px solid #2a2e39;
  padding: 16px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #1e222d;
  }

  &::-webkit-scrollbar-thumb {
    background: #363a45;
    border-radius: 3px;
  }
}

.stock-header {
  margin-bottom: 16px;

  h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
    color: #d1d4dc;
  }

  .current-price {
    font-size: 24px;
    font-weight: 700;

    .price-change,
    .price-percent {
      font-size: 14px;
      margin-left: 4px;
    }

    &.up { color: #10b981; }
    &.down { color: #ef4444; }
    &.flat { color: #d1d4dc; }
  }
}

.divider {
  height: 1px;
  background: #2a2e39;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;

  &.expandable {
    cursor: pointer;

    &:hover {
      background: #2a2e39;
      margin: 0 -16px;
      padding: 8px 16px;
    }
  }

  .stat-label {
    font-size: 12px;
    color: #787b86;
  }

  .stat-value {
    font-size: 12px;
    font-weight: 600;
    color: #d1d4dc;
  }

  .expand-icon {
    font-size: 10px;
    color: #787b86;
  }
}

.key-stats {
  margin-top: 8px;
  padding-left: 16px;
  border-left: 2px solid #2a2e39;
}

.key-stat-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 11px;

  span:first-child {
    color: #787b86;
  }

  span:last-child {
    color: #d1d4dc;
  }
}
</style>
