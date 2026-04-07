<template>
  <div class="advanced-features-demo">
    <div class="page-header">
      <h1>高级功能演示</h1>
      <p>Advanced Features Demo</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：高级K线图 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>高级K线图（带BOLL和RSI）</span>
          </template>

          <LazyChart
            chart-type="kline-advanced"
            :symbol="selectedStock"
            period="day"
            height="600px"
            @ready="onChartReady"
          />
        </el-card>
      </el-col>

      <!-- 右侧：板块轮动历史 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>板块轮动历史</span>
          </template>

          <div class="sector-history-panel">
            <el-select
              v-model="selectedSector"
              placeholder="选择板块"
              style="width: 100%; margin-bottom: 16px"
              @change="loadSectorHistory"
            >
              <el-option
                v-for="sector in sectors"
                :key="sector.code"
                :label="sector.name"
                :value="sector.code"
              />
            </el-select>

            <div v-if="sectorHistory.length > 0" class="history-chart">
              <EChart
                ref="historyChartRef"
                :option="historyChartOption"
                :height="300"
              />
            </div>

            <div v-else class="empty-state">
              <p>请选择板块查看历史趋势</p>
            </div>

            <div v-if="sectorTrend" class="trend-info">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item label="平均强度">
                  {{ sectorTrend.avg_strength }}
                </el-descriptions-item>
                <el-descriptions-item label="当前强度">
                  {{ sectorTrend.current_strength }}
                </el-descriptions-item>
                <el-descriptions-item label="最高强度">
                  {{ sectorTrend.max_strength }}
                </el-descriptions-item>
                <el-descriptions-item label="趋势">
                  <el-tag :type="trendType">{{ trendText }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>

        <!-- 自定义板块管理 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>自定义板块</span>
          </template>

          <CustomSectorManager />
        </el-card>
      </el-col>
    </el-row>

    <!-- 缓存统计 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>缓存统计</span>
            <el-button style="float: right" size="small" @click="refreshCacheStats">
            刷新
            </el-button>
          </template>

          <el-descriptions :column="4" border>
            <el-descriptions-item label="缓存项数量">
              {{ cacheStats.size }}
            </el-descriptions-item>
            <el-descriptions-item label="占用内存">
              {{ formatBytes(cacheStats.totalMemory) }}
            </el-descriptions-item>
            <el-descriptions-item label="图表组件">
              已加载
            </el-descriptions-item>
            <el-descriptions-item label="懒加载">
              已启用
            </el-descriptions-item>
          </el-descriptions>

          <div style="margin-top: 16px">
            <el-button size="small" @click="clearKlineCache">
              清除K线缓存
            </el-button>
            <el-button size="small" @click="clearIndicatorCache">
              清除指标缓存
            </el-button>
            <el-button size="small" @click="clearSectorCache">
              清除板块缓存
            </el-button>
            <el-button size="small" type="danger" @click="clearAllCache">
              清除所有缓存
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import LazyChart from '@/components/common/LazyChart.vue'
import CustomSectorManager from '@/components/sector/CustomSectorManager.vue'
import EChart from '@/components/common/EChart.vue'
import {
  getCacheStats,
  clearCacheByPrefix,
  clearAllCache
} from '@/utils/cacheManager'

// 选中的股票
const selectedStock = ref('600519')

// 板块列表
const sectors = ref([
  { code: 'BK0001', name: '金融' },
  { code: 'BK0002', name: '科技' },
  { code: 'BK0003', name: '医药' },
  { code: 'BK0004', name: '消费' },
  { code: 'BK0005', name: '能源' }
])

// 选中的板块
const selectedSector = ref('BK0001')

// 板块历史数据
const sectorHistory = ref<any[]>([])
const sectorTrend = ref<any>(null)
const historyChartRef = ref()

// 缓存统计
const cacheStats = ref({
  size: 0,
  keys: [],
  totalMemory: 0
})

// 趋势类型
const trendType = computed(() => {
  if (!sectorTrend.value) return 'info'
  const trend = sectorTrend.value.trend
  if (trend === 'up') return 'success'
  if (trend === 'down') return 'danger'
  return 'info'
})

// 趋势文本
const trendText = computed(() => {
  if (!sectorTrend.value) return '--'
  const trend = sectorTrend.value.trend
  if (trend === 'up') return '上升趋势'
  if (trend === 'down') return '下降趋势'
  return '平稳'
})

// 历史图表配置
const historyChartOption = computed(() => {
  if (sectorHistory.value.length === 0) {
    return {}
  }

  const dates = sectorHistory.value.map(item => {
    const date = new Date(item.timestamp)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`
  })
  const strength = sectorHistory.value.map(item => item.strength_score)
  const upRatio = sectorHistory.value.map(item => item.up_ratio)

  return {
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['强度得分', '上涨占比'],
      textStyle: { color: '#cbd5e1' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#cbd5e1', rotate: 45 }
    },
    yAxis: [
      {
        type: 'value',
        name: '强度得分',
        axisLine: { lineStyle: { color: '#475569' } },
        splitLine: { lineStyle: { color: 'rgba(71, 85, 105, 0.3)' } },
        axisLabel: { color: '#cbd5e1' }
      },
      {
        type: 'value',
        name: '上涨占比(%)',
        axisLine: { lineStyle: { color: '#475569' } },
        splitLine: { show: false },
        axisLabel: { color: '#cbd5e1' }
      }
    ],
    series: [
      {
        name: '强度得分',
        type: 'line',
        data: strength,
        smooth: true,
        lineStyle: { color: '#8b5cf6', width: 2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
              { offset: 1, color: 'rgba(139, 92, 246, 0.05)' }
            ]
          }
        }
      },
      {
        name: '上涨占比',
        type: 'line',
        yAxisIndex: 1,
        data: upRatio,
        smooth: true,
        lineStyle: { color: '#10b981', width: 2 }
      }
    ]
  }
})

// 图表准备就绪
const onChartReady = () => {
  console.log('K线图已加载')
}

// 加载板块历史
const loadSectorHistory = async () => {
  try {
    const response = await fetch(
      `/api/sector/history/${selectedSector.value}?days=7`
    )
    const result = await response.json()

    if (result.success) {
      sectorHistory.value = result.data
    }

    // 加载趋势分析
    const trendResponse = await fetch(
      `/api/sector/history/${selectedSector.value}/trend?days=7`
    )
    const trendResult = await trendResponse.json()

    if (trendResult.success) {
      sectorTrend.value = trendResult.data
    }
  } catch (error) {
    console.error('Failed to load sector history:', error)
  }
}

// 刷新缓存统计
const refreshCacheStats = () => {
  cacheStats.value = getCacheStats()
}

// 清除K线缓存
const clearKlineCache = () => {
  clearCacheByPrefix('kline')
  ElMessage.success('K线缓存已清除')
  refreshCacheStats()
}

// 清除指标缓存
const clearIndicatorCache = () => {
  clearCacheByPrefix('indicators')
  ElMessage.success('指标缓存已清除')
  refreshCacheStats()
}

// 清除板块缓存
const clearSectorCache = () => {
  clearCacheByPrefix('sector')
  ElMessage.success('板块缓存已清除')
  refreshCacheStats()
}

// 清除所有缓存
const clearAllCacheFn = () => {
  clearAllCache()
  ElMessage.success('所有缓存已清除')
  refreshCacheStats()
}

const clearAllCache = () => {
  clearAllCacheFn()
}

// 格式化字节
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 初始化
onMounted(() => {
  loadSectorHistory()
  refreshCacheStats()
})
</script>

<style scoped lang="scss">
.advanced-features-demo {
  padding: 20px;

  .page-header {
    text-align: center;
    margin-bottom: 30px;

    h1 {
      font-size: 28px;
      color: #f8fafc;
      margin-bottom: 8px;
    }

    p {
      font-size: 14px;
      color: #94a3b8;
    }
  }

  .sector-history-panel {
    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 200px;
      color: #94a3b8;
    }

    .trend-info {
      margin-top: 16px;
    }
  }
}
</style>
