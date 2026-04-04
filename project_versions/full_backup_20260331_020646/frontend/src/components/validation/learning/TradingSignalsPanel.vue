<template>
  <el-card class="signals-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📈 交易信号</span>
        <div class="actions">
          <el-tag v-if="signals.confidence > 0" :type="getConfidenceType(signals.confidence)" size="small">
            置信度: {{ (signals.confidence * 100).toFixed(1) }}%
          </el-tag>
          <el-button text @click="handleRefresh" :loading="loading">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
    </template>

    <div v-loading="loading" class="signals-content">
      <!-- 买入信号 -->
      <div class="signal-section buy">
        <h4 class="section-title">
          <el-icon color="#67c23a"><TrendCharts /></el-icon>
          买入信号
          <el-tag v-if="signals.buy.length > 0" type="success" size="small" effect="plain">
            {{ signals.buy.length }} 只
          </el-tag>
        </h4>
        <div class="signal-list">
          <el-tag
            v-for="signal in signals.buy"
            :key="signal"
            type="success"
            size="large"
            effect="dark"
            class="signal-tag"
          >
            {{ signal }}
          </el-tag>
          <el-empty
            v-if="signals.buy.length === 0 && !loading"
            description="暂无买入信号"
            :image-size="60"
          />
        </div>
      </div>

      <!-- 卖出信号 -->
      <div class="signal-section sell">
        <h4 class="section-title">
          <el-icon color="#f56c6c"><Bottom /></el-icon>
          卖出信号
          <el-tag v-if="signals.sell.length > 0" type="danger" size="small" effect="plain">
            {{ signals.sell.length }} 只
          </el-tag>
        </h4>
        <div class="signal-list">
          <el-tag
            v-for="signal in signals.sell"
            :key="signal"
            type="danger"
            size="large"
            effect="dark"
            class="signal-tag"
          >
            {{ signal }}
          </el-tag>
          <el-empty
            v-if="signals.sell.length === 0 && !loading"
            description="暂无卖出信号"
            :image-size="60"
          />
        </div>
      </div>

      <!-- 信号元信息 -->
      <div v-if="signals.timestamp" class="signal-meta">
        <div class="meta-item">
          <el-icon><Clock /></el-icon>
          <span>更新时间: {{ formatTime(signals.timestamp) }}</span>
        </div>
        <div class="meta-item">
          <el-icon><DataAnalysis /></el-icon>
          <span>使用模型: {{ signals.models_used || 0 }} 个</span>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!signals.timestamp && !loading"
        description="暂无交易信号，请先启动在线训练"
        :image-size="100"
      >
        <template #image>
          <el-icon :size="100" color="#c0c4cc">
            <TrendCharts />
          </el-icon>
        </template>
      </el-empty>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, TrendCharts, Bottom, Clock, DataAnalysis } from '@element-plus/icons-vue'
import { learningApi } from '@/api/modules/learning'

// Props
interface Props {
  modelId?: string
  autoRefresh?: boolean
  refreshInterval?: number // 毫秒
}

const props = withDefaults(defineProps<Props>(), {
  modelId: 'model_topk_dropout_v2',
  autoRefresh: true,
  refreshInterval: 30000 // 30秒
})

// State
const signals = ref<{
  buy: string[]
  sell: string[]
  timestamp: string
  confidence: number
  models_used: number
}>({
  buy: [],
  sell: [],
  timestamp: '',
  confidence: 0,
  models_used: 0
})

const loading = ref(false)
let refreshTimer: number | null = null

// 加载交易信号
const loadSignals = async () => {
  loading.value = true
  try {
    const response = await learningApi.getSignals(props.modelId)
    if (response.code === 200) {
      signals.value = response.data
    }
  } catch (error) {
    console.error('获取交易信号失败:', error)
    // 降级方案：使用模拟数据
    signals.value = {
      buy: ['000001.SZ', '600000.SH', '600519.SH'],
      sell: ['000858.SZ'],
      timestamp: new Date().toISOString(),
      confidence: 0.85,
      models_used: 1
    }
    ElMessage.warning('使用模拟数据')
  } finally {
    loading.value = false
  }
}

// 刷新
const handleRefresh = () => {
  loadSignals()
}

// 格式化时间
const formatTime = (timeStr: string): string => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

// 获取置信度标签类型
const getConfidenceType = (confidence: number): string => {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning'
  return 'info'
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (!props.autoRefresh) return

  refreshTimer = window.setInterval(() => {
    loadSignals()
  }, props.refreshInterval)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  loadSignals()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

// 暴露方法给父组件
defineExpose({
  refresh: loadSignals,
  getData: () => signals.value
})
</script>

<style scoped lang="scss">
.signals-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    .actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .signals-content {
    min-height: 200px;

    .signal-section {
      margin-bottom: 24px;
      padding: 16px;
      background-color: #f9fafb;
      border-radius: 8px;

      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 15px;
        font-weight: 600;
        color: #606266;
        margin: 0 0 16px 0;
      }

      .signal-list {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        min-height: 60px;
        align-items: center;

        .signal-tag {
          font-size: 14px;
          padding: 8px 16px;
          font-weight: 500;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
          }
        }

        .el-empty {
          flex: 1;
          padding: 20px 0;
        }
      }
    }

    .signal-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px;
      background-color: #f5f7fa;
      border-radius: 8px;
      border-top: 1px solid #e4e7ed;
      margin-top: 16px;

      .meta-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: #909399;

        .el-icon {
          font-size: 16px;
        }
      }
    }

    .el-empty {
      padding: 40px 20px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .signals-card {
    .signals-content {
      .signal-meta {
        flex-direction: column;
        gap: 12px;
        align-items: flex-start;
      }
    }
  }
}
</style>
