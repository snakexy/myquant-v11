/**
 * WebSocket Pinia Store v3.1
 *
 * 功能：
 * - 全局WebSocket连接管理
 * - 订阅状态管理
 * - 行情数据管理
 * - 连接状态管理
 *
 * @author Claude
 * @created 2026-01-27
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { WebSocketClient, createWebSocketClient } from '@/services/websocket'
import type { WebSocketMessage } from '@/services/websocket'

export const useWebSocketStore = defineStore('websocket', () => {
  // WebSocket客户端实例
  const client = ref<WebSocketClient | null>(null)

  // 连接状态
  const connected = ref(false)
  const connecting = ref(false)

  // 行情数据 { symbol: quoteData }
  const quotes = ref<Record<string, any>>({})

  // 订阅列表
  const subscriptions = ref<Set<string>>(new Set())

  // 统计信息
  const stats = ref({
    totalMessages: 0,
    quoteUpdates: 0,
    lastUpdateTime: null as string | null
  })

  /**
   * 连接WebSocket
   */
  async function connect(url?: string) {
    // 如果没有提供URL，根据页面协议自动选择
    if (!url) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      url = `${protocol}//${window.location.host}/api/v1/core/ws`
    }

    if (connected.value || connecting.value) {
      console.log('[WebSocketStore] 已连接或正在连接')
      return
    }

    console.log('[WebSocketStore] 连接到:', url)
    connecting.value = true

    try {
      // 创建客户端
      client.value = createWebSocketClient(url)

      // 监听连接成功
      client.value.on('connected', () => {
        connected.value = true
        connecting.value = false
        console.log('[WebSocketStore] ✅ 连接成功')
      })

      // 监听断开连接
      client.value.on('disconnected', () => {
        connected.value = false
        connecting.value = false
        console.log('[WebSocketStore] 🔌 连接断开')
      })

      // 监听完整快照
      client.value.on('snapshot', (message: WebSocketMessage) => {
        if (message.data) {
          // 更新所有行情数据
          Object.assign(quotes.value, message.data)
          stats.value.totalMessages++
        }
      })

      // 监听行情更新
      client.value.on('quote_update', (message: WebSocketMessage) => {
        if (message.symbol && message.data) {
          const symbol = message.symbol

          // 更新行情数据（增量更新）
          if (!quotes.value[symbol]) {
            quotes.value[symbol] = {}
          }

          Object.assign(quotes.value[symbol], message.data)

          // 更新统计
          stats.value.quoteUpdates++
          stats.value.totalMessages++
          stats.value.lastUpdateTime = message.timestamp || null
        }
      })

      // 监听心跳
      client.value.on('heartbeat', () => {
        // 心跳，保持连接
      })

      // 连接
      await client.value.connect()

    } catch (error) {
      console.error('[WebSocketStore] ❌ 连接失败:', error)
      connecting.value = false
      throw error
    }
  }

  /**
   * 断开连接
   */
  function disconnect() {
    if (client.value) {
      client.value.disconnect()
      client.value = null
    }

    connected.value = false
    connecting.value = false

    // 清空数据
    quotes.value = {}
    subscriptions.value.clear()

    // 重置统计
    stats.value = {
      totalMessages: 0,
      quoteUpdates: 0,
      lastUpdateTime: null
    }
  }

  /**
   * 订阅股票
   */
  function subscribe(symbols: string[]) {
    if (!client.value || !connected.value) {
      console.warn('[WebSocketStore] ⚠️ 未连接，无法订阅')
      return
    }

    client.value.subscribe(symbols)

    // 添加到订阅列表
    symbols.forEach(s => subscriptions.value.add(s))

    console.log('[WebSocketStore] 📊 订阅:', symbols)
  }

  /**
   * 取消订阅
   */
  function unsubscribe(symbols: string[]) {
    if (!client.value || !connected.value) {
      return
    }

    client.value.unsubscribe(symbols)

    // 从订阅列表移除
    symbols.forEach(s => subscriptions.value.delete(s))

    // 从行情数据中移除
    symbols.forEach(s => delete quotes.value[s])

    console.log('[WebSocketStore] 📊 取消订阅:', symbols)
  }

  /**
   * 获取股票行情
   */
  function getQuote(symbol: string): any | null {
    return quotes.value[symbol] || null
  }

  /**
   * 获取多个股票行情
   */
  function getQuotes(symbols: string[]): Record<string, any> {
    const result: Record<string, any> = {}

    symbols.forEach(symbol => {
      if (quotes.value[symbol]) {
        result[symbol] = quotes.value[symbol]
      }
    })

    return result
  }

  // 计算属性
  const subscriptionList = computed(() => Array.from(subscriptions.value))
  const connectionStatus = computed(() => {
    if (connecting.value) return 'connecting'
    if (connected.value) return 'connected'
    return 'disconnected'
  })

  return {
    // 状态
    connected,
    connecting,
    quotes,
    subscriptionList,
    connectionStatus,
    stats,

    // 方法
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    getQuote,
    getQuotes
  }
})
