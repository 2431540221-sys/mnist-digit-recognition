import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // VITE_API_BASE_URL — URL tuyệt đối tới backend (vd https://api.example.com)
  // Nếu không có thì dùng relative '/api' (proxy hoặc cùng origin)
  const apiBase = env.VITE_API_BASE_URL || '/api'

  return {
    plugins: [vue()],
    server: {
      port: 5173,
      proxy: {
        // Proxy dev: /api -> Flask ở port 5000
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/api/, ''),
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
    },
    define: {
      __API_BASE__: JSON.stringify(apiBase),
    },
  }
})
