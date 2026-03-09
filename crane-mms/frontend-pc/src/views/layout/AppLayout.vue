<template>
  <div class="app-layout">
    <el-container>
      <el-aside width="200px" class="aside">
        <div class="logo">智能起重机维保管理系统</div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical-demo"
          background-color="#001529"
          text-color="rgba(255, 255, 255, 0.7)"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/customers" v-if="hasPermission(['ADMIN', 'MANAGER'])">
            <el-icon><UserFilled /></el-icon>
            <span>客户管理</span>
          </el-menu-item>
          <el-menu-item index="/equipments/form" v-if="hasPermission(['ADMIN', 'MANAGER'])">
            <el-icon><Operation /></el-icon>
            <span>设备档案</span>
          </el-menu-item>
          <el-menu-item index="/orders">
            <el-icon><Document /></el-icon>
            <span>工单中心</span>
          </el-menu-item>
          <el-menu-item index="/system/users" v-if="hasPermission(['ADMIN'])">
            <el-icon><Monitor /></el-icon>
            <span>人员管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-right">
            <span class="user-info">
              {{ user?.name }} ({{ user?.role }})
            </span>
            <el-button type="text" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出
            </el-button>
          </div>
        </el-header>
        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { UserFilled, Operation, Document, SwitchButton, Monitor } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const activeMenu = computed(() => {
  const path = router.currentRoute.value.path
  return path
})

const hasPermission = (roles) => {
  return roles.includes(user.value?.role)
}

const handleLogout = () => {
  authStore.logout()
  ElMessage.success('退出成功')
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
  overflow: hidden;
}

.aside {
  background-color: #001529;
  color: white;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 16px;
  font-weight: bold;
  color: white;
}

.el-menu-vertical-demo {
  border-right: none;
  height: calc(100vh - 60px);
}

.el-menu-item {
  color: rgba(255, 255, 255, 0.7);
}

.el-menu-item:hover,
.el-menu-item.is-active {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
}

.header {
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  font-size: 14px;
  color: #333;
}

.main {
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
}
</style>