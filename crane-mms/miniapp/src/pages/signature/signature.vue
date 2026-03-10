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
  background: #f8f9fa;
  padding: 30rpx;
}

.header {
  margin-bottom: 40rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  display: block;
}

.tag {
  display: inline-block;
  font-size: 22rpx;
  background: #e6f7ff;
  color: #1890ff;
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
  margin-top: 10rpx;
}

.canvas-wrapper {
  background: #fff;
  border: 2rpx solid #ddd;
  border-radius: 16rpx;
  flex: 1;
  overflow: hidden;
}

.signature-canvas {
  width: 100%;
  height: 100%;
}

.tips {
  text-align: center;
  font-size: 24rpx;
  color: #999;
  margin-top: 20rpx;
}

.footer {
  margin-top: 40rpx;
  display: flex;
  gap: 20rpx;
}

.btn {
  flex: 1;
  height: 100rpx;
  line-height:100rpx;
  border-radius: 50rpx;
  font-size: 32rpx;
}

.btn-clear {
  background: #fff;
  color: #666;
  border: 2rpx solid #ddd;
}
</style>
