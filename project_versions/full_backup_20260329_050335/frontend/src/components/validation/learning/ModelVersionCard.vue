<template>
  <el-card class="version-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📦 模型版本</span>
        <el-button text @click="handleRefresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </template>

    <div v-if="loading && versions.length === 0" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="versions.length === 0" class="empty-container">
      <el-empty description="暂无版本信息" />
    </div>

    <div v-else class="version-list">
      <div
        v-for="version in versions"
        :key="version.versionId"
        class="version-item"
        :class="{ 'is-current': version.isCurrent }"
      >
        <div class="version-header">
          <div class="version-info">
            <span class="version-number">v{{ version.versionNumber }}</span>
            <el-tag v-if="version.isCurrent" type="success" size="small" effect="dark">
              当前版本
            </el-tag>
          </div>
          <div class="version-actions">
            <el-button
              v-if="!version.isCurrent"
              link
              type="primary"
              size="small"
              @click="handleRollback(version)"
            >
              回滚
            </el-button>
            <el-button
              link
              size="small"
              @click="handleViewDetails(version)"
            >
              详情
            </el-button>
          </div>
        </div>

        <div class="version-metrics">
          <div class="metric-item">
            <span class="metric-label">夏普比率</span>
            <span class="metric-value" :class="getMetricClass(version.performanceMetrics.sharpeRatio, 1.5)">
              {{ version.performanceMetrics.sharpeRatio.toFixed(2) }}
            </span>
          </div>
          <div class="metric-item">
            <span class="metric-label">总收益率</span>
            <span class="metric-value" :class="getMetricClass(version.performanceMetrics.totalReturnRate, 5)">
              {{ version.performanceMetrics.totalReturnRate.toFixed(2) }}%
            </span>
          </div>
          <div class="metric-item">
            <span class="metric-label">最大回撤</span>
            <span class="metric-value" :class="getDrawdownClass(version.performanceMetrics.maxDrawdown)">
              {{ version.performanceMetrics.maxDrawdown.toFixed(2) }}%
            </span>
          </div>
          <div class="metric-item">
            <span class="metric-label">胜率</span>
            <span class="metric-value" :class="getMetricClass(version.performanceMetrics.winRate, 50)">
              {{ version.performanceMetrics.winRate.toFixed(1) }}%
            </span>
          </div>
        </div>

        <div class="version-footer">
          <span class="create-time">{{ formatDate(version.createdAt) }}</span>
        </div>
      </div>
    </div>

    <!-- 版本详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="版本详情"
      width="600px"
    >
      <div v-if="selectedVersion" class="version-detail">
        <div class="detail-header">
          <h3>v{{ selectedVersion.versionNumber }}</h3>
          <el-tag v-if="selectedVersion.isCurrent" type="success">当前版本</el-tag>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">版本ID</span>
              <span class="value">{{ selectedVersion.versionId }}</span>
            </div>
            <div class="info-item">
              <span class="label">模型ID</span>
              <span class="value">{{ selectedVersion.modelId }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间</span>
              <span class="value">{{ formatDate(selectedVersion.createdAt) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>性能指标</h4>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-title">夏普比率</div>
              <div class="metric-value" :class="getMetricClass(selectedVersion.performanceMetrics.sharpeRatio, 1.5)">
                {{ selectedVersion.performanceMetrics.sharpeRatio.toFixed(2) }}
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-title">总收益率</div>
              <div class="metric-value" :class="getMetricClass(selectedVersion.performanceMetrics.totalReturnRate, 5)">
                {{ selectedVersion.performanceMetrics.totalReturnRate.toFixed(2) }}%
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-title">最大回撤</div>
              <div class="metric-value" :class="getDrawdownClass(selectedVersion.performanceMetrics.maxDrawdown)">
                {{ selectedVersion.performanceMetrics.maxDrawdown.toFixed(2) }}%
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-title">胜率</div>
              <div class="metric-value" :class="getMetricClass(selectedVersion.performanceMetrics.winRate, 50)">
                {{ selectedVersion.performanceMetrics.winRate.toFixed(1) }}%
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-title">盈亏比</div>
              <div class="metric-value" :class="getMetricClass(selectedVersion.performanceMetrics.profitLossRatio, 1.5)">
                {{ selectedVersion.performanceMetrics.profitLossRatio.toFixed(2) }}
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-title">波动率</div>
              <div class="metric-value">
                {{ selectedVersion.performanceMetrics.volatility.toFixed(2) }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="selectedVersion && !selectedVersion.isCurrent"
          type="primary"
          @click="handleRollback(selectedVersion)"
        >
          回滚到此版本
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { learningApi } from '@/api/modules/learning'
import type { ModelVersion } from '@/api/modules/learning'

// Props
interface Props {
  modelId: string
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: true,
  refreshInterval: 30000
})

// 版本列表
const versions = ref<ModelVersion[]>([])
const loading = ref(false)

// 详情弹窗
const detailDialogVisible = ref(false)
const selectedVersion = ref<ModelVersion | null>(null)

// 自动刷新定时器
let refreshTimer: number | null = null

// 加载版本列表
const loadVersions = async () => {
  loading.value = true
  try {
    const response = await learningApi.getModelVersions(props.modelId, 10)
    if (response.code === 200) {
      versions.value = response.data
    }
  } catch (error) {
    console.error('加载版本列表失败:', error)
    // 降级方案：使用默认版本数据
    versions.value = [
      {
        versionId: 'v_003',
        modelId: props.modelId,
        versionNumber: 3,
        createdAt: new Date().toISOString(),
        performanceMetrics: {
          sharpeRatio: 1.85,
          totalReturn: 150000,
          totalReturnRate: 15.0,
          maxDrawdown: 12.5,
          winRate: 58.0,
          profitLossRatio: 1.8,
          volatility: 15.2
        },
        isCurrent: true
      },
      {
        versionId: 'v_002',
        modelId: props.modelId,
        versionNumber: 2,
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        performanceMetrics: {
          sharpeRatio: 1.65,
          totalReturn: 120000,
          totalReturnRate: 12.0,
          maxDrawdown: 15.8,
          winRate: 55.0,
          profitLossRatio: 1.6,
          volatility: 16.5
        },
        isCurrent: false
      },
      {
        versionId: 'v_001',
        modelId: props.modelId,
        versionNumber: 1,
        createdAt: new Date(Date.now() - 172800000).toISOString(),
        performanceMetrics: {
          sharpeRatio: 1.42,
          totalReturn: 100000,
          totalReturnRate: 10.0,
          maxDrawdown: 18.2,
          winRate: 52.0,
          profitLossRatio: 1.4,
          volatility: 17.8
        },
        isCurrent: false
      }
    ]
    ElMessage.warning('使用默认版本数据')
  } finally {
    loading.value = false
  }
}

// 查看详情
const handleViewDetails = (version: ModelVersion) => {
  selectedVersion.value = version
  detailDialogVisible.value = true
}

// 回滚版本
const handleRollback = async (version: ModelVersion) => {
  try {
    await ElMessageBox.confirm(
      `确定要回滚到 v${version.versionNumber} 吗？当前版本将被替换。`,
      '回滚确认',
      {
        confirmButtonText: '确定回滚',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await learningApi.rollbackModel(props.modelId, version.versionId)
    if (response.code === 200) {
      ElMessage.success('已回滚到 v' + version.versionNumber)
      detailDialogVisible.value = false
      await loadVersions()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('回滚失败:', error)
      ElMessage.error('回滚失败')
    }
  }
}

// 刷新
const handleRefresh = () => {
  loadVersions()
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 指标样式（越大越好）
const getMetricClass = (value: number, threshold: number): string => {
  if (value >= threshold) return 'positive'
  if (value >= threshold * 0.8) return 'neutral'
  return 'negative'
}

// 回撤样式（越小越好）
const getDrawdownClass = (value: number): string => {
  if (value <= 10) return 'positive'
  if (value <= 20) return 'neutral'
  return 'negative'
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (props.autoRefresh && props.refreshInterval > 0) {
    refreshTimer = window.setInterval(() => {
      loadVersions()
    }, props.refreshInterval)
  }
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
  loadVersions()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

// 暴露方法
defineExpose({
  refresh: loadVersions
})
</script>

<style scoped lang="scss">
.version-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .loading-container,
  .empty-container {
    padding: 40px 0;
  }

  .version-list {
    .version-item {
      padding: 16px;
      margin-bottom: 12px;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      transition: all 0.3s;

      &:last-child {
        margin-bottom: 0;
      }

      &:hover {
        border-color: #409eff;
        box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
      }

      &.is-current {
        background: linear-gradient(135deg, rgba(103, 194, 58, 0.05) 0%, rgba(103, 194, 58, 0.02) 100%);
        border-color: #67c23a;
      }

      .version-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .version-info {
          display: flex;
          align-items: center;
          gap: 8px;

          .version-number {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }
        }

        .version-actions {
          display: flex;
          gap: 4px;
        }
      }

      .version-metrics {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 12px;

        .metric-item {
          display: flex;
          flex-direction: column;
          gap: 4px;

          .metric-label {
            font-size: 12px;
            color: #909399;
          }

          .metric-value {
            font-size: 14px;
            font-weight: 600;
            color: #303133;

            &.positive {
              color: #67c23a;
            }

            &.neutral {
              color: #e6a23c;
            }

            &.negative {
              color: #f56c6c;
            }
          }
        }
      }

      .version-footer {
        .create-time {
          font-size: 12px;
          color: #c0c4cc;
        }
      }
    }
  }

  .version-detail {
    .detail-header {
      display: flex;
      align-items: center;
      gap: 12px;

      h3 {
        margin: 0;
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
    }

    .detail-section {
      margin-top: 20px;

      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: #606266;
      }

      .info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 4px;

          .label {
            font-size: 12px;
            color: #909399;
          }

          .value {
            font-size: 13px;
            color: #303133;
            word-break: break-all;
          }
        }
      }

      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;

        .metric-card {
          padding: 12px;
          background-color: #f5f7fa;
          border-radius: 8px;
          text-align: center;

          .metric-title {
            font-size: 12px;
            color: #909399;
            margin-bottom: 8px;
          }

          .metric-value {
            font-size: 18px;
            font-weight: 600;
            color: #303133;

            &.positive {
              color: #67c23a;
            }

            &.neutral {
              color: #e6a23c;
            }

            &.negative {
              color: #f56c6c;
            }
          }
        }
      }
    }
  }
}
</style>
