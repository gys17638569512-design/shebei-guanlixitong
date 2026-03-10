<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <!-- Logo 区域 -->
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="#1677ff"/>
            <path d="M6 24V12l10-6 10 6v12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M16 6v18M6 16h20" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
            <circle cx="16" cy="16" r="3" fill="white"/>
          </svg>
        </div>
        <div class="logo-text">
          <div class="logo-name">维保管理系统</div>
          <div class="logo-sub">智能起重机 v1.0</div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
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
          to="/customers"
          class="nav-item"
          :class="{ active: isActive('/equipments') }"
          @click.prevent="router.push('/customers')"
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
          :class="{ active: isActive('/orders') }"
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
          v-if="hasPermission(['ADMIN'])"
          to="/system/users"
          class="nav-item"
          :class="{ active: isActive('/system') }"
        >
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.07 4.93l-1.41 1.41M4.93 4.93l1.41 1.41M12 2v2M12 20v2M2 12h2M20 12h2M19.07 19.07l-1.41-1.41M4.93 19.07l1.41-1.41"/>
            </svg>
          </span>
          <span class="nav-label">人员管理</span>
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
          <span class="page-name">{{ currentPageName }}</span>
        </div>
        <div class="topbar-right">
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
  '/customers': '客户管理',
  '/equipments': '设备档案',
  '/orders': '工单中心',
  '/system': '人员管理',
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

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--color-bg-page);
}

/* ─── 侧边栏 ─── */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  height: 100vh;
  background: linear-gradient(180deg, var(--sidebar-bg-from) 0%, var(--sidebar-bg-to) 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 100;
  box-shadow: 2px 0 12px rgba(0,0,0,.15);
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.logo-icon svg {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}
.logo-name {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
  letter-spacing: 0.02em;
}
.logo-sub {
  font-size: 10px;
  color: rgba(255,255,255,.45);
  margin-top: 2px;
}

/* 导航 */
.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  overflow-y: auto;
  scrollbar-width: none;
}
.sidebar-nav::-webkit-scrollbar { display: none; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  color: rgba(255,255,255,.6);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 2px;
  transition: var(--transition-fast);
  cursor: pointer;
}
.nav-item:hover {
  color: rgba(255,255,255,.9);
  background: rgba(255,255,255,.08);
}
.nav-item.active {
  background: linear-gradient(135deg, #1677ff 0%, #0958d9 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(22,119,255,.4);
}
.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}
.nav-icon svg { width: 18px; height: 18px; }
.nav-label { line-height: 1; }

/* 底部用户 */
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-top: 1px solid rgba(255,255,255,.08);
  background: rgba(0,0,0,.2);
}
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: #fff;
  font-size: 13px;
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
  color: rgba(255,255,255,.45);
  margin-top: 2px;
}
.user-info { flex: 1; min-width: 0; }
.logout-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(255,255,255,.08);
  border-radius: var(--radius-sm);
  color: rgba(255,255,255,.5);
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

/* ─── 主内容区 ─── */
.main-wrapper {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.topbar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  box-shadow: var(--shadow-xs);
}
.page-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.topbar-time {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scrollbar-width: thin;
  scrollbar-color: #d0d0d0 transparent;
}
.main-content::-webkit-scrollbar { width: 6px; }
.main-content::-webkit-scrollbar-track { background: transparent; }
.main-content::-webkit-scrollbar-thumb { background: #d0d0d0; border-radius: 3px; }
</style>