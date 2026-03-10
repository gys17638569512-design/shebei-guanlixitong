<template>
  <view class="container">
    <view class="header">
      <text class="title">设备巡检记录</text>
      <text class="subtitle">工单 ID: #{{ orderId }}</text>
    </view>
    
    <scroll-view scroll-y class="item-list">
      <view v-for="(item, index) in inspectionItems" :key="index" class="inspection-item">
        <view class="item-header">
          <text class="item-name">{{ index + 1 }}. {{ item.name }}</text>
          <switch 
            :checked="item.status === 'NORMAL'" 
            @change="(e) => onStatusChange(index, e)" 
            color="#007aff" 
          />
          <text :class="['status-label', item.status === 'NORMAL' ? 'text-success' : 'text-danger']">
            {{ item.status === 'NORMAL' ? '正常' : '异常' }}
          </text>
        </view>
        
        <!-- 异常处理区域 -->
        <view v-if="item.status === 'ABNORMAL'" class="abnormal-detail animated fadeIn">
          <textarea 
            class="remark-input" 
            v-model="item.remark" 
            placeholder="请输入故障描述 (必填)" 
          />
          <view class="photo-area">
            <watermark-camera @photoTaken="(res) => onPhotoTaken(index, res)" />
            <image v-if="item.photo" :src="item.photo" class="preview-img" mode="aspectFit" />
          </view>
        </view>
      </view>
    </scroll-view>
    
    <view class="footer">
      <button type="primary" class="submit-btn" @click="handleSubmit">提交检查结果</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import WatermarkCamera from '../../components/watermark-camera/watermark-camera.vue';

const orderId = ref('');
const templateId = ref('');
const inspectionItems = ref([]);

onLoad((options) => {
  orderId.value = options.id || '';
  templateId.value = options.templateId || '1';
  loadTemplate();
});

const loadTemplate = async () => {
  // 1. 尝试从本地缓存读取
  const cacheKey = `template_cache_${templateId.value}`;
  const cached = uni.getStorageSync(cacheKey);
  
  // 这里简化处理：如果没有缓存或者为了演示，手动构造一些常用检查项
  // 真实场景应该调用 API 拉取 FIX-07 定义的模板
  const defaultItems = [
    { name: '主梁结构', required: true, order: 1 },
    { name: '电气控制柜', required: true, order: 2 },
    { name: '钢丝绳磨损', required: true, order: 3 },
    { name: '限位装置', required: true, order: 4 },
    { name: '运行制动器', required: true, order: 5 }
  ];
  
  const rawItems = cached ? JSON.parse(cached) : defaultItems;
  
  inspectionItems.value = rawItems.map(it => ({
    ...it,
    status: 'NORMAL',
    remark: '',
    photo: ''
  }));
};

const onStatusChange = (index, e) => {
  inspectionItems.value[index].status = e.detail.value ? 'NORMAL' : 'ABNORMAL';
};

const onPhotoTaken = (index, res) => {
  inspectionItems.value[index].photo = res.filePath;
};

const handleSubmit = () => {
  // 校验异常项是否填写了备注
  const invalid = inspectionItems.value.find(it => it.status === 'ABNORMAL' && !it.remark);
  if (invalid) {
    uni.showToast({ title: '异常项必须填写备注', icon: 'none' });
    return;
  }
  
  // 保存草稿
  uni.setStorageSync(`draft_inspection_${orderId.value}`, JSON.stringify(inspectionItems.value));
  
  // 跳转到签名页
  uni.navigateTo({
    url: `/pages/signature/signature?id=${orderId.value}`
  });
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
}

.header {
  padding: 30rpx;
  background: #fff;
  border-bottom: 2rpx solid #eee;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  display: block;
}

.subtitle {
  font-size: 24rpx;
  color: #999;
}

.item-list {
  flex: 1;
  padding: 20rpx;
}

.inspection-item {
  background: #fff;
  padding: 30rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
}

.item-header {
  display: flex;
  align-items: center;
}

.item-name {
  flex: 1;
  font-size: 30rpx;
  font-weight: 500;
}

.status-label {
  width: 80rpx;
  text-align: right;
  font-size: 24rpx;
}

.abnormal-detail {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 2rpx dashed #eee;
}

.remark-input {
  width: 100%;
  height: 150rpx;
  background: #fcfcfc;
  border: 2rpx solid #eee;
  padding: 15rpx;
  font-size: 28rpx;
  border-radius: 8rpx;
}

.photo-area {
  margin-top: 20rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.preview-img {
  width: 200rpx;
  height: 120rpx;
  background: #eee;
  border-radius: 8rpx;
}

.footer {
  padding: 30rpx;
  background: #fff;
  border-top: 2rpx solid #eee;
}

.submit-btn {
  width: 100%;
  border-radius: 44rpx;
}

.text-success { color: #52c41a; }
.text-danger { color: #ff4d4f; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animated {
  animation-duration: 0.3s;
  animation-fill-mode: both;
}
.fadeIn { animation-name: fadeIn; }
</style>
