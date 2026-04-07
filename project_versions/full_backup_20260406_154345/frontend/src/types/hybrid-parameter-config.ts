/**
 * 混合参数配置类型定义
 */

// 参数类型枚举
export enum ParameterType {
  NUMBER = 'number',
  RANGE = 'range',
  TEXT = 'text',
  SELECT = 'select',
  BOOLEAN = 'boolean',
  DATE = 'date',
  COLOR = 'color',
  FILE = 'file',
  ARRAY = 'array',
  OBJECT = 'object'
}

// 参数验证规则接口
export interface ParameterValidation {
  required?: boolean
  min?: number
  max?: number
  step?: number
  pattern?: string
  minLength?: number
  maxLength?: number
  custom?: (value: any) => boolean | string
}

// 参数选项接口
export interface ParameterOption {
  label: string
  value: any
  description?: string
  icon?: string
  disabled?: boolean
}

// 参数建议接口
export interface ParameterSuggestion {
  value: string
  label?: string
  description?: string
  icon?: string
}

// 参数接口
export interface Parameter {
  name: string
  displayName: string
  type: ParameterType
  value: any
  defaultValue?: any
  validation?: ParameterValidation
  options?: ParameterOption[]
  suggestions?: ParameterSuggestion[]
  placeholder?: string
  description: string
  hint?: string
  group?: string
  order?: number
  advanced?: boolean
  hidden?: boolean
  disabled?: boolean
  error?: string | null
  modified?: boolean
  category?: string
}

// AI推荐接口
export interface AIRecommendation {
  id: string
  title: string
  description: string
  confidence: number
  parameters: Parameter[]
  reasoning?: string
  pros?: string[]
  cons?: string[]
  useCases?: string[]
  tags?: string[]
  createdAt: string
  version: string
}

// 参数分类接口
export interface ParameterCategory {
  id: string
  name: string
  description: string
  icon: string
  order: number
  parameters: Parameter[]
  collapsible?: boolean
  defaultExpanded?: boolean
}

// 参数模板接口
export interface ParameterTemplate {
  id: string
  name: string
  description: string
  category: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  tags: string[]
  parameters: Parameter[]
  createdAt: string
  updatedAt: string
  author?: string
  version?: string
  isPublic?: boolean
  usageCount?: number
  rating?: number
}

// 参数配置模式接口
export interface ParameterConfigMode {
  id: string
  name: string
  icon: string
  description: string
  features: string[]
  supportedParameters: string[]
}

// 参数同步状态接口
export interface ParameterSyncStatus {
  lastSync: string
  syncInProgress: boolean
  conflicts: Array<{
    parameterName: string
    localValue: any
    remoteValue: any
    resolution: 'local' | 'remote' | 'merge'
  }>
}

// 参数历史记录接口
export interface ParameterHistory {
  id: string
  parameterName: string
  oldValue: any
  newValue: any
  changedAt: string
  changedBy: 'user' | 'ai' | 'system'
  reason?: string
  context?: {
    mode: string
    recommendationId?: string
    templateId?: string
  }
}

// 参数比较结果接口
export interface ParameterComparison {
  parameter: string
  localValue: any
  remoteValue: any
  differences: Array<{
    type: 'value' | 'validation' | 'metadata'
    description: string
    severity: 'low' | 'medium' | 'high'
  }>
  recommendation: 'keep_local' | 'use_remote' | 'merge'
}

// 参数导入/导出接口
export interface ParameterExport {
  format: 'json' | 'yaml' | 'xml' | 'csv' | 'excel'
  parameters: Parameter[]
  metadata: {
    exportedAt: string
    exportedBy: string
    version: string
    description?: string
    tags?: string[]
  }
}

// 参数导入结果接口
export interface ParameterImportResult {
  success: boolean
  imported: number
  skipped: number
  errors: Array<{
    parameter: string
    message: string
    severity: 'error' | 'warning'
  }>
  warnings: string[]
  metadata?: {
    importedAt: string
    source: string
    version: string
  }
}

// 参数验证结果接口
export interface ParameterValidationResult {
  isValid: boolean
  errors: Array<{
    parameter: string
    message: string
    type: 'required' | 'format' | 'range' | 'custom'
    severity: 'error' | 'warning'
  }>
  warnings: Array<{
    parameter: string
    message: string
    type: 'suggestion' | 'deprecation'
  }>
}

// 参数搜索过滤器接口
export interface ParameterSearchFilter {
  query?: string
  categories?: string[]
  types?: ParameterType[]
  advanced?: boolean
  modified?: boolean
  hasError?: boolean
  tags?: string[]
}

// 参数搜索结果接口
export interface ParameterSearchResult {
  parameter: Parameter
  score: number
  matches: Array<{
    field: string
    value: string
    highlight: string
  }>
}

// 参数批量操作接口
export interface ParameterBatchOperation {
  type: 'set' | 'reset' | 'validate' | 'export' | 'import'
  parameters: string[]
  values?: Record<string, any>
  options?: {
    preserveValidation?: boolean
    skipHidden?: boolean
    includeMetadata?: boolean
  }
}

// 参数批量操作结果接口
export interface ParameterBatchResult {
  operation: ParameterBatchOperation
  success: boolean
  processed: number
  failed: number
  results: Array<{
    parameter: string
    success: boolean
    error?: string
  }>
  summary: {
    totalParameters: number
    successfulOperations: number
    failedOperations: number
    duration: number
  }
}

// 参数依赖关系接口
export interface ParameterDependency {
  source: string
  target: string
  type: 'value' | 'visibility' | 'enablement' | 'validation'
  condition: {
    operator: 'equals' | 'not_equals' | 'greater_than' | 'less_than' | 'contains' | 'not_contains'
    value: any
  }
  action: {
    type: 'set' | 'hide' | 'disable' | 'validate'
    value?: any
  }
}

// 参数条件接口
export interface ParameterCondition {
  id: string
  name: string
  description: string
  expression: string
  parameters: string[]
  isActive: boolean
  priority: number
}

// 参数组接口
export interface ParameterGroup {
  id: string
  name: string
  description: string
  icon: string
  order: number
  parameters: string[]
  layout: 'vertical' | 'horizontal' | 'grid'
  collapsible?: boolean
  defaultExpanded?: boolean
  border?: boolean
  backgroundColor?: string
}

// 参数预设接口
export interface ParameterPreset {
  id: string
  name: string
  description: string
  category: string
  tags: string[]
  parameters: Array<{
    name: string
    value: any
  overridden?: boolean
  }>
  isDefault?: boolean
  isReadOnly?: boolean
  createdAt: string
  updatedAt: string
  author?: string
  usageCount?: number
  rating?: number
}

// 参数配置状态接口
export interface ParameterConfigState {
  mode: 'ai' | 'manual' | 'hybrid'
  autoMode: boolean
  showAdvanced: boolean
  showValidation: boolean
  selectedRecommendations: string[]
  appliedRecommendations: string[]
  expandedCategories: string[]
  searchQuery: string
  activeFilters: ParameterSearchFilter
  validationResults: ParameterValidationResult
  syncStatus: ParameterSyncStatus
  history: ParameterHistory[]
  clipboard: {
    parameters: Parameter[]
    copiedAt: string
  }
}

// 参数配置事件接口
export interface ParameterConfigEvents {
  'parameter-changed': { parameter: string; oldValue: any; newValue: any }
  'parameter-validated': { parameter: string; result: ParameterValidationResult }
  'mode-changed': { oldMode: string; newMode: string }
  'recommendation-selected': { recommendationId: string; parameters: Parameter[] }
  'recommendation-applied': { recommendationId: string; parameters: Parameter[] }
  'template-loaded': { templateId: string; parameters: Parameter[] }
  'template-saved': { templateId: string; parameters: Parameter[] }
  'sync-started': { parameters: string[] }
  'sync-completed': { result: ParameterSyncStatus }
  'batch-operation': { operation: ParameterBatchOperation; result: ParameterBatchResult }
  'search-performed': { query: string; results: ParameterSearchResult[] }
  'filter-applied': { filter: ParameterSearchFilter; results: Parameter[] }
}

// 参数配置统计接口
export interface ParameterConfigStats {
  totalParameters: number
  visibleParameters: number
  modifiedParameters: number
  invalidParameters: number
  filledParameters: number
  completionRate: number
  mostUsedParameters: Array<{
    name: string
    usageCount: number
    lastUsed: string
  }>
  categoryDistribution: Array<{
    category: string
    count: number
    percentage: number
  }>
  validationSummary: {
    valid: number
    warnings: number
    errors: number
  }
}

// 参数配置设置接口
export interface ParameterConfigSettings {
  autoSave: boolean
  autoSaveInterval: number
  enableValidation: boolean
  validationMode: 'realtime' | 'on_change' | 'on_submit'
  enableHistory: boolean
  historyLimit: number
  enableSync: boolean
  syncInterval: number
  enableSuggestions: boolean
  suggestionMode: 'auto' | 'manual'
  enableAdvancedMode: boolean
  defaultViewMode: 'simple' | 'advanced' | 'expert'
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US'
  exportFormat: 'json' | 'yaml' | 'xml'
  showHiddenParameters: boolean
  enableBatchOperations: boolean
  enableParameterGroups: boolean
  enableParameterDependencies: boolean
}

// 参数配置错误类型
export enum ParameterConfigError {
  VALIDATION_ERROR = 'validation_error',
  SYNC_ERROR = 'sync_error',
  IMPORT_ERROR = 'import_error',
  EXPORT_ERROR = 'export_error',
  NETWORK_ERROR = 'network_error',
  PERMISSION_ERROR = 'permission_error',
  TEMPLATE_ERROR = 'template_error',
  BATCH_OPERATION_ERROR = 'batch_operation_error',
  SEARCH_ERROR = 'search_error',
  FILTER_ERROR = 'filter_error'
}

// 参数配置错误详情接口
export interface ParameterConfigErrorDetails {
  type: ParameterConfigError
  message: string
  details?: any
  timestamp: string
  parameter?: string
  context?: {
    mode?: string
    operation?: string
    recommendationId?: string
    templateId?: string
  }
}