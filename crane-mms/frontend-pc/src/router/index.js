import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AppLayout from '../views/layout/AppLayout.vue'
import CustomerList from '../views/customers/CustomerList.vue'
import CustomerDetail from '../views/customers/CustomerDetail.vue'
import EquipmentForm from '../views/equipments/EquipmentForm.vue'
import OrderList from '../views/orders/OrderList.vue'
import OrderDetail from '../views/orders/OrderDetail.vue'
import UserList from '../views/system/UserList.vue'
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
          redirect: '/orders'
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
          path: 'orders/:id',
          name: 'orderDetail',
          component: OrderDetail
        },
        {
          path: 'system/users',
          name: 'userList',
          component: UserList,
          meta: { requiresRole: ['ADMIN'] }
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