import { createRouter, createWebHistory } from 'vue-router'
import { getCurrentUser } from '../api'
import { useAuth } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginPage.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/RegisterPage.vue') },
  { path: '/', name: 'Home', meta: { requiresAuth: true }, component: () => import('../views/HomePage.vue') },
  { path: '/history', name: 'History', meta: { requiresAuth: true }, component: () => import('../views/HistoryPage.vue') },
  { path: '/history/:id', name: 'HistoryDetail', meta: { requiresAuth: true }, component: () => import('../views/HistoryDetail.vue') },
  { path: '/share/:code', name: 'Share', component: () => import('../views/SharePage.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

let authChecked = false
const auth = useAuth()

router.beforeEach(async (to) => {
  // 公开分享页无需登录态，直接放行（未登录访问也不触发 /auth/me 请求）
  if (to.name === 'Share') return true

  let loggedIn = Boolean(auth.user.value)
  if (!authChecked) {
    try {
      const response = await getCurrentUser()
      loggedIn = Boolean(response.data.user)
      auth.user.value = response.data.user
    } catch (error) {
      loggedIn = false
      auth.user.value = null
    }
    authChecked = true
  }

  if (to.meta.requiresAuth && !loggedIn) return { name: 'Login' }
  if ((to.name === 'Login' || to.name === 'Register') && loggedIn) return { name: 'Home' }
})

export default router
