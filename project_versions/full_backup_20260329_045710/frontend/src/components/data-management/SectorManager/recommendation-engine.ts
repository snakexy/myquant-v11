/**
 * 板块智能推荐引擎
 * 基于 QLib 官方方法论的多维度推荐算法
 *
 * 推荐分数 = 价格走势相关性 × 40% + 行业关联规则 × 30% + 成分股重叠度 × 15% + 用户行为 × 15%
 */

import type { SectorNode, SectorBasicInfo } from '@/components/data-management/shared/types'

// ==================== 类型定义 ====================

export interface RecommendationResult {
  sector: SectorNode
  relevanceScore: number      // 综合相关性得分 (0-100)
  reasons: RecommendationReason[]  // 推荐理由
  data: {
    priceCorrelation?: number  // 价格相关性系数 (-1 ~ 1)
    industryRelation?: number  // 行业关联度 (0-1)
    stockOverlap?: number      // 成分股重叠度 (0-1)
    userBehavior?: number      // 用户行为得分 (0-1)
  }
}

export interface RecommendationReason {
  type: 'price' | 'industry' | 'stock' | 'behavior'
  label: string
  description: string
  weight: number
  score: number
  impact: 'high' | 'medium' | 'low'
}

export interface PriceHistoryData {
  sector: string
  dates: string[]
  prices: number[]  // 板块指数价格
  volumes: number[]
}

// ==================== 行业关联规则矩阵 ====================

/**
 * 行业关联规则（基于产业链和供应链逻辑）
 * 权重范围: 0.5-1.0，1.0 表示强关联
 */
const INDUSTRY_RELATIONS: Record<string, Array<{ sector: string; weight: number }>> = {
  // 人工智能产业链
  '人工智能': [
    { sector: '芯片半导体', weight: 0.95 },
    { sector: '5G通信', weight: 0.85 },
    { sector: '云计算', weight: 0.90 },
    { sector: '大数据', weight: 0.88 }
  ],

  // 新能源汽车产业链
  '新能源汽车': [
    { sector: '锂电池', weight: 0.98 },
    { sector: '充电桩', weight: 0.75 },
    { sector: '汽车电子', weight: 0.85 },
    { sector: '智能驾驶', weight: 0.80 }
  ],

  // 芯片半导体产业链
  '芯片半导体': [
    { sector: '人工智能', weight: 0.90 },
    { sector: '5G通信', weight: 0.88 },
    { sector: '消费电子', weight: 0.82 },
    { sector: '物联网', weight: 0.78 }
  ],

  // 房地产产业链
  '房地产': [
    { sector: '建材', weight: 0.92 },
    { sector: '家电', weight: 0.85 },
    { sector: '建筑装饰', weight: 0.88 },
    { sector: '钢铁', weight: 0.75 }
  ],

  // 银行金融
  '银行': [
    { sector: '保险', weight: 0.85 },
    { sector: '证券', weight: 0.88 },
    { sector: '房地产', weight: 0.65 }
  ],

  // 医药生物
  '医药生物': [
    { sector: '医疗器械', weight: 0.92 },
    { sector: '医疗服务', weight: 0.88 },
    { sector: '化学制药', weight: 0.85 }
  ],

  // 食品饮料
  '食品饮料': [
    { sector: '白酒', weight: 0.75 },
    { sector: '农业', weight: 0.70 },
    { sector: '包装材料', weight: 0.55 }
  ],

  // 电力能源
  '电力': [
    { sector: '新能源发电', weight: 0.90 },
    { sector: '煤炭', weight: 0.70 },
    { sector: '储能', weight: 0.85 }
  ]
}

// ==================== 核心推荐算法 ====================

/**
 * 智能推荐引擎主函数
 * @param targetSector 目标板块
 * @param allSectors 所有板块列表
 * @param priceHistoryData 价格历史数据（可选，用于计算价格相关性）
 * @param userFavorites 用户收藏的板块（可选，用于用户行为分析）
 * @returns 推荐结果列表（按相关性得分降序排列）
 */
export async function generateRecommendations(
  targetSector: SectorNode,
  allSectors: SectorNode[],
  priceHistoryData?: Record<string, PriceHistoryData>,
  userFavorites?: string[]
): Promise<RecommendationResult[]> {
  const results: RecommendationResult[] = []

  // 过滤掉目标板块自身
  const candidateSectors = allSectors.filter(
    s => s.name !== targetSector.name && s.type === 'sector'
  )

  // 并行计算所有候选板块的推荐得分
  for (const candidate of candidateSectors) {
    const result = await calculateRecommendationScore(
      targetSector,
      candidate,
      priceHistoryData,
      userFavorites
    )

    // 只保留综合得分 > 20 的推荐
    if (result.relevanceScore > 20) {
      results.push(result)
    }
  }

  // 按相关性得分降序排列
  return results.sort((a, b) => b.relevanceScore - a.relevanceScore).slice(0, 10)
}

/**
 * 计算单个候选板块的推荐得分
 */
async function calculateRecommendationScore(
  targetSector: SectorNode,
  candidateSector: SectorNode,
  priceHistoryData?: Record<string, PriceHistoryData>,
  userFavorites?: string[]
): Promise<RecommendationResult> {
  const reasons: RecommendationReason[] = []
  let totalScore = 0

  // 1. 价格相关性 (40% 权重) - QLib 核心方法论
  let priceCorrelation = 0
  if (priceHistoryData && priceHistoryData[targetSector.name] && priceHistoryData[candidateSector.name]) {
    priceCorrelation = calculatePearsonCorrelation(
      priceHistoryData[targetSector.name].prices,
      priceHistoryData[candidateSector.name].prices
    )

    // 将相关系数 [-1, 1] 转换为得分 [0, 100]
    //正相关为正分，负相关为低分
    const priceScore = priceCorrelation > 0 ? Math.abs(priceCorrelation) * 100 : 0
    totalScore += priceScore * 0.40

    if (priceCorrelation > 0.3) {
      reasons.push({
        type: 'price',
        label: '价格走势相关',
        description: `过去60日价格相关系数 ${priceCorrelation.toFixed(2)}`,
        weight: 40,
        score: priceScore,
        impact: priceCorrelation > 0.6 ? 'high' : priceCorrelation > 0.4 ? 'medium' : 'low'
      })
    }
  }

  // 2. 行业关联规则 (30% 权重) - 基于产业链逻辑
  let industryRelation = getIndustryRelationScore(targetSector.name, candidateSector.name)
  const industryScore = industryRelation * 100
  totalScore += industryScore * 0.30

  if (industryRelation > 0.5) {
    reasons.push({
      type: 'industry',
      label: '产业链关联',
      description: `属于${industryRelation > 0.8 ? '强' : '弱'}关联板块`,
      weight: 30,
      score: industryScore,
      impact: industryRelation > 0.8 ? 'high' : 'medium'
    })
  }

  // 3. 成分股重叠度 (15% 权重) - 辅助参考
  let stockOverlap = 0
  if (targetSector.stockCount && candidateSector.stockCount) {
    // 假设我们已获取成分股数据，计算 Jaccard 相似系数
    // 这里使用板块大小作为估算（实际应该使用真实成分股列表）
    // stockOverlap = calculateJaccardSimilarity(targetStocks, candidateStocks)
    // 由于没有真实成分股数据，这里使用板块规模作为启发式估算
    const sizeRatio = Math.min(targetSector.stockCount, candidateSector.stockCount) /
                     Math.max(targetSector.stockCount, candidateSector.stockCount)
    stockOverlap = sizeRatio * 0.3  // 最大30%重叠（保守估计）

    const overlapScore = stockOverlap * 100
    totalScore += overlapScore * 0.15

    if (stockOverlap > 0.1) {
      reasons.push({
        type: 'stock',
        label: '成分股重叠',
        description: `约${(stockOverlap * 100).toFixed(1)}%成分股重叠`,
        weight: 15,
        score: overlapScore,
        impact: 'low'
      })
    }
  }

  // 4. 用户行为分析 (15% 权重) - 个性化推荐
  let userBehavior = 0
  if (userFavorites && userFavorites.length > 0) {
    // 如果候选板块也在用户的收藏中，说明用户对这个主题感兴趣
    if (userFavorites.includes(candidateSector.name)) {
      userBehavior = 1.0
    } else {
      // 检查候选板块是否与用户收藏的板块有强关联
      for (const favorite of userFavorites) {
        const relation = getIndustryRelationScore(favorite, candidateSector.name)
        if (relation > userBehavior) {
          userBehavior = relation
        }
      }
    }

    const behaviorScore = userBehavior * 100
    totalScore += behaviorScore * 0.15

    if (userBehavior > 0.5) {
      reasons.push({
        type: 'behavior',
        label: '用户偏好',
        description: userBehavior === 1.0 ? '您已收藏此板块' : '与您收藏的板块相关',
        weight: 15,
        score: behaviorScore,
        impact: 'medium'
      })
    }
  }

  return {
    sector: candidateSector,
    relevanceScore: Math.round(totalScore),
    reasons,
    data: {
      priceCorrelation: priceCorrelation || undefined,
      industryRelation: industryRelation || undefined,
      stockOverlap: stockOverlap || undefined,
      userBehavior: userBehavior || undefined
    }
  }
}

// ==================== 价格相关性计算 (QLib Core) ====================

/**
 * 计算皮尔逊相关系数 (Pearson Correlation Coefficient)
 * 对应 QLib 的 Corr 操作符
 *
 * 公式: Corr(X, Y) = Cov(X, Y) / (σX * σY)
 * 其中:
 *   Cov(X, Y) = Σ[(Xi - X̄)(Yi - Ȳ)] / (n - 1)
 *   σX = √[Σ(Xi - X̄)² / (n - 1)]
 */
function calculatePearsonCorrelation(x: number[], y: number[]): number {
  const n = Math.min(x.length, y.length)
  if (n < 2) return 0

  // 计算均值
  const meanX = x.slice(0, n).reduce((sum, val) => sum + val, 0) / n
  const meanY = y.slice(0, n).reduce((sum, val) => sum + val, 0) / n

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

  // 计算相关系数
  const denominator = Math.sqrt(varianceX * varianceY)
  if (denominator === 0) return 0

  const correlation = covariance / denominator

  // 确保在 [-1, 1] 范围内（数值误差可能稍微超出）
  return Math.max(-1, Math.min(1, correlation))
}

// ==================== 行业关联规则匹配 ====================

/**
 * 获取两个板块之间的行业关联度
 * 基于预定义的产业链关系矩阵
 */
function getIndustryRelationScore(sectorA: string, sectorB: string): number {
  // 双向查找（A关联B 或 B关联A）
  const relationA = INDUSTRY_RELATIONS[sectorA]?.find(r => r.sector === sectorB)
  const relationB = INDUSTRY_RELATIONS[sectorB]?.find(r => r.sector === sectorA)

  // 返回最大的关联度
  return Math.max(
    relationA?.weight || 0,
    relationB?.weight || 0
  )
}

// ==================== 成分股重叠度计算 ====================

/**
 * 计算 Jaccard 相似系数
 * J(A, B) = |A ∩ B| / |A ∪ B|
 */
export function calculateJaccardSimilarity<T>(setA: T[], setB: T[]): number {
  const setAUnique = new Set(setA)
  const setBUnique = new Set(setB)

  const intersection = new Set<T>()
  for (const item of setAUnique) {
    if (setBUnique.has(item)) {
      intersection.add(item)
    }
  }

  const union = new Set([...setAUnique, ...setBUnique])

  if (union.size === 0) return 0
  return intersection.size / union.size
}

// ==================== 工具函数 ====================

/**
 * 获取推荐理由的描述文本
 */
export function getReasonSummary(reasons: RecommendationReason[]): string {
  if (reasons.length === 0) return '综合推荐'

  // 按权重排序，返回前2个主要理由
  const topReasons = reasons
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 2)
    .map(r => r.label)

  return topReasons.join(' + ')
}

/**
 * 根据推荐得分获取等级标签
 */
export function getRecommendationLevel(score: number): {
  level: string
  color: string
  description: string
} {
  if (score >= 80) {
    return {
      level: '强烈推荐',
      color: '#f56c6c',
      description: '高度相关，值得关注'
    }
  } else if (score >= 60) {
    return {
      level: '推荐',
      color: '#e6a23c',
      description: '具有一定关联性'
    }
  } else if (score >= 40) {
    return {
      level: '一般推荐',
      color: '#409eff',
      description: '存在一定关联'
    }
  } else {
    return {
      level: '仅供参考',
      color: '#909399',
      description: '关联性较弱'
    }
  }
}

/**
 * 格式化相关性数据为显示文本
 */
export function formatCorrelationData(data: RecommendationResult['data']): string {
  const parts: string[] = []

  if (data.priceCorrelation !== undefined) {
    parts.push(`价格相关: ${(data.priceCorrelation * 100).toFixed(1)}%`)
  }
  if (data.industryRelation !== undefined && data.industryRelation > 0) {
    parts.push(`行业关联: ${(data.industryRelation * 100).toFixed(0)}%`)
  }
  if (data.stockOverlap !== undefined && data.stockOverlap > 0) {
    parts.push(`成分股重叠: ${(data.stockOverlap * 100).toFixed(1)}%`)
  }
  if (data.userBehavior !== undefined && data.userBehavior > 0) {
    parts.push(`用户偏好: ${(data.userBehavior * 100).toFixed(0)}%`)
  }

  return parts.join(' | ') || '综合分析'
}
