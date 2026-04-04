import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { autoDetectApiPort } from './vite-plugin-auto-detect-api-port'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // 暂时禁用自动检测，使用手动配置
    // autoDetectApiPort({
    //   portRange: [8000, 8020],
    //   healthCheckPath: '/api/v1/market/health',
    //   timeout: 2000,
    // }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      'lightweight-charts': resolve(__dirname, 'external/lightweight-charts/dist/lightweight-charts.development.mjs'),
      // 类型导入指向源码
      'lightweight-charts/typings': resolve(__dirname, 'external/lightweight-charts/src/typings'),
    },
    // 自动解析类型扩展名
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.d.ts'],
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
        additionalData: ``,
      },
    },
  },
  server: {
    port: 5180,
    host: '0.0.0.0',
    strictPort: false,  // 如果5180被占用，自动尝试下一个端口
    proxy: {
      // 调试端点（直接代理 /debug 到后端）
      '/debug': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // 代理到 v11 backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        secure: false,
      },
    },
    // proxy 配置由 autoDetectApiPort 插件自动设置
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        // M2-15优化：更细粒度的代码分割策略
        manualChunks: (id) => {
          // node_modules包分类
          if (id.includes('node_modules')) {
            // Vue核心框架
            if (id.includes('vue') || id.includes('pinia')) {
              return 'vue-core'
            }

            // 路由
            if (id.includes('vue-router')) {
              return 'router'
            }

            // Naive UI
            if (id.includes('naive-ui')) {
              return 'naive-ui'
            }

            // Element Plus
            if (id.includes('element-plus') || id.includes('@element-plus')) {
              return 'element-plus'
            }

            // 图表库 - lightweight-charts
            if (id.includes('lightweight-charts')) {
              return 'charts-lightweight'
            }

            // 图表库 - echarts
            if (id.includes('echarts')) {
              return 'charts-echarts'
            }

            // 图表库 - klinecharts
            if (id.includes('klinecharts') || id.includes('trading-vue-js')) {
              return 'charts-kline'
            }

            // 网络图
            if (id.includes('vis-network')) {
              return 'charts-network'
            }

            // 工具库
            if (id.includes('lodash') || id.includes('axios') || id.includes('dayjs')) {
              return 'utils'
            }

            // 动画库
            if (id.includes('gsap')) {
              return 'anim-gsap'
            }

            // 其他第三方库
            return 'vendor'
          }

          // 业务代码按模块分割
          if (id.includes('src/views')) {
            // 股票相关页面
            if (id.includes('stock') || id.includes('kline') || id.includes('SectorMap')) {
              return 'page-stock'
            }
            // 回测策略页面
            if (id.includes('backtest') || id.includes('strategy') || id.includes('UnrealBlueprint')) {
              return 'page-backtest'
            }
            // 数据管理页面
            if (id.includes('data') || id.includes('DataManagement')) {
              return 'page-data'
            }
            // 研究阶段页面
            if (id.includes('research') || id.includes('validation') || id.includes('production')) {
              return 'page-stage'
            }
            // 监控相关页面
            if (id.includes('monitor') || id.includes('Monitoring')) {
              return 'page-monitor'
            }
            // 其他页面
            return 'page-other'
          }

          // 组件代码分割
          if (id.includes('src/components')) {
            // 图表组件
            if (id.includes('charts')) {
              return 'comp-charts'
            }
            // 热点分析组件
            if (id.includes('hotspot')) {
              return 'comp-hotspot'
            }
            // 通用组件
            return 'comp-common'
          }
        },
        // 配置chunk文件名
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'naive-ui', 'echarts'],
  },
})