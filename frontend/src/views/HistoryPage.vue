<template>
  <div class="history-page">
    <div class="page-hero">
      <div class="hero-left">
        <h1 class="page-title">审查历史记录</h1>
        <p class="page-subtitle">查看你所有提交过的代码审查记录</p>
      </div>
      <el-button type="primary" :icon="Delete" round size="default"
        :disabled="selectedIds.length === 0" @click="batchDelete">
        批量删除<span v-if="selectedIds.length > 0"> ({{ selectedIds.length }})</span>
      </el-button>
    </div>

    <el-card class="history-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="history"
        @selection-change="handleSelectionChange"
        :header-cell-style="{ background: 'var(--bg-subtle)' }"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="filename" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-cell">
              <el-icon :size="16" color="var(--brand-primary)"><Document /></el-icon>
              <span class="file-name">{{ row.filename }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="language" label="语言" width="120">
          <template #default="{ row }">
            <el-tag round effect="plain">{{ row.language }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="issues_count" label="问题数" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.issues_count > 0" type="warning" round>{{ row.issues_count }}</el-tag>
            <el-tag v-else type="success" round>0</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="审查时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link :icon="View" @click="viewDetail(row.id)">查看</el-button>
            <el-button type="success" size="small" link :icon="Share" @click="openShare(row.id)">分享</el-button>
            <el-popconfirm title="确认删除？" @confirm="deleteRecord(row.id)">
              <template #reference>
                <el-button type="danger" size="small" link :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && history.length === 0" class="empty-wrap">
        <el-icon :size="40" color="#cbd5e1"><FolderOpened /></el-icon>
        <p class="empty-title">暂无审查记录</p>
        <p class="empty-desc">去提交你的第一份代码吧</p>
        <el-button type="primary" round @click="$router.push('/')">开始审查</el-button>
      </div>
    </el-card>

    <ShareDialog v-if="currentShareId" v-model="shareVisible" :review-id="currentShareId" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Share, Delete, View, FolderOpened } from '@element-plus/icons-vue'
import { getHistory, deleteHistory } from '../api'
import ShareDialog from '../components/ShareDialog.vue'

const router = useRouter()
const loading = ref(false)
const history = ref([])
const selectedIds = ref([])
const shareVisible = ref(false)
const currentShareId = ref('')

onMounted(loadHistory)

async function loadHistory() {
  loading.value = true
  try {
    const res = await getHistory()
    history.value = res.data.history
  } catch (e) {
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

function handleSelectionChange(rows) {
  selectedIds.value = rows.map(r => r.id)
}

function viewDetail(id) {
  router.push(`/history/${id}`)
}

function openShare(id) {
  currentShareId.value = id
  shareVisible.value = true
}

async function deleteRecord(id) {
  try {
    await deleteHistory(id)
    ElMessage.success('删除成功')
    loadHistory()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

async function batchDelete() {
  try {
    for (const id of selectedIds.value) {
      await deleteHistory(id)
    }
    ElMessage.success('批量删除成功')
    loadHistory()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.history-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
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
}

.history-card {
  border-radius: var(--radius-lg) !important;
}

.file-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.file-name {
  font-weight: 500;
  color: var(--text-primary);
}

.empty-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 48px 20px;
}
.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 8px 0 0;
}
.empty-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 8px;
}

@media (max-width: 768px) {
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
