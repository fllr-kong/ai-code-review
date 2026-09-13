import { computed, ref } from 'vue'
import { getCurrentUser, login as loginRequest, logout as logoutRequest, register as registerRequest } from '../api'

const user = ref(null)

export function useAuth() {
  const isLoggedIn = computed(() => Boolean(user.value))

  async function loadCurrentUser() {
    const response = await getCurrentUser()
    user.value = response.data.user
    return user.value
  }

  async function login(username, password) {
    const response = await loginRequest(username, password)
    user.value = response.data.user
    return user.value
  }

  async function register(username, password) {
    const response = await registerRequest(username, password)
    user.value = response.data.user
    return user.value
  }

  async function logout() {
    await logoutRequest()
    user.value = null
  }

  return { user, isLoggedIn, loadCurrentUser, login, register, logout }
}
