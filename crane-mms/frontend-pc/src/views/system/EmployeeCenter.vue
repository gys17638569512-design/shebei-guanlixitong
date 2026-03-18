<template>
  <div class="employee-center">
    <div class="page-header">
      <div class="title-group">
        <h1 class="page-title">员工账号中心</h1>
        <p class="page-subtitle">平台管理员统一创建与维护本公司员工账号，支持密码管理、微信绑定与手机号关联</p>
      </div>
      <div class="header-actions">
        <el-button @click="loadData">刷新数据</el-button>
        <el-button type="primary" @click="openCreateDialog">新增员工账号</el-button>
      </div>
    </div>

    <div class="summary-grid">
      <el-card v-for="item in summaryCards" :key="item.label" shadow="never" class="summary-card">
        <div class="summary-label">{{ item.label }}</div>
        <div class="summary-value">{{ item.value }}</div>
        <div class="summary-hint">{{ item.hint }}</div>
      </el-card>
    </div>

    <el-card class="table-card" shadow="never">
      <div class="toolbar">
        <el-input v-model="searchQuery" placeholder="搜索姓名、账号、部门" clearable style="width: 280px">
          <template #prefix>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#999">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
          </template>
        </el-input>
        <el-select v-model="roleFilter" placeholder="全部角色" clearable style="width: 160px">
          <el-option label="系统管理员" value="ADMIN" />
          <el-option label="业务经理" value="MANAGER" />
          <el-option label="技术工程师" value="TECH" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 160px">
          <el-option label="启用" value="ACTIVE" />
          <el-option label="停用" value="INACTIVE" />
        </el-select>
      </div>

      <el-table :data="filteredAccounts" v-loading="loading" style="width: 100%" border>
        <el-table-column width="60" align="center">
          <template #default="{ row }">
            <div class="avatar-circle">{{ (row.name || row.username || '?').charAt(0) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="username" label="账号" min-width="140">
          <template #default="{ row }">
            <code class="code-cell">{{ row.username }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" min-width="130" />
        <el-table-column prop="job_title" label="岗位" min-width="130" />
        <el-table-column prop="phone" label="手机号" min-width="130" />
        <el-table-column label="微信绑定" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.wechat_bound ? 'success' : 'info'" effect="light">
              {{ row.wechat_bound ? '已绑定' : '未绑定' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="账号状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'danger'" effect="light">
              {{ row.status === 'ACTIVE' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" min-width="150" />
        <el-table-column label="操作" width="280" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button link type="warning" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button
              link
              :type="row.status === 'ACTIVE' ? 'danger' : 'success'"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 'ACTIVE' ? '停用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑员工账号' : '新增员工账号'" width="560px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="登录账号" prop="username">
              <el-input v-model="form.username" placeholder="请输入登录账号" :disabled="isEdit" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="部门" prop="department">
              <el-input v-model="form.department" placeholder="如：平台运营部" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="岗位" prop="job_title">
              <el-input v-model="form.job_title" placeholder="如：系统管理员" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色" prop="role">
              <el-select v-model="form.role" style="width: 100%">
                <el-option label="系统管理员" value="ADMIN" />
                <el-option label="业务经理" value="MANAGER" />
                <el-option label="技术工程师" value="TECH" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="微信绑定" prop="wechat_bound">
              <el-switch v-model="form.wechat_bound" active-text="已绑定" inactive-text="未绑定" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="账号状态" prop="status">
              <el-switch v-model="form.statusEnabled" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="isEdit ? '重置登录密码（留空则不改）' : '初始登录密码'" prop="password">
          <el-input v-model="form.password" type="password" show-password :placeholder="isEdit ? '留空不修改密码' : '请设置初始密码'" />
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  fetchEmployeeAccounts,
  addEmployeeAccount,
  editEmployeeAccount,
  refreshEmployeePassword,
  changeEmployeeStatus
} from '@/api/system'

const loading = ref(false)
const submitLoading = ref(false)
const accounts = ref([])
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  username: '',
  department: '',
  job_title: '',
  phone: '',
  role: 'TECH',
  wechat_bound: false,
  statusEnabled: true,
  password: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const filteredAccounts = computed(() => {
  return accounts.value.filter((item) => {
    const keyword = searchQuery.value.trim().toLowerCase()
    const keywordMatched = !keyword || [item.name, item.username, item.department, item.job_title]
      .filter(Boolean)
      .some((value) => value.toLowerCase().includes(keyword))
    const roleMatched = !roleFilter.value || item.role === roleFilter.value
    const statusMatched = !statusFilter.value || item.status === statusFilter.value
    return keywordMatched && roleMatched && statusMatched
  })
})

const summaryCards = computed(() => {
  const total = accounts.value.length
  const active = accounts.value.filter((item) => item.status === 'ACTIVE').length
  const wechatBound = accounts.value.filter((item) => item.wechat_bound).length
  const needReset = accounts.value.filter((item) => item.must_change_password).length

  return [
    { label: '员工总数', value: total, hint: '平台侧全部员工账号' },
    { label: '启用账号', value: active, hint: '可正常登录使用' },
    { label: '微信绑定', value: wechatBound, hint: '可接收微信提醒' },
    { label: '待改密码', value: needReset, hint: '首次登录或重置后需处理' }
  ]
})

const syncFormToRow = (row) => {
  form.name = row?.name || ''
  form.username = row?.username || ''
  form.department = row?.department || ''
  form.job_title = row?.job_title || ''
  form.phone = row?.phone || ''
  form.role = row?.role || 'TECH'
  form.wechat_bound = Boolean(row?.wechat_bound)
  form.statusEnabled = (row?.status || 'ACTIVE') === 'ACTIVE'
  form.password = ''
}

const loadData = async () => {
  loading.value = true
  try {
    accounts.value = await fetchEmployeeAccounts()
  } catch (error) {
    ElMessage.error(error.message || '加载员工账号失败')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  editingId.value = null
  syncFormToRow()
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  editingId.value = row.id
  syncFormToRow(row)
  dialogVisible.value = true
}

const handleResetPassword = async (row) => {
  try {
    await ElMessageBox.confirm(`确认重置员工「${row.name}」的登录密码吗？`, '重置密码', {
      type: 'warning',
      confirmButtonText: '确认重置',
      cancelButtonText: '取消'
    })
    await refreshEmployeePassword(row.id, '123456')
    ElMessage.success('已重置密码，员工下次登录需改密')
    await loadData()
  } catch (error) {}
}

const handleToggleStatus = async (row) => {
  const nextStatus = row.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
  const actionText = nextStatus === 'ACTIVE' ? '启用' : '停用'
  try {
    await ElMessageBox.confirm(`确认${actionText}员工「${row.name}」账号吗？`, '状态变更', {
      type: 'warning',
      confirmButtonText: `确认${actionText}`,
      cancelButtonText: '取消'
    })
    await changeEmployeeStatus(row.id, nextStatus)
    ElMessage.success(`账号已${actionText}`)
    await loadData()
  } catch (error) {}
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const payload = {
        name: form.name,
        username: form.username,
        department: form.department,
        job_title: form.job_title,
        phone: form.phone,
        role: form.role,
        wechat_bound: form.wechat_bound,
        status: form.statusEnabled ? 'ACTIVE' : 'INACTIVE'
      }

      if (isEdit.value) {
        if (form.password) payload.password = form.password
        await editEmployeeAccount(editingId.value, payload)
        ElMessage.success('员工账号已更新')
      } else {
        payload.password = form.password || 'Admin@2024'
        await addEmployeeAccount(payload)
        ElMessage.success('员工账号已创建')
      }

      dialogVisible.value = false
      await loadData()
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      submitLoading.value = false
    }
  })
}

onMounted(loadData)
</script>

<style scoped>
.employee-center {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--color-text-primary);
}

.page-subtitle {
  margin: 0;
  color: var(--color-text-secondary);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  border-radius: var(--radius-lg);
}

.summary-label {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.summary-value {
  margin-top: 8px;
  font-size: 30px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.summary-hint {
  margin-top: 6px;
  color: var(--color-text-secondary);
  font-size: 12px;
}

.table-card {
  border-radius: var(--radius-lg);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e6f4ff, #bae0ff);
  color: var(--color-primary);
  font-weight: 700;
}

.code-cell {
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--color-bg-page);
  font-size: 12px;
}
</style>
