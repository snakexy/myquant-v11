/**
 * 因子评分颜色工具
 * 统一项目的五级色系规则
 *
 * 颜色映射（基于百分比得分）：
 * - 紫色 #8b5cf6: 卓越 (>100分)
 * - 红色 #ef5350: 优秀 (80-100分)
 * - 橙色 #f97316: 良好 (60-79分)
 * - 蓝色 #2962ff: 及格 (40-59分)
 * - 绿色 #26a69a: 较差 (<40分)
 *
 * 注意：此颜色规则用于因子评分，与中国股市涨跌颜色（红涨绿跌）是两套不同的体系
 */

/**
 * 五级色系常量
 */
export const FACTOR_COLORS = {
  EXCELLENT: '#8b5cf6',    // 紫色 - 卓越 (>100)
  OUTSTANDING: '#ef5350',  // 红色 - 优秀 (80-100)
  GOOD: '#f97316',         // 橙色 - 良好 (60-79)
  PASS: '#2962ff',         // 蓝色 - 及格 (40-59)
  POOR: '#26a69a'          // 绿色 - 较差 (<40)
} as const

/**
 * 获取因子评分颜色
 * 用于仪表盘、进度条、评分显示
 *
 * @param score 评分值 (0-100+)
 * @returns 对应的颜色值
 */
export const getFactorScoreColor = (score: number): string => {
  if (score > 100) return FACTOR_COLORS.EXCELLENT    // 紫色 - 卓越
  if (score >= 80) return FACTOR_COLORS.OUTSTANDING  // 红色 - 优秀
  if (score >= 60) return FACTOR_COLORS.GOOD         // 橙色 - 良好
  if (score >= 40) return FACTOR_COLORS.PASS         // 蓝色 - 及格
  return FACTOR_COLORS.POOR                          // 绿色 - 较差
}

/**
 * 获取因子中位数质量颜色
 * 用于分布图、统计卡片
 * 注意：中位数越小越好（接近0表示因子中性）
 *
 * @param median 中位数值
 * @returns 对应的颜色值
 */
export const getMedianQualityColor = (median: number): string => {
  const absMedian = Math.abs(median)
  if (absMedian <= 0.1) return '#ef5350'   // 红色 - 优秀
  if (absMedian <= 0.3) return '#ffa726'   // 橙色 - 良好
  if (absMedian <= 0.5) return '#afb42b'   // 黄绿色 - 一般
  return '#26a69a'                         // 绿色 - 较差
}

/**
 * 获取评分等级文字
 *
 * @param score 评分值 (0-100+)
 * @returns 中英文等级描述
 */
export const getScoreLevel = (score: number): { zh: string; en: string } => {
  if (score > 100) return { zh: '卓越', en: 'Excellent' }
  if (score >= 80) return { zh: '优秀', en: 'Outstanding' }
  if (score >= 60) return { zh: '良好', en: 'Good' }
  if (score >= 40) return { zh: '及格', en: 'Pass' }
  return { zh: '较差', en: 'Poor' }
}

/**
 * Element Plus Progress 组件颜色数组格式
 * 用于需要渐变效果的进度条
 */
export const FACTOR_COLOR_STEPS = [
  { color: FACTOR_COLORS.POOR, percentage: 40 },
  { color: FACTOR_COLORS.PASS, percentage: 60 },
  { color: FACTOR_COLORS.GOOD, percentage: 80 },
  { color: FACTOR_COLORS.OUTSTANDING, percentage: 100 },
  { color: FACTOR_COLORS.EXCELLENT, percentage: 120 }
]

/**
 * 获取涨跌颜色（中国股市风格：红涨绿跌）
 *
 * @param value 涨跌值（正数为涨，负数为跌）
 * @returns 对应的颜色值
 */
export const getPriceChangeColor = (value: number): string => {
  if (value > 0) return '#ef5350'   // 红色 - 涨
  if (value < 0) return '#26a69a'   // 绿色 - 跌
  return '#787b86'                  // 灰色 - 平
}
