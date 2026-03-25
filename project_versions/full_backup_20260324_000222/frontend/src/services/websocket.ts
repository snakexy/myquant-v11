/**
 * WebSocket 客户端服务 v3.1
 *
 * 功能：
 * - 连接管理
 * - 订阅管理
 * - 自动重连
 * - 心跳检测
 * - 消息处理
 *
 * @author Claude
 * @created 2026-01-27
 */

// import { EventEmitter } from 'events' // Node.js events模块在浏览器中不可用
import { EventEmitter } from './EventEmitter'

export interface WebSocketMessage {
  type: string
  symbol?: string
  data?: any
  timestamp?: string
}

export interface WebSocketConfig {
  url: string
  autoReconnect?: boolean
  reconnectInterval?: number
  heartbeatInterval?: number
}

type MessageHandler = (data: WebSocketMessage) => void

/**
 * WebSocket 客户端类
 */
export class WebSocketClient extends EventEmitter {
  private ws: WebSocket | null = null
  private config: WebSocketConfig
  private connected: boolean = false
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  private subscriptions: Set<string> = new Set()
  private messageHandlers: Map<string, MessageHandler[]> = new Map()

  constructor(config: WebSocketConfig) {
    super()
    this.config = {
      autoReconnect: true,
      reconnectInterval: 5000,
      heartbeatInterval: 30000,
      ...config
    }
  }

  /**
   * 连接WebSocket
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.url)

        this.ws.onopen = () => {
          console.log('[WebSocket] ✅ 连接成功')
          this.connected = true
          this.emit('connected')

          // 启动心跳
          this.startHeartbeat()

          // 恢复之前的订阅
          if (this.subscriptions.size > 0) {
            this.subscribe(Array.from(this.subscriptions))
          }

          resolve()
        }

        this.ws.onerror = (error) => {
          console.error('[WebSocket] ❌ 连接错误:', error)
          this.emit('error', error)
          reject(error)
        }

        this.ws.onclose = (event) => {
          console.log('[WebSocket] 🔌 连接关闭:', event.code, event.reason)
          this.connected = false
          this.emit('disconnected')

          // 停止心跳
          this.stopHeartbeat()

          // 自动重连
          if (this.config.autoReconnect!) {
            this.scheduleReconnect()
          }
        }

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data)
        }
      } catch (error) {
        console.error('[WebSocket] ❌ 连接失败:', error)
        reject(error)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    console.log('[WebSocket] 断开连接')

    // 停止重连
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    // 停止心跳
    this.stopHeartbeat()

    // 关闭连接
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.connected = false
  }

  /**
   * 订阅股票
   */
  subscribe(symbols: string[]): void {
    if (!this.connected) {
      console.warn('[WebSocket] ⚠️ 未连接，无法订阅')
      return
    }

    const message = {
      action: 'subscribe',
      symbols: symbols
    }

    this.send(message)

    // 添加到订阅列表
    symbols.forEach(s => this.subscriptions.add(s))

    console.log(`[WebSocket] 📊 订阅 ${symbols.length} 只股票:`, symbols)
  }

  /**
   * 取消订阅
   */
  unsubscribe(symbols: string[]): void {
    if (!this.connected) {
      return
    }

    const message = {
      action: 'unsubscribe',
      symbols: symbols
    }

    this.send(message)

    // 从订阅列表移除
    symbols.forEach(s => this.subscriptions.delete(s))

    console.log(`[WebSocket] 📊 取消订阅 ${symbols.length} 只股票:`, symbols)
  }

  /**
   * 添加消息处理器
   */
  on(type: string, handler: MessageHandler): this {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, [])
    }
    this.messageHandlers.get(type)!.push(handler)
    return this
  }

  /**
   * 移除消息处理器
   */
  off(type: string, handler?: MessageHandler): this {
    if (!handler) {
      this.messageHandlers.delete(type)
      return this
    }

    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
    return this
  }

  /**
   * 处理收到的消息
   */
  private handleMessage(data: string): void {
    try {
      const message: WebSocketMessage = JSON.parse(data)

      // 触发事件
      this.emit('message', message)
      this.emit(message.type, message)

      // 调用注册的处理器
      const handlers = this.messageHandlers.get(message.type)
      if (handlers) {
        handlers.forEach(handler => handler(message))
      }

      // 特殊消息类型处理
      switch (message.type) {
        case 'connected':
          console.log('[WebSocket] ✅ 连接确认:', message.client_id)
          break

        case 'snapshot':
          console.log('[WebSocket] 📸 收到完整快照')
          break

        case 'quote_update':
          // 行情更新
          console.log('[WebSocket] 📊 行情更新:', message.symbol)
          break

        case 'heartbeat':
          console.log('[WebSocket] 💓 心跳')
          break

        default:
          console.log('[WebSocket] 📨 收到消息:', message.type)
      }
    } catch (error) {
      console.error('[WebSocket] ❌ 消息解析失败:', error)
    }
  }

  /**
   * 发送消息
   */
  private send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('[WebSocket] ⚠️ 未连接，无法发送消息')
    }
  }

  /**
   * 安排重连
   */
  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return
    }

    console.log(`[WebSocket] 🔄 ${this.config.reconnectInterval}ms 后尝试重连...`)

    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null
      console.log('[WebSocket] 🔄 重新连接...')
      this.connect().catch(error => {
        console.error('[WebSocket] ❌ 重连失败:', error)
      })
    }, this.config.reconnectInterval!)
  }

  /**
   * 启动心跳
   */
  private startHeartbeat(): void {
    this.heartbeatTimer = window.setInterval(() => {
      if (this.connected) {
        this.send({ action: 'ping' })
      }
    }, this.config.heartbeatInterval!)
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 获取连接状态
   */
  isConnected(): boolean {
    return this.connected
  }

  /**
   * 获取订阅列表
   */
  getSubscriptions(): string[] {
    return Array.from(this.subscriptions)
  }
}

/**
 * 创建WebSocket客户端实例
 */
export function createWebSocketClient(url: string): WebSocketClient {
  return new WebSocketClient({
    url,
    autoReconnect: true,
    reconnectInterval: 5000,
    heartbeatInterval: 30000
  })
}

export default WebSocketClient
