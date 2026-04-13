<template>
  <div
    class="min-h-screen transition-colors duration-300"
    :class="themeClasses"
  >
    <!-- 加载中 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 阅读区域 -->
    <div v-else-if="chapter" class="max-w-3xl mx-auto px-6 py-12">
      <!-- 章节标题 -->
      <div class="text-center mb-12">
        <h1 class="text-2xl font-bold mb-2" :class="textClass">{{ chapter.title }}</h1>
        <div class="flex items-center justify-center space-x-4 text-sm" :class="subTextClass">
          <button
            v-if="chapter.prev_chapter"
            class="hover:text-indigo-500 transition-colors"
            @click="goToChapter(chapter.prev_chapter)"
          >
            上一章
          </button>
          <span v-else class="text-gray-300">已是第一章</span>
          <span>|</span>
          <button
            v-if="chapter.next_chapter"
            class="hover:text-indigo-500 transition-colors"
            @click="goToChapter(chapter.next_chapter)"
          >
            下一章
          </button>
          <span v-else class="text-gray-300">已是最后一章</span>
        </div>
      </div>

      <!-- 正文内容 -->
      <div
        class="leading-loose whitespace-pre-wrap"
        :class="[textClass, contentClass]"
        :style="{ fontSize: readerStore.fontSize + 'px' }"
      >
        {{ chapter.content }}
      </div>

      <!-- 底部导航 -->
      <div class="flex items-center justify-between mt-16 pt-8 border-t" :class="borderClass">
        <button
          v-if="chapter.prev_chapter"
          class="px-6 py-2 rounded-lg border transition-colors"
          :class="btnClass"
          @click="goToChapter(chapter.prev_chapter)"
        >
          上一章
        </button>
        <span v-else></span>
        <button
          class="px-6 py-2 rounded-lg border transition-colors"
          :class="btnClass"
          @click="$router.push(`/book/${bookId}`)"
        >
          目录
        </button>
        <button
          v-if="chapter.next_chapter"
          class="px-6 py-2 rounded-lg border transition-colors"
          :class="btnClass"
          @click="goToChapter(chapter.next_chapter)"
        >
          下一章
        </button>
        <span v-else></span>
      </div>
    </div>

    <!-- 右侧悬浮工具栏 -->
    <div class="fixed right-4 top-1/2 -translate-y-1/2 flex flex-col space-y-3 z-30">
      <button
        class="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center hover:shadow-lg transition-shadow"
        title="目录"
        @click="$router.push(`/book/${bookId}`)"
      >
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
      </button>
      <button
        class="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center hover:shadow-lg transition-shadow"
        title="字体大小"
        @click="toggleFontSize"
      >
        <span class="text-xs font-bold text-gray-600">A</span>
      </button>
      <button
        class="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center hover:shadow-lg transition-shadow"
        title="切换主题"
        @click="readerStore.toggleTheme()"
      >
        <svg v-if="readerStore.theme === 'light'" class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
        <svg v-else-if="readerStore.theme === 'dark'" class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <svg v-else class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      </button>
    </div>

    <!-- AI 助手 -->
    <AiChatPanel :book-id="bookId" :chapter-id="chapterId" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getChapterContent } from '@/api'
import { useReaderStore } from '@/stores/reader'
import { useBookshelfStore } from '@/stores/bookshelf'
import AiChatPanel from '@/components/AiChatPanel.vue'

const route = useRoute()
const router = useRouter()
const readerStore = useReaderStore()
const bookshelfStore = useBookshelfStore()

const bookId = Number(route.params.bookId)
const chapterNum = Number(route.params.chapterNum)
const chapterId = ref<number | undefined>(undefined)

const loading = ref(true)
const chapter = ref<any>(null)

// 主题样式
const themeClasses = computed(() => {
  switch (readerStore.theme) {
    case 'dark':
      return 'bg-gray-900'
    case 'sepia':
      return 'bg-amber-50'
    default:
      return 'bg-white'
  }
})

const textClass = computed(() => {
  switch (readerStore.theme) {
    case 'dark':
      return 'text-gray-200'
    case 'sepia':
      return 'text-amber-900'
    default:
      return 'text-gray-800'
  }
})

const subTextClass = computed(() => {
  switch (readerStore.theme) {
    case 'dark':
      return 'text-gray-500'
    case 'sepia':
      return 'text-amber-700'
    default:
      return 'text-gray-400'
  }
})

const borderClass = computed(() => {
  switch (readerStore.theme) {
    case 'dark':
      return 'border-gray-700'
    case 'sepia':
      return 'border-amber-200'
    default:
      return 'border-gray-200'
  }
})

const btnClass = computed(() => {
  switch (readerStore.theme) {
    case 'dark':
      return 'border-gray-700 text-gray-300 hover:bg-gray-800'
    case 'sepia':
      return 'border-amber-200 text-amber-800 hover:bg-amber-100'
    default:
      return 'border-gray-200 text-gray-600 hover:bg-gray-50'
  }
})

const contentClass = computed(() => {
  switch (readerStore.theme) {
    case 'dark':
      return 'text-gray-300'
    case 'sepia':
      return 'text-amber-800'
    default:
      return 'text-gray-700'
  }
})

function toggleFontSize() {
  const sizes = [16, 18, 20, 22, 24]
  const idx = sizes.indexOf(readerStore.fontSize)
  readerStore.fontSize = sizes[(idx + 1) % sizes.length]
}

async function loadChapter(bookId: number, chapterNum: number) {
  loading.value = true
  try {
    const { data } = await getChapterContent(bookId, chapterNum)
    chapter.value = data
    chapterId.value = data.id
    readerStore.setBook(bookId)
    readerStore.setChapter(chapterNum)

    // 更新阅读进度
    bookshelfStore.updateProgress(bookId, chapterNum, 0)
  } catch (e) {
    console.error('加载章节失败:', e)
  } finally {
    loading.value = false
  }
}

function goToChapter(num: number) {
  router.push(`/read/${bookId}/${num}`)
}

// 监听路由参数变化
watch(
  () => [route.params.bookId, route.params.chapterNum],
  ([newBookId, newChapterNum]) => {
    if (newBookId && newChapterNum) {
      loadChapter(Number(newBookId), Number(newChapterNum))
    }
  }
)

onMounted(() => {
  loadChapter(bookId, chapterNum)
})
</script>
