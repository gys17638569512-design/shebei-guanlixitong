<template>
  <div class="account-center pb-safe">
    <div class="profile-header">
      <div class="avatar-wrap">
        <van-icon name="manager" class="avatar-icon" />
      </div>
      <div class="user-meta">
        <div class="header-top">
          <h2 class="name">{{ data.mainAccount.display_name || '客户主账号' }}</h2>
          <van-tag round type="primary" class="status-tag">{{ data.companyProfile.status }}</van-tag>
        </div>
        <span class="role">{{ data.companyProfile.company_name }} · {{ data.companyProfile.portal_mode }}</span>
      </div>
    </div>

    <div class="shortcut-row">
      <van-button size="small" round plain type="primary" @click="handlePrimaryAction('main')">编辑主账号</van-button>
      <van-button size="small" round plain type="success" @click="handlePrimaryAction('sub')">新增子账号</van-button>
      <van-button size="small" round plain type="default" @click="handlePrimaryAction('company')">维护公司资料</van-button>
    </div>

    <van-tabs v-model:active="activeTab" color="#1677ff" title-active-color="#1677ff">
      <van-tab title="主账号信息">
        <div class="section-card">
          <van-cell title="登录账号" :value="data.mainAccount.username" />
          <van-cell title="绑定手机号" :value="data.mainAccount.phone" />
          <van-cell title="微信状态" :value="data.mainAccount.wechat_status" />
          <van-cell title="登录方式" :value="data.mainAccount.login_mode" />
          <van-cell title="最近登录" :value="data.mainAccount.last_login_at" />
          <van-cell title="创建时间" :value="data.mainAccount.created_at" />
          <div class="permission-block">
            <div class="block-title">主账号权限</div>
            <div class="tag-row">
              <van-tag v-for="item in data.mainAccount.permissions" :key="item" round type="primary" plain>{{ item }}</van-tag>
            </div>
          </div>
        </div>
      </van-tab>

      <van-tab title="子账号管理">
        <div class="section-card">
          <div class="sub-account-tip">后端接口接通后，这里将支持新增、启停、重置密码与微信绑定。</div>
          <van-cell-group inset>
            <van-cell
              v-for="account in data.subAccounts"
              :key="account.id"
              :title="account.name"
              :label="`${account.role} · ${account.phone} · 最近登录 ${account.last_login_at}`"
            >
              <template #extra>
                <div class="sub-account-extra">
                  <van-tag round :type="account.status === '启用' ? 'success' : 'default'">{{ account.status }}</van-tag>
                  <van-tag round plain type="primary">{{ account.wechat_status }}</van-tag>
                </div>
              </template>
            </van-cell>
          </van-cell-group>
          <van-button block round type="primary" class="section-action" @click="handlePrimaryAction('sub')">
            新建子账号
          </van-button>
        </div>
      </van-tab>

      <van-tab title="公司资料">
        <div class="section-card">
          <div class="company-block">
            <div class="company-logo">{{ data.companyProfile.logo_text }}</div>
            <div class="company-meta">
              <h3>{{ data.companyProfile.company_name }}</h3>
              <p>{{ data.companyProfile.industry }}</p>
            </div>
          </div>
          <van-cell title="公司简称" :value="data.companyProfile.short_name" />
          <van-cell title="联系人" :value="data.companyProfile.contact_name" />
          <van-cell title="联系电话" :value="data.companyProfile.contact_phone" />
          <van-cell title="办公地址" :label="data.companyProfile.address" vertical />
          <van-cell title="门户形态" :value="data.companyProfile.portal_mode" />
          <van-cell title="备注" :label="data.companyProfile.remark" vertical />
          <van-button block round type="default" class="section-action" @click="handlePrimaryAction('company')">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { fetchAccountCenter } from '../api/accountCenter'

const router = useRouter()
const activeTab = ref(0)
const data = ref({
  mainAccount: {},
  subAccounts: [],
  companyProfile: {}
})

const fetchData = async () => {
  data.value = await fetchAccountCenter()
}

const handlePrimaryAction = (scene) => {
  const messageMap = {
    main: '主账号编辑接口已预留，后端接通后支持资料维护、改密、微信/手机号绑定。',
    sub: '子账号管理接口已预留，后端接通后支持新增、启停、重置密码。',
    company: '公司资料接口已预留，后端接通后支持公司名称、Logo、联系人信息维护。'
  }
  showToast(messageMap[scene] || '接口已预留')
}

const handleLogout = () => {
  showConfirmDialog({
    title: '退出确认',
    message: '确定要退出当前系统吗？',
  }).then(() => {
    localStorage.removeItem('portal_token')
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
.role { font-size: 13px; opacity: 0.8; margin-top: 4px; display: block; }
.header-top {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.status-tag { border: none; }

.shortcut-row {
  display: flex;
  gap: 10px;
  padding: 16px 16px 0;
  flex-wrap: wrap;
}

.section-card {
  margin: 16px;
  background: #fff;
  border-radius: 20px;
  padding: 8px 0 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.permission-block {
  padding: 14px 16px 8px;
}
.block-title {
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
  padding: 12px 16px 8px;
  color: #64748b;
  font-size: 12px;
}
.sub-account-extra {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.company-block {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
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
  margin: 12px 16px 0;
  width: calc(100% - 32px);
}

.action-group { padding: 20px 16px; margin-top: 10px; }
.logout-btn {
  background: #fff !important;
  color: #ef4444 !important;
  border-color: #fee2e2 !important;
  font-weight: 700;
  font-size: 15px;
}

.interactive-card:active { transform: scale(0.98); transition: transform 0.1s; }
</style>
