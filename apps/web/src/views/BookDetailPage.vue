<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <NavBar :is-visible="true" />
    <div class="h-14"></div>

    <!-- 加载中 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 书籍详情 -->
    <div v-else-if="book" class="max-w-4xl mx-auto px-4 py-8">
      <!-- 头部信息 -->
      <div class="bg-white rounded-2xl p-6 shadow-sm">
        <div class="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-8">
          <!-- 封面 -->
          <div class="flex-shrink-0 mx-auto sm:mx-0">
            <div class="w-48 h-64 rounded-xl overflow-hidden shadow-lg">
              <img
                v-if="book.cover_url"
                :src="book.cover_url"
                :alt="book.title"
                class="w-full h-full object-cover"
              />
              <div
                v-else
                class="w-full h-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center"
              >
                <span class="text-white text-xl font-bold px-4 text-center leading-tight">{{ book.title }}</span>
              </div>
            </div>
          </div>

          <!-- 信息 -->
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ book.title }}</h1>
            <div class="space-y-2 text-sm text-gray-600">
              <p>
                <span class="text-gray-400">作者：</span>
                <span class="text-gray-800">{{ book.author }}</span>
              </p>
              <p>
                <span class="text-gray-400">分类：</span>
                <span class="text-indigo-600">{{ book.category }}</span>
              </p>
              <p>
                <span class="text-gray-400">字数：</span>
                <span>{{ formatWordCount(book.word_count) }}</span>
              </p>
              <p>
                <span class="text-gray-400">状态：</span>
                <span :class="book.status === '已完结' ? 'text-green-600' : 'text-orange-500'">
                  {{ book.status }}
                </span>
              </p>
              <p>
                <span class="text-gray-400">阅读：</span>
                <span>{{ formatReadCount(book.read_count) }}</span>
              </p>
              <p>
                <span class="text-gray-400">推荐：</span>
                <span>{{ formatReadCount(book.recommend_count) }}</span>
              </p>
            </div>

            <!-- 操作按钮 -->
            <div class="flex space-x-3 mt-6">
              <button
                class="flex-1 h-10 bg-indigo-500 text-white rounded-lg font-medium hover:bg-indigo-600 transition-colors"
                @click="startReading"
              >
                开始阅读
              </button>
              <button
                class="h-10 px-6 border border-indigo-500 text-indigo-500 rounded-lg font-medium hover:bg-indigo-50 transition-colors"
                @click="handleAddBookshelf"
              >
                {{ isInBookshelf ? '已在书架' : '加入书架' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 简介 -->
        <div class="mt-6 pt-6 border-t border-gray-100">
          <h3 class="text-base font-bold text-gray-900 mb-3">作品简介</h3>
          <p class="text-sm text-gray-600 leading-relaxed">{{ book.description }}</p>
        </div>
      </div>

      <!-- 章节列表 -->
      <div class="bg-white rounded-2xl p-6 shadow-sm mt-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-bold text-gray-900">章节目录</h3>
          <span class="text-sm text-gray-400">共 {{ chapters.length }} 章</span>
        </div>
        <div v-if="chaptersLoading" class="text-center py-8 text-gray-400">加载中...</div>
        <div v-else class="space-y-1">
          <div
            v-for="chapter in chapters"
            :key="chapter.id"
            class="flex items-center justify-between px-4 py-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            @click="$router.push(`/read/${bookId}/${chapter.chapter_number}`)"
          >
            <div class="flex items-center space-x-3">
              <span class="text-xs text-gray-400 w-8">{{ chapter.chapter_number }}.</span>
              <span class="text-sm text-gray-800">{{ chapter.title }}</span>
            </div>
            <span class="text-xs text-gray-400">{{ formatWordCount(chapter.word_count) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getBookDetail, getChapters } from '@/api'
import { useBookshelfStore } from '@/stores/bookshelf'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
const bookId = Number(route.params.id)
const bookshelfStore = useBookshelfStore()

const loading = ref(true)
const chaptersLoading = ref(true)
const book = ref<any>(null)
const chapters = ref<any[]>([])

const isInBookshelf = computed(() => {
  return bookshelfStore.books.some((b: any) => b.book_id === bookId)
})

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

function startReading() {
  if (chapters.value.length > 0) {
    const lastChapter = bookshelfStore.books.find((b: any) => b.book_id === bookId)
    const chapterNum = lastChapter ? lastChapter.current_chapter : 1
    window.location.href = `/read/${bookId}/${chapterNum}`
  }
}

async function handleAddBookshelf() {
  if (isInBookshelf.value) return
  await bookshelfStore.addBook(bookId)
}

onMounted(async () => {
  try {
    const [bookRes, chaptersRes] = await Promise.all([
      getBookDetail(bookId),
      getChapters(bookId),
    ])
    book.value = bookRes.data
    chapters.value = chaptersRes.data.chapters || []
  } catch (e) {
    console.error('加载书籍详情失败:', e)
  } finally {
    loading.value = false
    chaptersLoading.value = false
  }
})
</script>
