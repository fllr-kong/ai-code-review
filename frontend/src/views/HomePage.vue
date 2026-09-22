<template>
  <div class="home-page">
    <div class="page-hero">
      <div class="hero-left">
        <h1 class="page-title">代码审查</h1>
        <p class="page-subtitle">将代码粘贴到左侧编辑器，AI 会自动检测语言并给出审查建议</p>
      </div>
      <div class="hero-badge">
        <el-icon :size="16"><MagicStick /></el-icon>
        <span>AI Powered</span>
      </div>
    </div>

    <el-row :gutter="20" class="page-body">
      <el-col :xs="24" :lg="14">
        <EditorPanel
          v-model="code"
          v-model:language="language"
          :loading="loading"
          @submit="onSubmit"
        />
      </el-col>
      <el-col :xs="24" :lg="10">
        <ResultPanel
          :result="result"
          @select-issue="onSelectIssue"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import EditorPanel from '../components/EditorPanel.vue'
import ResultPanel from '../components/ResultPanel.vue'
import { reviewCode } from '../api'

const code = ref('')
const language = ref('python')
const loading = ref(false)
const result = ref(null)

const sampleCode = `def calculate_bonus(salary, performance):
    if performance >= 90:
        bonus = salary * 0.2
    elif performance >= 80:
        bonus = salary * 0.1
    else:
        bonus = 0
    
    return bonus

name = input("请输入姓名: ")
age = input("请输入年龄: ")
print(name + "的奖金是: " + bonus)`

code.value = sampleCode

async function onSubmit() {
  if (!code.value.trim()) {
    ElMessage.warning('请输入要审查的代码')
    return
  }

  loading.value = true
  result.value = null

  try {
    const res = await reviewCode(code.value, language.value)
    result.value = res.data
    if (result.value.error) {
      ElMessage.warning('审查完成，但有部分错误：' + result.value.error)
    } else {
      ElMessage.success('审查完成！发现 ' + (result.value.issues?.length || 0) + ' 个问题')
    }
  } catch (e) {
    ElMessage.error('审查失败：' + (e.response?.data?.error || e.message))
  } finally {
    loading.value = false
  }
}

function onSelectIssue(issue) {
}
</script>

<style scoped>
.home-page {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  padding: 20px 24px;
  gap: 16px;
}

.page-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-shrink: 0;
}
.hero-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}
.page-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.5;
}
.hero-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--brand-gradient-soft);
  color: var(--brand-primary-dark);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.page-body {
  flex: 1;
  min-height: 0;
  margin: 0 !important;
}
.page-body :deep(.el-col) {
  height: 100%;
}

@media (max-width: 768px) {
  .home-page {
    height: auto;
    min-height: calc(100vh - 64px);
    padding: 16px;
  }
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
