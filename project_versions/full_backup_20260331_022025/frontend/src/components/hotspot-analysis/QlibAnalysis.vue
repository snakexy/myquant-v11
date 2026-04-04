<template>
  <div class="qlib-analysis">
    <div class="panel-header">
      <h2>Qlib深度分析</h2>
      <div class="status-badge" :class="{ active: hasData }">
        <i class="fas fa-chart-line"></i>
        {{ hasData ? '分析完成' : '等待选择' }}
      </div>
    </div>

    <div class="panel-content">
      <div v-if="!selectedStock" class="empty-state">
        <i class="fas fa-mouse-pointer"></i>
        <p>请从左侧或中间选择一只股票查看Qlib分析</p>
        <div class="tips">
          <div class="tip-item">
            <i class="fas fa-lightbulb"></i>
            <span>技术指标分析（MA、MACD、RSI等）</span>
          </div>
          <div class="tip-item">
            <i class="fas fa-lightbulb"></i>
            <span>因子评分（动量、估值、质量、成长）</span>
          </div>
          <div class="tip-item">
            <i class="fas fa-lightbulb"></i>
            <span>ML模型预测（LSTM、LightGBM）</span>
          </div>
        </div>
      </div>

      <div v-else-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在加载Qlib分析...</p>
      </div>

      <div v-else class="analysis-content">
        <!-- 股票基本信息 -->
        <div class="stock-header">
          <h3 class="stock-title">{{ selectedStock.name }}</h3>
          <div class="stock-code">{{ selectedStock.code }}</div>
          <div
            class="stock-change"
            :class="getChangeClass(selectedStock.changePercent)"
          >
            {{ selectedStock.changePercent }}%
          </div>
        </div>

        <!-- 技术指标 -->
        <div class="analysis-section">
          <h4 class="section-title">
            <i class="fas fa-chart-bar"></i>
            技术指标
          </h4>
          <div class="indicators-grid">
            <div class="indicator-item">
              <div class="indicator-label">MA5</div>
              <div class="indicator-value">--</div>
            </div>
            <div class="indicator-item">
              <div class="indicator-label">MA20</div>
              <div class="indicator-value">--</div>
            </div>
            <div class="indicator-item">
              <div class="indicator-label">MACD</div>
              <div class="indicator-value">--</div>
            </div>
            <div class="indicator-item">
              <div class="indicator-label">RSI</div>
              <div class="indicator-value">--</div>
            </div>
            <div class="indicator-item">
              <div class="indicator-label">KDJ</div>
              <div class="indicator-value">--</div>
            </div>
            <div class="indicator-item">
              <div class="indicator-label">布林带</div>
              <div class="indicator-value">--</div>
            </div>
          </div>
        </div>

        <!-- 因子评分 -->
        <div class="analysis-section">
          <h4 class="section-title">
            <i class="fas fa-star"></i>
            因子评分
          </h4>
          <div class="factors-list">
            <div class="factor-item">
              <div class="factor-name">动量因子</div>
              <div class="factor-bar">
                <div class="bar-fill" style="width: 0%"></div>
              </div>
              <div class="factor-score">--</div>
            </div>
            <div class="factor-item">
              <div class="factor-name">估值因子</div>
              <div class="factor-bar">
                <div class="bar-fill" style="width: 0%"></div>
              </div>
              <div class="factor-score">--</div>
            </div>
            <div class="factor-item">
              <div class="factor-name">质量因子</div>
              <div class="factor-bar">
                <div class="bar-fill" style="width: 0%"></div>
              </div>
              <div class="factor-score">--</div>
            </div>
            <div class="factor-item">
              <div class="factor-name">成长因子</div>
              <div class="factor-bar">
                <div class="bar-fill" style="width: 0%"></div>
              </div>
              <div class="factor-score">--</div>
            </div>
          </div>
        </div>

        <!-- ML预测 -->
        <div class="analysis-section">
          <h4 class="section-title">
            <i class="fas fa-robot"></i>
            ML模型预测
          </h4>
          <div class="prediction-box">
            <div class="prediction-item">
              <div class="prediction-label">LSTM预测</div>
              <div class="prediction-value">--</div>
            </div>
            <div class="prediction-item">
              <div class="prediction-label">LightGBM评分</div>
              <div class="prediction-value">--</div>
            </div>
          </div>
        </div>

        <!-- 综合评分 -->
        <div class="analysis-section highlight">
          <h4 class="section-title">
            <i class="fas fa-trophy"></i>
            综合评分
          </h4>
          <div class="total-score">
            <div class="score-value">--</div>
            <div class="score-label">分</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Stock {
  code: string
  name: string
  changePercent: number
}

interface Props {
  selectedStock: Stock | null
  loading: boolean
}

const props = defineProps<Props>()

const hasData = computed(() => props.selectedStock !== null)

const getChangeClass = (change: number) => {
  if (change > 0) return 'rise'
  if (change < 0) return 'fall'
  return 'flat'
}
</script>

<style scoped lang="scss">
.qlib-analysis {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-surface);
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;

  h2 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .status-badge {
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-elevated);
    color: var(--text-secondary);

    &.active {
      background: rgba(16, 185, 129, 0.1);
      color: #10b981;
    }
  }
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;

  i {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  p {
    font-size: 14px;
    margin-bottom: 24px;
  }

  .tips {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .tip-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--text-secondary);

      i {
        font-size: 16px;
        color: #f59e0b;
      }
    }
  }
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

.analysis-content {
  .stock-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: var(--bg-elevated);
    border-radius: 12px;
    margin-bottom: 20px;

    .stock-title {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0;
    }

    .stock-code {
      padding: 4px 12px;
      background: var(--bg-deep);
      border-radius: 6px;
      font-size: 12px;
      color: var(--text-secondary);
    }

    .stock-change {
      margin-left: auto;
      padding: 6px 16px;
      border-radius: 8px;
      font-size: 16px;
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

  .analysis-section {
    padding: 16px;
    background: var(--bg-elevated);
    border-radius: 12px;
    margin-bottom: 16px;

    &.highlight {
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(139, 92, 246, 0.1));
      border: 1px solid rgba(37, 99, 235, 0.2);
    }

    .section-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 16px 0;
      display: flex;
      align-items: center;
      gap: 8px;

      i {
        color: var(--primary-color);
      }
    }
  }

  .indicators-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;

    .indicator-item {
      padding: 12px;
      background: var(--bg-deep);
      border-radius: 8px;
      text-align: center;

      .indicator-label {
        font-size: 11px;
        color: var(--text-secondary);
        margin-bottom: 4px;
      }

      .indicator-value {
        font-size: 14px;
        font-weight: 700;
        color: var(--text-primary);
      }
    }
  }

  .factors-list {
    .factor-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 0;

      &:not(:last-child) {
        border-bottom: 1px solid var(--border-light);
      }

      .factor-name {
        width: 80px;
        font-size: 13px;
        color: var(--text-primary);
        font-weight: 500;
      }

      .factor-bar {
        flex: 1;
        height: 8px;
        background: var(--bg-deep);
        border-radius: 4px;
        overflow: hidden;

        .bar-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--primary-color), #8b5cf6);
          border-radius: 4px;
          transition: width 0.6s ease;
        }
      }

      .factor-score {
        width: 40px;
        text-align: right;
        font-size: 13px;
        font-weight: 700;
        color: var(--primary-color);
      }
    }
  }

  .prediction-box {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;

    .prediction-item {
      padding: 12px;
      background: var(--bg-deep);
      border-radius: 8px;

      .prediction-label {
        font-size: 11px;
        color: var(--text-secondary);
        margin-bottom: 4px;
      }

      .prediction-value {
        font-size: 14px;
        font-weight: 700;
        color: var(--text-primary);
      }
    }
  }

  .total-score {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 20px;

    .score-value {
      font-size: 48px;
      font-weight: 800;
      background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .score-label {
      font-size: 16px;
      color: var(--text-secondary);
      font-weight: 600;
    }
  }
}
</style>
