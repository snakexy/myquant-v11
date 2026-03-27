// Mock数据服务 - 已禁用，使用QuantDataHub获取真实数据
// import { StockInfo, RealtimeData, IndicatorData } from './modules/data'

// 模拟延迟
const delay = (ms: number = 500) => new Promise(resolve => setTimeout(resolve, ms))

// 模拟股票数据
const mockStockList: StockInfo[] = [
  {
    code: '000001',
    name: '平安银行',
    market: 'SZ',
    sector: '金融',
    industry: '银行',
    currentPrice: 12.50,
    changePercent: 1.25,
    volume: 52000000,
    marketCap: 242500000000,
    pe: 5.8,
    pb: 0.65,
    roe: 11.2,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '000002',
    name: '万科A',
    market: 'SZ',
    sector: '房地产',
    industry: '房地产开发',
    currentPrice: 18.86,
    changePercent: -0.85,
    volume: 31000000,
    marketCap: 208000000000,
    pe: 7.2,
    pb: 0.85,
    roe: 9.5,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '600519',
    name: '贵州茅台',
    market: 'SH',
    sector: '消费',
    industry: '白酒',
    currentPrice: 1685.00,
    changePercent: 2.15,
    volume: 1200000,
    marketCap: 2112500000000,
    pe: 28.5,
    pb: 9.8,
    roe: 25.6,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '000858',
    name: '五粮液',
    market: 'SZ',
    sector: '消费',
    industry: '白酒',
    currentPrice: 156.30,
    changePercent: 1.85,
    volume: 8900000,
    marketCap: 603000000000,
    pe: 22.3,
    pb: 5.6,
    roe: 18.9,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '600036',
    name: '招商银行',
    market: 'SH',
    sector: '金融',
    industry: '银行',
    currentPrice: 32.15,
    changePercent: 0.95,
    volume: 28000000,
    marketCap: 815000000000,
    pe: 6.8,
    pb: 0.85,
    roe: 12.5,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '002415',
    name: '海康威视',
    market: 'SZ',
    sector: '科技',
    industry: '安防',
    currentPrice: 42.80,
    changePercent: -1.25,
    volume: 45000000,
    marketCap: 398000000000,
    pe: 18.5,
    pb: 3.2,
    roe: 17.8,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '300059',
    name: '东方财富',
    market: 'SZ',
    sector: '金融',
    industry: '证券',
    currentPrice: 18.95,
    changePercent: 3.25,
    volume: 68000000,
    marketCap: 298000000000,
    pe: 32.5,
    pb: 4.8,
    roe: 8.9,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '601318',
    name: '中国平安',
    market: 'SH',
    sector: '金融',
    industry: '保险',
    currentPrice: 45.20,
    changePercent: 0.65,
    volume: 58000000,
    marketCap: 828000000000,
    pe: 9.2,
    pb: 0.92,
    roe: 10.2,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '000001',
    name: '上证指数',
    market: 'SH',
    sector: '指数',
    industry: '综合',
    currentPrice: 3080.52,
    changePercent: 0.35,
    volume: 285000000000,
    marketCap: 0,
    pe: 0,
    pb: 0,
    roe: 0,
    lastUpdate: new Date().toISOString()
  },
  {
    code: '399001',
    name: '深证成指',
    market: 'SZ',
    sector: '指数',
    industry: '综合',
    currentPrice: 11250.85,
    changePercent: 0.65,
    volume: 325000000000,
    marketCap: 0,
    pe: 0,
    pb: 0,
    roe: 0,
    lastUpdate: new Date().toISOString()
  }
]

// 生成模拟历史数据
const generateHistoryData = (basePrice: number, days: number = 30) => {
  const data = []
  let currentPrice = basePrice

  for (let i = days; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)

    const change = (Math.random() - 0.5) * basePrice * 0.05
    currentPrice = Math.max(basePrice * 0.7, Math.min(basePrice * 1.3, currentPrice + change))

    data.push({
      date: date.toISOString().split('T')[0],
      open: currentPrice * (1 + (Math.random() - 0.5) * 0.02),
      high: currentPrice * (1 + Math.random() * 0.03),
      low: currentPrice * (1 - Math.random() * 0.03),
      close: currentPrice,
      volume: Math.floor(Math.random() * 10000000) + 1000000,
      amount: currentPrice * (Math.floor(Math.random() * 10000000) + 1000000)
    })
  }

  return data
}

// Mock API响应
const createMockResponse = (data: any) => ({
  code: 200,
  message: 'success',
  data,
  success: true
})

// Mock数据服务
export const mockService = {
  // 获取股票列表
  async getStockList(params?: any) {
    await delay()
    let result = [...mockStockList]

    if (params?.market) {
      result = result.filter(stock => stock.market === params.market || stock.sector === '指数')
    }

    if (params?.sector) {
      result = result.filter(stock => stock.sector === params.sector)
    }

    if (params?.page && params?.size) {
      const start = (params.page - 1) * params.size
      result = result.slice(start, start + params.size)
    }

    return createMockResponse(result)
  },

  // 获取股票详情
  async getStockDetail(code: string) {
    await delay()
    const stock = mockStockList.find(s => s.code === code)
    if (!stock) {
      throw new Error('股票不存在')
    }
    return createMockResponse(stock)
  },

  // 获取历史数据
  async getStockHistory(code: string, params: any) {
    await delay()
    const stock = mockStockList.find(s => s.code === code)
    if (!stock) {
      throw new Error('股票不存在')
    }

    const days = params?.frequency === 'daily' ? 30 :
                  params?.frequency === 'weekly' ? 12 : 24

    const historyData = generateHistoryData(stock.currentPrice, days)
    return createMockResponse(historyData)
  },

  // 获取实时数据
  async getRealtimeData(codes: string[]) {
    await delay()
    const data: RealtimeData[] = codes.map(code => {
      const stock = mockStockList.find(s => s.code === code)
      if (!stock) {
        return {
          code,
          name: code,
          price: 0,
          change: 0,
          changePercent: 0,
          volume: 0,
          timestamp: new Date().toISOString()
        }
      }

      const change = stock.currentPrice * (stock.changePercent / 100)
      return {
        code: stock.code,
        name: stock.name,
        price: stock.currentPrice,
        change: change,
        changePercent: stock.changePercent,
        volume: stock.volume,
        timestamp: stock.lastUpdate
      }
    })

    return createMockResponse(data)
  },

  // 获取技术指标
  async getIndicators(code: string, indicators: string[]) {
    await delay()
    const stock = mockStockList.find(s => s.code === code)
    if (!stock) {
      throw new Error('股票不存在')
    }

    const indicatorData: IndicatorData = {
      code: stock.code,
      name: stock.name,
      values: {},
      timestamp: new Date().toISOString()
    }

    indicators.forEach(indicator => {
      switch (indicator) {
        case 'MA5':
          indicatorData.values[indicator] = stock.currentPrice * 0.98
          break
        case 'MA10':
          indicatorData.values[indicator] = stock.currentPrice * 0.95
          break
        case 'MA20':
          indicatorData.values[indicator] = stock.currentPrice * 0.92
          break
        case 'MA60':
          indicatorData.values[indicator] = stock.currentPrice * 0.88
          break
        case 'RSI':
          indicatorData.values[indicator] = 30 + Math.random() * 40
          break
        case 'MACD':
          indicatorData.values[indicator] = (Math.random() - 0.5) * 2
          break
        case 'KDJ_K':
          indicatorData.values[indicator] = 20 + Math.random() * 60
          break
        case 'KDJ_D':
          indicatorData.values[indicator] = 20 + Math.random() * 60
          break
        case 'KDJ_J':
          indicatorData.values[indicator] = 20 + Math.random() * 60
          break
      }
    })

    return createMockResponse(indicatorData)
  },

  // 获取热门股票
  async getHotStocks(limit: number = 10) {
    await delay()
    const shuffled = [...mockStockList].sort(() => Math.random() - 0.5)
    return createMockResponse(shuffled.slice(0, limit))
  },

  // 搜索股票
  async searchStocks(keyword: string, limit: number = 10) {
    await delay()
    const result = mockStockList.filter(stock =>
      stock.name.includes(keyword) || stock.code.includes(keyword)
    ).slice(0, limit)
    return createMockResponse(result)
  },

  // 获取板块信息
  async getSectors() {
    await delay()
    const sectors = [
      { id: 'finance', name: '金融', count: 3 },
      { id: 'tech', name: '科技', count: 1 },
      { id: 'consumer', name: '消费', count: 2 },
      { id: 'estate', name: '房地产', count: 1 },
      { id: 'index', name: '指数', count: 2 }
    ]
    return createMockResponse(sectors)
  },

  // 获取数据质量
  async getDataQuality() {
    await delay()
    return createMockResponse({
      completeness: 99.5,
      accuracy: 99.8,
      timeliness: 99.2,
      consistency: 99.6,
      lastUpdate: new Date().toISOString()
    })
  },

  // 获取数据源状态
  async getDataSources() {
    await delay()
    return createMockResponse([
      {
        id: 'tushare',
        name: 'Tushare数据源',
        status: 'connected',
        lastUpdate: new Date().toISOString(),
        latency: 120,
        errorCount: 0
      },
      {
        id: 'akshare',
        name: 'AKShare数据源',
        status: 'connected',
        lastUpdate: new Date().toISOString(),
        latency: 150,
        errorCount: 0
      }
    ])
  }
}