<template>
  <div class="brand-config">
    <div class="page-header">
      <div class="title-group">
        <h1 class="page-title">平台品牌配置</h1>
        <p class="page-subtitle">统一维护系统名称、公司信息、Logo、主题色与报告抬头，后续可直接联动各端展示</p>
      </div>
      <div class="header-actions">
        <el-button @click="resetDefaults">恢复默认</el-button>
        <el-button type="primary" @click="saveSettings" :loading="saving">保存配置</el-button>
      </div>
    </div>

    <div class="config-grid">
      <el-card class="editor-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>品牌信息编辑</span>
            <el-tag type="success" effect="light">平台主体配置</el-tag>
          </div>
        </template>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="公司全称" prop="company_name">
                <el-input v-model="form.company_name" placeholder="请输入公司全称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="公司简称" prop="short_name">
                <el-input v-model="form.short_name" placeholder="请输入公司简称" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="系统名称" prop="system_name">
                <el-input v-model="form.system_name" placeholder="请输入系统名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="系统副标题" prop="system_subtitle">
                <el-input v-model="form.system_subtitle" placeholder="请输入系统副标题" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="管理端登录标题" prop="pc_login_title">
                <el-input v-model="form.pc_login_title" placeholder="请输入管理端登录标题" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="客户端登录标题" prop="portal_login_title">
                <el-input v-model="form.portal_login_title" placeholder="请输入客户端登录标题" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="工人端登录标题" prop="worker_login_title">
                <el-input v-model="form.worker_login_title" placeholder="请输入工人端登录标题" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="客服电话" prop="support_phone">
                <el-input v-model="form.support_phone" placeholder="请输入客服电话" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="公司地址" prop="address">
            <el-input v-model="form.address" type="textarea" :rows="2" placeholder="请输入公司地址" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="Logo 地址" prop="logo_url">
                <el-input v-model="form.logo_url" placeholder="/brand-mark.svg" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="浏览器图标" prop="favicon_url">
                <el-input v-model="form.favicon_url" placeholder="/brand-mark.svg" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="主题色" prop="theme_primary">
                <el-input v-model="form.theme_primary" placeholder="#1677ff" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="辅助色" prop="theme_secondary">
                <el-input v-model="form.theme_secondary" placeholder="#0ea5e9" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="报告抬头" prop="report_header_text">
            <el-input v-model="form.report_header_text" placeholder="请输入报告抬头" />
          </el-form-item>
          <el-form-item label="报告页尾" prop="report_footer_text">
            <el-input v-model="form.report_footer_text" placeholder="请输入报告页尾" />
          </el-form-item>
        </el-form>
      </el-card>

      <div class="preview-column">
        <el-card class="preview-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>品牌预览</span>
            </div>
          </template>

          <div class="preview-brand">
            <img class="brand-logo" :src="form.logo_url" alt="品牌 Logo" />
            <div class="brand-title">{{ form.system_name }}</div>
            <div class="brand-subtitle">{{ form.system_subtitle }}</div>
          </div>

          <div class="preview-list">
            <div class="preview-item">
              <span>公司全称</span>
              <strong>{{ form.company_name }}</strong>
            </div>
            <div class="preview-item">
              <span>客服电话</span>
              <strong>{{ form.support_phone }}</strong>
            </div>
            <div class="preview-item">
              <span>报告抬头</span>
              <strong>{{ form.report_header_text }}</strong>
            </div>
            <div class="preview-item">
              <span>主题色</span>
              <strong>{{ form.theme_primary }}</strong>
            </div>
          </div>
        </el-card>

        <el-card class="preview-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>联动范围</span>
            </div>
          </template>

          <el-space wrap>
            <el-tag v-for="item in linkedScopes" :key="item" type="info" effect="light">{{ item }}</el-tag>
          </el-space>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchPlatformSettings, persistPlatformSettings } from '@/api/system'

const formRef = ref(null)
const saving = ref(false)

const form = reactive({
  company_name: '',
  short_name: '',
  system_name: '',
  system_subtitle: '',
  logo_url: '',
  favicon_url: '',
  support_phone: '',
  address: '',
  pc_login_title: '',
  portal_login_title: '',
  worker_login_title: '',
  report_header_text: '',
  report_footer_text: '',
  theme_primary: '',
  theme_secondary: ''
})

const linkedScopes = [
  '管理端 Web',
  '客户端 Web',
  '工人端 Web',
  '管理端微信',
  '客户端微信',
  '工人端微信',
  '报告模板'
]

const rules = {
  company_name: [{ required: true, message: '请输入公司全称', trigger: 'blur' }],
  system_name: [{ required: true, message: '请输入系统名称', trigger: 'blur' }],
  logo_url: [{ required: true, message: '请输入 Logo 地址', trigger: 'blur' }],
  theme_primary: [{ required: true, message: '请输入主题色', trigger: 'blur' }]
}

const applySettings = (settings) => {
  Object.assign(form, settings)
}

const loadSettings = async () => {
  try {
    const data = await fetchPlatformSettings()
    applySettings(data)
  } catch (error) {
    ElMessage.error(error.message || '加载品牌配置失败')
  }
}

const saveSettings = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      await persistPlatformSettings({ ...form })
      ElMessage.success('品牌配置已保存')
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const resetDefaults = async () => {
  applySettings({
    company_name: '数字化起重机维修维保系统',
    short_name: '起重机维保',
    system_name: '数字化起重机维修维保系统',
    system_subtitle: '全生命周期设备服务平台',
    logo_url: '/brand-mark.svg',
    favicon_url: '/brand-mark.svg',
    support_phone: '400-800-1234',
    address: '中国 · 设备运维服务中心',
    pc_login_title: '管理端登录',
    portal_login_title: '客户端登录',
    worker_login_title: '工人端登录',
    report_header_text: '数字化起重机维修维保系统',
    report_footer_text: '如有疑问请联系平台客服',
    theme_primary: '#1677ff',
    theme_secondary: '#0ea5e9'
  })
  try {
    await persistPlatformSettings({ ...form })
    ElMessage.success('已恢复默认品牌配置')
  } catch (error) {
    ElMessage.error(error.message || '恢复默认失败')
  }
}

onMounted(loadSettings)
</script>

<style scoped>
.brand-config {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--color-text-primary);
}

.page-subtitle {
  margin: 0;
  color: var(--color-text-secondary);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.config-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(300px, 0.7fr);
  gap: 20px;
}

.editor-card,
.preview-card {
  border-radius: var(--radius-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
}

.preview-column {
  display: grid;
  gap: 20px;
}

.preview-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 12px 0 18px;
}

.brand-logo {
  width: 96px;
  height: 96px;
  border-radius: 22px;
  box-shadow: 0 12px 24px rgba(22, 119, 255, 0.18);
}

.brand-title {
  margin-top: 14px;
  font-size: 22px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.brand-subtitle {
  margin-top: 6px;
  color: var(--color-text-secondary);
}

.preview-list {
  display: grid;
  gap: 12px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border-light);
}

.preview-item span {
  color: var(--color-text-secondary);
}

.preview-item strong {
  color: var(--color-text-primary);
  text-align: right;
}
</style>
