<template>
  <el-dialog
    v-model="dialogVisible"
    title="🔬 板块对比"
    width="1000px"
    :before-close="handleClose"
    custom-class="comparison-dialog"
    append-to-body
    :z-index="20000"
  >
    <!-- 添加板块 -->
    <div class="add-sectors-section">
      <el-select
        v-model="selectedSectorCodes"
        multiple
        placeholder="选择板块进行对比（2-4个）"
        style="width: 100%"
        :multiple-limit="4"
        @change="handleSectorSelectionChange"
      >
        <el-option
          v-for="sector in availableSectors"
          :key="sector.id"
          :label="sector.name"
          :value="(sector as any).code || sector.name"
        >
          <span>{{ sector.name }}</span>
          <span v-if="sector.stockCount" class="sector-count">
            ({{ sector.stockCount }}只)
          </span>
        </el-option>
      </el-select>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><loading /></el-icon>
      <p>正在加载板块数据...</p>
    </div>

    <!-- 对比内容 -->
    <div v-else-if="comparisonResult && comparisonResult.sectors.length > 0" class="comparison-content">
      <!-- 维度选择 -->
      <div class="dimension-tabs">
        <el-radio-group v-model="activeDimension" size="small">
          <el-radio-button label="radar">雷达图</el-radio-button>
          <el-radio-button label="bar">柱状图</el-radio-button>
          <el-radio-button label="table">数据表</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 雷达图 -->
      <div v-if="activeDimension === 'radar'" class="chart-container">
        <div ref="radarChartRef" class="chart"></div>
      </div>

      <!-- 柱状图 -->
      <div v-else-if="activeDimension === 'bar'" class="chart-container">
        <div class="metric-selector">
          <el-select v-model="barChartMetric" size="small" style="width: 200px">
            <el-option label="涨跌幅" value="changePercent" />
            <el-option label="成分股数量" value="stockCount" />
            <el-option label="成交额" value="amount" />
            <el-option label="换手率" value="turnoverRate" />
          </el-select>
        </div>
        <div ref="barChartRef" class="chart"></div>
      </div>

      <!-- 数据表 -->
      <div v-else-if="activeDimension === 'table'" class="table-container">
        <el-table :data="comparisonResult.sectors" border stripe>
          <el-table-column prop="sector.name" label="板块名称" width="150" fixed />
          <el-table-column
            v-for="metric in comparisonResult.sectors[0]?.metrics"
            :key="metric.key"
            :label="metric.label"
            :prop="`metrics.${comparisonResult.sectors[0].metrics.indexOf(metric)}.formatted`"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              <span
                v-if="metric.key === 'changePercent'"
                :class="getChangeClass(row.metrics.find((m: any) => m.key === metric.key)?.value)"
              >
                {{ row.metrics.find((m: any) => m.key === metric.key)?.formatted }}
              </span>
              <span v-else>
                {{ row.metrics.find((m: any) => m.key === metric.key)?.formatted }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                link
                @click="handleViewDetail(row.sector)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 对比总结 -->
      <div class="comparison-summary">
        <h4>📊 对比总结</h4>
        <div class="summary-items">
          <div
            v-for="metric in comparisonResult.sectors[0]?.metrics"
            :key="metric.key"
            class="summary-item"
          >
            <span class="metric-label">{{ metric.label }}:</span>
            <span class="metric-best">
              {{ getBestSectorName(metric.key as keyof SectorBasicInfo) }}
            </span>
            <span class="metric-value">
              {{ getBestSectorValue(metric.key as keyof SectorBasicInfo) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="请选择板块进行对比">
        <template #image>
          <div class="empty-icon">📊</div>
        </template>
      </el-empty>
    </div>

    <!-- 底部操作 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          v-if="comparisonResult"
          type="primary"
          @click="handleSaveToFavorites"
        >
          保存到收藏夹
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { SectorNode } from '@/components/data-management/shared/types'
import type { SectorBasicInfo } from '@/components/data-management/shared/types'
import { fetchSectorInfo } from '@/components/data-management/shared/api'
import {
  compareSectors,
  getBestSector,
  getRadarChartData,
  getBarChartData,
  validateComparisonData,
  type ComparisonResult
} from './comparison-utils'

interface Props {
  visible: boolean
  availableSectors: SectorNode[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'view-detail': [sector: SectorNode]
  'save-to-favorites': [sectors: SectorNode[]]
}>()

// 状态
const dialogVisible = ref(false)
const loading = ref(false)
const activeDimension = ref<'radar' | 'bar' | 'table'>('radar')
const barChartMetric = ref<keyof SectorBasicInfo>('changePercent')
const selectedSectorCodes = ref<string[]>([])
const comparisonResult = ref<ComparisonResult | null>(null)

// 图表引用
const radarChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
let radarChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    resetState()
  }
})

watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 监听维度切换
watch(activeDimension, async () => {
  if (dialogVisible.value && comparisonResult.value) {
    await nextTick()
    renderChart()
  }
})

// 监听柱状图指标切换
watch(barChartMetric, () => {
  if (activeDimension.value === 'bar') {
    renderBarChart()
  }
})

// 重置状态
const resetState = () => {
  selectedSectorCodes.value = []
  comparisonResult.value = null
  activeDimension.value = 'radar'
  barChartMetric.value = 'changePercent'
}

// 处理板块选择变化
const handleSectorSelectionChange = async () => {
  if (selectedSectorCodes.value.length < 2) {
    comparisonResult.value = null
    return
  }

  await loadComparisonData()
}

// 加载对比数据
const loadComparisonData = async () => {
  if (selectedSectorCodes.value.length < 2) return

  loading.value = true

  try {
    // 获取选中的板块节点
    const selectedSectors = props.availableSectors.filter(sector => {
      const code = (sector as any).code || sector.name
      return selectedSectorCodes.value.includes(code)
    })

    // 获取每个板块的详细信息
    const sectorInfos: Array<{ node: SectorNode; info: SectorBasicInfo }> = []

    for (const sector of selectedSectors) {
      const response = await fetchSectorInfo(sector.name)
      if (response.success || response.code === 200) {
        const data = response.data
        sectorInfos.push({
          node: sector,
          info: {
            name: data.name || data.display_name || sector.name,
            type: data.type || '-',
            stockCount: data.stock_count || 0,
            changePercent: data.change_percent || 0,
            amount: data.amount || '-',
            turnoverRate: data.turnover_rate || '-'
          }
        })
      }
    }

    // 验证数据
    const validation = validateComparisonData(
      sectorInfos.map(s => s.node),
      sectorInfos.map(s => s.info)
    )

    if (!validation.valid) {
      ElMessage.warning(validation.message)
      return
    }

    // 创建对比结果
    comparisonResult.value = compareSectors(sectorInfos)

    // 渲染图表
    await nextTick()
    renderChart()
  } catch (error: any) {
    console.error('加载对比数据失败:', error)
    ElMessage.error(`加载对比数据失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!comparisonResult.value) return

  if (activeDimension.value === 'radar') {
    renderRadarChart()
  } else if (activeDimension.value === 'bar') {
    renderBarChart()
  }
}

// 渲染雷达图
const renderRadarChart = () => {
  if (!radarChartRef.value || !comparisonResult.value) return

  // 销毁已存在的图表
  if (radarChart) {
    radarChart.dispose()
  }

  // 创建新图表
  radarChart = echarts.init(radarChartRef.value)

  const { categories, series } = getRadarChartData(comparisonResult.value)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#2962ff',
      textStyle: { color: '#ffffff' }
    },
    legend: {
      data: series.map(s => s.name),
      textStyle: { color: 'rgba(255, 255, 255, 0.8)' },
      top: 10
    },
    radar: {
      indicator: categories.map(name => ({ name, max: 100 })),
      splitArea: {
        areaStyle: {
          color: ['rgba(102, 126, 234, 0.05)', 'rgba(102, 126, 234, 0.1)']
        }
      },
      axisLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.2)' }
      },
      splitLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      },
      name: {
        textStyle: { color: 'rgba(255, 255, 255, 0.8)' }
      }
    },
    series: [{
      type: 'radar',
      data: series.map(s => ({
        value: s.value,
        name: s.name
      })),
      areaStyle: {
        opacity: 0.3
      },
      lineStyle: {
        width: 2
      }
    }]
  }

  radarChart.setOption(option)
}

// 渲染柱状图
const renderBarChart = () => {
  if (!barChartRef.value || !comparisonResult.value) return

  // 销毁已存在的图表
  if (barChart) {
    barChart.dispose()
  }

  // 创建新图表
  barChart = echarts.init(barChartRef.value)

  const { categories, values, colors } = getBarChartData(
    comparisonResult.value,
    barChartMetric.value
  )

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#2962ff',
      textStyle: { color: '#ffffff' }
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.3)' }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.8)'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.3)' }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.8)'
      },
      splitLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    },
    series: [{
      type: 'bar',
      data: values.map((value, index) => ({
        value,
        itemStyle: { color: colors[index] }
      })),
      barWidth: '50%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0]
      }
    }]
  }

  barChart.setOption(option)
}

// 获取最优板块名称
const getBestSectorName = (metricKey: keyof SectorBasicInfo): string => {
  if (!comparisonResult.value) return '-'
  const best = getBestSector(comparisonResult.value, metricKey)
  return best?.sector.name || '-'
}

// 获取最优板块数值
const getBestSectorValue = (metricKey: keyof SectorBasicInfo): string => {
  if (!comparisonResult.value) return '-'
  const best = getBestSector(comparisonResult.value, metricKey)
  const metric = best?.metrics.find(m => m.key === metricKey)
  return metric?.formatted || '-'
}

// 获取涨跌幅样式类
const getChangeClass = (value: number): string => {
  if (value > 0) return 'text-up'
  if (value < 0) return 'text-down'
  return 'text-flat'
}

// 处理查看详情
const handleViewDetail = (sector: SectorNode) => {
  emit('view-detail', sector)
  handleClose()
}

// 处理保存到收藏夹
const handleSaveToFavorites = () => {
  if (!comparisonResult.value) return

  const sectors = comparisonResult.value.sectors.map(s => s.sector)
  emit('save-to-favorites', sectors)
  ElMessage.success('对比结果已保存到收藏夹')
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}

// 清理图表
onBeforeUnmount(() => {
  if (radarChart) {
    radarChart.dispose()
    radarChart = null
  }
  if (barChart) {
    barChart.dispose()
    barChart = null
  }
})
</script>

<style>
/* 全局样式 - 确保对话框在导航栏之上 */
.comparison-dialog .el-dialog {
  z-index: 20000 !important;
}

.comparison-dialog .el-dialog__header {
  z-index: 20001 !important;
}

.comparison-dialog .el-dialog__body {
  z-index: 20000 !important;
}

.comparison-dialog .el-overlay {
  z-index: 19999 !important;
}
</style>

<style scoped>
/* 添加板块 */
.add-sectors-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sector-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 4px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #2962ff;
}

/* 对比内容 */
.comparison-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 维度选择 */
.dimension-tabs {
  display: flex;
  justify-content: center;
  padding: 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
}

/* 图表容器 */
.chart-container {
  padding: 20px;
  background: rgba(26, 26, 46, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-container .chart {
  width: 100%;
  height: 400px;
}

.metric-selector {
  margin-bottom: 16px;
  text-align: center;
}

/* 数据表 */
.table-container {
  background: rgba(26, 26, 46, 0.5);
  border-radius: 8px;
  padding: 16px;
}

/* 涨跌颜色 */
.text-up {
  color: #f56c6c;
  font-weight: 600;
}

.text-down {
  color: #67c23a;
  font-weight: 600;
}

.text-flat {
  color: rgba(255, 255, 255, 0.6);
}

/* 表格样式 */
:deep(.el-table) {
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
}

:deep(.el-table th) {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.1);
}

:deep(.el-table td) {
  border-color: rgba(255, 255, 255, 0.05);
}

:deep(.el-table tr:hover > td) {
  background: rgba(255, 255, 255, 0.05);
}

/* 对比总结 */
.comparison-summary {
  padding: 16px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.comparison-summary h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #ffffff;
}

.summary-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.metric-label {
  color: rgba(255, 255, 255, 0.6);
}

.metric-best {
  color: #2962ff;
  font-weight: 600;
}

.metric-value {
  color: #ffffff;
  font-weight: 700;
}

/* 空状态 */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

/* 底部操作 */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
</style>
