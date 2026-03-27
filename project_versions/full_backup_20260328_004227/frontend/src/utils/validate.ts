// 验证函数库
import type { 
  ValidationRule, 
  ValidationResult, 
  FormValidationConfig 
} from './types'

/**
 * 验证单个值
 * @param value 要验证的值
 * @param rules 验证规则
 * @returns 验证结果
 */
export function validateValue(value: any, rules: ValidationRule[]): ValidationResult {
  for (const rule of rules) {
    const result = validateRule(value, rule)
    if (!result.valid) {
      return result
    }
  }
  
  return { valid: true }
}

/**
 * 验证单个规则
 * @param value 要验证的值
 * @param rule 验证规则
 * @returns 验证结果
 */
export function validateRule(value: any, rule: ValidationRule): ValidationResult {
  const { required, min, max, minLength, maxLength, pattern, email, url, phone, number, integer, positive, negative, custom } = rule

  // 必填验证
  if (required && (value === null || value === undefined || value === '')) {
    return { valid: false, message: '此字段为必填项', value }
  }

  // 如果值为空且不是必填，跳过其他验证
  if (value === null || value === undefined || value === '') {
    return { valid: true }
  }

  // 最小值验证
  if (typeof min === 'number' && typeof value === 'number' && value < min) {
    return { valid: false, message: `值不能小于${min}`, value }
  }

  // 最大值验证
  if (typeof max === 'number' && typeof value === 'number' && value > max) {
    return { valid: false, message: `值不能大于${max}`, value }
  }

  // 最小长度验证
  if (typeof minLength === 'number' && typeof value === 'string' && value.length < minLength) {
    return { valid: false, message: `长度不能少于${minLength}个字符`, value }
  }

  // 最大长度验证
  if (typeof maxLength === 'number' && typeof value === 'string' && value.length > maxLength) {
    return { valid: false, message: `长度不能超过${maxLength}个字符`, value }
  }

  // 正则表达式验证
  if (pattern && typeof value === 'string' && !pattern.test(value)) {
    return { valid: false, message: '格式不正确', value }
  }

  // 邮箱验证
  if (email && typeof value === 'string' && !isEmail(value)) {
    return { valid: false, message: '请输入有效的邮箱地址', value }
  }

  // URL验证
  if (url && typeof value === 'string' && !isUrl(value)) {
    return { valid: false, message: '请输入有效的URL地址', value }
  }

  // 电话号码验证
  if (phone && typeof value === 'string' && !isPhone(value)) {
    return { valid: false, message: '请输入有效的电话号码', value }
  }

  // 数字验证
  if (number && !isNumber(value)) {
    return { valid: false, message: '请输入有效的数字', value }
  }

  // 整数验证
  if (integer && !isInteger(value)) {
    return { valid: false, message: '请输入有效的整数', value }
  }

  // 正数验证
  if (positive && typeof value === 'number' && value <= 0) {
    return { valid: false, message: '请输入正数', value }
  }

  // 负数验证
  if (negative && typeof value === 'number' && value >= 0) {
    return { valid: false, message: '请输入负数', value }
  }

  // 自定义验证
  if (custom) {
    const customResult = custom(value)
    if (customResult !== true) {
      return { 
        valid: false, 
        message: typeof customResult === 'string' ? customResult : '验证失败', 
        value 
      }
    }
  }

  return { valid: true }
}

/**
 * 验证表单
 * @param data 表单数据
 * @param config 表单验证配置
 * @returns 验证结果
 */
export function validateForm(data: Record<string, any>, config: FormValidationConfig): Record<string, ValidationResult> {
  const results: Record<string, ValidationResult> = {}

  for (const [field, rules] of Object.entries(config)) {
    const value = data[field]
    results[field] = validateValue(value, rules)
  }

  return results
}

/**
 * 检查表单是否有效
 * @param results 验证结果
 * @returns 是否有效
 */
export function isFormValid(results: Record<string, ValidationResult>): boolean {
  return Object.values(results).every(result => result.valid)
}

/**
 * 获取表单错误信息
 * @param results 验证结果
 * @returns 错误信息对象
 */
export function getFormErrors(results: Record<string, ValidationResult>): Record<string, string> {
  const errors: Record<string, string> = {}
  
  for (const [field, result] of Object.entries(results)) {
    if (!result.valid && result.message) {
      errors[field] = result.message
    }
  }
  
  return errors
}

/**
 * 验证邮箱地址
 * @param email 邮箱地址
 * @returns 是否有效
 */
export function isEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证URL地址
 * @param url URL地址
 * @returns 是否有效
 */
export function isUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证电话号码（中国手机号）
 * @param phone 电话号码
 * @returns 是否有效
 */
export function isPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

/**
 * 验证数字
 * @param value 值
 * @returns 是否为数字
 */
export function isNumber(value: any): boolean {
  return typeof value === 'number' && !isNaN(value)
}

/**
 * 验证整数
 * @param value 值
 * @returns 是否为整数
 */
export function isInteger(value: any): boolean {
  return typeof value === 'number' && Number.isInteger(value)
}

/**
 * 验证字符串
 * @param value 值
 * @returns 是否为字符串
 */
export function isString(value: any): boolean {
  return typeof value === 'string'
}

/**
 * 验证布尔值
 * @param value 值
 * @returns 是否为布尔值
 */
export function isBoolean(value: any): boolean {
  return typeof value === 'boolean'
}

/**
 * 验证数组
 * @param value 值
 * @returns 是否为数组
 */
export function isArray(value: any): boolean {
  return Array.isArray(value)
}

/**
 * 验证对象
 * @param value 值
 * @returns 是否为对象
 */
export function isObject(value: any): boolean {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

/**
 * 验证日期
 * @param value 值
 * @returns 是否为有效日期
 */
export function isDate(value: any): boolean {
  if (value instanceof Date) {
    return !isNaN(value.getTime())
  }
  if (typeof value === 'string' || typeof value === 'number') {
    const date = new Date(value)
    return !isNaN(date.getTime())
  }
  return false
}

/**
 * 验证股票代码
 * @param symbol 股票代码
 * @returns 是否有效
 */
export function isStockSymbol(symbol: string): boolean {
  // 中国股票代码格式：6位数字.SH或SZ
  const stockRegex = /^\d{6}\.(SH|SZ)$/
  return stockRegex.test(symbol)
}

/**
 * 验证身份证号码（中国）
 * @param idCard 身份证号码
 * @returns 是否有效
 */
export function isIdCard(idCard: string): boolean {
  const idCardRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
  return idCardRegex.test(idCard)
}

/**
 * 验证银行卡号
 * @param cardNumber 银行卡号
 * @returns 是否有效
 */
export function isBankCard(cardNumber: string): boolean {
  const cardRegex = /^\d{16,19}$/
  return cardRegex.test(cardNumber)
}

/**
 * 验证IP地址
 * @param ip IP地址
 * @returns 是否有效
 */
export function isIpAddress(ip: string): boolean {
  const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  return ipRegex.test(ip)
}

/**
 * 验证MAC地址
 * @param mac MAC地址
 * @returns 是否有效
 */
export function isMacAddress(mac: string): boolean {
  const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/
  return macRegex.test(mac)
}

/**
 * 验证密码强度
 * @param password 密码
 * @returns 密码强度等级
 */
export function getPasswordStrength(password: string): 'weak' | 'medium' | 'strong' {
  let score = 0
  
  // 长度检查
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  
  // 字符类型检查
  if (/[a-z]/.test(password)) score++ // 小写字母
  if (/[A-Z]/.test(password)) score++ // 大写字母
  if (/\d/.test(password)) score++ // 数字
  if (/[^a-zA-Z0-9]/.test(password)) score++ // 特殊字符
  
  if (score <= 2) return 'weak'
  if (score <= 4) return 'medium'
  return 'strong'
}

/**
 * 验证价格范围
 * @param price 价格
 * @param min 最小价格
 * @param max 最大价格
 * @returns 是否有效
 */
export function isPriceInRange(price: number, min: number, max: number): boolean {
  return isNumber(price) && price >= min && price <= max
}

/**
 * 验证百分比
 * @param value 值
 * @param min 最小值
 * @param max 最大值
 * @returns 是否有效
 */
export function isPercentage(value: number, min = 0, max = 100): boolean {
  return isNumber(value) && value >= min && value <= max
}

/**
 * 验证时间范围
 * @param startDate 开始时间
 * @param endDate 结束时间
 * @returns 是否有效
 */
export function isValidDateRange(startDate: Date | string, endDate: Date | string): boolean {
  const start = new Date(startDate)
  const end = new Date(endDate)
  
  return isDate(start) && isDate(end) && start < end
}

/**
 * 验证文件类型
 * @param file 文件对象
 * @param allowedTypes 允许的文件类型
 * @returns 是否有效
 */
export function isFileTypeAllowed(file: File, allowedTypes: string[]): boolean {
  const fileType = file.type.toLowerCase()
  return allowedTypes.some(type => fileType.includes(type.toLowerCase()))
}

/**
 * 验证文件大小
 * @param file 文件对象
 * @param maxSize 最大大小（字节）
 * @returns 是否有效
 */
export function isFileSizeValid(file: File, maxSize: number): boolean {
  return file.size <= maxSize
}

/**
 * 验证用户名格式
 * @param username 用户名
 * @returns 是否有效
 */
export function isValidUsername(username: string): boolean {
  // 用户名规则：4-20位，只能包含字母、数字、下划线
  const usernameRegex = /^[a-zA-Z0-9_]{4,20}$/
  return usernameRegex.test(username)
}

/**
 * 验证JSON字符串
 * @param jsonString JSON字符串
 * @returns 是否有效
 */
export function isValidJSON(jsonString: string): boolean {
  try {
    JSON.parse(jsonString)
    return true
  } catch {
    return false
  }
}

/**
 * 验证颜色值
 * @param color 颜色值
 * @returns 是否有效
 */
export function isValidColor(color: string): boolean {
  const colorRegex = /^(#([0-9A-Fa-f]{3}){1,2}|rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)|rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\))$/
  return colorRegex.test(color)
}

/**
 * 验证纬度
 * @param latitude 纬度
 * @returns 是否有效
 */
export function isValidLatitude(latitude: number): boolean {
  return isNumber(latitude) && latitude >= -90 && latitude <= 90
}

/**
 * 验证经度
 * @param longitude 经度
 * @returns 是否有效
 */
export function isValidLongitude(longitude: number): boolean {
  return isNumber(longitude) && longitude >= -180 && longitude <= 180
}

/**
 * 验证坐标
 * @param latitude 纬度
 * @param longitude 经度
 * @returns 是否有效
 */
export function isValidCoordinates(latitude: number, longitude: number): boolean {
  return isValidLatitude(latitude) && isValidLongitude(longitude)
}

/**
 * 验证回测参数
 * @param params 回测参数
 * @returns 验证结果
 */
export function validateBacktestParams(params: {
  symbols: string[]
  startDate: string
  endDate: string
  initialCapital: number
}): ValidationResult {
  const { symbols, startDate, endDate, initialCapital } = params

  // 验证股票代码
  if (!symbols || symbols.length === 0) {
    return { valid: false, message: '请选择至少一只股票' }
  }

  for (const symbol of symbols) {
    if (!isStockSymbol(symbol)) {
      return { valid: false, message: `无效的股票代码: ${symbol}` }
    }
  }

  // 验证日期范围
  if (!isValidDateRange(startDate, endDate)) {
    return { valid: false, message: '结束日期必须晚于开始日期' }
  }

  // 验证初始资金
  if (!isNumber(initialCapital) || initialCapital <= 0) {
    return { valid: false, message: '初始资金必须为正数' }
  }

  return { valid: true }
}

/**
 * 验证策略参数
 * @param params 策略参数
 * @returns 验证结果
 */
export function validateStrategyParams(params: {
  name: string
  type: string
  parameters: Record<string, any>
}): ValidationResult {
  const { name, type, parameters } = params

  // 验证策略名称
  if (!name || name.trim().length === 0) {
    return { valid: false, message: '策略名称不能为空' }
  }

  if (name.length > 50) {
    return { valid: false, message: '策略名称不能超过50个字符' }
  }

  // 验证策略类型
  const validTypes = ['trend', 'mean_reversion', 'momentum', 'arbitrage', 'custom']
  if (!validTypes.includes(type)) {
    return { valid: false, message: '无效的策略类型' }
  }

  // 验证参数
  if (!parameters || typeof parameters !== 'object') {
    return { valid: false, message: '策略参数不能为空' }
  }

  return { valid: true }
}

/**
 * 验证订单参数
 * @param params 订单参数
 * @returns 验证结果
 */
export function validateOrderParams(params: {
  symbol: string
  type: string
  direction: string
  quantity: number
  price?: number
}): ValidationResult {
  const { symbol, type, direction, quantity, price } = params

  // 验证股票代码
  if (!isStockSymbol(symbol)) {
    return { valid: false, message: '无效的股票代码' }
  }

  // 验证订单类型
  const validTypes = ['market', 'limit', 'stop', 'stop_limit']
  if (!validTypes.includes(type)) {
    return { valid: false, message: '无效的订单类型' }
  }

  // 验证交易方向
  const validDirections = ['long', 'short']
  if (!validDirections.includes(direction)) {
    return { valid: false, message: '无效的交易方向' }
  }

  // 验证数量
  if (!isInteger(quantity) || quantity <= 0) {
    return { valid: false, message: '数量必须为正整数' }
  }

  // 验证价格（限价单需要价格）
  if ((type === 'limit' || type === 'stop_limit') && (!isNumber(price) || price <= 0)) {
    return { valid: false, message: '价格必须为正数' }
  }

  return { valid: true }
}