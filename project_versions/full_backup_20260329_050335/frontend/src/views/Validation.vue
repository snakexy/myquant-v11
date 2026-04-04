<template>
  <div class="validation-page">
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
          <h1 class="page-title"><i class="fas fa-check-double"></i> 验证阶段</h1>
          <p class="page-subtitle">策略验证与测试 - 确保策略有效性和稳定性</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="startNewValidation">
              <i class="fas fa-play"></i>
              <span>新建验证</span>
            </button>
            <button class="secondary-btn" @click="openValidationHistory">
              <i class="fas fa-history"></i>
              <span>验证历史</span>
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
      <!-- 验证工作台 -->
      <section class="validation-workspace">
        <div class="workspace-grid">
          <!-- 历史回测 -->
          <div class="workspace-card" @click="navigateToBacktest">
            <div class="card-icon">
              <i class="fas fa-chart-area"></i>
            </div>
            <div class="card-content">
              <h3>历史回测</h3>
              <p>基于历史数据进行策略回测，评估策略表现</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">回测次数</span>
                  <span class="stat-value">156</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">成功率</span>
                  <span class="stat-value">78%</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 85%"></div>
            </div>
          </div>

          <!-- 模拟实盘 -->
          <div class="workspace-card" @click="navigateToSimulation">
            <div class="card-icon">
              <i class="fas fa-robot"></i>
            </div>
            <div class="card-content">
              <h3>模拟实盘</h3>
              <p>实时模拟交易环境，测试策略实际表现</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">模拟账户</span>
                  <span class="stat-value">12</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">运行中</span>
                  <span class="stat-value">5</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 65%"></div>
            </div>
          </div>

          <!-- 实时监控 -->
          <div class="workspace-card" @click="navigateToMonitoring">
            <div class="card-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="card-content">
              <h3>实时监控</h3>
              <p>实时监控策略运行状态和风险指标</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">监控指标</span>
                  <span class="stat-value">12</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">活跃账户</span>
                  <span class="stat-value">8</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 75%"></div>
            </div>
          </div>

          <!-- 在线滚动训练 -->
          <div class="workspace-card" @click="navigateToLearning">
            <div class="card-icon">
              <i class="fas fa-brain"></i>
            </div>
            <div class="card-content">
              <h3>在线滚动训练</h3>
              <p>实时训练模型，优化策略参数</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">训练模型</span>
                  <span class="stat-value">6</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">已完成</span>
                  <span class="stat-value">42</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 60%"></div>
            </div>
          </div>

          <!-- 规则预警系统 -->
          <div class="workspace-card" @click="navigateToAlerts">
            <div class="card-icon">
              <i class="fas fa-bell"></i>
            </div>
            <div class="card-content">
              <h3>规则预警系统</h3>
              <p>基于阈值和条件的自定义预警规则</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">预警规则</span>
                  <span class="stat-value">8</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">活跃预警</span>
                  <span class="stat-value">2</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 50%"></div>
            </div>
          </div>

          <!-- AI智能预警 -->
          <div class="workspace-card" @click="navigateToAIAlerts">
            <div class="card-icon">
              <i class="fas fa-brain"></i>
            </div>
            <div class="card-content">
              <h3>AI智能预警</h3>
              <p>基于QLib原生的AI风险监控与预测</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">风险信号</span>
                  <span class="stat-value">23</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">AI模型</span>
                  <span class="stat-value">4</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 70%"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 当前验证任务 -->
      <section class="current-tasks">
        <div class="section-header">
          <h2>当前验证任务</h2>
          <button class="view-all-btn" @click="viewAllTasks">
            <span>查看全部</span>
            <i class="fas fa-arrow-right"></i>
          </button>
        </div>
        
        <div class="tasks-grid">
          <div class="task-card" v-for="task in currentTasks" :key="task.id">
            <div class="task-header">
              <h3>{{ task.name }}</h3>
              <div class="task-status" :class="task.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ task.statusText }}</span>
              </div>
            </div>
            
            <p class="task-description">{{ task.description }}</p>
            
            <div class="task-progress">
              <div class="progress-info">
                <span class="progress-label">进度</span>
                <span class="progress-value">{{ task.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
              </div>
            </div>
            
            <div class="task-metrics">
              <div class="metric-item">
                <span class="metric-label">收益率</span>
                <span class="metric-value" :class="getPerformanceClass(task.return)">
                  {{ task.return > 0 ? '+' : '' }}{{ task.return.toFixed(2) }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">夏普比率</span>
                <span class="metric-value">{{ task.sharpeRatio.toFixed(2) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">最大回撤</span>
                <span class="metric-value">{{ task.maxDrawdown.toFixed(2) }}%</span>
              </div>
            </div>
            
            <div class="task-footer">
              <div class="task-time">
                <i class="fas fa-clock"></i>
                <span>{{ task.estimatedTime }}</span>
              </div>
              <div class="task-actions">
                <button class="action-btn" @click="pauseTask(task)" v-if="task.status === 'running'">
                  <i class="fas fa-pause"></i>
                </button>
                <button class="action-btn" @click="resumeTask(task)" v-else-if="task.status === 'paused'">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn" @click="viewTask(task)">
                  <i class="fas fa-eye"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 验证工具箱 -->
      <section class="validation-tools">
        <div class="section-header">
          <h2>验证工具箱</h2>
          <p>专业的策略验证和分析工具</p>
        </div>
        
        <div class="tools-grid">
          <div class="tool-card" v-for="tool in validationTools" :key="tool.id" @click="openTool(tool)">
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
const currentTasks = ref([
  {
    id: 1,
    name: '多因子选股策略回测',
    description: '对最新版本的多因子选股策略进行全面历史回测验证',
    status: 'running',
    statusText: '运行中',
    progress: 75,
    return: 12.5,
    sharpeRatio: 1.85,
    maxDrawdown: -8.3,
    estimatedTime: '剩余2小时'
  },
  {
    id: 2,
    name: '机器学习模型模拟交易',
    description: '在模拟环境中测试LSTM模型的实际交易表现',
    status: 'running',
    statusText: '运行中',
    progress: 45,
    return: 8.7,
    sharpeRatio: 1.42,
    maxDrawdown: -12.1,
    estimatedTime: '剩余5小时'
  },
  {
    id: 3,
    name: '事件驱动策略风险评估',
    description: '对事件驱动策略进行全面的风险分析和压力测试',
    status: 'paused',
    statusText: '已暂停',
    progress: 30,
    return: 15.2,
    sharpeRatio: 2.1,
    maxDrawdown: -6.8,
    estimatedTime: '剩余8小时'
  }
])

const validationTools = ref([
  {
    id: 1,
    name: '回测引擎',
    description: '高性能历史数据回测和性能分析',
    icon: 'fas fa-chart-area',
    isNew: false
  },
  {
    id: 2,
    name: '模拟交易系统',
    description: '实时模拟交易环境和订单执行',
    icon: 'fas fa-robot',
    isNew: false
  },
  {
    id: 3,
    name: '风险分析工具',
    description: '全面的风险指标计算和压力测试',
    icon: 'fas fa-shield-alt',
    isNew: true
  },
  {
    id: 4,
    name: '性能优化器',
    description: '策略参数优化和性能提升',
    icon: 'fas fa-sliders-h',
    isNew: true
  },
  {
    id: 5,
    name: '报告生成器',
    description: '自动生成详细的验证报告',
    icon: 'fas fa-file-alt',
    isNew: false
  },
  {
    id: 6,
    name: '对比分析工具',
    description: '多策略对比分析和排名',
    icon: 'fas fa-balance-scale',
    isNew: false
  }
])

// 方法
const startNewValidation = () => {
  console.log('开始新验证')
  // 这里可以添加开始新验证的逻辑
}

const openValidationHistory = () => {
  console.log('打开验证历史')
  // 这里可以添加打开验证历史的逻辑
}

const openSettings = () => {
  console.log('打开设置')
  // 这里可以添加设置页面逻辑
}

const navigateToBacktest = () => {
  router.push('/validation/backtest')
}

const navigateToSimulation = () => {
  router.push('/validation/simulation')
}

const navigateToMonitoring = () => {
  router.push('/validation/monitoring')
}

const navigateToLearning = () => {
  router.push('/validation/learning')
}

const navigateToAlerts = () => {
  router.push('/validation/alerts')
}

const navigateToAIAlerts = () => {
  router.push('/validation/ai-alerts')
}

const viewAllTasks = () => {
  console.log('查看所有任务')
  // 这里可以添加查看所有任务的逻辑
}

const pauseTask = (task: any) => {
  console.log('暂停任务:', task.name)
  // 这里可以添加暂停任务的逻辑
}

const resumeTask = (task: any) => {
  console.log('恢复任务:', task.name)
  // 这里可以添加恢复任务的逻辑
}

const viewTask = (task: any) => {
  console.log('查看任务:', task.name)
  // 这里可以添加查看任务的逻辑
}

const openTool = (tool: any) => {
  console.log('打开工具:', tool.name)
  // 这里可以添加打开工具的逻辑
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
      ctx.fillStyle = `rgba(245, 158, 11, ${particle.opacity})`
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

.validation-page {
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
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
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
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
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
  max-width: 1400px;
  margin: 0 auto;
}

// 验证工作台
.validation-workspace {
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
        0 8px 32px rgba(245, 158, 11, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      cursor: pointer;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(245, 158, 11, 0.15),
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
        background: rgba(245, 158, 11, 0.1);
        border-radius: 12px;
        color: #f59e0b;
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
          background: linear-gradient(90deg, #f59e0b, #d97706);
          transition: width 0.3s ease;
        }
      }
    }
  }
}

// 当前验证任务
.current-tasks {
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
  
  .tasks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 24px;
    
    .task-card {
      padding: 24px;
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      box-shadow:
        0 8px 32px rgba(245, 158, 11, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(245, 158, 11, 0.15),
          inset 0 1px 0 rgba(255, 255, 255, 0.15);
      }
      
      .task-header {
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
        
        .task-status {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          
          &.running {
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
          
          &.completed {
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
           
            .status-dot {
              background: #3b82f6;
            }
          }
          
          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
        }
      }
      
      .task-description {
        margin: 0 0 20px 0;
        color: var(--text-secondary);
        font-size: 14px;
        line-height: 1.5;
      }
      
      .task-progress {
        margin-bottom: 20px;
        
        .progress-info {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          
          .progress-label {
            font-size: 12px;
            color: var(--text-secondary);
          }
          
          .progress-value {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-primary);
          }
        }
        
        .progress-bar {
          height: 6px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
          overflow: hidden;
          
          .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #f59e0b, #d97706);
            transition: width 0.3s ease;
          }
        }
      }
      
      .task-metrics {
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
            
            // 收益率（红涨绿跌）
            &.positive {
              color: var(--market-rise);
            }

            &.negative {
              color: var(--market-fall);
            }
          }
        }
      }
      
      .task-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        
        .task-time {
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--text-secondary);
          font-size: 12px;
        }
        
        .task-actions {
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

// 验证工具箱
.validation-tools {
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
        0 8px 32px rgba(245, 158, 11, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      cursor: pointer;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(245, 158, 11, 0.15),
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
        background: rgba(245, 158, 11, 0.1);
        border-radius: 12px;
        color: #f59e0b;
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
        background: linear-gradient(135deg, #f59e0b, #d97706);
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
  .workspace-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tasks-grid {
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
  
  .workspace-grid {
    grid-template-columns: 1fr;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
}

  /* 统一滑杆样式覆盖 */
  .parameter-range {
    /* 使用全局滑杆样式 */
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    background: var(--border-color);
    border-radius: 3px;
    outline: none;
    transition: all 0.3s ease;
    border: none;
    padding: 0;
  }

  .parameter-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
  }

  .parameter-range::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-webkit-slider-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    border: none;
  }

  .parameter-range::-moz-range-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-moz-range-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-webkit-slider-runnable-track {
    height: 100%;
    border-radius: 3px;
  }

  .parameter-range::-moz-range-track {
    height: 100%;
    border-radius: 3px;
  }

  .range-input-group {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0;
  }

  .range-value {
    min-width: 60px;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--primary-color);
    text-align: center;
    transition: all 0.3s ease;
  }

  /* 参数配置滑杆样式增强 */
  .parameter-slider {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: var(--border-radius);
    transition: all 0.3s ease;
  }

  .parameter-slider:hover {
    background: var(--bg-hover);
  }

  .parameter-slider .parameter-info {
    flex: 1;
  }

  .parameter-slider .parameter-name {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .parameter-slider .parameter-desc {
    font-size: var(--font-size-xs);
    color: var(--text-regular);
  }

  .parameter-slider .parameter-control {
    flex: 2;
    display: flex;
    align-items: center;
    gap: 12px;
  }

</style>