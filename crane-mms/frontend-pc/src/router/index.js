import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AppLayout from '../views/layout/AppLayout.vue'
import CustomerList from '../views/customers/CustomerList.vue'
import CustomerDetail from '../views/customers/CustomerDetail.vue'
import EquipmentForm from '../views/equipments/EquipmentForm.vue'
import EquipmentList from '../views/equipments/EquipmentList.vue'
import OrderList from '../views/orders/OrderList.vue'
import OrderDetail from '../views/orders/OrderDetail.vue'
import BatchSchedule from '../views/orders/BatchSchedule.vue'
import UserList from '../views/system/UserList.vue'
import PartList from '../views/system/PartList.vue'
import Dashboard from '../views/Dashboard.vue'
import { useAuthStore } from '../stores/auth'

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
          name: 'userList',
          component: UserList,
          meta: { requiresRole: ['ADMIN'] }
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
          meta: { requiresRole: ['ADMIN', 'MANAGER'] }
        },
        {
          path: 'system/audit',
          name: 'auditLog',
          component: () => import('../views/system/AuditLog.vue'),
          meta: { requiresRole: ['ADMIN'] }
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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.token) {
    next('/login')
  } else if (to.meta.requiresRole) {
    if (to.meta.requiresRole.includes(authStore.user?.role)) {
      next()
    } else {
      next('/orders')
    }
  } else {
    next()
  }
})

export default router