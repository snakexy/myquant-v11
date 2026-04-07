/**
 * 技术指标注册表
 * 定义所有支持的技术指标配置
 */

export type IndicatorType = 'oscillator' | 'overlay' | 'volume';

export interface SeriesConfig {
  key: string;
  label: string;
  color: string;
  lineWidth?: number;
  type: 'line' | 'histogram' | 'area';
}

export interface IndicatorConfig {
  id: string;
  name: string;
  type: IndicatorType;
  defaultParams: Record<string, number | number[]>;
  series: SeriesConfig[];
  paneHeight?: number;
}

export const INDICATOR_REGISTRY: Record<string, IndicatorConfig> = {
  // 独立指标 - MACD
  MACD: {
    id: 'MACD',
    name: 'MACD',
    type: 'oscillator',
    defaultParams: { fast: 12, slow: 26, signal: 9 },
    series: [
      { key: 'macd', label: 'MACD', color: '#FF6B6B', type: 'line', lineWidth: 2 },
      { key: 'signal', label: 'Signal', color: '#26A69A', type: 'line', lineWidth: 2 },
      { key: 'histogram', label: 'Hist', color: '#2196F3', type: 'histogram' }
    ],
    paneHeight: 120
  },

  // 独立指标 - KDJ
  KDJ: {
    id: 'KDJ',
    name: 'KDJ',
    type: 'oscillator',
    defaultParams: { kPeriod: 9, dPeriod: 3, jPeriod: 3 },
    series: [
      { key: 'k', label: 'K', color: '#FF6B6B', type: 'line', lineWidth: 2 },
      { key: 'd', label: 'D', color: '#26A69A', type: 'line', lineWidth: 2 },
      { key: 'j', label: 'J', color: '#2196F3', type: 'line', lineWidth: 2 }
    ],
    paneHeight: 120
  },

  // 独立指标 - SKDJ（慢速随机指标，通达信公式：只有SK和SD，没有SJ）
  SKDJ: {
    id: 'SKDJ',
    name: 'SKDJ',
    type: 'oscillator',
    defaultParams: { fastk_period: 9, slowk_period: 3, slowd_period: 3 },
    series: [
      { key: 'sk', label: 'SK', color: '#FF6B6B', type: 'line', lineWidth: 2 },
      { key: 'sd', label: 'SD', color: '#26A69A', type: 'line', lineWidth: 2 }
    ],
    paneHeight: 120
  },

  // 独立指标 - RSI
  RSI: {
    id: 'RSI',
    name: 'RSI',
    type: 'oscillator',
    defaultParams: { period: 14 },
    series: [
      { key: 'rsi', label: 'RSI', color: '#2196F3', type: 'line', lineWidth: 2 }
    ],
    paneHeight: 120
  },

  // 独立指标 - CCI
  CCI: {
    id: 'CCI',
    name: 'CCI',
    type: 'oscillator',
    defaultParams: { period: 14 },
    series: [
      { key: 'cci', label: 'CCI', color: '#FF9800', type: 'line', lineWidth: 2 }
    ],
    paneHeight: 120
  },

  // 独立指标 - OBV
  OBV: {
    id: 'OBV',
    name: 'OBV',
    type: 'volume',
    defaultParams: { period: 12 },
    series: [
      { key: 'obv', label: 'OBV', color: '#9C27B0', type: 'line', lineWidth: 2 },
      { key: 'maobv', label: 'MAOBV', color: '#FFD700', type: 'line', lineWidth: 1 }
    ],
    paneHeight: 120
  },

  // 独立指标 - WR（威廉指标）
  WR: {
    id: 'WR',
    name: 'WR',
    type: 'oscillator',
    defaultParams: { period: 14 },
    series: [
      { key: 'wr', label: 'WR', color: '#E91E63', type: 'line', lineWidth: 2 }
    ],
    paneHeight: 120
  },

  // 独立指标 - ATR（平均真实波幅）
  ATR: {
    id: 'ATR',
    name: 'ATR',
    type: 'oscillator',
    defaultParams: { period: 14 },
    series: [
      { key: 'atr', label: 'ATR', color: '#FF9800', type: 'line', lineWidth: 2 }
    ],
    paneHeight: 120
  },

  // 独立指标 - BIAS（乖离率）
  BIAS: {
    id: 'BIAS',
    name: 'BIAS',
    type: 'oscillator',
    defaultParams: { period: 6 },
    series: [
      { key: 'bias', label: 'BIAS', color: '#00BCD4', type: 'line', lineWidth: 2 }
    ],
    paneHeight: 120
  },

  // 主图叠加 - MA
  MA: {
    id: 'MA',
    name: 'MA',
    type: 'overlay',
    defaultParams: { periods: [5, 10, 20, 30, 60] },
    series: [
      { key: 'ma5', label: 'MA5', color: '#FFFFFF', type: 'line', lineWidth: 1 },
      { key: 'ma10', label: 'MA10', color: '#FFFF00', type: 'line', lineWidth: 1 },
      { key: 'ma20', label: 'MA20', color: '#FF00FF', type: 'line', lineWidth: 1 },
      { key: 'ma30', label: 'MA30', color: '#00FFFF', type: 'line', lineWidth: 1 },
      { key: 'ma60', label: 'MA60', color: '#00FF00', type: 'line', lineWidth: 1 }
    ]
  },

  // 主图叠加 - BOLL
  BOLL: {
    id: 'BOLL',
    name: '布林带',
    type: 'overlay',
    defaultParams: { period: 20, stdDev: 2 },
    series: [
      { key: 'upper', label: 'UP', color: '#FF6B6B', type: 'line', lineWidth: 1 },
      { key: 'middle', label: 'MID', color: '#26A69A', type: 'line', lineWidth: 1 },
      { key: 'lower', label: 'LOW', color: '#FF6B6B', type: 'line', lineWidth: 1 }
    ]
  },

  // 主图叠加 - SMC V2 (Smart Money Concepts)
  SMC: {
    id: 'SMC',
    name: 'SMC V2',
    type: 'overlay',
    defaultParams: {
      swing_length: 5,
      close_break: true,
      show_swing_points: true,
      show_bms: true,
      show_choch: true,
      show_ob: true,
      show_fvg: true,
      // BMS/CHoCH 显示数量
      bos_count: 5,
      choch_count: 5,
      // OB/FVG 显示数量
      ob_count: 5,
      fvg_count: 5,
      // BMS 线条参数
      bms_box_size: 8,
      bms_line_style: 1,
      bms_line_width: 1,
      // CHoCH 线条参数
      choch_diamond_size: 6,
      choch_line_style: 1,
      choch_line_width: 1,
      // 颜色配置 (TradingView V2 风格)
      swing_high_color: '#00D9FF',  // 亮青色
      swing_low_color: '#FF61D2',   // 亮粉色
      bms_color: '#FFD700',         // 金色
      choch_color: '#9C27B0',       // 紫色
      ob_bullish: '#00D9FF',        // 青色
      ob_bearish: '#FF61D2',        // 粉色
      ob_opacity: 15,
      fvg_bullish: '#4CAF50',       // 绿色
      fvg_bearish: '#F44336',       // 红色
      fvg_opacity: 12,
    },
    series: [
      { key: 'swing_highs', label: 'SwingH', color: '#00D9FF', type: 'line', lineWidth: 2 },
      { key: 'swing_lows', label: 'SwingL', color: '#FF61D2', type: 'line', lineWidth: 2 }
    ]
  }
};

export type IndicatorId = keyof typeof INDICATOR_REGISTRY;

// 获取独立指标列表（包括 oscillator 和 volume 类型）
export const getOscillatorIndicators = () =>
  Object.values(INDICATOR_REGISTRY).filter(i => i.type === 'oscillator' || i.type === 'volume');

// 获取主图叠加指标列表
export const getOverlayIndicators = () =>
  Object.values(INDICATOR_REGISTRY).filter(i => i.type === 'overlay');

// 获取指标配置
export const getIndicatorConfig = (id: string): IndicatorConfig | undefined =>
  INDICATOR_REGISTRY[id];
