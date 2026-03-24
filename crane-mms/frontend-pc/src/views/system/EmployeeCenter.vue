<template>
  <div class="workspace-page permission-management">
    <section class="workspace-hero">
      <div class="workspace-hero__body">
        <p class="workspace-kicker">Permission Governance</p>
        <h2 class="workspace-title">角色默认权限与个人覆盖统一治理</h2>
        <p class="workspace-description">
          在同一工作台查看全部账号、切换角色、维护默认权限模板，并针对个人做覆盖授权，让设置区入口和操作能力都能精确收口。
        </p>
        <div class="workspace-badges">
          <span class="soft-pill">账号总数 {{ accounts.length }}</span>
          <span class="soft-pill">启用账号 {{ summaryCards[1]?.value || 0 }}</span>
          <span class="soft-pill">权限模块 {{ permissionModules.length }}</span>
        </div>
      </div>
      <div class="workspace-hero__aside">
        <div class="workspace-aside-card">
          <span class="workspace-aside-card__label">治理模式</span>
          <span class="workspace-aside-card__value">角色 + 个人覆盖</span>
          <span class="workspace-aside-card__meta">先继承角色默认权限，再做单人覆盖开关</span>
        </div>
        <div class="workspace-actions governance-hero-actions">
          <el-button @click="reloadPage">刷新数据</el-button>
          <el-button v-if="canCreateAccount" type="primary" @click="openCreateDialog">新增账号</el-button>
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
            <h3 class="surface-panel__title">账号总表</h3>
            <p class="surface-panel__subtitle">从账号列表进入详情，继续维护角色默认权限和个人覆盖。</p>
          </div>
        </div>
        <div class="surface-panel__body">
          <div class="filter-strip">
            <el-input v-model="searchQuery" class="filter-strip__grow" placeholder="搜索姓名、账号、部门" clearable>
              <template #prefix>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#7f93a6">
                  <circle cx="11" cy="11" r="8" />
                  <path d="M21 21l-4.35-4.35" />
                </svg>
              </template>
            </el-input>
            <el-select v-model="roleFilter" placeholder="全部角色" clearable style="width: 160px">
              <el-option label="系统管理员" value="ADMIN" />
              <el-option label="业务经理" value="MANAGER" />
              <el-option label="技术工程师" value="TECH" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 160px">
              <el-option label="启用" value="ACTIVE" />
              <el-option label="停用" value="INACTIVE" />
            </el-select>
          </div>

          <el-table :data="filteredAccounts" v-loading="loading" style="width: 100%" border>
            <el-table-column width="60" align="center">
              <template #default="{ row }">
                <div class="avatar-circle">{{ (row.name || row.username || '?').charAt(0) }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="姓名" min-width="120" />
            <el-table-column prop="username" label="账号" min-width="140">
              <template #default="{ row }">
                <code class="code-cell">{{ row.username }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="department" label="部门" min-width="130" />
            <el-table-column prop="job_title" label="岗位" min-width="130" />
            <el-table-column label="角色" width="120" align="center">
              <template #default="{ row }">
                <el-tag effect="light">{{ getRoleName(row.role) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="账号状态" width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'danger'" effect="light">
                  {{ row.status === 'ACTIVE' ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_login_at" label="最后登录" min-width="150" />
            <el-table-column label="操作" width="320" align="center" fixed="right">
              <template #default="{ row }">
                <el-button v-if="canViewDetail" link type="primary" @click="openPermissionDrawer(row)">查看详情</el-button>
                <el-button v-if="canEditAccount" link type="success" @click="openEditDialog(row)">编辑</el-button>
                <el-button v-if="canResetPassword" link type="warning" @click="handleResetPassword(row)">重置密码</el-button>
                <el-button
                  v-if="canToggleStatus"
                  link
                  :type="row.status === 'ACTIVE' ? 'danger' : 'success'"
                  @click="handleToggleStatus(row)"
                >
                  {{ row.status === 'ACTIVE' ? '停用' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </article>

      <div class="surface-grid">
        <article class="surface-panel surface-panel--dark">
          <div class="surface-panel__header">
            <div>
              <h3 class="surface-panel__title">角色分布</h3>
              <p class="surface-panel__subtitle">先看角色结构，再决定默认权限模板是否需要收紧。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div class="data-rail">
              <div v-for="item in roleBreakdown" :key="item.label" class="data-rail__item">
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
              <h3 class="surface-panel__title">权限域覆盖</h3>
              <p class="surface-panel__subtitle">第一版仅覆盖设置区五个模块，但粒度已细到页面、操作和模块区块。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div class="module-chip-grid">
              <div v-for="module in permissionModules" :key="module.module_key" class="module-chip-card">
                <strong>{{ module.label }}</strong>
                <span>{{ module.groups?.length || 0 }} 组权限</span>
                <small>{{ module.route }}</small>
              </div>
            </div>
          </div>
        </article>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑账号' : '新增账号'" width="560px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="登录账号" prop="username">
              <el-input v-model="form.username" placeholder="请输入登录账号" :disabled="isEdit" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="部门" prop="department">
              <el-input v-model="form.department" placeholder="如：平台运营部" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="岗位" prop="job_title">
              <el-input v-model="form.job_title" placeholder="如：系统管理员" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色" prop="role">
              <el-select v-model="form.role" style="width: 100%">
                <el-option label="系统管理员" value="ADMIN" />
                <el-option label="业务经理" value="MANAGER" />
                <el-option label="技术工程师" value="TECH" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="微信绑定" prop="wechat_bound">
              <el-switch v-model="form.wechat_bound" active-text="已绑定" inactive-text="未绑定" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="账号状态" prop="status">
              <el-switch v-model="form.statusEnabled" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="isEdit ? '重置登录密码（留空则不改）' : '初始登录密码'" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="isEdit ? '留空不修改密码' : '请设置初始密码'"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">
          {{ isEdit ? '保存修改' : '创建账号' }}
        </el-button>
      </template>
    </el-dialog>

    <el-drawer
      v-model="detailDrawerVisible"
      title="账号详情与权限"
      size="760px"
      destroy-on-close
      class="permission-drawer"
    >
      <div v-loading="detailLoading" class="drawer-shell">
        <el-empty v-if="!permissionDetail" description="请选择账号查看详情" />

        <template v-else>
          <div class="drawer-hero">
            <div>
              <div class="drawer-title">{{ permissionDetail.user.name }}</div>
              <div class="drawer-subtitle">{{ permissionDetail.user.username }} · {{ getRoleName(permissionDetail.user.role) }}</div>
            </div>
            <div class="drawer-tags">
              <el-tag type="info">角色默认 {{ rolePermissionsDraft.length }} 项</el-tag>
              <el-tag type="success">最终生效 {{ permissionDetail.effective_permissions.length }} 项</el-tag>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-card">
              <span>手机号</span>
              <strong>{{ selectedAccount?.phone || '未设置' }}</strong>
            </div>
            <div class="info-card">
              <span>部门 / 岗位</span>
              <strong>{{ selectedAccount?.department || '未设置' }} / {{ selectedAccount?.job_title || '未设置' }}</strong>
            </div>
            <div class="info-card">
              <span>账号状态</span>
              <strong>{{ selectedAccount?.status === 'ACTIVE' ? '启用' : '停用' }}</strong>
            </div>
            <div class="info-card">
              <span>最后登录</span>
              <strong>{{ selectedAccount?.last_login_at || '暂无记录' }}</strong>
            </div>
          </div>

          <div v-if="canViewRoleDefaults" class="permission-section">
            <div class="section-head">
              <div>
                <h3>角色默认权限</h3>
                <p>当前账号继承自 {{ getRoleName(permissionDetail.user.role) }}，在这里修改会影响同角色成员。</p>
              </div>
              <el-button
                v-if="canEditRoleDefaults"
                type="primary"
                @click="saveRoleTemplate"
                :loading="roleSaveLoading"
              >
                保存当前角色默认权限
              </el-button>
            </div>

            <div v-for="module in permissionModules" :key="`${permissionDetail.user.role}-${module.module_key}`" class="permission-card">
              <div class="module-header">
                <div>
                  <div class="module-title">{{ module.label }}</div>
                  <div class="module-route">{{ module.route }}</div>
                </div>
              </div>
              <el-checkbox-group v-model="rolePermissionsDraft" :disabled="!canEditRoleDefaults">
                <div v-for="group in module.groups" :key="group.group_key" class="permission-group">
                  <div class="group-title">{{ group.label }}</div>
                  <div class="permission-grid">
                    <el-checkbox
                      v-for="item in group.items"
                      :key="item.key"
                      :label="item.key"
                      border
                      class="permission-checkbox"
                    >
                      <span class="permission-label">{{ item.label }}</span>
                      <span class="permission-key">{{ item.key }}</span>
                    </el-checkbox>
                  </div>
                </div>
              </el-checkbox-group>
            </div>
          </div>

          <div v-if="canViewUserOverrides" class="permission-section">
            <div class="section-head">
              <div>
                <h3>个人覆盖权限</h3>
                <p>在继承角色默认权限后，可以对单个员工做额外授权或显式禁用。</p>
              </div>
              <el-button
                v-if="canEditUserOverrides"
                type="primary"
                plain
                @click="saveUserOverrides"
                :loading="overrideSaveLoading"
              >
                保存个人覆盖
              </el-button>
            </div>

            <div v-for="module in permissionModules" :key="`${permissionDetail.user.id}-${module.module_key}`" class="permission-card">
              <div class="module-header">
                <div class="module-title">{{ module.label }}</div>
              </div>
              <div v-for="group in module.groups" :key="group.group_key" class="permission-group">
                <div class="group-title">{{ group.label }}</div>
                <div v-for="item in group.items" :key="item.key" class="override-row">
                  <div class="override-meta">
                    <div class="permission-label">{{ item.label }}</div>
                    <div class="permission-key">{{ item.key }}</div>
                  </div>
                  <el-radio-group v-model="overrideDraft[item.key]" :disabled="!canEditUserOverrides" size="small">
                    <el-radio-button label="inherit">继承</el-radio-button>
                    <el-radio-button label="allow">额外允许</el-radio-button>
                    <el-radio-button label="deny">显式禁用</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </div>
          </div>

          <div v-if="canViewEffectivePreview" class="permission-section">
            <div class="section-head compact">
              <div>
                <h3>生效权限预览</h3>
                <p>以下是当前账号最终生效的权限结果。</p>
              </div>
            </div>

            <el-empty v-if="!effectivePermissionCards.length" description="当前没有生效的设置权限" />
            <div v-else class="effective-grid">
              <div v-for="item in effectivePermissionCards" :key="item.key" class="effective-card">
                <div class="effective-module">{{ item.moduleLabel }}</div>
                <div class="effective-label">{{ item.label }}</div>
                <div class="effective-key">{{ item.key }}</div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  fetchEmployeeAccounts,
  addEmployeeAccount,
  editEmployeeAccount,
  refreshEmployeePassword,
  changeEmployeeStatus,
  fetchPermissionCatalog,
  fetchUserPermissionDetail,
  updateRolePermissions,
  updateUserPermissionOverrides
} from '@/api/system'
import { useAuthStore } from '@/stores/auth'
import { SETTINGS_PERMISSIONS } from '@/constants/permissions'

const authStore = useAuthStore()

const loading = ref(false)
const submitLoading = ref(false)
const detailLoading = ref(false)
const roleSaveLoading = ref(false)
const overrideSaveLoading = ref(false)
const accounts = ref([])
const permissionCatalog = ref({ modules: [], role_templates: {}, all_permission_keys: [] })
const permissionDetail = ref(null)
const selectedAccount = ref(null)
const rolePermissionsDraft = ref([])
const overrideDraft = ref({})

const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const detailDrawerVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  username: '',
  department: '',
  job_title: '',
  phone: '',
  role: 'TECH',
  wechat_bound: false,
  statusEnabled: true,
  password: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const filteredAccounts = computed(() => {
  return accounts.value.filter((item) => {
    const keyword = searchQuery.value.trim().toLowerCase()
    const keywordMatched = !keyword || [item.name, item.username, item.department, item.job_title]
      .filter(Boolean)
      .some((value) => value.toLowerCase().includes(keyword))
    const roleMatched = !roleFilter.value || item.role === roleFilter.value
    const statusMatched = !statusFilter.value || item.status === statusFilter.value
    return keywordMatched && roleMatched && statusMatched
  })
})

const summaryCards = computed(() => {
  const total = accounts.value.length
  const active = accounts.value.filter((item) => item.status === 'ACTIVE').length
  const wechatBound = accounts.value.filter((item) => item.wechat_bound).length
  const needReset = accounts.value.filter((item) => item.must_change_password).length

  return [
    { label: '账号总数', value: total, hint: '权限中心可管理的全部员工' },
    { label: '启用账号', value: active, hint: '当前允许登录的平台账号' },
    { label: '微信绑定', value: wechatBound, hint: '可接收微信提醒的成员' },
    { label: '待改密码', value: needReset, hint: '首次登录或重置后需处理' }
  ]
})

const roleBreakdown = computed(() => {
  const adminCount = accounts.value.filter((item) => item.role === 'ADMIN').length
  const managerCount = accounts.value.filter((item) => item.role === 'MANAGER').length
  const techCount = accounts.value.filter((item) => item.role === 'TECH').length
  return [
    {
      label: '系统管理员',
      value: `${adminCount} 人`,
      description: '拥有最高设置域权限，通常负责角色模板和治理基线。',
      tone: adminCount > 1 ? 'warning' : 'success'
    },
    {
      label: '业务经理',
      value: `${managerCount} 人`,
      description: '负责业务协同与设置页访问，适合按角色模板批量治理。',
      tone: ''
    },
    {
      label: '技术工程师',
      value: `${techCount} 人`,
      description: '通常以业务执行为主，设置权限应根据实际工作边界谨慎开放。',
      tone: techCount ? 'success' : 'warning'
    }
  ]
})

const permissionMetaMap = computed(() => {
  const map = {}
  permissionCatalog.value.modules.forEach((module) => {
    module.groups.forEach((group) => {
      group.items.forEach((item) => {
        map[item.key] = {
          ...item,
          groupLabel: group.label,
          moduleKey: module.module_key,
          moduleLabel: module.label
        }
      })
    })
  })
  return map
})

const permissionModules = computed(() => permissionCatalog.value.modules || [])

const effectivePermissionCards = computed(() => {
  return (permissionDetail.value?.effective_permissions || []).map((key) => ({
    key,
    label: permissionMetaMap.value[key]?.label || key,
    moduleLabel: permissionMetaMap.value[key]?.moduleLabel || '未分类'
  }))
})

const canCreateAccount = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_ACCOUNT_CREATE))
const canEditAccount = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_ACCOUNT_EDIT))
const canResetPassword = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_ACCOUNT_RESET_PASSWORD))
const canToggleStatus = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_ACCOUNT_STATUS))
const canViewDetail = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_DETAIL_VIEW))
const canViewRoleDefaults = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_MODULE_ROLE_DEFAULTS))
const canEditRoleDefaults = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_ROLE_TEMPLATE_EDIT))
const canViewUserOverrides = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_MODULE_USER_OVERRIDES))
const canEditUserOverrides = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_USER_OVERRIDE_EDIT))
const canViewEffectivePreview = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_MODULE_EFFECTIVE_PREVIEW))

const getRoleName = (role) => {
  const map = { ADMIN: '系统管理员', MANAGER: '业务经理', TECH: '技术工程师' }
  return map[role] || role
}

const syncFormToRow = (row) => {
  form.name = row?.name || ''
  form.username = row?.username || ''
  form.department = row?.department || ''
  form.job_title = row?.job_title || ''
  form.phone = row?.phone || ''
  form.role = row?.role || 'TECH'
  form.wechat_bound = Boolean(row?.wechat_bound)
  form.statusEnabled = (row?.status || 'ACTIVE') === 'ACTIVE'
  form.password = ''
}

const applyPermissionDetail = (detail) => {
  permissionDetail.value = detail
  rolePermissionsDraft.value = [...(detail.role_permissions || [])]
  const nextDraft = {}
  ;(permissionCatalog.value.all_permission_keys || []).forEach((key) => {
    nextDraft[key] = 'inherit'
  })
  ;(detail.user_overrides?.allow_permissions || []).forEach((key) => {
    nextDraft[key] = 'allow'
  })
  ;(detail.user_overrides?.deny_permissions || []).forEach((key) => {
    nextDraft[key] = 'deny'
  })
  overrideDraft.value = nextDraft
}

const loadAccounts = async () => {
  loading.value = true
  try {
    accounts.value = await fetchEmployeeAccounts()
  } catch (error) {
    ElMessage.error(error.message || '加载账号列表失败')
  } finally {
    loading.value = false
  }
}

const loadPermissionCatalogData = async () => {
  try {
    permissionCatalog.value = await fetchPermissionCatalog()
  } catch (error) {
    ElMessage.error(error.message || '加载权限目录失败')
  }
}

const reloadPage = async () => {
  await Promise.all([loadAccounts(), loadPermissionCatalogData(), authStore.fetchCurrentUser().catch(() => null)])
  if (detailDrawerVisible.value && selectedAccount.value) {
    await openPermissionDrawer(selectedAccount.value)
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  editingId.value = null
  syncFormToRow()
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  editingId.value = row.id
  syncFormToRow(row)
  dialogVisible.value = true
}

const openPermissionDrawer = async (row) => {
  selectedAccount.value = row
  detailDrawerVisible.value = true
  detailLoading.value = true
  try {
    const detail = await fetchUserPermissionDetail(row.id)
    applyPermissionDetail(detail)
  } catch (error) {
    ElMessage.error(error.message || '加载权限详情失败')
  } finally {
    detailLoading.value = false
  }
}

const handleResetPassword = async (row) => {
  try {
    await ElMessageBox.confirm(`确认重置账号「${row.name}」的登录密码吗？`, '重置密码', {
      type: 'warning',
      confirmButtonText: '确认重置',
      cancelButtonText: '取消'
    })
    await refreshEmployeePassword(row.id, '123456')
    ElMessage.success('已重置密码，员工下次登录需改密')
    await loadAccounts()
  } catch (error) {}
}

const handleToggleStatus = async (row) => {
  const nextStatus = row.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
  const actionText = nextStatus === 'ACTIVE' ? '启用' : '停用'
  try {
    await ElMessageBox.confirm(`确认${actionText}账号「${row.name}」吗？`, '状态变更', {
      type: 'warning',
      confirmButtonText: `确认${actionText}`,
      cancelButtonText: '取消'
    })
    await changeEmployeeStatus(row.id, nextStatus)
    ElMessage.success(`账号已${actionText}`)
    await loadAccounts()
    if (selectedAccount.value?.id === row.id) {
      await openPermissionDrawer({ ...row, status: nextStatus })
    }
  } catch (error) {}
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const payload = {
        name: form.name,
        username: form.username,
        department: form.department,
        job_title: form.job_title,
        phone: form.phone,
        role: form.role,
        wechat_bound: form.wechat_bound,
        status: form.statusEnabled ? 'ACTIVE' : 'INACTIVE'
      }

      if (isEdit.value) {
        if (form.password) payload.password = form.password
        await editEmployeeAccount(editingId.value, payload)
        ElMessage.success('账号资料已更新')
      } else {
        payload.password = form.password || 'Admin@2024'
        await addEmployeeAccount(payload)
        ElMessage.success('账号已创建')
      }

      dialogVisible.value = false
      await loadAccounts()
      if (detailDrawerVisible.value && selectedAccount.value?.id === editingId.value) {
        const refreshed = accounts.value.find((item) => item.id === editingId.value) || selectedAccount.value
        await openPermissionDrawer(refreshed)
      }
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const saveRoleTemplate = async () => {
  if (!permissionDetail.value) return
  roleSaveLoading.value = true
  try {
    const result = await updateRolePermissions(permissionDetail.value.user.role, {
      permissions: rolePermissionsDraft.value
    })
    permissionCatalog.value.role_templates[permissionDetail.value.user.role] = result.permissions
    ElMessage.success('角色默认权限已更新')
    if (authStore.user?.role === permissionDetail.value.user.role) {
      await authStore.fetchCurrentUser().catch(() => null)
    }
    await openPermissionDrawer(selectedAccount.value)
  } catch (error) {
    ElMessage.error(error.message || '保存角色默认权限失败')
  } finally {
    roleSaveLoading.value = false
  }
}

const saveUserOverrides = async () => {
  if (!permissionDetail.value) return
  overrideSaveLoading.value = true
  try {
    const allowPermissions = []
    const denyPermissions = []
    Object.entries(overrideDraft.value).forEach(([key, mode]) => {
      if (mode === 'allow') allowPermissions.push(key)
      if (mode === 'deny') denyPermissions.push(key)
    })
    const detail = await updateUserPermissionOverrides(permissionDetail.value.user.id, {
      allow_permissions: allowPermissions,
      deny_permissions: denyPermissions
    })
    applyPermissionDetail(detail)
    ElMessage.success('个人覆盖权限已更新')
    if (authStore.user?.id === permissionDetail.value.user.id) {
      await authStore.fetchCurrentUser().catch(() => null)
    }
  } catch (error) {
    ElMessage.error(error.message || '保存个人覆盖失败')
  } finally {
    overrideSaveLoading.value = false
  }
}

onMounted(async () => {
  await reloadPage()
})
</script>

<style scoped>
.permission-management {
  padding: 0;
}

.governance-hero-actions {
  margin-top: 14px;
}

.module-chip-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.module-chip-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(241, 246, 251, 0.9);
  border: 1px solid rgba(15, 33, 51, 0.06);
}

.module-chip-card strong {
  color: var(--color-text-primary);
}

.module-chip-card span,
.module-chip-card small {
  color: var(--color-text-secondary);
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e6f4ff, #bae0ff);
  color: var(--color-primary);
  font-weight: 700;
}

.code-cell {
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--color-bg-page);
  font-size: 12px;
}

.drawer-shell {
  padding-right: 8px;
}

.drawer-hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  padding: 18px 20px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(15, 47, 74, 0.95), rgba(18, 77, 131, 0.82));
  color: #fff;
  margin-bottom: 18px;
}

.drawer-title {
  font-size: 24px;
  font-weight: 700;
}

.drawer-subtitle {
  margin-top: 8px;
  color: rgba(255,255,255,.72);
}

.drawer-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.info-card {
  border-radius: 18px;
  border: 1px solid var(--color-border-light);
  padding: 14px 16px;
  background: rgba(255,255,255,.72);
}

.info-card span {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.info-card strong {
  color: var(--color-text-primary);
}

.permission-section {
  margin-top: 20px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.section-head.compact {
  margin-bottom: 10px;
}

.section-head h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: var(--color-text-primary);
}

.section-head p {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.permission-card {
  border: 1px solid var(--color-border-light);
  border-radius: 20px;
  padding: 16px;
  background: #fff;
  margin-bottom: 14px;
}

.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.module-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.module-route {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-placeholder);
}

.permission-group + .permission-group {
  margin-top: 16px;
}

.group-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-secondary);
  margin-bottom: 10px;
}

.permission-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.permission-checkbox {
  margin-right: 0;
  align-items: flex-start;
  height: auto;
}

.permission-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.permission-key {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: var(--color-text-placeholder);
  word-break: break-all;
}

.override-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 0;
  border-top: 1px solid var(--color-border-light);
}

.override-row:first-child {
  border-top: none;
}

.override-meta {
  flex: 1;
  min-width: 0;
}

.effective-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.effective-card {
  border-radius: 18px;
  padding: 14px 16px;
  background: linear-gradient(180deg, rgba(255,255,255,.94), rgba(247,250,252,.88));
  border: 1px solid var(--color-border-light);
}

.effective-module {
  font-size: 11px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--color-primary);
  font-weight: 700;
}

.effective-label {
  margin-top: 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.effective-key {
  margin-top: 6px;
  font-size: 11px;
  color: var(--color-text-placeholder);
  word-break: break-all;
}

@media (max-width: 900px) {
  .module-chip-grid,
  .permission-grid,
  .info-grid,
  .effective-grid {
    grid-template-columns: 1fr;
  }

  .override-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
