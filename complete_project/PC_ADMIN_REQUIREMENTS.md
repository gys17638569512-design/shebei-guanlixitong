# PC 管理后台 — 全功能开发需求文档
> 直接粘贴给 Cursor AI 使用。开发前请先读取 `.cursorrules` 文件。

---

## 一、项目定位

**系统名称**：智能起重机维保管理系统 · PC 管理后台
**使用人群**：老郭（ADMIN）、业务经理（MANAGER）、内勤文员（MANAGER）
**核心目标**：在电脑上完成客户/设备建档、工单派发、进度监控、报告交付的全流程闭环
**视觉风格**：简洁浅色系，白底 + 主色 `#2979FF`，基于 Element Plus 默认组件，干净专业

---

## 二、技术栈（不可更改）

| 项 | 技术 |
|----|------|
| 框架 | Vue 3 + `<script setup>` Composition API |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| HTTP | Axios（已封装在 `src/utils/request.js`） |
| 构建 | Vite |
| 后端接口 | `http://localhost:8000/api/v1` |

---

## 三、目录结构（严格遵守）

```
frontend-pc/src/
├── api/                  # 所有后端接口调用，按模块分文件
│   ├── auth.js
│   ├── customer.js
│   ├── equipment.js
│   ├── order.js
│   ├── template.js       # 检查模板接口
│   ├── user.js
│   ├── stats.js
│   └── report.js
├── stores/
│   └── auth.js           # 用户登录态 Pinia store
├── utils/
│   └── request.js        # Axios 封装（已有，勿重复创建）
├── router/
│   └── index.js          # 路由配置 + 权限守卫
├── views/
│   ├── LoginView.vue
│   ├── Dashboard.vue              # 首页看板
│   ├── layout/
│   │   └── AppLayout.vue          # 整体框架（侧边栏+顶栏+内容区）
│   ├── customers/
│   │   ├── CustomerList.vue       # 客户列表
│   │   └── CustomerDetail.vue     # 客户详情+设备列表
│   ├── equipments/
│   │   ├── EquipmentList.vue      # 设备列表
│   │   └── EquipmentForm.vue      # 新建/编辑设备
│   ├── orders/
│   │   ├── OrderList.vue          # 工单中心
│   │   ├── OrderDetail.vue        # 工单详情
│   │   └── BatchSchedule.vue      # 批量排期
│   ├── templates/
│   │   └── TemplateList.vue       # 检查模板管理
│   └── system/
│       ├── UserList.vue           # 用户管理
│       └── AuditLog.vue           # 操作日志
└── components/
    └── SignaturePreview.vue        # 签名图预览组件（复用）
```

---

## 四、全局基础设施

### 4.1 `src/utils/request.js`（如不存在则创建）

```javascript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const request = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 15000,
})

// 请求拦截：自动携带 Token
request.interceptors.request.use(config => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// 响应拦截：统一处理错误
request.interceptors.response.use(
  res => {
    const data = res.data
    if (data.code !== 200) {
      ElMessage.error(data.msg || '操作失败')
      return Promise.reject(data)
    }
    return data.data  // 直接返回 data 字段，调用方无需 res.data.data
  },
  err => {
    if (err.response?.status === 401) {
      useAuthStore().logout()
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else if (err.response?.status === 403) {
      ElMessage.error('权限不足')
    } else {
      ElMessage.error(err.response?.data?.msg || '网络错误，请重试')
    }
    return Promise.reject(err)
  }
)

export default request
```

### 4.2 `src/stores/auth.js`

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAdmin = computed(() => user.value?.role === 'ADMIN')
  const isManager = computed(() => ['ADMIN', 'MANAGER'].includes(user.value?.role))

  async function login(username, password) {
    // 后端 login 接口用 form data
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const res = await request.post('/auth/login', formData)
    token.value = res.access_token
    user.value = res.user || { username, role: res.role }
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isAdmin, isManager, login, logout }
})
```

### 4.3 `src/router/index.js`

路由守卫规则：
- 未登录 → 强制跳转 `/login`
- TECH 角色 → 无权访问 PC 后台，跳转登录页并提示"请使用手机端操作"
- MANAGER 角色 → 不显示「用户管理」「操作日志」菜单，访问时显示 403

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/views/layout/AppLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'customers', component: () => import('@/views/customers/CustomerList.vue') },
      { path: 'customers/:id', component: () => import('@/views/customers/CustomerDetail.vue') },
      { path: 'equipments', component: () => import('@/views/equipments/EquipmentList.vue') },
      { path: 'equipments/new', component: () => import('@/views/equipments/EquipmentForm.vue') },
      { path: 'equipments/:id/edit', component: () => import('@/views/equipments/EquipmentForm.vue') },
      { path: 'orders', component: () => import('@/views/orders/OrderList.vue') },
      { path: 'orders/batch', component: () => import('@/views/orders/BatchSchedule.vue') },
      { path: 'orders/:id', component: () => import('@/views/orders/OrderDetail.vue') },
      { path: 'templates', component: () => import('@/views/templates/TemplateList.vue'), meta: { adminOnly: true } },
      { path: 'system/users', component: () => import('@/views/system/UserList.vue'), meta: { adminOnly: true } },
      { path: 'system/audit', component: () => import('@/views/system/AuditLog.vue'), meta: { adminOnly: true } },
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.token) return next('/login')
  if (auth.user?.role === 'TECH') {
    auth.logout()
    return next('/login')
  }
  if (to.meta.adminOnly && !auth.isAdmin) return next('/dashboard')
  next()
})

export default router
```

---

## 五、页面详细需求

---

### 5.1 登录页 `LoginView.vue`

**布局**：左侧占 55% 放品牌区（系统名称 + Slogan + 背景图），右侧占 45% 放登录表单

**登录表单**：
- 账号输入框（图标：el-icon-User）
- 密码输入框（图标：el-icon-Lock，支持显示/隐藏密码）
- 登录按钮（`width: 100%`，主色，加载态）
- 回车键触发登录

**交互**：
- 登录成功 → 跳转 `/dashboard`
- 登录失败 → 表单下方显示红色错误提示（不用 ElMessage，直接行内显示）

---

### 5.2 整体布局 `AppLayout.vue`

**结构**：
```
┌─────────────────────────────────────────────┐
│  顶栏（固定，64px）                          │
├──────────┬──────────────────────────────────┤
│          │                                  │
│ 侧边栏   │    主内容区（router-view）        │
│ (220px)  │                                  │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

**侧边栏菜单**（按角色显示）：

```
📊 工作台
─────────
📋 工单中心
  ├── 全部工单
  └── 批量排期
─────────
👥 客户管理
🏗️ 设备档案
─────────
📝 检查模板          （仅 ADMIN 可见）
─────────
⚙️ 系统设置
  ├── 用户管理        （仅 ADMIN 可见）
  └── 操作日志        （仅 ADMIN 可见）
```

**顶栏**：
- 左侧：收缩/展开侧边栏按钮 + 面包屑导航
- 右侧：当前用户姓名 + 角色标签 + 退出登录下拉

**侧边栏收缩**：点击按钮折叠为图标模式（64px），hover 显示 tooltip

---

### 5.3 工作台首页 `Dashboard.vue`

**顶部数字卡片**（4个，一行排列）：

| 卡片 | 数据来源 | 颜色 |
|------|----------|------|
| 本月完工工单 | stats API | 蓝色 |
| 待处理工单 | stats API | 橙色 |
| 进行中工单 | stats API | 绿色 |
| 设备总数 | stats API | 紫色 |

**中部两栏**：
- 左侧（60%）：近 7 日工单趋势折线图（使用 echarts 或 element-plus 的图表）
- 右侧（40%）：设备类型分布饼图

**底部**：系统通知列表（设备临期预警 + 库存告警），每条显示级别图标（危险/警告）、内容、日期，点击跳转对应页面

**数据接口**：`GET /api/v1/stats/dashboard` + `GET /api/v1/stats/notifications`

> 图表使用 ECharts，安装：`npm install echarts`，按需引入

---

### 5.4 客户列表 `CustomerList.vue`

**顶部操作栏**：
- 搜索框（按公司名或联系人模糊搜索，输入 300ms 防抖后自动搜索）
- 「新建客户」按钮（右对齐）

**表格列**：
| 列 | 说明 |
|----|------|
| 公司名称 | 可点击，跳转详情页 |
| 主联系人 | 姓名 |
| 联系电话 | |
| 地址 | 超长省略，hover 显示 tooltip |
| 设备数量 | 数字徽标 |
| 操作 | 编辑、删除（删除需二次确认弹窗） |

**新建/编辑客户**：使用 `ElDrawer`（右侧抽屉），宽度 `520px`

抽屉表单字段：
- 公司名称（必填）
- 地址（必填）
- 联系人列表（动态增减行，至少一条）：
  - 姓名（必填）
  - 手机号（必填，11位校验）
  - 职位（选填）
  - 是否主联系人（单选，只能一个为主）
- 客户门户登录手机号（选填，用于客户自助登录）

---

### 5.5 客户详情 `CustomerDetail.vue`

**布局**：上方客户信息卡片 + 下方该客户名下的设备表格

**客户信息卡片**：
- 显示公司名、地址、所有联系人（带职位）
- 右上角「编辑」按钮（复用新建抽屉）

**名下设备表格**：
- 列：设备名称、大类、型号、安装位置、下次特检日期（临期高亮）、操作
- 操作：「查看详情」「新建工单」
- 表格右上角「新增设备」按钮（跳转 EquipmentForm，自动带入 customer_id）

---

### 5.6 设备表单 `EquipmentForm.vue`（新建/编辑通用）

**表单字段**（分三个分组用 ElDivider 分隔）：

**基础信息**：
- 所属客户（下拉搜索，必填）
- 设备名称（必填）
- 设备大类（下拉：桥式起重机 / 门式起重机 / 悬臂起重机，必填）
- 型式（联动大类，桥式→单梁/双梁，门式→通用/半门，悬臂→柱式/壁挂）

**技术参数**：
- 额定吨位（必填，单位 t）
- 跨度（必填，单位 m）
- 起升高度（必填，单位 m）
- 工作级别（下拉：A1~A8）
- 安装位置（文本，必填）

**档案信息**：
- 上次特检日期（日期选择器）
- 下次特检日期（日期选择器，自动提示距今天数）
- 质保到期日（日期选择器）

**部件清单**（可编辑表格）：
- 「智能填充」按钮：调用 `GET /equipments/templates?category=&model_type=` 自动填入部件清单
- 支持手动增行、删行、编辑每行的部件名称/规格/数量

---

### 5.7 设备列表 `EquipmentList.vue`

**顶部**：搜索框（按名称/客户名）+ 大类筛选下拉 + 「新增设备」按钮

**表格列**：设备名称、所属客户、大类、吨位、安装位置、下次特检日期（临期 30 天内橙色高亮，已过期红色高亮）、操作（编辑/删除）

---

### 5.8 工单中心 `OrderList.vue`

**顶部 Tab 快速筛选**（使用 `ElTabs`）：
- 全部 / 待处理 / 进行中 / 待签字 / 已完成

**高级筛选栏**（可折叠）：
- 客户名（下拉搜索）
- 工程师（下拉）
- 工单类型（月检/季检/年检/临时维保）
- 计划日期范围（日期区间选择器）

**表格列**：
| 列 | 说明 |
|----|------|
| 工单编号 | #ORD-000001 格式 |
| 客户名称 | |
| 设备名称 | |
| 工单类型 | 标签样式 |
| 负责工程师 | |
| 计划日期 | 已逾期未完成的日期显示红色 |
| 状态 | 彩色标签：待处理=橙/进行中=蓝/待签字=红/已完成=绿 |
| 操作 | 「详情」按钮 |

**顶部右侧**：
- 「新建派单」按钮 → 弹出 ElDialog
- 「批量排期」按钮 → 跳转 `/orders/batch`

**新建派单弹窗**：
- 选择客户（下拉搜索）
- 选择设备（联动客户，只显示该客户名下设备）
- 工单类型（下拉）
- 指派工程师（只显示 TECH 角色用户）
- 计划日期（日期选择器，不能选今天之前）
- 提交按钮 + loading 态

---

### 5.9 工单详情 `OrderDetail.vue`

**整体布局**：左侧主内容（70%）+ 右侧时间线（30%）

#### 左侧主内容（从上到下）：

**工单基础信息卡**：
- 工单编号、状态（彩色徽标）、工单类型、计划日期
- 客户名称（可点击跳转客户详情）
- 设备名称（可点击跳转设备详情）
- 负责工程师

**打卡记录卡**（已打卡时显示）：
- 打卡时间、打卡地址
- 打卡照片（`ElImage` 组件，支持点击预览大图）

**检查结果卡**（已提交检查时显示）：
- 表格展示：检查项 / 结果（正常✓ 用绿色，异常✗ 用红色）/ 异常备注 / 异常照片
- 照片点击可预览

**现场照片墙**（已上传照片时显示）：
- 3列瀑布流排列，点击预览

**客户签名**（已签名时显示）：
- 显示签名图片 + 签名时间

**报告区域**（已完成时显示）：
- PDF 状态：生成中 / 已生成
- 「下载 PDF 报告」按钮（a 标签直接打开 pdf_report_url）
- e 签宝认证编号（如有）

#### 右侧时间线：

使用 `ElTimeline` 组件，显示工单全过程节点：

```
● 工单创建      2024-03-10 09:00  by 老郭
● 现场打卡      2024-03-10 14:23  地址：上海市...
● 提交检查      2024-03-10 16:45  共 8 项检查
● 客户签字      2024-03-10 17:02
● PDF 生成完成  2024-03-10 17:03
```

#### 操作按钮区（根据状态显示不同按钮）：

| 工单状态 | 可用操作 | 权限 |
|----------|----------|------|
| 待处理 | 转派工程师、强制改期、手动作废 | ADMIN / MANAGER |
| 进行中 | 转派工程师、手动作废 | ADMIN |
| 待签字 | 手动作废 | ADMIN |
| 已完成 | 下载 PDF、重发邮件通知（如有邮箱） | 全部 |
| 已作废 | 无操作 | — |

**转派弹窗**：选择新工程师（下拉）+ 备注（选填）→ 调用 `PUT /orders/{id}/reassign`

**强制改期弹窗**：选择新日期 + 必填备注 → 调用 `PUT /orders/{id}/reschedule`

**手动作废弹窗**：必须填写作废原因（不少于10字）→ 调用 `PUT /orders/{id}/cancel`，此操作需二次确认（ElMessageBox）

---

### 5.10 批量排期 `BatchSchedule.vue`

**页面说明**：一次性给多台设备安排一个月的维保计划

**操作流程**：

**第一步：选择设备**
- 左侧：设备多选表格（支持按客户筛选，勾选后加入右侧列表）
- 右侧：已选设备列表（可移除）

**第二步：配置计划**
- 工单类型（统一设置）
- 每台设备单独选择：
  - 负责工程师（下拉）
  - 计划日期（日期选择器）
- 「复制到全部」快捷按钮（将第一行的工程师/日期批量应用到所有设备）

**第三步：提交**
- 预览汇总表（X 台设备，X 个工单）
- 提交调用 `POST /orders/batch`
- 返回结果显示：成功创建 X 条，跳过 X 条（已有工单）

---

### 5.11 检查模板管理 `TemplateList.vue`（仅 ADMIN）

**列表页**：
- 表格列：模板名称、适用设备大类、当前版本号、检查项数量、状态（启用/禁用）、操作
- 「新建模板」按钮

**新建/编辑模板**：使用整页抽屉（`ElDrawer`，宽 700px）

抽屉内容：
- 模板名称（必填）
- 适用设备大类（下拉）
- 检查项列表（可拖拽排序，可增删）：
  - 每行：序号 / 检查项名称 / 是否必填（开关）/ 删除按钮
  - 底部「添加检查项」按钮

**版本管理逻辑**：
- 编辑并保存已有模板 → 自动新建版本（version+1），旧版本标记为历史
- 页面提示："保存后将生成 V{n+1} 版本，已派发工单不受影响"
- 可查看历史版本列表（只读）

**接口**：
- `GET /api/v1/templates` — 列表
- `POST /api/v1/templates` — 新建
- `PUT /api/v1/templates/{id}` — 更新（后端自动版本迭代）
- `GET /api/v1/templates/{id}/versions` — 历史版本列表（只读展示）

---

### 5.12 用户管理 `UserList.vue`（仅 ADMIN）

**表格列**：用户名、姓名、角色（标签）、手机号、状态（启用/禁用）、操作（编辑/重置密码）

**新建/编辑用户**：ElDialog 表单
- 用户名（新建必填，编辑不可改）
- 姓名（必填）
- 角色（下拉：管理员/经理/工程师）
- 手机号（选填）
- 所属经理（仅工程师角色显示，下拉选择 MANAGER）

**重置密码**：弹出确认框，输入新密码（调用 `PUT /api/v1/users/{id}/password`）

---

### 5.13 操作日志 `AuditLog.vue`（仅 ADMIN）

**筛选栏**：操作人（下拉）+ 操作类型（CREATE/UPDATE/DELETE）+ 日期范围

**表格列**：操作时间、操作人、操作类型（彩色标签）、涉及表名、记录 ID、变更内容（JSON 格式，可展开查看）

**无需分页，一次加载最近 200 条**

---

## 六、通用 UI 规范

### 颜色系统（CSS 变量写在 `src/main.css`）：
```css
:root {
  --color-primary: #2979FF;
  --color-success: #67C23A;
  --color-warning: #E6A23C;
  --color-danger:  #F56C6C;
  --color-info:    #909399;
  --bg-page:       #F5F7FA;
  --bg-card:       #FFFFFF;
  --border-color:  #EBEEF5;
  --text-primary:  #303133;
  --text-regular:  #606266;
  --text-secondary:#909399;
}
```

### 工单状态标签颜色（全局统一）：
| 状态 | 文字 | 背景 |
|------|------|------|
| 待处理 PENDING | `#E6A23C` | `#FDF6EC` |
| 进行中 IN_PROGRESS | `#2979FF` | `#EBF2FF` |
| 待签字 PENDING_SIGN | `#F56C6C` | `#FEF0F0` |
| 已完成 COMPLETED | `#67C23A` | `#F0F9EB` |
| 已作废 CANCELLED | `#909399` | `#F4F4F5` |

### 通用交互原则：
- 所有表格需要 loading 骨架屏（`v-loading` 指令）
- 所有写操作（创建/更新/删除）完成后自动刷新当前列表
- 删除操作统一使用 `ElMessageBox.confirm` 二次确认
- 表格空数据时显示 Element Plus 的 `el-empty` 组件
- 操作成功统一使用 `ElMessage.success('xxx成功')`
- 列表页所有筛选条件改变自动触发搜索（防抖 300ms），无需手动点「查询」按钮

---

## 七、API 对应关系速查

| 页面操作 | 接口 | 方法 |
|----------|------|------|
| 登录 | `/auth/login` | POST（form-data） |
| 获取当前用户 | `/auth/me` | GET |
| 客户列表 | `/customers?search=` | GET |
| 新建客户 | `/customers` | POST |
| 客户详情 | `/customers/{id}` | GET |
| 更新客户 | `/customers/{id}` | PUT |
| 删除客户 | `/customers/{id}` | DELETE |
| 客户名下设备 | `/customers/{id}/equipments` | GET |
| 设备列表 | `/equipments?search=` | GET |
| 设备BOM模板 | `/equipments/templates` | GET |
| 新建设备 | `/equipments` | POST |
| 更新设备 | `/equipments/{id}` | PUT |
| 删除设备 | `/equipments/{id}` | DELETE |
| 工单列表 | `/orders?status=&customer_id=&technician_id=` | GET |
| 新建工单 | `/orders` | POST |
| 批量排期 | `/orders/batch` | POST |
| 工单详情 | `/orders/{id}` | GET |
| 转派工单 | `/orders/{id}/reassign` | PUT |
| 强制改期 | `/orders/{id}/reschedule` | PUT |
| 手动作废 | `/orders/{id}/cancel` | PUT |
| 下载报告 | 直接打开 pdf_report_url | — |
| 检查模板列表 | `/templates` | GET |
| 新建模板 | `/templates` | POST |
| 更新模板 | `/templates/{id}` | PUT |
| 用户列表 | `/users` | GET |
| 新建用户 | `/users` | POST |
| 更新用户 | `/users/{id}` | PUT |
| 重置密码 | `/users/{id}/password` | PUT |
| 操作日志 | `/audit-logs` | GET |
| 首页看板 | `/stats/dashboard` | GET |
| 系统通知 | `/stats/notifications` | GET |

---

## 八、开发顺序建议

Cursor AI 请按以下顺序开发，每完成一个页面在浏览器验证后再开始下一个：

1. **基础设施**：`request.js` + `auth store` + `router` + `AppLayout.vue`
2. **登录页** `LoginView.vue`
3. **首页看板** `Dashboard.vue`（先用静态假数据，后接口）
4. **客户管理**：`CustomerList.vue` → `CustomerDetail.vue`
5. **设备档案**：`EquipmentList.vue` → `EquipmentForm.vue`
6. **工单中心**：`OrderList.vue` → `OrderDetail.vue`
7. **批量排期** `BatchSchedule.vue`
8. **检查模板** `TemplateList.vue`
9. **系统管理**：`UserList.vue` → `AuditLog.vue`

---

## 九、启动和验证

```bash
cd crane-mms/frontend-pc
npm install
npm run dev
# 浏览器打开 http://localhost:5173

# 确保后端已启动：
cd crane-mms/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 测试账号：
# admin / Admin@2024    → 可访问所有页面
# manager01 / Manager@2024 → 无系统管理菜单
```

---

## 十、注意事项

1. **全部用 `<script setup>` + Composition API**，不用 Options API
2. **API 调用全部封装在 `src/api/` 目录**，页面组件不直接调用 axios
3. **表格分页**：每页默认 20 条，使用 Element Plus `ElPagination` 组件
4. **日期格式**：统一显示 `YYYY-MM-DD`，表单中使用 `ElDatePicker`
5. **ECharts**：仅在 Dashboard 页使用，其他页面不引入（避免打包体积过大）
6. **后端接口尚未实现的功能**（如 reschedule、cancel）：先完成前端页面和交互，接口调用处加注释 `// TODO: 后端接口待实现`，不阻塞开发
