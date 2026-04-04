<template>
  <n-card class="data-management-card" hoverable>
    <template #header>
      <div class="card-header">
        <div class="card-icon">
          <n-icon size="24" color="#10b981">
            <Database />
          </n-icon>
        </div>
        <div class="card-title">
          <h3>数据管理</h3>
          <p class="card-subtitle">数据库查看与数据新鲜度监控</p>
        </div>
        <div class="card-actions">
          <n-dropdown trigger="hover" placement="bottom-end">
            <template #trigger>
              <n-button circle size="small" quaternary>
                <template #icon>
                  <n-icon><EllipsisVertical /></n-icon>
                </template>
              </n-button>
            </template>
            <template #dropdown>
              <n-doption @click="refreshData">
                <template #icon>
                  <n-icon><Refresh /></n-icon>
                </template>
                刷新数据
              </n-doption>
              <n-doption @click="exportData">
                <template #icon>
                  <n-icon><Download /></n-icon>
                </template>
                导出数据
              </n-doption>
              <n-doption @click="showSettings">
                <template #icon>
                  <n-icon><Settings /></n-icon>
                </template>
                数据设置
              </n-doption>
            </template>
          </n-dropdown>
        </div>
      </div>
    </template>
    
    <div class="card-content">
      <!-- 数据概览 -->
      <div class="data-overview">
        <h4>数据概览</h4>
        <div class="overview-grid">
          <div class="overview-item">
            <div class="item-header">
              <n-icon size="20" color="#2563eb">
                <BarChart />
              </n-icon>
              <span>总股票数</span>
            </div>
            <div class="item-value">{{ formatNumber(dataOverview.totalStocks) }}</div>
          </div>
          <div class="overview-item">
            <div class="item-header">
              <n-icon size="20" color="#10b981">
                <Calendar />
              </n-icon>
              <span>数据覆盖天数</span>
            </div>
            <div class="item-value">{{ dataOverview.coverageDays }}天</div>
          </div>
          <div class="overview-item">
            <div class="item-header">
              <n-icon size="20" color="#f59e0b">
                <Time />
              </n-icon>
              <span>最新更新</span>
            </div>
            <div class="item-value">{{ formatDateTime(dataOverview.lastUpdate) }}</div>
          </div>
          <div class="overview-item">
            <div class="item-header">
              <n-icon size="20" color="#10b981">
                <CloudUpload />
              </n-icon>
              <span>数据大小</span>
            </div>
            <div class="item-value">{{ formatFileSize(dataOverview.dataSize) }}</div>
          </div>
        </div>
      </div>
      
      <!-- 数据新鲜度监控 -->
      <div class="freshness-monitor">
        <div class="section-header">
          <h4>数据新鲜度监控</h4>
          <n-select
            v-model:value="selectedTable"
            :options="tableOptions"
            size="small"
            style="width: 150px"
          />
        </div>
        
        <div class="freshness-grid">
          <div
            v-for="item in freshnessData"
            :key="item.table"
            class="freshness-item"
            :class="{ 'freshness-good': item.freshness > 90, 'freshness-warning': item.freshness > 70 && item.freshness <= 90, 'freshness-bad': item.freshness <= 70 }"
          >
            <div class="item-table">{{ item.table }}</div>
            <div class="item-freshness">
              <div class="freshness-bar">
                <div 
                  class="freshness-fill" 
                  :style="{ width: `${item.freshness}%` }"
                ></div>
              </div>
              <span class="freshness-value">{{ item.freshness }}%</span>
            </div>
            <div class="item-status">
              <n-tag
                :type="getFreshnessTagType(item.freshness)"
                size="small"
              >
                {{ getFreshnessStatus(item.freshness) }}
              </n-tag>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 数据库详情 -->
      <div class="database-details">
        <div class="section-header">
          <h4>数据库详情</h4>
          <n-button size="small" @click="toggleDetails">
            {{ showDetails ? '收起' : '展开' }}
          </n-button>
        </div>
        
        <div v-show="showDetails" class="details-content">
          <n-data-table
            :columns="detailColumns"
            :data="databaseDetails"
            size="small"
            striped
            :pagination="{
              pageSize: 10,
              showSizePicker: true,
              showQuickJumper: true
            }"
          />
        </div>
      </div>
      
      <!-- 数据质量热力图 -->
      <div class="quality-heatmap">
        <div class="section-header">
          <h4>数据质量热力图</h4>
          <n-select
            v-model:value="selectedMetric"
            :options="metricOptions"
            size="small"
            style="width: 150px"
          />
        </div>
        
        <div class="heatmap-container">
          <BaseChart
            :option="heatmapOption"
            width="100%"
            height="300px"
            :loading="heatmapLoading"
          />
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="card-loading">
      <n-spin size="large" />
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { NCard, NIcon, NButton, NDropdown, NDropdownOption, NSelect, NTag, NDataTable, NSpin } from 'naive-ui'
import { EllipsisVertical, Refresh, Download, Settings, Database, BarChart, Calendar, Time, CloudUpload } from '@vicons/ionicons5'
import BaseChart from '../charts/BaseChart.vue'
import { formatNumber, formatDateTime, formatFileSize } from '@/utils/format'
import type { EChartsOption } from 'echarts'

interface DataOverview {
  totalStocks: number
  coverageDays: number
  lastUpdate: Date
  dataSize: number
}

interface FreshnessItem {
  table: string
  freshness: number
  recordCount: number
  missingCount: number
}

interface DatabaseDetail {
  tableName: string
  recordCount: number
  lastUpdate: Date
  size: string
  status: 'active' | 'inactive' | 'updating'
}

interface Props {
  refreshAction?: () => Promise<void>
  exportAction?: () => Promise<void>
  settingsAction?: () => void
}

const props = defineProps<Props>()

const emit = defineEmits<{
  refresh: []
  export: []
  settings: []
}>()

// 响应式数据
const loading = ref(false)
const showDetails = ref(false)
const selectedTable = ref('all')
const selectedMetric = ref('completeness')
const heatmapLoading = ref(false)

const dataOverview = ref<DataOverview>({
  totalStocks: 0,
  coverageDays: 0,
  lastUpdate: new Date(),
  dataSize: 0
})

const freshnessData = ref<FreshnessItem[]>([])
const databaseDetails = ref<DatabaseDetail[]>([])

// 选项配置
const tableOptions = [
  { label: '全部表', value: 'all' },
  { label: '股票基础表', value: 'stocks' },
  { label: '日线数据表', value: 'daily' },
  { label: '分钟线表', value: 'minute' },
  { label: '财务数据表', value: 'financial' },
  { label: '因子数据表', value: 'factors' }
]

const metricOptions = [
  { label: '完整度', value: 'completeness' },
  { label: '准确性', value: 'accuracy' },
  { label: '一致性', value: 'consistency' },
  { label: '及时性', value: 'timeliness' }
]

// 表格列配置
const detailColumns = computed(() => [
  { title: '表名', key: 'tableName', width: 150 },
  { title: '记录数', key: 'recordCount', width: 100 },
  { title: '最后更新', key: 'lastUpdate', width: 150, render: (row: DatabaseDetail) => formatDateTime(row.lastUpdate) },
  { title: '大小', key: 'size', width: 100 },
  { title: '状态', key: 'status', width: 100, render: (row: DatabaseDetail) => getStatusTag(row.status) }
])

// 热力图配置
const heatmapOption = computed<EChartsOption>(() => {
  if (freshnessData.value.length === 0) return {}
  
  // 生成热力图数据
  const data = freshnessData.value.map(item => [
    item.table,
    item.freshness
  ])
  
  return {
    title: { text: '数据质量热力图' },
    tooltip: { 
      trigger: 'item',
      formatter: (params: any) => {
        const [table, value] = params.data
        return `${table}: ${value}%`
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item[0]),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      inRange: {
        color: ['#313695'],
        symbol: 'rect',
        symbolSize: [120, 20],
        symbolOffset: [0, -20]
      },
      outOfRange: {
        color: ['#ccc']
      }
    },
    series: [
      {
        name: '数据质量',
        type: 'heatmap',
        data: data.map((item, index) => [index, 0, item[1]]),
        label: {
          show: true
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

// 方法
const getFreshnessTagType = (freshness: number) => {
  if (freshness > 90) return 'success'
  if (freshness > 70) return 'warning'
  return 'error'
}

const getFreshnessStatus = (freshness: number) => {
  if (freshness > 90) return '优秀'
  if (freshness > 80) return '良好'
  if (freshness > 70) return '一般'
  return '较差'
}

const getStatusTag = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    inactive: 'error',
    updating: 'warning'
  }
  return typeMap[status] || 'default'
}

const refreshData = async () => {
  loading.value = true
  try {
    if (props.refreshAction) {
      await props.refreshAction()
    }
    await loadData()
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    loading.value = false
  }
}

const exportData = async () => {
  if (props.exportAction) {
    emit('export')
    await props.exportAction()
  }
}

const showSettings = () => {
  if (props.settingsAction) {
    emit('settings')
    props.settingsAction()
  }
}

const toggleDetails = () => {
  showDetails.value = !showDetails.value
}

const loadData = async () => {
  // 模拟数据加载
  dataOverview.value = {
    totalStocks: 4876,
    coverageDays: 365,
    lastUpdate: new Date(Date.now() - 2 * 60 * 60 * 1000),
    dataSize: 2.3 * 1024 * 1024 * 1024 // 2.3GB
  }
  
  freshnessData.value = [
    { table: '股票基础', freshness: 95, recordCount: 4876, missingCount: 244 },
    { table: '日线数据', freshness: 88, recordCount: 1240000, missingCount: 148800 },
    { table: '分钟线', freshness: 92, recordCount: 37200000, missingCount: 2976000 },
    { table: '财务数据', freshness: 85, recordCount: 4876, missingCount: 731 },
    { table: '因子数据', freshness: 90, recordCount: 1240000, missingCount: 124000 }
  ]
  
  databaseDetails.value = [
    { tableName: 'stock_basic', recordCount: 4876, lastUpdate: new Date(), size: '125MB', status: 'active' },
    { tableName: 'daily_data', recordCount: 1240000, lastUpdate: new Date(Date.now() - 2 * 60 * 60 * 1000), size: '1.8GB', status: 'active' },
    { tableName: 'minute_data', recordCount: 37200000, lastUpdate: new Date(Date.now() - 30 * 60 * 1000), size: '15.2GB', status: 'active' },
    { tableName: 'financial_data', recordCount: 4876, lastUpdate: new Date(Date.now() - 24 * 60 * 60 * 1000), size: '245MB', status: 'updating' },
    { tableName: 'factor_data', recordCount: 1240000, lastUpdate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), size: '3.1GB', status: 'active' }
  ]
}

// 生命周期
onMounted(() => {
  loadData()
})

// 监听选择变化
watch([selectedTable, selectedMetric], () => {
  heatmapLoading.value = true
  setTimeout(() => {
    heatmapLoading.value = false
  }, 500)
})
</script>

<style lang="scss" scoped>
.data-management-card {
  height: 100%;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .card-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .card-title {
      flex: 1;
      margin-left: 12px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #f8fafc;
        line-height: 1.2;
      }
      
      .card-subtitle {
        margin: 4px 0 0 0;
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.2;
      }
    }
    
    .card-actions {
      margin-left: auto;
    }
  }
  
  .card-content {
    position: relative;
    
    .section-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      
      h4 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: #f8fafc;
      }
    }
    
    .data-overview {
      margin-bottom: 24px;
      
      .overview-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        
        .overview-item {
          padding: 16px;
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 8px;
          
          .item-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            
            span {
              font-size: 12px;
              color: #94a3b8;
            }
          }
          
          .item-value {
            font-size: 20px;
            font-weight: 600;
            color: #f8fafc;
          }
        }
      }
    }
    
    .freshness-monitor {
      margin-bottom: 24px;
      
      .freshness-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 12px;
        
        .freshness-item {
          padding: 16px;
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 8px;
          
          .item-table {
            font-size: 14px;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 8px;
          }
          
          .item-freshness {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            
            .freshness-bar {
              flex: 1;
              height: 8px;
              background: rgba(148, 163, 184, 0.2);
              border-radius: 4px;
              overflow: hidden;
              
              .freshness-fill {
                height: 100%;
                background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
                transition: width 0.3s ease;
              }
            }
            
            .freshness-value {
              font-size: 16px;
              font-weight: 600;
              min-width: 40px;
            }
          }
          
          .item-status {
            margin-top: 8px;
          }
          
          &.freshness-good {
            border-color: rgba(16, 185, 129, 0.3);
            
            .freshness-fill {
              background: linear-gradient(90deg, #10b981 0%, #10b981 100%);
            }
          }
          
          &.freshness-warning {
            border-color: rgba(245, 158, 11, 0.3);
            
            .freshness-fill {
              background: linear-gradient(90deg, #f59e0b 0%, #f59e0b 100%);
            }
          }
          
          &.freshness-bad {
            border-color: rgba(239, 68, 68, 0.3);
            
            .freshness-fill {
              background: linear-gradient(90deg, #ef4444 0%, #ef4444 100%);
            }
          }
        }
      }
    }
    
    .database-details {
      margin-bottom: 24px;
      
      .details-content {
        margin-top: 16px;
      }
    }
    
    .quality-heatmap {
      .heatmap-container {
        border-radius: 8px;
        overflow: hidden;
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(148, 163, 184, 0.1);
      }
    }
  }
  
  .card-loading {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(2px);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
  }
}
</style>