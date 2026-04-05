/**
 * 浏览器兼容的 EventEmitter 实现
 * 用于替代 Node.js 的 events 模块
 */

export class EventEmitter {
  private events: Map<string, Function[]> = new Map()

  on(eventName: string, listener: Function): this {
    const listeners = this.events.get(eventName) || []
    listeners.push(listener)
    this.events.set(eventName, listeners)
    return this
  }

  off(eventName: string, listener?: Function): this {
    if (!listener) {
      this.events.delete(eventName)
      return this
    }

    const listeners = this.events.get(eventName)
    if (listeners) {
      const index = listeners.indexOf(listener)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
    return this
  }

  emit(eventName: string, ...args: any[]): boolean {
    const listeners = this.events.get(eventName)
    if (listeners) {
      listeners.forEach(listener => listener(...args))
      return true
    }
    return false
  }

  once(eventName: string, listener: Function): this {
    const onceWrapper = (...args: any[]) => {
      listener(...args)
      this.off(eventName, onceWrapper)
    }
    return this.on(eventName, onceWrapper)
  }
}
