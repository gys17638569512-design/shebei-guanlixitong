<template>
  <div class="workspace-page order-page">
    <section class="workspace-hero">
      <div class="workspace-hero__body">
        <p class="workspace-kicker">Work Order Operations</p>
        <h2 class="workspace-title">派工、执行、签字与归档统一调度</h2>
        <p class="workspace-description">
          用同一工作台管理工单节奏，快速判断待处理、进行中、待签字和已完成任务的分布，并直接发起新派单。
        </p>
        <div class="workspace-badges">
          <span class="soft-pill">总工单 {{ tableData.length }}</span>
          <span class="soft-pill">逾期 {{ overdueCount }}</span>
          <span class="soft-pill">完成率 {{ completionRate }}%</span>
        </div>
      </div>
      <div class="workspace-hero__aside">
        <div class="workspace-aside-card">
          <span class="workspace-aside-card__label">当前视图</span>
          <span class="workspace-aside-card__value">{{ hasRole(['ADMIN', 'MANAGER']) ? '全局调度' : '我的任务' }}</span>
          <span class="workspace-aside-card__meta">依据账号角色展示全局工单或个人工单</span>
        </div>
        <div class="workspace-actions">
          <el-button
            v-if="hasRole(['ADMIN', 'MANAGER'])"
            type="primary"
            size="large"
            @click="openCreateDialog"
          >
            新建派单
          </el-button>
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
            <h3 class="surface-panel__title">工单节奏总表</h3>
            <p class="surface-panel__subtitle">按状态、类型和关键词切换，快速定位需要推进的工单。</p>
          </div>
        </div>
        <div class="surface-panel__body">
          <div class="status-deck">
            <button
              v-for="tab in statusTabs"
              :key="tab.value"
              class="status-tile"
              :class="{ active: activeTab === tab.value }"
              type="button"
              @click="activeTab = tab.value"
            >
              <span class="status-tile__count">{{ getStatusCount(tab.value) }}</span>
              <span class="status-tile__label">{{ tab.label }}</span>
            </button>
          </div>

          <div class="filter-strip">
            <el-input
              v-model="searchQuery"
              class="filter-strip__grow"
              placeholder="搜索客户名、设备名或工程师"
              clearable
            />
            <el-select v-model="typeFilter" clearable placeholder="工单类型" style="width: 180px">
              <el-option label="周检" value="周检" />
              <el-option label="月检" value="月检" />
              <el-option label="季检" value="季检" />
              <el-option label="年检" value="年检" />
              <el-option label="临时维保" value="临时维保" />
            </el-select>
            <span class="soft-pill soft-pill--light">当前 {{ filteredData.length }} 条</span>
          </div>

          <el-table :data="filteredData" v-loading="loading" style="width: 100%">
            <el-table-column prop="order_type" label="类型" width="110" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="getTypeTagType(row.order_type)" round>
                  {{ row.order_type || '月检' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="customer_name" label="客户名" min-width="160" show-overflow-tooltip />
            <el-table-column prop="equipment_name" label="设备名" min-width="150" show-overflow-tooltip />
            <el-table-column prop="technician_name" label="负责工程师" width="130" />
            <el-table-column prop="plan_date" label="计划日期" width="130">
              <template #default="{ row }">
                <span :class="isOverdue(row.plan_date) && row.status !== 'COMPLETED' ? 'overdue' : ''">
                  {{ row.plan_date }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120" align="center">
              <template #default="{ row }">
                <span class="status-badge" :class="'status-' + row.status">
                  {{ getStatusLabel(row.status) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="goToDetail(row.id)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="!loading && filteredData.length === 0" class="empty-state">
            <div class="empty-title">当前条件下没有工单</div>
            <div class="empty-subtitle">尝试切换状态、工单类型，或直接创建新的派单任务。</div>
          </div>
        </div>
      </article>

      <div class="surface-grid">
        <article class="surface-panel surface-panel--dark">
          <div class="surface-panel__header">
            <div>
              <h3 class="surface-panel__title">工单判读</h3>
              <p class="surface-panel__subtitle">把状态分布转换成调度建议，减少遗漏。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div class="data-rail">
              <div v-for="item in signalRows" :key="item.label" class="data-rail__item">
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
              <h3 class="surface-panel__title">临期待办</h3>
              <p class="surface-panel__subtitle">优先关注逾期或临近计划日期的工单。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div v-if="focusOrders.length" class="data-rail">
              <div v-for="row in focusOrders" :key="row.id" class="data-rail__item">
                <div class="stacked-text">
                  <strong>{{ row.customer_name || '未命名客户' }}</strong>
                  <span>{{ row.equipment_name || '未命名设备' }} · {{ row.plan_date }}</span>
                </div>
                <el-button type="primary" link @click="goToDetail(row.id)">查看</el-button>
              </div>
            </div>
            <el-empty v-else description="暂无临期待办工单" />
          </div>
        </article>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" title="新建派单" width="560px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="选择客户" prop="customer_id">
              <el-select v-model="form.customer_id" placeholder="请选择" filterable style="width:100%" @change="handleCustomerChange">
                <el-option v-for="item in customers" :key="item.id" :label="item.company_name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="选择设备" prop="equipment_id">
              <el-select v-model="form.equipment_id" placeholder="请先选择客户" style="width:100%" :disabled="!form.customer_id">
                <el-option v-for="item in equipments" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工单类型" prop="order_type">
              <el-select v-model="form.order_type" style="width:100%">
                <el-option label="周检" value="周检" />
                <el-option label="月检" value="月检" />
                <el-option label="季检" value="季检" />
                <el-option label="年检" value="年检" />
                <el-option label="临时维保" value="临时维保" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划日期" prop="plan_date">
              <el-date-picker v-model="form.plan_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="派工给" prop="technician_id">
          <el-select v-model="form.technician_id" placeholder="请选择工程师" filterable style="width:100%">
            <el-option v-for="item in technicians" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitOrder">确认派单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrders, getMyOrders, createOrder } from '@/api/order'
import { getCustomers, getCustomerDetail } from '@/api/customer'
import { getUsers } from '@/api/user'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const tableData = ref([])
const activeTab = ref('ALL')
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const searchQuery = ref('')
const typeFilter = ref('')

const form = reactive({
  customer_id: '',
  equipment_id: '',
  technician_id: '',
  plan_date: '',
  order_type: '月检'
})

const rules = {
  customer_id: [{ required: true, message: '请选择客户' }],
  equipment_id: [{ required: true, message: '请选择设备' }],
  technician_id: [{ required: true, message: '请选择工程师' }],
  plan_date: [{ required: true, message: '请选择日期' }],
  order_type: [{ required: true, message: '请选择工单类型' }]
}

const customers = ref([])
const equipments = ref([])
const technicians = ref([])

const statusTabs = [
  { value: 'ALL', label: '全部' },
  { value: 'PENDING', label: '待处理' },
  { value: 'IN_PROGRESS', label: '进行中' },
  { value: 'PENDING_SIGN', label: '待签字' },
  { value: 'COMPLETED', label: '已完成' }
]

const filteredData = computed(() => {
  return tableData.value.filter((item) => {
    const statusMatched = activeTab.value === 'ALL' || item.status === activeTab.value
    const typeMatched = !typeFilter.value || item.order_type === typeFilter.value
    const keyword = searchQuery.value.trim().toLowerCase()
    const keywordMatched = !keyword || [item.customer_name, item.equipment_name, item.technician_name]
      .filter(Boolean)
      .some((value) => value.toLowerCase().includes(keyword))
    return statusMatched && typeMatched && keywordMatched
  })
})

const overdueCount = computed(() => tableData.value.filter((item) => isOverdue(item.plan_date) && item.status !== 'COMPLETED').length)
const completionRate = computed(() => {
  const total = tableData.value.length
  const completed = tableData.value.filter((item) => item.status === 'COMPLETED').length
  return total ? Math.round((completed / total) * 100) : 0
})

const summaryCards = computed(() => [
  { label: '工单总量', value: tableData.value.length, hint: '当前视图中的全部维保工单' },
  { label: '待处理', value: getStatusCount('PENDING'), hint: '尚未开始执行的待办任务' },
  { label: '待签字', value: getStatusCount('PENDING_SIGN'), hint: '已执行待客户签字归档的任务' },
  { label: '完成率', value: `${completionRate.value}%`, hint: '已完成工单在总工单中的占比' }
])

const focusOrders = computed(() => filteredData.value
  .filter((item) => item.plan_date)
  .slice()
  .sort((a, b) => new Date(a.plan_date) - new Date(b.plan_date))
  .slice(0, 5))

const signalRows = computed(() => [
  {
    label: '逾期工单',
    value: `${overdueCount.value} 单`,
    description: '建议优先处理已超过计划日期但仍未完成的任务。',
    tone: overdueCount.value ? 'danger' : 'success'
  },
  {
    label: '签字积压',
    value: `${getStatusCount('PENDING_SIGN')} 单`,
    description: '待签字过多会拉长归档闭环周期，需要尽快跟进。',
    tone: getStatusCount('PENDING_SIGN') ? 'warning' : 'success'
  },
  {
    label: '执行在途',
    value: `${getStatusCount('IN_PROGRESS')} 单`,
    description: '进行中工单反映当前现场工作压力与资源投入状态。',
    tone: getStatusCount('IN_PROGRESS') > 3 ? 'warning' : ''
  }
])

const getStatusCount = (status) => {
  if (status === 'ALL') return tableData.value.length
  return tableData.value.filter((item) => item.status === status).length
}

const getStatusLabel = (status) => {
  const map = { PENDING: '待处理', IN_PROGRESS: '进行中', PENDING_SIGN: '待签字', COMPLETED: '已完成', RESCHEDULED: '已改期', REASSIGNED: '已转派' }
  return map[status] || status
}

const getTypeTagType = (type) => {
  const map = { 周检: 'info', 月检: '', 季检: 'warning', 年检: 'danger', 临时维保: 'success' }
  return map[type] || ''
}

const isOverdue = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const hasRole = (roles) => roles.includes(authStore.user?.role)
const goToDetail = (id) => router.push(`/orders/${id}`)

const loadData = async () => {
  loading.value = true
  try {
    const res = authStore.user?.role === 'TECH' ? await getMyOrders() : await getOrders()
    tableData.value = res || []
  } catch (error) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const openCreateDialog = async () => {
  Object.assign(form, { customer_id: '', equipment_id: '', technician_id: '', plan_date: '', order_type: '月检' })
  equipments.value = []
  dialogVisible.value = true
  try {
    const [customerRes, technicianRes] = await Promise.all([getCustomers(), getUsers({ role: 'TECH' })])
    customers.value = customerRes || []
    technicians.value = (technicianRes?.items || technicianRes || []).map((item) => ({ id: item.id, name: item.name || item.username }))
  } catch (error) {}
}

const handleCustomerChange = async (value) => {
  form.equipment_id = ''
  if (!value) {
    equipments.value = []
    return
  }
  try {
    const res = await getCustomerDetail(value)
    equipments.value = res?.equipments || []
  } catch (error) {}
}

const submitOrder = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await createOrder(form)
        ElMessage.success('工单派发成功')
        dialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error('派单失败，请重试')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(loadData)
</script>

<style scoped>
.status-deck {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.status-tile {
  padding: 16px;
  border: 1px solid rgba(15, 33, 51, 0.08);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(243, 247, 251, 0.88));
  cursor: pointer;
  transition: var(--transition-fast);
}

.status-tile:hover,
.status-tile.active {
  border-color: rgba(47, 137, 255, 0.26);
  box-shadow: 0 16px 24px rgba(47, 137, 255, 0.12);
}

.status-tile__count {
  display: block;
  font-family: var(--font-display);
  font-size: 30px;
  color: var(--color-text-primary);
}

.status-tile__label {
  display: block;
  margin-top: 8px;
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-PENDING {
  background: #fff7e6;
  color: #c26f00;
}

.status-IN_PROGRESS {
  background: #edf5ff;
  color: var(--color-primary-dark);
}

.status-PENDING_SIGN {
  background: #f4ecff;
  color: #6e42d9;
}

.status-COMPLETED {
  background: #ecf9f2;
  color: #1f8f60;
}

.status-RESCHEDULED,
.status-REASSIGNED {
  background: #f2f4f6;
  color: var(--color-text-secondary);
}

.overdue {
  color: var(--color-danger);
  font-weight: 800;
}

.empty-state {
  padding: 36px 0 8px;
  text-align: center;
}

.empty-title {
  color: var(--color-text-primary);
  font-weight: 800;
}

.empty-subtitle {
  margin-top: 8px;
  color: var(--color-text-secondary);
}

@media (max-width: 1100px) {
  .status-deck {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
