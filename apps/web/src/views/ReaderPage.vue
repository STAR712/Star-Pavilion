<template>
  <div
    class="reader-shell"
    :class="{ 'reader-shell--chat-open': chatOpen }"
    :style="readerCssVars"
  >
    <header class="reader-header">
      <div class="reader-header__inner page-shell">
        <button class="reader-link" @click="router.push(`/book/${bookId}`)">返回详情</button>

        <div class="reader-header__center">
          <p class="reader-header__eyebrow">{{ book?.title || '沉浸式阅读' }}</p>
          <h1>{{ chapter?.title || '正在载入章节…' }}</h1>
        </div>

        <div class="reader-header__actions">
          <button class="reader-link" @click="toggleChat">{{ chatOpen ? '收起 AI' : '打开 AI' }}</button>
          <button class="reader-link" @click="openShelfOrLogin">
            {{ authStore.isAuthenticated ? '我的书架' : '登录' }}
          </button>
        </div>
      </div>
    </header>

    <main class="reader-main page-shell" :class="{ 'reader-main--chat-open': chatOpen }">
      <div v-if="loading" class="reader-status">正在加载阅读内容…</div>

      <template v-else-if="book && chapter">
        <section class="reader-scene">
          <div class="reader-scene__intro">
            <p class="section-eyebrow">IMMERSIVE READER</p>
            <h2>{{ chapter.title }}</h2>
            <p class="reader-scene__copy">
              {{ chapterLead }}
            </p>
          </div>

          <div class="reader-scene__meta">
            <div>
              <span>分类</span>
              <strong>{{ book.category }}</strong>
            </div>
            <div>
              <span>作者</span>
              <strong>{{ book.author }}</strong>
            </div>
            <div>
              <span>章节</span>
              <strong>{{ chapter.chapterNumber }} / {{ chapters.length }}</strong>
            </div>
            <div>
              <span>进度</span>
              <strong>{{ chapterProgress }}%</strong>
            </div>
          </div>
        </section>

        <section class="reader-tools">
          <div class="reader-tools__group">
            <span class="reader-tools__label">阅读主题</span>
            <button
              v-for="option in themeOptions"
              :key="option.value"
              class="tool-chip"
              :class="{ 'tool-chip--active': normalizedTheme === option.value }"
              @click="readerStore.setTheme(option.value)"
            >
              {{ option.label }}
            </button>
          </div>

          <div class="reader-tools__group">
            <span class="reader-tools__label">字号</span>
            <button class="tool-chip" @click="readerStore.decreaseFontSize()">A-</button>
            <span class="reader-tools__value">{{ readerStore.fontSize }}px</span>
            <button class="tool-chip" @click="readerStore.increaseFontSize()">A+</button>
          </div>

          <div class="reader-tools__group reader-tools__group--progress">
            <span class="reader-tools__label">阅读进度</span>
            <div class="reader-progress">
              <span :style="{ width: `${chapterProgress}%` }"></span>
            </div>
            <strong>第 {{ chapter.chapterNumber }} 章</strong>
          </div>
        </section>

        <article class="reader-article">
          <div class="reader-article__meta">
            <span>{{ book.category }}</span>
            <span>{{ book.author }}</span>
            <span>{{ formatWordCount(chapter.wordCount) }}</span>
          </div>

          <div class="reader-article__content" :style="{ fontSize: `${readerStore.fontSize}px` }">
            <p v-for="(paragraph, index) in paragraphs" :key="`${chapter.id}-${index}`">
              {{ paragraph }}
            </p>
          </div>

          <div class="reader-nav">
            <button class="reader-nav__btn" :disabled="!chapter.prevChapter" @click="goToChapter(chapter.prevChapter)">
              上一章
            </button>
            <button class="reader-nav__btn reader-nav__btn--ghost" @click="router.push(`/book/${bookId}`)">
              返回目录
            </button>
            <button class="reader-nav__btn" :disabled="!chapter.nextChapter" @click="goToChapter(chapter.nextChapter)">
              下一章
            </button>
          </div>
        </article>
      </template>

      <div v-else class="reader-status">章节不存在或暂时无法读取。</div>
    </main>

    <AiChatPanel
      v-model:open="chatOpen"
      :book-id="bookId"
      :chapter-id="chapter?.id"
      :book-title="book?.title"
      :chapter-title="chapter?.title"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AiChatPanel from '@/components/AiChatPanel.vue'
import { useAuthStore } from '@/stores/auth'
import { useBookshelfStore } from '@/stores/bookshelf'
import { useReaderStore } from '@/stores/reader'
import { fetchReaderBundle } from '@/services/library'
import type { LibraryBook, LibraryChapter, LibraryChapterDetail } from '@/data/mockLibrary'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const readerStore = useReaderStore()
const bookshelfStore = useBookshelfStore()

const bookId = computed(() => Number(route.params.bookId))
const chapterNumber = computed(() => Number(route.params.chapterNum))

const loading = ref(true)
const book = ref<LibraryBook | null>(null)
const chapters = ref<LibraryChapter[]>([])
const chapter = ref<LibraryChapterDetail | null>(null)

const themeOptions = [
  { value: 'eye' as const, label: '护眼' },
  { value: 'paper' as const, label: '羊皮纸' },
  { value: 'night' as const, label: '夜间' },
]

const chatOpen = computed({
  get: () => readerStore.sidebarOpen,
  set: (value: boolean) => readerStore.setSidebarOpen(value),
})

const normalizedTheme = computed<'eye' | 'paper' | 'night'>(() => {
  if (readerStore.theme === 'light') return 'eye'
  if (readerStore.theme === 'sepia') return 'paper'
  if (readerStore.theme === 'dark') return 'night'
  return readerStore.theme as 'eye' | 'paper' | 'night'
})

const readerCssVars = computed(() => {
  switch (normalizedTheme.value) {
    case 'night':
      return {
        '--reader-bg': '#121419',
        '--reader-panel': 'rgba(24, 27, 33, 0.82)',
        '--reader-card': 'rgba(18, 21, 26, 0.92)',
        '--reader-text': '#d9dce3',
        '--reader-muted': '#98a1b1',
        '--reader-border': 'rgba(120, 138, 164, 0.16)',
        '--reader-progress': '#aab6ff',
      }
    case 'eye':
      return {
        '--reader-bg': '#eaf2e2',
        '--reader-panel': 'rgba(244, 249, 238, 0.88)',
        '--reader-card': 'rgba(253, 255, 249, 0.96)',
        '--reader-text': '#274237',
        '--reader-muted': '#647a6e',
        '--reader-border': 'rgba(101, 124, 112, 0.14)',
        '--reader-progress': '#5d8f6d',
      }
    default:
      return {
        '--reader-bg': '#f4ebdf',
        '--reader-panel': 'rgba(252, 245, 237, 0.84)',
        '--reader-card': 'rgba(255, 251, 246, 0.96)',
        '--reader-text': '#34251d',
        '--reader-muted': '#816557',
        '--reader-border': 'rgba(132, 98, 78, 0.14)',
        '--reader-progress': '#8c3f2c',
      }
  }
})

const chapterProgress = computed(() => {
  if (!chapter.value || chapters.value.length === 0) return 0
  return Math.round((chapter.value.chapterNumber / chapters.value.length) * 100)
})

const paragraphs = computed(() => {
  const content = chapter.value?.content || ''
  return content
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)
})

const chapterLead = computed(() => paragraphs.value[0] || book.value?.description || '故事正在缓慢展开。')

function formatWordCount(value: number) {
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万字`
  return `${value}字`
}

function toggleChat() {
  chatOpen.value = !chatOpen.value
}

function openShelfOrLogin() {
  if (authStore.isAuthenticated) {
    router.push('/bookshelf')
    return
  }

  router.push({
    path: '/login',
    query: { redirect: route.fullPath },
  })
}

function goToChapter(target?: number | null) {
  if (!target) return
  router.push(`/read/${bookId.value}/${target}`)
}

async function loadReader() {
  loading.value = true
  try {
    const bundle = await fetchReaderBundle(bookId.value, chapterNumber.value)
    book.value = bundle.book
    chapters.value = bundle.chapters
    chapter.value = bundle.chapter
    readerStore.setBook(bundle.book.id)
    readerStore.setChapter(bundle.chapter.chapterNumber)
    await bookshelfStore.updateProgress(bundle.book.id, bundle.chapter.chapterNumber, chapterProgress.value, {
      title: bundle.book.title,
      author: bundle.book.author,
      cover_url: bundle.book.coverUrl || '',
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } finally {
    loading.value = false
  }
}

onMounted(loadReader)

watch(
  () => [route.params.bookId, route.params.chapterNum],
  () => {
    loadReader()
  },
)
</script>

<style scoped>
.reader-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--reader-progress) 18%, transparent), transparent 26%),
    linear-gradient(180deg, var(--reader-bg) 0%, color-mix(in srgb, var(--reader-bg) 88%, #ffffff 12%) 100%);
  color: var(--reader-text);
}

.page-shell {
  width: min(1160px, calc(100vw - 32px));
  margin: 0 auto;
}

.reader-header {
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid var(--reader-border);
  background: color-mix(in srgb, var(--reader-panel) 96%, transparent);
  backdrop-filter: blur(20px);
}

.reader-header__inner {
  display: grid;
  min-height: 80px;
  grid-template-columns: 160px minmax(0, 1fr) 260px;
  align-items: center;
  gap: 16px;
}

.reader-header__center {
  text-align: center;
}

.reader-header__eyebrow,
.section-eyebrow {
  font-size: 11px;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--reader-muted);
}

.reader-header__center h1 {
  margin: 8px 0 0;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: clamp(1.24rem, 2.3vw, 2rem);
  line-height: 1.24;
}

.reader-header__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.reader-link,
.tool-chip,
.reader-nav__btn {
  border: 1px solid var(--reader-border);
  background: color-mix(in srgb, var(--reader-panel) 86%, white 14%);
  color: var(--reader-text);
}

.reader-link {
  border-radius: 999px;
  padding: 10px 16px;
}

.reader-main {
  display: grid;
  gap: 22px;
  padding: 28px 0 52px;
  transition: padding-right 0.3s ease;
}

.reader-status,
.reader-scene,
.reader-tools,
.reader-article {
  border: 1px solid var(--reader-border);
  border-radius: 30px;
  background: var(--reader-panel);
  box-shadow: 0 24px 60px rgba(36, 25, 18, 0.08);
}

.reader-status {
  padding: 28px;
  color: var(--reader-muted);
}

.reader-scene {
  display: grid;
  gap: 22px;
  grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.9fr);
  padding: 28px;
}

.reader-scene__intro h2 {
  margin: 12px 0 0;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1.06;
}

.reader-scene__copy {
  margin: 18px 0 0;
  max-width: 50rem;
  line-height: 1.95;
  color: var(--reader-muted);
}

.reader-scene__meta {
  display: grid;
  gap: 14px;
  align-content: start;
}

.reader-scene__meta div {
  border-radius: 22px;
  background: color-mix(in srgb, var(--reader-card) 92%, transparent);
  padding: 18px;
}

.reader-scene__meta span {
  display: block;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--reader-muted);
}

.reader-scene__meta strong {
  display: block;
  margin-top: 10px;
  font-size: 20px;
}

.reader-tools {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 18px 24px;
  padding: 18px 24px;
}

.reader-tools__group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.reader-tools__group--progress {
  margin-left: auto;
}

.reader-tools__label {
  font-size: 13px;
  color: var(--reader-muted);
}

.tool-chip {
  border-radius: 999px;
  padding: 8px 14px;
}

.tool-chip--active {
  border-color: color-mix(in srgb, var(--reader-progress) 36%, transparent);
  background: color-mix(in srgb, var(--reader-progress) 18%, var(--reader-panel) 82%);
}

.reader-tools__value {
  min-width: 48px;
  text-align: center;
}

.reader-progress {
  height: 8px;
  width: clamp(160px, 16vw, 260px);
  overflow: hidden;
  border-radius: 999px;
  background: color-mix(in srgb, var(--reader-border) 70%, transparent);
}

.reader-progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, color-mix(in srgb, var(--reader-progress) 78%, white 22%), var(--reader-progress));
}

.reader-article {
  max-width: 860px;
  margin: 0 auto;
  background: var(--reader-card);
  padding: 34px clamp(22px, 4vw, 56px);
}

.reader-article__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: var(--reader-muted);
}

.reader-article__content {
  margin-top: 24px;
  line-height: 2;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  letter-spacing: 0.02em;
}

.reader-article__content p {
  margin: 0;
  text-indent: 2em;
}

.reader-article__content p + p {
  margin-top: 1.3em;
}

.reader-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  margin-top: 34px;
}

.reader-nav__btn {
  min-width: 132px;
  border-radius: 999px;
  padding: 12px 18px;
}

.reader-nav__btn--ghost {
  flex: 1;
}

.reader-nav__btn:disabled {
  opacity: 0.42;
}

@media (min-width: 1180px) {
  .reader-shell--chat-open .reader-main {
    padding-right: min(26vw, 360px);
  }
}

@media (max-width: 900px) {
  .reader-header__inner {
    grid-template-columns: 1fr;
    justify-items: center;
    padding: 14px 0;
  }

  .reader-header__actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .reader-scene {
    grid-template-columns: 1fr;
  }

  .reader-tools__group--progress {
    margin-left: 0;
  }

  .reader-progress {
    width: min(100%, 220px);
  }
}

@media (max-width: 720px) {
  .page-shell {
    width: min(calc(100vw - 24px), 100%);
  }

  .reader-main {
    gap: 16px;
    padding: 18px 0 40px;
  }

  .reader-scene,
  .reader-tools,
  .reader-article {
    border-radius: 24px;
  }

  .reader-scene,
  .reader-tools,
  .reader-article {
    padding-left: 18px;
    padding-right: 18px;
  }

  .reader-article {
    padding-top: 24px;
    padding-bottom: 24px;
  }

  .reader-nav__btn,
  .reader-nav__btn--ghost {
    width: 100%;
  }
}
</style>
