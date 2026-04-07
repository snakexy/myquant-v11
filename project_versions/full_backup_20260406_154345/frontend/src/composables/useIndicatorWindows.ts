/**
 * useIndicatorWindows - 技术指标窗口管理 Composable
 *
 * 提供独立分窗技术指标的管理功能：
 * - 添加/删除指标窗口
 * - 调整窗口高度
 * - 管理窗口布局
 * - 指标数据计算
 */

import { ref, computed, watch } from 'vue'
import { fetchKlineWithIndicators } from '@/api/modules/indicators'
import type { IChartApi, IChartSeriesApi } from 'lightweight-charts'

// 指标配置类型
export interface IndicatorConfig {
  id: string
  name: string
  type: 'main' | 'sub'  // main=主图叠加, sub=副图独立
  height: number
  visible: boolean
  params?: Record<string, any>
  chartInstance?: IChartApi
  seriesInstance?: IChartSeriesApi
}

// 主图指标类型
const MAIN_OVERLAY_INDICATORS = ['MA', 'BOLL', 'EMA', 'SMA', 'VWAP', 'SAR']

// 副图指标类型
const SUB_INDICATORS = ['MACD', 'KDJ', 'RSI', 'CCI', 'OBV', 'ATR', 'STOCH', 'STOCHRSI']

// 默认指标参数
const DEFAULT_INDICATOR_PARAMS = {
  MA: { periods: [5, 10, 20, 30, 60], color: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'] },
  BOLL: { period: 20, stdDev: 2, upperColor: 'rgba(250, 173, 20, 0.3)', lowerColor: 'rgba(250, 173, 20, 0.3)' },
  MACD: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9, histogramColor: '#26A69A' },
  KDJ: { fastKPeriod: 9, slowKPeriod: 3, slowDPeriod: 3, overbought: 80, oversold: 20 },
  RSI: { period: 14, overbought: 70, oversold: 30 },
  CCI: { period: 14, overbought: 100, oversold: -100 },
  OBV: {},
  ATR: { period: 14 }
}

export interface UseIndicatorWindowsOptions {
  symbol?: string
  period?: string
  count?: number
}

export interface UseIndicatorWindowsReturn {
  // 状态
  mainIndicators: typeof mainIndicators
  subIndicators: typeof subIndicators
  availableIndicators: typeof availableIndicators

  // 主图指标
  addMainIndicator: (indicator: string, params?: any) => void
  removeMainIndicator: (indicator: string) => void
  hasMainIndicator: (indicator: string) => boolean

  // 副图指标
  addSubIndicator: (indicator: string, params?: any) => void
  removeSubIndicator: (indicator: string) => void
  toggleSubIndicator: (indicator: string) => void
  updateSubIndicatorHeight: (indicator: string, height: number) => void

  // 数据计算
  calculateIndicators: (df: any) => Promise<any>
  refreshData: () => Promise<void>

  // 布局管理
  resetLayout: () => void
  saveLayout: () => void
  loadLayout: () => void
}

/**
 * 技术指标窗口管理 Composable
 */
export function useIndicatorWindows(
  options: UseIndicatorWindowsOptions = {}
): UseIndicatorWindowsReturn {
  const { symbol = ref(''), period = ref('1d'), count = ref(500) } = options

  // ==================== 状态 ====================

  // 主图指标（叠加显示）
  const mainIndicators = ref<IndicatorConfig[]>([])

  // 副图指标（独立窗口）
  const subIndicators = ref<IndicatorConfig[]>([
    {
      id: 'MACD',
      name: 'MACD',
      type: 'sub',
      height: 120,
      visible: true,
      params: { ...DEFAULT_INDICATOR_PARAMS.MACD }
    },
    {
      id: 'KDJ',
      name: 'KDJ',
      type: 'sub',
      height: 100,
      visible: false,
      params: { ...DEFAULT_INDICATOR_PARAMS.KDJ }
    },
    {
      id: 'RSI',
      name: 'RSI',
      type: 'sub',
      height: 100,
      visible: false,
      params: { ...DEFAULT_INDICATOR_PARAMS.RSI }
    }
  ])

  // 可用指标列表
  const availableIndicators = computed(() => {
    return {
      main: MAIN_OVERLAY_INDICATORS.map(name => ({
        id: name,
        name: name,
        type: 'main' as const,
        params: DEFAULT_INDICATOR_PARAMS[name] || {},
        description: getIndicatorDescription(name)
      })),
      sub: SUB_INDICATORS.map(name => ({
        id: name,
        name: name,
        type: 'sub' as const,
        params: DEFAULT_INDICATOR_PARAMS[name] || {},
        description: getIndicatorDescription(name)
      }))
    }
  })

  // ==================== 主图指标操作 ====================

  /**
   * 添加主图指标
   */
  const addMainIndicator = (indicator: string, params?: any) => {
    if (hasMainIndicator(indicator)) {
      console.warn(`[useIndicatorWindows] 主图指标 ${indicator} 已存在`)
      return
    }

    mainIndicators.value.push({
      id: indicator,
      name: indicator,
      type: 'main',
      height: 0,  // 主图不使用高度
      visible: true,
      params: params || DEFAULT_INDICATOR_PARAMS[indicator] || {}
    })

    console.log(`[useIndicatorWindows] 已添加主图指标: ${indicator}`)
  }

  /**
   * 移除主图指标
   */
  const removeMainIndicator = (indicator: string) => {
    const index = mainIndicators.value.findIndex(ind => ind.id === indicator)
    if (index !== -1) {
      mainIndicators.value.splice(index, 1)
      console.log(`[useIndicatorWindows] 已移除主图指标: ${indicator}`)
    }
  }

  /**
   * 检查主图指标是否存在
   */
  const hasMainIndicator = (indicator: string): boolean => {
    return mainIndicators.value.some(ind => ind.id === indicator)
  }

  // ==================== 副图指标操作 ====================

  /**
   * 添加副图指标
   */
  const addSubIndicator = (indicator: string, params?: any) => {
    const existing = subIndicators.value.findIndex(ind => ind.id === indicator)
    if (existing !== -1) {
      // 已存在，只设置为可见
      subIndicators.value[existing].visible = true
      if (params) {
        subIndicators.value[existing].params = { ...subIndicators.value[existing].params, ...params }
      }
    } else {
      // 不存在，添加新的
      subIndicators.value.push({
        id: indicator,
        name: indicator,
        type: 'sub',
        height: getDefaultIndicatorHeight(indicator),
        visible: true,
        params: params || DEFAULT_INDICATOR_PARAMS[indicator] || {}
      })
    }

    console.log(`[useIndicatorWindows] 已添加副图指标: ${indicator}`)
  }

  /**
   * 移除副图指标
   */
  const removeSubIndicator = (indicator: string) => {
    const index = subIndicators.value.findIndex(ind => ind.id === indicator)
    if (index !== -1) {
      subIndicators.value.splice(index, 1)
      console.log(`[useIndicatorWindows] 已移除副图指标: ${indicator}`)
    }
  }

  /**
   * 切换副图指标可见性
   */
  const toggleSubIndicator = (indicator: string) => {
    const ind = subIndicators.value.find(i => i.id === indicator)
    if (ind) {
      ind.visible = !ind.visible
      console.log(`[useIndicatorWindows] ${indicator} 可见性: ${ind.visible}`)
    }
  }

  /**
   * 更新副图指标高度
   */
  const updateSubIndicatorHeight = (indicator: string, height: number) => {
    const ind = subIndicators.value.find(i => i.id === indicator)
    if (ind) {
      ind.height = Math.max(50, Math.min(400, height))
      console.log(`[useIndicatorWindows] ${indicator} 高度更新为: ${ind.height}px`)
    }
  }

  // ==================== 数据计算 ====================

  /**
   * 计算指标数据
   */
  const calculateIndicators = async (df: any) => {
    // 这里调用后端 API 计算指标
    // 实际实现需要在图表中集成
    return df
  }

  /**
   * 刷新数据
   */
  const refreshData = async () => {
    if (!symbol.value) return

    try {
      // 获取带指标的K线数据
      const subIndicatorNames = subIndicators.value
        .filter(ind => ind.visible)
        .map(ind => ind.id)

      const response = await fetchKlineWithIndicators({
        symbol: symbol.value,
        period: period.value,
        indicators: subIndicatorNames
      })

      console.log(`[useIndicatorWindows] 数据已刷新: ${response?.count} 条`)
    } catch (error) {
      console.error('[useIndicatorWindows] 刷新数据失败:', error)
    }
  }

  // ==================== 布局管理 ====================

  /**
   * 重置布局
   */
  const resetLayout = () => {
    mainIndicators.value = []
    subIndicators.value = [
      {
        id: 'MACD',
        name: 'MACD',
        type: 'sub',
        height: 120,
        visible: true,
        params: { ...DEFAULT_INDICATOR_PARAMS.MACD }
      }
    ]
    console.log('[useIndicatorWindows] 布局已重置')
  }

  /**
   * 保存布局到本地存储
   */
  const saveLayout = () => {
    const layout = {
      main: mainIndicators.value.map(ind => ({ id: ind.id, params: ind.params })),
      sub: subIndicators.value.map(ind => ({
        id: ind.id,
        height: ind.height,
        visible: ind.visible,
        params: ind.params
      }))
    }
    localStorage.setItem('indicator-layout', JSON.stringify(layout))
    console.log('[useIndicatorWindows] 布局已保存')
  }

  /**
   * 从本地存储加载布局
   */
  const loadLayout = () => {
    try {
      const saved = localStorage.getItem('indicator-layout')
      if (saved) {
        const layout = JSON.parse(saved)

        // 恢复主图指标
        mainIndicators.value = layout.main.map((item: any) => ({
          id: item.id,
          name: item.id,
          type: 'main' as const,
          height: 0,
          visible: true,
          params: item.params || {}
        }))

        // 恢复副图指标
        subIndicators.value = layout.sub.map((item: any) => ({
          id: item.id,
          name: item.id,
          type: 'sub' as const,
          height: item.height,
          visible: item.visible,
          params: item.params || {}
        }))

        console.log('[useIndicatorWindows] 布局已加载')
      }
    } catch (error) {
      console.error('[useIndicatorWindows] 加载布局失败:', error)
    }
  }

  // ==================== 工具函数 ====================

  /**
   * 获取指标描述
   */
  function getIndicatorDescription(indicator: string): string {
    const descriptions: Record<string, string> = {
      MA: '移动平均线 - 趋势跟踪指标',
      BOLL: '布林带 - 波动率通道',
      EMA: '指数移动平均线',
      SMA: '简单移动平均线',
      MACD: '指数平滑异同移动平均线 - 趋势震荡指标',
      KDJ: '随机指标 - 超买超卖震荡指标',
      RSI: '相对强弱指标 - 动量振荡指标',
      CCI: '顺势指标 - 趋势跟踪振荡指标',
      OBV: '能量潮 - 成交量趋势指标',
      ATR: '平均真实波幅 - 波动率指标',
      STOCH: '随机指标 - 超买超卖指标',
      STOCHRSI: '相对强弱随机指标'
    }
    return descriptions[indicator] || ''
  }

  /**
   * 获取指标默认高度
   */
  function getDefaultIndicatorHeight(indicator: string): number {
    const heights: Record<string, number> = {
      MACD: 120,
      KDJ: 100,
      RSI: 80,
      CCI: 80,
      OBV: 80,
      ATR: 60,
      STOCH: 100,
      STOCHRSI: 80
    }
    return heights[indicator] || 100
  }

  // ==================== 返回 ====================

  return {
    mainIndicators,
    subIndicators,
    availableIndicators,

    addMainIndicator,
    removeMainIndicator,
    hasMainIndicator,

    addSubIndicator,
    removeSubIndicator,
    toggleSubIndicator,
    updateSubIndicatorHeight,

    calculateIndicators,
    refreshData,

    resetLayout,
    saveLayout,
    loadLayout
  }
}
