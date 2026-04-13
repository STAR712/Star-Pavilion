import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
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
      path: '/read/:bookId/:chapterNum',
      name: 'Reader',
      component: () => import('@/views/ReaderPage.vue')
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

export default router
