<template>
  <div class="realtime-rankings">
    <div class="panel-header">
      <h2>实时排行榜</h2>
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div class="panel-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else class="rankings-list">
        <div
          v-for="(stock, index) in currentRankings"
          :key="stock.code"
          class="stock-item"
          @click="$emit('stockClick', stock)"
        >
          <div class="stock-rank" :class="`rank-${index + 1}`">
            {{ index + 1 }}
          </div>

          <div class="stock-info">
            <div class="stock-name">{{ stock.name }}</div>
            <div class="stock-code">{{ stock.code }}</div>
          </div>

          <div class="stock-change-wrapper">
            <div class="stock-price" :class="getPriceClass(stock.changePercent)">
              <div class="price-value">{{ stock.changePercent }}%</div>
            </div>
            <div
              class="stock-current-price"
              :class="getPriceClass(stock.changePercent)"
              v-if="stock.current_price"
            >
              {{ stock.current_price.toFixed(2) }}元
            </div>
          </div>

          <div class="stock-volume">
            <div class="volume-value">{{ formatVolume(stock.amount) }}</div>
            <div class="volume-label">成交额</div>
          </div>

          <div class="stock-action">
            <button class="detail-btn">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>

        <div v-if="currentRankings.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>暂无数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Stock {
  code: string
  name: string
  changePercent: number
  current_price?: number  // 收盘价字段（匹配API）
  volume: number
  amount: number | string  // 成交额可能是数字或字符串（带"亿"单位）
  market: string
}

interface Props {
  rankings: {
    topRise: Stock[]
    topFall: Stock[]
    topAmount: Stock[]
  }
  loading: boolean
}

const props = defineProps<Props>()

defineEmits<{
  stockClick: [stock: Stock]
}>()

const activeTab = ref<'topRise' | 'topFall' | 'topAmount'>('topRise')

const tabs = [
  { key: 'topRise' as const, label: '涨幅榜', icon: 'fas fa-arrow-trend-up' },
  { key: 'topFall' as const, label: '跌幅榜', icon: 'fas fa-arrow-trend-down' },
  { key: 'topAmount' as const, label: '成交额榜', icon: 'fas fa-coins' }
]

const currentRankings = computed(() => {
  return props.rankings[activeTab.value] || []
})

const getPriceClass = (change: number) => {
  if (change > 0) return 'rise'
  if (change < 0) return 'fall'
  return 'flat'
}

const getChangeLabel = (change: number) => {
  if (change > 0) return '上涨'
  if (change < 0) return '下跌'
  return '平盘'
}

const formatVolume = (amount: number | undefined) => {
  if (!amount || amount === 0) return '--'
  if (amount >= 100000000) {
    return `${(amount / 100000000).toFixed(2)}亿`
  } else if (amount >= 10000) {
    return `${(amount / 10000).toFixed(2)}万`
  }
  return amount.toString()
}
</script>

<style scoped lang="scss">
.realtime-rankings {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-surface);
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-light);

  h2 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 16px 0;
  }

  .tabs {
    display: flex;
    gap: 8px;

    .tab-btn {
      flex: 1;
      padding: 10px 16px;
      background: transparent;
      border: 1px solid var(--border-light);
      border-radius: 8px;
      color: var(--text-secondary);
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;

      &:hover {
        background: var(--bg-elevated);
        border-color: var(--primary-color);
      }

      &.active {
        background: var(--primary-color);
        border-color: var(--primary-color);
        color: white;
      }
    }
  }
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  position: relative;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-color);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.rankings-list {
  .stock-item {
    display: flex;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-light);
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: var(--bg-elevated);
    }

    .stock-rank {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 700;
      margin-right: 12px;
      background: var(--bg-elevated);
      color: var(--text-secondary);

      &.rank-1 {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: white;
      }

      &.rank-2 {
        background: linear-gradient(135deg, #9ca3af, #6b7280);
        color: white;
      }

      &.rank-3 {
        background: linear-gradient(135deg, #cd7f32, #b87333);
        color: white;
      }
    }

    .stock-info {
      flex: 1;
      min-width: 0;

      .stock-name {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .stock-code {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }

    .stock-change-wrapper {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      margin-right: 16px;
      min-width: 80px;

      .stock-price {
        text-align: right;
        margin-bottom: 4px;

        .price-value {
          font-size: 18px;
          font-weight: 700;
        }
      }

      .stock-current-price {
        font-size: 12px;
        font-weight: 500;
        color: var(--text-secondary); // 默认灰色

        &.rise {
          color: #ef4444; // 红涨
        }

        &.fall {
          color: #22c55e; // 绿跌
        }

        &.flat {
          color: var(--text-secondary); // 平盘灰色
        }
      }

      .stock-price {
        &.rise .price-value {
          color: #ef4444;
        }

        &.fall .price-value {
          color: #22c55e;
        }

        &.flat .price-value {
          color: var(--text-primary);
        }
      }
    }

    .stock-price {
      text-align: right;
      margin-right: 16px;

      .price-value {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 2px;
      }

      .price-label {
        font-size: 11px;
        font-weight: 500;
      }

      &.rise {
        .price-value,
        .price-label {
          color: #ef4444;
        }
      }

      &.fall {
        .price-value,
        .price-label {
          color: #10b981;
        }
      }

      &.flat {
        .price-value,
        .price-label {
          color: var(--text-secondary);
        }
      }
    }

    .stock-volume {
      text-align: right;
      margin-right: 12px;

      .volume-value {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 2px;
      }

      .volume-label {
        font-size: 11px;
        color: var(--text-secondary);
      }
    }

    .stock-action {
      .detail-btn {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        border: 1px solid var(--border-light);
        background: transparent;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;

        &:hover {
          background: var(--primary-color);
          border-color: var(--primary-color);
          color: white;
        }
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-secondary);

  i {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  p {
    font-size: 14px;
  }
}
</style>
