import { describe, it, expect } from 'vitest'
import { 
  formatNumber, 
  formatPercentage, 
  formatCurrency, 
  formatDate, 
  formatRelativeTime,
  formatFileSize 
} from '../format'

describe('格式化函数测试', () => {
  describe('formatNumber', () => {
    it('应该正确格式化整数', () => {
      expect(formatNumber(1234)).toBe('1,234.00')
      expect(formatNumber(0)).toBe('0.00')
      expect(formatNumber(-1234)).toBe('-1,234.00')
    })

    it('应该正确格式化小数', () => {
      expect(formatNumber(1234.567)).toBe('1,234.57')
      expect(formatNumber(1234.567, { decimals: 3 })).toBe('1,234.567')
    })

    it('应该处理无效数字', () => {
      expect(formatNumber(NaN)).toBe('无效数字')
    })
  })

  describe('formatPercentage', () => {
    it('应该正确格式化百分比', () => {
      expect(formatPercentage(0.1234)).toBe('12.34%')
      expect(formatPercentage(0.1234, 1)).toBe('12.3%')
      expect(formatPercentage(0)).toBe('0.00%')
    })

    it('应该处理负值', () => {
      expect(formatPercentage(-0.1234)).toBe('12.34%')
    })

    it('应该处理无效百分比', () => {
      expect(formatPercentage(NaN)).toBe('无效百分比')
    })
  })

  describe('formatCurrency', () => {
    it('应该正确格式化货币', () => {
      expect(formatCurrency(1234.56)).toBe('¥1,234.56')
      expect(formatCurrency(1234.56, 'USD', 'en-US')).toBe('$1,234.56')
    })

    it('应该处理大数值', () => {
      expect(formatCurrency(1234567.89)).toBe('¥1,234,567.89')
    })
  })

  describe('formatDate', () => {
    it('应该正确格式化日期', () => {
      const date = new Date('2023-12-08T14:30:00')
      expect(formatDate(date)).toContain('2023')
      expect(formatDate('2023-12-08')).toContain('2023')
    })

    it('应该支持自定义格式', () => {
      const date = new Date('2023-12-08T14:30:00')
      expect(formatDate(date, { showTime: false })).not.toContain(':')
    })

    it('应该处理无效日期', () => {
      expect(formatDate('invalid')).toBe('无效日期')
    })
  })

  describe('formatRelativeTime', () => {
    it('应该正确格式化相对时间', () => {
      const now = new Date()
      const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)
      expect(formatRelativeTime(oneHourAgo)).toBe('1小时前')
    })

    it('应该处理无效日期', () => {
      expect(formatRelativeTime('invalid')).toBe('无效日期')
    })
  })

  describe('formatFileSize', () => {
    it('应该正确格式化文件大小', () => {
      expect(formatFileSize(1024)).toBe('1.00 KB')
      expect(formatFileSize(1048576)).toBe('1.00 MB')
      expect(formatFileSize(1073741824)).toBe('1.00 GB')
    })

    it('应该处理小数值', () => {
      expect(formatFileSize(1536)).toBe('1.50 KB')
    })

    it('应该处理0字节', () => {
      expect(formatFileSize(0)).toBe('0 B')
    })
  })
})