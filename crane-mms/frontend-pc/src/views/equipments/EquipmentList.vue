<template>
  <div class="workspace-page equipment-page">
    <section class="workspace-hero">
      <div class="workspace-hero__body">
        <p class="workspace-kicker">Equipment Registry</p>
        <h2 class="workspace-title">设备资产、检验周期与模板录入集中查看</h2>
        <p class="workspace-description">
          把设备档案、客户归属、模板适配和检验风险放到同一视图中管理，减少新增设备与后续派工的切换成本。
        </p>
        <div class="workspace-badges">
          <span class="soft-pill">在册设备 {{ equipmentList.length }}</span>
          <span class="soft-pill">30 天内到检 {{ dueSoonCount }}</span>
          <span class="soft-pill">客户覆盖 {{ customerCoverage }}</span>
        </div>
      </div>
      <div class="workspace-hero__aside">
        <div class="workspace-aside-card">
          <span class="workspace-aside-card__label">录入模式</span>
          <span class="workspace-aside-card__value">模板驱动</span>
          <span class="workspace-aside-card__meta">先命中模板，再补充厂家与个性化参数</span>
        </div>
        <div class="workspace-actions">
          <el-button v-if="canVisitTemplateCenter" @click="goTemplateCenter">设备模板中心</el-button>
          <el-button type="primary" @click="handleCreate">新增设备</el-button>
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
            <h3 class="surface-panel__title">设备台账总览</h3>
            <p class="surface-panel__subtitle">支持按客户与关键词筛选，快速进入设备档案、派单或模板补录流程。</p>
          </div>
        </div>
        <div class="surface-panel__body">
          <div class="filter-strip">
            <el-input
              v-model="searchForm.keyword"
              class="filter-strip__grow"
              placeholder="搜索设备名称或出厂编号"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
            <el-select
              v-model="searchForm.customer_id"
              placeholder="归属客户"
              clearable
              style="width: 220px"
              @change="handleSearch"
            >
              <el-option v-for="item in customerOptions" :key="item.id" :label="item.company_name" :value="item.id" />
            </el-select>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </div>

          <div class="table-caption">
            <span>重点关注临近检验设备，它们会在表格中高亮提示。</span>
            <strong>共 {{ equipmentList.length }} 台设备</strong>
          </div>

          <el-table
            v-loading="loading"
            :data="equipmentList"
            style="width: 100%"
            :row-class-name="tableRowClassName"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="设备资产信息" min-width="280">
              <template #default="{ row }">
                <div class="equip-info-cell">
                  <div class="equip-name">{{ row.name }}</div>
                  <div class="equip-code">{{ row.asset_qr_code ? `编号：${row.asset_qr_code}` : '暂无出厂编号' }}</div>
                  <div class="equip-tags">
                    <el-tag size="small" type="info">{{ row.category || '起重设备' }}</el-tag>
                    <el-tag size="small" v-if="row.model_type">{{ row.model_type }}</el-tag>
                    <el-tag size="small" type="warning" v-if="row.tonnage">{{ row.tonnage }}</el-tag>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="归属客户" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">{{ row.customer?.company_name || '—' }}</template>
            </el-table-column>
            <el-table-column label="当前状态" width="110">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status || '正常' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="检验与维保窗口" min-width="220">
              <template #default="{ row }">
                <div class="date-info">
                  <div class="date-row">
                    <span class="label">安装日期</span>
                    <span>{{ formatDate(row.install_date) }}</span>
                  </div>
                  <div class="date-row" :class="getNextInspectClass(row.next_inspect_date)">
                    <span class="label">下次定检</span>
                    <strong>{{ formatDate(row.next_inspect_date) }}</strong>
                    <el-tooltip v-if="isNearingInspection(row.next_inspect_date)" content="距离下次定检不足 30 天" placement="top">
                      <el-icon class="warning-icon"><Warning /></el-icon>
                    </el-tooltip>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="190" fixed="right" align="center">
              <template #default="{ row }">
                <div class="action-btns">
                  <el-button link type="primary" @click="goToDetail(row.id)">档案</el-button>
                  <el-button link type="success" @click="handleCreateOrder(row)">派单</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </article>

      <div class="surface-grid">
        <article class="surface-panel surface-panel--dark">
          <div class="surface-panel__header">
            <div>
              <h3 class="surface-panel__title">检验压力</h3>
              <p class="surface-panel__subtitle">将设备到检节点翻译成明确的运营预警。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div class="data-rail">
              <div v-for="item in inspectionSignals" :key="item.label" class="data-rail__item">
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
              <h3 class="surface-panel__title">最近到检设备</h3>
              <p class="surface-panel__subtitle">优先处理距离检验时间最近的设备，减少超期风险。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div v-if="upcomingInspections.length" class="data-rail">
              <div v-for="row in upcomingInspections" :key="row.id" class="data-rail__item">
                <div class="stacked-text">
                  <strong>{{ row.name }}</strong>
                  <span>{{ row.customer?.company_name || '未关联客户' }} · {{ formatDate(row.next_inspect_date) }}</span>
                </div>
                <el-button type="primary" link @click="goToDetail(row.id)">查看</el-button>
              </div>
            </div>
            <el-empty v-else description="暂无临近检验设备" />
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Warning } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'
import { SETTINGS_PERMISSIONS } from '@/constants/permissions'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const equipmentList = ref([])
const customerOptions = ref([])

const searchForm = ref({
  keyword: '',
  customer_id: ''
})

const canVisitTemplateCenter = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_ACCESS))
const dueSoonCount = computed(() => equipmentList.value.filter((item) => isNearingInspection(item.next_inspect_date)).length)
const overdueCount = computed(() => equipmentList.value.filter((item) => {
  if (!item.next_inspect_date) return false
  return dayjs(item.next_inspect_date).diff(dayjs(), 'day') < 0
}).length)
const customerCoverage = computed(() => new Set(equipmentList.value.map((item) => item.customer_id).filter(Boolean)).size)

const summaryCards = computed(() => [
  { label: '设备总量', value: equipmentList.value.length, hint: '当前台账中的全部设备资产' },
  { label: '30 天内到检', value: dueSoonCount.value, hint: '建议提前安排检验与派工准备' },
  { label: '已超期', value: overdueCount.value, hint: '需要优先跟进的高风险设备' },
  { label: '客户覆盖', value: customerCoverage.value, hint: '当前设备所覆盖的客户主体数量' }
])

const inspectionSignals = computed(() => [
  {
    label: '到检预警',
    value: `${dueSoonCount.value} 台`,
    description: '距离下次定检不足 30 天的设备数量。',
    tone: dueSoonCount.value ? 'warning' : 'success'
  },
  {
    label: '超期设备',
    value: `${overdueCount.value} 台`,
    description: '已超过定检日期，建议优先安排处理或确认状态。',
    tone: overdueCount.value ? 'danger' : 'success'
  },
  {
    label: '模板录入',
    value: canVisitTemplateCenter.value ? '已开放' : '未授权',
    description: '设备模板中心可帮助后续新增设备时自动预填充。',
    tone: canVisitTemplateCenter.value ? 'success' : ''
  }
])

const upcomingInspections = computed(() => equipmentList.value
  .filter((item) => item.next_inspect_date)
  .slice()
  .sort((a, b) => dayjs(a.next_inspect_date).valueOf() - dayjs(b.next_inspect_date).valueOf())
  .slice(0, 5))

const fetchEquipments = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.value.keyword) params.search = searchForm.value.keyword
    if (searchForm.value.customer_id) params.customer_id = searchForm.value.customer_id
    const res = await request.get('/equipments', { params })
    equipmentList.value = res || []
  } catch (error) {
    ElMessage.error(error.message || '获取设备列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCustomers = async () => {
  try {
    const res = await request.get('/customers')
    customerOptions.value = res || []
  } catch (error) {
    customerOptions.value = []
  }
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

const goTemplateCenter = () => {
  router.push('/equipment-templates')
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
    正常: 'success',
    故障: 'danger',
    待检: 'warning',
    已停用: 'info'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return dayjs(dateStr).format('YYYY-MM-DD')
}

const isNearingInspection = (dateStr) => {
  if (!dateStr) return false
  const diffDays = dayjs(dateStr).diff(dayjs(), 'day')
  return diffDays <= 30 && diffDays >= -365
}

const getNextInspectClass = (dateStr) => {
  if (!dateStr) return ''
  const diffDays = dayjs(dateStr).diff(dayjs(), 'day')
  if (diffDays < 0) return 'text-danger'
  if (diffDays <= 15) return 'text-danger'
  if (diffDays <= 30) return 'text-warning'
  return 'text-normal'
}

const tableRowClassName = ({ row }) => {
  if (isNearingInspection(row.next_inspect_date)) {
    return 'warning-row'
  }
  return ''
}
</script>

<style scoped>
.equip-info-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.equip-name {
  font-size: 15px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.equip-code {
  color: var(--color-text-placeholder);
  font-size: 12px;
  font-family: Consolas, monospace;
}

.equip-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
}

.date-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-row .label {
  min-width: 60px;
  color: var(--color-text-secondary);
}

.text-danger {
  color: var(--color-danger);
}

.text-warning {
  color: var(--color-warning);
}

.text-normal {
  color: var(--color-text-regular);
}

.warning-icon {
  color: var(--color-danger);
}

.action-btns {
  display: flex;
  justify-content: center;
  gap: 8px;
}

:deep(.warning-row) {
  --el-table-tr-bg-color: #fff7f0;
}

:deep(.warning-row:hover > td.el-table__cell) {
  background-color: #fff1e6 !important;
}
</style>
