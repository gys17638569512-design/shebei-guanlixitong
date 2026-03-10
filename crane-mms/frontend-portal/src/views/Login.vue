<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="login-header">
        <div class="logo-box">🏗️</div>
        <h1>客户维保门户</h1>
        <p>专业 · 透明 · 高效的设备管理专家</p>
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
                placeholder="请输入手机号或客户账号"
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
        </van-form>
      </div>

      <div class="login-footer">
        <div class="footer-links">
          <span>服务条款</span>
          <span class="divider">|</span>
          <span>隐私政策</span>
        </div>
        <p>© 2024 智管起重机 · 运维管理中心</p>
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
      contact_name: res.contact_name
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
  /* 适配多端：在大屏上显示带背景图片的宽屏设计，在小屏上回退到纯色渐变 */
  background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

/* 媒体查询：大屏 (PC/Tablet) 环境下的样式覆盖 */
@media (min-width: 768px) {
  .login-wrapper {
    position: relative; /* 添加相对定位，建立 stacking context */
    background: url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop') no-repeat center center;
    background-size: cover;
  }
  .login-wrapper::before {
    content: '';
    position: absolute;
    inset: 0;
    backdrop-filter: blur(8px);
    background: rgba(15, 23, 42, 0.4);
    z-index: 0; /* 降低 z-index */
  }
  .login-container {
    background: rgba(255, 255, 255, 0.95);
    padding: 40px;
    border-radius: 24px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    position: relative;
    z-index: 10; /* 确保大幅高于 0 */
    transform: scale(1.05); /* 大屏稍作放大 */
  }
  .login-header h1 { color: #1e293b !important; }
  .login-header p { color: #64748b !important; }
  .login-card { box-shadow: none !important; padding: 10px 0 !important; }
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
  color: #1e293b;
  margin-bottom: 30px;
}

.logo-box {
  font-size: 64px;
  margin-bottom: 16px;
  filter: drop-shadow(0 8px 16px rgba(0,0,0,0.1));
}

.login-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 1px;
}

.login-header p {
  margin: 8px 0 0;
  font-size: 14px;
  color: #64748b;
}

.login-card {
  background: #fff;
  border-radius: 20px;
  padding: 30px 10px 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.06);
}

/* 登录方式切换 */
.login-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
  gap: 32px;
}
.tab-item {
  font-size: 16px;
  color: #64748b;
  font-weight: 500;
  padding-bottom: 8px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}
.tab-item.active {
  color: #1677ff;
  font-weight: 700;
}
.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  background: #1677ff;
  border-radius: 2px;
}

.custom-field {
  padding: 16px 12px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
}

.code-btn {
  height: 32px;
  font-weight: 600;
}

.submit-box {
  margin: 32px 16px 20px;
}

.login-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, #1677ff 0%, #0958d9 100%) !important;
  border: none !important;
  box-shadow: 0 6px 16px rgba(22, 137, 250, 0.3) !important;
}

/* 其他登录方式 */
.other-methods {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
.wechat-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #f0fdf4;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s;
}
.wechat-btn:active { transform: scale(0.9); }

.login-footer {
  text-align: center;
  margin-top: 40px;
  color: #94a3b8;
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

