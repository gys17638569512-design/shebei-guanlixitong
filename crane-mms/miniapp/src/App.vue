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
  background:
    radial-gradient(circle at top left, rgba(19, 111, 218, 0.16), transparent 26%),
    radial-gradient(circle at 88% 10%, rgba(255, 179, 71, 0.16), transparent 22%),
    linear-gradient(180deg, #dfe8f0 0%, #edf3f8 34%, #f8fbfe 100%);
  color: #102130;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
}

button::after {
  border: none;
}

button {
  border-radius: 999rpx;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
