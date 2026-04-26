<template>
  <div class="library-page">
    <NavBar :is-visible="true" />

    <main class="library-shell">
      <section class="library-head">
        <div>
          <p class="library-eyebrow">ALL STORIES</p>
          <h1>全部作品</h1>
          <p>用接近网文站的筛选方式组织本地 demo 书库，重点展示完整产品框架和阅读动线。</p>
        </div>

        <label class="library-search">
          <span>搜索</span>
          <input v-model="keyword" type="text" placeholder="输入书名、作者或简介关键词" />
        </label>
      </section>

      <section class="filter-panel">
        <div class="filter-row">
          <span>分类</span>
          <button
            v-for="category in categories"
            :key="category"
            :class="{ active: activeCategory === category }"
            @click="activeCategory = category"
          >
            {{ category }}
          </button>
        </div>
        <div class="filter-row">
          <span>状态</span>
          <button
            v-for="status in statuses"
            :key="status"
            :class="{ active: activeStatus === status }"
            @click="activeStatus = status"
          >
            {{ status }}
          </button>
        </div>
        <div class="filter-row">
          <span>属性</span>
          <button
            v-for="access in accessTypes"
            :key="access"
            :class="{ active: activeAccess === access }"
            @click="activeAccess = access"
          >
            {{ access }}
          </button>
        </div>
      </section>

      <section class="library-content">
        <div class="library-toolbar">
          <strong>{{ filteredBooks.length }} 部作品</strong>
          <div>
            <button :class="{ active: sortBy === 'read' }" @click="sortBy = 'read'">热度</button>
            <button :class="{ active: sortBy === 'recommend' }" @click="sortBy = 'recommend'">推荐</button>
            <button :class="{ active: sortBy === 'new' }" @click="sortBy = 'new'">最新</button>
          </div>
        </div>

        <div v-if="loading" class="library-status">正在加载作品...</div>
        <div v-else-if="filteredBooks.length === 0" class="library-status">没有匹配的作品。</div>
        <div v-else class="library-list">
          <article
            v-for="book in sortedBooks"
            :key="book.id"
            class="library-item"
            @click="router.push(`/book/${book.id}`)"
          >
            <div class="library-cover">
              <span>{{ book.category }}</span>
              <strong>{{ book.title.slice(0, 4) }}</strong>
            </div>
            <div class="library-info">
              <div class="library-info__title">
                <h2>{{ book.title }}</h2>
                <span>{{ book.status }}</span>
              </div>
              <p>{{ book.description }}</p>
              <div class="library-meta">
                <span>{{ book.author }}</span>
                <span>{{ formatWordCount(book.word_count) }}</span>
                <span>{{ book.is_free ? '免费' : '精选' }}</span>
                <span>{{ formatCompact(book.read_count) }} 热读</span>
              </div>
            </div>
            <button class="library-action" @click.stop="router.push(`/read/${book.id}/1`)">
              阅读
            </button>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getBooks } from '@/api'
import NavBar from '@/components/NavBar.vue'

type BookRecord = {
  id: number
  title: string
  author: string
  category: string
  description: string
  word_count: number
  recommend_count: number
  read_count: number
  status: string
  is_free: boolean
}

const router = useRouter()
const loading = ref(true)
const books = ref<BookRecord[]>([])
const keyword = ref('')
const activeCategory = ref('全部')
const activeStatus = ref('全部')
const activeAccess = ref('全部')
const sortBy = ref<'read' | 'recommend' | 'new'>('read')

const categories = ['全部', '玄幻', '都市', '科幻', '历史', '言情', '悬疑']
const statuses = ['全部', '连载中', '已完结']
const accessTypes = ['全部', '免费', '精选']

const filteredBooks = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  return books.value.filter((book) => {
    const matchesKeyword = !query || [book.title, book.author, book.description]
      .some((field) => field.toLowerCase().includes(query))
    const matchesCategory = activeCategory.value === '全部' || book.category === activeCategory.value
    const matchesStatus = activeStatus.value === '全部' || book.status === activeStatus.value
    const matchesAccess =
      activeAccess.value === '全部' ||
      (activeAccess.value === '免费' && book.is_free) ||
      (activeAccess.value === '精选' && !book.is_free)
    return matchesKeyword && matchesCategory && matchesStatus && matchesAccess
  })
})

const sortedBooks = computed(() => {
  const list = [...filteredBooks.value]
  if (sortBy.value === 'recommend') {
    return list.sort((a, b) => (b.recommend_count || 0) - (a.recommend_count || 0))
  }
  if (sortBy.value === 'new') {
    return list.sort((a, b) => b.id - a.id)
  }
  return list.sort((a, b) => (b.read_count || 0) - (a.read_count || 0))
})

function formatCompact(value?: number) {
  if (!value) return '0'
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万`
  return value.toLocaleString('zh-CN')
}

function formatWordCount(value?: number) {
  if (!value) return '0字'
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万字`
  return `${value}字`
}

async function loadBooks() {
  loading.value = true
  try {
    const { data } = await getBooks({ page: 1, size: 100 })
    books.value = data.books || []
  } finally {
    loading.value = false
  }
}

onMounted(loadBooks)
</script>

<style scoped>
.library-page {
  min-height: 100vh;
  background: #f8f3ee;
  color: #24191b;
}

.library-shell {
  width: min(1180px, calc(100vw - 32px));
  margin: 0 auto;
  padding: 46px 0 80px;
}

.library-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 360px);
  gap: 24px;
  align-items: end;
  border-bottom: 1px solid rgba(80, 56, 42, 0.14);
  padding-bottom: 28px;
}

.library-eyebrow {
  margin: 0 0 12px;
  color: #9b634d;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.22em;
}

.library-head h1 {
  margin: 0;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: clamp(38px, 6vw, 72px);
}

.library-head p {
  max-width: 640px;
  color: #6b554b;
  line-height: 1.8;
}

.library-search {
  display: grid;
  gap: 8px;
}

.library-search span {
  color: #8d6a59;
  font-size: 13px;
}

.library-search input {
  height: 48px;
  border: 1px solid rgba(80, 56, 42, 0.14);
  border-radius: 8px;
  background: rgba(255, 252, 248, 0.86);
  padding: 0 16px;
  outline: none;
}

.filter-panel,
.library-content {
  border: 1px solid rgba(80, 56, 42, 0.12);
  border-radius: 8px;
  background: rgba(255, 252, 248, 0.78);
}

.filter-panel {
  display: grid;
  gap: 14px;
  margin-top: 24px;
  padding: 20px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-row > span {
  width: 48px;
  color: #8d6a59;
  font-weight: 700;
}

.filter-row button,
.library-toolbar button,
.library-action {
  border: 0;
  border-radius: 999px;
  background: transparent;
  padding: 8px 14px;
  color: #5d463c;
  cursor: pointer;
}

.filter-row button.active,
.library-toolbar button.active {
  background: #8c3f2c;
  color: white;
}

.library-content {
  margin-top: 18px;
  overflow: hidden;
}

.library-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(80, 56, 42, 0.1);
  padding: 18px 20px;
}

.library-toolbar div {
  display: flex;
  gap: 8px;
}

.library-status {
  padding: 60px 20px;
  color: #8d6a59;
  text-align: center;
}

.library-list {
  display: grid;
}

.library-item {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  border-bottom: 1px solid rgba(80, 56, 42, 0.08);
  padding: 18px 20px;
  cursor: pointer;
}

.library-item:hover {
  background: rgba(248, 240, 232, 0.68);
}

.library-cover {
  display: grid;
  height: 108px;
  align-content: space-between;
  border-radius: 8px;
  background: linear-gradient(145deg, #3a2724, #b06a4c);
  padding: 12px;
  color: white;
}

.library-cover span {
  font-size: 12px;
  opacity: 0.72;
}

.library-cover strong {
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  line-height: 1.2;
}

.library-info__title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.library-info h2 {
  margin: 0;
  font-size: 20px;
}

.library-info__title span {
  border-radius: 999px;
  background: rgba(140, 63, 44, 0.1);
  padding: 4px 10px;
  color: #8c3f2c;
  font-size: 12px;
}

.library-info p {
  display: -webkit-box;
  margin: 10px 0;
  overflow: hidden;
  color: #6b554b;
  line-height: 1.7;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.library-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  color: #8d6a59;
  font-size: 13px;
}

.library-action {
  background: #24191b;
  color: white;
}

@media (max-width: 780px) {
  .library-head,
  .library-item {
    grid-template-columns: 1fr;
  }

  .library-toolbar {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
  }

  .library-cover {
    width: 82px;
  }
}
</style>
