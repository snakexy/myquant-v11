/**
 * 国际化翻译文件
 * 简体中文 / English
 */

export const translations = {
  zh: {
    // 指标相关
    indicators: {
      title: '技术指标',
      oscillator: '独立指标',
      overlay: '主图叠加',
      button: '指标',

      // 指标名称
      macd: 'MACD',
      kdj: 'KDJ',
      skdj: 'SKDJ',
      rsi: 'RSI',
      cci: 'CCI',
      obv: 'OBV',
      wr: 'WR',
      atr: 'ATR',
      bias: 'BIAS',
      ma: 'MA',
      boll: '布林带',
      smc: 'SMC V2',

      // SKDJ 参数
      skdj_fastk_period: 'K值周期',
      skdj_slowk_period: 'K平滑周期',
      skdj_slowd_period: 'D周期',

      // KDJ 参数
      kdj_k_period: 'K值周期',
      kdj_d_period: 'D周期',
      kdj_j_period: 'J周期',

      // MACD 参数
      macd_fast: '快线周期',
      macd_slow: '慢线周期',
      macd_signal: '信号线周期',

      // 通用
      period: '周期',
      close: '关闭',
      settings: '设置'
    },

    // 其他常见文本
    common: {
      save: '保存',
      cancel: '取消',
      confirm: '确认',
      delete: '删除',
      edit: '编辑',
      add: '添加',
      remove: '移除',
      loading: '加载中...',
      noData: '暂无数据'
    }
  },

  en: {
    // Indicators
    indicators: {
      title: 'Technical Indicators',
      oscillator: 'Oscillators',
      overlay: 'Overlay',
      button: 'Indicators',

      // Indicator names
      macd: 'MACD',
      kdj: 'KDJ',
      skdj: 'SKDJ',
      rsi: 'RSI',
      cci: 'CCI',
      obv: 'OBV',
      wr: 'WR',
      atr: 'ATR',
      bias: 'BIAS',
      ma: 'MA',
      boll: 'Bollinger Bands',
      smc: 'SMC V2',

      // SKDJ parameters
      skdj_fastk_period: 'K Period',
      skdj_slowk_period: 'K Smoothing',
      skdj_slowd_period: 'D Period',

      // KDJ parameters
      kdj_k_period: 'K Period',
      kdj_d_period: 'D Period',
      kdj_j_period: 'J Period',

      // MACD parameters
      macd_fast: 'Fast Period',
      macd_slow: 'Slow Period',
      macd_signal: 'Signal Period',

      // Common
      period: 'Period',
      close: 'Close',
      settings: 'Settings'
    },

    // Common text
    common: {
      save: 'Save',
      cancel: 'Cancel',
      confirm: 'Confirm',
      delete: 'Delete',
      edit: 'Edit',
      add: 'Add',
      remove: 'Remove',
      loading: 'Loading...',
      noData: 'No Data'
    }
  }
}

export type Language = keyof typeof translations
export type TranslationKey = keyof typeof translations.zh
