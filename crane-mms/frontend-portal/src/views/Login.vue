<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="login-header">
        <div class="logo-box" aria-hidden="true">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" rx="18" fill="#1677FF"/>
            <path d="M14 46V24L32 12L50 24V46" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M32 12V46M14 29H50" stroke="white" stroke-width="2.8" stroke-linecap="round" opacity="0.55"/>
            <circle cx="32" cy="32" r="5.5" fill="white"/>
          </svg>
        </div>
        <h1>数字化起重机维修维保系统</h1>
        <p>客户服务门户 · 专业 · 透明 · 高效</p>
        <div class="header-chips">
          <span>设备总览</span>
          <span>电子签字</span>
          <span>微信协同</span>
        </div>
      </div>

      <div class="login-card">
        <!-- 登录方式切换 Tab -->
        <div class="login-tabs">
          <span 
            class="tab-item" 
            :class="{ active: loginType === 'pwd' }"
            @click="loginType = 'pwd'"
          >账号密码登录</span>
          <span 
            class="tab-item" 
            :class="{ active: loginType === 'sms' }"
            @click="loginType = 'sms'"
          >验证码登录</span>
        </div>

        <van-form @submit="handleLogin" class="login-form">
          <van-cell-group inset :border="false">
            
            <!-- 账号密码模式 -->
            <template v-if="loginType === 'pwd'">
              <van-field
                v-model="username"
                name="username"
                label="账号"
                placeholder="请输入客户登录手机号"
                left-icon="user-o"
                :rules="[{ required: true, message: '请填写账号' }]"
                class="custom-field"
              />
              <van-field
                v-model="password"
                type="password"
                name="password"
                label="密码"
                placeholder="请输入登录密码"
                left-icon="lock-o"
                :rules="[{ required: true, message: '请填写密码' }]"
                class="custom-field"
              />
            </template>

            <!-- 验证码模式 (暂留UI) -->
            <template v-else>
              <van-field
                v-model="phone"
                name="phone"
                label="手机号"
                placeholder="请输入关联手机号"
                left-icon="phone-o"
                :rules="[{ required: true, message: '请填写手机号' }, { pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误' }]"
                class="custom-field"
              />
              <van-field
                v-model="smsCode"
                center
                clearable
                label="验证码"
                placeholder="六位数字"
                left-icon="shield-check-o"
                :rules="[{ required: true, message: '按需填写' }]"
                class="custom-field"
              >
                <template #button>
                  <van-button 
                    size="small" type="primary" plain round 
                    :disabled="countdown > 0 || !phone"
                    @click="sendCode" class="code-btn"
                  >
                    {{ countdown > 0 ? `${countdown}s` : '获取' }}
                  </van-button>
                </template>
              </van-field>
            </template>
          </van-cell-group>
          
          <div class="submit-box">
            <van-button 
              round block type="primary" native-type="submit" 
              :loading="loading" class="login-btn"
            >
              立 即 登 录
            </van-button>
          </div>
          
          <!-- 预留其他登录方式入口 -->
          <div class="other-methods">
            <span class="wechat-btn" @click="showToast('微信登录开发中...')">
              <van-icon name="wechat" color="#07c160" size="24" />
            </span>
          </div>

          <p class="login-tip">测试账号：13800138000 / 123456</p>
        </van-form>
      </div>

      <div class="login-footer">
        <div class="footer-links">
          <span>服务条款</span>
          <span class="divider">|</span>
          <span>隐私政策</span>
        </div>
        <p>© 2024 数字化起重机维修维保系统</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import request from '../utils/request'

const router = useRouter()
const loginType = ref('pwd') // 默认账号密码登录
const username = ref('')
const password = ref('')
const phone = ref('')
const smsCode = ref('')
const loading = ref(false)
const countdown = ref(0)
let timer = null

const sendCode = async () => {
  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    return showToast('请输入有效的手机号')
  }
  try {
    const res = await request.post('/auth/send_code', { phone: phone.value })
    showToast({ message: res.msg || '验证码已发送', type: 'success' })
    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (err) {}
}

const handleLogin = async () => {
  loading.value = true
  try {
    let payload = {}
    if (loginType.value === 'pwd') {
      payload = { username: username.value, password: password.value, login_type: 'pwd' }
    } else {
      payload = { phone: phone.value, code: smsCode.value, login_type: 'sms' }
    }

    const res = await request.post('/auth/login', payload)
    
    localStorage.setItem('portal_token', res.access_token)
    localStorage.setItem('portal_customer', JSON.stringify({
      id: res.customer_id,
      company_name: res.company_name,
      contact_name: res.contact_name,
      account_id: res.account_id || null,
      account_role: res.account_role || '',
      role_label: res.role_label || '',
      account_type: res.account_type || 'CUSTOMER'
    }))
    
    showToast({ message: '登录成功', type: 'success' })
    router.push('/')
  } catch (err) {} finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(12, 117, 216, 0.18), transparent 26%),
    radial-gradient(circle at 90% 12%, rgba(255, 179, 71, 0.16), transparent 24%),
    linear-gradient(140deg, #dfe8f0 0%, #eff4f8 34%, #fbfdff 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}

.login-wrapper::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.26) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.26) 1px, transparent 1px);
  background-size: 110px 110px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.28), transparent 76%);
  opacity: 0.5;
}

@media (min-width: 768px) {
  .login-container {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(247, 250, 253, 0.9));
    padding: 42px 40px 34px;
    border-radius: 30px;
    box-shadow: 0 32px 64px rgba(8, 24, 40, 0.14);
    border: 1px solid rgba(16, 33, 48, 0.08);
    position: relative;
    z-index: 1;
    transform: scale(1.02);
  }
  .login-card { box-shadow: none !important; padding: 12px 0 0 !important; background: transparent !important; }
  .login-footer p { color: #94a3b8 !important; }
}

.login-container {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 2;
}

.login-header {
  text-align: center;
  color: var(--portal-ink);
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

.logo-box {
  width: 88px;
  height: 88px;
  margin: 0 auto 16px;
  filter: drop-shadow(0 12px 20px rgba(12, 117, 216, 0.18));
}

.logo-box svg {
  width: 100%;
  height: 100%;
  display: block;
}

.login-header h1 {
  margin: 0;
  font-family: var(--portal-font-display);
  font-size: 30px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.login-header p {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--portal-text);
}

.header-chips {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.header-chips span {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--portal-primary-dark);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  box-shadow: 0 8px 18px rgba(8, 24, 40, 0.05);
}

.login-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 250, 253, 0.92));
  border-radius: 26px;
  padding: 30px 10px 20px;
  box-shadow: 0 24px 46px rgba(8, 24, 40, 0.1);
  border: 1px solid rgba(16, 33, 48, 0.08);
}

.login-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
  gap: 32px;
}
.tab-item {
  font-size: 16px;
  color: var(--portal-muted);
  font-weight: 600;
  padding-bottom: 8px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}
.tab-item.active {
  color: var(--portal-primary);
  font-weight: 700;
}
.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 3px;
  background: linear-gradient(135deg, var(--portal-primary), var(--portal-accent));
  border-radius: 2px;
}

.custom-field {
  padding: 16px 12px;
  background: rgba(245, 248, 251, 0.9);
  border-radius: 18px;
  margin-bottom: 12px;
  border: 1px solid rgba(16, 33, 48, 0.05);
}

.code-btn {
  height: 32px;
  font-weight: 600;
}

.submit-box {
  margin: 32px 16px 20px;
}

.login-btn {
  height: 50px;
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--portal-primary) 0%, var(--portal-primary-dark) 100%) !important;
  border: none !important;
  box-shadow: 0 16px 30px rgba(12, 117, 216, 0.24) !important;
  letter-spacing: 0.12em;
}

.other-methods {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.login-tip {
  margin: 18px 0 0;
  text-align: center;
  font-size: 12px;
  color: var(--portal-muted);
}

.wechat-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 12px 22px rgba(8, 24, 40, 0.08);
}
.wechat-btn:active { transform: scale(0.9); }

.login-footer {
  text-align: center;
  margin-top: 34px;
  color: var(--portal-muted);
}

.footer-links {
  font-size: 13px;
  margin-bottom: 12px;
}

.divider {
  margin: 0 16px;
  color: #cbd5e1;
}

.login-footer p {
  font-size: 12px;
  transform: scale(0.9);
}
</style>

