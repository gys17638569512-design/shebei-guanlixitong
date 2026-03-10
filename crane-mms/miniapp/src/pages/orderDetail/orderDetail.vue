<template>
  <view class="detail-container">
    <view class="status-banner" :class="order.status.toLowerCase()">
      <text class="status-label">{{ getStatusLabel(order.status) }}</text>
      <text class="status-desc">{{ getStatusDesc(order.status) }}</text>
    </view>

    <view class="cell-group">
      <view class="group-title">基础信息</view>
      <view class="cell">
        <text class="label">工单编号</text>
        <text class="value">#{{ order.id }}</text>
      </view>
      <view class="cell">
        <text class="label">设备名称</text>
        <text class="value">{{ order.equipment_name }}</text>
      </view>
      <view class="cell">
        <text class="label">维保类型</text>
        <text class="value">{{ order.order_type }}</text>
      </view>
      <view class="cell">
        <text class="label">计划日期</text>
        <text class="value">{{ order.plan_date }}</text>
      </view>
    </view>

    <view class="cell-group" v-if="order.status === 'PENDING' || order.status === 'IN_PROGRESS'">
      <view class="group-title">现场实施</view>
      
      <!-- 打卡区域 -->
      <view class="action-card" v-if="order.status === 'PENDING'">
        <text class="card-tip">到达现场后，请先点击签到开始工作</text>
        <button class="btn-main" @click="handleCheckin">现场打卡签到</button>
      </view>

      <!-- 维保反馈区域 -->
      <view class="form-area" v-if="order.status === 'IN_PROGRESS'">
        <view class="form-item">
          <text class="form-label">问题排查与描述</text>
          <textarea v-model="formData.problem_description" class="textarea" placeholder="请记录现场发现的隐患或问题..." />
        </view>
        <view class="form-item">
          <text class="form-label">处理结果与结论</text>
          <textarea v-model="formData.solution" class="textarea" placeholder="请填写最终的处理方案与结论..." />
        </view>
        
        <view class="btn-group">
          <button class="btn-sub" @click="handlePushSign">推送客户签字</button>
          <button class="btn-main" @click="handleComplete">确认直接完工</button>
        </view>
      </view>
    </view>

    <view class="cell-group" v-if="order.status === 'COMPLETED'">
      <view class="group-title">维保总结</view>
      <view class="memo-box">
        <text class="memo-text">{{ order.solution || '暂无总结' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getOrderDetail, checkinOrder, completeOrder, pushForSign } from '../../api/order'

const order = ref<any>({ status: '' })
const formData = ref({
  problem_description: '',
  solution: ''
})

onLoad((options) => {
  if (options && options.id) {
    loadData(Number(options.id))
  }
})

const loadData = async (id: number) => {
  uni.showLoading({ title: '加载中' })
  try {
    const res: any = await getOrderDetail(id)
    order.value = res
    formData.value.problem_description = res.problem_description || ''
    formData.value.solution = res.solution || ''
  } catch (err) {} finally {
    uni.hideLoading()
  }
}

const handleCheckin = async () => {
  uni.showModal({
    title: '签到确认',
    content: '确定已到达客户现场并开始维保吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await checkinOrder(order.value.id, { checkin_time: new Date() })
          uni.showToast({ title: '已签到', icon: 'success' })
          loadData(order.value.id)
        } catch (err) {}
      }
    }
  })
}

const handlePushSign = async () => {
  if (!formData.value.solution) return uni.showToast({ title: '请填写处理结论', icon: 'none' })
  
  try {
    await pushForSign(order.value.id, formData.value)
    uni.showToast({ title: '已推送到客户手机', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 1500)
  } catch (err) {}
}

const handleComplete = async () => {
  if (!formData.value.solution) return uni.showToast({ title: '请填写处理结论', icon: 'none' })
  
  uni.showModal({
    title: '完工确认',
    content: '直接完工将跳过客户在线签字环节，请确认现场已口头验收？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await completeOrder(order.value.id, formData.value)
          uni.showToast({ title: '已完工归档', icon: 'success' })
          setTimeout(() => uni.navigateBack(), 1500)
        } catch (err) {}
      }
    }
  })
}

const getStatusLabel = (s: string) => {
  const map: any = { PENDING: '待签到', IN_PROGRESS: '执行中', PENDING_SIGN: '待客户确认', COMPLETED: '已完工' }
  return map[s] || s
}

const getStatusDesc = (s: string) => {
  const map: any = { 
    PENDING: '请在到达现场后点击下方签到', 
    IN_PROGRESS: '工作正在开展，请记录维保详情', 
    PENDING_SIGN: '内容已推送，等待客户手机签字', 
    COMPLETED: '本次维保任务已圆满结束并归档' 
  }
  return map[s] || ''
}
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background-color: #f5f6f7;
  padding-bottom: 60rpx;
}

.status-banner {
  padding: 60rpx 40rpx;
  color: #fff;
}
.status-banner.pending { background-color: #f9a825; }
.status-banner.in_progress { background-color: #1976d2; }
.status-banner.pending_sign { background-color: #e53935; }
.status-banner.completed { background-color: #43a047; }

.status-label {
  font-size: 44rpx;
  font-weight: bold;
  display: block;
}

.status-desc {
  font-size: 26rpx;
  opacity: 0.9;
  margin-top: 10rpx;
  display: block;
}

.cell-group {
  background-color: #fff;
  margin-top: 20rpx;
  padding: 0 30rpx;
}

.group-title {
  font-size: 24rpx;
  color: #999;
  padding: 30rpx 0 20rpx;
}

.cell {
  display: flex;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
  font-size: 30rpx;
}

.cell:last-child { border-bottom: none; }

.label { color: #666; }
.value { color: #333; font-weight: 500; }

.action-card {
  padding: 40rpx 0;
  text-align: center;
}

.card-tip {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 30rpx;
  display: block;
}

.btn-main {
  background-color: #2979ff;
  color: #fff;
  border-radius: 12rpx;
  font-size: 32rpx;
}

.form-area {
  padding-bottom: 40rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 16rpx;
  display: block;
}

.textarea {
  width: 100%;
  height: 200rpx;
  background-color: #f7f7f7;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.btn-group {
  margin-top: 40rpx;
  display: flex;
  gap: 20rpx;
}

.btn-sub {
  flex: 1;
  background-color: #e3f2fd;
  color: #1976d2;
  font-size: 28rpx;
  border-radius: 12rpx;
}

.btn-main {
  flex: 1.5;
}

.memo-box {
  padding: 30rpx;
  background-color: #fafafa;
  border-radius: 12rpx;
}

.memo-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}
</style>
