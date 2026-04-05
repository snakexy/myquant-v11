<template>
  <div class="smart-recommendations">
    <div class="panel-header">
      <h2>
        <i class="fas fa-stars"></i>
        智能推荐
      </h2>
      <div class="recommendation-info">
        基于实时行情 + Qlib量化分析 + ML模型预测
      </div>
    </div>

    <div class="panel-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>分析中...</p>
      </div>

      <div v-else class="recommendations-grid">
        <!-- 超热股票 -->
        <div class="recommendation-section super-hot">
          <div class="section-header">
            <div class="section-icon">
              <i class="fas fa-fire"></i>
            </div>
            <div class="section-info">
              <h3>超热股票</h3>
              <p>前10名，强烈关注</p>
            </div>
            <div class="section-count">{{ recommendations.superHot.length }}</div>
          </div>

          <div class="stocks-list">
            <div
              v-for="stock in recommendations.superHot"
              :key="stock.code"
              class="stock-card"
              @click="$emit('stockClick', stock)"
            >
              <div class="stock-header">
                <div class="stock-name">{{ stock.name }}</div>
                <div
                  class="stock-change"
                  :class="getChangeClass(stock.changePercent)"
                >
                  {{ stock.changePercent }}%
                </div>
              </div>
              <div class="stock-meta">
                <span class="stock-code">{{ stock.code }}</span>
                <span class="stock-score">综合评分: --</span>
              </div>
            </div>

            <div v-if="recommendations.superHot.length === 0" class="empty-hint">
              暂无超热股票
            </div>
          </div>
        </div>

        <!-- 热门股票 -->
        <div class="recommendation-section hot">
          <div class="section-header">
            <div class="section-icon">
              <i class="fas fa-star"></i>
            </div>
            <div class="section-info">
              <h3>热门股票</h3>
              <p>11-50名，重点关注</p>
            </div>
            <div class="section-count">{{ recommendations.hot.length }}</div>
          </div>

          <div class="stocks-list">
            <div
              v-for="stock in recommendations.hot.slice(0, 10)"
              :key="stock.code"
              class="stock-card"
              @click="$emit('stockClick', stock)"
            >
              <div class="stock-header">
                <div class="stock-name">{{ stock.name }}</div>
                <div
                  class="stock-change"
                  :class="getChangeClass(stock.changePercent)"
                >
                  {{ stock.changePercent }}%
                </div>
              </div>
              <div class="stock-meta">
                <span class="stock-code">{{ stock.code }}</span>
              </div>
            </div>

            <div v-if="recommendations.hot.length === 0" class="empty-hint">
              暂无热门股票
            </div>
          </div>
        </div>

        <!-- 关注股票 -->
        <div class="recommendation-section watch">
          <div class="section-header">
            <div class="section-icon">
              <i class="fas fa-eye"></i>
            </div>
            <div class="section-info">
              <h3>关注股票</h3>
              <p>51-100名，观察等待</p>
            </div>
            <div class="section-count">{{ recommendations.watch.length }}</div>
          </div>

          <div class="stocks-list">
            <div
              v-for="stock in recommendations.watch.slice(0, 10)"
              :key="stock.code"
              class="stock-card"
              @click="$emit('stockClick', stock)"
            >
              <div class="stock-header">
                <div class="stock-name">{{ stock.name }}</div>
                <div
                  class="stock-change"
                  :class="getChangeClass(stock.changePercent)"
                >
                  {{ stock.changePercent }}%
                </div>
              </div>
              <div class="stock-meta">
                <span class="stock-code">{{ stock.code }}</span>
              </div>
            </div>

            <div v-if="recommendations.watch.length === 0" class="empty-hint">
              暂无关注股票
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Stock {
  code: string
  name: string
  changePercent: number
}

interface Props {
  recommendations: {
    superHot: Stock[]
    hot: Stock[]
    watch: Stock[]
  }
  loading: boolean
}

defineProps<Props>()

defineEmits<{
  stockClick: [stock: Stock]
}>()

const getChangeClass = (change: number) => {
  if (change > 0) return 'rise'
  if (change < 0) return 'fall'
  return 'flat'
}
</script>

<style scoped lang="scss">
.smart-recommendations {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-surface);
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  gap: 16px;

  h2 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;

    i {
      color: #f59e0b;
    }
  }

  .recommendation-info {
    font-size: 12px;
    color: var(--text-secondary);
    margin-left: auto;
  }
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

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  height: 100%;

  .recommendation-section {
    background: var(--bg-elevated);
    border-radius: 12px;
    border: 1px solid var(--border-light);
    overflow: hidden;
    display: flex;
    flex-direction: column;

    &.super-hot {
      border-color: rgba(239, 68, 68, 0.3);
      background: linear-gradient(180deg, rgba(239, 68, 68, 0.05) 0%, var(--bg-elevated) 100%);
    }

    &.hot {
      border-color: rgba(245, 158, 11, 0.3);
      background: linear-gradient(180deg, rgba(245, 158, 11, 0.05) 0%, var(--bg-elevated) 100%);
    }

    &.watch {
      border-color: rgba(59, 130, 246, 0.3);
      background: linear-gradient(180deg, rgba(59, 130, 246, 0.05) 0%, var(--bg-elevated) 100%);
    }

    .section-header {
      padding: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--border-light);

      .section-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: white;
      }

      .section-info {
        flex: 1;

        h3 {
          font-size: 15px;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 2px 0;
        }

        p {
          font-size: 11px;
          color: var(--text-secondary);
          margin: 0;
        }
      }

      .section-count {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: var(--bg-deep);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 700;
        color: var(--text-primary);
      }
    }

    .super-hot & .section-icon {
      background: linear-gradient(135deg, #ef4444, #dc2626);
    }

    .hot & .section-icon {
      background: linear-gradient(135deg, #f59e0b, #d97706);
    }

    .watch & .section-icon {
      background: linear-gradient(135deg, #3b82f6, #2563eb);
    }

    .stocks-list {
      flex: 1;
      overflow-y: auto;
      padding: 8px;

      .stock-card {
        padding: 12px;
        background: var(--bg-deep);
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .stock-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 6px;

          .stock-name {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
          }

          .stock-change {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 700;

            &.rise {
              background: rgba(239, 68, 68, 0.1);
              color: #ef4444;
            }

            &.fall {
              background: rgba(16, 185, 129, 0.1);
              color: #10b981;
            }

            &.flat {
              background: rgba(156, 163, 175, 0.1);
              color: #9ca3af;
            }
          }
        }

        .stock-meta {
          display: flex;
          justify-content: space-between;
          font-size: 11px;

          .stock-code {
            color: var(--text-secondary);
          }

          .stock-score {
            color: var(--primary-color);
            font-weight: 600;
          }
        }
      }

      .empty-hint {
        padding: 40px 20px;
        text-align: center;
        color: var(--text-secondary);
        font-size: 13px;
      }
    }
  }
}
</style>
