<template>
  <view class="profile-page">
    <view class="hero-card">
      <view class="avatar">{{ avatarText }}</view>
      <view class="hero-info">
        <text class="name">{{ profile.name }}</text>
        <text class="sub">{{ profile.roleLabel }}</text>
      </view>
      <view class="status-tag" :class="{ active: profile.isBoundWechat }">
        {{ profile.isBoundWechat ? '微信已绑定' : '微信未绑定' }}
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">账号信息</view>
      <view class="info-list">
        <view class="info-row">
          <text class="label">账号</text>
          <text class="value">{{ profile.username }}</text>
        </view>
        <view class="info-row">
          <text class="label">姓名</text>
          <text class="value">{{ profile.name }}</text>
        </view>
        <view class="info-row">
          <text class="label">手机号</text>
          <text class="value">{{ profile.phone }}</text>
        </view>
        <view class="info-row">
          <text class="label">邮箱</text>
          <text class="value">{{ profile.email }}</text>
        </view>
        <view class="info-row">
          <text class="label">微信绑定</text>
          <text class="value">{{ profile.isBoundWechat ? '已绑定' : '未绑定' }}</text>
        </view>
        <view class="info-row">
          <text class="label">账号状态</text>
          <text class="value">{{ profile.statusLabel }}</text>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">资料维护</view>
      <view class="form-list">
        <view class="form-item">
          <text class="form-label">显示名称</text>
          <input v-model="form.display_name" class="form-input" placeholder="用于页面展示的名称" />
        </view>
        <view class="form-item">
          <text class="form-label">姓名</text>
          <input v-model="form.name" class="form-input" placeholder="请输入真实姓名" />
        </view>
        <view class="form-item">
          <text class="form-label">手机号</text>
          <input v-model="form.phone" class="form-input" type="number" placeholder="请输入手机号" />
        </view>
        <view class="form-item">
          <text class="form-label">邮箱</text>
          <input v-model="form.email" class="form-input" placeholder="请输入邮箱" />
        </view>
      </view>
      <button class="action-btn" :loading="saving" @click="handleSaveProfile">保存资料</button>
    </view>

    <view class="section-card">
      <view class="section-title">账号绑定</view>
      <view class="bind-grid">
        <view class="bind-item">
          <text class="bind-name">手机号</text>
          <text class="bind-desc">{{ profile.mobileBound ? '手机号已绑定，可用于后续通知触达。' : '请先在上方资料维护中填写手机号并保存。' }}</text>
          <button class="bind-btn secondary" disabled>{{ profile.mobileBound ? '已绑定手机号' : '待补充手机号' }}</button>
        </view>
        <view class="bind-item">
          <text class="bind-name">微信</text>
          <text class="bind-desc">{{ profile.isBoundWechat ? '当前已绑定微信，可用于消息通知与快捷登录。' : '点击后将为当前演示账号创建小程序绑定记录。' }}</text>
          <button class="bind-btn" :loading="wechatLoading" @click="handleWechatAction">
            {{ profile.isBoundWechat ? '解除微信绑定' : '绑定微信（演示）' }}
          </button>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">操作</view>
      <button class="action-btn secondary" :loading="reloading" @click="handleReload">刷新资料</button>
      <button class="action-btn danger" @click="handleLogout">退出登录</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { bindMyWechat, getMyProfile, unbindMyWechat, updateMyProfile } from '../../api/profile'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const saving = ref(false)
const reloading = ref(false)
const wechatLoading = ref(false)
const form = reactive({
  display_name: '',
  name: '',
  phone: '',
  email: ''
})

const profile = computed(() => {
  const user = authStore.userInfo || {}
  const name = user.display_name || user.name || user.username || '工程师'
  const labelMap: Record<string, string> = {
    ADMIN: '平台管理员',
    MANAGER: '维保经理',
    TECH: '现场工程师'
  }
  const roleLabel = `${user.department ? `${user.department} · ` : ''}${user.job_title || labelMap[user.role] || '工人操作端账号'}`
  return {
    username: user.username || user.account || '待完善',
    name,
    phone: user.phone || user.mobile || '未绑定',
    email: user.email || '未填写',
    roleLabel,
    isBoundWechat: Boolean(user.wechat_bound || user.isWechatBound || user.wechat_openid),
    mobileBound: Boolean(user.mobile_bound || user.phone),
    statusLabel: user.status === 'INACTIVE' ? '停用' : '启用',
  }
})

const avatarText = computed(() => {
  const name = profile.value.name || '工'
  return name.slice(0, 1)
})

const syncForm = (user: any = {}) => {
  form.display_name = user.display_name || user.name || ''
  form.name = user.name || ''
  form.phone = user.phone || ''
  form.email = user.email || ''
}

const refreshProfile = async (showToast = false) => {
  if (!authStore.token) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }

  try {
    const data: any = await getMyProfile()
    authStore.setUserInfo(data || {})
    syncForm(data || {})
    if (showToast) {
      uni.showToast({ title: '资料已刷新', icon: 'none' })
    }
  } catch (error) {
  }
}

const handleReload = async () => {
  reloading.value = true
  try {
    await refreshProfile(true)
  } finally {
    reloading.value = false
  }
}

const handleSaveProfile = async () => {
  saving.value = true
  try {
    const data: any = await updateMyProfile({
      display_name: form.display_name,
      name: form.name,
      phone: form.phone,
      email: form.email
    })
    authStore.setUserInfo(data || {})
    syncForm(data || {})
    uni.showToast({ title: '资料已保存', icon: 'success' })
  } catch (error) {
  } finally {
    saving.value = false
  }
}

const handleWechatAction = async () => {
  wechatLoading.value = true
  try {
    if (profile.value.isBoundWechat) {
      await unbindMyWechat('miniapp')
      await refreshProfile()
      uni.showToast({ title: '微信已解绑', icon: 'success' })
    } else {
      await bindMyWechat({
        scene: 'miniapp',
        openid: `demo-openid-${Date.now()}`,
        nickname: profile.value.name
      })
      await refreshProfile()
      uni.showToast({ title: '微信已绑定', icon: 'success' })
    }
  } catch (error) {
  } finally {
    wechatLoading.value = false
  }
}

const handleLogout = () => {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出当前账号吗？',
    success: (res) => {
      if (res.confirm) authStore.logout()
    }
  })
}

onMounted(() => {
  syncForm(authStore.userInfo || {})
  refreshProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 30rpx;
  background: linear-gradient(180deg, #f7f8fa 0%, #eef4ff 100%);
}

.hero-card,
.section-card {
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  padding: 30rpx;
  margin-bottom: 24rpx;
}

.hero-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  background: linear-gradient(135deg, #2979ff 0%, #1565c0 100%);
  color: #fff;
}

.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 42rpx;
  font-weight: 700;
}

.hero-info {
  flex: 1;
}

.name {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
}

.sub {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  opacity: 0.85;
}

.status-tag {
  padding: 12rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  background: rgba(255, 255, 255, 0.22);
}

.status-tag.active {
  background: rgba(82, 196, 26, 0.2);
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 18rpx;
}

.info-list {
  display: grid;
  gap: 16rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18rpx 20rpx;
  border-radius: 16rpx;
  background: #f8fafc;
}

.label {
  color: #64748b;
}

.value {
  color: #111827;
  font-weight: 600;
}

.bind-grid {
  display: grid;
  gap: 18rpx;
}

.form-list {
  display: grid;
  gap: 18rpx;
}

.form-item,
.bind-item {
  padding: 22rpx;
  border-radius: 18rpx;
  background: #f8fafc;
}

.form-label {
  display: block;
  margin-bottom: 12rpx;
  font-size: 26rpx;
  color: #475569;
}

.form-input {
  height: 84rpx;
  line-height: 84rpx;
  padding: 0 22rpx;
  border-radius: 14rpx;
  background: #fff;
  color: #111827;
  font-size: 26rpx;
}

.bind-name {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #111827;
}

.bind-desc {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #64748b;
}

.bind-btn,
.action-btn {
  margin-top: 16rpx;
  border-radius: 999rpx;
  background: #2979ff;
  color: #fff;
  font-size: 26rpx;
}

.bind-btn {
  opacity: 1;
}

.action-btn {
  margin-top: 14rpx;
}

.bind-btn.secondary,
.action-btn.secondary {
  background: #94a3b8;
}

.action-btn.danger {
  background: #ef4444;
}
</style>
