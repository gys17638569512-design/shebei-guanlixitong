<template>
  <div class="order-list pb-safe">
    <!-- 玻璃态沉浸式导航栏 -->
    <van-nav-bar 
      title="我的维保工单" 
      fixed 
      placeholder 
      :border="false"
      class="glass-nav"
    />
    
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh" class="pull-wrap">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
        class="order-cards"
      >
        <!-- 悬浮微交互卡片 -->
        <div 
          v-for="item in list" 
          :key="item.id" 
          class="order-card interactive-card"
          @click="goDetail(item.id)"
        >
          <!-- 状态光效角标 -->
          <div 
            class="status-badge"
            :class="getStatusColorConfig(item.status).bgClass"
          >
            {{ getStatusLabel(item.status) }}
          </div>

          <div class="card-content">
            <div class="order-serial"># ORD-{{ String(item.id).padStart(6, '0') }}</div>
            <h3 class="equipment-name">{{ item.equipment_name }}</h3>
            
            <div class="info-grid">
              <div class="info-cell bg-slate text-left">
                <span class="cell-label">计划日期</span>
                <span class="cell-value">{{ item.plan_date }}</span>
              </div>
              <div class="info-cell bg-slate text-right">
                <span class="cell-label">维保类型</span>
                <span class="cell-value text-primary">{{ item.order_type }}</span>
              </div>
            </div>
          </div>

          <!-- 签字区动作条 -->
          <div class="card-actions" v-if="item.status === 'PENDING_SIGN' || item.status === 'IN_PROGRESS'">
            <van-button 
              size="small" 
              round 
              class="sign-btn shadow-btn"
              @click.stop="goSign(item.id)"
            >
              <template #icon><van-icon name="edit" /></template>
              立即签字确认
            </van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 空状态 -->
    <van-empty 
      v-if="finished && list.length === 0" 
      description="暂无历史工单记录" 
      image="search"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'

const router = useRouter()
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)

const onLoad = async () => {
  try {
    const res = await request.get('/orders')
    list.value = res || []
    finished.value = true
  } catch (err) {
    finished.value = true
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const onRefresh = () => {
  finished.value = false
  loading.value = true
  onLoad()
}

const goDetail = (id) => router.push(`/orders/${id}`)
const goSign = (id) => router.push(`/sign/${id}`)

const getStatusColorConfig = (s) => {
  const map = { 
    PENDING: { bgClass: 'badge-warning' }, 
    IN_PROGRESS: { bgClass: 'badge-primary' }, 
    PENDING_SIGN: { bgClass: 'badge-danger' }, 
    COMPLETED: { bgClass: 'badge-success' } 
  }
  return map[s] || { bgClass: 'badge-default' }
}

const getStatusLabel = (s) => {
  const map = { PENDING: '待处理', IN_PROGRESS: '进行中', PENDING_SIGN: '待签字', COMPLETED: '已归档' }
  return map[s] || s
}
</script>

<style scoped>
.pb-safe { padding-bottom: calc(env(safe-area-inset-bottom) + 20px); }
.order-list { min-height: 100vh; background-color: #f6f7f9; }

/* 玻璃态导航栏 */
.order-list :deep(.van-nav-bar) {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
}
.order-list :deep(.van-nav-bar__title) {
  font-weight: 700;
  letter-spacing: 0.5px;
}

.pull-wrap { margin-top: 8px; }
.order-cards { padding: 12px 16px; }

/* 现代卡片设计 */
.order-card {
  position: relative;
  background: #ffffff;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.02);
  overflow: hidden;
  transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.interactive-card:active {
  transform: scale(0.97);
}

/* 状态角标 */
.status-badge {
  position: absolute;
  top: 0;
  right: 0;
  padding: 6px 16px;
  border-bottom-left-radius: 16px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1px;
  color: #fff;
  z-index: 10;
}
.badge-warning { background: linear-gradient(135deg, #f59e0b, #fbbf24); box-shadow: -2px 2px 10px rgba(245, 158, 11, 0.3); }
.badge-primary { background: linear-gradient(135deg, #2563eb, #3b82f6); box-shadow: -2px 2px 10px rgba(37, 99, 235, 0.3); }
.badge-danger { background: linear-gradient(135deg, #dc2626, #ef4444); box-shadow: -2px 2px 10px rgba(220, 38, 38, 0.3); }
.badge-success { background: linear-gradient(135deg, #059669, #10b981); box-shadow: -2px 2px 10px rgba(5, 150, 105, 0.3); }
.badge-default { background: #94a3b8; }

/* 卡片内容排版 */
.card-content { margin-top: 4px; }
.order-serial {
  font-size: 12px;
  color: #94a3b8;
  font-family: 'JetBrains Mono', 'Courier New', Courier, monospace;
  margin-bottom: 8px;
}
.equipment-name {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1.3;
  letter-spacing: -0.5px;
}

/* 信息网格 */
.info-grid {
  display: flex;
  gap: 12px;
}
.info-cell {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}
.bg-slate { background-color: #f8fafc; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.cell-label {
  font-size: 10px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}
.cell-value {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}
.text-primary { color: #2563eb; }

/* 底部操作区 */
.card-actions {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;
  display: flex;
  justify-content: flex-end;
}
.sign-btn {
  background: linear-gradient(135deg, #1677ff, #0958d9) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600;
  padding: 0 24px !important;
}
.shadow-btn {
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.3) !important;
}
</style>
