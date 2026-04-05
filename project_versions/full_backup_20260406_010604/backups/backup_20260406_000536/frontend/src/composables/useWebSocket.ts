/**
 * MyQuant v9.0.0 - WebSocket Composable
 * WebSocket客户端 - 实时行情接收
 */

import { ref, onUnmounted } from 'vue'
import { logger } from '@/utils/logger'

export interface QuoteUpdate {
  type: string
  symbol: string
  data: any
  timestamp: string
}

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const subscribedSymbols = ref<Set<string>>(new Set())

  // 行情更新回调
  const onQuoteUpdate = ref<(update: QuoteUpdate) => void>(() => {})

  /**
   * 连接WebSocket
   */
  const connect = () => {
    // 根据页面协议自动选择ws://或wss://
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}/ws`

    try {
      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = () => {
        console.log('WebSocket connected')
        connected.value = true
        logger.info('WebSocket已连接')
      }

      ws.value.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          if (message.type === 'quote_update' || message.type === 'quote_snapshot') {
            onQuoteUpdate.value(message)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.value.onclose = () => {
        console.log('WebSocket disconnected')
        connected.value = false
        logger.warn('WebSocket已断开')

        // 5秒后重连
        setTimeout(() => {
          if (!connected.value) {
            connect()
          }
        }, 5000)
      }

      ws.value.onerror = (error) => {
        console.error('WebSocket error:', error)
        logger.error('WebSocket错误')
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      logger.error('WebSocket连接失败')
    }
  }

  /**
   * 订阅股票行情
   */
  const subscribe = (symbols: string[]) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected')
      return
    }

    const message = {
      type: 'subscribe',
      symbols: symbols
    }

    ws.value.send(JSON.stringify(message))

    // 更新订阅列表
    symbols.forEach(symbol => subscribedSymbols.value.add(symbol))

    console.log('Subscribed to:', symbols)
  }

  /**
   * 取消订阅
   */
  const unsubscribe = (symbols: string[]) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      return
    }

    const message = {
      type: 'unsubscribe',
      symbols: symbols
    }

    ws.value.send(JSON.stringify(message))

    // 更新订阅列表
    symbols.forEach(symbol => subscribedSymbols.value.delete(symbol))

    console.log('Unsubscribed from:', symbols)
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
    subscribedSymbols,
    onQuoteUpdate,
    connect,
    subscribe,
    unsubscribe,
    sendPing,
    disconnect
  }
}

/**
 * 全局WebSocket实例
 */
let globalWs: ReturnType<typeof useWebSocket> | null = null

export function useGlobalWebSocket() {
  if (!globalWs) {
    globalWs = useWebSocket()
    globalWs.connect()
  }

  return globalWs
}
