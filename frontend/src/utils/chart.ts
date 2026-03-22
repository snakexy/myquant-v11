// 图表工具函数库
import type { ChartType } from '@/types/global'

// 扩展图表配置接口
interface ExtendedChartConfig {
  title?: string
  subtitle?: string
  width?: number
  height?: number
  theme?: 'light' | 'dark'
  animation?: boolean
  legend?: boolean | any
  grid?: boolean | any
  tooltip?: boolean | any
  colors?: string[]
  radius?: string
  center?: string[]
  showLabel?: boolean
  showPercent?: boolean
  showVolume?: boolean
  showMA?: boolean
  maPeriods?: number[]
  xAxisData?: any[]
  yAxisData?: any[]
  maxValue?: number
  series?: ExtendedChartSeries[]
  type?: ChartType
}

interface ExtendedChartSeries {
  name: string
  data?: any[]
  type?: string
  smooth?: boolean
  symbol?: string
  symbolSize?: number
  lineWidth?: number
  color?: string
  area?: boolean
  barWidth?: string | number
  borderRadius?: number[]
}

// 模拟 echarts 类型
interface EChartsInstance {
  getOption(): any
  setOption(option: any): void
  getDataURL(options?: any): string
}

/**
 * 图表工具类
 */
export class ChartUtils {
  /**
   * 创建基础图表配置
   * @param type 图表类型
   * @param config 图表配置
   * @returns ECharts配置对象
   */
  static createBaseChart(type: ChartType, config: ExtendedChartConfig = {}): any {
    const {
      title,
      subtitle,
      width,
      height,
      theme = 'dark',
      animation = true,
      legend = true,
      grid = true,
      tooltip = true,
      colors = this.getDefaultColors(theme)
    } = config

    const baseConfig: any = {
      backgroundColor: 'transparent',
      animation,
      color: colors,
      title: title ? {
        text: title,
        subtext: subtitle,
        left: 'center',
        textStyle: {
          color: theme === 'dark' ? '#ffffff' : '#333333',
          fontSize: 16,
          fontWeight: 'bold'
        },
        subtextStyle: {
          color: theme === 'dark' ? '#cccccc' : '#666666',
          fontSize: 12
        }
      } : undefined,
      legend: legend ? {
        show: true,
        top: 'top',
        left: 'center',
        textStyle: {
          color: theme === 'dark' ? '#ffffff' : '#333333'
        }
      } : { show: false },
      grid: grid ? {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
        borderColor: theme === 'dark' ? '#444444' : '#e0e0e0',
        borderWidth: 1
      } : undefined,
      tooltip: tooltip ? {
        trigger: 'axis',
        backgroundColor: theme === 'dark' ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
        borderColor: theme === 'dark' ? '#444444' : '#e0e0e0',
        borderWidth: 1,
        textStyle: {
          color: theme === 'dark' ? '#ffffff' : '#333333'
        }
      } : { show: false }
    }

    return baseConfig
  }

  /**
   * 创建折线图配置
   * @param data 数据
   * @param config 配置
   * @returns ECharts配置对象
   */
  static createLineChart(data: any[], config: ExtendedChartConfig = {}): any {
    const baseConfig = this.createBaseChart('line', config)
    const { series = [] } = config

    return {
      ...baseConfig,
      xAxis: {
        type: 'category',
        data: data.map(item => item.name || item.x),
        axisLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
          }
        },
        axisLabel: {
          color: config.theme === 'dark' ? '#cccccc' : '#666666'
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
          }
        },
        axisLabel: {
          color: config.theme === 'dark' ? '#cccccc' : '#666666'
        },
        splitLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#333333' : '#f0f0f0'
          }
        }
      },
      series: series.map((s: ExtendedChartSeries) => ({
        name: s.name,
        type: 'line',
        data: s.data || data.map(item => item.value || item.y),
        smooth: s.smooth || false,
        symbol: s.symbol || 'circle',
        symbolSize: s.symbolSize || 6,
        lineStyle: {
          width: s.lineWidth || 2,
          color: s.color
        },
        itemStyle: {
          color: s.color
        },
        areaStyle: s.area ? {
          opacity: 0.3
        } : undefined
      }))
    }
  }

  /**
   * 创建柱状图配置
   * @param data 数据
   * @param config 配置
   * @returns ECharts配置对象
   */
  static createBarChart(data: any[], config: ExtendedChartConfig = {}): any {
    const baseConfig = this.createBaseChart('bar', config)
    const { series = [] } = config

    return {
      ...baseConfig,
      xAxis: {
        type: 'category',
        data: data.map(item => item.name || item.x),
        axisLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
          }
        },
        axisLabel: {
          color: config.theme === 'dark' ? '#cccccc' : '#666666'
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
          }
        },
        axisLabel: {
          color: config.theme === 'dark' ? '#cccccc' : '#666666'
        },
        splitLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#333333' : '#f0f0f0'
          }
        }
      },
      series: series.map((s: ExtendedChartSeries) => ({
        name: s.name,
        type: 'bar',
        data: s.data || data.map(item => item.value || item.y),
        barWidth: s.barWidth || '60%',
        itemStyle: {
          color: s.color,
          borderRadius: s.borderRadius || [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }))
    }
  }

  /**
   * 创建K线图配置
   * @param data K线数据
   * @param config 配置
   * @returns ECharts配置对象
   */
  static createCandlestickChart(data: any[], config: ExtendedChartConfig = {}): any {
    const baseConfig = this.createBaseChart('candlestick', config)
    const { showVolume = true, showMA = true, maPeriods = [5, 10, 20] } = config

    const candlestickData = data.map(item => [
      item.open,
      item.close,
      item.low,
      item.high
    ])

    const volumeData = data.map(item => item.volume)
    const categoryData = data.map(item => item.timestamp || item.date)

    const series: any[] = [
      {
        name: 'K线',
        type: 'candlestick',
        data: candlestickData,
        itemStyle: {
          color: '#10b981', // 阳线颜色
          color0: '#ef4444', // 阴线颜色
          borderColor: '#10b981',
          borderColor0: '#ef4444'
        }
      }
    ]

    // 添加移动平均线
    if (showMA) {
      maPeriods.forEach(period => {
        const maData = this.calculateMA(data, period)
        series.push({
          name: `MA${period}`,
          type: 'line',
          data: maData,
          smooth: true,
          lineStyle: {
            width: 1,
            color: this.getMAColor(period)
          },
          symbol: 'none'
        })
      })
    }

    // 添加成交量
    if (showVolume) {
      series.push({
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumeData,
        itemStyle: {
          color: (params: any) => {
            const klineData = data[params.dataIndex]
            return klineData.close >= klineData.open ? '#10b981' : '#ef4444'
          }
        }
      })
    }

    return {
      ...baseConfig,
      xAxis: [
        {
          type: 'category',
          data: categoryData,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        },
        {
          type: 'category',
          gridIndex: 1,
          data: categoryData,
          axisLabel: { show: false }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true
          },
          axisLine: {
            lineStyle: {
              color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
            }
          },
          axisLabel: {
            color: config.theme === 'dark' ? '#cccccc' : '#666666'
          },
          splitLine: {
            lineStyle: {
              color: config.theme === 'dark' ? '#333333' : '#f0f0f0'
            }
          }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          splitLine: { show: false }
        }
      ],
      grid: [
        {
          left: '10%',
          right: '8%',
          height: '50%'
        },
        {
          left: '10%',
          right: '8%',
          top: '63%',
          height: '16%'
        }
      ],
      series
    }
  }

  /**
   * 创建饼图配置
   * @param data 数据
   * @param config 配置
   * @returns ECharts配置对象
   */
  static createPieChart(data: any[], config: ExtendedChartConfig = {}): any {
    const baseConfig = this.createBaseChart('pie', config)
    const { showLabel = true, showPercent = true } = config

    return {
      ...baseConfig,
      series: [
        {
          name: '数据',
          type: 'pie',
          radius: config.radius || '50%',
          center: config.center || ['50%', '50%'],
          data: data.map(item => ({
            value: item.value,
            name: item.name,
            itemStyle: {
              color: item.color
            }
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            show: showLabel,
            formatter: showPercent 
              ? '{b}: {c} ({d}%)'
              : '{b}: {c}',
            color: config.theme === 'dark' ? '#ffffff' : '#333333'
          },
          labelLine: {
            show: true,
            lineStyle: {
              color: config.theme === 'dark' ? '#cccccc' : '#666666'
            }
          }
        }
      ]
    }
  }

  /**
   * 创建散点图配置
   * @param data 数据
   * @param config 配置
   * @returns ECharts配置对象
   */
  static createScatterChart(data: any[], config: ExtendedChartConfig = {}): any {
    const baseConfig = this.createBaseChart('scatter', config)
    const { series = [] } = config

    return {
      ...baseConfig,
      xAxis: {
        type: 'value',
        scale: true,
        axisLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
          }
        },
        axisLabel: {
          color: config.theme === 'dark' ? '#cccccc' : '#666666'
        },
        splitLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#333333' : '#f0f0f0'
          }
        }
      },
      yAxis: {
        type: 'value',
        scale: true,
        axisLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
          }
        },
        axisLabel: {
          color: config.theme === 'dark' ? '#cccccc' : '#666666'
        },
        splitLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#333333' : '#f0f0f0'
          }
        }
      },
      series: series.map((s: ExtendedChartSeries) => ({
        name: s.name,
        type: 'scatter',
        data: s.data || data,
        symbolSize: s.symbolSize || 8,
        itemStyle: {
          color: s.color
        }
      }))
    }
  }

  /**
   * 创建热力图配置
   * @param data 数据
   * @param config 配置
   * @returns ECharts配置对象
   */
  static createHeatmapChart(data: any[], config: ExtendedChartConfig = {}): any {
    const baseConfig = this.createBaseChart('heatmap', config)
    const { xAxisData, yAxisData } = config

    return {
      ...baseConfig,
      xAxis: {
        type: 'category',
        data: xAxisData,
        splitArea: {
          show: true
        },
        axisLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
          }
        },
        axisLabel: {
          color: config.theme === 'dark' ? '#cccccc' : '#666666'
        }
      },
      yAxis: {
        type: 'category',
        data: yAxisData,
        splitArea: {
          show: true
        },
        axisLine: {
          lineStyle: {
            color: config.theme === 'dark' ? '#444444' : '#e0e0e0'
          }
        },
        axisLabel: {
          color: config.theme === 'dark' ? '#cccccc' : '#666666'
        }
      },
      visualMap: {
        min: 0,
        max: config.maxValue || 100,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '0%',
        textStyle: {
          color: config.theme === 'dark' ? '#ffffff' : '#333333'
        },
        inRange: {
          color: config.colors || [
            '#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8'
          ]
        }
      },
      series: [
        {
          name: '热力图',
          type: 'heatmap',
          data: data,
          label: {
            show: true,
            color: config.theme === 'dark' ? '#ffffff' : '#333333'
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
  }

  /**
   * 计算移动平均线
   * @param data K线数据
   * @param period 周期
   * @returns MA数据数组
   */
  static calculateMA(data: any[], period: number): number[] {
    const result: number[] = []
    
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push(null)
      } else {
        let sum = 0
        for (let j = 0; j < period; j++) {
          sum += data[i - j].close
        }
        result.push(sum / period)
      }
    }
    
    return result
  }

  /**
   * 获取默认颜色方案
   * @param theme 主题
   * @returns 颜色数组
   */
  static getDefaultColors(theme: string = 'dark'): string[] {
    if (theme === 'dark') {
      return [
        '#00ff88', // 亮绿 - 数据输入
        '#ffaa00', // 橙色 - 数据处理
        '#0088ff', // 亮蓝 - 数据输出
        '#ff0066', // 亮红 - 错误
        '#ff6b6b', // 红色
        '#4ecdc4', // 绿色
        '#45b7d1', // 蓝色
        '#96ceb4', // 青色
        '#ffeaa7', // 黄色
        '#dfe6e9', // 浅绿
        '#a29bfe', // 紫色
        '#fd79a8'  // 粉色
      ]
    } else {
      return [
        '#1890ff', // 蓝色
        '#52c41a', // 绿色
        '#faad14', // 橙色
        '#f5222d', // 红色
        '#722ed1', // 紫色
        '#eb2f96', // 粉色
        '#13c2c2', // 青色
        '#52c41a', // 绿色
        '#1890ff', // 蓝色
        '#faad14', // 橙色
        '#f5222d'  // 红色
      ]
    }
  }

  /**
   * 获取移动平均线颜色
   * @param period 周期
   * @returns 颜色值
   */
  static getMAColor(period: number): string {
    const colorMap: Record<number, string> = {
      5: '#ff6b6b',
      10: '#4ecdc4',
      20: '#45b7d1',
      30: '#96ceb4',
      60: '#ffeaa7'
    }
    return colorMap[period] || '#a29bfe'
  }

  /**
   * 格式化图表数据
   * @param rawData 原始数据
   * @param type 图表类型
   * @returns 格式化后的数据
   */
  static formatChartData(rawData: any[], type: ChartType): any[] {
    switch (type) {
      case 'line':
      case 'bar':
        return rawData.map(item => ({
          name: item.name || item.label || item.x,
          value: item.value || item.y
        }))
      
      case 'candlestick':
        return rawData.map(item => ({
          timestamp: item.timestamp || item.date,
          open: item.open,
          close: item.close,
          high: item.high,
          low: item.low,
          volume: item.volume
        }))
      
      case 'pie':
        return rawData.map(item => ({
          name: item.name || item.label,
          value: item.value || item.y
        }))
      
      case 'scatter':
        return rawData.map(item => [item.x, item.y])
      
      case 'heatmap':
        return rawData.map(item => [item.x, item.y, item.value])
      
      default:
        return rawData
    }
  }

  /**
   * 创建响应式图表配置
   * @param config 基础配置
   * @param container 容器元素
   * @returns 响应式配置
   */
  static createResponsiveChart(
    config: ExtendedChartConfig,
    container: HTMLElement
  ): any {
    const rect = container.getBoundingClientRect()
    const width = rect.width
    const height = rect.height

    // 根据容器大小调整配置
    const responsiveConfig = { ...config }
    
    if (width < 768) {
      // 移动端配置
      ;(responsiveConfig as any).legend = { show: false }
      ;(responsiveConfig as any).grid = {
        left: '5%',
        right: '5%',
        top: '10%',
        bottom: '10%'
      }
    } else if (width < 1024) {
      // 平板配置
      ;(responsiveConfig as any).legend = {
        show: true,
        top: '5%',
        textStyle: { fontSize: 12 }
      }
      ;(responsiveConfig as any).grid = {
        left: '8%',
        right: '8%',
        top: '15%',
        bottom: '10%'
      }
    }

    return {
      ...this.createBaseChart(config.type || 'line', responsiveConfig),
      width,
      height
    }
  }

  /**
   * 添加图表动画效果
   * @param chart ECharts实例
   * @param animationType 动画类型
   */
  static addAnimation(
    chart: echarts.ECharts,
    animationType: 'fadeIn' | 'scaleIn' | 'slideIn' = 'fadeIn'
  ): void {
    const option = chart.getOption()
    
    switch (animationType) {
      case 'fadeIn':
        option.animation = true
        option.animationDuration = 1000
        option.animationEasing = 'cubicOut'
        break
      
      case 'scaleIn':
        option.animation = true
        option.animationDuration = 800
        option.animationEasing = 'elasticOut'
        break
      
      case 'slideIn':
        option.animation = true
        option.animationDuration = 1200
        option.animationEasing = 'cubicInOut'
        break
    }
    
    chart.setOption(option)
  }

  /**
   * 导出图表为图片
   * @param chart ECharts实例
   * @param filename 文件名
   * @param type 图片类型
   */
  static exportChart(
    chart: echarts.ECharts,
    filename = 'chart',
    type: 'png' | 'jpeg' = 'png'
  ): void {
    const url = chart.getDataURL({
      type,
      pixelRatio: 2,
      backgroundColor: '#fff'
    })
    
    const link = document.createElement('a')
    link.download = `${filename}.${type}`
    link.href = url
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  /**
   * 创建图表主题
   * @param themeName 主题名称
   * @returns 主题配置
   */
  static createChartTheme(themeName: string): any {
    const themes: Record<string, any> = {
      dark: {
        backgroundColor: 'transparent',
        textStyle: {
          color: '#ffffff'
        },
        title: {
          textStyle: {
            color: '#ffffff'
          }
        },
        legend: {
          textStyle: {
            color: '#ffffff'
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#444444',
          textStyle: {
            color: '#ffffff'
          }
        },
        grid: {
          borderColor: '#444444'
        },
        categoryAxis: {
          axisLine: {
            lineStyle: {
              color: '#444444'
            }
          },
          axisTick: {
            lineStyle: {
              color: '#444444'
            }
          },
          axisLabel: {
            color: '#cccccc'
          },
          splitLine: {
            lineStyle: {
              color: '#333333'
            }
          }
        },
        valueAxis: {
          axisLine: {
            lineStyle: {
              color: '#444444'
            }
          },
          axisTick: {
            lineStyle: {
              color: '#444444'
            }
          },
          axisLabel: {
            color: '#cccccc'
          },
          splitLine: {
            lineStyle: {
              color: '#333333'
            }
          }
        }
      },
      light: {
        backgroundColor: 'transparent',
        textStyle: {
          color: '#333333'
        },
        title: {
          textStyle: {
            color: '#333333'
          }
        },
        legend: {
          textStyle: {
            color: '#333333'
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderColor: '#e0e0e0',
          textStyle: {
            color: '#333333'
          }
        },
        grid: {
          borderColor: '#e0e0e0'
        },
        categoryAxis: {
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          },
          axisTick: {
            lineStyle: {
              color: '#e0e0e0'
            }
          },
          axisLabel: {
            color: '#666666'
          },
          splitLine: {
            lineStyle: {
              color: '#f0f0f0'
            }
          }
        },
        valueAxis: {
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          },
          axisTick: {
            lineStyle: {
              color: '#e0e0e0'
            }
          },
          axisLabel: {
            color: '#666666'
          },
          splitLine: {
            lineStyle: {
              color: '#f0f0f0'
            }
          }
        }
      }
    }

    return themes[themeName] || themes.dark
  }

  /**
   * 注册自定义主题
   * @param themeName 主题名称
   * @param themeConfig 主题配置
   */
  static registerTheme(themeName: string, themeConfig: any): void {
    echarts.registerTheme(themeName, themeConfig)
  }

  /**
   * 获取图表统计信息
   * @param data 数据
   * @returns 统计信息
   */
  static getChartStats(data: number[]): {
    min: number
    max: number
    mean: number
    median: number
    std: number
  } {
    const sortedData = [...data].sort((a, b) => a - b)
    const sum = data.reduce((acc, val) => acc + val, 0)
    const mean = sum / data.length
    
    // 计算中位数
    const mid = Math.floor(sortedData.length / 2)
    const median = sortedData.length % 2 === 0
      ? (sortedData[mid - 1] + sortedData[mid]) / 2
      : sortedData[mid]
    
    // 计算标准差
    const squaredDiffs = data.map(value => Math.pow(value - mean, 2))
    const avgSquaredDiff = squaredDiffs.reduce((acc, val) => acc + val, 0) / data.length
    const std = Math.sqrt(avgSquaredDiff)
    
    return {
      min: sortedData[0],
      max: sortedData[sortedData.length - 1],
      mean,
      median,
      std
    }
  }
}