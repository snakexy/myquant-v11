<template>
  <div class="hybrid-parameter-config">
    <!-- 组件头部 -->
    <div class="config-header">
      <h3 class="config-title">
        <i class="fas fa-sliders-h"></i>
        混合参数配置
      </h3>
      <div class="config-actions">
        <button
          class="action-btn"
          @click="toggleView"
          :class="{ active: showAdvanced }"
          title="切换视图"
        >
          <i :class="showAdvanced ? 'fas fa-compress' : 'fas fa-expand'"></i>
        </button>
        <button
          class="action-btn"
          @click="resetParameters"
          title="重置参数"
        >
          <i class="fas fa-undo"></i>
        </button>
        <button
          class="action-btn"
          @click="toggleAutoMode"
          :class="{ active: autoMode }"
          title="切换自动模式"
        >
          <i :class="autoMode ? 'fas fa-robot' : 'fas fa-user'"></i>
        </button>
      </div>
    </div>

    <!-- 参数配置模式选择 -->
    <div class="mode-selector">
      <div class="mode-tabs">
        <button
          v-for="mode in configModes"
          :key="mode.id"
          class="mode-tab"
          :class="{ active: selectedMode === mode.id }"
          @click="selectMode(mode.id)"
        >
          <i :class="mode.icon"></i>
          <span>{{ mode.name }}</span>
        </button>
      </div>
    </div>

    <!-- AI推荐参数区域 -->
    <div class="ai-recommendations" v-if="selectedMode === 'ai'">
      <div class="section-header">
        <h4 class="section-title">
          <i class="fas fa-magic"></i>
          AI智能推荐
        </h4>
        <div class="section-actions">
          <button
            class="refresh-btn"
            @click="refreshRecommendations"
            :disabled="isRefreshing"
          >
            <i class="fas fa-sync" :class="{ 'fa-spin': isRefreshing }"></i>
            {{ isRefreshing ? '刷新中...' : '刷新推荐' }}
          </button>
          <button
            class="apply-all-btn"
            @click="applyAllRecommendations"
            :disabled="!hasValidRecommendations"
          >
            <i class="fas fa-check-double"></i>
            应用全部
          </button>
        </div>
      </div>

      <div class="recommendations-grid">
        <div
          v-for="(recommendation, index) in aiRecommendations"
          :key="index"
          class="recommendation-item"
          :class="{ 
            selected: selectedRecommendations.includes(index),
            applied: appliedRecommendations.includes(index)
          }"
        >
          <div class="recommendation-header">
            <h5 class="recommendation-title">{{ recommendation.title }}</h5>
            <div class="recommendation-confidence">
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
          
          <div class="recommendation-content">
            <p class="recommendation-description">{{ recommendation.description }}</p>
            
            <div class="recommendation-params">
              <div
                v-for="param in recommendation.parameters"
                :key="param.name"
                class="param-display"
              >
                <span class="param-name">{{ param.displayName }}:</span>
                <span class="param-value">{{ formatParameterValue(param) }}</span>
                <button
                  class="param-edit-btn"
                  @click="editRecommendationParam(index, param)"
                  title="编辑参数"
                >
                  <i class="fas fa-edit"></i>
                </button>
              </div>
            </div>
          </div>
          
          <div class="recommendation-actions">
            <button
              class="select-btn"
              @click="toggleRecommendationSelection(index)"
              :class="{ selected: selectedRecommendations.includes(index) }"
            >
              <i class="fas fa-check"></i>
              {{ selectedRecommendations.includes(index) ? '已选择' : '选择' }}
            </button>
            <button
              class="apply-btn"
              @click="applyRecommendation(index)"
              :disabled="appliedRecommendations.includes(index)"
            >
              <i class="fas fa-play"></i>
              {{ appliedRecommendations.includes(index) ? '已应用' : '应用' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 手动参数配置区域 -->
    <div class="manual-parameters" v-if="selectedMode === 'manual'">
      <div class="section-header">
        <h4 class="section-title">
          <i class="fas fa-user-cog"></i>
          手动参数配置
        </h4>
        <div class="section-actions">
          <button
            class="load-template-btn"
            @click="showTemplateDialog = true"
          >
            <i class="fas fa-file-alt"></i>
            加载模板
          </button>
          <button
            class="save-template-btn"
            @click="saveAsTemplate"
          >
            <i class="fas fa-save"></i>
            保存模板
          </button>
        </div>
      </div>

      <div class="parameter-categories">
        <div
          v-for="category in parameterCategories"
          :key="category.id"
          class="category-section"
        >
          <div class="category-header" @click="toggleCategory(category.id)">
            <h5 class="category-title">
              <i :class="category.icon"></i>
              {{ category.name }}
            </h5>
            <i 
              class="category-toggle"
              :class="expandedCategories.includes(category.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"
            ></i>
          </div>
          
          <div 
            class="category-content"
            v-show="expandedCategories.includes(category.id)"
          >
            <div
              v-for="param in category.parameters"
              :key="param.name"
              class="parameter-item"
              :class="{ 
                'has-error': param.error,
                'modified': isParameterModified(param)
              }"
            >
              <div class="parameter-header">
                <label class="parameter-label">
                  {{ param.displayName }}
                  <span class="required-indicator" v-if="param.required">*</span>
                </label>
                <div class="parameter-info">
                  <button
                    class="info-btn"
                    @click="showParameterInfo(param)"
                    title="参数说明"
                  >
                    <i class="fas fa-info-circle"></i>
                  </button>
                  <div class="parameter-type">
                    <i :class="getParameterTypeIcon(param.type)"></i>
                    {{ getParameterTypeName(param.type) }}
                  </div>
                </div>
              </div>
              
              <div class="parameter-control">
                <!-- 数值输入 -->
                <div v-if="param.type === 'number'" class="number-input-group">
                  <input
                    type="number"
                    v-model="param.value"
                    :min="param.min"
                    :max="param.max"
                    :step="param.step"
                    class="parameter-input"
                    @input="validateParameter(param)"
                  />
                  <div class="input-controls">
                    <button
                      class="control-btn"
                      @click="adjustParameter(param, -1)"
                      title="减少"
                    >
                      <i class="fas fa-minus"></i>
                    </button>
                    <button
                      class="control-btn"
                      @click="adjustParameter(param, 1)"
                      title="增加"
                    >
                      <i class="fas fa-plus"></i>
                    </button>
                  </div>
                </div>
                
                <!-- 滑块输入 -->
                <div v-else-if="param.type === 'range'" class="range-input-group">
                  <input
                    type="range"
                    v-model="param.value"
                    :min="param.min"
                    :max="param.max"
                    :step="param.step"
                    class="parameter-range"
                    @input="validateParameter(param)"
                  />
                  <div class="range-value">
                    {{ param.value }}
                  </div>
                </div>
                
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
                <div v-else-if="param.type === 'boolean'" class="checkbox-group">
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      v-model="param.value"
                      :id="param.name"
                      @change="validateParameter(param)"
                    />
                    <span class="checkbox-text">{{ param.description }}</span>
                  </label>
                </div>
                
                <!-- 文本输入 -->
                <div v-else-if="param.type === 'text'" class="text-input-group">
                  <input
                    type="text"
                    v-model="param.value"
                    :placeholder="param.placeholder"
                    class="parameter-input"
                    @input="validateParameter(param)"
                  />
                  <div class="input-suggestions" v-if="param.suggestions">
                    <button
                      v-for="suggestion in param.suggestions"
                      :key="suggestion"
                      class="suggestion-btn"
                      @click="applySuggestion(param, suggestion)"
                    >
                      {{ suggestion }}
                    </button>
                  </div>
                </div>
                
                <!-- 日期选择 -->
                <div v-else-if="param.type === 'date'" class="date-input-group">
                  <input
                    type="date"
                    v-model="param.value"
                    :min="param.min"
                    :max="param.max"
                    class="parameter-input"
                    @change="validateParameter(param)"
                  />
                </div>
                
                <!-- 颜色选择 -->
                <div v-else-if="param.type === 'color'" class="color-input-group">
                  <input
                    type="color"
                    v-model="param.value"
                    class="parameter-color"
                    @change="validateParameter(param)"
                  />
                  <div 
                    class="color-preview"
                    :style="{ backgroundColor: param.value }"
                  ></div>
                </div>
              </div>
              
              <div class="parameter-description">
                <p>{{ param.description }}</p>
                <div class="parameter-validation" v-if="param.error">
                  <i class="fas fa-exclamation-triangle"></i>
                  {{ param.error }}
                </div>
                <div class="parameter-hint" v-if="param.hint">
                  <i class="fas fa-lightbulb"></i>
                  {{ param.hint }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 混合模式区域 -->
    <div class="hybrid-mode" v-if="selectedMode === 'hybrid'">
      <div class="section-header">
        <h4 class="section-title">
          <i class="fas fa-layer-group"></i>
          混合模式
        </h4>
        <div class="section-actions">
          <button
            class="sync-btn"
            @click="syncWithAI"
            :disabled="isSyncing"
          >
            <i class="fas fa-sync" :class="{ 'fa-spin': isSyncing }"></i>
            {{ isSyncing ? '同步中...' : 'AI同步' }}
          </button>
        </div>
      </div>

      <div class="hybrid-content">
        <div class="hybrid-columns">
          <!-- AI推荐列 -->
          <div class="hybrid-column ai-column">
            <h5 class="column-title">
              <i class="fas fa-robot"></i>
              AI推荐
            </h5>
            <div class="column-params">
              <div
                v-for="param in aiParameters"
                :key="param.name"
                class="hybrid-param"
              >
                <div class="param-info">
                  <span class="param-name">{{ param.displayName }}</span>
                  <span class="param-value">{{ formatParameterValue(param) }}</span>
                </div>
                <button
                  class="adopt-btn"
                  @click="adoptAIParameter(param)"
                  title="采用AI推荐"
                >
                  <i class="fas fa-arrow-right"></i>
                </button>
              </div>
            </div>
          </div>
          
          <!-- 用户自定义列 -->
          <div class="hybrid-column user-column">
            <h5 class="column-title">
              <i class="fas fa-user"></i>
              用户自定义
            </h5>
            <div class="column-params">
              <div
                v-for="param in userParameters"
                :key="param.name"
                class="hybrid-param"
              >
                <div class="param-control">
                  <!-- 根据参数类型渲染相应的控件 -->
                  <input
                    v-if="param.type === 'number'"
                    type="number"
                    v-model="param.value"
                    :min="param.min"
                    :max="param.max"
                    :step="param.step"
                    class="hybrid-input"
                    @input="validateParameter(param)"
                  />
                  <select
                    v-else-if="param.type === 'select'"
                    v-model="param.value"
                    class="hybrid-select"
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
                  <input
                    v-else-if="param.type === 'text'"
                    type="text"
                    v-model="param.value"
                    :placeholder="param.placeholder"
                    class="hybrid-input"
                    @input="validateParameter(param)"
                  />
                </div>
                <div class="param-status">
                  <div
                    class="status-indicator"
                    :class="getParameterStatus(param)"
                  ></div>
                  <span class="status-text">{{ getParameterStatusText(param) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 参数验证和预览区域 -->
    <div class="validation-preview" v-if="showValidation">
      <div class="section-header">
        <h4 class="section-title">
          <i class="fas fa-check-circle"></i>
          参数验证与预览
        </h4>
      </div>
      
      <div class="validation-results">
        <div class="validation-summary">
          <div class="summary-item">
            <span class="summary-label">有效参数:</span>
            <span class="summary-value valid">{{ validParameterCount }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">错误参数:</span>
            <span class="summary-value invalid">{{ invalidParameterCount }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">完成度:</span>
            <div class="progress-bar">
              <div 
                class="progress-fill"
                :style="{ width: completionPercentage + '%' }"
              ></div>
            </div>
            <span class="progress-value">{{ completionPercentage }}%</span>
          </div>
        </div>
        
        <div class="parameter-preview">
          <h5 class="preview-title">参数预览</h5>
          <div class="preview-content">
            <pre>{{ formatParameterPreview() }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮区域 -->
    <div class="config-actions-bottom">
      <button
        class="primary-btn"
        @click="applyConfiguration"
        :disabled="!canApplyConfiguration"
      >
        <i class="fas fa-check"></i>
        应用配置
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
      <button
        class="secondary-btn"
        @click="shareConfiguration"
        :disabled="!hasValidConfiguration"
      >
        <i class="fas fa-share"></i>
        分享配置
      </button>
    </div>

    <!-- 参数信息对话框 -->
    <div class="modal-overlay" v-if="showInfoDialog" @click="showInfoDialog = false">
      <div class="modal-dialog" @click.stop>
        <div class="dialog-header">
          <h4>参数说明</h4>
          <button class="close-btn" @click="showInfoDialog = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="dialog-content" v-if="selectedParameter">
          <h5>{{ selectedParameter.displayName }}</h5>
          <p>{{ selectedParameter.description }}</p>
          <div class="parameter-details">
            <div class="detail-item">
              <span class="detail-label">类型:</span>
              <span class="detail-value">{{ getParameterTypeName(selectedParameter.type) }}</span>
            </div>
            <div class="detail-item" v-if="selectedParameter.min !== undefined">
              <span class="detail-label">最小值:</span>
              <span class="detail-value">{{ selectedParameter.min }}</span>
            </div>
            <div class="detail-item" v-if="selectedParameter.max !== undefined">
              <span class="detail-label">最大值:</span>
              <span class="detail-value">{{ selectedParameter.max }}</span>
            </div>
            <div class="detail-item" v-if="selectedParameter.defaultValue !== undefined">
              <span class="detail-label">默认值:</span>
              <span class="detail-value">{{ selectedParameter.defaultValue }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模板对话框 -->
    <div class="modal-overlay" v-if="showTemplateDialog" @click="showTemplateDialog = false">
      <div class="modal-dialog template-dialog" @click.stop>
        <div class="dialog-header">
          <h4>参数模板</h4>
          <button class="close-btn" @click="showTemplateDialog = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="dialog-content">
          <div class="template-grid">
            <div
              v-for="template in parameterTemplates"
              :key="template.id"
              class="template-card"
              @click="loadTemplate(template)"
            >
              <div class="template-header">
                <h5>{{ template.name }}</h5>
                <div class="template-meta">
                  <span class="template-category">{{ template.category }}</span>
                  <span class="template-difficulty">{{ template.difficulty }}</span>
                </div>
              </div>
              <p class="template-description">{{ template.description }}</p>
              <div class="template-params">
                <span class="param-count">{{ template.parameters.length }} 个参数</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { intelligentRecommendationService } from '../../services/intelligent-recommendation.service'
import { workflowService } from '../../services/workflow.service'
import type { 
  Parameter, 
  ParameterTemplate, 
  AIRecommendation,
  ParameterCategory 
} from '../../types/hybrid-parameter-config'

// 响应式数据
const showAdvanced = ref(false)
const autoMode = ref(false)
const selectedMode = ref<'ai' | 'manual' | 'hybrid'>('hybrid')
const isRefreshing = ref(false)
const isSyncing = ref(false)
const showValidation = ref(true)
const showInfoDialog = ref(false)
const showTemplateDialog = ref(false)
const selectedParameter = ref<Parameter | null>(null)
const selectedRecommendations = ref<number[]>([])
const appliedRecommendations = ref<number[]>([])
const expandedCategories = ref<string[]>([])

// AI推荐相关
const aiRecommendations = ref<AIRecommendation[]>([])
const aiParameters = ref<Parameter[]>([])

// 手动参数相关
const parameterCategories = ref<ParameterCategory[]>([])
const userParameters = ref<Parameter[]>([])

// 模板相关
const parameterTemplates = ref<ParameterTemplate[]>([])

// 配置模式
const configModes = ref([
  {
    id: 'ai',
    name: 'AI推荐',
    icon: 'fas fa-robot',
    description: '使用AI智能推荐参数'
  },
  {
    id: 'manual',
    name: '手动配置',
    icon: 'fas fa-user-cog',
    description: '手动配置所有参数'
  },
  {
    id: 'hybrid',
    name: '混合模式',
    icon: 'fas fa-layer-group',
    description: 'AI推荐与手动配置结合'
  }
])

// 计算属性
const hasValidRecommendations = computed(() => {
  return aiRecommendations.value.length > 0 && 
         aiRecommendations.value.some(rec => rec.confidence > 70)
})

const validParameterCount = computed(() => {
  const allParams = [...aiParameters.value, ...userParameters.value]
  return allParams.filter(param => !param.error).length
})

const invalidParameterCount = computed(() => {
  const allParams = [...aiParameters.value, ...userParameters.value]
  return allParams.filter(param => param.error).length
})

const completionPercentage = computed(() => {
  const totalParams = validParameterCount.value + invalidParameterCount.value
  if (totalParams === 0) return 0
  return Math.round((validParameterCount.value / totalParams) * 100)
})

const canApplyConfiguration = computed(() => {
  return completionPercentage.value === 100
})

const hasValidConfiguration = computed(() => {
  return validParameterCount.value > 0
})

// 方法
const toggleView = () => {
  showAdvanced.value = !showAdvanced.value
}

const resetParameters = () => {
  // 重置所有参数到默认值
  const resetParam = (param: Parameter) => {
    if (param.defaultValue !== undefined) {
      param.value = param.defaultValue
    }
    param.error = null
  }
  
  aiParameters.value.forEach(resetParam)
  userParameters.value.forEach(resetParam)
}

const toggleAutoMode = () => {
  autoMode.value = !autoMode.value
  if (autoMode.value) {
    // 启用自动模式，开始AI监控
    startAutoMode()
  } else {
    // 停止自动模式
    stopAutoMode()
  }
}

const selectMode = (mode: 'ai' | 'manual' | 'hybrid') => {
  selectedMode.value = mode
  // 根据模式加载相应的参数
  loadParametersForMode(mode)
}

const loadParametersForMode = async (mode: 'ai' | 'manual' | 'hybrid') => {
  try {
    switch (mode) {
      case 'ai':
        await loadAIRecommendations()
        break
      case 'manual':
        await loadManualParameters()
        break
      case 'hybrid':
        await loadHybridParameters()
        break
    }
  } catch (error) {
    console.error(`加载${mode}模式参数失败:`, error)
  }
}

const loadAIRecommendations = async () => {
  isRefreshing.value = true
  try {
    const recommendations = await intelligentRecommendationService.getParameterRecommendations()
    aiRecommendations.value = recommendations
    
    // 提取AI参数
    aiParameters.value = recommendations.length > 0 
      ? recommendations[0].parameters 
      : []
  } finally {
    isRefreshing.value = false
  }
}

const loadManualParameters = async () => {
  try {
    const categories = await intelligentRecommendationService.getParameterCategories()
    parameterCategories.value = categories
    
    // 展开第一个分类
    if (categories.length > 0) {
      expandedCategories.value = [categories[0].id]
    }
    
    // 收集所有参数
    userParameters.value = categories.flatMap(cat => cat.parameters)
  } catch (error) {
    console.error('加载手动参数失败:', error)
  }
}

const loadHybridParameters = async () => {
  await Promise.all([
    loadAIRecommendations(),
    loadManualParameters()
  ])
}

const refreshRecommendations = () => {
  loadAIRecommendations()
}

const applyAllRecommendations = () => {
  selectedRecommendations.value = aiRecommendations.value.map((_, index) => index)
}

const toggleRecommendationSelection = (index: number) => {
  const selectedIndex = selectedRecommendations.value.indexOf(index)
  if (selectedIndex > -1) {
    selectedRecommendations.value.splice(selectedIndex, 1)
  } else {
    selectedRecommendations.value.push(index)
  }
}

const applyRecommendation = async (index: number) => {
  try {
    const recommendation = aiRecommendations.value[index]
    await intelligentRecommendationService.applyParameterRecommendation(recommendation)
    
    appliedRecommendations.value.push(index)
    
    // 更新参数
    aiParameters.value = recommendation.parameters
  } catch (error) {
    console.error('应用推荐失败:', error)
  }
}

const editRecommendationParam = (recommendationIndex: number, param: Parameter) => {
  // 可以添加编辑推荐参数的逻辑
  console.log('编辑推荐参数:', recommendationIndex, param)
}

const formatParameterValue = (param: Parameter) => {
  if (param.type === 'boolean') {
    return param.value ? '是' : '否'
  } else if (param.type === 'select') {
    const option = param.options?.find(opt => opt.value === param.value)
    return option?.label || param.value
  } else if (param.type === 'date') {
    return new Date(param.value).toLocaleDateString()
  }
  return param.value
}

const toggleCategory = (categoryId: string) => {
  const index = expandedCategories.value.indexOf(categoryId)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(categoryId)
  }
}

const getParameterTypeIcon = (type: string) => {
  const icons = {
    'number': 'fas fa-hashtag',
    'range': 'fas fa-sliders-h',
    'text': 'fas fa-font',
    'select': 'fas fa-list',
    'boolean': 'fas fa-check-square',
    'date': 'fas fa-calendar',
    'color': 'fas fa-palette'
  }
  return icons[type] || 'fas fa-question'
}

const getParameterTypeName = (type: string) => {
  const names = {
    'number': '数值',
    'range': '范围',
    'text': '文本',
    'select': '选择',
    'boolean': '布尔值',
    'date': '日期',
    'color': '颜色'
  }
  return names[type] || '未知'
}

const validateParameter = (param: Parameter) => {
  param.error = null
  
  switch (param.type) {
    case 'number':
    case 'range':
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
      } else if (param.validation?.minLength && param.value.length < param.validation.minLength) {
        param.error = `长度不能少于 ${param.validation.minLength} 个字符`
      } else if (param.validation?.maxLength && param.value.length > param.validation.maxLength) {
        param.error = `长度不能超过 ${param.validation.maxLength} 个字符`
      } else if (param.validation?.pattern && !new RegExp(param.validation.pattern).test(param.value)) {
        param.error = '格式不正确'
      }
      break
      
    case 'select':
      if (param.required && !param.value) {
        param.error = '请选择一个选项'
      }
      break
      
    case 'boolean':
      // 布尔值总是有效的
      break
      
    case 'date':
      if (param.required && !param.value) {
        param.error = '请选择日期'
      } else if (param.value) {
        const date = new Date(param.value)
        if (isNaN(date.getTime())) {
          param.error = '请输入有效的日期'
        } else if (param.min && date < new Date(param.min)) {
          param.error = `日期不能早于 ${param.min}`
        } else if (param.max && date > new Date(param.max)) {
          param.error = `日期不能晚于 ${param.max}`
        }
      }
      break
  }
}

const adjustParameter = (param: Parameter, direction: number) => {
  const step = param.step || 1
  const newValue = Number(param.value) + (direction * step)
  
  if (param.min !== undefined && newValue < param.min) return
  if (param.max !== undefined && newValue > param.max) return
  
  param.value = newValue
  validateParameter(param)
}

const applySuggestion = (param: Parameter, suggestion: string) => {
  param.value = suggestion
  validateParameter(param)
}

const showParameterInfo = (param: Parameter) => {
  selectedParameter.value = param
  showInfoDialog.value = true
}

const isParameterModified = (param: Parameter) => {
  return param.defaultValue !== undefined && param.value !== param.defaultValue
}

const syncWithAI = async () => {
  isSyncing.value = true
  try {
    const syncResult = await intelligentRecommendationService.syncParametersWithAI(userParameters.value)
    
    // 更新用户参数
    userParameters.value = syncResult.parameters
  } catch (error) {
    console.error('AI同步失败:', error)
  } finally {
    isSyncing.value = false
  }
}

const adoptAIParameter = (param: Parameter) => {
  // 在用户参数中找到对应的参数并更新
  const userParam = userParameters.value.find(p => p.name === param.name)
  if (userParam) {
    userParam.value = param.value
    validateParameter(userParam)
  }
}

const getParameterStatus = (param: Parameter) => {
  if (param.error) return 'error'
  if (isParameterModified(param)) return 'modified'
  return 'valid'
}

const getParameterStatusText = (param: Parameter) => {
  const status = getParameterStatus(param)
  const statusTexts = {
    'valid': '有效',
    'modified': '已修改',
    'error': '错误'
  }
  return statusTexts[status] || '未知'
}

const formatParameterPreview = () => {
  const allParams = [...aiParameters.value, ...userParameters.value]
  const config = {}
  
  allParams.forEach(param => {
    config[param.name] = param.value
  })
  
  return JSON.stringify(config, null, 2)
}

const applyConfiguration = async () => {
  if (!canApplyConfiguration.value) return
  
  try {
    const allParams = [...aiParameters.value, ...userParameters.value]
    await workflowService.updateParameters(allParams)
    
    // 可以添加成功提示
    console.log('配置应用成功')
  } catch (error) {
    console.error('应用配置失败:', error)
  }
}

const saveConfiguration = () => {
  const config = {
    mode: selectedMode.value,
    aiParameters: aiParameters.value,
    userParameters: userParameters.value,
    timestamp: new Date().toISOString()
  }
  
  localStorage.setItem('hybrid-parameter-config', JSON.stringify(config))
  console.log('配置已保存')
}

const exportConfiguration = () => {
  const config = {
    mode: selectedMode.value,
    aiParameters: aiParameters.value,
    userParameters: userParameters.value,
    timestamp: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(config, null, 2)], {
    type: 'application/json'
  })
  
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `hybrid-parameter-config-${Date.now()}.json`
  a.click()
  
  URL.revokeObjectURL(url)
}

const shareConfiguration = async () => {
  try {
    const config = {
      mode: selectedMode.value,
      aiParameters: aiParameters.value,
      userParameters: userParameters.value,
      timestamp: new Date().toISOString()
    }
    
    const shareId = await intelligentRecommendationService.shareConfiguration(config)
    
    // 可以复制分享链接到剪贴板
    const shareUrl = `${window.location.origin}/shared-config/${shareId}`
    navigator.clipboard.writeText(shareUrl)
    
    console.log('配置已分享:', shareUrl)
  } catch (error) {
    console.error('分享配置失败:', error)
  }
}

const loadTemplate = (template: ParameterTemplate) => {
  userParameters.value = template.parameters.map(param => ({ ...param }))
  showTemplateDialog.value = false
}

const saveAsTemplate = () => {
  const template = {
    id: `template-${Date.now()}`,
    name: `自定义模板 ${new Date().toLocaleDateString()}`,
    category: '自定义',
    difficulty: '中级',
    description: '用户自定义的参数模板',
    parameters: userParameters.value
  }
  
  parameterTemplates.value.push(template)
  localStorage.setItem('parameter-templates', JSON.stringify(parameterTemplates.value))
  
  console.log('模板已保存')
}

const startAutoMode = () => {
  // 启动自动模式，定期同步AI推荐
  console.log('自动模式已启动')
}

const stopAutoMode = () => {
  // 停止自动模式
  console.log('自动模式已停止')
}

// 监听模式变化
watch(selectedMode, (newMode) => {
  loadParametersForMode(newMode)
})

// 组件挂载时的初始化
onMounted(async () => {
  // 加载保存的配置
  const savedConfig = localStorage.getItem('hybrid-parameter-config')
  if (savedConfig) {
    try {
      const config = JSON.parse(savedConfig)
      selectedMode.value = config.mode || 'hybrid'
      aiParameters.value = config.aiParameters || []
      userParameters.value = config.userParameters || []
    } catch (error) {
      console.error('加载保存的配置失败:', error)
    }
  }
  
  // 加载参数模板
  const savedTemplates = localStorage.getItem('parameter-templates')
  if (savedTemplates) {
    try {
      parameterTemplates.value = JSON.parse(savedTemplates)
    } catch (error) {
      console.error('加载参数模板失败:', error)
    }
  }
  
  // 初始化参数
  await loadParametersForMode(selectedMode.value)
})
</script>

<style scoped>
.hybrid-parameter-config {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
  overflow: hidden;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.config-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-actions {
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

.mode-selector {
  padding: 16px;
  border-bottom: 1px solid #e9ecef;
}

.mode-tabs {
  display: flex;
  gap: 8px;
}

.mode-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-tab:hover {
  border-color: #007bff;
  background: #f8f9ff;
}

.mode-tab.active {
  border-color: #007bff;
  background: #007bff;
  color: white;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-actions {
  display: flex;
  gap: 8px;
}

.refresh-btn,
.apply-all-btn,
.load-template-btn,
.save-template-btn,
.sync-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: background 0.2s;
}

.refresh-btn:hover:not(:disabled),
.apply-all-btn:hover:not(:disabled),
.load-template-btn:hover,
.save-template-btn:hover,
.sync-btn:hover:not(:disabled) {
  background: #0056b3;
}

.refresh-btn:disabled,
.apply-all-btn:disabled,
.sync-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.ai-recommendations,
.manual-parameters,
.hybrid-mode {
  padding: 16px;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
}

.recommendation-item {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
}

.recommendation-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
}

.recommendation-item.selected {
  border-color: #007bff;
  background: #f8f9ff;
}

.recommendation-item.applied {
  border-color: #28a745;
  background: #f8fff8;
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.recommendation-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.recommendation-confidence {
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

.recommendation-content {
  margin-bottom: 16px;
}

.recommendation-description {
  margin: 0 0 12px 0;
  color: #666;
  line-height: 1.5;
}

.recommendation-params {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.param-name {
  font-weight: 500;
  color: #333;
}

.param-value {
  color: #666;
  font-family: monospace;
}

.param-edit-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  padding: 2px;
}

.param-edit-btn:hover {
  color: #0056b3;
}

.recommendation-actions {
  display: flex;
  gap: 8px;
}

.select-btn,
.apply-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.select-btn {
  background: #f8f9fa;
  color: #333;
  border: 1px solid #e9ecef;
}

.select-btn:hover,
.select-btn.selected {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.apply-btn {
  background: #28a745;
  color: white;
}

.apply-btn:hover:not(:disabled) {
  background: #218838;
}

.apply-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.parameter-categories {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-section {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  cursor: pointer;
  transition: background 0.2s;
}

.category-header:hover {
  background: #e9ecef;
}

.category-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-toggle {
  color: #666;
  transition: transform 0.2s;
}

.category-content {
  padding: 16px;
}

.parameter-item {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.parameter-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.parameter-item.has-error {
  border-left: 3px solid #dc3545;
}

.parameter-item.modified {
  border-left: 3px solid #ffc107;
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
  display: flex;
  align-items: center;
  gap: 4px;
}

.required-indicator {
  color: #dc3545;
  font-weight: bold;
}

.parameter-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-btn {
  background: none;
  border: none;
  color: #17a2b8;
  cursor: pointer;
  padding: 2px;
}

.info-btn:hover {
  color: #138496;
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

.number-input-group,
.range-input-group,
.text-input-group,
.date-input-group,
.color-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.parameter-input,
.parameter-select,
.parameter-range,
.hybrid-input,
.hybrid-select {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.parameter-input:focus,
.parameter-select:focus,
.parameter-range:focus,
.hybrid-input:focus,
.hybrid-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

.input-controls {
  display: flex;
  gap: 4px;
}

.control-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px 6px;
  cursor: pointer;
  font-size: 12px;
}

.control-btn:hover {
  background: #e9ecef;
}

.range-value {
  min-width: 40px;
  text-align: center;
  font-weight: 600;
  color: #333;
}

.checkbox-group {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
}

.checkbox-text {
  color: #333;
  line-height: 1.4;
}

.input-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.suggestion-btn {
  background: #e9ecef;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-btn:hover {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.color-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #ddd;
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

.parameter-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #17a2b8;
  font-size: 12px;
  margin-top: 4px;
}

.hybrid-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hybrid-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.hybrid-column {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
}

.column-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.column-params {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hybrid-param {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.param-control {
  flex: 1;
}

.param-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.valid {
  background: #28a745;
}

.status-indicator.modified {
  background: #ffc107;
}

.status-indicator.error {
  background: #dc3545;
}

.status-text {
  font-size: 12px;
  color: #666;
}

.adopt-btn {
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 12px;
}

.adopt-btn:hover {
  background: #138496;
}

.validation-preview {
  padding: 16px;
  border-top: 1px solid #e9ecef;
}

.validation-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border: 1px solid #e9ecef;
  border-radius: 4px;
}

.summary-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
}

.summary-value.valid {
  color: #28a745;
}

.summary-value.invalid {
  color: #dc3545;
}

.progress-bar {
  width: 100px;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 4px;
}

.progress-fill {
  height: 100%;
  background: #007bff;
  transition: width 0.3s;
}

.progress-value {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.parameter-preview {
  margin-top: 16px;
}

.preview-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.preview-content {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.preview-content pre {
  margin: 0;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.4;
  color: #333;
}

.config-actions-bottom {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e9ecef;
  justify-content: center;
}

.primary-btn,
.secondary-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.primary-btn {
  background: #007bff;
  color: white;
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

.template-dialog {
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
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.template-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.template-header h5 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.template-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.template-category,
.template-difficulty {
  font-size: 12px;
  color: #666;
}

.template-description {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.template-params {
  display: flex;
  justify-content: flex-end;
}

.param-count {
  font-size: 12px;
  color: #666;
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 12px;
}

.parameter-details {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.detail-label {
  font-weight: 500;
  color: #666;
}

.detail-value {
  font-weight: 600;
  color: #333;
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