<template>
  <view class="watermark-camera-wrapper">
    <button type="primary" size="mini" @click="takePhoto" :loading="loading">
      <text class="uni-icons-camera"></text> 现场拍照 (带存证)
    </button>
    
    <!-- 用于生成水印的隐藏 Canvas -->
    <canvas 
      v-if="canvasId"
      :canvas-id="canvasId" 
      :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px', position: 'fixed', left: '-9999px', top: '-9999px' }"
    ></canvas>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { addWatermark } from '../../utils/watermark';

const emit = defineEmits(['photoTaken']);
const loading = ref(false);
const canvasId = ref('');
const canvasWidth = ref(0);
const canvasHeight = ref(0);

const takePhoto = () => {
  uni.chooseMedia({
    count: 1,
    mediaType: ['image'],
    sourceType: ['camera'],
    success: async (res) => {
      loading.value = true;
      const tempFilePath = res.tempFiles[0].tempFilePath;
      
      try {
        // 1. 获取图片信息以设置 Canvas 尺寸
        const imgInfo = await new Promise((resolve, reject) => {
          uni.getImageInfo({ src: tempFilePath, success: resolve, fail: reject });
        });
        
        canvasWidth.value = imgInfo.width;
        canvasHeight.value = imgInfo.height;
        canvasId.value = 'camera-canvas-' + Date.now();
        
        // 2. 获取当前位置
        let address = '位置获取失败';
        try {
          const loc = await new Promise((resolve, reject) => {
            uni.getLocation({ type: 'wgs84', success: resolve, fail: reject });
          });
          // 简化版：直接显示经纬度，避免依赖外部逆地理编码接口
          address = `经度:${loc.longitude.toFixed(4)} 纬度:${loc.latitude.toFixed(4)}`;
        } catch (e) {
          console.warn('GPS 获取失败', e);
        }
        
        // 3. 添加水印
        const watermarkedPath = await addWatermark(tempFilePath, address);
        
        // 4. 返回结果
        emit('photoTaken', {
          filePath: watermarkedPath,
          address: address,
          timestamp: Date.now()
        });
        
        uni.showToast({ title: '照片已加水印', icon: 'success' });
      } catch (err) {
        console.error('拍照处理失败', err);
        uni.showToast({ title: '处理失败', icon: 'error' });
      } finally {
        loading.value = false;
        canvasId.value = '';
      }
    }
  });
};
</script>

<style scoped>
.watermark-camera-wrapper {
  display: inline-block;
}
</style>
