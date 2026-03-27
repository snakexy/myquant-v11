<template>
  <div class="data-management-page">
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
          <h1 class="page-title">数据管理</h1>
          <p class="page-subtitle">量化数据中枢 - 数据质量监控与管理</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="refreshData">
              <i class="fas fa-sync-alt"></i>
              <span>刷新数据</span>
            </button>
            <button class="secondary-btn" @click="openSettings">
              <i class="fas fa-cog"></i>
              <span>设置</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 数据概览卡片 -->
      <section class="overview-section">
        <div class="overview-grid">
          <div class="overview-card" v-for="card in overviewCards" :key="card.id">
            <div class="card-icon">
              <i :class="card.icon"></i>
            </div>
            <div class="card-content">
              <h3>{{ card.title }}</h3>
              <div class="card-value">{{ card.value }}</div>
              <div class="card-change" :class="card.changeType">
                <i :class="getChangeIcon(card.changeType)"></i>
                <span>{{ card.change }}</span>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" :style="{ width: card.progress + '%' }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 数据质量监控 -->
      <section class="quality-section">
        <div class="section-header">
          <h2>数据质量监控</h2>
          <p>实时监控数据完整性和准确性</p>
        </div>
        
        <div class="quality-grid">
          <div class="quality-card" v-for="quality in qualityMetrics" :key="quality.id">
            <div class="quality-header">
              <h3>{{ quality.name }}</h3>
              <div class="quality-status" :class="quality.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ quality.status }}</span>
              </div>
            </div>
            
            <div class="quality-metrics">
              <div class="metric-item">
                <span class="metric-label">完整度</span>
                <span class="metric-value">{{ quality.completeness }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">准确度</span>
                <span class="metric-value">{{ quality.accuracy }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">及时性</span>
                <span class="metric-value">{{ quality.timeliness }}%</span>
              </div>
            </div>
            
            <div class="quality-chart">
              <canvas :ref="'qualityChart-' + quality.id" width="200" height="100"></canvas>
            </div>
          </div>
        </div>
      </section>

      <!-- 数据新鲜度热力图 -->
      <section class="freshness-section">
        <DataFreshnessHeatmap />
      </section>

      <!-- 数据源管理 -->
      <section class="sources-section">
        <div class="section-header">
          <h2>数据源管理</h2>
          <p>配置和监控各个数据源状态</p>
        </div>
        
        <div class="sources-grid">
          <div class="source-card" v-for="source in dataSources" :key="source.id">
            <div class="source-header">
              <div class="source-info">
                <h3>{{ source.name }}</h3>
                <p>{{ source.description }}</p>
              </div>
              <div class="source-status" :class="source.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ source.statusText }}</span>
              </div>
            </div>
            
            <div class="source-metrics">
              <div class="metric-row">
                <div class="metric">
                  <span class="metric-label">数据量</span>
                  <span class="metric-value">{{ source.dataCount }}</span>
                </div>
                <div class="metric">
                  <span class="metric-label">更新频率</span>
                  <span class="metric-value">{{ source.updateFreq }}</span>
                </div>
              </div>
              
              <div class="metric-row">
                <div class="metric">
                  <span class="metric-label">延迟</span>
                  <span class="metric-value">{{ source.latency }}ms</span>
                </div>
                <div class="metric">
                  <span class="metric-label">成功率</span>
                  <span class="metric-value">{{ source.successRate }}%</span>
                </div>
              </div>
            </div>
            
            <div class="source-actions">
              <button class="action-btn" @click="testConnection(source)">
                <i class="fas fa-plug"></i>
                <span>测试连接</span>
              </button>
              <button class="action-btn" @click="configureSource(source)">
                <i class="fas fa-cog"></i>
                <span>配置</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 数据更新计划 -->
      <section class="schedule-section">
        <div class="section-header">
          <h2>数据更新计划</h2>
          <p>管理数据更新任务和时间安排</p>
        </div>
        
        <div class="schedule-timeline">
          <div class="timeline-item" v-for="task in updateTasks" :key="task.id">
            <div class="timeline-marker" :class="task.status"></div>
            <div class="timeline-content">
              <div class="task-header">
                <h3>{{ task.name }}</h3>
                <div class="task-time">{{ task.nextRun }}</div>
              </div>
              <p class="task-description">{{ task.description }}</p>
              <div class="task-actions">
                <button class="task-btn" @click="runTask(task)">
                  <i class="fas fa-play"></i>
                  <span>立即执行</span>
                </button>
                <button class="task-btn" @click="editTask(task)">
                  <i class="fas fa-edit"></i>
                  <span>编辑</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DataFreshnessHeatmap from '@/components/DataFreshnessHeatmap.vue'

// 响应式数据
const overviewCards = ref([
  {
    id: 1,
    title: '总数据量',
    value: '2.3TB',
    change: '+12.5%',
    changeType: 'up',
    progress: 85,
    icon: 'fas fa-database'
  },
  {
    id: 2,
    title: '数据完整度',
    value: '96.8%',
    change: '+2.1%',
    changeType: 'up',
    progress: 96.8,
    icon: 'fas fa-check-circle'
  },
  {
    id: 3,
    title: '活跃数据源',
    value: '12',
    change: '+2',
    changeType: 'up',
    progress: 80,
    icon: 'fas fa-server'
  },
  {
    id: 4,
    title: '今日更新',
    value: '1.2GB',
    change: '-5.2%',
    changeType: 'down',
    progress: 65,
    icon: 'fas fa-sync'
  }
])

const qualityMetrics = ref([
  {
    id: 1,
    name: '股票基础数据',
    status: 'good',
    completeness: 98.5,
    accuracy: 99.2,
    timeliness: 95.8
  },
  {
    id: 2,
    name: '财务数据',
    status: 'good',
    completeness: 96.2,
    accuracy: 97.8,
    timeliness: 92.5
  },
  {
    id: 3,
    name: '技术指标',
    status: 'warning',
    completeness: 94.8,
    accuracy: 96.5,
    timeliness: 89.2
  },
  {
    id: 4,
    name: '新闻数据',
    status: 'good',
    completeness: 92.3,
    accuracy: 94.1,
    timeliness: 96.8
  }
])

const dataSources = ref([
  {
    id: 'quant-data-hub',
    name: 'QuantDataHub 数据中枢',
    description: '统一量化数据中枢，整合多数据源管理',
    status: 'active',
    statusText: '运行中',
    dataCount: '2.5M',
    updateFreq: '实时',
    latency: 30,
    successRate: 99.9
  },
  {
    id: 'qmt',
    name: 'QMT (迅投)',
    description: '高性能量化交易接口，支持前复权调整因子',
    status: 'active',
    statusText: '连接正常',
    dataCount: '1.8M',
    updateFreq: '实时',
    latency: 45,
    successRate: 99.8
  },
  {
    id: 'mootdx',
    name: '通达信 (mootdx)',
    description: '通达信数据接口，作为备用数据源',
    status: 'active',
    statusText: '连接正常',
    dataCount: '1.2M',
    updateFreq: '5分钟',
    latency: 120,
    successRate: 99.5
  },
  {
    id: 'tushare',
    name: 'Tushare Pro',
    description: '中国股票市场数据API（开发中）',
    status: 'development',
    statusText: '开发中',
    dataCount: '0',
    updateFreq: '计划中',
    latency: null,
    successRate: 0
  },
  {
    id: 'wind',
    name: 'Wind金融终端',
    description: '专业金融数据服务（开发中）',
    status: 'development',
    statusText: '开发中',
    dataCount: '0',
    updateFreq: '计划中',
    latency: null,
    successRate: 0
  }
])

const updateTasks = ref([
  {
    id: 1,
    name: '股票基础数据更新',
    description: '每日收盘后更新股票基础信息',
    nextRun: '15:30',
    status: 'scheduled'
  },
  {
    id: 2,
    name: '财务数据同步',
    description: '同步上市公司财务报表数据',
    nextRun: '18:00',
    status: 'scheduled'
  },
  {
    id: 3,
    name: '技术指标计算',
    description: '重新计算所有技术指标',
    nextRun: '20:00',
    status: 'running'
  },
  {
    id: 4,
    name: '数据质量检查',
    description: '执行数据完整性和准确性检查',
    nextRun: '22:00',
    status: 'completed'
  }
])

// 方法
const getChangeIcon = (type: string) => {
  const iconMap = {
    up: 'fas fa-arrow-up',
    down: 'fas fa-arrow-down',
    stable: 'fas fa-minus'
  }
  return iconMap[type] || 'fas fa-minus'
}

const refreshData = async () => {
  console.log('刷新数据')
  try {
    // 从API获取最新的数据源状态
    const { getDataSources } = await import('@/api/dataManagement')
    const sources = await getDataSources()
    dataSources.value = sources
    console.log('数据源已刷新:', sources)
  } catch (error) {
    console.error('刷新数据源失败:', error)
  }
}

const openSettings = () => {
  console.log('打开设置')
  // 这里可以添加设置页面逻辑
}

const testConnection = async (source: any) => {
  console.log('测试连接:', source.name)
  try {
    // 调用后端API测试数据源连接
    const response = await fetch(`/api/v1/data-management/sources/${source.id}/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    const result = await response.json()
    
    if (result.success) {
      // 更新数据源状态
      const sourceIndex = dataSources.value.findIndex(s => s.id === source.id)
      if (sourceIndex !== -1) {
        dataSources.value[sourceIndex].status = result.data.status
        dataSources.value[sourceIndex].statusText = result.data.statusText
        dataSources.value[sourceIndex].latency = result.data.latency
        dataSources.value[sourceIndex].successRate = result.data.successRate
      }
      
      // 显示成功消息
      console.log(`${source.name} 连接测试成功:`, result.data)
    } else {
      console.error(`${source.name} 连接测试失败:`, result.message)
    }
  } catch (error) {
    console.error(`测试 ${source.name} 连接时发生错误:`, error)
  }
}

const configureSource = (source: any) => {
  console.log('配置数据源:', source.name)
  // 这里可以添加数据源配置逻辑
}

const runTask = (task: any) => {
  console.log('执行任务:', task.name)
  // 这里可以添加任务执行逻辑
}

const editTask = (task: any) => {
  console.log('编辑任务:', task.name)
  // 这里可以添加任务编辑逻辑
}

// 初始化粒子系统
const initParticleSystem = () => {
  const particleSystemEl = document.querySelector('.particle-system')
  if (!particleSystemEl) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.pointerEvents = 'none'
  
  particleSystemEl.appendChild(canvas)
  
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
      ctx.fillStyle = `rgba(124, 58, 237, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 生命周期
onMounted(() => {
  initParticleSystem()
})
</script>

<style lang="scss" scoped>
.data-management-page {
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
      rgba(124, 58, 237, 0.03) 50%, 
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
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
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
  max-width: 1400px;
  margin: 0 auto;
}

// 概览卡片
.overview-section {
  margin-bottom: 60px;
  
  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    
    .overview-card {
      position: relative;
      padding: 24px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      overflow: hidden;
      
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
        font-size: 20px;
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
    }
  }
}

// 数据质量监控
.quality-section {
  margin-bottom: 60px;
  
  .section-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .quality-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    
    .quality-card {
      padding: 24px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      
      .quality-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        
        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .quality-status {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          
          &.good {
            background: rgba(16, 185, 129, 0.1);
            color: var(--market-rise);
            
            .status-dot {
              background: var(--market-rise);
            }
          }
          
          &.warning {
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
            
            .status-dot {
              background: #f59e0b;
            }
          }
          
          &.error {
            background: rgba(239, 68, 68, 0.1);
            color: var(--market-fall);
            
            .status-dot {
              background: var(--market-fall);
            }
          }
          
          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
        }
      }
      
      .quality-metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 20px;
        
        .metric-item {
          text-align: center;
          
          .metric-label {
            display: block;
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 4px;
          }
          
          .metric-value {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
          }
        }
      }
      
      .quality-chart {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        
        canvas {
          max-width: 100%;
          height: auto;
        }
      }
    }
  }
}

// 数据新鲜度热力图
.freshness-section {
  margin-bottom: 60px;
}

// 数据源管理
.sources-section {
  margin-bottom: 60px;
  
  .section-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .sources-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
    
    .source-card {
      padding: 24px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      
      .source-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 20px;
        
        .source-info {
          flex: 1;
          
          h3 {
            margin: 0 0 8px 0;
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          p {
            margin: 0;
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.5;
          }
        }
        
        .source-status {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          
          &.active {
            background: rgba(16, 185, 129, 0.1);
            color: var(--market-rise);
            
            .status-dot {
              background: var(--market-rise);
              animation: pulse 2s infinite;
            }
          }
          
          &.warning {
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
            
            .status-dot {
              background: #f59e0b;
            }
          }
          
          &.error {
            background: rgba(239, 68, 68, 0.1);
            color: var(--market-fall);
            
            .status-dot {
              background: var(--market-fall);
            }
          }
          
          &.development {
            background: rgba(107, 114, 128, 0.1);
            color: #6b7280;
            
            .status-dot {
              background: #6b7280;
            }
          }
          
          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
          
          .status-text {
            font-size: 12px;
          }
        }
      }
      
      .source-metrics {
        margin-bottom: 20px;
        
        .metric-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin-bottom: 12px;
          
          .metric {
            text-align: center;
            
            .metric-label {
              display: block;
              font-size: 12px;
              color: var(--text-secondary);
              margin-bottom: 4px;
            }
            
            .metric-value {
              font-size: 16px;
              font-weight: 600;
              color: var(--text-primary);
            }
          }
        }
      }
      
      .source-actions {
        display: flex;
        gap: 12px;
        
        .action-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          color: var(--text-primary);
          font-size: 14px;
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
}

// 更新计划
.schedule-section {
  .section-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .schedule-timeline {
    position: relative;
    
    &::before {
      content: '';
      position: absolute;
      left: 20px;
      top: 0;
      bottom: 0;
      width: 2px;
      background: rgba(255, 255, 255, 0.1);
    }
    
    .timeline-item {
      position: relative;
      padding-left: 60px;
      margin-bottom: 32px;
      
      .timeline-marker {
        position: absolute;
        left: 12px;
        top: 8px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: var(--secondary);
        border: 3px solid var(--bg-deep);
        
        &.scheduled {
          background: #f59e0b;
        }
        
        &.running {
          background: #3b82f6;
          animation: pulse 2s infinite;
        }
        
        &.completed {
          background: var(--market-rise);
        }
      }
      
      .timeline-content {
        padding: 20px;
        background: rgba(26, 26, 46, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        
        .task-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
          
          h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          .task-time {
            font-size: 14px;
            color: var(--secondary);
            font-weight: 500;
          }
        }
        
        .task-description {
          margin: 0 0 16px 0;
          color: var(--text-secondary);
          font-size: 14px;
          line-height: 1.5;
        }
        
        .task-actions {
          display: flex;
          gap: 12px;
          
          .task-btn {
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

// 响应式设计
@media (max-width: 1024px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quality-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .sources-grid {
    grid-template-columns: 1fr;
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
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .quality-grid {
    grid-template-columns: 1fr;
  }
  
  .sources-grid {
    grid-template-columns: 1fr;
  }
  
  .schedule-timeline {
    .timeline-item {
      padding-left: 40px;
    }
  }
}
</style>