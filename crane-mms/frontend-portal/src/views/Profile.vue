<template>
  <div class="account-center pb-safe">
    <div class="profile-header">
      <div class="avatar-wrap">
        <van-icon name="manager" class="avatar-icon" />
      </div>
      <div class="user-meta">
        <div class="header-top">
          <h2 class="name">{{ data.mainAccount.display_name || data.mainAccount.name || '客户主账号' }}</h2>
          <van-tag round type="primary" class="status-tag">{{ data.companyProfile.status || '已开通' }}</van-tag>
        </div>
        <span class="role">{{ data.companyProfile.company_name || '客户公司' }} · {{ data.companyProfile.portal_mode || 'Web 完整版 + 微信核心版' }}</span>
        <span class="permission-tip">
          {{ canManageAccounts ? '当前账号可管理主账号、子账号与公司资料' : '当前账号为只读/执行角色，仅可维护个人资料与查看账号信息' }}
        </span>
      </div>
    </div>

    <div class="self-card">
      <div class="self-head">
        <div>
          <div class="self-name">{{ selfAccount.display_name || selfAccount.name || '当前账号' }}</div>
          <div class="self-role">
            {{ selfAccount.role_label || '主账号' }} · {{ selfAccount.account_type === 'CUSTOMER_ACCOUNT' ? '客户子账号' : '客户主账号' }}
          </div>
        </div>
        <van-tag round :type="canManageAccounts ? 'primary' : 'success'">
          {{ canManageAccounts ? '管理权限' : '个人权限' }}
        </van-tag>
      </div>
      <div class="self-grid">
        <div class="self-item">
          <span>登录账号</span>
          <strong>{{ selfAccount.username || '未设置' }}</strong>
        </div>
        <div class="self-item">
          <span>手机号</span>
          <strong>{{ selfAccount.phone || '未绑定' }}</strong>
        </div>
        <div class="self-item">
          <span>邮箱</span>
          <strong>{{ selfAccount.email || '未设置' }}</strong>
        </div>
        <div class="self-item">
          <span>签字权限</span>
          <strong>{{ canSignOrders ? '可签字' : '不可签字' }}</strong>
        </div>
      </div>
      <div class="self-actions">
        <van-button size="small" round plain type="primary" @click="openDialog('self')">编辑我的资料</van-button>
        <van-button
          v-if="canChangeOwnPassword"
          size="small"
          round
          plain
          type="warning"
          @click="openDialog('self-password')"
        >
          修改登录密码
        </van-button>
      </div>
    </div>

    <div v-if="canManageAccounts" class="shortcut-row">
      <van-button size="small" round plain type="primary" @click="openDialog('main')">编辑主账号</van-button>
      <van-button size="small" round plain type="success" @click="openDialog('sub')">新增子账号</van-button>
      <van-button size="small" round plain type="default" @click="openDialog('company')">维护公司资料</van-button>
    </div>

    <van-tabs v-model:active="activeTab" color="#1677ff" title-active-color="#1677ff">
      <van-tab title="主账号信息">
        <div class="section-card">
          <van-cell title="登录账号" :value="data.mainAccount.username || '未配置'" />
          <van-cell title="绑定手机号" :value="data.mainAccount.phone || '未绑定'" />
          <van-cell title="微信状态" :value="data.mainAccount.wechat_status || '未绑定'" />
          <van-cell title="登录方式" :value="data.mainAccount.login_mode || '账号密码'" />
          <van-cell title="最近登录" :value="data.mainAccount.last_login_at || '未记录'" />
          <van-cell title="创建时间" :value="data.mainAccount.created_at || '未记录'" />
          <div class="permission-block">
            <div class="block-title">主账号权限</div>
            <div class="tag-row">
              <van-tag v-for="item in data.mainAccount.permissions || []" :key="item" round type="primary" plain>{{ item }}</van-tag>
            </div>
          </div>
          <van-button
            v-if="canManageAccounts"
            block
            round
            type="primary"
            class="section-action"
            @click="openDialog('main')"
          >
            编辑主账号资料
          </van-button>
        </div>
      </van-tab>

      <van-tab title="子账号管理">
        <div class="section-card">
          <div class="sub-account-tip">
            {{ canManageAccounts ? '客户主账号或管理员子账号可在这里维护下属人员账号。' : '当前账号暂无管理权限，可查看子账号与分工信息。' }}
          </div>

          <van-empty
            v-if="!data.subAccounts.length"
            image="search"
            description="暂无子账号，点击下方按钮立即创建"
          />

          <div v-else class="sub-account-list">
            <div v-for="account in data.subAccounts" :key="account.id" class="sub-account-card">
              <div class="sub-account-head">
                <div>
                  <div class="sub-account-name">{{ account.display_name || account.name }}</div>
                  <div class="sub-account-meta">
                    {{ account.role_label || account.role }} · {{ account.phone || '未绑定手机号' }}
                  </div>
                </div>
                <div class="sub-account-tags">
                  <van-tag round :type="(account.status_label || '停用') === '启用' ? 'success' : 'default'">
                    {{ account.status_label || '停用' }}
                  </van-tag>
                  <van-tag round plain type="primary">{{ account.wechat_status || '未绑定' }}</van-tag>
                </div>
              </div>
              <div class="sub-account-meta-row">
                <span>登录账号：{{ account.username }}</span>
                <span>最近登录：{{ account.last_login_at || '未记录' }}</span>
              </div>
              <div class="sub-account-meta-row">
                <span>邮箱：{{ account.email || '未设置' }}</span>
                <span>需改密：{{ account.must_change_password ? '是' : '否' }}</span>
              </div>
              <div v-if="canManageAccounts" class="sub-account-actions">
                <van-button size="small" round plain type="primary" @click="openDialog('sub', account)">编辑</van-button>
                <van-button size="small" round plain type="warning" @click="openDialog('reset', account)">重置密码</van-button>
                <van-button
                  size="small"
                  round
                  plain
                  :type="account.is_active ? 'danger' : 'success'"
                  @click="toggleSubStatus(account)"
                >
                  {{ account.is_active ? '停用' : '启用' }}
                </van-button>
              </div>
            </div>
          </div>

          <van-button
            v-if="canManageAccounts"
            block
            round
            type="primary"
            class="section-action"
            @click="openDialog('sub')"
          >
            新建子账号
          </van-button>
        </div>
      </van-tab>

      <van-tab title="公司资料">
        <div class="section-card">
          <div class="company-block">
            <div v-if="data.companyProfile.logo_url" class="company-logo image-logo">
              <img :src="data.companyProfile.logo_url" alt="公司 Logo" class="company-logo-image" />
            </div>
            <div v-else class="company-logo">{{ data.companyProfile.logo_text || '客' }}</div>
            <div class="company-meta">
              <h3>{{ data.companyProfile.company_name || '客户公司' }}</h3>
              <p>{{ data.companyProfile.industry || '未设置行业' }}</p>
            </div>
          </div>
          <van-cell title="公司简称" :value="data.companyProfile.short_name || '未设置'" />
          <van-cell title="联系人" :value="data.companyProfile.contact_name || '未设置'" />
          <van-cell title="联系电话" :value="data.companyProfile.contact_phone || '未设置'" />
          <van-cell title="办公地址" :label="data.companyProfile.address || '未设置'" vertical />
          <van-cell title="门户形态" :value="data.companyProfile.portal_mode || '未设置'" />
          <van-cell title="Logo 地址" :label="data.companyProfile.logo_url || '未设置'" vertical />
          <van-cell title="备注" :label="data.companyProfile.remark || '未设置'" vertical />
          <van-button
            v-if="canManageAccounts"
            block
            round
            type="default"
            class="section-action"
            @click="openDialog('company')"
          >
            编辑公司资料
          </van-button>
        </div>
      </van-tab>
    </van-tabs>

    <div class="action-group">
      <van-button block round class="logout-btn" @click="handleLogout">
        安全退出登录
      </van-button>
    </div>

    <van-popup v-model:show="dialogVisible" position="bottom" round :style="{ minHeight: '60vh' }">
      <div class="editor-sheet">
        <div class="editor-header">
          <div>
            <div class="editor-title">{{ dialogTitle }}</div>
            <div class="editor-subtitle">{{ dialogSubtitle }}</div>
          </div>
          <van-button size="small" plain round @click="dialogVisible = false">关闭</van-button>
        </div>

        <div v-if="dialogType === 'main'" class="editor-body">
          <van-cell-group inset>
            <van-field v-model="mainForm.name" label="负责人姓名" placeholder="请输入主账号姓名" />
            <van-field v-model="mainForm.display_name" label="显示名称" placeholder="请输入显示名称" />
            <van-field v-model="mainForm.phone" label="登录手机号" type="tel" placeholder="请输入手机号" />
            <van-field v-model="mainForm.email" label="邮箱" placeholder="请输入邮箱" />
          </van-cell-group>
        </div>

        <div v-else-if="dialogType === 'sub'" class="editor-body">
          <van-cell-group inset>
            <van-field v-model="subForm.name" label="姓名" placeholder="请输入子账号姓名" />
            <van-field v-model="subForm.display_name" label="显示名称" placeholder="可选，默认同姓名" />
            <van-field v-model="subForm.username" label="登录账号" placeholder="请输入登录账号" />
            <van-field v-model="subForm.phone" label="手机号" type="tel" placeholder="请输入手机号" />
            <van-field v-model="subForm.email" label="邮箱" placeholder="请输入邮箱" />
            <van-field
              v-if="subDialogMode === 'create'"
              v-model="subForm.password"
              label="初始密码"
              type="password"
              placeholder="请输入初始密码"
            />
          </van-cell-group>
          <div class="role-card">
            <div class="field-title">角色权限</div>
            <van-radio-group v-model="subForm.role" direction="horizontal" class="role-group">
              <van-radio v-for="item in roleOptions" :key="item.value" :name="item.value">
                {{ item.label }}
              </van-radio>
            </van-radio-group>
          </div>
        </div>

        <div v-else-if="dialogType === 'reset'" class="editor-body">
          <div class="reset-target">重置账号：{{ resetTargetName || '未选择子账号' }}</div>
          <van-cell-group inset>
            <van-field v-model="resetForm.password" label="新密码" type="password" placeholder="请输入新密码" />
          </van-cell-group>
        </div>

        <div v-else-if="dialogType === 'self'" class="editor-body">
          <van-cell-group inset>
            <van-field v-model="selfForm.name" label="姓名" placeholder="请输入姓名" />
            <van-field v-model="selfForm.display_name" label="显示名称" placeholder="请输入显示名称" />
            <van-field v-model="selfForm.phone" label="手机号" type="tel" placeholder="请输入手机号" />
            <van-field
              v-if="selfAccount.account_type === 'CUSTOMER_ACCOUNT'"
              v-model="selfForm.email"
              label="邮箱"
              placeholder="请输入邮箱"
            />
          </van-cell-group>
        </div>

        <div v-else-if="dialogType === 'self-password'" class="editor-body">
          <div class="reset-target">当前账号：{{ selfAccount.display_name || selfAccount.name || '当前账号' }}</div>
          <van-cell-group inset>
            <van-field v-model="selfPasswordForm.password" label="新密码" type="password" placeholder="请输入新密码" />
          </van-cell-group>
        </div>

        <div v-else class="editor-body">
          <van-cell-group inset>
            <van-field v-model="companyForm.company_name" label="公司全称" placeholder="请输入公司全称" />
            <van-field v-model="companyForm.short_name" label="公司简称" placeholder="请输入公司简称" />
            <van-field v-model="companyForm.industry" label="所属行业" placeholder="请输入行业" />
            <van-field v-model="companyForm.contact_name" label="联系人" placeholder="请输入联系人" />
            <van-field v-model="companyForm.contact_phone" label="联系电话" type="tel" placeholder="请输入联系电话" />
            <van-field v-model="companyForm.logo_url" label="Logo 地址" placeholder="请输入 Logo 图片地址" />
            <van-field v-model="companyForm.address" label="办公地址" type="textarea" rows="2" autosize placeholder="请输入办公地址" />
            <van-field v-model="companyForm.remark" label="备注说明" type="textarea" rows="2" autosize placeholder="请输入备注说明" />
          </van-cell-group>
        </div>

        <div class="editor-footer">
          <van-button block round type="primary" :loading="submitting" @click="submitDialog">
            {{ dialogActionText }}
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import {
  createSubAccount,
  fetchAccountCenter,
  fetchCurrentPortalAccount,
  resetSubAccountPassword,
  updateCompanyProfile,
  updateCurrentPortalAccount,
  updateCurrentPortalPassword,
  updateMainAccount,
  updateSubAccount,
  updateSubAccountStatus
} from '../api/accountCenter'
import { clearPortalSession, getPortalPermissions, getPortalSession } from '../utils/portalAuth'

const router = useRouter()
const portalCustomer = ref(getPortalSession())
const activeTab = ref(0)
const dialogVisible = ref(false)
const dialogType = ref('main')
const subDialogMode = ref('create')
const editingSubAccountId = ref(null)
const resetTargetName = ref('')
const submitting = ref(false)
const data = ref({
  mainAccount: {},
  subAccounts: [],
  companyProfile: {}
})
const selfAccount = ref({})

const mainForm = reactive({
  name: '',
  display_name: '',
  phone: '',
  email: ''
})

const subForm = reactive({
  role: 'ADMIN',
  username: '',
  name: '',
  display_name: '',
  phone: '',
  email: '',
  password: ''
})

const selfForm = reactive({
  name: '',
  display_name: '',
  phone: '',
  email: ''
})

const resetForm = reactive({
  password: ''
})

const selfPasswordForm = reactive({
  password: ''
})

const companyForm = reactive({
  company_name: '',
  short_name: '',
  industry: '',
  contact_name: '',
  contact_phone: '',
  logo_url: '',
  address: '',
  remark: ''
})

const roleOptions = [
  { label: '管理员', value: 'ADMIN' },
  { label: '签字人', value: 'SIGNER' },
  { label: '查看人', value: 'VIEWER' },
  { label: '报修人', value: 'REPORTER' }
]

const permissions = computed(() => getPortalPermissions({
  account_type: selfAccount.value.account_type || portalCustomer.value.account_type,
  account_role: selfAccount.value.account_role || portalCustomer.value.account_role
}))

const canManageAccounts = computed(() => permissions.value.canManageAccounts)
const canSignOrders = computed(() => permissions.value.canSignOrders)
const canChangeOwnPassword = computed(() => permissions.value.canChangeOwnPassword)

const dialogTitle = computed(() => {
  if (dialogType.value === 'sub') {
    return subDialogMode.value === 'create' ? '新增子账号' : '编辑子账号'
  }
  const map = {
    main: '编辑主账号',
    reset: '重置子账号密码',
    self: '编辑我的资料',
    'self-password': '修改我的登录密码',
    company: '维护公司资料'
  }
  return map[dialogType.value]
})

const dialogSubtitle = computed(() => {
  if (dialogType.value === 'sub') {
    return subDialogMode.value === 'create'
      ? '为客户公司新增员工或其他人员账号'
      : '调整子账号姓名、登录账号、角色与联系方式'
  }
  const map = {
    main: '维护客户主账号联系人、显示名称与登录手机号',
    reset: '重置后子账号再次登录时需按新密码进入系统',
    self: '维护当前登录账号的个人资料信息',
    'self-password': '仅影响当前登录账号的密码，不影响其他账号',
    company: '调整客户公司名称、联系人、地址与 Logo'
  }
  return map[dialogType.value]
})

const dialogActionText = computed(() => {
  if (dialogType.value === 'reset' || dialogType.value === 'self-password') return '确认更新密码'
  return '保存并更新'
})

const syncPortalSession = (account = {}) => {
  const nextSession = {
    ...portalCustomer.value,
    contact_name: account.display_name || account.name || portalCustomer.value.contact_name,
    account_role: account.account_role || portalCustomer.value.account_role || (account.account_type === 'CUSTOMER' ? 'OWNER' : ''),
    role_label: account.role_label || portalCustomer.value.role_label,
    account_type: account.account_type || portalCustomer.value.account_type || 'CUSTOMER'
  }
  portalCustomer.value = nextSession
  localStorage.setItem('portal_customer', JSON.stringify(nextSession))
}

const fillMainForm = () => {
  mainForm.name = data.value.mainAccount.name || data.value.mainAccount.display_name || ''
  mainForm.display_name = data.value.mainAccount.display_name || ''
  mainForm.phone = data.value.companyProfile.contact_phone || data.value.mainAccount.phone || ''
  mainForm.email = data.value.mainAccount.email || ''
}

const fillSubForm = (account = null) => {
  subForm.role = account?.role || 'ADMIN'
  subForm.username = account?.username || ''
  subForm.name = account?.name || ''
  subForm.display_name = account?.display_name || ''
  subForm.phone = account?.phone_raw || account?.phone || ''
  subForm.email = account?.email || ''
  subForm.password = ''
}

const fillSelfForm = () => {
  selfForm.name = selfAccount.value.name || ''
  selfForm.display_name = selfAccount.value.display_name || ''
  selfForm.phone = selfAccount.value.phone || ''
  selfForm.email = selfAccount.value.email || ''
}

const fillResetForm = (account = null) => {
  editingSubAccountId.value = account?.id || null
  resetTargetName.value = account?.display_name || account?.name || ''
  resetForm.password = ''
}

const fillSelfPasswordForm = () => {
  selfPasswordForm.password = ''
}

const fillCompanyForm = () => {
  companyForm.company_name = data.value.companyProfile.company_name || ''
  companyForm.short_name = data.value.companyProfile.short_name || ''
  companyForm.industry = data.value.companyProfile.industry || ''
  companyForm.contact_name = data.value.companyProfile.contact_name || ''
  companyForm.contact_phone = data.value.companyProfile.contact_phone || ''
  companyForm.logo_url = data.value.companyProfile.logo_url || ''
  companyForm.address = data.value.companyProfile.address || ''
  companyForm.remark = data.value.companyProfile.remark || ''
}

const normalizeSubAccounts = (subAccounts = []) => {
  return subAccounts.map((account) => ({
    ...account,
    phone_raw: account.phone_raw || account.phone
  }))
}

const fetchData = async () => {
  try {
    const [accountCenter, currentAccount] = await Promise.all([
      fetchAccountCenter(),
      fetchCurrentPortalAccount()
    ])
    data.value = {
      ...accountCenter,
      subAccounts: normalizeSubAccounts(accountCenter.subAccounts || [])
    }
    selfAccount.value = currentAccount || {}
    syncPortalSession(currentAccount || {})
    fillMainForm()
    fillCompanyForm()
    fillSelfForm()
  } catch (error) {
    showToast(error.message || '加载账号中心失败')
  }
}

const openDialog = (type, account = null) => {
  const manageTypes = ['main', 'sub', 'reset', 'company']
  if (manageTypes.includes(type) && !canManageAccounts.value) {
    showToast('当前账号暂无管理权限')
    return
  }
  if (type === 'self-password' && !canChangeOwnPassword.value) {
    showToast('当前账号暂不支持在线改密')
    return
  }

  dialogType.value = type
  if (type === 'main') {
    fillMainForm()
  } else if (type === 'sub') {
    subDialogMode.value = account ? 'edit' : 'create'
    editingSubAccountId.value = account?.id || null
    fillSubForm(account)
  } else if (type === 'reset') {
    fillResetForm(account)
  } else if (type === 'self') {
    fillSelfForm()
  } else if (type === 'self-password') {
    fillSelfPasswordForm()
  } else {
    fillCompanyForm()
  }
  dialogVisible.value = true
}

const validateMainForm = () => {
  if (!mainForm.name.trim()) {
    showToast('请输入主账号姓名')
    return false
  }
  if (!mainForm.phone.trim()) {
    showToast('请输入登录手机号')
    return false
  }
  return true
}

const validateSubForm = () => {
  if (!subForm.name.trim()) {
    showToast('请输入子账号姓名')
    return false
  }
  if (!subForm.username.trim()) {
    showToast('请输入登录账号')
    return false
  }
  if (subDialogMode.value === 'create' && !subForm.password.trim()) {
    showToast('请输入初始密码')
    return false
  }
  return true
}

const validateSelfForm = () => {
  if (!selfForm.name.trim()) {
    showToast('请输入姓名')
    return false
  }
  if (!selfForm.phone.trim()) {
    showToast('请输入手机号')
    return false
  }
  return true
}

const validateResetForm = () => {
  if (!resetForm.password.trim()) {
    showToast('请输入新密码')
    return false
  }
  return true
}

const validateSelfPasswordForm = () => {
  if (!selfPasswordForm.password.trim()) {
    showToast('请输入新密码')
    return false
  }
  return true
}

const validateCompanyForm = () => {
  if (!companyForm.company_name.trim()) {
    showToast('请输入公司全称')
    return false
  }
  if (!companyForm.contact_name.trim()) {
    showToast('请输入联系人')
    return false
  }
  if (!companyForm.contact_phone.trim()) {
    showToast('请输入联系电话')
    return false
  }
  return true
}

const submitMainForm = async () => {
  if (!validateMainForm()) return
  await updateMainAccount({
    name: mainForm.name,
    display_name: mainForm.display_name,
    phone: mainForm.phone,
    email: mainForm.email
  })
  showToast('主账号信息已更新')
}

const submitSubForm = async () => {
  if (!validateSubForm()) return

  const payload = {
    role: subForm.role,
    username: subForm.username,
    name: subForm.name,
    display_name: subForm.display_name,
    phone: subForm.phone,
    email: subForm.email
  }

  if (subDialogMode.value === 'create') {
    await createSubAccount({
      ...payload,
      password: subForm.password
    })
    showToast('子账号创建成功')
    return
  }

  await updateSubAccount(editingSubAccountId.value, payload)
  showToast('子账号信息已更新')
}

const submitSelfForm = async () => {
  if (!validateSelfForm()) return
  const data = await updateCurrentPortalAccount({
    name: selfForm.name,
    display_name: selfForm.display_name,
    phone: selfForm.phone,
    email: selfAccount.value.account_type === 'CUSTOMER_ACCOUNT' ? selfForm.email : undefined
  })
  selfAccount.value = data || {}
  syncPortalSession(data || {})
  showToast('我的资料已更新')
}

const submitResetForm = async () => {
  if (!validateResetForm()) return
  await resetSubAccountPassword(editingSubAccountId.value, resetForm.password)
  showToast('子账号密码已重置')
}

const submitSelfPasswordForm = async () => {
  if (!validateSelfPasswordForm()) return
  const data = await updateCurrentPortalPassword(selfPasswordForm.password)
  selfAccount.value = data || {}
  showToast('我的登录密码已更新')
}

const submitCompanyForm = async () => {
  if (!validateCompanyForm()) return
  await updateCompanyProfile({
    company_name: companyForm.company_name,
    short_name: companyForm.short_name,
    industry: companyForm.industry,
    contact_name: companyForm.contact_name,
    contact_phone: companyForm.contact_phone,
    logo_url: companyForm.logo_url,
    address: companyForm.address,
    remark: companyForm.remark
  })
  showToast('公司资料已更新')
}

const submitDialog = async () => {
  submitting.value = true
  try {
    if (dialogType.value === 'main') {
      await submitMainForm()
    } else if (dialogType.value === 'sub') {
      await submitSubForm()
    } else if (dialogType.value === 'reset') {
      await submitResetForm()
    } else if (dialogType.value === 'self') {
      await submitSelfForm()
    } else if (dialogType.value === 'self-password') {
      await submitSelfPasswordForm()
    } else {
      await submitCompanyForm()
    }
    dialogVisible.value = false
    await fetchData()
  } catch (error) {
    showToast(error.message || '保存失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const toggleSubStatus = async (account) => {
  const nextActive = !account.is_active
  const actionText = nextActive ? '启用' : '停用'
  try {
    await showConfirmDialog({
      title: `${actionText}子账号`,
      message: `确认要${actionText}「${account.display_name || account.name}」吗？`,
    })
    await updateSubAccountStatus(account.id, nextActive)
    showToast(`子账号已${actionText}`)
    await fetchData()
  } catch (error) {}
}

const handleLogout = () => {
  showConfirmDialog({
    title: '退出确认',
    message: '确定要退出当前系统吗？',
  }).then(() => {
    clearPortalSession()
    router.push('/login')
  }).catch(() => {})
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.account-center { background-color: #f7f8fa; min-height: 100vh; }
.pb-safe { padding-bottom: calc(env(safe-area-inset-bottom) + 80px); }

.profile-header {
  background: linear-gradient(135deg, #1677ff, #3b82f6);
  padding: 60px 24px 40px;
  display: flex;
  align-items: center;
  gap: 16px;
  color: #fff;
}

.avatar-wrap {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.4);
}

.avatar-icon { font-size: 32px; }
.name { margin: 0; font-size: 20px; font-weight: 800; letter-spacing: 0.5px; }
.role { font-size: 13px; opacity: 0.9; margin-top: 4px; display: block; }
.permission-tip {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.82;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.status-tag { border: none; }

.self-card,
.section-card {
  margin: 16px;
  background: #fff;
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.shortcut-row {
  display: flex;
  gap: 10px;
  padding: 0 16px 0;
  flex-wrap: wrap;
}

.self-head,
.sub-account-head,
.sub-account-meta-row,
.sub-account-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.self-name,
.sub-account-name {
  font-size: 15px;
  font-weight: 800;
  color: #1e293b;
}

.self-role,
.sub-account-meta {
  margin-top: 6px;
  font-size: 12px;
  color: #64748b;
}

.self-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.self-item {
  padding: 12px;
  border-radius: 14px;
  background: #f8fafc;
}

.self-item span {
  display: block;
  font-size: 12px;
  color: #64748b;
}

.self-item strong {
  display: block;
  margin-top: 6px;
  color: #1e293b;
  font-size: 13px;
}

.self-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.permission-block {
  padding: 14px 0 8px;
}

.block-title,
.field-title {
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 10px;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sub-account-tip {
  color: #64748b;
  font-size: 12px;
  margin-bottom: 12px;
}

.sub-account-list {
  display: grid;
  gap: 12px;
}

.sub-account-card {
  padding: 14px 16px;
  border-radius: 16px;
  background: #f8fafc;
}

.sub-account-tags,
.sub-account-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.sub-account-meta-row {
  margin-top: 10px;
  font-size: 12px;
  color: #64748b;
}

.sub-account-actions {
  margin-top: 12px;
}

.company-block {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-bottom: 12px;
}

.company-logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #1677ff, #3b82f6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 22px;
  overflow: hidden;
}

.image-logo {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.company-logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.company-meta h3,
.company-meta p {
  margin: 0;
}

.company-meta h3 {
  font-size: 16px;
  color: #1e293b;
}

.company-meta p {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.section-action {
  margin-top: 12px;
  width: 100%;
}

.action-group { padding: 20px 16px; margin-top: 10px; }

.logout-btn {
  background: #fff !important;
  color: #ef4444 !important;
  border-color: #fee2e2 !important;
  font-weight: 700;
  font-size: 15px;
}

.editor-sheet {
  padding: 20px 16px 28px;
}

.editor-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.editor-title {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
}

.editor-subtitle {
  margin-top: 6px;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}

.editor-body {
  display: grid;
  gap: 14px;
}

.role-card {
  margin: 0 16px;
  padding: 14px 16px;
  border-radius: 16px;
  background: #f8fafc;
}

.role-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.reset-target {
  margin: 0 16px 12px;
  padding: 12px 14px;
  border-radius: 14px;
  background: #fff7ed;
  color: #9a3412;
  font-size: 13px;
  font-weight: 600;
}

.editor-footer {
  margin-top: 18px;
}
</style>
