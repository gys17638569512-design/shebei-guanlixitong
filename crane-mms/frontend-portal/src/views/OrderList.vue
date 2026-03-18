<template>
  <div class="order-list pb-safe">
    <!-- 沉浸式导航栏 -->
    <van-nav-bar 
      title="服务记录中心" 
      fixed 
      placeholder 
      :border="false"
      class="glass-nav"
    />
    
    <div class="sticky-tabs">
      <van-tabs v-model:active="activeCategory" @change="onCategoryChange" color="#1677ff" background="transparent">
        <van-tab title="维保记录" name="maintenance" />
        <van-tab title="维修记录" name="repair" />
      </van-tabs>
    </div>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh" class="pull-wrap">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
        class="order-cards"
      >
        <!-- 记录卡片 -->
        <div 
          v-for="item in currentList" 
          :key="item.id" 
          class="order-card interactive-card"
          @click="goDetail(item)"
        >
          <!-- 状态标识 -->
          <div 
            class="status-badge"
            :class="getStatusColor(item.status)"
          >
            {{ item.status }}
          </div>

          <div class="card-content">
            <div class="order-serial">
              # {{ activeCategory === 'maintenance' ? 'MT-' : 'RP-' }}{{ String(item.id).padStart(6, '0') }}
            </div>
            <h3 class="equipment-name">{{ item.equipment_name }}</h3>
            
            <!-- 维保展示 -->
            <div v-if="activeCategory === 'maintenance'" class="info-grid">
              <div class="info-cell bg-slate">
                <span class="cell-label">计划日期</span>
                <span class="cell-value">{{ item.plan_date }}</span>
              </div>
              <div class="info-cell bg-slate">
                <span class="cell-label">维保类型</span>
                <span class="cell-value text-primary">{{ item.order_type }}</span>
              </div>
            </div>

            <!-- 维修展示 -->
            <div v-else class="info-grid">
              <div class="info-cell bg-slate">
                <span class="cell-label">维修时间</span>
                <span class="cell-value">{{ item.created_at }}</span>
              </div>
              <div class="info-cell bg-slate">
                <span class="cell-label">费用确认</span>
                <span class="cell-value text-orange">{{ item.total_fee }} 元</span>
              </div>
            </div>

            <!-- 简述位 -->
            <p v-if="item.fault_symptom" class="description">{{ item.fault_symptom }}</p>
          </div>

          <!-- 报告下载动作区 -->
          <div class="card-actions" v-if="item.pdf_report_url || item.has_report">
            <van-button 
              size="small" 
              round 
              plain
              class="report-btn"
              icon="description-o"
              @click.stop="openReport(item.pdf_report_url)"
            >
              查看 PDF 报告单
            </van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 空状态 -->
    <van-empty 
      v-if="finished && currentList.length === 0" 
      description="暂无相关记录" 
      image="search"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'

const router = useRouter()
const activeCategory = ref('maintenance')
const currentList = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)

const onLoad = async () => {
  try {
    const endpoint = activeCategory.value === 'maintenance' ? '/orders' : '/repairs'
    const res = await request.get(endpoint)
    currentList.value = res || []
    
    // 统一后端 status 映射 (维保记录后端返回的是英文枚举名，需转换)
    if (activeCategory.value === 'maintenance') {
      const statusMap = { PENDING: '待处理', IN_PROGRESS: '进行中', PENDING_SIGN: '待签字', COMPLETED: '已完工' }
      currentList.value = currentList.value.map(o => ({
        ...o,
        status: statusMap[o.status] || o.status
      }))
    }
    
    finished.value = true
  } catch (err) {
    finished.value = true
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const onCategoryChange = () => {
  currentList.value = []
  finished.value = false
  loading.value = true
  onLoad()
}

const onRefresh = () => {
  onCategoryChange()
}

const goDetail = (item) => {
  if (activeCategory.value === 'maintenance') {
    router.push(`/orders/${item.id}`)
  }
}

const openReport = (url) => {
  if (url) window.open(url, '_blank')
}

const getStatusColor = (s) => {
  if (['已完工', '已完成'].includes(s)) return 'badge-success'
  if (['待处理', '待签字'].includes(s)) return 'badge-danger'
  return 'badge-primary'
}
</script>

<style scoped>
.pb-safe { padding-bottom: calc(env(safe-area-inset-bottom) + 80px); }
.order-list { min-height: 100vh; }

.glass-nav :deep(.van-nav-bar) {
  background: rgba(255, 255, 255, 0.64) !important;
  backdrop-filter: saturate(180%) blur(20px);
}

.sticky-tabs {
  position: sticky;
  top: 46px;
  z-index: 100;
  background: rgba(238, 243, 248, 0.84);
  backdrop-filter: blur(14px);
  padding: 0 0 10px;
}

.order-cards { padding: 12px 16px; }

.order-card {
  position: relative;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(246, 249, 252, 0.9));
  border-radius: 24px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 18px 34px rgba(8, 24, 40, 0.06);
  border: 1px solid rgba(16, 33, 48, 0.06);
  transition: transform 0.2s;
}

.status-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 0.04em;
  box-shadow: 0 12px 20px rgba(8, 24, 40, 0.08);
}
.badge-warning { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.badge-primary { background: linear-gradient(135deg, #2563eb, #3b82f6); }
.badge-danger { background: linear-gradient(135deg, #dc2626, #ef4444); }
.badge-success { background: linear-gradient(135deg, #059669, #10b981); }

.order-serial { font-size: 12px; color: var(--portal-muted); font-family: monospace; margin-bottom: 8px; }
.equipment-name { margin: 0 80px 16px 0; font-size: 17px; font-weight: 800; color: var(--portal-ink); }

.info-grid { display: flex; gap: 10px; margin-bottom: 12px; }
.info-cell { flex: 1; padding: 12px; border-radius: 16px; }
.bg-slate { background-color: rgba(239, 244, 249, 0.92); }
.cell-label { display: block; font-size: 10px; color: var(--portal-muted); margin-bottom: 6px; letter-spacing: 0.08em; text-transform: uppercase; }
.cell-value { font-size: 13px; font-weight: 700; color: var(--portal-ink); }
.text-primary { color: #2563eb; }
.text-orange { color: #f59e0b; }

.description { font-size: 12px; color: var(--portal-text); line-height: 1.6; margin: 8px 0; }

.card-actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed rgba(16, 33, 48, 0.08);
  display: flex;
  justify-content: flex-end;
}
.report-btn { border-radius: 999px; font-weight: 700; font-size: 12px; }
</style>
