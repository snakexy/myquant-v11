<template>
  <div class="sector-view">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-radio-group v-model="viewMode" @change="handleViewModeChange">
        <el-radio-button label="ranking">板块排名</el-radio-button>
        <el-radio-button label="heatmap">热力图</el-radio-button>
        <el-radio-button label="rotation">轮动分析</el-radio-button>
      </el-radio-group>

      <div class="filters">
        <el-select v-model="period" placeholder="周期" @change="fetchData" style="width: 120px">
          <el-option label="1日" :value="1" />
          <el-option label="3日" :value="3" />
          <el-option label="5日" :value="5" />
          <el-option label="10日" :value="10" />
        </el-select>

        <el-button @click="fetchData" :loading="loading" :icon="Refresh">刷新</el-button>
      </div>
    </div>

    <!-- 板块排名视图 -->
    <div v-show="viewMode === 'ranking'" class="section">
      <div class="section-header">
        <h3>板块强度排名</h3>
      </div>

      <el-table :data="rankingData" stripe v-loading="loading" @row-click="viewSectorDetail" class="clickable-rows">
        <el-table-column type="index" label="排名" width="80">
          <template #default="scope">
            <el-tag v-if="scope.$index < 3" :type="scope.$index === 0 ? 'danger' : scope.$index === 1 ? 'warning' : 'success'">
              {{ scope.$index + 1 }}
            </el-tag>
            <span v-else>{{ scope.$index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="sector_name" label="板块名称" width="150" />

        <el-table-column label="平均涨跌幅" width="130">
          <template #default="{ row }">
            <span :class="getChangeClass(row.strength.avg_change)">
              {{ formatPercent(row.strength.avg_change) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="strength.up_count" label="上涨" width="80" />
        <el-table-column prop="strength.down_count" label="下跌" width="80" />
        <el-table-column prop="strength.total_count" label="总计" width="80" />

        <el-table-column label="上涨占比" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.strength.up_ratio" :color="getProgressColor(row.strength.up_ratio)" />
          </template>
        </el-table-column>

        <el-table-column label="强度得分" width="120">
          <template #default="{ row }">
            <el-tag :type="getStrengthType(row.strength.strength_score)">
              {{ row.strength.strength_score }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click.stop="viewSectorDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 板块热力图视图 -->
    <div v-show="viewMode === 'heatmap'" class="section">
      <div class="section-header">
        <h3>板块热力图</h3>
      </div>
      <div class="heatmap-container" ref="heatmapChart"></div>
    </div>

    <!-- 板块轮动分析视图 -->
    <div v-show="viewMode === 'rotation'" class="rotation-view">
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="section">
            <div class="section-header">
              <h3>热点板块</h3>
            </div>
            <div class="sector-list hot">
              <div v-for="sector in rotationData.hot_sectors" :key="sector.sector_code" class="sector-card" @click="viewSectorDetail(sector)">
                <div class="sector-header">
                  <span class="sector-name">{{ sector.sector_name }}</span>
                  <el-tag :type="getStrengthType(sector.strength.strength_score)" size="small">
                    {{ sector.strength.strength_score }}
                  </el-tag>
                </div>
                <div class="sector-metrics">
                  <span :class="getChangeClass(sector.strength.avg_change)">
                    {{ formatPercent(sector.strength.avg_change) }}
                  </span>
                  <span class="text-secondary">上涨: {{ sector.strength.up_ratio }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="section">
            <div class="section-header">
              <h3>冷门板块</h3>
            </div>
            <div class="sector-list cold">
              <div v-for="sector in rotationData.cold_sectors" :key="sector.sector_code" class="sector-card" @click="viewSectorDetail(sector)">
                <div class="sector-header">
                  <span class="sector-name">{{ sector.sector_name }}</span>
                  <el-tag :type="getStrengthType(sector.strength.strength_score)" size="small">
                    {{ sector.strength.strength_score }}
                  </el-tag>
                </div>
                <div class="sector-metrics">
                  <span :class="getChangeClass(sector.strength.avg_change)">
                    {{ formatPercent(sector.strength.avg_change) }}
                  </span>
                  <span class="text-secondary">上涨: {{ sector.strength.up_ratio }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <div class="section" v-if="rotationData.rotation_signal?.length > 0">
        <div class="section-header">
          <h3>轮动信号</h3>
        </div>
        <div class="signals">
          <el-alert
            v-for="sector in rotationData.rotation_signal"
            :key="sector.sector_code"
            :type="sector.strength.strength_score > 0 ? 'success' : 'warning'"
            :title="`${sector.sector_name} - 强度变化显著`"
            :description="`平均涨跌幅: ${formatPercent(sector.strength.avg_change)}, 上涨占比: ${sector.strength.up_ratio}%`"
            show-icon
            :closable="false"
          />
        </div>
      </div>
    </div>

    <!-- 板块详情对话框 -->
    <el-dialog v-model="detailVisible" :title="`${selectedSector?.sector_name} - 详情`" width="80%">
      <div v-loading="detailLoading">
        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-statistic title="平均涨跌幅" :value="sectorDetail?.strength?.avg_change || 0">
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="上涨家数" :value="sectorDetail?.strength?.up_count || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="下跌家数" :value="sectorDetail?.strength?.down_count || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="强度得分" :value="sectorDetail?.strength?.strength_score || 0" />
          </el-col>
        </el-row>

        <el-divider />

        <h4>板块内股票</h4>
        <el-table :data="sectorDetail?.stocks || []" stripe>
          <el-table-column prop="symbol" label="代码" width="100" />
          <el-table-column prop="price" label="价格" width="100">
            <template #default="{ row }">
              {{ formatPrice(row.price) }}
            </template>
          </el-table-column>
          <el-table-column prop="open" label="开盘" width="100">
            <template #default="{ row }">
              {{ formatPrice(row.open) }}
            </template>
          </el-table-column>
          <el-table-column prop="high" label="最高" width="100">
            <template #default="{ row }">
              {{ formatPrice(row.high) }}
            </template>
          </el-table-column>
          <el-table-column prop="low" label="最低" width="100">
            <template #default="{ row }">
              {{ formatPrice(row.low) }}
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="120">
            <template #default="{ row }">
              {{ formatVolume(row.volume) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface SectorStrength {
  avg_change: number
  up_count: number
  down_count: number
  flat_count: number
  total_count: number
  up_ratio: number
  strength_score: number
}

interface SectorData {
  sector_code: string
  sector_name: string
  strength: SectorStrength
}

const viewMode = ref<'ranking' | 'heatmap' | 'rotation'>('ranking')
const period = ref(1)
const loading = ref(false)

const rankingData = ref<SectorData[]>([])
const rotationData = ref<{
  hot_sectors: SectorData[]
  cold_sectors: SectorData[]
  rotation_signal: SectorData[]
}>({ hot_sectors: [], cold_sectors: [], rotation_signal: [] })
const heatmapData = ref<any[]>([])

const detailVisible = ref(false)
const selectedSector = ref<SectorData | null>(null)
const sectorDetail = ref<any>(null)
const detailLoading = ref(false)

const heatmapChart = ref<HTMLElement>()
let heatmapChartInstance: echarts.ECharts | null = null

// WebSocket
let ws: WebSocket | null = null

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchRankingData(),
      fetchRotationData(),
      fetchHeatmapData()
    ])
    ElMessage.success('数据刷新成功')
  } catch (error: any) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

const fetchRankingData = async () => {
  try {
    const response = await fetch(
      `/api/v1/sector/ranking?period=${period.value}&top_n=20`
    )
    const result = await response.json()
    if (result.success) {
      rankingData.value = result.data
    }
  } catch (error: any) {
    console.error('Error fetching ranking data:', error)
  }
}

const fetchRotationData = async () => {
  try {
    const response = await fetch(
      `/api/v1/sector/rotation?window=${period.value}`
    )
    const result = await response.json()
    if (result.success) {
      rotationData.value = result.data
    }
  } catch (error: any) {
    console.error('Error fetching rotation data:', error)
  }
}

const fetchHeatmapData = async () => {
  try {
    const response = await fetch('/api/v1/sector/heatmap')
    const result = await response.json()
    if (result.success) {
      heatmapData.value = result.data
      await nextTick()
      renderHeatmap()
    }
  } catch (error: any) {
    console.error('Error fetching heatmap data:', error)
  }
}

// 渲染热力图
const renderHeatmap = () => {
  if (!heatmapChart.value || heatmapData.value.length === 0) return

  if (!heatmapChartInstance) {
    heatmapChartInstance = echarts.init(heatmapChart.value)
  }

  const data = heatmapData.value.map((item, index) => [index, 0, item.value, item.name])
  const categories = heatmapData.value.map(item => item.name)

  const option: EChartsOption = {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const item = heatmapData.value[params.data[0]]
        return `${item.name}<br/>涨跌幅: ${item.value.toFixed(2)}%<br/>上涨: ${item.up_count}家<br/>下跌: ${item.down_count}家`
      }
    },
    grid: {
      height: '60%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: categories,
      splitArea: { show: true },
      axisLabel: { rotate: 45, interval: 0 }
    },
    yAxis: {
      type: 'category',
      data: ['板块'],
      splitArea: { show: true }
    },
    visualMap: {
      min: -3,
      max: 3,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#10b981', '#ffffff', '#ef4444']
      }
    },
    series: [{
      name: '涨跌幅',
      type: 'heatmap',
      data: data,
      label: {
        show: true,
        formatter: (params: any) => params.data[2].toFixed(2) + '%'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  heatmapChartInstance.setOption(option)
}

// 查看板块详情
const viewSectorDetail = async (sector: SectorData) => {
  selectedSector.value = sector
  detailVisible.value = true
  detailLoading.value = true

  try {
    const response = await fetch(
      `/api/v1/sector/detail?sector_code=${sector.sector_code}`
    )
    const result = await response.json()
    if (result.success) {
      sectorDetail.value = result
    }
  } catch (error: any) {
    ElMessage.error('获取板块详情失败')
  } finally {
    detailLoading.value = false
  }
}

// WebSocket连接
const connectWebSocket = () => {
  // 根据页面协议自动选择ws://或wss://
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws = newWebSocket(`${protocol}//${window.location.host}/ws`)

  ws.onopen = () => {
    console.log('WebSocket connected')
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'quote') {
      handleRealtimeQuote(data.data)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  ws.onclose = () => {
    setTimeout(connectWebSocket, 5000)
  }
}

const handleRealtimeQuote = (data: any) => {
  // 实时更新板块数据
  console.log('Realtime quote:', data)
}

// 视图模式切换
const handleViewModeChange = async () => {
  if (viewMode.value === 'heatmap') {
    await nextTick()
    renderHeatmap()
  }
}

// 格式化函数
const formatPercent = (percent: number) => {
  if (!percent) return '--'
  return `${percent > 0 ? '+' : ''}${percent.toFixed(2)}%`
}

const formatPrice = (value: number) => {
  return value ? value.toFixed(2) : '--'
}

const formatVolume = (value: number) => {
  if (!value) return '--'
  if (value >= 100000000) return (value / 100000000).toFixed(2) + '亿'
  if (value >= 10000) return (value / 10000).toFixed(2) + '万'
  return value.toString()
}

const getChangeClass = (change: number) => {
  if (!change) return ''
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return 'text-flat'
}

const getStrengthType = (score: number) => {
  if (score >= 50) return 'success'
  if (score >= 20) return ''
  if (score >= 0) return 'info'
  return 'danger'
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 50) return '#e6a23c'
  return '#f56c6c'
}

// 生命周期
onMounted(() => {
  fetchData()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) ws.close()
  if (heatmapChartInstance) heatmapChartInstance.dispose()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.sector-view {
  padding: $spacing-lg;

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-lg;
    padding: $spacing-md;
    background: $bg-surface;
    border-radius: $radius-md;
    border: 1px solid $border-light;

    .filters {
      display: flex;
      gap: $spacing-md;
      align-items: center;
    }
  }

  .section {
    background: $bg-surface;
    border: 1px solid $border-light;
    border-radius: $radius-lg;
    padding: $spacing-lg;
    margin-bottom: $spacing-xl;

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: $spacing-lg;

      h3 {
        margin: 0;
        font-size: $font-lg;
        color: $text-primary;
      }
    }
  }

  .clickable-rows {
    :deep(.el-table__body tr) {
      cursor: pointer;

      &:hover {
        background: $bg-hover;
      }
    }
  }

  .heatmap-container,
  .rotation-container {
    width: 100%;
    height: 500px;
  }

  .rotation-view {
    .sector-list {
      display: flex;
      flex-direction: column;
      gap: $spacing-md;
      max-height: 500px;
      overflow-y: auto;

      .sector-card {
        padding: $spacing-md;
        border-radius: $radius-md;
        border: 1px solid $border-light;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          transform: translateY(-2px);
          box-shadow: $shadow-md;
        }

        .sector-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: $spacing-sm;

          .sector-name {
            font-weight: bold;
            font-size: $font-md;
          }
        }

        .sector-metrics {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
      }

      &.hot .sector-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
      }

      &.cold .sector-card {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
      }
    }

    .signals {
      display: flex;
      flex-direction: column;
      gap: $spacing-sm;
    }
  }

  .stats-row {
    margin-bottom: $spacing-lg;

    :deep(.el-statistic) {
      text-align: center;

      .el-statistic__head {
        font-size: $font-sm;
        color: $text-secondary;
      }

      .el-statistic__content {
        font-size: $font-xl;
        font-weight: bold;
      }
    }
  }

  .text-up {
    color: #ef4444;
    font-weight: bold;
  }

  .text-down {
    color: #10b981;
    font-weight: bold;
  }

  .text-flat {
    color: $text-secondary;
  }

  .text-secondary {
    color: $text-secondary;
    font-size: $font-sm;
  }
}
</style>
