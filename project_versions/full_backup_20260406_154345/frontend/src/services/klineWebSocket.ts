/**
 * K线 WebSocket 客户端
 *
 * 连接到 ws://localhost:8000/ws/kline/{symbol}
 * 处理实时 K线推送
 */

export interface KlineBar {
  time: string | number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export type KlineMessageHandler = (data: KlineBar | KlineBar[]) => void

export interface KlineWebSocketConfig {
  onHistory?: (bars: KlineBar[]) => void
  onBarUpdate?: (bar: KlineBar) => void
  onBarClose?: (bar: KlineBar) => void
  onError?: (message: string) => void
  onConnected?: () => void
  onDisconnected?: () => void
}

export class KlineWebSocket {
  private ws: WebSocket | null = null
  private symbol: string
  private config: KlineWebSocketConfig
  private reconnectTimer: number | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  constructor(symbol: string, config: KlineWebSocketConfig) {
    this.symbol = symbol
    this.config = config
  }

  connect(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('[KlineWS] 已连接，跳过')
      return
    }

    // 根据当前页面协议选择 ws:// 或 wss://
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//localhost:8000/ws/kline/${this.symbol}`
    console.log('[KlineWS] 连接:', wsUrl)

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('[KlineWS] ✅ 连接成功')
        this.reconnectAttempts = 0
        this.config.onConnected?.()
      }

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data)
      }

      this.ws.onerror = (error) => {
        console.error('[KlineWS] ❌ 连接错误:', error)
      }

      this.ws.onclose = () => {
        console.log('[KlineWS] 🔌 连接关闭')
        this.config.onDisconnected?.()

        // 自动重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000)
          console.log(`[KlineWS] 🔄 ${delay}ms 后重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
          this.reconnectTimer = window.setTimeout(() => this.connect(), delay)
        }
      }
    } catch (error) {
      console.error('[KlineWS] ❌ 连接失败:', error)
      this.config.onError?.(`连接失败: ${error}`)
    }
  }

  disconnect(): void {
    console.log('[KlineWS] 断开连接')

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    this.reconnectAttempts = this.maxReconnectAttempts // 停止自动重连

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  private handleMessage(data: string): void {
    // 处理心跳消息（纯文本）
    if (data === 'ping') {
      this.ws?.send('pong')
      return
    }
    if (data === 'pong') {
      return
    }

    try {
      const message = JSON.parse(data)

      switch (message.type) {
        case 'history':
          console.log('[KlineWS] 📜 收到历史数据:', message.bars?.length, '根')
          this.config.onHistory?.(message.bars || [])
          break

        case 'bar_update':
          console.log('[KlineWS] 📊 Bar 更新:', message.bar)
          this.config.onBarUpdate?.(message.bar)
          break

        case 'bar_close':
          console.log('[KlineWS] 📈 Bar 收线:', message.bar)
          this.config.onBarClose?.(message.bar)
          break

        case 'error':
          console.error('[KlineWS] ❌ 错误:', message.message)
          this.config.onError?.(message.message)
          break

        default:
          console.log('[KlineWS] 📨 未知消息类型:', message.type)
      }
    } catch (error) {
      console.error('[KlineWS] ❌ 消息解析失败:', error, data)
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  updateSymbol(newSymbol: string): void {
    if (newSymbol === this.symbol) return

    const wasConnected = this.isConnected()
    this.disconnect()

    // 等待旧连接完全关闭后再连接新股票
    setTimeout(() => {
      this.symbol = newSymbol
      this.reconnectAttempts = 0 // 重置重连计数
      this.connect()
    }, 100)
  }
}

/**
 * 创建 K线 WebSocket 客户端
 */
export function createKlineWebSocket(symbol: string, config: KlineWebSocketConfig): KlineWebSocket {
  return new KlineWebSocket(symbol, config)
}
