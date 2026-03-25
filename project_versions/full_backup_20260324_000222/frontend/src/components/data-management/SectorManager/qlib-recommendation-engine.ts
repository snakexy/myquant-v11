/**
 * QLib 官方方法论 - 板块智能推荐引擎
 *
 * 基于 QLib 官方文档的三大核心支柱：
 * 1. 价格走势相关性 - 通过 Corr 操作符计算
 * 2. 风险归因分析 - 通过 risk_analysis 和 brinson_pa
 * 3. IC 分析 - 预测值与真实值的相关性
 */

import type { SectorNode } from '@/components/data-management/shared/types'

// ==================== 类型定义 ====================

export interface QLibRecommendationResult {
  sector: SectorNode
  relevanceScore: number      // 综合相关性得分 (0-100)
  reasons: QLibRecommendationReason[]
  metrics: {
    // 核心支柱1：价格相关性
    priceCorrelation?: {
      coefficient: number      // 皮尔逊相关系数 [-1, 1]
      significance: number     // 统计显著性 p-value
      laggedCorrelation?: number  // 滞后相关性（用于因果关系分析）
    }
    // 核心支柱2：风险归因分析
    riskAttribution?: {
      systematicRisk: number   // 系统性风险 (β)
      specificRisk: number     // 特异性风险
      totalRisk: number        // 总风险
      brinsonAttribution?: {
        allocation: number     // 配置效应
        selection: number      // 选择效应
        interaction: number    // 交互效应
      }
    }
    // 核心支柱3：IC 分析
    icAnalysis?: {
      ic: number               // IC 值 (预测相关性)
      rankIC: number           // Rank IC (排名相关性)
      icStd: number            // IC 标准差
      ir: number               // Information Ratio (IC/IC_STD)
    }
    // 辅助指标
    industryRelation?: number  // 行业关联度 [0, 1]
    userBehavior?: number      // 用户行为得分 [0, 1]
  }
}

export interface QLibRecommendationReason {
  type: 'price_corr' | 'risk_attribution' | 'ic_analysis' | 'industry' | 'behavior'
  label: string
  description: string
  weight: number              // 权重 (0-100)
  score: number               // 得分 (0-100)
  impact: 'critical' | 'high' | 'medium' | 'low'
  qlibRef?: string            // QLib 文档引用
}

// 权重配置（严格按照 QLib 方法论）
const QLIB_WEIGHTS = {
  PRICE_CORRELATION: 50,      // 价格相关性 - 最重要
  RISK_ATTRIBUTION: 30,       // 风险归因分析
  IC_ANALYSIS: 15,            // IC 分析
  INDUSTRY_RELATION: 3,       // 行业关联 - 辅助
  USER_BEHAVIOR: 2            // 用户行为 - 辅助
}

// ==================== QLib 核心支柱实现 ====================

/**
 * 核心支柱 1: 价格相关性分析
 * 参考 QLib Corr 操作符
 * 文档: https://qlib.readthedocs.io/en/latest/reference/api.html#Corr
 *
 * 计算两个板块之间的价格相关性，包括：
 * - 皮尔逊相关系数
 * - 统计显著性 (t-test)
 * - 滞后相关性 (Granger 因果关系)
 */
function calculatePriceCorrelation(
  pricesA: number[],
  pricesB: number[]
): QLibRecommendationResult['metrics']['priceCorrelation'] {
  const n = Math.min(pricesA.length, pricesB.length)
  if (n < 30) return undefined  // 样本量不足

  const seriesA = pricesA.slice(0, n)
  const seriesB = pricesB.slice(0, n)

  // 1. 计算皮尔逊相关系数 (Pearson Correlation)
  const pearsonCorr = calculatePearsonCorrelation(seriesA, seriesB)

  // 2. 计算统计显著性 (t-test)
  const tStat = pearsonCorr * Math.sqrt((n - 2) / (1 - pearsonCorr * pearsonCorr))
  const pValue = 2 * (1 - normalCDF(Math.abs(tStat)))  // 双尾检验

  // 3. 计算滞后相关性 (Granger 因果关系分析)
  let laggedCorrelation: number | undefined
  if (n > 60) {
    laggedCorrelation = calculateLaggedCorrelation(seriesA, seriesB, 5)  // 5期滞后
  }

  return {
    coefficient: pearsonCorr,
    significance: pValue,
    laggedCorrelation
  }
}

/**
 * 计算皮尔逊相关系数
 * Corr(X, Y) = Cov(X, Y) / (σX * σY)
 */
function calculatePearsonCorrelation(x: number[], y: number[]): number {
  const n = x.length
  if (n !== y.length || n < 2) return 0

  // 计算均值
  const meanX = x.reduce((a, b) => a + b, 0) / n
  const meanY = y.reduce((a, b) => a + b, 0) / n

  // 计算协方差和方差
  let covariance = 0
  let varianceX = 0
  let varianceY = 0

  for (let i = 0; i < n; i++) {
    const diffX = x[i] - meanX
    const diffY = y[i] - meanY
    covariance += diffX * diffY
    varianceX += diffX * diffX
    varianceY += diffY * diffY
  }

  covariance /= (n - 1)
  varianceX /= (n - 1)
  varianceY /= (n - 1)

  const stdX = Math.sqrt(varianceX)
  const stdY = Math.sqrt(varianceY)

  if (stdX === 0 || stdY === 0) return 0

  return covariance / (stdX * stdY)
}

/**
 * 计算滞后相关性 (用于 Granger 因果关系分析)
 */
function calculateLaggedCorrelation(x: number[], y: number[], maxLag: number): number {
  let maxCorr = 0

  for (let lag = 1; lag <= maxLag; lag++) {
    if (x.length - lag < 30) continue

    const xLagged = x.slice(lag)
    const yShifted = y.slice(0, -lag)

    const corr = calculatePearsonCorrelation(xLagged, yShifted)
    if (Math.abs(corr) > Math.abs(maxCorr)) {
      maxCorr = corr
    }
  }

  return maxCorr
}

/**
 * 标准正态分布累积分布函数
 */
function normalCDF(x: number): number {
  const a1 = 0.254829592
  const a2 = -0.284496736
  const a3 = 1.421413741
  const a4 = -1.453152027
  const a5 = 1.061405429
  const p = 0.3275911

  const sign = x < 0 ? -1 : 1
  x = Math.abs(x) / Math.sqrt(2)

  const t = 1.0 / (1.0 + p * x)
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x)

  return 0.5 * (1.0 + sign * y)
}

/**
 * 核心支柱 2: 风险归因分析
 * 参考 QLib risk_analysis 和 brinson_pa
 * 文档: https://qlib.readthedocs.io/en/latest/component/report.html
 *
 * 分析板块的风险特征，包括：
 * - 系统性风险 (β)
 * - 特异性风险
 * - Brinson 归因分析
 */
function calculateRiskAttribution(
  returnsA: number[],
  returnsB: number[],
  marketReturns?: number[]
): QLibRecommendationResult['metrics']['riskAttribution'] {
  const n = Math.min(returnsA.length, returnsB.length)
  if (n < 30) return undefined

  const seriesA = returnsA.slice(0, n)
  const seriesB = returnsB.slice(0, n)

  // 1. 计算系统性风险 (β)
  // β = Cov(A, B) / Var(B)
  const beta = calculateBeta(seriesA, seriesB)

  // 2. 计算特异性风险
  const totalRiskA = calculateStdDev(seriesA)
  const systematicRisk = Math.abs(beta) * calculateStdDev(seriesB)
  const specificRisk = Math.sqrt(Math.abs(totalRiskA * totalRiskA - systematicRisk * systematicRisk))

  // 3. Brinson 归因分析 (如果有市场组合数据)
  let brinsonAttribution: { allocation: number; selection: number; interaction: number } | undefined
  if (marketReturns && marketReturns.length >= n) {
    brinsonAttribution = calculateBrinsonAttribution(
      seriesA,
      seriesB,
      marketReturns.slice(0, n)
    )
  }

  return {
    systematicRisk: beta,
    specificRisk: specificRisk,
    totalRisk: totalRiskA,
    brinsonAttribution
  }
}

/**
 * 计算 Beta 系数
 * β = Cov(A, B) / Var(B)
 */
function calculateBeta(returns: number[], marketReturns: number[]): number {
  const n = returns.length
  if (n !== marketReturns.length || n < 2) return 0

  const meanReturns = returns.reduce((a, b) => a + b, 0) / n
  const meanMarket = marketReturns.reduce((a, b) => a + b, 0) / n

  let covariance = 0
  let variance = 0

  for (let i = 0; i < n; i++) {
    const diffReturn = returns[i] - meanReturns
    const diffMarket = marketReturns[i] - meanMarket
    covariance += diffReturn * diffMarket
    variance += diffMarket * diffMarket
  }

  covariance /= (n - 1)
  variance /= (n - 1)

  if (variance === 0) return 0

  return covariance / variance
}

/**
 * 计算标准差
 */
function calculateStdDev(series: number[]): number {
  const n = series.length
  if (n < 2) return 0

  const mean = series.reduce((a, b) => a + b, 0) / n
  let variance = 0

  for (let i = 0; i < n; i++) {
    variance += (series[i] - mean) ** 2
  }

  return Math.sqrt(variance / (n - 1))
}

/**
 * Brinson 归因分析
 * 分解超额收益为：配置效应 + 选择效应 + 交互效应
 */
function calculateBrinsonAttribution(
  returns: number[],
  benchmarkReturns: number[],
  marketReturns: number[]
): { allocation: number; selection: number; interaction: number } {
  const n = returns.length

  // 计算平均收益率
  const avgReturn = returns.reduce((a, b) => a + b, 0) / n
  const avgBenchmark = benchmarkReturns.reduce((a, b) => a + b, 0) / n
  const avgMarket = marketReturns.reduce((a, b) => a + b, 0) / n

  // 配置效应: (基准权重 - 市场权重) * (基准收益率 - 市场收益率)
  const allocation = (avgBenchmark - avgMarket) * (avgBenchmark - avgMarket)

  // 选择效应: 市场权重 * (组合收益率 - 基准收益率)
  const selection = avgMarket * (avgReturn - avgBenchmark)

  // 交互效应: (基准权重 - 市场权重) * (组合收益率 - 基准收益率)
  const interaction = (avgBenchmark - avgMarket) * (avgReturn - avgBenchmark)

  return {
    allocation,
    selection,
    interaction
  }
}

/**
 * 核心支柱 3: IC 分析 (Information Coefficient)
 * 参考 QLib IC 分析
 * 文档: https://qlib.readthedocs.io/en/latest/component/analysis.html
 *
 * IC = Corr(Prediction, Realization)
 * 衡量预测值与真实值的相关性
 */
function calculateICAnalysis(
  predictions: number[],
  realizations: number[]
): QLibRecommendationResult['metrics']['icAnalysis'] {
  const n = Math.min(predictions.length, realizations.length)
  if (n < 30) return undefined

  const preds = predictions.slice(0, n)
  const reals = realizations.slice(0, n)

  // 1. 计算常规 IC (Pearson correlation)
  const ic = calculatePearsonCorrelation(preds, reals)

  // 2. 计算 Rank IC (Spearman correlation)
  const rankIC = calculateRankCorrelation(preds, reals)

  // 3. 计算 IC 标准差
  const icSeries: number[] = []
  const windowSize = Math.min(20, Math.floor(n / 2))

  for (let i = windowSize; i < n; i++) {
    const windowPreds = preds.slice(i - windowSize, i)
    const windowReals = reals.slice(i - windowSize, i)
    const windowIC = calculatePearsonCorrelation(windowPreds, windowReals)
    icSeries.push(windowIC)
  }

  const icStd = calculateStdDev(icSeries)

  // 4. 计算 IR (Information Ratio)
  const ir = icStd !== 0 ? Math.abs(ic / icStd) : 0

  return {
    ic,
    rankIC,
    icStd,
    ir
  }
}

/**
 * 计算 Spearman 秩相关系数 (Rank Correlation)
 */
function calculateRankCorrelation(x: number[], y: number[]): number {
  const n = x.length
  if (n !== y.length || n < 2) return 0

  // 计算排名
  const rankX = getRanks(x)
  const rankY = getRanks(y)

  // 计算排名的皮尔逊相关系数
  return calculatePearsonCorrelation(rankX, rankY)
}

/**
 * 计算数据的排名 (用于 Spearman 相关)
 */
function getRanks(data: number[]): number[] {
  const sorted = [...data].sort((a, b) => a - b)
  const ranks = new Map<number, number>()

  sorted.forEach((value, index) => {
    if (!ranks.has(value)) {
      ranks.set(value, index + 1)
    }
  })

  return data.map(value => ranks.get(value) || 0)
}

// ==================== 行业关联规则（辅助指标） ====================

const INDUSTRY_RELATIONS: Record<string, Array<{ sector: string; weight: number }>> = {
  '人工智能': [
    { sector: '芯片半导体', weight: 0.95 },
    { sector: '5G通信', weight: 0.85 },
    { sector: '云计算', weight: 0.90 },
    { sector: '大数据', weight: 0.88 }
  ],
  '新能源汽车': [
    { sector: '锂电池', weight: 0.98 },
    { sector: '充电桩', weight: 0.75 },
    { sector: '汽车电子', weight: 0.85 },
    { sector: '智能驾驶', weight: 0.80 }
  ],
  '芯片半导体': [
    { sector: '人工智能', weight: 0.90 },
    { sector: '5G通信', weight: 0.88 },
    { sector: '消费电子', weight: 0.82 },
    { sector: '物联网', weight: 0.78 }
  ]
}

function getIndustryRelationScore(sectorA: string, sectorB: string): number {
  const relationA = INDUSTRY_RELATIONS[sectorA]?.find(r => r.sector === sectorB)
  const relationB = INDUSTRY_RELATIONS[sectorB]?.find(r => r.sector === sectorA)

  return Math.max(
    relationA?.weight || 0,
    relationB?.weight || 0
  )
}

// ==================== 主推荐函数 ====================

export interface PriceHistoryData {
  sector: string
  dates: string[]
  prices: number[]
  returns?: number[]
  predictions?: number[]  // 用于 IC 分析
}

export async function generateQLibRecommendations(
  targetSector: SectorNode,
  allSectors: SectorNode[],
  priceHistoryData?: Record<string, PriceHistoryData>,
  userFavorites?: string[]
): Promise<QLibRecommendationResult[]> {
  const results: QLibRecommendationResult[] = []

  const candidateSectors = allSectors.filter(
    s => s.name !== targetSector.name && s.type === 'sector'
  )

  for (const candidate of candidateSectors) {
    const result = await calculateQLibRecommendationScore(
      targetSector,
      candidate,
      priceHistoryData,
      userFavorites
    )

    if (result.relevanceScore > 20) {
      results.push(result)
    }
  }

  return results.sort((a, b) => b.relevanceScore - a.relevanceScore).slice(0, 10)
}

async function calculateQLibRecommendationScore(
  targetSector: SectorNode,
  candidateSector: SectorNode,
  priceHistoryData?: Record<string, PriceHistoryData>,
  userFavorites?: string[]
): Promise<QLibRecommendationResult> {
  const reasons: QLibRecommendationReason[] = []
  let totalScore = 0

  // === 核心支柱 1: 价格相关性 (50% 权重) ===
  if (priceHistoryData?.[targetSector.name]?.prices &&
      priceHistoryData?.[candidateSector.name]?.prices) {
    const priceCorr = calculatePriceCorrelation(
      priceHistoryData[targetSector.name].prices,
      priceHistoryData[candidateSector.name].prices
    )

    if (priceCorr) {
      // 相关系数转换为得分 (0-100)
      const priceScore = Math.abs(priceCorr.coefficient) * 100
      totalScore += priceScore * (QLIB_WEIGHTS.PRICE_CORRELATION / 100)

      const impact = priceCorr.significance < 0.05 ? 'critical' :
                   priceCorr.significance < 0.1 ? 'high' : 'medium'

      reasons.push({
        type: 'price_corr',
        label: '价格相关性',
        description: `相关系数 ${priceCorr.coefficient.toFixed(3)} (p=${priceCorr.significance.toFixed(3)})`,
        weight: QLIB_WEIGHTS.PRICE_CORRELATION,
        score: priceScore,
        impact,
        qlibRef: 'QLib Corr 操作符'
      })
    }
  }

  // === 核心支柱 2: 风险归因分析 (30% 权重) ===
  if (priceHistoryData?.[targetSector.name]?.returns &&
      priceHistoryData?.[candidateSector.name]?.returns) {
    const riskAttr = calculateRiskAttribution(
      priceHistoryData[targetSector.name].returns!,
      priceHistoryData[candidateSector.name].returns!,
      priceHistoryData['market']?.returns  // 市场组合数据
    )

    if (riskAttr) {
      // 风险相似度评分
      const riskScore = (1 - Math.abs(riskAttr.systematicRisk - 1) * 0.5) * 100
      totalScore += riskScore * (QLIB_WEIGHTS.RISK_ATTRIBUTION / 100)

      reasons.push({
        type: 'risk_attribution',
        label: '风险归因',
        description: `β=${riskAttr.systematicRisk.toFixed(3)}, 特异性风险=${riskAttr.specificRisk.toFixed(3)}`,
        weight: QLIB_WEIGHTS.RISK_ATTRIBUTION,
        score: riskScore,
        impact: 'high',
        qlibRef: 'QLib risk_analysis'
      })
    }
  }

  // === 核心支柱 3: IC 分析 (15% 权重) ===
  if (priceHistoryData?.[candidateSector.name]?.predictions &&
      priceHistoryData?.[candidateSector.name]?.prices) {
    const icAnalysis = calculateICAnalysis(
      priceHistoryData[candidateSector.name].predictions!,
      priceHistoryData[candidateSector.name].prices
    )

    if (icAnalysis) {
      const icScore = (Math.abs(icAnalysis.ic) + Math.abs(icAnalysis.rankIC)) / 2 * 100
      totalScore += icScore * (QLIB_WEIGHTS.IC_ANALYSIS / 100)

      reasons.push({
        type: 'ic_analysis',
        label: 'IC 分析',
        description: `IC=${icAnalysis.ic.toFixed(3)}, RankIC=${icAnalysis.rankIC.toFixed(3)}, IR=${icAnalysis.ir.toFixed(3)}`,
        weight: QLIB_WEIGHTS.IC_ANALYSIS,
        score: icScore,
        impact: icAnalysis.ir > 1 ? 'high' : 'medium',
        qlibRef: 'QLib IC 分析'
      })
    }
  }

  // === 辅助指标: 行业关联 (3% 权重) ===
  const industryRel = getIndustryRelationScore(targetSector.name, candidateSector.name)
  if (industryRel > 0) {
    const industryScore = industryRel * 100
    totalScore += industryScore * (QLIB_WEIGHTS.INDUSTRY_RELATION / 100)

    reasons.push({
      type: 'industry',
      label: '产业链关联',
      description: `关联度 ${(industryRel * 100).toFixed(0)}%`,
      weight: QLIB_WEIGHTS.INDUSTRY_RELATION,
      score: industryScore,
      impact: 'low'
    })
  }

  // === 辅助指标: 用户行为 (2% 权重) ===
  if (userFavorites && userFavorites.length > 0) {
    const isFavorited = userFavorites.includes(candidateSector.name)
    const behaviorScore = isFavorited ? 100 : 0
    totalScore += behaviorScore * (QLIB_WEIGHTS.USER_BEHAVIOR / 100)

    if (isFavorited) {
      reasons.push({
        type: 'behavior',
        label: '用户偏好',
        description: '您已收藏此板块',
        weight: QLIB_WEIGHTS.USER_BEHAVIOR,
        score: behaviorScore,
        impact: 'low'
      })
    }
  }

  return {
    sector: candidateSector,
    relevanceScore: Math.round(totalScore),
    reasons,
    metrics: {}
  }
}

// ==================== 工具函数 ====================

export function getQLibReasonSummary(reasons: QLibRecommendationReason[]): string {
  if (reasons.length === 0) return '综合分析'

  const qlibReasons = reasons.filter(r => r.qlibRef)
  if (qlibReasons.length === 0) return '综合分析'

  return qlibReasons
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 2)
    .map(r => r.label)
    .join(' + ')
}

export function getQLibRecommendationLevel(score: number): {
  level: string
  color: string
  description: string
} {
  if (score >= 80) {
    return {
      level: '强烈推荐',
      color: '#f56c6c',
      description: '基于 QLib 方法论的高度相关'
    }
  } else if (score >= 60) {
    return {
      level: '推荐',
      color: '#e6a23c',
      description: 'QLib 多指标分析显示相关'
    }
  } else if (score >= 40) {
    return {
      level: '一般推荐',
      color: '#409eff',
      description: '存在一定的关联性'
    }
  } else {
    return {
      level: '参考',
      color: '#909399',
      description: '关联性较弱'
    }
  }
}
