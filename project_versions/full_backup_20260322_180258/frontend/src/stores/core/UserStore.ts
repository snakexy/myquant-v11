/**
 * MyQuant v10.0.0 - User Store (Unified)
 * 统一用户状态管理 - 合并 user.ts + userSettings.ts + ui.ts
 *
 * 功能模块:
 * - 用户资料和认证管理
 * - 用户偏好和设置管理
 * - UI状态管理（模态框、提示框、加载状态等）
 * - 指标参数管理
 * - 自定义板块管理
 * - 活动记录和配置保存
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { logger } from '@/utils/logger'

// ==================== 类型定义 ====================

/**
 * 用户资料
 */
export interface UserProfile {
  id: string
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'user' | 'analyst'
  createdAt: string
}

/**
 * 用户偏好
 */
export interface UserPreferences {
  theme: 'dark' | 'light'
  language: 'zh' | 'en'
  autoSave: boolean
  notifications: {
    enabled: boolean
    types: string[]
  }
}

/**
 * 指标参数类型
 */
export interface IndicatorParams {
  ma: {
    periods: number[]
    colors: string[]
  }
  boll: {
    period: number
    nbdevup: number
    nbdevdn: number
    colors: {
      upper: string
      middle: string
      lower: string
      fill: string
    }
  }
  macd: {
    fastperiod: number
    slowperiod: number
    signalperiod: number
    colors: {
      dif: string
      dea: string
      macdUp: string
      macdDown: string
    }
  }
  kdj: {
    fastk_period: number
    slowk_period: number
    slowd_period: number
    colors: {
      k: string
      d: string
      j: string
    }
  }
  rsi: {
    period: number
    overbought: number
    oversold: number
    colors: {
      line: string
      overbought: string
      oversold: string
    }
  }
}

/**
 * 用户设置
 */
export interface UserSettings {
  // 指标参数
  indicatorParams: IndicatorParams

  // 默认选中的指标
  defaultIndicators: {
    ma: boolean
    boll: boolean
    macd: boolean
    kdj: boolean
    rsi: boolean
    vol: boolean
  }

  // 自定义板块组合
  customSectors: Array<{
    id: string
    name: string
    stocks: string[]
    description?: string
    color?: string
  }>

  // 图表偏好
  chartPreferences: {
    defaultPeriod: string
    autoRefresh: boolean
    refreshInterval: number
    showGrid: boolean
    showVolume: boolean
    animationEnabled: boolean
  }

  // 主题设置
  theme: {
    mode: 'dark' | 'light'
    primaryColor: string
    accentColor: string
  }

  // 布局设置
  layout: {
    sidebarCollapsed: boolean
    toolbarPosition: 'top' | 'bottom'
  }
}

/**
 * 模态框状态
 */
export interface ModalState {
  id: string
  type: 'info' | 'warning' | 'error' | 'success' | 'confirm'
  title: string
  content: string
  showCloseButton?: boolean
  showCancelButton?: boolean
  confirmText?: string
  cancelText?: string
  onConfirm?: () => void
  onCancel?: () => void
  onClose?: () => void
}

/**
 * 提示框
 */
export interface Toast {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title?: string
  message: string
  duration?: number
  showClose?: boolean
  action?: {
    text: string
    handler: () => void
  }
}

/**
 * 活动记录
 */
export interface Activity {
  id: string
  type: 'strategy' | 'backtest' | 'data' | 'system'
  title: string
  description: string
  timestamp: string
}

/**
 * 保存的配置
 */
export interface SavedConfig {
  id: string
  name: string
  type: 'strategy' | 'backtest' | 'monitor'
  config: Record<string, any>
  createdAt: string
}

// ==================== 常量定义 ====================

/**
 * 默认指标参数
 */
export const defaultIndicatorParams: IndicatorParams = {
  ma: {
    periods: [5, 10, 20, 30, 60],
    colors: ['#fbbf24', '#3b82f6', '#a855f7', '#10b981', '#f59e0b']
  },
  boll: {
    period: 20,
    nbdevup: 2,
    nbdevdn: 2,
    colors: {
      upper: '#f59e0b',
      middle: '#ffffff',
      lower: '#f59e0b',
      fill: 'rgba(245, 158, 11, 0.1)'
    }
  },
  macd: {
    fastperiod: 12,
    slowperiod: 26,
    signalperiod: 9,
    colors: {
      dif: '#ffffff',
      dea: '#fbbf24',
      macdUp: '#ef4444',
      macdDown: '#10b981'
    }
  },
  kdj: {
    fastk_period: 9,
    slowk_period: 3,
    slowd_period: 3,
    colors: {
      k: '#ffffff',
      d: '#fbbf24',
      j: '#a855f7'
    }
  },
  rsi: {
    period: 14,
    overbought: 70,
    oversold: 30,
    colors: {
      line: '#3b82f6',
      overbought: '#ef4444',
      oversold: '#10b981'
    }
  }
}

/**
 * 默认用户设置
 */
const defaultSettings: UserSettings = {
  indicatorParams: JSON.parse(JSON.stringify(defaultIndicatorParams)),
  defaultIndicators: {
    ma: true,
    boll: false,
    macd: true,
    kdj: false,
    rsi: false,
    vol: true
  },
  customSectors: [],
  chartPreferences: {
    defaultPeriod: 'day',
    autoRefresh: true,
    refreshInterval: 3000, // 3秒
    showGrid: true,
    showVolume: true,
    animationEnabled: false
  },
  theme: {
    mode: 'dark',
    primaryColor: '#8b5cf6',
    accentColor: '#3b82f6'
  },
  layout: {
    sidebarCollapsed: false,
    toolbarPosition: 'top'
  }
}

/**
 * 默认用户偏好
 */
const defaultPreferences: UserPreferences = {
  theme: 'dark',
  language: 'zh',
  autoSave: true,
  notifications: {
    enabled: true,
    types: ['strategy', 'backtest', 'alert']
  }
}

// ==================== Store 定义 ====================

export const useUserStore = defineStore('user', () => {
  // ==================== 状态 ====================

  // 用户信息
  const profile = ref<UserProfile | null>(null)
  const isLoggedIn = ref(false)

  // 用户偏好
  const preferences = ref<UserPreferences>({ ...defaultPreferences })

  // 用户设置
  const settings = ref<UserSettings>({ ...defaultSettings })

  // UI状态
  const modals = ref<ModalState[]>([])
  const toasts = ref<Toast[]>([])
  const loadingStates = ref<Record<string, boolean>>({})
  const animationEnabled = ref(true)
  const sidebarCollapsed = ref(false)
  const layoutMode = ref<'default' | 'compact' | 'wide'>('default')

  // 活动和配置
  const recentActivities = ref<Activity[]>([])
  const savedConfigs = ref<SavedConfig[]>([])

  // 内部状态
  const isSettingsLoaded = ref(false)

  // ==================== 计算属性 ====================

  /**
   * 用户名
   */
  const userName = computed(() => profile.value?.name || '用户')

  /**
   * 用户角色
   */
  const userRole = computed(() => profile.value?.role || 'user')

  /**
   * 是否有活动模态框
   */
  const hasActiveModals = computed(() => modals.value.length > 0)

  /**
   * 是否有提示框
   */
  const hasToasts = computed(() => toasts.value.length > 0)

  /**
   * 是否有加载状态
   */
  const isAnyLoading = computed(() =>
    Object.values(loadingStates.value).some(state => state)
  )

  /**
   * 用户设置（响应式）
   */
  const userSettings = computed(() => settings.value)

  // ==================== 用户管理 ====================

  /**
   * 设置用户资料
   */
  const setProfile = (userProfile: UserProfile) => {
    profile.value = userProfile
    isLoggedIn.value = true
    localStorage.setItem('userProfile', JSON.stringify(userProfile))
    logger.info('用户资料已设置:', userProfile.name)
  }

  /**
   * 更新用户资料
   */
  const updateProfile = (updates: Partial<UserProfile>) => {
    if (profile.value) {
      profile.value = { ...profile.value, ...updates }
      localStorage.setItem('userProfile', JSON.stringify(profile.value))
      logger.info('用户资料已更新')
    }
  }

  /**
   * 用户登出
   */
  const logout = () => {
    profile.value = null
    isLoggedIn.value = false
    localStorage.removeItem('userProfile')
    logger.info('用户已登出')
  }

  /**
   * 设置用户偏好
   */
  const setPreferences = (newPreferences: Partial<UserPreferences>) => {
    preferences.value = { ...preferences.value, ...newPreferences }
    localStorage.setItem('userPreferences', JSON.stringify(preferences.value))
    logger.info('用户偏好已更新')
  }

  // ==================== UI管理 ====================

  /**
   * 打开模态框
   */
  const openModal = (modal: Omit<ModalState, 'id'>) => {
    const newModal: ModalState = {
      ...modal,
      id: Date.now().toString()
    }
    modals.value.push(newModal)
    return newModal.id
  }

  /**
   * 关闭模态框
   */
  const closeModal = (id: string) => {
    const index = modals.value.findIndex(m => m.id === id)
    if (index > -1) {
      const modal = modals.value[index]
      modals.value.splice(index, 1)
      if (modal.onClose) {
        modal.onClose()
      }
    }
  }

  /**
   * 关闭所有模态框
   */
  const closeAllModals = () => {
    modals.value.forEach(modal => {
      if (modal.onClose) {
        modal.onClose()
      }
    })
    modals.value = []
  }

  /**
   * 显示提示框
   */
  const showToast = (toast: Omit<Toast, 'id'>) => {
    const newToast: Toast = {
      ...toast,
      id: Date.now().toString()
    }
    toasts.value.push(newToast)

    // 自动移除toast
    if (toast.duration !== 0) {
      setTimeout(() => {
        removeToast(newToast.id)
      }, toast.duration || 3000)
    }

    return newToast.id
  }

  /**
   * 移除提示框
   */
  const removeToast = (id: string) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  /**
   * 清除所有提示框
   */
  const clearToasts = () => {
    toasts.value = []
  }

  /**
   * 设置加载状态
   */
  const setLoading = (key: string, isLoading: boolean) => {
    loadingStates.value[key] = isLoading
  }

  /**
   * 清除加载状态
   */
  const clearLoading = (key?: string) => {
    if (key) {
      delete loadingStates.value[key]
    } else {
      loadingStates.value = {}
    }
  }

  /**
   * 切换动画
   */
  const toggleAnimation = () => {
    animationEnabled.value = !animationEnabled.value
    localStorage.setItem('animationEnabled', animationEnabled.value.toString())
  }

  /**
   * 切换侧边栏
   */
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value.toString())
  }

  /**
   * 设置布局模式
   */
  const setLayoutMode = (mode: 'default' | 'compact' | 'wide') => {
    layoutMode.value = mode
    localStorage.setItem('layoutMode', mode)
  }

  // ==================== 设置管理 ====================

  /**
   * 加载用户设置
   */
  const loadUserSettings = (): UserSettings => {
    try {
      const stored = localStorage.getItem('myquant_user_settings')

      if (stored) {
        const parsed = JSON.parse(stored)
        // 合并默认设置（处理新增字段）
        settings.value = mergeDeep(defaultSettings, parsed)
        logger.info('用户设置已加载')
      } else {
        settings.value = { ...defaultSettings }
      }
    } catch (e) {
      logger.error('加载用户设置失败:', e)
      settings.value = { ...defaultSettings }
    }

    isSettingsLoaded.value = true
    return settings.value
  }

  /**
   * 保存用户设置
   */
  const saveUserSettings = (newSettings?: Partial<UserSettings>): void => {
    try {
      if (newSettings) {
        settings.value = mergeDeep(settings.value, newSettings)
      }

      localStorage.setItem('myquant_user_settings', JSON.stringify(settings.value))
      logger.info('用户设置已保存')
    } catch (e) {
      logger.error('保存用户设置失败:', e)
    }
  }

  /**
   * 重置用户设置
   */
  const resetUserSettings = (): void => {
    settings.value = { ...defaultSettings }
    saveUserSettings()
    logger.info('用户设置已重置')
  }

  /**
   * 导出设置
   */
  const exportSettings = (): string => {
    return JSON.stringify(settings.value, null, 2)
  }

  /**
   * 导入设置
   */
  const importSettings = (jsonString: string): boolean => {
    try {
      const imported = JSON.parse(jsonString)

      // 验证导入的设置
      if (typeof imported === 'object' && imported !== null) {
        settings.value = mergeDeep(defaultSettings, imported)
        saveUserSettings()
        logger.info('设置已导入')
        return true
      }

      return false
    } catch (e) {
      logger.error('导入设置失败:', e)
      return false
    }
  }

  /**
   * 深度合并对象
   */
  function mergeDeep(target: any, source: any): any {
    const output = { ...target }

    if (isObject(target) && isObject(source)) {
      Object.keys(source).forEach(key => {
        if (isObject(source[key])) {
          if (!(key in target)) {
            Object.assign(output, { [key]: source[key] })
          } else {
            output[key] = mergeDeep(target[key], source[key])
          }
        } else {
          Object.assign(output, { [key]: source[key] })
        }
      })
    }

    return output
  }

  function isObject(item: any): boolean {
    return item && typeof item === 'object' && !Array.isArray(item)
  }

  // ==================== 自定义板块管理 ====================

  /**
   * 自定义板块管理器
   */
  const customSectorManager = {
    /**
     * 添加自定义板块
     */
    add(sector: Omit<UserSettings['customSectors'][0], 'id'>): string {
      const id = `custom_${Date.now()}`

      settings.value.customSectors.push({
        ...sector,
        id
      })

      saveUserSettings()
      logger.info('自定义板块已添加:', sector.name)
      return id
    },

    /**
     * 更新自定义板块
     */
    update(id: string, data: Partial<UserSettings['customSectors'][0]>): boolean {
      const index = settings.value.customSectors.findIndex(s => s.id === id)

      if (index >= 0) {
        settings.value.customSectors[index] = {
          ...settings.value.customSectors[index],
          ...data
        }
        saveUserSettings()
        logger.info('自定义板块已更新:', id)
        return true
      }

      return false
    },

    /**
     * 删除自定义板块
     */
    delete(id: string): boolean {
      const index = settings.value.customSectors.findIndex(s => s.id === id)

      if (index >= 0) {
        settings.value.customSectors.splice(index, 1)
        saveUserSettings()
        logger.info('自定义板块已删除:', id)
        return true
      }

      return false
    },

    /**
     * 获取自定义板块
     */
    get(id: string): UserSettings['customSectors'][0] | undefined {
      return settings.value.customSectors.find(s => s.id === id)
    },

    /**
     * 获取所有自定义板块
     */
    getAll(): UserSettings['customSectors'] {
      return settings.value.customSectors
    }
  }

  // ==================== 指标参数管理 ====================

  /**
   * 指标参数管理器
   */
  const indicatorParamsManager = {
    /**
     * 更新指标参数
     */
    update(indicator: keyof UserSettings['indicatorParams'], params: any): void {
      settings.value.indicatorParams[indicator] = {
        ...settings.value.indicatorParams[indicator],
        ...params
      }

      saveUserSettings()
      logger.info('指标参数已更新:', indicator)
    },

    /**
     * 重置指标参数
     */
    reset(indicator?: keyof UserSettings['indicatorParams']): void {
      if (indicator) {
        settings.value.indicatorParams[indicator] = JSON.parse(
          JSON.stringify(defaultIndicatorParams[indicator])
        )
        logger.info('指标参数已重置:', indicator)
      } else {
        settings.value.indicatorParams = JSON.parse(JSON.stringify(defaultIndicatorParams))
        logger.info('所有指标参数已重置')
      }

      saveUserSettings()
    },

    /**
     * 获取指标参数
     */
    get(indicator: keyof UserSettings['indicatorParams']): any {
      return settings.value.indicatorParams[indicator]
    },

    /**
     * 获取所有指标参数
     */
    getAll(): UserSettings['indicatorParams'] {
      return settings.value.indicatorParams
    }
  }

  // ==================== 活动和配置管理 ====================

  /**
   * 添加活动记录
   */
  const addActivity = (activity: Omit<Activity, 'id' | 'timestamp'>) => {
    const newActivity: Activity = {
      ...activity,
      id: Date.now().toString(),
      timestamp: new Date().toISOString()
    }
    recentActivities.value.unshift(newActivity)

    // 只保留最近50条活动
    if (recentActivities.value.length > 50) {
      recentActivities.value = recentActivities.value.slice(0, 50)
    }

    logger.info('活动已添加:', activity.title)
  }

  /**
   * 保存配置
   */
  const saveConfig = (config: Omit<SavedConfig, 'id' | 'createdAt'>) => {
    const newConfig: SavedConfig = {
      ...config,
      id: Date.now().toString(),
      createdAt: new Date().toISOString()
    }
    savedConfigs.value.push(newConfig)
    localStorage.setItem('savedConfigs', JSON.stringify(savedConfigs.value))
    logger.info('配置已保存:', config.name)
  }

  /**
   * 删除配置
   */
  const deleteConfig = (id: string) => {
    const index = savedConfigs.value.findIndex(c => c.id === id)
    if (index > -1) {
      const config = savedConfigs.value[index]
      savedConfigs.value.splice(index, 1)
      localStorage.setItem('savedConfigs', JSON.stringify(savedConfigs.value))
      logger.info('配置已删除:', config.name)
    }
  }

  /**
   * 获取配置
   */
  const getConfig = (id: string): SavedConfig | undefined => {
    return savedConfigs.value.find(c => c.id === id)
  }

  /**
   * 获取所有配置
   */
  const getAllConfigs = (): SavedConfig[] => {
    return savedConfigs.value
  }

  // ==================== 初始化 ====================

  /**
   * 初始化用户数据
   */
  const initializeUser = () => {
    // 加载用户资料
    const savedProfile = localStorage.getItem('userProfile')
    if (savedProfile) {
      try {
        profile.value = JSON.parse(savedProfile)
        isLoggedIn.value = true
        logger.info('用户资料已加载')
      } catch (e) {
        logger.error('解析用户资料失败:', e)
      }
    }

    // 加载用户偏好
    const savedPreferences = localStorage.getItem('userPreferences')
    if (savedPreferences) {
      try {
        preferences.value = { ...preferences.value, ...JSON.parse(savedPreferences) }
        logger.info('用户偏好已加载')
      } catch (e) {
        logger.error('解析用户偏好失败:', e)
      }
    }

    // 加载保存的配置
    const savedConfigsData = localStorage.getItem('savedConfigs')
    if (savedConfigsData) {
      try {
        savedConfigs.value = JSON.parse(savedConfigsData)
        logger.info('保存的配置已加载')
      } catch (e) {
        logger.error('解析保存的配置失败:', e)
      }
    }

    // 加载用户设置
    loadUserSettings()

    // 加载UI状态
    const savedAnimation = localStorage.getItem('animationEnabled')
    if (savedAnimation !== null) {
      animationEnabled.value = savedAnimation === 'true'
    }

    const savedSidebar = localStorage.getItem('sidebarCollapsed')
    if (savedSidebar !== null) {
      sidebarCollapsed.value = savedSidebar === 'true'
    }

    const savedLayout = localStorage.getItem('layoutMode') as 'default' | 'compact' | 'wide'
    if (savedLayout) {
      layoutMode.value = savedLayout
    }

    logger.info('用户数据初始化完成')
  }

  /**
   * 重置所有数据
   */
  const resetAll = () => {
    // 清除用户数据
    profile.value = null
    isLoggedIn.value = false
    preferences.value = { ...defaultPreferences }
    recentActivities.value = []
    savedConfigs.value = []

    // 清除设置
    settings.value = { ...defaultSettings }

    // 清除UI状态
    modals.value = []
    toasts.value = []
    loadingStates.value = {}
    animationEnabled.value = true
    sidebarCollapsed.value = false
    layoutMode.value = 'default'

    // 清除localStorage
    localStorage.removeItem('userProfile')
    localStorage.removeItem('userPreferences')
    localStorage.removeItem('savedConfigs')
    localStorage.removeItem('myquant_user_settings')
    localStorage.removeItem('animationEnabled')
    localStorage.removeItem('sidebarCollapsed')
    localStorage.removeItem('layoutMode')

    logger.info('所有用户数据已重置')
  }

  // ==================== 监听器 ====================

  // 监听设置变化并自动保存
  watch(
    settings,
    () => {
      if (isSettingsLoaded.value) {
        saveUserSettings()
      }
    },
    { deep: true }
  )

  // 监听用户偏好变化并自动保存
  watch(
    preferences,
    () => {
      localStorage.setItem('userPreferences', JSON.stringify(preferences.value))
    },
    { deep: true }
  )

  // ==================== 返回值 ====================

  return {
    // 状态
    profile,
    isLoggedIn,
    preferences,
    settings,
    modals,
    toasts,
    loadingStates,
    animationEnabled,
    sidebarCollapsed,
    layoutMode,
    recentActivities,
    savedConfigs,

    // 计算属性
    userName,
    userRole,
    hasActiveModals,
    hasToasts,
    isAnyLoading,
    userSettings,

    // 用户管理
    setProfile,
    updateProfile,
    logout,
    setPreferences,

    // UI管理
    openModal,
    closeModal,
    closeAllModals,
    showToast,
    removeToast,
    clearToasts,
    setLoading,
    clearLoading,
    toggleAnimation,
    toggleSidebar,
    setLayoutMode,

    // 设置管理
    loadUserSettings,
    saveUserSettings,
    resetUserSettings,
    exportSettings,
    importSettings,
    customSectorManager,
    indicatorParamsManager,

    // 活动和配置管理
    addActivity,
    saveConfig,
    deleteConfig,
    getConfig,
    getAllConfigs,

    // 初始化和重置
    initializeUser,
    resetAll
  }
})

// ==================== 类型导出 ====================

export type {
  UserProfile,
  UserPreferences,
  UserSettings,
  IndicatorParams,
  ModalState,
  Toast,
  Activity,
  SavedConfig
}
