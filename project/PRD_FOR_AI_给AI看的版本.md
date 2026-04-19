# 郭氏维保管理系统 — AI开发PRD
> 版本：V1.0 | 日期：2026-03-28 | 用途：提供给Cursor/AI直接使用的开发规格文档
> 配套文件：AI交接文档_V4终稿.md（详细交互规格）| BUGFIX_INSTRUCTIONS.md（Bug修复指令）| CURSOR_GUIDE.md（后端模块Prompt）
> 仓库：https://github.com/gys17638569512-design/shebei-guanlixitong

---

## SECTION 0 — 快速上下文

**这是什么项目**
起重机维保SaaS平台。郭永盛（老郭）是业务方，已有后端V1.0（FastAPI+MySQL，27个文件，10个测试全绿）。现在需要：① 修复后端已知Bug → ② 完成后端剩余模块 → ③ 开发PC前端 → ④ 完善小程序。

**当前最紧急的事**
后端有3个P0 Bug必须先修：密码明文"123" / JWT 30分钟过期 / 缺数据库连接池参数。修复方法在 `BUGFIX_INSTRUCTIONS.md`，粘贴到Cursor Chat执行，完成后`pytest tests/ -v`验证全绿。

**不可更改的约定**
- 技术栈锁定（见Section 1）
- 所有字段设置下拉项必须从接口取，禁止硬编码
- 数据隔离必须在service层实现，不能只靠前端
- 每次改动后`pytest tests/ -v`全绿才能继续

---

## SECTION 1 — 技术栈

```
后端:       Python 3.10+ / FastAPI / SQLAlchemy / MySQL 8.0
PC前端:     Vue3 + Element Plus + Pinia + Axios
小程序:     uni-app（注意：不是原生微信小程序）
客户门户:   Vue3 + Element Plus
部署:       Windows Server 2025
开发工具:   Cursor + pytest
```

**后端分层架构（严格遵守）**
```
routers/     → 接收请求、参数验证、权限检查、调用service（不直接操作DB）
services/    → 业务逻辑、调用repository、写审计日志（不直接写SQL）
repositories/→ 数据库CRUD（不含业务逻辑）
models/      → SQLAlchemy ORM模型（只定义表结构）
schemas/     → Pydantic Schema（校验和序列化）
core/        → 安全/权限/异常/审计/响应等横切工具
```

---

## SECTION 2 — 用户角色与权限

```
ADMIN（管理员）
  - 首页：全局视角，可切换三种视角预览
  - 数据：全部数据
  - 权限：系统设置、授权管理、视角切换

MANAGER（业务经理）
  - 首页：仅经理视角，无切换按钮
  - 数据：仅 manager_id=自己 的客户和工单
  - 权限：新建派单、客户管理

TECH（工程师）
  - 首页：仅工程师视角，无切换按钮
  - 数据：仅 assigned_engineer=自己 的工单
  - 权限：查看工单、填写检查
```

**⚠️ 关键约束：数据隔离必须在 service 层用 manager_id / assigned_engineer 过滤，不能只靠前端隐藏**

---

## SECTION 3 — 数据模型

### 3.1 核心表（★=新增/需更新字段）

```sql
-- User（★新增字段）
id, username, ★phone VARCHAR(20), email, role ENUM('ADMIN','MANAGER','TECH'),
★manager_id INT FK→User.id,  -- 工程师所属经理
is_active BOOL, password_hash

-- Customer
id, customer_no, company_name, short_name, industry, address, city,
manager_id FK→User.id, contract_no, contract_start, contract_end,
created_at, updated_at

-- Contact（一客户多联系人）
id, customer_id FK→Customer.id, name, position, phone, wechat, email,
is_primary BOOL, receive_notify BOOL

-- Equipment（★三编号新增）
id, customer_id, name, category,  -- category联动FieldSetting
★system_no VARCHAR(50) UNIQUE,    -- 二维码专属码，全局唯一
★factory_no VARCHAR(100),         -- 铭牌原厂编号，选填
★site_no VARCHAR(100),            -- 客户场内编号，选填
model_type, rated_capacity, span, lift_height, work_level,
location_address, location_area, location_track,
install_date, next_inspection_date, warranty_expire,
qr_code_url, created_at

-- WorkOrder
id, order_no, equipment_id, engineer_id, manager_id,
type,  -- 联动FieldSetting.category='order_type'
status ENUM('PENDING','IN_PROGRESS','PENDING_SIGN','COMPLETED','CANCELLED'),
priority ENUM('NORMAL','URGENT'),
planned_date DATE,
★check_template_version INT,  -- 记录使用的模板版本，完成后锁定
remark, created_by, created_at, updated_at

-- InspectionTemplate（★版本控制新增）
id, device_category, check_type,
★version INT DEFAULT 1,
★is_active BOOL DEFAULT TRUE,
★parent_id INT FK→self,  -- 版本链，父版本ID
created_at, created_by

-- InspectionItem
id, template_id FK→InspectionTemplate.id,
name, description,
result_types VARCHAR(100),  -- JSON: ["pass_fail","photo","number"]
unit VARCHAR(20), min_val FLOAT, max_val FLOAT,
is_required BOOL, sort_order INT

-- Report
id, work_order_id FK→WorkOrder.id, report_no,
pdf_url, status ENUM('GENERATING','DONE','FAILED'),
sign_cert_no VARCHAR(200),  -- e签宝/法大大证书编号
created_at

-- FieldSetting（★新表：所有下拉配置）
id, category ENUM('device_type','order_type','industry','position'),
value VARCHAR(100), label VARCHAR(100),
is_system BOOL,  -- TRUE=预置不可删，FALSE=自定义可删
sort_order INT

-- NumberRule（★新表：编号规则）
id, target ENUM('device','order','customer','report'),
prefix VARCHAR(10), include_year BOOL DEFAULT TRUE,
seq_length INT DEFAULT 6,
reset_cycle ENUM('yearly','never'),
current_seq INT DEFAULT 0

-- AuditLog（不可删除）
id, user_id, action VARCHAR(50), resource VARCHAR(50),
resource_id INT, detail TEXT, created_at

-- SitePhoto（★新表）
id, work_order_id, photo_url, take_time DATETIME,
gps_lat FLOAT, gps_lng FLOAT, watermark_info TEXT

-- CheckInRecord（★新表）
id, work_order_id,
step ENUM('arrive','start','abnormal','finish'),
timestamp DATETIME, gps_lat FLOAT, gps_lng FLOAT, note TEXT

-- FileAttachment（★新表）
id, device_id FK→Equipment.id,
file_name, file_type ENUM('pdf','jpg','png','dwg'),
file_url, upload_time DATETIME, uploaded_by INT FK→User.id

-- ReportSendRecord（★新表）
id, report_id FK→Report.id,
sent_to VARCHAR(200), sent_at DATETIME,
sent_by INT FK→User.id,
status ENUM('success','failed')
```

### 3.2 系统设备编号生成规则

```python
def generate_system_no(factory_no: str | None, prefix: str, dealer_id: int, year: int, seq: int, seq_len: int) -> str:
    """
    有出厂编号 → GS-0001-2024-[QD50001]（后缀用出厂编号，去除特殊字符转大写）
    无出厂编号 → GS-0001-2024-000001（后缀自动递增，位数由seq_len决定）
    dealer_id 补零到4位
    """
    dealer_str = str(dealer_id).zfill(4)
    if factory_no:
        suffix = re.sub(r'[^A-Z0-9]', '', factory_no.upper())
        return f"{prefix}-{dealer_str}-{year}-{suffix}"
    else:
        seq_str = str(seq).zfill(seq_len)
        return f"{prefix}-{dealer_str}-{year}-{seq_str}"
```

### 3.3 工单状态机

```
PENDING → IN_PROGRESS   触发：工程师GPS打卡（到场）
PENDING → CANCELLED     触发：管理员/经理手动作废
PENDING → PENDING       触发：改期（更新planned_date）或转派（更新engineer_id）
IN_PROGRESS → PENDING_SIGN  触发：工程师提交全部检查结果
PENDING_SIGN → COMPLETED    触发：客户手写签字确认
COMPLETED → （终态）
CANCELLED → （终态）

操作权限约束：
- 转派：仅PENDING状态可用
- 改期：仅PENDING状态可用
- 作废：PENDING和IN_PROGRESS可用，PENDING_SIGN/COMPLETED/CANCELLED不可用
```

### 3.4 检查模板版本控制

```
每次保存 → 新建记录，version+1，parent_id=上一版本id
停用 → is_active=False，不删除
工单派单时 → 记录当前模板version到WorkOrder.check_template_version
报告生成时 → 使用WorkOrder.check_template_version对应的快照数据
历史数据不受后续模板变更影响
```

---

## SECTION 4 — API接口规范

```
基础路径: /api/v1/
认证: Authorization: Bearer <JWT_TOKEN>  有效期24h
返回格式: { "code": 0, "msg": "ok", "data": {...} }
错误码: 400=参数错误 401=未授权 403=无权限 404=不存在 422=校验失败 500=服务器错误
分页: ?page=1&page_size=20
时间: ISO 8601，Asia/Shanghai时区
文件上传: multipart/form-data，图片≤10MB，文件≤50MB
```

---

## SECTION 5 — PC管理后台功能规格

### 5.1 全局布局

```
侧边栏（左）:
  - 默认展开：图标+文字
  - 汉堡按钮收起为纯图标
  - 导航项：工作台 / 工单中心（红点=待处理数）/ 客户管理 / 设备档案 / 报告中心 / 系统设置
  - 底部：用户头像+姓名+角色，点击→下拉菜单（个人资料/修改密码/退出）

顶部栏（上）:
  - 左：汉堡按钮 + 面包屑
  - 中：全局搜索框（混合搜索工单/客户/设备，输入后下拉结果分组）
  - 右：通知铃铛（红点）+ 用户角色chip + 公司名（点击→系统设置→公司信息）+ 实时时钟
```

### 5.2 首页工作台

```
ADMIN视角:
  - 5张统计卡片：本周待处理 / 进行中 / 本月完工 / 逾期（红色边框）/ 设备预警
  - 逾期工单列表（左宽）：左侧红竖条，点击行→工单详情，"查看全部"→工单中心
  - 工程师动态（右窄）：今日工单+本周完工+状态；点击→该工程师工单列表
  - 设备预警（左下）：按设备/按客户Tab；"安排维保"→新建派单抽屉（预填客户+设备+优先级=URGENT）
  - 完工趋势折线图（右下）：近30天
  - FAB快捷菜单（右下角）：展开→新建派单/安排维保/新增客户

MANAGER视角（数据范围=自己负责的客户和工单）:
  - 统计卡片：我的客户数/待处理工单/临期设备/逾期工单
  - 待处理&逾期工单列表（左）
  - 我负责的客户列表（右）：设备数/工单数/状态
  - 设备临期预警网格（底）

TECH视角（数据范围=分配给自己的工单）:
  - 工单按日期分组：今天（进行中+待出发）/明天/逾期（红色高亮）
  - 右侧：本周每日完工柱状图+最近5条记录
```

### 5.3 工单中心

#### 工单列表
```
顶部5张统计卡：总数/待处理/进行中/逾期/本月完工
状态Tab：全部/待处理/进行中/待签字/已完成（各带数量徽标）
筛选：搜索(编号/客户/设备名) + 客户下拉 + 工程师下拉 + 工单类型下拉 + 日期区间 + "仅看逾期"开关
表格列：工单编号(蓝可点击) / 客户名(蓝可点击) / 设备名(蓝可点击) / 工单类型 / 工程师 / 计划日期 / 状态 / 逾期标识 / 最近更新
逾期判断：planned_date<今天 AND status NOT IN ('COMPLETED','CANCELLED') → 整行浅红背景
行操作(hover)，按状态动态显示：

  PENDING:     查看详情 | 时间线 | 转派 | 改期 | 作废 | 下载PDF
  IN_PROGRESS: 查看详情 | 时间线 | 转派 |  —  | 作废 |    —
  PENDING_SIGN:查看详情 | 时间线 |  —  |  —  |  —  |    —
  COMPLETED:   查看详情 | 时间线 |  —  |  —  |  —  | 下载PDF
  CANCELLED:   查看详情 |  —    |  —  |  —  |  —  |    —

批量排期按钮：选多台设备+日期+工程师，批量创建，重复检测（同设备同日期跳过）
```

#### 工单详情
```
头部：工单编号 + 状态标签 + 优先级标签 + 关联客户/设备（蓝色可跳转）+ 操作按钮组（按状态动态）

PENDING状态内容：
  - 基础信息卡（客户/设备/工程师/计划日期/工单类型）
  - 检查项预览（来自 InspectionTemplate v=WorkOrder.check_template_version）
  - 时间线（工单创建记录）

IN_PROGRESS 追加：
  - GPS打卡记录（到达时间+坐标）

PENDING_SIGN 追加：
  - 检查结果列表（每项：名称/结果/异常备注/异常照片缩略图）

COMPLETED 追加：
  - 完成总结卡（总检查项数/异常项数/照片数）
  - 四步打卡记录（到场/开始作业/异常登记（如有）/完工离场）+ 时间戳+GPS
  - 检查结果表格（异常项红色标注+实测数据+处理情况）
  - 现场照片墙（缩略图网格，点击全屏预览）
  - 客户签字图片
  - 操作按钮：查看报告→报告预览抽屉 | 下载PDF
```

#### 工单时间线视图（独立视图，时间线图标点击后展示）
```
节点顺序（蓝色，最后已完成节点绿色高亮）：
工单创建(时间+操作人) → 派单(时间+工程师) → 到场打卡(GPS) → 开始作业 
→ 异常登记(如有) → 完工离场 → 客户签字 → 报告生成 → 发送给客户(如有)
```

#### 新建派单抽屉（三步）
```
入口与预填：
  工单列表"+ 新建派单"          → 无预填，无提示条
  首页"安排维保"按钮             → 预填客户+设备，priority=URGENT，橙色提示条
  客户详情"新建工单"按钮         → 预填客户，绿色提示条
  设备详情"新建工单"按钮         → 预填客户+设备，蓝色提示条

Step1 基本信息：
  customer_id（必填，下拉搜索）
  equipment_id（必填，联动customer_id过滤，下拉仅显示设备名称）
  → 选择equipment_id+order_type后：展示检查项预览
  order_type（必填，来自FieldSetting.category='order_type'）
  priority（必填，默认NORMAL，URGENT=紧急）
  planned_date（必填）

Step2 安排人员：
  engineer_id（必填，卡片选择，显示今日工单数，空闲=0单标绿色）
  remark（选填）

Step3 确认派单：
  信息摘要卡 + 确认后发微信+短信通知给工程师
```

#### 操作弹窗
```
转派弹窗：
  new_engineer_id（必填，显示今日工单数）
  reason（必填）
  notify_old BOOL（默认False）
  notify_new BOOL（默认True）
  约束：仅PENDING可转派

改期弹窗：
  new_date（必填）
  reason（必填）
  notify_engineer BOOL（默认True）
  约束：仅PENDING可改期

作废弹窗：
  reason（必填）
  红色警告：不可恢复，记录在AuditLog
```

### 5.4 客户管理

#### 客户列表
```
表格列：公司名称(必显,蓝色可点击) / 客户编号 / 城市地区 / 主联系人 / 设备数 
       / 待处理工单 / 最近维保日期 / 下次临期预警 / 负责经理
筛选：公司名搜索 + 负责经理 + 城市 + 是否有临期设备 + 是否有逾期工单 + 高级筛选面板
行操作：眼睛→侧边预览抽屉 | 铅笔→编辑客户信息抽屉 | 公司名→客户详情页

侧边预览抽屉内容：
  基础信息（名称/地址/负责经理）
  名下设备列表（状态+临期情况）
  合同信息
  历史工单（最近3条）
  "查看完整资料"按钮→客户详情页
```

#### 客户详情页
```
Hero区：
  客户名+状态标签+位置地址
  统计条：设备总数/正常/临期/逾期/待处理工单
  操作按钮：编辑信息 | 新建工单 | 门户授权 | 客户账号管理

Tab内容：
  联系人Tab：
    列表（头像+姓名+职位+手机+邮箱+主联系人标签）
    行操作：铅笔→编辑联系人弹窗 | 删除
    "＋添加联系人"→添加联系人抽屉

  设备档案Tab：
    该客户设备列表（精简版）
    设备名→设备详情页
    "＋新建设备"→新建设备表单（自动带入customer_id和客户地址）

  维保记录Tab：
    历史工单列表
    工单编号→工单详情页

  报告归档Tab：
    该客户所有报告
    操作：查看/下载/发送
```

#### 相关弹窗/抽屉
```
编辑客户信息抽屉（来自：列表铅笔 / 详情"编辑信息"）：
  customer_no（只读，灰底）
  company_name（必填）/ short_name / industry（来自FieldSetting.category='industry'）
  address / city / phone / email
  manager_id（从用户列表选，角色=MANAGER）
  合同信息（contract_no / contract_start / contract_end）
  remark
  底部：最近3条修改记录（AuditLog）

添加/编辑联系人抽屉：
  name（必填）
  position（下拉来自FieldSetting.category='position'，可切换为手动输入）
  phone（必填）/ wechat / email / tel
  is_primary BOOL（开关）
  receive_notify BOOL（开关）
  编辑模式：带入已有数据

门户授权抽屉（来自：详情"门户授权"）：
  portal_enabled BOOL（总开关，关闭后所有portal账号立即封号）
  account_quota INT（账号上限）
  expire_date DATE
  permissions: {report: BOOL, equipment: BOOL, work_order: BOOL}
  send_notify_sms BOOL（向主联系人发开通短信）

客户账号管理页（来自：详情"客户账号管理"）：
  配额进度卡片（4个）
  账号列表：name/position/portal_role/phone/password_status/is_active
  portal_role ENUM('business','equipment_mgr','operator')
  行操作：编辑 | 重置密码 | 删除
  "＋新增账号"弹窗：head_color/name/position/phone/email/portal_role/权限开关/发送激活短信
```

### 5.5 设备档案

#### 设备列表
```
表格列（默认）：
  设备编号 / 设备名称(必显) / 所属客户(蓝可点击) / 设备大类 / 型式型号 
  / 额定参数 / 安装位置 / 年检状态 / 质保到期日 / 设备状态(正常/临期/逾期)

三编号列（可通过"列显示"控制）：
  system_no（蓝色等宽字体，"唯一码"标签）
  factory_no（未录入显示"—未录入"灰斜体）
  site_no（同上）

列显示控制：右上角"列显示"按钮→弹出面板，设备名称列固定不可隐藏
筛选：搜索(名称/编号/客户) + 设备大类(来自FieldSetting) + 客户 + 状态
行操作(hover)：查看详情 | 编辑设备 | 打印二维码（直接下载）
逾期行：整行浅红色背景
```

#### 设备详情页
```
Hero区：
  设备图标（按大类着色）+ 设备名+状态+大类标签
  三编号横条（三格并排）：
    system_no（蓝色，"唯一码"标签，hover显示复制图标）
    factory_no（"铭牌原厂"，未填="—未填写"灰斜体）
    site_no（"客户内部叫法"，未填同上）
  统计条：历史工单/本年已检/距下次检查/发现异常/报告数量

操作按钮：打印二维码 | 编辑设备 | ＋新建工单

Tab内容：

  基础信息Tab：
    技术参数（6项：大类/吨位/跨度/出厂年份/起升高度/工作级别）
    编号详情区（独立卡片）：
      system_no大字 + 迷你二维码 + 下载/打印按钮
      下方两格：factory_no / site_no
      右上角"编辑编号"按钮→编辑设备编号弹窗
    安装位置（6项）

  维保记录Tab：
    历史工单表格（编号/类型/工程师/完成日期/结果/报告）
    工单编号→工单详情 | 报告"查看"→报告预览抽屉

  提醒规则Tab：
    当前规则列表（各类型提前天数）
    "编辑规则"按钮
    说明：单台设备规则优先于全局规则

  部件清单Tab：
    部件列表（名称/规格型号/数量/单位/上次更换/状态）
    "智能填充"按钮（后续版本：根据大类+型号推荐BOM）
    "＋添加部件"→添加部件弹窗

  文件管理Tab：
    文件列表（文件名/文件类型/上传时间）
    拖拽/点击上传区（PDF/JPG/PNG/DWG）
    在线预览
```

#### 新建设备表单（独立页面，左右两栏）
```
左侧表单区块：
  1.基础信息：
    customer_id（必填，选后自动带入地址）
    category（必填，来自FieldSetting.category='device_type'）→选后自动推荐检查模板
    name（必填）/ model_type / rated_capacity / span / lift_height / work_level / year

  2.设备编号区（背景浅灰）：
    factory_no（选填，输入后system_no后缀实时变化）
    site_no（选填）
    system_no（自动生成，三种状态）：
      有factory_no → 绿色背景，"使用出厂编号作后缀"
      无factory_no → 蓝色背景，"自动递增"
      手动修改 → 橙色边框，"手动模式·请确保唯一"
    "手动修改"/"恢复自动"切换按钮

  3.检查与提醒：
    template_id（联动category自动推荐，可手动选择）
    next_inspection_date / reminder_days

  4.安装位置：
    location_address（选customer后自动带入，可改）/ location_area / location_track

  5.文件上传：拖拽/点击，PDF/JPG/PNG/DWG

  6.备注：remark

右侧预览区（sticky固定）：
  编号预览卡：三编号实时状态+逻辑说明文字
  二维码预览：模拟图（保存后正式生成）+ 下载/打印贴纸按钮

打印贴纸弹窗：
  单张格式（80×80mm，1码/张：设备名+二维码+编号+公司名）
  A4批量格式（每页4张，40×50mm）
  范围：仅当前设备 | 该客户所有设备

底部操作栏（固定）：取消 | 保存草稿 | 保存设备
```

#### 编辑设备编号弹窗（来自：详情"编辑编号"）
```
factory_no：输入后实时更新system_no后缀
site_no：独立编辑
system_no：联动factory_no；"手动修改"→自由输入；"恢复自动"→还原
底部橙色警告：修改system_no后，已打印贴纸失效，需重新打印
```

#### 添加部件弹窗
```
表格式多行录入：
  每行：name / model_spec / quantity / unit(下拉:套/个/台/条/件/米) / last_replace_date
"＋添加一行"追加 | 每行有删除按钮 | 支持一次提交多行
```

### 5.6 报告中心

```
4张统计卡片：总数/已签字/待签字/本月新增
表格列：report_no / customer_name(蓝可点击) / equipment_name(蓝可点击) / order_type
       / created_at / engineer / file_size / sign_status / report_status(生成中/已生成/失败)
筛选：客户 + 工程师 + 日期区间 + 签字状态 + 工单类型 + "仅看未签字"快速过滤
行操作(hover)：
  眼睛 → 报告预览抽屉
  下载 → 直接下载PDF
  邮件 → 发送报告弹窗
  (生成失败时) 重试 → 重新生成
批量操作：勾选多行→批量下载（打包下载，含进度反馈）

报告预览抽屉：
  公司信息 + 设备信息 + 检查结果表格（异常项红色标注+实测数据）
  + 工程师结论建议 + 现场照片区 + 双方签字 + e签宝认证编号
  底部：下载PDF | 发送给客户

发送报告弹窗：
  to: 主联系人邮箱（默认勾选）+ 其他联系人（可勾选）
  cc: 手动添加邮箱
  subject: 可修改
```

### 5.7 系统设置

```
左侧二级菜单结构：
  基础设置：公司信息 | 外观主题
  人员管理：用户管理 | 权限管理
  业务配置：字段设置 | 检查模板 | 全局提醒规则 | 消息通知
  系统记录：操作日志
  平台管理：授权管理
```

#### 字段设置
```
5个配置区块：

1.编号规则（4套，各含保存按钮）：
  设备编号：prefix / include_dealer_id / include_year / seq_length / 实时预览
  工单编号：prefix / include_year / seq_length / reset_cycle(yearly/never)
  客户编号：prefix / include_year / seq_length / input_mode(auto/manual)
  报告编号：prefix / include_year / seq_length / reset_cycle

2.设备大类（FieldSetting.category='device_type'）：
  标签列表，虚线边框=is_system=True不可删，实线边框=is_system=False可删
  输入框+"＋添加"，支持回车快速添加
  预置值：桥式起重机/门式起重机/悬臂起重机/电动葫芦

3.工单类型（FieldSetting.category='order_type'）：
  同上，预置值：周巡检/月检/季检/小修/大修/年检

4.客户行业类型（FieldSetting.category='industry'）：
  同上，预置值：钢铁冶金/港口码头/电力能源/航运物流/制造业

5.联系人职位（FieldSetting.category='position'）：
  同上，预置值：采购部长/设备科长/生产主任/门卫主任

⚠️ 以上所有下拉必须从 FieldSetting 接口动态获取，前端不可硬编码任何选项值
```

#### 检查模板管理
```
总览视图：设备大类（行）× 检查类型（列）矩阵
  已配置格子：蓝色，显示检查项数+版本号，点击→操作面板弹窗
  未配置格子：虚线+号，点击→引导新建
  操作面板（弹窗）：编辑检查项 | 查看历史版本 | 停用此模板

三级树形表格：
  一级：设备大类（展开/收起）→ 操作：+添加类型/编辑/删除
  二级：检查类型（展开/收起）→ 操作：+添加检查项/编辑/停用/删除
  三级：检查项表格行 → 操作：编辑（行内展开）/删除

检查项编辑页（独立页面，三级树"编辑"进入）：
  面包屑：检查模板 / 设备大类 / 检查类型
  页头：模板名称+版本号+启用状态 + 保存（→自动生成新版本VN+1）/ 取消
  右上角两个图标按钮：
    👁 填写预览抽屉（模拟工程师端小程序填写效果）
    🕐 历史版本抽屉（版本时间线+变更说明+查看）
  检查项全宽表格：
    列：拖拽手柄/序号/名称/检查说明/结果类型标签/必填红点/操作图标
    点击行→展开行内编辑区（蓝色背景）：
      name / description / result_types多选（正常异常/数值输入/拍照）
      数值配置：unit/min_val/max_val
      is_required BOOL
    底部"＋添加检查项"虚线按钮
  启用开关关闭→停用确认弹窗（列明影响范围）
```

#### 用户管理
```
列表：头像+姓名+账号 / 角色标签 / 手机号 / 登录账号 / 状态开关
行操作(hover)：铅笔→编辑用户弹窗 | 锁→重置密码弹窗 | ×→禁用确认弹窗
管理员行：只有铅笔，无锁无×

新增用户弹窗：
  head_color（6色选择，实时预览首字母）
  name / phone / email
  username / role / password（实时强度检测：弱/中/强）
  创建后发短信通知勾选

重置密码弹窗：橙色警告 + new_password / confirm_password
禁用确认弹窗：红色警告（说明待处理工单需手动转派）
```

#### 权限管理
```
岗位权限矩阵：
  行：功能模块（工单中心/客户管理/报告中心/设备档案/系统设置）
  列：管理员/业务经理/工程师/自定义岗位
  格子：勾选框（灰色=系统锁定不可改）

新增岗位弹窗：
  name / description
  权限模板（快速复制：参考业务经理/工程师权限）
  权限分组列表（逐项勾选）
  实时计数：已选N项
```

#### 消息通知
```
各事件类型开关（工单创建/完成/逾期/设备临期...）
通知方式（工程师和客户分别配置）：
  微信订阅消息（工程师 / 客户端）
  短信（工程师 / 客户端，重要通知兜底）
短信签名设置
注：微信推送失败时短信自动兜底
```

#### 授权管理（平台管理）
```
发展商列表：公司名/联系人/授权状态/到期日/客户数/设备数/账号数（已用/上限）
状态4种颜色：试用(橙)/正式(绿)/临期(红竖条+"立即续费")/锁定(灰置暗+"重新授权")
行操作：续期 | 修改权限 | 锁定

新增授权弹窗（4块）：
  基础信息：company_name / contact / phone / email
  授权类型：trial/formal + expire_date
  功能模块开关（控制发展商能用哪些模块）
  配额上限：max_customers / max_equipment / max_staff / max_engineers

续费记录弹窗（记录图标）：历史续费流水（时间段/金额/状态）
```

### 5.8 个人中心

```
入口：左下角用户头像→下拉菜单（个人资料/修改密码/退出登录）

个人资料页（两列布局）：
  左列：
    头像（hover显示编辑蒙层，可上传）
    可编辑：name / phone / email
    只读（灰底）：username / company / role
  右列：
    账号安全（密码/邮箱/手机绑定状态）
    最近登录记录（设备/地点/时间，最近5条）
  "保存修改"：点击后短暂绿色反馈

修改密码页（两种Tab）：
  旧密码验证：current_password + new_password（实时强度检测）+ confirm_password
  手机验证码：phone（只读）+ 发送验证码 + code + new_password
```

---

## SECTION 6 — 微信小程序功能规格

> 使用 uni-app 框架，不是纯原生微信小程序

### 6.1 功能清单（均为P0）

```
工单列表：
  按状态分组（待处理/进行中/已完成）
  点击任务卡片→查看设备历史维保记录、上次故障情况、客户联系人信息

水印相机：
  拍照自动附加水印：时间（精确到秒）+ 位置文字 + 工单编号
  照片不可在相册删除打卡标记

离线检查表单：
  断网时可填写（本地缓存模板）
  断网状态下已缓存模板可正常渲染
  联网后自动同步

异常处理逻辑（重要）：
  勾选"异常"→自动展开"原因说明"必填框和"拍照"按钮
  不填写原因无法进入下一步（前端强校验）

GPS打卡：
  到场/完工时记录timestamp + gps_lat + gps_lng
  定位失败→提示手动输入地址，不能阻断整个作业流程

离线队列：
  离线操作缓存到本地队列
  网络恢复后批量自动上传，按时间顺序提交

电子签字：
  客户手写签名（canvas）
  接入第三方电子签名平台（法大大/签名宝）
  返回sign_cert_no存入Report表

二维码扫码（P1）：
  扫设备system_no→快速调取设备档案
```

### 6.2 现场作业流程

```
1. 接单 → 工单列表收到通知，查看工单
2. 查阅 → 点击任务卡片，查看设备历史记录和客户联系人
3. 到场 → GPS打卡（step=arrive）
4. 拍照 → 水印相机拍设备现状
5. 检查 → 逐项填写检查项；异常项填写原因+拍照（强制）
6. 完工 → GPS打卡（step=finish）
7. 签字 → 客户手写签字（电子签名平台）
8. 提交 → 上传全部数据（离线→队列等待）
9. 报告 → 后端自动生成PDF，推送给客户
```

---

## SECTION 7 — 所有可点击入口与跳转（完整清单）

### 7.1 全局蓝色链接
```
任意位置 客户名称(蓝色)       → 客户详情页
任意位置 设备名称(蓝色)       → 设备详情页
任意位置 工单编号(蓝色)       → 工单详情页
顶栏     公司名称             → 系统设置→公司信息
```

### 7.2 按钮/图标入口（38个）
```
[首页]
首页→设备预警 "安排维保"          → 新建派单抽屉(预填客户+设备+URGENT+橙色提示条)
首页→工单列表 "查看全部→"         → 工单中心列表页
首页FAB       "新建派单"           → 新建派单抽屉(无预填)
首页FAB       "安排维保"           → 新建派单抽屉(同上)
首页FAB       "新增客户"           → 新建客户表单

[工单中心]
工单列表行(hover) 查看详情图标     → 工单详情页
工单列表行(hover) 时间线图标       → 工单时间线视图
工单列表行(hover) 转派图标         → 转派弹窗
工单列表行(hover) 改期图标         → 改期弹窗
工单列表行(hover) 作废图标         → 作废弹窗
工单列表行(hover) 下载PDF图标      → 直接下载该工单PDF
工单详情(COMPLETED) "查看报告"     → 报告预览抽屉
工单详情(COMPLETED) "下载PDF"      → 直接下载PDF

[客户管理]
客户列表行(hover) 眼睛图标         → 客户侧边预览抽屉
客户列表行(hover) 铅笔图标         → 编辑客户信息抽屉
客户详情→操作区  "新建工单"        → 新建派单抽屉(预填客户+绿色提示条)
客户详情→操作区  "编辑信息"        → 编辑客户信息抽屉
客户详情→操作区  "门户授权"        → 门户授权抽屉
客户详情→操作区  "客户账号管理"    → 客户账号管理独立页面
客户详情→联系人  铅笔图标          → 编辑联系人弹窗(带入已有数据)
客户详情→联系人  "＋添加联系人"    → 添加联系人抽屉
客户详情→设备Tab "＋新建设备"      → 新建设备表单(自动带入customer_id+蓝色提示条)

[设备档案]
设备列表行(hover) 查看详情图标     → 设备详情页
设备列表行(hover) 编辑图标         → 新建设备表单(编辑模式+带入已有数据)
设备列表行(hover) 打印二维码图标   → 直接下载该设备二维码
设备详情→操作区  "新建工单"        → 新建派单抽屉(预填客户+设备+蓝色提示条)
设备详情→操作区  "编辑设备"        → 新建设备表单(编辑模式)
设备详情→操作区  "打印二维码"      → 打印贴纸弹窗(单张/A4批量两种格式)
设备详情→基础信息 "编辑编号"       → 编辑设备编号弹窗(三编号+联动逻辑)
设备详情→部件清单 "＋添加部件"     → 添加部件弹窗(表格式批量)

[报告中心]
报告列表行(hover) 眼睛图标         → 报告预览抽屉
报告列表行(hover) 邮件图标         → 发送报告弹窗
报告列表行(hover) 下载图标         → 直接下载PDF
报告预览抽屉     "发送给客户"       → 发送报告弹窗

[系统设置]
用户管理列表行   铅笔图标           → 编辑用户弹窗
用户管理列表行   锁图标             → 重置密码弹窗
用户管理列表行   ×图标              → 禁用确认弹窗
权限管理         "＋新增岗位"        → 新增岗位弹窗(含权限模板复制)
检查模板矩阵     已配置格子点击      → 操作面板(编辑检查项/历史版本/停用)
检查模板矩阵     未配置格子点击      → 引导新建弹窗
检查模板编辑页   启用开关关闭时      → 停用确认弹窗(列明影响范围)
检查模板编辑页   👁图标             → 填写预览抽屉(工程师端实际效果)
检查模板编辑页   🕐图标             → 历史版本抽屉(版本时间线+变更说明)
客户账号管理     铅笔图标           → 编辑账号弹窗
客户账号管理     锁图标             → 重置密码弹窗
客户账号管理     删除图标           → 删除确认弹窗(说明配额释放)

[个人中心]
左下角头像       点击               → 下拉菜单(个人资料/修改密码/退出登录)
```

---

## SECTION 8 — 第三方服务接入

```
电子签名（P0）：
  接入法大大或签名宝
  流程：上传文件→创建签署流程→客户签字→返回sign_cert_no→存入Report
  报告预览显示e签宝认证编号

微信订阅消息（P0）：
  工单创建/完成/逾期/设备临期提醒→工程师
  报告生成/发送→客户
  使用微信官方API，需模板ID配置

短信（P0）：
  推荐：阿里云SMS或腾讯云SMS
  用途：微信推送失败时兜底，重要通知不漏达
  需短信签名配置（系统设置→消息通知）

图片/文件存储（P0）：
  推荐：阿里云OSS或腾讯云COS
  现场照片、设备文件、报告PDF均存OSS
  返回URL存DB

地图/定位（P0）：
  推荐：腾讯地图小程序SDK
  用途：工程师GPS打卡，获取gps_lat+gps_lng+位置文字

水印相机（P0）：
  使用微信小程序生态开源组件
  水印内容：时间（精确到秒）+ 位置文字 + 工单编号
  照片写入的水印不可在相册删除
```

---

## SECTION 9 — 非功能需求

```
性能：
  API响应 < 500ms（普通查询）
  列表页（含分页）< 1s
  PDF生成 < 10s
  图片上传 < 5s（4G，≤5MB）
  离线：断网下完成完整检查表单填写

安全：
  JWT有效期24h（当前Bug：30分钟，待修复）
  密码bcrypt哈希（当前Bug：明文"123"，待修复）
  8位以上强密码，首次登录强制改密
  service层数据隔离（当前Bug，待修复）
  AuditLog不可删除（维保记录是法律证据）
  数据库连接池：pool_size=10, max_overflow=20, pool_recycle=3600（当前Bug，待修复）

兼容性：
  PC：Chrome 90+/Edge 90+，分辨率≥1280×768
  小程序：微信基础库2.15+，iOS 14+/Android 8+
  门户：Chrome 90+/Safari 14+，支持手机访问
```

---

## SECTION 10 — 已知Bug（优先修复，见BUGFIX_INSTRUCTIONS.md）

```
P0 — 必须在开发前修复：
  [BUG-01] 所有测试账号密码为"123"，登录文档明文暴露
  [BUG-02] JWT过期时间30分钟（应为24小时）
  [BUG-03] 缺数据库连接池保护参数

P1 — 尽快修复：
  [BUG-04] Router层直接ORM查询，N+1性能问题
  [BUG-05] MANAGER角色customer列表返回全部数据（应过滤manager_id）
  [BUG-06] User模型缺phone和manager_id字段
  [BUG-07] InspectionTemplate无版本控制，修改检查项会导致历史记录失真
  [BUG-08] PDF生成库（reportlab）未配置中文字体路径，中文乱码
  [BUG-09] Equipment模型缺system_no/factory_no/site_no三个字段
```

---

## SECTION 11 — 开发顺序建议

```
M1 后端修复     → BUGFIX_INSTRUCTIONS.md → pytest全绿
M2 后端完整版   → CURSOR_GUIDE.md模块05-09 → 所有API可用
M3 PC前端搭架  → Vue3+路由+Pinia+Element Plus → 首页可访问
M4 PC前端核心  → 工单中心+客户管理+设备档案 → 核心流程走通
M5 PC前端完整  → 报告中心+系统设置+个人中心 → 全功能可用
M6 小程序      → uni-app工程师端 → 完整作业流程+离线队列
M7 集成联调    → 前后端联调+第三方服务接入
M8 生产部署    → Windows Server 2025+安全加固+备份

每个阶段约定：
  - 一个Cursor Chat只做一个模块
  - 完成后pytest全绿才进下一阶段
  - 字段设置类下拉必须从接口取
  - 数据隔离必须在service层
```

---

## SECTION 12 — 后端待实现功能清单（UI已设计完毕，接口需实现）

```
1.  设备三编号存储+system_no生成逻辑（有factory_no时用作后缀，否则递增）
2.  字段设置CRUD（FieldSetting表，区分is_system）
3.  编号规则配置+编号生成服务（NumberRule表）
4.  检查模板版本控制（保存时新建版本，历史永久保留）
5.  工单详情已完成状态：检查结果+打卡记录+现场照片+签字的完整存储和返回
6.  新建派单：customer_id→equipment列表联动接口
7.  工单操作权限按status动态校验（接口层）
8.  逾期工单判断：planned_date<今天 AND status NOT IN ('COMPLETED','CANCELLED')
9.  提醒规则优先级：单台设备规则覆盖全局，不叠加推送
10. 联系人CRUD（含is_primary切换逻辑）
11. 客户门户账号管理（配额/激活/权限开关/密码重置）
12. 设备部件清单CRUD（支持批量新增）
13. 设备文件上传和预览（存OSS，返回预览URL）
14. 操作日志记录（覆盖所有敏感增删改）
15. 报告PDF生成（配置reportlab中文字体，避免乱码）
16. 报告发送历史记录（ReportSendRecord表）
17. 批量排期接口（多设备批量创建工单，重复检测）
18. [后续版本] 安全隐患实时推送
19. [后续版本] 维修工单独立流程（含费用单据和分支签字）
```

---

## SECTION 13 — 操作日志覆盖范围

```
必须记录到AuditLog的操作：
  客户/联系人：新增/修改/删除
  设备档案：新增/修改/删除/system_no变更
  工单：创建/转派/改期/作废
  用户账号：创建/禁用/密码重置
  权限配置：岗位新增/权限变更
  检查模板：新增版本/启用/停用
  系统设置：字段设置变更/编号规则变更
  报告：发送操作（记录sent_to）
  授权管理：发展商授权新增/变更/续费
  任何涉及资产变动的操作（备件库存增减/费用确认）
```
