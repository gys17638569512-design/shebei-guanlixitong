<template>
  <div class="user-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">人员管理</h1>
        <p class="page-subtitle">管理系统用户账号及权限分配</p>
      </div>
      <el-button type="primary" size="large" @click="handleAdd">
        <span class="btn-icon">＋</span> 新增员工
      </el-button>
    </div>

    <!-- 人员 卡片区 -->
    <div class="table-card">
      <div class="toolbar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索账号或姓名…"
          clearable
          style="width: 260px"
        >
          <template #prefix>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#999">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
          </template>
        </el-input>
        <span class="total-hint">共 {{ filteredUsers.length }} 名员工</span>
      </div>

      <el-table :data="filteredUsers" v-loading="loading" style="width: 100%">
        <el-table-column width="60" align="center">
          <template #default="{ row }">
            <div class="user-mini-avatar">{{ (row.name || row.username || '?').charAt(0) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="真实姓名" width="130">
          <template #default="{ row }">
            <span class="user-name-cell">{{ row.name || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="登录账号" width="150">
          <template #default="{ row }">
            <code class="code-cell">{{ row.username }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="系统角色" width="140">
          <template #default="{ row }">
            <span class="role-badge" :class="'role-' + row.role">
              {{ getRoleName(row.role) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-divider direction="vertical" />
            <el-button
              size="small"
              type="danger"
              link
              @click="handleDelete(row)"
              :disabled="row.id === 1"
            >
              {{ row.id === 1 ? '受保护' : '注销' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && filteredUsers.length === 0" class="empty-state">
        <div class="empty-icon">👤</div>
        <div class="empty-text">暂无员工数据</div>
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑员工' : '新增员工'"
      width="460px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="name">
              <el-input v-model="form.name" placeholder="员工姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="登录账号" prop="username">
              <el-input v-model="form.username" placeholder="登录用账号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="系统角色" prop="role">
          <el-select v-model="form.role" style="width:100%">
            <el-option label="🔧 技术工程师" value="TECH" />
            <el-option label="📊 业务经理"   value="MANAGER" />
            <el-option label="⚙️ 系统管理员"  value="ADMIN" />
          </el-select>
        </el-form-item>
        <el-form-item :label="isEdit ? '重置密码（不改请留空）' : '初始密码'" :prop="isEdit ? '' : 'password'">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="isEdit ? '留空则不修改密码' : '请设置初始密码'"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">
          {{ isEdit ? '保存修改' : '创建账号' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, deleteUser } from '@/api/user'

const loading = ref(false)
const users = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentEditId = ref(null)

const form = ref({ name: '', username: '', role: 'TECH', password: '' })

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [{ required: true, message: '请设置初始密码', trigger: 'blur' }],
}

const getRoleName = (role) => {
  const m = { ADMIN: '管理员', MANAGER: '业务经理', TECH: '技术工程师' }
  return m[role] || role
}

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u =>
    (u.name || '').toLowerCase().includes(q) ||
    (u.username || '').toLowerCase().includes(q)
  )
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUsers({ skip: 0, limit: 1000 })
    users.value = res?.items || res || []
  } catch { users.value = [] }
  finally { loading.value = false }
}

const handleAdd = () => {
  isEdit.value = false
  form.value = { name: '', username: '', role: 'TECH', password: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentEditId.value = row.id
  form.value = { name: row.name, username: row.username, role: row.role, password: '' }
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要注销员工「${row.name}」(${row.username}) 吗？此操作不可撤销。`,
    '危险操作确认', { type: 'warning', confirmButtonText: '确认注销', cancelButtonText: '取消' }
  ).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success('账号已注销')
      loadData()
    } catch {}
  }).catch(() => {})
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const payload = { ...form.value }
        if (isEdit.value && !payload.password) delete payload.password
        if (isEdit.value) {
          await updateUser(currentEditId.value, payload)
          ElMessage.success('员工资料已更新')
        } else {
          await createUser(payload)
          ElMessage.success('✅ 员工账号已创建')
        }
        dialogVisible.value = false
        loadData()
      } catch {} finally { submitLoading.value = false }
    }
  })
}

onMounted(loadData)
</script>

<style scoped>
.user-list { padding: 0; }

.table-card {
  background: #fff;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--color-border-light);
}
.total-hint { font-size: 13px; color: var(--color-text-secondary); }

.user-mini-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e6f4ff, #bae0ff);
  color: var(--color-primary);
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto;
}
.user-name-cell { font-weight: 600; color: var(--color-text-primary); }
.code-cell {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  background: var(--color-bg-page);
  padding: 2px 7px;
  border-radius: var(--radius-xs);
  color: var(--color-text-regular);
}

.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}
.role-ADMIN   { background: #fff1f0; color: #cf1322; }
.role-MANAGER { background: #fffbe6; color: #d48806; }
.role-TECH    { background: #f6ffed; color: #389e0d; }

.btn-icon { margin-right: 4px; font-weight: 300; }
.empty-state { text-align: center; padding: 48px 20px; }
.empty-icon { font-size: 40px; margin-bottom: 10px; }
.empty-text { font-size: 15px; font-weight: 600; color: var(--color-text-secondary); }
</style>
