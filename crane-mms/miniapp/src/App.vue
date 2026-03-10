<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { useAuthStore } from "./stores/auth";
import { processQueue } from "./utils/offline-queue";

onLaunch(() => {
  console.log("App Launch");
  const authStore = useAuthStore();
  
  // 全局登录状态检查：如果没有 Token 且不在登录页，自动跳转
  if (!authStore.token) {
    uni.reLaunch({
      url: "/pages/login/login"
    });
  }

  // 监听网络状态变化
  uni.onNetworkStatusChange((res) => {
    if (res.isConnected) {
      console.log('[网络] 已恢复连接，开始同步离线队列');
      processQueue();
    }
  });
});

onShow(() => {
  console.log("App Show");
});

onHide(() => {
  console.log("App Hide");
});
</script>

<style>
/* 每个页面公共css */
page {
  background-color: #f5f6f7;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica,
    Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei',
    sans-serif;
}

button::after {
  border: none;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
