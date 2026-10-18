// Cấu hình API backend.
// - Trong dev: dùng proxy '/api' (Vite proxy -> http://localhost:5000)
// - Trong production: đặt VITE_API_BASE_URL trong .env.production
//   hoặc file cấu hình deploy (vd Vercel env vars)
//
// Mặc định: '/api' — hoạt động khi backend cùng domain (vd qua Nginx/Vercel rewrites)
const BASE = (typeof __API_BASE__ !== 'undefined' && __API_BASE__) || '/api'

export const API_URL = `${BASE}/predict`
export const API_DEBUG_URL = `${BASE}/debug-segments`
export const API_HEALTH_URL = `${BASE}/health`
