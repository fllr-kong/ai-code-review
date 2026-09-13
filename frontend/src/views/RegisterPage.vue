<template>
  <div class="auth-page">
    <!-- 装饰性背景：渐变 + 浮动色块 -->
    <div class="bg-decoration">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <div class="auth-wrapper">
      <!-- 左侧品牌介绍（宽屏显示） -->
      <div class="brand-panel">
        <div class="brand-logo">
          <el-icon :size="44"><Monitor /></el-icon>
        </div>
        <h2 class="brand-title">加入 AI 审查</h2>
        <p class="brand-desc">10 秒创建账号，开启你的代码质量之旅</p>
        <ul class="brand-features">
          <li><el-icon><Select /></el-icon>所有历史记录自动云端保存</li>
          <li><el-icon><Select /></el-icon>多语言检测，智能识别代码类型</li>
          <li><el-icon><Select /></el-icon>按严重等级分组：错误 / 警告 / 建议</li>
        </ul>
      </div>

      <!-- 右侧注册卡片 -->
      <el-card class="auth-card" shadow="hover">
        <div class="auth-header">
          <h1 class="hero-title">
            <span v-for="(ch, i) in titleChars" :key="i" class="hero-char" :style="{ animationDelay: i * 0.06 + 's' }">{{ ch.char }}</span>
            <span class="hero-sparkle" aria-label="sparkle">✨</span>
          </h1>
          <p class="hero-sub">仅需用户名和密码即可注册</p>
        </div>

        <el-form
          ref="registerFormRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleRegister"
          class="auth-form"
          label-position="top"
          size="large"
        >
          <el-form-item prop="username" label="用户名">
            <el-input
              v-model="form.username"
              placeholder="3-20 位中文、字母、数字或下划线"
              :prefix-icon="User"
              autocomplete="username"
              clearable
              maxlength="20"
              show-word-limit
            />
          </el-form-item>

          <el-form-item prop="password" label="密码">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              placeholder="至少 6 位，建议字母+数字组合"
              :prefix-icon="Lock"
              autocomplete="new-password"
            />
            <div class="pwd-hint">
              <span :class="{ ok: form.password.length >= 6 }">● 至少 6 位</span>
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword" label="确认密码">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              show-password
              placeholder="请再次输入密码"
              :prefix-icon="Lock"
              autocomplete="new-password"
              @keyup.enter="handleRegister"
            />
          </el-form-item>

          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="submit-button"
            size="large"
          >
            {{ loading ? '注册中...' : '注 册 账 号' }}
          </el-button>
        </el-form>

        <div class="auth-footer">
          <span>已有账号？</span>
          <router-link to="/login" class="link-primary">返回登录 →</router-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor, Select } from '@element-plus/icons-vue'
import { useAuth } from '../stores/auth'

const router = useRouter()
const auth = useAuth()
const registerFormRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

// 标题逐字拆分：创建账号
const titleChars = '创建账号'.split('').map((ch) => ({ char: ch }))

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度 3-20 位', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9_\u4e00-\u9fff]{3,20}$/,
      message: '支持中文、字母、数字和下划线',
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度 6-128 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value, cb) => {
        if (value !== form.password) cb(new Error('两次输入的密码不一致'))
        else cb()
      },
      trigger: 'blur'
    }
  ]
}

async function handleRegister() {
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await auth.register(form.username, form.password)
    ElMessage.success({ message: `注册成功！欢迎你，${form.username} 🎉`, duration: 2000 })
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ========== 全屏背景 ========== */
.auth-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

/* 背景装饰球 */
.bg-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: float 18s ease-in-out infinite;
}
.blob-1 {
  width: 420px; height: 420px;
  background: #ff9a9e;
  top: -120px; left: -80px;
}
.blob-2 {
  width: 380px; height: 380px;
  background: #a1c4fd;
  bottom: -100px; right: -60px;
  animation-delay: -6s;
}
.blob-3 {
  width: 320px; height: 320px;
  background: #fbc2eb;
  top: 40%; right: 20%;
  animation-delay: -12s;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%      { transform: translate(40px, -30px) scale(1.08); }
  66%      { transform: translate(-30px, 40px) scale(0.95); }
}
.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 48px 48px;
}

/* ========== 两列布局 ========== */
.auth-wrapper {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  width: min(960px, 100%);
  min-height: 600px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 30px 60px -15px rgba(0, 0, 0, 0.3),
    0 10px 30px -10px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

/* ========== 左侧品牌面板 ========== */
.brand-panel {
  background: linear-gradient(160deg, rgba(102, 126, 234, 0.92), rgba(118, 75, 162, 0.92));
  color: #fff;
  padding: 56px 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.brand-panel::after {
  content: '';
  position: absolute;
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 70%);
  right: -100px; bottom: -100px;
  border-radius: 50%;
}
.brand-logo {
  width: 72px; height: 72px;
  background: rgba(255,255,255,0.18);
  border: 2px solid rgba(255,255,255,0.35);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 28px;
  backdrop-filter: blur(6px);
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2);
}
.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px;
  letter-spacing: 0.5px;
}
.brand-desc {
  font-size: 15px;
  opacity: 0.9;
  margin: 0 0 36px;
  line-height: 1.6;
}
.brand-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.brand-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  opacity: 0.92;
  line-height: 1.5;
}
.brand-features li .el-icon {
  flex-shrink: 0;
  width: 20px; height: 20px;
  background: rgba(255,255,255,0.22);
  border-radius: 50%;
  padding: 3px;
  color: #fff;
}

/* ========== 右侧表单卡片 ========== */
.auth-card {
  background: #fff;
  border: none !important;
  padding: 48px 44px !important;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
:deep(.el-card__body) {
  padding: 0;
  display: flex;
  flex-direction: column;
  flex: 1;
  justify-content: center;
}

.auth-header {
  margin-bottom: 24px;
}

/* ========== 标题动画：逐字弹跳 + ✨ 闪烁抖动 ========== */
.hero-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 6px;
  color: #1f2937;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
  line-height: 1.4;
}
.hero-char {
  display: inline-block;
  opacity: 0;
  transform: translateY(22px) rotate(-8deg) scale(0.7);
  animation: heroCharIn 0.6s cubic-bezier(0.2, 0.9, 0.3, 1.3) forwards;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
@keyframes heroCharIn {
  0% {
    opacity: 0;
    transform: translateY(22px) rotate(-8deg) scale(0.7);
  }
  60% {
    opacity: 1;
    transform: translateY(-6px) rotate(4deg) scale(1.08);
  }
  100% {
    opacity: 1;
    transform: translateY(0) rotate(0) scale(1);
  }
}
.hero-sparkle {
  display: inline-block;
  margin-left: 6px;
  font-size: 26px;
  animation: sparkleShake 1.8s ease-in-out infinite;
  animation-delay: 0.4s;
  filter: drop-shadow(0 0 6px rgba(251, 191, 36, 0.6));
}
@keyframes sparkleShake {
  0%, 70%, 100% { transform: scale(1) rotate(0deg); opacity: 1; }
  10%      { transform: scale(1.25) rotate(-12deg); opacity: 0.85; }
  20%      { transform: scale(0.9)  rotate(10deg);  opacity: 1; }
  35%      { transform: scale(1.2)  rotate(-8deg);  opacity: 0.9; }
  50%      { transform: scale(1)    rotate(0deg);  opacity: 1; }
}
.hero-sub {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
  opacity: 0;
  transform: translateY(10px);
  animation: heroSubIn 0.7s ease-out 0.5s forwards;
}
@keyframes heroSubIn {
  to { opacity: 1; transform: translateY(0); }
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 18px;
}
.auth-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #374151;
  padding-bottom: 4px;
  font-size: 14px;
}
.auth-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #e5e7eb inset;
  padding: 4px 12px;
  border-radius: 10px;
  transition: all 0.2s;
}
.auth-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c7d2fe inset;
}
.auth-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #818cf8 inset !important;
}

.pwd-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #9ca3af;
}
.pwd-hint .ok {
  color: #10b981;
  font-weight: 600;
}

.submit-button {
  width: 100%;
  margin-top: 4px;
  height: 46px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 2px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 8px 20px -8px rgba(102, 126, 234, 0.7);
  transition: all 0.25s;
}
.submit-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px -8px rgba(102, 126, 234, 0.8);
  filter: brightness(1.05);
}
.submit-button:active {
  transform: translateY(0);
}

.auth-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #6b7280;
}
.link-primary {
  color: #6366f1;
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
  transition: all 0.2s;
}
.link-primary:hover {
  color: #4f46e5;
  text-decoration: underline;
}

/* ========== 响应式：窄屏隐藏左侧品牌 ========== */
@media (max-width: 768px) {
  .auth-wrapper {
    grid-template-columns: 1fr;
    min-height: auto;
  }
  .brand-panel {
    display: none;
  }
  .auth-card {
    padding: 36px 24px !important;
  }
  .auth-header h1 { font-size: 22px; }
}
</style>
