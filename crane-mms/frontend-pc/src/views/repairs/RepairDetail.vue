<template>
  <div class="repair-detail">
    <div class="page-header" v-if="order">
      <el-button @click="router.back()" style="margin-right: 20px;">返回列表</el-button>
      <h2>维修工单 #RM-{{ String(order.id).padStart(5, '0') }}</h2>
      <el-tag :type="getStatusType(order.status)" class="ms-4">{{ getStatusLabel(order.status) }}</el-tag>
    </div>

    <el-row :gutter="20" v-if="order">
      <!-- 左侧：工单信息 & 处理状态 -->
      <el-col :span="16">
        <el-card shadow="never" class="info-card">
          <template #header>
            <div class="card-title">基本信息与进度</div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="关联设备ID">{{ order.equipment_id }}</el-descriptions-item>
            <el-descriptions-item label="处理人ID">{{ order.tech_id }}</el-descriptions-item>
            <el-descriptions-item label="计划日期">{{ order.plan_date }}</el-descriptions-item>
            <el-descriptions-item label="人工费用">¥ {{ order.labor_cost }}</el-descriptions-item>
            <el-descriptions-item label="材料费用">¥ {{ order.material_cost }}</el-descriptions-item>
            <el-descriptions-item label="总计定损" class="fw-bold text-danger">¥ {{ (order.labor_cost + order.material_cost).toFixed(2) }}</el-descriptions-item>
            <el-descriptions-item label="报修问题" :span="2">{{ order.problem_description || '暂无描述' }}</el-descriptions-item>
            <el-descriptions-item label="处理记录" :span="2">{{ order.solution || '暂无处理记录' }}</el-descriptions-item>
          </el-descriptions>

          <div class="actions-area mt-4" v-if="order.status !== 'COMPLETED'">
            <el-divider>更新流程</el-divider>
            <el-form :model="updateForm" label-width="100px">
              <el-form-item label="更新状态">
                <el-select v-model="updateForm.status" style="width: 200px">
                  <el-option label="待处理" value="PENDING" />
                  <el-option label="进行中" value="IN_PROGRESS" />
                  <el-option label="待签字确认" value="PENDING_SIGN" />
                  <el-option label="已完成" value="COMPLETED" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="定损费用录入">
                <el-row :gutter="10">
                  <el-col :span="11">
                    <el-input-number v-model="updateForm.labor_cost" :precision="2" :step="100" placeholder="人工费" style="width: 100%" />
                  </el-col>
                  <el-col :span="2" style="text-align: center;">+</el-col>
                  <el-col :span="11">
                    <el-input-number v-model="updateForm.material_cost" :precision="2" :step="100" placeholder="材料费" style="width: 100%" />
                  </el-col>
                </el-row>
              </el-form-item>

              <el-form-item label="处理方案">
                <el-input type="textarea" v-model="updateForm.solution" :rows="3" placeholder="填写检修更换配件详情和维修结果" />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="handleUpdate" :loading="submitLoading">提交进度更新</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never" class="info-card">
          <template #header>
            <div class="card-title">签字凭证</div>
          </template>
          <div v-if="order.sign_url" class="sign-preview">
            <el-image :src="order.sign_url" fit="contain" style="width: 100%; height: 200px;" :preview-src-list="[order.sign_url]" />
            <p class="text-center text-success mt-2">✓ 客户已签字确认</p>
          </div>
          <el-empty v-else description="暂无电子签字" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getRepairDetail, updateRepairOrder } from '@/api/repair'

const route = useRoute()
const router = useRouter()
const orderId = route.params.id

const order = ref(null)
const submitLoading = ref(false)
const updateForm = ref({
  status: '',
  labor_cost: 0,
  material_cost: 0,
  solution: ''
})

const getStatusType = (status) => {
  const map = { PENDING: 'warning', IN_PROGRESS: '', PENDING_SIGN: 'danger', COMPLETED: 'success' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { PENDING: '待分配', IN_PROGRESS: '维修中', PENDING_SIGN: '待签字确认', COMPLETED: '已完工' }
  return map[status] || status
}

const loadData = async () => {
  try {
    const res = await getRepairDetail(orderId)
    order.value = res
    updateForm.value = {
      status: res.status,
      labor_cost: res.labor_cost,
      material_cost: res.material_cost,
      solution: res.solution || ''
    }
  } catch (error) {
    ElMessage.error('无法加载工单详情')
  }
}

const handleUpdate = async () => {
  submitLoading.value = true
  try {
    await updateRepairOrder(orderId, updateForm.value)
    ElMessage.success('工单进度已更新并且费用已保存！')
    await loadData()
  } catch (error) {
    //
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}
.page-header h2 { margin: 0; }
.card-title { font-weight: bold; }
.ms-4 { margin-left: 1rem; }
.mt-4 { margin-top: 1rem; }
.mt-2 { margin-top: 0.5rem; }
.text-center { text-align: center; }
.fw-bold { font-weight: 700; }
.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }
</style>
