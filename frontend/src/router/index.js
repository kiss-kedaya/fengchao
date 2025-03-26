import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import VerificationCode from '../views/VerificationCode.vue'
import Orders from '../views/Orders.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/verification',
    name: 'Verification',
    component: VerificationCode
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || ''),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('authorization')
  
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    // 如果需要登录的页面且未登录，重定向到登录页
    next({ name: 'Login' })
  } else if (to.name === 'Login' && isAuthenticated) {
    // 如果已登录且访问登录页，重定向到订单页
    next({ name: 'Orders' })
  } else {
    next()
  }
})

export default router 