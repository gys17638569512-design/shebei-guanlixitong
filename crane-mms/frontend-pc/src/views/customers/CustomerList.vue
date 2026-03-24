<template>
  <div class="workspace-page customer-page">
    <section class="workspace-hero">
      <div class="workspace-hero__body">
        <p class="workspace-kicker">Customer Operations</p>
        <h2 class="workspace-title">客户关系与门户接入一体管理</h2>
        <p class="workspace-description">
          在一个页面里维护客户档案、联系人、门户访问手机号和协作入口，方便后续设备、工单与签字链路快速挂接。
        </p>
        <div class="workspace-badges">
          <span class="soft-pill">客户总量 {{ tableData.length }}</span>
          <span class="soft-pill">门户就绪 {{ portalReadyCount }}</span>
          <span class="soft-pill">多联系人客户 {{ multiContactCount }}</span>
        </div>
      </div>
      <div class="workspace-hero__aside">
        <div class="workspace-aside-card">
          <span class="workspace-aside-card__label">新增动作</span>
          <span class="workspace-aside-card__value">客户建档</span>
          <span class="workspace-aside-card__meta">创建后即可继续录入设备和绑定门户手机号</span>
        </div>
        <div class="workspace-actions customer-hero-actions">
          <el-button type="primary" size="large" @click="openDrawer">新建客户</el-button>
        </div>
      </div>
    </section>

    <section class="metrics-grid">
      <article v-for="item in summaryCards" :key="item.label" class="metric-tile">
        <div class="metric-label">{{ item.label }}</div>
        <div class="metric-value">{{ item.value }}</div>
        <div class="metric-footnote">{{ item.hint }}</div>
      </article>
    </section>

    <section class="surface-grid surface-grid--two">
      <article class="surface-panel">
        <div class="surface-panel__header">
          <div>
            <h3 class="surface-panel__title">客户档案总表</h3>
            <p class="surface-panel__subtitle">搜索公司名或联系人，快速进入详情或继续补充档案。</p>
          </div>
        </div>
        <div class="surface-panel__body">
          <div class="filter-strip">
            <el-input
              v-model="searchQuery"
              class="filter-strip__grow"
              placeholder="搜索公司名或联系人"
              clearable
              @clear="searchQuery = ''"
              @keyup.enter="loadData"
            >
              <template #prefix>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#7f93a6">
                  <circle cx="11" cy="11" r="8" />
                  <path d="M21 21l-4.35-4.35" />
                </svg>
              </template>
            </el-input>
            <el-button @click="loadData">搜索</el-button>
            <span class="soft-pill soft-pill--light">结果 {{ filteredData.length }} 条</span>
          </div>

          <div class="table-caption">
            <span>客户、联系人、门户入口将在后续设备与工单流转中复用。</span>
            <strong>总计 {{ filteredData.length }} 条记录</strong>
          </div>

          <el-table
            :data="filteredData"
            v-loading="loading"
            style="width: 100%"
            row-key="id"
          >
            <el-table-column width="60" align="center">
              <template #default="{ $index }">
                <span class="row-index">{{ String($index + 1).padStart(2, '0') }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="company_name" label="客户主体" min-width="220">
              <template #default="{ row }">
                <div class="company-cell">
                  <div class="company-avatar">{{ row.company_name?.charAt(0) }}</div>
                  <div class="stacked-text">
                    <strong class="company-link" @click="goToDetail(row.id)">{{ row.company_name }}</strong>
                    <span>{{ row.contact_name || '未填写主联系人' }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="contact_phone" label="联系电话" width="170">
              <template #default="{ row }">
                <span class="mono-text">{{ row.contact_phone || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="login_phone" label="门户登录手机号" width="180">
              <template #default="{ row }">
                <el-tag :type="row.login_phone ? 'success' : 'info'" effect="light">
                  {{ row.login_phone || '未配置' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="address" label="公司地址" min-width="240" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="address-cell">{{ row.address || '未填写地址' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="goToDetail(row.id)">查看</el-button>
                <el-button type="success" link size="small" @click="openEdit(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="!loading && filteredData.length === 0" class="empty-state">
            <div class="empty-icon">客户档案池为空</div>
            <div class="empty-sub">先创建客户主体，再继续录入设备与维保计划。</div>
          </div>
        </div>
      </article>

      <div class="surface-grid">
        <article class="surface-panel surface-panel--dark">
          <div class="surface-panel__header">
            <div>
              <h3 class="surface-panel__title">接入信号</h3>
              <p class="surface-panel__subtitle">门户准备度和联系人覆盖情况会直接影响后续协作效率。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div class="data-rail">
              <div v-for="item in insightRows" :key="item.label" class="data-rail__item">
                <div class="stacked-text">
                  <span class="eyebrow-label">{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                  <span>{{ item.description }}</span>
                </div>
                <span class="status-dot" :class="item.tone"></span>
              </div>
            </div>
          </div>
        </article>

        <article class="surface-panel">
          <div class="surface-panel__header">
            <div>
              <h3 class="surface-panel__title">最近录入客户</h3>
              <p class="surface-panel__subtitle">便于快速补全联系人、门户手机号和设备信息。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div v-if="recentCustomers.length" class="data-rail">
              <div v-for="row in recentCustomers" :key="row.id" class="data-rail__item">
                <div class="stacked-text">
                  <strong>{{ row.company_name }}</strong>
                  <span>{{ row.contact_name || '未填写主联系人' }} · {{ row.contact_phone || '无联系电话' }}</span>
                </div>
                <el-button type="primary" link @click="goToDetail(row.id)">查看</el-button>
              </div>
            </div>
            <el-empty v-else description="暂无最近录入客户" />
          </div>
        </article>
      </div>
    </section>

    <el-drawer
      v-model="drawerVisible"
      :title="editingId ? '编辑客户档案' : '新建客户档案'"
      size="540px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
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
              <el-input v-model="form.contact_phone" placeholder="手机或座机" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="公司地址">
          <el-input v-model="form.address" placeholder="详细地址" />
        </el-form-item>

        <el-form-item label="门户登录手机号" prop="login_phone">
          <el-input v-model="form.login_phone" placeholder="用于客户登录门户收验证码" />
        </el-form-item>

        <div class="drawer-section-head">
          <span>其他联系人</span>
          <el-button type="primary" text @click="addContact">新增联系人</el-button>
        </div>

        <div v-for="(contact, index) in form.contacts" :key="index" class="contact-card">
          <div class="contact-card__head">
            <strong>联系人 {{ index + 1 }}</strong>
            <el-button type="danger" text size="small" @click="removeContact(index)">删除</el-button>
          </div>
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item :prop="`contacts.${index}.name`" :rules="{ required: true, message: '请输入姓名' }">
                <el-input v-model="contact.name" placeholder="姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :prop="`contacts.${index}.phone`" :rules="{ required: true, message: '请输入电话' }">
                <el-input v-model="contact.phone" placeholder="电话" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">
          {{ editingId ? '保存修改' : '保存创建' }}
        </el-button>
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
const editingId = ref(null)

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
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const newThisMonth = computed(() => {
  const now = new Date()
  return tableData.value.filter((item) => {
    if (!item.created_at) return false
    const date = new Date(item.created_at)
    return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear()
  }).length
})

const portalReadyCount = computed(() => tableData.value.filter((item) => item.login_phone).length)
const multiContactCount = computed(() => tableData.value.filter((item) => (item.contacts?.length || 0) > 1).length)

const filteredData = computed(() => {
  if (!searchQuery.value) return tableData.value
  const keyword = searchQuery.value.toLowerCase()
  return tableData.value.filter((item) =>
    item.company_name?.toLowerCase().includes(keyword) ||
    item.contact_name?.toLowerCase().includes(keyword)
  )
})

const recentCustomers = computed(() => filteredData.value
  .slice()
  .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
  .slice(0, 5))

const summaryCards = computed(() => [
  { label: '客户总量', value: tableData.value.length, hint: '已建档客户主体数量' },
  { label: '本月新增', value: newThisMonth.value, hint: '本月新录入的客户档案' },
  { label: '门户就绪', value: portalReadyCount.value, hint: '已配置门户登录手机号的客户' },
  { label: '检索结果', value: filteredData.value.length, hint: '当前筛选条件命中的客户数量' }
])

const insightRows = computed(() => [
  {
    label: '门户接入率',
    value: tableData.value.length ? `${Math.round((portalReadyCount.value / tableData.value.length) * 100)}%` : '0%',
    description: '客户门户手机号配置越完整，后续签字与查看报告越顺畅。',
    tone: portalReadyCount.value < tableData.value.length ? 'warning' : 'success'
  },
  {
    label: '联系人冗余',
    value: `${multiContactCount.value} 家`,
    description: '具备多联系人意味着后续沟通容错更高，适合优先推进门户协同。',
    tone: multiContactCount.value ? 'success' : ''
  },
  {
    label: '当月建档',
    value: `${newThisMonth.value} 家`,
    description: '新客户较多时，建议同步检查设备模板是否覆盖到对应场景。',
    tone: newThisMonth.value > 2 ? 'warning' : ''
  }
])

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCustomers({ search: searchQuery.value })
    tableData.value = res || []
  } catch (error) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => router.push(`/customers/${id}`)

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
    } catch (error) {}
  }).catch(() => {})
}

const addContact = () => form.contacts.push({ name: '', phone: '', position: '' })
const removeContact = (index) => form.contacts.splice(index, 1)

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
          ElMessage.success('客户创建成功')
        }
        drawerVisible.value = false
        loadData()
      } catch (error) {
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
.customer-hero-actions {
  margin-top: 14px;
}

.row-index {
  color: var(--color-text-placeholder);
  font-variant-numeric: tabular-nums;
}

.company-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.company-avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(47, 137, 255, 0.14), rgba(100, 180, 255, 0.22));
  color: var(--color-primary-dark);
  font-weight: 800;
}

.company-link {
  cursor: pointer;
}

.company-link:hover {
  color: var(--color-primary);
}

.mono-text {
  font-variant-numeric: tabular-nums;
}

.address-cell {
  color: var(--color-text-secondary);
}

.drawer-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 10px 0 14px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.contact-card {
  padding: 14px;
  border-radius: 18px;
  background: rgba(239, 245, 250, 0.88);
  border: 1px solid rgba(15, 33, 51, 0.06);
}

.contact-card + .contact-card {
  margin-top: 12px;
}

.contact-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.empty-state {
  padding: 36px 0 8px;
  text-align: center;
}

.empty-icon {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--color-text-primary);
}

.empty-sub {
  margin-top: 8px;
  color: var(--color-text-secondary);
}
</style>
