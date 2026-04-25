<template>
  <div class="detail-shell">
    <header class="detail-header">
      <div class="page-shell detail-header__inner">
        <button class="ghost-link" @click="router.push('/')">返回首页</button>

        <div class="detail-header__meta">
          <span>{{ source === 'api' ? 'API 数据' : 'Mock 回退' }}</span>
          <router-link class="ghost-link" to="/bookshelf">我的书架</router-link>
          <router-link v-if="!authStore.isAuthenticated" class="ghost-link" :to="{ path: '/login', query: { redirect: route.fullPath } }">
            登录
          </router-link>
          <button v-else class="ghost-link" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </header>

    <main class="page-shell detail-main">
      <div v-if="loading" class="detail-hero">
        <SkeletonCard :horizontal="true" />
        <div style="display:grid;gap:14px;padding:20px;">
          <div class="skeleton-pulse" style="height:20px;width:40%;border-radius:12px;background:linear-gradient(90deg,rgba(200,180,160,0.15) 25%,rgba(200,180,160,0.3) 50%,rgba(200,180,160,0.15) 75%);background-size:200% 100%;animation:skeleton-shimmer 1.5s ease-in-out infinite;"></div>
          <div class="skeleton-pulse" style="height:36px;width:70%;border-radius:12px;background:linear-gradient(90deg,rgba(200,180,160,0.15) 25%,rgba(200,180,160,0.3) 50%,rgba(200,180,160,0.15) 75%);background-size:200% 100%;animation:skeleton-shimmer 1.5s ease-in-out infinite;"></div>
          <div class="skeleton-pulse" style="height:16px;width:90%;border-radius:12px;background:linear-gradient(90deg,rgba(200,180,160,0.15) 25%,rgba(200,180,160,0.3) 50%,rgba(200,180,160,0.15) 75%);background-size:200% 100%;animation:skeleton-shimmer 1.5s ease-in-out infinite;"></div>
        </div>
      </div>

      <template v-else-if="book">
        <section class="detail-hero">
          <div class="detail-cover" :style="{ boxShadow: `0 30px 60px ${palette.glow}` }">
            <img
              v-if="book.coverUrl"
              :src="book.coverUrl"
              :alt="book.title"
              class="detail-cover__image"
            />
            <div v-else class="detail-cover__fallback" :style="{ background: palette.surface }">
              <span>{{ book.category }}</span>
              <h1>{{ book.title }}</h1>
              <p>{{ book.author }}</p>
            </div>
          </div>

          <div class="detail-copy">
            <p class="detail-copy__eyebrow">{{ book.category }} · {{ book.status }}</p>
            <h2>{{ book.title }}</h2>
            <p class="detail-copy__author">{{ book.author }}</p>
            <p class="detail-copy__desc">{{ book.description }}</p>

            <div class="detail-tags">
              <span v-for="tag in book.tags" :key="tag">{{ tag }}</span>
            </div>

            <div class="detail-actions">
              <button class="action-primary" @click="startReading">立即阅读</button>
              <button class="action-secondary" @click="handleAddBookshelf">
                {{ isInBookshelf ? '已在书架' : '加入书架' }}
              </button>
            </div>

            <p v-if="actionFeedback" class="detail-feedback">{{ actionFeedback }}</p>

            <div class="detail-stats">
              <div class="detail-stat">
                <span>字数</span>
                <strong>{{ formatWordCount(book.wordCount) }}</strong>
              </div>
              <div class="detail-stat">
                <span>章节</span>
                <strong>{{ chapters.length }} 章</strong>
              </div>
              <div class="detail-stat">
                <span>热度</span>
                <strong>{{ formatCompact(book.readCount) }}</strong>
              </div>
              <div class="detail-stat">
                <span>推荐</span>
                <strong>{{ formatCompact(book.recommendCount) }}</strong>
              </div>
            </div>
          </div>
        </section>

        <section class="detail-layout">
          <div class="chapter-panel">
            <div class="section-head">
              <div>
                <p class="section-eyebrow">章节目录</p>
                <h3>从这里跳转进阅读器</h3>
              </div>
              <span>{{ chapters.length }} Chapters</span>
            </div>

            <div class="chapter-list">
              <button
                v-for="chapter in chapters"
                :key="chapter.id"
                class="chapter-item"
                @click="openChapter(chapter.chapterNumber)"
              >
                <div>
                  <strong>第 {{ chapter.chapterNumber }} 章</strong>
                  <h4>{{ chapter.title }}</h4>
                  <p>{{ chapter.preview }}</p>
                </div>
                <span>{{ formatWordCount(chapter.wordCount) }}</span>
              </button>
            </div>
          </div>

          <aside class="info-panel">
            <div class="info-card">
              <p class="section-eyebrow">阅读动线</p>
              <h3>首页 -> 详情页 -> 阅读器</h3>
              <p>现在书籍卡片会先进入详情页，章节点击后进入阅读器，阅读页再通过玻璃态 AI 助手实现“边读边聊”。</p>
            </div>

            <div class="info-card">
              <p class="section-eyebrow">书架同步</p>
              <h3>{{ authStore.isAuthenticated ? '已登录，可同步书架' : '登录后可持久化书架' }}</h3>
              <p>{{ authStore.isAuthenticated ? '当前账号的书架和阅读进度会跨页面同步。' : '未登录时点击加入书架会自动带你进入登录页，并在成功后回到当前书籍。' }}</p>
            </div>
          </aside>
        </section>
      </template>

      <div v-else class="status-panel">没有找到这本书。</div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBookshelfStore } from '@/stores/bookshelf'
import { fetchBookBundle, getCategoryPalette } from '@/services/library'
import SkeletonCard from '@/components/SkeletonCard.vue'
import type { LibraryBook, LibraryChapter, LibrarySource } from '@/data/mockLibrary'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const bookshelfStore = useBookshelfStore()

const bookId = Number(route.params.id)

const loading = ref(true)
const source = ref<LibrarySource>('mock')
const book = ref<LibraryBook | null>(null)
const chapters = ref<LibraryChapter[]>([])
const actionFeedback = ref('')

const palette = computed(() => getCategoryPalette(book.value?.category || '都市'))
const isInBookshelf = computed(() => bookshelfStore.books.some((item: any) => Number(item.book_id) === bookId))

function formatCompact(value: number) {
  if (value >= 100000000) return `${(value / 100000000).toFixed(1)}亿`
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万`
  return value.toLocaleString('zh-CN')
}

function formatWordCount(value: number) {
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万字`
  return `${value}字`
}

function startReading() {
  const progressRecord = bookshelfStore.books.find((item: any) => Number(item.book_id) === bookId)
  const chapterNumber = progressRecord ? Number(progressRecord.current_chapter || 1) : chapters.value[0]?.chapterNumber || 1
  openChapter(chapterNumber)
}

function openChapter(chapterNumber: number) {
  router.push(`/read/${bookId}/${chapterNumber}`)
}

function handleLogout() {
  authStore.logout()
  bookshelfStore.clearBooks()
  actionFeedback.value = '已退出登录'
}

async function handleAddBookshelf() {
  if (!book.value || isInBookshelf.value) return
  actionFeedback.value = ''

  try {
    await bookshelfStore.addBook(bookId, {
      title: book.value.title,
      author: book.value.author,
      cover_url: book.value.coverUrl || '',
    })
    actionFeedback.value = '已加入书架，稍后可在“我的书架”中继续阅读。'
  } catch (error: any) {
    if (error instanceof Error && error.message === 'AUTH_REQUIRED') {
      router.push({
        path: '/login',
        query: { redirect: route.fullPath },
      })
      return
    }

    actionFeedback.value = error?.response?.data?.detail || '加入书架失败，请稍后重试。'
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const [bundle] = await Promise.all([
      fetchBookBundle(bookId),
      bookshelfStore.fetchBookshelf(),
    ])
    book.value = bundle.book
    chapters.value = bundle.chapters
    source.value = bundle.source
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(255, 211, 170, 0.28), transparent 25%),
    linear-gradient(180deg, #fbf6ef 0%, #f4ebdf 52%, #f7f0e8 100%);
}

.page-shell {
  width: min(1280px, calc(100vw - 32px));
  margin: 0 auto;
}

.detail-header {
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid rgba(126, 84, 60, 0.12);
  background: rgba(252, 247, 241, 0.82);
  backdrop-filter: blur(20px);
}

.detail-header__inner,
.detail-header__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detail-header__inner {
  min-height: 68px;
}

.ghost-link {
  border: 0;
  background: transparent;
  color: #734c3a;
  text-decoration: none;
}

.detail-main {
  padding: 28px 0 64px;
}

.status-panel,
.detail-hero,
.chapter-panel,
.info-card {
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 30px;
  background: rgba(255, 252, 249, 0.8);
  box-shadow: 0 24px 60px rgba(95, 58, 39, 0.08);
}

.status-panel {
  padding: 28px;
  color: #6b5449;
}

.detail-hero {
  display: grid;
  gap: 28px;
  grid-template-columns: 320px minmax(0, 1fr);
  padding: 28px;
}

.detail-cover {
  overflow: hidden;
  border-radius: 28px;
}

.detail-cover__image,
.detail-cover__fallback {
  min-height: 420px;
  width: 100%;
}

.detail-cover__image {
  object-fit: cover;
}

.detail-cover__fallback {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px;
  color: white;
}

.detail-cover__fallback span {
  align-self: start;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  padding: 8px 14px;
}

.detail-cover__fallback h1 {
  margin: 0;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 52px;
  line-height: 1;
}

.detail-cover__fallback p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
}

.detail-copy__eyebrow,
.section-eyebrow {
  font-size: 11px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: #9c6b4c;
}

.detail-copy h2,
.section-head h3,
.info-card h3 {
  margin-top: 14px;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  color: #271914;
}

.detail-copy h2 {
  font-size: clamp(2.4rem, 5vw, 4.4rem);
  line-height: 0.98;
}

.detail-copy__author {
  margin-top: 10px;
  font-size: 18px;
  color: #8b624f;
}

.detail-copy__desc,
.info-card p,
.chapter-item p {
  line-height: 1.9;
  color: #6b5449;
}

.detail-tags,
.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 22px;
}

.detail-tags span,
.action-secondary {
  border: 1px solid rgba(127, 63, 44, 0.14);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  padding: 10px 16px;
  color: #744b39;
}

.action-primary,
.action-secondary {
  border-radius: 999px;
  padding: 12px 22px;
}

.action-primary {
  border: 0;
  background: linear-gradient(135deg, #201317, #8c3f2c);
  color: white;
}

.detail-feedback {
  margin: 16px 0 0;
  color: #8c3f2c;
}

.detail-stats {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 26px;
}

.detail-stat {
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.76);
  padding: 18px;
}

.detail-stat span {
  display: block;
  color: #8e6958;
}

.detail-stat strong {
  display: block;
  margin-top: 10px;
  color: #2a1b16;
}

.detail-layout {
  display: grid;
  gap: 22px;
  grid-template-columns: minmax(0, 1.3fr) 320px;
  margin-top: 22px;
}

.chapter-panel,
.info-card {
  padding: 24px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.chapter-list {
  display: grid;
  gap: 14px;
  margin-top: 20px;
}

.chapter-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid rgba(127, 63, 44, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.74);
  padding: 18px;
  text-align: left;
}

.chapter-item strong {
  color: #2b1c17;
}

.chapter-item h4 {
  margin: 10px 0 0;
  color: #6d4b3b;
}

.chapter-item p {
  margin: 12px 0 0;
}

.info-panel {
  display: grid;
  gap: 16px;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 1080px) {
  .detail-hero,
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .detail-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .page-shell {
    width: min(calc(100vw - 24px), 100%);
  }

  .detail-main {
    padding: 16px 0 40px;
  }

  .detail-header__inner,
  .detail-header__meta,
  .section-head,
  .chapter-item {
    flex-direction: column;
    align-items: start;
  }

  .status-panel,
  .detail-hero,
  .chapter-panel,
  .info-card {
    border-radius: 24px;
  }

  .detail-hero,
  .chapter-panel,
  .info-card {
    padding: 18px;
  }

  .detail-cover__fallback h1 {
    font-size: 38px;
  }

  .detail-stats {
    grid-template-columns: 1fr;
  }
}
</style>
