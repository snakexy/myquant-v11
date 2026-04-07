<template>
  <div class="production-page">
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
          <h1 class="page-title"><i class="fas fa-rocket"></i> 上线阶段</h1>
          <p class="page-subtitle">实盘交易管理 - 策略上线与实时监控</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="deployStrategy">
              <i class="fas fa-rocket"></i>
              <span>部署策略</span>
            </button>
            <button class="secondary-btn" @click="openTradingHistory">
              <i class="fas fa-history"></i>
              <span>交易历史</span>
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
      <!-- 实盘交易概览 -->
      <section class="trading-overview">
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

      <!-- 上线工作台 -->
      <section class="production-workspace">
        <div class="workspace-grid">
          <!-- 实盘交易 -->
          <div class="workspace-card" @click="navigateToLiveTrading">
            <div class="card-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="card-content">
              <h3>实盘交易</h3>
              <p>管理实盘交易策略，实时监控交易执行</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">活跃策略</span>
                  <span class="stat-value">8</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">今日交易</span>
                  <span class="stat-value">156</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 90%"></div>
            </div>
          </div>

          <!-- 风险控制 -->
          <div class="workspace-card" @click="navigateToRiskControl">
            <div class="card-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <div class="card-content">
              <h3>风险控制</h3>
              <p>实时风险监控和自动止损机制</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">风险指标</span>
                  <span class="stat-value">12</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">预警次数</span>
                  <span class="stat-value">3</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 75%"></div>
            </div>
          </div>

          <!-- 资金管理 -->
          <div class="workspace-card" @click="navigateToCapitalManagement">
            <div class="card-icon">
              <i class="fas fa-wallet"></i>
            </div>
            <div class="card-content">
              <h3>资金管理</h3>
              <p>账户资金分配和仓位管理</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">管理资金</span>
                  <span class="stat-value">500万</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">使用率</span>
                  <span class="stat-value">68%</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 68%"></div>
            </div>
          </div>

          <!-- 性能监控 -->
          <div class="workspace-card" @click="navigateToPerformanceMonitoring">
            <div class="card-icon">
              <i class="fas fa-tachometer-alt"></i>
            </div>
            <div class="card-content">
              <h3>性能监控</h3>
              <p>策略性能实时监控和分析</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">监控指标</span>
                  <span class="stat-value">24</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">异常次数</span>
                  <span class="stat-value">1</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 85%"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 当前运行策略 -->
      <section class="active-strategies">
        <div class="section-header">
          <h2>当前运行策略</h2>
          <button class="view-all-btn" @click="viewAllStrategies">
            <span>查看全部</span>
            <i class="fas fa-arrow-right"></i>
          </button>
        </div>
        
        <div class="strategies-grid">
          <div class="strategy-card" v-for="strategy in activeStrategies" :key="strategy.id">
            <div class="strategy-header">
              <h3>{{ strategy.name }}</h3>
              <div class="strategy-status" :class="strategy.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ strategy.statusText }}</span>
              </div>
            </div>
            
            <p class="strategy-description">{{ strategy.description }}</p>
            
            <div class="strategy-metrics">
              <div class="metric-item">
                <span class="metric-label">今日收益</span>
                <span class="metric-value" :class="getPerformanceClass(strategy.todayReturn)">
                  {{ strategy.todayReturn > 0 ? '+' : '' }}{{ strategy.todayReturn.toFixed(2) }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">累计收益</span>
                <span class="metric-value" :class="getPerformanceClass(strategy.totalReturn)">
                  {{ strategy.totalReturn > 0 ? '+' : '' }}{{ strategy.totalReturn.toFixed(2) }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">夏普比率</span>
                <span class="metric-value">{{ strategy.sharpeRatio.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="strategy-footer">
              <div class="strategy-time">
                <i class="fas fa-clock"></i>
                <span>运行时间: {{ strategy.runningTime }}</span>
              </div>
              <div class="strategy-actions">
                <button class="action-btn" @click="pauseStrategy(strategy)" v-if="strategy.status === 'active'">
                  <i class="fas fa-pause"></i>
                </button>
                <button class="action-btn" @click="resumeStrategy(strategy)" v-else-if="strategy.status === 'paused'">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn" @click="viewStrategy(strategy)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn" @click="editStrategy(strategy)">
                  <i class="fas fa-edit"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 实盘工具箱 -->
      <section class="production-tools">
        <div class="section-header">
          <h2>实盘工具箱</h2>
          <p>专业的实盘交易管理工具</p>
        </div>
        
        <div class="tools-grid">
          <div class="tool-card" v-for="tool in productionTools" :key="tool.id" @click="openTool(tool)">
            <div class="tool-icon">
              <i :class="tool.icon"></i>
            </div>
            <div class="tool-content">
              <h3>{{ tool.name }}</h3>
              <p>{{ tool.description }}</p>
            </div>
            <div class="tool-badge" v-if="tool.isNew">新</div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const overviewCards = ref([
  {
    id: 1,
    title: '总资产',
    value: '5,234,567',
    change: '+2.3%',
    changeType: 'up',
    progress: 85,
    icon: 'fas fa-wallet'
  },
  {
    id: 2,
    title: '今日收益',
    value: '+12,345',
    change: '+1.8%',
    changeType: 'up',
    progress: 70,
    icon: 'fas fa-chart-line'
  },
  {
    id: 3,
    title: '活跃策略',
    value: '8',
    change: '+2',
    changeType: 'up',
    progress: 80,
    icon: 'fas fa-robot'
  },
  {
    id: 4,
    title: '风险等级',
    value: '低',
    change: '稳定',
    changeType: 'stable',
    progress: 30,
    icon: 'fas fa-shield-alt'
  }
])

const activeStrategies = ref([
  {
    id: 1,
    name: '多因子选股策略v3.0',
    description: '基于基本面和技术面的多因子选股模型，已通过验证阶段并投入实盘',
    status: 'active',
    statusText: '运行中',
    todayReturn: 1.2,
    totalReturn: 23.5,
    sharpeRatio: 2.1,
    runningTime: '15天'
  },
  {
    id: 2,
    name: '机器学习预测模型',
    description: '使用LSTM神经网络预测股票价格走势，已完成模拟实盘验证',
    status: 'active',
    statusText: '运行中',
    todayReturn: 0.8,
    totalReturn: 18.7,
    sharpeRatio: 1.8,
    runningTime: '8天'
  },
  {
    id: 3,
    name: '事件驱动策略',
    description: '基于财报发布、政策变化等事件的量化交易策略，正在风险控制中',
    status: 'paused',
    statusText: '已暂停',
    todayReturn: 0,
    totalReturn: 15.2,
    sharpeRatio: 1.6,
    runningTime: '22天'
  }
])

const productionTools = ref([
  {
    id: 1,
    name: '交易执行引擎',
    description: '高性能交易订单执行和管理，支持多种交易接口',
    icon: 'fas fa-exchange-alt',
    isNew: false
  },
  {
    id: 2,
    name: '风险监控系统',
    description: '实时风险监控和自动止损，多维度风险指标',
    icon: 'fas fa-shield-alt',
    isNew: false
  },
  {
    id: 3,
    name: '仓位管理工具',
    description: '智能仓位分配、动态调仓和风险控制',
    icon: 'fas fa-wallet',
    isNew: true
  },
  {
    id: 4,
    name: '绩效跟踪系统',
    description: '实时跟踪策略表现和投资组合绩效',
    icon: 'fas fa-tachometer-alt',
    isNew: true
  },
  {
    id: 5,
    name: '报警系统',
    description: '异常情况自动报警和处理，多渠道通知',
    icon: 'fas fa-bell',
    isNew: false
  },
  {
    id: 6,
    name: '报告生成器',
    description: '自动生成交易报告和分析，支持多种格式',
    icon: 'fas fa-file-alt',
    isNew: false
  }
])

// 方法
const deployStrategy = () => {
  console.log('部署策略')
  // 这里可以添加部署策略的逻辑
}

const openTradingHistory = () => {
  console.log('打开交易历史')
  // 这里可以添加打开交易历史的逻辑
}

const openSettings = () => {
  console.log('打开设置')
  // 这里可以添加设置页面逻辑
}

const navigateToLiveTrading = () => {
  console.log('导航到实盘交易')
  // 这里可以添加导航逻辑
}

const navigateToRiskControl = () => {
  console.log('导航到风险控制')
  // 这里可以添加导航逻辑
}

const navigateToCapitalManagement = () => {
  console.log('导航到资金管理')
  // 这里可以添加导航逻辑
}

const navigateToPerformanceMonitoring = () => {
  console.log('导航到性能监控')
  // 这里可以添加导航逻辑
}

const viewAllStrategies = () => {
  console.log('查看所有策略')
  // 这里可以添加查看所有策略的逻辑
}

const pauseStrategy = (strategy: any) => {
  console.log('暂停策略:', strategy.name)
  // 这里可以添加暂停策略的逻辑
}

const resumeStrategy = (strategy: any) => {
  console.log('恢复策略:', strategy.name)
  // 这里可以添加恢复策略的逻辑
}

const viewStrategy = (strategy: any) => {
  console.log('查看策略:', strategy.name)
  // 这里可以添加查看策略的逻辑
}

const editStrategy = (strategy: any) => {
  console.log('编辑策略:', strategy.name)
  // 这里可以添加编辑策略的逻辑
}

const openTool = (tool: any) => {
  console.log('打开工具:', tool.name)
  // 这里可以添加打开工具的逻辑
}

const getChangeIcon = (type: string) => {
  const iconMap = {
    up: 'fas fa-arrow-up',
    down: 'fas fa-arrow-down',
    stable: 'fas fa-minus'
  }
  return iconMap[type] || 'fas fa-minus'
}

const getPerformanceClass = (value: number) => {
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return 'neutral'
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
      ctx.fillStyle = `rgba(239, 68, 68, ${particle.opacity})`
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
@use '@/assets/styles/variables.scss' as *;

.production-page {
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
      rgba(239, 68, 68, 0.03) 50%, 
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
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
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
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);
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

// 实盘交易概览
.trading-overview {
  margin-bottom: 60px;
  
  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    
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
        0 8px 32px rgba(239, 68, 68, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(239, 68, 68, 0.15),
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
        background: rgba(239, 68, 68, 0.1);
        border-radius: 12px;
        color: var(--market-fall);
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
          font-size: 28px;
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
          background: linear-gradient(90deg, #ef4444, #dc2626);
          transition: width 0.3s ease;
        }
      }
    }
  }
}

// 上线工作台
.production-workspace {
  margin-bottom: 60px;
  
  .workspace-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    
    .workspace-card {
      position: relative;
      padding: 24px;
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      overflow: hidden;
      box-shadow:
        0 8px 32px rgba(239, 68, 68, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      cursor: pointer;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(239, 68, 68, 0.15),
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
        background: rgba(239, 68, 68, 0.1);
        border-radius: 12px;
        color: var(--market-fall);
        font-size: 20px;
      }
      
      .card-content {
        h3 {
          margin: 0 0 12px 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        p {
          margin: 0 0 20px 0;
          color: var(--text-secondary);
          font-size: 14px;
          line-height: 1.5;
        }
        
        .card-stats {
          display: flex;
          gap: 24px;
          
          .stat-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
            
            .stat-label {
              font-size: 12px;
              color: var(--text-secondary);
            }
            
            .stat-value {
              font-size: 18px;
              font-weight: 600;
              color: var(--text-primary);
            }
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
          background: linear-gradient(90deg, #ef4444, #dc2626);
          transition: width 0.3s ease;
        }
      }
    }
  }
}

// 当前运行策略
.active-strategies {
  margin-bottom: 60px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 40px;
    
    h2 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .view-all-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
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
  
  .strategies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 24px;
    
    .strategy-card {
      padding: 24px;
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      box-shadow:
        0 8px 32px rgba(239, 68, 68, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(239, 68, 68, 0.15),
          inset 0 1px 0 rgba(255, 255, 255, 0.15);
      }
      
      .strategy-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        
        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .strategy-status {
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
          
          &.paused {
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
           
            .status-dot {
              background: #f59e0b;
            }
          }
          
          &.stopped {
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
      
      .strategy-description {
        margin: 0 0 20px 0;
        color: var(--text-secondary);
        font-size: 14px;
        line-height: 1.5;
      }
      
      .strategy-metrics {
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
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            
            &.positive {
              color: var(--market-rise);
            }
            
            &.negative {
              color: var(--market-fall);
            }
          }
        }
      }
      
      .strategy-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        
        .strategy-time {
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--text-secondary);
          font-size: 12px;
        }
        
        .strategy-actions {
          display: flex;
          gap: 8px;
          
          .action-btn {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.2s ease;
            
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

// 实盘工具箱
.production-tools {
  .section-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 16px;
    }
  }
  
  .tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    
    .tool-card {
      position: relative;
      padding: 24px;
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      box-shadow:
        0 8px 32px rgba(239, 68, 68, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      cursor: pointer;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(239, 68, 68, 0.15),
          inset 0 1px 0 rgba(255, 255, 255, 0.15);
      }
      
      .tool-icon {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(239, 68, 68, 0.1);
        border-radius: 12px;
        color: var(--market-fall);
        font-size: 20px;
      }
      
      .tool-content {
        h3 {
          margin: 0 0 12px 0;
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
      
      .tool-badge {
        position: absolute;
        top: 16px;
        left: 16px;
        padding: 4px 8px;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        font-size: 12px;
        font-weight: 500;
        border-radius: 12px;
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
  
  .workspace-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .strategies-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tools-grid {
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
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .workspace-grid {
    grid-template-columns: 1fr;
  }
  
  .strategies-grid {
    grid-template-columns: 1fr;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
}
</style>