<template>
  <div class="user-list">
    <el-card shadow="never">
      <div class="header-tools" style="margin-bottom: 20px; display: flex; justify-content: space-between;">
        <div class="left-tools">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索账号/姓名" 
            clearable 
            style="width: 250px; margin-right: 15px;"
            :prefix-icon="Search"
          />
        </div>
        <el-button type="primary" :icon="Plus" @click="handleAdd">记录新员工</el-button>
      </div>

      <el-table 
        :data="filteredUsers" 
        style="width: 100%" 
        v-loading="loading" 
        border 
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="username" label="初始账号" width="150" />
        <el-table-column prop="name" label="真实姓名" width="150" />
        <el-table-column prop="role" label="系统角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">{{ getRoleName(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleEdit(row)">编辑/改密</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)" :disabled="row.id === 1">注销辞退</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- User Form Dialog -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑员工资料' : '录入新员工'"
      width="500px"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
      >
        <el-form-item label="真实姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入员工真实姓名" />
        </el-form-item>
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="form.username" placeholder="请输入系统登录账号" />
        </el-form-item>
        <el-form-item label="系统权限" prop="role">
          <el-select v-model="form.role" placeholder="请选择分配的系统角色" style="width: 100%">
            <el-option label="技术工程师" value="TECH" />
            <el-option label="业务经理" value="MANAGER" />
            <el-option label="系统管理员" value="ADMIN" />
          </el-select>
        </el-form-item>
        <el-form-item :label="isEdit ? '重置密码' : '初始密码'" :prop="isEdit ? '' : 'password'">
          <el-input 
            v-model="form.password" 
            type="password" 
            show-password 
            :placeholder="isEdit ? '不修改请留空' : '请输入初始密码'" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">提交保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, deleteUser } from '@/api/user'

const loading = ref(false)
const users = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const form = ref({
  name: '',
  username: '',
  role: 'TECH',
  password: ''
})

const currentUserEditingId = ref(null)

const rules = {
  name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [{ required: true, message: '新员工必须设置初始密码', trigger: 'blur' }]
}

const getRoleName = (role) => {
  const map = {
    'ADMIN': '系统管理员',
    'MANAGER': '业务经理',
    'TECH': '技术工程师'
  }
  return map[role] || role
}

const getRoleTagType = (role) => {
  const map = {
    'ADMIN': 'danger',
    'MANAGER': 'warning',
    'TECH': 'success'
  }
  return map[role] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUsers({ skip: 0, limit: 1000 })
    users.value = res.items || []
  } catch (error) {
    console.error('Failed to load users', error)
  } finally {
    loading.value = false
  }
}

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(u => 
    u.name.toLowerCase().includes(query) || 
    u.username.toLowerCase().includes(query)
  )
})

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    name: '',
    username: '',
    role: 'TECH',
    password: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentUserEditingId.value = row.id
  form.value = {
    name: row.name,
    username: row.username,
    role: row.role,
    password: '' // 不显示原密码
  }
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要永久注销员工 ${row.name} (${row.username}) 吗？此操作无法撤销。`,
    '高危警告',
    {
      confirmButtonText: '确定注销',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success('账号已永久注销')
      loadData()
    } catch (error) {
    }
  }).catch(() => {})
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const payload = { ...form.value }
        if (isEdit.value && !payload.password) {
          delete payload.password // 没有填密码就不修改
        }
        
        if (isEdit.value) {
          await updateUser(currentUserEditingId.value, payload)
          ElMessage.success('员工资料更新成功')
        } else {
          await createUser(payload)
          ElMessage.success('新员工录入成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.user-list {
  padding: 0;
}
</style>
