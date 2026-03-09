<template>
  <div class="order-detail" v-loading="loading">
    <el-page-header @back="goBack" title="返回" style="margin-bottom: 20px;">
      <template #content>
        <span class="text-large font-600 mr-3"> 工单详细信息 </span>
        <el-tag :type="getStatusType(order.status)" style="vertical-align: middle;">
          {{ getStatusLabel(order.status) }}
        </el-tag>
      </template>
      <template #extra>
        <el-button v-if="order.status === 'PENDING' && hasRole(['ADMIN', 'MANAGER'])" type="warning" plain>转派工单</el-button>
        <el-button v-if="order.status === 'COMPLETED' && order.pdf_report_url" type="primary" tag="a" :href="order.pdf_report_url" target="_blank">
          下载 PDF 维修报告
        </el-button>
      </template>
    </el-page-header>

    <div v-if="order.id">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card shadow="never" class="mb-20">
            <template #header>基本信息</template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="客户名称">{{ order.customer?.company_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="联系电话">{{ order.customer?.contact_phone || '-' }} ({{ order.customer?.contact_name }})</el-descriptions-item>
              <el-descriptions-item label="设备名称">{{ order.equipment?.name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="设备大类">{{ order.equipment?.category || '-' }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card shadow="never" class="mb-20" v-if="order.checkin_time">
            <template #header>现场打卡信息</template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="打卡时间">{{ order.checkin_time }}</el-descriptions-item>
              <el-descriptions-item label="打卡地址">{{ order.checkin_address }}</el-descriptions-item>
            </el-descriptions>
            <div class="photo-container" v-if="order.checkin_photo">
              <span class="photo-title">到场照片：</span>
              <el-image 
                :src="order.checkin_photo" 
                :preview-src-list="[order.checkin_photo]"
                fit="cover" 
                class="photo-item"
              />
            </div>
          </el-card>

          <el-card shadow="never" class="mb-20" v-if="order.status === 'COMPLETED' || order.status === 'WAITING_SIGN'">
            <template #header>维护反馈与结论</template>
            <div class="desc-content"><strong>问题描述：</strong><br/>{{ order.problem_description || '无' }}</div>
            <div class="desc-content"><strong>解决措施：</strong><br/>{{ order.solution || '无' }}</div>
            
            <div class="photo-container mt-20" v-if="order.photo_urls && order.photo_urls.length > 0">
              <span class="photo-title">现场照片瀑布流：</span>
              <div class="photo-wall">
                <el-image 
                  v-for="(url, index) in order.photo_urls" 
                  :key="index"
                  :src="url" 
                  :preview-src-list="order.photo_urls"
                  fit="cover" 
                  class="photo-wall-item"
                />
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="never" class="mb-20">
            <template #header>业务与派单</template>
            <div class="side-info">
              <p><strong>计划日期：</strong> {{ order.plan_date || '-' }}</p>
              <p><strong>负责工程师：</strong> {{ order.technician?.name || '-' }}</p>
              <p><strong>进度状态：</strong> {{ getStatusLabel(order.status) }}</p>
            </div>
          </el-card>

          <el-card shadow="never" class="mb-20" v-if="order.sign_url">
            <template #header>客户电子签名</template>
            <el-image 
              :src="order.sign_url" 
              :preview-src-list="[order.sign_url]"
              fit="contain" 
              style="width: 100%; height: 150px; background-color: #f9f9f9;"
            />
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getOrderDetail } from '@/api/order'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)
const order = ref({})

const loadData = async () => {
  const id = route.params.id
  if (!id) return
  
  loading.value = true
  try {
    const res = await getOrderDetail(id)
    order.value = res || {}
  } catch (err) {
    console.error(err)
    // mock fallback format
    order.value = {
        id: 1,
        status: 'PENDING',
        customer: { company_name: '测试客户' },
        equipment: { name: '起重机' },
        technician: { name: 'admin' }
    }
  } finally {
    loading.value = false
  }
}

const hasRole = (roles) => {
  return roles.includes(authStore.user?.role)
}

const getStatusType = (status) => {
  const map = {
    'PENDING': 'warning',
    'IN_PROGRESS': 'primary',
    'WAITING_SIGN': 'success',
    'COMPLETED': 'success',
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    'PENDING': '待处理',
    'IN_PROGRESS': '进行中',
    'WAITING_SIGN': '待签字',
    'COMPLETED': '已完成',
  }
  return map[status] || status
}

const goBack = () => {
  router.push('/orders')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.mb-20 {
  margin-bottom: 20px;
}
.mt-20 {
  margin-top: 20px;
}
.photo-container {
  margin-top: 15px;
}
.photo-title {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
}
.photo-item {
  width: 150px;
  height: 150px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
}
.desc-content {
  line-height: 1.6;
  margin-bottom: 15px;
  white-space: pre-wrap;
}
.photo-wall {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.photo-wall-item {
  width: 120px;
  height: 120px;
  border-radius: 4px;
  border: 1px solid #ddd;
}
.side-info p {
  margin: 10px 0;
  color: #606266;
}
</style>