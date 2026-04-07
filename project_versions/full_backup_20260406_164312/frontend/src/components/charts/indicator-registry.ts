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
