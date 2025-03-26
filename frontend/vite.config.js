import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
    __VUE_PROD_DEVTOOLS__: 'false',
    __VUE_OPTIONS_API__: 'true'
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, options) => {
          // 添加调试信息
          proxy.on('error', (err, req, res) => {
            console.log('代理错误', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('发送请求到:', proxyReq.path);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('收到响应:', proxyRes.statusCode);
          });
        }
      }
    }
  }
}) 