<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <!-- Logo 区域 -->
      <div class="sidebar-logo">
        <div class="logo-icon">
          <img src="/brand-mark.svg" alt="品牌标识" />
        </div>
        <div class="logo-text">
          <div class="logo-name">数字化起重机维修维保系统</div>
          <div class="logo-sub">管理端</div>
          <div class="logo-status">多端协同 · 指挥中枢</div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <router-link
          v-if="hasPermission(['ADMIN', 'MANAGER'])"
          to="/dashboard"
          class="nav-item"
          :class="{ active: isActive('/dashboard') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </span>
          <span class="nav-label">控制看板</span>
        </router-link>

        <router-link
          v-if="hasPermission(['ADMIN', 'MANAGER'])"
          to="/customers"
          class="nav-item"
          :class="{ active: isActive('/customers') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 00-3-3.87"/>
              <path d="M16 3.13a4 4 0 010 7.75"/>
            </svg>
          </span>
          <span class="nav-label">客户管理</span>
        </router-link>

        <router-link
          v-if="hasPermission(['ADMIN', 'MANAGER'])"
          to="/equipments"
          class="nav-item"
          :class="{ active: isActive('/equipments') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <rect x="2" y="3" width="20" height="14" rx="2"/>
              <path d="M8 21h8M12 17v4"/>
              <path d="M7 8h2M11 8h6M7 11h4M13 11h4"/>
            </svg>
          </span>
          <span class="nav-label">设备档案</span>
        </router-link>

        <router-link
          to="/orders"
          class="nav-item"
          :class="{ active: route.path === '/orders' }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
            </svg>
          </span>
          <span class="nav-label">工单中心</span>
        </router-link>

        <router-link
          to="/repairs"
          class="nav-item"
          :class="{ active: isActive('/repairs') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M14.7 10.3a2.828 2.828 0 11-4-4l3.1-3.1a2 2 0 012.8 0l1.2 1.2a2 2 0 010 2.8l-3.1 3.1zM5 21l3-3m-1-5l5 5"/>
            </svg>
          </span>
          <span class="nav-label">维修工单</span>
        </router-link>

        <router-link
          v-if="hasPermission(['ADMIN', 'MANAGER'])"
          to="/orders/batch"
          class="nav-item"
          :class="{ active: isActive('/orders/batch') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <path d="M16 2v4M8 2v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>
            </svg>
          </span>
          <span class="nav-label">批量排期</span>
        </router-link>

        <router-link
          v-if="hasPermission(['ADMIN'])"
          to="/system/employees"
          class="nav-item"
          :class="{ active: isActive('/system/employees') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.07 4.93l-1.41 1.41M4.93 4.93l1.41 1.41M12 2v2M12 20v2M2 12h2M20 12h2M19.07 19.07l-1.41-1.41M4.93 19.07l1.41-1.41"/>
            </svg>
          </span>
          <span class="nav-label">员工账号中心</span>
        </router-link>

        <router-link
          v-if="hasPermission(['ADMIN'])"
          to="/system/brand-config"
          class="nav-item"
          :class="{ active: isActive('/system/brand-config') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <rect x="3" y="3" width="18" height="18" rx="3"/>
              <path d="M7 17l3-4 3 3 4-5"/>
            </svg>
          </span>
          <span class="nav-label">平台品牌配置</span>
        </router-link>

        <router-link
          v-if="hasPermission(['ADMIN', 'MANAGER'])"
          to="/system/parts"
          class="nav-item"
          :class="{ active: isActive('/system/parts') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/>
              <line x1="7" y1="7" x2="7.01" y2="7"/>
            </svg>
          </span>
          <span class="nav-label">备件库</span>
        </router-link>

        <router-link
          v-if="hasPermission(['ADMIN'])"
          to="/system/audit"
          class="nav-item"
          :class="{ active: isActive('/system/audit') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              <path d="M12 8v4M12 16h.01"/>
            </svg>
          </span>
          <span class="nav-label">安全审计</span>
        </router-link>

        <router-link
          v-if="hasPermission(['ADMIN', 'MANAGER'])"
          to="/system/reports"
          class="nav-item"
          :class="{ active: isActive('/system/reports') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </span>
          <span class="nav-label">集中报告</span>
        </router-link>
      </nav>

      <!-- 底部用户区 -->
      <div class="sidebar-user">
        <div class="user-avatar">{{ userInitial }}</div>
        <div class="user-info">
          <div class="user-name">{{ user?.name || user?.username }}</div>
          <div class="user-role">{{ getRoleName(user?.role) }}</div>
        </div>
        <button class="logout-btn" @click="handleLogout" title="退出登录">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-wrapper">
      <!-- 顶栏 -->
      <header class="topbar">
        <div class="breadcrumb-area">
          <span class="page-overline">Operation Deck</span>
          <span class="page-name">{{ currentPageName }}</span>
        </div>
        <div class="topbar-right">
          <div class="status-chip">{{ getRoleName(user?.role) }}</div>
          <!-- 通知铃铛 -->
          <el-popover
            placement="bottom-end"
            width="320"
            trigger="click"
            popper-class="notification-popover"
          >
            <template #reference>
              <div class="notification-bell">
                <el-badge :value="notifications.length" :hidden="notifications.length === 0" :max="99">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                    <path d="M13.73 21a2 2 0 01-3.46 0"/>
                  </svg>
                </el-badge>
              </div>
            </template>
            <div class="notification-list">
              <div class="notif-header">
                <span>消息通知</span>
                <span class="notif-count" v-if="notifications.length">{{ notifications.length }} 条</span>
              </div>
              <div class="notif-body">
                <div v-if="notifications.length === 0" class="notif-empty">暂无新通知</div>
                <div v-for="n in notifications" :key="n.id" class="notif-item" @click="handleNotifClick(n)">
                  <div class="notif-icon" :class="`icon-${n.level}`">!</div>
                  <div class="notif-content">
                    <div class="notif-title">{{ n.title }}</div>
                    <div class="notif-msg">{{ n.message }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-popover>
          <div class="topbar-time">{{ currentTime }}</div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const currentTime = ref('')

const user = computed(() => authStore.user)

const userInitial = computed(() => {
  const name = user.value?.name || user.value?.username || '?'
  return name.charAt(0).toUpperCase()
})

const isActive = (path) => {
  return route.path.startsWith(path)
}

const pageNameMap = {
  '/dashboard': '控制看板',
  '/customers': '客户管理',
  '/equipments': '设备档案',
  '/orders': '工单中心',
  '/system/employees': '员工账号中心',
  '/system/brand-config': '平台品牌配置',
  '/repairs': '故障维修',
  '/system/audit': '安全审计',
  '/system/reports': '集中报告'
}

const currentPageName = computed(() => {
  for (const [key, val] of Object.entries(pageNameMap)) {
    if (route.path.startsWith(key)) return val
  }
  return '首页'
})

const hasPermission = (roles) => roles.includes(user.value?.role)

const getRoleName = (role) => {
  const map = { ADMIN: '系统管理员', MANAGER: '业务经理', TECH: '技术工程师' }
  return map[role] || role
}

const handleLogout = () => {
  authStore.logout()
  ElMessage.success('退出成功')
  router.push('/login')
}

let timer
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
}

const notifications = ref([])
const fetchNotifications = async () => {
  try {
    const res = await request.get('/stats/notifications')
    notifications.value = res || []
  } catch (err) { }
}

const handleNotifClick = (n) => {
  if (n.link) router.push(n.link)
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  fetchNotifications()
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  overflow: hidden;
  background: transparent;
}

.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  min-height: 100vh;
  background: linear-gradient(180deg, var(--sidebar-bg-from) 0%, var(--sidebar-bg-to) 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 100;
  box-shadow: 24px 0 42px rgba(5, 17, 31, 0.18);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

.sidebar::before,
.sidebar::after {
  content: "";
  position: absolute;
  pointer-events: none;
}

.sidebar::before {
  inset: 0;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.05), transparent 30%),
    radial-gradient(circle at top right, rgba(71, 179, 255, 0.18), transparent 26%);
}

.sidebar::after {
  inset: 20px 18px auto;
  height: 120px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px 20px 18px;
  border-bottom: 1px solid rgba(255,255,255,.08);
  position: relative;
  z-index: 1;
}

.logo-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.logo-icon img {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  display: block;
}
.logo-text {
  min-width: 0;
}
.logo-name {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  line-height: 1.35;
  letter-spacing: 0.04em;
}
.logo-sub {
  font-size: 11px;
  color: rgba(255,255,255,.54);
  margin-top: 4px;
}
.logo-status {
  margin-top: 8px;
  font-size: 11px;
  color: rgba(255, 196, 124, 0.9);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sidebar-nav {
  flex: 1;
  padding: 18px 14px;
  overflow-y: auto;
  scrollbar-width: none;
  position: relative;
  z-index: 1;
}
.sidebar-nav::-webkit-scrollbar { display: none; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 14px;
  border-radius: 18px;
  color: rgba(255,255,255,.62);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  transition: var(--transition-fast);
  cursor: pointer;
  border: 1px solid transparent;
}
.nav-item:hover {
  color: rgba(255,255,255,.9);
  background: rgba(255,255,255,.08);
  border-color: rgba(255,255,255,.08);
  transform: translateX(2px);
}
.nav-item.active {
  background: linear-gradient(135deg, rgba(12, 117, 216, 0.9) 0%, rgba(9, 77, 141, 0.96) 100%);
  color: #fff;
  box-shadow: 0 16px 28px rgba(12, 117, 216, 0.24);
  border-color: rgba(255,255,255,.08);
}
.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-icon svg { width: 18px; height: 18px; }
.nav-label {
  line-height: 1;
  white-space: nowrap;
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px 20px;
  border-top: 1px solid rgba(255,255,255,.08);
  background: rgba(0,0,0,.2);
  position: relative;
  z-index: 1;
}
.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-strong));
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,.9);
  line-height: 1.2;
}
.user-role {
  font-size: 11px;
  color: rgba(255,255,255,.5);
  margin-top: 4px;
}
.user-info { flex: 1; min-width: 0; }
.logout-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255,255,255,.08);
  border-radius: 12px;
  color: rgba(255,255,255,.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: var(--transition-fast);
  padding: 0;
}
.logout-btn:hover {
  background: rgba(255,77,79,.2);
  color: #ff4d4f;
}
.logout-btn svg { width: 14px; height: 14px; }

.main-wrapper {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  overflow: hidden;
  position: relative;
}

.main-wrapper::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 100% 0, rgba(255, 179, 71, 0.12), transparent 24%),
    radial-gradient(circle at 0 18%, rgba(12, 117, 216, 0.1), transparent 26%);
}

.topbar {
  height: 78px;
  margin: 18px 18px 0;
  padding: 0 24px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(247, 250, 252, 0.78));
  border: 1px solid rgba(16, 33, 48, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  box-shadow: 0 16px 32px rgba(10, 24, 39, 0.06);
  backdrop-filter: blur(16px);
}

.breadcrumb-area {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-overline {
  font-size: 11px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--color-text-placeholder);
  font-weight: 700;
}
.page-name {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: 0.04em;
}
.topbar-time {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.08em;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 22px 18px 20px;
  scrollbar-width: thin;
  scrollbar-color: #d0d0d0 transparent;
}
.main-content::-webkit-scrollbar { width: 6px; }
.main-content::-webkit-scrollbar-track { background: transparent; }
.main-content::-webkit-scrollbar-thumb { background: #d0d0d0; border-radius: 3px; }

.topbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(12, 117, 216, 0.09);
  color: var(--color-primary-dark);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.status-chip::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 0 6px rgba(255, 179, 71, 0.18);
}
.notification-bell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 16px;
  cursor: pointer;
  color: var(--color-text-regular);
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(16, 33, 48, 0.08);
}
.notification-bell:hover {
  background: rgba(12, 117, 216, 0.08);
  color: var(--color-primary);
}
.notification-bell svg { width: 20px; height: 20px; }

:deep(.notification-popover) {
  padding: 0 !important;
  border-radius: 22px !important;
  border: 1px solid rgba(16, 33, 48, 0.08) !important;
  box-shadow: var(--shadow-lg) !important;
}
.notification-list {
  display: flex;
  flex-direction: column;
}
.notif-header {
  padding: 16px 18px;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
}
.notif-count {
  font-size: 12px;
  color: var(--color-primary);
  background: rgba(12, 117, 216, 0.08);
  padding: 4px 8px;
  border-radius: 999px;
}
.notif-body {
  max-height: 300px;
  overflow-y: auto;
}
.notif-empty {
  padding: 30px;
  text-align: center;
  color: var(--color-text-placeholder);
  font-size: 13px;
}
.notif-item {
  display: flex;
  gap: 12px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background 0.2s;
}
.notif-item:hover {
  background: rgba(12, 117, 216, 0.04);
}
.notif-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  color: #fff;
  flex-shrink: 0;
}
.icon-danger { background: var(--color-danger); }
.icon-warning { background: var(--color-warning); }
.icon-info { background: var(--color-info); }
.notif-content { flex: 1; }
.notif-title { font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 4px; }
.notif-msg { font-size: 12px; color: var(--color-text-secondary); line-height: 1.4; }
</style>
