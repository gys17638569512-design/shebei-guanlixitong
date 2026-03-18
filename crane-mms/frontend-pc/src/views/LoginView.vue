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
        <h1 class="brand-name">数字化起重机<br/>维修维保系统</h1>
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

        <div class="signal-matrix">
          <div class="signal-card">
            <span class="signal-label">系统定位</span>
            <strong>工业服务指挥舱</strong>
          </div>
          <div class="signal-card">
            <span class="signal-label">多端协同</span>
            <strong>管理端 / 客户门户 / 微信作业端</strong>
          </div>
          <div class="signal-card">
            <span class="signal-label">闭环能力</span>
            <strong>排期、执行、签字、归档一体化</strong>
          </div>
        </div>
      </div>

      <!-- 装饰圆圈 -->
      <div class="deco-grid"></div>
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

        <p class="login-tip">测试账号：admin / Admin@2024，manager01 / Manager@2024，tech01 / Tech@2024</p>

        <div class="login-footer-note">
          <span class="footer-pill">实时看板</span>
          <span class="footer-pill">工单闭环</span>
          <span class="footer-pill">移动协同</span>
        </div>
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

const getLandingPathByRole = (role) => {
  if (role === 'TECH') {
    return '/repairs'
  }
  return '/dashboard'
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await authStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功，欢迎回来！')
        const role = authStore.user?.role || response?.user?.role
        router.push(getLandingPathByRole(role))
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
  background:
    radial-gradient(circle at 15% 20%, rgba(36, 146, 242, 0.18), transparent 24%),
    radial-gradient(circle at 88% 16%, rgba(255, 179, 71, 0.14), transparent 24%),
    linear-gradient(135deg, #d9e5ef 0%, #eff4f8 36%, #fbfdff 100%);
}

.login-left {
  flex: 1;
  background:
    linear-gradient(145deg, rgba(7, 21, 33, 0.96) 0%, rgba(12, 38, 61, 0.94) 48%, rgba(18, 58, 92, 0.96) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.brand-content {
  position: relative;
  z-index: 2;
  padding: 48px;
  max-width: 520px;
}

.brand-logo svg {
  width: 64px;
  height: 64px;
  margin-bottom: 28px;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 38px;
  font-weight: 800;
  color: #fff;
  line-height: 1.18;
  margin: 0 0 18px;
  letter-spacing: 0.04em;
}

.brand-tagline {
  font-size: 15px;
  color: rgba(255,255,255,.62);
  margin: 0 0 32px;
  line-height: 1.7;
  max-width: 420px;
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
  background: var(--color-accent);
  box-shadow: 0 0 16px rgba(255, 179, 71, 0.48);
  flex-shrink: 0;
}

.signal-matrix {
  margin-top: 34px;
  display: grid;
  gap: 14px;
}

.signal-card {
  border-radius: 20px;
  padding: 16px 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
}

.signal-label {
  display: block;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255, 196, 124, 0.85);
  margin-bottom: 8px;
}

.signal-card strong {
  display: block;
  color: rgba(255, 255, 255, 0.94);
  font-size: 14px;
  line-height: 1.5;
}

.deco-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.06) 1px, transparent 1px);
  background-size: 84px 84px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.4), transparent 70%);
  opacity: 0.28;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.12;
  background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, transparent 70%);
}
.c1 { width: 420px; height: 420px; top: -100px; right: -100px; }
.c2 { width: 280px; height: 280px; bottom: 50px; left: -80px; opacity: 0.08; }
.c3 { width: 170px; height: 170px; bottom: 200px; right: 90px; opacity: 0.1; }

.login-right {
  width: 500px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(251, 253, 255, 0.74);
  padding: 48px 42px;
  backdrop-filter: blur(18px);
}

.login-box {
  width: 100%;
  max-width: 380px;
  padding: 34px 30px 28px;
  border-radius: 30px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(247, 250, 253, 0.9));
  border: 1px solid rgba(16, 33, 48, 0.08);
  box-shadow: 0 28px 56px rgba(10, 24, 39, 0.12);
}

.login-header { margin-bottom: 32px; }
.login-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
  margin: 0 0 10px;
  letter-spacing: 0.04em;
}
.login-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

.login-form :deep(.el-form-item__label) {
  font-size: 12px !important;
  font-weight: 600 !important;
  color: var(--color-text-secondary) !important;
  padding-bottom: 6px !important;
  line-height: 1 !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.login-form :deep(.el-input__wrapper) {
  border-radius: 18px !important;
  padding: 0 16px !important;
  height: 48px;
  background: rgba(245, 248, 251, 0.92) !important;
}

.login-btn {
  width: 100%;
  margin-top: 28px;
  height: 50px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  border-radius: 999px !important;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%) !important;
  border: none !important;
  letter-spacing: 0.28em;
  box-shadow: 0 16px 32px rgba(12, 117, 216, 0.24) !important;
  transition: all 0.2s ease !important;
}
.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 34px rgba(12, 117, 216, 0.3) !important;
}

.login-tip {
  text-align: center;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 18px 0 0;
  line-height: 1.6;
}

.login-footer-note {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.footer-pill {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(12, 117, 216, 0.08);
  color: var(--color-primary-dark);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

@media (max-width: 768px) {
  .login-left { display: none; }
  .login-right {
    width: 100%;
    padding: 24px;
    background: transparent;
  }
  .login-box {
    padding: 28px 22px 24px;
  }
}
</style>
