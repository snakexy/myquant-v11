<template>
  <div class="factor-analysis-correlation">
    <!-- 相关性配置面板 -->
    <div class="config-panel">
      <div class="config-header">
        <h3 class="config-title">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          {{ isZh ? '相关性配置' : 'Correlation Configuration' }}
        </h3>
      </div>

      <div class="config-body">
        <!-- 相关性方法选择 -->
        <div class="config-item">
          <label class="config-label">
            {{ isZh ? '相关性方法' : 'Correlation Method' }}
          </label>
          <div class="config-controls">
            <label class="radio-label">
              <input
                type="radio"
                v-model="correlationMethod"
                value="pearson"
                name="correlation-method"
              />
              <span>Pearson</span>
            </label>
            <label class="radio-label">
              <input
                type="radio"
                v-model="correlationMethod"
                value="spearman"
                name="correlation-method"
              />
              <span>Spearman</span>
            </label>
          </div>
          <div class="config-hint">
            {{ isZh ? 'Pearson: 线性相关性，Spearman: 秩相关性' : 'Pearson: Linear correlation, Spearman: Rank correlation' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 相关性热力图 -->
    <div class="chart-container">
      <FactorCorrelationHeatmap
        :task-id="taskId"
        :method="correlationMethod"
        :is-zh="isZh"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FactorCorrelationHeatmap from '../../../FactorCorrelationHeatmap.vue'

interface Props {
  taskId: string
  isZh: boolean
}

const props = defineProps<Props>()

// 相关性配置
const correlationMethod = ref<'pearson' | 'spearman'>('pearson')
</script>

<style scoped lang="scss">
.factor-analysis-correlation {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  overflow-y: auto;

  /* 相关性配置面板 */
  .config-panel {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;

    .config-header {
      padding: 16px 20px;
      border-bottom: 1px solid #e5e7eb;
      background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);

      .config-title {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 8px;

        .icon-sm {
          width: 20px;
          height: 20px;
        }
      }
    }

    .config-body {
      padding: 20px;

      .config-item {
        margin-bottom: 20px;

        &:last-child {
          margin-bottom: 0;
        }

        .config-label {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: #374151;
          margin-bottom: 10px;
        }

        .config-controls {
          display: flex;
          gap: 20px;
          margin-bottom: 8px;

          .radio-label {
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            font-size: 14px;
            color: #4b5563;

            input[type="radio"] {
              width: 18px;
              height: 18px;
              cursor: pointer;
              accent-color: #2962ff;

              &:hover {
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
              }
            }

            span {
              user-select: none;
            }

            &:hover {
              color: #2962ff;
            }
          }
        }

        .config-hint {
          font-size: 12px;
          color: #6b7280;
          line-height: 1.5;
        }
      }
    }
  }

  /* 图表容器 */
  .chart-container {
    flex: 1;
    min-height: 500px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    overflow: hidden;
  }
}

/* 滚动条样式 */
.factor-analysis-correlation::-webkit-scrollbar {
  width: 8px;
}

.factor-analysis-correlation::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.factor-analysis-correlation::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;

  &:hover {
    background: #94a3b8;
  }
}
</style>
