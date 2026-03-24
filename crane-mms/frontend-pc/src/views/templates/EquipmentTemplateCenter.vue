<template>
  <div class="workspace-page template-center">
    <section class="workspace-hero">
      <div class="workspace-hero__body">
        <p class="workspace-kicker">Template Governance</p>
        <h2 class="workspace-title">设备模板、候选审核与检修基底统一维护</h2>
        <p class="workspace-description">
          模板中心负责正式模板版本、设备录入候选回流和检修通用模板，让新增设备从纯手填切换成推荐命中、确认应用、回流沉淀的闭环。
        </p>
        <div class="workspace-badges">
          <span class="soft-pill">模板组 {{ groups.length }}</span>
          <span class="soft-pill">待审候选 {{ candidates.length }}</span>
          <span class="soft-pill">检修基底 {{ baseTemplates.length }}</span>
        </div>
      </div>
      <div class="workspace-hero__aside">
        <div class="workspace-aside-card">
          <span class="workspace-aside-card__label">版本策略</span>
          <span class="workspace-aside-card__value">通用版 + 厂家版</span>
          <span class="workspace-aside-card__meta">按大类、型式、吨位与跨度规则命中设备模板</span>
        </div>
        <div class="workspace-actions hero-actions">
          <el-button @click="reloadAll" :loading="pageLoading">刷新</el-button>
          <el-button v-if="canManageGroups" type="primary" @click="openGroupDialog">新建模板组</el-button>
          <el-button v-if="canManageVersions" type="success" @click="openVersionDialog()">新建模板版本</el-button>
        </div>
      </div>
    </section>

    <section class="metrics-grid">
      <article v-for="item in summaryCards" :key="item.label" class="metric-tile">
        <div class="metric-label">{{ item.label }}</div>
        <div class="metric-value">{{ item.value }}</div>
        <div class="metric-footnote">{{ item.hint }}</div>
      </article>
    </section>

    <el-tabs v-model="activeTab">
      <el-tab-pane v-if="canViewTemplatesTab" label="设备模板" name="versions">
        <el-card shadow="never" class="panel-card">
          <div class="filter-bar">
            <el-select v-model="filters.category" placeholder="设备大类" clearable style="width: 150px">
              <el-option v-for="item in categories" :key="item" :label="item" :value="item" />
            </el-select>
            <el-select v-model="filters.modelType" placeholder="设备型式" clearable style="width: 150px">
              <el-option v-for="item in modelTypeOptions" :key="item" :label="item" :value="item" />
            </el-select>
            <el-input v-model="filters.manufacturer" placeholder="厂家搜索" clearable style="width: 180px" />
            <el-select v-model="filters.ruleType" placeholder="规则类型" clearable style="width: 150px">
              <el-option label="范围优先模板" value="RANGE" />
              <el-option label="精确模板" value="EXACT" />
            </el-select>
          </div>

          <el-table :data="filteredTemplateRows" v-loading="pageLoading" border stripe>
            <el-table-column label="模板组 / 版本" min-width="220">
              <template #default="{ row }">
                <div class="stack">
                  <strong>{{ row.name }}</strong>
                  <span class="muted">{{ row.groupName }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="适用设备" min-width="180">
              <template #default="{ row }">
                <div class="stack">
                  <span>{{ row.category }}</span>
                  <span class="muted">{{ row.model_type }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="厂家" width="140">
              <template #default="{ row }">
                <el-tag :type="row.manufacturer ? 'warning' : 'info'">{{ row.manufacturer || '通用版' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="匹配规则" min-width="210">
              <template #default="{ row }">
                <div class="stack">
                  <span>吨位: {{ formatRule(row.tonnage_rule_type, row.tonnage_exact, row.tonnage_min, row.tonnage_max) }}</span>
                  <span class="muted">跨度: {{ formatRule(row.span_rule_type, row.span_exact, row.span_min, row.span_max) }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="内容概览" width="170">
              <template #default="{ row }">
                <div class="stack small">
                  <span>{{ row.parts?.length || 0 }} 部件</span>
                  <span>{{ row.inspection_items?.length || 0 }} 检修项</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'info'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="openPreview(row)">预览</el-button>
                <el-button v-if="canManageVersions" link type="success" @click="openVersionDialog(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane v-if="canViewCandidatesTab" label="模板候选" name="candidates">
        <div class="candidate-layout">
          <el-card shadow="never" class="panel-card">
            <template #header>
              <div class="panel-header">
                <span>待审核候选</span>
                <el-tag type="warning">{{ candidates.length }} 条</el-tag>
              </div>
            </template>
            <el-table :data="candidates" highlight-current-row @current-change="handleCandidateSelect">
              <el-table-column prop="equipment_name" label="来源设备" min-width="140" />
              <el-table-column prop="status" label="状态" width="120" />
              <el-table-column label="差异数" width="90" align="center">
                <template #default="{ row }">{{ row.diff_summary?.length || 0 }}</template>
              </el-table-column>
            </el-table>
          </el-card>

          <el-card shadow="never" class="panel-card">
            <template #header>
              <div class="panel-header">
                <span>候选对比</span>
                <div v-if="selectedCandidate && canReviewCandidates" class="review-actions">
                  <el-button size="small" type="danger" plain @click="rejectCandidate(selectedCandidate)">驳回</el-button>
                  <el-button size="small" type="primary" @click="approveCandidate(selectedCandidate)">通过并生成新版本</el-button>
                </div>
              </div>
            </template>
            <el-empty v-if="!selectedCandidate" description="请选择左侧候选" />
            <div v-else class="candidate-detail">
              <div class="tag-list">
                <el-tag v-for="diff in selectedCandidate.diff_summary" :key="diff.field" type="warning" effect="plain">
                  {{ diff.field }} · {{ diff.change_type }}
                </el-tag>
              </div>
              <div class="compare-grid">
                <div class="compare-card">
                  <div class="compare-title">原模板</div>
                  <pre>{{ prettyJson(selectedCandidateSource ? selectedCandidateSource.inspection_items : { message: '无原模板' }) }}</pre>
                </div>
                <div class="compare-card emphasis">
                  <div class="compare-title">候选快照</div>
                  <pre>{{ prettyJson(selectedCandidate.snapshot) }}</pre>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane v-if="canViewBaseTemplatesTab" label="检修通用模板" name="bases">
        <el-card shadow="never" class="panel-card">
          <div class="filter-bar">
            <el-select v-model="baseFilters.category" placeholder="设备大类" clearable style="width: 150px">
              <el-option v-for="item in categories" :key="item" :label="item" :value="item" />
            </el-select>
            <el-select v-model="baseFilters.modelType" placeholder="设备型式" clearable style="width: 150px">
              <el-option v-for="item in modelTypeOptions" :key="item" :label="item" :value="item" />
            </el-select>
            <el-button v-if="canManageBaseTemplates" type="primary" @click="openBaseDialog()">新建检修通用模板</el-button>
          </div>
          <el-table :data="filteredBaseTemplates" border stripe>
            <el-table-column prop="name" label="模板名称" min-width="220" />
            <el-table-column label="适用范围" min-width="220">
              <template #default="{ row }">
                <div class="stack">
                  <span>{{ row.category }} / {{ row.model_type }}</span>
                  <span class="muted">吨位: {{ formatRule(row.tonnage_rule_type, row.tonnage_exact, row.tonnage_min, row.tonnage_max) }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="检修项数" width="100" align="center">
              <template #default="{ row }">{{ row.items?.length || 0 }}</template>
            </el-table-column>
            <el-table-column prop="note" label="备注" min-width="180" show-overflow-tooltip />
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button v-if="canManageBaseTemplates" link type="primary" @click="openBaseDialog(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="groupDialogVisible" title="新建模板组" width="500px">
      <el-form :model="groupForm" label-position="top">
        <el-form-item label="设备大类">
          <el-select v-model="groupForm.category" style="width: 100%">
            <el-option v-for="item in categories" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备型式">
          <el-select v-model="groupForm.model_type" style="width: 100%">
            <el-option v-for="item in modelTypeMap[groupForm.category] || []" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板组名称">
          <el-input v-model="groupForm.name" placeholder="例如：桥式起重机-QD 模板组" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="groupDialogVisible = false">取消</el-button>
        <el-button v-if="canManageGroups" type="primary" :loading="dialogLoading" @click="submitGroup">保存模板组</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="versionDialogVisible" :title="editingVersionId ? '编辑模板版本' : '新建模板版本'" width="920px">
      <div v-loading="versionDialogLoading">
        <el-form :model="versionForm" label-position="top">
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="模板组">
                <el-select v-model="versionForm.group_id" style="width: 100%">
                  <el-option v-for="group in groups" :key="group.id" :label="`${group.category} / ${group.model_type}`" :value="group.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="模板名称">
                <el-input v-model="versionForm.name" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="厂家版本">
                <el-input v-model="versionForm.manufacturer" placeholder="留空则为通用版" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <div class="rule-box">
                <div class="rule-title">吨位规则</div>
                <el-radio-group v-model="versionForm.tonnage_rule_type">
                  <el-radio value="EXACT">精确值</el-radio>
                  <el-radio value="RANGE">范围段</el-radio>
                </el-radio-group>
                <div v-if="versionForm.tonnage_rule_type === 'EXACT'" class="rule-row">
                  <el-input v-model="versionForm.tonnage_exact" placeholder="例: 10t" />
                </div>
                <div v-else class="rule-row dual">
                  <el-input-number v-model="versionForm.tonnage_min" :min="0" style="width: 100%" />
                  <span>至</span>
                  <el-input-number v-model="versionForm.tonnage_max" :min="0" style="width: 100%" />
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="rule-box">
                <div class="rule-title">跨度规则</div>
                <el-radio-group v-model="versionForm.span_rule_type">
                  <el-radio value="EXACT">精确值</el-radio>
                  <el-radio value="RANGE">范围段</el-radio>
                </el-radio-group>
                <div v-if="versionForm.span_rule_type === 'EXACT'" class="rule-row">
                  <el-input v-model="versionForm.span_exact" placeholder="例: 16.5m" />
                </div>
                <div v-else class="rule-row dual">
                  <el-input-number v-model="versionForm.span_min" :min="0" style="width: 100%" />
                  <span>至</span>
                  <el-input-number v-model="versionForm.span_max" :min="0" style="width: 100%" />
                </div>
              </div>
            </el-col>
          </el-row>

          <el-divider content-position="left">默认技术参数</el-divider>
          <el-row :gutter="16">
            <el-col :span="6"><el-input v-model="versionForm.default_params.tonnage" placeholder="默认吨位" /></el-col>
            <el-col :span="6"><el-input v-model="versionForm.default_params.span" placeholder="默认跨度" /></el-col>
            <el-col :span="6"><el-input v-model="versionForm.default_params.lifting_height" placeholder="起升高度" /></el-col>
            <el-col :span="6"><el-input v-model="versionForm.default_params.work_class" placeholder="工作级别" /></el-col>
          </el-row>
          <el-input v-model="versionForm.default_params.installation_location" placeholder="默认安装位置" style="margin-top: 12px" />

          <el-divider content-position="left">
            <span>核心部件清单</span>
            <el-button type="primary" link @click="addVersionPart">新增部件</el-button>
          </el-divider>
          <el-table :data="versionForm.parts" size="small" border>
            <el-table-column label="部件名称" min-width="160"><template #default="{ row }"><el-input v-model="row.part_name" /></template></el-table-column>
            <el-table-column label="规格参数" min-width="220"><template #default="{ row }"><el-input v-model="row.specification" /></template></el-table-column>
            <el-table-column label="数量" width="110"><template #default="{ row }"><el-input-number v-model="row.quantity" :min="1" style="width: 100%" /></template></el-table-column>
            <el-table-column width="80" align="center"><template #default="{ $index }"><el-button link type="danger" @click="removeVersionPart($index)">删除</el-button></template></el-table-column>
          </el-table>

          <el-divider content-position="left">
            <span>建议检修项</span>
            <div class="inline-actions">
              <el-select v-model="versionForm.base_template_id" placeholder="先选通用模板" style="width: 220px">
                <el-option v-for="item in baseTemplates" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
              <el-button @click="applyBaseTemplate">引用通用模板</el-button>
              <el-button type="primary" link @click="addVersionInspectionItem">新增检修项</el-button>
            </div>
          </el-divider>
          <el-table :data="versionForm.inspection_items" size="small" border>
            <el-table-column label="检修项" min-width="160"><template #default="{ row }"><el-input v-model="row.item_name" /></template></el-table-column>
            <el-table-column label="说明" min-width="240"><template #default="{ row }"><el-input v-model="row.description" /></template></el-table-column>
            <el-table-column label="必检" width="90" align="center"><template #default="{ row }"><el-switch v-model="row.required" /></template></el-table-column>
            <el-table-column width="80" align="center"><template #default="{ $index }"><el-button link type="danger" @click="removeVersionInspectionItem($index)">删除</el-button></template></el-table-column>
          </el-table>

          <el-form-item label="版本备注" style="margin-top: 14px">
            <el-input v-model="versionForm.version_note" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="versionDialogVisible = false">取消</el-button>
        <el-button v-if="canManageVersions" type="primary" :loading="dialogLoading" @click="submitVersion">保存模板版本</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="baseDialogVisible" :title="editingBaseId ? '编辑检修通用模板' : '新建检修通用模板'" width="860px">
      <el-form :model="baseForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="设备大类"><el-select v-model="baseForm.category" style="width: 100%"><el-option v-for="item in categories" :key="item" :label="item" :value="item" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="设备型式"><el-select v-model="baseForm.model_type" style="width: 100%"><el-option v-for="item in modelTypeMap[baseForm.category] || []" :key="item" :label="item" :value="item" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="模板名称"><el-input v-model="baseForm.name" /></el-form-item></el-col>
        </el-row>
        <div class="rule-box">
          <div class="rule-title">吨位规则</div>
          <el-radio-group v-model="baseForm.tonnage_rule_type">
            <el-radio value="EXACT">精确值</el-radio>
            <el-radio value="RANGE">范围段</el-radio>
          </el-radio-group>
          <div v-if="baseForm.tonnage_rule_type === 'EXACT'" class="rule-row"><el-input v-model="baseForm.tonnage_exact" placeholder="例: 10t" /></div>
          <div v-else class="rule-row dual"><el-input-number v-model="baseForm.tonnage_min" :min="0" style="width: 100%" /><span>至</span><el-input-number v-model="baseForm.tonnage_max" :min="0" style="width: 100%" /></div>
        </div>
        <el-divider content-position="left">
          <span>检修项清单</span>
          <el-button type="primary" link @click="addBaseInspectionItem">新增检修项</el-button>
        </el-divider>
        <el-table :data="baseForm.items" size="small" border>
          <el-table-column label="检修项" min-width="180"><template #default="{ row }"><el-input v-model="row.item_name" /></template></el-table-column>
          <el-table-column label="说明" min-width="260"><template #default="{ row }"><el-input v-model="row.description" /></template></el-table-column>
          <el-table-column label="必检" width="90" align="center"><template #default="{ row }"><el-switch v-model="row.required" /></template></el-table-column>
          <el-table-column width="80" align="center"><template #default="{ $index }"><el-button link type="danger" @click="removeBaseInspectionItem($index)">删除</el-button></template></el-table-column>
        </el-table>
        <el-form-item label="备注" style="margin-top: 14px"><el-input v-model="baseForm.note" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="baseDialogVisible = false">取消</el-button>
        <el-button v-if="canManageBaseTemplates" type="primary" :loading="dialogLoading" @click="submitBaseTemplate">保存检修通用模板</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewDialogVisible" title="模板预览" width="860px">
      <div v-if="previewVersion" class="compare-grid">
        <div class="compare-card emphasis"><div class="compare-title">默认参数</div><pre>{{ prettyJson(previewVersion.default_params) }}</pre></div>
        <div class="compare-card"><div class="compare-title">部件清单</div><pre>{{ prettyJson(previewVersion.parts) }}</pre></div>
        <div class="compare-card full"><div class="compare-title">建议检修项</div><pre>{{ prettyJson(previewVersion.inspection_items) }}</pre></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { SETTINGS_PERMISSIONS } from '@/constants/permissions'
import {
  approveEquipmentTemplateCandidate,
  createEquipmentTemplateGroup,
  createEquipmentTemplateVersion,
  createInspectionBaseTemplate,
  getEquipmentTemplateCandidates,
  getEquipmentTemplateGroups,
  getEquipmentTemplateVersion,
  getInspectionBaseTemplates,
  rejectEquipmentTemplateCandidate,
  updateEquipmentTemplateVersion,
  updateInspectionBaseTemplate
} from '@/api/equipmentTemplate'

const authStore = useAuthStore()

const categories = ['桥式起重机', '门式起重机', '悬臂起重机']
const modelTypeMap = {
  '桥式起重机': ['QD型', 'LDA型', 'LH型', 'QZ型'],
  '门式起重机': ['MH型', 'MG型', 'BMH型'],
  '悬臂起重机': ['BZ型', 'BZD型']
}

const activeTab = ref('versions')
const pageLoading = ref(false)
const dialogLoading = ref(false)
const versionDialogLoading = ref(false)
const groups = ref([])
const candidates = ref([])
const baseTemplates = ref([])
const selectedCandidate = ref(null)
const selectedCandidateSource = ref(null)
const previewVersion = ref(null)
const groupDialogVisible = ref(false)
const versionDialogVisible = ref(false)
const baseDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const editingVersionId = ref(null)
const editingBaseId = ref(null)

const filters = reactive({ category: '', modelType: '', manufacturer: '', ruleType: '' })
const baseFilters = reactive({ category: '', modelType: '' })
const groupForm = reactive({ category: '桥式起重机', model_type: '', name: '' })
const versionForm = reactive(createVersionForm())
const baseForm = reactive(createBaseForm())

const canManageGroups = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_GROUP_MANAGE))
const canManageVersions = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_VERSION_MANAGE))
const canManageBaseTemplates = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_BASE_TEMPLATE_MANAGE))
const canReviewCandidates = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_CANDIDATES_REVIEW))
const canViewTemplatesTab = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_MODULE_TEMPLATES))
const canViewCandidatesTab = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_MODULE_CANDIDATES))
const canViewBaseTemplatesTab = computed(() => authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_MODULE_BASE_TEMPLATES))

function createVersionForm() {
  return {
    group_id: null,
    name: '',
    manufacturer: '',
    tonnage_rule_type: 'RANGE',
    tonnage_exact: '',
    tonnage_min: 0,
    tonnage_max: 0,
    span_rule_type: 'RANGE',
    span_exact: '',
    span_min: 0,
    span_max: 0,
    default_params: { tonnage: '', span: '', lifting_height: '', work_class: 'A5', installation_location: '' },
    parts: [],
    inspection_items: [],
    version_note: '',
    base_template_id: null
  }
}

function createBaseForm() {
  return { category: '桥式起重机', model_type: '', name: '', tonnage_rule_type: 'EXACT', tonnage_exact: '', tonnage_min: 0, tonnage_max: 0, items: [], note: '' }
}

const modelTypeOptions = computed(() => [...new Set(Object.values(modelTypeMap).flat())])
const templateRows = computed(() => groups.value.flatMap(group => (group.active_versions || []).map(version => ({ ...version, groupName: group.name, category: group.category, model_type: group.model_type }))))
const summaryCards = computed(() => [
  {
    label: '模板组',
    value: groups.value.length,
    hint: '按设备大类与型式组织的模板集合'
  },
  {
    label: '生效版本',
    value: templateRows.value.length,
    hint: '当前可用于设备匹配的正式模板版本'
  },
  {
    label: '待审候选',
    value: candidates.value.length,
    hint: '来自设备录入回流、等待审核的新模板候选'
  },
  {
    label: '检修基底',
    value: baseTemplates.value.length,
    hint: '可在模板编辑中一键引用的检修通用模板'
  }
])

const filteredTemplateRows = computed(() => templateRows.value.filter(row => {
  if (filters.category && row.category !== filters.category) return false
  if (filters.modelType && row.model_type !== filters.modelType) return false
  if (filters.manufacturer && !(row.manufacturer || '通用版').toLowerCase().includes(filters.manufacturer.toLowerCase())) return false
  if (filters.ruleType === 'RANGE' && !(row.tonnage_rule_type === 'RANGE' || row.span_rule_type === 'RANGE')) return false
  if (filters.ruleType === 'EXACT' && !(row.tonnage_rule_type === 'EXACT' && row.span_rule_type === 'EXACT')) return false
  return true
}))

const filteredBaseTemplates = computed(() => baseTemplates.value.filter(row => (!baseFilters.category || row.category === baseFilters.category) && (!baseFilters.modelType || row.model_type === baseFilters.modelType)))

const loadGroups = async () => {
  if (!canViewTemplatesTab.value) {
    groups.value = []
    return
  }
  groups.value = await getEquipmentTemplateGroups()
}
const loadCandidates = async () => {
  if (!canViewCandidatesTab.value) {
    candidates.value = []
    selectedCandidate.value = null
    return
  }
  candidates.value = await getEquipmentTemplateCandidates()
  selectedCandidate.value = candidates.value[0] || null
}
const loadBaseTemplates = async () => {
  if (!canViewBaseTemplatesTab.value) {
    baseTemplates.value = []
    return
  }
  baseTemplates.value = await getInspectionBaseTemplates()
}

const reloadAll = async () => {
  pageLoading.value = true
  try {
    await Promise.all([loadGroups(), loadCandidates(), loadBaseTemplates()])
    syncActiveTab()
  } catch (error) {
    ElMessage.error(error.message || '加载模板中心数据失败')
  } finally {
    pageLoading.value = false
  }
}

const syncActiveTab = () => {
  if (activeTab.value === 'candidates' && !canViewCandidatesTab.value) {
    activeTab.value = canViewTemplatesTab.value ? 'versions' : 'bases'
  }
  if (activeTab.value === 'bases' && !canViewBaseTemplatesTab.value) {
    activeTab.value = canViewTemplatesTab.value ? 'versions' : 'candidates'
  }
  if (activeTab.value === 'versions' && !canViewTemplatesTab.value) {
    activeTab.value = canViewCandidatesTab.value ? 'candidates' : 'bases'
  }
}

const openGroupDialog = () => {
  groupForm.category = '桥式起重机'
  groupForm.model_type = ''
  groupForm.name = ''
  groupDialogVisible.value = true
}

const openVersionDialog = async (row = null) => {
  Object.assign(versionForm, createVersionForm())
  editingVersionId.value = null
  versionDialogVisible.value = true
  if (!row) return
  editingVersionId.value = row.id
  versionDialogLoading.value = true
  try {
    const detail = await getEquipmentTemplateVersion(row.id)
    Object.assign(versionForm, { ...detail, manufacturer: detail.manufacturer || '', parts: detail.parts || [], inspection_items: detail.inspection_items || [], default_params: { tonnage: '', span: '', lifting_height: '', work_class: 'A5', installation_location: '', ...(detail.default_params || {}) } })
  } catch (error) {
    ElMessage.error(error.message || '加载模板版本失败')
  } finally {
    versionDialogLoading.value = false
  }
}

const openBaseDialog = (row = null) => {
  Object.assign(baseForm, createBaseForm())
  editingBaseId.value = null
  if (row) {
    editingBaseId.value = row.id
    Object.assign(baseForm, JSON.parse(JSON.stringify(row)))
  }
  baseDialogVisible.value = true
}

const openPreview = async (row) => {
  try {
    previewVersion.value = await getEquipmentTemplateVersion(row.id)
    previewDialogVisible.value = true
  } catch (error) {
    ElMessage.error(error.message || '加载模板预览失败')
  }
}

const submitGroup = async () => {
  if (!groupForm.category || !groupForm.model_type || !groupForm.name) return ElMessage.warning('请完整填写模板组信息')
  dialogLoading.value = true
  try {
    const created = await createEquipmentTemplateGroup(groupForm)
    versionForm.group_id = created.id
    groupDialogVisible.value = false
    ElMessage.success('模板组已创建')
    await loadGroups()
  } catch (error) {
    ElMessage.error(error.message || '创建模板组失败')
  } finally {
    dialogLoading.value = false
  }
}

const submitVersion = async () => {
  if (!versionForm.group_id || !versionForm.name) return ElMessage.warning('请先选择模板组并填写模板名称')
  dialogLoading.value = true
  try {
    const payload = JSON.parse(JSON.stringify(versionForm))
    if (editingVersionId.value) {
      await updateEquipmentTemplateVersion(editingVersionId.value, payload)
      ElMessage.success('模板版本已更新')
    } else {
      await createEquipmentTemplateVersion(payload)
      ElMessage.success('模板版本已创建')
    }
    versionDialogVisible.value = false
    await loadGroups()
  } catch (error) {
    ElMessage.error(error.message || '保存模板版本失败')
  } finally {
    dialogLoading.value = false
  }
}

const submitBaseTemplate = async () => {
  if (!baseForm.category || !baseForm.model_type || !baseForm.name) return ElMessage.warning('请完整填写检修通用模板')
  dialogLoading.value = true
  try {
    const payload = JSON.parse(JSON.stringify(baseForm))
    if (editingBaseId.value) {
      await updateInspectionBaseTemplate(editingBaseId.value, payload)
      ElMessage.success('检修通用模板已更新')
    } else {
      await createInspectionBaseTemplate(payload)
      ElMessage.success('检修通用模板已创建')
    }
    baseDialogVisible.value = false
    await loadBaseTemplates()
  } catch (error) {
    ElMessage.error(error.message || '保存检修通用模板失败')
  } finally {
    dialogLoading.value = false
  }
}

const addVersionPart = () => versionForm.parts.push({ part_name: '', specification: '', quantity: 1 })
const removeVersionPart = (index) => versionForm.parts.splice(index, 1)
const addVersionInspectionItem = () => versionForm.inspection_items.push({ item_name: '', description: '', required: true })
const removeVersionInspectionItem = (index) => versionForm.inspection_items.splice(index, 1)
const addBaseInspectionItem = () => baseForm.items.push({ item_name: '', description: '', required: true })
const removeBaseInspectionItem = (index) => baseForm.items.splice(index, 1)
const handleCandidateSelect = (row) => { selectedCandidate.value = row }

const applyBaseTemplate = () => {
  const matched = baseTemplates.value.find(item => item.id === versionForm.base_template_id)
  if (!matched) return ElMessage.warning('请先选择检修通用模板')
  versionForm.inspection_items = JSON.parse(JSON.stringify(matched.items || []))
  ElMessage.success('已引用检修通用模板')
}

watch(selectedCandidate, async (value) => {
  if (!value?.source_template_version_id) {
    selectedCandidateSource.value = null
    return
  }
  try {
    selectedCandidateSource.value = await getEquipmentTemplateVersion(value.source_template_version_id)
  } catch {
    selectedCandidateSource.value = null
  }
})

watch([canViewTemplatesTab, canViewCandidatesTab, canViewBaseTemplatesTab], syncActiveTab)

const approveCandidate = async (candidate) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入审核备注（可选）', '通过候选', { confirmButtonText: '通过', cancelButtonText: '取消' })
    await approveEquipmentTemplateCandidate(candidate.id, { review_note: value || '' })
    ElMessage.success('候选已通过')
    await reloadAll()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(error.message || '审核失败')
  }
}

const rejectCandidate = async (candidate) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因（可选）', '驳回候选', { confirmButtonText: '驳回', cancelButtonText: '取消' })
    await rejectEquipmentTemplateCandidate(candidate.id, { review_note: value || '' })
    ElMessage.success('候选已驳回')
    await reloadAll()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(error.message || '驳回失败')
  }
}

const formatRule = (ruleType, exact, min, max) => ruleType === 'EXACT' ? (exact || '未设置') : `${min ?? 0} - ${max ?? 0}`
const prettyJson = (value) => JSON.stringify(value || {}, null, 2)

onMounted(reloadAll)
</script>

<style scoped>
.template-center {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero-actions,
.filter-bar,
.review-actions,
.inline-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.template-center :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.template-center :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.template-center :deep(.el-tabs__item) {
  min-height: 42px;
  border-radius: 999px;
  color: var(--color-text-secondary);
  font-weight: 700;
}

.template-center :deep(.el-tabs__item.is-active) {
  color: var(--color-primary-dark);
}

.template-center :deep(.el-tabs__active-bar) {
  height: 32px;
  border-radius: 999px;
  background: rgba(47, 137, 255, 0.1);
  bottom: 5px;
}

.panel-card { border-radius: 28px; border: 1px solid rgba(16,33,48,.08); box-shadow: 0 16px 30px rgba(18,31,45,.04); }
.stack { display: flex; flex-direction: column; gap: 6px; }
.small { font-size: 12px; }
.muted { font-size: 12px; color: var(--color-text-secondary); }
.candidate-layout, .compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; font-weight: 700; }
.candidate-detail, .tag-list { display: flex; flex-direction: column; gap: 14px; }
.tag-list { flex-direction: row; flex-wrap: wrap; }
.compare-card { padding: 16px; border-radius: 18px; background: rgba(247,250,252,.92); border: 1px solid rgba(16,33,48,.08); }
.compare-card.emphasis { background: linear-gradient(180deg, rgba(231,245,255,.95), rgba(247,251,255,.96)); }
.compare-card.full { grid-column: 1 / -1; }
.compare-title, .rule-title { font-weight: 700; margin-bottom: 10px; color: var(--color-text-primary); }
.rule-box { padding: 16px; border-radius: 18px; background: rgba(247,250,252,.92); border: 1px solid rgba(16,33,48,.08); }
.rule-row { margin-top: 14px; }
.rule-row.dual { display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; align-items: center; }
pre { margin: 0; padding: 12px 14px; border-radius: 14px; background: rgba(15,23,42,.9); color: #eaf4ff; font-size: 12px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
@media (max-width: 1200px) { .candidate-layout, .compare-grid { grid-template-columns: 1fr; } }
</style>
