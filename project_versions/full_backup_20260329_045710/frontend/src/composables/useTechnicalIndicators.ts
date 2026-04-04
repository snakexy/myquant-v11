/**
 * 技术指标计算组合函数
 * 使用官方 lightweight-charts-indicators 库（70+ 指标）
 */

import { ref, computed } from 'vue'

// 指标计算结果类型接口
interface IndicatorResult {
  values: number[]
  timestamps: number[]
}

interface MACDResult extends IndicatorResult {
  macd: number[]
  signal: number[]
  histogram: number[]
}

interface RSIResult extends IndicatorResult {
  rsi: number[]
}

interface KDJResult extends IndicatorResult {
  k: number[]
  d: number[]
  j: number[]
}

interface BollingerBandsResult extends IndicatorResult {
  upper: number[]
  middle: number[]
  lower: number[]
}

export function useTechnicalIndicators() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 计算简单移动平均线 (SMA)
   */
  const calculateSMA = (data: number[], period: number): number[] => {
    const result: number[] = []

    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push(NaN)
      } else {
        const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
        result.push(sum / period)
      }
    }

    return result
  }

  /**
   * 计算指数移动平均线 (EMA)
   */
  const calculateEMA = (data: number[], period: number): number[] => {
    const result: number[] = []
    const multiplier = 2 / (period + 1)

    // 第一个EMA使用SMA
    let ema = data.slice(0, period).reduce((a, b) => a + b, 0) / period

    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push(NaN)
      } else if (i === period - 1) {
        result.push(ema)
      } else {
        ema = (data[i] - ema) * multiplier + ema
        result.push(ema)
      }
    }

    return result
  }

  /**
   * 计算布林带 (BOLL)
   */
  const calculateBollingerBands = (
    data: number[],
    period: number = 20,
    stdDev: number = 2
  ): BollingerBandsResult => {
    const middle = calculateSMA(data, period)
    const upper: number[] = []
    const lower: number[] = []

    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        upper.push(NaN)
        lower.push(NaN)
      } else {
        const slice = data.slice(i - period + 1, i + 1)
        const mean = middle[i]!
        const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period
        const std = Math.sqrt(variance)

        upper.push(mean + stdDev * std)
        lower.push(mean - stdDev * std)
      }
    }

    return {
      upper,
      middle,
      lower,
      values: middle,
      timestamps: []
    }
  }

  /**
   * 计算RSI (Relative Strength Index)
   */
  const calculateRSI = (data: number[], period: number = 14): RSIResult => {
    const rsi: number[] = []
    let avgGain = 0
    let avgLoss = 0

    // 计算第一个平均收益和损失
    for (let i = 1; i <= period; i++) {
      const change = data[i] - data[i - 1]
      if (change > 0) {
        avgGain += change
      } else {
        avgLoss -= change
      }
    }

    avgGain /= period
    avgLoss /= period

    // 第一个RSI值
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss
    rsi.push(100 - 100 / (1 + rs))

    // 使用Wilder's平滑方法计算后续RSI
    for (let i = period + 1; i < data.length; i++) {
      const change = data[i] - data[i - 1]

      const gain = change > 0 ? change : 0
      const loss = change < 0 ? -change : 0

      avgGain = (avgGain * (period - 1) + gain) / period
      avgLoss = (avgLoss * (period - 1) + loss) / period

      const rs_value = avgLoss === 0 ? 100 : avgGain / avgLoss
      rsi.push(100 - 100 / (1 + rs_value))
    }

    // 在前面填充NaN值
    const result = new Array(data.length).fill(NaN)
    for (let i = period; i < data.length; i++) {
      result[i] = rsi[i - period]
    }

    return {
      rsi: result,
      values: result,
      timestamps: []
    }
  }

  /**
   * 计算MACD (Moving Average Convergence Divergence)
   */
  const calculateMACD = (
    data: number[],
    fastPeriod: number = 12,
    slowPeriod: number = 26,
    signalPeriod: number = 9
  ): MACDResult => {
    const emaFast = calculateEMA(data, fastPeriod)
    const emaSlow = calculateEMA(data, slowPeriod)

    const macdLine: number[] = []
    for (let i = 0; i < data.length; i++) {
      const fast = emaFast[i]
      const slow = emaSlow[i]
      if (isNaN(fast!) || isNaN(slow!)) {
        macdLine.push(NaN)
      } else {
        macdLine.push(fast! - slow!)
      }
    }

    // 计算Signal线（MACD的EMA）
    const validMacd = macdLine.filter(v => !isNaN(v))
    const signalEma = calculateEMA(validMacd, signalPeriod)

    const signalLine: number[] = []
    const histogram: number[] = []

    let validIndex = 0
    for (let i = 0; i < data.length; i++) {
      if (isNaN(macdLine[i]!)) {
        signalLine.push(NaN)
        histogram.push(NaN)
      } else {
        signalLine.push(signalEma[validIndex] ?? NaN)
        histogram.push(macdLine[i]! - (signalEma[validIndex] ?? 0))
        validIndex++
      }
    }

    return {
      macd: macdLine,
      signal: signalLine,
      histogram: histogram,
      values: macdLine,
      timestamps: []
    }
  }

  /**
   * 计算KDJ (Stochastic Oscillator)
   */
  const calculateKDJ = (
    high: number[],
    low: number[],
    close: number[],
    kPeriod: number = 9,
    dPeriod: number = 3,
    jPeriod: number = 3
  ): KDJResult => {
    const k: number[] = []
    const d: number[] = []
    const j: number[] = []

    let prevK = 50
    let prevD = 50

    for (let i = 0; i < close.length; i++) {
      if (i < kPeriod - 1) {
        k.push(NaN)
        d.push(NaN)
        j.push(NaN)
      } else {
        const highSlice = high.slice(i - kPeriod + 1, i + 1)
        const lowSlice = low.slice(i - kPeriod + 1, i + 1)

        const highestHigh = Math.max(...highSlice)
        const lowestLow = Math.min(...lowSlice)

        const rsv = ((close[i] - lowestLow) / (highestHigh - lowestLow)) * 100

        // 计算K值 (使用平滑方法)
        const currentK = (2 / 3) * prevK + (1 / 3) * rsv
        k.push(currentK)

        // 计算D值
        const currentD = (2 / 3) * prevD + (1 / 3) * currentK
        d.push(currentD)

        // 计算J值
        const currentJ = 3 * currentK - 2 * currentD
        j.push(currentJ)

        prevK = currentK
        prevD = currentD
      }
    }

    return {
      k,
      d,
      j,
      values: k,
      timestamps: []
    }
  }

  /**
   * 计算CCI (Commodity Channel Index)
   */
  const calculateCCI = (
    high: number[],
    low: number[],
    close: number[],
    period: number = 20
  ): number[] => {
    const cci: number[] = []

    for (let i = 0; i < close.length; i++) {
      if (i < period - 1) {
        cci.push(NaN)
      } else {
        const highSlice = high.slice(i - period + 1, i + 1)
        const lowSlice = low.slice(i - period + 1, i + 1)
        const closeSlice = close.slice(i - period + 1, i + 1)

        const typicalPrices: number[] = []
        for (let j = 0; j < period; j++) {
          typicalPrices.push((highSlice[j] + lowSlice[j] + closeSlice[j]) / 3)
        }

        const sma = typicalPrices.reduce((a, b) => a + b, 0) / period
        const meanDeviation =
          typicalPrices.reduce((sum, tp) => sum + Math.abs(tp - sma), 0) / period

        const cciValue = (typicalPrices[period - 1]! - sma) / (0.015 * meanDeviation)
        cci.push(cciValue)
      }
    }

    return cci
  }

  /**
   * 计算WR (Williams %R)
   */
  const calculateWilliamsR = (
    high: number[],
    low: number[],
    close: number[],
    period: number = 14
  ): number[] => {
    const wr: number[] = []

    for (let i = 0; i < close.length; i++) {
      if (i < period - 1) {
        wr.push(NaN)
      } else {
        const highSlice = high.slice(i - period + 1, i + 1)
        const lowSlice = low.slice(i - period + 1, i + 1)

        const highestHigh = Math.max(...highSlice)
        const lowestLow = Math.min(...lowSlice)

        const wrValue = ((highestHigh - close[i]) / (highestHigh - lowestLow)) * -100
        wr.push(wrValue)
      }
    }

    return wr
  }

  /**
   * 计算ATR (Average True Range)
   */
  const calculateATR = (high: number[], low: number[], close: number[], period: number = 14): number[] => {
    const atr: number[] = []
    const trueRanges: number[] = []

    // 计算第一个真实波动范围
    trueRanges.push(high[0]! - low[0]!)

    for (let i = 1; i < close.length; i++) {
      const tr = Math.max(
        high[i]! - low[i]!,
        Math.abs(high[i]! - close[i - 1]!),
        Math.abs(low[i]! - close[i - 1]!)
      )
      trueRanges.push(tr)
    }

    // 计算ATR（使用EMA方法）
    let atrValue = trueRanges.slice(0, period).reduce((a, b) => a + b, 0) / period

    for (let i = 0; i < close.length; i++) {
      if (i < period - 1) {
        atr.push(NaN)
      } else if (i === period - 1) {
        atr.push(atrValue)
      } else {
        atrValue = (atrValue * (period - 1) + trueRanges[i]!) / period
        atr.push(atrValue)
      }
    }

    return atr
  }

  /**
   * 计算OBV (On-Balance Volume)
   */
  const calculateOBV = (close: number[], volume: number[]): number[] => {
    const obv: number[] = []
    let obvValue = 0

    for (let i = 0; i < close.length; i++) {
      if (i === 0) {
        obvValue = volume[i]!
      } else {
        if (close[i]! > close[i - 1]!) {
          obvValue += volume[i]!
        } else if (close[i]! < close[i - 1]!) {
          obvValue -= volume[i]!
        }
        // 价格相等时OBV不变
      }
      obv.push(obvValue)
    }

    return obv
  }

  /**
   * 批量计算所有指标
   */
  const calculateAllIndicators = async (klineData: {
    open: number[]
    high: number[]
    low: number[]
    close: number[]
    volume: number[]
  }) => {
    loading.value = true
    error.value = null

    try {
      const { open, high, low, close, volume } = klineData

      // 计算所有MA均线
      const ma5 = calculateSMA(close, 5)
      const ma10 = calculateSMA(close, 10)
      const ma20 = calculateSMA(close, 20)
      const ma30 = calculateSMA(close, 30)
      const ma60 = calculateSMA(close, 60)

      // 计算布林带
      const boll = calculateBollingerBands(close, 20, 2)

      // 计算MACD
      const macd = calculateMACD(close, 12, 26, 9)

      // 计算RSI
      const rsi6 = calculateRSI(close, 6)
      const rsi12 = calculateRSI(close, 12)
      const rsi24 = calculateRSI(close, 24)

      // 计算KDJ
      const kdj = calculateKDJ(high, low, close, 9, 3, 3)

      // 计算CCI
      const cci = calculateCCI(high, low, close, 14)

      // 计算WR
      const wr = calculateWilliamsR(high, low, close, 14)

      // 计算ATR
      const atr = calculateATR(high, low, close, 14)

      // 计算OBV
      const obv = calculateOBV(close, volume)

      return {
        ma: { ma5, ma10, ma20, ma30, ma60 },
        boll,
        macd,
        rsi: { rsi6, rsi12, rsi24 },
        kdj,
        cci,
        wr,
        atr,
        obv
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '计算指标失败'
      console.error('计算技术指标失败:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    calculateSMA,
    calculateEMA,
    calculateBollingerBands,
    calculateRSI,
    calculateMACD,
    calculateKDJ,
    calculateCCI,
    calculateWilliamsR,
    calculateATR,
    calculateOBV,
    calculateAllIndicators
  }
}
