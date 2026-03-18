<template>
  <div class="h5-container">
    <div class="app-backdrop"></div>
    <router-view />
    <!-- 底部 TabBar 导航 -->
    <van-tabbar v-if="showTabBar" v-model="active" route active-color="#1677ff" placeholder fixed border class="control-tabbar">
      <van-tabbar-item replace to="/" icon="wap-home-outline">首页</van-tabbar-item>
      <van-tabbar-item replace to="/equipments" icon="apps-o">设备一览</van-tabbar-item>
      <van-tabbar-item replace to="/records" icon="orders-o">维保记录</van-tabbar-item>
      <van-tabbar-item replace to="/account-center" icon="manager-o">账号中心</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

// 仅在需要身份验证且不是特定全屏页（如登录、签字）时显示 TabBar
const showTabBar = computed(() => {
  const hiddenPages = ['Login', 'OrderSign']
  return route.meta.requiresAuth && !hiddenPages.includes(route.name)
})
</script>

<style>
.h5-container {
  min-height: 100vh;
  position: relative;
}

.h5-container > * {
  position: relative;
  z-index: 1;
}

.app-backdrop {
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at top left, rgba(12, 117, 216, 0.08), transparent 28%),
    radial-gradient(circle at 88% 8%, rgba(255, 179, 71, 0.12), transparent 22%);
  z-index: 0;
}

.control-tabbar :deep(.van-tabbar) {
  left: 14px;
  right: 14px;
  bottom: 12px;
  width: auto;
  height: 74px;
  border: none;
  border-radius: 28px;
  overflow: hidden;
  background: rgba(8, 21, 33, 0.86);
  backdrop-filter: blur(22px);
  box-shadow: 0 24px 46px rgba(8, 21, 33, 0.18);
}

.control-tabbar :deep(.van-tabbar::before) {
  content: "";
  position: absolute;
  inset: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  pointer-events: none;
}

.control-tabbar :deep(.van-tabbar-item) {
  color: rgba(236, 242, 247, 0.62);
}

.control-tabbar :deep(.van-tabbar-item--active) {
  color: #ffffff;
}

.control-tabbar :deep(.van-tabbar-item__text) {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
}

@media (min-width: 960px) {
  .control-tabbar :deep(.van-tabbar) {
    left: 50%;
    right: auto;
    width: 640px;
    transform: translateX(-50%);
  }
}
</style>
