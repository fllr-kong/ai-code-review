<template>
  <div class="result-panel">
    <div v-if="!result" class="empty-state">
      <div class="empty-illustration">
        <el-icon :size="48" color="#cbd5e1"><DataAnalysis /></el-icon>
      </div>
      <p class="empty-title">等待审查结果</p>
      <p class="empty-desc">提交代码后，审查结果将在此展示</p>
    </div>

    <template v-else>
      <!-- 统计卡片 -->
      <div class="summary-grid">
        <div class="stat-card stat-total">
          <div class="stat-icon"><el-icon :size="18"><Document /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ result.summary?.total_lines || 0 }}</span>
            <span class="stat-label">代码行数</span>
          </div>
        </div>
        <div class="stat-card stat-issues" :class="{ active: result.issues?.length > 0 }">
          <div class="stat-icon"><el-icon :size="18"><Warning /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ result.summary?.issues_count || result.issues?.length || 0 }}</span>
            <span class="stat-label">问题总数</span>
          </div>
        </div>
        <div class="stat-card stat-error">
          <div class="stat-icon"><el-icon :size="18"><CircleClose /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ countBySeverity('error') }}</span>
            <span class="stat-label">错误</span>
          </div>
        </div>
        <div class="stat-card stat-warning">
          <div class="stat-icon"><el-icon :size="18"><WarningFilled /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ countBySeverity('warning') }}</span>
            <span class="stat-label">警告</span>
          </div>
        </div>
        <div class="stat-card stat-suggestion">
          <div class="stat-icon"><el-icon :size="18"><InfoFilled /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ countBySeverity('suggestion') }}</span>
            <span class="stat-label">建议</span>
          </div>
        </div>
      </div>

      <div class="result-body">
        <div class="issue-list">
          <div class="issue-list-header">
            <span>发现的问题</span>
            <el-tag size="small" round>{{ result.issues?.length || 0 }}</el-tag>
          </div>
          <div v-if="!result.issues || result.issues.length === 0" class="no-issues">
            <el-icon :size="36" color="#10b981"><CircleCheck /></el-icon>
            <p>代码质量良好</p>
            <p class="no-issues-sub">未发现问题</p>
          </div>
          <template v-else>
            <div v-for="(group, key) in groupedIssues" :key="key" class="issue-group">
              <div v-if="group.length > 0" class="group-title" :class="key">
                <span class="group-dot"></span>
                {{ severityLabel(key) }}
                <span class="group-count">{{ group.length }}</span>
              </div>
              <div
                v-for="(issue, idx) in group"
                :key="idx"
                class="issue-item"
                :class="{ active: selectedIssue === issue }"
                @click="selectIssue(issue)"
              >
                <div class="issue-header">
                  <el-tag :type="severityTagType(issue.severity)" size="small" effect="dark" round>
                    L{{ issue.line }}
                  </el-tag>
                  <el-tag size="small" round>{{ issue.category }}</el-tag>
                </div>
                <div class="issue-title">{{ issue.title }}</div>
              </div>
            </div>
          </template>
        </div>

        <div class="right-panel">
          <el-tabs v-model="rightTab" type="border-card" class="detail-tabs">
            <el-tab-pane label="问题详情" name="issue">
              <div v-if="selectedIssue" class="diff-content">
                <div class="diff-header">
                  <el-tag :type="severityTagType(selectedIssue.severity)" effect="dark" round>
                    {{ severityLabel(selectedIssue.severity) }}
                  </el-tag>
                  <el-tag round>{{ selectedIssue.category }}</el-tag>
                  <span class="issue-title-text">{{ selectedIssue.title }}</span>
                </div>
                <div class="diff-desc">
                  <strong>问题描述</strong>
                  <p>{{ selectedIssue.description }}</p>
                </div>
                <div class="diff-suggestion">
                  <strong>修改建议</strong>
                  <p>{{ selectedIssue.suggestion }}</p>
                </div>
                <div class="diff-code">
                  <div class="code-pane">
                    <div class="pane-label">
                      <el-icon :size="12"><Document /></el-icon>
                      原代码
                    </div>
                    <pre><code>{{ selectedIssue.original_code }}</code></pre>
                  </div>
                  <div class="code-pane code-pane-fixed">
                    <div class="pane-label">
                      <el-icon :size="12" color="#10b981"><Check /></el-icon>
                      修改后
                    </div>
                    <pre><code>{{ selectedIssue.fixed_code }}</code></pre>
                  </div>
                </div>
              </div>
              <div v-else class="diff-empty">
                <el-icon :size="32" color="#cbd5e1"><Pointer /></el-icon>
                <p>点击左侧问题查看详情</p>
              </div>
            </el-tab-pane>

            <el-tab-pane label="修改后代码" name="fixed">
              <div v-if="result.full_fixed_code" class="fixed-code-wrap">
                <div class="fixed-actions">
                  <el-button type="primary" size="small" @click="copyFixedCode" round>
                    <el-icon><CopyDocument /></el-icon>
                    复制完整代码
                  </el-button>
                </div>
                <pre class="fixed-code"><code>{{ result.full_fixed_code }}</code></pre>
              </div>
              <div v-else class="diff-empty">
                <p>暂无修改后代码</p>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  CopyDocument, CircleCheck, CircleClose, Warning, WarningFilled,
  InfoFilled, Document, DataAnalysis, Check, Pointer
} from '@element-plus/icons-vue'

const props = defineProps({
  result: { type: Object, default: null }
})

const emit = defineEmits(['select-issue'])

const selectedIssue = ref(null)
const rightTab = ref('issue')

const groupedIssues = computed(() => {
  if (!props.result?.issues) return {}
  const groups = { error: [], warning: [], suggestion: [] }
  props.result.issues.forEach(issue => {
    if (groups[issue.severity]) {
      groups[issue.severity].push(issue)
    }
  })
  return groups
})

function countBySeverity(sev) {
  if (!props.result?.issues) return 0
  return props.result.issues.filter(i => i.severity === sev).length
}

function severityLabel(sev) {
  return { error: '错误', warning: '警告', suggestion: '建议' }[sev] || sev
}

function severityTagType(sev) {
  return { error: 'danger', warning: 'warning', suggestion: 'info' }[sev] || ''
}

function selectIssue(issue) {
  selectedIssue.value = issue
  emit('select-issue', issue)
}

async function copyFixedCode() {
  if (props.result?.full_fixed_code) {
    await navigator.clipboard.writeText(props.result.full_fixed_code)
    ElMessage.success('已复制修改后的代码')
  }
}
</script>

<style scoped>
.result-panel {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  border: 1px solid var(--border-light);
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* ========== 空状态 ========== */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 4px;
}
.empty-illustration {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--brand-gradient-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}
.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
}
.empty-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

/* ========== 统计卡片 ========== */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  padding: 16px;
  border-bottom: 1px solid var(--border-light);
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--bg-subtle);
  border: 1px solid var(--border-light);
  transition: all 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}
.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--text-muted);
  background: #fff;
  border: 1px solid var(--border-light);
}
.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}
.stat-label {
  font-size: 11px;
  color: var(--text-muted);
}
/* 彩色变体 */
.stat-issues.active .stat-icon { background: #fef3c7; color: #f59e0b; border-color: #fde68a; }
.stat-issues.active .stat-value { color: #d97706; }
.stat-error .stat-icon { background: #fee2e2; color: #ef4444; border-color: #fecaca; }
.stat-error .stat-value { color: #dc2626; }
.stat-warning .stat-icon { background: #fef3c7; color: #f59e0b; border-color: #fde68a; }
.stat-warning .stat-value { color: #d97706; }
.stat-suggestion .stat-icon { background: #dbeafe; color: #3b82f6; border-color: #bfdbfe; }
.stat-suggestion .stat-value { color: #2563eb; }

/* ========== 结果主体 ========== */
.result-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

.issue-list {
  width: 260px;
  border-right: 1px solid var(--border-light);
  overflow-y: auto;
  flex-shrink: 0;
}
.issue-list-header {
  padding: 12px 16px;
  font-weight: 700;
  font-size: 13px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
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
.no-issues-sub {
  font-size: 12px !important;
  color: var(--text-muted) !important;
  font-weight: 400 !important;
}

.issue-group {
  border-bottom: 1px solid var(--border-light);
}
.group-title {
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.3px;
}
.group-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.group-count {
  margin-left: auto;
  font-size: 11px;
  background: #fff;
  padding: 1px 8px;
  border-radius: 10px;
  border: 1px solid var(--border-light);
}
.group-title.error { background: #fef2f2; color: #dc2626; }
.group-title.error .group-dot { background: #ef4444; }
.group-title.warning { background: #fffbeb; color: #d97706; }
.group-title.warning .group-dot { background: #f59e0b; }
.group-title.suggestion { background: #eff6ff; color: #2563eb; }
.group-title.suggestion .group-dot { background: #3b82f6; }

.issue-item {
  padding: 10px 16px;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}
.issue-item:hover {
  background: var(--bg-hover);
}
.issue-item.active {
  background: #eef2ff;
  border-left-color: var(--brand-primary);
}
.issue-header {
  display: flex;
  gap: 6px;
  margin-bottom: 4px;
}
.issue-title {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
}

/* ========== 右侧面板 ========== */
.right-panel {
  flex: 1;
  padding: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.detail-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.right-panel :deep(.el-tabs--border-card) {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border-light) !important;
  box-shadow: none !important;
}
.right-panel :deep(.el-tabs--border-card > .el-tabs__header) {
  background: var(--bg-subtle) !important;
}
.right-panel :deep(.el-tabs--border-card > .el-tabs__content) {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

.diff-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}
.issue-title-text {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 15px;
}

.diff-desc,
.diff-suggestion {
  margin-bottom: 12px;
  line-height: 1.6;
  font-size: 13px;
  color: var(--text-secondary);
}
.diff-desc strong,
.diff-suggestion strong {
  display: block;
  color: var(--text-primary);
  font-size: 13px;
  margin-bottom: 4px;
}
.diff-desc p,
.diff-suggestion p {
  margin: 0;
}

.diff-code {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
.code-pane {
  flex: 1;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.code-pane-fixed {
  border-color: #bbf7d0;
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
.code-pane pre {
  margin: 0;
  padding: 12px;
  background: #1e1e2e;
  color: #cdd6f4;
  font-size: 13px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  overflow-x: auto;
  max-height: 300px;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.5;
}

.diff-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 200px;
  color: var(--text-muted);
  font-size: 14px;
}

.fixed-code-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.fixed-actions {
  display: flex;
  justify-content: flex-end;
}
.fixed-code {
  margin: 0;
  padding: 14px;
  background: #1e1e2e;
  color: #cdd6f4;
  font-size: 13px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  max-height: 500px;
  overflow: auto;
  border-radius: var(--radius-sm);
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 1024px) {
  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .result-body {
    flex-direction: column;
  }
  .issue-list {
    width: 100%;
    max-height: 250px;
    border-right: none;
    border-bottom: 1px solid var(--border-light);
  }
  .diff-code {
    flex-direction: column;
  }
}
</style>
