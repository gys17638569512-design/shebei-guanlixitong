<template>
  <div class="report-archive-container">
    <div class="page-header">
      <div class="title-group">
        <h1 class="page-title">集中报告中心</h1>
        <p class="page-subtitle">归档与下载所有已完成工单的维护报告及电子签名凭证</p>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-card v-if="canViewArchive" class="table-card">
      <el-table :data="reports" v-loading="loading" style="width: 100%" border stripe>
        <el-table-column prop="order_id" label="工单ID" width="90" align="center" />
        <el-table-column prop="equipment_name" label="关联设备" min-width="150" />
        <el-table-column prop="customer_name" label="所属客户" min-width="150" />
        <el-table-column prop="completed_at" label="归档时间" width="180" align="center" />
        <el-table-column label="PDF 报告" width="120" align="center">
          <template #default="{ row }">
            <el-link type="primary" :href="row.pdf_url" target="_blank" v-if="row.pdf_url && canDownloadReports">
              下载报告 <el-icon><Download /></el-icon>
            </el-link>
            <span v-else class="text-gray">{{ row.pdf_url ? '无下载权限' : '生成中...' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="电子签章证书" width="140" align="center">
          <template #default="{ row }">
            <el-link type="success" :href="row.esign_cert_url" target="_blank" v-if="row.esign_cert_url && canViewSignature">
              查看凭证 <el-icon><Document /></el-icon>
            </el-link>
            <span v-else class="text-gray">{{ row.esign_cert_url ? '无查看权限' : '未提供凭证' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getReportArchive } from '@/api/report'
import { Download, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { SETTINGS_PERMISSIONS } from '@/constants/permissions'

const authStore = useAuthStore()
const loading = ref(false)
const reports = ref([])
const canViewArchive = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.REPORTS_MODULE_ARCHIVE))
const canDownloadReports = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.REPORTS_DOWNLOAD))
const canViewSignature = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.REPORTS_SIGNATURE_VIEW))

const fetchReports = async () => {
  loading.value = true
  try {
    const res = await getReportArchive()
    reports.value = res || []
  } catch (err) {
    ElMessage.error('加载报告列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchReports)
</script>

<style scoped>
.report-archive-container {
  padding: 0;
}
.title-group {
  margin-bottom: 24px;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}
.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
}
.text-gray {
  color: #999;
  font-size: 12px;
}
</style>
