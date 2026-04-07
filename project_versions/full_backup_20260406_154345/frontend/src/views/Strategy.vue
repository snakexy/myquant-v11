<template>
  <div class="strategy-page">
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
          <h1 class="page-title"><i class="fas fa-chess"></i> 策略中心</h1>
          <p class="page-subtitle">智能量化策略开发与管理平台</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="createNewStrategy">
              <i class="fas fa-plus"></i>
              <span>创建策略</span>
            </button>
            <button class="secondary-btn" @click="importStrategy">
              <i class="fas fa-upload"></i>
              <span>导入策略</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 策略统计 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card" v-for="stat in strategyStats" :key="stat.id">
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

      <!-- 策略分类 -->
      <section class="categories-section">
        <div class="section-header">
          <h2>策略分类</h2>
          <p>按类型浏览和管理策略</p>
        </div>
        
        <div class="categories-grid">
          <div 
            v-for="category in strategyCategories" 
            :key="category.id"
            class="category-card"
            @click="selectCategory(category)"
            :class="{ active: selectedCategory === category.id }"
          >
            <div class="category-icon">
              <i :class="category.icon"></i>
            </div>
            <div class="category-content">
              <h3>{{ category.name }}</h3>
              <p>{{ category.description }}</p>
              <div class="category-stats">
                <span class="strategy-count">{{ category.count }} 个策略</span>
                <span class="performance" :class="category.performanceClass">
                  {{ category.avgPerformance }}% 平均收益
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 策略列表 -->
      <section class="strategies-section">
        <div class="section-header">
          <h2>策略列表</h2>
          <div class="filter-controls">
            <div class="search-box">
              <i class="fas fa-search"></i>
              <input 
                type="text" 
                placeholder="搜索策略名称或描述..." 
                v-model="searchQuery"
              >
            </div>
            <select v-model="sortBy" class="sort-select">
              <option value="name">按名称排序</option>
              <option value="performance">按收益率排序</option>
              <option value="sharpe">按夏普比率排序</option>
              <option value="created">按创建时间排序</option>
            </select>
          </div>
        </div>
        
        <div class="strategies-grid">
          <div 
            v-for="strategy in filteredStrategies" 
            :key="strategy.id"
            class="strategy-card"
            @click="viewStrategy(strategy)"
          >
            <div class="strategy-header">
              <div class="strategy-info">
                <h3>{{ strategy.name }}</h3>
                <p>{{ strategy.description }}</p>
              </div>
              <div class="strategy-status" :class="strategy.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ getStatusText(strategy.status) }}</span>
              </div>
            </div>
            
            <div class="strategy-metrics">
              <div class="metric-row">
                <div class="metric">
                  <span class="metric-label">年化收益</span>
                  <span class="metric-value" :class="getPerformanceClass(strategy.annualReturn)">
                    {{ strategy.annualReturn }}%
                  </span>
                </div>
                <div class="metric">
                  <span class="metric-label">最大回撤</span>
                  <span class="metric-value" :class="getRiskClass(strategy.maxDrawdown)">
                    {{ strategy.maxDrawdown }}%
                  </span>
                </div>
              </div>
              
              <div class="metric-row">
                <div class="metric">
                  <span class="metric-label">夏普比率</span>
                  <span class="metric-value">{{ strategy.sharpeRatio }}</span>
                </div>
                <div class="metric">
                  <span class="metric-label">胜率</span>
                  <span class="metric-value">{{ strategy.winRate }}%</span>
                </div>
              </div>
            </div>
            
            <div class="strategy-tags">
              <span 
                v-for="tag in strategy.tags" 
                :key="tag"
                class="strategy-tag"
              >
                {{ tag }}
              </span>
            </div>
            
            <div class="strategy-actions">
              <button class="action-btn" @click.stop="editStrategy(strategy)">
                <i class="fas fa-edit"></i>
              </button>
              <button class="action-btn" @click.stop="backtestStrategy(strategy)">
                <i class="fas fa-chart-line"></i>
              </button>
              <button class="action-btn" @click.stop="deployStrategy(strategy)">
                <i class="fas fa-rocket"></i>
              </button>
              <button class="action-btn" @click.stop="deleteStrategy(strategy)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- AI策略生成 -->
      <section class="ai-generation-section">
        <div class="section-header">
          <h2>AI策略生成</h2>
          <p>使用人工智能快速生成量化策略</p>
        </div>
        
        <div class="ai-interface">
          <div class="ai-input-area">
            <div class="input-group">
              <label>策略需求描述</label>
              <textarea 
                v-model="strategyDescription"
                placeholder="请描述您想要的策略特征，例如：基于均线和RSI的趋势跟踪策略，适合A股市场，风险偏好中等..."
                rows="4"
              ></textarea>
            </div>
            
            <div class="input-group">
              <label>策略类型</label>
              <select v-model="aiStrategyType">
                <option value="trend">趋势跟踪</option>
                <option value="mean-reversion">均值回归</option>
                <option value="momentum">动量策略</option>
                <option value="arbitrage">套利策略</option>
                <option value="custom">自定义</option>
              </select>
            </div>
            
            <div class="input-group">
              <label>风险偏好</label>
              <div class="risk-slider">
                <input 
                  type="range" 
                  min="1" 
                  max="5" 
                  v-model="riskPreference"
                  class="slider"
                >
                <div class="risk-labels">
                  <span>保守</span>
                  <span>稳健</span>
                  <span>平衡</span>
                  <span>积极</span>
                  <span>激进</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="ai-output-area">
            <div class="generation-controls">
              <button 
                class="generate-btn" 
                @click="generateStrategy"
                :disabled="isGenerating || !strategyDescription"
              >
                <i class="fas fa-magic" v-if="!isGenerating"></i>
                <i class="fas fa-spinner fa-spin" v-if="isGenerating"></i>
                <span>{{ isGenerating ? '生成中...' : '生成策略' }}</span>
              </button>
            </div>
            
            <div class="generated-strategy" v-if="generatedStrategy">
              <h3>生成的策略</h3>
              <div class="strategy-preview">
                <div class="preview-header">
                  <h4>{{ generatedStrategy.name }}</h4>
                  <div class="preview-score">
                    <span class="score-label">AI评分</span>
                    <span class="score-value">{{ generatedStrategy.aiScore }}</span>
                  </div>
                </div>
                
                <div class="preview-content">
                  <p>{{ generatedStrategy.description }}</p>
                  
                  <div class="preview-params">
                    <h5>策略参数</h5>
                    <div class="params-list">
                      <div 
                        v-for="param in generatedStrategy.parameters" 
                        :key="param.name"
                        class="param-item"
                      >
                        <span class="param-name">{{ param.name }}:</span>
                        <span class="param-value">{{ param.value }}</span>
                        <span class="param-desc">{{ param.description }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="preview-actions">
                    <button class="accept-btn" @click="acceptGeneratedStrategy">
                      <i class="fas fa-check"></i>
                      <span>采纳策略</span>
                    </button>
                    <button class="regenerate-btn" @click="regenerateStrategy">
                      <i class="fas fa-redo"></i>
                      <span>重新生成</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const selectedCategory = ref('all')
const searchQuery = ref('')
const sortBy = ref('name')
const strategyDescription = ref('')
const aiStrategyType = ref('trend')
const riskPreference = ref(3)
const isGenerating = ref(false)
const generatedStrategy = ref(null)

// 策略统计
const strategyStats = ref([
  {
    id: 1,
    icon: 'fas fa-chart-line',
    label: '总策略数',
    value: '156',
    change: '+12',
    trend: 'up'
  },
  {
    id: 2,
    icon: 'fas fa-rocket',
    label: '运行中',
    value: '23',
    change: '+5',
    trend: 'up'
  },
  {
    id: 3,
    icon: 'fas fa-trophy',
    label: '高收益策略',
    value: '48',
    change: '+8',
    trend: 'up'
  },
  {
    id: 4,
    icon: 'fas fa-robot',
    label: 'AI生成',
    value: '67',
    change: '+15',
    trend: 'up'
  }
])

// 策略分类
const strategyCategories = ref([
  {
    id: 'trend',
    name: '趋势跟踪',
    description: '基于价格趋势的策略',
    icon: 'fas fa-chart-line',
    count: 42,
    avgPerformance: 15.2,
    performanceClass: 'good'
  },
  {
    id: 'mean-reversion',
    name: '均值回归',
    description: '基于均值回归的策略',
    icon: 'fas fa-balance-scale',
    count: 38,
    avgPerformance: 12.8,
    performanceClass: 'normal'
  },
  {
    id: 'momentum',
    name: '动量策略',
    description: '基于价格动量的策略',
    icon: 'fas fa-rocket',
    count: 31,
    avgPerformance: 18.5,
    performanceClass: 'excellent'
  },
  {
    id: 'arbitrage',
    name: '套利策略',
    description: '基于价差的套利策略',
    icon: 'fas fa-exchange-alt',
    count: 25,
    avgPerformance: 8.3,
    performanceClass: 'normal'
  },
  {
    id: 'ai-generated',
    name: 'AI生成',
    description: '人工智能生成的策略',
    icon: 'fas fa-robot',
    count: 20,
    avgPerformance: 22.1,
    performanceClass: 'excellent'
  }
])

// 策略列表
const strategies = ref([
  {
    id: 1,
    name: '双均线趋势跟踪',
    description: '基于短期和长期均线的趋势跟踪策略',
    category: 'trend',
    annualReturn: 15.2,
    maxDrawdown: -8.5,
    sharpeRatio: 1.23,
    winRate: 58.3,
    status: 'active',
    tags: ['趋势', '均线', '中风险'],
    created: '2024-01-15'
  },
  {
    id: 2,
    name: 'RSI均值回归',
    description: '利用RSI指标进行均值回归交易',
    category: 'mean-reversion',
    annualReturn: 12.8,
    maxDrawdown: -6.2,
    sharpeRatio: 1.05,
    winRate: 62.1,
    status: 'active',
    tags: ['均值回归', 'RSI', '低风险'],
    created: '2024-01-20'
  },
  {
    id: 3,
    name: '动量突破策略',
    description: '基于价格动量的突破交易策略',
    category: 'momentum',
    annualReturn: 22.5,
    maxDrawdown: -12.8,
    sharpeRatio: 1.67,
    winRate: 55.2,
    status: 'testing',
    tags: ['动量', '突破', '高风险'],
    created: '2024-02-01'
  },
  {
    id: 4,
    name: '跨市场套利',
    description: '利用不同市场间的价差进行套利',
    category: 'arbitrage',
    annualReturn: 8.3,
    maxDrawdown: -3.2,
    sharpeRatio: 0.85,
    winRate: 71.5,
    status: 'active',
    tags: ['套利', '跨市场', '低风险'],
    created: '2024-02-10'
  },
  {
    id: 5,
    name: 'AI增强趋势策略',
    description: 'AI优化的趋势跟踪策略',
    category: 'ai-generated',
    annualReturn: 25.8,
    maxDrawdown: -10.5,
    sharpeRatio: 1.89,
    winRate: 61.2,
    status: 'active',
    tags: ['AI', '趋势', '中高风险'],
    created: '2024-02-15'
  }
])

// 计算属性
const filteredStrategies = computed(() => {
  let filtered = strategies.value

  // 按分类过滤
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(s => s.category === selectedCategory.value)
  }

  // 按搜索词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(s => 
      s.name.toLowerCase().includes(query) || 
      s.description.toLowerCase().includes(query) ||
      s.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'performance':
        return b.annualReturn - a.annualReturn
      case 'sharpe':
        return b.sharpeRatio - a.sharpeRatio
      case 'created':
        return new Date(b.created).getTime() - new Date(a.created).getTime()
      default:
        return 0
    }
  })

  return filtered
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
    testing: '测试中',
    inactive: '已停止',
    draft: '草稿'
  }
  return statusMap[status] || status
}

const getPerformanceClass = (value: number) => {
  if (value > 20) return 'excellent'
  if (value > 15) return 'good'
  if (value > 10) return 'normal'
  return 'poor'
}

const getRiskClass = (value: number) => {
  if (value > -5) return 'high'
  if (value > -10) return 'medium'
  return 'low'
}

const selectCategory = (category: any) => {
  selectedCategory.value = category.id
}

const createNewStrategy = () => {
  router.push('/function/strategy-center/dashboard')
}

const importStrategy = () => {
  console.log('导入策略')
}

const viewStrategy = (strategy: any) => {
  router.push('/function/strategy-center/architecture')
}

const editStrategy = (strategy: any) => {
  console.log('编辑策略', strategy)
}

const backtestStrategy = (strategy: any) => {
  router.push('/function/backtest-lab/dashboard')
}

const deployStrategy = (strategy: any) => {
  console.log('部署策略', strategy)
}

const deleteStrategy = (strategy: any) => {
  const index = strategies.value.findIndex(s => s.id === strategy.id)
  if (index > -1) {
    strategies.value.splice(index, 1)
  }
}

const generateStrategy = async () => {
  isGenerating.value = true
  
  // 模拟AI生成策略
  setTimeout(() => {
    generatedStrategy.value = {
      name: 'AI生成策略_' + Date.now(),
      description: '基于您的需求描述，AI生成了一个结合趋势跟踪和均值回归的混合策略',
      aiScore: 8.5,
      parameters: [
        { name: '短期均线', value: 'MA5', description: '短期趋势指标' },
        { name: '长期均线', value: 'MA20', description: '长期趋势指标' },
        { name: 'RSI周期', value: '14', description: '超买超卖指标' },
        { name: '止损比例', value: '2%', description: '风险控制参数' }
      ]
    }
    isGenerating.value = false
  }, 3000)
}

const acceptGeneratedStrategy = () => {
  if (generatedStrategy.value) {
    const newStrategy = {
      id: Date.now(),
      name: generatedStrategy.value.name,
      description: generatedStrategy.value.description,
      category: 'ai-generated',
      annualReturn: Math.random() * 20 + 10,
      maxDrawdown: -Math.random() * 10 - 5,
      sharpeRatio: Math.random() * 1.5 + 0.8,
      winRate: Math.random() * 30 + 50,
      status: 'draft',
      tags: ['AI生成', '混合策略'],
      created: new Date().toISOString().split('T')[0]
    }
    strategies.value.unshift(newStrategy)
    generatedStrategy.value = null
  }
}

const regenerateStrategy = () => {
  generateStrategy()
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
@use '@/assets/styles/variables.scss' as *;

.strategy-page {
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
        color: var(--secondary);
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

// 分类区域
.categories-section {
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
  
  .categories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    
    .category-card {
      display: flex;
      align-items: center;
      gap: 20px;
      padding: 24px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover, &.active {
        transform: translateY(-4px);
        border-color: var(--secondary);
        box-shadow: 0 12px 24px rgba(124, 58, 237, 0.2);
      }
      
      .category-icon {
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(124, 58, 237, 0.1);
        border-radius: 12px;
        color: var(--secondary);
        font-size: 24px;
      }
      
      .category-content {
        flex: 1;
        
        h3 {
          margin: 0 0 8px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        p {
          margin: 0 0 12px 0;
          color: var(--text-secondary);
          font-size: 14px;
          line-height: 1.5;
        }
        
        .category-stats {
          display: flex;
          gap: 16px;
          
          .strategy-count {
            font-size: 12px;
            color: var(--text-secondary);
          }
          
          .performance {
            font-size: 12px;
            font-weight: 500;
            
            &.excellent {
              color: var(--market-rise);
            }
            
            &.good {
              color: #84cc16;
            }
            
            &.normal {
              color: var(--text-primary);
            }
            
            &.poor {
              color: var(--market-fall);
            }
          }
        }
      }
    }
  }
}

// 策略列表区域
.strategies-section {
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
    
    .filter-controls {
      display: flex;
      gap: 16px;
      
      .search-box {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 8px 12px;
        
        i {
          color: var(--text-secondary);
          margin-right: 8px;
        }
        
        input {
          background: none;
          border: none;
          color: var(--text-primary);
          outline: none;
          width: 200px;
        }
      }
      
      .sort-select {
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: var(--text-primary);
        outline: none;
      }
    }
  }
  
  .strategies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 24px;
    
    .strategy-card {
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 24px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-8px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
      }
      
      .strategy-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 20px;
        
        .strategy-info {
          flex: 1;
          
          h3 {
            margin: 0 0 8px 0;
            font-size: 20px;
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
        
        .strategy-status {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 8px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          
          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            
            &.active {
              background: var(--market-rise);
              animation: pulse 2s infinite;
            }
            
            &.testing {
              background: #f59e0b;
            }
            
            &.inactive {
              background: #6b7280;
            }
            
            &.draft {
              background: #3b82f6;
            }
          }
          
          .status-text {
            font-size: 12px;
            color: var(--text-secondary);
          }
        }
      }
      
      .strategy-metrics {
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
              font-size: 18px;
              font-weight: 600;
              
              &.excellent {
                color: var(--market-rise);
              }
              
              &.good {
                color: #84cc16;
              }
              
              &.normal {
                color: var(--text-primary);
              }
              
              &.poor {
                color: var(--market-fall);
              }
            }
          }
        }
      }
      
      .strategy-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 20px;
        
        .strategy-tag {
          padding: 4px 8px;
          background: rgba(124, 58, 237, 0.1);
          color: var(--secondary);
          border-radius: 4px;
          font-size: 12px;
        }
      }
      
      .strategy-actions {
        display: flex;
        justify-content: space-between;
        
        .action-btn {
          width: 36px;
          height: 36px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
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

// AI生成区域
.ai-generation-section {
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
  
  .ai-interface {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    background: rgba(26, 26, 46, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 32px;
    
    .ai-input-area {
      .input-group {
        margin-bottom: 24px;
        
        label {
          display: block;
          margin-bottom: 8px;
          color: var(--text-primary);
          font-size: 14px;
          font-weight: 500;
        }
        
        textarea, select {
          width: 100%;
          padding: 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-primary);
          font-size: 14px;
          
          &:focus {
            outline: none;
            border-color: var(--secondary);
          }
        }
        
        textarea {
          resize: vertical;
          min-height: 100px;
        }
        
        .risk-slider {
          .slider {
            width: 100%;
            margin-bottom: 8px;
          }
          
          .risk-labels {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-secondary);
          }
        }
      }
    }
    
    .ai-output-area {
      .generation-controls {
        margin-bottom: 24px;
        
        .generate-btn {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 16px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
          }
          
          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
        }
      }
      
      .generated-strategy {
        .strategy-preview {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          padding: 20px;
          
          h3 {
            margin: 0 0 16px 0;
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          .preview-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            
            h4 {
              margin: 0;
              font-size: 16px;
              font-weight: 600;
              color: var(--text-primary);
            }
            
            .preview-score {
              text-align: center;
              
              .score-label {
                display: block;
                font-size: 12px;
                color: var(--text-secondary);
                margin-bottom: 4px;
              }
              
              .score-value {
                font-size: 20px;
                font-weight: 700;
                color: var(--secondary);
              }
            }
          }
          
          .preview-content {
            p {
              margin: 0 0 16px 0;
              color: var(--text-secondary);
              font-size: 14px;
              line-height: 1.5;
            }
            
            .preview-params {
              margin-bottom: 20px;
              
              h5 {
                margin: 0 0 12px 0;
                font-size: 14px;
                font-weight: 600;
                color: var(--text-primary);
              }
              
              .params-list {
                .param-item {
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  margin-bottom: 8px;
                  padding: 8px;
                  background: rgba(255, 255, 255, 0.02);
                  border-radius: 4px;
                  
                  .param-name {
                    font-size: 12px;
                    color: var(--text-secondary);
                    min-width: 80px;
                  }
                  
                  .param-value {
                    font-size: 12px;
                    color: var(--secondary);
                    font-weight: 500;
                    min-width: 60px;
                  }
                  
                  .param-desc {
                    font-size: 12px;
                    color: var(--text-secondary);
                    flex: 1;
                  }
                }
              }
            }
            
            .preview-actions {
              display: flex;
              gap: 12px;
              
              .accept-btn, .regenerate-btn {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                border: none;
              }
              
              .accept-btn {
                background: rgba(16, 185, 129, 0.2);
                color: var(--market-rise);
                
                &:hover {
                  background: rgba(16, 185, 129, 0.3);
                }
              }
              
              .regenerate-btn {
                background: rgba(255, 255, 255, 0.05);
                color: var(--text-primary);
                border: 1px solid rgba(255, 255, 255, 0.1);
                
                &:hover {
                  background: rgba(255, 255, 255, 0.1);
                }
              }
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
  .ai-interface {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .strategies-grid {
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
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
  
  .categories-grid {
    grid-template-columns: 1fr;
  }
  
  .strategies-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    .filter-controls {
      flex-direction: column;
      gap: 12px;
      
      .search-box input {
        width: 150px;
      }
    }
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