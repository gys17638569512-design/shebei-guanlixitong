<template>
  <div class="customer-detail">
    <el-page-header @back="goBack" title="返回" style="margin-bottom: 20px;">
      <template #content>
        <span class="text-large font-600 mr-3"> 客户详情 </span>
      </template>
    </el-page-header>

    <el-card class="info-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-button type="primary" @click="goToEquipmentForm">新建设备</el-button>
        </div>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="公司名">{{ customerInfo.company_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="主联系人">{{ customerInfo.contact_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ customerInfo.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="3">{{ customerInfo.address || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div style="margin-top: 20px" v-if="customerInfo.contacts && customerInfo.contacts.length > 0">
        <el-divider>其他联系人</el-divider>
        <el-table :data="customerInfo.contacts" style="width: 100%" size="small" border>
          <el-table-column prop="name" label="姓名" width="180" />
          <el-table-column prop="phone" label="电话" width="180" />
        </el-table>
      </div>
    </el-card>

    <el-card shadow="never" class="table-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>名下设备</span>
        </div>
      </template>
      
      <el-table :data="customerInfo.equipments || []" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="name" label="设备名称" min-width="150" />
        <el-table-column prop="category" label="设备大类" min-width="120" />
        <el-table-column prop="model_type" label="型式" width="120" />
        <el-table-column prop="tonnage" label="吨位" width="100" />
        <el-table-column prop="work_class" label="工作级别" width="100" />
        <el-table-column prop="installation_location" label="安装位置" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editEquipment(row.id)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getCustomerDetail } from '@/api/customer'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const customerInfo = ref({})
const customerId = route.params.id

const loadDetail = async () => {
  if (!customerId) return
  loading.value = true
  try {
    const res = await getCustomerDetail(customerId)
    customerInfo.value = res || {}
  } catch (err) {
    console.warn(err)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/customers')
}

const goToEquipmentForm = () => {
  router.push(`/equipments/form?customerId=${customerId}`)
}

const editEquipment = (equipmentId) => {
  router.push(`/equipments/form/${equipmentId}`)
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.customer-detail {
  padding-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>