<template>
  <div class="audit-log-container">
    <div class="page-header">
      <div class="title-group">
        <h1 class="page-title">系统安全审计</h1>
        <p class="page-subtitle">追踪并监控全平台的敏感操作记录，确保业务合规与安全</p>
      </div>
    </div>

    <!-- 筛选区域 -->
    <el-card v-if="canUseFilters" class="filter-card mb-24">
      <el-form :inline="true" :model="filters" size="default">
        <el-form-item label="操作动作">
          <el-select v-model="filters.action" placeholder="全部" clearable style="width: 120px">
            <el-option label="创建 (CREATE)" value="CREATE" />
            <el-option label="修改 (UPDATE)" value="UPDATE" />
            <el-option label="删除 (DELETE)" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标表名">
          <el-input v-model="filters.table_name" placeholder="输入表名模糊查询" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;margin-right:4px">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            查询
          </el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card v-if="canViewLogs" class="table-card">
      <el-table :data="logs" v-loading="loading" style="width: 100%" border stripe>
        <el-table-column prop="log_id" label="ID" width="70" align="center" />
        <el-table-column prop="created_at" label="操作时间" width="180" align="center" />
        <el-table-column prop="user_name" label="操作人" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.user_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="动作" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)" size="small" effect="dark">
              {{ row.action }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="table_name" label="影响对象(表)" width="150" align="center" />
        <el-table-column prop="record_id" label="记录ID" width="90" align="center" />
        <el-table-column prop="new_value" label="变更详细内容">
          <template #default="{ row }">
            <div class="json-preview" :class="{ disabled: !canViewDetail }" @click="showDetail(row.new_value)">
              {{ row.new_value || '无详细内容' }}
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="变更快照详情" width="500px">
      <pre class="json-content">{{ formattedDetail }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getAuditLogs } from '@/api/audit'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { SETTINGS_PERMISSIONS } from '@/constants/permissions'

const authStore = useAuthStore()
const canUseFilters = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.AUDIT_FILTERS_USE))
const canViewLogs = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.AUDIT_MODULE_LOGS))
const canViewDetail = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.AUDIT_MODULE_DETAIL))

const loading = ref(false)
const logs = ref([])
const filters = ref({
  action: '',
  table_name: ''
})

const detailVisible = ref(false)
const formattedDetail = ref('')

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await getAuditLogs(filters.value)
    logs.value = res || []
  } catch (err) {
    ElMessage.error('加载审计日志失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchLogs()
}

const resetFilters = () => {
  filters.value = { action: '', table_name: '' }
  fetchLogs()
}

const getActionType = (action) => {
  const map = { CREATE: 'success', UPDATE: 'warning', DELETE: 'danger' }
  return map[action] || 'info'
}

const showDetail = (val) => {
  if (!canViewDetail.value) return
  if (!val) return
  try {
    // 尝试解析并格式化 JSON 字符串
    const obj = typeof val === 'string' ? JSON.parse(val) : val
    formattedDetail.value = JSON.stringify(obj, null, 2)
  } catch (e) {
    formattedDetail.value = val
  }
  detailVisible.value = true
}

onMounted(fetchLogs)
</script>

<style scoped>
.audit-log-container {
  padding: 0;
}

.title-group {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.filter-card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.table-card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.json-preview {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: monospace;
  font-size: 12px;
  color: var(--color-text-regular);
  cursor: pointer;
}

.json-preview:hover {
  color: var(--color-primary);
  text-decoration: underline;
}

.json-preview.disabled {
  cursor: default;
  color: var(--color-text-placeholder);
  text-decoration: none;
}

.json-content {
  background: #f8f9fa;
  padding: 15px;
  border-radius: var(--radius-sm);
  font-family: monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}

.mb-24 {
  margin-bottom: 24px;
}
</style>
