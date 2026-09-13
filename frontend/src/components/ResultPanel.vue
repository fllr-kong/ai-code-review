<template>
  <div class="result-panel">
    <div v-if="!result" class="empty-state">
      <el-empty description="提交代码审查后，结果将在此展示" />
    </div>
    <template v-else>
      <div class="summary-bar">
        <div class="summary-item">
          <span class="label">代码行数</span>
          <span class="value">{{ result.summary?.total_lines || 0 }}</span>
        </div>
        <div class="summary-item">
          <span class="label">问题总数</span>
          <span class="value" :class="{ 'has-issues': result.issues?.length > 0 }">
            {{ result.summary?.issues_count || result.issues?.length || 0 }}
          </span>
        </div>
        <div class="summary-item errors">
          <span class="label">错误</span>
          <span class="value">{{ countBySeverity('error') }}</span>
        </div>
        <div class="summary-item warnings">
          <span class="label">警告</span>
          <span class="value">{{ countBySeverity('warning') }}</span>
        </div>
        <div class="summary-item suggestions">
          <span class="label">建议</span>
          <span class="value">{{ countBySeverity('suggestion') }}</span>
        </div>
      </div>

      <div class="result-body">
        <div class="issue-list">
          <div class="issue-list-header">发现的问题</div>
          <div v-if="!result.issues || result.issues.length === 0" class="no-issues">
            <el-icon :size="40" color="#67C23A"><CircleCheck /></el-icon>
            <p>代码质量良好，未发现问题！</p>
          </div>
          <template v-else>
            <div v-for="(group, key) in groupedIssues" :key="key" class="issue-group">
              <div class="group-title" :class="key">
                {{ severityLabel(key) }} ({{ group.length }})
              </div>
              <div
                v-for="(issue, idx) in group"
                :key="idx"
                class="issue-item"
                :class="{ active: selectedIssue === issue }"
                @click="selectIssue(issue)"
              >
                <div class="issue-header">
                  <el-tag :type="severityTagType(issue.severity)" size="small" effect="dark">
                    L{{ issue.line }}
                  </el-tag>
                  <el-tag size="small">{{ issue.category }}</el-tag>
                </div>
                <div class="issue-title">{{ issue.title }}</div>
              </div>
            </div>
          </template>
        </div>

        <div class="right-panel">
          <el-tabs v-model="rightTab" type="border-card">
            <el-tab-pane label="问题详情" name="issue">
              <div v-if="selectedIssue" class="diff-content">
                <div class="diff-header">
                  <el-tag :type="severityTagType(selectedIssue.severity)" effect="dark">
                    {{ severityLabel(selectedIssue.severity) }}
                  </el-tag>
                  <el-tag style="margin-left: 8px">{{ selectedIssue.category }}</el-tag>
                  <span class="issue-title-text">{{ selectedIssue.title }}</span>
                </div>
                <div class="diff-desc">
                  <strong>问题描述：</strong>{{ selectedIssue.description }}
                </div>
                <div class="diff-suggestion">
                  <strong>修改建议：</strong>{{ selectedIssue.suggestion }}
                </div>
                <div class="diff-code">
                  <div class="code-pane">
                    <div class="pane-label">原代码</div>
                    <pre><code>{{ selectedIssue.original_code }}</code></pre>
                  </div>
                  <div class="code-pane">
                    <div class="pane-label">修改后</div>
                    <pre><code>{{ selectedIssue.fixed_code }}</code></pre>
                  </div>
                </div>
              </div>
              <div v-else class="diff-empty">
                <p>点击左侧问题查看详情</p>
              </div>
            </el-tab-pane>

            <el-tab-pane label="修改后代码" name="fixed">
              <div v-if="result.full_fixed_code" class="fixed-code-wrap">
                <div class="fixed-actions">
                  <el-button type="primary" size="small" @click="copyFixedCode">
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
import { CopyDocument, CircleCheck } from '@element-plus/icons-vue'

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
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.empty-state {
  padding: 60px 0;
}
.summary-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  border-bottom: 1px solid #ebeef5;
}
.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 70px;
}
.summary-item .label {
  font-size: 12px;
  color: #909399;
}
.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
.summary-item .value.has-issues {
  color: #E6A23C;
}
.summary-item.errors .value { color: #F56C6C; }
.summary-item.warnings .value { color: #E6A23C; }
.summary-item.suggestions .value { color: #409EFF; }
.result-body {
  display: flex;
  min-height: 500px;
}
.issue-list {
  width: 300px;
  border-right: 1px solid #ebeef5;
  overflow-y: auto;
}
.issue-list-header {
  padding: 12px 16px;
  font-weight: bold;
  border-bottom: 1px solid #ebeef5;
  background: #fafbfc;
}
.no-issues {
  text-align: center;
  padding: 40px 20px;
  color: #67C23A;
}
.no-issues p {
  margin-top: 12px;
  color: #606266;
}
.issue-group {
  border-bottom: 1px solid #f0f2f5;
}
.group-title {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
}
.group-title.error { background: #fef0f0; color: #F56C6C; }
.group-title.warning { background: #fdf6ec; color: #E6A23C; }
.group-title.suggestion { background: #ecf5ff; color: #409EFF; }
.issue-item {
  padding: 10px 16px;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}
.issue-item:hover {
  background: #f5f7fa;
}
.issue-item.active {
  background: #ecf5ff;
  border-left-color: #409EFF;
}
.issue-header {
  display: flex;
  gap: 6px;
  margin-bottom: 4px;
}
.issue-title {
  font-size: 13px;
  color: #303133;
  line-height: 1.4;
}
.right-panel {
  flex: 1;
  padding: 12px;
  overflow: hidden;
}
.right-panel :deep(.el-tabs--border-card > .el-tabs__header) {
  background: #fafbfc;
}
.right-panel :deep(.el-tabs--border-card > .el-tabs__content) {
  padding: 16px;
  overflow-y: auto;
  max-height: 480px;
}
.diff-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.issue-title-text {
  margin-left: 8px;
  font-weight: bold;
  color: #303133;
  font-size: 15px;
}
.diff-desc, .diff-suggestion {
  margin-bottom: 8px;
  line-height: 1.6;
}
.diff-desc strong, .diff-suggestion strong {
  color: #606266;
}
.diff-code {
  display: flex;
  gap: 12px;
  margin: 16px 0;
}
.code-pane {
  flex: 1;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}
.pane-label {
  padding: 6px 12px;
  background: #f5f7fa;
  font-size: 12px;
  color: #909399;
  border-bottom: 1px solid #ebeef5;
}
.code-pane pre {
  margin: 0;
  padding: 12px;
  background: #1e1e1e;
  color: #d4d4d4;
  font-size: 13px;
  overflow-x: auto;
  max-height: 300px;
  white-space: pre-wrap;
  word-break: break-all;
}
.diff-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  color: #909399;
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
  padding: 12px;
  background: #1e1e1e;
  color: #d4d4d4;
  font-size: 13px;
  max-height: 500px;
  overflow: auto;
  border-radius: 4px;
}
</style>
