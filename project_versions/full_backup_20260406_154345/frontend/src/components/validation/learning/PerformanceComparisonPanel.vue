<template>
  <el-card class="comparison-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📊 性能对比</span>
        <el-button text @click="handleRefresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </template>

    <div v-if="loading && !comparisonData" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="!comparisonData" class="empty-container">
      <el-empty description="暂无对比数据" />
    </div>

    <div v-else class="comparison-content">
      <!-- 版本信息概览 -->
      <div class="version-overview">
        <div class="version-card current">
          <div class="version-badge">当前版本</div>
          <div class="version-number">v{{ comparisonData.currentVersion.versionNumber }}</div>
          <div class="version-time">{{ formatDate(comparisonData.currentVersion.createdAt) }}</div>
        </div>

        <div v-if="comparisonData.previousVersion" class="version-card previous">
          <div class="version-badge">上一版本</div>
          <div class="version-number">v{{ comparisonData.previousVersion.versionNumber }}</div>
          <div class="version-time">{{ formatDate(comparisonData.previousVersion.createdAt) }}</div>
        </div>

        <div v-if="comparisonData.baselineVersion" class="version-card baseline">
          <div class="version-badge">基线版本</div>
          <div class="version-number">v{{ comparisonData.baselineVersion.versionNumber }}</div>
          <div class="version-time">{{ formatDate(comparisonData.baselineVersion.createdAt) }}</div>
        </div>
      </div>

      <el-divider />

      <!-- 性能指标对比表格 -->
      <div class="comparison-table">
        <h4>指标变化</h4>

        <div class="metric-row">
          <div class="metric-name">夏普比率</div>
          <div class="metric-values">
            <div class="metric-value">
              <span class="label">当前</span>
              <span class="value">{{ comparisonData.currentVersion.performanceMetrics.sharpeRatio.toFixed(2) }}</span>
            </div>
            <div v-if="comparisonData.previousVersion" class="metric-value">
              <span class="label">上一版本</span>
              <span class="value">{{ comparisonData.previousVersion.performanceMetrics.sharpeRatio.toFixed(2) }}</span>
            </div>
          </div>
          <div class="metric-change" :class="getChangeClass(comparisonData.comparison.sharpeRatioChange)">
            <el-icon v-if="comparisonData.comparison.sharpeRatioChange > 0"><Top /></el-icon>
            <el-icon v-else-if="comparisonData.comparison.sharpeRatioChange < 0"><Bottom /></el-icon>
            <el-icon v-else><Minus /></el-icon>
            <span>{{ formatChange(comparisonData.comparison.sharpeRatioChange) }}</span>
          </div>
        </div>

        <div class="metric-row">
          <div class="metric-name">总收益率</div>
          <div class="metric-values">
            <div class="metric-value">
              <span class="label">当前</span>
              <span class="value">{{ comparisonData.currentVersion.performanceMetrics.totalReturnRate.toFixed(2) }}%</span>
            </div>
            <div v-if="comparisonData.previousVersion" class="metric-value">
              <span class="label">上一版本</span>
              <span class="value">{{ comparisonData.previousVersion.performanceMetrics.totalReturnRate.toFixed(2) }}%</span>
            </div>
          </div>
          <div class="metric-change" :class="getChangeClass(comparisonData.comparison.totalReturnChange)">
            <el-icon v-if="comparisonData.comparison.totalReturnChange > 0"><Top /></el-icon>
            <el-icon v-else-if="comparisonData.comparison.totalReturnChange < 0"><Bottom /></el-icon>
            <el-icon v-else><Minus /></el-icon>
            <span>{{ formatChange(comparisonData.comparison.totalReturnChange) }}</span>
          </div>
        </div>

        <div class="metric-row">
          <div class="metric-name">最大回撤</div>
          <div class="metric-values">
            <div class="metric-value">
              <span class="label">当前</span>
              <span class="value">{{ comparisonData.currentVersion.performanceMetrics.maxDrawdown.toFixed(2) }}%</span>
            </div>
            <div v-if="comparisonData.previousVersion" class="metric-value">
              <span class="label">上一版本</span>
              <span class="value">{{ comparisonData.previousVersion.performanceMetrics.maxDrawdown.toFixed(2) }}%</span>
            </div>
          </div>
          <div class="metric-change" :class="getDrawdownChangeClass(comparisonData.comparison.maxDrawdownChange)">
            <el-icon v-if="comparisonData.comparison.maxDrawdownChange < 0"><Top /></el-icon>
            <el-icon v-else-if="comparisonData.comparison.maxDrawdownChange > 0"><Bottom /></el-icon>
            <el-icon v-else><Minus /></el-icon>
            <span>{{ formatChange(comparisonData.comparison.maxDrawdownChange) }}</span>
          </div>
        </div>
      </div>

      <el-divider />

      <!-- 详细性能指标雷达图 -->
      <div class="radar-chart-container">
        <h4>性能雷达图</h4>
        <div ref="radarChartRef" class="radar-chart"></div>
      </div>

      <!-- 性能评分 -->
      <div class="performance-summary">
        <el-alert
          :type="getPerformanceAlertType()"
          :closable="false"
          show-icon
        >
          <template #title>
            <span class="summary-title">{{ performanceSummary }}</span>
          </template>
        </el-alert>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Top, Bottom, Minus } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { learningApi } from '@/api/modules/learning'
import type { PerformanceComparison } from '@/api/modules/learning'

// Props
interface Props {
  modelId: string
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: true,
  refreshInterval: 60000
})

// 对比数据
const comparisonData = ref<PerformanceComparison | null>(null)
const loading = ref(false)

// 雷达图
const radarChartRef = ref<HTMLElement>()
let radarChartInstance: echarts.ECharts | null = null

// 自动刷新定时器
let refreshTimer: number | null = null

// 加载性能对比数据
const loadComparison = async () => {
  loading.value = true
  try {
    const response = await learningApi.getPerformanceComparison(props.modelId)
    if (response.code === 200) {
      comparisonData.value = response.data
      await nextTick()
      initRadarChart()
    }
  } catch (error) {
    console.error('加载性能对比失败:', error)
    // 降级方案：使用默认对比数据
    comparisonData.value = {
      currentVersion: {
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
      previousVersion: {
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
      baselineVersion: {
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
      },
      comparison: {
        sharpeRatioChange: 0.20,
        totalReturnChange: 3.0,
        maxDrawdownChange: -3.3
      }
    }
    await nextTick()
    initRadarChart()
    ElMessage.warning('使用默认对比数据')
  } finally {
    loading.value = false
  }
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChartRef.value || !comparisonData.value) return

  if (!radarChartInstance) {
    radarChartInstance = echarts.init(radarChartRef.value)
  }

  const current = comparisonData.value.currentVersion.performanceMetrics
  const previous = comparisonData.value.previousVersion?.performanceMetrics
  const baseline = comparisonData.value.baselineVersion?.performanceMetrics

  const option: EChartsOption = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      data: ['当前版本', '上一版本', '基线版本'],
      bottom: 0
    },
    radar: {
      indicator: [
        { name: '夏普比率', max: 2.5 },
        { name: '收益率(%)', max: 20 },
        { name: '胜率(%)', max: 70 },
        { name: '盈亏比', max: 2.5 },
        { name: '波动率(反向)', max: 25 }
      ],
      radius: '60%'
    },
    series: [
      {
        name: '性能对比',
        type: 'radar',
        data: [
          {
            value: [
              current.sharpeRatio,
              current.totalReturnRate,
              current.winRate,
              current.profitLossRatio,
              25 - current.volatility
            ],
            name: '当前版本',
            itemStyle: { color: '#67c23a' },
            areaStyle: { color: 'rgba(103, 194, 58, 0.3)' }
          },
          ...(previous
            ? [
                {
                  value: [
                    previous.sharpeRatio,
                    previous.totalReturnRate,
                    previous.winRate,
                    previous.profitLossRatio,
                    25 - previous.volatility
                  ],
                  name: '上一版本',
                  itemStyle: { color: '#409eff' },
                  areaStyle: { color: 'rgba(64, 158, 255, 0.3)' }
                }
              ]
            : []),
          ...(baseline
            ? [
                {
                  value: [
                    baseline.sharpeRatio,
                    baseline.totalReturnRate,
                    baseline.winRate,
                    baseline.profitLossRatio,
                    25 - baseline.volatility
                  ],
                  name: '基线版本',
                  itemStyle: { color: '#909399' },
                  areaStyle: { color: 'rgba(144, 147, 153, 0.3)' }
                }
              ]
            : [])
        ]
      }
    ]
  }

  radarChartInstance.setOption(option)
}

// 刷新
const handleRefresh = () => {
  loadComparison()
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  })
}

// 格式化变化
const formatChange = (value: number): string => {
  const sign = value > 0 ? '+' : ''
  return sign + value.toFixed(2)
}

// 获取变化样式（越大越好）
const getChangeClass = (value: number): string => {
  if (value > 0.05) return 'positive'
  if (value < -0.05) return 'negative'
  return 'neutral'
}

// 获取回撤变化样式（越小越好）
const getDrawdownChangeClass = (value: number): string => {
  if (value < -0.05) return 'positive'
  if (value > 0.05) return 'negative'
  return 'neutral'
}

// 性能摘要
const performanceSummary = (): string => {
  if (!comparisonData.value) return '暂无数据'

  const { sharpeRatioChange, totalReturnChange, maxDrawdownChange } = comparisonData.value.comparison

  const improvements = []
  const declines = []

  if (sharpeRatioChange > 0.05) improvements.push('夏普比率提升')
  if (sharpeRatioChange < -0.05) declines.push('夏普比率下降')

  if (totalReturnChange > 1) improvements.push('收益率提升')
  if (totalReturnChange < -1) declines.push('收益率下降')

  if (maxDrawdownChange < -0.5) improvements.push('回撤减小')
  if (maxDrawdownChange > 0.5) declines.push('回撤增大')

  if (improvements.length > 0 && declines.length === 0) {
    return `当前版本表现优秀：${improvements.join('、')}，建议继续保持`
  } else if (improvements.length > declines.length) {
    return `当前版本表现良好：${improvements.join('、')}，但${declines.join('、')}`
  } else if (declines.length > improvements.length) {
    return `当前版本需要优化：${declines.join('、')}，建议重新训练`
  } else {
    return '当前版本表现平稳，各指标变化不大'
  }
}

// 获取提示框类型
const getPerformanceAlertType = (): 'success' | 'warning' | 'info' => {
  if (!comparisonData.value) return 'info'

  const { sharpeRatioChange, totalReturnChange, maxDrawdownChange } = comparisonData.value.comparison

  if (sharpeRatioChange > 0.05 && totalReturnChange > 1 && maxDrawdownChange < -0.5) {
    return 'success'
  } else if (sharpeRatioChange < -0.05 || totalReturnChange < -1 || maxDrawdownChange > 0.5) {
    return 'warning'
  } else {
    return 'info'
  }
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (props.autoRefresh && props.refreshInterval > 0) {
    refreshTimer = window.setInterval(() => {
      loadComparison()
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

// 窗口大小改变时重绘图表
const handleResize = () => {
  radarChartInstance?.resize()
}

// 生命周期
onMounted(() => {
  loadComparison()
  startAutoRefresh()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopAutoRefresh()
  window.removeEventListener('resize', handleResize)
  radarChartInstance?.dispose()
})

// 暴露方法
defineExpose({
  refresh: loadComparison
})
</script>

<style scoped lang="scss">
.comparison-card {
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
    padding: 60px 0;
  }

  .comparison-content {
    .version-overview {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;

      .version-card {
        flex: 1;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e4e7ed;
        text-align: center;
        transition: all 0.3s;

        &:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        &.current {
          background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(103, 194, 58, 0.05) 100%);
          border-color: #67c23a;
        }

        &.previous {
          background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(64, 158, 255, 0.05) 100%);
          border-color: #409eff;
        }

        &.baseline {
          background: linear-gradient(135deg, rgba(144, 147, 153, 0.1) 0%, rgba(144, 147, 153, 0.05) 100%);
          border-color: #909399;
        }

        .version-badge {
          font-size: 11px;
          color: #606266;
          margin-bottom: 4px;
        }

        .version-number {
          font-size: 18px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 4px;
        }

        .version-time {
          font-size: 11px;
          color: #909399;
        }
      }
    }

    .comparison-table {
      h4 {
        margin: 0 0 16px 0;
        font-size: 14px;
        font-weight: 600;
        color: #606266;
      }

      .metric-row {
        display: grid;
        grid-template-columns: 120px 1fr 100px;
        gap: 12px;
        align-items: center;
        padding: 12px;
        margin-bottom: 8px;
        background-color: #f5f7fa;
        border-radius: 8px;

        &:last-child {
          margin-bottom: 0;
        }

        .metric-name {
          font-size: 13px;
          font-weight: 500;
          color: #303133;
        }

        .metric-values {
          display: flex;
          gap: 24px;

          .metric-value {
            display: flex;
            flex-direction: column;
            gap: 2px;

            .label {
              font-size: 11px;
              color: #909399;
            }

            .value {
              font-size: 14px;
              font-weight: 600;
              color: #303133;
            }
          }
        }

        .metric-change {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
          font-size: 13px;
          font-weight: 600;
          padding: 4px 8px;
          border-radius: 4px;

          &.positive {
            color: #67c23a;
            background-color: rgba(103, 194, 58, 0.1);
          }

          &.negative {
            color: #f56c6c;
            background-color: rgba(245, 108, 108, 0.1);
          }

          &.neutral {
            color: #909399;
            background-color: rgba(144, 147, 153, 0.1);
          }
        }
      }
    }

    .radar-chart-container {
      margin-top: 20px;

      h4 {
        margin: 0 0 16px 0;
        font-size: 14px;
        font-weight: 600;
        color: #606266;
      }

      .radar-chart {
        width: 100%;
        height: 300px;
      }
    }

    .performance-summary {
      margin-top: 20px;

      .summary-title {
        font-size: 14px;
      }
    }
  }
}
</style>
