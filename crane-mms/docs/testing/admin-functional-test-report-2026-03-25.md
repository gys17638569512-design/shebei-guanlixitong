# 管理端功能测试报告（管理员视角）- 2026-03-25

## 1. 测试范围
- 测试对象：管理端 Web（生产环境）
- 基础地址：`http://47.95.157.135`
- 登录页：`http://47.95.157.135/login`
- 账号角色：`admin`（系统管理员）
- 覆盖模块：
  - 登录/退出
  - 控制看板
  - 客户管理（列表、搜索、新建客户抽屉打开/取消）
  - 设备档案
  - 工单中心
  - 维修工单
  - 批量排期
  - 备件库
  - 设备模板中心
  - 权限管理
  - 平台品牌配置
  - 安全审计
  - 报告集中

## 2. 测试环境与执行方式
- 执行日期：2026-03-25（Asia/Shanghai）
- 环境类型：生产环境（只读优先）
- 自动化方式：Playwright CLI（真实浏览器会话）
- 账号与凭据：
  - 用户名：`admin`
  - 密码：`Admin@2026!`
- 数据安全策略：
  - 未执行创建/删除/修改真实业务数据
  - 仅在客户管理执行“打开新建客户抽屉 -> 校验字段 -> 取消退出”

### 自动化工具说明
- 本机 `npx` 可用；`playwright` skill wrapper 为 `.sh` 脚本，当前 Windows 环境无可用 `bash/WSL`。
- 使用等价命令继续执行：`npx --package @playwright/cli playwright-cli ...`。

## 3. 测试结果汇总

| 模块 | 结果 | 结论摘要 |
|---|---|---|
| 登录/退出 | 通过 | 登录成功跳转 `/dashboard`；退出后返回 `/login` |
| 控制看板 | 通过 | 页面可访问，核心接口 200 |
| 客户管理 | 通过 | 列表/搜索正常；新建客户弹窗可打开并取消，无写入 |
| 设备档案 | 通过 | 页面可访问，接口 200 |
| 工单中心 | 通过 | 页面可访问，接口 200 |
| 维修工单 | 通过 | 页面可访问，接口 200 |
| 批量排期 | 通过 | 页面可访问，接口 200 |
| 备件库 | 通过 | 页面可访问，接口 200 |
| 设备模板中心 | 通过 | 页面可访问，接口 200 |
| 权限管理 | 通过 | 页面可访问，接口 200 |
| 平台品牌配置 | 通过 | 页面可访问，接口 200 |
| 安全审计 | 通过 | 页面可访问，接口 200 |
| 报告集中 | 失败 | 核心接口 `GET /api/v1/orders/reports/archive` 返回 500 |

**汇总：** 13 个模块/流程中，12 项通过，1 项失败（报告集中）。

## 4. 逐模块结果（含关键证据）

1. 登录/退出
- 登录：`POST /api/v1/auth/login` 返回 200，成功进入 `/dashboard`。
- 退出：点击“退出登录”后返回 `/login`。
- 证据：`13-logout-login-page.png`。

2. 控制看板（`/dashboard`）
- 页面可正常加载。
- 接口：`/api/v1/stats/dashboard`、`/api/v1/stats/notifications`、`/api/v1/users/me` 均为 200。
- 证据：`01-dashboard.png`、`01-dashboard-network.log`。

3. 客户管理（`/customers`）
- 列表页可访问，空数据态展示正常。
- 搜索框输入“测试客户”并点击搜索，流程正常。
- 点击“新建客户”可打开表单抽屉，校验字段后点击“取消”成功退出，未保存数据。
- 证据：`02-customers.png`、`02-customers-new-dialog.png`、`02-customers-network.log`。

4. 设备档案（`/equipments`）
- 页面可访问，相关接口 200。
- 证据：`03-equipments.png`、`03-equipments-network.log`。

5. 工单中心（`/orders`）
- 页面可访问，相关接口 200。
- 证据：`04-orders.png`、`04-orders-network.log`。

6. 维修工单（`/repairs`）
- 页面可访问，相关接口 200。
- 证据：`05-repairs.png`、`05-repairs-network.log`。

7. 批量排期（`/orders/batch`）
- 页面可访问，相关接口 200。
- 证据：`06-orders-batch.png`、`06-orders-batch-network.log`。

8. 备件库（`/system/parts`）
- 页面可访问，相关接口 200。
- 证据：`07-parts.png`、`07-parts-network.log`。

9. 设备模板中心（`/equipment-templates`）
- 页面可访问，相关接口 200。
- 证据：`08-equipment-templates.png`、`08-equipment-templates-network.log`。

10. 权限管理（`/system/employees`）
- 页面可访问，相关接口 200。
- 证据：`09-permissions.png`、`09-permissions-network.log`。

11. 平台品牌配置（`/system/brand-config`）
- 页面可访问，相关接口 200。
- 证据：`10-brand-config.png`、`10-brand-config-network.log`。

12. 安全审计（`/system/audit`）
- 页面可访问，相关接口 200。
- 证据：`11-audit.png`、`11-audit-network.log`。

13. 报告集中（`/system/reports`）
- 页面可访问，但核心归档接口请求失败。
- 接口异常：`GET /api/v1/orders/reports/archive` -> `500 Internal Server Error`。
- 前端控制台同步出现 error（Failed to load resource 500）。
- 证据：`12-reports.png`、`12-reports-network.log`、`12-reports-console-error.log`。

## 5. 发现的问题（Findings）

### F-001 报告集中接口 500（高优先级）
- 模块：报告集中
- 现象：页面加载时请求归档数据接口失败，返回 500。
- 请求：`GET http://47.95.157.135/api/v1/orders/reports/archive`
- 实际结果：`500 Internal Server Error`
- 影响：管理员无法正常查看报告归档数据，影响报告集中模块核心可用性。
- 证据：
  - `output/playwright/admin-functional-test-2026-03-25/12-reports-network.log`
  - `output/playwright/admin-functional-test-2026-03-25/12-reports-console-error.log`

## 6. 风险与建议
- 风险 1：报告集中接口 500 导致管理端报告归档不可用，可能影响运维追踪、审计留痕与客户交付闭环。
- 风险 2：当前环境业务数据较少（多处空数据态），部分“有数据场景”交互（详情页、导出、筛选联动）未完全覆盖。
- 建议：
  - 优先修复 `GET /api/v1/orders/reports/archive` 的后端异常并回归管理端页面展示。
  - 在隔离测试环境准备标准样例数据（客户/设备/工单/报告），补充“有数据场景”回归。
  - 对报告模块增加接口健康监控与错误告警，避免生产端静默失败。

## 7. 产物路径
- 测试报告：
  - `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\docs\testing\admin-functional-test-report-2026-03-25.md`
- Playwright 证据目录：
  - `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\output\playwright\admin-functional-test-2026-03-25\`

## 8. 修复回归补充（2026-03-25）

- 修复内容：
  - 后端 `GET /api/v1/orders/reports/archive` 原先引用了不存在的 `WorkOrder.completed_at`，已改为按 `updated_at`/`created_at` 作为归档时间来源。
  - 已新增回归测试：`backend/tests/test_report_archive.py`。
- 本地验证：
  - 命令：`python -m pytest tests/test_report_archive.py tests/test_smoke.py -q`
  - 结果：`3 passed`
- 生产部署：
  - 仅同步 `backend/routers/report.py`
  - 仅重建 `backend` 服务
- 生产回归结果：
  - `GET http://47.95.157.135/api/v1/orders/reports/archive` -> `200`
  - `http://47.95.157.135/system/reports` 页面可正常打开
  - 当前生产环境为空数据场景，表头与空态渲染正常，无 500、无控制台错误
- 结论更新：
  - 原问题 `F-001 报告集中接口 500` 已修复并完成回归
  - 管理端本轮已覆盖模块恢复为 `13/13 通过`
- 回归证据：
  - `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\output\playwright\admin-functional-test-2026-03-25-retest-reports\reports-page.png`
  - `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\output\playwright\admin-functional-test-2026-03-25-retest-reports\reports-network.log`
  - `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\output\playwright\admin-functional-test-2026-03-25-retest-reports\reports-console-error.log`
