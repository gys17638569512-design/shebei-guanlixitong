<template>
  <div class="dashboard-container" v-loading="loading">
    <!-- 顶部欢迎区 -->
    <header class="welcome-header">
      <div class="welcome-text">
        <span class="welcome-kicker">运营指挥舱</span>
        <h1 class="welcome-title">您好，{{ userName }}</h1>
        <p class="welcome-subtitle">从排期、执行、签字到归档，实时掌握起重机维保业务的每一个关键节点。</p>
        <div class="signal-row">
          <span class="signal-pill">全国工单态势</span>
          <span class="signal-pill ghost">维保执行闭环</span>
          <span class="signal-pill ghost">多端实时协同</span>
        </div>
      </div>
      <div class="time-capsule">
        <span class="capsule-label">当前日期</span>
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
        axisLabel: { color: '#6a7f92', fontFamily: 'Bahnschrift, Segoe UI, PingFang SC, Microsoft YaHei, sans-serif' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { type: 'dashed', color: 'rgba(16, 33, 48, 0.08)' } },
        axisLabel: { color: '#6a7f92' }
      },
      series: [
        {
          name: '工单数',
          type: 'line',
          smooth: true,
          data: stats.value.order_trend.map(i => i.count),
          itemStyle: { color: '#0c75d8', borderWidth: 2 },
          lineStyle: { width: 3, shadowColor: 'rgba(12, 117, 216, 0.34)', shadowBlur: 10, shadowOffsetY: 5 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(12, 117, 216, 0.2)' },
              { offset: 1, color: 'rgba(12, 117, 216, 0)' }
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
      legend: { bottom: '0%', left: 'center', icon: 'circle', itemGap: 15, textStyle: { color: '#5e7387' } },
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
      color: ['#0c75d8', '#1fa56d', '#ffb347', '#4bb1ff', '#f05f61']
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

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 30px;
  padding: 28px 30px;
  border-radius: 28px;
  background:
    linear-gradient(140deg, rgba(8, 21, 33, 0.96) 0%, rgba(15, 42, 67, 0.92) 52%, rgba(20, 75, 116, 0.88) 100%);
  box-shadow: 0 28px 54px rgba(8, 24, 40, 0.14);
  overflow: hidden;
  position: relative;
}

.welcome-header::before,
.welcome-header::after {
  content: "";
  position: absolute;
  pointer-events: none;
}

.welcome-header::before {
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 100px 100px;
  opacity: 0.36;
}

.welcome-header::after {
  top: -70px;
  right: -40px;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 179, 71, 0.24), transparent 68%);
}

.welcome-text,
.time-capsule {
  position: relative;
  z-index: 1;
}

.welcome-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 196, 124, 0.96);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 16px;
}
.welcome-title {
  font-family: var(--font-display);
  font-size: 34px;
  font-weight: 800;
  color: #f8fbff;
  margin: 0 0 8px 0;
  letter-spacing: 0.04em;
}
.welcome-subtitle {
  font-size: 15px;
  color: rgba(236, 242, 247, 0.72);
  margin: 0;
  font-weight: 500;
  max-width: 700px;
  line-height: 1.7;
}

.signal-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.signal-pill {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: #f8fbff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.signal-pill.ghost {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(236, 242, 247, 0.78);
}
.time-capsule {
  min-width: 220px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 14px 18px;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.capsule-label {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: rgba(255, 196, 124, 0.88);
  margin-bottom: 10px;
}
.curr-date {
  font-size: 14px;
  font-weight: 700;
  color: #f8fbff;
  letter-spacing: 0.5px;
  line-height: 1.5;
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.bento-card {
  position: relative;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.86));
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 18px 40px rgba(8, 24, 40, 0.08);
  border: 1px solid rgba(16, 33, 48, 0.08);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}
.bento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 48px rgba(8, 24, 40, 0.12);
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
.glow-orb.bg-blue { background: #0c75d8; }
.glow-orb.bg-orange { background: #ffb347; }
.glow-orb.bg-green { background: #1fa56d; }
.glow-orb.bg-purple { background: #4bb1ff; }

.card-content {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.card-label {
  font-size: 14px;
  font-weight: 700;
  color: #6a7f92;
  margin: 0 0 8px 0;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.card-value {
  font-family: var(--font-display);
  font-size: 38px;
  font-weight: 900;
  color: #102130;
  margin: 0;
  line-height: 1.1;
  letter-spacing: 0.02em;
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
.icon-box.blue { background: rgba(12, 117, 216, 0.1); color: #0c75d8; }
.icon-box.orange { background: rgba(255, 179, 71, 0.14); color: #d37a15; }
.icon-box.green { background: rgba(31, 165, 109, 0.12); color: #1b8f5f; }
.icon-box.purple { background: rgba(71, 179, 255, 0.12); color: #0f79c4; }

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}
@media (max-width: 1024px) {
  .charts-grid { grid-template-columns: 1fr; }
}

.chart-panel {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.86));
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 18px 40px rgba(8, 24, 40, 0.08);
  border: 1px solid rgba(16, 33, 48, 0.08);
}
.panel-header {
  font-size: 15px;
  font-weight: 700;
  color: #102130;
  margin-bottom: 24px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.chart-container {
  width: 100%;
  height: 320px;
}

@media (max-width: 900px) {
  .welcome-header {
    flex-direction: column;
    padding: 24px 22px;
  }

  .welcome-title {
    font-size: 28px;
  }

  .time-capsule {
    min-width: auto;
    width: 100%;
  }
}
</style>
