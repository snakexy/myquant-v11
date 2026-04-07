/**
 * Vite插件：自动检测后端API端口
 */
import type { Plugin } from 'vite'

export interface AutoDetectApiPortOptions {
  /**
   * 端口检测范围
   * @default [8000, 8020]
   */
  portRange?: [number, number]

  /**
   * 健康检查路径
   * @default '/api/v1/market/health'
   */
  healthCheckPath?: string

  /**
   * 检测超时时间（毫秒）
   * @default 1000
   */
  timeout?: number
}

export function autoDetectApiPort(options: AutoDetectApiPortOptions = {}): Plugin {
  const {
    portRange = [8000, 8020],
    healthCheckPath = '/api/v1/market/health',
    timeout = 1000,
  } = options

  return {
    name: 'vite-plugin-auto-detect-api-port',
    apply: 'serve',  // 仅在开发模式应用

    async configResolved(config) {
      const [startPort, endPort] = portRange
      let detectedPort = startPort

      console.log(`\n🔍 正在检测后端API端口 (${startPort}-${endPort})...`)

      // 检测可用端口
      for (let port = startPort; port <= endPort; port++) {
        const available = await checkBackendPort(port, healthCheckPath, timeout)
        if (available) {
          detectedPort = port
          break
        }
      }

      console.log(`✅ 检测到后端API服务运行在端口: ${detectedPort}`)

      // 更新代理配置
      if (config.server) {
        if (!config.server.proxy) {
          config.server.proxy = {}
        }

        config.server.proxy['/api'] = {
          target: `http://localhost:${detectedPort}`,
          changeOrigin: true,
          secure: false,
        }

        config.server.proxy['/ws'] = {
          target: `ws://localhost:${detectedPort}`,
          ws: true,
        }
      }

      // 将端口注入到环境变量
      if (!config.define) {
        config.define = {}
      }

      config.define['__API_PORT__'] = JSON.stringify(detectedPort)
    },
  }
}

/**
 * 检查后端端口是否有服务运行
 */
async function checkBackendPort(
  port: number,
  healthCheckPath: string,
  timeout: number
): Promise<boolean> {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    const response = await fetch(`http://localhost:${port}${healthCheckPath}`, {
      method: 'GET',
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (response.ok) {
      const data = await response.json()
      return data.status === 'healthy' || data.service === 'market_analysis'
    }

    return false
  } catch (error) {
    // 端口没有服务或其他错误
    return false
  }
}
