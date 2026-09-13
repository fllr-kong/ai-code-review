<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审查历史记录</span>
          <el-button type="danger" size="small" :disabled="selectedIds.length === 0" @click="batchDelete">
            批量删除
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="history"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="filename" label="文件名" min-width="150">
          <template #default="{ row }">
            <el-icon><Document /></el-icon>
            <span>{{ row.filename }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="language" label="语言" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.language }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="issues_count" label="问题数" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.issues_count > 0" type="warning">{{ row.issues_count }}</el-tag>
            <el-tag v-else type="success">0</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="审查时间" width="180" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewDetail(row.id)">查看</el-button>
            <el-popconfirm title="确认删除？" @confirm="deleteRecord(row.id)">
              <template #reference>
                <el-button type="danger" size="small" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && history.length === 0" description="暂无审查记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { getHistory, deleteHistory } from '../api'

const router = useRouter()
const loading = ref(false)
const history = ref([])
const selectedIds = ref([])

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
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}
</style>
