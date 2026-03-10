<template>
  <div class="order-detail">
    <van-nav-bar 
      title="工单详情" 
      left-arrow 
      @click-left="router.back()" 
      fixed 
      placeholder 
    />

    <van-skeleton title :row="5" :loading="!order.id">
      <div class="detail-content">
        <div class="status-banner" :class="order.status.toLowerCase()">
          <van-icon name="clock-o" v-if="order.status !== 'COMPLETED'" />
          <van-icon name="passed" v-else />
          <span>{{ getStatusLabel(order.status) }}</span>
        </div>

        <van-cell-group inset title="基础信息">
          <van-cell title="工单流水" :value="`#${order.id}`" />
          <van-cell title="维保类型" :value="order.order_type" />
          <van-cell title="计划日期" :value="order.plan_date" />
          <van-cell title="打卡时间" :value="order.checkin_time || '—'" />
        </van-cell-group>

        <van-cell-group inset title="维保排查结果" v-if="order.problem_description">
          <van-cell title="发现问题与隐患">
            <template #label><div class="text-content">{{ order.problem_description }}</div></template>
          </van-cell>
          <van-cell title="处理结论与建议">
            <template #label><div class="text-content">{{ order.solution }}</div></template>
          </van-cell>
        </van-cell-group>

        <div class="action-bar" v-if="order.status === 'COMPLETED' && order.pdf_report_url">
          <van-button 
            block 
            type="primary" 
            icon="description"
            @click="viewReport"
          >
            查看完整的 PDF 维保报告
          </van-button>
        </div>

        <div class="action-bar" v-if="order.status === 'PENDING_SIGN' || order.status === 'IN_PROGRESS'">
          <van-button 
            block 
            type="danger" 
            round
            @click="router.push(`/sign/${order.id}`)"
          >
            手写确认并签字归档
          </van-button>
        </div>
      </div>
    </van-skeleton>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const order = ref({ status: '' })

const loadData = async () => {
  try {
    const res = await request.get(`/orders/${route.params.id}`)
    order.value = res || {}
  } catch (err) {}
}

const getStatusLabel = (s) => {
  const map = { PENDING: '系统待处理', IN_PROGRESS: '维保进行中', PENDING_SIGN: '等待客户验收', COMPLETED: '维保已完结' }
  return map[s] || s
}

const viewReport = () => {
  if (order.value.pdf_report_url) {
    window.open(order.value.pdf_report_url, '_blank')
  }
}

onMounted(loadData)
</script>

<style scoped>
.order-detail { min-height: 100vh; padding-bottom: 30px; }
.status-banner {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #fff;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 12px;
}
.status-banner.completed { background: linear-gradient(135deg, #07c160, #39d38d); }
.status-banner.pending_sign { background: linear-gradient(135deg, #ee0a24, #ff4c4c); }
.status-banner.in_progress { background: linear-gradient(135deg, #1989fa, #5cadff); }
.status-banner.pending { background: linear-gradient(135deg, #ff976a, #ffbb9a); }

.text-content { color: #323233; padding-top: 4px; line-height: 1.5; white-space: pre-wrap; }
.action-bar { margin: 24px 16px; }
</style>
