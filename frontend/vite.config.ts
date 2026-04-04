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
      'lightweight-charts': resolve(__dirname, 'external/lightweight-charts/dist/lightweight-charts.standalone.development.mjs'),
    },
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
        // 代码分割策略：最大化合并避免循环依赖
        manualChunks: (id) => {
          // node_modules: 只分割大型图表库
          if (id.includes('node_modules')) {
            // 图表库单独分割（体积大）
            if (id.includes('lightweight-charts') || id.includes('echarts')) {
              return 'charts'
            }
            // 其他所有 node_modules 合并
            return 'vendor'
          }

          // 业务代码：合并避免循环
          if (id.includes('src/views') || id.includes('src/components')) {
            return 'app'
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