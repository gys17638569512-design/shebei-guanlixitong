<template>
  <div class="command-shell">
    <aside class="command-sidebar">
      <div class="brand-block">
        <div class="brand-mark">
          <img src="/brand-mark.svg" alt="品牌标识" />
        </div>
        <div class="brand-copy">
          <div class="brand-title">数字化起重机维保系统</div>
          <div class="brand-subtitle">Operations Command Center</div>
          <div class="brand-meta">设备、排程、权限与模板一体调度</div>
        </div>
      </div>

      <div class="nav-block">
        <div class="nav-caption">业务中枢</div>
        <router-link
          v-for="item in businessNav"
          :key="item.path"
          :to="item.path"
          class="nav-entry"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-entry__icon">
            <el-icon><component :is="item.icon" /></el-icon>
          </span>
          <span class="nav-entry__body">
            <strong>{{ item.label }}</strong>
            <small>{{ item.hint }}</small>
          </span>
        </router-link>
      </div>

      <div v-if="showSettingsPanel" class="settings-block">
        <div class="settings-head" :class="{ active: isSettingsRoute }">
          <span class="settings-head__icon">
            <el-icon><Setting /></el-icon>
          </span>
          <div>
            <div class="settings-head__title">设置工作台</div>
            <div class="settings-head__subtitle">模板、权限、品牌、审计、报告</div>
          </div>
        </div>

        <router-link
          v-for="item in settingsNav"
          :key="item.path"
          :to="item.path"
          class="settings-entry"
          :class="{ active: isActive(item.path) }"
        >
          <span class="settings-entry__icon">
            <el-icon><component :is="item.icon" /></el-icon>
          </span>
          <span class="settings-entry__body">
            <strong>{{ item.label }}</strong>
            <small>{{ item.hint }}</small>
          </span>
          <span class="settings-entry__chevron">›</span>
        </router-link>
      </div>

      <div class="sidebar-profile">
        <div class="profile-avatar">{{ userInitial }}</div>
        <div class="profile-copy">
          <strong>{{ user?.name || user?.username }}</strong>
          <span>{{ getRoleName(user?.role) }}</span>
        </div>
        <button class="profile-action" @click="handleLogout" title="退出登录">
          <el-icon><SwitchButton /></el-icon>
        </button>
      </div>
    </aside>

    <div class="command-main">
      <header class="command-topbar">
        <div class="topbar-copy">
          <span class="topbar-kicker">{{ topbarKicker }}</span>
          <h1 class="topbar-title">{{ currentPageName }}</h1>
          <p class="topbar-subtitle">{{ topbarSubtitle }}</p>
        </div>

        <div class="topbar-center">
          <div class="status-panel">
            <span class="status-panel__label">当前作业层</span>
            <strong>{{ isSettingsRoute ? '设置管控域' : '业务执行域' }}</strong>
            <small>{{ fullDate }}</small>
          </div>
        </div>

        <div class="topbar-actions">
          <div class="role-chip">
            <span class="status-dot success"></span>
            {{ getRoleName(user?.role) }}
          </div>

          <el-popover
            placement="bottom-end"
            width="340"
            trigger="click"
            popper-class="notification-popover"
          >
            <template #reference>
              <button class="notif-trigger" type="button">
                <el-badge :value="notifications.length" :hidden="notifications.length === 0" :max="99">
                  <el-icon><Bell /></el-icon>
                </el-badge>
              </button>
            </template>
            <div class="notif-panel">
              <div class="notif-panel__head">
                <strong>消息通知</strong>
                <span v-if="notifications.length">{{ notifications.length }} 条</span>
              </div>
              <div v-if="notifications.length === 0" class="notif-empty">暂无新通知</div>
              <div
                v-for="item in notifications"
                :key="item.id"
                class="notif-row"
                @click="handleNotifClick(item)"
              >
                <span class="notif-row__badge" :class="item.level || 'info'"></span>
                <div class="notif-row__body">
                  <strong>{{ item.title }}</strong>
                  <span>{{ item.message }}</span>
                </div>
              </div>
            </div>
          </el-popover>

          <div class="time-chip">{{ currentTime }}</div>
        </div>
      </header>

      <main class="command-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Bell,
  Calendar,
  CollectionTag,
  DataAnalysis,
  Document,
  Files,
  Histogram,
  Monitor,
  OfficeBuilding,
  Postcard,
  Setting,
  SwitchButton,
  Tools,
  UserFilled,
  Warning
} from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'
import { SETTINGS_PERMISSIONS } from '@/constants/permissions'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const currentTime = ref('')
const notifications = ref([])
const permissions = SETTINGS_PERMISSIONS

const user = computed(() => authStore.user)
const userInitial = computed(() => {
  const label = user.value?.name || user.value?.username || '?'
  return label.charAt(0).toUpperCase()
})

const hasRole = (roles) => roles.includes(user.value?.role)
const canAccessSetting = (permissionKey) => authStore.hasPermission(permissionKey)
const isActive = (path) => path === '/dashboard' ? route.path === path : route.path.startsWith(path)

const businessNav = computed(() => ([
  { path: '/dashboard', label: '控制看板', hint: '运行概览与风险脉冲', icon: DataAnalysis, roles: ['ADMIN', 'MANAGER'] },
  { path: '/customers', label: '客户管理', hint: '客户档案与联系人', icon: OfficeBuilding, roles: ['ADMIN', 'MANAGER'] },
  { path: '/equipments', label: '设备档案', hint: '设备台账与参数快照', icon: Monitor, roles: ['ADMIN', 'MANAGER'] },
  { path: '/orders', label: '工单中心', hint: '派工、进度、签字闭环', icon: Document, roles: ['ADMIN', 'MANAGER', 'TECH'] },
  { path: '/repairs', label: '维修工单', hint: '故障维修与处理记录', icon: Tools, roles: ['ADMIN', 'MANAGER', 'TECH'] },
  { path: '/orders/batch', label: '批量排期', hint: '成组调度与计划编排', icon: Calendar, roles: ['ADMIN', 'MANAGER'] },
  { path: '/system/parts', label: '备件库', hint: '库存、部件、规格基线', icon: CollectionTag, roles: ['ADMIN', 'MANAGER'] }
]).filter((item) => hasRole(item.roles)))

const settingsNav = computed(() => ([
  { path: '/equipment-templates', label: '设备模板中心', hint: '模板组、候选、通用模板', icon: Files, permission: permissions.EQUIPMENT_TEMPLATES_ACCESS },
  { path: '/system/employees', label: '权限管理', hint: '账号、角色默认权限、个人覆盖', icon: UserFilled, permission: permissions.PERMISSION_MANAGEMENT_ACCESS },
  { path: '/system/brand-config', label: '平台品牌配置', hint: '品牌资产、门户样式、展示规范', icon: Postcard, permission: permissions.BRAND_CONFIG_ACCESS },
  { path: '/system/audit', label: '安全审计', hint: '审计事件与账号痕迹', icon: Warning, permission: permissions.AUDIT_ACCESS },
  { path: '/system/reports', label: '报告集中', hint: '归档报告与签字材料', icon: Histogram, permission: permissions.REPORTS_ACCESS }
]).filter((item) => canAccessSetting(item.permission)))

const showSettingsPanel = computed(() => settingsNav.value.length > 0)

const isSettingsRoute = computed(() => settingsNav.value.some((item) => isActive(item.path)))

const pageNameMap = {
  '/dashboard': '控制看板',
  '/customers': '客户管理',
  '/equipments': '设备档案',
  '/equipment-templates': '设备模板中心',
  '/orders': '工单中心',
  '/repairs': '维修工单',
  '/orders/batch': '批量排期',
  '/system/parts': '备件库',
  '/system/employees': '权限管理',
  '/system/brand-config': '平台品牌配置',
  '/system/audit': '安全审计',
  '/system/reports': '报告集中'
}

const currentPageName = computed(() => {
  for (const [key, value] of Object.entries(pageNameMap)) {
    if (route.path.startsWith(key)) {
      return value
    }
  }
  return '控制中心'
})

const topbarKicker = computed(() => isSettingsRoute.value ? 'Settings Control Layer' : 'Operations Mesh')
const topbarSubtitle = computed(() => isSettingsRoute.value
  ? '统一维护模板、权限、品牌、审计与报告治理能力。'
  : '围绕客户、设备、工单与维保执行的日常运营工作台。')
const fullDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 星期${['日', '一', '二', '三', '四', '五', '六'][now.getDay()]}`
})

const getRoleName = (role) => {
  const map = { ADMIN: '系统管理员', MANAGER: '业务经理', TECH: '技术工程师' }
  return map[role] || role || '未登录'
}

const handleLogout = () => {
  authStore.logout()
  ElMessage.success('退出成功')
  router.push('/login')
}

const handleNotifClick = (item) => {
  if (item.link) {
    router.push(item.link)
  }
}

const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
}

const fetchNotifications = async () => {
  try {
    const res = await request.get('/stats/notifications')
    notifications.value = res || []
  } catch (error) {
    notifications.value = []
  }
}

let timer = null

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  fetchNotifications()
  authStore.fetchCurrentUser().catch(() => null)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped>
.command-shell {
  display: flex;
  min-height: 100vh;
}

.command-sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  min-height: 100vh;
  padding: 22px 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background:
    linear-gradient(180deg, var(--sidebar-bg-from) 0%, var(--sidebar-bg-mid) 42%, var(--sidebar-bg-to) 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 24px 0 54px rgba(6, 17, 28, 0.18);
  position: relative;
  overflow: hidden;
}

.command-sidebar::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at top right, rgba(100, 180, 255, 0.18), transparent 26%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 24%);
}

.brand-block,
.nav-block,
.settings-block,
.sidebar-profile {
  position: relative;
  z-index: 1;
}

.brand-block {
  display: flex;
  gap: 14px;
  padding: 16px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.03));
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-mark {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.14), rgba(255, 255, 255, 0.04));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.brand-mark img {
  width: 34px;
  height: 34px;
}

.brand-copy {
  min-width: 0;
}

.brand-title {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 800;
  line-height: 1.35;
  color: #fff;
  letter-spacing: 0.04em;
}

.brand-subtitle {
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.58);
  font-size: 12px;
}

.brand-meta {
  margin-top: 10px;
  color: rgba(255, 191, 95, 0.9);
  font-size: 11px;
  letter-spacing: 0.08em;
}

.nav-block,
.settings-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-block {
  flex: 1;
  min-height: 0;
}

.nav-caption {
  padding: 0 10px;
  color: rgba(255, 255, 255, 0.46);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

.nav-entry,
.settings-entry {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 14px;
  border-radius: 20px;
  color: rgba(241, 247, 255, 0.72);
  border: 1px solid transparent;
  transition: var(--transition-fast);
}

.nav-entry:hover,
.settings-entry:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.08);
  transform: translateX(2px);
}

.nav-entry.active {
  color: #fff;
  background: linear-gradient(135deg, rgba(47, 137, 255, 0.86), rgba(19, 88, 184, 0.96));
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 18px 32px rgba(47, 137, 255, 0.26);
}

.settings-head {
  display: flex;
  gap: 12px;
  padding: 14px 14px 12px;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.04));
  color: rgba(241, 247, 255, 0.78);
}

.settings-head.active {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.settings-head__icon,
.nav-entry__icon,
.settings-entry__icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.settings-head__title {
  font-size: 14px;
  font-weight: 800;
}

.settings-head__subtitle {
  margin-top: 5px;
  font-size: 12px;
  color: rgba(241, 247, 255, 0.52);
}

.nav-entry__body,
.settings-entry__body {
  min-width: 0;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 4px;
}

.nav-entry__body strong,
.settings-entry__body strong {
  font-size: 14px;
  line-height: 1.1;
}

.nav-entry__body small,
.settings-entry__body small {
  color: rgba(241, 247, 255, 0.5);
  font-size: 11px;
}

.settings-entry {
  background: rgba(255, 255, 255, 0.03);
}

.settings-entry.active {
  color: #fff;
  background: rgba(47, 137, 255, 0.16);
  border-color: rgba(85, 164, 255, 0.22);
}

.settings-entry__chevron {
  color: rgba(241, 247, 255, 0.42);
  font-size: 18px;
  line-height: 1;
}

.sidebar-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 22px;
  background: rgba(0, 0, 0, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.profile-avatar {
  width: 42px;
  height: 42px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-strong));
  color: #fff;
  font-weight: 800;
}

.profile-copy {
  min-width: 0;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 4px;
}

.profile-copy strong {
  color: #fff;
  font-size: 14px;
}

.profile-copy span {
  color: rgba(241, 247, 255, 0.56);
  font-size: 12px;
}

.profile-action {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: rgba(241, 247, 255, 0.66);
  background: rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: var(--transition-fast);
}

.profile-action:hover {
  color: #fff;
  background: rgba(231, 98, 98, 0.22);
}

.command-main {
  flex: 1;
  min-width: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.command-main::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 100% 0%, rgba(255, 191, 95, 0.1), transparent 22%),
    radial-gradient(circle at 0% 12%, rgba(47, 137, 255, 0.12), transparent 24%);
}

.command-topbar {
  margin: 18px 18px 0;
  padding: 18px 24px;
  min-height: 94px;
  border-radius: 28px;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) auto auto;
  align-items: center;
  gap: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(247, 250, 252, 0.84));
  border: 1px solid rgba(15, 33, 51, 0.08);
  box-shadow: 0 18px 34px rgba(10, 24, 39, 0.06);
  backdrop-filter: blur(18px);
  position: relative;
  z-index: 1;
}

.topbar-kicker {
  display: block;
  color: var(--color-text-placeholder);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

.topbar-title {
  margin: 8px 0 0;
  font-family: var(--font-display);
  font-size: 28px;
  line-height: 1.08;
  letter-spacing: 0.03em;
  color: var(--color-text-primary);
}

.topbar-subtitle {
  margin: 8px 0 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.status-panel {
  min-width: 240px;
  padding: 16px 18px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(239, 246, 253, 0.92), rgba(233, 241, 247, 0.88));
  border: 1px solid rgba(15, 33, 51, 0.08);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.status-panel__label {
  color: var(--color-text-placeholder);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.status-panel strong {
  color: var(--color-text-primary);
  font-size: 16px;
}

.status-panel small {
  color: var(--color-text-secondary);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-chip,
.time-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(47, 137, 255, 0.08);
  color: var(--color-primary-dark);
  font-size: 12px;
  font-weight: 800;
}

.time-chip {
  background: rgba(15, 33, 51, 0.05);
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.08em;
}

.notif-trigger {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.92);
  color: var(--color-text-regular);
  box-shadow: inset 0 0 0 1px rgba(15, 33, 51, 0.08);
  cursor: pointer;
}

.notif-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notif-panel__head {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-secondary);
}

.notif-empty {
  padding: 16px 0;
  text-align: center;
  color: var(--color-text-secondary);
}

.notif-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(243, 247, 251, 0.92);
  cursor: pointer;
}

.notif-row__badge {
  width: 10px;
  height: 10px;
  margin-top: 6px;
  border-radius: 50%;
  background: var(--color-info);
  flex-shrink: 0;
}

.notif-row__badge.warning {
  background: var(--color-warning);
}

.notif-row__badge.danger {
  background: var(--color-danger);
}

.notif-row__body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.notif-row__body strong {
  color: var(--color-text-primary);
}

.notif-row__body span {
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.command-content {
  flex: 1;
  overflow-y: auto;
  padding: 22px 18px 20px;
  position: relative;
  z-index: 1;
}

@media (max-width: 1380px) {
  .command-topbar {
    grid-template-columns: 1fr;
  }

  .topbar-center,
  .topbar-actions {
    justify-self: stretch;
  }
}

@media (max-width: 1100px) {
  .command-shell {
    flex-direction: column;
  }

  .command-sidebar {
    width: 100%;
    min-width: 0;
    min-height: auto;
  }
}
</style>
