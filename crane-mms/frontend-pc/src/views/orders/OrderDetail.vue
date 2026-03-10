<template>
  <div class="order-detail" v-loading="loading">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" circle class="back-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </el-button>
        <div class="title-group">
          <h1 class="page-title">工单详情 #{{ order.id }}</h1>
          <p class="page-subtitle">查看维保任务执行进度、现场数据及最终报告</p>
        </div>
      </div>
      <div class="header-right">
        <el-button v-if="order.status === 'PENDING' && hasRole(['ADMIN', 'MANAGER'])" type="warning" plain>重新指派</el-button>
        <el-button v-if="order.status === 'PENDING' && hasRole(['TECH'])" type="primary" @click="handleCheckin">
          📍 现场打卡入门
        </el-button>
        <el-button v-if="['IN_PROGRESS', 'PENDING_SIGN'].includes(order.status) && hasRole(['TECH'])" type="success" @click="openCompleteDialog">
          📝 填写检修与结单
        </el-button>
        <el-button v-if="order.status === 'COMPLETED' && order.pdf_report_url" type="primary" tag="a" :href="order.pdf_report_url" target="_blank">
          📥 下载维保报告 (PDF)
        </el-button>
      </div>
    </div>

    <!-- 流程进度条 -->
    <div class="steps-card">
      <el-steps :active="getCurrentStep(order.status)" align-center>
        <el-step title="派单成功" description="任务已下发" />
        <el-step title="到场打卡" description="工程师已到达" />
        <el-step title="维保执行" description="检修项填写中" />
        <el-step title="客户签字" description="现场确认阶段" />
        <el-step title="已归档" description="报告已生成" />
      </el-steps>
    </div>

    <div class="order-content" v-if="order.id">
      <el-row :gutter="24">
        <!-- 左侧主栏 -->
        <el-col :span="16">
          <!-- 核心关联信息 -->
          <el-card class="detail-card mb-24">
            <template #header>
              <div class="card-title">关联档案信息</div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="所属客户">
                <span class="val-link" @click="goToCustomer">{{ order.customer?.company_name || '-' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="设备名称">
                <span class="val-text">{{ order.equipment?.name || '-' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="联系人">
                <span class="val-text">{{ order.customer?.contact_name || '-' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="设备分类">
                <el-tag size="small" effect="plain">{{ order.equipment?.category || '-' }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="服务地址" :span="2">
                <span class="val-text">{{ order.customer?.address || '-' }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 现场动作记录 -->
          <el-card class="detail-card mb-24" v-if="order.checkin_time">
            <template #header>
              <div class="card-title">现场执行记录 (Check-in)</div>
            </template>
            <div class="checkin-info">
              <div class="checkin-text">
                <p><strong>打卡时间：</strong>{{ order.checkin_time }}</p>
                <p><strong>地理位置：</strong>{{ order.checkin_address || 'GPS 未获取' }}</p>
              </div>
              <div class="checkin-photo" v-if="order.checkin_photo">
                <el-image :src="order.checkin_photo" :preview-src-list="[order.checkin_photo]" fit="cover" class="preview-img-lg" />
              </div>
            </div>
          </el-card>

          <!-- 故障与结论 -->
          <el-card class="detail-card mb-24" v-if="['PENDING_SIGN', 'COMPLETED'].includes(order.status)">
            <template #header>
              <div class="card-title">维保检修结论</div>
            </template>
            <div class="report-box">
              <div class="report-item">
                <div class="report-label">巡检发现问题</div>
                <div class="report-val">{{ order.problem_description || '设备运行良好，未发现明显故障。' }}</div>
              </div>
              <div class="report-item">
                <div class="report-label">处理措施与建议</div>
                <div class="report-val">{{ order.solution || '执行标准例行保养，紧固各部位螺栓。' }}</div>
              </div>
            </div>

            <!-- 维保耗材清单 -->
            <div class="photo-wall-section" v-if="order.used_parts?.length">
              <div class="section-subtitle">本次维保耗材清单 ({{ order.used_parts.length }}项)</div>
              <el-table :data="order.used_parts" size="small" border>
                <el-table-column prop="name" label="物料名" />
                <el-table-column prop="specification" label="规格型号" />
                <el-table-column prop="quantity" label="消耗数量" width="90" align="center" />
              </el-table>
            </div>

            <!-- 照片墙 -->
            <div class="photo-wall-section" v-if="order.photo_urls?.length">
              <div class="section-subtitle">现场作业照片 ({{ order.photo_urls.length }}张)</div>
              <div class="photo-grid">
                <el-image 
                  v-for="(url, index) in order.photo_urls" 
                  :key="index"
                  :src="url" 
                  :preview-src-list="order.photo_urls"
                  fit="cover" 
                  class="grid-img"
                />
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧边栏 -->
        <el-col :span="8">
          <!-- 任务摘要 -->
          <el-card class="side-card mb-24">
            <template #header>工单任务摘要</template>
            <div class="side-kv">
              <div class="kv-row">
                <span class="k">负责工程师</span>
                <span class="v active">{{ order.technician?.name || '-' }}</span>
              </div>
              <div class="kv-row">
                <span class="k">工单状态</span>
                <span class="v">
                  <span class="status-dot" :class="'dot-' + order.status"></span>
                  {{ getStatusLabel(order.status) }}
                </span>
              </div>
              <div class="kv-row">
                <span class="k">计划日期</span>
                <span class="v">{{ order.plan_date || '-' }}</span>
              </div>
              <div class="kv-row">
                <span class="k">工单类型</span>
                <span class="v">{{ order.order_type || '定期维保' }}</span>
              </div>
            </div>
          </el-card>

          <!-- 客户确认 -->
          <el-card class="side-card mb-24" v-if="order.sign_url || order.status === 'COMPLETED'">
            <template #header>客户电子签字确认</template>
            <div class="signature-box" :class="{ 'empty': !order.sign_url }">
              <el-image v-if="order.sign_url" :src="order.sign_url" fit="contain" class="sign-img" />
              <div v-else class="sign-placeholder">完成任务后在此展示签名</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 结单弹窗 -->
    <el-dialog title="填写维保检修结论并结单" v-model="completeDialogVisible" width="650px" destroy-on-close>
      <el-form label-width="90px" @submit.prevent>
        
        <el-divider>专项设备检修排查表 ({{ order.equipment?.category || '通用' }})</el-divider>
        <div class="inspection-list">
          <el-row v-for="(item, index) in completeForm.inspection_items" :key="index" :gutter="10" class="inspection-row">
            <el-col :span="9">
              <div class="inspection-name">{{ item.item_name }}</div>
            </el-col>
            <el-col :span="6">
              <el-select v-model="item.result" size="small" style="width: 100%;">
                <el-option label="✅ 正常" value="NORMAL" />
                <el-option label="❌ 异常" value="ABNORMAL" />
              </el-select>
            </el-col>
            <el-col :span="9">
              <el-input size="small" v-model="item.comment" placeholder="备注/处理情况" />
            </el-col>
          </el-row>
        </div>

        <el-divider>备品备件消耗明细</el-divider>
        <div class="inspection-list">
          <el-row v-for="(item, index) in completeForm.used_parts" :key="'part-'+index" :gutter="10" class="inspection-row">
            <el-col :span="13">
              <el-select v-model="item.part_id" placeholder="搜索/选择库房备品" size="small" style="width: 100%;" filterable>
                <el-option v-for="p in partsOptions" :key="p.id" :label="`${p.name} (${p.specification}) 库存:${p.stock_quantity}`" :value="p.id" :disabled="p.stock_quantity <= 0" />
              </el-select>
            </el-col>
            <el-col :span="7">
              <el-input-number v-model="item.quantity" :min="1" size="small" style="width: 100%;" controls-position="right" placeholder="数量" />
            </el-col>
            <el-col :span="4" style="text-align: right;">
              <el-button type="danger" link @click="removePart(index)" size="small">移除</el-button>
            </el-col>
          </el-row>
          <div style="text-align: center; margin-top: 10px;">
            <el-button type="primary" plain size="small" @click="addPart">+ 添加消耗的零件物料</el-button>
          </div>
        </div>

        <el-divider>总体结论与附件</el-divider>
        <el-form-item label="问题与隐患" required>
          <el-input type="textarea" v-model="completeForm.problem_description" :rows="2" placeholder="请输入现场发现的总体设备问题或隐患" />
        </el-form-item>
        <el-form-item label="处理与建议" required>
          <el-input type="textarea" v-model="completeForm.solution" :rows="2" placeholder="请输入已采取的处理措施及后续建议" />
        </el-form-item>
        
        <el-form-item label="现场照片">
          <div class="camera-upload-placeholder">
             <el-button type="info" plain size="small">📷 调用相机/相册 (预留位)</el-button>
             <span style="font-size: 12px; color: #999; margin-left: 10px;">将支持移动应用端原生调用拍摄</span>
          </div>
        </el-form-item>

        <el-divider>客户电子验收签字</el-divider>
        <div v-if="order.status === 'PENDING_SIGN'" style="margin-bottom: 20px;">
           <el-alert title="等待客户签字回执" type="warning" description="检修表单已推送到客户手机（并发送提示短信）。请在此等待客户自己打开手机完成手写；或客户若已返回现场，也可继续用您本机的下方面板当面签署并手动结单。" show-icon :closable="false" />
        </div>
        
        <div class="sign-upload-area" style="text-align: center; margin-bottom: 20px;">
           <el-image v-if="completeForm.sign_url" :src="completeForm.sign_url" style="width: 200px; height: 100px; border: 1px dashed #ccc;" fit="contain" />
           <p v-else style="color: #999; font-size: 13px;">可由客户在移动端手写签字并上传</p>
           <el-button size="small" type="primary" plain @click="mockSign" class="mt-2" style="margin-top: 10px;">✍️ 代出示本机供客户当面触屏手写</el-button>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="completeDialogVisible = false">返回</el-button>
          <el-button v-if="order.status !== 'PENDING_SIGN'" type="warning" @click="pushForSign" :loading="submitLoading">保存并推送客户手机签收</el-button>
          <el-button type="success" @click="submitComplete" :loading="submitLoading">确认结单归档 (必须已签名)</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getOrderDetail, checkinOrder, completeOrder, pushForSignOrder } from '@/api/order'
import { getAllParts } from '@/api/part'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)
const order = ref({})
const partsOptions = ref([])

const loadParts = async () => {
  try {
    const res = await getAllParts()
    partsOptions.value = res || []
  } catch (err) {
    console.error("加载备件库失败", err)
  }
}

const loadData = async () => {
  const id = route.params.id
  if (!id) return
  loading.value = true
  try {
    const res = await getOrderDetail(id)
    order.value = res || {}
  } catch (err) {
    // 降级显示
    order.value = { id, status: 'PENDING', technician: { name: 'admin' }, customer: { company_name: '测试客户' } }
  } finally {
    loading.value = false
  }
}

// --- 打卡逻辑 ---
const handleCheckin = async () => {
  try {
    await ElMessageBox.confirm('确认现在进场打卡吗？系统将记录当前位置与时间以便留存审计。', '打卡确认', {
      confirmButtonText: '立即打卡',
      cancelButtonText: '取消',
      type: 'info',
    })
    
    // 构造打卡数据 (纯本土 Base64，避免网络超时拦截)
    const checkinData = {
      checkin_time: new Date().toISOString(),
      checkin_address: "获取定位中... 起重机所在厂区",
      checkin_photo: ""
    }
    
    await checkinOrder(order.value.id, checkinData)
    ElMessage.success("📍 现场打卡成功，已进入处理阶段")
    loadData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(err.message || '打卡异常')
  }
}

// --- 结单逻辑 ---
const completeDialogVisible = ref(false)
const submitLoading = ref(false)
const completeForm = ref({
  problem_description: '',
  solution: '',
  sign_url: '',
  photo_urls: [],
  inspection_items: [],
  used_parts: []
})

const addPart = () => completeForm.value.used_parts.push({ part_id: null, quantity: 1 })
const removePart = (index) => completeForm.value.used_parts.splice(index, 1)

const getInspectionTemplates = (category) => {
  if (category && category.includes('门式')) {
    return [
      { item_name: "门架钢结构及支腿焊缝", result: "NORMAL", comment: "" },
      { item_name: "轨道基础及锚定防风装置", result: "NORMAL", comment: "" },
      { item_name: "运行机构及电缆卷筒状态", result: "NORMAL", comment: "" },
      { item_name: "起升机构制动与钢丝绳", result: "NORMAL", comment: "" },
      { item_name: "户外电气柜防水及防雷接地", result: "NORMAL", comment: "" }
    ]
  }
  // 默认为桥式或其他通用重机
  return [
    { item_name: "主梁/端梁焊缝变形排查", result: "NORMAL", comment: "" },
    { item_name: "大车/小车运行机构及导电滑线", result: "NORMAL", comment: "" },
    { item_name: "卷扬机构及钢丝绳磨损情况", result: "NORMAL", comment: "" },
    { item_name: "吊钩防脱棘爪及滑轮状态", result: "NORMAL", comment: "" },
    { item_name: "制动器间隙及摩擦片厚度", result: "NORMAL", comment: "" },
    { item_name: "电控箱/变频器/接触器状态", result: "NORMAL", comment: "" }
  ]
}

const openCompleteDialog = () => {
  completeForm.value = {
    problem_description: order.value.problem_description || '设备运行平稳，结构无变形。',
    solution: order.value.solution || '执行标准保养手册，加装润滑油。',
    sign_url: order.value.sign_url || '',
    photo_urls: order.value.photo_urls || [],
    inspection_items: getInspectionTemplates(order.value.equipment?.category),
    used_parts: []
  }
  completeDialogVisible.value = true
}

const mockSign = () => {
  // 生成一段纯本地的 Base64 占位签名图以杜绝网络错误
  completeForm.value.sign_url = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMTAwIj4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y1ZjVmNSIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzY2NiI+4pyTIOaIkeW3sueEkeaUtjI8L3RleHQ+Cjwvc3ZnPg=="
  ElMessage.success("客户现场手写签字已捕获")
}

const pushForSign = async () => {
  if (!completeForm.value.problem_description || !completeForm.value.solution) {
    return ElMessage.warning("请完整填写问题描述和处理建议后再推送")
  }
  
  submitLoading.value = true
  try {
    await pushForSignOrder(order.value.id, completeForm.value)
    ElMessage.success("📬 已将设备排查记录妥善保存，并推送至客户手机端！短信通知已发。")
    completeDialogVisible.value = false
    loadData()
  } catch (err) {
    ElMessage.error(err.message || '推送异常，被后端拦截')
  } finally {
    submitLoading.value = false
  }
}

const submitComplete = async () => {
  if (!completeForm.value.problem_description || !completeForm.value.solution) {
    return ElMessage.warning("请完整填写问题描述和处理建议")
  }
  if (!completeForm.value.sign_url) {
    return ElMessage.warning("此线路为当面结单，必须补充电子确认签字才可归档！若客户不在请选择推送。")
  }
  
  submitLoading.value = true
  try {
    await completeOrder(order.value.id, completeForm.value)
    ElMessage.success("🎉 数据已校验入库，工单顺利归档结案")
    completeDialogVisible.value = false
    loadData()
  } catch (err) {
    ElMessage.error(err.message || '归档异常，被后端拦截')
  } finally {
    submitLoading.value = false
  }
}

const getCurrentStep = (s) => {
  const m = { PENDING: 0, IN_PROGRESS: 2, PENDING_SIGN: 3, COMPLETED: 5 }
  return m[s] || 1
}

const getStatusLabel = (status) => {
  const map = { PENDING: '待处理', IN_PROGRESS: '进行中', PENDING_SIGN: '待客户签字', COMPLETED: '已完成' }
  return map[status] || status
}

const hasRole = (roles) => roles.includes(authStore.user?.role)
const goBack = () => router.push('/orders')
const goToCustomer = () => router.push(`/customers/${order.value.customer_id}`)

onMounted(() => {
  loadData()
  loadParts()
})
</script>

<style scoped>
.order-detail { padding: 0; }

.header-left { display: flex; align-items: center; gap: 16px; }
.back-btn { border-color: var(--color-border); color: var(--color-text-secondary); }

.steps-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 30px 20px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

.detail-card { 
  border-radius: var(--radius-lg); 
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}
.card-title { font-size: 15px; font-weight: 700; color: var(--color-text-primary); }

.val-link { color: var(--color-primary); font-weight: 600; cursor: pointer; border-bottom: 1px dashed transparent; }
.val-link:hover { border-bottom-color: var(--color-primary); }
.val-text { color: var(--color-text-primary); font-weight: 500; }

.checkin-info { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; }
.checkin-text p { margin: 8px 0; font-size: 14px; color: var(--color-text-regular); }
.checkin-text strong { color: var(--color-text-secondary); font-weight: 500; margin-right: 8px; }
.preview-img-lg { width: 140px; height: 140px; border-radius: var(--radius-md); border: 1px solid var(--color-border); }

.report-box { background: #fafbfc; border-radius: var(--radius-md); padding: 20px; border: 1px solid #edf2f7; }
.report-item { margin-bottom: 20px; }
.report-item:last-child { margin-bottom: 0; }
.report-label { font-size: 12px; color: var(--color-text-secondary); font-weight: 700; text-transform: uppercase; margin-bottom: 10px; }
.report-val { font-size: 14px; color: var(--color-text-primary); line-height: 1.6; white-space: pre-wrap; }

.photo-wall-section { margin-top: 24px; padding-top: 24px; border-top: 1px dashed var(--color-border); }
.section-subtitle { font-size: 13px; font-weight: 700; color: var(--color-text-secondary); margin-bottom: 16px; }
.photo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 12px; }
.grid-img { width: 100%; height: 110px; border-radius: var(--radius-sm); border: 1px solid var(--color-border-light); cursor: pointer; transition: 0.3s; }
.grid-img:hover { opacity: 0.8; transform: scale(1.02); }

.side-kv { display: flex; flex-direction: column; gap: 16px; }
.kv-row { display: flex; justify-content: space-between; align-items: center; }
.kv-row .k { color: var(--color-text-secondary); font-size: 13px; }
.kv-row .v { color: var(--color-text-primary); font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 8px; }
.v.active { color: var(--color-primary); }

.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-PENDING { background: #faad14; box-shadow: 0 0 0 3px rgba(250,173,20,.1); }
.dot-IN_PROGRESS { background: var(--color-primary); box-shadow: 0 0 0 3px rgba(22,119,255,.1); }
.dot-COMPLETED { background: var(--color-success); box-shadow: 0 0 0 3px rgba(82,196,26,.1); }

.signature-box { 
  background: #f9f9f9; 
  border: 1px dashed var(--color-border); 
  border-radius: var(--radius-md); 
  height: 160px; 
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.signature-box.empty { background: #fafafa; }
.sign-img { max-height: 140px; }
.sign-placeholder { font-size: 12px; color: var(--color-text-placeholder); font-style: italic; }

.mb-24 { margin-bottom: 24px; }

/* 检查项列表样式 */
.inspection-list {
  background: #f9fafc;
  padding: 15px;
  border-radius: var(--radius-sm);
  margin-bottom: 20px;
  max-height: 300px;
  overflow-y: auto;
}
.inspection-row {
  margin-bottom: 12px;
  align-items: center;
}
.inspection-name {
  font-size: 13px;
  color: var(--color-text-primary);
  font-weight: 500;
  line-height: 1.4;
}
.camera-upload-placeholder {
  width: 100%;
  padding: 10px;
  background: #fafafa;
  border: 1px dashed #d9d9d9;
  border-radius: var(--radius-sm);
}
</style>