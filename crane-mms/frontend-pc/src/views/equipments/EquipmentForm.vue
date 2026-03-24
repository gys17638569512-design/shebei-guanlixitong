<template>
  <div class="equipment-form">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" circle class="back-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </el-button>
        <div class="title-group">
          <h1 class="page-title">{{ isEdit ? '编辑设备档案' : '新建设备档案' }}</h1>
          <p class="page-subtitle">{{ isEdit ? '修改现有设备、模板来源与检修建议项' : '录入设备基础信息，并在命中模板后快速套用标准参数、部件和检修项' }}</p>
        </div>
      </div>
    </div>

    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="form-wrapper" v-loading="loading">
      <div class="form-card">
        <div class="card-section-title"><span class="icon">🏗️</span> 基础身份</div>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="设备大类" prop="category">
              <el-select v-model="form.category" @change="handleCategoryChange" style="width: 100%">
                <el-option v-for="item in categories" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="设备型式" prop="model_type">
              <el-select v-model="form.model_type" :disabled="!form.category" style="width: 100%">
                <el-option v-for="item in availableModelTypes" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="厂家版本">
              <el-input v-model="form.manufacturer" placeholder="留空则按通用版匹配" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="设备名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <div class="form-card">
        <div class="card-section-title"><span class="icon">📐</span> 关键技术参数</div>
        <el-row :gutter="20">
          <el-col :span="6"><el-form-item label="吨位" prop="tonnage"><el-input v-model="form.tonnage" placeholder="例: 10t" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="跨度" prop="span"><el-input v-model="form.span" placeholder="例: 16.5m" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="起升高度"><el-input v-model="form.lifting_height" placeholder="例: 9m" /></el-form-item></el-col>
          <el-col :span="6">
            <el-form-item label="工作级别">
              <el-select v-model="form.work_class" style="width: 100%">
                <el-option v-for="v in ['A3','A4','A5','A6','A7','A8']" :key="v" :label="v" :value="v" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="安装/运行位置">
          <el-input v-model="form.installation_location" placeholder="例如: 总装二号车间 3号线" />
        </el-form-item>
      </div>

      <div class="form-card template-card">
        <div class="card-section-title flex-between">
          <span><span class="icon">🧠</span> 模板匹配摘要</span>
          <el-button v-if="canVisitTemplateCenter" text type="primary" @click="goTemplateCenter">前往模板中心</el-button>
        </div>
        <div v-if="matchState.loading" class="match-state loading">正在根据设备参数匹配模板...</div>
        <div v-else-if="matchState.data?.matched" class="match-state matched">
          <div class="match-main">
            <div>
              <div class="match-title">{{ matchState.data.template_name }}</div>
              <div class="match-subtitle">
                已命中 {{ matchState.data.manufacturer || '通用版' }} · 版本 {{ matchState.data.version }}
              </div>
            </div>
            <div class="match-tags">
              <el-tag type="success">{{ matchState.data.parts?.length || 0 }} 个部件</el-tag>
              <el-tag type="warning">{{ matchState.data.inspection_items?.length || 0 }} 个检修项</el-tag>
            </div>
          </div>
          <div class="match-actions">
            <el-button @click="previewDialogVisible = true">预览模板</el-button>
            <el-button type="primary" @click="applyMatchedTemplate">应用模板</el-button>
          </div>
        </div>
        <div v-else class="match-state empty">
          {{ matchState.message || '先填写设备大类、型式、吨位、跨度和厂家后，系统会自动尝试推荐模板。' }}
        </div>
      </div>

      <div class="form-card">
        <div class="card-section-title"><span class="icon">📅</span> 维保与特检计划</div>
        <el-row :gutter="20">
          <el-col :span="8"><el-form-item label="上次特检日期"><el-date-picker v-model="form.last_inspection_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="下次特检预警日"><el-date-picker v-model="form.next_inspection_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="质保到期日"><el-date-picker v-model="form.warranty_end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
        </el-row>
      </div>

      <div class="form-card">
        <div class="card-section-title flex-between">
          <span><span class="icon">🛠️</span> 建议检修项</span>
          <el-button type="primary" link @click="addInspectionItem">新增检修项</el-button>
        </div>
        <el-table :data="form.inspection_items" size="small" border>
          <el-table-column label="检修项" min-width="180"><template #default="{ row }"><el-input v-model="row.item_name" /></template></el-table-column>
          <el-table-column label="说明" min-width="260"><template #default="{ row }"><el-input v-model="row.description" /></template></el-table-column>
          <el-table-column label="必检" width="90" align="center"><template #default="{ row }"><el-switch v-model="row.required" /></template></el-table-column>
          <el-table-column width="90" align="center"><template #default="{ $index }"><el-button link type="danger" @click="removeInspectionItem($index)">删除</el-button></template></el-table-column>
        </el-table>
      </div>

      <div class="form-card parts-card">
        <div class="card-section-title flex-between">
          <span><span class="icon">🔩</span> 核心部件清单</span>
          <el-button type="primary" link @click="addPart">新增部件</el-button>
        </div>
        <el-table :data="form.parts" size="small" border>
          <el-table-column label="部件名称" min-width="180"><template #default="{ row }"><el-input v-model="row.part_name" /></template></el-table-column>
          <el-table-column label="详细规格/参数" min-width="260"><template #default="{ row }"><el-input v-model="row.specification" /></template></el-table-column>
          <el-table-column label="数量" width="120"><template #default="{ row }"><el-input-number v-model="row.quantity" :min="1" style="width: 100%" /></template></el-table-column>
          <el-table-column width="90" align="center"><template #default="{ $index }"><el-button link type="danger" @click="removePart($index)">删除</el-button></template></el-table-column>
        </el-table>
      </div>

      <div class="form-footer">
        <el-checkbox v-model="form.submit_as_template_candidate">将本次手工补录内容提交为模板候选</el-checkbox>
        <div class="footer-actions">
          <el-button @click="goBack" size="large" style="width: 120px">取消</el-button>
          <el-button type="primary" size="large" @click="submitForm" :loading="submitLoading" style="width: 220px">
            {{ isEdit ? '保存所有修改' : '确认并录入档案' }}
          </el-button>
        </div>
      </div>
    </el-form>

    <el-dialog v-model="previewDialogVisible" title="模板预览" width="860px">
      <div v-if="matchState.data" class="preview-shell">
        <div class="preview-card">
          <h3>默认参数</h3>
          <pre>{{ prettyJson(matchState.data.default_params) }}</pre>
        </div>
        <div class="preview-card">
          <h3>核心部件</h3>
          <pre>{{ prettyJson(matchState.data.parts) }}</pre>
        </div>
        <div class="preview-card full">
          <h3>建议检修项</h3>
          <pre>{{ prettyJson(matchState.data.inspection_items) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createEquipment, getEquipmentDetail, updateEquipment } from '@/api/equipment'
import { matchEquipmentTemplate } from '@/api/equipmentTemplate'
import { useAuthStore } from '@/stores/auth'
import { SETTINGS_PERMISSIONS } from '@/constants/permissions'

const categories = ['桥式起重机', '门式起重机', '悬臂起重机']
const typeMap = {
  '桥式起重机': ['QD型', 'LDA型', 'LH型', 'QZ型'],
  '门式起重机': ['MH型', 'MG型', 'BMH型'],
  '悬臂起重机': ['BZ型', 'BZD型']
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isEdit = computed(() => !!route.params.id)
const equipmentId = route.params.id
const customerId = route.query.customerId
const loading = ref(false)
const submitLoading = ref(false)
const previewDialogVisible = ref(false)
const formRef = ref(null)
let matchTimer = null

const form = reactive({
  customer_id: customerId || null,
  category: '',
  model_type: '',
  name: '',
  manufacturer: '',
  tonnage: '',
  span: '',
  lifting_height: '',
  work_class: 'A5',
  installation_location: '',
  last_inspection_date: null,
  next_inspection_date: null,
  warranty_end_date: null,
  inspection_items: [],
  parts: [],
  applied_template_id: null,
  applied_template_version: null,
  submit_as_template_candidate: false
})

const matchState = reactive({
  loading: false,
  data: null,
  message: ''
})

const rules = {
  category: [{ required: true, message: '请选择大类', trigger: 'change' }],
  model_type: [{ required: true, message: '请选择型式', trigger: 'change' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  tonnage: [{ required: true, message: '请输入吨位', trigger: 'blur' }],
  span: [{ required: true, message: '请输入跨度', trigger: 'blur' }]
}

const availableModelTypes = computed(() => typeMap[form.category] || [])
const canVisitTemplateCenter = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_ACCESS))

const resetMatchState = (message = '') => {
  matchState.loading = false
  matchState.data = null
  matchState.message = message
}

const handleCategoryChange = () => {
  form.model_type = ''
}

const addPart = () => form.parts.push({ part_name: '', specification: '', quantity: 1 })
const removePart = (index) => form.parts.splice(index, 1)
const addInspectionItem = () => form.inspection_items.push({ item_name: '', description: '', required: true })
const removeInspectionItem = (index) => form.inspection_items.splice(index, 1)

const fetchTemplateMatch = async () => {
  if (!form.category || !form.model_type || !form.tonnage || !form.span) {
    resetMatchState('先填写设备大类、型式、吨位、跨度和厂家后，系统会自动尝试推荐模板。')
    return
  }
  matchState.loading = true
  try {
    const res = await matchEquipmentTemplate({
      category: form.category,
      model_type: form.model_type,
      tonnage: form.tonnage,
      span: form.span,
      manufacturer: form.manufacturer || undefined
    })
    if (res?.matched) {
      matchState.data = res
      matchState.message = ''
    } else {
      resetMatchState(res?.message || '未命中模板，请继续手工录入。')
    }
  } catch (error) {
    resetMatchState(error.message || '模板匹配失败，请继续手工录入。')
  } finally {
    matchState.loading = false
  }
}

watch(
  () => [form.category, form.model_type, form.tonnage, form.span, form.manufacturer],
  () => {
    clearTimeout(matchTimer)
    matchTimer = setTimeout(fetchTemplateMatch, 300)
  }
)

const applyMatchedTemplate = () => {
  if (!matchState.data?.matched) return
  const defaults = matchState.data.default_params || {}
  form.tonnage = defaults.tonnage || form.tonnage
  form.span = defaults.span || form.span
  form.lifting_height = defaults.lifting_height || form.lifting_height
  form.work_class = defaults.work_class || form.work_class
  form.installation_location = defaults.installation_location || form.installation_location
  form.parts = (matchState.data.parts || []).map(item => ({ part_name: item.part_name, specification: item.specification || '', quantity: item.quantity || 1 }))
  form.inspection_items = (matchState.data.inspection_items || []).map(item => ({ item_name: item.item_name, description: item.description || '', required: item.required !== false }))
  form.applied_template_id = matchState.data.group_id
  form.applied_template_version = matchState.data.version
  ElMessage.success('模板内容已带入当前设备档案')
}

const loadData = async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    const res = await getEquipmentDetail(equipmentId)
    if (res) {
      Object.assign(form, {
        ...res,
        manufacturer: res.manufacturer || '',
        inspection_items: res.inspection_items || [],
        parts: res.parts || []
      })
    }
  } finally {
    loading.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const payload = JSON.parse(JSON.stringify(form))
      if (isEdit.value) {
        await updateEquipment(equipmentId, payload)
        ElMessage.success('设备档案已成功更新')
      } else {
        await createEquipment(payload)
        ElMessage.success('新设备档案录入成功')
      }
      goBack()
    } catch (error) {
      ElMessage.error(error.message || '保存设备档案失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const prettyJson = (value) => JSON.stringify(value || [], null, 2)
const goBack = () => router.back()
const goTemplateCenter = () => router.push('/equipment-templates')

onMounted(async () => {
  if (isEdit.value) await loadData()
  await fetchTemplateMatch()
})
</script>

<style scoped>
.equipment-form { padding: 0; }
.header-left { display: flex; align-items: center; gap: 16px; }
.back-btn { border-color: var(--color-border); color: var(--color-text-secondary); }
.form-wrapper { max-width: 1040px; margin: 0 auto; }
.form-card { background: #fff; border-radius: var(--radius-lg); padding: 24px; margin-bottom: 24px; box-shadow: var(--shadow-sm); border: 1px solid var(--color-border-light); }
.card-section-title { font-size: 15px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 18px; display: flex; align-items: center; gap: 10px; }
.flex-between { justify-content: space-between; }
.icon { font-size: 18px; }
.template-card { background: linear-gradient(180deg, rgba(247, 251, 255, 0.96), rgba(255, 255, 255, 0.98)); }
.match-state { padding: 16px 18px; border-radius: 18px; border: 1px dashed rgba(16, 33, 48, 0.12); color: var(--color-text-secondary); }
.match-state.matched { border-style: solid; background: rgba(231, 245, 255, 0.7); }
.match-main { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.match-title { font-size: 18px; font-weight: 700; color: var(--color-text-primary); }
.match-subtitle { margin-top: 6px; color: var(--color-text-secondary); font-size: 13px; }
.match-tags, .match-actions, .footer-actions { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.match-actions { margin-top: 14px; }
.form-footer { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin: 40px 0 60px; }
.preview-shell { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.preview-card { padding: 16px; border-radius: 18px; background: rgba(247,250,252,.92); border: 1px solid rgba(16,33,48,.08); }
.preview-card.full { grid-column: 1 / -1; }
.preview-card h3 { margin: 0 0 10px; font-size: 15px; color: var(--color-text-primary); }
pre { margin: 0; padding: 12px 14px; border-radius: 14px; background: rgba(15,23,42,.9); color: #eaf4ff; font-size: 12px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
:deep(.el-form-item__label) { font-size: 13px !important; color: var(--color-text-secondary) !important; margin-bottom: 6px !important; }
@media (max-width: 960px) { .form-footer, .match-main, .preview-shell { grid-template-columns: 1fr; flex-direction: column; align-items: flex-start; } }
</style>
