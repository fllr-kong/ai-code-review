<template>
  <el-container class="app-container">
    <template v-if="!isPlainPage">
      <el-header class="app-header" height="64px">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            <div class="logo-icon">
              <el-icon :size="22"><Monitor /></el-icon>
            </div>
            <span class="logo-text">AI 代码审查助手</span>
          </div>
          <el-menu mode="horizontal" :default-active="$route.path" router class="nav-menu" :ellipsis="false">
            <el-menu-item index="/">
              <el-icon><EditPen /></el-icon>
              <span>代码审查</span>
            </el-menu-item>
            <el-menu-item index="/history">
              <el-icon><Clock /></el-icon>
              <span>历史记录</span>
            </el-menu-item>
          </el-menu>
          <div v-if="auth.user.value" class="user-area">
            <div class="user-avatar">{{ auth.user.value.username.charAt(0).toUpperCase() }}</div>
            <span class="user-name">{{ auth.user.value.username }}</span>
            <el-button link class="logout-btn" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出
            </el-button>
          </div>
        </div>
      </el-header>
    </template>
    <el-main :class="{ 'auth-main': isPlainPage }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, EditPen, Clock, SwitchButton } from '@element-plus/icons-vue'
import { useAuth } from './stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuth()

const isPlainPage = computed(() =>
  ['Login', 'Register', 'Share'].includes(route.name)
)

async function handleLogout() {
  try {
    await auth.logout()
    ElMessage.success('已退出登录')
  } catch (e) {
  }
  router.push('/login')
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: var(--bg-base);
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.header-content {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
}
.logo:hover {
  opacity: 0.85;
}
.logo-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--brand-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 12px -2px rgba(99, 102, 241, 0.4);
}
.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.3px;
}

.nav-menu {
  background: transparent;
  border-bottom: none;
  flex: 1;
}
.nav-menu :deep(.el-menu-item) {
  color: var(--text-secondary);
  border-bottom: 3px solid transparent;
  font-weight: 500;
  font-size: 14px;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.nav-menu :deep(.el-menu-item:hover) {
  color: var(--brand-primary);
  background: rgba(99, 102, 241, 0.06);
}
.nav-menu :deep(.el-menu-item.is-active) {
  color: var(--brand-primary);
  border-bottom: 3px solid var(--brand-primary);
  background: transparent;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--brand-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 8px -1px rgba(99, 102, 241, 0.35);
}
.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}
.logout-btn {
  color: var(--text-muted) !important;
  font-size: 13px;
}
.logout-btn:hover {
  color: #ef4444 !important;
}

.auth-main {
  padding: 0;
}

@media (max-width: 768px) {
  .header-content {
    gap: 16px;
  }
  .logo-text {
    display: none;
  }
  .user-name {
    display: none;
  }
}
</style>
