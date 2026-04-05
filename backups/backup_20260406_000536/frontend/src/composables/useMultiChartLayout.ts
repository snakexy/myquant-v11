/**
 * 多图表实例布局管理
 * 用于管理主图和多个独立指标窗格的布局、时间轴同步和高度调整
 */

import { ref, computed, onUnmounted } from 'vue'
import { createChart } from 'lightweight-charts'

// 类型定义
type IChartApi = any
type LogicalRange = any

// 图表窗格配置接口
export interface ChartPane {
  id: string
  name: string
  chart: IChartApi | null
  container: HTMLElement | null
  height: number
  minHeight: number
  maxHeight: number
  visible: boolean
  order: number
}

// 布局配置接口
export interface LayoutConfig {
  mainChartHeight: number
  paneHeights: Record<string, number>
  visiblePanes: string[]
}

export function useMultiChartLayout() {
  // 主图表实例
  const mainChart = ref<IChartApi | null>(null)
  const mainChartContainer = ref<HTMLElement | null>(null)

  // 指标窗格映射
  const indicatorPanes = ref<Map<string, ChartPane>>(new Map())

  // 当前激活的窗格ID列表（按顺序）
  const activePaneIds = ref<string[]>([])

  // 是否正在同步时间轴（防止循环触发）
  const isSyncing = ref(false)

  // 布局配置
  const config = ref<LayoutConfig>({
    mainChartHeight: 400,
    paneHeights: {
      MACD: 150,
      RSI: 120,
      KDJ: 120,
      CCI: 120,
      WR: 120,
      ATR: 120,
      OBV: 120
    },
    visiblePanes: []
  })

  /**
   * 初始化主图表
   */
  const initMainChart = (container: HTMLElement, options?: any) => {
    if (mainChart.value) {
      mainChart.value.remove()
    }

    mainChartContainer.value = container
    mainChart.value = createChart(container, {
      width: container.clientWidth,
      height: config.value.mainChartHeight,
      ...options
    })

    return mainChart.value
  }

  /**
   * 创建指标窗格
   */
  const createIndicatorPane = (
    id: string,
    name: string,
    container: HTMLElement,
    options?: any
  ): IChartApi => {
    // 如果窗格已存在，先移除
    if (indicatorPanes.value.has(id)) {
      removeIndicatorPane(id)
    }

    const height = config.value.paneHeights[id] || 120

    const chart = createChart(container, {
      width: container.clientWidth,
      height: height,
      timeScale: {
        borderColor: '#2A2E39',
        timeVisible: false, // 指标窗格不显示时间轴
        secondsVisible: false
      },
      rightPriceScale: {
        borderColor: '#2A2E39'
      },
      ...options
    })

    const pane: ChartPane = {
      id,
      name,
      chart,
      container,
      height,
      minHeight: 80,
      maxHeight: 400,
      visible: true,
      order: activePaneIds.value.length
    }

    indicatorPanes.value.set(id, pane)
    activePaneIds.value.push(id)

    // 同步时间轴
    syncTimeScale(chart)

    return chart
  }

  /**
   * 移除指标窗格
   */
  const removeIndicatorPane = (id: string) => {
    const pane = indicatorPanes.value.get(id)
    if (pane?.chart) {
      pane.chart.remove()
    }

    indicatorPanes.value.delete(id)
    activePaneIds.value = activePaneIds.value.filter(paneId => paneId !== id)
  }

  /**
   * 显示/隐藏指标窗格
   */
  const toggleIndicatorPane = (id: string, visible: boolean) => {
    const pane = indicatorPanes.value.get(id)
    if (pane) {
      pane.visible = visible

      if (visible) {
        if (!activePaneIds.value.includes(id)) {
          activePaneIds.value.push(id)
        }
      } else {
        activePaneIds.value = activePaneIds.value.filter(paneId => paneId !== id)
      }
    }
  }

  /**
   * 调整窗格高度
   */
  const resizePane = (id: string, newHeight: number) => {
    const pane = indicatorPanes.value.get(id)
    if (!pane) return

    // 限制高度范围
    const clampedHeight = Math.max(
      pane.minHeight,
      Math.min(pane.maxHeight, newHeight)
    )

    pane.height = clampedHeight
    config.value.paneHeights[id] = clampedHeight

    // 更新图表高度
    if (pane.chart && pane.container) {
      pane.chart.applyOptions({
        height: clampedHeight
      })
    }

    // 保存配置到本地存储
    saveLayoutConfig()

    return clampedHeight
  }

  /**
   * 调整主图表高度
   */
  const resizeMainChart = (newHeight: number) => {
    config.value.mainChartHeight = newHeight

    if (mainChart.value) {
      mainChart.value.applyOptions({
        height: newHeight
      })
    }

    saveLayoutConfig()

    return newHeight
  }

  /**
   * 同步时间轴
   * 将新窗格的时间轴与主图表同步
   */
  const syncTimeScale = (newChart: IChartApi) => {
    if (!mainChart.value) return

    // 主图表时间轴变化时，同步所有窗格
    const mainTimeScale = mainChart.value.timeScale()
    const newTimeScale = newChart.timeScale()

    const handleMainRangeChange = (range: LogicalRange | null) => {
      if (range && !isSyncing.value) {
        isSyncing.value = true
        newTimeScale.setVisibleLogicalRange(range)
        setTimeout(() => {
          isSyncing.value = false
        }, 0)
      }
    }

    const handleNewRangeChange = (range: LogicalRange | null) => {
      if (range && !isSyncing.value) {
        isSyncing.value = true
        mainTimeScale.setVisibleLogicalRange(range)
        // 同步其他窗格
        indicatorPanes.value.forEach((pane) => {
          if (pane.chart && pane.chart !== newChart) {
            pane.chart.timeScale().setVisibleLogicalRange(range)
          }
        })
        setTimeout(() => {
          isSyncing.value = false
        }, 0)
      }
    }

    // 订阅时间轴变化
    try {
      mainTimeScale.subscribeVisibleLogicalRangeChange(handleMainRangeChange)
      newTimeScale.subscribeVisibleLogicalRangeChange(handleNewRangeChange)
    } catch (error) {
      console.warn('时间轴同步订阅失败:', error)
    }
  }

  /**
   * 同步所有窗格时间轴到主图表
   */
  const syncAllPanesToMain = () => {
    if (!mainChart.value) return

    try {
      const mainTimeScale = mainChart.value.timeScale()
      const range = mainTimeScale.getVisibleLogicalRange()

      if (range) {
        indicatorPanes.value.forEach((pane) => {
          if (pane.chart && pane.visible) {
            pane.chart.timeScale().setVisibleLogicalRange(range)
          }
        })
      }
    } catch (error) {
      console.warn('同步所有窗格失败:', error)
    }
  }

  /**
   * 获取图表实例
   */
  const getChart = (id: string): IChartApi | null => {
    if (id === 'main') {
      return mainChart.value
    }

    const pane = indicatorPanes.value.get(id)
    return pane?.chart || null
  }

  /**
   * 获取所有图表实例
   */
  const getAllCharts = (): IChartApi[] => {
    const charts: IChartApi[] = []

    if (mainChart.value) {
      charts.push(mainChart.value)
    }

    indicatorPanes.value.forEach((pane) => {
      if (pane.chart && pane.visible) {
        charts.push(pane.chart)
      }
    })

    return charts
  }

  /**
   * 响应式调整所有图表大小
   */
  const resizeAllCharts = (width: number) => {
    if (mainChart.value) {
      mainChart.value.applyOptions({ width })
    }

    indicatorPanes.value.forEach((pane) => {
      if (pane.chart) {
        pane.chart.applyOptions({ width })
      }
    })
  }

  /**
   * 保存布局配置到本地存储
   */
  const saveLayoutConfig = () => {
    try {
      localStorage.setItem(
        'kline-chart-layout',
        JSON.stringify(config.value)
      )
    } catch (error) {
      console.warn('保存布局配置失败:', error)
    }
  }

  /**
   * 从本地存储加载布局配置
   */
  const loadLayoutConfig = () => {
    try {
      const saved = localStorage.getItem('kline-chart-layout')
      if (saved) {
        const parsed = JSON.parse(saved)
        config.value = { ...config.value, ...parsed }
        return true
      }
    } catch (error) {
      console.warn('加载布局配置失败:', error)
    }
    return false
  }

  /**
   * 重置布局配置
   */
  const resetLayoutConfig = () => {
    config.value = {
      mainChartHeight: 400,
      paneHeights: {
        MACD: 150,
        RSI: 120,
        KDJ: 120,
        CCI: 120,
        WR: 120,
        ATR: 120,
        OBV: 120
      },
      visiblePanes: []
    }

    // 应用默认高度
    indicatorPanes.value.forEach((pane) => {
      const defaultHeight = config.value.paneHeights[pane.id] || 120
      resizePane(pane.id, defaultHeight)
    })

    saveLayoutConfig()
  }

  /**
   * 清理所有图表
   */
  const disposeAllCharts = () => {
    if (mainChart.value) {
      mainChart.value.remove()
      mainChart.value = null
    }

    indicatorPanes.value.forEach((pane) => {
      if (pane.chart) {
        pane.chart.remove()
      }
    })

    indicatorPanes.value.clear()
    activePaneIds.value = []
  }

  // 计算属性：可见窗格列表（按顺序）
  const visiblePanes = computed(() => {
    return activePaneIds.value
      .map(id => indicatorPanes.value.get(id))
      .filter(pane => pane && pane.visible) as ChartPane[]
  })

  // 计算属性：总高度
  const totalHeight = computed(() => {
    let total = config.value.mainChartHeight
    visiblePanes.value.forEach(pane => {
      total += pane.height
    })
    return total
  })

  // 组件卸载时清理
  onUnmounted(() => {
    disposeAllCharts()
  })

  return {
    // 状态
    mainChart,
    mainChartContainer,
    indicatorPanes,
    activePaneIds,
    visiblePanes,
    config,
    totalHeight,

    // 方法
    initMainChart,
    createIndicatorPane,
    removeIndicatorPane,
    toggleIndicatorPane,
    resizePane,
    resizeMainChart,
    syncTimeScale,
    syncAllPanesToMain,
    getChart,
    getAllCharts,
    resizeAllCharts,
    saveLayoutConfig,
    loadLayoutConfig,
    resetLayoutConfig,
    disposeAllCharts
  }
}
