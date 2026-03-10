<template>
  <div class="equipment-list-container">
    <div class="header-bar">
      <h2>设备台账总览</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>新增设备
      </el-button>
    </div>

    <!-- 搜索筛选区 -->
    <div class="filter-card card-panel">
      <el-form :inline="true" :model="searchForm" @submit.prevent>
        <el-form-item label="模糊搜索">
          <el-input 
            v-model="searchForm.keyword" 
            placeholder="搜索设备名称或出厂编号" 
            clearable 
            @keyup.enter="handleSearch"
            style="width: 240px"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="归属客户">
          <el-select 
            v-model="searchForm.customer_id" 
            placeholder="全部分类" 
            clearable 
            @change="handleSearch"
            style="width: 200px"
          >
            <el-option 
              v-for="c in customerOptions" 
              :key="c.id" 
              :label="c.company_name" 
              :value="c.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 设备记录表格 -->
    <div class="table-card card-panel">
      <el-table 
        v-loading="loading" 
        :data="equipmentList" 
        style="width: 100%" 
        :row-class-name="tableRowClassName"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="设备资产信息" min-width="260">
          <template #default="{ row }">
            <div class="equip-info-cell">
              <div class="equip-name">{{ row.name }}</div>
              <div class="equip-code" v-if="row.asset_qr_code">编号：{{ row.asset_qr_code }}</div>
              <div class="equip-tags">
                <el-tag size="small" type="info">{{ row.category || '起重设备' }}</el-tag>
                <el-tag size="small" type="info" v-if="row.model_type">{{ row.model_type }}</el-tag>
                <el-tag size="small" type="warning" v-if="row.tonnage">{{ row.tonnage }}T</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="归属客户" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div>{{ row.customer?.company_name || '—' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="当前状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status || '正常' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="近期与维保情况" min-width="200">
          <template #default="{ row }">
            <div class="date-info">
              <div class="date-row">
                <span class="label">安装日期:</span> 
                <span>{{ formatDate(row.install_date) }}</span>
              </div>
              <div class="date-row" :class="getNextInspectClass(row.next_inspect_date)">
                <span class="label" title="特约年检期限">下次定检:</span> 
                <strong>{{ formatDate(row.next_inspect_date) }}</strong>
                <el-tooltip v-if="isNearingInspection(row.next_inspect_date)" content="距离下次定检不足30天！" placement="top">
                  <el-icon class="warning-icon"><Warning /></el-icon>
                </el-tooltip>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-btns">
              <el-button link type="primary" @click="goToDetail(row.id)">档案</el-button>
              <el-button link type="success" @click="handleCreateOrder(row)">派单</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页预留区 (由于后端暂未返回分页，前端简单显示) -->
      <div class="pagination-wrapper">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="equipmentList.length"
          :page-size="100"
          :current-page="1"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Plus, Warning } from '@element-plus/icons-vue'
import request from '../../utils/request'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const equipmentList = ref([])
const customerOptions = ref([])

const searchForm = ref({
  keyword: '',
  customer_id: ''
})

const fetchEquipments = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.value.keyword) params.search = searchForm.value.keyword
    if (searchForm.value.customer_id) params.customer_id = searchForm.value.customer_id
    
    // 调用现有的 /api/v1/equipments 接口 (注意后端实际已挂载为 /api/v1/equipments)
    const res = await request.get('/equipments', { params })
    equipmentList.value = res || []
  } catch (err) {
    ElMessage.error(err.message || '获取设备列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCustomers = async () => {
  try {
    const res = await request.get('/customers')
    customerOptions.value = res || []
  } catch (err) {}
}

onMounted(() => {
  fetchCustomers()
  fetchEquipments()
})

const handleSearch = () => {
  fetchEquipments()
}

const resetSearch = () => {
  searchForm.value.keyword = ''
  searchForm.value.customer_id = ''
  fetchEquipments()
}

const handleCreate = () => {
  router.push('/equipments/form')
}

const goToDetail = (equipmentId) => {
  router.push(`/equipments/form/${equipmentId}`)
}

const handleCreateOrder = (row) => {
  router.push({
    path: '/orders',
    query: { create_equipment_id: row.id, create_customer_id: row.customer_id }
  })
}

const getStatusType = (status) => {
  const map = {
    '正常': 'success',
    '故障': 'danger',
    '待检': 'warning',
    '已停用': 'info'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return dayjs(dateStr).format('YYYY-MM-DD')
}

// 重点：计算设备是否临近检验（30天内标红）
const isNearingInspection = (dateStr) => {
  if (!dateStr) return false
  const diffDays = dayjs(dateStr).diff(dayjs(), 'day')
  return diffDays <= 30 && diffDays >= -365
}

// 根据临近状态返回不同文字颜色类
const getNextInspectClass = (dateStr) => {
  if (!dateStr) return ''
  const diffDays = dayjs(dateStr).diff(dayjs(), 'day')
  if (diffDays < 0) return 'text-danger' // 已超期
  if (diffDays <= 15) return 'text-danger' // 紧急 (15天内)
  if (diffDays <= 30) return 'text-warning' // 预警 (30天内)
  return 'text-normal'
}

// 给将临期的整行加个弱高亮效果
const tableRowClassName = ({ row }) => {
  if (isNearingInspection(row.next_inspect_date)) {
    return 'warning-row'
  }
  return ''
}
</script>

<style scoped>
.equipment-list-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-bar h2 {
  margin: 0;
  font-size: 20px;
  color: var(--color-text-primary);
  font-weight: 600;
}

.card-panel {
  background: var(--color-bg-panel);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

.filter-card {
  padding-bottom: 4px;
}

.equip-info-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.equip-name {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
}
.equip-code {
  font-size: 12px;
  color: #94a3b8;
  font-family: monospace;
}
.equip-tags {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}

.date-info {
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.date-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.date-row .label {
  color: #64748b;
  width: 65px;
  flex-shrink: 0;
}
.text-danger { color: #ef4444; }
.text-warning { color: #f59e0b; }
.text-normal { color: #334155; }
.warning-icon { color: #ef4444; margin-left: 4px; }

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.action-btns {
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* 临近特检整行高亮指示 */
:deep(.warning-row) {
  --el-table-tr-bg-color: #fffbfa;
}
:deep(.warning-row:hover > td.el-table__cell) {
  background-color: #fff1f0 !important;
}
</style>
