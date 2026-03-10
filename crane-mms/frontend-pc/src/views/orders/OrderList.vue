<template>
  <div class="order-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">工单中心</h1>
        <p class="page-subtitle">管理所有维保工单，实时追踪任务进度</p>
      </div>
      <el-button
        v-if="hasRole(['ADMIN', 'MANAGER'])"
        type="primary"
        size="large"
        @click="openCreateDialog"
      >
        <span class="btn-icon">＋</span> 新建派单
      </el-button>
    </div>

    <!-- 状态看板 -->
    <div class="status-board">
      <div
        v-for="tab in statusTabs"
        :key="tab.value"
        class="status-tab"
        :class="{ active: activeTab === tab.value }"
        @click="activeTab = tab.value"
      >
        <div class="tab-count" :class="tab.colorClass">{{ getStatusCount(tab.value) }}</div>
        <div class="tab-label">{{ tab.label }}</div>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="table-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="filter-label">
            共 <strong>{{ filteredData.length }}</strong> 条工单
          </span>
        </div>
      </div>

      <el-table :data="filteredData" v-loading="loading" style="width: 100%">
        <el-table-column prop="order_type" label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getTypeTagType(row.order_type)" round>
              {{ row.order_type || '月检' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" label="客户名" min-width="160" show-overflow-tooltip />
        <el-table-column prop="equipment_name" label="设备名" min-width="150" show-overflow-tooltip />
        <el-table-column prop="technician_name" label="负责工程师" width="120" />
        <el-table-column prop="plan_date" label="计划日期" width="120">
          <template #default="{ row }">
            <span :class="isOverdue(row.plan_date) && row.status !== 'COMPLETED' ? 'overdue' : ''">
              {{ row.plan_date }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
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
        <div class="empty-icon">📋</div>
        <div class="empty-text">该状态下暂无工单</div>
      </div>
    </div>

    <!-- 新建工单弹窗 -->
    <el-dialog v-model="dialogVisible" title="新建派单" width="520px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="选择客户" prop="customer_id">
              <el-select v-model="form.customer_id" placeholder="请选择" filterable style="width:100%" @change="handleCustomerChange">
                <el-option v-for="c in customers" :key="c.id" :label="c.company_name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="选择设备" prop="equipment_id">
              <el-select v-model="form.equipment_id" placeholder="请先选择客户" style="width:100%" :disabled="!form.customer_id">
                <el-option v-for="e in equipments" :key="e.id" :label="e.name" :value="e.id" />
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
            <el-option v-for="t in technicians" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder" :loading="submitLoading">确认派单</el-button>
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

const form = reactive({
  customer_id: '', equipment_id: '', technician_id: '',
  plan_date: '', order_type: '月检'
})
const rules = {
  customer_id: [{ required: true, message: '请选择客户' }],
  equipment_id: [{ required: true, message: '请选择设备' }],
  technician_id: [{ required: true, message: '请选择工程师' }],
  plan_date: [{ required: true, message: '请选择日期' }],
  order_type: [{ required: true, message: '请选择工单类型' }],
}

const customers = ref([])
const equipments = ref([])
const technicians = ref([])

const statusTabs = [
  { value: 'ALL', label: '全部', colorClass: 'c-default' },
  { value: 'PENDING', label: '待处理', colorClass: 'c-warning' },
  { value: 'IN_PROGRESS', label: '进行中', colorClass: 'c-primary' },
  { value: 'PENDING_SIGN', label: '待签字', colorClass: 'c-info' },
  { value: 'COMPLETED', label: '已完成', colorClass: 'c-success' },
]

const filteredData = computed(() => {
  if (activeTab.value === 'ALL') return tableData.value
  return tableData.value.filter(o => o.status === activeTab.value)
})

const getStatusCount = (status) => {
  if (status === 'ALL') return tableData.value.length
  return tableData.value.filter(o => o.status === status).length
}

const getStatusLabel = (status) => {
  const m = { PENDING: '待处理', IN_PROGRESS: '进行中', PENDING_SIGN: '待签字', COMPLETED: '已完成', RESCHEDULED: '已改期', REASSIGNED: '已转派' }
  return m[status] || status
}

const getTypeTagType = (type) => {
  const m = { '周检': 'info', '月检': '', '季检': 'warning', '年检': 'danger', '临时维保': 'success' }
  return m[type] || ''
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
  } catch { tableData.value = [] }
  finally { loading.value = false }
}

const openCreateDialog = async () => {
  Object.assign(form, { customer_id: '', equipment_id: '', technician_id: '', plan_date: '', order_type: '月检' })
  equipments.value = []
  dialogVisible.value = true
  try {
    const [cr, tr] = await Promise.all([getCustomers(), getUsers({ role: 'TECH' })])
    customers.value = cr || []
    technicians.value = (tr?.items || tr || []).map(u => ({ id: u.id, name: u.name || u.username }))
  } catch {}
}

const handleCustomerChange = async (val) => {
  form.equipment_id = ''
  if (!val) { equipments.value = []; return }
  try {
    const res = await getCustomerDetail(val)
    equipments.value = res?.equipments || []
  } catch {}
}

const submitOrder = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await createOrder(form)
        ElMessage.success('✅ 工单派发成功')
        dialogVisible.value = false
        loadData()
      } catch {
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
.order-list { padding: 0; }

/* 状态看板 */
.status-board {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.status-tab {
  flex: 1;
  background: #fff;
  border: 2px solid transparent;
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  cursor: pointer;
  transition: var(--transition-fast);
  box-shadow: var(--shadow-sm);
  text-align: center;
}
.status-tab:hover { border-color: var(--color-border); transform: translateY(-1px); }
.status-tab.active {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(22,119,255,.15);
}
.tab-count {
  font-size: 24px;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 4px;
}
.tab-label { font-size: 12px; color: var(--color-text-secondary); font-weight: 500; }
.c-default { color: var(--color-text-primary); }
.c-warning { color: #faad14; }
.c-primary { color: var(--color-primary); }
.c-info    { color: #722ed1; }
.c-success { color: var(--color-success); }

/* 表格 */
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
.filter-label { font-size: 13px; color: var(--color-text-secondary); }
.filter-label strong { color: var(--color-text-primary); }

/* 状态徽章 */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}
.status-PENDING        { background: #fff7e6; color: #d46b08; }
.status-IN_PROGRESS    { background: #e6f4ff; color: #0958d9; }
.status-PENDING_SIGN   { background: #f9f0ff; color: #531dab; }
.status-COMPLETED      { background: #f6ffed; color: #389e0d; }
.status-RESCHEDULED,
.status-REASSIGNED     { background: #f5f5f5; color: #595959; }

.overdue { color: var(--color-danger); font-weight: 600; }

.btn-icon { margin-right: 4px; font-weight: 300; }
.empty-state { text-align: center; padding: 48px 20px; }
.empty-icon { font-size: 40px; margin-bottom: 10px; }
.empty-text { font-size: 15px; font-weight: 600; color: var(--color-text-secondary); }
</style>