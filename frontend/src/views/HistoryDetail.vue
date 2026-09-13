<template>
  <div class="history-detail">
    <el-page-header @back="$router.push('/history')" :content="'审查详情 - ' + record?.filename" />

    <div v-loading="loading" v-if="record" class="detail-content">
      <el-descriptions :column="4" border style="margin-top: 16px">
        <el-descriptions-item label="文件">{{ record.filename }}</el-descriptions-item>
        <el-descriptions-item label="语言">{{ record.language }}</el-descriptions-item>
        <el-descriptions-item label="代码行数">{{ record.total_lines }}</el-descriptions-item>
        <el-descriptions-item label="问题数">
          <el-tag :type="record.issues_count > 0 ? 'warning' : 'success'">
            {{ record.issues_count }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审查时间" :span="4">{{ record.created_at }}</el-descriptions-item>
      </el-descriptions>

      <el-tabs v-model="activeTab" style="margin-top: 20px">
        <el-tab-pane label="原代码" name="code">
          <pre class="code-block"><code>{{ record.code }}</code></pre>
        </el-tab-pane>
        <el-tab-pane label="审查结果" name="result">
          <div v-if="result.issues?.length > 0" class="issues-list">
            <div v-for="(issue, idx) in result.issues" :key="idx" class="issue-block">
              <el-divider content-position="left">
                <el-tag :type="severityTagType(issue.severity)" effect="dark">
                  第 {{ issue.line }} 行
                </el-tag>
                <el-tag style="margin-left: 8px">{{ issue.category }}</el-tag>
                <span style="margin-left: 8px">{{ issue.title }}</span>
              </el-divider>
              <div class="issue-body">
                <p><strong>描述：</strong>{{ issue.description }}</p>
                <p><strong>建议：</strong>{{ issue.suggestion }}</p>
                <div class="code-compare">
                  <div class="compare-pane">
                    <div class="pane-label">原代码</div>
                    <pre><code>{{ issue.original_code }}</code></pre>
                  </div>
                  <div class="compare-pane">
                    <div class="pane-label">修改后</div>
                    <pre><code>{{ issue.fixed_code }}</code></pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="代码质量良好，未发现问题！" />
        </el-tab-pane>
        <el-tab-pane label="完整修改后代码" name="fixed">
          <pre class="code-block fixed"><code>{{ result.full_fixed_code }}</code></pre>
          <el-button type="primary" @click="copyFixedCode" style="margin-top: 12px">
            复制代码
          </el-button>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getHistoryDetail } from '../api'

const route = useRoute()
const loading = ref(false)
const record = ref(null)
const activeTab = ref('code')

const result = computed(() => record.value?.result || {})

onMounted(() => loadDetail())

async function loadDetail() {
  loading.value = true
  try {
    const res = await getHistoryDetail(route.params.id)
    record.value = res.data
  } catch (e) {
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
}

function severityTagType(sev) {
  return { error: 'danger', warning: 'warning', suggestion: 'info' }[sev] || ''
}

async function copyFixedCode() {
  if (result.value.full_fixed_code) {
    await navigator.clipboard.writeText(result.value.full_fixed_code)
    ElMessage.success('已复制')
  }
}
</script>

<style scoped>
.history-detail {
  max-width: 1200px;
  margin: 0 auto;
}
.code-block {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 500px;
  white-space: pre-wrap;
  word-break: break-all;
}
.code-block.fixed {
  max-height: 600px;
}
.issue-block {
  margin-bottom: 24px;
}
.issue-body {
  padding: 0 12px;
}
.code-compare {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
.compare-pane {
  flex: 1;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}
.compare-pane pre {
  margin: 0;
  padding: 10px;
  background: #1e1e1e;
  color: #d4d4d4;
  font-size: 13px;
  max-height: 250px;
  overflow: auto;
}
.pane-label {
  padding: 6px 12px;
  background: #f5f7fa;
  font-size: 12px;
  color: #909399;
  border-bottom: 1px solid #ebeef5;
}
</style>
