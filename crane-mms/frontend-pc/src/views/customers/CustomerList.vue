<template>
  <div class="customer-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">客户管理</h1>
        <p class="page-subtitle">管理所有客户档案及联系人信息</p>
      </div>
      <el-button type="primary" size="large" @click="openDrawer">
        <span class="btn-icon">＋</span> 新建客户
      </el-button>
    </div>

    <!-- 统计卡片行 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">客户总数</div>
        <div class="stat-value primary">{{ tableData.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">本月新增</div>
        <div class="stat-value success">{{ newThisMonth }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">搜索结果</div>
        <div class="stat-value">{{ filteredData.length }}</div>
      </div>
    </div>

    <!-- 主表格卡片 -->
    <div class="table-card">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索公司名或联系人…"
            clearable
            style="width: 280px"
            @clear="searchQuery = ''"
            @keyup.enter="loadData"
          >
            <template #prefix>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#888">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
              </svg>
            </template>
          </el-input>
          <el-button @click="loadData" style="margin-left: 8px;">搜索</el-button>
        </div>
        <div class="toolbar-right">
          <span class="total-hint">共 {{ filteredData.length }} 条记录</span>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="filteredData"
        v-loading="loading"
        style="width: 100%"
        row-key="id"
        :header-cell-style="{ background: '#fafbfc', fontWeight: '600', fontSize: '12px', color: '#595959' }"
      >
        <el-table-column width="50" align="center">
          <template #default="{ $index }">
            <span class="row-index">{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="company_name" label="公司名称" min-width="200">
          <template #default="{ row }">
            <div class="company-cell">
              <div class="company-avatar">{{ row.company_name?.charAt(0) }}</div>
              <span class="company-link" @click="goToDetail(row.id)">{{ row.company_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="contact_name" label="主联系人" width="120" />
        <el-table-column prop="contact_phone" label="联系电话" width="160">
          <template #default="{ row }">
            <span class="phone-cell">{{ row.contact_phone || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="公司地址" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="address-cell">{{ row.address || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="goToDetail(row.id)">查看</el-button>
            <el-button type="warning" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <div v-if="!loading && filteredData.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <div class="empty-text">暂无客户数据</div>
        <div class="empty-sub">点击右上角「新建客户」添加第一个客户</div>
      </div>
    </div>

    <!-- 新建抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="新建客户"
      size="520px"
      destroy-on-close
      :body-style="{ padding: '24px' }"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <div class="form-section-title">基本信息</div>
        <el-form-item label="公司名称" prop="company_name">
          <el-input v-model="form.company_name" placeholder="请输入公司全称" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="主联系人" prop="contact_name">
              <el-input v-model="form.contact_name" placeholder="联系人姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="form.contact_phone" placeholder="手机/座机" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="公司地址">
          <el-input v-model="form.address" placeholder="详细地址" />
        </el-form-item>

        <div class="form-section-title" style="margin-top:16px">门户访问配置</div>
        <el-form-item label="门户登录手机号" prop="login_phone">
          <el-input v-model="form.login_phone" placeholder="用于客户登录 H5 门户收验证码" />
          <div style="font-size: 12px; color: #999; margin-top: 4px;">设置后，客户即可使用此号码登录并查看其专属维保单</div>
        </el-form-item>

        <div class="form-section-title" style="margin-top:16px">
          其他联系人
          <el-button type="primary" text size="small" @click="addContact" style="float:right;margin-top:-2px">
            ＋ 添加
          </el-button>
        </div>

        <div v-for="(contact, index) in form.contacts" :key="index" class="contact-card">
          <div class="contact-card-header">
            <span>联系人 {{ index + 1 }}</span>
            <el-button type="danger" text size="small" @click="removeContact(index)">删除</el-button>
          </div>
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item
                :prop="`contacts.${index}.name`"
                :rules="{ required: true, message: '请输入姓名' }"
              >
                <el-input v-model="contact.name" placeholder="姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                :prop="`contacts.${index}.phone`"
                :rules="{ required: true, message: '请输入电话' }"
              >
                <el-input v-model="contact.phone" placeholder="电话" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">保存创建</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCustomers, createCustomer, updateCustomer, deleteCustomer } from '@/api/customer'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const searchQuery = ref('')
const drawerVisible = ref(false)
const formRef = ref(null)
const submitLoading = ref(false)

const form = reactive({
  company_name: '',
  contact_name: '',
  contact_phone: '',
  address: '',
  login_phone: '',
  contacts: []
})

const rules = {
  company_name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }],
  contact_name: [{ required: true, message: '请输入主联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
}

// 本月新增（简单计算）
const newThisMonth = computed(() => {
  const now = new Date()
  return tableData.value.filter(c => {
    if (!c.created_at) return false
    const d = new Date(c.created_at)
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  }).length
})

const filteredData = computed(() => {
  if (!searchQuery.value) return tableData.value
  const q = searchQuery.value.toLowerCase()
  return tableData.value.filter(c =>
    c.company_name?.toLowerCase().includes(q) ||
    c.contact_name?.toLowerCase().includes(q)
  )
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCustomers({ search: searchQuery.value })
    tableData.value = res || []
  } catch (err) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => router.push(`/customers/${id}`)

const editingId = ref(null)

const openDrawer = () => {
  editingId.value = null
  Object.assign(form, { company_name: '', contact_name: '', contact_phone: '', address: '', login_phone: '', contacts: [] })
  drawerVisible.value = true
  formRef.value?.clearValidate()
}

const openEdit = (row) => {
  editingId.value = row.id
  Object.assign(form, {
    company_name: row.company_name,
    contact_name: row.contact_name,
    contact_phone: row.contact_phone,
    address: row.address,
    login_phone: row.login_phone,
    contacts: []
  })
  drawerVisible.value = true
  formRef.value?.clearValidate()
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除客户「${row.company_name}」吗？该客户名下若有历史工单将拒绝删除。`,
    '高危警告',
    { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    try {
      await deleteCustomer(row.id)
      ElMessage.success('客户已删除')
      loadData()
    } catch (err) {}
  }).catch(() => {})
}

const addContact = () => form.contacts.push({ name: '', phone: '', position: '' })
const removeContact = (i) => form.contacts.splice(i, 1)

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (editingId.value) {
          await updateCustomer(editingId.value, form)
          ElMessage.success('客户信息已更新')
        } else {
          await createCustomer(form)
          ElMessage.success('✅ 客户创建成功')
        }
        drawerVisible.value = false
        loadData()
      } catch (err) {
        ElMessage.error('创建失败，请检查填写信息')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(loadData)
</script>

<style scoped>
.customer-list { padding: 0; }

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}
.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1;
}
.stat-value.primary { color: var(--color-primary); }
.stat-value.success { color: var(--color-success); }

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
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-light);
}
.toolbar-left { display: flex; align-items: center; gap: 8px; }
.total-hint { font-size: 13px; color: var(--color-text-secondary); }

.row-index {
  font-size: 12px;
  color: var(--color-text-placeholder);
  font-variant-numeric: tabular-nums;
}

.company-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
.company-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #e6f4ff, #bae0ff);
  color: var(--color-primary);
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.company-link {
  color: var(--color-primary);
  font-weight: 600;
  cursor: pointer;
  font-size: 14px;
  transition: var(--transition-fast);
}
.company-link:hover { color: var(--color-primary-hover); text-decoration: underline; }

.phone-cell { font-variant-numeric: tabular-nums; color: var(--color-text-regular); }
.address-cell { color: var(--color-text-secondary); font-size: 13px; }

.empty-state {
  text-align: center;
  padding: 60px 20px;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-text { font-size: 16px; font-weight: 600; color: var(--color-text-regular); margin-bottom: 8px; }
.empty-sub { font-size: 13px; color: var(--color-text-secondary); }

.btn-icon { margin-right: 4px; font-weight: 300; }

.form-section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border-light);
}
.contact-card {
  background: var(--color-bg-page);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  margin-bottom: 10px;
}
.contact-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-regular);
  margin-bottom: 10px;
}
</style>