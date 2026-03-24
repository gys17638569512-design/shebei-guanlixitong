import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AppLayout from '../views/layout/AppLayout.vue'
import CustomerList from '../views/customers/CustomerList.vue'
import CustomerDetail from '../views/customers/CustomerDetail.vue'
import EquipmentForm from '../views/equipments/EquipmentForm.vue'
import EquipmentList from '../views/equipments/EquipmentList.vue'
import EquipmentTemplateCenter from '../views/templates/EquipmentTemplateCenter.vue'
import OrderList from '../views/orders/OrderList.vue'
import OrderDetail from '../views/orders/OrderDetail.vue'
import BatchSchedule from '../views/orders/BatchSchedule.vue'
import EmployeeCenter from '../views/system/EmployeeCenter.vue'
import BrandConfig from '../views/system/BrandConfig.vue'
import PartList from '../views/system/PartList.vue'
import Dashboard from '../views/Dashboard.vue'
import { useAuthStore } from '../stores/auth'
import { SETTINGS_PERMISSIONS } from '../constants/permissions'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: Dashboard,
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'customers',
          name: 'customers',
          component: CustomerList,
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'customers/:id',
          name: 'customerDetail',
          component: CustomerDetail,
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'equipments',
          name: 'equipmentList',
          component: EquipmentList,
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'equipments/form',
          name: 'equipmentForm',
          component: EquipmentForm,
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'equipments/form/:id',
          name: 'equipmentEdit',
          component: EquipmentForm,
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'equipment-templates',
          name: 'equipmentTemplateCenter',
          component: EquipmentTemplateCenter,
          meta: { requiresPermission: SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_ACCESS }
        },
        {
          path: 'orders',
          name: 'orders',
          component: OrderList
        },
        {
          path: 'orders/batch',
          name: 'orderBatch',
          component: BatchSchedule,
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'orders/:id',
          name: 'orderDetail',
          component: OrderDetail
        },
        {
          path: 'system/users',
          redirect: '/system/employees'
        },
        {
          path: 'system/employees',
          name: 'employeeCenter',
          component: EmployeeCenter,
          meta: { requiresPermission: SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_ACCESS }
        },
        {
          path: 'system/brand-config',
          name: 'brandConfig',
          component: BrandConfig,
          meta: { requiresPermission: SETTINGS_PERMISSIONS.BRAND_CONFIG_ACCESS }
        },
        {
          path: 'system/parts',
          name: 'partList',
          component: PartList,
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'system/reports',
          name: 'reportArchive',
          component: () => import('../views/system/ReportArchive.vue'),
          meta: { requiresPermission: SETTINGS_PERMISSIONS.REPORTS_ACCESS }
        },
        {
          path: 'system/audit',
          name: 'auditLog',
          component: () => import('../views/system/AuditLog.vue'),
          meta: { requiresPermission: SETTINGS_PERMISSIONS.AUDIT_ACCESS }
        },
        {
          path: 'repairs',
          name: 'repairList',
          component: () => import('../views/repairs/RepairList.vue'),
          meta: { requiresRole: ['ADMIN', 'MANAGER', 'TECH'] }
        },
        {
          path: 'repairs/:id',
          name: 'repairDetail',
          component: () => import('../views/repairs/RepairDetail.vue'),
          meta: { requiresRole: ['ADMIN', 'MANAGER', 'TECH'] }
        }
      ]
    }
  ]
})

const getDefaultRoute = (authStore) => {
  if (authStore.user?.role === 'TECH') {
    return '/repairs'
  }
  if (authStore.hasPermission(SETTINGS_PERMISSIONS.PERMISSION_MANAGEMENT_ACCESS)) {
    return '/system/employees'
  }
  if (authStore.hasPermission(SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_ACCESS)) {
    return '/equipment-templates'
  }
  if (authStore.hasPermission(SETTINGS_PERMISSIONS.REPORTS_ACCESS)) {
    return '/system/reports'
  }
  return '/dashboard'
}

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.token) {
    next('/login')
    return
  }

  if (requiresAuth && authStore.token && !authStore.user?.effective_permissions) {
    try {
      await authStore.fetchCurrentUser()
    } catch (error) {}
  }

  if (to.meta.requiresPermission) {
    const requiredPermissions = Array.isArray(to.meta.requiresPermission)
      ? to.meta.requiresPermission
      : [to.meta.requiresPermission]
    const permissionMatch = to.meta.permissionMatch || 'all'
    const passed = permissionMatch === 'any'
      ? authStore.hasAnyPermission(requiredPermissions)
      : authStore.hasAllPermissions(requiredPermissions)
    if (!passed) {
      next(getDefaultRoute(authStore))
      return
    }
  }

  if (to.meta.requiresRole && !to.meta.requiresPermission) {
    if (!to.meta.requiresRole.includes(authStore.user?.role)) {
      next(getDefaultRoute(authStore))
      return
    }
  }

  next()
})

export default router
