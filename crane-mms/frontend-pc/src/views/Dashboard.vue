<template>
  <div class="dashboard-container" v-loading="loading">
    <!-- 顶部欢迎区 -->
    <header class="welcome-header">
      <div class="welcome-text">
        <h1 class="welcome-title">您好, {{ userName }} 👋</h1>
        <p class="welcome-subtitle">实时掌握全国起重机维保动态与全生命周期数据。</p>
      </div>
      <div class="time-capsule">
        <span class="curr-date">{{ fullDate }}</span>
      </div>
    </header>

    <!-- 便当盒数据卡片 / Bento Grid -->
    <div class="bento-grid">
      <!-- 累计工单 -->
      <div class="bento-card group">
        <div class="glow-orb bg-blue"></div>
        <div class="card-content">
          <div>
            <p class="card-label">累计工单</p>
            <h3 class="card-value">{{ stats.cards.total_orders || 0 }}</h3>
          </div>
          <div class="icon-box blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
          </div>
        </div>
      </div>

      <!-- 进行中任务 -->
      <div class="bento-card group">
        <div class="glow-orb bg-orange"></div>
        <div class="card-content">
          <div>
            <p class="card-label">进行中任务</p>
            <h3 class="card-value">{{ stats.cards.ongoing_orders || 0 }}</h3>
          </div>
          <div class="icon-box orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
          </div>
        </div>
      </div>

      <!-- 已归档结案 -->
      <div class="bento-card group">
        <div class="glow-orb bg-green"></div>
        <div class="card-content">
          <div>
            <p class="card-label">已归档结案</p>
            <h3 class="card-value">{{ stats.cards.completed_orders || 0 }}</h3>
          </div>
          <div class="icon-box green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
        </div>
      </div>

      <!-- 在册设备 -->
      <div class="bento-card group">
        <div class="glow-orb bg-purple"></div>
        <div class="card-content">
          <div>
            <p class="card-label">在册设备</p>
            <h3 class="card-value">{{ stats.cards.total_equipments || 0 }}</h3>
          </div>
          <div class="icon-box purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表展示区 -->
    <div class="charts-grid mt-6">
      <div class="chart-panel trend-panel">
        <div class="panel-header">近七日维保任务趋势</div>
        <div id="trend-chart" class="chart-container"></div>
      </div>
      <div class="chart-panel pie-panel">
        <div class="panel-header">设备类型画像</div>
        <div id="pie-chart" class="chart-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
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
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日 星期${['日','一','二','三','四','五','六'][d.getDay()]}`
})

let trendChart = null
let pieChart = null

const initCharts = () => {
  // 趋势图
  const trendDom = document.getElementById('trend-chart')
  if (trendDom) {
    trendChart = echarts.init(trendDom)
    const option = {
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: stats.value.order_trend.map(i => i.date),
        axisLine: { lineStyle: { color: '#eee' } },
        axisLabel: { color: '#999', fontFamily: 'Inter' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } }
      },
      series: [
        {
          name: '工单数',
          type: 'line',
          smooth: true,
          data: stats.value.order_trend.map(i => i.count),
          itemStyle: { color: '#3b82f6', borderWidth: 2 },
          lineStyle: { width: 3, shadowColor: 'rgba(59, 130, 246, 0.4)', shadowBlur: 10, shadowOffsetY: 5 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(59, 130, 246,0.2)' },
              { offset: 1, color: 'rgba(59, 130, 246,0)' }
            ])
          }
        }
      ]
    }
    trendChart.setOption(option)
  }

  // 饼图
  const pieDom = document.getElementById('pie-chart')
  if (pieDom) {
    pieChart = echarts.init(pieDom)
    const option = {
      tooltip: { trigger: 'item' },
      legend: { bottom: '0%', left: 'center', icon: 'circle', itemGap: 15 },
      series: [
        {
          name: '占比分布',
          type: 'pie',
          radius: ['45%', '75%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 12, borderColor: '#fff', borderWidth: 3 },
          label: { show: false },
          emphasis: { 
            label: { show: true, fontSize: 16, fontWeight: 'bold' },
            itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.1)' }
          },
          data: stats.value.equipment_distribution
        }
      ],
      color: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']
    }
    pieChart.setOption(option)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDashboardStats()
    stats.value = res || stats.value
    // DOM 渲染后初始化图表
    setTimeout(initCharts, 100)
  } catch (err) {
    ElMessage.error("获取统计数据失败")
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
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
  max-width: 1600px;
  margin: 0 auto;
}

/* ==================== 头部欢迎区 ==================== */
.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}
.welcome-title {
  font-size: 28px;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}
.welcome-subtitle {
  font-size: 15px;
  color: #64748b;
  margin: 0;
  font-weight: 500;
}
.time-capsule {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 8px 20px;
  border-radius: 9999px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
}
.curr-date {
  font-size: 14px;
  font-weight: 600;
  color: #0ea5e9;
  letter-spacing: 0.5px;
}

/* ==================== Bento Grid 数据卡片 ==================== */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.bento-card {
  position: relative;
  background: #ffffff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(226, 232, 240, 0.4);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}
.bento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06);
}

.glow-orb {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.2;
  transition: opacity 0.3s ease;
}
.bento-card:hover .glow-orb {
  opacity: 0.4;
}
.glow-orb.bg-blue { background: #3b82f6; }
.glow-orb.bg-orange { background: #f59e0b; }
.glow-orb.bg-green { background: #10b981; }
.glow-orb.bg-purple { background: #8b5cf6; }

.card-content {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.card-label {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  margin: 0 0 8px 0;
}
.card-value {
  font-size: 36px;
  font-weight: 900;
  color: #0f172a;
  margin: 0;
  line-height: 1.1;
  font-family: 'Inter', system-ui, sans-serif;
  letter-spacing: -1px;
}

.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-box svg { width: 24px; height: 24px; }
.icon-box.blue { background: #eff6ff; color: #3b82f6; }
.icon-box.orange { background: #fffbeb; color: #f59e0b; }
.icon-box.green { background: #ecfdf5; color: #10b981; }
.icon-box.purple { background: #f5f3ff; color: #8b5cf6; }

/* ==================== 现代图表画板 ==================== */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}
@media (max-width: 1024px) {
  .charts-grid { grid-template-columns: 1fr; }
}

.chart-panel {
  background: #ffffff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(226, 232, 240, 0.4);
}
.panel-header {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 24px;
}
.chart-container {
  width: 100%;
  height: 320px;
}
</style>
