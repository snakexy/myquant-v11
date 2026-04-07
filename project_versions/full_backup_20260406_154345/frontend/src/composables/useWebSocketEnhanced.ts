/**
 * MyQuant v9.0.0 - Enhanced WebSocket Composable
 * 增强版WebSocket客户端 - 支持K线、板块、指标实时更新
 */

import { ref, onUnmounted } from 'vue'
import { logger } from '@/utils/logger'

export interface QuoteUpdate {
  type: 'quote_update' | 'quote_snapshot'
  symbol: string
  data: any
  timestamp: string
}

export interface KlineUpdate {
  type: 'kline_update'
  symbol: string
  period: string
  data: any[]
  timestamp: string
}

export interface SectorUpdate {
  type: 'sector_update'
  sector_code: string
  data: any
  timestamp: string
}

export interface IndicatorUpdate {
  type: 'indicator_update'
  symbol: string
  data: any
  timestamp: string
}

export type MessageUpdate = QuoteUpdate | KlineUpdate | SectorUpdate | IndicatorUpdate

export function useWebSocketEnhanced() {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const subscribedQuotes = ref<Set<string>>(new Set())
  const subscribedKlines = ref<Map<string, string>>(new Map())  // symbol -> period
  const subscribedSectors = ref<Set<string>>(new Set())

  // 更新回调
  const onQuoteUpdate = ref<(update: QuoteUpdate) => void>(() => {})
  const onKlineUpdate = ref<(update: KlineUpdate) => void>(() => {})
  const onSectorUpdate = ref<(update: SectorUpdate) => void>(() => {})
  const onIndicatorUpdate = ref<(update: IndicatorUpdate) => void>(() => {})

  /**
   * 连接WebSocket
   */
  const connect = () => {
    // 根据页面协议自动选择ws://或wss://
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = import.meta.env.VITE_WS_URL_ENHANCED || `${protocol}//${window.location.host}/ws/enhanced`

    try {
      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = () => {
        console.log('[WS-Enhanced] Connected')
        connected.value = true
        logger.info('增强版WebSocket已连接')
      }

      ws.value.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          switch (message.type) {
            case 'quote_update':
            case 'quote_snapshot':
              onQuoteUpdate.value(message)
              break

            case 'kline_update':
              onKlineUpdate.value(message)
              break

            case 'sector_update':
              onSectorUpdate.value(message)
              break

            case 'indicator_update':
              onIndicatorUpdate.value(message)
              break

            case 'pong':
              // 心跳响应
              break

            default:
              console.warn('[WS-Enhanced] Unknown message type:', message.type)
          }
        } catch (error) {
          console.error('[WS-Enhanced] Failed to parse message:', error)
        }
      }

      ws.value.onclose = () => {
        console.log('[WS-Enhanced] Disconnected')
        connected.value = false
        logger.warn('增强版WebSocket已断开')

        // 5秒后重连
        setTimeout(() => {
          if (!connected.value) {
            connect()
          }
        }, 5000)
      }

      ws.value.onerror = (error) => {
        console.error('[WS-Enhanced] Error:', error)
        logger.error('增强版WebSocket错误')
      }
    } catch (error) {
      console.error('[WS-Enhanced] Failed to connect:', error)
      logger.error('增强版WebSocket连接失败')
    }
  }

  /**
   * 订阅股票行情
   */
  const subscribeQuotes = (symbols: string[]) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      console.warn('[WS-Enhanced] Not connected')
      return
    }

    const message = {
      type: 'subscribe_quotes',
      symbols: symbols
    }

    ws.value.send(JSON.stringify(message))

    symbols.forEach(symbol => subscribedQuotes.value.add(symbol))
    console.log('[WS-Enhanced] Subscribed to quotes:', symbols)
  }

  /**
   * 取消订阅行情
   */
  const unsubscribeQuotes = (symbols: string[]) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      return
    }

    const message = {
      type: 'unsubscribe_quotes',
      symbols: symbols
    }

    ws.value.send(JSON.stringify(message))

    symbols.forEach(symbol => subscribedQuotes.value.delete(symbol))
    console.log('[WS-Enhanced] Unsubscribed from quotes:', symbols)
  }

  /**
   * 订阅K线数据
   */
  const subscribeKlines = (symbol: string, period: string = 'day', count: number = 100) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      console.warn('[WS-Enhanced] Not connected')
      return
    }

    const message = {
      type: 'subscribe_klines',
      symbol: symbol,
      period: period,
      count: count
    }

    ws.value.send(JSON.stringify(message))

    subscribedKlines.value.set(symbol, period)
    console.log(`[WS-Enhanced] Subscribed to K-line: ${symbol} (${period})`)
  }

  /**
   * 取消订阅K线
   */
  const unsubscribeKlines = (symbol: string) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      return
    }

    const message = {
      type: 'unsubscribe_klines',
      symbol: symbol
    }

    ws.value.send(JSON.stringify(message))

    subscribedKlines.value.delete(symbol)
    console.log(`[WS-Enhanced] Unsubscribed from K-line: ${symbol}`)
  }

  /**
   * 订阅板块数据
   */
  const subscribeSectors = (sectors: string[]) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      console.warn('[WS-Enhanced] Not connected')
      return
    }

    const message = {
      type: 'subscribe_sectors',
      sectors: sectors
    }

    ws.value.send(JSON.stringify(message))

    sectors.forEach(sector => subscribedSectors.value.add(sector))
    console.log('[WS-Enhanced] Subscribed to sectors:', sectors)
  }

  /**
   * 取消订阅板块
   */
  const unsubscribeSectors = (sectors: string[]) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      return
    }

    const message = {
      type: 'unsubscribe_sectors',
      sectors: sectors
    }

    ws.value.send(JSON.stringify(message))

    sectors.forEach(sector => subscribedSectors.value.delete(sector))
    console.log('[WS-Enhanced] Unsubscribed from sectors:', sectors)
  }

  /**
   * 发送心跳
   */
  const sendPing = () => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      return
    }

    ws.value.send(JSON.stringify({ type: 'ping' }))
  }

  /**
   * 断开连接
   */
  const disconnect = () => {
    if (ws.value) {
      ws.value.close()
      ws.value = null
      connected.value = false
    }
  }

  // 组件卸载时断开连接
  onUnmounted(() => {
    disconnect()
  })

  // 心跳检测
  const heartbeatInterval = setInterval(() => {
    if (connected.value) {
      sendPing()
    }
  }, 30000)

  // 清理心跳
  onUnmounted(() => {
    clearInterval(heartbeatInterval)
  })

  return {
    connected,
    subscribedQuotes,
    subscribedKlines,
    subscribedSectors,
    onQuoteUpdate,
    onKlineUpdate,
    onSectorUpdate,
    onIndicatorUpdate,
    connect,
    subscribeQuotes,
    unsubscribeQuotes,
    subscribeKlines,
    unsubscribeKlines,
    subscribeSectors,
    unsubscribeSectors,
    sendPing,
    disconnect
  }
}


/**
 * 全局增强版WebSocket实例
 */
let globalEnhancedWs: ReturnType<typeof useWebSocketEnhanced> | null = null

export function useGlobalWebSocketEnhanced() {
  if (!globalEnhancedWs) {
    globalEnhancedWs = useWebSocketEnhanced()
    globalEnhancedWs.connect()
  }

  return globalEnhancedWs
}
