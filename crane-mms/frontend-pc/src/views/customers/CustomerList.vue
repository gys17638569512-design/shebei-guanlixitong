<template>
  <div class="customer-list">
    <el-card shadow="never">
      <div class="header-tools">
        <el-input 
          v-model="searchQuery" 
          placeholder="搜索客户名/联系人" 
          clearable 
          style="width: 300px" 
          @clear="loadData"
          @keyup.enter="loadData">
          <template #append>
            <el-button icon="Search" @click="loadData" />
          </template>
        </el-input>
        <el-button type="primary" icon="Plus" @click="openDrawer">新建客户</el-button>
      </div>

      <el-table :data="tableData" v-loading="loading" style="width: 100%; margin-top: 20px" stripe>
        <el-table-column prop="company_name" label="公司名" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="goToDetail(row.id)">{{ row.company_name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="contact_name" label="主联系人" width="150" />
        <el-table-column prop="contact_phone" label="联系电话" width="180" />
        <el-table-column prop="address" label="地址" min-width="250" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToDetail(row.id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer
      v-model="drawerVisible"
      title="新建客户"
      size="50%"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="公司名" prop="company_name">
          <el-input v-model="form.company_name" placeholder="请输入公司名" />
        </el-form-item>
        <el-form-item label="主联系人" prop="contact_name">
          <el-input v-model="form.contact_name" placeholder="请输入主联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="form.contact_phone" placeholder="请输入主联系人电话" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入公司地址" />
        </el-form-item>
        
        <el-divider>其他联系人</el-divider>
        
        <div v-for="(contact, index) in form.contacts" :key="index" class="contact-row">
          <el-form-item :label="'姓名 ' + (index + 1)" :prop="'contacts.' + index + '.name'" :rules="{ required: true, message: '请输入联系人姓名', trigger: 'blur' }">
            <el-input v-model="contact.name" placeholder="姓名" />
          </el-form-item>
          <el-form-item :label="'电话 ' + (index + 1)" :prop="'contacts.' + index + '.phone'" :rules="{ required: true, message: '请输入联系人电话', trigger: 'blur' }">
            <el-input v-model="contact.phone" placeholder="电话" />
          </el-form-item>
          <el-button type="danger" icon="Delete" circle plain @click="removeContact(index)" class="rm-btn" />
        </div>
        
        <el-button type="primary" plain icon="Plus" @click="addContact" style="margin-left: 100px; margin-bottom: 20px;">添加联系人</el-button>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">保存</el-button>
        </span>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCustomers, createCustomer } from '@/api/customer'
import { ElMessage } from 'element-plus'
import { Search, Plus, Delete } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const searchQuery = ref('')

const drawerVisible = ref(false)
const formRef = ref(null)
const submitLoading = ref(false)

const form = reactive({
  company_name: '',
  contact_name: '',
  contact_phone: '',
  address: '',
  contacts: []
})

const rules = {
  company_name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }],
  contact_name: [{ required: true, message: '请输入主联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCustomers({ search: searchQuery.value })
    // If backend isn't ready, wrap with res || []
    tableData.value = res || []
  } catch (err) {
    // Already handled in request interceptor
    console.warn(err)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => {
  router.push(`/customers/${id}`)
}

const openDrawer = () => {
  form.company_name = ''
  form.contact_name = ''
  form.contact_phone = ''
  form.address = ''
  form.contacts = []
  drawerVisible.value = true
  if (formRef.value) formRef.value.clearValidate()
}

const addContact = () => {
  form.contacts.push({ name: '', phone: '', role: '其它联系人' })
}

const removeContact = (index) => {
  form.contacts.splice(index, 1)
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await createCustomer(form)
        ElMessage.success('创建客户成功')
        drawerVisible.value = false
        loadData()
      } catch (err) {
        console.warn(err)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.header-tools {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.contact-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0px;
}
.contact-row .el-form-item {
  flex: 1;
  margin-right: 10px;
}
.rm-btn {
  margin-top: 0px;
}
</style>