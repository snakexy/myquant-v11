/**
 * DataStore 单元测试
 * M2-17 Store重构验收测试
 * DataStore是最核心的数据管理中心
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useDataStore } from '../DataStore'

describe('DataStore', () => {
  let dataStore: ReturnType<typeof useDataStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    dataStore = useDataStore()
    localStorage.clear()
  })

  describe('股票基础数据', () => {
    it('应该能够设置股票数据', () => {
      const mockData = {
        '600519.SH': {
          symbol: '600519.SH',
          name: '贵州茅台',
          price: 1850.5,
          change: 1.2
        }
      }

      dataStore.setStockData(mockData)
      expect(dataStore.stockData['600519.SH']).toBeDefined()
    })

    it('应该能够获取单个股票数据', () => {
      const mockData = {
        '600519.SH': {
          symbol: '600519.SH',
          name: '贵州茅台',
          price: 1850.5
        }
      }

      dataStore.setStockData(mockData)
      const stock = dataStore.getStock('600519.SH')

      expect(stock?.name).toBe('贵州茅台')
    })
  })

  describe('实时行情', () => {
    it('应该能够更新实时行情', () => {
      const quotes = [
        { symbol: '600519.SH', price: 1850.5, change: 1.2 },
        { symbol: '000001.SZ', price: 12.5, change: -0.5 }
      ]

      dataStore.updateQuotes(quotes)
      expect(dataStore.quotes['600519.SH']).toBeDefined()
    })

    it('应该能够计算涨跌幅榜', () => {
      const quotes = [
        { symbol: '600519.SH', name: '贵州茅台', price: 1850.5, change: 5.2 },
        { symbol: '000001.SZ', name: '平安银行', price: 12.5, change: -2.5 },
        { symbol: '000002.SZ', name: '万科A', price: 8.5, change: 3.1 }
      ]

      dataStore.updateQuotes(quotes)

      // 验证涨幅榜
      expect(dataStore.topGainers.length).toBeGreaterThan(0)
      expect(dataStore.topGainers[0].change).toBeGreaterThanOrEqual(dataStore.topGainers[1]?.change || 0)

      // 验证跌幅榜
      expect(dataStore.topLosers.length).toBeGreaterThan(0)
      expect(dataStore.topLosers[0].change).toBeLessThanOrEqual(dataStore.topLosers[1]?.change || 0)
    })
  })

  describe('K线数据', () => {
    it('应该能够设置K线数据', () => {
      const klineData = [
        { time: '2024-01-01', open: 1850, high: 1860, low: 1840, close: 1855, volume: 10000 }
      ]

      dataStore.setKlineData('600519.SH', 'day', klineData)
      expect(dataStore.klineData['600519.SH_day']).toBeDefined()
    })

    it('应该能够获取K线数据', () => {
      const klineData = [
        { time: '2024-01-01', open: 1850, high: 1860, low: 1840, close: 1855, volume: 10000 },
        { time: '2024-01-02', open: 1855, high: 1870, low: 1850, close: 1865, volume: 12000 }
      ]

      dataStore.setKlineData('600519.SH', 'day', klineData)
      const retrieved = dataStore.getKlineData('600519.SH', 'day')

      expect(retrieved).toHaveLength(2)
      expect(retrieved[0].close).toBe(1855)
    })
  })

  describe('板块数据', () => {
    it('应该能够设置板块数据', () => {
      const sectors = [
        { name: '白酒', change: 2.5, stocks: ['600519.SH'] },
        { name: '银行', change: -1.2, stocks: ['000001.SZ'] }
      ]

      dataStore.setSectors(sectors)
      expect(dataStore.sectors.length).toBe(2)
    })

    it('应该能够计算热门板块', () => {
      const sectors = [
        { name: '白酒', change: 3.5, stocks: [] },
        { name: '银行', change: -2.5, stocks: [] },
        { name: '科技', change: 2.1, stocks: [] }
      ]

      dataStore.setSectors(sectors)

      expect(dataStore.hotSectors.length).toBeGreaterThan(0)
      expect(dataStore.hotSectors[0].change).toBeGreaterThanOrEqual(0)
    })
  })

  describe('自选股管理', () => {
    it('应该能够添加自选股', () => {
      dataStore.addToWatchlist('600519.SH', '贵州茅台')

      expect(dataStore.watchlist.some(w => w.symbol === '600519.SH')).toBe(true)
    })

    it('应该能够移除自选股', () => {
      dataStore.addToWatchlist('600519.SH', '贵州茅台')
      dataStore.removeFromWatchlist('600519.SH')

      expect(dataStore.watchlist.some(w => w.symbol === '600519.SH')).toBe(false)
    })

    it('不应该重复添加自选股', () => {
      dataStore.addToWatchlist('600519.SH', '贵州茅台')
      dataStore.addToWatchlist('600519.SH', '贵州茅台')

      const count = dataStore.watchlist.filter(w => w.symbol === '600519.SH').length
      expect(count).toBe(1)
    })

    it('应该能够持久化自选股', () => {
      dataStore.addToWatchlist('600519.SH', '贵州茅台')
      dataStore.addToWatchlist('000001.SZ', '平安银行')

      // 保存到localStorage
      dataStore.saveWatchlist()

      const saved = localStorage.getItem('data-store-watchlist')
      expect(saved).not.toBeNull()

      if (saved) {
        const parsed = JSON.parse(saved)
        expect(parsed).toHaveLength(2)
      }
    })
  })

  describe('数据源管理', () => {
    it('应该能够设置数据源', () => {
      dataStore.setDataSource('XtQuant')
      expect(dataStore.dataSource).toBe('XtQuant')
    })

    it('应该支持的数据源列表', () => {
      const sources = ['XtQuant', 'TDX', 'QLib', 'Online']

      sources.forEach(source => {
        dataStore.setDataSource(source as any)
        expect(dataStore.dataSource).toBe(source)
      })
    })
  })

  describe('搜索和筛选', () => {
    it('应该能够搜索股票', () => {
      const stocks = [
        { symbol: '600519.SH', name: '贵州茅台', pinyin: 'gzmt' },
        { symbol: '000001.SZ', name: '平安银行', pinyin: 'payh' }
      ]

      dataStore.setStockSearchResults(stocks)

      const results = dataStore.searchStocks('茅台')
      expect(results.length).toBeGreaterThan(0)
    })
  })

  describe('计算属性', () => {
    it('应该正确计算市场统计', () => {
      const quotes = [
        { symbol: '600519.SH', price: 1850.5, change: 1.2, amount: 10000 },
        { symbol: '000001.SZ', price: 12.5, change: -0.5, amount: 5000 }
      ]

      dataStore.updateQuotes(quotes)

      const stats = dataStore.marketStats
      expect(stats).toHaveProperty('totalStocks')
      expect(stats).toHaveProperty('upCount')
      expect(stats).toHaveProperty('downCount')
    })

    it('应该正确计算板块统计', () => {
      const sectors = [
        { name: '白酒', change: 2.5, stocks: [] },
        { name: '银行', change: -1.2, stocks: [] }
      ]

      dataStore.setSectors(sectors)

      const stats = dataStore.sectorStats
      expect(stats.totalSectors).toBe(2)
    })
  })
})
