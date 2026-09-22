import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  withCredentials: true
})

// 响应拦截器：统一处理 401 未授权
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 只在非登录接口报 401 时提示，避免登录页面重复提示
      const url = error.config?.url || ''
      if (!url.includes('/auth/login')) {
        ElMessage.warning(error.response.data?.error || '登录已过期，请重新登录')
      }
      // 懒加载 router，避免 api.js 和 router 循环引用
      import('../router').then(({ default: router }) => {
        const name = router.currentRoute.value.name
        if (name !== 'Login' && name !== 'Register') {
          router.push('/login')
        }
      })
    }
    return Promise.reject(error)
  }
)

export function login(username, password) {
  return api.post('/auth/login', { username, password })
}

export function register(username, password) {
  return api.post('/auth/register', { username, password })
}

export function logout() {
  return api.post('/auth/logout')
}

export function getCurrentUser() {
  return api.get('/auth/me')
}

export function reviewCode(code, language, filename = 'untitled') {
  return api.post('/review', { code, language, filename })
}

export function reviewBatch(files, language) {
  const formData = new FormData()
  files.forEach(f => formData.append('files', f))
  formData.append('language', language)
  return api.post('/review/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function getHistory() {
  return api.get('/history')
}

export function getHistoryDetail(id) {
  return api.get(`/history/${id}`)
}

export function deleteHistory(id) {
  return api.delete(`/history/${id}`)
}

export function getShareStatus(id) {
  return api.get(`/history/${id}/share`)
}

export function createShare(id) {
  return api.post(`/history/${id}/share`)
}

export function revokeShare(id) {
  return api.delete(`/history/${id}/share`)
}

export function getSharedReview(code) {
  return api.get(`/share/${code}`)
}

export function detectLanguage(code) {
  return api.post('/detect-language', { code })
}
