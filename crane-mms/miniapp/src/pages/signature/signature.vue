<template>
  <view class="container">
    <view class="header">
      <text class="title">客户签字确认</text>
      <text class="tag">法律效力凭证</text>
    </view>
    
    <view class="canvas-wrapper">
      <canvas 
        canvas-id="signature-canvas" 
        class="signature-canvas"
        @touchstart="onTouchStart"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
        disable-scroll
      ></canvas>
    </view>
    
    <view class="tips">请在上方灰色区域内完成电子签名</view>
    
    <view class="footer">
      <button class="btn btn-clear" @click="clearCanvas">重新签字</button>
      <button class="btn btn-submit" type="primary" @click="handleConfirm">确认提交</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { pushToQueue } from '../../utils/offline-queue';

const orderId = ref('');
const ctx = ref(null);
const hasSigned = ref(false);

onLoad((options) => {
  orderId.value = options.id || '';
});

onMounted(() => {
  ctx.value = uni.createCanvasContext('signature-canvas');
  ctx.value.setStrokeStyle('#000000');
  ctx.value.setLineWidth(4);
  ctx.value.setLineCap('round');
  ctx.value.setLineJoin('round');
});

const onTouchStart = (e) => {
  const { x, y } = e.touches[0];
  ctx.value.moveTo(x, y);
  hasSigned.value = true;
};

const onTouchMove = (e) => {
  const { x, y } = e.touches[0];
  ctx.value.lineTo(x, y);
  ctx.value.stroke();
  ctx.value.draw(true);
};

const onTouchEnd = () => {
  // 结束当前路径，以便下一次开始新路径
};

const clearCanvas = () => {
  ctx.value.clearRect(0, 0, 1000, 1000);
  ctx.value.draw();
  hasSigned.value = false;
};

const handleConfirm = () => {
  if (!hasSigned.value) {
    uni.showToast({ title: '请先完成签名', icon: 'none' });
    return;
  }
  
  uni.canvasToTempFilePath({
    canvasId: 'signature-canvas',
    fileType: 'png',
    success: (res) => {
      const signPath = res.tempFilePath;
      submitOrder(signPath);
    }
  });
};

const submitOrder = async (signPath) => {
  uni.showLoading({ title: '正在提交...', mask: true });
  
  // 从 Storage 读取检查结果缓存
  const inspectionDraft = uni.getStorageSync(`draft_inspection_${orderId.value}`);
  const payload = {
    signature: signPath, // 实际应用中需先上传拿到 URL，此处模拟
    inspection_data: inspectionDraft ? JSON.parse(inspectionDraft) : []
  };

  try {
    const { request } = await import('../../utils/request');
    // 假设后端接口为 PUT /orders/{id}/complete
    await request.put(`/orders/${orderId.value}/complete`, payload);
    
    uni.hideLoading();
    uni.showToast({ title: '提交成功', icon: 'success' });
    
    // 清除草稿
    uni.removeStorageSync(`draft_inspection_${orderId.value}`);
    
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/index/index' });
    }, 1500);
    
  } catch (err) {
    uni.hideLoading();
    // 网络错误或其它失败，存入离线队列
    if (err.errMsg && err.errMsg.includes('request:fail')) {
      pushToQueue('complete_order', { orderId: orderId.value, payload });
      uni.showModal({
        title: '离线保存成功',
        content: '当前网络不佳，数据已存入待处理队列。网络恢复后将自动为您同步至云端。',
        showCancel: false,
        success: () => uni.reLaunch({ url: '/pages/index/index' })
      });
    } else {
      uni.showToast({ title: '提交失败，请重试', icon: 'none' });
    }
  }
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 30rpx;
}

.header {
  margin-bottom: 30rpx;
  padding: 28rpx;
  border-radius: 28rpx;
  background: linear-gradient(145deg, rgba(8, 21, 33, 0.96) 0%, rgba(12, 38, 61, 0.94) 56%, rgba(19, 74, 113, 0.9) 100%);
  color: #fff;
  box-shadow: 0 24rpx 40rpx rgba(8, 24, 40, 0.14);
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  display: block;
}

.tag {
  display: inline-block;
  font-size: 22rpx;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 196, 124, 0.96);
  padding: 6rpx 14rpx;
  border-radius: 999rpx;
  margin-top: 10rpx;
}

.canvas-wrapper {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 249, 252, 0.92));
  border: 2rpx solid rgba(16, 33, 48, 0.06);
  border-radius: 28rpx;
  flex: 1;
  overflow: hidden;
  box-shadow: 0 24rpx 38rpx rgba(8, 24, 40, 0.08);
}

.signature-canvas {
  width: 100%;
  height: 100%;
}

.tips {
  text-align: center;
  font-size: 24rpx;
  color: #7f93a5;
  margin-top: 20rpx;
}

.footer {
  margin-top: 30rpx;
  display: flex;
  gap: 20rpx;
}

.btn {
  flex: 1;
  height: 100rpx;
  line-height:100rpx;
  border-radius: 999rpx;
  font-size: 32rpx;
}

.btn-clear {
  background: rgba(255, 255, 255, 0.92);
  color: #42586a;
  border: 2rpx solid rgba(16, 33, 48, 0.08);
}

.btn-submit {
  background: linear-gradient(135deg, #136fda, #094d8d) !important;
  box-shadow: 0 20rpx 36rpx rgba(19, 111, 218, 0.22);
}
</style>
