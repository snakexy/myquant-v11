<template>
  <section class="quality-section">
    <div class="section-header">
      <h2>数据质量监控</h2>
      <p>实时监控数据完整性和准确性</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="quality-grid">
      <div
        v-for="quality in qualities"
        :key="quality.id"
        class="quality-card"
        :class="quality.status"
      >
        <div class="quality-header">
          <h3>{{ quality.name }}</h3>
          <div class="quality-status" :class="quality.status">
            <span class="status-dot"></span>
            <span class="status-text">{{ quality.statusText }}</span>
          </div>
        </div>

        <div class="quality-metrics">
          <div class="metric-item">
            <span class="metric-label">完整度</span>
            <span class="metric-value">{{ quality.completeness }}%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">准确率</span>
            <span class="metric-value">{{ quality.accuracy }}%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">及时性</span>
            <span class="metric-value">{{ quality.timeliness }}%</span>
          </div>
        </div>

        <div class="quality-progress">
          <div class="progress-bar">
            <div
              class="progress-fill"
              :class="quality.status"
              :style="{ width: quality.completeness + '%' }"
            ></div>
          </div>
        </div>

        <div class="quality-actions">
          <button class="action-btn" @click="checkDetail(quality.id)">
            <i class="fas fa-search"></i>
            查看详情
          </button>
          <button class="action-btn" @click="fixIssue(quality.id)" v-if="quality.status !== 'healthy'">
            <i class="fas fa-wrench"></i>
            修复问题
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface QualityMetric {
  id: string
  name: string
  status: 'healthy' | 'warning' | 'error'
  statusText: string
  completeness: number
  accuracy: number
  timeliness: number
}

const loading = ref(true)
const qualities = ref<QualityMetric[]>([])

const loadData = () => {
  loading.value = true

  // 模拟数据质量检查结果
  setTimeout(() => {
    qualities.value = [
      {
        id: 'daily-data',
        name: '日线数据',
        status: 'healthy',
        statusText: '正常',
        completeness: 98.5,
        accuracy: 99.2,
        timeliness: 100
      },
      {
        id: 'minute-data',
        name: '分钟线数据',
        status: 'warning',
        statusText: '警告',
        completeness: 92.3,
        accuracy: 96.8,
        timeliness: 89.5
      },
      {
        id: 'tick-data',
        name: '分笔数据',
        status: 'healthy',
        statusText: '正常',
        completeness: 95.7,
        accuracy: 98.1,
        timeliness: 97.3
      },
      {
        id: 'financial-data',
        name: '财务数据',
        status: 'healthy',
        statusText: '正常',
        completeness: 99.1,
        accuracy: 99.8,
        timeliness: 95.2
      },
      {
        id: 'index-data',
        name: '指数数据',
        status: 'error',
        statusText: '异常',
        completeness: 78.5,
        accuracy: 85.3,
        timeliness: 72.1
      },
      {
        id: 'sector-data',
        name: '板块数据',
        status: 'healthy',
        statusText: '正常',
        completeness: 96.8,
        accuracy: 97.5,
        timeliness: 98.9
      }
    ]
    loading.value = false
  }, 500)
}

const checkDetail = (id: string) => {
  console.log('查看详情:', id)
  // TODO: 打开详情对话框
}

const fixIssue = (id: string) => {
  console.log('修复问题:', id)
  // TODO: 执行修复操作
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.quality-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 24px;

  h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  p {
    font-size: 14px;
    color: var(--text-secondary);
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--card-bg);
  border-radius: 12px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.quality-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.quality-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  &.healthy {
    border-left: 4px solid #10b981;
  }

  &.warning {
    border-left: 4px solid #f59e0b;
  }

  &.error {
    border-left: 4px solid #ef4444;
  }
}

.quality-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.quality-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  &.healthy {
    color: #10b981;

    .status-dot {
      background: #10b981;
      box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
    }
  }

  &.warning {
    color: #f59e0b;

    .status-dot {
      background: #f59e0b;
      box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
    }
  }

  &.error {
    color: #ef4444;

    .status-dot {
      background: #ef4444;
      box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
    }
  }
}

.quality-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.metric-item {
  text-align: center;

  .metric-label {
    display: block;
    font-size: 11px;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }

  .metric-value {
    display: block;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.quality-progress {
  margin-bottom: 16px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;

  &.healthy {
    background: linear-gradient(90deg, #10b981, #059669);
  }

  &.warning {
    background: linear-gradient(90deg, #f59e0b, #d97706);
  }

  &.error {
    background: linear-gradient(90deg, #ef4444, #dc2626);
  }
}

.quality-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary-color);
  }

  i {
    margin-right: 4px;
  }
}

@media (max-width: 768px) {
  .quality-grid {
    grid-template-columns: 1fr;
  }

  .quality-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
