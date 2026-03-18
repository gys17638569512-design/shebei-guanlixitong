<template>
  <view class="home-container">
    <!-- 顶部弧形渐变背景与用户信息 -->
    <view class="header-bg">
      <view class="user-card">
        <view class="user-info">
          <text class="greeting">你好, {{ displayName }} 👋</text>
          <text class="role">{{ roleLabel }}</text>
        </view>
        <view class="header-actions">
          <view class="profile-btn" @click="goProfile">
            <text class="icon">👤</text>
          </view>
          <view class="logout-btn" @click="handleLogout">
            <text class="icon">🚪</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 悬浮的分类 Tab -->
    <view class="tabs-container">
      <view class="task-tabs shadow-sm">
        <view 
          v-for="(tab, index) in tabs" 
          :key="index" 
          class="tab-item" 
          :class="{ active: currentTab === index }"
          @click="currentTab = index"
        >
          <text>{{ tab }}</text>
          <view class="active-line" v-if="currentTab === index"></view>
        </view>
      </view>
    </view>

    <!-- 列表区域 -->
    <scroll-view scroll-y class="list-area" @refresherrefresh="onRefresh" :refresher-enabled="true" :refresher-triggered="triggered">
      <view v-if="filteredOrders.length > 0" class="order-list pb-safe">
        <view 
          v-for="order in filteredOrders" 
          :key="order.id" 
          class="order-card interactive-card"
          @click="goDetail(order.id)"
        >
          <view class="card-header">
            <view class="type-badge">{{ order.order_type }}</view>
            <view class="status-pill" :class="order.status.toLowerCase()">
              <view class="dot"></view>
              {{ getStatusLabel(order.status) }}
            </view>
          </view>
          
          <view class="card-body">
            <text class="equipment-title">{{ order.equipment_name }}</text>
            <view class="info-group">
              <view class="info-row">
                <text class="icon">📅</text>
                <text class="value font-mono">{{ order.plan_date }}</text>
              </view>
              <view class="info-row">
                <text class="icon">🏢</text>
                <text class="value text-ellipsis">{{ order.customer_name }}</text>
              </view>
            </view>
          </view>
          
          <view class="card-footer">
            <text class="order-no">#ORD-{{ String(order.id).padStart(6, '0') }}</text>
            <view class="action-text" v-if="order.status === 'PENDING' || order.status === 'IN_PROGRESS'">
              立刻处理 <text class="arrow">→</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-else class="empty-state">
        <view class="empty-icon">📭</view>
        <text class="empty-text">当前分类下暂无维保任务</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getMyOrders } from '../../api/order'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const orders = ref<any[]>([])
const tabs = ['全部', '待完成', '已完工']
const currentTab = ref(1) // 默认显示待完成
const triggered = ref(false)

const displayName = computed(() => {
  const user = authStore.userInfo || {}
  return user.display_name || user.name || user.username || '工程师'
})

const roleLabel = computed(() => {
  const user = authStore.userInfo || {}
  const labelMap: Record<string, string> = {
    ADMIN: '平台管理员',
    MANAGER: '维保经理',
    TECH: '现场工程师'
  }
  const department = user.department ? `${user.department} · ` : ''
  const title = user.job_title || labelMap[user.role] || '工人操作端账号'
  return `${department}${title}`
})

const loadOrders = async () => {
  try {
    const res: any = await getMyOrders()
    orders.value = res || []
  } catch (err) {}
}

const onRefresh = async () => {
  triggered.value = true
  await loadOrders()
  triggered.value = false
}

const filteredOrders = computed(() => {
  if (currentTab.value === 0) return orders.value
  if (currentTab.value === 1) return orders.value.filter(o => o.status !== 'COMPLETED')
  return orders.value.filter(o => o.status === 'COMPLETED')
})

const getStatusLabel = (s: string) => {
  const map: any = { PENDING: '待处理', IN_PROGRESS: '进行中', PENDING_SIGN: '待签字', COMPLETED: '已完成' }
  return map[s] || s
}

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/orderDetail/orderDetail?id=${id}` })
}

const goProfile = () => {
  uni.navigateTo({ url: '/pages/profile/profile' })
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) authStore.logout()
    }
  })
}

onMounted(() => {
  if (!authStore.token) {
    uni.reLaunch({ url: '/pages/login/login' })
  } else {
    loadOrders()
  }
})
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f7f8fa;
}

/* 顶部背景与用户信息 */
.header-bg {
  background: linear-gradient(135deg, #2979ff 0%, #1565c0 100%);
  padding: 100rpx 40rpx 80rpx;
  border-bottom-left-radius: 60rpx;
  border-bottom-right-radius: 60rpx;
  position: relative;
  z-index: 10;
}

.user-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.greeting {
  font-size: 40rpx;
  font-weight: 800;
  color: #fff;
  display: block;
  letter-spacing: 2rpx;
}

.role {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 10rpx;
  display: block;
}

.profile-btn,
.logout-btn {
  width: 72rpx;
  height: 72rpx;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2rpx solid rgba(255, 255, 255, 0.3);
}

.profile-btn .icon,
.logout-btn .icon {
  font-size: 32rpx;
}

/* 悬浮选项卡 */
.tabs-container {
  padding: 0 40rpx;
  margin-top: -46rpx;
  position: relative;
  z-index: 20;
}

.task-tabs {
  display: flex;
  background-color: #fff;
  height: 92rpx;
  border-radius: 20rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 500;
  color: #64748b;
  position: relative;
  transition: all 0.2s;
}

.tab-item.active {
  color: #2979ff;
  font-size: 30rpx;
  font-weight: bold;
}

.active-line {
  position: absolute;
  bottom: 0;
  width: 32rpx;
  height: 6rpx;
  background: #2979ff;
  border-radius: 6rpx 6rpx 0 0;
}

/* 列表区 */
.list-area {
  flex: 1;
  overflow: hidden;
  margin-top: 20rpx;
}

.order-list {
  padding: 20rpx 40rpx;
}

.pb-safe {
  padding-bottom: calc(env(safe-area-inset-bottom) + 40rpx);
}

/* 现代卡片样式 */
.order-card {
  background-color: #fff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
  border: 1rpx solid rgba(0, 0, 0, 0.02);
  transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.interactive-card:active {
  transform: scale(0.96);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.type-badge {
  font-size: 22rpx;
  font-weight: bold;
  background-color: #f1f5f9;
  color: #475569;
  padding: 6rpx 16rpx;
  border-radius: 12rpx;
  letter-spacing: 1rpx;
}

.status-pill {
  display: flex;
  align-items: center;
  font-size: 22rpx;
  font-weight: bold;
  padding: 6rpx 16rpx;
  border-radius: 30rpx;
}

.status-pill .dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  margin-right: 8rpx;
}

.status-pill.pending { background: #fffbeb; color: #d97706; }
.status-pill.pending .dot { background: #f59e0b; }
.status-pill.in_progress { background: #eff6ff; color: #1d4ed8; }
.status-pill.in_progress .dot { background: #3b82f6; }
.status-pill.pending_sign { background: #fef2f2; color: #b91c1c; }
.status-pill.pending_sign .dot { background: #ef4444; }
.status-pill.completed { background: #f0fdf4; color: #15803d; }
.status-pill.completed .dot { background: #22c55e; }

.card-body {
  margin-bottom: 24rpx;
}

.equipment-title {
  font-size: 34rpx;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 20rpx;
  display: block;
  line-height: 1.4;
}

.info-group {
  background: #f8fafc;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 10rpx;
  font-size: 26rpx;
}
.info-row:last-child { margin-bottom: 0; }

.info-row .icon {
  font-size: 24rpx;
  margin-right: 12rpx;
}

.info-row .value {
  color: #334155;
  flex: 1;
  font-weight: 500;
}

.font-mono {
  font-family: 'Courier New', Courier, monospace;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-footer {
  padding-top: 24rpx;
  border-top: 2rpx dashed #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-no {
  font-size: 24rpx;
  color: #94a3b8;
  font-weight: bold;
}

.action-text {
  font-size: 26rpx;
  font-weight: bold;
  color: #2979ff;
  display: flex;
  align-items: center;
}

.action-text .arrow {
  margin-left: 6rpx;
  font-size: 28rpx;
}

.empty-state {
  padding-top: 200rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
  opacity: 0.8;
}

.empty-text {
  color: #94a3b8;
  font-size: 28rpx;
}
</style>
