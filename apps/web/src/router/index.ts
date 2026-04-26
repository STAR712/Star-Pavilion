import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/HomePage.vue')
    },
    {
      path: '/book/:id',
      name: 'BookDetail',
      component: () => import('@/views/BookDetailPage.vue')
    },
    {
      path: '/library',
      name: 'Library',
      component: () => import('@/views/LibraryPage.vue')
    },
    {
      path: '/read/:bookId/:chapterNum',
      name: 'Reader',
      component: () => import('@/views/ReaderPage.vue')
    },
    {
      path: '/bookshelf',
      name: 'Bookshelf',
      component: () => import('@/views/BookshelfPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginPage.vue')
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/RegisterPage.vue')
    },
    {
      path: '/author',
      name: 'AuthorZone',
      component: () => import('@/views/AuthorZone.vue')
    },
    {
      path: '/rank',
      name: 'Ranking',
      component: () => import('@/views/RankPage.vue')
    }
  ]
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  await authStore.hydrateSession()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    return { path: '/' }
  }
})

export default router
