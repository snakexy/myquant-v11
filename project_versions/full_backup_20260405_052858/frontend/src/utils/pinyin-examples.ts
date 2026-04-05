/**
 * pinyin-pro 库使用示例
 *
 * 这个文件展示了 pinyin-pro 库的各种转换方式
 * 用于理解前端拼音搜索的实现原理
 */

import { pinyin } from 'pinyin-pro'

// ============================================
// 1. 基础用法 - 获取拼音
// ============================================

// 示例 1: 获取完整拼音
console.log(pinyin('中国银行')) // 输出: 'zhōng guó yín háng'

// 示例 2: 获取首字母
console.log(pinyin('中国银行', { mode: 'first' })) // 输出: 'zh g y h'

// 示例 3: 去除声调
console.log(pinyin('中国银行', { toneType: 'none' })) // 输出: 'zhong guo yin hang'

// 示例 4: 去除声调 + 首字母
console.log(pinyin('中国银行', { mode: 'first', toneType: 'none' })) // 输出: 'zh g y h'

// ============================================
// 2. 股票搜索相关用法
// ============================================

/**
 * 获取拼音首字母 (用于首字母搜索)
 */
export const getPinyinInitials = (text: string): string => {
  const result = pinyin(text, { mode: 'first', toneType: 'none' })
  return result.toUpperCase().replace(/\s+/g, '')
}

// 测试
console.log(getPinyinInitials('浦发银行')) // 输出: 'PFYH'
console.log(getPinyinInitials('平安银行')) // 输出: 'PAYH'
console.log(getPinyinInitials('招商银行')) // 输出: 'ZSYH'
console.log(getPinyinInitials('中国石油')) // 输出: 'ZGSY'

/**
 * 获取完整拼音 (用于全拼搜索)
 */
export const getPinyinFull = (text: string): string => {
  const result = pinyin(text, { toneType: 'none' })
  return result.replace(/\s+/g, '').toLowerCase()
}

// 测试
console.log(getPinyinFull('浦发银行')) // 输出: 'pufayinhang'
console.log(getPinyinFull('平安银行')) // 输出: 'pinganyinhang'
console.log(getPinyinFull('招商银行')) // 输出: 'zhaoshangyinhang'

// ============================================
// 3. 搜索匹配示例
// ============================================

interface StockSearchExample {
  stockName: string
  searchInputs: string[]
  matchResults: boolean[]
}

const examples: StockSearchExample[] = [
  {
    stockName: '浦发银行',
    searchInputs: ['pfyh', 'pufa', 'pufayinhang', '600000'],
    matchResults: [true, true, true, true] // 都能匹配
  },
  {
    stockName: '平安银行',
    searchInputs: ['payh', 'pingan', 'pinganyinhang', '000001'],
    matchResults: [true, true, true, true]
  },
  {
    stockName: '中国石油',
    searchInputs: ['zgsy', 'zhongguo', 'zhongguoshiyou', '601857'],
    matchResults: [true, true, true, true]
  }
]

/**
 * 股票搜索函数 (支持多种输入方式)
 */
export const searchStock = (
  stockName: string,
  stockCode: string,
  searchTerm: string
): boolean => {
  const term = searchTerm.toLowerCase()

  // 1. 股票代码匹配
  if (stockCode.toLowerCase().includes(term)) {
    return true
  }

  // 2. 股票名称匹配 (中文)
  if (stockName.includes(searchTerm)) {
    return true
  }

  // 3. 拼音首字母匹配
  const initials = getPinyinInitials(stockName)
  if (initials.toLowerCase().includes(term)) {
    return true
  }

  // 4. 拼音全拼匹配
  const fullPinyin = getPinyinFull(stockName)
  if (fullPinyin.includes(term)) {
    return true
  }

  return false
}

// ============================================
// 4. 实际使用场景
// ============================================

/**
 * 场景 1: 用户输入 "pfyh"
 * searchStock('浦发银行', '600000.SH', 'pfyh')
 * -> initials = 'PFYH'
 * -> 'PFYH'.toLowerCase().includes('pfyh') = true
 * -> 返回: true ✓
 */

/**
 * 场景 2: 用户输入 "pufa"
 * searchStock('浦发银行', '600000.SH', 'pufa')
 * -> fullPinyin = 'pufayinhang'
 * -> 'pufayinhang'.includes('pufa') = true
 * -> 返回: true ✓
 */

/**
 * 场景 3: 用户输入 "zx" (搜索中信证券)
 * searchStock('中信证券', '600030.SH', 'zx')
 * -> initials = 'ZXZQ'
 * -> 'ZXZQ'.toLowerCase().includes('zx') = true
 * -> 返回: true ✓
 */

/**
 * 场景 4: 用户输入 "zhongxin"
 * searchStock('中信证券', '600030.SH', 'zhongxin')
 * -> fullPinyin = 'zhongxinzhengquan'
 * -> 'zhongxinzhengquan'.includes('zhongxin') = true
 * -> 返回: true ✓
 */

// ============================================
// 5. 性能优化建议
// ============================================

/**
 * 对于大量股票列表,建议:
 * 1. 缓存拼音转换结果,避免重复计算
 * 2. 使用 Web Worker 进行拼音转换,避免阻塞主线程
 * 3. 对于首字母搜索,可以建立索引
 */

// 缓存示例
const pinyinCache = new Map<string, { initials: string; full: string }>()

export const getPinyinWithCache = (text: string) => {
  if (pinyinCache.has(text)) {
    return pinyinCache.get(text)!
  }

  const result = {
    initials: getPinyinInitials(text),
    full: getPinyinFull(text)
  }

  pinyinCache.set(text, result)
  return result
}

export default {
  pinyin,
  getPinyinInitials,
  getPinyinFull,
  searchStock,
  getPinyinWithCache
}
