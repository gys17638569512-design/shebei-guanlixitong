<template>
  <div class="home-container pb-safe">
    <!-- 顶部欢迎区 -->
    <div class="header-section">
      <div class="welcome-text">
        <span class="greeting">您好,</span>
        <h2 class="company-name">{{ stats.customer_name || '加载中...' }}</h2>
      </div>
      <van-icon name="bell" class="notification-icon" />
    </div>

    <!-- 核心统计仪表盘 -->
    <div class="stats-board interactive-card">
      <div class="stats-item">
        <span class="stats-num">{{ stats.equipment_count || 0 }}</span>
        <span class="stats-label">设备总数</span>
      </div>
      <div class="stats-divider"></div>
      <div class="stats-item">
        <span class="stats-num text-warning">{{ stats.pending_order_count || 0 }}</span>
        <span class="stats-label">待办事项</span>
      </div>
    </div>

    <!-- 快捷导航 -->
    <div class="quick-nav">
      <div class="nav-item" @click="router.push('/equipments')">
        <div class="icon-wrap bg-blue"><van-icon name="shop-o" /></div>
        <span>设备一览</span>
      </div>
      <div class="nav-item" @click="router.push('/records')">
        <div class="icon-wrap bg-orange"><van-icon name="records-o" /></div>
        <span>维保记录</span>
      </div>
    </div>

    <!-- 单位基础信息 -->
    <div class="info-section">
      <h3 class="section-title">单位基本资料</h3>
      <div class="profile-card interactive-card">
        <div class="profile-row">
          <span class="row-label">单位名称</span>
          <span class="row-value">{{ profile.company_name }}</span>
        </div>
        <div class="profile-row">
          <span class="row-label">详细地址</span>
          <span class="row-value">{{ profile.address }}</span>
        </div>
        <div class="profile-row">
          <span class="row-label">联系人</span>
          <span class="row-value">{{ profile.contact_name }}</span>
        </div>
        <div class="profile-row">
          <span class="row-label">联系电话</span>
          <span class="row-value">{{ profile.contact_phone }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'

const router = useRouter()
const stats = ref({})
const profile = ref({})

const fetchData = async () => {
  try {
    const [statsRes, profileRes] = await Promise.all([
      request.get('/stats'),
      request.get('/me')
    ])
    stats.value = statsRes
    profile.value = profileRes
  } catch (err) {
    console.error('Failed to fetch data', err)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home-container {
  padding: 20px 16px;
  background-color: #f7f8fa;
  min-height: calc(100vh - 50px);
}
.pb-safe { padding-bottom: calc(env(safe-area-inset-bottom) + 30px); }

/* Header */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.greeting { font-size: 14px; color: #94a3b8; }
.company-name { 
  margin: 4px 0 0 0; 
  font-size: 22px; 
  font-weight: 800; 
  color: #1e293b; 
  letter-spacing: -0.5px;
}
.notification-icon { font-size: 24px; color: #64748b; margin-top: 8px; }

/* Stats Board */
.stats-board {
  background: linear-gradient(135deg, #1e293b, #334155);
  border-radius: 24px;
  padding: 28px 20px;
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  box-shadow: 0 10px 25px rgba(30, 41, 59, 0.15);
}
.stats-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stats-num { font-size: 28px; font-weight: 800; color: #fff; margin-bottom: 4px; }
.stats-label { font-size: 12px; color: #94a3b8; }
.stats-divider { width: 1px; height: 40px; background: rgba(255, 255, 255, 0.1); }
.text-warning { color: #fbbf24 !important; }

/* Quick Nav */
.quick-nav {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
}
.nav-item {
  flex: 1;
  background: #fff;
  border-radius: 20px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  font-size: 13px;
  font-weight: 700;
  color: #475569;
}
.icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}
.bg-blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.bg-orange { background: linear-gradient(135deg, #f59e0b, #d97706); }

/* Info Section */
.info-section { margin-bottom: 24px; }
.section-title { font-size: 16px; font-weight: 800; color: #1e293b; margin-bottom: 16px; padding-left: 4px; }
.profile-card {
  background: #fff;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}
.profile-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}
.profile-row:last-child { border-bottom: none; }
.row-label { color: #94a3b8; font-size: 13px; }
.row-value { color: #1e293b; font-size: 13px; font-weight: 600; text-align: right; max-width: 65%; }

.interactive-card:active { transform: scale(0.98); transition: transform 0.1s; }
</style>
