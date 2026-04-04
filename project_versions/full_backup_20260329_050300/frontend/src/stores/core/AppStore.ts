/**
 * MyQuant v10.0.0 - Unified Application Store
 * 统一应用状态管理 - M2-17重构
 *
 * 合并来源：
 * - app.ts (应用全局状态)
 * - state.ts (功能状态、导航历史)
 * - theme.ts (主题系统)
 *
 * 职责：
 * - 应用配置（主题、语言、侧边栏）
 * - 功能状态管理（功能、层级、导航历史）
 * - 通知系统
 * - 加载状态
 *
 * @author Claude (M2-17 Store重构)
 * @created 2026-02-04
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

// ========== 类型定义 ==========

// 主题模式
export type ThemeMode = 'light' | 'dark' | 'auto'
export type PrimaryColor = 'purple' | 'blue' | 'green' | 'orange' | 'red'

// 主题颜色接口
export interface ThemeColors {
  // 主色调
  primary: string
  primaryHover: string
  primaryLight: string
  secondary: string

  // 涨跌颜色
  up: string
  down: string
  flat: string

  // 背景色
  bgDeep: string
  bgSurface: string
  bgElevated: string
  bgHover: string

  // 文字色
  textPrimary: string
  textSecondary: string
  textMuted: string
  textDisabled: string

  // 边框色
  borderLight: string
  borderMedium: string
  borderDark: string
}

// 通知接口
export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  read: boolean
  timestamp: string
}

// 层级状态接口
interface LayerState {
  functionId: string
  layer: number
  timestamp: number
  data: any
}

// 功能状态接口
interface FunctionState {
  functionId: string
  layers: Record<number, LayerState>
  lastAccessed: number
}

// 全局状态接口
interface GlobalState {
  currentFunction?: string
  currentLayer?: number
  navigationHistory: Array<{
    functionId: string
    layer: number
    timestamp: number
  }>
  userPreferences: {
    autoSave: boolean
    saveInterval: number
    maxHistorySize: number
  }
}

// 用户偏好接口
interface UserPreferences {
  theme: ThemeMode
  language: 'zh' | 'en'
  autoSave: boolean
  notifications: {
    enabled: boolean
    types: string[]
  }
}

// ========== 常量定义 ==========

// 预设颜色
export const PRESET_COLORS: Record<PrimaryColor, { primary: string; secondary: string }> = {
  purple: { primary: '#8b5cf6', secondary: '#3b82f6' },
  blue: { primary: '#3b82f6', secondary: '#06b6d4' },
  green: { primary: '#10b981', secondary: '#06b6d4' },
  orange: { primary: '#f59e0b', secondary: '#ef4444' },
  red: { primary: '#ef4444', secondary: '#f59e0b' }
}

// 浅色主题
const LIGHT_THEME: ThemeColors = {
  primary: '#8b5cf6',
  primaryHover: '#7c3aed',
  primaryLight: '#a78bfa',
  secondary: '#3b82f6',

  up: '#ef4444',
  down: '#10b981',
  flat: '#94a3b8',

  bgDeep: '#f8fafc',
  bgSurface: '#ffffff',
  bgElevated: '#f1f5f9',
  bgHover: '#e2e8f0',

  textPrimary: '#0f172a',
  textSecondary: '#475569',
  textMuted: '#94a3b8',
  textDisabled: '#cbd5e1',

  borderLight: 'rgba(0, 0, 0, 0.06)',
  borderMedium: 'rgba(0, 0, 0, 0.12)',
  borderDark: 'rgba(0, 0, 0, 0.18)'
}

// 深色主题
const DARK_THEME: ThemeColors = {
  primary: '#8b5cf6',
  primaryHover: '#7c3aed',
  primaryLight: '#a78bfa',
  secondary: '#3b82f6',

  up: '#ef4444',
  down: '#10b981',
  flat: '#94a3b8',

  bgDeep: '#0a0a0f',
  bgSurface: '#1a1a2e',
  bgElevated: '#252530',
  bgHover: '#2d2d3a',

  textPrimary: '#f8fafc',
  textSecondary: '#cbd5e1',
  textMuted: '#94a3b8',
  textDisabled: '#64748b',

  borderLight: 'rgba(255, 255, 255, 0.06)',
  borderMedium: 'rgba(255, 255, 255, 0.12)',
  borderDark: 'rgba(255, 255, 255, 0.18)'
}

// ========== Store定义 ==========

export const useAppStore = defineStore('app', () => {
  // ========== 状态 ==========

  // 主题状态
  const themeMode = ref<ThemeMode>('dark')
  const primaryColor = ref<PrimaryColor>('purple')
  const compactMode = ref(false)
  const animationEnabled = ref(true)
  const reducedMotion = ref(false)

  // 应用配置
  const language = ref<'zh' | 'en'>(localStorage.getItem('language') as 'zh' | 'en' || 'zh')
  const sidebarCollapsed = ref(false)
  const currentFunction = ref<string | null>(null)
  const loading = ref(false)

  // 通知系统
  const notifications = ref<Notification[]>([])

  // 功能状态管理
  const functionStates = ref<Map<string, FunctionState>>(new Map())
  const globalState = ref<GlobalState>({
    navigationHistory: [],
    userPreferences: {
      autoSave: true,
      saveInterval: 30000, // 30秒
      maxHistorySize: 50
    }
  })

  // 自动保存定时器
  let autoSaveTimer: number | null = null

  // ========== 计算属性 ==========

  /**
   * 当前实际主题模式（处理auto模式）
   */
  const currentThemeMode = computed<'light' | 'dark'>(() => {
    if (themeMode.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return themeMode.value
  })

  /**
   * 是否为暗色模式
   */
  const isDarkTheme = computed(() => currentThemeMode.value === 'dark')

  /**
   * 当前主题颜色
   */
  const themeColors = computed<ThemeColors>(() => {
    const baseColors = currentThemeMode.value === 'dark' ? DARK_THEME : LIGHT_THEME
    const preset = PRESET_COLORS[primaryColor.value]

    return {
      ...baseColors,
      primary: preset.primary,
      secondary: preset.secondary
    }
  })

  /**
   * CSS变量对象
   */
  const cssVars = computed<Record<string, string>>(() => {
    return {
      '--color-primary': themeColors.value.primary,
      '--color-primary-hover': themeColors.value.primaryHover,
      '--color-primary-light': themeColors.value.primaryLight,
      '--color-secondary': themeColors.value.secondary,
      '--color-up': themeColors.value.up,
      '--color-down': themeColors.value.down,
      '--color-flat': themeColors.value.flat,
      '--bg-deep': themeColors.value.bgDeep,
      '--bg-surface': themeColors.value.bgSurface,
      '--bg-elevated': themeColors.value.bgElevated,
      '--bg-hover': themeColors.value.bgHover,
      '--text-primary': themeColors.value.textPrimary,
      '--text-secondary': themeColors.value.textSecondary,
      '--text-muted': themeColors.value.textMuted,
      '--text-disabled': themeColors.value.textDisabled,
      '--border-light': themeColors.value.borderLight,
      '--border-medium': themeColors.value.borderMedium,
      '--border-dark': themeColors.value.borderDark
    }
  })

  /**
   * 是否有未读通知
   */
  const hasUnreadNotifications = computed(() =>
    notifications.value.some(n => !n.read)
  )

  /**
   * 当前功能状态
   */
  const currentFunctionState = computed(() => {
    if (!globalState.value.currentFunction) return null
    return functionStates.value.get(globalState.value.currentFunction)
  })

  /**
   * 导航历史
   */
  const navigationHistory = computed(() => globalState.value.navigationHistory)

  /**
   * 是否可以后退
   */
  const canGoBack = computed(() => navigationHistory.value.length > 1)

  // ========== 主题操作 ==========

  /**
   * 设置主题模式
   */
  const setThemeMode = (mode: ThemeMode) => {
    themeMode.value = mode
    saveTheme()
  }

  /**
   * 切换主题模式
   */
  const toggleThemeMode = () => {
    const modes: ThemeMode[] = ['light', 'dark', 'auto']
    const currentIndex = modes.indexOf(themeMode.value)
    themeMode.value = modes[(currentIndex + 1) % modes.length]
    saveTheme()
  }

  /**
   * 设置主色调
   */
  const setPrimaryColor = (color: PrimaryColor) => {
    primaryColor.value = color
    saveTheme()
  }

  /**
   * 切换紧凑模式
   */
  const toggleCompactMode = () => {
    compactMode.value = !compactMode.value
    saveTheme()
  }

  /**
   * 切换动画
   */
  const toggleAnimation = () => {
    animationEnabled.value = !animationEnabled.value
    saveTheme()
  }

  /**
   * 切换减少动效
   */
  const toggleReducedMotion = () => {
    reducedMotion.value = !reducedMotion.value
    saveTheme()
  }

  /**
   * 应用主题到DOM
   */
  const applyTheme = () => {
    const root = document.documentElement

    // 设置主题模式
    root.classList.remove('light', 'dark')
    root.classList.add(currentThemeMode.value)

    // 设置紧凑模式
    root.classList.toggle('compact', compactMode.value)

    // 设置动画
    root.classList.toggle('no-animation', !animationEnabled.value)
    root.classList.toggle('reduced-motion', reducedMotion.value)

    // 设置CSS变量
    Object.entries(cssVars.value).forEach(([key, value]) => {
      root.style.setProperty(key, value)
    })

    // 设置Element Plus主题
    if (currentThemeMode.value === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }

  /**
   * 保存主题到本地存储
   */
  const saveTheme = () => {
    try {
      const themeData = {
        mode: themeMode.value,
        primaryColor: primaryColor.value,
        compactMode: compactMode.value,
        animationEnabled: animationEnabled.value,
        reducedMotion: reducedMotion.value
      }
      localStorage.setItem('myquant_theme', JSON.stringify(themeData))
    } catch (e) {
      console.error('保存主题失败:', e)
    }
  }

  /**
   * 从本地存储加载主题
   */
  const loadTheme = () => {
    try {
      const saved = localStorage.getItem('myquant_theme')
      if (saved) {
        const themeData = JSON.parse(saved)
        themeMode.value = themeData.mode || 'dark'
        primaryColor.value = themeData.primaryColor || 'purple'
        compactMode.value = themeData.compactMode || false
        animationEnabled.value = themeData.animationEnabled !== false
        reducedMotion.value = themeData.reducedMotion || false
      }
    } catch (e) {
      console.error('加载主题失败:', e)
    }
  }

  /**
   * 重置主题
   */
  const resetTheme = () => {
    themeMode.value = 'dark'
    primaryColor.value = 'purple'
    compactMode.value = false
    animationEnabled.value = true
    reducedMotion.value = false
    saveTheme()
  }

  // ========== 应用配置操作 ==========

  /**
   * 设置语言
   */
  const setLanguage = (newLanguage: 'zh' | 'en') => {
    language.value = newLanguage
    localStorage.setItem('language', newLanguage)
  }

  /**
   * 切换侧边栏
   */
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed.value))
  }

  /**
   * 设置当前功能
   */
  const setCurrentFunction = (functionId: string | null) => {
    currentFunction.value = functionId
  }

  /**
   * 设置加载状态
   */
  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  // ========== 通知操作 ==========

  /**
   * 添加通知
   */
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date().toISOString()
    }
    notifications.value.unshift(newNotification)
  }

  /**
   * 标记通知为已读
   */
  const markNotificationAsRead = (id: string) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  }

  /**
   * 移除通知
   */
  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * 清空所有通知
   */
  const clearNotifications = () => {
    notifications.value = []
  }

  // ========== 功能状态操作 ==========

  /**
   * 初始化功能状态
   */
  const initializeFunctionState = (functionId: string) => {
    if (!functionStates.value.has(functionId)) {
      functionStates.value.set(functionId, {
        functionId,
        layers: {},
        lastAccessed: Date.now()
      })
    }

    globalState.value.currentFunction = functionId
    startAutoSave()
  }

  /**
   * 保存层级状态
   */
  const saveLayerState = (functionId: string, layer: number, state: LayerState) => {
    const functionState = functionStates.value.get(functionId)
    if (!functionState) {
      initializeFunctionState(functionId)
    }

    const updatedFunctionState = functionStates.value.get(functionId)!
    updatedFunctionState.layers[layer] = state
    updatedFunctionState.lastAccessed = Date.now()

    globalState.value.currentLayer = layer
    addToNavigationHistory(functionId, layer)
    persistToStorage()
  }

  /**
   * 获取层级状态
   */
  const getLayerState = (functionId: string, layer: number): LayerState | null => {
    const functionState = functionStates.value.get(functionId)
    if (!functionState) return null

    return functionState.layers[layer] || null
  }

  /**
   * 清除层级状态
   */
  const clearLayerState = (functionId: string, layer: number) => {
    const functionState = functionStates.value.get(functionId)
    if (!functionState) return

    delete functionState.layers[layer]
    functionState.lastAccessed = Date.now()

    persistToStorage()
  }

  /**
   * 清除功能状态
   */
  const clearFunctionState = (functionId: string) => {
    functionStates.value.delete(functionId)

    if (globalState.value.currentFunction === functionId) {
      globalState.value.currentFunction = undefined
      globalState.value.currentLayer = undefined
    }

    persistToStorage()
  }

  /**
   * 添加到导航历史
   */
  const addToNavigationHistory = (functionId: string, layer: number) => {
    const historyEntry = {
      functionId,
      layer,
      timestamp: Date.now()
    }

    // 避免重复添加相同的条目
    const lastEntry = globalState.value.navigationHistory[globalState.value.navigationHistory.length - 1]
    if (lastEntry && lastEntry.functionId === functionId && lastEntry.layer === layer) {
      return
    }

    globalState.value.navigationHistory.push(historyEntry)

    // 限制历史记录大小
    if (globalState.value.navigationHistory.length > globalState.value.userPreferences.maxHistorySize) {
      globalState.value.navigationHistory.shift()
    }
  }

  /**
   * 导航后退
   */
  const goBack = () => {
    if (!canGoBack.value) return null

    const history = globalState.value.navigationHistory
    if (history.length <= 1) return null

    // 移除当前条目
    history.pop()

    // 获取上一个条目
    const previousEntry = history[history.length - 1]
    if (previousEntry) {
      globalState.value.currentFunction = previousEntry.functionId
      globalState.value.currentLayer = previousEntry.layer

      return previousEntry
    }

    return null
  }

  /**
   * 更新用户偏好
   */
  const updateUserPreferences = (preferences: Partial<GlobalState['userPreferences']>) => {
    globalState.value.userPreferences = {
      ...globalState.value.userPreferences,
      ...preferences
    }

    if (autoSaveTimer) {
      clearInterval(autoSaveTimer)
    }

    if (globalState.value.userPreferences.autoSave) {
      startAutoSave()
    }

    persistToStorage()
  }

  /**
   * 启动自动保存
   */
  const startAutoSave = () => {
    if (!globalState.value.userPreferences.autoSave) return

    if (autoSaveTimer) {
      clearInterval(autoSaveTimer)
    }

    autoSaveTimer = setInterval(() => {
      persistToStorage()
    }, globalState.value.userPreferences.saveInterval) as unknown as number
  }

  /**
   * 停止自动保存
   */
  const stopAutoSave = () => {
    if (autoSaveTimer) {
      clearInterval(autoSaveTimer)
      autoSaveTimer = null
    }
  }

  /**
   * 持久化到localStorage
   */
  const persistToStorage = () => {
    try {
      const storageData = {
        functionStates: Array.from(functionStates.value.entries()),
        globalState: globalState.value,
        timestamp: Date.now()
      }

      localStorage.setItem('myquant_app_state', JSON.stringify(storageData))
    } catch (error) {
      console.warn('Failed to persist state to localStorage:', error)
    }
  }

  /**
   * 从localStorage恢复
   */
  const restoreFromStorage = () => {
    try {
      const storedData = localStorage.getItem('myquant_app_state')
      if (!storedData) return

      const storageData = JSON.parse(storedData)

      // 恢复功能状态
      if (storageData.functionStates) {
        functionStates.value = new Map(storageData.functionStates)
      }

      // 恢复全局状态
      if (storageData.globalState) {
        globalState.value = {
          ...globalState.value,
          ...storageData.globalState
        }
      }

      console.log('[AppStore] State restored from localStorage:', {
        functionCount: functionStates.value.size,
        lastSaved: new Date(storageData.timestamp).toLocaleString()
      })
    } catch (error) {
      console.warn('Failed to restore state from localStorage:', error)
    }
  }

  /**
   * 清除所有状态
   */
  const clearAllStates = () => {
    functionStates.value.clear()
    globalState.value.navigationHistory = []
    globalState.value.currentFunction = undefined
    globalState.value.currentLayer = undefined

    localStorage.removeItem('myquant_app_state')
  }

  /**
   * 获取状态统计信息
   */
  const getStateStats = () => {
    const stats = {
      totalFunctions: functionStates.value.size,
      totalLayers: 0,
      oldestState: null as Date | null,
      newestState: null as Date | null,
      memoryUsage: 0
    }

    let oldestTimestamp = Date.now()
    let newestTimestamp = 0

    functionStates.value.forEach((functionState) => {
      stats.totalLayers += Object.keys(functionState.layers).length

      if (functionState.lastAccessed < oldestTimestamp) {
        oldestTimestamp = functionState.lastAccessed
      }

      if (functionState.lastAccessed > newestTimestamp) {
        newestTimestamp = functionState.lastAccessed
      }

      // 估算内存使用
      stats.memoryUsage += JSON.stringify(functionState).length
    })

    stats.oldestState = new Date(oldestTimestamp)
    stats.newestState = new Date(newestTimestamp)
    stats.memoryUsage = Math.round(stats.memoryUsage / 1024) // KB

    return stats
  }

  // ========== 初始化 ==========

  /**
   * 初始化应用
   */
  const initializeApp = () => {
    // 加载主题
    loadTheme()

    // 恢复状态
    restoreFromStorage()

    // 监听系统主题变化
    if (typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', () => {
        if (themeMode.value === 'auto') {
          applyTheme()
        }
      })

      // 监听系统减少动效偏好
      const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      reducedMotionQuery.addEventListener('change', (e) => {
        reducedMotion.value = e.matches
        applyTheme()
      })
    }

    // 应用主题
    applyTheme()
  }

  // ========== 监听变化 ==========

  // 监听主题变化并应用
  watch(
    [themeMode, primaryColor, compactMode, animationEnabled, reducedMotion],
    () => {
      applyTheme()
    },
    { deep: true, immediate: true }
  )

  return {
    // ========== 主题状态 ==========
    themeMode,
    primaryColor,
    compactMode,
    animationEnabled,
    reducedMotion,
    currentThemeMode,
    isDarkTheme,
    themeColors,
    cssVars,

    // ========== 应用配置 ==========
    language,
    sidebarCollapsed,
    currentFunction,
    loading,

    // ========== 通知系统 ==========
    notifications,
    hasUnreadNotifications,

    // ========== 功能状态 ==========
    functionStates,
    globalState,
    currentFunctionState,
    navigationHistory,
    canGoBack,

    // ========== 主题操作 ==========
    setThemeMode,
    toggleThemeMode,
    setPrimaryColor,
    toggleCompactMode,
    toggleAnimation,
    toggleReducedMotion,
    applyTheme,
    resetTheme,

    // ========== 应用配置操作 ==========
    setLanguage,
    toggleSidebar,
    setCurrentFunction,
    setLoading,

    // ========== 通知操作 ==========
    addNotification,
    markNotificationAsRead,
    removeNotification,
    clearNotifications,

    // ========== 功能状态操作 ==========
    initializeFunctionState,
    saveLayerState,
    getLayerState,
    clearLayerState,
    clearFunctionState,
    goBack,
    updateUserPreferences,
    clearAllStates,
    getStateStats,

    // ========== 初始化 ==========
    initializeApp
  }
})
