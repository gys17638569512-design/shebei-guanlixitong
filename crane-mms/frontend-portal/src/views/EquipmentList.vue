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
  background: rgba(255, 255, 255, 0.62) !important;
  backdrop-filter: blur(18px);
}

.filter-sticky {
  position: sticky;
  top: 46px;
  z-index: 100;
  background: rgba(238, 243, 248, 0.84);
  backdrop-filter: blur(16px);
  padding: 0 0 10px;
}

.equip-list { padding: 12px 16px; }

.equip-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(246, 249, 252, 0.9));
  border-radius: 24px;
  padding: 18px;
  margin-bottom: 16px;
  box-shadow: 0 18px 32px rgba(8, 24, 40, 0.06);
  border: 1px solid rgba(16, 33, 48, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.name { margin: 0; font-size: 17px; font-weight: 800; color: var(--portal-ink); margin-bottom: 4px; }
.category { font-size: 12px; color: var(--portal-muted); }
.status-tag { padding: 4px 10px; font-weight: 700; box-shadow: 0 10px 18px rgba(8, 24, 40, 0.08); }

.specs-grid {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
}
.spec-item {
  flex: 1;
  background: rgba(239, 244, 249, 0.9);
  padding: 12px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
}
.spec-label { font-size: 10px; color: var(--portal-muted); text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.08em; }
.spec-val { font-size: 13px; font-weight: 700; color: var(--portal-ink); }
.text-danger { color: #ef4444; }

.detail-btn {
  border-color: rgba(16, 33, 48, 0.1) !important;
  color: var(--portal-text) !important;
  font-weight: 600;
  font-size: 12px;
}
</style>
