<template>
  <div class="customer-detail">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" circle class="back-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </el-button>
        <div class="title-group">
          <h1 class="page-title">{{ customerInfo.company_name || '加载中...' }}</h1>
          <p class="page-subtitle">客户编号: #{{ customerId }} · 档案详情与关联设备</p>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="goToEquipmentForm">
          <span class="btn-icon">＋</span> 新建设备
        </el-button>
      </div>
    </div>

    <!-- 概览统计 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">关联设备总数</div>
        <div class="stat-value primary">{{ customerInfo.equipments?.length || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">联系人数量</div>
        <div class="stat-value success">{{ (customerInfo.contacts?.length || 0) + 1 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">最近维保记录</div>
        <div class="stat-value">暂无</div>
      </div>
    </div>

    <!-- 客户基本信息卡片 -->
    <el-card class="info-card" v-loading="loading">
      <template #header>
        <div class="card-header-simple">
          <span class="header-icon">🏢</span>
          基本资料
        </div>
      </template>
      
      <el-descriptions :column="3" border class="custom-descriptions">
        <el-descriptions-item label="公司全称" :span="2">
          <span class="desc-value bold">{{ customerInfo.company_name || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="主联系人">
          <span class="desc-value">{{ customerInfo.contact_name || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="联系电话">
          <span class="desc-value phone">{{ customerInfo.contact_phone || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="详细地址" :span="2">
          <span class="desc-value">{{ customerInfo.address || '-' }}</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 其他联系人表格 -->
      <div class="contacts-section" v-if="customerInfo.contacts && customerInfo.contacts.length > 0">
        <div class="section-title">其他业务联系人</div>
        <el-table :data="customerInfo.contacts" style="width: 100%" size="small" class="mini-table">
          <el-table-column prop="name" label="姓名" width="150" />
          <el-table-column prop="phone" label="联系电话" width="180" />
          <el-table-column prop="role" label="职位/角色">
            <template #default="{ row }">
              <el-tag size="small" type="info" effect="plain">{{ row.role || '业务配合' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 设备列表卡片 -->
    <div class="table-card" style="margin-top: 24px">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="header-icon">🏗️</span>
          <span class="toolbar-title">名下设备档案</span>
        </div>
        <div class="toolbar-right">
          <span class="total-hint">共 {{ customerInfo.equipments?.length || 0 }} 台设备</span>
        </div>
      </div>
      
      <el-table :data="customerInfo.equipments || []" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="设备名称" min-width="150">
          <template #default="{ row }">
            <span class="equipment-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="model_type" label="型式" width="100" />
        <el-table-column label="参数 (吨位/跨度)" width="160">
          <template #default="{ row }">
            <span class="param-tag">{{ row.tonnage || '-' }}</span>
            <span class="param-divider">/</span>
            <span class="param-tag">{{ row.span || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="installation_location" label="安装位置" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editEquipment(row.id)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && (!customerInfo.equipments || customerInfo.equipments.length === 0)" class="empty-state">
        <div class="empty-icon">⚙️</div>
        <div class="empty-text">暂无关联设备</div>
        <el-button type="primary" plain size="small" @click="goToEquipmentForm">立即添加设备</el-button>
      </div>
    </div>
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

const goBack = () => router.push('/customers')
const goToEquipmentForm = () => router.push(`/equipments/form?customerId=${customerId}`)
const editEquipment = (equipmentId) => router.push(`/equipments/form/${equipmentId}`)

onMounted(loadDetail)
</script>

<style scoped>
.customer-detail { padding: 0; }

.header-left { display: flex; align-items: center; gap: 16px; }
.back-btn { 
  border-color: var(--color-border); 
  color: var(--color-text-secondary);
  transition: var(--transition-fast);
}
.back-btn:hover {
  background: var(--color-bg-card);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.title-group { line-height: 1.2; }

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border-light);
}
.stat-label { font-size: 12px; color: var(--color-text-secondary); margin-bottom: 8px; font-weight: 500; }
.stat-value { font-size: 24px; font-weight: 800; color: var(--color-text-primary); }
.stat-value.primary { color: var(--color-primary); }
.stat-value.success { color: var(--color-success); }

.card-header-simple {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
}
.header-icon { font-size: 18px; }

.custom-descriptions :deep(.el-descriptions__label) {
  background: #fafbfc !important;
  font-weight: 600 !important;
  color: var(--color-text-secondary) !important;
  width: 120px;
}
.desc-value { color: var(--color-text-primary); font-weight: 500; }
.desc-value.bold { font-weight: 700; font-size: 15px; }
.desc-value.phone { font-variant-numeric: tabular-nums; }

.contacts-section { margin-top: 24px; }
.section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
  padding-left: 4px;
  border-left: 3px solid var(--color-primary);
}
.mini-table { border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--color-border-light); }

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
.toolbar-title { font-size: 15px; font-weight: 700; color: var(--color-text-primary); }
.total-hint { font-size: 13px; color: var(--color-text-secondary); }

.equipment-name { font-weight: 600; color: var(--color-text-primary); }
.param-tag { font-variant-numeric: tabular-nums; font-weight: 500; color: var(--color-text-regular); }
.param-divider { color: var(--color-text-placeholder); margin: 0 4px; }

.empty-state { text-align: center; padding: 40px 20px; }
.empty-icon { font-size: 32px; margin-bottom: 8px; }
.empty-text { font-size: 14px; color: var(--color-text-secondary); margin-bottom: 16px; }

.btn-icon { margin-right: 4px; font-weight: 300; }
</style>