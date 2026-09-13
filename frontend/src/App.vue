<template>
  <el-container class="app-container">
    <template v-if="!isAuthPage">
      <el-header class="app-header" height="60px">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            <el-icon :size="28" color="#409EFF"><Monitor /></el-icon>
            <span>AI 代码审查助手</span>
          </div>
          <el-menu mode="horizontal" :default-active="$route.path" router class="nav-menu">
            <el-menu-item index="/">代码审查</el-menu-item>
            <el-menu-item index="/history">历史记录</el-menu-item>
          </el-menu>
          <div v-if="auth.user.value" class="user-area">
            <span>{{ auth.user.value.username }}</span>
            <el-button link type="info" @click="handleLogout">退出</el-button>
          </div>
        </div>
      </el-header>
    </template>
    <el-main :class="{ 'auth-main': isAuthPage }">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuth } from './stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuth()

const isAuthPage = computed(() => route.name === 'Login' || route.name === 'Register')

async function handleLogout() {
  try {
    await auth.logout()
    ElMessage.success('已退出登录')
  } catch (e) {
    // 忽略退出时的网络错误
  }
  router.push('/login')
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  padding: 0 20px;
}
.header-content {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 40px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
}
.nav-menu {
  background: transparent;
  border-bottom: none;
  flex: 1;
}
.nav-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.85);
  border-bottom: 2px solid transparent;
}
.nav-menu :deep(.el-menu-item.is-active) {
  color: #fff;
  border-bottom: 2px solid #fff;
  background: transparent;
}
.nav-menu :deep(.el-menu-item:hover) {
  color: #fff;
  background: transparent;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
}
.user-area :deep(.el-button) {
  color: rgba(255, 255, 255, 0.85);
}
.auth-main {
  padding: 0;
}
</style>
