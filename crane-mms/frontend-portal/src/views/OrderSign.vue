<template>
  <div class="order-sign">
    <van-nav-bar 
      title="维保验收确认" 
      left-arrow 
      @click-left="router.back()" 
      fixed 
      placeholder 
    />

    <div class="sign-notice">
      <van-notice-bar 
        left-icon="info-o" 
        text="请在下方空白处清晰书写您的姓名。点击确认后，本工单将自动生成带有您签名的法律效力报告。" 
      />
    </div>

    <div class="canvas-box">
      <canvas 
        ref="canvasRef" 
        @touchstart.prevent="startDraw"
        @touchmove.prevent="moveDraw"
        @touchend.prevent="endDraw"
        class="sign-canvas"
      ></canvas>
      <div class="canvas-placeholder" v-if="!hasDrawn">请在此区域手写签名</div>
    </div>

    <div class="footer-btns">
      <van-button round plain block @click="clearCanvas">重写</van-button>
      <van-button round block type="primary" :loading="submitting" @click="handleSubmit">确认结单并签字</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast } from 'vant'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const canvasRef = ref(null)
const hasDrawn = ref(false)
const submitting = ref(false)
let ctx = null

onMounted(() => {
  const canvas = canvasRef.value
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  ctx = canvas.getContext('2d')
  ctx.lineWidth = 4
  ctx.lineCap = 'round'
  ctx.strokeStyle = '#000'
})

const startDraw = (e) => {
  hasDrawn.value = true
  const rect = canvasRef.value.getBoundingClientRect()
  const touch = e.touches[0]
  ctx.beginPath()
  ctx.moveTo(touch.clientX - rect.left, touch.clientY - rect.top)
}

const moveDraw = (e) => {
  const rect = canvasRef.value.getBoundingClientRect()
  const touch = e.touches[0]
  ctx.lineTo(touch.clientX - rect.left, touch.clientY - rect.top)
  ctx.stroke()
}

const endDraw = () => {
  ctx.closePath()
}

const clearCanvas = () => {
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  hasDrawn.value = false
}

const handleSubmit = async () => {
  if (!hasDrawn.value) return showToast('请输入签名后再提交')
  
  submitting.value = true
  try {
    const signData = canvasRef.value.toDataURL('image/png')
    await request.post(`/orders/${route.params.id}/sign`, { sign_url: signData })
    showToast({ message: '签字确认成功！工单已归档', type: 'success' })
    setTimeout(() => router.push('/'), 1500)
  } catch (err) {} finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.order-sign { height: 100vh; display: flex; flex-direction: column; background: #fff; }
.sign-notice { flex-shrink: 0; }
.canvas-box { 
  flex: 1; 
  margin: 16px; 
  border: 2px dashed #ebedf0; 
  border-radius: 8px; 
  position: relative;
  background: #fafafa;
}
.sign-canvas { width: 100%; height: 100%; touch-action: none; }
.canvas-placeholder {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  color: #c8c9cc;
  pointer-events: none;
  font-size: 18px;
}
.footer-btns { padding: 16px; display: flex; gap: 12px; }
</style>
