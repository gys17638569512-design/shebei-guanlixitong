<template>
  <div class="home-container pb-safe">
    <!-- 顶部欢迎区 -->
    <div class="header-section">
      <div class="welcome-text">
        <span class="section-kicker">客户服务门户</span>
        <span class="greeting">您好,</span>
        <h2 class="company-name">{{ stats.customer_name || '加载中...' }}</h2>
        <span class="account-name">{{ currentOperator }}</span>
      </div>
      <div class="notification-pill">
        <van-icon name="bell" class="notification-icon" />
        <span>{{ Number(stats.pending_order_count || 0) > 0 ? '待处理提醒' : '运行平稳' }}</span>
      </div>
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
      <div class="nav-item" @click="router.push('/account-center')">
        <div class="icon-wrap bg-green"><van-icon name="friends-o" /></div>
        <span>账号中心</span>
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
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { getPortalSession } from '../utils/portalAuth'

const router = useRouter()
const stats = ref({})
const profile = ref({})
const portalCustomer = ref(getPortalSession())

const currentOperator = computed(() => {
  if (!portalCustomer.value?.contact_name) return '欢迎回来'
  if (portalCustomer.value?.account_type === 'CUSTOMER_ACCOUNT') {
    return `当前账号：${portalCustomer.value.contact_name}`
  }
  return `主账号：${portalCustomer.value.contact_name}`
})

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
  padding: 20px 16px 10px;
  min-height: calc(100vh - 50px);
}
.pb-safe { padding-bottom: calc(env(safe-area-inset-bottom) + 30px); }

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  gap: 14px;
  margin-bottom: 22px;
  padding: 22px 18px;
  border-radius: 28px;
  background:
    linear-gradient(145deg, rgba(8, 21, 33, 0.96) 0%, rgba(12, 38, 61, 0.94) 56%, rgba(19, 74, 113, 0.9) 100%);
  box-shadow: 0 24px 46px rgba(8, 24, 40, 0.16);
  position: relative;
  overflow: hidden;
}

.header-section::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 80px 80px;
  opacity: 0.28;
}

.welcome-text,
.notification-pill {
  position: relative;
  z-index: 1;
}

.section-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 196, 124, 0.94);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.greeting { font-size: 14px; color: rgba(236, 242, 247, 0.68); }
.company-name {
  margin: 4px 0 0 0; 
  font-family: var(--portal-font-display);
  font-size: 24px; 
  font-weight: 800; 
  color: #f8fbff; 
  letter-spacing: 0.04em;
}
.account-name {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  color: rgba(236, 242, 247, 0.74);
}

.notification-pill {
  min-width: 112px;
  padding: 14px 12px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.12);
  color: #f8fbff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  text-align: center;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.notification-icon { font-size: 22px; color: rgba(255, 196, 124, 0.96); }

.stats-board {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(246, 249, 252, 0.9));
  border-radius: 28px;
  padding: 28px 20px;
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  box-shadow: 0 18px 36px rgba(8, 24, 40, 0.08);
  border: 1px solid rgba(16, 33, 48, 0.08);
  position: relative;
  overflow: hidden;
}

.stats-board::after {
  content: "";
  position: absolute;
  right: -30px;
  top: -26px;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(12, 117, 216, 0.14), transparent 68%);
}
.stats-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
}
.stats-num {
  font-family: var(--portal-font-display);
  font-size: 30px;
  font-weight: 800;
  color: var(--portal-ink);
  margin-bottom: 4px;
}
.stats-label {
  font-size: 12px;
  color: var(--portal-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.stats-divider { width: 1px; height: 44px; background: rgba(16, 33, 48, 0.08); }
.text-warning { color: #fbbf24 !important; }

.quick-nav {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
}
.nav-item {
  flex: 1;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 249, 252, 0.88));
  border-radius: 24px;
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  box-shadow: 0 16px 28px rgba(8, 24, 40, 0.06);
  border: 1px solid rgba(16, 33, 48, 0.06);
  font-size: 12px;
  font-weight: 700;
  color: var(--portal-text);
  letter-spacing: 0.04em;
}
.icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  box-shadow: 0 14px 24px rgba(8, 24, 40, 0.12);
}
.bg-blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.bg-orange { background: linear-gradient(135deg, #f59e0b, #d97706); }
.bg-green { background: linear-gradient(135deg, #22c55e, #16a34a); }

.info-section { margin-bottom: 24px; }
.section-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--portal-ink);
  margin-bottom: 16px;
  padding-left: 4px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.profile-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 249, 252, 0.88));
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 18px 32px rgba(8, 24, 40, 0.06);
  border: 1px solid rgba(16, 33, 48, 0.06);
}
.profile-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(16, 33, 48, 0.06);
}
.profile-row:last-child { border-bottom: none; }
.row-label { color: var(--portal-muted); font-size: 13px; }
.row-value { color: var(--portal-ink); font-size: 13px; font-weight: 600; text-align: right; max-width: 65%; }

@media (max-width: 420px) {
  .header-section {
    flex-direction: column;
  }

  .notification-pill {
    width: 100%;
    flex-direction: row;
    justify-content: center;
  }
}
</style>
