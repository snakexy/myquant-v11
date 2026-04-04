import { ref, type Ref } from 'vue'

export interface VPBucket {
  price: number
  volume: number
  buyVolume: number
  sellVolume: number
  y: number
}

export interface VPStats {
  pocPrice: string
  pocVolume: number
  vaLow: string
  vaHigh: string
  vaVolume: number
}

export interface VPSelection {
  x: number
  y: number
  time: number
  price: number
}

export function useVolumeProfile() {
  const isVPActive = ref(false)
  const showVPCanvas = ref(false)
  const vpStats = ref<VPStats | null>(null)

  let selectionStart: VPSelection | null = null
  let selectionEnd: VPSelection | null = null
  let isSelecting = false

  const toggleVP = () => {
    isVPActive.value = !isVPActive.value
    showVPCanvas.value = isVPActive.value

    if (!isVPActive.value) {
      selectionStart = null
      selectionEnd = null
      vpStats.value = null
    }
  }

  const activateVP = () => {
    isVPActive.value = true
    showVPCanvas.value = true
  }

  const deactivateVP = () => {
    isVPActive.value = false
    showVPCanvas.value = false
    selectionStart = null
    selectionEnd = null
    vpStats.value = null
  }

  const startSelection = (x: number, y: number, time: number, price: number) => {
    selectionStart = { x, y, time, price }
    selectionEnd = { x, y, time, price }
    isSelecting = true
  }

  const updateSelection = (x: number, y: number, time: number, price: number) => {
    if (!isSelecting) return
    selectionEnd = { x, y, time, price }
  }

  const endSelection = () => {
    if (!isSelecting) return null
    isSelecting = false
    return { start: selectionStart!, end: selectionEnd! }
  }

  // 计算双向成交量分布
  const calculateVP = (
    klineData: any[],
    startTime: number,
    endTime: number,
    minPrice: number,
    maxPrice: number,
    priceToCoordinate: (price: number) => number | null
  ): { buckets: VPBucket[]; pocIndex: number; vaLow: number; vaHigh: number; maxVolume: number } | null => {
    const selectedBars = klineData.filter(d => d.time >= startTime && d.time <= endTime)
    if (selectedBars.length < 2) return null

    const highs = selectedBars.map(d => d.high)
    const lows = selectedBars.map(d => d.low)
    const barMaxPrice = Math.max(...highs)
    const barMinPrice = Math.min(...lows)
    const priceRange = barMaxPrice - barMinPrice

    if (priceRange === 0) return null

    const bucketCount = 30
    const buckets: VPBucket[] = []

    for (let i = 0; i < bucketCount; i++) {
      const bucketLow = barMinPrice + (priceRange * i) / bucketCount
      const bucketHigh = barMinPrice + (priceRange * (i + 1)) / bucketCount
      const bucketPrice = (bucketLow + bucketHigh) / 2

      let buyVolume = 0
      let sellVolume = 0

      for (const bar of selectedBars) {
        const overlapLow = Math.max(bar.low, bucketLow)
        const overlapHigh = Math.min(bar.high, bucketHigh)
        if (overlapHigh > overlapLow) {
          const overlapRatio = (overlapHigh - overlapLow) / (bar.high - bar.low)
          const vol = bar.volume * overlapRatio

          if (bar.close >= bar.open) {
            buyVolume += vol * 0.7
            sellVolume += vol * 0.3
          } else {
            buyVolume += vol * 0.3
            sellVolume += vol * 0.7
          }
        }
      }

      const y = priceToCoordinate(bucketPrice)
      buckets.push({
        price: bucketPrice,
        volume: buyVolume + sellVolume,
        buyVolume,
        sellVolume,
        y: y ?? 0
      })
    }

    const maxVolume = Math.max(...buckets.map(b => Math.max(b.buyVolume, b.sellVolume)))
    const pocIndex = buckets.findIndex(b => b.volume === Math.max(...buckets.map(x => x.volume)))

    const totalVolume = buckets.reduce((sum, b) => sum + b.volume, 0)
    const targetVA = totalVolume * 0.7

    let vaLow = pocIndex
    let vaHigh = pocIndex
    let currentVA = buckets[pocIndex].volume

    while (currentVA < targetVA && (vaLow > 0 || vaHigh < buckets.length - 1)) {
      const volBelow = vaLow > 0 ? buckets[vaLow - 1].volume : 0
      const volAbove = vaHigh < buckets.length - 1 ? buckets[vaHigh + 1].volume : 0

      if (volBelow >= volAbove && vaLow > 0) {
        vaLow--
        currentVA += buckets[vaLow].volume
      } else if (vaHigh < buckets.length - 1) {
        vaHigh++
        currentVA += buckets[vaHigh].volume
      } else {
        break
      }
    }

    vpStats.value = {
      pocPrice: buckets[pocIndex].price.toFixed(2),
      pocVolume: buckets[pocIndex].volume,
      vaLow: buckets[vaLow].price.toFixed(2),
      vaHigh: buckets[vaHigh].price.toFixed(2),
      vaVolume: currentVA
    }

    return { buckets, pocIndex, vaLow, vaHigh, maxVolume }
  }

  const drawSelection = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    if (!selectionStart || !selectionEnd) return

    const x = Math.min(selectionStart.x, selectionEnd.x)
    const y = Math.min(selectionStart.y, selectionEnd.y)
    const w = Math.abs(selectionEnd.x - selectionStart.x)
    const h = Math.abs(selectionEnd.y - selectionStart.y)

    ctx.fillStyle = 'rgba(33, 150, 243, 0.1)'
    ctx.fillRect(x, y, w, h)

    ctx.strokeStyle = 'rgba(33, 150, 243, 0.5)'
    ctx.lineWidth = 1
    ctx.setLineDash([4, 4])
    ctx.strokeRect(x, y, w, h)
    ctx.setLineDash([])
  }

  // 绘制双向成交量分布（在框选区域左侧）
  const drawVP = (
    ctx: CanvasRenderingContext2D,
    canvasWidth: number,
    canvasHeight: number,
    buckets: VPBucket[],
    maxVolume: number,
    pocIndex: number,
    vaLow: number,
    vaHigh: number,
    minPrice: number,
    maxPrice: number,
    priceToCoordinate: (price: number) => number | null
  ) => {
    if (!selectionStart || !selectionEnd) return

    const x1 = Math.min(selectionStart.x, selectionEnd.x)
    const x2 = Math.max(selectionStart.x, selectionEnd.x)
    // 使用固定宽度，基于整个图表宽度，不随框选区域变化
    const vpWidth = Math.min(canvasWidth * 0.12, 100) // 固定宽度最大100px

    // 重新计算Y坐标
    const bucketCoords = buckets.map((b, i) => ({
      ...b,
      y: priceToCoordinate(b.price)
    })).filter(b => b.y !== null)

    if (bucketCoords.length === 0) return

    // 计算行高
    let rowHeight = 16
    if (bucketCoords.length > 1) {
      const firstY = bucketCoords[0].y!
      const lastY = bucketCoords[bucketCoords.length - 1].y!
      const avgSpacing = Math.abs(lastY - firstY) / (bucketCoords.length - 1)
      rowHeight = Math.min(Math.max(avgSpacing * 0.9, 8), 20)
    }

    // 绘制VA背景（在整个选择区域）
    const vaBuckets = bucketCoords.filter((_, i) => i >= vaLow && i <= vaHigh)
    if (vaBuckets.length > 0) {
      const vaTopY = Math.min(...vaBuckets.map(b => b.y!))
      const vaBottomY = Math.max(...vaBuckets.map(b => b.y!))
      ctx.fillStyle = 'rgba(255, 255, 255, 0.03)'
      ctx.fillRect(x1, vaTopY - rowHeight/2, x2 - x1, vaBottomY - vaTopY + rowHeight)
    }

    // 绘制双向柱状图（中轴在框选最左边，买卖都向右）
    bucketCoords.forEach((bucket, i) => {
      const y = bucket.y! - rowHeight / 2
      const axisX = x1 // 中轴线在框选最左边

      // 卖方柱状图（下跌色 - 蓝色，从左向右）
      const sellWidth = (bucket.sellVolume / maxVolume) * vpWidth
      ctx.fillStyle = i === pocIndex ? 'rgba(66, 133, 244, 0.9)' : 'rgba(66, 133, 244, 0.6)'
      ctx.fillRect(axisX, y, sellWidth, rowHeight - 1)

      // 买方柱状图（上涨色 - 粉色，从卖柱右边继续向右）
      const buyWidth = (bucket.buyVolume / maxVolume) * vpWidth
      ctx.fillStyle = i === pocIndex ? 'rgba(255, 105, 180, 0.9)' : 'rgba(255, 105, 180, 0.6)'
      ctx.fillRect(axisX + sellWidth, y, buyWidth, rowHeight - 1)

      // 卖买分隔线
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
      ctx.lineWidth = 0.5
      ctx.beginPath()
      ctx.moveTo(axisX + sellWidth, y)
      ctx.lineTo(axisX + sellWidth, y + rowHeight - 1)
      ctx.stroke()
    })

    // 绘制中轴线（框选最左边）
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(x1, bucketCoords[0].y! - rowHeight)
    ctx.lineTo(x1, bucketCoords[bucketCoords.length - 1].y! + rowHeight)
    ctx.stroke()

    // 绘制POC标记
    const pocBucket = bucketCoords[pocIndex]
    if (pocBucket) {
      const pocY = pocBucket.y!

      // POC水平线
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)'
      ctx.lineWidth = 1
      ctx.setLineDash([3, 3])
      ctx.beginPath()
      ctx.moveTo(x1, pocY)
      ctx.lineTo(x2, pocY)
      ctx.stroke()
      ctx.setLineDash([])

      // POC标签（右侧）
      ctx.fillStyle = '#ffffff'
      ctx.font = 'bold 10px sans-serif'
      ctx.fillText(`POC ${pocBucket.price.toFixed(2)}`, x2 + 5, pocY + 3)
    }

    // 绘制VA边界
    const vaTopBucket = bucketCoords[vaHigh]
    const vaBottomBucket = bucketCoords[vaLow]
    if (vaTopBucket && vaBottomBucket) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)'
      ctx.lineWidth = 1
      ctx.setLineDash([3, 3])

      const vaTopY = vaTopBucket.y! - rowHeight/2
      const vaBottomY = vaBottomBucket.y! + rowHeight/2

      ctx.beginPath()
      ctx.moveTo(x1, vaTopY)
      ctx.lineTo(x2, vaTopY)
      ctx.moveTo(x1, vaBottomY)
      ctx.lineTo(x2, vaBottomY)
      ctx.stroke()
      ctx.setLineDash([])

      // VA标签（左侧）
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)'
      ctx.font = '9px sans-serif'
      ctx.fillText('VAH', x1 - 28, vaTopY + 3)
      ctx.fillText('VAL', x1 - 28, vaBottomY + 3)
    }

    // 绘制图例（左上角）
    const legendY = bucketCoords[0].y! - rowHeight - 20
    // 卖方 - 蓝色
    ctx.fillStyle = 'rgba(66, 133, 244, 0.8)'
    ctx.fillRect(x1 + 5, legendY, 8, 8)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.font = '10px sans-serif'
    ctx.fillText('卖', x1 + 18, legendY + 7)

    // 买方 - 粉色
    ctx.fillStyle = 'rgba(255, 105, 180, 0.8)'
    ctx.fillRect(x1 + 35, legendY, 8, 8)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.fillText('买', x1 + 48, legendY + 7)
  }

  const clearCanvas = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.clearRect(0, 0, width, height)
  }

  return {
    isVPActive,
    showVPCanvas,
    vpStats,
    isSelecting: () => isSelecting,
    selectionStart: () => selectionStart,
    selectionEnd: () => selectionEnd,
    toggleVP,
    activateVP,
    deactivateVP,
    startSelection,
    updateSelection,
    endSelection,
    calculateVP,
    drawSelection,
    drawVP,
    clearCanvas
  }
}
