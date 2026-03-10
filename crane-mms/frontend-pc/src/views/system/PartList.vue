<template>
  <div class="part-list">
    <el-card shadow="never">
      <div class="header-tools" style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div class="left-tools">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索零件编号/名称" 
            clearable 
            style="width: 250px;"
            :prefix-icon="Search"
          />
        </div>
        <el-button type="primary" :icon="Plus" @click="handleAdd">录入新备件</el-button>
      </div>

      <el-table
        :data="filteredParts"
        v-loading="loading"
        style="width: 100%"
        border
        stripe
      >
        <el-table-column prop="part_no" label="零件编号" width="140" />
        <el-table-column prop="name" label="零件名称" min-width="200" />
        <el-table-column prop="specification" label="规格型号" width="180" show-overflow-tooltip />
        <el-table-column prop="unit" label="计量单位" width="90" align="center" />
        <el-table-column prop="stock_quantity" label="库存数量" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getStockTagType(row)" size="small">{{ row.stock_quantity }} {{ row.unit }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_threshold" label="预警阈值" width="100" align="center" />
        <el-table-column prop="price" label="单价(元)" width="100" align="right">
          <template #default="{ row }">{{ row.price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" link @click="handleAdjust(row)">库存调整</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && filteredParts.length === 0" style="text-align: center; padding: 40px; color: #999;">
        暂无备件数据
      </div>
    </el-card>

    <!-- 新建/编辑弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑备件资料' : '录入新备件'"
      width="480px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="零件编号" prop="part_no">
          <el-input v-model="form.part_no" placeholder="如: PT-1001" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="零件名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入完整零件名称" />
        </el-form-item>
        <el-form-item label="规格型号">
          <el-input v-model="form.specification" placeholder="如: Φ200mm" />
        </el-form-item>
        <el-form-item label="计量单位" prop="unit">
          <el-select v-model="form.unit" style="width: 100%">
            <el-option label="个" value="个" />
            <el-option label="件" value="件" />
            <el-option label="片" value="片" />
            <el-option label="桶" value="桶" />
            <el-option label="套" value="套" />
            <el-option label="米" value="米" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="初始库存" prop="stock_quantity">
              <el-input-number v-model="form.stock_quantity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预警数量" prop="warning_threshold">
              <el-input-number v-model="form.warning_threshold" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="参考单价(元)">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 库存调整弹窗 -->
    <el-dialog v-model="adjustDialogVisible" title="库存快速调整" width="360px">
      <p style="color:#666; margin-bottom: 16px;">当前零件：<strong>{{ adjustingPart?.name }}</strong>，当前库存：{{ adjustingPart?.stock_quantity }} {{ adjustingPart?.unit }}</p>
      <el-radio-group v-model="adjustType" style="margin-bottom: 16px;">
        <el-radio value="in">入库</el-radio>
        <el-radio value="out">出库</el-radio>
      </el-radio-group>
      <el-input-number v-model="adjustQty" :min="1" placeholder="调整数量" style="width: 100%" />
      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdjust" :loading="submitLoading">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getAllParts, createPart, updatePart, adjustPartStock } from '@/api/part'

const loading = ref(false)
const parts = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const adjustDialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const adjustingPart = ref(null)
const adjustType = ref('in')
const adjustQty = ref(1)

const form = ref({
  part_no: '', name: '', specification: '',
  unit: '个', stock_quantity: 0, warning_threshold: 5, price: 0
})

const rules = {
  part_no: [{ required: true, message: '请输入零件编号' }],
  name: [{ required: true, message: '请输入零件名称' }],
  unit: [{ required: true, message: '请选择计量单位' }],
}

const getStockTagType = (row) => {
  if (row.stock_quantity <= 0) return 'danger'
  if (row.stock_quantity <= row.warning_threshold) return 'warning'
  return 'success'
}

const filteredParts = computed(() => {
  if (!searchQuery.value) return parts.value
  const q = searchQuery.value.toLowerCase()
  return parts.value.filter(p => 
    p.name?.toLowerCase().includes(q) ||
    p.part_no?.toLowerCase().includes(q)
  )
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getAllParts()
    parts.value = res || []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  form.value = { part_no: '', name: '', specification: '', unit: '个', stock_quantity: 0, warning_threshold: 5, price: 0 }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const handleAdjust = (row) => {
  adjustingPart.value = row
  adjustQty.value = 1
  adjustType.value = 'in'
  adjustDialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updatePart(form.value.id, form.value)
          ElMessage.success('备件资料已更新')
        } else {
          await createPart(form.value)
          ElMessage.success('新备件录入成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (err) {
        ElMessage.error(err.message || '操作失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const submitAdjust = async () => {
  if (!adjustingPart.value) return
  submitLoading.value = true
  try {
    await adjustPartStock(adjustingPart.value.id, adjustType.value, adjustQty.value)
    ElMessage.success(`库存调整成功`)
    adjustDialogVisible.value = false
    loadData()
  } catch (err) {
    ElMessage.error(err.message || '库存调整失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.part-list { padding: 0; }
</style>
