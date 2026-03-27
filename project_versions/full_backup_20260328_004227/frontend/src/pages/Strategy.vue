<template>
  <div class="strategy">
    <div class="strategy-header">
      <h1 class="strategy-title">策略中心</h1>
      <p class="strategy-subtitle">创建、管理和优化量化交易策略</p>
    </div>
    
    <div class="strategy-container">
      <!-- 策略列表 -->
      <div class="strategy-list-section">
        <div class="section-header">
          <h3>策略列表</h3>
          <div class="section-actions">
            <QuantButton
              type="primary"
              icon="PlusOutlined"
              size="small"
              @click="handleCreateStrategy"
            >
              新建策略
            </QuantButton>
            <QuantButton
              type="ghost"
              icon="ImportOutlined"
              size="small"
              @click="handleImportStrategy"
            >
              导入策略
            </QuantButton>
          </div>
        </div>
        
        <div class="list-controls">
          <QuantInput
            v-model:value="searchQuery"
            placeholder="搜索策略..."
            prefix-icon="SearchOutlined"
            clearable
            @input="handleSearch"
          />
          <QuantSelect
            v-model:value="filterStatus"
            :options="statusOptions"
            placeholder="筛选状态"
            clearable
            @change="handleStatusFilter"
          />
          <QuantSelect
            v-model:value="sortBy"
            :options="sortOptions"
            placeholder="排序方式"
            @change="handleSort"
          />
        </div>
        
        <QuantTable
          :data="filteredStrategies"
          :columns="strategyColumns"
          :loading="strategyLoading"
          :paginated="true"
          :page-size="pageSize"
          :total="totalStrategies"
          hoverable
          @row-click="handleStrategyClick"
          @row-dbl-click="handleStrategyEdit"
          @sort-change="handleTableSort"
        >
          <template #cell-status="{ row }">
            <QuantTag
              :type="getStatusTagType(row.status)"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </QuantTag>
          </template>
          
          <template #cell-performance="{ row }">
            <span :class="getPerformanceClass(row.performance)">
              {{ formatPercent(row.performance) }}
            </span>
          </template>
          
          <template #cell-risk="{ row }">
            <QuantTag
              :type="getRiskTagType(row.risk)"
              size="small"
            >
              {{ getRiskText(row.risk) }}
            </QuantTag>
          </template>
          
          <template #cell-actions="{ row }">
            <div class="action-buttons">
              <QuantButton
                type="ghost"
                size="small"
                icon="EditOutlined"
                @click="handleStrategyEdit(row)"
              >
                编辑
              </QuantButton>
              <QuantButton
                type="ghost"
                size="small"
                icon="PlayCircleOutlined"
                @click="handleStrategyTest(row)"
              >
                测试
              </QuantButton>
              <QuantButton
                type="ghost"
                size="small"
                icon="BarChartOutlined"
                @click="handleStrategyBacktest(row)"
              >
                回测
              </QuantButton>
              <QuantButton
                type="ghost"
                size="small"
                icon="DeleteOutlined"
                @click="handleStrategyDelete(row)"
              >
                删除
              </QuantButton>
            </div>
          </template>
        </QuantTable>
      </div>
      
      <!-- 策略编辑器 -->
      <div class="strategy-editor-section">
        <div class="section-header">
          <h3>策略编辑器</h3>
          <div class="section-actions">
            <QuantButton
              type="primary"
              size="small"
              :loading="saveLoading"
              @click="handleSaveStrategy"
            >
              保存策略
            </QuantButton>
            <QuantButton
              type="secondary"
              size="small"
              @click="handleValidateStrategy"
            >
              验证代码
            </QuantButton>
          </div>
        </div>
        
        <div class="editor-container">
          <!-- 代码编辑器 -->
          <div class="code-editor">
            <div class="editor-tabs">
              <div
                v-for="tab in editorTabs"
                :key="tab.key"
                :class="getTabClass(tab)"
                @click="handleTabChange(tab)"
              >
                {{ tab.name }}
              </div>
            </div>
            
            <div class="editor-content">
              <div v-if="activeTab === 'code'" class="code-section">
                <QuantInput
                  v-model:value="strategyCode"
                  type="textarea"
                  placeholder="输入策略代码..."
                  :rows="20"
                  @input="handleCodeChange"
                />
              </div>
              
              <div v-else-if="activeTab === 'config'" class="config-section">
                <QuantForm
                  :model-value="strategyConfig"
                  :rules="configRules"
                  label-width="120px"
                  size="medium"
                >
                  <QuantFormItem label="策略名称" prop="name">
                    <QuantInput v-model:value="strategyConfig.name" />
                  </QuantFormItem>
                  <QuantFormItem label="策略描述" prop="description">
                    <QuantInput v-model:value="strategyConfig.description" type="textarea" :rows="3" />
                  </QuantFormItem>
                  <QuantFormItem label="初始资金" prop="initialCapital">
                    <QuantInput v-model:value="strategyConfig.initialCapital" type="number" />
                  </QuantFormItem>
                  <QuantFormItem label="最大持仓" prop="maxPosition">
                    <QuantInput v-model:value="strategyConfig.maxPosition" type="number" />
                  </QuantFormItem>
                  <QuantFormItem label="止损比例" prop="stopLoss">
                    <QuantInput v-model:value="strategyConfig.stopLoss" type="number" />
                  </QuantFormItem>
                  <QuantFormItem label="止盈比例" prop="takeProfit">
                    <QuantInput v-model:value="strategyConfig.takeProfit" type="number" />
                  </QuantFormItem>
                  <QuantFormItem label="交易频率" prop="frequency">
                    <QuantSelect
                      v-model:value="strategyConfig.frequency"
                      :options="frequencyOptions"
                    />
                  </QuantFormItem>
                </QuantForm>
              </div>
              
              <div v-else-if="activeTab === 'backtest'" class="backtest-section">
                <div class="backtest-summary" v-if="backtestResult">
                  <h4>回测结果</h4>
                  <div class="summary-grid">
                    <div class="summary-item">
                      <label>总收益率:</label>
                      <span :class="getPerformanceClass(backtestResult.totalReturn)">
                        {{ formatPercent(backtestResult.totalReturn) }}
                      </span>
                    </div>
                    <div class="summary-item">
                      <label>年化收益率:</label>
                      <span :class="getPerformanceClass(backtestResult.annualReturn)">
                        {{ formatPercent(backtestResult.annualReturn) }}
                      </span>
                    </div>
                    <div class="summary-item">
                      <label>最大回撤:</label>
                      <span :class="getPerformanceClass(-backtestResult.maxDrawdown)">
                        {{ formatPercent(backtestResult.maxDrawdown) }}
                      </span>
                    </div>
                    <div class="summary-item">
                      <label>夏普比率:</label>
                      <span>{{ backtestResult.sharpeRatio?.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>
                
                <QuantButton
                  v-if="!backtestResult"
                  type="primary"
                  @click="handleRunBacktest"
                >
                  运行回测
                </QuantButton>
              </div>
            </div>
          </div>
          
          <!-- 策略模板 -->
          <div class="strategy-templates">
            <h4>策略模板</h4>
            <div class="template-grid">
              <div
                v-for="template in strategyTemplates"
                :key="template.id"
                class="template-item"
                @click="handleUseTemplate(template)"
              >
                <div class="template-icon">
                  <n-icon :size="24">
                    <component :is="template.icon" />
                  </n-icon>
                </div>
                <div class="template-info">
                  <h5>{{ template.name }}</h5>
                  <p>{{ template.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 策略导入模态框 -->
    <QuantModal
      v-model:visible="importModalVisible"
      title="导入策略"
      width="600px"
      @confirm="handleImportConfirm"
      @cancel="handleImportCancel"
    >
      <div class="import-form">
        <QuantForm
          :model-value="importConfig"
          :rules="importRules"
          label-width="100px"
          size="medium"
        >
          <QuantFormItem label="导入方式" prop="type">
            <QuantSelect
              v-model:value="importConfig.type"
              :options="importTypeOptions"
            />
          </QuantFormItem>
          <QuantFormItem v-if="importConfig.type === 'file'" label="选择文件" prop="file">
            <input
              ref="fileInput"
              type="file"
              accept=".py,.js,.json"
              @change="handleFileSelect"
            />
          </QuantFormItem>
          <QuantFormItem v-if="importConfig.type === 'url'" label="策略URL" prop="url">
            <QuantInput v-model:value="importConfig.url" placeholder="输入策略文件URL..." />
          </QuantFormItem>
          <QuantFormItem v-if="importConfig.type === 'text'" label="策略代码" prop="code">
            <QuantInput v-model:value="importConfig.code" type="textarea" :rows="10" />
          </QuantFormItem>
        </QuantForm>
      </div>
    </QuantModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon, NSelect, NOption, NTag } from 'naive-ui'
import { useStrategyStore, useMessage } from '@/stores'
import QuantButton from '@/components/ui/Button.vue'
import QuantInput from '@/components/ui/Input.vue'
import QuantSelect from '@/components/ui/Select.vue'
import QuantTable from '@/components/ui/Table.vue'
import QuantModal from '@/components/ui/Modal.vue'
import QuantForm from '@/components/ui/Form.vue'
import QuantFormItem from '@/components/ui/Form.vue'
import QuantTag from '@/components/ui/Tag.vue'
import { formatPercent } from '@/utils/format'
import type { Strategy, TableColumn, StrategyTemplate } from '@/types/components'

const router = useRouter()
const strategyStore = useStrategyStore()
const message = useMessage()

// 响应式数据
const strategyLoading = ref(false)
const saveLoading = ref(false)
const searchQuery = ref('')
const filterStatus = ref('')
const sortBy = ref('updatedAt')
const pageSize = ref(10)
const currentPage = ref(1)

const activeTab = ref('code')
const strategyCode = ref('')
const backtestResult = ref(null)

const importModalVisible = ref(false)

// 选项数据
const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '运行中', value: 'active' },
  { label: '已停止', value: 'inactive' },
  { label: '测试中', value: 'testing' },
  { label: '错误', value: 'error' }
]

const sortOptions = [
  { label: '更新时间', value: 'updatedAt' },
  { label: '名称', value: 'name' },
  { label: '收益率', value: 'performance' },
  { label: '风险等级', value: 'risk' }
]

const frequencyOptions = [
  { label: '每日', value: 'daily' },
  { label: '每周', value: 'weekly' },
  { label: '每月', value: 'monthly' }
]

const importTypeOptions = [
  { label: '文件导入', value: 'file' },
  { label: 'URL导入', value: 'url' },
  { label: '文本导入', value: 'text' }
]

// 策略配置
const strategyConfig = reactive({
  name: '',
  description: '',
  initialCapital: 100000,
  maxPosition: 10,
  stopLoss: 0.05,
  takeProfit: 0.1,
  frequency: 'daily'
})

// 导入配置
const importConfig = reactive({
  type: 'file',
  url: '',
  code: ''
})

// 配置规则
const configRules = {
  name: [
    { required: true, message: '请输入策略名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入策略描述', trigger: 'blur' }
  ]
}

const importRules = {
  url: [
    { required: true, message: '请输入策略URL', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入策略代码', trigger: 'blur' }
  ]
}

// 编辑器标签
const editorTabs = ref([
  { key: 'code', name: '策略代码' },
  { key: 'config', name: '策略配置' },
  { key: 'backtest', name: '回测结果' }
])

// 策略模板
const strategyTemplates = ref<StrategyTemplate[]>([
  {
    id: 'ma_strategy',
    name: '均线策略',
    description: '基于移动平均线的趋势跟踪策略',
    icon: 'LineChartOutlined'
  },
  {
    id: 'rsi_strategy',
    name: 'RSI策略',
    description: '基于相对强弱指数的超买超卖策略',
    icon: 'AreaChartOutlined'
  },
  {
    id: 'boll_strategy',
    name: '布林带策略',
    description: '基于布林带的突破策略',
    icon: 'BarChartOutlined'
  },
  {
    id: 'macd_strategy',
    name: 'MACD策略',
    description: '基于MACD指标的趋势策略',
    icon: 'StockOutlined'
  }
])

// 策略表格列
const strategyColumns = computed<TableColumn[]>(() => [
  {
    key: 'name',
    title: '策略名称',
    dataIndex: 'name',
    width: 200,
    sortable: true
  },
  {
    key: 'status',
    title: '状态',
    dataIndex: 'status',
    width: 100,
    sortable: true
  },
  {
    key: 'performance',
    title: '收益率',
    dataIndex: 'performance',
    width: 120,
    sortable: true,
    align: 'right'
  },
  {
    key: 'risk',
    title: '风险等级',
    dataIndex: 'risk',
    width: 100,
    sortable: true
  },
  {
    key: 'updatedAt',
    title: '更新时间',
    dataIndex: 'updatedAt',
    width: 150,
    sortable: true
  },
  {
    key: 'actions',
    title: '操作',
    width: 200,
    fixed: 'right'
  }
])

// 计算属性
const strategies = computed(() => strategyStore.strategies)
const totalStrategies = computed(() => strategies.value.length)

const filteredStrategies = computed(() => {
  let filtered = strategies.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(strategy => 
      strategy.name.toLowerCase().includes(query) ||
      strategy.description.toLowerCase().includes(query)
    )
  }

  // 状态过滤
  if (filterStatus.value) {
    filtered = filtered.filter(strategy => strategy.status === filterStatus.value)
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'performance':
        return b.performance - a.performance
      case 'risk':
        return a.risk.localeCompare(b.risk)
      case 'updatedAt':
      default:
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    }
  })

  return filtered
})

// 事件处理函数
const handleCreateStrategy = () => {
  strategyConfig.name = ''
  strategyConfig.description = ''
  strategyCode.value = ''
  backtestResult.value = null
  activeTab.value = 'code'
}

const handleImportStrategy = () => {
  importModalVisible.value = true
}

const handleSearch = (query: string) => {
  searchQuery.value = query
  currentPage.value = 1
}

const handleStatusFilter = (status: string) => {
  filterStatus.value = status
  currentPage.value = 1
}

const handleSort = (sort: string) => {
  sortBy.value = sort
  currentPage.value = 1
}

const handleTableSort = ({ column, order }: any) => {
  sortBy.value = column
  // 实际排序逻辑在filteredStrategies中处理
}

const handleStrategyClick = (strategy: Strategy) => {
  console.log('策略点击:', strategy)
}

const handleStrategyEdit = (strategy: Strategy) => {
  Object.assign(strategyConfig, {
    name: strategy.name,
    description: strategy.description,
    ...strategy.config
  })
  strategyCode.value = strategy.code || ''
  backtestResult.value = strategy.backtestResult || null
  activeTab.value = 'code'
}

const handleStrategyTest = (strategy: Strategy) => {
  console.log('测试策略:', strategy)
  message.info('开始测试策略...')
}

const handleStrategyBacktest = (strategy: Strategy) => {
  router.push(`/backtest?strategy=${strategy.id}`)
}

const handleStrategyDelete = (strategy: Strategy) => {
  console.log('删除策略:', strategy)
  message.warning('确定要删除这个策略吗？')
}

const handleSaveStrategy = async () => {
  saveLoading.value = true
  try {
    await strategyStore.saveStrategy({
      ...strategyConfig,
      code: strategyCode.value
    })
    message.success('策略保存成功')
  } catch (error) {
    console.error('保存策略失败:', error)
    message.error('策略保存失败')
  } finally {
    saveLoading.value = false
  }
}

const handleValidateStrategy = () => {
  console.log('验证策略代码')
  // 实现策略代码验证逻辑
}

const handleCodeChange = (code: string) => {
  strategyCode.value = code
}

const handleTabChange = (tab: any) => {
  activeTab.value = tab.key
}

const handleRunBacktest = async () => {
  try {
    const result = await strategyStore.runBacktest({
      ...strategyConfig,
      code: strategyCode.value
    })
    backtestResult.value = result
    activeTab.value = 'backtest'
    message.success('回测完成')
  } catch (error) {
    console.error('回测失败:', error)
    message.error('回测失败')
  }
}

const handleUseTemplate = (template: StrategyTemplate) => {
  console.log('使用模板:', template)
  // 实现模板使用逻辑
}

const handleImportConfirm = async () => {
  try {
    await strategyStore.importStrategy(importConfig)
    message.success('策略导入成功')
    importModalVisible.value = false
  } catch (error) {
    console.error('导入策略失败:', error)
    message.error('策略导入失败')
  }
}

const handleImportCancel = () => {
  importModalVisible.value = false
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    console.log('选择文件:', file)
    // 实现文件读取逻辑
  }
}

// 工具函数
const getTabClass = (tab: any) => {
  return {
    'editor-tab': true,
    'editor-tab--active': activeTab.value === tab.key
  }
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '运行中',
    inactive: '已停止',
    testing: '测试中',
    error: '错误'
  }
  return statusMap[status] || '未知'
}

const getStatusTagType = (status: string) => {
  const typeMap = {
    active: 'success',
    inactive: 'default',
    testing: 'warning',
    error: 'danger'
  }
  return typeMap[status] || 'default'
}

const getRiskText = (risk: string) => {
  const riskMap = {
    low: '低',
    medium: '中',
    high: '高'
  }
  return riskMap[risk] || '未知'
}

const getRiskTagType = (risk: string) => {
  const typeMap = {
    low: 'success',
    medium: 'warning',
    high: 'danger'
  }
  return typeMap[risk] || 'default'
}

const getPerformanceClass = (performance: number) => {
  if (performance > 0) return 'performance-positive'
  if (performance < 0) return 'performance-negative'
  return 'performance-neutral'
}

// 生命周期
onMounted(async () => {
  strategyLoading.value = true
  try {
    await strategyStore.fetchStrategies()
  } catch (error) {
    console.error('获取策略列表失败:', error)
    message.error('获取策略列表失败')
  } finally {
    strategyLoading.value = false
  }
})
</script>

<style lang="scss" scoped>
.strategy {
  padding: var(--spacing-4);
  max-width: 1400px;
  margin: 0 auto;
  
  &-header {
    text-align: center;
    margin-bottom: var(--spacing-6);
  }
  
  &-title {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 var(--spacing-2) 0;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  &-subtitle {
    font-size: var(--font-size-base);
    color: var(--text-secondary);
    margin: 0;
  }
  
  &-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-4);
  }
  
  &-list-section, &-editor-section {
    background: var(--bg-color-base);
    border: 1px solid var(--border-color)-base;
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-4);
  }
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-4);
    
    h3 {
      font-size: var(--font-size-lg);
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
    
    .section-actions {
      display: flex;
      gap: var(--spacing-2);
    }
  }
  
  .list-controls {
    display: flex;
    gap: var(--spacing-2);
    margin-bottom: var(--spacing-4);
    
    .quant-input {
      flex: 1;
    }
    
    .quant-select {
      width: 150px;
    }
  }
  
  .editor-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--spacing-4);
    margin-top: var(--spacing-4);
  }
  
  .code-editor {
    .editor-tabs {
      display: flex;
      border-bottom: 1px solid var(--border-color)-base;
      margin-bottom: var(--spacing-4);
    }
    
    .editor-tab {
      padding: var(--spacing-2) var(--spacing-3);
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all var(--transition-duration-base) var(--transition-timing-function-base);
      
      &:hover {
        background-color: var(--bg-color-secondary);
      }
      
      &--active {
        border-bottom-color: var(--primary-color);
        color: var(--primary-color);
      }
    }
    
    .editor-content {
      min-height: 400px;
    }
    
    .code-section {
      .quant-input {
        height: 100%;
        font-family: 'JetBrains Mono', 'Monaco', 'Consolas', monospace;
      }
    }
    
    .config-section {
      .quant-form {
        max-width: 400px;
      }
    }
    
    .backtest-section {
      .backtest-summary {
        margin-bottom: var(--spacing-4);
        
        h4 {
          font-size: var(--font-size-base);
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 var(--spacing-3) 0;
        }
        
        .summary-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--spacing-3);
          
          .summary-item {
            display: flex;
            justify-content: space-between;
            padding: var(--spacing-2);
            background-color: var(--bg-color-secondary);
            border-radius: var(--border-radius-base);
            
            label {
              font-weight: 500;
              color: var(--text-secondary);
            }
            
            span {
              font-weight: 600;
            }
          }
        }
      }
    }
  }
  
  .strategy-templates {
    margin-top: var(--spacing-4);
    
    h4 {
      font-size: var(--font-size-base);
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 var(--spacing-3) 0;
    }
    
    .template-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--spacing-3);
    }
    
    .template-item {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);
      padding: var(--spacing-3);
      border: 1px solid var(--border-color)-base;
      border-radius: var(--border-radius-base);
      cursor: pointer;
      transition: all var(--transition-duration-base) var(--transition-timing-function-base);
      
      &:hover {
        background-color: var(--bg-color-secondary);
        border-color: var(--primary-color);
      }
      
      .template-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        background-color: var(--bg-color-tertiary);
        border-radius: var(--border-radius-base);
        color: var(--primary-color);
      }
      
      .template-info {
        h5 {
          font-size: var(--font-size-base);
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 var(--spacing-1) 0;
        }
        
        p {
          font-size: var(--font-size-sm);
          color: var(--text-secondary);
          margin: 0;
        }
      }
    }
  }
  
  .action-buttons {
    display: flex;
    gap: var(--spacing-1);
  }
}

.performance-positive {
  color: var(--success-color);
}

.performance-negative {
  color: var(--danger-color);
}

.performance-neutral {
  color: var(--text-primary);
}

.import-form {
  padding: var(--spacing-2) 0;
}

// 响应式设计
@media (max-width: 1024px) {
  .strategy {
    &-container {
      grid-template-columns: 1fr;
    }
    
    .editor-container {
      grid-template-columns: 1fr;
    }
    
    .template-grid {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .strategy {
    padding: var(--spacing-2);
    
    .list-controls {
      flex-direction: column;
      
      .quant-input,
      .quant-select {
        width: 100%;
        margin-bottom: var(--spacing-2);
      }
    }
    
    .section-header {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-2);
    }
  }
}
</style>