<template>
  <div class="home-page">
    <el-row :gutter="16">
      <el-col :span="14">
        <EditorPanel
          v-model="code"
          v-model:language="language"
          :loading="loading"
          @submit="onSubmit"
        />
      </el-col>
      <el-col :span="10">
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
  height: calc(100vh - 60px);
}
</style>
