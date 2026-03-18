<template>
  <div class="profile-container pb-safe">
    <!-- 顶部背景与头像 -->
    <div class="profile-header">
      <div class="avatar-wrap">
        <van-icon name="manager" class="avatar-icon" />
      </div>
      <div class="user-meta">
        <h2 class="name">{{ profile.contact_name || '加载中...' }}</h2>
        <span class="role">客户代表 · {{ profile.company_name }}</span>
      </div>
    </div>

    <!-- 单位详情卡片 -->
    <div class="info-group">
      <div class="group-title">单位详细资料</div>
      <div class="info-card interactive-card">
        <van-cell title="公司全称" :value="profile.company_name" />
        <van-cell title="联系电话" :value="profile.contact_phone" />
        <van-cell title="办公地址" :label="profile.address" vertical />
        <van-cell title="注册时间" :value="profile.created_at" />
      </div>
    </div>

    <!-- 管理操作 -->
    <div class="action-group">
      <van-button 
        block 
        round 
        class="logout-btn"
        @click="handleLogout"
      >
        安全退出登录
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog } from 'vant'
import request from '../utils/request'

const router = useRouter()
const profile = ref({})

const fetchData = async () => {
  try {
    const res = await request.get('/me')
    profile.value = res || {}
  } catch (err) {
    console.error(err)
  }
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
.profile-container { background-color: #f7f8fa; min-height: 100vh; }
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

.info-group { padding: 20px 16px; }
.group-title { font-size: 14px; color: #94a3b8; font-weight: 700; margin-bottom: 12px; padding-left: 4px; }
.info-card { border-radius: 20px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }

.action-group { padding: 20px 16px; margin-top: 10px; }
.logout-btn {
  background: #fff !important;
  color: #ef4444 !important;
  border-color: #fee2e2 !important;
  font-weight: 700;
  font-size: 15px;
}

.interactive-card:active { transform: scale(0.98); transiton: transform 0.1s; }
</style>
