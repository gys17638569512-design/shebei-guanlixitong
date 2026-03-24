# Command Center UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the admin UI into a deep-light mixed command-center experience, while preserving the existing business workflows and settings permission system.

**Architecture:** Keep the current Vue 3 + Element Plus data and route structure, but replace the visual shell with a unified design language: dark navigation, floating top command bar, deep focus panels, and modular light work surfaces. Refactor the main list pages into shared information patterns so the dashboard, customer, equipment, order, template, and permission pages feel like one coherent product.

**Tech Stack:** Vue 3, Pinia, Vue Router, Element Plus, Vite

---

### Task 1: Establish command-center design primitives

**Files:**
- Modify: `frontend-pc/src/style.css`

- [ ] Define page-level color tokens, elevation, gradients, surface styles, and utility layout classes.
- [ ] Add reusable command-center primitives for hero headers, metrics, toolbars, data surfaces, and split-panels.
- [ ] Restyle core Element Plus controls to match the new visual system.

### Task 2: Rebuild the application shell

**Files:**
- Modify: `frontend-pc/src/views/layout/AppLayout.vue`

- [ ] Replace the existing shell with a deeper mixed-tone workspace layout.
- [ ] Keep current route and permission behavior intact while restructuring the sidebar, settings zone, and topbar.
- [ ] Add contextual topbar metadata and a more productized navigation hierarchy.

### Task 3: Refactor primary operations pages

**Files:**
- Modify: `frontend-pc/src/views/Dashboard.vue`
- Modify: `frontend-pc/src/views/customers/CustomerList.vue`
- Modify: `frontend-pc/src/views/equipments/EquipmentList.vue`
- Modify: `frontend-pc/src/views/orders/OrderList.vue`

- [ ] Restructure each page into a consistent hero + KPI + workbench layout.
- [ ] Re-group information to better fit the new command-center IA without changing core actions.
- [ ] Keep existing API calls and business logic stable.

### Task 4: Refactor settings experience pages

**Files:**
- Modify: `frontend-pc/src/views/templates/EquipmentTemplateCenter.vue`
- Modify: `frontend-pc/src/views/system/EmployeeCenter.vue`

- [ ] Rework the template center into a stronger multi-panel management surface.
- [ ] Rework permission management into a more productized operations console while keeping role-default and override editing intact.
- [ ] Preserve the current permission-based visibility behavior.

### Task 5: Verify and preview

**Files:**
- Test: `frontend-pc`

- [ ] Run `npm run build` in `frontend-pc`.
- [ ] Generate local browser previews for the redesigned shell and key pages.
- [ ] Summarize remaining polish items or visual follow-ups.
