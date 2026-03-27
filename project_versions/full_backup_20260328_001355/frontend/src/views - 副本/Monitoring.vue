<template>
  <div class="monitoring-page">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-stream-overlay"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">实时监控</h1>
          <p class="page-subtitle">全方位量化交易实时监控系统</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="createMonitor">
              <i class="fas fa-plus"></i>
              <span>新建监控</span>
            </button>
            <button class="secondary-btn" @click="showAlerts">
              <i class="fas fa-bell"></i>
              <span>预警管理</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 监控统计 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card" v-for="stat in monitorStats" :key="stat.id">
            <div class="stat-icon">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
            <div class="stat-trend" :class="stat.trend">
              <i :class="getTrendIcon(stat.trend)"></i>
              <span>{{ stat.change }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 多屏监控 -->
      <section class="multi-screen-section">
        <div class="section-header">
          <h2>多屏监控</h2>
          <div class="layout-controls">
            <div class="layout-selector">
              <button 
                v-for="layout in screenLayouts" 
                :key="layout.id"
                class="layout-btn"
                :class="{ active: currentLayout === layout.id }"
                @click="changeLayout(layout.id)"
              >
                <i :class="layout.icon"></i>
                <span>{{ layout.name }}</span>
              </button>
            </div>
            <div class="refresh-control">
              <button class="refresh-btn" @click="refreshData">
                <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>
              </button>
              <span class="refresh-interval">{{ refreshInterval }}秒</span>
            </div>
          </div>
        </div>
        
        <div class="monitoring-grid" :class="`layout-${currentLayout}`">
          <div 
            v-for="screen in monitoringScreens" 
            :key="screen.id"
            class="monitor-screen"
            @click="expandScreen(screen)"
          >
            <div class="screen-header">
              <div class="screen-info">
                <h3>{{ screen.title }}</h3>
                <p>{{ screen.subtitle }}</p>
              </div>
              <div class="screen-status" :class="screen.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ getStatusText(screen.status) }}</span>
              </div>
            </div>
            
            <div class="screen-content">
              <div class="chart-container" :id="`chart-${screen.id}`"></div>
              
              <div class="screen-metrics">
                <div class="metric-item" v-for="metric in screen.metrics" :key="metric.name">
                  <span class="metric-name">{{ metric.name }}</span>
                  <span class="metric-value" :class="getMetricClass(metric.value, metric.type)">
                    {{ formatMetric(metric.value, metric.type) }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="screen-actions">
              <button class="action-btn" @click.stop="configureScreen(screen)">
                <i class="fas fa-cog"></i>
              </button>
              <button class="action-btn" @click.stop="fullscreenScreen(screen)">
                <i class="fas fa-expand"></i>
              </button>
              <button class="action-btn" @click.stop="duplicateScreen(screen)">
                <i class="fas fa-copy"></i>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 预警墙 -->
      <section class="alerts-section">
        <div class="section-header">
          <h2>预警墙</h2>
          <div class="alert-controls">
            <div class="filter-tabs">
              <button 
                v-for="filter in alertFilters" 
                :key="filter.id"
                class="filter-tab"
                :class="{ active: activeAlertFilter === filter.id }"
                @click="activeAlertFilter = filter.id"
              >
                {{ filter.name }}
                <span class="alert-count">{{ filter.count }}</span>
              </button>
            </div>
            <button class="clear-btn" @click="clearAlerts">
              <i class="fas fa-trash"></i>
              <span>清除全部</span>
            </button>
          </div>
        </div>
        
        <div class="alerts-wall">
          <div 
            v-for="alert in filteredAlerts" 
            :key="alert.id"
            class="alert-card"
            :class="alert.level"
          >
            <div class="alert-header">
              <div class="alert-icon">
                <i :class="getAlertIcon(alert.level)"></i>
              </div>
              <div class="alert-info">
                <h4>{{ alert.title }}</h4>
                <p>{{ alert.description }}</p>
              </div>
              <div class="alert-time">
                {{ formatTime(alert.timestamp) }}
              </div>
            </div>
            
            <div class="alert-content">
              <div class="alert-details">
                <div class="detail-item">
                  <span class="detail-label">触发条件:</span>
                  <span class="detail-value">{{ alert.condition }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">当前值:</span>
                  <span class="detail-value">{{ alert.currentValue }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">阈值:</span>
                  <span class="detail-value">{{ alert.threshold }}</span>
                </div>
              </div>
            </div>
            
            <div class="alert-actions">
              <button class="action-btn" @click="handleAlert(alert)">
                <i class="fas fa-check"></i>
                <span>处理</span>
              </button>
              <button class="action-btn" @click="dismissAlert(alert)">
                <i class="fas fa-times"></i>
                <span>忽略</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 性能监控 -->
      <section class="performance-section">
        <div class="section-header">
          <h2>系统性能监控</h2>
          <div class="performance-controls">
            <div class="time-range-selector">
              <button 
                v-for="range in timeRanges" 
                :key="range.id"
                class="range-btn"
                :class="{ active: selectedTimeRange === range.id }"
                @click="selectedTimeRange = range.id"
              >
                {{ range.name }}
              </button>
            </div>
            <button class="export-btn" @click="exportPerformanceData">
              <i class="fas fa-download"></i>
              <span>导出数据</span>
            </button>
          </div>
        </div>
        
        <div class="performance-grid">
          <div class="performance-card">
            <h3>CPU使用率</h3>
            <div class="performance-chart" id="cpu-chart"></div>
            <div class="performance-stats">
              <span class="current-value">{{ currentPerformance.cpu }}%</span>
              <span class="peak-value">峰值: {{ performanceStats.cpuPeak }}%</span>
            </div>
          </div>
          
          <div class="performance-card">
            <h3>内存使用率</h3>
            <div class="performance-chart" id="memory-chart"></div>
            <div class="performance-stats">
              <span class="current-value">{{ currentPerformance.memory }}%</span>
              <span class="peak-value">峰值: {{ performanceStats.memoryPeak }}%</span>
            </div>
          </div>
          
          <div class="performance-card">
            <h3>网络延迟</h3>
            <div class="performance-chart" id="network-chart"></div>
            <div class="performance-stats">
              <span class="current-value">{{ currentPerformance.network }}ms</span>
              <span class="peak-value">峰值: {{ performanceStats.networkPeak }}ms</span>
            </div>
          </div>
          
          <div class="performance-card">
            <h3>数据延迟</h3>
            <div class="performance-chart" id="data-chart"></div>
            <div class="performance-stats">
              <span class="current-value">{{ currentPerformance.dataDelay }}ms</span>
              <span class="peak-value">峰值: {{ performanceStats.dataDelayPeak }}ms</span>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const currentLayout = ref('2x2')
const isRefreshing = ref(false)
const refreshInterval = ref(5)
const activeAlertFilter = ref('all')
const selectedTimeRange = ref('1h')

// 监控统计
const monitorStats = ref([
  {
    id: 1,
    icon: 'fas fa-desktop',
    label: '监控屏幕',
    value: '8',
    change: '+2',
    trend: 'up'
  },
  {
    id: 2,
    icon: 'fas fa-bell',
    label: '活跃预警',
    value: '23',
    change: '+5',
    trend: 'up'
  },
  {
    id: 3,
    icon: 'fas fa-chart-line',
    label: '实时数据流',
    value: '156',
    change: '+18',
    trend: 'up'
  },
  {
    id: 4,
    icon: 'fas fa-tachometer-alt',
    label: '系统负载',
    value: '45%',
    change: '-3%',
    trend: 'down'
  }
])

// 屏幕布局配置
const screenLayouts = ref([
  { id: '1x1', name: '单屏', icon: 'fas fa-square' },
  { id: '2x2', name: '四屏', icon: 'fas fa-th-large' },
  { id: '3x3', name: '九屏', icon: 'fas fa-th' },
  { id: '4x4', name: '十六屏', icon: 'fas fa-th' }
])

// 监控屏幕数据
const monitoringScreens = ref([
  {
    id: 1,
    title: '沪深300指数',
    subtitle: '实时行情',
    status: 'active',
    metrics: [
      { name: '当前价格', value: 4567.89, type: 'price' },
      { name: '涨跌幅', value: 1.23, type: 'percentage' },
      { name: '成交量', value: 123456789, type: 'volume' }
    ]
  },
  {
    id: 2,
    title: '策略A',
    subtitle: '趋势跟踪',
    status: 'active',
    metrics: [
      { name: '今日收益', value: 2.34, type: 'percentage' },
      { name: '累计收益', value: 15.67, type: 'percentage' },
      { name: '胜率', value: 65.4, type: 'percentage' }
    ]
  },
  {
    id: 3,
    title: '系统健康度',
    subtitle: '性能监控',
    status: 'warning',
    metrics: [
      { name: 'CPU使用率', value: 67.8, type: 'percentage' },
      { name: '内存使用率', value: 78.9, type: 'percentage' },
      { name: '网络延迟', value: 23, type: 'number' }
    ]
  },
  {
    id: 4,
    title: '数据延迟',
    subtitle: '实时监控',
    status: 'active',
    metrics: [
      { name: '行情延迟', value: 12, type: 'number' },
      { name: '交易延迟', value: 45, type: 'number' },
      { name: '队列深度', value: 156, type: 'number' }
    ]
  }
])

// 预警过滤器
const alertFilters = ref([
  { id: 'all', name: '全部', count: 23 },
  { id: 'critical', name: '紧急', count: 3 },
  { id: 'warning', name: '警告', count: 12 },
  { id: 'info', name: '信息', count: 8 }
])

// 预警数据
const alerts = ref([
  {
    id: 1,
    level: 'critical',
    title: '策略A止损触发',
    description: '策略A当前亏损超过设定的止损阈值',
    condition: '亏损 > 5%',
    currentValue: '-5.2%',
    threshold: '-5%',
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: 2,
    level: 'warning',
    title: '系统负载过高',
    description: 'CPU使用率持续高于阈值',
    condition: 'CPU > 80%',
    currentValue: '82.3%',
    threshold: '80%',
    timestamp: new Date(Date.now() - 15 * 60 * 1000)
  },
  {
    id: 3,
    level: 'info',
    title: '新策略上线',
    description: '策略B已成功部署并开始运行',
    condition: '策略状态变更',
    currentValue: '运行中',
    threshold: '部署完成',
    timestamp: new Date(Date.now() - 30 * 60 * 1000)
  }
])

// 时间范围选择
const timeRanges = ref([
  { id: '5m', name: '5分钟' },
  { id: '15m', name: '15分钟' },
  { id: '1h', name: '1小时' },
  { id: '4h', name: '4小时' },
  { id: '1d', name: '1天' }
])

// 当前性能数据
const currentPerformance = ref({
  cpu: 67.8,
  memory: 78.9,
  network: 23,
  dataDelay: 12
})

// 性能统计数据
const performanceStats = ref({
  cpuPeak: 85.2,
  memoryPeak: 89.1,
  networkPeak: 45,
  dataDelayPeak: 28
})

// 计算属性
const filteredAlerts = computed(() => {
  if (activeAlertFilter.value === 'all') {
    return alerts.value
  }
  return alerts.value.filter(alert => alert.level === activeAlertFilter.value)
})

// 方法
const getTrendIcon = (trend: string) => {
  const iconMap = {
    up: 'fas fa-arrow-up',
    down: 'fas fa-arrow-down',
    stable: 'fas fa-minus'
  }
  return iconMap[trend] || 'fas fa-minus'
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '运行中',
    warning: '警告',
    error: '错误',
    inactive: '已停止'
  }
  return statusMap[status] || status
}

const getMetricClass = (value: number, type: string) => {
  if (type === 'percentage') {
    if (value > 5) return 'positive'
    if (value < -5) return 'negative'
    return 'neutral'
  }
  return 'neutral'
}

const formatMetric = (value: number, type: string) => {
  switch (type) {
    case 'price':
      return value.toFixed(2)
    case 'percentage':
      return `${value.toFixed(2)}%`
    case 'volume':
      return formatNumber(value)
    case 'number':
      return value.toString()
    default:
      return value.toString()
  }
}

const formatNumber = (num: number) => {
  if (num >= 100000000) {
    return (num / 100000000).toFixed(2) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(2) + '万'
  }
  return num.toString()
}

const getAlertIcon = (level: string) => {
  const iconMap = {
    critical: 'fas fa-exclamation-triangle',
    warning: 'fas fa-exclamation-circle',
    info: 'fas fa-info-circle'
  }
  return iconMap[level] || 'fas fa-info-circle'
}

const formatTime = (timestamp: Date) => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

const createMonitor = () => {
  router.push('/function/real-time-monitoring/dashboard')
}

const showAlerts = () => {
  console.log('显示预警管理')
}

const changeLayout = (layoutId: string) => {
  currentLayout.value = layoutId
}

const refreshData = () => {
  isRefreshing.value = true
  setTimeout(() => {
    isRefreshing.value = false
    // 更新数据
    updateMonitoringData()
  }, 1000)
}

const updateMonitoringData = () => {
  // 模拟数据更新
  monitoringScreens.value.forEach(screen => {
    screen.metrics.forEach(metric => {
      if (metric.type === 'percentage') {
        metric.value += (Math.random() - 0.5) * 2
      } else if (metric.type === 'number') {
        metric.value += Math.floor((Math.random() - 0.5) * 10)
      }
    })
  })
  
  // 更新性能数据
  currentPerformance.value.cpu += (Math.random() - 0.5) * 5
  currentPerformance.value.memory += (Math.random() - 0.5) * 3
  currentPerformance.value.network += (Math.random() - 0.5) * 8
  currentPerformance.value.dataDelay += (Math.random() - 0.5) * 4
}

const expandScreen = (screen: any) => {
  console.log('展开屏幕', screen)
}

const configureScreen = (screen: any) => {
  console.log('配置屏幕', screen)
}

const fullscreenScreen = (screen: any) => {
  console.log('全屏显示', screen)
}

const duplicateScreen = (screen: any) => {
  const newScreen = {
    ...screen,
    id: Date.now(),
    title: screen.title + ' (副本)'
  }
  monitoringScreens.value.push(newScreen)
}

const handleAlert = (alert: any) => {
  console.log('处理预警', alert)
  const index = alerts.value.findIndex(a => a.id === alert.id)
  if (index > -1) {
    alerts.value.splice(index, 1)
  }
}

const dismissAlert = (alert: any) => {
  const index = alerts.value.findIndex(a => a.id === alert.id)
  if (index > -1) {
    alerts.value.splice(index, 1)
  }
}

const clearAlerts = () => {
  alerts.value = []
}

const exportPerformanceData = () => {
  console.log('导出性能数据')
}

// 初始化粒子系统
const initParticleSystem = () => {
  const particleSystem = document.querySelector('.particle-system')
  if (!particleSystem) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.pointerEvents = 'none'
  
  particleSystem.appendChild(canvas)
  
  // 简单的粒子动画
  const particles: any[] = []
  for (let i = 0; i < 25; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(particle => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx = -particle.vx
      if (particle.y < 0 || particle.y > canvas.height) particle.vy = -particle.vy
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(245, 158, 11, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 定时刷新数据
let refreshTimer: any = null

const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    updateMonitoringData()
  }, refreshInterval.value * 1000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  initParticleSystem()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.monitoring-page {
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
  overflow-x: hidden;
}

// 沉浸式背景
.immersive-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  
  .particle-system {
    position: absolute;
    width: 100%;
    height: 100%;
  }
  
  .data-stream-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, 
      transparent 30%, 
      rgba(245, 158, 11, 0.03) 50%, 
      transparent 70%);
    animation: dataFlow 8s linear infinite;
  }
  
  .grid-pattern {
    position: absolute;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
  }
}

// 页面头部
.page-header {
  position: relative;
  z-index: 10;
  padding: 24px 40px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .header-left {
    .page-title {
      margin: 0 0 8px 0;
      font-size: 32px;
      font-weight: 700;
      background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .page-subtitle {
      margin: 0;
      color: var(--text-secondary);
      font-size: 16px;
    }
  }
  
  .header-right {
    .action-buttons {
      display: flex;
      gap: 16px;
      
      .primary-btn, .secondary-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
      }
      
      .primary-btn {
        background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(245, 158, 11, 0.3);
        }
      }
      
      .secondary-btn {
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-primary);
        border: 1px solid rgba(255, 255, 255, 0.1);
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
}

// 主内容区域
.main-content {
  position: relative;
  z-index: 5;
  padding: 40px;
}

// 统计区域
.stats-section {
  margin-bottom: 60px;
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    
    .stat-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 24px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      
      .stat-icon {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: var(--warning);
        font-size: 20px;
      }
      
      .stat-content {
        flex: 1;
        
        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 14px;
          color: var(--text-secondary);
        }
      }
      
      .stat-trend {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        
        &.up {
          background: rgba(16, 185, 129, 0.1);
          color: var(--market-rise);
        }
        
        &.down {
          background: rgba(239, 68, 68, 0.1);
          color: var(--market-fall);
        }
        
        &.stable {
          background: rgba(245, 158, 11, 0.1);
          color: #f59e0b;
        }
      }
    }
  }
}

// 多屏监控区域
.multi-screen-section {
  margin-bottom: 60px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
    
    h2 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .layout-controls {
      display: flex;
      align-items: center;
      gap: 24px;
      
      .layout-selector {
        display: flex;
        gap: 8px;
        
        .layout-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover, &.active {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            border-color: var(--warning);
          }
        }
      }
      
      .refresh-control {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .refresh-btn {
          width: 32px;
          height: 32px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 50%;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
          }
        }
        
        .refresh-interval {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
    }
  }
  
  .monitoring-grid {
    display: grid;
    gap: 16px;
    
    &.layout-1x1 {
      grid-template-columns: 1fr;
    }
    
    &.layout-2x2 {
      grid-template-columns: repeat(2, 1fr);
    }
    
    &.layout-3x3 {
      grid-template-columns: repeat(3, 1fr);
    }
    
    &.layout-4x4 {
      grid-template-columns: repeat(4, 1fr);
    }
    
    .monitor-screen {
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 16px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      }
      
      .screen-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 12px;
        
        .screen-info {
          flex: 1;
          
          h3 {
            margin: 0 0 4px 0;
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          p {
            margin: 0;
            color: var(--text-secondary);
            font-size: 12px;
          }
        }
        
        .screen-status {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 2px 6px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          
          .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            
            &.active {
              background: var(--market-rise);
              animation: pulse 2s infinite;
            }
            
            &.warning {
              background: #f59e0b;
            }
            
            &.error {
              background: var(--market-fall);
            }
            
            &.inactive {
              background: #6b7280;
            }
          }
          
          .status-text {
            font-size: 10px;
            color: var(--text-secondary);
          }
        }
      }
      
      .screen-content {
        margin-bottom: 12px;
        
        .chart-container {
          height: 120px;
          background: rgba(255, 255, 255, 0.02);
          border-radius: 4px;
          position: relative;
          overflow: hidden;
          
          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.3), transparent);
            animation: chartFlow 3s linear infinite;
          }
        }
        
        .screen-metrics {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          
          .metric-item {
            flex: 1;
            min-width: 80px;
            text-align: center;
            padding: 4px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 4px;
            
            .metric-name {
              display: block;
              font-size: 10px;
              color: var(--text-secondary);
              margin-bottom: 2px;
            }
            
            .metric-value {
              font-size: 12px;
              font-weight: 600;
              
              &.positive {
                color: var(--market-rise);
              }
              
              &.negative {
                color: var(--market-fall);
              }
              
              &.neutral {
                color: var(--text-primary);
              }
            }
          }
        }
      }
      
      .screen-actions {
        display: flex;
        justify-content: space-between;
        
        .action-btn {
          width: 24px;
          height: 24px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 4px;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
          }
        }
      }
    }
  }
}

// 预警墙区域
.alerts-section {
  margin-bottom: 60px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
    
    h2 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .alert-controls {
      display: flex;
      align-items: center;
      gap: 24px;
      
      .filter-tabs {
        display: flex;
        gap: 8px;
        
        .filter-tab {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover, &.active {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            border-color: var(--warning);
          }
          
          .alert-count {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 500;
          }
        }
      }
      
      .clear-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 12px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 6px;
        color: var(--market-fall);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: rgba(239, 68, 68, 0.5);
        }
      }
    }
  }
  
  .alerts-wall {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 16px;
    
    .alert-card {
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 16px;
      transition: all 0.3s ease;
      
      &.critical {
        border-color: rgba(239, 68, 68, 0.3);
        background: rgba(239, 68, 68, 0.05);
      }
      
      &.warning {
        border-color: rgba(245, 158, 11, 0.3);
        background: rgba(245, 158, 11, 0.05);
      }
      
      &.info {
        border-color: rgba(59, 130, 246, 0.3);
        background: rgba(59, 130, 246, 0.05);
      }
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      }
      
      .alert-header {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 12px;
        
        .alert-icon {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          
          .critical & {
            background: rgba(239, 68, 68, 0.2);
            color: var(--market-fall);
          }
          
          .warning & {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
          }
          
          .info & {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
          }
        }
        
        .alert-info {
          flex: 1;
          
          h4 {
            margin: 0 0 4px 0;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          p {
            margin: 0;
            color: var(--text-secondary);
            font-size: 12px;
            line-height: 1.4;
          }
        }
        
        .alert-time {
          font-size: 10px;
          color: var(--text-secondary);
        }
      }
      
      .alert-content {
        margin-bottom: 12px;
        
        .alert-details {
          .detail-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            
            .detail-label {
              font-size: 11px;
              color: var(--text-secondary);
            }
            
            .detail-value {
              font-size: 11px;
              color: var(--text-primary);
              font-weight: 500;
            }
          }
        }
      }
      
      .alert-actions {
        display: flex;
        gap: 8px;
        
        .action-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
          padding: 6px 8px;
          border-radius: 4px;
          font-size: 11px;
          cursor: pointer;
          transition: all 0.3s ease;
          border: none;
          
          &:first-child {
            background: rgba(16, 185, 129, 0.2);
            color: var(--market-rise);
            
            &:hover {
              background: rgba(16, 185, 129, 0.3);
            }
          }
          
          &:last-child {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            
            &:hover {
              background: rgba(255, 255, 255, 0.1);
              color: var(--text-primary);
            }
          }
        }
      }
    }
  }
}

// 性能监控区域
.performance-section {
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
    
    h2 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .performance-controls {
      display: flex;
      align-items: center;
      gap: 24px;
      
      .time-range-selector {
        display: flex;
        gap: 8px;
        
        .range-btn {
          padding: 8px 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover, &.active {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            border-color: var(--warning);
          }
        }
      }
      
      .export-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
  
  .performance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    
    .performance-card {
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 20px;
      
      h3 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .performance-chart {
        height: 120px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 6px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
        
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.3), transparent);
          animation: chartFlow 3s linear infinite;
        }
      }
      
      .performance-stats {
        display: flex;
        justify-content: space-between;
        
        .current-value {
          font-size: 18px;
          font-weight: 700;
          color: var(--text-primary);
        }
        
        .peak-value {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
    }
  }
}

// 动画
@keyframes dataFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes chartFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .monitoring-grid {
    &.layout-3x3 {
      grid-template-columns: repeat(2, 1fr);
    }
    
    &.layout-4x4 {
      grid-template-columns: repeat(3, 1fr);
    }
  }
  
  .alerts-wall {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
  
  .performance-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 20px;
    
    .header-content {
      flex-direction: column;
      gap: 16px;
      text-align: center;
    }
  }
  
  .main-content {
    padding: 20px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    
    .layout-controls,
    .alert-controls,
    .performance-controls {
      flex-direction: column;
      gap: 12px;
      align-items: flex-start;
      width: 100%;
    }
  }
  
  .monitoring-grid {
    grid-template-columns: 1fr;
    
    &.layout-2x2,
    &.layout-3x3,
    &.layout-4x4 {
      grid-template-columns: 1fr;
    }
  }
  
  .alerts-wall {
    grid-template-columns: 1fr;
  }
  
  .performance-grid {
    grid-template-columns: 1fr;
  }
}
</style>