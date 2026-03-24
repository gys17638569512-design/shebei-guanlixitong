<template>
  <div class="workspace-page dashboard-page" v-loading="loading">
    <section class="workspace-hero">
      <div class="workspace-hero__body">
        <p class="workspace-kicker">Operations Situation Room</p>
        <h2 class="workspace-title">您好，{{ userName }}，今日维保指挥面已就绪</h2>
        <p class="workspace-description">
          从排程、执行、签字到归档，以统一作业视图掌握起重机维保业务的节奏、风险与资源状态。
        </p>
        <div class="workspace-badges">
          <span class="soft-pill">闭环率 {{ completionRate }}%</span>
          <span class="soft-pill">进行中 {{ stats.cards.ongoing_orders || 0 }} 项</span>
          <span class="soft-pill">设备分布 {{ stats.equipment_distribution.length || 0 }} 类</span>
        </div>
      </div>

      <div class="workspace-hero__aside dashboard-hero-grid">
        <div class="workspace-aside-card">
          <span class="workspace-aside-card__label">今日态势</span>
          <span class="workspace-aside-card__value">{{ fullDate }}</span>
          <span class="workspace-aside-card__meta">控制看板基于当前归档与工单数据实时刷新</span>
        </div>
        <div class="workspace-aside-card">
          <span class="workspace-aside-card__label">主导设备类型</span>
          <span class="workspace-aside-card__value">{{ dominantCategory }}</span>
          <span class="workspace-aside-card__meta">当前设备画像中占比最高的设备门类</span>
        </div>
      </div>
    </section>

    <section class="metrics-grid">
      <article v-for="card in metricCards" :key="card.label" class="metric-tile">
        <div class="metric-label">{{ card.label }}</div>
        <div class="metric-value">{{ card.value }}</div>
        <div class="metric-footnote">{{ card.hint }}</div>
      </article>
    </section>

    <section class="surface-grid surface-grid--two">
      <article class="surface-panel">
        <div class="surface-panel__header">
          <div>
            <h3 class="surface-panel__title">近七日工单节奏</h3>
            <p class="surface-panel__subtitle">观察排程波动、执行压强与交付节奏。</p>
          </div>
        </div>
        <div class="surface-panel__body">
          <div id="trend-chart" class="chart-container chart-container--large"></div>
        </div>
      </article>

      <div class="surface-grid">
        <article class="surface-panel">
          <div class="surface-panel__header">
            <div>
              <h3 class="surface-panel__title">设备类型画像</h3>
              <p class="surface-panel__subtitle">当前在册设备结构，用于判断资源侧重点。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div id="pie-chart" class="chart-container chart-container--medium"></div>
          </div>
        </article>

        <article class="surface-panel surface-panel--dark">
          <div class="surface-panel__header">
            <div>
              <h3 class="surface-panel__title">运行判读</h3>
              <p class="surface-panel__subtitle">把统计数据翻译成可行动的运营提示。</p>
            </div>
          </div>
          <div class="surface-panel__body">
            <div class="data-rail">
              <div v-for="item in insightRows" :key="item.label" class="data-rail__item">
                <div class="stacked-text">
                  <span class="eyebrow-label">{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                  <span>{{ item.description }}</span>
                </div>
                <span class="status-dot" :class="item.tone"></span>
              </div>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getDashboardStats } from '@/api/stats'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const loading = ref(false)
const stats = ref({
  cards: {},
  equipment_distribution: [],
  order_trend: []
})

const userName = computed(() => authStore.user?.name || '管理员')
const fullDate = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${['日', '一', '二', '三', '四', '五', '六'][d.getDay()]}`
})

const completionRate = computed(() => {
  const total = Number(stats.value.cards.total_orders || 0)
  const completed = Number(stats.value.cards.completed_orders || 0)
  return total ? Math.round((completed / total) * 100) : 0
})

const dominantCategory = computed(() => {
  const items = stats.value.equipment_distribution || []
  if (!items.length) return '暂无数据'
  return items.slice().sort((a, b) => (b.value || 0) - (a.value || 0))[0].name
})

const pendingArchiveCount = computed(() => {
  const total = Number(stats.value.cards.total_orders || 0)
  const completed = Number(stats.value.cards.completed_orders || 0)
  return Math.max(total - completed, 0)
})

const metricCards = computed(() => [
  {
    label: '累计工单',
    value: stats.value.cards.total_orders || 0,
    hint: '当前系统内累计沉淀的维保任务'
  },
  {
    label: '进行中任务',
    value: stats.value.cards.ongoing_orders || 0,
    hint: '需要持续追踪执行状态的在途工单'
  },
  {
    label: '归档闭环',
    value: `${completionRate.value}%`,
    hint: '已签字归档工单在总工单中的占比'
  },
  {
    label: '在册设备',
    value: stats.value.cards.total_equipments || 0,
    hint: '当前纳入运营视图的设备资产总数'
  }
])

const insightRows = computed(() => [
  {
    label: '归档缺口',
    value: `${pendingArchiveCount.value} 单`,
    description: pendingArchiveCount.value ? '仍有工单未进入归档闭环，建议优先跟进签字资料。' : '当前归档节奏健康，没有明显积压。',
    tone: pendingArchiveCount.value > 3 ? 'warning' : 'success'
  },
  {
    label: '执行压力',
    value: `${stats.value.cards.ongoing_orders || 0} 单`,
    description: '结合进行中任务数，判断现场资源是否需要调配。',
    tone: Number(stats.value.cards.ongoing_orders || 0) > 4 ? 'warning' : ''
  },
  {
    label: '设备结构',
    value: dominantCategory.value,
    description: '主导设备类型将影响模板维护与备件优先级。',
    tone: 'success'
  }
])

let trendChart = null
let pieChart = null

const initCharts = () => {
  const trendDom = document.getElementById('trend-chart')
  if (trendDom) {
    trendChart?.dispose()
    trendChart = echarts.init(trendDom)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '4%', right: '3%', top: '8%', bottom: '6%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: stats.value.order_trend.map((item) => item.date),
        axisLine: { lineStyle: { color: '#d9e4ef' } },
        axisLabel: { color: '#6c8194', fontFamily: 'Bahnschrift, Segoe UI, sans-serif' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: 'rgba(15, 33, 51, 0.08)', type: 'dashed' } },
        axisLabel: { color: '#6c8194' }
      },
      series: [
        {
          name: '工单数',
          type: 'line',
          smooth: true,
          data: stats.value.order_trend.map((item) => item.count),
          symbolSize: 9,
          itemStyle: { color: '#2f89ff' },
          lineStyle: { width: 4, shadowColor: 'rgba(47, 137, 255, 0.18)', shadowBlur: 14 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(47, 137, 255, 0.28)' },
              { offset: 1, color: 'rgba(47, 137, 255, 0.02)' }
            ])
          }
        }
      ]
    })
  }

  const pieDom = document.getElementById('pie-chart')
  if (pieDom) {
    pieChart?.dispose()
    pieChart = echarts.init(pieDom)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      legend: {
        bottom: '0%',
        left: 'center',
        icon: 'circle',
        itemGap: 14,
        textStyle: { color: '#667a8c' }
      },
      series: [
        {
          type: 'pie',
          radius: ['48%', '76%'],
          center: ['50%', '43%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 14,
            borderColor: '#fff',
            borderWidth: 4
          },
          label: { show: false },
          emphasis: {
            label: { show: true, fontSize: 16, fontWeight: 'bold' },
            itemStyle: { shadowBlur: 14, shadowColor: 'rgba(10, 24, 39, 0.12)' }
          },
          data: stats.value.equipment_distribution
        }
      ],
      color: ['#2f89ff', '#2cb67d', '#ffbf5f', '#6cc0ff', '#7d5cff']
    })
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDashboardStats()
    stats.value = res || stats.value
    await nextTick()
    initCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.dashboard-hero-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(200px, 1fr));
  gap: 14px;
}

.chart-container {
  width: 100%;
}

.chart-container--large {
  height: 360px;
}

.chart-container--medium {
  height: 280px;
}

@media (max-width: 1200px) {
  .dashboard-hero-grid {
    grid-template-columns: 1fr;
  }
}
</style>
