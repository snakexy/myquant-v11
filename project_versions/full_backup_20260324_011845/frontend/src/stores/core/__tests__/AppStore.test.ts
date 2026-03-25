/**
 * AppStore 单元测试
 * M2-17 Store重构验收测试
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAppStore } from '../AppStore'

describe('AppStore', () => {
  let appStore: ReturnType<typeof useAppStore>

  beforeEach(() => {
    // 创建新的Pinia实例
    setActivePinia(createPinia())
    appStore = useAppStore()

    // 清理localStorage
    localStorage.clear()
  })

  describe('主题系统', () => {
    it('应该初始化默认主题', () => {
      expect(appStore.themeMode).toBe('auto')
      expect(appStore.primaryColor).toBe('purple')
    })

    it('应该能够设置主题模式', () => {
      appStore.setThemeMode('dark')
      expect(appStore.themeMode).toBe('dark')
    })

    it('应该能够设置主色调', () => {
      appStore.setPrimaryColor('blue')
      expect(appStore.primaryColor).toBe('blue')
    })

    it('应该返回正确的主题颜色', () => {
      const colors = appStore.themeColors
      expect(colors).toHaveProperty('primary')
      expect(colors).toHaveProperty('bgDeep')
      expect(colors).toHaveProperty('textPrimary')
    })

    it('应该支持5种预设颜色', () => {
      const colors = ['purple', 'blue', 'green', 'orange', 'red'] as const

      colors.forEach(color => {
        appStore.setPrimaryColor(color)
        expect(appStore.primaryColor).toBe(color)
      })
    })
  })

  describe('应用配置', () => {
    it('应该初始化默认语言', () => {
      expect(appStore.language).toBe('zh')
    })

    it('应该能够设置语言', () => {
      appStore.setLanguage('en')
      expect(appStore.language).toBe('en')
    })

    it('应该能够切换侧边栏', () => {
      appStore.toggleSidebar()
      expect(appStore.sidebarCollapsed).toBe(true)

      appStore.toggleSidebar()
      expect(appStore.sidebarCollapsed).toBe(false)
    })
  })

  describe('通知系统', () => {
    it('应该能够添加通知', () => {
      appStore.addNotification({
        type: 'success',
        title: '测试',
        message: '测试消息'
      })

      expect(appStore.notifications.length).toBe(1)
      expect(appStore.notifications[0].type).toBe('success')
    })

    it('应该能够标记通知为已读', () => {
      appStore.addNotification({
        type: 'info',
        title: '测试',
        message: '测试消息'
      })

      const notificationId = appStore.notifications[0].id
      appStore.markAsRead(notificationId)

      expect(appStore.notifications[0].read).toBe(true)
    })

    it('应该能够删除通知', () => {
      appStore.addNotification({
        type: 'info',
        title: '测试',
        message: '测试消息'
      })

      const notificationId = appStore.notifications[0].id
      appStore.removeNotification(notificationId)

      expect(appStore.notifications.length).toBe(0)
    })

    it('应该能够标记所有通知为已读', () => {
      appStore.addNotification({ type: 'info', title: '测试1', message: '消息1' })
      appStore.addNotification({ type: 'info', title: '测试2', message: '消息2' })

      appStore.markAllAsRead()

      expect(appStore.notifications.every(n => n.read)).toBe(true)
    })

    it('应该正确计算未读通知数量', () => {
      appStore.addNotification({ type: 'info', title: '测试1', message: '消息1' })
      appStore.addNotification({ type: 'info', title: '测试2', message: '消息2' })

      expect(appStore.unreadCount).toBe(2)

      appStore.markAllAsRead()
      expect(appStore.unreadCount).toBe(0)
    })
  })

  describe('功能状态管理', () => {
    it('应该能够设置当前功能', () => {
      appStore.setCurrentFunction('test-function', 1)
      expect(appStore.currentFunction).toBe('test-function')
      expect(appStore.currentLayer).toBe(1)
    })

    it('应该能够添加导航历史', () => {
      appStore.setCurrentFunction('func1', 1)
      appStore.setCurrentFunction('func2', 2)

      expect(appStore.navigationHistory.length).toBeGreaterThan(0)
    })

    it('应该能够清除导航历史', () => {
      appStore.setCurrentFunction('func1', 1)
      appStore.clearNavigationHistory()

      expect(appStore.navigationHistory.length).toBe(0)
    })
  })

  describe('数据持久化', () => {
    it('应该能够保存配置到localStorage', () => {
      appStore.setThemeMode('dark')
      appStore.setLanguage('en')
      appStore.savePreferences()

      const saved = localStorage.getItem('app-store-preferences')
      expect(saved).not.toBeNull()

      if (saved) {
        const parsed = JSON.parse(saved)
        expect(parsed.themeMode).toBe('dark')
        expect(parsed.language).toBe('en')
      }
    })

    it('应该能够从localStorage加载配置', () => {
      // 保存配置
      localStorage.setItem('app-store-preferences', JSON.stringify({
        themeMode: 'dark',
        language: 'en',
        sidebarCollapsed: true
      }))

      // 重新创建store会自动加载
      setActivePinia(createPinia())
      const newStore = useAppStore()

      // 验证加载的配置
      expect(newStore.themeMode).toBe('dark')
      expect(newStore.language).toBe('en')
    })
  })

  describe('自动保存', () => {
    it('应该在配置变化时自动保存', () => {
      const spy = vi.spyOn(appStore, 'savePreferences')

      appStore.setThemeMode('dark')

      // 验证savePreferences被调用（可能有延迟）
      expect(spy).toHaveBeenCalled()
    })
  })
})
