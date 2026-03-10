import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '客户登录' }
  },
  {
    path: '/',
    name: 'OrderList',
    component: () => import('../views/OrderList.vue'),
    meta: { title: '我的维保工单', requiresAuth: true }
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('../views/OrderDetail.vue'),
    meta: { title: '工单详情', requiresAuth: true }
  },
  {
    path: '/sign/:id',
    name: 'OrderSign',
    component: () => import('../views/OrderSign.vue'),
    meta: { title: '确认签字', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }

  const token = localStorage.getItem('portal_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
