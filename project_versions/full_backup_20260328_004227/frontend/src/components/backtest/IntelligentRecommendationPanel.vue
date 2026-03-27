<template>
  <div class="intelligent-recommendation-panel">
    <!-- 面板头部 -->
    <div class="panel-header">
      <h3 class="panel-title">
        <i class="fas fa-magic"></i>
        智能推荐助手
      </h3>
      <div class="panel-actions">
        <button 
          class="action-btn"
          @click="togglePanel"
          :class="{ active: isExpanded }"
        >
          <i :class="isExpanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
        </button>
        <button 
          class="action-btn"
          @click="resetPanel"
          title="重置面板"
        >
          <i class="fas fa-redo"></i>
        </button>
      </div>
    </div>

    <!-- 面板内容 -->
    <div class="panel-content" v-show="isExpanded">
      <!-- 经验水平选择 -->
      <div class="experience-section">
        <h4 class="section-title">
          <i class="fas fa-user-graduate"></i>
          经验水平
        </h4>
        <div class="experience-levels">
          <button
            v-for="level in experienceLevels"
            :key="level.id"
            class="level-btn"
            :class="{ active: selectedExperienceLevel === level.id }"
            @click="selectExperienceLevel(level.id)"
          >
            <i :class="level.icon"></i>
            <span>{{ level.name }}</span>
            <small>{{ level.description }}</small>
          </button>
        </div>
      </div>

      <!-- 自然语言输入 -->
      <div class="nlp-section">
        <h4 class="section-title">
          <i class="fas fa-comments"></i>
          描述您的需求
        </h4>
        <div class="nlp-input-container">
          <textarea
            v-model="userInput"
            class="nlp-textarea"
            placeholder="请用自然语言描述您想要实现的回测策略，例如：'我想测试一个基于移动平均线的趋势跟踪策略，使用沪深300股票数据，回测时间为2020年到2023年'..."
            rows="4"
            @input="handleInputChange"
          ></textarea>
          <div class="input-actions">
            <button
              class="analyze-btn"
              @click="analyzeUserInput"
              :disabled="!userInput.trim() || isAnalyzing"
            >
              <i class="fas fa-search" v-if="!isAnalyzing"></i>
              <i class="fas fa-spinner fa-spin" v-else></i>
              {{ isAnalyzing ? '分析中...' : '智能分析' }}
            </button>
            <button
              class="template-btn"
              @click="showTemplateDialog = true"
              title="使用模板"
            >
              <i class="fas fa-file-alt"></i>
              模板
            </button>
          </div>
        </div>
      </div>

      <!-- 智能推荐结果 -->
      <div class="recommendations-section" v-if="recommendations.length > 0">
        <h4 class="section-title">
          <i class="fas fa-lightbulb"></i>
          智能推荐
        </h4>
        <div class="recommendations-container">
          <div
            v-for="(recommendation, index) in recommendations"
            :key="index"
            class="recommendation-card"
            :class="{ selected: selectedRecommendation === index }"
            @click="selectRecommendation(index)"
          >
            <div class="card-header">
              <h5 class="card-title">{{ recommendation.title }}</h5>
              <div class="card-confidence">
                <span class="confidence-label">置信度</span>
                <div class="confidence-bar">
                  <div 
                    class="confidence-fill"
                    :style="{ width: recommendation.confidence + '%' }"
                  ></div>
                </div>
                <span class="confidence-value">{{ recommendation.confidence }}%</span>
              </div>
            </div>
            <div class="card-content">
              <p class="card-description">{{ recommendation.description }}</p>
              <div class="card-tags">
                <span
                  v-for="tag in recommendation.tags"
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
            <div class="card-actions">
              <button
                class="apply-btn"
                @click.stop="applyRecommendation(index)"
              >
                <i class="fas fa-check"></i>
                应用推荐
              </button>
              <button
                class="details-btn"
                @click.stop="showRecommendationDetails(index)"
              >
                <i class="fas fa-info-circle"></i>
                详情
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 工作流预览 -->
      <div class="workflow-preview-section" v-if="workflowPreview">
        <h4 class="section-title">
          <i class="fas fa-project-diagram"></i>
          工作流预览
        </h4>
        <div class="workflow-preview">
          <div class="preview-canvas">
            <canvas
              ref="previewCanvas"
              class="workflow-canvas"
              width="400"
              height="200"
            ></canvas>
          </div>
          <div class="preview-info">
            <div class="info-item">
              <span class="info-label">节点数量:</span>
              <span class="info-value">{{ workflowPreview.nodeCount }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">连接数量:</span>
              <span class="info-value">{{ workflowPreview.connectionCount }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">预计耗时:</span>
              <span class="info-value">{{ workflowPreview.estimatedTime }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 参数配置 -->
      <div class="parameters-section" v-if="selectedRecommendation !== null">
        <h4 class="section-title">
          <i class="fas fa-sliders-h"></i>
          参数配置
        </h4>
        <div class="parameters-container">
          <div
            v-for="param in recommendedParameters"
            :key="param.name"
            class="parameter-item"
          >
            <div class="parameter-header">
              <label class="parameter-label">{{ param.displayName }}</label>
              <div class="parameter-type">
                <i :class="getParameterTypeIcon(param.type)"></i>
                {{ getParameterTypeName(param.type) }}
              </div>
            </div>
            <div class="parameter-control">
              <!-- 数值输入 -->
              <input
                v-if="param.type === 'number'"
                type="number"
                v-model="param.value"
                :min="param.min"
                :max="param.max"
                :step="param.step"
                class="parameter-input"
                @input="validateParameter(param)"
              />
              
              <!-- 选择框 -->
              <select
                v-else-if="param.type === 'select'"
                v-model="param.value"
                class="parameter-select"
                @change="validateParameter(param)"
              >
                <option
                  v-for="option in param.options"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
              
              <!-- 复选框 -->
              <div v-else-if="param.type === 'boolean'" class="parameter-checkbox">
                <input
                  type="checkbox"
                  v-model="param.value"
                  :id="param.name"
                  @change="validateParameter(param)"
                />
                <label :for="param.name">{{ param.description }}</label>
              </div>
              
              <!-- 文本输入 -->
              <input
                v-else-if="param.type === 'text'"
                type="text"
                v-model="param.value"
                :placeholder="param.placeholder"
                class="parameter-input"
                @input="validateParameter(param)"
              />
              
              <!-- 日期选择 -->
              <input
                v-else-if="param.type === 'date'"
                type="date"
                v-model="param.value"
                :min="param.min"
                :max="param.max"
                class="parameter-input"
                @change="validateParameter(param)"
              />
            </div>
            <div class="parameter-description">
              <p>{{ param.description }}</p>
              <div class="parameter-validation" v-if="param.error">
                <i class="fas fa-exclamation-triangle"></i>
                {{ param.error }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions-section">
        <button
          class="primary-btn"
          @click="generateWorkflow"
          :disabled="!canGenerateWorkflow"
        >
          <i class="fas fa-play"></i>
          生成工作流
        </button>
        <button
          class="secondary-btn"
          @click="saveConfiguration"
          :disabled="!hasValidConfiguration"
        >
          <i class="fas fa-save"></i>
          保存配置
        </button>
        <button
          class="secondary-btn"
          @click="exportConfiguration"
          :disabled="!hasValidConfiguration"
        >
          <i class="fas fa-download"></i>
          导出配置
        </button>
      </div>
    </div>

    <!-- 模板对话框 -->
    <div class="modal-overlay" v-if="showTemplateDialog" @click="showTemplateDialog = false">
      <div class="modal-dialog" @click.stop>
        <div class="dialog-header">
          <h4>选择模板</h4>
          <button class="close-btn" @click="showTemplateDialog = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="dialog-content">
          <div class="template-grid">
            <div
              v-for="template in templates"
              :key="template.id"
              class="template-card"
              @click="useTemplate(template)"
            >
              <div class="template-icon">
                <i :class="template.icon"></i>
              </div>
              <h5 class="template-title">{{ template.title }}</h5>
              <p class="template-description">{{ template.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 推荐详情对话框 -->
    <div class="modal-overlay" v-if="showDetailsDialog" @click="showDetailsDialog = false">
      <div class="modal-dialog details-dialog" @click.stop>
        <div class="dialog-header">
          <h4>推荐详情</h4>
          <button class="close-btn" @click="showDetailsDialog = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="dialog-content" v-if="selectedRecommendation !== null">
          <div class="details-section">
            <h5>推荐策略</h5>
            <p>{{ recommendations[selectedRecommendation].description }}</p>
          </div>
          <div class="details-section">
            <h5>技术指标</h5>
            <ul>
              <li
                v-for="indicator in recommendations[selectedRecommendation].indicators"
                :key="indicator"
              >
                {{ indicator }}
              </li>
            </ul>
          </div>
          <div class="details-section">
            <h5>预期收益</h5>
            <div class="performance-metrics">
              <div class="metric">
                <span class="metric-label">年化收益率:</span>
                <span class="metric-value">{{ recommendations[selectedRecommendation].expectedReturn }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">最大回撤:</span>
                <span class="metric-value">{{ recommendations[selectedRecommendation].maxDrawdown }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">夏普比率:</span>
                <span class="metric-value">{{ recommendations[selectedRecommendation].sharpeRatio }}</span>
              </div>
            </div>
          </div>
          <div class="details-section">
            <h5>风险提示</h5>
            <p>{{ recommendations[selectedRecommendation].riskWarning }}</p>
          </div>
        </div>
        <div class="dialog-actions">
          <button class="primary-btn" @click="applyRecommendation(selectedRecommendation)">
            应用此推荐
          </button>
          <button class="secondary-btn" @click="showDetailsDialog = false">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { intelligentRecommendationService } from '../../services/intelligent-recommendation.service'
import { workflowService } from '../../services/workflow.service'
import type { 
  ExperienceLevel, 
  Recommendation, 
  Parameter, 
  Template,
  WorkflowPreview 
} from '../../types/intelligent-recommendation'

// 响应式数据
const isExpanded = ref(true)
const selectedExperienceLevel = ref<ExperienceLevel>('intermediate')
const userInput = ref('')
const isAnalyzing = ref(false)
const recommendations = ref<Recommendation[]>([])
const selectedRecommendation = ref<number | null>(null)
const recommendedParameters = ref<Parameter[]>([])
const workflowPreview = ref<WorkflowPreview | null>(null)
const showTemplateDialog = ref(false)
const showDetailsDialog = ref(false)
const previewCanvas = ref<HTMLCanvasElement | null>(null)

// 经验水平配置
const experienceLevels = ref([
  {
    id: 'beginner' as ExperienceLevel,
    name: '新手',
    description: '适合刚入门的用户',
    icon: 'fas fa-seedling'
  },
  {
    id: 'intermediate' as ExperienceLevel,
    name: '进阶',
    description: '有一定经验的用户',
    icon: 'fas fa-user'
  },
  {
    id: 'advanced' as ExperienceLevel,
    name: '专家',
    description: '经验丰富的专业用户',
    icon: 'fas fa-user-tie'
  }
])

// 模板配置
const templates = ref<Template[]>([
  {
    id: 'ma-trend',
    title: '移动平均线趋势策略',
    description: '基于移动平均线的趋势跟踪策略',
    icon: 'fas fa-chart-line',
    template: '我想实现一个基于移动平均线的趋势跟踪策略，使用双均线交叉信号'
  },
  {
    id: 'rsi-mean-reversion',
    title: 'RSI均值回归策略',
    description: '基于RSI指标的超买超卖均值回归策略',
    icon: 'fas fa-chart-area',
    template: '我想测试一个RSI均值回归策略，当RSI低于30时买入，高于70时卖出'
  },
  {
    id: 'momentum',
    title: '动量策略',
    description: '基于价格动量的突破策略',
    icon: 'fas fa-rocket',
    template: '我想实现一个动量突破策略，当价格突破20日高点时买入'
  },
  {
    id: 'pairs-trading',
    title: '配对交易策略',
    description: '基于统计套利的配对交易策略',
    icon: 'fas fa-balance-scale',
    template: '我想测试一个配对交易策略，在相关股票之间进行统计套利'
  }
])

// 计算属性
const canGenerateWorkflow = computed(() => {
  return selectedRecommendation.value !== null && 
         recommendedParameters.value.every(param => !param.error)
})

const hasValidConfiguration = computed(() => {
  return selectedRecommendation.value !== null && 
         recommendedParameters.value.length > 0
})

// 方法
const togglePanel = () => {
  isExpanded.value = !isExpanded.value
}

const resetPanel = () => {
  userInput.value = ''
  recommendations.value = []
  selectedRecommendation.value = null
  recommendedParameters.value = []
  workflowPreview.value = null
}

const selectExperienceLevel = (level: ExperienceLevel) => {
  selectedExperienceLevel.value = level
  // 根据经验水平调整推荐算法的参数
  intelligentRecommendationService.updateExperienceLevel(level)
}

const handleInputChange = () => {
  // 实时输入处理，可以添加自动完成等功能
}

const analyzeUserInput = async () => {
  if (!userInput.value.trim() || isAnalyzing.value) return
  
  isAnalyzing.value = true
  
  try {
    const result = await intelligentRecommendationService.analyzeUserInput({
      input: userInput.value,
      experienceLevel: selectedExperienceLevel.value,
      context: getAnalysisContext()
    })
    
    recommendations.value = result.recommendations
    if (result.recommendations.length > 0) {
      selectedRecommendation.value = 0
      await selectRecommendation(0)
    }
  } catch (error) {
    console.error('分析用户输入失败:', error)
    // 可以添加错误提示
  } finally {
    isAnalyzing.value = false
  }
}

const getAnalysisContext = () => {
  // 获取分析上下文，包括当前工作流状态、市场环境等
  return {
    currentWorkflow: workflowService.getCurrentWorkflow(),
    marketEnvironment: getMarketEnvironment(),
    availableDataSources: getAvailableDataSources()
  }
}

const getMarketEnvironment = () => {
  // 获取当前市场环境信息
  return {
    market: 'A股',
    sector: '全市场',
    volatility: '中等',
    trend: '震荡'
  }
}

const getAvailableDataSources = () => {
  // 获取可用的数据源
  return [
    { id: 'tushare', name: 'Tushare', type: 'stock' },
    { id: 'qlib', name: 'QLib', type: 'stock' },
    { id: 'wind', name: 'Wind', type: 'stock' }
  ]
}

const selectRecommendation = async (index: number) => {
  selectedRecommendation.value = index
  const recommendation = recommendations.value[index]
  
  try {
    const parameters = await intelligentRecommendationService.getRecommendedParameters(
      recommendation.id,
      selectedExperienceLevel.value
    )
    
    recommendedParameters.value = parameters
    await generateWorkflowPreview()
  } catch (error) {
    console.error('获取推荐参数失败:', error)
  }
}

const generateWorkflowPreview = async () => {
  if (selectedRecommendation.value === null) return
  
  try {
    const preview = await intelligentRecommendationService.generateWorkflowPreview({
      recommendationId: recommendations.value[selectedRecommendation.value].id,
      parameters: recommendedParameters.value.map(param => ({
        name: param.name,
        value: param.value
      }))
    })
    
    workflowPreview.value = preview
    await nextTick()
    renderWorkflowPreview()
  } catch (error) {
    console.error('生成工作流预览失败:', error)
  }
}

const renderWorkflowPreview = () => {
  if (!previewCanvas.value || !workflowPreview.value) return
  
  const ctx = previewCanvas.value.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, previewCanvas.value.width, previewCanvas.value.height)
  
  // 渲染简化的工作流预览
  const { nodes, connections } = workflowPreview.value
  const nodeMap = new Map()
  
  // 绘制节点
  nodes.forEach((node, index) => {
    const x = 50 + (index % 3) * 120
    const y = 50 + Math.floor(index / 3) * 80
    
    nodeMap.set(node.id, { x, y })
    
    // 绘制节点
    ctx.fillStyle = getNodeColor(node.type)
    ctx.fillRect(x - 30, y - 20, 60, 40)
    
    // 绘制节点标签
    ctx.fillStyle = '#333'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(node.name, x, y + 5)
  })
  
  // 绘制连接
  ctx.strokeStyle = '#666'
  ctx.lineWidth = 2
  connections.forEach(connection => {
    const from = nodeMap.get(connection.from)
    const to = nodeMap.get(connection.to)
    
    if (from && to) {
      ctx.beginPath()
      ctx.moveTo(from.x, from.y)
      ctx.lineTo(to.x, to.y)
      ctx.stroke()
    }
  })
}

const getNodeColor = (nodeType: string) => {
  const colors = {
    'data_source': '#4CAF50',
    'data_processing': '#2196F3',
    'strategy': '#FF9800',
    'backtest': '#9C27B0',
    'analysis': '#673AB7'
  }
  return colors[nodeType] || '#999'
}

const validateParameter = (param: Parameter) => {
  param.error = null
  
  switch (param.type) {
    case 'number':
      const numValue = Number(param.value)
      if (isNaN(numValue)) {
        param.error = '请输入有效的数字'
      } else if (param.min !== undefined && numValue < param.min) {
        param.error = `值不能小于 ${param.min}`
      } else if (param.max !== undefined && numValue > param.max) {
        param.error = `值不能大于 ${param.max}`
      }
      break
      
    case 'text':
      if (param.required && !param.value.trim()) {
        param.error = '此字段为必填项'
      }
      break
      
    case 'select':
      if (param.required && !param.value) {
        param.error = '请选择一个选项'
      }
      break
  }
}

const getParameterTypeIcon = (type: string) => {
  const icons = {
    'number': 'fas fa-hashtag',
    'text': 'fas fa-font',
    'select': 'fas fa-list',
    'boolean': 'fas fa-check-square',
    'date': 'fas fa-calendar'
  }
  return icons[type] || 'fas fa-question'
}

const getParameterTypeName = (type: string) => {
  const names = {
    'number': '数值',
    'text': '文本',
    'select': '选择',
    'boolean': '布尔值',
    'date': '日期'
  }
  return names[type] || '未知'
}

const applyRecommendation = async (index: number) => {
  await selectRecommendation(index)
  // 可以添加应用推荐的逻辑
}

const showRecommendationDetails = (index: number) => {
  selectedRecommendation.value = index
  showDetailsDialog.value = true
}

const useTemplate = (template: Template) => {
  userInput.value = template.template
  showTemplateDialog.value = false
  // 自动分析模板
  analyzeUserInput()
}

const generateWorkflow = async () => {
  if (!canGenerateWorkflow.value) return
  
  try {
    const workflow = await intelligentRecommendationService.generateWorkflow({
      recommendationId: recommendations.value[selectedRecommendation.value!].id,
      parameters: recommendedParameters.value.map(param => ({
        name: param.name,
        value: param.value
      })),
      experienceLevel: selectedExperienceLevel.value
    })
    
    // 将生成的工作流应用到工作流服务
    await workflowService.loadWorkflow(workflow)
    
    // 可以添加成功提示
    console.log('工作流生成成功:', workflow)
  } catch (error) {
    console.error('生成工作流失败:', error)
  }
}

const saveConfiguration = () => {
  if (!hasValidConfiguration.value) return
  
  const configuration = {
    recommendation: recommendations.value[selectedRecommendation.value!],
    parameters: recommendedParameters.value,
    experienceLevel: selectedExperienceLevel.value,
    timestamp: new Date().toISOString()
  }
  
  // 保存到本地存储或发送到服务器
  localStorage.setItem('intelligent-recommendation-config', JSON.stringify(configuration))
  
  // 可以添加成功提示
  console.log('配置已保存:', configuration)
}

const exportConfiguration = () => {
  if (!hasValidConfiguration.value) return
  
  const configuration = {
    recommendation: recommendations.value[selectedRecommendation.value!],
    parameters: recommendedParameters.value,
    experienceLevel: selectedExperienceLevel.value,
    timestamp: new Date().toISOString()
  }
  
  // 导出为JSON文件
  const blob = new Blob([JSON.stringify(configuration, null, 2)], {
    type: 'application/json'
  })
  
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `intelligent-recommendation-${Date.now()}.json`
  a.click()
  
  URL.revokeObjectURL(url)
}

// 监听推荐变化，自动生成预览
watch(selectedRecommendation, (newIndex) => {
  if (newIndex !== null) {
    generateWorkflowPreview()
  }
})

// 组件挂载时的初始化
onMounted(() => {
  // 加载保存的配置
  const savedConfig = localStorage.getItem('intelligent-recommendation-config')
  if (savedConfig) {
    try {
      const configuration = JSON.parse(savedConfig)
      selectedExperienceLevel.value = configuration.experienceLevel || 'intermediate'
      // 可以恢复其他配置
    } catch (error) {
      console.error('加载保存的配置失败:', error)
    }
  }
})
</script>

<style scoped>
.intelligent-recommendation-panel {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 6px 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f0f0f0;
}

.action-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.panel-content {
  padding: 16px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.experience-section {
  margin-bottom: 24px;
}

.experience-levels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.level-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.level-btn:hover {
  border-color: #007bff;
  background: #f8f9ff;
}

.level-btn.active {
  border-color: #007bff;
  background: #007bff;
  color: white;
}

.level-btn i {
  font-size: 24px;
  margin-bottom: 8px;
}

.level-btn span {
  font-weight: 600;
  margin-bottom: 4px;
}

.level-btn small {
  color: #666;
  font-size: 12px;
}

.nlp-section {
  margin-bottom: 24px;
}

.nlp-input-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nlp-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 100px;
}

.nlp-textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

.input-actions {
  display: flex;
  gap: 8px;
}

.analyze-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.analyze-btn:hover:not(:disabled) {
  background: #0056b3;
}

.analyze-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.template-btn {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
}

.template-btn:hover {
  background: #545b62;
}

.recommendations-section {
  margin-bottom: 24px;
}

.recommendations-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.recommendation-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.recommendation-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
}

.recommendation-card.selected {
  border-color: #007bff;
  background: #f8f9ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-confidence {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.confidence-label {
  font-size: 12px;
  color: #666;
}

.confidence-bar {
  width: 80px;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: #28a745;
  transition: width 0.3s;
}

.confidence-value {
  font-size: 12px;
  font-weight: 600;
  color: #28a745;
}

.card-content {
  margin-bottom: 16px;
}

.card-description {
  margin: 0 0 8px 0;
  color: #666;
  line-height: 1.5;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  background: #e9ecef;
  color: #495057;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 12px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.apply-btn {
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.apply-btn:hover {
  background: #218838;
}

.details-btn {
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.details-btn:hover {
  background: #138496;
}

.workflow-preview-section {
  margin-bottom: 24px;
}

.workflow-preview {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.preview-canvas {
  border: 1px solid #e9ecef;
  border-radius: 4px;
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.info-label {
  color: #666;
  font-size: 14px;
}

.info-value {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.parameters-section {
  margin-bottom: 24px;
}

.parameters-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.parameter-item {
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
}

.parameter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.parameter-label {
  font-weight: 600;
  color: #333;
}

.parameter-type {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 12px;
}

.parameter-control {
  margin-bottom: 8px;
}

.parameter-input,
.parameter-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.parameter-input:focus,
.parameter-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

.parameter-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}

.parameter-checkbox input[type="checkbox"] {
  margin: 0;
}

.parameter-description {
  color: #666;
  font-size: 12px;
  line-height: 1.4;
}

.parameter-validation {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
}

.actions-section {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.primary-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.primary-btn:hover:not(:disabled) {
  background: #0056b3;
}

.primary-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.secondary-btn {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 500;
}

.secondary-btn:hover:not(:disabled) {
  background: #545b62;
}

.secondary-btn:disabled {
  background: #adb5bd;
  cursor: not-allowed;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-dialog {
  background: white;
  border-radius: 8px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  margin: 20px;
}

.details-dialog {
  max-width: 800px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e9ecef;
}

.dialog-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 4px;
}

.close-btn:hover {
  color: #333;
}

.dialog-content {
  padding: 16px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.template-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.template-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
}

.template-icon {
  font-size: 32px;
  color: #007bff;
  margin-bottom: 8px;
}

.template-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.template-description {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.details-section {
  margin-bottom: 20px;
}

.details-section h5 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.details-section p,
.details-section ul {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.details-section ul {
  padding-left: 20px;
}

.performance-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border: 1px solid #e9ecef;
  border-radius: 4px;
}

.metric-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.dialog-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px;
  border-top: 1px solid #e9ecef;
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