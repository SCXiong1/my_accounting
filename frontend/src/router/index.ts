import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginPage.vue'),
    },
    {
      path: '/pin-change',
      name: 'pin-change',
      component: () => import('../views/PinChangePage.vue'),
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

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.user) {
    try {
      await auth.fetchProfile()
    } catch {
      return { name: 'login' }
    }
  }

  if (!auth.user && to.meta.requiresAuth) {
    return { name: 'login' }
  }

  if (to.name === 'login' && auth.user) {
    if (auth.mustChangePin) {
      return { name: 'pin-change' }
    }
    return { name: 'home' }
  }

  if (to.meta.requiresAuth && auth.mustChangePin && to.name !== 'pin-change') {
    return { name: 'pin-change' }
  }
})

export default router
