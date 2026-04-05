/**
 * 混合参数配置服务类
 * 提供参数配置、验证、同步等功能
 */

import { ref, reactive, computed, watch } from 'vue'
import type {
  Parameter,
  ParameterValidation,
  ParameterOption,
  ParameterSuggestion,
  AIRecommendation,
  ParameterCategory,
  ParameterTemplate,
  ParameterConfigMode,
  ParameterSyncStatus,
  ParameterHistory,
  ParameterComparison,
  ParameterExport,
  ParameterImportResult,
  ParameterValidationResult,
  ParameterSearchFilter,
  ParameterSearchResult,
  ParameterBatchOperation,
  ParameterBatchResult,
  ParameterDependency,
  ParameterCondition,
  ParameterGroup,
  ParameterPreset,
  ParameterConfigState,
  ParameterConfigEvents,
  ParameterConfigStats,
  ParameterConfigSettings,
  ParameterConfigError,
  ParameterConfigErrorDetails
} from '@/types/hybrid-parameter-config'

import { ParameterType } from '@/types/hybrid-parameter-config'

// 事件发射器接口
interface EventEmitter {
  on(event: string, callback: Function): void
  off(event: string, callback: Function): void
  emit(event: string, data?: any): void
}

/**
 * 混合参数配置服务类
 */
export class HybridParameterConfigService implements EventEmitter {
  // 事件监听器
  private listeners: Map<string, Function[]> = new Map()

  // 状态管理
  private state = reactive<ParameterConfigState>({
    mode: 'hybrid',
    autoMode: false,
    showAdvanced: false,
    showValidation: true,
    selectedRecommendations: [],
    appliedRecommendations: [],
    expandedCategories: [],
    searchQuery: '',
    activeFilters: {},
    validationResults: {
      isValid: true,
      errors: [],
      warnings: []
    },
    syncStatus: {
      lastSync: new Date().toISOString(),
      syncInProgress: false,
      conflicts: []
    },
    history: [],
    clipboard: {
      parameters: [],
      copiedAt: ''
    }
  })

  // 设置
  private settings = reactive<ParameterConfigSettings>({
    autoSave: true,
    autoSaveInterval: 30000,
    enableValidation: true,
    validationMode: 'realtime',
    enableHistory: true,
    historyLimit: 100,
    enableSync: true,
    syncInterval: 60000,
    enableSuggestions: true,
    suggestionMode: 'auto',
    enableAdvancedMode: true,
    defaultViewMode: 'simple',
    theme: 'auto',
    language: 'zh-CN',
    exportFormat: 'json',
    showHiddenParameters: false,
    enableBatchOperations: true,
    enableParameterGroups: true,
    enableParameterDependencies: true
  })

  // 参数存储
  private parameters = ref<Parameter[]>([])
  private categories = ref<ParameterCategory[]>([])
  private templates = ref<ParameterTemplate[]>([])
  private recommendations = ref<AIRecommendation[]>([])
  private presets = ref<ParameterPreset[]>([])
  private dependencies = ref<ParameterDependency[]>([])
  private conditions = ref<ParameterCondition[]>([])
  private groups = ref<ParameterGroup[]>([])

  // 计算属性
  readonly visibleParameters = computed(() => {
    return this.parameters.value.filter(param => 
      !param.hidden && 
      (this.settings.showHiddenParameters || !param.advanced || this.state.showAdvanced)
    )
  })

  readonly modifiedParameters = computed(() => {
    return this.parameters.value.filter(param => param.modified)
  })

  readonly invalidParameters = computed(() => {
    return this.parameters.value.filter(param => param.error)
  })

  readonly completionRate = computed(() => {
    const total = this.visibleParameters.value.length
    const filled = this.visibleParameters.value.filter(param => 
      param.value !== null && param.value !== undefined && param.value !== ''
    ).length
    return total > 0 ? Math.round((filled / total) * 100) : 0
  })

  readonly statistics = computed((): ParameterConfigStats => {
    const total = this.parameters.value.length
    const visible = this.visibleParameters.value.length
    const modified = this.modifiedParameters.value.length
    const invalid = this.invalidParameters.value.length
    const filled = this.visibleParameters.value.filter(param => 
      param.value !== null && param.value !== undefined && param.value !== ''
    ).length

    // 计算类别分布
    const categoryDistribution = this.categories.value.map(category => {
      const count = this.parameters.value.filter(param => param.category === category.id).length
      return {
        category: category.name,
        count,
        percentage: total > 0 ? Math.round((count / total) * 100) : 0
      }
    })

    // 计算验证摘要
    const validationSummary = {
      valid: this.state.validationResults.errors.length === 0 ? total - invalid : total - this.state.validationResults.errors.length,
      warnings: this.state.validationResults.warnings.length,
      errors: this.state.validationResults.errors.length
    }

    return {
      totalParameters: total,
      visibleParameters: visible,
      modifiedParameters: modified,
      invalidParameters: invalid,
      filledParameters: filled,
      completionRate: this.completionRate.value,
      mostUsedParameters: [], // 需要从历史记录中计算
      categoryDistribution,
      validationSummary
    }
  })

  /**
   * 构造函数
   */
  constructor() {
    this.initializeDefaultParameters()
    this.initializeDefaultCategories()
    this.initializeDefaultTemplates()
    this.initializeDefaultPresets()
    this.setupAutoSave()
    this.setupAutoSync()
  }

  /**
   * 初始化默认参数
   */
  private initializeDefaultParameters(): void {
    this.parameters.value = [
      {
        name: 'strategy_name',
        displayName: '策略名称',
        type: ParameterType.TEXT,
        value: '',
        placeholder: '请输入策略名称',
        description: '策略的唯一标识名称',
        group: 'basic',
        order: 1,
        validation: {
          required: true,
          minLength: 2,
          maxLength: 50,
          pattern: '^[a-zA-Z0-9_-]+$'
        }
      },
      {
        name: 'start_date',
        displayName: '开始日期',
        type: ParameterType.DATE,
        value: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        description: '回测开始日期',
        group: 'time',
        order: 1,
        validation: {
          required: true
        }
      },
      {
        name: 'end_date',
        displayName: '结束日期',
        type: ParameterType.DATE,
        value: new Date().toISOString().split('T')[0],
        description: '回测结束日期',
        group: 'time',
        order: 2,
        validation: {
          required: true
        }
      },
      {
        name: 'initial_capital',
        displayName: '初始资金',
        type: ParameterType.NUMBER,
        value: 1000000,
        description: '回测初始资金金额',
        group: 'capital',
        order: 1,
        validation: {
          required: true,
          min: 1000,
          max: 1000000000,
          step: 1000
        }
      },
      {
        name: 'benchmark',
        displayName: '基准指数',
        type: ParameterType.SELECT,
        value: '000300',
        description: '用于比较的基准指数',
        group: 'benchmark',
        order: 1,
        options: [
          { label: '沪深300', value: '000300' },
          { label: '中证500', value: '000905' },
          { label: '中证1000', value: '000852' },
          { label: '创业板指', value: '399006' },
          { label: '科创50', value: '000688' }
        ],
        validation: {
          required: true
        }
      },
      {
        name: 'universe',
        displayName: '股票池',
        type: ParameterType.SELECT,
        value: 'all',
        description: '策略交易的股票范围',
        group: 'universe',
        order: 1,
        options: [
          { label: '全市场', value: 'all' },
          { label: '沪深300成分股', value: 'hs300' },
          { label: '中证500成分股', value: 'zz500' },
          { label: '中证1000成分股', value: 'zz1000' },
          { label: '创业板成分股', value: 'cyb' },
          { label: '科创板成分股', value: 'kcb' }
        ],
        validation: {
          required: true
        }
      },
      {
        name: 'rebalance_frequency',
        displayName: '调仓频率',
        type: ParameterType.SELECT,
        value: 'monthly',
        description: '投资组合的调仓频率',
        group: 'trading',
        order: 1,
        options: [
          { label: '每日', value: 'daily' },
          { label: '每周', value: 'weekly' },
          { label: '每月', value: 'monthly' },
          { label: '每季度', value: 'quarterly' },
          { label: '每半年', value: 'semi_annually' },
          { label: '每年', value: 'annually' }
        ],
        validation: {
          required: true
        }
      },
      {
        name: 'position_limit',
        displayName: '持仓限制',
        type: ParameterType.NUMBER,
        value: 0.1,
        description: '单个股票的最大持仓比例',
        group: 'risk',
        order: 1,
        validation: {
          required: true,
          min: 0.01,
          max: 1,
          step: 0.01
        }
      },
      {
        name: 'enable_short_selling',
        displayName: '允许做空',
        type: ParameterType.BOOLEAN,
        value: false,
        description: '是否允许做空交易',
        group: 'trading',
        order: 2,
        advanced: true
      },
      {
        name: 'enable_leverage',
        displayName: '允许杠杆',
        type: ParameterType.BOOLEAN,
        value: false,
        description: '是否使用杠杆交易',
        group: 'risk',
        order: 2,
        advanced: true
      },
      {
        name: 'leverage_ratio',
        displayName: '杠杆比例',
        type: ParameterType.NUMBER,
        value: 1,
        description: '杠杆交易的比例倍数',
        group: 'risk',
        order: 3,
        advanced: true,
        validation: {
          min: 1,
          max: 10,
          step: 0.1
        },
        hidden: true
      }
    ]
  }

  /**
   * 初始化默认分类
   */
  private initializeDefaultCategories(): void {
    this.categories.value = [
      {
        id: 'basic',
        name: '基本设置',
        description: '策略的基本配置信息',
        icon: 'settings',
        order: 1,
        parameters: [],
        collapsible: false,
        defaultExpanded: true
      },
      {
        id: 'time',
        name: '时间设置',
        description: '回测的时间范围配置',
        icon: 'calendar',
        order: 2,
        parameters: [],
        collapsible: false,
        defaultExpanded: true
      },
      {
        id: 'capital',
        name: '资金设置',
        description: '资金相关的配置参数',
        icon: 'money',
        order: 3,
        parameters: [],
        collapsible: false,
        defaultExpanded: true
      },
      {
        id: 'universe',
        name: '股票池',
        description: '交易标的的选择范围',
        icon: 'stock',
        order: 4,
        parameters: [],
        collapsible: false,
        defaultExpanded: true
      },
      {
        id: 'benchmark',
        name: '基准设置',
        description: '业绩比较基准配置',
        icon: 'chart',
        order: 5,
        parameters: [],
        collapsible: false,
        defaultExpanded: true
      },
      {
        id: 'trading',
        name: '交易设置',
        description: '交易相关的配置参数',
        icon: 'trade',
        order: 6,
        parameters: [],
        collapsible: true,
        defaultExpanded: false
      },
      {
        id: 'risk',
        name: '风险控制',
        description: '风险管理相关配置',
        icon: 'shield',
        order: 7,
        parameters: [],
        collapsible: true,
        defaultExpanded: false
      }
    ]

    // 更新分类中的参数列表
    this.updateCategoryParameters()
  }

  /**
   * 初始化默认模板
   */
  private initializeDefaultTemplates(): void {
    this.templates.value = [
      {
        id: 'beginner_template',
        name: '新手模板',
        description: '适合初学者的简单回测配置',
        category: 'basic',
        difficulty: 'beginner',
        tags: ['新手', '简单', '基础'],
        parameters: [
          {
            name: 'strategy_name',
            displayName: '策略名称',
            type: ParameterType.TEXT,
            value: 'my_first_strategy',
            description: '策略的唯一标识名称',
            group: 'basic',
            order: 1,
            validation: {
              required: true,
              minLength: 2,
              maxLength: 50
            }
          },
          {
            name: 'start_date',
            displayName: '开始日期',
            type: ParameterType.DATE,
            value: '2023-01-01',
            description: '回测开始日期',
            group: 'time',
            order: 1,
            validation: {
              required: true
            }
          },
          {
            name: 'end_date',
            displayName: '结束日期',
            type: ParameterType.DATE,
            value: '2023-12-31',
            description: '回测结束日期',
            group: 'time',
            order: 2,
            validation: {
              required: true
            }
          },
          {
            name: 'initial_capital',
            displayName: '初始资金',
            type: ParameterType.NUMBER,
            value: 100000,
            description: '回测初始资金金额',
            group: 'capital',
            order: 1,
            validation: {
              required: true,
              min: 1000,
              max: 10000000,
              step: 1000
            }
          },
          {
            name: 'benchmark',
            displayName: '基准指数',
            type: ParameterType.SELECT,
            value: '000300',
            description: '用于比较的基准指数',
            group: 'benchmark',
            order: 1,
            options: [
              { label: '沪深300', value: '000300' },
              { label: '中证500', value: '000905' }
            ],
            validation: {
              required: true
            }
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        author: 'System',
        version: '1.0.0',
        isPublic: true,
        usageCount: 0,
        rating: 5
      },
      {
        id: 'advanced_template',
        name: '高级模板',
        description: '适合有经验用户的完整回测配置',
        category: 'advanced',
        difficulty: 'advanced',
        tags: ['高级', '完整', '专业'],
        parameters: [
          {
            name: 'strategy_name',
            displayName: '策略名称',
            type: ParameterType.TEXT,
            value: 'advanced_strategy',
            description: '策略的唯一标识名称',
            group: 'basic',
            order: 1,
            validation: {
              required: true,
              minLength: 2,
              maxLength: 50,
              pattern: '^[a-zA-Z0-9_-]+$'
            }
          },
          {
            name: 'start_date',
            displayName: '开始日期',
            type: ParameterType.DATE,
            value: '2020-01-01',
            description: '回测开始日期',
            group: 'time',
            order: 1,
            validation: {
              required: true
            }
          },
          {
            name: 'end_date',
            displayName: '结束日期',
            type: ParameterType.DATE,
            value: '2023-12-31',
            description: '回测结束日期',
            group: 'time',
            order: 2,
            validation: {
              required: true
            }
          },
          {
            name: 'initial_capital',
            displayName: '初始资金',
            type: ParameterType.NUMBER,
            value: 10000000,
            description: '回测初始资金金额',
            group: 'capital',
            order: 1,
            validation: {
              required: true,
              min: 100000,
              max: 1000000000,
              step: 10000
            }
          },
          {
            name: 'benchmark',
            displayName: '基准指数',
            type: ParameterType.SELECT,
            value: '000300',
            description: '用于比较的基准指数',
            group: 'benchmark',
            order: 1,
            options: [
              { label: '沪深300', value: '000300' },
              { label: '中证500', value: '000905' },
              { label: '中证1000', value: '000852' },
              { label: '创业板指', value: '399006' },
              { label: '科创50', value: '000688' }
            ],
            validation: {
              required: true
            }
          },
          {
            name: 'universe',
            displayName: '股票池',
            type: ParameterType.SELECT,
            value: 'hs300',
            description: '策略交易的股票范围',
            group: 'universe',
            order: 1,
            options: [
              { label: '全市场', value: 'all' },
              { label: '沪深300成分股', value: 'hs300' },
              { label: '中证500成分股', value: 'zz500' },
              { label: '中证1000成分股', value: 'zz1000' }
            ],
            validation: {
              required: true
            }
          },
          {
            name: 'rebalance_frequency',
            displayName: '调仓频率',
            type: ParameterType.SELECT,
            value: 'monthly',
            description: '投资组合的调仓频率',
            group: 'trading',
            order: 1,
            options: [
              { label: '每日', value: 'daily' },
              { label: '每周', value: 'weekly' },
              { label: '每月', value: 'monthly' },
              { label: '每季度', value: 'quarterly' }
            ],
            validation: {
              required: true
            }
          },
          {
            name: 'position_limit',
            displayName: '持仓限制',
            type: ParameterType.NUMBER,
            value: 0.05,
            description: '单个股票的最大持仓比例',
            group: 'risk',
            order: 1,
            validation: {
              required: true,
              min: 0.01,
              max: 0.2,
              step: 0.01
            }
          },
          {
            name: 'enable_short_selling',
            displayName: '允许做空',
            type: ParameterType.BOOLEAN,
            value: true,
            description: '是否允许做空交易',
            group: 'trading',
            order: 2,
            advanced: true
          },
          {
            name: 'enable_leverage',
            displayName: '允许杠杆',
            type: ParameterType.BOOLEAN,
            value: false,
            description: '是否使用杠杆交易',
            group: 'risk',
            order: 2,
            advanced: true
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        author: 'System',
        version: '1.0.0',
        isPublic: true,
        usageCount: 0,
        rating: 5
      }
    ]
  }

  /**
   * 初始化默认预设
   */
  private initializeDefaultPresets(): void {
    this.presets.value = [
      {
        id: 'conservative_preset',
        name: '保守型预设',
        description: '适合风险厌恶投资者的保守配置',
        category: 'risk',
        tags: ['保守', '低风险', '稳健'],
        parameters: [
          { name: 'position_limit', value: 0.03 },
          { name: 'enable_short_selling', value: false },
          { name: 'enable_leverage', value: false },
          { name: 'rebalance_frequency', value: 'quarterly' }
        ],
        isDefault: false,
        isReadOnly: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        author: 'System',
        usageCount: 0,
        rating: 4
      },
      {
        id: 'aggressive_preset',
        name: '激进型预设',
        description: '适合风险偏好投资者的激进配置',
        category: 'risk',
        tags: ['激进', '高风险', '高收益'],
        parameters: [
          { name: 'position_limit', value: 0.15 },
          { name: 'enable_short_selling', value: true },
          { name: 'enable_leverage', value: true },
          { name: 'leverage_ratio', value: 2 },
          { name: 'rebalance_frequency', value: 'weekly' }
        ],
        isDefault: false,
        isReadOnly: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        author: 'System',
        usageCount: 0,
        rating: 4
      },
      {
        id: 'balanced_preset',
        name: '平衡型预设',
        description: '风险和收益平衡的中等配置',
        category: 'risk',
        tags: ['平衡', '中等风险', '稳健收益'],
        parameters: [
          { name: 'position_limit', value: 0.08 },
          { name: 'enable_short_selling', value: false },
          { name: 'enable_leverage', value: false },
          { name: 'rebalance_frequency', value: 'monthly' }
        ],
        isDefault: true,
        isReadOnly: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        author: 'System',
        usageCount: 0,
        rating: 5
      }
    ]
  }

  /**
   * 更新分类中的参数列表
   */
  private updateCategoryParameters(): void {
    this.categories.value.forEach(category => {
      category.parameters = this.parameters.value
        .filter(param => param.group === category.id)
        .map(param => param.name) as any
    })
  }

  /**
   * 设置自动保存
   */
  private setupAutoSave(): void {
    if (!this.settings.autoSave) return

    setInterval(() => {
      this.saveParameters()
    }, this.settings.autoSaveInterval)
  }

  /**
   * 设置自动同步
   */
  private setupAutoSync(): void {
    if (!this.settings.enableSync) return

    setInterval(() => {
      this.syncParameters()
    }, this.settings.syncInterval)
  }

  /**
   * 获取参数值
   */
  getParameterValue(name: string): any {
    const parameter = this.parameters.value.find(p => p.name === name)
    return parameter ? parameter.value : undefined
  }

  /**
   * 设置参数值
   */
  setParameterValue(name: string, value: any): void {
    const parameter = this.parameters.value.find(p => p.name === name)
    if (!parameter) return

    const oldValue = parameter.value
    parameter.value = value
    parameter.modified = value !== parameter.defaultValue

    // 验证参数
    if (this.settings.enableValidation) {
      this.validateParameter(parameter)
    }

    // 添加到历史记录
    if (this.settings.enableHistory) {
      this.addToHistory(parameter.name, oldValue, value, 'user')
    }

    // 处理依赖关系
    this.processDependencies(parameter)

    // 发射事件
    this.emit('parameter-changed', { parameter: name, oldValue, newValue: value })

    // 自动保存
    if (this.settings.autoSave && this.settings.validationMode === 'realtime') {
      this.saveParameters()
    }
  }

  /**
   * 验证参数
   */
  private validateParameter(parameter: Parameter): void {
    if (!parameter.validation) {
      parameter.error = null
      return
    }

    const { validation } = parameter
    let error = null

    // 必填验证
    if (validation.required && (parameter.value === null || parameter.value === undefined || parameter.value === '')) {
      error = '此参数为必填项'
    }
    // 类型验证
    else if (parameter.value !== null && parameter.value !== undefined) {
      switch (parameter.type) {
        case ParameterType.NUMBER:
          const numValue = Number(parameter.value)
          if (isNaN(numValue)) {
            error = '请输入有效的数字'
          } else {
            if (validation.min !== undefined && numValue < validation.min) {
              error = `值不能小于 ${validation.min}`
            } else if (validation.max !== undefined && numValue > validation.max) {
              error = `值不能大于 ${validation.max}`
            }
          }
          break
        case ParameterType.TEXT:
          const strValue = String(parameter.value)
          if (validation.minLength !== undefined && strValue.length < validation.minLength) {
            error = `长度不能少于 ${validation.minLength} 个字符`
          } else if (validation.maxLength !== undefined && strValue.length > validation.maxLength) {
            error = `长度不能超过 ${validation.maxLength} 个字符`
          } else if (validation.pattern && !new RegExp(validation.pattern).test(strValue)) {
            error = '格式不正确'
          }
          break
      }
    }

    // 自定义验证
    if (!error && validation.custom) {
      const customResult = validation.custom(parameter.value)
      if (customResult !== true) {
        error = typeof customResult === 'string' ? customResult : '验证失败'
      }
    }

    parameter.error = error

    // 更新整体验证结果
    this.updateValidationResults()
  }

  /**
   * 更新整体验证结果
   */
  private updateValidationResults(): void {
    const errors = this.parameters.value
      .filter(param => param.error)
      .map(param => ({
        parameter: param.name,
        message: param.error!,
        type: 'custom' as const,
        severity: 'error' as const
      }))

    this.state.validationResults = {
      isValid: errors.length === 0,
      errors,
      warnings: []
    }

    this.emit('parameter-validated', { 
      result: this.state.validationResults 
    })
  }

  /**
   * 添加到历史记录
   */
  private addToHistory(parameterName: string, oldValue: any, newValue: any, changedBy: 'user' | 'ai' | 'system', reason?: string): void {
    const historyItem: ParameterHistory = {
      id: Date.now().toString(),
      parameterName,
      oldValue,
      newValue,
      changedAt: new Date().toISOString(),
      changedBy,
      reason,
      context: {
        mode: this.state.mode
      }
    }

    this.state.history.unshift(historyItem)

    // 限制历史记录数量
    if (this.state.history.length > this.settings.historyLimit) {
      this.state.history = this.state.history.slice(0, this.settings.historyLimit)
    }
  }

  /**
   * 处理依赖关系
   */
  private processDependencies(changedParameter: Parameter): void {
    if (!this.settings.enableParameterDependencies) return

    this.dependencies.value.forEach(dependency => {
      if (dependency.source === changedParameter.name) {
        const targetParameter = this.parameters.value.find(p => p.name === dependency.target)
        if (!targetParameter) return

        const conditionMet = this.evaluateCondition(dependency.condition, changedParameter.value)
        
        if (conditionMet) {
          this.applyDependencyAction(dependency.action, targetParameter)
        }
      }
    })
  }

  /**
   * 评估条件
   */
  private evaluateCondition(condition: any, value: any): boolean {
    switch (condition.operator) {
      case 'equals':
        return value === condition.value
      case 'not_equals':
        return value !== condition.value
      case 'greater_than':
        return Number(value) > Number(condition.value)
      case 'less_than':
        return Number(value) < Number(condition.value)
      case 'contains':
        return String(value).includes(String(condition.value))
      case 'not_contains':
        return !String(value).includes(String(condition.value))
      default:
        return false
    }
  }

  /**
   * 应用依赖动作
   */
  private applyDependencyAction(action: any, targetParameter: Parameter): void {
    switch (action.type) {
      case 'set':
        if (action.value !== undefined) {
          this.setParameterValue(targetParameter.name, action.value)
        }
        break
      case 'hide':
        targetParameter.hidden = true
        break
      case 'disable':
        targetParameter.disabled = true
        break
      case 'validate':
        if (this.settings.enableValidation) {
          this.validateParameter(targetParameter)
        }
        break
    }
  }

  /**
   * 保存参数
   */
  private async saveParameters(): Promise<void> {
    try {
      const parametersData = JSON.stringify(this.parameters.value)
      localStorage.setItem('hybrid_parameter_config', parametersData)
      
      // 这里可以添加API调用保存到服务器
      // await api.saveParameters(this.parameters.value)
    } catch (error) {
      console.error('保存参数失败:', error)
    }
  }

  /**
   * 同步参数
   */
  private async syncParameters(): Promise<void> {
    if (this.state.syncStatus.syncInProgress) return

    this.state.syncStatus.syncInProgress = true
    this.emit('sync-started', { parameters: this.parameters.value.map(p => p.name) })

    try {
      // 这里可以添加API调用同步到服务器
      // const result = await api.syncParameters(this.parameters.value)
      
      this.state.syncStatus.lastSync = new Date().toISOString()
      this.state.syncStatus.conflicts = []
      
      this.emit('sync-completed', { result: this.state.syncStatus })
    } catch (error) {
      console.error('同步参数失败:', error)
    } finally {
      this.state.syncStatus.syncInProgress = false
    }
  }

  /**
   * 加载模板
   */
  loadTemplate(templateId: string): void {
    const template = this.templates.value.find(t => t.id === templateId)
    if (!template) return

    template.parameters.forEach(templateParam => {
      const parameter = this.parameters.value.find(p => p.name === templateParam.name)
      if (parameter) {
        const oldValue = parameter.value
        parameter.value = templateParam.value
        parameter.modified = templateParam.value !== parameter.defaultValue

        if (this.settings.enableHistory) {
          this.addToHistory(parameter.name, oldValue, templateParam.value, 'user', `加载模板: ${template.name}`)
        }
      }
    })

    this.updateValidationResults()
    this.emit('template-loaded', { templateId, parameters: template.parameters })
  }

  /**
   * 保存为模板
   */
  saveAsTemplate(name: string, description: string, category: string): void {
    const template: ParameterTemplate = {
      id: Date.now().toString(),
      name,
      description,
      category,
      difficulty: 'intermediate',
      tags: [],
      parameters: this.parameters.value.map(param => ({
        ...param,
        value: param.value
      })),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      author: 'User',
      version: '1.0.0',
      isPublic: false,
      usageCount: 0,
      rating: 0
    }

    this.templates.value.push(template)
    this.emit('template-saved', { templateId: template.id, parameters: template.parameters })
  }

  /**
   * 应用预设
   */
  applyPreset(presetId: string): void {
    const preset = this.presets.value.find(p => p.id === presetId)
    if (!preset) return

    preset.parameters.forEach(presetParam => {
      const parameter = this.parameters.value.find(p => p.name === presetParam.name)
      if (parameter) {
        const oldValue = parameter.value
        parameter.value = presetParam.value
        parameter.modified = presetParam.value !== parameter.defaultValue

        if (this.settings.enableHistory) {
          this.addToHistory(parameter.name, oldValue, presetParam.value, 'user', `应用预设: ${preset.name}`)
        }
      }
    })

    this.updateValidationResults()
  }

  /**
   * 搜索参数
   */
  searchParameters(filter: ParameterSearchFilter): ParameterSearchResult[] {
    const query = (filter.query || '').toLowerCase()
    const results: ParameterSearchResult[] = []

    this.parameters.value.forEach(parameter => {
      let score = 0
      const matches: Array<{ field: string; value: string; highlight: string }> = []

      // 名称匹配
      if (parameter.displayName.toLowerCase().includes(query)) {
        score += 10
        matches.push({
          field: 'displayName',
          value: parameter.displayName,
          highlight: this.highlightText(parameter.displayName, query)
        })
      }

      // 描述匹配
      if (parameter.description.toLowerCase().includes(query)) {
        score += 5
        matches.push({
          field: 'description',
          value: parameter.description,
          highlight: this.highlightText(parameter.description, query)
        })
      }

      // 分类匹配
      if (filter.categories && filter.categories.includes(parameter.group || '')) {
        score += 3
      }

      // 类型匹配
      if (filter.types && filter.types.includes(parameter.type)) {
        score += 2
      }

      // 高级参数匹配
      if (filter.advanced !== undefined && parameter.advanced === filter.advanced) {
        score += 1
      }

      // 修改状态匹配
      if (filter.modified !== undefined && parameter.modified === filter.modified) {
        score += 1
      }

      // 错误状态匹配
      if (filter.hasError !== undefined && (parameter.error ? true : false) === filter.hasError) {
        score += 1
      }

      if (score > 0) {
        results.push({
          parameter,
          score,
          matches
        })
      }
    })

    return results.sort((a, b) => b.score - a.score)
  }

  /**
   * 高亮文本
   */
  private highlightText(text: string, query: string): string {
    if (!query) return text
    const regex = new RegExp(`(${query})`, 'gi')
    return text.replace(regex, '<mark>$1</mark>')
  }

  /**
   * 批量操作
   */
  async batchOperation(operation: ParameterBatchOperation): Promise<ParameterBatchResult> {
    const results: Array<{ parameter: string; success: boolean; error?: string }> = []
    let processed = 0
    let failed = 0

    for (const parameterName of operation.parameters) {
      try {
        const parameter = this.parameters.value.find(p => p.name === parameterName)
        if (!parameter) {
          results.push({
            parameter: parameterName,
            success: false,
            error: '参数不存在'
          })
          failed++
          continue
        }

        switch (operation.type) {
          case 'set':
            if (operation.values && operation.values[parameterName] !== undefined) {
              this.setParameterValue(parameterName, operation.values[parameterName])
            }
            break
          case 'reset':
            this.setParameterValue(parameterName, parameter.defaultValue)
            break
          case 'validate':
            if (this.settings.enableValidation) {
              this.validateParameter(parameter)
            }
            break
        }

        results.push({
          parameter: parameterName,
          success: true
        })
        processed++
      } catch (error) {
        results.push({
          parameter: parameterName,
          success: false,
          error: error instanceof Error ? error.message : '未知错误'
        })
        failed++
      }
    }

    const batchResult: ParameterBatchResult = {
      operation,
      success: failed === 0,
      processed,
      failed,
      results,
      summary: {
        totalParameters: operation.parameters.length,
        successfulOperations: processed,
        failedOperations: failed,
        duration: 0 // 这里应该计算实际耗时
      }
    }

    this.emit('batch-operation', { operation, result: batchResult })
    return batchResult
  }

  /**
   * 导出参数
   */
  exportParameters(format: string = 'json'): ParameterExport {
    const exportData: ParameterExport = {
      format: format as any,
      parameters: this.parameters.value,
      metadata: {
        exportedAt: new Date().toISOString(),
        exportedBy: 'User',
        version: '1.0.0',
        description: '混合参数配置导出',
        tags: ['export', 'parameters']
      }
    }

    return exportData
  }

  /**
   * 导入参数
   */
  async importParameters(data: any, format: string = 'json'): Promise<ParameterImportResult> {
    const result: ParameterImportResult = {
      success: true,
      imported: 0,
      skipped: 0,
      errors: [],
      warnings: [],
      metadata: {
        importedAt: new Date().toISOString(),
        source: 'user_import',
        version: '1.0.0'
      }
    }

    try {
      const importedParameters = Array.isArray(data) ? data : data.parameters || []
      
      for (const importedParam of importedParameters) {
        const existingParam = this.parameters.value.find(p => p.name === importedParam.name)
        
        if (existingParam) {
          const oldValue = existingParam.value
          existingParam.value = importedParam.value
          existingParam.modified = importedParam.value !== existingParam.defaultValue
          
          if (this.settings.enableHistory) {
            this.addToHistory(existingParam.name, oldValue, importedParam.value, 'user', '导入参数')
          }
          
          result.imported++
        } else {
          result.skipped++
          result.warnings.push(`参数 ${importedParam.name} 不存在，已跳过`)
        }
      }

      this.updateValidationResults()
    } catch (error) {
      result.success = false
      result.errors.push({
        parameter: 'import',
        message: error instanceof Error ? error.message : '导入失败',
        severity: 'error'
      })
    }

    return result
  }

  /**
   * 设置配置模式
   */
  setConfigMode(mode: 'ai' | 'manual' | 'hybrid'): void {
    const oldMode = this.state.mode
    this.state.mode = mode
    
    this.emit('mode-changed', { oldMode, newMode: mode })
  }

  /**
   * 切换自动模式
   */
  toggleAutoMode(): void {
    this.state.autoMode = !this.state.autoMode
  }

  /**
   * 切换高级参数显示
   */
  toggleAdvancedParameters(): void {
    this.state.showAdvanced = !this.state.showAdvanced
  }

  /**
   * 切换验证显示
   */
  toggleValidationDisplay(): void {
    this.state.showValidation = !this.state.showValidation
  }

  /**
   * 重置所有参数
   */
  resetAllParameters(): void {
    this.parameters.value.forEach(parameter => {
      const oldValue = parameter.value
      parameter.value = parameter.defaultValue
      parameter.modified = false
      parameter.error = null

      if (this.settings.enableHistory) {
        this.addToHistory(parameter.name, oldValue, parameter.defaultValue, 'user', '重置参数')
      }
    })

    this.updateValidationResults()
  }

  /**
   * 获取状态
   */
  getState(): ParameterConfigState {
    return { ...this.state }
  }

  /**
   * 获取设置
   */
  getSettings(): ParameterConfigSettings {
    return { ...this.settings }
  }

  /**
   * 更新设置
   */
  updateSettings(newSettings: Partial<ParameterConfigSettings>): void {
    Object.assign(this.settings, newSettings)
  }

  /**
   * 获取参数
   */
  getParameters(): Parameter[] {
    return [...this.parameters.value]
  }

  /**
   * 获取分类
   */
  getCategories(): ParameterCategory[] {
    return [...this.categories.value]
  }

  /**
   * 获取模板
   */
  getTemplates(): ParameterTemplate[] {
    return [...this.templates.value]
  }

  /**
   * 获取预设
   */
  getPresets(): ParameterPreset[] {
    return [...this.presets.value]
  }

  /**
   * 获取统计信息
   */
  getStatistics(): ParameterConfigStats {
    return this.statistics.value
  }

  // 事件发射器方法
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(callback)
  }

  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(event: string, data?: any): void {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.forEach(callback => callback(data))
    }
  }
}

// 创建单例实例
export const hybridParameterConfigService = new HybridParameterConfigService()