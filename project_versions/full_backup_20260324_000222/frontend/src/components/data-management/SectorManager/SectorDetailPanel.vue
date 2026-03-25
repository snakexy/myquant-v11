<template>
  <el-drawer
    v-model="drawerVisible"
    :title="`${sectorInfo.name || '板块'} 详情`"
    size="60%"
    :before-close="handleClose"
    custom-class="sector-detail-drawer"
    append-to-body
    :z-index="25000"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 详情内容 -->
    <div v-else class="detail-content">
      <!-- 基本信息 -->
      <div class="info-section">
        <h4 class="section-title">📊 基本信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="板块名称">
            {{ sectorInfo.name }}
          </el-descriptions-item>
          <el-descriptions-item label="板块类型">
            {{ sectorInfo.type || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="成分股数量">
            {{ sectorInfo.stockCount }} 只
          </el-descriptions-item>
          <el-descriptions-item label="涨跌幅">
            <span :class="getChangeClass(sectorInfo.changePercent)">
              {{ formatChange(sectorInfo.changePercent) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="成交额">
            {{ sectorInfo.amount || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="换手率">
            {{ sectorInfo.turnoverRate || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 成分股TOP10 -->
      <div class="top-stocks-section">
        <h4 class="section-title">🏆 TOP10 成分股</h4>
        <el-table :data="topStocks" stripe max-height="400">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="code" label="代码" width="100" />
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="changePercent" label="涨跌幅" width="100">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">
                {{ formatChange(row.changePercent) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="contribution" label="贡献度">
            <template #default="{ row }">
              <el-progress
                :percentage="row.contribution || 0"
                :color="getProgressColor(row.contribution)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="成交额">
            <template #default="{ row }">
              {{ row.amount || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 历史走势图 -->
      <div class="chart-section">
        <h4 class="section-title">📈 历史走势</h4>
        <div ref="chartRef" class="chart-container"></div>
      </div>

      <!-- 智能推荐 -->
      <div class="recommendation-section">
        <div class="section-header">
          <h4 class="section-title">🤖 智能推荐</h4>
          <el-button
            type="primary"
            size="small"
            @click="showRecommendationDialog = true"
            :icon="MagicStick"
          >
            发现相关板块
          </el-button>
        </div>
        <p class="recommendation-hint">
          基于 QLib 方法论，从价格相关性、行业关联、成分股重叠等多维度智能推荐相关板块
        </p>
      </div>
    </div>

    <!-- 智能推荐对话框 -->
    <SectorRecommendationDialog
      v-model:visible="showRecommendationDialog"
      :target-sector="currentSectorNode"
      :all-sectors="allSectors"
      @select-sector="handleSelectRecommendedSector"
      @add-to-compare="handleAddToCompare"
      @view-detail="handleViewRecommendedDetail"
    />
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, MagicStick } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { SectorBasicInfo, SectorStockInfo, SectorNode } from '@/components/data-management/shared/types'
import { fetchSectorInfo, fetchSectorStocks, getSectorStocksRealtime, getKlineData } from '@/components/data-management/shared/api'
import SectorRecommendationDialog from './SectorRecommendationDialog.vue'

interface Props {
  visible: boolean
  sectorName: string
  sectorCode?: string  // 添加板块代码用于API调用
  allSectors?: SectorNode[]  // 所有板块列表（用于推荐）
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'select-sector': [sector: SectorNode]  // 选择推荐的板块
  'add-to-compare': [sector: SectorNode]  // 添加到对比
}>()

// 状态
const drawerVisible = ref(false)
const loading = ref(false)
const realtimeLoading = ref(false)  // 实时数据加载状态
const sectorInfo = ref<SectorBasicInfo>({
  name: '',
  type: '',
  stockCount: 0,
  changePercent: 0,
  amount: ''
})
const topStocks = ref<SectorStockInfo[]>([])
const chartRef = ref<HTMLElement>()
const hasRealtimeData = ref(false)  // 是否有实时数据
const showRecommendationDialog = ref(false)  // 推荐对话框显示状态
const currentSectorNode = ref<SectorNode | null>(null)  // 当前板块节点
let chart: echarts.ECharts | null = null

// 监听visible变化
watch(() => props.visible, (newVal) => {
  drawerVisible.value = newVal
  if (newVal && props.sectorName) {
    loadSectorDetail()
    // 更新当前板块节点
    currentSectorNode.value = createCurrentSectorNode()
  }
})

// 监听drawerVisible变化
watch(drawerVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 加载板块详情
const loadSectorDetail = async () => {
  if (!props.sectorName) return

  loading.value = true
  hasRealtimeData.value = false

  try {
    // 1. 获取板块基本信息
    const infoResponse = await fetchSectorInfo(props.sectorName)
    if (infoResponse.success || infoResponse.code === 200) {
      const data = infoResponse.data
      sectorInfo.value = {
        name: data.name || data.display_name || props.sectorName,
        type: data.type || '-',
        stockCount: data.stock_count || 0,
        changePercent: data.change_percent || 0,
        amount: data.amount || '-',
        turnoverRate: data.turnover_rate || '-'
      }
    }

    // 2. 获取成分股列表
    const stocksResponse = await fetchSectorStocks(props.sectorName)
    if (stocksResponse.success || stocksResponse.code === 200) {
      const data = stocksResponse.data
      if (data && data.stocks) {
        // 保存原始股票代码
        const stockCodes = data.stocks.map((s: any) => s.code || s)

        // 获取QMT实时行情（允许失败）
        try {
          await loadRealtimeQuote(stockCodes)
        } catch (error) {
          console.warn('获取实时行情失败（非致命错误）:', error)
          // 继续执行，不影响其他数据展示
        }

        // 转换为股票信息列表，取TOP10
        topStocks.value = data.stocks.slice(0, 10).map((stock: any) => ({
          code: stock.code || stock,
          name: stock.name || `股票${stock.code || stock}`,
          market: stock.market || '-',
          changePercent: stock.change_percent || 0,
          contribution: stock.contribution || 0,
          amount: stock.amount || '-'
        }))
      }
    }

    // 3. 加载图表（允许失败）
    await nextTick()
    try {
      await loadHistoricalData()
    } catch (error) {
      console.warn('加载历史数据失败（非致命错误）:', error)
      // 继续执行，不影响其他数据展示
    }
  } catch (error: any) {
    console.error('加载板块详情失败:', error)
    ElMessage.error(`加载详情失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 加载实时行情（多数据源支持：QMT > mootdx）
const loadRealtimeQuote = async (stockCodes: string[]) => {
  if (stockCodes.length === 0) return

  realtimeLoading.value = true
  try {
    const response = await getSectorStocksRealtime(stockCodes)

    if (response.code === 200 && response.data) {
      // 更新板块统计信息（从实时数据聚合）
      updateSectorFromRealtime(response.data)
      hasRealtimeData.value = true
      ElMessage.success('实时行情数据已更新')
    } else {
      // 所有数据源都不可达
      console.warn('无法获取实时行情:', response.message)
      ElMessage.warning('无法获取实时行情，请确保QMT或mootdx数据源可用')
      hasRealtimeData.value = false
    }
  } catch (error: any) {
    console.error('获取实时行情失败:', error)
    ElMessage.warning('获取实时行情失败，请确保QMT或mootdx数据源可用')
    hasRealtimeData.value = false
  } finally {
    realtimeLoading.value = false
  }
}

// 从实时数据更新板块信息
const updateSectorFromRealtime = (realtimeData: any) => {
  if (!realtimeData) return

  // 计算板块涨跌幅（从成分股加权平均）
  let totalChange = 0
  let totalAmount = 0
  let stockCount = 0

  // 更新TOP10表格中的个股数据
  topStocks.value = topStocks.value.map(stock => {
    const stockData = realtimeData[stock.code]
    if (stockData) {
      const changePercent = stockData.lastPrice > 0 && stockData.openPrice > 0
        ? ((stockData.lastPrice - stockData.openPrice) / stockData.openPrice * 100)
        : 0

      totalChange += changePercent
      totalAmount += stockData.amount || 0
      stockCount++

      return {
        ...stock,
        changePercent: parseFloat(changePercent.toFixed(2)),
        amount: formatAmount(stockData.amount || 0),
        // 贡献度基于涨跌幅绝对值
        contribution: Math.min(100, Math.abs(changePercent) * 10)
      }
    }
    return stock
  })

  // 更新板块整体信息
  if (stockCount > 0) {
    sectorInfo.value.changePercent = parseFloat((totalChange / stockCount).toFixed(2))
    sectorInfo.value.amount = formatAmount(totalAmount)
  }
}

// 加载历史数据（不允许使用模拟数据）
const loadHistoricalData = async () => {
  try {
    // 获取板块的成分股列表
    if (topStocks.value.length === 0) {
      console.warn('没有成分股数据，无法加载历史走势')
      ElMessage.warning('没有成分股数据，无法加载历史走势')
      return
    }

    // 使用第一只股票作为代表来获取历史数据
    const representativeStock = topStocks.value[0]

    // 转换股票代码格式：sh600000 -> 600000.SH
    const convertedCode = convertStockCode(representativeStock.code)

    // 从统一数据中枢获取历史数据
    const response = await fetch(`/api/v1/stock-data/historical/${convertedCode}?days=30`)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const result = await response.json()

    if (!result.success || !result.data || result.data.length === 0) {
      throw new Error(result.message || '未找到历史数据')
    }

    // 转换数据格式
    const chartData = {
      dates: result.data.map((item: any) => item.date),
      values: result.data.map((item: any) => parseFloat(item.close))
    }

    console.log(`成功从 ${result.data_source} 获取 ${result.count} 条历史数据`)
    console.log(`数据时间范围: ${result.start_date} 到 ${result.end_date}`)

    initChart(chartData)
  } catch (error: any) {
    console.error('加载历史数据失败:', error)
    ElMessage.error(`加载历史数据失败: ${error.message}`)
    throw error // 向上抛出错误，不使用模拟数据
  }
}

// 转换股票代码格式
const convertStockCode = (code: string): string => {
  if (!code) return ''

  // 移除 sh/sz 前缀
  let cleanCode = code.replace(/^(sh|sz)/i, '')

  // 添加市场后缀
  if (code.toLowerCase().startsWith('sh')) {
    return cleanCode + '.SH'
  } else if (code.toLowerCase().startsWith('sz')) {
    return cleanCode + '.SZ'
  }

  // 如果没有前缀，默认为SH
  return cleanCode + '.SH'
}

// 格式化成交额
const formatAmount = (amount: number): string => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toString()
}

// 初始化图表
const initChart = (chartData?: { dates: string[], values: number[] }) => {
  if (!chartRef.value) return

  // 销毁已存在的图表
  if (chart) {
    chart.dispose()
  }

  // 创建新图表
  chart = echarts.init(chartRef.value)

  // 图表配置
  const option = {
    backgroundColor: 'transparent',
    title: {
      text: `${props.sectorName} 历史走势`,
      left: 'center',
      textStyle: {
        color: '#ffffff',
        fontSize: 14
      },
      subtext: hasRealtimeData.value ? '数据来源：QMT实时行情' : '数据来源：历史数据',
      subtextStyle: {
        color: 'rgba(255, 255, 255, 0.5)',
        fontSize: 12
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#2962ff',
      textStyle: {
        color: '#ffffff'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 80,
      containLabel: true,
      backgroundColor: 'transparent'
    },
    xAxis: {
      type: 'category',
      data: chartData?.dates || [],  // 使用传入的历史数据
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    },
    series: [{
      name: '板块指数',
      type: 'line',
      data: chartData?.values || [],  // 使用传入的历史数据
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        color: '#2962ff',
        width: 2
      },
      itemStyle: {
        color: '#2962ff'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
          { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
        ])
      }
    }]
  }

  chart.setOption(option)
}

// 格式化涨跌幅
const formatChange = (value: number): string => {
  if (value === undefined || value === null) return '-'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

// 获取涨跌幅样式类
const getChangeClass = (value: number): string => {
  if (value > 0) return 'text-up'
  if (value < 0) return 'text-down'
  return 'text-flat'
}

// 获取进度条颜色
const getProgressColor = (value: number): string => {
  if (value >= 80) return '#f56c6c'
  if (value >= 60) return '#e6a23c'
  if (value >= 40) return '#409eff'
  return '#67c23a'
}

// 关闭抽屉
const handleClose = () => {
  drawerVisible.value = false
}

// 创建当前板块节点（用于推荐）
const createCurrentSectorNode = (): SectorNode => {
  return {
    id: props.sectorName || '',
    name: props.sectorName || '',
    type: 'sector',
    stockCount: sectorInfo.value.stockCount || 0
  }
}

// 处理选择推荐板块
const handleSelectRecommendedSector = (sector: SectorNode) => {
  emit('select-sector', sector)
  ElMessage.success(`已选择板块: ${sector.name}`)
}

// 处理添加到对比
const handleAddToCompare = (sector: SectorNode) => {
  emit('add-to-compare', sector)
}

// 处理查看推荐板块详情
const handleViewRecommendedDetail = (sector: SectorNode) => {
  // 关闭当前详情，打开新板块详情
  drawerVisible.value = false
  showRecommendationDialog.value = false

  // 触发父组件更新
  nextTick(() => {
    emit('select-sector', sector)
  })
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  chart?.resize()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #2962ff;
}

.detail-content {
  padding: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-section,
.top-stocks-section,
.chart-section {
  margin-bottom: 32px;
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
  background: transparent !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

:deep(.el-table__body-wrapper) {
  background: transparent !important;
}

:deep(.el-table__header-wrapper) {
  background: transparent !important;
}

:deep(.el-table th) {
  background: rgba(255, 255, 255, 0.05) !important;
  color: rgba(255, 255, 255, 0.8) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-table td) {
  background: rgba(26, 26, 46, 0.3) !important;
  border-color: rgba(255, 255, 255, 0.05) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

:deep(.el-table tr:hover > td) {
  background: rgba(255, 255, 255, 0.08) !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(255, 255, 255, 0.02) !important;
}

:deep(.el-table__empty-block) {
  background: transparent !important;
}

:deep(.el-table__empty-text) {
  color: rgba(255, 255, 255, 0.5) !important;
}

/* 描述列表样式 */
:deep(.el-descriptions) {
  --el-descriptions-table-border-color: rgba(255, 255, 255, 0.1);
  background: transparent !important;
}

:deep(.el-descriptions__body) {
  background: transparent !important;
}

:deep(.el-descriptions__table) {
  background: transparent !important;
}

:deep(.el-descriptions__table tbody) {
  background: transparent !important;
}

:deep(.el-descriptions__table tr) {
  background: transparent !important;
}

:deep(.el-descriptions__label) {
  background: rgba(255, 255, 255, 0.05) !important;
  color: rgba(255, 255, 255, 0.7) !important;
}

:deep(.el-descriptions__content) {
  background: rgba(26, 26, 46, 0.3) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

:deep(.el-descriptions__body .el-descriptions__table .el-descriptions__cell.is-bordered) {
  border-color: rgba(255, 255, 255, 0.1);
  background: transparent !important;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 300px;
  background: rgba(26, 26, 46, 0.5);
  border-radius: 8px;
  padding: 16px;
}

/* 抽屉样式 */
:deep(.el-drawer) {
  background: rgba(26, 26, 46, 0.98);
  z-index: 10001 !important;
}

:deep(.el-drawer__header) {
  background: rgba(102, 126, 234, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 0;
  padding: 20px;
  z-index: 10002 !important;
}

:deep(.el-drawer__title) {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-drawer__body) {
  padding: 20px;
  z-index: 10001 !important;
}

:deep(.el-drawer__close-btn) {
  color: rgba(255, 255, 255, 0.7);
}

:deep(.el-drawer__close-btn:hover) {
  color: #ffffff;
}

/* 推荐部分 */
.recommendation-section {
  margin-top: 32px;
  padding: 20px;
  background: rgba(102, 126, 234, 0.08);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.recommendation-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.recommendation-hint {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
}
</style>
