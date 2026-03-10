<template>
  <div class="batch-schedule">
    <div class="page-header" style="margin-bottom: 24px;">
      <div>
        <h1 class="page-title">月度批量排期</h1>
        <p class="page-subtitle">快速为多台设备同时生成例行维保工单，一键派单到位</p>
      </div>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：配置面板 -->
      <el-col :span="10">
        <el-card shadow="never" style="margin-bottom: 16px;">
          <template #header>
            <div style="font-weight: 600;">① 排期基本设置</div>
          </template>
          <el-form label-position="top">
            <el-form-item label="工单类型（统一）">
              <el-select v-model="batchForm.order_type" style="width:100%">
                <el-option label="月检" value="月检" />
                <el-option label="季检" value="季检" />
                <el-option label="年检" value="年检" />
                <el-option label="周检" value="周检" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认计划日期">
              <el-date-picker v-model="defaultDate" type="date" value-format="YYYY-MM-DD" style="width:100%" placeholder="点击后各设备自动填充此日期" @change="applyDefaultDate" />
            </el-form-item>
            <el-form-item label="默认派工工程师">
              <el-select v-model="defaultTechnician" filterable placeholder="选择后自动填充各行" style="width:100%" @change="applyDefaultTechnician">
                <el-option v-for="t in technicians" :key="t.id" :label="`${t.name} (${t.username})`" :value="t.id" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never">
          <template #header>
            <div style="font-weight: 600; display:flex; justify-content:space-between; align-items:center;">
              <span>② 选择要排期的设备</span>
              <el-button type="primary" text size="small" @click="loadEquipments">🔄 刷新列表</el-button>
            </div>
          </template>
          <el-input v-model="equipSearch" placeholder="搜索设备名称或客户" clearable style="margin-bottom:12px;" :prefix-icon="Search" />
          <div class="equip-select-list" style="max-height: 380px; overflow-y: auto;">
            <div
              v-for="e in filteredEquipments"
              :key="e.id"
              class="equip-item"
              :class="{ selected: isSelected(e.id) }"
              @click="toggleEquipment(e)"
            >
              <div class="equip-name">{{ e.name }}</div>
              <div class="equip-meta">{{ e.customer_name }} · {{ e.category }}</div>
              <el-icon class="check-icon" v-if="isSelected(e.id)"><Check /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：已选/待排期列表 -->
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div style="font-weight: 600; display:flex; justify-content:space-between; align-items:center;">
              <span>③ 确认排期明细（已选 {{ selectedItems.length }} 台）</span>
              <el-button type="primary" @click="submitBatch" :loading="submitting" :disabled="selectedItems.length === 0">
                🚀 一键提交全部排期
              </el-button>
            </div>
          </template>

          <div v-if="selectedItems.length === 0" style="text-align:center; padding:40px; color:#bbb;">
            <div style="font-size: 36px; margin-bottom: 12px;">📋</div>
            <div>请在左侧点选需要安排维保的设备</div>
          </div>

          <div v-else>
            <div v-for="(item, index) in selectedItems" :key="item.equipment_id" class="schedule-row">
              <el-row :gutter="12" align="middle">
                <el-col :span="7">
                  <div class="equip-label">
                    <strong>{{ item.equipment_name }}</strong>
                    <div style="font-size:12px;color:#999;">{{ item.customer_name }}</div>
                  </div>
                </el-col>
                <el-col :span="7">
                  <el-date-picker
                    v-model="item.plan_date"
                    type="date"
                    value-format="YYYY-MM-DD"
                    size="small"
                    style="width:100%"
                    placeholder="维保日期"
                  />
                </el-col>
                <el-col :span="8">
                  <el-select v-model="item.technician_id" filterable size="small" style="width:100%" placeholder="指派工程师">
                    <el-option v-for="t in technicians" :key="t.id" :label="t.name" :value="t.id" />
                  </el-select>
                </el-col>
                <el-col :span="2" style="text-align:center;">
                  <el-button type="danger" circle size="small" @click="removeItem(index)">
                    <el-icon><Close /></el-icon>
                  </el-button>
                </el-col>
              </el-row>
            </div>
          </div>

          <!-- 批量提交结果 -->
          <el-alert
            v-if="batchResult"
            style="margin-top: 16px;"
            :title="`✅ 成功创建 ${batchResult.created_count} 条工单，跳过 ${batchResult.skipped_count} 条（已存在未完成工单）`"
            type="success"
            show-icon
            :closable="false"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Check, Close, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getEquipments } from '@/api/equipment'
import { getUsers } from '@/api/user'
import request from '@/utils/request'

const equipSearch = ref('')
const equipments = ref([])
const technicians = ref([])
const selectedItems = ref([])
const defaultDate = ref('')
const defaultTechnician = ref(null)
const submitting = ref(false)
const batchResult = ref(null)

const batchForm = ref({
  order_type: '月检'
})

const filteredEquipments = computed(() => {
  if (!equipSearch.value) return equipments.value
  const q = equipSearch.value.toLowerCase()
  return equipments.value.filter(e =>
    e.name?.toLowerCase().includes(q) ||
    e.customer_name?.toLowerCase().includes(q)
  )
})

const isSelected = (id) => selectedItems.value.some(i => i.equipment_id === id)

const toggleEquipment = (e) => {
  const idx = selectedItems.value.findIndex(i => i.equipment_id === e.id)
  if (idx >= 0) {
    selectedItems.value.splice(idx, 1)
  } else {
    selectedItems.value.push({
      equipment_id: e.id,
      customer_id: e.customer_id,
      equipment_name: e.name,
      customer_name: e.customer_name,
      plan_date: defaultDate.value || '',
      technician_id: defaultTechnician.value || null
    })
  }
}

const removeItem = (index) => {
  selectedItems.value.splice(index, 1)
}

const applyDefaultDate = (val) => {
  selectedItems.value.forEach(i => { i.plan_date = val })
}

const applyDefaultTechnician = (val) => {
  selectedItems.value.forEach(i => { i.technician_id = val })
}

const loadEquipments = async () => {
  try {
    const res = await getEquipments()
    equipments.value = res || []
  } catch {}
}

const loadTechnicians = async () => {
  try {
    const res = await getUsers({ skip: 0, limit: 100 })
    technicians.value = (res?.items || []).filter(u => u.role === 'TECH')
  } catch {}
}

const submitBatch = async () => {
  const invalid = selectedItems.value.filter(i => !i.plan_date || !i.technician_id)
  if (invalid.length > 0) {
    ElMessage.warning(`有 ${invalid.length} 条记录尚未填写日期或工程师，请补全后再提交`)
    return
  }

  submitting.value = true
  batchResult.value = null
  try {
    const payload = {
      order_type: batchForm.value.order_type,
      items: selectedItems.value.map(i => ({
        equipment_id: i.equipment_id,
        customer_id: i.customer_id,
        technician_id: i.technician_id,
        plan_date: i.plan_date
      }))
    }
    const res = await request.post('/orders/batch', payload)
    batchResult.value = res
    ElMessage.success(`🎉 批量排期完成！成功创建 ${res.created_count} 条工单`)
    selectedItems.value = []
  } catch (err) {
    ElMessage.error('提交失败，请检查数据')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadEquipments()
  loadTechnicians()
})
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; margin: 0 0 6px; }
.page-subtitle { font-size: 14px; color: #888; margin: 0; }

.equip-item {
  display: flex;
  flex-direction: column;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  background: #f9fafb;
  position: relative;
  transition: all .2s;
}
.equip-item:hover { background: #eef5ff; border-color: #c2d9ff; }
.equip-item.selected { background: #e6f4ff; border-color: #1677ff; }
.equip-name { font-weight: 600; font-size: 14px; color: #222; }
.equip-meta { font-size: 12px; color: #888; margin-top: 2px; }
.check-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #1677ff; font-size: 16px; }

.schedule-row {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}
.schedule-row:last-child { border-bottom: none; }
.equip-label strong { font-size: 13px; }
</style>
