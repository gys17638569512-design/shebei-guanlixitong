<template>
  <div class="repair-detail">
    <div class="page-header" v-if="order">
      <el-button @click="router.back()" style="margin-right: 20px;">返回列表</el-button>
      <h2>维修工单 #RM-{{ String(order.id).padStart(5, '0') }}</h2>
      <el-tag :type="getStatusType(order.status)" class="ms-4">{{ getStatusLabel(order.status) }}</el-tag>
      <div class="header-actions">
        <el-button v-if="isCompleted" type="primary" plain :loading="reportLoading" @click="handleDownloadReport">
          下载检修 PDF 报告
        </el-button>
      </div>
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
            <el-descriptions-item label="创建时间">{{ formatDateTime(order.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="人工费用">¥ {{ formatMoney(order.labor_fee) }}</el-descriptions-item>
            <el-descriptions-item label="其他费用">¥ {{ formatMoney(order.other_fee) }}</el-descriptions-item>
            <el-descriptions-item label="总计定损" class="fw-bold text-danger">¥ {{ formatMoney(order.total_fee) }}</el-descriptions-item>
            <el-descriptions-item label="故障现象" :span="2">{{ order.fault_symptom || '暂无描述' }}</el-descriptions-item>
            <el-descriptions-item label="防范建议" :span="2">{{ order.prevention_advice || '暂无处理记录' }}</el-descriptions-item>
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
                    <el-input-number v-model="updateForm.labor_fee" :precision="2" :step="100" placeholder="人工费" style="width: 100%" />
                  </el-col>
                  <el-col :span="2" style="text-align: center;">+</el-col>
                  <el-col :span="11">
                    <el-input-number v-model="updateForm.other_fee" :precision="2" :step="100" placeholder="其他费用" style="width: 100%" />
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
          <div v-if="order.client_sign_url" class="sign-preview">
            <el-image :src="order.client_sign_url" fit="contain" style="width: 100%; height: 200px;" :preview-src-list="[order.client_sign_url]" />
            <p class="text-center text-success mt-2">✓ 客户已签字确认</p>
          </div>
          <el-empty v-else description="暂无电子签字" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getRepairDetail, getRepairReport, updateRepairOrder } from '@/api/repair'

const route = useRoute()
const router = useRouter()
const orderId = route.params.id

const order = ref(null)
const submitLoading = ref(false)
const reportLoading = ref(false)
const updateForm = ref({
  status: '',
  labor_fee: 0,
  other_fee: 0,
  solution: ''
})

const isCompleted = computed(() => ['COMPLETED', '已完成'].includes(order.value?.status))

const getStatusType = (status) => {
  const map = {
    PENDING: 'warning',
    IN_PROGRESS: '',
    PENDING_SIGN: 'danger',
    COMPLETED: 'success',
    待处理: 'warning',
    进行中: '',
    待客户确认: 'danger',
    已完成: 'success'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    PENDING: '待分配',
    IN_PROGRESS: '维修中',
    PENDING_SIGN: '待签字确认',
    COMPLETED: '已完工',
    待处理: '待分配',
    进行中: '维修中',
    待客户确认: '待签字确认',
    已完成: '已完工'
  }
  return map[status] || status
}

const formatMoney = (value) => Number(value || 0).toFixed(2)

const formatDateTime = (value) => value || '—'

const loadData = async () => {
  try {
    const res = await getRepairDetail(orderId)
    order.value = res
    updateForm.value = {
      status: res.status,
      labor_fee: res.labor_fee,
      other_fee: res.other_fee,
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
    ElMessage.success(updateForm.value.status === 'COMPLETED' ? '工单已完工，PDF 报告开始生成' : '工单进度已更新并且费用已保存！')
    await loadData()
  } catch (error) {
    //
  } finally {
    submitLoading.value = false
  }
}

const handleDownloadReport = async () => {
  reportLoading.value = true
  try {
    const res = await getRepairReport(orderId)
    if (res?.pdf_url) {
      window.open(res.pdf_url, '_blank')
      await loadData()
      return
    }
    ElMessage.info('报告正在生成中，请稍后再试')
  } catch (error) {
    ElMessage.error('获取检修 PDF 报告失败')
  } finally {
    reportLoading.value = false
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
.header-actions { margin-left: auto; }
.card-title { font-weight: bold; }
.ms-4 { margin-left: 1rem; }
.mt-4 { margin-top: 1rem; }
.mt-2 { margin-top: 0.5rem; }
.text-center { text-align: center; }
.fw-bold { font-weight: 700; }
.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }
</style>
