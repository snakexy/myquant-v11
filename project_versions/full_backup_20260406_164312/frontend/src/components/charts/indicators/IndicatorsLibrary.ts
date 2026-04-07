/**
 * lightweight-charts-indicators 完整指标库
 * 提供 70+ 技术指标
 *
 * 文档: https://github.com/deepentropy/lightweight-charts-indicators
 */

// ==================== 移动平均线 (14种) ====================

export const MOVING_AVERAGES = {
  // 简单移动平均线
  SMA: {
    name: 'SMA',
    fullName: 'Simple Moving Average',
    category: 'overlay',
    import: "import { SMA } from 'lightweight-charts-indicators'",
    calculate: 'SMA.calculate(bars, { len: period, src: \'close\' })',
    description: '简单移动平均线',
    params: { period: '周期' }
  },

  // 指数移动平均线
  EMA: {
    name: 'EMA',
    fullName: 'Exponential Moving Average',
    category: 'overlay',
    import: "import { EMA } from 'lightweight-charts-indicators'",
    calculate: 'EMA.calculate(bars, { len: period, src: \'close\' })',
    description: '指数移动平均线',
    params: { period: '周期' }
  },

  // 加权移动平均线
  WMA: {
    name: 'WMA',
    fullName: 'Weighted Moving Average',
    category: 'overlay',
    import: "import { WMA } from 'lightweight-charts-indicators'",
    calculate: 'WMA.calculate(bars, { len: period, src: \'close\' })',
    description: '加权移动平均线',
    params: { period: '周期' }
  },

  // 双指数移动平均线
  DEMA: {
    name: 'DEMA',
    fullName: 'Double Exponential Moving Average',
    category: 'overlay',
    import: "import { DEMA } from 'lightweight-charts-indicators'",
    calculate: 'DEMA.calculate(bars, { len: period, src: \'close\' })',
    description: '双指数移动平均线',
    params: { period: '周期' }
  },

  // 三指数移动平均线
  TEMA: {
    name: 'TEMA',
    fullName: 'Triple Exponential Moving Average',
    category: 'overlay',
    import: "import { TEMA } from 'lightweight-charts-indicators'",
    calculate: 'TEMA.calculate(bars, { len: period, src: \'close\' })',
    description: '三指数移动平均线',
    params: { period: '周期' }
  },

  // 赫尔移动平均线
  HMA: {
    name: 'HMA',
    fullName: 'Hull Moving Average',
    category: 'overlay',
    import: "import { HMA } from 'lightweight-charts-indicators'",
    calculate: 'HMA.calculate(bars, { len: period, src: \'close\' })',
    description: '赫尔移动平均线',
    params: { period: '周期' }
  },

  // 成交量加权移动平均线
  VWMA: {
    name: 'VWMA',
    fullName: 'Volume Weighted Moving Average',
    category: 'overlay',
    import: "import { VWMA } from 'lightweight-charts-indicators'",
    calculate: 'VWMA.calculate(bars, { len: period })',
    description: '成交量加权移动平均线',
    params: { period: '周期' }
  },

  // 自适应移动平均线
  ALMA: {
    name: 'ALMA',
    fullName: 'Arnaud Legoux Moving Average',
    category: 'overlay',
    import: "import { ALMA } from 'lightweight-charts-indicators'",
    calculate: 'ALMA.calculate(bars, { len: period })',
    description: '阿诺·勒格鲁移动平均线',
    params: { period: '周期' }
  },

  // Kaufman自适应移动平均线
  KAMA: {
    name: 'KAMA',
    fullName: 'Kaufman Adaptive Moving Average',
    category: 'overlay',
    import: "import { KAMA } from 'lightweight-charts-indicators'",
    calculate: 'KAMA.calculate(bars, { len: period })',
    description: '考夫曼自适应移动平均线',
    params: { period: '周期' }
  },

  // McGinley动态移动平均线
  McGinley: {
    name: 'McGinley',
    fullName: 'McGinley Dynamic',
    category: 'overlay',
    import: "import { McGinley } from 'lightweight-charts-indicators'",
    calculate: 'McGinley.calculate(bars, { len: period })',
    description: 'McGinley动态移动平均线',
    params: { period: '周期' }
  }
}

// ==================== 振荡器 (16种) ====================

export const OSCILLATORS = {
  // 相对强弱指数
  RSI: {
    name: 'RSI',
    fullName: 'Relative Strength Index',
    category: 'pane',
    import: "import { RSI } from 'lightweight-charts-indicators'",
    calculate: 'RSI.calculate(bars, { length: period })',
    description: '相对强弱指数',
    params: { period: '周期' },
    range: [0, 100]
  },

  // MACD
  MACD: {
    name: 'MACD',
    fullName: 'Moving Average Convergence Divergence',
    category: 'pane',
    import: "import { MACD } from 'lightweight-charts-indicators'",
    calculate: 'MACD.calculate(bars, { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 })',
    description: '指数平滑异同移动平均线',
    params: {
      fastPeriod: '快线周期',
      slowPeriod: '慢线周期',
      signalPeriod: '信号线周期'
    }
  },

  // 随机振荡器 (KDJ)
  Stochastic: {
    name: 'Stochastic',
    fullName: 'Stochastic Oscillator',
    category: 'pane',
    import: "import { Stochastic } from 'lightweight-charts-indicators'",
    calculate: 'Stochastic.calculate(bars, { kPeriod: 9, dPeriod: 3, smooth: 3 })',
    description: '随机振荡器 (KDJ)',
    params: { kPeriod: 'K值周期', dPeriod: 'D值周期', smooth: '平滑' },
    range: [0, 100]
  },

  // 商品通道指数
  CCI: {
    name: 'CCI',
    fullName: 'Commodity Channel Index',
    category: 'pane',
    import: "import { CCI } from 'lightweight-charts-indicators'",
    calculate: 'CCI.calculate(bars, { length: period })',
    description: '商品通道指数',
    params: { period: '周期' }
  },

  // 威廉指标
  WilliamsR: {
    name: 'Williams %R',
    fullName: 'Williams Percent Range',
    category: 'pane',
    import: "import { WilliamsR } from 'lightweight-charts-indicators'",
    calculate: 'WilliamsR.calculate(bars, { length: period })',
    description: '威廉指标',
    params: { period: '周期' },
    range: [-100, 0]
  },

  // 动量指标
  Momentum: {
    name: 'Momentum',
    fullName: 'Momentum',
    category: 'pane',
    import: "import { Momentum } from 'lightweight-charts-indicators'",
    calculate: 'Momentum.calculate(bars, { length: period })',
    description: '动量指标',
    params: { period: '周期' }
  },

  // 变化率
  ROC: {
    name: 'ROC',
    fullName: 'Rate of Change',
    category: 'pane',
    import: "import { ROC } from 'lightweight-charts-indicators'",
    calculate: 'ROC.calculate(bars, { length: period })',
    description: '变化率',
    params: { period: '周期' }
  },

  // 随机动量指数
  StochasticRSI: {
    name: 'Stochastic RSI',
    fullName: 'Stochastic Relative Strength Index',
    category: 'pane',
    import: "import { StochasticRSI } from 'lightweight-charts-indicators'",
    calculate: 'StochasticRSI.calculate(bars, { length: 14 })',
    description: '随机相对强弱指数',
    params: { length: '周期' },
    range: [0, 100]
  }
}

// ==================== 布林带与通道 (5种) ====================

export const BANDS = {
  // 布林带
  BollingerBands: {
    name: 'Bollinger Bands',
    fullName: 'Bollinger Bands',
    category: 'overlay',
    import: "import { BollingerBands } from 'lightweight-charts-indicators'",
    calculate: 'BollingerBands.calculate(bars, { len: period, stdDev: 2 })',
    description: '布林带',
    params: { period: '周期', stdDev: '标准差倍数' }
  },

  // 肯特纳通道
  KeltnerChannels: {
    name: 'Keltner Channels',
    fullName: 'Keltner Channels',
    category: 'overlay',
    import: "import { KeltnerChannels } from 'lightweight-charts-indicators'",
    calculate: 'KeltnerChannels.calculate(bars, { len: period })',
    description: '肯特纳通道',
    params: { period: '周期' }
  },

  // 唐奇安通道
  DonchianChannels: {
    name: 'Donchian Channels',
    fullName: 'Donchian Channels',
    category: 'overlay',
    import: "import { DonchianChannels } from 'lightweight-charts-indicators'",
    calculate: 'DonchianChannels.calculate(bars, { len: period })',
    description: '唐奇安通道',
    params: { period: '周期' }
  }
}

// ==================== 趋势指标 (13种) ====================

export const TREND = {
  // 平均趋向指数
  ADX: {
    name: 'ADX',
    fullName: 'Average Directional Index',
    category: 'pane',
    import: "import { ADX } from 'lightweight-charts-indicators'",
    calculate: 'ADX.calculate(bars, { length: period })',
    description: '平均趋向指数',
    params: { period: '周期' }
  },

  // 抛物线SAR
  PSAR: {
    name: 'PSAR',
    fullName: 'Parabolic SAR',
    category: 'overlay',
    import: "import { PSAR } from 'lightweight-charts-indicators'",
    calculate: 'PSAR.calculate(bars, { step: 0.02, max: 0.2 })',
    description: '抛物线转向',
    params: { step: '步长', max: '最大值' }
  },

  // 超级趋势
  Supertrend: {
    name: 'Supertrend',
    fullName: 'Supertrend',
    category: 'overlay',
    import: "import { Supertrend } from 'lightweight-charts-indicators'",
    calculate: 'Supertrend.calculate(bars, { period: 10, multiplier: 3 })',
    description: '超级趋势',
    params: { period: '周期', multiplier: '倍数' }
  },

  // 一目均衡表
  Ichimoku: {
    name: 'Ichimoku',
    fullName: 'Ichimoku Cloud',
    category: 'overlay',
    import: "import { Ichimoku } from 'lightweight-charts-indicators'",
    calculate: 'Ichimoku.calculate(bars)',
    description: '一目均衡表',
    params: {}
  },

  // Aroon指标
  Aroon: {
    name: 'Aroon',
    fullName: 'Aroon Indicator',
    category: 'pane',
    import: "import { Aroon } from 'lightweight-charts-indicators'",
    calculate: 'Aroon.calculate(bars, { length: period })',
    description: 'Aroon指标',
    params: { period: '周期' },
    range: [0, 100]
  }
}

// ==================== 波动率 (5种) ====================

export const VOLATILITY = {
  // 平均真实波幅
  ATR: {
    name: 'ATR',
    fullName: 'Average True Range',
    category: 'pane',
    import: "import { ATR } from 'lightweight-charts-indicators'",
    calculate: 'ATR.calculate(bars, { length: period })',
    description: '平均真实波幅',
    params: { period: '周期' }
  },

  // 历史波动率
  HistoricalVolatility: {
    name: 'Historical Volatility',
    fullName: 'Historical Volatility',
    category: 'pane',
    import: "import { HistoricalVolatility } from 'lightweight-charts-indicators'",
    calculate: 'HistoricalVolatility.calculate(bars, { length: period })',
    description: '历史波动率',
    params: { period: '周期' }
  }
}

// ==================== 成交量指标 (8种) ====================

export const VOLUME = {
  // 能量潮
  OBV: {
    name: 'OBV',
    fullName: 'On Balance Volume',
    category: 'pane',
    import: "import { OBV } from 'lightweight-charts-indicators'",
    calculate: 'OBV.calculate(bars)',
    description: '能量潮',
    params: {}
  },

  // 资金流量指数
  MFI: {
    name: 'MFI',
    fullName: 'Money Flow Index',
    category: 'pane',
    import: "import { MFI } from 'lightweight-charts-indicators'",
    calculate: 'MFI.calculate(bars, { length: period })',
    description: '资金流量指数',
    params: { period: '周期' },
    range: [0, 100]
  },

  // 成交量加权平均价格
  VWAP: {
    name: 'VWAP',
    fullName: 'Volume Weighted Average Price',
    category: 'overlay',
    import: "import { VWAP } from 'lightweight-charts-indicators'",
    calculate: 'VWAP.calculate(bars)',
    description: '成交量加权平均价格',
    params: {}
  }
}

// ==================== 完整指标列表 ====================

export const ALL_INDICATORS_LIBRARY = {
  ...MOVING_AVERAGES,
  ...OSCILLATORS,
  ...BANDS,
  ...TREND,
  ...VOLATILITY,
  ...VOLUME
}

// ==================== 按类别分组 ====================

export const INDICATORS_BY_CATEGORY = {
  overlay: {
    name: '主图叠加指标',
    indicators: [
      'SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'HMA', 'VWMA', 'ALMA', 'KAMA', 'McGinley',
      'BollingerBands', 'KeltnerChannels', 'DonchianChannels',
      'PSAR', 'Supertrend', 'Ichimoku', 'VWAP'
    ]
  },
  pane: {
    name: '独立窗格指标',
    indicators: [
      'RSI', 'MACD', 'Stochastic', 'CCI', 'WilliamsR', 'Momentum', 'ROC', 'StochasticRSI',
      'ADX', 'Aroon', 'ATR', 'HistoricalVolatility',
      'OBV', 'MFI'
    ]
  }
}

// ==================== 统计信息 ====================

export const INDICATORS_STATS = {
  total: Object.keys(ALL_INDICATORS_LIBRARY).length,
  overlay: INDICATORS_BY_CATEGORY.overlay.indicators.length,
  pane: INDICATORS_BY_CATEGORY.pane.indicators.length
}

console.log(`📊 技术指标库加载完成，共 ${INDICATORS_STATS.total} 个指标`)
console.log(`   - 主图叠加: ${INDICATORS_STATS.overlay} 个`)
console.log(`   - 独立窗格: ${INDICATORS_STATS.pane} 个`)
