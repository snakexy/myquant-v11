/**
 * 浏览器兼容的简单 EventEmitter 实现
 */
export class EventEmitter {
  private events: Map<string, Array<(...args: any[]) => void>> = new Map()

  on(event: string, listener: (...args: any[]) => void): this {
    if (!this.events.has(event)) {
      this.events.set(event, [])
    }
    this.events.get(event)!.push(listener)
    return this
  }

  off(event: string, listener: (...args: any[]) => void): this {
    if (!this.events.has(event)) return this

    const listeners = this.events.get(event)!
    const index = listeners.indexOf(listener)
    if (index > -1) {
      listeners.splice(index, 1)
    }

    if (listeners.length === 0) {
      this.events.delete(event)
    }

    return this
  }

  emit(event: string, ...args: any[]): boolean {
    if (!this.events.has(event)) return false

    const listeners = this.events.get(event)!
    listeners.forEach(listener => {
      try {
        listener(...args)
      } catch (error) {
        console.error(`Error in event listener for "${event}":`, error)
      }
    })

    return true
  }

  once(event: string, listener: (...args: any[]) => void): this {
    const onceListener = (...args: any[]) => {
      this.off(event, onceListener)
      listener(...args)
    }
    return this.on(event, onceListener)
  }

  removeAllListeners(event?: string): this {
    if (event) {
      this.events.delete(event)
    } else {
      this.events.clear()
    }
    return this
  }

  listenerCount(event: string): number {
    return this.events.get(event)?.length || 0
  }

  eventNames(): string[] {
    return Array.from(this.events.keys())
  }
}