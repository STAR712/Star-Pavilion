<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar :is-visible="true" />
    <div class="h-14"></div>

    <div class="max-w-4xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-8">排行榜</h1>

      <!-- 分类标签 -->
      <div class="flex space-x-2 mb-6 overflow-x-auto pb-2">
        <button
          v-for="cat in categoryTabs"
          :key="cat.key"
          class="px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors"
          :class="activeCategory === cat.key ? 'bg-indigo-500 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'"
          @click="switchCategory(cat.key)"
        >
          {{ cat.name }}
        </button>
      </div>

      <!-- 排行列表 -->
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div v-if="loading" class="text-center py-16 text-gray-400">加载中...</div>
        <div v-else-if="books.length === 0" class="text-center py-16 text-gray-400">暂无数据</div>
        <div v-else>
          <div
            v-for="(book, index) in books"
            :key="book.id"
            class="flex items-center px-6 py-4 border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors cursor-pointer"
            @click="$router.push(`/book/${book.id}`)"
          >
            <!-- 排名 -->
            <div class="w-10 flex-shrink-0">
              <span
                v-if="index < 3"
                class="inline-flex items-center justify-center w-7 h-7 rounded-full text-white text-sm font-bold"
                :class="rankColors[index]"
              >
                {{ index + 1 }}
              </span>
              <span v-else class="inline-flex items-center justify-center w-7 h-7 text-gray-400 text-sm font-bold">
                {{ index + 1 }}
              </span>
            </div>

            <!-- 封面缩略图 -->
            <div class="w-12 h-16 rounded overflow-hidden flex-shrink-0 mx-4">
              <div
                v-if="!book.cover_url"
                class="w-full h-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center"
              >
                <span class="text-white text-xs font-bold px-1 text-center leading-tight">{{ book.title.slice(0, 2) }}</span>
              </div>
              <img v-else :src="book.cover_url" :alt="book.title" class="w-full h-full object-cover" />
            </div>

            <!-- 书籍信息 -->
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-medium text-gray-900 truncate">{{ book.title }}</h3>
              <p class="text-xs text-gray-500 mt-1">{{ book.author }}</p>
              <div class="flex items-center space-x-4 mt-1">
                <span class="text-xs text-gray-400">{{ book.category }}</span>
                <span class="text-xs text-gray-400">{{ formatWordCount(book.word_count) }}</span>
                <span class="text-xs" :class="book.status === '已完结' ? 'text-green-500' : 'text-orange-500'">
                  {{ book.status }}
                </span>
              </div>
            </div>

            <!-- 数据 -->
            <div class="flex-shrink-0 text-right ml-4">
              <p class="text-sm font-medium text-red-500">{{ formatReadCount(book.read_count) }}</p>
              <p class="text-xs text-gray-400">阅读量</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getBooks } from '@/api'
import NavBar from '@/components/NavBar.vue'

const categoryTabs = [
  { name: '全部', key: '' },
  { name: '玄幻', key: '玄幻' },
  { name: '都市', key: '都市' },
  { name: '科幻', key: '科幻' },
  { name: '历史', key: '历史' },
  { name: '言情', key: '言情' },
  { name: '悬疑', key: '悬疑' },
]

const rankColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500']

const activeCategory = ref('')
const loading = ref(true)
const books = ref<any[]>([])

function formatWordCount(count?: number): string {
  if (!count) return '0字'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万字'
  return count + '字'
}

function formatReadCount(count?: number): string {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万'
  return count.toString()
}

async function loadBooks() {
  loading.value = true
  try {
    const params: any = { page: 1, size: 20 }
    if (activeCategory.value) {
      params.category = activeCategory.value
    }
    const { data } = await getBooks(params)
    // 按阅读量排序
    books.value = (data.books || []).sort((a: any, b: any) => (b.read_count || 0) - (a.read_count || 0))
  } catch (e) {
    console.error('加载排行失败:', e)
  } finally {
    loading.value = false
  }
}

function switchCategory(key: string) {
  activeCategory.value = key
  loadBooks()
}

onMounted(() => {
  loadBooks()
})
</script>
