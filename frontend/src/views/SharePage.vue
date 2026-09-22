<template>
  <div class="share-page">
    <div class="share-topbar">
      <div class="topbar-inner">
        <div class="brand" @click="$router.push('/')">
          <div class="brand-icon">
            <el-icon :size="18"><Monitor /></el-icon>
          </div>
          <span>AI 代码审查助手</span>
        </div>
        <el-button type="primary" round size="default" @click="$router.push('/')">
          我也要试用
        </el-button>
      </div>
    </div>

    <div class="share-container">
      <el-result v-if="notFound" icon="error" title="分享不存在或已被取消" sub-title="请联系分享者重新获取链接">
        <template #extra>
          <el-button type="primary" round @click="$router.push('/')">返回首页</el-button>
        </template>
      </el-result>

      <template v-else>
        <el-alert
          v-if="record"
          :title="`${record.owner_name || '匿名用户'} 分享的代码审查结果（只读）`"
          type="success"
          :closable="false"
          show-icon
          class="share-banner"
        />

        <el-card v-if="record" class="share-card" shadow="never" v-loading="loading">
          <div class="card-title-row">
            <el-icon :size="20" color="var(--brand-primary)"><Document /></el-icon>
            <span class="card-title">{{ record.filename }}</span>
          </div>

          <el-descriptions :column="4" border style="margin-top: 12px">
            <el-descriptions-item label="文件">{{ record.filename }}</el-descriptions-item>
            <el-descriptions-item label="语言">{{ record.language }}</el-descriptions-item>
            <el-descriptions-item label="代码行数">{{ record.total_lines }}</el-descriptions-item>
            <el-descriptions-item label="问题数">
              <el-tag :type="record.issues_count > 0 ? 'warning' : 'success'" round>
                {{ record.issues_count }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="审查时间" :span="4">{{ record.created_at }}</el-descriptions-item>
          </el-descriptions>

          <el-tabs v-model="activeTab" class="share-tabs">
            <el-tab-pane label="原代码" name="code">
              <pre class="code-block"><code>{{ record.code }}</code></pre>
            </el-tab-pane>
            <el-tab-pane label="审查结果" name="result">
              <div v-if="result.issues?.length > 0" class="issues-list">
                <div v-for="(issue, idx) in result.issues" :key="idx" class="issue-block">
                  <div class="issue-divider">
                    <el-tag :type="severityTagType(issue.severity)" effect="dark" round>
                      第 {{ issue.line }} 行
                    </el-tag>
                    <el-tag round>{{ issue.category }}</el-tag>
                    <span class="issue-title-text">{{ issue.title }}</span>
                  </div>
                  <div class="issue-body">
                    <div class="issue-section">
                      <strong>描述</strong>
                      <p>{{ issue.description }}</p>
                    </div>
                    <div class="issue-section">
                      <strong>建议</strong>
                      <p>{{ issue.suggestion }}</p>
                    </div>
                    <div class="code-compare">
                      <div class="compare-pane">
                        <div class="pane-label">
                          <el-icon :size="12"><Document /></el-icon>
                          原代码
                        </div>
                        <pre><code>{{ issue.original_code }}</code></pre>
                      </div>
                      <div class="compare-pane compare-pane-fixed">
                        <div class="pane-label">
                          <el-icon :size="12" color="#10b981"><Check /></el-icon>
                          修改后
                        </div>
                        <pre><code>{{ issue.fixed_code }}</code></pre>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="no-issues">
                <el-icon :size="36" color="#10b981"><CircleCheck /></el-icon>
                <p>代码质量良好，未发现问题</p>
              </div>
            </el-tab-pane>
            <el-tab-pane label="完整修改后代码" name="fixed">
              <div class="fixed-wrap">
                <el-button type="primary" round :icon="CopyDocument" @click="copyFixedCode">
                  复制代码
                </el-button>
                <pre class="code-block code-block-fixed"><code>{{ result.full_fixed_code }}</code></pre>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, Document, Check, CircleCheck, CopyDocument } from '@element-plus/icons-vue'
import { getSharedReview } from '../api'

const route = useRoute()
const loading = ref(false)
const record = ref(null)
const notFound = ref(false)
const activeTab = ref('code')

const result = computed(() => record.value?.result || {})

onMounted(loadShared)

async function loadShared() {
  loading.value = true
  try {
    const res = await getSharedReview(route.params.code)
    record.value = res.data
  } catch (e) {
    if (e.response?.status === 404) {
      notFound.value = true
    } else {
      ElMessage.error('加载分享内容失败')
    }
  } finally {
    loading.value = false
  }
}

function severityTagType(sev) {
  return { error: 'danger', warning: 'warning', suggestion: 'info' }[sev] || ''
}

async function copyFixedCode() {
  if (result.value.full_fixed_code) {
    try {
      await navigator.clipboard.writeText(result.value.full_fixed_code)
      ElMessage.success('已复制')
    } catch (e) {
      ElMessage.error('复制失败')
    }
  }
}
</script>

<style scoped>
.share-page {
  min-height: 100vh;
  background: var(--bg-base);
}

.share-topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--border-light);
}
.topbar-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  transition: opacity 0.2s;
}
.brand:hover {
  opacity: 0.8;
}
.brand-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--brand-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 2px 8px -1px rgba(99, 102, 241, 0.35);
}

.share-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px 24px;
}

.share-banner {
  margin-bottom: 16px;
  border-radius: var(--radius-md);
}

.share-card {
  border-radius: var(--radius-lg) !important;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.share-tabs {
  margin-top: 20px;
}

.code-block {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 16px;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  max-height: 500px;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}
.code-block-fixed {
  max-height: 600px;
}

.issue-block {
  margin-bottom: 28px;
}
.issue-divider {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
  flex-wrap: wrap;
}
.issue-title-text {
  font-weight: 600;
  color: var(--text-primary);
}
.issue-body {
  padding: 12px 0;
}
.issue-section {
  margin-bottom: 10px;
  line-height: 1.6;
}
.issue-section strong {
  display: block;
  color: var(--text-primary);
  font-size: 13px;
  margin-bottom: 2px;
}
.issue-section p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.code-compare {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
.compare-pane {
  flex: 1;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.compare-pane-fixed {
  border-color: #bbf7d0;
}
.compare-pane pre {
  margin: 0;
  padding: 12px;
  background: #1e1e2e;
  color: #cdd6f4;
  font-size: 13px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  max-height: 250px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.5;
}
.pane-label {
  padding: 6px 12px;
  background: var(--bg-subtle);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  gap: 4px;
}

.no-issues {
  text-align: center;
  padding: 40px 20px;
}
.no-issues p {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
}

.fixed-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (max-width: 768px) {
  .code-compare {
    flex-direction: column;
  }
}
</style>
