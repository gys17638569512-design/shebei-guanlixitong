<template>
  <div class="login-page">
    <!-- 左侧：品牌展示区 -->
    <div class="login-left">
      <div class="brand-content">
        <div class="brand-logo">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="48" height="48" rx="14" fill="rgba(255,255,255,0.15)"/>
            <path d="M10 36V20L24 10l14 10v16" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M24 10v26M10 24h28" stroke="white" stroke-width="2" stroke-linecap="round" opacity="0.5"/>
            <circle cx="24" cy="24" r="4" fill="white"/>
          </svg>
        </div>
        <h1 class="brand-name">智能起重机<br/>维保管理系统</h1>
        <p class="brand-tagline">全生命周期数字化维保 · 安全可靠 · 高效运营</p>

        <div class="feature-list">
          <div class="feature-item">
            <span class="feature-dot"></span>
            客户档案与设备全生命周期管理
          </div>
          <div class="feature-item">
            <span class="feature-dot"></span>
            工单派发与现场移动端作业
          </div>
          <div class="feature-item">
            <span class="feature-dot"></span>
            电子签名与PDF报告自动生成
          </div>
          <div class="feature-item">
            <span class="feature-dot"></span>
            特检预警与维保计划智能排期
          </div>
        </div>
      </div>

      <!-- 装饰圆圈 -->
      <div class="deco-circle c1"></div>
      <div class="deco-circle c2"></div>
      <div class="deco-circle c3"></div>
    </div>

    <!-- 右侧：登录表单 -->
    <div class="login-right">
      <div class="login-box">
        <div class="login-header">
          <h2 class="login-title">欢迎回来</h2>
          <p class="login-subtitle">请登录您的账户以继续</p>
        </div>

        <el-form
          :model="loginForm"
          :rules="rules"
          ref="loginFormRef"
          label-position="top"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item label="登录账号" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入账号"
              size="large"
              :prefix-icon="UserIcon"
              autocomplete="username"
            />
          </el-form-item>

          <el-form-item label="登录密码" prop="password" style="margin-top: 16px;">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="LockIcon"
              show-password
              autocomplete="current-password"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中…' : '登 录' }}
          </el-button>
        </el-form>

        <p class="login-tip">管理员账号：admin / 密码：Admin@2024</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref(null)
const loading = ref(false)

// 内联 SVG 图标组件，避免额外依赖
const UserIcon = markRaw({
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8', style: 'width:16px;height:16px' }, [
      h('path', { d: 'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2' }),
      h('circle', { cx: '12', cy: '7', r: '4' })
    ])
  }
})
const LockIcon = markRaw({
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8', style: 'width:16px;height:16px' }, [
      h('rect', { x: '3', y: '11', width: '18', height: '11', rx: '2', ry: '2' }),
      h('path', { d: 'M7 11V7a5 5 0 0110 0v4' })
    ])
  }
})

import { h } from 'vue'

const loginForm = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功，欢迎回来！')
        router.push('/')
      } catch {
        ElMessage.error('账号或密码错误，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 左侧品牌区 */
.login-left {
  flex: 1;
  background: linear-gradient(135deg, #0d1b2a 0%, #0e2a4a 40%, #0a3d7a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.brand-content {
  position: relative;
  z-index: 2;
  padding: 40px;
  max-width: 420px;
}

.brand-logo svg {
  width: 56px;
  height: 56px;
  margin-bottom: 24px;
}

.brand-name {
  font-size: 32px;
  font-weight: 800;
  color: #fff;
  line-height: 1.3;
  margin: 0 0 16px;
  letter-spacing: -0.02em;
}

.brand-tagline {
  font-size: 15px;
  color: rgba(255,255,255,.55);
  margin: 0 0 36px;
  line-height: 1.6;
}

.feature-list { display: flex; flex-direction: column; gap: 14px; }
.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255,255,255,.75);
  font-size: 14px;
  font-weight: 500;
}
.feature-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1677ff;
  box-shadow: 0 0 8px rgba(22,119,255,.6);
  flex-shrink: 0;
}

/* 装饰圆圈 */
.deco-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.06;
  background: radial-gradient(circle, #fff 0%, transparent 70%);
}
.c1 { width: 400px; height: 400px; top: -100px; right: -100px; }
.c2 { width: 250px; height: 250px; bottom: 50px; left: -80px; opacity: 0.04; }
.c3 { width: 150px; height: 150px; bottom: 200px; right: 80px; opacity: 0.05; }

/* 右侧表单区 */
.login-right {
  width: 460px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  padding: 40px;
}

.login-box { width: 100%; max-width: 360px; }

.login-header { margin-bottom: 32px; }
.login-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--color-text-primary);
  margin: 0 0 8px;
  letter-spacing: -0.02em;
}
.login-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.login-form :deep(.el-form-item__label) {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: var(--color-text-regular) !important;
  padding-bottom: 6px !important;
  line-height: 1 !important;
}
.login-form :deep(.el-input__wrapper) {
  border-radius: var(--radius-md) !important;
  padding: 0 14px !important;
  height: 44px;
}

.login-btn {
  width: 100%;
  margin-top: 28px;
  height: 46px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  border-radius: var(--radius-md) !important;
  background: linear-gradient(135deg, #1677ff 0%, #0958d9 100%) !important;
  border: none !important;
  letter-spacing: 2px;
  box-shadow: 0 6px 20px rgba(22,119,255,.4) !important;
  transition: all 0.2s ease !important;
}
.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(22,119,255,.5) !important;
}

.login-tip {
  text-align: center;
  font-size: 12px;
  color: var(--color-text-placeholder);
  margin: 20px 0 0;
}

@media (max-width: 768px) {
  .login-left { display: none; }
  .login-right { width: 100%; padding: 24px; }
}
</style>