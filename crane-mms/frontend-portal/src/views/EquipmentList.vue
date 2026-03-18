<template>
  <div class="equip-container pb-safe">
    <van-nav-bar title="设备一览表" fixed placeholder :border="false" class="glass-nav" />

    <!-- 搜索与筛选 -->
    <div class="filter-sticky">
      <van-search v-model="searchText" placeholder="搜索设备名称" background="transparent" />
      <van-tabs v-model:active="activeTab" color="#1677ff" background="transparent" shrink>
        <van-tab title="全部" name="all" />
        <van-tab title="正常" name="正常" />
        <van-tab title="待检" name="待检" />
      </van-tabs>
    </div>

    <!-- 设备列表 -->
    <div class="equip-list">
      <div 
        v-for="item in filteredList" 
        :key="item.id" 
        class="equip-card interactive-card"
      >
        <div class="card-header">
          <div class="equip-main">
            <h3 class="name">{{ item.name }}</h3>
            <span class="category">{{ item.category }} · {{ item.model_type }}</span>
          </div>
          <van-tag :type="item.status === '正常' ? 'success' : 'danger'" round size="medium" class="status-tag">
            {{ item.status }}
          </van-tag>
        </div>

        <div class="specs-grid">
          <div class="spec-item">
            <span class="spec-label">起重量</span>
            <span class="spec-val">{{ item.tonnage }}</span>
          </div>
          <div class="spec-item">
            <span class="spec-label">下次报检</span>
            <span class="spec-val" :class="{ 'text-danger': item.status === '待检' }">
              {{ item.next_inspection_date }}
            </span>
          </div>
        </div>

        <div class="card-footer">
          <van-button size="small" plain round block class="detail-btn">
            查看技术档案详情
          </van-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <van-empty v-if="filteredList.length === 0" description="暂无符合条件的设备" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import request from '../utils/request'

const list = ref([])
const searchText = ref('')
const activeTab = ref('all')

const fetchData = async () => {
  try {
    const res = await request.get('/equipments')
    list.value = res || []
  } catch (err) {
    console.error(err)
  }
}

const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchText.value.toLowerCase())
    const matchesTab = activeTab.value === 'all' || item.status === activeTab.value
    return matchesSearch && matchesTab
  })
})

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.equip-container { background-color: #f7f8fa; min-height: 100vh; }
.pb-safe { padding-bottom: calc(env(safe-area-inset-bottom) + 30px); }

.glass-nav :deep(.van-nav-bar) {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(10px);
}

.filter-sticky {
  position: sticky;
  top: 46px;
  z-index: 100;
  background: rgba(247, 248, 250, 0.9);
  backdrop-filter: blur(10px);
  padding-bottom: 8px;
}

.equip-list { padding: 12px 16px; }

.equip-card {
  background: #fff;
  border-radius: 20px;
  padding: 18px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0,0,0,0.01);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.name { margin: 0; font-size: 16px; font-weight: 800; color: #1e293b; margin-bottom: 4px; }
.category { font-size: 12px; color: #94a3b8; }
.status-tag { padding: 4px 10px; font-weight: 700; }

.specs-grid {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
}
.spec-item {
  flex: 1;
  background: #f8fafc;
  padding: 10px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}
.spec-label { font-size: 10px; color: #64748b; text-transform: uppercase; margin-bottom: 4px; }
.spec-val { font-size: 13px; font-weight: 700; color: #334155; }
.text-danger { color: #ef4444; }

.detail-btn {
  border-color: #e2e8f0 !important;
  color: #64748b !important;
  font-weight: 600;
  font-size: 12px;
}

.interactive-card:active { transform: scale(0.98); }
</style>
