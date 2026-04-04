// 工具类型定义

// 验证规则类型
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  email?: boolean
  url?: boolean
  phone?: boolean
  number?: boolean
  integer?: boolean
  positive?: boolean
  negative?: boolean
  custom?: (value: any) => boolean | string
}

// 验证结果类型
export interface ValidationResult {
  valid: boolean
  message?: string
  field?: string
  value?: any
}

// 表单验证配置类型
export interface FormValidationConfig {
  [key: string]: ValidationRule[]
}

// 防抖配置类型
export interface DebounceConfig {
  delay: number
  immediate?: boolean
  maxWait?: number
}

// 节流配置类型
export interface ThrottleConfig {
  delay: number
  leading?: boolean
  trailing?: boolean
}

// 深度比较配置类型
export interface DeepCompareConfig {
  ignoreCase?: boolean
  ignoreWhitespace?: boolean
  ignoreUndefined?: boolean
  ignoreNull?: boolean
  ignoreEmptyString?: boolean
  ignoreEmptyArray?: boolean
  ignoreEmptyObject?: boolean
}

// 缓存配置类型
export interface CacheConfig {
  ttl?: number // 生存时间(毫秒)
  maxSize?: number // 最大缓存数量
  strategy?: 'lru' | 'fifo' | 'custom'
  keyGenerator?: (key: any) => string
  isExpired?: (value: any, timestamp: number) => boolean
}

// 缓存项类型
export interface CacheItem<T = any> {
  value: T
  timestamp: number
  ttl?: number
  expires?: number
}

// 本地存储配置类型
export interface StorageConfig {
  prefix?: string
  ttl?: number // 生存时间(毫秒)
  serializer?: (value: any) => string
  deserializer?: (value: string) => any
  driver?: 'localStorage' | 'sessionStorage' | 'memory'
}

// 日期格式化配置类型
export interface DateFormatConfig {
  format?: string
  locale?: string
  timezone?: string
  showTime?: boolean
  showDate?: boolean
  showSeconds?: boolean
  use12Hour?: boolean
}

// 数字格式化配置类型
export interface NumberFormatConfig {
  decimals?: number
  thousandsSeparator?: string
  decimalSeparator?: string
  prefix?: string
  suffix?: string
  showSign?: boolean
  absolute?: boolean
}

// 文件格式化配置类型
export interface FileFormatConfig {
  sizeUnit?: 'B' | 'KB' | 'MB' | 'GB' | 'TB'
  decimals?: number
  showUnit?: boolean
  useBinary?: boolean // 使用1024进制
}

// 颜色格式化配置类型
export interface ColorFormatConfig {
  format?: 'hex' | 'rgb' | 'rgba' | 'hsl' | 'hsla'
  uppercase?: boolean
  prefix?: string
}

// URL构建配置类型
export interface UrlBuilderConfig {
  baseUrl?: string
  params?: Record<string, any>
  hash?: string
  query?: Record<string, any>
  path?: string
}

// 错误处理配置类型
export interface ErrorHandlingConfig {
  retry?: number
  retryDelay?: number
  timeout?: number
  silent?: boolean
  onError?: (error: Error) => void
  onSuccess?: (result: any) => void
}

// 日志配置类型
export interface LoggerConfig {
  level?: 'debug' | 'info' | 'warn' | 'error'
  prefix?: string
  enableConsole?: boolean
  enableStorage?: boolean
  maxStorageSize?: number
  dateFormat?: string
}

// 性能监控配置类型
export interface PerformanceConfig {
  enable?: boolean
  sampleRate?: number
  maxSamples?: number
  reportInterval?: number
  onReport?: (metrics: PerformanceMetrics) => void
}

// 性能指标类型
export interface PerformanceMetrics {
  fps?: number
  memory?: number
  timing?: {
    domInteractive?: number
    loadEventEnd?: number
    firstPaint?: number
    firstContentfulPaint?: number
  }
  navigation?: {
    type?: string
    redirectCount?: number
  redirectTime?: number
  dnsTime?: number
    connectTime?: number
    requestTime?: number
    responseTime?: number
    domLoadingTime?: number
  }
}

// 事件处理配置类型
export interface EventConfig {
  passive?: boolean
  capture?: boolean
  once?: boolean
  preventDefault?: boolean
  stopPropagation?: boolean
}

// 拖拽事件类型
export interface DragEvent {
  clientX: number
  clientY: number
  movementX: number
  movementY: number
  offsetX: number
  offsetY: number
  pageX: number
  pageY: number
  screenX: number
  screenY: number
  target: Element
  currentTarget: Element
  preventDefault: () => void
  stopPropagation: () => void
}

// 调整大小事件类型
export interface ResizeEvent {
  width: number
  height: number
  deltaX: number
  deltaY: number
  clientX: number
  clientY: number
  target: Element
  currentTarget: Element
  preventDefault: () => void
  stopPropagation: () => void
}

// 拖拽配置类型
export interface DragConfig {
  axis?: 'x' | 'y' | 'both'
  containment?: 'parent' | 'window' | 'viewport' | Element
  handle?: string
  grid?: number[]
  snap?: boolean
  snapMode?: 'grid' | 'magnet'
  snapTolerance?: number
  onStart?: (event: DragEvent) => void
  onMove?: (event: DragEvent) => void
  onEnd?: (event: DragEvent) => void
}

// 调整大小配置类型
export interface ResizeConfig {
  axis?: 'x' | 'y' | 'both'
  handles?: string[]
  minWidth?: number
  maxWidth?: number
  minHeight?: number
  maxHeight?: number
  aspectRatio?: number
  grid?: number[]
  snap?: boolean
  onStart?: (event: ResizeEvent) => void
  onMove?: (event: ResizeEvent) => void
  onEnd?: (event: ResizeEvent) => void
}

// 键盘快捷键配置类型
export interface HotkeyConfig {
  key: string | string[]
  ctrl?: boolean
  alt?: boolean
  shift?: boolean
  meta?: boolean
  prevent?: boolean
  handler?: (event: KeyboardEvent) => void
  description?: string
}

// 复制到剪贴板配置类型
export interface ClipboardConfig {
  target?: 'text' | 'html' | 'image'
  successMessage?: string
  errorMessage?: string
  onSuccess?: () => void
  onError?: (error: Error) => void
}

// 图片处理配置类型
export interface ImageProcessConfig {
  maxWidth?: number
  maxHeight?: number
  quality?: number
  format?: 'jpeg' | 'png' | 'webp'
  keepAspectRatio?: boolean
  crop?: {
    x?: number
    y?: number
    width?: number
    height?: number
  }
}

// 数组工具配置类型
export interface ArrayUtilsConfig {
  compareFn?: (a: any, b: any) => number
  uniqueKey?: string | ((item: any) => any)
  sortBy?: string | ((item: any) => any)
  groupBy?: string | ((item: any) => any)
}

// 对象工具配置类型
export interface ObjectUtilsConfig {
  deep?: boolean
  omitNull?: boolean
  omitUndefined?: boolean
  omitEmpty?: boolean
  customFilter?: (key: string, value: any) => boolean
}

// 字符串工具配置类型
export interface StringUtilsConfig {
  ignoreCase?: boolean
  ignoreWhitespace?: boolean
  ignoreAccents?: boolean
  trim?: boolean
  maxLength?: number
  minLength?: number
  pattern?: RegExp
}

// 加密配置类型
export interface EncryptionConfig {
  algorithm?: 'AES' | 'DES' | 'RSA'
  key?: string
  iv?: string
  mode?: 'CBC' | 'ECB' | 'CFB'
  padding?: 'PKCS7' | 'ISO97971' | 'ANSIX931'
  output?: 'base64' | 'hex'
}

// 压缩配置类型
export interface CompressionConfig {
  algorithm?: 'gzip' | 'deflate' | 'brotli'
  level?: number // 压缩级别 1-9
  chunkSize?: number
  windowBits?: number
  memLevel?: number
}

// 网络请求配置类型
export interface RequestConfig {
  timeout?: number
  retries?: number
  retryDelay?: number
  headers?: Record<string, string>
  params?: Record<string, any>
  data?: any
  responseType?: 'json' | 'text' | 'blob' | 'arrayBuffer'
  onProgress?: (progress: number) => void
  onUploadProgress?: (progress: UploadProgress) => void
}

// 上传进度类型
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
  speed: number
  timeRemaining: number
}

// WebSocket配置类型
export interface WebSocketConfig {
  url: string
  protocols?: string[]
  reconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeat?: {
    interval: number
    message: any
  timeout?: number
  }
  onOpen?: (event: Event) => void
  onClose?: (event: CloseEvent) => void
  onMessage?: (event: MessageEvent) => void
  onError?: (event: Event) => void
}

// 地理位置配置类型
export interface GeolocationConfig {
  enableHighAccuracy?: boolean
  timeout?: number
  maximumAge?: number
  onSuccess?: (position: GeolocationPosition) => void
  onError?: (error: GeolocationPositionError) => void
}

// 设备信息类型
export interface DeviceInfo {
  userAgent: string
  platform: string
  browser: string
  browserVersion: string
  mobile: boolean
  tablet: boolean
  desktop: boolean
  os: string
  osVersion: string
  screen: {
    width: number
    height: number
    colorDepth: number
    pixelRatio: number
  }
  viewport: {
    width: number
    height: number
  }
  features: {
    webgl: boolean
    webgl2: boolean
    canvas: boolean
    svg: boolean
    audio: boolean
    video: boolean
    localStorage: boolean
    sessionStorage: boolean
    webWorkers: boolean
    touch: boolean
    geolocation: boolean
    notification: boolean
  }
}

// 环境变量类型
export interface EnvironmentConfig {
  development?: boolean
  production?: boolean
  test?: boolean
  staging?: boolean
  version?: string
  buildTime?: string
  commit?: string
  branch?: string
}

// 主题工具配置类型
export interface ThemeUtilsConfig {
  defaultTheme?: string
  storageKey?: string
  followSystem?: boolean
  themes?: Record<string, ThemeDefinition>
}

// 主题定义类型
export interface ThemeDefinition {
  name: string
  colors: Record<string, string>
  fonts: Record<string, string>
  spacing: Record<string, string>
  borderRadius: Record<string, string>
  shadows: Record<string, string>
  transitions: Record<string, string>
}

// 国际化配置类型
export interface I18nConfig {
  defaultLocale?: string
  fallbackLocale?: string
  storageKey?: string
  messages?: Record<string, Record<string, string>>
  pluralRules?: Record<string, (count: number) => string>
  dateTimeFormats?: Record<string, string>
  numberFormats?: Record<string, string>
}