<template>
  <el-dialog
    :model-value="modelValue"
    width="540px"
    :close-on-click-modal="false"
    class="share-dialog"
    @update:model-value="$emit('update:modelValue', $event)"
    @open="handleOpen"
    @closed="handleClosed"
  >
    <template #header>
      <div class="dialog-header">
        <div class="dialog-icon">
          <el-icon :size="20"><Share /></el-icon>
        </div>
        <div>
          <h3 class="dialog-title">分享审查结果</h3>
          <p class="dialog-sub">生成链接后任何人可免登录查看</p>
        </div>
      </div>
    </template>

    <div v-loading="loading" class="share-body">
      <template v-if="code">
        <el-alert
          title="任何拿到链接或分享码的人都可以免登录查看这份审查结果，请确认不含敏感代码。"
          type="warning"
          :closable="false"
          show-icon
          class="share-warning"
        />

        <div class="field">
          <div class="field-label">分享码</div>
          <div class="code-row">
            <div class="share-code">{{ code }}</div>
            <el-button type="primary" plain round @click="copyCode">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
          </div>
        </div>

        <div class="field">
          <div class="field-label">分享链接</div>
          <div class="link-row">
            <el-input :model-value="shareUrl" readonly class="link-input" />
            <el-button type="primary" round @click="copyLink">
              复制链接
            </el-button>
          </div>
        </div>

        <p v-if="createdAt" class="share-time">
          <el-icon :size="12"><Clock /></el-icon>
          分享时间：{{ createdAt }}
        </p>
      </template>
    </div>

    <template #footer>
      <el-popconfirm
        title="取消分享后，原链接和分享码将立即失效，确定？"
        @confirm="handleRevoke"
      >
        <template #reference>
          <el-button type="danger" plain round :loading="loading" :disabled="!code">
            取消分享
          </el-button>
        </template>
      </el-popconfirm>
      <el-button round @click="$emit('update:modelValue', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Share, CopyDocument, Clock } from '@element-plus/icons-vue'
import { createShare, getShareStatus, revokeShare } from '../api'

const props = defineProps({
  modelValue: Boolean,
  reviewId: { type: String, required: true }
})
const emit = defineEmits(['update:modelValue', 'revoked'])

const loading = ref(false)
const code = ref('')
const createdAt = ref('')

const shareUrl = computed(() =>
  code.value ? `${window.location.origin}/share/${code.value}` : ''
)

async function handleOpen() {
  loading.value = true
  code.value = ''
  try {
    const res = await getShareStatus(props.reviewId)
    if (res.data.shared) {
      code.value = res.data.code
      createdAt.value = res.data.created_at
    } else {
      const created = await createShare(props.reviewId)
      code.value = created.data.code
      createdAt.value = created.data.created_at
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '创建分享失败')
    emit('update:modelValue', false)
  } finally {
    loading.value = false
  }
}

function handleClosed() {
  code.value = ''
  createdAt.value = ''
}

async function copyText(text, successMsg) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(successMsg)
  } catch (e) {
    ElMessage.error('复制失败，请手动选择复制')
  }
}

function copyCode() {
  copyText(code.value, '分享码已复制')
}

function copyLink() {
  copyText(shareUrl.value, '分享链接已复制')
}

async function handleRevoke() {
  try {
    await revokeShare(props.reviewId)
    ElMessage.success('已取消分享')
    emit('revoked')
    emit('update:modelValue', false)
  } catch (e) {
    ElMessage.error('取消分享失败')
  }
}
</script>

<style scoped>
.dialog-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.dialog-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--brand-gradient-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--brand-primary);
  flex-shrink: 0;
}
.dialog-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}
.dialog-sub {
  font-size: 12px;
  color: var(--text-muted);
  margin: 2px 0 0;
}

.share-body {
  min-height: 140px;
}
.share-warning {
  margin-bottom: 16px;
  border-radius: var(--radius-sm);
}

.field {
  margin-bottom: 18px;
}
.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.code-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.share-code {
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 4px;
  color: var(--brand-primary);
  background: var(--brand-gradient-soft);
  padding: 8px 20px;
  border-radius: var(--radius-sm);
  border: 1px solid #c7d2fe;
  flex: 1;
  text-align: center;
}

.link-row {
  display: flex;
  gap: 10px;
  align-items: center;
}
.link-input {
  flex: 1;
}

.share-time {
  font-size: 12px;
  color: var(--text-muted);
  margin: 4px 0 0;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
