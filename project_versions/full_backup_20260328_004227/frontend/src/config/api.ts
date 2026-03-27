/**
 * API配置
 *
 * 说明：
 * 如果需要修改后端地址，只需修改此文件中的 API_BASE_URL
 * 前端所有API调用都会自动使用新地址
 */

// 后端API基础URL (使用相对路径，通过Vite代理)
export const API_BASE_URL = '/api'

// API路径常量
export const API_PATHS = {
  // 数据源配置相关
  TDX_CONFIG: '/v1/data-source-config/tdx',
  TDX_DETECT: '/v1/data-source-config/tdx/detect',
  TDX_CONVERT_STREAM: '/v1/data-source-config/tdx/convert-stream',

  // 可以添加更多API路径...
} as const

// 完整URL构建辅助函数
export function buildApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`
}
