<template>
  <div class="chart-test-page">
    <!-- 测试工具栏 -->
    <div class="test-toolbar">
      <h1>逐步添加指标测试 - 使用官方指标库</h1>
      <div class="toolbar-content">
        <button @click="changePeriod('5min')">5分</button>
        <button @click="changePeriod('15min')">15分</button>
        <button @click="changePeriod('30min')">30分</button>
        <button @click="changePeriod('60min')">小时</button>
        <button @click="changePeriod('day')">日线</button>
        <button @click="changePeriod('week')">周线</button>
        <button @click="changePeriod('month')">月线</button>
        <button class="active">{{ currentPeriod }}</button>
      </div>
    </div>

    <!-- 指标控制面板 -->
    <div class="indicator-panel">
      <div class="panel-section">
        <h3>1. 主图指标 (使用 lightweight-charts-indicators)</h3>
        <button @click="toggleMA('MA5')" :class="{ active: hasMA5 }">MA5</button>
        <button @click="toggleMA('MA10')" :class="{ active: hasMA10 }">MA10</button>
        <button @click="toggleMA('MA20')" :class="{ active: hasMA20 }">MA20</button>
        <button @click="toggleMA('MA60')" :class="{ active: hasMA60 }">MA60</button>
      </div>

      <div class="panel-section">
        <h3>2. 成交量</h3>
        <button @click="toggleVolume" :class="{ active: hasVolume }">成交量</button>
      </div>

      <div class="panel-section">
        <h3>3. 独立窗格指标</h3>
        <button @click="togglePaneIndicator('MACD')" :class="{ active: hasMACD }">MACD</button>
        <button @click="togglePaneIndicator('RSI')" :class="{ active: hasRSI }">RSI</button>
      </div>

      <div class="panel-section">
        <h3>诊断</h3>
        <button @click="runDiagnose">诊断图表</button>
      </div>

      <div class="panel-section">
        <h3>操作</h3>
        <button @click="clearAll" class="clear-button">🗑️ 清除所有指标</button>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧工具栏 -->
      <div class="test-left-toolbar">
        <button class="tool-btn active" title="光标">🖱️</button>
      </div>

      <div class="chart-container" ref="chartContainer"></div>

      <!-- 右侧边栏 -->
      <div class="test-sidebar">
        <h3>状态</h3>
        <div class="status-list">
          <p>主图指标: {{ mainIndicatorCount }}</p>
          <p>独立窗格: {{ paneCount }}</p>
          <p>数据点数: {{ dataCount }}</p>
          <p>✅ 使用官方 lightweight-charts-indicators 库</p>
          <p>✅ 请测试：鼠标滚轮、拖动、十字准星</p>
        </div>
      </div>
    </div>

    <div class="status">
      <p>状态: {{ status }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { createChart, CandlestickSeries, LineSeries, HistogramSeries } from 'lightweight-charts'
import { addMAIndicator, addMACDIndicator, addRSIIndicator } from '@/components/charts/indicators'
import type { Bar } from 'oakscriptjs'

const chartContainer = ref<HTMLElement>()
const status = ref('初始化中...')
const currentPeriod = ref('日线')
const stockCode = ref('600000.SH')
const dataCount = ref(0)

// 指标状态
const hasMA5 = ref(false)
const hasMA10 = ref(false)
const hasMA20 = ref(false)
const hasMA60 = ref(false)
const hasVolume = ref(true)  // ✅ 成交量默认显示
const hasMACD = ref(false)
const hasRSI = ref(false)

let chart: any = null
let candlestickSeries: any = null
let volumeSeries: any = null

// 存储K线数据（用于指标计算）
let klineBars: Bar[] = []

// 存储主图叠加指标系列
const overlaySeries = new Map<string, any>()

// ✅ 存储独立窗格指标的 series 列表（直接用指标名称作为 key）
const indicatorPanes = new Map<string, any[]>()

// ✅ 包装函数：通过指标名称删除 pane
const removeIndicatorPane = async (indicatorName: string) => {
  const seriesList = indicatorPanes.get(indicatorName)
  if (!seriesList) {
    console.warn(`[removeIndicatorPane] ⚠️ 未找到 ${indicatorName} 的 series 记录`)
    return
  }

  console.log(`\n========== [removeIndicatorPane] 开始删除 ${indicatorName} ==========`)
  console.log(`[removeIndicatorPane] 找到 ${seriesList.length} 个 series`)

  // ✅ 调试：显示删除前的 pane 状态
  const panesBefore = chart.panes()
  console.log(`[removeIndicatorPane] 删除前有 ${panesBefore.length} 个 pane`)
  panesBefore.forEach((pane, i) => {
    const seriesInPane = pane.series()
    const titles = seriesInPane.map((s: any) => s.options()?.title || 'unknown').join(', ')
    console.log(`[removeIndicatorPane]   pane ${i}: [${titles}] (${seriesInPane.length} 个 series)`)
  })

  // ✅ 第一步：删除所有 series
  console.log(`[removeIndicatorPane] 开始删除 ${seriesList.length} 个 series...`)
  let deletedCount = 0
  seriesList.forEach((series: any) => {
    try {
      const title = series.options()?.title || 'unknown'
      console.log(`[removeIndicatorPane]   删除 series: ${title}`)
      chart.removeSeries(series)
      deletedCount++
    } catch (e) {
      console.error(`[removeIndicatorPane]   ❌ 删除 series 失败:`, e)
    }
  })
  console.log(`[removeIndicatorPane] 成功删除 ${deletedCount}/${seriesList.length} 个 series`)

  // ✅ 第二步：等待 lightweight-charts 更新状态，然后检查并删除空的 pane
  await new Promise(resolve => setTimeout(resolve, 10))

  // 调试：显示删除后的 pane 状态
  const panesAfter = chart.panes()
  console.log(`[removeIndicatorPane] 删除后有 ${panesAfter.length} 个 pane`)
  panesAfter.forEach((pane, i) => {
    const seriesInPane = pane.series()
    const titles = seriesInPane.map((s: any) => s.options()?.title || 'unknown').join(', ')
    console.log(`[removeIndicatorPane]   pane ${i}: [${titles}] (${seriesInPane.length} 个 series)`)
  })

  // ✅ 第三步：从后往前遍历，删除空的 pane
  console.log(`[removeIndicatorPane] 检查并删除空的 pane...`)
  for (let i = panesAfter.length - 1; i >= 1; i--) {
    const pane = panesAfter[i]
    const seriesInPane = pane.series()

    console.log(`[removeIndicatorPane] 检查 pane ${i}: ${seriesInPane.length} 个 series`)

    // 如果这个 pane 没有 series 了，删除它
    if (seriesInPane.length === 0) {
      try {
        console.log(`[removeIndicatorPane] ✅ pane ${i} 为空，准备删除`)
        chart.removePane(i)
        console.log(`[removeIndicatorPane] ✅ 已删除 pane ${i}`)
      } catch (e) {
        console.error(`[removeIndicatorPane] ❌ 删除 pane ${i} 失败:`, e)
      }
    } else {
      const titles = seriesInPane.map((s: any) => s.options()?.title || 'unknown')
      console.log(`[removeIndicatorPane] ⚠️ pane ${i} 不为空，保留: [${titles}]`)
    }
  }

  // 最终状态
  const panesFinal = chart.panes()
  console.log(`[removeIndicatorPane] 最终有 ${panesFinal.length} 个 pane`)

  // 清理映射
  indicatorPanes.delete(indicatorName)

  // ✅ 强制重绘图表
  try {
    const container = chartContainer.value
    if (container) {
      const { width, height } = container.getBoundingClientRect()
      chart.resize(width, height)
      console.log(`[removeIndicatorPane] ✅ 已强制重绘图表`)
    }
  } catch (e) {
    console.warn(`[removeIndicatorPane] 强制重绘失败:`, e)
  }

  console.log(`========== [removeIndicatorPane] ${indicatorName} 删除完成 ==========\n`)
}

// 首次加载标记
let isInitialLoad = true

const mainIndicatorCount = computed(() => {
  return [hasMA5, hasMA10, hasMA20, hasMA60].filter(v => v.value).length
})

const paneCount = computed(() => {
  return [hasMACD, hasRSI].filter(v => v.value).length
})

const loadKlineData = async (period: string, symbol: string) => {
  try {
    status.value = `加载${symbol} ${period}数据...`

    // ✅ 完整的周期映射
    const periodMap: Record<string, string> = {
      '5min': '5min',
      '15min': '15min',
      '30min': '30min',
      '60min': '60min',
      'day': 'day',
      'week': 'week',
      'month': 'month'
    }

    const mappedPeriod = periodMap[period]
    if (!mappedPeriod) {
      console.error(`[loadKlineData] ❌ 不支持的周期: ${period}`)
      status.value = `不支持的周期: ${period}`
      return
    }

    const params = new URLSearchParams({
      symbol: symbol,
      period: mappedPeriod,
      count: '100'  // count参数：日线为天数，分钟线为根数
    })

    const requestUrl = `/api/v1/market/kline-data?${params.toString()}`
    console.log(`[loadKlineData] 📡 请求URL: ${requestUrl}`)
    console.log(`[loadKlineData] 📊 周期参数: ${period} -> ${mappedPeriod}`)

    const response = await fetch(requestUrl)
    const result = await response.json()

    console.log(`[loadKlineData] ✅ 响应数据条数: ${result.data?.length || 0}`)
    console.log(`[loadKlineData] 🔍 第一条数据:`, result.data?.[0])

    if (result.success && result.data && Array.isArray(result.data) && result.data.length > 0) {
      // 转换为 lightweight-charts 格式
      const chartData = result.data.map((item: any) => ({
        time: new Date(item.datetime || item.time).getTime() / 1000,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }))

      // 转换为 Bar 格式（用于指标计算）
      klineBars = result.data.map((item: any) => ({
        time: new Date(item.datetime || item.time).getTime() / 1000,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }))

      // 设置K线数据
      candlestickSeries.setData(chartData)
      dataCount.value = chartData.length

      // ✅ 先恢复保存的指标状态（在首次加载时）
      if (isInitialLoad) {
        console.log('[loadKlineData] 首次加载，先恢复保存的指标状态')
        await restoreIndicatorStates()
        // 恢复状态后，创建实际的系列和窗格
        await applySavedIndicatorSeries()
        isInitialLoad = false
      }

      // 更新成交量
      if (hasVolume.value && volumeSeries) {
        const volumeData = chartData
          .filter((item: any) => item.volume != null && !isNaN(item.volume))
          .map((item: any) => ({
            time: item.time,
            value: item.volume,
            color: item.close >= item.open ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'
          }))
        volumeSeries.setData(volumeData)
      }

      // ✅ 使用官方指标库更新所有MA指标
      await updateAllMAIndicators()

      // ✅ 确保垂直布局正确
      ensureVerticalLayout()

      chart.timeScale().fitContent()

      status.value = `✅ 加载成功: ${chartData.length}条数据`
      console.log(`[ChartTest] 数据加载成功:`, {
        symbol,
        period,
        count: chartData.length
      })
    } else {
      status.value = '⚠️ 无数据'
    }
  } catch (error) {
    console.error('[ChartTest] 数据加载失败:', error)
    status.value = '❌ 数据加载失败: ' + error
  }
}

// 使用官方指标库更新所有MA指标
const updateAllMAIndicators = async () => {
  console.log(`[updateAllMAIndicators] 开始使用官方指标库更新MA`)

  const colorMap: Record<string, string> = {
    'MA5': '#FF6B6B',
    'MA10': '#4ECDC4',
    'MA20': '#45B7D1',
    'MA60': '#FFA07A'
  }

  const periodMap: Record<string, number> = {
    'MA5': 5,
    'MA10': 10,
    'MA20': 20,
    'MA60': 60
  }

  // 遍历所有激活的MA指标
  for (const [key, isActive] of [
    ['MA5', hasMA5.value],
    ['MA10', hasMA10.value],
    ['MA20', hasMA20.value],
    ['MA60', hasMA60.value]
  ]) {
    if (isActive) {
      console.log(`[updateAllMAIndicators] 更新 ${key}`)

      // 使用官方 addMAIndicator 函数
      await addMAIndicator(
        chart,
        overlaySeries,
        klineBars,
        {
          key,
          period: periodMap[key as string],
          color: colorMap[key as string]
        }
      )

      console.log(`[updateAllMAIndicators] ✅ ${key} 更新完成`)
    }
  }
}

onMounted(() => {
  try {
    if (!chartContainer.value) {
      status.value = '❌ 找不到容器'
      return
    }

    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight

    // 创建图表
    chart = createChart(chartContainer.value, {
      width,
      height,
      layout: {
        background: { color: '#131722' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
        horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
      },
      handleScroll: true,
      handleScale: true,
      kineticScroll: true,
    })

    console.log('[ChartTest] ✅ 图表创建成功')

    // 创建K线系列
    candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    // 创建成交量系列（这会自动创建'volume' price scale）
    volumeSeries = chart.addSeries(HistogramSeries, {
      priceScaleId: 'volume',
      color: '#26a69a',
    })

    console.log('[ChartTest] ✅ 图表初始化完成（布局将在数据加载后设置）')

    // 加载数据
    loadKlineData('day', stockCode.value)

  } catch (error) {
    console.error('[ChartTest] 创建失败:', error)
    status.value = '❌ 创建失败: ' + error
  }
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
  }
})

const changePeriod = (period: string) => {
  // 周期映射
  const periodLabels: Record<string, string> = {
    '5min': '5分',
    '15min': '15分',
    '30min': '30分',
    '60min': '小时',
    'day': '日线',
    'week': '周线',
    'month': '月线'
  }

  currentPeriod.value = periodLabels[period] || period
  console.log(`[changePeriod] 切换周期: ${period} (${currentPeriod.value})`)
  loadKlineData(period, stockCode.value)
}

// ==================== localStorage 持久化 ====================

const STORAGE_KEY = 'kline-indicators-preferences'

// 保存设置到 localStorage
const savePreferences = () => {
  const preferences = {
    indicators: {
      MA5: hasMA5.value,
      MA10: hasMA10.value,
      MA20: hasMA20.value,
      MA60: hasMA60.value,
      Volume: hasVolume.value,
      MACD: hasMACD.value,
      RSI: hasRSI.value
    },
    paneHeights: {} as Record<string, number>
  }

  // 保存窗格高度
  if (chart) {
    chart.panes().forEach((pane: any, index: number) => {
      if (index > 0) {  // 跳过主图
        const paneHeight = pane._height?.value
        if (paneHeight) {
          preferences.paneHeights[index] = paneHeight
        }
      }
    })
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences))
    console.log('[savePreferences] ✅ 设置已保存:', preferences)
  } catch (error) {
    console.error('[savePreferences] ❌ 保存失败:', error)
  }
}

// 从 localStorage 加载设置
const loadPreferences = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) {
      console.log('[loadPreferences] ⚠️ 没有保存的设置')
      return null
    }

    const preferences = JSON.parse(saved)
    console.log('[loadPreferences] ✅ 加载设置:', preferences)
    return preferences
  } catch (error) {
    console.error('[loadPreferences] ❌ 加载失败:', error)
    return null
  }
}

// ✅ 只恢复指标状态（不创建系列），在数据加载前调用
const restoreIndicatorStates = () => {
  const preferences = loadPreferences()
  if (!preferences || !preferences.indicators) {
    console.log('[restoreIndicatorStates] ⚠️ 没有保存的指标状态')
    return
  }

  console.log('[restoreIndicatorStates] 恢复指标状态')
  const { MA5, MA10, MA20, MA60, Volume, MACD, RSI } = preferences.indicators

  // 只恢复状态，不创建系列
  if (MA5) hasMA5.value = true
  if (MA10) hasMA10.value = true
  if (MA20) hasMA20.value = true
  if (MA60) hasMA60.value = true
  if (Volume) hasVolume.value = true
  if (MACD) hasMACD.value = true
  if (RSI) hasRSI.value = true

  console.log('[restoreIndicatorStates] ✅ 状态已恢复:', {
    MA5: hasMA5.value,
    MA10: hasMA10.value,
    MA20: hasMA20.value,
    MA60: hasMA60.value,
    Volume: hasVolume.value,
    MACD: hasMACD.value,
    RSI: hasRSI.value
  })
}

// ✅ 确保垂直布局正确（使用官方推荐方式：通过series.priceScale()）
const ensureVerticalLayout = () => {
  if (!chart || !candlestickSeries) return

  // 主图K线：最低35%，最高98%（更靠上显示）
  // 官方文档：https://tradingview.github.io/lightweight-charts/tutorials/customization/price-scale
  try {
    candlestickSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.02,   // 上边距 2%（最高到98%）
        bottom: 0.35  // 下边距 35%（最低到35%）
      }
    })
    console.log('[ensureVerticalLayout] ✅ 主图布局已设置（通过series.priceScale()）')
  } catch (error) {
    console.error('[ensureVerticalLayout] 主图布局设置失败:', error)
  }

  // 成交量：位于底部0%-25%（占用25%高度）
  // 注意：只有当volume price scale存在时才能设置
  try {
    const volumePriceScale = chart.priceScale('volume')
    if (volumePriceScale) {
      volumePriceScale.applyOptions({
        scaleMargins: {
          top: 0.75,   // 上边距 75%（从75%往下）
          bottom: 0    // 下边距 0%（到底部）
        },
      })
      console.log('[ensureVerticalLayout] ✅ 成交量布局已设置')
    }
  } catch (error) {
    console.warn('[ensureVerticalLayout] 成交量布局设置失败（可能还没有数据）:', error)
  }
}

// 应用保存的指标系列（状态已在restoreIndicatorStates中恢复）
const applySavedIndicatorSeries = async () => {
  const preferences = loadPreferences()
  if (!preferences) return

  console.log('[applySavedIndicatorSeries] 开始创建保存的指标系列')

  // 恢复指标状态
  if (preferences.indicators) {
    const { MA5, MA10, MA20, MA60, Volume, MACD, RSI } = preferences.indicators

    // 恢复主图指标（直接设置状态，不通过toggle避免循环）
    const colorMap: Record<string, string> = {
      'MA5': '#FF6B6B',
      'MA10': '#4ECDC4',
      'MA20': '#45B7D1',
      'MA60': '#FFA07A'
    }

    const periodMap: Record<string, number> = {
      'MA5': 5,
      'MA10': 10,
      'MA20': 20,
      'MA60': 60
    }

    // 恢复MA指标
    const maIndicators = [
      { key: 'MA5', period: 5, has: MA5 },
      { key: 'MA10', period: 10, has: MA10 },
      { key: 'MA20', period: 20, has: MA20 },
      { key: 'MA60', period: 60, has: MA60 }
    ]

    for (const ma of maIndicators) {
      if (ma.has && !overlaySeries.has(ma.key)) {
        try {
          const series = chart.addSeries(LineSeries, {
            color: colorMap[ma.key as keyof typeof colorMap],
            lineWidth: 1,
            title: ma.key,
            lastValueVisible: true,
            priceLineVisible: false,
          })
          overlaySeries.set(ma.key, series)

          await addMAIndicator(chart, overlaySeries, klineBars, {
            key: ma.key,
            period: ma.period,
            color: colorMap[ma.key as keyof typeof colorMap]
          })

          console.log(`[applySavedIndicatorSeries] ✅ 恢复 ${ma.key}`)
        } catch (error) {
          console.error(`[applySavedIndicatorSeries] ❌ 恢复 ${ma.key} 失败:`, error)
        }
      }
    }

    // 恢复成交量状态（不需要创建系列，系列已存在）
    if (Volume) {
      console.log(`[applySavedIndicatorSeries] ✅ 成交量已启用`)
    }

    // 恢复独立窗格指标
    setTimeout(async () => {
      if (MACD && !indicatorPanes.has('MACD')) {
        try {
          const paneIndex = chart.panes().length
          const tempMap = new Map<number, any[]>()
          await addMACDIndicator(chart, klineBars, tempMap, paneIndex)

          // ✅ 只保存 series 列表
          indicatorPanes.set('MACD', Array.from(tempMap.values()).flat())

          console.log(`[applySavedIndicatorSeries] ✅ 恢复 MACD`)
        } catch (error) {
          console.error(`[applySavedIndicatorSeries] ❌ 恢复 MACD 失败:`, error)
        }
      }

      if (RSI && !indicatorPanes.has('RSI')) {
        try {
          const paneIndex = chart.panes().length
          const tempMap = new Map<number, any[]>()
          await addRSIIndicator(chart, klineBars, tempMap, paneIndex)

          // ✅ 只保存 series 列表
          indicatorPanes.set('RSI', Array.from(tempMap.values()).flat())

          console.log(`[applySavedIndicatorSeries] ✅ 恢复 RSI`)
        } catch (error) {
          console.error(`[applySavedIndicatorSeries] ❌ 恢复 RSI 失败:`, error)
        }
      }

      // 恢复窗格高度
      if (preferences.paneHeights && chart) {
        Object.entries(preferences.paneHeights).forEach(([index, height]) => {
          const paneIndex = parseInt(index)
          const panes = chart.panes()
          if (panes[paneIndex]) {
            panes[paneIndex].setHeight(height)
            console.log(`[applySavedIndicatorSeries] ✅ 恢复窗格 ${paneIndex} 高度为 ${height}px`)
          }
        })
      }
    }, 300)
  }
}

// 监听用户操作并自动保存
const watchAndSave = () => {
  // 监听所有指标状态变化
  const indicators = [
    hasMA5, hasMA10, hasMA20, hasMA60,
    hasVolume, hasMACD, hasRSI
  ]

  indicators.forEach(ref => {
    watch(ref, () => {
      savePreferences()
    })
  })

  // 监听窗格高度变化（通过 ResizeObserver）
  if (chartContainer.value) {
    const observer = new MutationObserver(() => {
      savePreferences()
    })
    observer.observe(chartContainer.value, {
      subtree: true,
      attributes: true,
      attributeFilter: ['style']
    })
  }
}

// ==================== 原有的切换指标函数 ====================

// 切换主图指标
const toggleMA = async (key: string) => {
  const refMap: Record<string, any> = {
    'MA5': hasMA5,
    'MA10': hasMA10,
    'MA20': hasMA20,
    'MA60': hasMA60
  }

  const colorMap: Record<string, string> = {
    'MA5': '#FF6B6B',
    'MA10': '#4ECDC4',
    'MA20': '#45B7D1',
    'MA60': '#FFA07A'
  }

  const periodMap: Record<string, number> = {
    'MA5': 5,
    'MA10': 10,
    'MA20': 20,
    'MA60': 60
  }

  const isActive = refMap[key]
  isActive.value = !isActive.value

  if (isActive.value) {
    // 创建指标系列
    console.log(`[toggleMA] 准备创建 ${key} 系列`)
    try {
      const series = chart.addSeries(LineSeries, {
        color: colorMap[key],
        lineWidth: 1,
        title: key,
        lastValueVisible: true,   // 显示右边数值标签
        priceLineVisible: false,  // 隐藏价格线（横虚线）
      })
      overlaySeries.set(key, series)
      console.log(`[toggleMA] ✅ 成功创建 ${key} 系列`)

      // 使用官方指标库计算并更新
      await addMAIndicator(chart, overlaySeries, klineBars, {
        key,
        period: periodMap[key],
        color: colorMap[key]
      })

      // ✅ 保存设置
      savePreferences()
    } catch (error) {
      console.error(`[toggleMA] ❌ 创建 ${key} 失败:`, error)
    }
  } else {
    // 删除指标系列
    if (overlaySeries.has(key)) {
      const series = overlaySeries.get(key)
      series.setData([])
      console.log(`[toggleMA] ❌ 清空 ${key}`)
      // ✅ 保存设置
      savePreferences()
    }
  }
}

// 切换成交量
const toggleVolume = () => {
  hasVolume.value = !hasVolume.value

  // 直接更新成交量显示，不需要重新加载数据
  if (hasVolume.value && volumeSeries && klineBars.length > 0) {
    // 显示成交量：从klineBars中提取数据
    const volumeData = klineBars
      .filter((item: any) => item.volume != null && !isNaN(item.volume))
      .map((item: any) => ({
        time: item.time,
        value: item.volume,
        color: item.close >= item.open ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'
      }))
    volumeSeries.setData(volumeData)
    console.log(`[toggleVolume] ✅ 成交量已显示`)
  } else if (!hasVolume.value && volumeSeries) {
    // 隐藏成交量：清空数据
    volumeSeries.setData([])
    console.log(`[toggleVolume] ❌ 成交量已隐藏`)
  }

  // ✅ 保存设置
  savePreferences()
}

// 切换独立窗格指标
const togglePaneIndicator = async (key: string) => {
  const refMap: Record<string, any> = {
    'MACD': hasMACD,
    'RSI': hasRSI
  }

  const isActive = refMap[key]
  const shouldEnable = !isActive.value  // 目标状态

  if (shouldEnable) {
    // 创建指标
    // 检查是否已经存在
    if (indicatorPanes.has(key)) {
      console.log(`[togglePaneIndicator] ⚠️ ${key} 窗格已存在`)
      isActive.value = true
      return
    }

    // ✅ 使用动态索引 - 谁先创建谁就在上面
    const paneIndex = chart.panes().length

    console.log(`[togglePaneIndicator] 准备创建 ${key} 窗格，动态paneIndex=${paneIndex}`)

    try {
      if (key === 'MACD' && chart) {
        // 临时创建一个 Map 来传递给 addMACDIndicator
        const tempMap = new Map<number, any[]>()
        await addMACDIndicator(chart, klineBars, tempMap, paneIndex)

        // ✅ 只保存 series 列表，不保存 paneIndex
        indicatorPanes.set('MACD', Array.from(tempMap.values()).flat())

        isActive.value = true
        console.log(`[togglePaneIndicator] ✅ MACD 窗格创建成功`)
      } else if (key === 'RSI' && chart) {
        // 临时创建一个 Map 来传递给 addRSIIndicator
        const tempMap = new Map<number, any[]>()
        await addRSIIndicator(chart, klineBars, tempMap, paneIndex)

        // ✅ 只保存 series 列表，不保存 paneIndex
        indicatorPanes.set('RSI', Array.from(tempMap.values()).flat())

        isActive.value = true
        console.log(`[togglePaneIndicator] ✅ RSI 窗格创建成功`)
      }

      // ✅ 保存设置
      savePreferences()
    } catch (error) {
      console.error(`[togglePaneIndicator] ❌ 创建 ${key} 失败:`, error)
      isActive.value = false
    }
  } else {
    // 删除指标
    if (!chart) return

    // ✅ 使用包装函数，类似 removePane('MACD')
    await removeIndicatorPane(key)

    isActive.value = false
    savePreferences()
  }
}

// 诊断
const runDiagnose = () => {
  if (!chart) {
    console.log('❌ 图表未初始化')
    return
  }

  const allPanes = chart.panes()
  console.log('====== 图表诊断 ======')
  console.log('总窗格数:', allPanes.length)
  console.log('激活的指标:', {
    MA5: hasMA5.value,
    MA10: hasMA10.value,
    MA20: hasMA20.value,
    MA60: hasMA60.value,
    Volume: hasVolume.value,
    MACD: hasMACD.value,
    RSI: hasRSI.value
  })
  console.log('overlaySeries数量:', overlaySeries.size)
  console.log('indicatorPanes数量:', indicatorPanes.size)
  console.log('indicatorPanes详情:', Array.from(indicatorPanes.entries()).map(([k, v]) => `${k}: ${v.length} series`))

  // 显示保存的设置
  const saved = loadPreferences()
  console.log('保存的设置:', saved)

  allPanes.forEach((pane: any, index: number) => {
    const paneData = pane as any
    const paneHeight = paneData._height?.value || 'unknown'
    const seriesObjects = paneData._series || paneData.series || []
    const titles = seriesObjects.map((s: any) => s._specs?.title || 'unknown').join(', ')
    console.log(`  窗格 ${index}: 高度=${paneHeight}px, 系列=[${titles}]`)
  })

  console.log('====================')
}

// 清除所有指标
const clearAll = () => {
  hasMA5.value = false
  hasMA10.value = false
  hasMA20.value = false
  hasMA60.value = false
  hasVolume.value = false
  hasMACD.value = false
  hasRSI.value = false

  // 清空所有主图指标系列数据
  overlaySeries.forEach(series => {
    series.setData([])
  })

  // ✅ 删除所有独立窗格的系列（删除系列会自动删除窗格）
  if (chart) {
    console.log(`[clearAll] 当前indicatorPanes数量: ${indicatorPanes.size}`)

    indicatorPanes.forEach((seriesList, key) => {
      console.log(`[clearAll] 删除 ${key} 的 ${seriesList.length} 个系列`)
      seriesList.forEach((series: any) => {
        try {
          chart.removeSeries(series)
        } catch (error) {
          console.error(`[clearAll] ❌ 删除系列失败:`, error)
        }
      })
    })

    console.log(`[clearAll] 删除后窗格数:`, chart.panes().length)

    // ✅ 重置 nextAvailablePaneIndex
    nextAvailablePaneIndex = chart.panes().length
    console.log(`[clearAll] nextAvailablePaneIndex 重置为 ${nextAvailablePaneIndex}`)
  }

  // 清空映射
  indicatorPanes.clear()

  volumeSeries?.setData([])

  // ✅ 清除保存的设置
  try {
    localStorage.removeItem(STORAGE_KEY)
    console.log('[clearAll] ✅ 已清除保存的设置')
  } catch (error) {
    console.error('[clearAll] ❌ 清除保存设置失败:', error)
  }

  console.log('[clearAll] ✅ 所有指标已清除')
  loadKlineData(currentPeriod.value === '5分' ? '5min' : 'day', stockCode.value)
}
</script>

<style scoped>
.chart-test-page {
  width: 100vw;
  height: 100vh;
  background: #0f0f23;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 测试工具栏 */
.test-toolbar {
  padding: 10px 20px;
  background: #131722;
  border-bottom: 1px solid #2a2e39;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

.test-toolbar h1 {
  color: #d1d4dc;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.toolbar-content {
  display: flex;
  gap: 8px;
}

.toolbar-content button {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #2a2e39;
  color: #d1d4dc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s ease;
}

.toolbar-content button:hover {
  background: #2a2e39;
}

.toolbar-content button.active {
  background: #2962ff;
  border-color: #2962ff;
  color: white;
}

/* 指标控制面板 */
.indicator-panel {
  padding: 10px 20px;
  background: #1e222d;
  border-bottom: 1px solid #2a2e39;
  display: flex;
  gap: 16px;
  overflow-x: auto;
  flex-shrink: 0;
}

.panel-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-section h3 {
  color: #787b86;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  margin: 0;
}

.panel-section button {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #2a2e39;
  color: #d1d4dc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.panel-section button:hover {
  background: #2a2e39;
}

.panel-section button.active {
  background: #2962ff;
  border-color: #2962ff;
  color: white;
}

/* 清除按钮特殊样式 */
.panel-section button.clear-button {
  background: #ef5350;
  border-color: #ef5350;
  color: white;
  font-weight: 600;
}

.panel-section button.clear-button:hover {
  background: #e53935;
  border-color: #e53935;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* 左侧工具栏 */
.test-left-toolbar {
  position: absolute;
  left: 6px;
  top: 6px;
  width: 40px;
  background: #131722;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 3px;
  z-index: 100;
}

.tool-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  color: #d1d4dc;
  border-radius: 3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.1s ease;
}

.tool-btn:hover {
  background: #1e222d;
}

.tool-btn.active {
  background: #2962ff;
  color: white;
}

/* 图表容器 */
.chart-container {
  flex: 1;
  background: #131722;
  min-width: 0;
  margin-left: 50px;
}

/* 右侧边栏 */
.test-sidebar {
  width: 280px;
  background: #131722;
  border-left: 1px solid #2a2e39;
  overflow-y: auto;
  flex-shrink: 0;
}

.test-sidebar h3 {
  color: #d1d4dc;
  padding: 12px 16px;
  margin: 0;
  font-size: 14px;
  border-bottom: 1px solid #2a2e39;
}

.status-list {
  padding: 16px;
}

.status-list p {
  margin: 8px 0;
  font-size: 13px;
  color: #d1d4dc;
}

.test-list {
  padding: 16px;
}

.test-item {
  margin: 12px 0;
  font-size: 13px;
}

.test-label {
  color: #d1d4dc;
  display: block;
  margin-bottom: 4px;
}

.test-placeholder {
  color: #787b86;
  font-family: monospace;
}

.instructions {
  padding: 16px;
  border-top: 1px solid #2a2e39;
  margin-top: auto;
}

.instructions p {
  margin: 8px 0;
  font-size: 12px;
  color: #d1d4dc;
}

.instructions ol {
  margin: 8px 0;
  padding-left: 20px;
  font-size: 12px;
  color: #787b86;
}

.instructions li {
  margin: 4px 0;
}

.stock-item {
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #2a2e39;
  cursor: pointer;
  transition: background 0.15s ease;
}

.stock-item:hover {
  background: #1e222d;
}

.stock-item .code {
  color: #d1d4dc;
  font-size: 13px;
  font-weight: 500;
}

.stock-item .name {
  color: #787b86;
  font-size: 12px;
}

/* 状态栏 */
.status {
  padding: 10px 20px;
  background: #1e222d;
  border-top: 1px solid #2a2e39;
  color: #d1d4dc;
  font-family: monospace;
  font-size: 13px;
  flex-shrink: 0;
}

.status p {
  margin: 3px 0;
}
</style>
