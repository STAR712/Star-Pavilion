<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <NavBar :is-visible="navVisible" />

    <!-- 顶部占位 -->
    <div class="h-14"></div>

    <!-- 轮播图区域 -->
    <section class="max-w-7xl mx-auto px-4 mt-6">
      <div class="relative rounded-2xl overflow-hidden h-48 sm:h-64 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500">
        <div class="absolute inset-0 flex items-center px-8 sm:px-16">
          <div class="text-white">
            <h2 class="text-2xl sm:text-3xl font-bold mb-2">AI 智能阅读</h2>
            <p class="text-white/80 text-sm sm:text-base mb-4">沉浸式阅读体验，AI 助手随时为你解答</p>
            <button
              class="bg-white text-indigo-600 px-6 py-2 rounded-full text-sm font-medium hover:bg-white/90 transition-colors"
              @click="$router.push('/book/1')"
            >
              立即体验
            </button>
          </div>
        </div>
        <!-- 装饰元素 -->
        <div class="absolute right-0 top-0 w-1/3 h-full opacity-20">
          <svg viewBox="0 0 200 200" class="w-full h-full">
            <circle cx="100" cy="100" r="80" fill="white" />
            <circle cx="150" cy="50" r="40" fill="white" />
          </svg>
        </div>
      </div>
    </section>

    <!-- 我的书架 -->
    <section class="max-w-7xl mx-auto px-4 mt-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">我的书架</h2>
        <router-link to="/" class="text-sm text-indigo-600 hover:text-indigo-700">查看全部</router-link>
      </div>
      <div v-if="bookshelfStore.loading" class="text-center py-8 text-gray-400">加载中...</div>
      <div v-else-if="bookshelfStore.books.length === 0" class="text-center py-8 text-gray-400">
        书架空空如也，去逛逛吧
      </div>
      <div v-else class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-4">
        <BookCard
          v-for="item in bookshelfStore.books.slice(0, 6)"
          :key="item.book_id"
          :book="{
            id: item.book_id,
            title: item.book_title,
            author: item.book_author,
            cover_url: item.book_cover_url,
          }"
        />
      </div>
    </section>

    <!-- 分类推荐 -->
    <section v-for="cat in categories" :key="cat.name" class="max-w-7xl mx-auto px-4 mt-8">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center space-x-2">
          <span class="w-1 h-5 bg-indigo-500 rounded-full"></span>
          <h2 class="text-lg font-bold text-gray-900">{{ cat.name }}</h2>
        </div>
        <button
          class="text-sm text-gray-500 hover:text-indigo-600 transition-colors"
          @click="loadCategory(cat.key)"
        >
          换一批
        </button>
      </div>
      <div v-if="cat.loading" class="text-center py-8 text-gray-400">加载中...</div>
      <div v-else class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-4">
        <BookCard
          v-for="book in cat.books"
          :key="book.id"
          :book="book"
        />
      </div>
    </section>

    <!-- 底部 -->
    <footer class="max-w-7xl mx-auto px-4 py-12 mt-12 border-t border-gray-200">
      <div class="text-center text-sm text-gray-400">
        <p>AI小说阅读平台 - 沉浸式阅读体验</p>
        <p class="mt-1">Powered by Vue3 + FastAPI + AI</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useScroll } from '@/composables/useScroll'
import { getBooks } from '@/api'
import { useBookshelfStore } from '@/stores/bookshelf'
import NavBar from '@/components/NavBar.vue'
import BookCard from '@/components/BookCard.vue'

const { isVisible: navVisible } = useScroll()
const bookshelfStore = useBookshelfStore()

const categories = reactive([
  { name: '玄幻推荐', key: '玄幻', books: [] as any[], loading: false },
  { name: '都市热门', key: '都市', books: [] as any[], loading: false },
  { name: '科幻经典', key: '科幻', books: [] as any[], loading: false },
  { name: '历史佳作', key: '历史', books: [] as any[], loading: false },
  { name: '言情治愈', key: '言情', books: [] as any[], loading: false },
  { name: '悬疑烧脑', key: '悬疑', books: [] as any[], loading: false },
])

async function loadCategory(key: string) {
  const cat = categories.find(c => c.key === key)
  if (!cat) return
  cat.loading = true
  try {
    const { data } = await getBooks({ category: key, page: 1, size: 6 })
    cat.books = data.books || []
  } catch (e) {
    console.error('加载分类失败:', e)
  } finally {
    cat.loading = false
  }
}

async function loadAllCategories() {
  for (const cat of categories) {
    await loadCategory(cat.key)
  }
}

onMounted(async () => {
  bookshelfStore.fetchBookshelf()
  await loadAllCategories()
})
</script>
