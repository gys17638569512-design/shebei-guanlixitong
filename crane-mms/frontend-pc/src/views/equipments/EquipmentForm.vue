<template>
  <div class="equipment-form">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" circle class="back-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </el-button>
        <div class="title-group">
          <h1 class="page-title">{{ isEdit ? '编辑设备档案' : '新建设备档案' }}</h1>
          <p class="page-subtitle">{{ isEdit ? '修改现有设备的详细技术参数与部件清单' : '录入新设备的基础信息及核心技术参数' }}</p>
        </div>
      </div>
    </div>

    <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="form-wrapper" v-loading="loading">
      
      <!-- 第一部分：基础信息 -->
      <div class="form-card">
        <div class="card-section-title">
          <span class="icon">🏗️</span> 基础类别与名称
        </div>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="设备大类" prop="category">
              <el-select v-model="form.category" placeholder="请选择" @change="handleCategoryChange" style="width: 100%">
                <el-option label="桥式起重机" value="桥式起重机" />
                <el-option label="门式起重机" value="门式起重机" />
                <el-option label="悬臂起重机" value="悬臂起重机" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="设备型式" prop="model_type">
              <el-select v-model="form.model_type" placeholder="请先选择大类" style="width: 100%" :disabled="!form.category">
                <el-option v-for="type in availableModelTypes" :key="type" :label="type" :value="type" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="设备名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 第二部分：技术参数 -->
      <div class="form-card">
        <div class="card-section-title">
          <span class="icon">📐</span> 关键技术参数
        </div>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="吨位 (Tonnage)" prop="tonnage">
              <el-input v-model="form.tonnage" placeholder="例: 10t" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="跨度 (Span)" prop="span">
              <el-input v-model="form.span" placeholder="例: 16.5m" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="起升高度" prop="lifting_height">
              <el-input v-model="form.lifting_height" placeholder="例: 9m" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="工作级别" prop="work_class">
              <el-select v-model="form.work_class" placeholder="选择" style="width: 100%">
                <el-option v-for="v in ['A3','A4','A5','A6','A7','A8']" :key="v" :label="v" :value="v" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="安装/运行位置" prop="installation_location">
          <el-input v-model="form.installation_location" placeholder="例如: 总装二号车间 3号线" />
        </el-form-item>
      </div>

      <!-- 第三部分：特检日期 -->
      <div class="form-card">
        <div class="card-section-title">
          <span class="icon">📅</span> 维保与特检计划
        </div>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="上次特检日期" prop="last_inspection_date">
              <el-date-picker v-model="form.last_inspection_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="下次特检预警日" prop="next_inspection_date">
              <el-date-picker v-model="form.next_inspection_date" type="date" placeholder="预警日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="质保到期日" prop="warranty_end_date">
              <el-date-picker v-model="form.warranty_end_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 第四部分：部件清单 -->
      <div class="form-card parts-card">
        <div class="card-section-title flex-between">
          <span><span class="icon">🔩</span> 核心部件清单</span>
          <el-button type="success" size="small" plain @click="fetchTemplates" :loading="templateLoading">
            ✨ 智能填充部件模板
          </el-button>
        </div>
        
        <div class="parts-table-wrapper">
          <el-table :data="form.parts" style="width: 100%" size="small">
            <el-table-column label="部件名称" width="220">
              <template #default="{ row }">
                <el-input v-model="row.part_name" placeholder="部件名" />
              </template>
            </el-table-column>
            <el-table-column label="详细规格/参数">
              <template #default="{ row }">
                <el-input v-model="row.specification" placeholder="如: Ф16mm, 长度200m" />
              </template>
            </el-table-column>
            <el-table-column label="数量" width="140" align="center">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" size="small" style="width: 100px" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ $index }">
                <el-button type="danger" link @click="removePart($index)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="table-add-btn" @click="addPart">
            <span>＋ 手动增加部件行</span>
          </div>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="form-footer">
        <el-button @click="goBack" size="large" style="width: 120px">取消</el-button>
        <el-button type="primary" size="large" @click="submitForm" :loading="submitLoading" style="width: 200px">
          {{ isEdit ? '保存所有修改' : '确认并录入档案' }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createEquipment, updateEquipment, getEquipmentDetail, getEquipmentTemplates } from '@/api/equipment'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const equipmentId = route.params.id
const customerId = route.query.customerId

const loading = ref(false)
const submitLoading = ref(false)
const templateLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  customer_id: customerId || null,
  category: '', model_type: '', name: '',
  tonnage: '', span: '', lifting_height: '',
  work_class: '', installation_location: '',
  last_inspection_date: null, next_inspection_date: null, warranty_end_date: null,
  parts: []
})

const rules = {
  category: [{ required: true, message: '请选择大类', trigger: 'change' }],
  model_type: [{ required: true, message: '请选择型式', trigger: 'change' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const typeMap = {
  '桥式起重机': ['QD型', 'LDA型', 'LH型', 'QZ型'],
  '门式起重机': ['MH型', 'MG型', 'BMH型'],
  '悬臂起重机': ['BZ型', 'BZD型']
}
const availableModelTypes = computed(() => typeMap[form.category] || [])

const handleCategoryChange = () => { form.model_type = '' }
const addPart = () => form.parts.push({ part_name: '', specification: '', quantity: 1 })
const removePart = (i) => form.parts.splice(i, 1)

const fetchTemplates = async () => {
  if (!form.category || !form.model_type) {
    ElMessage.warning('请先完成大类和型式的选择')
    return
  }
  templateLoading.value = true
  try {
    const res = await getEquipmentTemplates({ category: form.category, model_type: form.model_type })
    if (res?.length) {
      form.parts = res.map(t => ({ part_name: t.part_name, specification: t.specification || '', quantity: 1 }))
      ElMessage.success('✅ 已根据型号预填充核心部件清单')
    } else {
      ElMessage.info('暂无对应型号的预设模板')
    }
  } catch {
    // 降级 MOCK 数据
    form.parts = [
      { part_name: '控制柜', specification: '标准配置', quantity: 1 },
      { part_name: '钢丝绳', specification: 'Ф12mm/14mm', quantity: 1 },
      { part_name: '核心制动器', specification: '电磁/液压', quantity: 2 }
    ]
    ElMessage.success('已应用通用部件模板')
  } finally { templateLoading.value = false }
}

const loadData = async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    const res = await getEquipmentDetail(equipmentId)
    if (res) Object.assign(form, res)
  } finally { loading.value = false }
}

const goBack = () => router.back()

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateEquipment(equipmentId, form)
          ElMessage.success('✅ 设备档案已成功更新')
        } else {
          await createEquipment(form)
          ElMessage.success('✅ 新设备档案录入成功')
        }
        goBack()
      } finally { submitLoading.value = false }
    }
  })
}

onMounted(() => { if (isEdit.value) loadData() })
</script>

<style scoped>
.equipment-form { padding: 0; }

.header-left { display: flex; align-items: center; gap: 16px; }
.back-btn { 
  border-color: var(--color-border); 
  color: var(--color-text-secondary);
}
.back-btn:hover { color: var(--color-primary); border-color: var(--color-primary); }

.form-wrapper { max-width: 1000px; margin: 0 auto; }

.form-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

.card-section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.card-section-title .icon { font-size: 18px; }
.card-section-title.flex-between { justify-content: space-between; margin-bottom: 16px; }

.parts-card { padding: 20px 0 0; }
.parts-card .card-section-title { padding: 0 24px; }

.parts-table-wrapper { border-top: 1px solid var(--color-border-light); }
.table-add-btn {
  padding: 14px;
  text-align: center;
  color: var(--color-primary);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  background: #fafbfc;
  transition: var(--transition-fast);
}
.table-add-btn:hover { background: var(--color-primary-light); }

.form-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin: 40px 0 60px;
}

:deep(.el-form-item__label) { 
  font-size: 13px !important; 
  color: var(--color-text-secondary) !important;
  margin-bottom: 6px !important;
}
:deep(.el-divider__text) { background: var(--color-bg-page); }
</style>