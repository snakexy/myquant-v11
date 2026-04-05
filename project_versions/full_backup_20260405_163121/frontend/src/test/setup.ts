import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// 全局配置
config.global.stubs = {
  // 存根组件
  'n-button': true,
  'n-input': true,
  'n-card': true,
  'n-modal': true,
  'n-table': true,
  'n-form': true,
  'n-form-item': true,
  'n-select': true,
  'n-date-picker': true,
  'n-switch': true,
  'n-checkbox': true,
  'n-radio': true,
  'n-tooltip': true,
  'n-dropdown': true,
  'n-menu': true,
  'n-layout': true,
  'n-layout-sider': true,
  'n-layout-header': true,
  'n-layout-content': true,
  'n-layout-footer': true,
  'n-breadcrumb': true,
  'n-breadcrumb-item': true,
  'n-icon': true,
  'n-avatar': true,
  'n-badge': true,
  'n-tag': true,
  'n-progress': true,
  'n-alert': true,
  'n-message': true,
  'n-notification': true,
  'n-dialog': true,
  'n-popover': true,
  'n-tabs': true,
  'n-tab-pane': true,
  'n-collapse': true,
  'n-collapse-item': true,
  'n-spin': true,
  'n-empty': true,
  'n-result': true,
  'n-page-header': true,
  'n-pagination': true,
  'n-grid': true,
  'n-grid-item': true,
  'n-space': true,
  'n-divider': true,
  'n-affix': true,
  'n-anchor': true,
  'n-anchor-link': true,
  'n-back-top': true,
  'n-config-provider': true,
  'n-global-style': true,
  'n-loading-bar-provider': true,
  'n-message-provider': true,
  'n-notification-provider': true,
  'n-modal-provider': true,
  'n-dialog-provider': true
}

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn()
}
vi.stubGlobal('localStorage', localStorageMock)

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn()
}
vi.stubGlobal('sessionStorage', sessionStorageMock)

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock ResizeObserver
vi.stubGlobal('ResizeObserver', vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
})))

// Mock IntersectionObserver
vi.stubGlobal('IntersectionObserver', vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
})))

// Mock requestAnimationFrame
vi.stubGlobal('requestAnimationFrame', vi.fn(cb => setTimeout(cb, 16)))
vi.stubGlobal('cancelAnimationFrame', vi.fn(id => clearTimeout(id)))

// Mock console methods for cleaner test output
const originalConsole = globalThis.console
globalThis.console = {
  ...originalConsole,
  // 保留 error 和 warn 用于调试
  log: vi.fn(),
  debug: vi.fn(),
  info: vi.fn(),
}