# Settings Permission Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bottom "设置" navigation zone, rename the employee center to "权限管理", and introduce role-default plus per-user override permissions for the five settings modules.

**Architecture:** Store role defaults and user overrides in dedicated backend tables, compute effective permissions on the server, return them in auth and user payloads, and let the frontend render navigation, route access, and page actions from those effective permissions. Keep settings permission scope limited to the five requested settings modules so business flows like equipment creation are not blocked.

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, Pinia, Element Plus, pytest

---

### Task 1: Lock permission behavior with backend tests

**Files:**
- Create: `backend/tests/test_settings_permission_management.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run `pytest backend/tests/test_settings_permission_management.py -q` and confirm the new tests fail for missing permission tables/endpoints**
- [ ] **Step 3: Implement only the minimum backend code required to satisfy the tests**
- [ ] **Step 4: Re-run the focused permission test file until it passes**

### Task 2: Add backend permission catalog and persistence

**Files:**
- Create: `backend/core/permission_catalog.py`
- Create: `backend/models/access_control.py`
- Create: `backend/schemas/permission.py`
- Create: `backend/services/permission_service.py`
- Modify: `backend/models/__init__.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Define the five settings modules and their page/action/module permission keys**
- [ ] **Step 2: Add SQLAlchemy models for role default permissions and user permission overrides**
- [ ] **Step 3: Add schema objects for catalog, role template updates, and user override updates**
- [ ] **Step 4: Implement effective permission resolution and role-template seeding**

### Task 3: Wire permission-aware auth and user APIs

**Files:**
- Modify: `backend/core/permissions.py`
- Modify: `backend/services/auth.py`
- Modify: `backend/schemas/user.py`
- Modify: `backend/services/user_service.py`
- Modify: `backend/routers/user.py`

- [ ] **Step 1: Add `require_permission` helpers that compute effective permissions**
- [ ] **Step 2: Return effective permissions and override metadata in login and `/users/me` payloads**
- [ ] **Step 3: Add permission-management endpoints for catalog, user detail, role defaults, and personal overrides**
- [ ] **Step 4: Replace hard-coded settings-role checks with permission checks where needed**

### Task 4: Reshape the sidebar into business plus settings navigation

**Files:**
- Modify: `frontend-pc/src/views/layout/AppLayout.vue`
- Modify: `frontend-pc/src/router/index.js`
- Modify: `frontend-pc/src/stores/auth.js`

- [ ] **Step 1: Add a bottom settings section that contains the five requested modules**
- [ ] **Step 2: Remove those modules from the business navigation area while keeping `备件库` in business navigation**
- [ ] **Step 3: Add permission-aware helpers to auth state and route guards**
- [ ] **Step 4: Refresh current-user permissions on app load so old sessions can still see the correct menu**

### Task 5: Turn employee center into permission management

**Files:**
- Modify: `frontend-pc/src/api/system.js`
- Modify: `frontend-pc/src/views/system/EmployeeCenter.vue`

- [ ] **Step 1: Expand the system API module with permission catalog and save endpoints**
- [ ] **Step 2: Rename the page copy from “员工账号中心” to “权限管理”**
- [ ] **Step 3: Keep the account list and CRUD actions, then add a detail drawer for account info and permissions**
- [ ] **Step 4: In the detail flow, show role defaults, personal overrides, and effective permissions for the selected employee**
- [ ] **Step 5: Allow editing the current role’s default permissions from inside the employee detail flow**

### Task 6: Apply permissions to settings-page actions and modules

**Files:**
- Modify: `frontend-pc/src/views/templates/EquipmentTemplateCenter.vue`
- Modify: `frontend-pc/src/views/system/BrandConfig.vue`
- Modify: `frontend-pc/src/views/system/AuditLog.vue`
- Modify: `frontend-pc/src/views/system/ReportArchive.vue`

- [ ] **Step 1: Hide or disable settings actions when the current user lacks the matching permission**
- [ ] **Step 2: Gate settings-page tabs or panels using module-level permissions where practical**
- [ ] **Step 3: Keep read-only access working when a user has page access but not edit permissions**

### Task 7: Verify the end-to-end result

**Files:**
- Test: `backend/tests/test_settings_permission_management.py`
- Test: `backend/tests/test_equipment_template_center.py`
- Test: `frontend-pc`

- [ ] **Step 1: Run `pytest tests/test_settings_permission_management.py -q`**
- [ ] **Step 2: Run `pytest tests/test_equipment_template_center.py -q` to catch permission regressions around template management**
- [ ] **Step 3: Run `npm run build` in `frontend-pc`**
- [ ] **Step 4: Summarize any warnings or remaining limits without overstating completion**
