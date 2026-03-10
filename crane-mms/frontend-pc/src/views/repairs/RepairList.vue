<template>
  <div class="repair-list">
    <el-card shadow="never">
      <div class="header-tools" style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div class="filter-group">
          <el-select v-model="statusFilter" placeholder="全部状态" clearable @change="loadData" style="width: 140px; margin-right: 12px;">
            <el-option label="待处理" value="PENDING" />
            <el-option label="进行中" value="IN_PROGRESS" />
            <el-option label="待签字" value="PENDING_SIGN" />
            <el-option label="已完成" value="COMPLETED" />
          </el-select>
          <el-button type="primary" plain :icon="Refresh" @click="loadData">刷新</el-button>
        </div>
        <el-button v-if="hasRole(['ADMIN', 'MANAGER'])" type="primary" :icon="Plus" @click="handleAdd">新建故障维修工单</el-button>
      </div>

      <el-table :data="repairs" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="工单编号" width="100">
          <template #default="{ row }"># RM-{{ String(row.id).padStart(5, '0') }}</template>
        </el-table-column>
        <el-table-column prop="equipment_id" label="设备ID" width="100" />
        <el-table-column prop="problem_description" label="故障描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="工单状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plan_date" label="维修日期" width="120" />
        <el-table-column prop="labor_cost" label="人工费(元)" width="120" />
        <el-table-column prop="material_cost" label="材料费(元)" width="120" />
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.id)">维保详情记录</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新建故障维修工单" width="550px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="关联设备" prop="equipment_id">
          <el-input-number v-model="form.equipment_id" :min="1" style="width: 100%" placeholder="填写设备ID" />
        </el-form-item>
        <el-form-item label="分配技师" prop="tech_id">
          <el-input-number v-model="form.tech_id" :min="1" style="width: 100%" placeholder="填写技师ID" />
        </el-form-item>
        <el-form-item label="计划日期" prop="plan_date">
          <el-date-picker v-model="form.plan_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="故障描述" prop="problem_description">
          <el-input type="textarea" v-model="form.problem_description" :rows="3" placeholder="请详细描述故障现象" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">派发工单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getRepairOrders, createRepairOrder } from '@/api/repair'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const repairs = ref([])
const statusFilter = ref('')
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const form = ref({
  equipment_id: null,
  tech_id: null,
  plan_date: '',
  problem_description: ''
})

const rules = {
  equipment_id: [{ required: true, message: '请填写设备ID' }],
  tech_id: [{ required: true, message: '请填写技师ID' }],
  plan_date: [{ required: true, message: '请选择日期' }],
}

const hasRole = (roles) => {
  return roles.includes(authStore.user?.role)
}

const getStatusType = (status) => {
  const map = { PENDING: 'warning', IN_PROGRESS: '', PENDING_SIGN: 'danger', COMPLETED: 'success' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { PENDING: '待分配', IN_PROGRESS: '维修中', PENDING_SIGN: '待签字确认', COMPLETED: '已完工' }
  return map[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getRepairOrders({ status: statusFilter.value || undefined })
    repairs.value = res || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  form.value = { equipment_id: null, tech_id: null, plan_date: '', problem_description: '' }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await createRepairOrder(form.value)
        ElMessage.success('派单成功')
        dialogVisible.value = false
        loadData()
      } catch (err) {
        // Error handled in interceptor
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const goDetail = (id) => {
  router.push(`/repairs/${id}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.repair-list { padding: 0; }
</style>
