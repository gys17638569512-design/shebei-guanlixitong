# Cursor 开发手册 — 智能起重机维保管理系统

> 本文档是你在 Cursor 里开发此项目的**完整操作指南**。
> 每次开始一个新模块前，请先读对应章节。

---

## 第一步：在 Cursor 里打开项目

1. 把收到的 `crane-mms` 整个文件夹放到你电脑某个位置（比如 `D:\projects\crane-mms`）
2. 打开 Cursor → File → Open Folder → 选择 `crane-mms` 文件夹
3. Cursor 会自动读取根目录的 `.cursorrules` 文件，AI 就"知道"这个项目的所有规则了

---

## 第二步：环境配置（只做一次）

### 安装 Python 环境

```bash
# 在 Cursor 终端执行（Ctrl+` 打开终端）
cd backend
pip install -r requirements.txt
```

### 配置数据库

1. 确保 MySQL 8.0 已安装并运行
2. 用 MySQL Workbench 或命令行创建数据库：

```sql
CREATE DATABASE crane_mms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 配置环境变量：

```bash
# 在 backend/ 目录下
copy ..\env.example .env
# 然后用 Cursor 打开 .env，修改这一行：
# DATABASE_URL=mysql+pymysql://root:你的MySQL密码@localhost:3306/crane_mms
```

### 初始化测试数据

```bash
cd backend
python seed_data.py
```

成功输出：
```
✅ 测试数据初始化完成！
登录账号：
  管理员：admin     / Admin@123
  经理：  manager01 / Manager@123
  工程师：tech01    / Tech@123
```

### 启动后端

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

浏览器打开：http://localhost:8000/docs
看到接口文档页面 = 启动成功 ✅

---

## 第三步：如何用 Cursor AI 开发每个模块

### 黄金法则

**每个模块 = 一个独立的 Cursor 对话（Chat）**

不要在一个对话里做多个模块，AI 上下文会混乱。

### 操作步骤

1. 打开 Cursor → 点击左侧 Chat 图标 → New Chat
2. 第一句话**必须粘贴**下面的「会话开场白」
3. 再粘贴该模块专属的开发指令
4. 让 AI 生成代码后，在终端运行测试
5. 测试全绿才算完成，关闭这个 Chat，下一个模块开新 Chat

### 会话开场白（每次新模块必须粘贴）

```
请读取项目根目录的 .cursorrules 文件，严格按照其中的规范开发。

项目状态：
- 已完成：模块01（骨架）、模块02（认证）、模块03（客户设备）、模块04（工单）
- 本次任务：[在这里填写本次要做的模块名]

后端已可访问：http://localhost:8000/docs
```

---

## 模块开发顺序与指令

按以下顺序开发，每个模块完成测试后再开始下一个。

---

### 模块05：小程序现场作业

**粘贴以下内容给 Cursor AI：**

```
本次任务：开发微信小程序师傅端，实现现场作业核心功能。

目录：miniprogram/（在 crane-mms 根目录下新建此目录）

需要实现的功能：

1. utils/request.js（统一HTTP请求封装）
   - 基础URL配置（指向 http://localhost:8000/api/v1）
   - 自动从 Storage 读取 token，附加到 Authorization Header
   - 响应拦截：code !== 200 时自动显示 toast 错误
   - 401 时跳转到登录页
   - 返回 Promise，支持 async/await

2. utils/offline-queue.js（离线队列）
   - push(taskType, data)：将任务存入 wx.storage 队列
   - processQueue()：网络恢复后，依次执行队列中的请求
   - 在 app.js 中监听网络状态，恢复时自动调用 processQueue()

3. utils/watermark.js（水印工具）
   - addWatermark(tempFilePath, text)
   - 用 Canvas 2D 在图片右下角绘制半透明黑色背景+白色文字水印
   - 水印内容：拍摄时间（YYYY-MM-DD HH:mm:ss）+ 地址（换行显示）
   - 返回新的临时文件路径

4. components/watermark-camera/（水印相机组件）
   - 触发 wx.chooseMedia 拍照
   - 同时调用 wx.getLocation 获取坐标
   - 调用腾讯地图逆地理编码 API 将坐标转为文字地址
     （KEY 从 app.js 全局配置读取：app.globalData.mapKey）
   - 调用 watermark.js 生成水印图
   - 触发自定义事件 bind:photoTaken，传出 { filePath, address, lat, lng }
   - 注意：wx.getLocation 需在 app.json 中声明 permission，提供完整配置

5. components/sign-canvas/（签名板组件）
   - Canvas 监听 touchstart/touchmove/touchend 绘制笔迹
   - 线条颜色黑色，线宽 3px，平滑连线
   - 「清除」按钮：重置画布
   - 「确认」按钮：调用 wx.canvasToTempFilePath 导出 PNG
   - 触发事件 bind:signed，传出临时文件路径
   - 透明背景导出

6. pages/login/（登录页）
   - 账号密码输入框 + 登录按钮
   - 调用 POST /auth/login，成功后存 token 和用户信息到 Storage
   - 跳转到任务大厅

7. pages/task-list/（任务大厅）
   - 调用 GET /orders/my 获取当前工程师的工单列表
   - 卡片展示：客户名 / 设备名 / 计划日期 / 状态
   - 状态用颜色区分：待处理=橙色，进行中=蓝色，已完成=绿色
   - 点击卡片进入 task-detail 页

8. pages/task-detail/（工单详情）
   - 展示工单完整信息
   - 「开始打卡」按钮：调用 watermark-camera 组件拍到场照
     拍完后调用 PUT /orders/{id}/checkin 接口
   - 打卡成功后显示「开始检查」按钮，进入 inspection 页

9. pages/inspection/（检查填单）
   - onLoad 时从后端拉取检查模板，同时存入 Storage 作为离线备份
   - 离线时从 Storage 读取模板（飞行模式也能打开）
   - 渲染检查项列表，每项支持「正常/异常」切换
   - 选「异常」时，展开：原因文本框（必填）+ watermark-camera 按钮（可拍照）
   - 所有填写内容实时存入 Storage（防意外退出丢失）
   - 底部「提交」按钮：校验所有必填项 → 跳转到签名页

10. pages/signature/（客户签名页）
    - 展示工单摘要信息
    - 嵌入 sign-canvas 组件让客户签名
    - 「确认提交」按钮：
      a. 将签名图片上传到后端（POST /upload 接口，先把接口也写了）
      b. 调用 PUT /orders/{id}/complete 提交工单
      c. 成功后显示「提交成功」并返回任务大厅

注意：
- 所有页面均需处理网络失败的情况，显示友好错误提示
- app.json 需配置所有页面路径和必要权限
- 使用微信小程序原生语法（WXML/WXSS/JS），不用 uni-app
```

---

### 模块06：e签宝接入

**粘贴以下内容给 Cursor AI：**

```
本次任务：实现后端 e签宝电子签名接入 和 文件上传接口。

1. 新建 backend/services/cos_service.py（腾讯云COS上传）
   - upload_file(local_path: str, cos_key: str) -> str
     上传文件到COS，返回公开访问URL
   - upload_bytes(data: bytes, cos_key: str, content_type: str) -> str
     上传字节流（用于上传签名PNG）
   - 从 config.settings 读取 COS_SECRET_ID / COS_SECRET_KEY / COS_BUCKET / COS_REGION
   - 安装依赖：cos-python-sdk-v5

2. 新建 backend/services/esign_service.py（e签宝签署）
   - complete_esign(order_id: int, pdf_path: str, signer_name: str, db: Session) -> str
     完整流程：上传文件→创建签署流程→返回签署证书URL
   - 当 config.settings.ESIGN_MOCK == True 时：
     跳过真实API调用，直接返回 "https://mock-esign.example.com/cert/{order_id}"
     并将此URL更新到 work_orders.esign_cert_url
   - 真实调用时对接 e签宝开放平台 API（v3版本）
   - 网络请求失败时重试3次，全部失败记录错误日志后抛出异常

3. 新建 backend/routers/upload.py（文件上传接口）
   - POST /api/v1/upload/image
     接收 multipart/form-data 图片文件
     压缩到800KB以下（使用Pillow）
     上传到COS，返回 { url: "https://..." }
   - POST /api/v1/upload/sign
     接收签名PNG文件（透明背景）
     直接上传到COS，返回 { url: "https://..." }
   - 文件大小限制：10MB
   - 支持格式：jpg/jpeg/png/webp

4. 在 main.py 中注册 upload 路由

5. 在 tests/ 中新建 test_upload_esign.py
   测试：Mock模式下 complete_esign 正常返回URL
   测试：上传接口返回正确的URL格式

注意：
- Pillow 安装：pip install Pillow
- e签宝 Mock 模式默认开启（ESIGN_MOCK=true in .env）
- COS 如果没配置密钥，上传接口返回本地文件路径作为 fallback（开发阶段用）
```

---

### 模块07：PDF报告生成

**粘贴以下内容给 Cursor AI：**

```
本次任务：实现 PDF 维保报告自动生成。

1. 安装依赖
   pip install weasyprint jinja2
   （WeasyPrint 在 Windows 上需要先安装 GTK，说明见下方）

2. 新建 backend/templates/report_maintenance.html（Jinja2模板）
   报告包含以下区域：
   - 报告头：公司名称（右上角）、报告编号、生成时间
   - 设备信息表：设备名称、型号、安装位置、客户公司、负责联系人
   - 检查结果表格：检查项 | 结果（正常✓/异常✗） | 异常备注
   - 现场照片：最多6张，2列排版，图片下方显示水印中的时间地址
   - 结论与建议：工程师文字说明区域
   - 签名区：左侧工程师姓名+日期，右侧「客户签名」图片（base64嵌入）
   - 公章区：右下角叠加公章PNG（size约2×2cm）
   - 页脚：e签宝认证编号 | 第X页/共X页
   CSS 要求：
   - 字体：font-family: "Microsoft YaHei", "SimHei", "Arial", sans-serif
   - A4纸尺寸：@page { size: A4; margin: 1.5cm; }
   - 表格有边框，标题行深蓝底色白字
   - 照片最大宽度不超过列宽，高度自适应

3. 新建 backend/services/pdf_service.py
   - generate_maintenance_report(order_id: int, db: Session) -> str
     a. 从数据库查询工单完整数据（含设备/客户/检查数据）
     b. 从 photo_urls 下载照片并转为 base64（嵌入HTML，不依赖外部路径）
     c. 签名图片从 sign_url 下载转为 base64
     d. 用 Jinja2 渲染 report_maintenance.html
     e. WeasyPrint 将 HTML 转为 PDF 字节
     f. 上传 PDF 到 COS（调用 cos_service.upload_bytes）
     g. 更新 work_orders.pdf_report_url
     h. 返回 PDF 的 COS URL
   
   - 异常处理：照片下载失败时用占位图代替，不中断整个报告生成

4. 在 services/order_service.py 的 complete_order() 中，
   取消 TODO 注释，启用 BackgroundTasks 异步触发 PDF 生成：
   background_tasks.add_task(pdf_service.generate_maintenance_report, order_id, db)

5. 新建 backend/routers/report.py
   GET /api/v1/orders/{id}/report
   - 返回 { pdf_url: "...", esign_cert_url: "..." }
   - 如果PDF尚未生成（pdf_report_url为空），返回 { status: "generating" }

6. 在 tests/ 中新建 test_pdf.py
   测试：给定 mock 工单数据，generate_maintenance_report 能生成有效PDF字节
   （不上传COS，直接检查返回的字节长度>1000）

Windows 安装 WeasyPrint 说明（告诉用户）：
WeasyPrint 需要 GTK 运行库，Windows 上需要额外安装：
1. 下载 GTK3 Runtime for Windows：https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
2. 安装后重启 Cursor/终端
3. 然后 pip install weasyprint 才能正常使用
```

---

### 模块08：PC管理后台

**粘贴以下内容给 Cursor AI：**

```
本次任务：使用 Vue3 + Element Plus 开发 PC 管理后台。

在 crane-mms 根目录下新建 frontend-pc/ 目录。

技术栈：
- Vue 3 (Composition API + <script setup>)
- Element Plus
- Pinia（状态管理）
- Vue Router 4
- Axios
- Vite

初始化命令：
npm create vue@latest frontend-pc
（选择：Vue Router ✓, Pinia ✓，其他选 No）
cd frontend-pc && npm install element-plus axios

需要实现的页面和功能：

1. src/utils/request.js（Axios 封装）
   - baseURL: http://localhost:8000/api/v1
   - 请求拦截：自动加 Authorization: Bearer {token}
   - 响应拦截：code !== 200 时 ElMessage.error(msg)；401 跳登录页

2. src/stores/auth.js（Pinia）
   - state: { token, user }
   - actions: login(username, password), logout()
   - token 同步存 localStorage

3. src/router/index.js
   - 路由守卫：无 token 跳转 /login
   - TECH 角色只能访问 /orders（无客户/设备管理菜单）

4. src/views/LoginView.vue
   - 账号密码表单 + 登录按钮
   - 调用 auth store 的 login()
   - 登录成功跳 /

5. src/views/layout/AppLayout.vue（整体布局）
   - 左侧菜单：客户管理 / 设备档案 / 工单中心
   - 顶部：当前登录人姓名 + 角色 + 退出按钮
   - 右侧内容区（router-view）

6. src/views/customers/CustomerList.vue
   - 表格：公司名 / 主联系人 / 联系电话 / 操作
   - 顶部：搜索框 + 新建客户按钮
   - 新建客户：抽屉(El-Drawer)表单，含动态增减联系人行
   - 点击公司名 → 跳转 CustomerDetail

7. src/views/customers/CustomerDetail.vue
   - 展示客户信息（卡片形式）
   - 下方设备列表（表格）
   - 右上角「新建设备」按钮 → 跳转 EquipmentForm

8. src/views/equipments/EquipmentForm.vue（新建/编辑设备）
   - 设备大类下拉（桥式起重机/门式起重机/悬臂起重机）
   - 型式下拉（联动大类）
   - 基础参数输入：吨位、跨度、起升高度、工作级别、安装位置
   - 「智能填充部件清单」按钮：
     调用 GET /equipments/templates?category=&model_type=
     返回结果填入下方可编辑表格（支持增删改行）
   - 特检信息：上次/下次特检日期（日期选择器）
   - 质保到期日
   - 提交调用 POST /equipments

9. src/views/orders/OrderList.vue（工单中心）
   - 顶部标签页快速筛选：全部/待处理/进行中/已完成
   - 表格：客户名/设备名/工程师/计划日期/状态（彩色标签）/操作
   - 「新建派单」按钮 → 弹窗（El-Dialog）：
     选客户（下拉）→ 选设备（联动）→ 选工程师（只显示TECH角色）→ 选日期
   - 操作列：「查看详情」按钮

10. src/views/orders/OrderDetail.vue（工单详情）
    - 工单基本信息卡片
    - 打卡信息（时间 + 地址 + 打卡照片）
    - 现场照片瀑布流（El-Image 支持预览）
    - 客户签名预览
    - 已完成工单显示「下载PDF报告」按钮（a href=pdf_url target=_blank）
    - 待处理工单显示「转派」按钮

注意：
- 所有 API 调用封装到 src/api/ 目录，按模块分文件
- 使用 <script setup> + Composition API，不用 Options API
- 响应式设计，最小支持 1280px 宽度
- 所有表格支持 loading 状态
```

---

### 模块09：集成测试 + Windows 部署

**粘贴以下内容给 Cursor AI：**

```
本次任务：编写集成测试并生成 Windows Server 2025 部署脚本。

1. 新建 backend/tests/test_integration.py
   完整端到端测试，按顺序执行：
   - 用 admin 登录
   - 创建客户（含2个联系人）
   - 创建设备（含部件清单）
   - 以 manager 身份派单给 tech
   - 以 tech 身份打卡（checkin）
   - 以 tech 身份提交工单（含mock照片URL和签名URL）
   - 断言工单状态=已完成
   - 断言 pdf_report_url 字段有值（Mock模式下也应有）
   - 清理所有测试数据

2. 新建 deploy/start.bat（Windows 启动脚本）
   @echo off
   cd /d %~dp0\..\backend
   call uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
   （放在 deploy/ 目录下）

3. 新建 deploy/install_service.bat（注册为Windows服务，需管理员运行）
   使用 nssm 将后端注册为系统服务，开机自启
   包含注释说明 nssm 的下载地址

4. 新建 deploy/nginx.conf（nginx反向代理配置示例）
   - /api/ → 代理到 localhost:8000
   - / → 指向 frontend-pc/dist/ 目录
   - 包含 gzip 压缩配置
   - 包含静态资源缓存配置

5. 新建 deploy/DEPLOY_GUIDE.md（部署步骤说明文档）
   - 环境要求清单
   - 分步骤说明（从零到可访问）
   - 常见问题排查

6. 更新 backend/tests/test_integration.py
   运行命令：pytest tests/test_integration.py -v
   必须 100% 通过才算部署就绪

最终验收：
所有测试（test_core.py + test_integration.py）全部通过
```

---

## 快速排查指南

| 现象 | 先看这里 | 排查命令 |
|------|---------|---------|
| API 返回 500 | `services/` 对应文件 | 看 uvicorn 控制台的完整报错栈 |
| API 返回 401 | `core/security.py` | 检查 Token 是否过期，重新登录 |
| API 返回 403 | `core/permissions.py` | 检查当前用户角色是否在 require_role 列表 |
| 小程序数据不同步 | `utils/offline-queue.js` | 微信开发者工具 → Storage 面板查看队列 |
| PDF 生成失败 | `services/pdf_service.py` | 检查 WeasyPrint GTK 是否安装 |
| e签宝失败 | `services/esign_service.py` | 检查 .env 中 ESIGN_MOCK=true 是否生效 |
| 数据库连接失败 | `.env` 文件 | 检查 DATABASE_URL 格式和密码是否正确 |
| 前端 401 循环跳转 | `src/utils/request.js` | 检查 localStorage 中 token 是否存在 |

---

## 数据库管理

### 重置数据库（开发阶段）
```bash
cd backend
python seed_data.py
# 注意：此命令会清空所有数据！
```

### 修改表结构（生产环境用 Alembic）
```bash
# 1. 修改 models/ 中的模型
# 2. 生成迁移脚本
alembic revision --autogenerate -m "描述这次改了什么"
# 3. 执行迁移
alembic upgrade head
# 4. 回滚（如果有问题）
alembic downgrade -1
```

---

## 登录账号（测试用）

| 账号 | 密码 | 角色 | 权限 |
|------|------|------|------|
| admin | Admin@123 | ADMIN | 看所有数据，做所有操作 |
| manager01 | Manager@123 | MANAGER | 只看自己名下的客户/工单 |
| tech01 | Tech@123 | TECH | 只看分配给自己的工单 |
