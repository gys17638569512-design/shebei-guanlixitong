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
  background-color: #f7f8fa;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 450rpx;
  background: linear-gradient(135deg, #2979ff 0%, #1565c0 100%);
  border-bottom-left-radius: 80rpx;
  border-bottom-right-radius: 80rpx;
}

.content-box {
  position: relative;
  z-index: 10;
  padding: 0 60rpx;
}

.login-header {
  text-align: center;
  padding: 120rpx 0 60rpx;
  color: #fff;
}

.logo-circle {
  width: 140rpx;
  height: 140rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 30rpx;
  font-size: 80rpx;
  box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.15);
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
  font-size: 44rpx;
  font-weight: 800;
  display: block;
  letter-spacing: 2rpx;
}

.subtitle {
  font-size: 24rpx;
  opacity: 0.8;
  margin-top: 10rpx;
  display: block;
}

.login-form {
  background: #fff;
  border-radius: 30rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 20rpx 40rpx rgba(0,0,0,0.05);
  margin-top: 40rpx;
}

.input-item {
  display: flex;
  align-items: center;
  background-color: #f5f6f7;
  border-radius: 16rpx;
  margin-bottom: 30rpx;
  padding: 0 30rpx;
  height: 100rpx;
}

.input-icon {
  font-size: 32rpx;
  margin-right: 20rpx;
  color: #999;
}

.input {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.placeholder {
  color: #bbb;
}

.login-btn {
  margin-top: 60rpx;
  height: 100rpx;
  line-height: 100rpx;
  background: linear-gradient(90deg, #2979ff 0%, #0056e0 100%);
  color: #fff;
  border-radius: 50rpx;
  font-size: 34rpx;
  font-weight: bold;
  box-shadow: 0 10rpx 30rpx rgba(41, 121, 255, 0.3);
}

.login-footer {
  text-align: center;
  margin-top: 100rpx;
  font-size: 24rpx;
  color: #999;
}
</style>

