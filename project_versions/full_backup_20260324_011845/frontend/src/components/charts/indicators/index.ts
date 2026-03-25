/**
 * 技术指标模块 - 统一导出
 *
 * 使用官方 lightweight-charts-indicators 库
 * https://github.com/tradingview/lightweight-charts-indicators
 */

// ==================== 主图叠加指标 ====================

export {
  addMAIndicator,
  getMAConfigs,
  MA_PERIODS
} from './MA'

export {
  addBOLLIndicator
} from './BOLL'

// ==================== 独立窗格指标 ====================

export {
  addMACDIndicator
} from './MACD'

export {
  addRSIIndicator
} from './RSI'

export {
  addKDJIndicator
} from './KDJ'

export {
  addCCIIndicator
} from './CCI'

export {
  addWRIndicator
} from './WR'

export {
  addATRIndicator
} from './ATR'

export {
  addOBVIndicator
} from './OBV'

// ==================== 新增指标 (2026-01-30) ====================

export {
  addStochasticIndicator
} from './Stochastic'

export {
  addADXIndicator
} from './ADX'

export {
  addSupertrendIndicator,
  getSupertrendConfig
} from './Supertrend'

export {
  addPSARIndicator
} from './PSAR'

export {
  addVWAPIndicator
} from './VWAP'

// ==================== 类型导出 ====================

export type { MAConfig } from './MA'
export type { SupertrendConfig } from './Supertrend'

// ==================== 指标元数据 ====================

/**
 * 指标窗格索引配置
 * pane 0: 主图（K线 + 成交量 + 叠加指标）
 * pane 1-9: 独立窗格指标
 */
export const INDICATOR_PANES = {
  MACD: 1,
  RSI: 2,
  KDJ: 3,
  CCI: 4,
  WR: 5,
  ATR: 6,
  OBV: 7,
  STOCHASTIC: 8,
  ADX: 9
} as const

/**
 * 主图叠加指标列表
 */
export const OVERLAY_INDICATORS = [
  'MA5',
  'MA10',
  'MA20',
  'MA30',
  'MA60',
  'BOLL',
  'SUPERTREND',
  'PSAR',  // 【v9.2.1 新增】
  'VWAP'   // 【v9.2.1 新增】
] as const

/**
 * 独立窗格指标列表
 */
export const PANE_INDICATORS = [
  'MACD',
  'RSI',
  'KDJ',
  'CCI',
  'WR',
  'ATR',
  'OBV',
  'STOCHASTIC',  // 新增
  'ADX'           // 新增
] as const

/**
 * 所有支持的指标
 */
export const ALL_INDICATORS = [
  ...OVERLAY_INDICATORS,
  ...PANE_INDICATORS,
  'VOL'  // 成交量（特殊处理）
] as const

/**
 * 指标默认窗格高度（像素）
 */
export const DEFAULT_PANE_HEIGHTS = {
  MACD: 150,
  RSI: 120,
  KDJ: 120,
  CCI: 120,
  WR: 120,
  ATR: 120,
  OBV: 120,
  STOCHASTIC: 150,  // 新增
  ADX: 150           // 新增
} as const
