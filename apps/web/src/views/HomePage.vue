<template>
  <div class="home-shell">
    <header class="home-header">
      <div class="page-shell home-header__inner">
        <router-link to="/" class="brand">
          <span class="brand__mark">星</span>
          <span>
            <strong>Star Pavilion</strong>
            <small>FICTION SALON</small>
          </span>
        </router-link>

        <nav class="home-nav">
          <router-link class="home-nav__link" to="/">首页</router-link>
          <router-link class="home-nav__link" to="/rank">排行榜</router-link>
          <router-link class="home-nav__link" to="/author">作家专区</router-link>
          <router-link class="home-nav__link" to="/bookshelf">我的书架</router-link>
        </nav>

        <div class="home-header__actions">
          <label class="search-box">
            <input
              v-model="searchText"
              type="text"
              placeholder="搜索今夜想读的故事"
            />
          </label>

          <template v-if="authStore.isAuthenticated">
            <router-link class="header-link header-link--accent" to="/bookshelf">
              书架 {{ bookshelfStore.books.length }}
            </router-link>
            <span class="header-user">{{ authStore.user?.username }}</span>
            <button class="header-link" @click="handleLogout">退出</button>
          </template>
          <template v-else>
            <router-link class="header-link" to="/login">登录</router-link>
            <router-link class="header-link header-link--accent" to="/register">注册</router-link>
          </template>
        </div>
      </div>
    </header>

    <main class="page-shell home-main">
      <section v-if="activeBannerBook" class="banner-shell">
        <div
          class="banner-stage"
          :style="{ boxShadow: `0 34px 80px ${activePalette.glow}` }"
        >
          <div class="banner-stage__backdrop" :style="{ background: activePalette.surface }"></div>

          <div class="banner-copy">
            <p class="hero-copy__eyebrow">CURATED FICTION CAROUSEL</p>
            <h1>{{ activeBannerBook.title }}</h1>
            <p class="hero-copy__text">
              {{ activeBannerBook.description }}
            </p>

            <div class="hero-stats">
              <div class="hero-stat">
                <span>作者</span>
                <strong>{{ activeBannerBook.author }}</strong>
              </div>
              <div class="hero-stat">
                <span>热度</span>
                <strong>{{ formatCompact(activeBannerBook.readCount) }}</strong>
              </div>
              <div class="hero-stat">
                <span>章节</span>
                <strong>{{ activeBannerBook.chapterCount }} 章</strong>
              </div>
            </div>

            <div class="banner-actions">
              <button class="action-primary" @click="openReader(activeBannerBook.id, 1)">立即阅读</button>
              <button class="action-secondary" @click="openBook(activeBannerBook.id)">查看详情</button>
            </div>
          </div>

          <div class="banner-card">
            <div class="banner-card__cover" :style="{ background: activePalette.surface }">
              <span>{{ activeBannerBook.category }}</span>
              <h2>{{ activeBannerBook.title }}</h2>
              <p>{{ activeBannerBook.author }}</p>
            </div>

            <div class="banner-card__body">
              <div class="banner-card__badges">
                <span v-for="tag in activeBannerBook.tags" :key="tag">{{ tag }}</span>
              </div>
              <p>{{ source === 'api' ? '当前 Banner 已连接 API 书库。' : '当前处于 Mock 回退模式，但链路完整可读。' }}</p>
              <div class="banner-card__footer">
                <span>{{ formatWordCount(activeBannerBook.wordCount) }}</span>
                <span>{{ activeBannerBook.isFree ? '免费阅读' : '精选付费' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="banner-rail">
          <div class="banner-rail__tabs">
            <button
              v-for="(book, index) in bannerBooks"
              :key="book.id"
              class="banner-tab"
              :class="{ 'banner-tab--active': index === activeBannerIndex }"
              @click="activeBannerIndex = index"
            >
              <span>0{{ index + 1 }}</span>
              <strong>{{ book.title }}</strong>
              <small>{{ book.category }}</small>
            </button>
          </div>

          <div class="banner-rail__actions">
            <button class="rail-action" @click="cycleBanner(-1)">上一部</button>
            <button class="rail-action" @click="cycleBanner(1)">下一部</button>
          </div>
        </div>
      </section>

      <section class="insight-strip">
        <div class="insight-card">
          <span>当前书籍</span>
          <strong>{{ books.length }}</strong>
        </div>
        <div class="insight-card">
          <span>累计热度</span>
          <strong>{{ formatCompact(totalReads) }}</strong>
        </div>
        <div class="insight-card">
          <span>数据来源</span>
          <strong>{{ source === 'api' ? 'API' : 'Mock' }}</strong>
        </div>
        <div class="insight-card">
          <span>登录状态</span>
          <strong>{{ authStore.isAuthenticated ? '已登录' : '未登录' }}</strong>
        </div>
      </section>

      <section class="resume-panel">
        <div>
          <p class="section-eyebrow">CONTINUE READING</p>
          <h2>从上次停下的地方，直接回到故事里。</h2>
          <p class="section-note">
            {{ authStore.isAuthenticated ? '书架与阅读进度会实时同步。' : '登录后可同步书架和阅读进度。' }}
          </p>
        </div>

        <div v-if="resumeBook" class="resume-card">
          <button class="resume-card__info" @click="openReader(resumeBook.id, resumeChapter)">
            <div class="resume-card__cover" :style="{ background: getCategoryPalette(resumeBook.category).surface }">
              <span>{{ resumeBook.category }}</span>
              <strong>{{ resumeBook.title }}</strong>
            </div>
            <div class="resume-card__text">
              <h3>{{ resumeBook.title }}</h3>
              <p>已读至第 {{ resumeChapter }} 章，当前进度 {{ resumeProgress }}%</p>
              <div class="resume-card__bar">
                <span :style="{ width: `${resumeProgress}%` }"></span>
              </div>
            </div>
          </button>
          <button class="action-primary" @click="openReader(resumeBook.id, resumeChapter)">继续阅读</button>
        </div>

        <div v-else class="resume-empty">
          <p>书架还没有记录，先从一部感兴趣的小说开始。</p>
        </div>
      </section>

      <section class="category-strip">
        <button
          class="category-pill"
          :class="{ 'category-pill--active': activeCategory === '全部' }"
          @click="activeCategory = '全部'"
        >
          全部
        </button>
        <button
          v-for="category in categories"
          :key="category.name"
          class="category-pill"
          :class="{ 'category-pill--active': activeCategory === category.name }"
          @click="activeCategory = category.name"
        >
          {{ category.name }}
          <span>{{ category.count }}</span>
        </button>
      </section>

      <section class="section-block">
        <div class="section-head">
          <div>
            <p class="section-eyebrow">HOME TO DETAIL TO READER</p>
            <h2>首页所有卡片都能直接进入详情页，再切入阅读器。</h2>
          </div>
          <span class="section-note">点击任意卡片即可进入完整链路</span>
        </div>

        <SkeletonList v-if="loading" :count="8" />
        <div v-else-if="filteredBooks.length === 0" class="empty-panel">没有匹配的小说，换个关键词试试看。</div>
        <div v-else class="book-grid">
          <article
            v-for="book in filteredBooks"
            :key="book.id"
            class="book-card"
            @click="openBook(book.id)"
          >
            <div class="book-card__cover" :style="{ background: getCategoryPalette(book.category).surface }">
              <span>{{ book.category }}</span>
              <h3>{{ book.title }}</h3>
              <p>{{ book.author }}</p>
            </div>
            <div class="book-card__body">
              <div class="book-card__meta">
                <span>{{ book.status }}</span>
                <span>{{ book.isFree ? '免费' : '付费' }}</span>
              </div>
              <p class="book-card__desc">{{ book.description }}</p>
              <div class="book-card__footer">
                <strong>{{ formatWordCount(book.wordCount) }}</strong>
                <span>{{ formatCompact(book.readCount) }} 热读</span>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="feature-grid">
        <div class="section-block">
          <div class="section-head">
            <div>
              <p class="section-eyebrow">RECENT FAVORITES</p>
              <h2>高热作品，适合从详情页继续展开。</h2>
            </div>
          </div>
          <div class="compact-list">
            <button
              v-for="book in latestBooks"
              :key="book.id"
              class="compact-list__item"
              @click="openBook(book.id)"
            >
              <div class="compact-list__cover" :style="{ background: getCategoryPalette(book.category).surface }"></div>
              <div class="compact-list__body">
                <strong>{{ book.title }}</strong>
                <p>{{ book.author }} · {{ book.category }}</p>
              </div>
              <span>{{ formatCompact(book.recommendCount) }}</span>
            </button>
          </div>
        </div>

        <div class="section-block">
          <div class="section-head">
            <div>
              <p class="section-eyebrow">FREE TO START</p>
              <h2>先挑一本不设门槛的故事。</h2>
            </div>
          </div>
          <div class="free-list">
            <button
              v-for="book in freeBooks"
              :key="book.id"
              class="free-list__item"
              @click="openBook(book.id)"
            >
              <h3>{{ book.title }}</h3>
              <p>{{ book.description }}</p>
              <span>立即进入详情</span>
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBookshelfStore } from '@/stores/bookshelf'
import { fetchLibraryBooks, getCategoryPalette } from '@/services/library'
import SkeletonList from '@/components/SkeletonList.vue'
import type { LibraryBook, LibrarySource } from '@/data/mockLibrary'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const bookshelfStore = useBookshelfStore()

const loading = ref(true)
const books = ref<LibraryBook[]>([])
const source = ref<LibrarySource>('mock')
const searchText = ref(String(route.query.q || ''))
const activeCategory = ref('全部')
const activeBannerIndex = ref(0)

let bannerTimer: number | null = null

const filteredBooks = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  return books.value.filter((book) => {
    const hitCategory = activeCategory.value === '全部' || book.category === activeCategory.value
    const hitKeyword = !keyword || [book.title, book.author, book.description, ...book.tags].some((field) =>
      field.toLowerCase().includes(keyword),
    )
    return hitCategory && hitKeyword
  })
})

const bannerBooks = computed(() =>
  [...books.value]
    .sort((left, right) => (right.readCount + right.recommendCount) - (left.readCount + left.recommendCount))
    .slice(0, 4),
)
const activeBannerBook = computed(() => bannerBooks.value[activeBannerIndex.value] || bannerBooks.value[0] || null)
const activePalette = computed(() => getCategoryPalette(activeBannerBook.value?.category || '都市'))
const latestBooks = computed(() => [...books.value].sort((left, right) => right.recommendCount - left.recommendCount).slice(0, 5))
const freeBooks = computed(() => books.value.filter((book) => book.isFree).slice(0, 3))
const totalReads = computed(() => books.value.reduce((sum, book) => sum + book.readCount, 0))

const categories = computed(() => {
  const bucket = new Map<string, number>()
  for (const book of books.value) {
    bucket.set(book.category, (bucket.get(book.category) || 0) + 1)
  }
  return Array.from(bucket.entries()).map(([name, count]) => ({ name, count }))
})

const resumeEntry = computed(() => bookshelfStore.books.find((item: any) => Number(item.progress || 0) < 100) || bookshelfStore.books[0] || null)
const resumeBook = computed(() => books.value.find((book) => book.id === Number(resumeEntry.value?.book_id)) || activeBannerBook.value)
const resumeChapter = computed(() => Math.max(1, Number(resumeEntry.value?.current_chapter || 1)))
const resumeProgress = computed(() => Math.max(0, Math.min(100, Math.round(Number(resumeEntry.value?.progress || 0)))))

function formatCompact(value: number) {
  if (value >= 100000000) return `${(value / 100000000).toFixed(1)}亿`
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万`
  return value.toLocaleString('zh-CN')
}

function formatWordCount(value: number) {
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万字`
  return `${value}字`
}

function openBook(bookId: number) {
  router.push(`/book/${bookId}`)
}

function openReader(bookId: number, chapterNumber: number = 1) {
  router.push(`/read/${bookId}/${chapterNumber}`)
}

function cycleBanner(step: number) {
  if (bannerBooks.value.length === 0) return
  activeBannerIndex.value = (activeBannerIndex.value + step + bannerBooks.value.length) % bannerBooks.value.length
}

function startBannerTimer() {
  if (bannerTimer !== null || bannerBooks.value.length <= 1) return
  bannerTimer = window.setInterval(() => {
    cycleBanner(1)
  }, 5000)
}

function stopBannerTimer() {
  if (bannerTimer !== null) {
    window.clearInterval(bannerTimer)
    bannerTimer = null
  }
}

function handleLogout() {
  authStore.logout()
  bookshelfStore.clearBooks()
}

watch(
  () => route.query.q,
  (value) => {
    searchText.value = String(value || '')
  },
)

watch(bannerBooks, (value) => {
  if (value.length === 0) {
    activeBannerIndex.value = 0
    stopBannerTimer()
    return
  }

  if (activeBannerIndex.value >= value.length) {
    activeBannerIndex.value = 0
  }

  stopBannerTimer()
  startBannerTimer()
})

onMounted(async () => {
  loading.value = true
  try {
    const [library] = await Promise.all([
      fetchLibraryBooks(16),
      bookshelfStore.fetchBookshelf(),
    ])
    books.value = library.books
    source.value = library.source
    startBannerTimer()
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  stopBannerTimer()
})
</script>

<style scoped>
.home-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 151, 0.28), transparent 24%),
    radial-gradient(circle at top right, rgba(188, 95, 67, 0.16), transparent 18%),
    linear-gradient(180deg, #fdf8f2 0%, #f4e9dc 48%, #f8f0e8 100%);
}

.page-shell {
  width: min(1320px, calc(100vw - 32px));
  margin: 0 auto;
}

.home-header {
  position: sticky;
  top: 0;
  z-index: 30;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(27, 21, 21, 0.82);
  backdrop-filter: blur(22px);
}

.home-header__inner {
  display: grid;
  min-height: 82px;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 24px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: white;
  text-decoration: none;
}

.brand__mark {
  display: grid;
  height: 44px;
  width: 44px;
  place-items: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #ad6445, #f3c18e);
  color: #201317;
  font-weight: 700;
  font-size: 20px;
}

.brand strong,
.brand small {
  display: block;
}

.brand strong {
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 28px;
}

.brand small {
  margin-top: 4px;
  letter-spacing: 0.24em;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.64);
}

.home-nav {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.home-nav__link,
.header-link {
  border-radius: 999px;
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.82);
  text-decoration: none;
  transition: background 0.25s ease, color 0.25s ease;
}

.home-nav__link:hover,
.header-link:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

.home-header__actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-box input {
  height: 44px;
  min-width: 220px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  padding: 0 18px;
  color: white;
  outline: none;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.46);
}

.header-link {
  border: 0;
  background: rgba(255, 255, 255, 0.08);
}

.header-link--accent {
  background: linear-gradient(135deg, #be714f, #f3c08e);
  color: #201317;
}

.header-user {
  color: rgba(255, 255, 255, 0.72);
}

.home-main {
  display: grid;
  gap: 22px;
  padding: 24px 0 64px;
}

.banner-shell,
.resume-panel,
.section-block,
.insight-card {
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 32px;
  background: rgba(255, 252, 249, 0.72);
  box-shadow: 0 24px 60px rgba(95, 58, 39, 0.08);
  backdrop-filter: blur(18px);
}

.banner-shell {
  padding: 22px;
}

.banner-stage {
  position: relative;
  display: grid;
  gap: 26px;
  grid-template-columns: minmax(0, 1.2fr) 360px;
  overflow: hidden;
  border-radius: 28px;
  padding: clamp(22px, 4vw, 36px);
  color: white;
}

.banner-stage__backdrop {
  position: absolute;
  inset: 0;
  opacity: 0.96;
}

.banner-copy,
.banner-card {
  position: relative;
  z-index: 1;
}

.hero-copy__eyebrow,
.section-eyebrow {
  font-size: 11px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: #9d6b53;
}

.banner-copy .hero-copy__eyebrow {
  color: rgba(255, 255, 255, 0.68);
}

.banner-copy h1 {
  margin: 16px 0 0;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: clamp(2.8rem, 6vw, 5.4rem);
  line-height: 0.95;
}

.hero-copy__text {
  margin-top: 18px;
  max-width: 40rem;
  line-height: 1.9;
  color: rgba(255, 255, 255, 0.82);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 22px;
}

.hero-stat {
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.12);
  padding: 16px;
}

.hero-stat span {
  display: block;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.68);
}

.hero-stat strong {
  display: block;
  margin-top: 10px;
  font-size: 24px;
}

.banner-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.banner-card {
  display: grid;
  gap: 18px;
  align-content: start;
}

.banner-card__cover {
  min-height: 280px;
  border-radius: 28px;
  padding: 24px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18);
}

.banner-card__cover span {
  display: inline-flex;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  padding: 8px 14px;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.banner-card__cover h2 {
  margin: 58px 0 0;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 42px;
  line-height: 1;
}

.banner-card__cover p {
  margin-top: 12px;
  color: rgba(255, 255, 255, 0.76);
}

.banner-card__body {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.14);
  padding: 18px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.8);
}

.banner-card__badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.banner-card__badges span {
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  padding: 8px 12px;
}

.banner-card__body p {
  margin: 14px 0 0;
}

.banner-card__footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
  color: white;
}

.banner-rail {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  margin-top: 18px;
}

.banner-rail__tabs {
  display: grid;
  flex: 1;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.banner-tab,
.rail-action,
.category-pill,
.action-primary,
.action-secondary,
.compact-list__item,
.free-list__item,
.resume-card__info,
.book-card {
  cursor: pointer;
}

.banner-tab {
  display: grid;
  gap: 6px;
  border: 1px solid rgba(126, 84, 60, 0.1);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.68);
  padding: 14px 16px;
  text-align: left;
  color: #6a4f43;
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.banner-tab span {
  font-size: 12px;
  letter-spacing: 0.18em;
  color: #a36c53;
}

.banner-tab strong {
  color: #241917;
}

.banner-tab small {
  color: #846659;
}

.banner-tab--active {
  transform: translateY(-2px);
  border-color: rgba(140, 63, 44, 0.22);
  box-shadow: 0 18px 34px rgba(90, 48, 28, 0.1);
}

.banner-rail__actions {
  display: flex;
  gap: 12px;
}

.rail-action,
.action-secondary,
.category-pill {
  border: 1px solid rgba(127, 63, 44, 0.14);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  padding: 12px 18px;
  color: #6f4939;
}

.insight-strip {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.insight-card {
  padding: 22px;
}

.insight-card span {
  display: block;
  color: #8c6958;
}

.insight-card strong {
  display: block;
  margin-top: 10px;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 34px;
  color: #2a1b16;
}

.resume-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
}

.resume-panel h2,
.section-head h2 {
  margin-top: 12px;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: clamp(1.8rem, 3vw, 3.2rem);
  color: #281916;
}

.section-note {
  color: #85685a;
}

.resume-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.resume-card__info {
  display: grid;
  width: min(520px, 100%);
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 16px;
  border: 0;
  background: transparent;
  text-align: left;
}

.resume-card__cover {
  min-height: 190px;
  border-radius: 24px;
  padding: 18px;
  color: white;
}

.resume-card__cover strong {
  display: block;
  margin-top: 78px;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 34px;
  line-height: 1.04;
}

.resume-card__text h3 {
  margin: 0;
  font-size: 26px;
  color: #2b1c17;
}

.resume-card__text p {
  margin-top: 12px;
  color: #72584c;
}

.resume-card__bar {
  margin-top: 16px;
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(127, 63, 44, 0.1);
}

.resume-card__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #d78a61, #8c3f2c);
}

.resume-empty {
  display: grid;
  place-items: center;
  min-width: 280px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.68);
  padding: 28px;
  color: #765c50;
}

.category-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.category-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.category-pill--active {
  background: linear-gradient(135deg, #201317, #8c3f2c);
  color: white;
}

.section-block {
  padding: 26px;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 18px;
}

.empty-panel {
  margin-top: 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  padding: 24px;
  color: #735a4d;
}

.book-grid,
.feature-grid {
  display: grid;
  gap: 18px;
}

.book-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 20px;
}

.book-card {
  overflow: hidden;
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.76);
  box-shadow: 0 18px 40px rgba(90, 48, 28, 0.08);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 26px 52px rgba(90, 48, 28, 0.12);
}

.book-card__cover {
  min-height: 230px;
  padding: 20px;
  color: white;
}

.book-card__cover h3 {
  margin: 70px 0 0;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 34px;
  line-height: 1.04;
}

.book-card__cover p {
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.8);
}

.book-card__body {
  display: grid;
  gap: 14px;
  padding: 18px;
}

.book-card__meta,
.book-card__footer,
.compact-list__item,
.free-list__item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.book-card__meta,
.book-card__footer {
  color: #8c6f61;
}

.book-card__desc {
  color: #6a5348;
  line-height: 1.8;
}

.feature-grid {
  grid-template-columns: 1.1fr 0.9fr;
}

.compact-list {
  display: grid;
  gap: 12px;
  margin-top: 20px;
}

.compact-list__item {
  align-items: center;
  border: 1px solid rgba(127, 63, 44, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  padding: 14px;
  text-align: left;
}

.compact-list__cover {
  height: 64px;
  width: 64px;
  flex: none;
  border-radius: 18px;
}

.compact-list__body {
  flex: 1;
}

.compact-list__body strong {
  display: block;
  color: #281916;
}

.compact-list__body p {
  margin: 8px 0 0;
  color: #84685a;
}

.free-list {
  display: grid;
  gap: 12px;
  margin-top: 20px;
}

.free-list__item {
  flex-direction: column;
  align-items: start;
  border: 1px solid rgba(127, 63, 44, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.74);
  padding: 18px;
  text-align: left;
}

.free-list__item h3 {
  margin: 0;
  color: #281916;
}

.free-list__item p {
  margin: 12px 0 0;
  line-height: 1.8;
  color: #71574b;
}

.free-list__item span {
  margin-top: 14px;
  color: #8c3f2c;
}

.action-primary,
.action-secondary {
  border-radius: 999px;
  padding: 12px 20px;
}

.action-primary {
  border: 0;
  background: linear-gradient(135deg, #201317, #8c3f2c);
  color: white;
}

@media (max-width: 1180px) {
  .home-header__inner,
  .banner-stage,
  .feature-grid,
  .resume-panel {
    grid-template-columns: 1fr;
  }

  .home-header__inner {
    justify-items: start;
  }

  .home-nav {
    justify-content: start;
    flex-wrap: wrap;
  }

  .home-header__actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .search-box {
    flex: 1;
  }

  .search-box input {
    width: 100%;
  }

  .banner-rail {
    flex-direction: column;
  }

  .banner-rail__tabs,
  .insight-strip,
  .book-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .resume-card {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 720px) {
  .page-shell {
    width: min(calc(100vw - 24px), 100%);
  }

  .home-main {
    gap: 16px;
    padding: 16px 0 40px;
  }

  .banner-shell,
  .resume-panel,
  .section-block {
    border-radius: 24px;
    padding: 18px;
  }

  .banner-stage {
    border-radius: 24px;
    padding: 20px;
  }

  .hero-stats,
  .insight-strip,
  .banner-rail__tabs,
  .book-grid,
  .feature-grid {
    grid-template-columns: 1fr;
  }

  .resume-card__info {
    grid-template-columns: 1fr;
  }

  .resume-card__cover strong {
    margin-top: 46px;
  }

  .section-head {
    align-items: start;
    flex-direction: column;
  }
}
</style>
