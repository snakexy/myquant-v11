<template>
  <div class="overview-card data-freshness-heatmap">
    <div class="card-icon">
      🔥
    </div>
    <div class="card-content">
      <h3>数据新鲜度热力图</h3>
      <div class="card-value">{{ overallFreshness }}%</div>
      <div class="card-change" :class="getTrendClass(trend)">
        <i :class="getTrendIcon(trend)"></i>
        <span>{{ trendText }}</span>
      </div>
    </div>
    
    <div v-if="!isMinimized" class="heatmap-details">
      <!-- 时间范围选择器 -->
      <div class="time-range-selector">
        <div class="section-title">时间范围选择</div>
        <div class="time-range-controls">
          <div class="preset-buttons">
            <button
              v-for="preset in timePresets"
              :key="preset.value"
              class="preset-btn"
              :class="{ active: selectedTimeRange === preset.value }"
              @click="selectTimeRange(preset.value)"
            >
              {{ preset.label }}
            </button>
          </div>
          <div class="custom-range">
            <div class="date-inputs">
              <input
                type="date"
                v-model="customStartDate"
                class="date-input"
                :max="customEndDate || today"
              />
              <span class="date-separator">至</span>
              <input
                type="date"
                v-model="customEndDate"
                class="date-input"
                :min="customStartDate"
                :max="today"
              />
            </div>
            <button class="apply-btn" @click="applyCustomRange">应用</button>
          </div>
        </div>
      </div>
      
      <!-- 板块数据新鲜度 -->
      <div class="section-title">板块数据新鲜度</div>
      <div class="sector-freshness">
        <div v-for="sector in sectorFreshness" :key="sector.name" class="sector-item">
          <div class="sector-info">
            <span class="sector-name">{{ sector.name }}</span>
            <span class="freshness-percent">{{ sector.freshness }}%</span>
          </div>
          <div class="freshness-bar">
            <div
              class="freshness-fill"
              :style="{ width: sector.freshness + '%' }"
              :class="getFreshnessClass(sector.freshness)"
            ></div>
          </div>
          <div class="sector-details">
            <span class="detail-item">更新: {{ formatTime(sector.lastUpdate) }}</span>
            <span class="detail-item">缺失: {{ sector.missingCount }}</span>
          </div>
        </div>
      </div>
      
      <!-- 时间分布热力图 -->
      <div class="section-title">时间分布热力图</div>
      <div class="time-heatmap">
        <div class="heatmap-legend">
          <span class="legend-item">
            <div class="legend-color heat-minimal"></div>
            <span>低</span>
          </span>
          <span class="legend-item">
            <div class="legend-color heat-low"></div>
            <span>中低</span>
          </span>
          <span class="legend-item">
            <div class="legend-color heat-medium"></div>
            <span>中高</span>
          </span>
          <span class="legend-item">
            <div class="legend-color heat-high"></div>
            <span>高</span>
          </span>
        </div>
        <div v-for="timeSlot in timeDistribution" :key="timeSlot.time" class="time-slot">
          <div class="time-label">{{ timeSlot.time }}</div>
          <div class="heat-bar">
            <div
              v-for="(block, index) in timeSlot.blocks"
              :key="index"
              class="heat-block"
              :class="getHeatClass(block.intensity)"
              :title="`强度: ${(block.intensity * 100).toFixed(1)}%`"
            ></div>
          </div>
          <div class="time-stats">{{ timeSlot.stats }}</div>
        </div>
      </div>
      
      <!-- 数据质量统计 -->
      <div class="section-title">数据质量统计</div>
      <div class="quality-stats">
        <div class="stat-item">
          <div class="stat-label">总数据量</div>
          <div class="stat-value">{{ formatNumber(totalDataCount) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">完整数据</div>
          <div class="stat-value">{{ formatNumber(completeDataCount) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">缺失数据</div>
          <div class="stat-value">{{ formatNumber(missingDataCount) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">异常数据</div>
          <div class="stat-value">{{ formatNumber(anomalyCount) }}</div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="heatmap-actions">
        <button class="action-btn" @click="filterBySector">
          <i class="fas fa-filter"></i>
          <span>按板块筛选</span>
        </button>
        <button class="action-btn" @click="filterByTime">
          <i class="fas fa-clock"></i>
          <span>按时间筛选</span>
        </button>
        <button class="action-btn" @click="showAnomalies">
          <i class="fas fa-exclamation-triangle"></i>
          <span>异常数据</span>
        </button>
        <button class="action-btn" @click="exportData">
          <i class="fas fa-download"></i>
          <span>导出报告</span>
        </button>
        <button class="action-btn" @click="refreshData">
          <i class="fas fa-sync-alt"></i>
          <span>刷新数据</span>
        </button>
      </div>
    </div>
    
    <div class="card-progress">
      <div class="progress-bar" :style="{ width: overallFreshness + '%' }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

// 响应式数据
const isMinimized = ref(false)
const overallFreshness = ref(94.5)
const trend = ref(2.3)
const selectedTimeRange = ref('1year')

// 时间范围预设
const timePresets = ref([
  { label: '最近1年', value: '1year' },
  { label: '最近6个月', value: '6months' },
  { label: '最近3个月', value: '3months' },
  { label: '最近1个月', value: '1month' },
  { label: '最近1周', value: '1week' }
])

// 自定义时间范围
const customStartDate = ref('')
const customEndDate = ref('')
const today = computed(() => new Date().toISOString().split('T')[0])

// 数据统计
const totalDataCount = ref(12500000)
const completeDataCount = ref(11875000)
const missingDataCount = ref(625000)
const anomalyCount = ref(12500)

// 板块新鲜度数据
const sectorFreshness = ref([
  {
    name: '实时行情',
    freshness: 99.8,
    lastUpdate: new Date(Date.now() - 5 * 60 * 1000),
    missingCount: 12
  },
  {
    name: '日K线数据',
    freshness: 95.2,
    lastUpdate: new Date(Date.now() - 2 * 60 * 60 * 1000),
    missingCount: 234
  },
  {
    name: '技术指标',
    freshness: 94.7,
    lastUpdate: new Date(Date.now() - 30 * 60 * 1000),
    missingCount: 156
  },
  {
    name: '基本面数据',
    freshness: 97.3,
    lastUpdate: new Date(Date.now() - 24 * 60 * 60 * 1000),
    missingCount: 45
  },
  {
    name: '新闻数据',
    freshness: 92.1,
    lastUpdate: new Date(Date.now() - 6 * 60 * 60 * 1000),
    missingCount: 89
  }
])

// 时间分布热力图数据
const timeDistribution = ref([
  { time: '00:00', blocks: generateHeatBlocks(0.2), stats: '2.3K' },
  { time: '04:00', blocks: generateHeatBlocks(0.3), stats: '5.1K' },
  { time: '08:00', blocks: generateHeatBlocks(0.8), stats: '15.2K' },
  { time: '12:00', blocks: generateHeatBlocks(0.9), stats: '18.7K' },
  { time: '16:00', blocks: generateHeatBlocks(0.8), stats: '16.4K' },
  { time: '20:00', blocks: generateHeatBlocks(0.4), stats: '8.9K' }
])

// 生成热力图块
function generateHeatBlocks(baseIntensity: number) {
  const blocks = []
  for (let i = 0; i < 16; i++) {
    // 添加一些随机变化
    const variation = (Math.random() - 0.5) * 0.2
    const intensity = Math.max(0, Math.min(1, baseIntensity + variation))
    blocks.push({ intensity })
  }
  return blocks
}

// 获取新鲜度等级样式类
function getFreshnessClass(freshness: number) {
  if (freshness >= 98) return 'excellent'
  if (freshness >= 95) return 'good'
  if (freshness >= 90) return 'fair'
  return 'poor'
}

// 获取热力图块样式类
function getHeatClass(intensity: number) {
  if (intensity >= 0.8) return 'heat-high'
  if (intensity >= 0.5) return 'heat-medium'
  if (intensity >= 0.2) return 'heat-low'
  return 'heat-minimal'
}

// 获取趋势样式类
function getTrendClass(trend: number) {
  if (trend > 0) return 'up'
  if (trend < 0) return 'down'
  return 'stable'
}

// 获取趋势图标
function getTrendIcon(trend: number) {
  if (trend > 0) return 'fas fa-arrow-up'
  if (trend < 0) return 'fas fa-arrow-down'
  return 'fas fa-minus'
}

// 计算趋势文本
const trendText = computed(() => {
  if (trend.value > 0) return `+${trend.value.toFixed(1)}%`
  if (trend.value < 0) return `${trend.value.toFixed(1)}%`
  return '0%'
})

// 格式化时间
function formatTime(date: Date) {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

// 格式化数字
function formatNumber(num: number) {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

// 方法
const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}

const closeHeatmap = () => {
  console.log('关闭数据新鲜度热力图')
}

const selectTimeRange = (range: string) => {
  selectedTimeRange.value = range
  loadFreshnessData(range)
}

const applyCustomRange = () => {
  if (customStartDate.value && customEndDate.value) {
    loadFreshnessData('custom', {
      startDate: customStartDate.value,
      endDate: customEndDate.value
    })
  }
}

const filterBySector = () => {
  console.log('按板块筛选')
  // 实现板块筛选逻辑
}

const filterByTime = () => {
  console.log('按时间筛选')
  // 实现时间筛选逻辑
}

const showAnomalies = () => {
  console.log('显示异常数据')
  // 实现异常数据显示逻辑
}

const exportData = () => {
  console.log('导出数据报告')
  // 实现数据导出逻辑
}

const refreshData = async () => {
  console.log('刷新数据')
  await loadFreshnessData(selectedTimeRange.value)
}

// 加载新鲜度数据
const loadFreshnessData = async (timeRange: string, customRange?: { startDate: string, endDate: string }) => {
  try {
    const params = new URLSearchParams()
    params.append('timeRange', timeRange)
    if (customRange) {
      params.append('startDate', customRange.startDate)
      params.append('endDate', customRange.endDate)
    }
    
    const response = await fetch(`/api/v1/data-management/freshness/status?${params.toString()}`)
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        updateFreshnessData(data.data)
      }
    }
  } catch (error) {
    console.error('获取数据新鲜度失败:', error)
  }
}

// 更新新鲜度数据
function updateFreshnessData(data: any) {
  if (data.overallScore !== undefined) {
    overallFreshness.value = data.overallScore
  }
  
  if (data.freshnessDetails && data.freshnessDetails.length > 0) {
    updateSectorFreshness(data.freshnessDetails)
  }
  
  if (data.totalDataCount !== undefined) {
    totalDataCount.value = data.totalDataCount
  }
  
  if (data.completeDataCount !== undefined) {
    completeDataCount.value = data.completeDataCount
  }
  
  if (data.missingDataCount !== undefined) {
    missingDataCount.value = data.missingDataCount
  }
  
  if (data.anomalyCount !== undefined) {
    anomalyCount.value = data.anomalyCount
  }
}

// 初始化数据
onMounted(async () => {
  // 设置默认时间范围为最近1年
  const oneYearAgo = new Date()
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1)
  customStartDate.value = oneYearAgo.toISOString().split('T')[0]
  customEndDate.value = today.value
  
  // 加载初始数据
  await loadFreshnessData('1year')
})

// 更新板块新鲜度数据
function updateSectorFreshness(freshnessDetails: any[]) {
  freshnessDetails.forEach(detail => {
    const sector = sectorFreshness.value.find(s => s.name === detail.category)
    if (sector) {
      sector.freshness = detail.score
      sector.lastUpdate = new Date(detail.lastUpdate)
      sector.missingCount = detail.issueCount || 0
    }
  })
}
</script>

<style lang="scss" scoped>
// 使用与概览卡片完全一致的样式
.overview-card {
  position: relative;
  padding: 24px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(8px) saturate(120%);
  -webkit-backdrop-filter: blur(8px) saturate(120%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  box-shadow:
    0 8px 32px rgba(124, 58, 237, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px) saturate(150%);
    -webkit-backdrop-filter: blur(12px) saturate(150%);
    box-shadow:
      0 12px 40px rgba(124, 58, 237, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.15);
  }
  
  .card-icon {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(124, 58, 237, 0.1);
    border-radius: 12px;
    color: var(--secondary);
    font-size: 24px;
  }
  
  .card-content {
    h3 {
      margin: 0 0 12px 0;
      font-size: 16px;
      font-weight: 500;
      color: var(--text-secondary);
    }
    
    .card-value {
      font-size: 32px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 12px;
    }
    
    .card-change {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      font-weight: 500;
      
      &.up {
        color: var(--market-rise);
      }
      
      &.down {
        color: var(--market-fall);
      }
      
      &.stable {
        color: var(--text-secondary);
      }
    }
  }
  
  .card-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    
    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, var(--secondary), var(--primary));
      transition: width 0.3s ease;
    }
  }
  
  // 热力图详情内容
  .heatmap-details {
    margin-top: 20px;
    
    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 16px;
    }
    
    .time-range-selector {
      margin-bottom: 24px;
      
      .time-range-controls {
        .preset-buttons {
          display: flex;
          gap: 8px;
          margin-bottom: 16px;
          flex-wrap: wrap;
          
          .preset-btn {
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background: rgba(255, 255, 255, 0.1);
              border-color: rgba(255, 255, 255, 0.2);
            }
            
            &.active {
              background: rgba(124, 58, 237, 0.2);
              border-color: rgba(124, 58, 237, 0.4);
              color: var(--secondary);
            }
          }
        }
        
        .custom-range {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .date-inputs {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .date-input {
              padding: 6px 12px;
              background: rgba(255, 255, 255, 0.05);
              border: 1px solid rgba(255, 255, 255, 0.1);
              border-radius: 4px;
              color: var(--text-primary);
              font-size: 12px;
              
              &:focus {
                outline: none;
                border-color: rgba(124, 58, 237, 0.4);
                background: rgba(255, 255, 255, 0.08);
              }
            }
            
            .date-separator {
              color: var(--text-secondary);
              font-size: 12px;
            }
          }
          
          .apply-btn {
            padding: 6px 16px;
            background: rgba(124, 58, 237, 0.2);
            border: 1px solid rgba(124, 58, 237, 0.4);
            border-radius: 4px;
            color: var(--secondary);
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background: rgba(124, 58, 237, 0.3);
              border-color: rgba(124, 58, 237, 0.6);
            }
          }
        }
      }
    }
    
    .sector-freshness {
      margin-bottom: 24px;
      
      .sector-item {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        
        .sector-info {
          width: 80px;
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          
          .sector-name {
            font-size: 14px;
            color: var(--text-primary);
            font-weight: 500;
          }
          
          .freshness-percent {
            font-size: 12px;
            color: var(--text-secondary);
          }
        }
        
        .freshness-bar {
          flex: 1;
          height: 16px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          overflow: hidden;
          margin-left: 16px;
          
          .freshness-fill {
            height: 100%;
            transition: width 0.5s ease;
           
            &.excellent {
              background: linear-gradient(90deg, #10b981, #34d399);
            }
           
            &.good {
              background: linear-gradient(90deg, #3b82f6, #60a5fa);
            }
           
            &.fair {
              background: linear-gradient(90deg, #f59e0b, #fbbf24);
            }
           
            &.poor {
              background: linear-gradient(90deg, #ef4444, #f87171);
            }
          }
        }
        
        .sector-details {
          display: flex;
          gap: 16px;
          margin-top: 8px;
          margin-left: 96px;
          
          .detail-item {
            font-size: 11px;
            color: var(--text-secondary);
          }
        }
      }
    }
    
    .time-heatmap {
      margin-bottom: 24px;
      
      .heatmap-legend {
        display: flex;
        gap: 16px;
        margin-bottom: 16px;
        justify-content: center;
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: var(--text-secondary);
          
          .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 2px;
            
            &.heat-minimal {
              background: rgba(124, 58, 237, 0.1);
            }
            
            &.heat-low {
              background: rgba(124, 58, 237, 0.3);
            }
            
            &.heat-medium {
              background: rgba(124, 58, 237, 0.5);
            }
            
            &.heat-high {
              background: rgba(124, 58, 237, 0.8);
            }
          }
        }
      }
      
      .time-slot {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        
        .time-label {
          width: 60px;
          font-size: 12px;
          color: var(--text-secondary);
        }
        
        .heat-bar {
          display: flex;
          gap: 2px;
          flex: 1;
          
          .heat-block {
            width: 12px;
            height: 16px;
            border-radius: 2px;
            cursor: pointer;
            transition: all 0.2s ease;
           
            &:hover {
              transform: scale(1.1);
              z-index: 1;
            }
           
            &.heat-high {
              background: rgba(124, 58, 237, 0.8);
            }
           
            &.heat-medium {
              background: rgba(124, 58, 237, 0.5);
            }
           
            &.heat-low {
              background: rgba(124, 58, 237, 0.3);
            }
           
            &.heat-minimal {
              background: rgba(124, 58, 237, 0.1);
            }
          }
        }
        
        .time-stats {
          width: 50px;
          font-size: 11px;
          color: var(--text-secondary);
          text-align: right;
        }
      }
    }
    
    .quality-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
      
      .stat-item {
        padding: 16px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        text-align: center;
        
        .stat-label {
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 8px;
        }
        
        .stat-value {
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
      }
    }
    
    .heatmap-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
      
      .action-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: var(--text-primary);
        font-size: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
}
</style>