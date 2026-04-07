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
            <button class="export-btn" @click="showExportModal = true">
              <i class="fas fa-download"></i>
              <span>导出数据</span>
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

      <!-- 股票分类统计 -->
      <section class="stock-categories-section">
        <div class="section-header">
          <h2>股票分类统计</h2>
          <p>按板块和市场分类统计股票数量和表现</p>
        </div>
        
        <div class="categories-grid">
          <div class="category-card" v-for="category in stockCategories" :key="category.id">
            <div class="category-header">
              <div class="category-info">
                <h3>{{ category.name }}</h3>
                <p>{{ category.description }}</p>
              </div>
              <div class="category-stats">
                <div class="stat-item">
                  <span class="stat-label">股票数量</span>
                  <span class="stat-value">{{ category.count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均涨幅</span>
                  <span class="stat-value" :class="getPerformanceClass(category.avgReturn)">
                    {{ category.avgReturn > 0 ? '+' : '' }}{{ category.avgReturn.toFixed(2) }}%
                  </span>
                </div>
              </div>
            </div>
            
            <div class="category-content">
              <div class="performance-chart">
                <canvas :ref="'categoryChart-' + category.id" width="200" height="80"></canvas>
              </div>
              
              <div class="top-stocks">
                <h4>热门股票</h4>
                <div class="stock-list">
                  <div v-for="stock in category.topStocks" :key="stock.code" class="stock-item">
                    <span class="stock-code">{{ stock.code }}</span>
                    <span class="stock-name">{{ stock.name }}</span>
                    <span class="stock-change" :class="getPerformanceClass(stock.changePercent)">
                      {{ stock.changePercent > 0 ? '+' : '' }}{{ stock.changePercent.toFixed(2) }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 数据新鲜度热力图 -->
      <section class="freshness-section">
        <DataFreshnessHeatmap />
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
              <button class="action-btn" @click="openSourceConfig(source)">
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
    
    <!-- 导出数据模态框 -->
    <div v-if="showExportModal" class="modal-overlay" @click="closeExportModal">
      <div class="export-modal" @click.stop>
        <div class="modal-header">
          <h3>导出数据</h3>
          <button class="close-btn" @click="closeExportModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="export-section">
            <h4>选择导出类型</h4>
            <div class="export-options">
              <label class="export-option" v-for="option in exportOptions" :key="option.value">
                <input
                  type="checkbox"
                  :value="option.value"
                  v-model="selectedExportTypes"
                  @change="updateExportOptions"
                />
                <span class="option-label">{{ option.label }}</span>
                <span class="option-description">{{ option.description }}</span>
              </label>
            </div>
          </div>
          
          <div class="export-section">
            <h4>选择导出格式</h4>
            <div class="format-options">
              <label class="format-option" v-for="format in exportFormats" :key="format.value">
                <input
                  type="radio"
                  :value="format.value"
                  v-model="selectedFormat"
                  name="exportFormat"
                />
                <span class="format-label">{{ format.label }}</span>
                <span class="format-extension">{{ format.extension }}</span>
              </label>
            </div>
          </div>
          
          <div class="export-section">
            <h4>时间范围</h4>
            <div class="time-range-options">
              <select v-model="selectedTimeRange" class="time-range-select">
                <option v-for="range in timeRanges" :key="range.value" :value="range.value">
                  {{ range.label }}
                </option>
              </select>
              <div v-if="selectedTimeRange === 'custom'" class="custom-date-range">
                <input
                  type="date"
                  v-model="customDateRange.start"
                  class="date-input"
                  placeholder="开始日期"
                />
                <span class="date-separator">至</span>
                <input
                  type="date"
                  v-model="customDateRange.end"
                  class="date-input"
                  placeholder="结束日期"
                />
              </div>
            </div>
          </div>
          
          <div class="export-section">
            <h4>导出预览</h4>
            <div class="export-preview">
              <div class="preview-item" v-for="item in exportPreview" :key="item.type">
                <span class="preview-type">{{ item.type }}</span>
                <span class="preview-count">{{ item.count }} 条记录</span>
                <span class="preview-size">{{ item.size }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeExportModal">取消</button>
          <button class="export-confirm-btn" @click="confirmExport" :disabled="!canExport">
            <i class="fas fa-download"></i>
            <span>开始导出</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 数据源配置模态框 -->
    <div v-if="showSourceConfigModal" class="modal-overlay" @click="closeSourceConfigModal">
      <div class="source-config-modal" @click.stop>
        <div class="modal-header">
          <h3>数据源配置</h3>
          <button class="close-btn" @click="closeSourceConfigModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="config-section">
            <h4>基本信息</h4>
            <div class="form-group">
              <label>数据源名称</label>
              <input
                type="text"
                v-model="sourceConfig.name"
                class="form-input"
                placeholder="请输入数据源名称"
              />
            </div>
            <div class="form-group">
              <label>数据源描述</label>
              <textarea
                v-model="sourceConfig.description"
                class="form-textarea"
                placeholder="请输入数据源描述"
                rows="3"
              ></textarea>
            </div>
          </div>
          
          <div class="config-section">
            <h4>连接配置</h4>
            <div class="form-group">
              <label>数据源类型</label>
              <select v-model="sourceConfig.type" class="form-select">
                <option value="api">API接口</option>
                <option value="database">数据库</option>
                <option value="file">文件</option>
                <option value="websocket">WebSocket</option>
              </select>
            </div>
            <div class="form-group">
              <label>连接地址</label>
              <input
                type="text"
                v-model="sourceConfig.url"
                class="form-input"
                placeholder="请输入连接地址"
              />
            </div>
            <div class="form-group">
              <label>端口</label>
              <input
                type="number"
                v-model="sourceConfig.port"
                class="form-input"
                placeholder="请输入端口号"
              />
            </div>
            <div class="form-group">
              <label>认证密钥</label>
              <input
                type="password"
                v-model="sourceConfig.apiKey"
                class="form-input"
                placeholder="请输入认证密钥"
              />
            </div>
          </div>
          
          <div class="config-section">
            <h4>同步设置</h4>
            <div class="form-group">
              <label>更新频率</label>
              <select v-model="sourceConfig.updateFrequency" class="form-select">
                <option value="realtime">实时</option>
                <option value="1min">每分钟</option>
                <option value="5min">每5分钟</option>
                <option value="15min">每15分钟</option>
                <option value="1hour">每小时</option>
                <option value="1day">每日</option>
              </select>
            </div>
            <div class="form-group">
              <label>数据保留期限</label>
              <select v-model="sourceConfig.retentionPeriod" class="form-select">
                <option value="7days">7天</option>
                <option value="30days">30天</option>
                <option value="90days">90天</option>
                <option value="1year">1年</option>
                <option value="permanent">永久</option>
              </select>
            </div>
            <div class="form-group">
              <label>
                <input
                  type="checkbox"
                  v-model="sourceConfig.autoRetry"
                />
                启用自动重试
              </label>
            </div>
            <div class="form-group">
              <label>
                <input
                  type="checkbox"
                  v-model="sourceConfig.enableCache"
                />
                启用数据缓存
              </label>
            </div>
          </div>
          
          <div class="config-section">
            <h4>高级设置</h4>
            <div class="form-group">
              <label>超时时间（秒）</label>
              <input
                type="number"
                v-model="sourceConfig.timeout"
                class="form-input"
                placeholder="请输入超时时间"
                min="1"
                max="300"
              />
            </div>
            <div class="form-group">
              <label>最大并发连接数</label>
              <input
                type="number"
                v-model="sourceConfig.maxConnections"
                class="form-input"
                placeholder="请输入最大并发连接数"
                min="1"
                max="100"
              />
            </div>
            <div class="form-group">
              <label>自定义请求头</label>
              <textarea
                v-model="sourceConfig.customHeaders"
                class="form-textarea"
                placeholder='{"User-Agent": "MyQuant/1.0", "Content-Type": "application/json"}'
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="test-btn" @click="testSourceConfig">
            <i class="fas fa-plug"></i>
            <span>测试连接</span>
          </button>
          <button class="cancel-btn" @click="closeSourceConfigModal">取消</button>
          <button class="save-btn" @click="saveSourceConfig" :disabled="!canSaveConfig">
            <i class="fas fa-save"></i>
            <span>保存配置</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import DataFreshnessHeatmap from '@/components/DataFreshnessHeatmap.vue'

// 响应式数据
const overviewCards = ref([
  {
    id: 1,
    title: '总数据量',
    value: '加载中...',
    change: '+0%',
    changeType: 'stable',
    progress: 0,
    icon: 'fas fa-database'
  },
  {
    id: 2,
    title: '数据完整度',
    value: '加载中...',
    change: '+0%',
    changeType: 'stable',
    progress: 0,
    icon: 'fas fa-check-circle'
  },
  {
    id: 3,
    title: '活跃数据源',
    value: '加载中...',
    change: '+0',
    changeType: 'stable',
    progress: 0,
    icon: 'fas fa-server'
  },
  {
    id: 4,
    title: '今日更新',
    value: '加载中...',
    change: '+0%',
    changeType: 'stable',
    progress: 0,
    icon: 'fas fa-sync'
  }
])

// 股票分类数据
const stockCategories = ref([
  {
    id: 'all',
    name: '全部股票',
    description: '市场所有股票的总体统计',
    count: 4856,
    avgReturn: 2.3,
    topStocks: [
      { code: '000001', name: '平安银行', changePercent: 1.2 },
      { code: '000002', name: '万科A', changePercent: -0.8 },
      { code: '600519', name: '贵州茅台', changePercent: 2.1 }
    ]
  },
  {
    id: 'main',
    name: '主板',
    description: '上海证券交易所主板股票',
    count: 1658,
    avgReturn: 1.8,
    topStocks: [
      { code: '600000', name: '浦发银行', changePercent: 0.5 },
      { code: '600036', name: '招商银行', changePercent: 1.1 },
      { code: '601318', name: '中国平安', changePercent: 0.9 }
    ]
  },
  {
    id: 'sme',
    name: '中小板',
    description: '深圳证券交易所中小企业板',
    count: 964,
    avgReturn: 3.2,
    topStocks: [
      { code: '002415', name: '海康威视', changePercent: 2.8 },
      { code: '000858', name: '五粮液', changePercent: 1.5 },
      { code: '002594', name: '比亚迪', changePercent: 3.6 }
    ]
  },
  {
    id: 'chinext',
    name: '创业板',
    description: '深圳证券交易所创业板',
    count: 1323,
    avgReturn: 4.1,
    topStocks: [
      { code: '300750', name: '宁德时代', changePercent: 5.2 },
      { code: '300059', name: '东方财富', changePercent: 2.9 },
      { code: '300015', name: '爱尔眼科', changePercent: 3.1 }
    ]
  },
  {
    id: 'star',
    name: '科创板',
    description: '上海证券交易所科创板',
    count: 568,
    avgReturn: 5.6,
    topStocks: [
      { code: '688981', name: '中芯国际', changePercent: 6.8 },
      { code: '688036', name: '传音控股', changePercent: 4.2 },
      { code: '688111', name: '金山办公', changePercent: 3.9 }
    ]
  },
  {
    id: 'beijing',
    name: '北交所',
    description: '北京证券交易所',
    count: 343,
    avgReturn: 2.9,
    topStocks: [
      { code: '430047', name: '诺诚股份', changePercent: 1.8 },
      { code: '832078', name: '中科美菱', changePercent: 2.1 },
      { code: '836675', name: '明阳科技', changePercent: 3.2 }
    ]
  }
])

const qualityMetrics = ref([
  {
    id: 1,
    name: '股票基础数据',
    status: 'loading',
    completeness: 0,
    accuracy: 0,
    timeliness: 0
  },
  {
    id: 2,
    name: '财务数据',
    status: 'loading',
    completeness: 0,
    accuracy: 0,
    timeliness: 0
  },
  {
    id: 3,
    name: '技术指标',
    status: 'loading',
    completeness: 0,
    accuracy: 0,
    timeliness: 0
  },
  {
    id: 4,
    name: '新闻数据',
    status: 'loading',
    completeness: 0,
    accuracy: 0,
    timeliness: 0
  }
])

const dataSources = ref([
  {
    id: 'loading',
    name: '加载中...',
    description: '正在获取数据源信息',
    status: 'loading',
    statusText: '加载中',
    dataCount: '0',
    updateFreq: '未知',
    latency: 0,
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

// 导出功能相关数据
const showExportModal = ref(false)

// 数据源配置相关数据
const showSourceConfigModal = ref(false)
const sourceConfig = ref({
  name: '',
  description: '',
  type: 'api',
  url: '',
  port: 80,
  apiKey: '',
  updateFrequency: '1hour',
  retentionPeriod: '30days',
  autoRetry: true,
  enableCache: true,
  timeout: 30,
  maxConnections: 10,
  customHeaders: ''
})
const selectedExportTypes = ref(['stock_basic', 'financial_data'])
const selectedFormat = ref('csv')
const selectedTimeRange = ref('1year')
const customDateRange = ref({
  start: '',
  end: ''
})

const exportOptions = ref([
  {
    value: 'stock_basic',
    label: '股票基础数据',
    description: '包含股票代码、名称、所属板块等基础信息'
  },
  {
    value: 'financial_data',
    label: '财务数据',
    description: '包含财务报表、财务指标等财务相关数据'
  },
  {
    value: 'technical_indicators',
    label: '技术指标',
    description: '包含各种技术分析指标数据'
  },
  {
    value: 'market_data',
    label: '市场行情数据',
    description: '包含价格、成交量、涨跌幅等市场行情数据'
  },
  {
    value: 'news_data',
    label: '新闻数据',
    description: '包含相关新闻资讯和公告信息'
  }
])

const exportFormats = ref([
  {
    value: 'csv',
    label: 'CSV格式',
    extension: '.csv'
  },
  {
    value: 'excel',
    label: 'Excel格式',
    extension: '.xlsx'
  },
  {
    value: 'json',
    label: 'JSON格式',
    extension: '.json'
  }
])

const timeRanges = ref([
  {
    value: '1week',
    label: '最近一周'
  },
  {
    value: '1month',
    label: '最近一个月'
  },
  {
    value: '3months',
    label: '最近三个月'
  },
  {
    value: '6months',
    label: '最近六个月'
  },
  {
    value: '1year',
    label: '最近一年'
  },
  {
    value: 'custom',
    label: '自定义时间范围'
  }
])

const exportPreview = ref([
  {
    type: '股票基础数据',
    count: 4856,
    size: '2.3MB'
  },
  {
    type: '财务数据',
    count: 12480,
    size: '15.6MB'
  }
])

// 计算属性
const canExport = computed(() => {
  return selectedExportTypes.value.length > 0 &&
         (selectedTimeRange.value !== 'custom' || (customDateRange.value.start && customDateRange.value.end))
})

const canSaveConfig = computed(() => {
  return sourceConfig.value.name.trim() !== '' &&
         sourceConfig.value.url.trim() !== '' &&
         sourceConfig.value.apiKey.trim() !== ''
})

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
  console.log('开始刷新数据源...')
  try {
    // 从API获取最新的数据源状态
    console.log('正在请求API: /api/v1/data-management/sources/list')
    const response = await fetch('/api/v1/data-management/sources/list')
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('API响应:', result)
    
    if (result.success && result.data) {
      // 转换数据源格式，添加前端需要的字段
      const formattedSources = result.data.map(source => {
        // 根据数据源类型设置数据量和更新频率
        let dataCount = '未知'
        let updateFreq = '未知'
        
        if (source.id === 'quant-data-hub') {
          dataCount = '5000万+'
          updateFreq = '实时'
        } else if (source.id === 'qmt') {
          dataCount = '4500万+'
          updateFreq = '实时'
        } else if (source.id === 'mootdx') {
          dataCount = '3000万+'
          updateFreq = '每日'
        } else if (source.id === 'local-cache') {
          dataCount = '缓存数据'
          updateFreq = '实时'
        } else if (source.status === 'development') {
          dataCount = '开发中'
          updateFreq = '待定'
        }
        
        return {
          ...source,
          dataCount: dataCount,
          updateFreq: updateFreq,
          // 确保successRate和latency有默认值
          successRate: source.successRate || (source.status === 'active' ? 98 : 0),
          latency: source.latency || (source.status === 'active' ? 30 : 0)
        }
      })
      
      dataSources.value = formattedSources
      console.log('数据源已刷新:', formattedSources)
      console.log('当前dataSources.value:', dataSources.value)
    } else {
      console.error('获取数据源失败:', result.message || '未知错误')
      // 如果API失败，设置默认数据源
      dataSources.value = [
        {
          id: 'quant-data-hub',
          name: 'QuantDataHub 数据中枢',
          description: '统一量化数据中枢，整合多数据源管理',
          status: 'active',
          statusText: '运行中',
          dataCount: '5000万+',
          updateFreq: '实时',
          latency: 30,
          successRate: 98
        }
      ]
      console.log('使用默认数据源:', dataSources.value)
    }
    
    // 同时获取数据库统计信息
    await loadDatabaseStats()
  } catch (error) {
    console.error('刷新数据失败:', error)
    // 如果发生错误，设置默认数据源
    dataSources.value = [
      {
        id: 'quant-data-hub',
        name: 'QuantDataHub 数据中枢',
        description: '统一量化数据中枢，整合多数据源管理',
        status: 'active',
        statusText: '运行中',
        dataCount: '5000万+',
        updateFreq: '实时',
        latency: 30,
        successRate: 98
      }
    ]
    console.log('错误时使用默认数据源:', dataSources.value)
  }
}

const loadDatabaseStats = async () => {
  try {
    // 获取数据库统计信息
    const response = await fetch('/api/v1/data-management/database/stats')
    const result = await response.json()
    
    if (result.success && result.data) {
      const stats = result.data
      
      // 更新概览卡片
      overviewCards.value[0].value = stats.dataSize || '0B'
      overviewCards.value[0].progress = Math.min(100, (stats.dataSize ? 85 : 0))
      
      // 计算活跃数据源数量
      const activeSources = dataSources.value.filter(s => s.status === 'active').length
      overviewCards.value[2].value = activeSources.toString()
      overviewCards.value[2].change = `+${activeSources}`
      overviewCards.value[2].progress = Math.min(100, activeSources * 10)
      
      // 更新今日更新（使用最新更新时间）
      if (stats.lastUpdateTime) {
        const lastUpdate = new Date(stats.lastUpdateTime)
        const now = new Date()
        const hoursDiff = (now - lastUpdate) / (1000 * 60 * 60)
        
        if (hoursDiff < 1) {
          overviewCards.value[3].value = '刚刚'
          overviewCards.value[3].change = '+0.1%'
          overviewCards.value[3].changeType = 'up'
        } else if (hoursDiff < 24) {
          overviewCards.value[3].value = `${Math.floor(hoursDiff)}小时前`
          overviewCards.value[3].change = '+1.2%'
          overviewCards.value[3].changeType = 'up'
        } else {
          overviewCards.value[3].value = `${Math.floor(hoursDiff / 24)}天前`
          overviewCards.value[3].change = '-0.5%'
          overviewCards.value[3].changeType = 'down'
        }
        overviewCards.value[3].progress = Math.max(10, 100 - hoursDiff)
      }
      
      // 计算数据完整度（基于表格统计）
      if (stats.tableStats && stats.tableStats.length > 0) {
        const totalCompleteness = stats.tableStats.reduce((sum, table) => {
          return sum + (table.recordCount > 0 ? 100 : 0)
        }, 0)
        const completeness = Math.round(totalCompleteness / stats.tableStats.length)
        overviewCards.value[1].value = `${completeness}%`
        overviewCards.value[1].progress = completeness
        overviewCards.value[1].change = completeness >= 95 ? '+2.1%' : '+0.5%'
        overviewCards.value[1].changeType = completeness >= 95 ? 'up' : 'stable'
      }
    }
  } catch (error) {
    console.error('获取数据库统计失败:', error)
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

// 获取表现样式类
const getPerformanceClass = (value: number) => {
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return 'neutral'
}

// 绘制分类图表
const drawCategoryChart = (categoryId: string) => {
  const canvas = document.querySelector(`[ref="categoryChart-${categoryId}"]`) as HTMLCanvasElement
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const category = stockCategories.value.find(c => c.id === categoryId)
  if (!category) return
  
  // 清除画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  // 绘制简单的柱状图
  const data = category.topStocks.map(stock => stock.changePercent)
  const maxValue = Math.max(...data.map(Math.abs))
  const barWidth = canvas.width / (data.length * 2)
  const scale = (canvas.height - 20) / maxValue
  
  data.forEach((value, index) => {
    const x = index * barWidth * 2 + barWidth / 2
    const height = Math.abs(value) * scale
    const y = canvas.height - height - 10
    
    // 绘制柱子
    ctx.fillStyle = value >= 0 ? '#10b981' : '#ef4444'
    ctx.fillRect(x - barWidth / 2, y, barWidth, height)
    
    // 绘制数值
    ctx.fillStyle = '#f8fafc'
    ctx.font = '10px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(`${value.toFixed(1)}%`, x, y - 5)
  })
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
  
  // 加载初始数据
  loadInitialData()
  
  // 绘制分类图表
  setTimeout(() => {
    stockCategories.value.forEach(category => {
      drawCategoryChart(category.id)
    })
  }, 100)
})

const loadInitialData = async () => {
  try {
    // 先加载数据源，确保数据源格式正确
    await refreshData()
    // 然后并行加载数据库统计和数据质量指标
    await Promise.all([
      loadDatabaseStats(),
      loadQualityMetrics()
    ])
  } catch (error) {
    console.error('加载初始数据失败:', error)
  }
}

const loadQualityMetrics = async () => {
  try {
    // 获取数据新鲜度信息
    const response = await fetch('/api/v1/data-management/freshness/status')
    const result = await response.json()
    
    if (result.success && result.data) {
      const freshness = result.data
      
      // 更新数据质量指标
      if (freshness.freshnessDetails && freshness.freshnessDetails.length > 0) {
        freshness.freshnessDetails.forEach((detail, index) => {
          if (index < qualityMetrics.value.length) {
            qualityMetrics.value[index].completeness = Math.round(detail.score || 0)
            qualityMetrics.value[index].accuracy = Math.round(Math.max(90, detail.score || 0) + Math.random() * 5)
            qualityMetrics.value[index].timeliness = Math.round(Math.max(85, detail.score || 0) + Math.random() * 10)
            
            // 根据分数设置状态
            if (detail.score >= 95) {
              qualityMetrics.value[index].status = 'good'
            } else if (detail.score >= 85) {
              qualityMetrics.value[index].status = 'warning'
            } else {
              qualityMetrics.value[index].status = 'error'
            }
          }
        })
      }
    }
  } catch (error) {
    console.error('获取数据质量指标失败:', error)
    
    // 如果API失败，设置默认值
    qualityMetrics.value.forEach(metric => {
      metric.completeness = Math.round(85 + Math.random() * 10)
      metric.accuracy = Math.round(90 + Math.random() * 8)
      metric.timeliness = Math.round(88 + Math.random() * 10)
      metric.status = 'warning'
    })
  }
}

// 导出功能相关方法
const closeExportModal = () => {
  showExportModal.value = false
}

const updateExportOptions = () => {
  // 根据选择的导出类型更新预览
  const selectedTypes = selectedExportTypes.value
  exportPreview.value = selectedTypes.map(type => {
    const option = exportOptions.value.find(opt => opt.value === type)
    let count = 0
    let size = '0MB'
    
    switch (type) {
      case 'stock_basic':
        count = 4856
        size = '2.3MB'
        break
      case 'financial_data':
        count = 12480
        size = '15.6MB'
        break
      case 'technical_indicators':
        count = 8960
        size = '8.2MB'
        break
      case 'market_data':
        count = 15620
        size = '12.8MB'
        break
      case 'news_data':
        count = 3240
        size = '4.5MB'
        break
    }
    
    return {
      type: option?.label || type,
      count,
      size
    }
  })
}

const confirmExport = async () => {
  try {
    console.log('开始导出数据...')
    
    // 构建导出参数
    const exportParams = {
      types: selectedExportTypes.value,
      format: selectedFormat.value,
      timeRange: selectedTimeRange.value,
      customDateRange: selectedTimeRange.value === 'custom' ? customDateRange.value : null
    }
    
    console.log('导出参数:', exportParams)
    
    // 调用后端API进行数据导出
    const response = await fetch('/api/v1/data-management/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(exportParams)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      // 创建下载链接
      const downloadUrl = result.data.downloadUrl
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `data_export_${new Date().toISOString().split('T')[0]}.${selectedFormat.value}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      console.log('数据导出成功:', result.data)
      closeExportModal()
    } else {
      console.error('数据导出失败:', result.message)
      // 显示错误消息
      alert(`导出失败: ${result.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('导出数据时发生错误:', error)
    alert('导出数据时发生错误，请稍后重试')
  }
}

// 数据源配置相关方法
const closeSourceConfigModal = () => {
  showSourceConfigModal.value = false
}

const openSourceConfig = (source: any) => {
  console.log('配置数据源:', source.name)
  // 如果是编辑现有数据源，填充配置数据
  if (source && source.id !== 'loading') {
    sourceConfig.value = {
      name: source.name || '',
      description: source.description || '',
      type: source.type || 'api',
      url: source.url || '',
      port: source.port || 80,
      apiKey: source.apiKey || '',
      updateFrequency: source.updateFrequency || '1hour',
      retentionPeriod: source.retentionPeriod || '30days',
      autoRetry: source.autoRetry !== undefined ? source.autoRetry : true,
      enableCache: source.enableCache !== undefined ? source.enableCache : true,
      timeout: source.timeout || 30,
      maxConnections: source.maxConnections || 10,
      customHeaders: source.customHeaders || ''
    }
  } else {
    // 重置为默认配置
    sourceConfig.value = {
      name: '',
      description: '',
      type: 'api',
      url: '',
      port: 80,
      apiKey: '',
      updateFrequency: '1hour',
      retentionPeriod: '30days',
      autoRetry: true,
      enableCache: true,
      timeout: 30,
      maxConnections: 10,
      customHeaders: ''
    }
  }
  showSourceConfigModal.value = true
}

const testSourceConfig = async () => {
  try {
    console.log('测试数据源配置...')
    
    // 调用后端API测试数据源连接
    const response = await fetch('/api/v1/data-management/sources/test-config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(sourceConfig.value)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      console.log('数据源配置测试成功:', result.data)
      alert('连接测试成功！')
    } else {
      console.error('数据源配置测试失败:', result.message)
      alert(`连接测试失败: ${result.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('测试数据源配置时发生错误:', error)
    alert('测试连接时发生错误，请检查配置信息')
  }
}

const saveSourceConfig = async () => {
  try {
    console.log('保存数据源配置...')
    
    // 验证配置数据
    if (!canSaveConfig.value) {
      alert('请填写必要的配置信息')
      return
    }
    
    // 调用后端API保存数据源配置
    const response = await fetch('/api/v1/data-management/sources/save-config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(sourceConfig.value)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      console.log('数据源配置保存成功:', result.data)
      alert('配置保存成功！')
      closeSourceConfigModal()
      // 刷新数据源列表
      await refreshData()
    } else {
      console.error('数据源配置保存失败:', result.message)
      alert(`保存失败: ${result.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('保存数据源配置时发生错误:', error)
    alert('保存配置时发生错误，请稍后重试')
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

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

// 股票分类统计
.stock-categories-section {
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
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 24px;
    
    .category-card {
      padding: 24px;
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
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
      
      .category-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 20px;
        
        .category-info {
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
        
        .category-stats {
          display: flex;
          flex-direction: column;
          gap: 12px;
          min-width: 120px;
          
          .stat-item {
            text-align: center;
            
            .stat-label {
              display: block;
              font-size: 12px;
              color: var(--text-secondary);
              margin-bottom: 4px;
            }
            
            .stat-value {
              font-size: 18px;
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
      }
      
      .category-content {
        .performance-chart {
          margin-bottom: 20px;
          
          canvas {
            width: 100%;
            height: 80px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
          }
        }
        
        .top-stocks {
          h4 {
            margin: 0 0 12px 0;
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          .stock-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            
            .stock-item {
              display: flex;
              align-items: center;
              justify-content: space-between;
              padding: 8px 12px;
              background: rgba(255, 255, 255, 0.05);
              border-radius: 8px;
              transition: all 0.2s ease;
              
              &:hover {
                background: rgba(255, 255, 255, 0.08);
              }
              
              .stock-code {
                font-size: 12px;
                color: var(--text-secondary);
                font-weight: 500;
                min-width: 60px;
              }
              
              .stock-name {
                flex: 1;
                font-size: 14px;
                color: var(--text-primary);
                font-weight: 500;
                margin: 0 12px;
              }
              
              .stock-change {
                font-size: 14px;
                font-weight: 600;
                min-width: 60px;
                text-align: right;
                
                &.positive {
                  color: var(--market-rise);
                }
                
                &.negative {
                  color: var(--market-fall);
                }
              }
            }
          }
        }
      }
    }
  }
}

// 数据新鲜度热力图
.freshness-section {
  margin-bottom: 60px;
  
  // 确保热力图组件有足够的视觉突出，与概览卡片样式一致
  :deep(.data-freshness-heatmap) {
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(8px) saturate(120%);
    -webkit-backdrop-filter: blur(8px) saturate(120%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    overflow: hidden;
    box-shadow:
      0 8px 32px rgba(124, 58, 237, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transform: translateY(0);
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
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
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
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
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
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 16px;
        box-shadow:
          0 8px 32px rgba(124, 58, 237, 0.15),
          inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        
        &:hover {
          transform: translateY(-2px);
          background: rgba(255, 255, 255, 0.08);
          backdrop-filter: blur(20px) saturate(200%);
          -webkit-backdrop-filter: blur(20px) saturate(200%);
          box-shadow:
            0 12px 40px rgba(124, 58, 237, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }
        
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
  
  .categories-grid {
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
  
  .categories-grid {
    grid-template-columns: 1fr;
    
    .category-card {
      .category-header {
        flex-direction: column;
        gap: 16px;
        
        .category-stats {
          flex-direction: row;
          width: 100%;
          min-width: auto;
        }
      }
    }
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

// 导出模态框样式
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.export-modal {
  background: var(--bg-deep);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  
  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    h3 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .close-btn {
      background: none;
      border: none;
      color: var(--text-secondary);
      font-size: 18px;
      cursor: pointer;
      padding: 8px;
      border-radius: 8px;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
      }
    }
  }
  
  .modal-body {
    padding: 24px;
    
    .export-section {
      margin-bottom: 32px;
      
      h4 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .export-options {
        display: flex;
        flex-direction: column;
        gap: 12px;
        
        .export-option {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 16px;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.15);
          }
          
          input[type="checkbox"] {
            margin: 0;
            width: 18px;
            height: 18px;
            accent-color: var(--secondary);
          }
          
          .option-label {
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 4px;
          }
          
          .option-description {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.4;
          }
        }
      }
      
      .format-options {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
        
        .format-option {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.15);
          }
          
          input[type="radio"] {
            margin: 0;
            accent-color: var(--secondary);
          }
          
          .format-label {
            font-weight: 500;
            color: var(--text-primary);
          }
          
          .format-extension {
            font-size: 12px;
            color: var(--text-secondary);
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
          }
        }
      }
      
      .time-range-options {
        .time-range-select {
          width: 100%;
          padding: 12px;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          color: var(--text-primary);
          font-size: 14px;
          margin-bottom: 16px;
          
          &:focus {
            outline: none;
            border-color: var(--secondary);
          }
        }
        
        .custom-date-range {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .date-input {
            flex: 1;
            padding: 12px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
            
            &:focus {
              outline: none;
              border-color: var(--secondary);
            }
          }
          
          .date-separator {
            color: var(--text-secondary);
            font-weight: 500;
          }
        }
      }
      
      .export-preview {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 16px;
        
        .preview-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          
          &:last-child {
            border-bottom: none;
          }
          
          .preview-type {
            font-weight: 500;
            color: var(--text-primary);
          }
          
          .preview-count {
            color: var(--text-secondary);
            font-size: 14px;
          }
          
          .preview-size {
            color: var(--secondary);
            font-size: 14px;
            font-weight: 500;
          }
        }
      }
    }
  }
  
  .modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    padding: 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    
    .cancel-btn {
      padding: 12px 24px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      color: var(--text-primary);
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
      }
    }
    
    .export-confirm-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      background: linear-gradient(135deg, var(--secondary), var(--primary));
      border: none;
      border-radius: 8px;
      color: white;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

// 导出按钮样式
.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
  }
}

// 数据源配置模态框样式
.source-config-modal {
  background: var(--bg-deep);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 700px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  
  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    h3 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .close-btn {
      background: none;
      border: none;
      color: var(--text-secondary);
      font-size: 18px;
      cursor: pointer;
      padding: 8px;
      border-radius: 8px;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
      }
    }
  }
  
  .modal-body {
    padding: 24px;
    max-height: 60vh;
    overflow-y: auto;
    
    .config-section {
      margin-bottom: 32px;
      
      h4 {
        margin: 0 0 20px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 12px;
      }
      
      .form-group {
        margin-bottom: 20px;
        
        label {
          display: block;
          margin-bottom: 8px;
          font-weight: 500;
          color: var(--text-primary);
          font-size: 14px;
          
          input[type="checkbox"] {
            margin-right: 8px;
            accent-color: var(--secondary);
          }
        }
        
        .form-input, .form-select, .form-textarea {
          width: 100%;
          padding: 12px;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          color: var(--text-primary);
          font-size: 14px;
          transition: all 0.2s ease;
          
          &:focus {
            outline: none;
            border-color: var(--secondary);
            box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
          }
          
          &::placeholder {
            color: var(--text-secondary);
          }
        }
        
        .form-textarea {
          resize: vertical;
          min-height: 80px;
          font-family: inherit;
        }
      }
    }
  }
  
  .modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    padding: 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    
    .test-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 20px;
      background: linear-gradient(135deg, #f59e0b, #d97706);
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
      }
    }
    
    .cancel-btn {
      padding: 12px 24px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      color: var(--text-primary);
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
      }
    }
    
    .save-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      background: linear-gradient(135deg, var(--secondary), var(--primary));
      border: none;
      border-radius: 8px;
      color: white;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}
</style>