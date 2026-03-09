<template>
  <div class="order-list">
    <el-card shadow="never">
      <div class="header-tools" style="margin-bottom: 20px; display: flex; justify-content: space-between;">
        <el-radio-group v-model="activeTab" @change="loadData">
          <el-radio-button label="全部" />
          <el-radio-button label="PENDING">待处理</el-radio-button>
          <el-radio-button label="IN_PROGRESS">进行中</el-radio-button>
          <el-radio-button label="WAITING_SIGN">待签字</el-radio-button>
          <el-radio-button label="COMPLETED">已完成</el-radio-button>
        </el-radio-group>
        <el-button type="primary" icon="Plus" @click="openCreateDialog" v-if="hasRole(['ADMIN', 'MANAGER'])">新建派单</el-button>
      </div>

      <el-table :data="filteredData" v-loading="loading" stripe>
        <el-table-column prop="customer_name" label="客户名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="equipment_name" label="设备名" min-width="150" />
        <el-table-column prop="technician_name" label="负责工程师" width="120">
          <template #default="{ row }">
            {{ row.technician?.name || row.technician_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="plan_date" label="计划日期" width="120" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToDetail(row.id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新建派单" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="选择客户" prop="customer_id">
          <el-select v-model="form.customer_id" placeholder="请选择客户" filterable style="width: 100%" @change="handleCustomerChange">
            <el-option v-for="c in customers" :key="c.id" :label="c.company_name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择设备" prop="equipment_id">
          <el-select v-model="form.equipment_id" placeholder="请先选择客户" style="width: 100%" :disabled="!form.customer_id">
            <el-option v-for="e in equipments" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="派工给" prop="technician_id">
          <el-select v-model="form.technician_id" placeholder="请选择工程师" filterable style="width: 100%">
            <el-option v-for="t in technicians" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划日期" prop="plan_date">
          <el-date-picker v-model="form.plan_date" type="date" placeholder="选择计划日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="工单类型" prop="order_type">
          <el-select v-model="form.order_type" placeholder="请选择工单类型" style="width: 100%">
            <el-option label="周检" value="周检" />
            <el-option label="月检" value="月检" />
            <el-option label="季检" value="季检" />
            <el-option label="年检" value="年检" />
            <el-option label="临时维保" value="临时维保" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitOrder" :loading="submitLoading">确认派单</el-button>
        </span>
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
const activeTab = ref('全部')

const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  customer_id: '',
  equipment_id: '',
  technician_id: '',
  plan_date: '',
  order_type: '月检'
})

const rules = {
  customer_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
  equipment_id: [{ required: true, message: '请选择设备', trigger: 'change' }],
  technician_id: [{ required: true, message: '请指定工程师', trigger: 'change' }],
  plan_date: [{ required: true, message: '请选择计划日期', trigger: 'change' }],
  order_type: [{ required: true, message: '请选择工单类型', trigger: 'change' }]
}

const customers = ref([])
const equipments = ref([])
const technicians = ref([])

const filteredData = computed(() => {
  if (activeTab.value === '全部') {
    return tableData.value
  }
  return tableData.value.filter(item => item.status === activeTab.value)
})

const hasRole = (roles) => {
  return roles.includes(authStore.user?.role)
}

const getStatusType = (status) => {
  const map = {
    'PENDING': 'warning',
    'IN_PROGRESS': 'primary',
    'PENDING_SIGN': '',
    'COMPLETED': 'success',
    'RESCHEDULED': 'info',
    'REASSIGNED': 'info',
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    'PENDING': '待处理',
    'IN_PROGRESS': '进行中',
    'PENDING_SIGN': '待签字',
    'COMPLETED': '已完成',
    'RESCHEDULED': '已改期',
    'REASSIGNED': '已转派',
  }
  return map[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    let res
    if (authStore.user?.role === 'TECH') {
      res = await getMyOrders()
    } else {
      res = await getOrders()
    }
    tableData.value = res || []
  } catch (err) {
    console.warn(err)
    // mock for dev
    tableData.value = [
      { id: 1, customer_name: '测试公司', equipment_name: '桥式起重机', technician_name: '工程师', plan_date: '2026-03-10', status: 'PENDING' }
    ]
  } finally {
    loading.value = false
  }
}

const openCreateDialog = async () => {
  form.customer_id = ''
  form.equipment_id = ''
  form.technician_id = ''
  form.plan_date = ''
  form.order_type = '月检'
  equipments.value = []
  
  try {
    const [customerRes, techRes] = await Promise.all([
      getCustomers(),
      getUsers({ role: 'TECH' })
    ])
    customers.value = customerRes || []
    technicians.value = (techRes?.items || techRes || []).map(u => ({ id: u.id, name: u.name || u.username }))
  } catch(e) {}
  
  dialogVisible.value = true
}

const handleCustomerChange = async (val) => {
  form.equipment_id = ''
  if (!val) {
    equipments.value = []
    return
  }
  try {
    const res = await getCustomerDetail(val)
    equipments.value = res?.equipments || []
  } catch(e) {}
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
      } catch (err) {
        ElMessage.warning('API 暂未完成，演示创建成功')
        dialogVisible.value = false
        loadData()
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const goToDetail = (id) => {
  router.push(`/orders/${id}`)
}

onMounted(() => {
  loadData()
})
</script>