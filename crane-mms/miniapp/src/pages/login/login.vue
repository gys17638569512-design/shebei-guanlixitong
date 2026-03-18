<template>
  <view class="login-container">
    <view class="login-bg"></view>
    
    <view class="content-box">
      <view class="login-header">
        <view class="logo-circle">
          <view class="logo-mark">
            <view class="logo-roof"></view>
            <view class="logo-cross"></view>
            <view class="logo-dot"></view>
          </view>
        </view>
        <text class="title">数字化起重机维修维保系统</text>
        <text class="subtitle">工人操作端 · 现场作业中心</text>
        <view class="header-tags">
          <text class="header-tag">离线可用</text>
          <text class="header-tag">微信协同</text>
          <text class="header-tag">电子签字</text>
        </view>
      </view>
  
      <view class="login-form">
        <view class="input-item">
          <text class="input-icon">👤</text>
          <input v-model="username" class="input" placeholder="请输入员工账号" placeholder-class="placeholder" />
        </view>
        <view class="input-item">
          <text class="input-icon">🔒</text>
          <input v-model="password" class="input" password placeholder="请输入登录密码" placeholder-class="placeholder" />
        </view>
        
        <button class="login-btn" :loading="loading" @click="handleLogin">登 录 系 统</button>

        <text class="login-tip">工程师测试账号：tech01 / Tech@2024</text>
      </view>
  
      <view class="login-footer">
        <text>© 2024 数字化起重机维修维保系统</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { login } from '../../api/auth'
import { useAuthStore } from '../../stores/auth'

const username = ref('')
const password = ref('')
const loading = ref(false)
const authStore = useAuthStore()

const handleLogin = async () => {
  if (!username.value || !password.value) {
    uni.showToast({ title: '请填写账号和密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res: any = await login({ username: username.value, password: password.value })

    authStore.setAuth(res.access_token, res.user || {})

    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/index/index' })
    }, 1000)
  } catch (err) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 520rpx;
  background: linear-gradient(145deg, rgba(8, 21, 33, 0.96) 0%, rgba(12, 38, 61, 0.94) 56%, rgba(19, 74, 113, 0.9) 100%);
  border-bottom-left-radius: 110rpx;
  border-bottom-right-radius: 110rpx;
}

.login-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 2rpx, transparent 2rpx),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 2rpx, transparent 2rpx);
  background-size: 90rpx 90rpx;
  opacity: 0.3;
}

.content-box {
  position: relative;
  z-index: 10;
  padding: 0 52rpx;
}

.login-header {
  text-align: center;
  padding: 120rpx 0 56rpx;
  color: #fff;
}

.logo-circle {
  width: 140rpx;
  height: 140rpx;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 30rpx;
  font-size: 80rpx;
  box-shadow: 0 24rpx 46rpx rgba(8, 24, 40, 0.18);
}

.logo-mark {
  width: 72rpx;
  height: 72rpx;
  position: relative;
}

.logo-roof {
  position: absolute;
  inset: 10rpx;
  border: 6rpx solid #2979ff;
  border-bottom-width: 10rpx;
  border-radius: 12rpx;
}

.logo-cross {
  position: absolute;
  top: 14rpx;
  bottom: 14rpx;
  left: 50%;
  width: 6rpx;
  transform: translateX(-50%);
  background: rgba(41, 121, 255, 0.55);
  border-radius: 999rpx;
}

.logo-cross::before {
  content: '';
  position: absolute;
  top: 22rpx;
  left: -22rpx;
  width: 50rpx;
  height: 6rpx;
  background: rgba(41, 121, 255, 0.55);
  border-radius: 999rpx;
}

.logo-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 16rpx;
  height: 16rpx;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: #2979ff;
}

.title {
  font-size: 42rpx;
  font-weight: 800;
  display: block;
  letter-spacing: 4rpx;
}

.subtitle {
  font-size: 24rpx;
  opacity: 0.8;
  margin-top: 10rpx;
  display: block;
}

.header-tags {
  margin-top: 24rpx;
  display: flex;
  justify-content: center;
  gap: 12rpx;
  flex-wrap: wrap;
}

.header-tag {
  display: inline-flex;
  align-items: center;
  min-height: 48rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 196, 124, 0.96);
  font-size: 20rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
}

.login-form {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(246, 249, 252, 0.9));
  border-radius: 40rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 30rpx 60rpx rgba(8, 24, 40, 0.12);
  margin-top: 40rpx;
  border: 2rpx solid rgba(16, 33, 48, 0.06);
}

.input-item {
  display: flex;
  align-items: center;
  background-color: rgba(239, 244, 249, 0.9);
  border-radius: 24rpx;
  margin-bottom: 30rpx;
  padding: 0 30rpx;
  height: 100rpx;
}

.input-icon {
  font-size: 32rpx;
  margin-right: 20rpx;
  color: #75889a;
}

.input {
  flex: 1;
  font-size: 30rpx;
  color: #102130;
}

.placeholder {
  color: #90a1b1;
}

.login-btn {
  margin-top: 60rpx;
  height: 100rpx;
  line-height: 100rpx;
  background: linear-gradient(135deg, #136fda 0%, #094d8d 100%);
  color: #fff;
  border-radius: 999rpx;
  font-size: 32rpx;
  font-weight: bold;
  box-shadow: 0 22rpx 42rpx rgba(19, 111, 218, 0.24);
  letter-spacing: 6rpx;
}

.login-tip {
  display: block;
  margin-top: 24rpx;
  text-align: center;
  font-size: 24rpx;
  color: #7f8ea3;
  line-height: 1.7;
}

.login-footer {
  text-align: center;
  margin-top: 100rpx;
  font-size: 24rpx;
  color: #7f8ea3;
}
</style>

