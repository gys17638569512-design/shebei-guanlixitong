<template>
  <div class="h5-container">
    <router-view />
  </div>
</template>

<script setup>
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
}
</style>
