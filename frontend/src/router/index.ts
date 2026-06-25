import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../lib/token'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginPage.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterPage.vue'),
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/transactions',
      name: 'transactions',
      component: () => import('../views/TransactionListPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/transactions/add',
      name: 'transactionAdd',
      component: () => import('../views/TransactionFormPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/transactions/:id/edit',
      name: 'transactionEdit',
      component: () => import('../views/TransactionFormPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/categories',
      name: 'categories',
      component: () => import('../views/CategoryManagePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tags',
      name: 'tags',
      component: () => import('../views/TagManagePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('../views/StatisticsPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfilePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/trash',
      name: 'trash',
      component: () => import('../views/TrashPage.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

// 导航守卫：未登录 → /login
router.beforeEach((to, _from) => {
  const token = getToken()
  if (to.meta.requiresAuth && !token) {
    return { name: 'login' }
  }
  if ((to.name === 'login' || to.name === 'register') && token) {
    return { name: 'home' }
  }
})

export default router
