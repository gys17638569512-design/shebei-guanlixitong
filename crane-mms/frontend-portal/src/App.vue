<template>
  <div class="h5-container">
    <router-view />
    <!-- 底部 TabBar 导航 -->
    <van-tabbar v-if="showTabBar" v-model="active" route active-color="#1677ff" placeholder fixed border>
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
/* 移动端基础样式 */
html, body, #app, .h5-container {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #f7f8fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica,
    Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei',
    sans-serif;
  color: #323233;
}
:root {
  --van-primary-color: #1677ff;
}
</style>
