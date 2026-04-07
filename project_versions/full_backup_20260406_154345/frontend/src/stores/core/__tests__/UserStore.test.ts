/**
 * UserStore 单元测试
 * M2-17 Store重构验收测试
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useUserStore } from '../UserStore'

describe('UserStore', () => {
  let userStore: ReturnType<typeof useUserStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    userStore = useUserStore()
    localStorage.clear()
  })

  describe('用户信息', () => {
    it('应该初始化默认用户信息', () => {
      expect(userStore.isLoggedIn).toBe(false)
      expect(userStore.username).toBe('')
    })

    it('应该能够设置用户信息', () => {
      userStore.setUserInfo({
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        role: 'user'
      })

      expect(userStore.username).toBe('testuser')
      expect(userStore.isLoggedIn).toBe(true)
    })

    it('应该能够清除用户信息', () => {
      userStore.setUserInfo({
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        role: 'user'
      })

      userStore.clearUserInfo()
      expect(userStore.isLoggedIn).toBe(false)
      expect(userStore.username).toBe('')
    })
  })

  describe('用户偏好', () => {
    it('应该能够设置偏好', () => {
      userStore.setPreference('theme', 'dark')
      expect(userStore.getPreference('theme')).toBe('dark')
    })

    it('应该能够批量设置偏好', () => {
      userStore.setPreferences({
        theme: 'dark',
        language: 'en',
        sidebarCollapsed: true
      })

      expect(userStore.preferences.theme).toBe('dark')
      expect(userStore.preferences.language).toBe('en')
      expect(userStore.preferences.sidebarCollapsed).toBe(true)
    })

    it('应该能够重置偏好', () => {
      userStore.setPreferences({
        theme: 'dark',
        language: 'en'
      })

      userStore.resetPreferences()
      expect(userStore.preferences.theme).toBe('light')
      expect(userStore.preferences.language).toBe('zh')
    })
  })

  describe('指标参数配置', () => {
    it('应该能够设置MA指标参数', () => {
      userStore.setIndicatorParams('MA', {
        periods: [5, 10, 20, 30, 60]
      })

      expect(userStore.indicatorParams.MA.periods).toEqual([5, 10, 20, 30, 60])
    })

    it('应该能够设置BOLL指标参数', () => {
      userStore.setIndicatorParams('BOLL', {
        period: 20,
        stdDev: 2
      })

      expect(userStore.indicatorParams.BOLL.period).toBe(20)
      expect(userStore.indicatorParams.BOLL.stdDev).toBe(2)
    })

    it('应该能够设置MACD指标参数', () => {
      userStore.setIndicatorParams('MACD', {
        fastPeriod: 12,
        slowPeriod: 26,
        signalPeriod: 9
      })

      expect(userStore.indicatorParams.MACD.fastPeriod).toBe(12)
      expect(userStore.indicatorParams.MACD.slowPeriod).toBe(26)
    })

    it('应该能够设置KDJ指标参数', () => {
      userStore.setIndicatorParams('KDJ', {
        kPeriod: 9,
        dPeriod: 3,
        jPeriod: 3
      })

      expect(userStore.indicatorParams.KDJ.kPeriod).toBe(9)
    })

    it('应该能够设置RSI指标参数', () => {
      userStore.setIndicatorParams('RSI', {
        period: 14,
        overbought: 70,
        oversold: 30
      })

      expect(userStore.indicatorParams.RSI.period).toBe(14)
      expect(userStore.indicatorParams.RSI.overbought).toBe(70)
      expect(userStore.indicatorParams.RSI.oversold).toBe(30)
    })
  })

  describe('自定义板块', () => {
    it('应该能够创建自定义板块', () => {
      userStore.createCustomSector('我的自选', ['600519.SH', '000001.SZ'])

      expect(userStore.customSectors.length).toBe(1)
      expect(userStore.customSectors[0].name).toBe('我的自选')
    })

    it('应该能够删除自定义板块', () => {
      userStore.createCustomSector('测试', ['600519.SH'])
      userStore.deleteCustomSector('测试')

      expect(userStore.customSectors.length).toBe(0)
    })

    it('应该能够添加股票到自定义板块', () => {
      userStore.createCustomSector('我的自选', [])
      userStore.addStockToCustomSector('我的自选', '600519.SH')

      const sector = userStore.customSectors.find(s => s.name === '我的自选')
      expect(sector?.stocks).toContain('600519.SH')
    })

    it('应该能够从自定义板块移除股票', () => {
      userStore.createCustomSector('我的自选', ['600519.SH', '000001.SZ'])
      userStore.removeStockFromCustomSector('我的自选', '600519.SH')

      const sector = userStore.customSectors.find(s => s.name === '我的自选')
      expect(sector?.stocks).not.toContain('600519.SH')
    })
  })

  describe('UI状态管理', () => {
    it('应该能够打开模态框', () => {
      userStore.openModal('test-modal', { data: 'test' })

      expect(userStore.activeModals.length).toBe(1)
      expect(userStore.activeModals[0].id).toBe('test-modal')
    })

    it('应该能够关闭模态框', () => {
      userStore.openModal('test-modal')
      userStore.closeModal('test-modal')

      expect(userStore.activeModals.length).toBe(0)
    })

    it('应该能够关闭所有模态框', () => {
      userStore.openModal('modal1')
      userStore.openModal('modal2')
      userStore.closeAllModals()

      expect(userStore.activeModals.length).toBe(0)
    })

    it('应该能够显示提示框', () => {
      userStore.showToast('success', '操作成功', '详细消息')

      expect(userStore.toasts.length).toBe(1)
      expect(userStore.toasts[0].type).toBe('success')
    })

    it('应该能够移除提示框', () => {
      userStore.showToast('info', '测试')
      const toastId = userStore.toasts[0].id

      userStore.removeToast(toastId)
      expect(userStore.toasts.length).toBe(0)
    })

    it('应该能够清除所有提示框', () => {
      userStore.showToast('info', '测试1')
      userStore.showToast('success', '测试2')
      userStore.clearToasts()

      expect(userStore.toasts.length).toBe(0)
    })

    it('应该能够设置加载状态', () => {
      userStore.setLoading('test-action', true)
      expect(userStore.isLoading('test-action')).toBe(true)

      userStore.setLoading('test-action', false)
      expect(userStore.isLoading('test-action')).toBe(false)
    })

    it('应该能够清除加载状态', () => {
      userStore.setLoading('action1', true)
      userStore.setLoading('action2', true)
      userStore.clearLoading()

      expect(userStore.loadingStates.size).toBe(0)
    })
  })

  describe('图表偏好设置', () => {
    it('应该能够设置图表类型', () => {
      userStore.setChartPreference('chartType', 'candlestick')
      expect(userStore.chartPreferences.chartType).toBe('candlestick')
    })

    it('应该能够设置显示的指标', () => {
      userStore.setChartPreference('indicators', ['MA', 'BOLL', 'VOL'])
      expect(userStore.chartPreferences.indicators).toEqual(['MA', 'BOLL', 'VOL'])
    })

    it('应该能够设置图表颜色', () => {
      userStore.setChartPreference('upColor', '#ef4444')
      expect(userStore.chartPreferences.upColor).toBe('#ef4444')
    })
  })

  describe('活动记录', () => {
    it('应该能够添加活动记录', () => {
      userStore.addActivity({
        type: 'view',
        description: '查看了股票',
        metadata: { symbol: '600519.SH' }
      })

      expect(userStore.activities.length).toBe(1)
      expect(userStore.activities[0].type).toBe('view')
    })

    it('应该限制活动记录数量为50条', () => {
      // 添加51条记录
      for (let i = 0; i < 51; i++) {
        userStore.addActivity({
          type: 'test',
          description: `测试活动${i}`
        })
      }

      // 应该只保留最近50条
      expect(userStore.activities.length).toBe(50)
    })

    it('应该能够清除活动记录', () => {
      userStore.addActivity({ type: 'test', description: '测试' })
      userStore.clearActivities()

      expect(userStore.activities.length).toBe(0)
    })
  })

  describe('配置保存和加载', () => {
    it('应该能够保存配置到localStorage', () => {
      userStore.setPreferences({ theme: 'dark', language: 'en' })
      userStore.saveConfig()

      const saved = localStorage.getItem('user-store-config')
      expect(saved).not.toBeNull()

      if (saved) {
        const parsed = JSON.parse(saved)
        expect(parsed.preferences.theme).toBe('dark')
      }
    })

    it('应该能够从localStorage加载配置', () => {
      localStorage.setItem('user-store-config', JSON.stringify({
        preferences: { theme: 'dark', language: 'en' },
        indicatorParams: { MA: { periods: [5, 10, 20] } }
      }))

      // 重新创建store会自动加载
      setActivePinia(createPinia())
      const newStore = useUserStore()

      expect(newStore.preferences.theme).toBe('dark')
      expect(newStore.indicatorParams.MA.periods).toEqual([5, 10, 20])
    })
  })
})
