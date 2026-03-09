<template>
  <div class="equipment-form">
    <el-page-header @back="goBack" :title="isEdit ? '返回' : '返回'" style="margin-bottom: 20px;">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ isEdit ? '编辑设备档案' : '新建设备档案' }} </span>
      </template>
    </el-page-header>

    <el-card shadow="never" v-loading="loading">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="form-container">
        <el-divider content-position="left">基础类别信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备大类" prop="category">
              <el-select v-model="form.category" placeholder="选择设备大类" @change="handleCategoryChange" style="width: 100%">
                <el-option label="桥式起重机" value="桥式起重机" />
                <el-option label="门式起重机" value="门式起重机" />
                <el-option label="悬臂起重机" value="悬臂起重机" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="型式" prop="model_type">
              <el-select v-model="form.model_type" placeholder="选择型式" style="width: 100%">
                <el-option v-for="type in availableModelTypes" :key="type" :label="type" :value="type" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">基础参数输入</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="设备名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="吨位" prop="tonnage">
              <el-input v-model="form.tonnage" placeholder="例如: 10t" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="跨度" prop="span">
              <el-input v-model="form.span" placeholder="例如: 16m" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="起升高度" prop="lifting_height">
              <el-input v-model="form.lifting_height" placeholder="例如: 8m" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工作级别" prop="work_class">
              <el-select v-model="form.work_class" placeholder="选择工作级别" style="width: 100%">
                <el-option label="A3" value="A3" />
                <el-option label="A4" value="A4" />
                <el-option label="A5" value="A5" />
                <el-option label="A6" value="A6" />
                <el-option label="A7" value="A7" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="安装位置" prop="installation_location">
              <el-input v-model="form.installation_location" placeholder="例如: 一号车间" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">特检与质保信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="上次特检日期" prop="last_inspection_date">
              <el-date-picker v-model="form.last_inspection_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="下次特检日期" prop="next_inspection_date">
              <el-date-picker v-model="form.next_inspection_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="质保到期日" prop="warranty_end_date">
              <el-date-picker v-model="form.warranty_end_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">
          部件清单
          <el-button type="success" size="small" plain @click="fetchTemplates" style="margin-left: 20px;" :loading="templateLoading">
            智能填充部件清单
          </el-button>
        </el-divider>
        
        <el-table :data="form.parts" style="width: 100%" border size="small">
          <el-table-column label="部件名称" width="200">
            <template #default="{ row, $index }">
              <el-input v-model="row.part_name" placeholder="部件名" />
            </template>
          </el-table-column>
          <el-table-column label="规格参数">
            <template #default="{ row }">
              <el-input v-model="row.specification" placeholder="规格如: Ф12mm" />
            </template>
          </el-table-column>
          <el-table-column label="数量" width="150">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ $index }">
              <el-button type="danger" icon="Delete" circle plain @click="removePart($index)" />
            </template>
          </el-table-column>
        </el-table>
        <el-button class="mt-2" type="primary" plain icon="Plus" @click="addPart">手动添加一行</el-button>

        <div style="margin-top: 40px; text-align: center;">
          <el-button @click="goBack" size="large">取消</el-button>
          <el-button type="primary" size="large" @click="submitForm" :loading="submitLoading">保存设备档案</el-button>
        </div>
      </el-form>
    </el-card>
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
  category: '',
  model_type: '',
  name: '',
  tonnage: '',
  span: '',
  lifting_height: '',
  work_class: '',
  installation_location: '',
  last_inspection_date: null,
  next_inspection_date: null,
  warranty_end_date: null,
  parts: []
})

const rules = {
  category: [{ required: true, message: '请选择大类', trigger: 'change' }],
  model_type: [{ required: true, message: '请选择型式', trigger: 'change' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }]
}

// 联动数据
const typeMap = {
  '桥式起重机': ['QD型', 'LDA型', 'LH型', 'QZ型'],
  '门式起重机': ['MH型', 'MG型', 'BMH型'],
  '悬臂起重机': ['BZ型', 'BZD型']
}
const availableModelTypes = computed(() => typeMap[form.category] || [])

const handleCategoryChange = () => {
  form.model_type = ''
}

const addPart = () => {
  form.parts.push({ part_name: '', specification: '', quantity: 1 })
}

const removePart = (index) => {
  form.parts.splice(index, 1)
}

const fetchTemplates = async () => {
  if (!form.category || !form.model_type) {
    ElMessage.warning('请先选择设备大类和型式')
    return
  }
  templateLoading.value = true
  try {
    const res = await getEquipmentTemplates({ category: form.category, model_type: form.model_type })
    if (res && res.length) {
      form.parts = res.map(t => ({
        part_name: t.part_name,
        specification: t.specification || '',
        quantity: 1
      }))
      ElMessage.success('已自动填充常见部件列表')
    } else {
      ElMessage.info('该型号暂无可填充部件模板')
    }
  } catch (err) {
    // mock fallback
    form.parts = [
      { part_name: '钢丝绳', specification: '', quantity: 1 },
      { part_name: '吊钩', specification: '', quantity: 1 },
      { part_name: '减速器', specification: '', quantity: 1 }
    ]
    ElMessage.success('已自动填充通用部件模板(Mock)')
  } finally {
    templateLoading.value = false
  }
}

const loadData = async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    const res = await getEquipmentDetail(equipmentId)
    if (res) {
      Object.assign(form, res)
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateEquipment(equipmentId, form)
          ElMessage.success('更新设备成功')
        } else {
          await createEquipment(form)
          ElMessage.success('创建设备成功')
        }
        goBack()
      } catch (err) {
        console.warn(err)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(() => {
  if (isEdit.value) {
    loadData()
  }
})
</script>

<style scoped>
.form-container {
  max-width: 1000px;
  margin: 0 auto;
}
.mt-2 {
  margin-top: 10px;
}
</style>