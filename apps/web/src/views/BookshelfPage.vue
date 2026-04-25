<template>
  <div class="shelf-shell">
    <header class="shelf-header">
      <div class="page-shell shelf-header__inner">
        <router-link to="/" class="shelf-brand">Star Pavilion</router-link>
        <div class="shelf-header__actions">
          <router-link to="/" class="header-link">首页</router-link>
          <router-link to="/rank" class="header-link">排行榜</router-link>
          <button v-if="authStore.isAuthenticated" class="header-link" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </header>

    <main class="page-shell shelf-main">
      <section class="shelf-hero">
        <div>
          <p class="section-eyebrow">MY BOOKSHELF</p>
          <h1>我的书架</h1>
          <p class="section-copy">
            这里会实时同步当前登录用户加入书架的小说与阅读进度。
          </p>
        </div>
        <div class="shelf-meta">
          <strong>{{ bookshelfStore.books.length }}</strong>
          <span>本在架作品</span>
        </div>
      </section>

      <section v-if="!authStore.isAuthenticated" class="empty-panel">
        <p>登录后即可查看和同步你的书架。</p>
        <router-link class="action-primary" to="/login?redirect=/bookshelf">去登录</router-link>
      </section>

      <section v-else-if="bookshelfStore.books.length === 0" class="empty-panel">
        <p>书架还是空的，先去首页挑一本到书架里吧。</p>
        <router-link class="action-primary" to="/">去首页选书</router-link>
      </section>

      <section v-else-if="bookshelfStore.books.length > 0" class="shelf-grid">
        <article
          v-for="item in bookshelfStore.books"
          :key="item.id"
          class="shelf-card"
        >
          <button class="shelf-card__cover" @click="continueReading(item)">
            <span>{{ item.book_category || '小说' }}</span>
            <h2>{{ item.book_title }}</h2>
            <p>{{ item.book_author }}</p>
          </button>

          <div class="shelf-card__body">
            <p class="shelf-card__desc">
              {{ item.book_description || '这本书正在等待你继续翻页。' }}
            </p>

            <div class="shelf-card__progress">
              <div class="shelf-card__bar">
                <span :style="{ width: `${Math.min(100, Math.max(0, Number(item.progress || 0)))}%` }"></span>
              </div>
              <strong>第 {{ item.current_chapter }} 章 · {{ Math.round(item.progress || 0) }}%</strong>
            </div>

            <div class="shelf-card__actions">
              <button class="action-primary" @click="continueReading(item)">继续阅读</button>
              <button class="action-secondary" @click="removeBook(item.book_id)">移出书架</button>
            </div>
          </div>
        </article>
      </section>

      <section v-else class="shelf-grid">
        <SkeletonList :count="3" />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBookshelfStore } from '@/stores/bookshelf'
import SkeletonList from '@/components/SkeletonList.vue'

const router = useRouter()
const authStore = useAuthStore()
const bookshelfStore = useBookshelfStore()

function continueReading(item: any) {
  router.push(`/read/${item.book_id}/${item.current_chapter || 1}`)
}

async function removeBook(bookId: number) {
  await bookshelfStore.removeBook(bookId)
}

function handleLogout() {
  authStore.logout()
  bookshelfStore.clearBooks()
  router.push('/')
}

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await bookshelfStore.fetchBookshelf()
  }
})
</script>

<style scoped>
.shelf-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(255, 215, 184, 0.26), transparent 24%),
    linear-gradient(180deg, #fbf6ef 0%, #f1e7dc 100%);
}

.page-shell {
  width: min(1280px, calc(100vw - 32px));
  margin: 0 auto;
}

.shelf-header {
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid rgba(126, 84, 60, 0.12);
  background: rgba(253, 248, 242, 0.82);
  backdrop-filter: blur(18px);
}

.shelf-header__inner {
  display: flex;
  min-height: 72px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.shelf-brand {
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 30px;
  color: #2a1b16;
  text-decoration: none;
}

.shelf-header__actions {
  display: flex;
  gap: 10px;
}

.header-link {
  border-radius: 999px;
  border: 1px solid rgba(127, 63, 44, 0.14);
  background: rgba(255, 255, 255, 0.74);
  padding: 10px 16px;
  color: #7b4f3d;
  text-decoration: none;
}

.shelf-main {
  padding: 28px 0 54px;
}

.shelf-hero,
.empty-panel,
.shelf-card {
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 30px;
  background: rgba(255, 252, 248, 0.82);
  box-shadow: 0 24px 60px rgba(95, 58, 39, 0.08);
}

.shelf-hero {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
  padding: 28px;
}

.section-eyebrow {
  font-size: 11px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: #9c6b4c;
}

.shelf-hero h1 {
  margin-top: 10px;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: clamp(2.2rem, 4vw, 4rem);
  color: #271914;
}

.section-copy {
  margin-top: 14px;
  line-height: 1.9;
  color: #6c564a;
}

.shelf-meta {
  min-width: 180px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.76);
  padding: 20px;
  text-align: center;
}

.shelf-meta strong {
  display: block;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 40px;
  color: #2a1b16;
}

.shelf-meta span {
  color: #8d6f60;
}

.empty-panel {
  margin-top: 22px;
  display: grid;
  gap: 14px;
  justify-items: start;
  padding: 24px;
  color: #6d584d;
}

.shelf-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 22px;
}

.shelf-card {
  overflow: hidden;
}

.shelf-card__cover {
  display: flex;
  min-height: 220px;
  width: 100%;
  flex-direction: column;
  justify-content: space-between;
  border: 0;
  background: linear-gradient(135deg, #231519, #8f452f 55%, #d78a61);
  padding: 20px;
  color: white;
  text-align: left;
}

.shelf-card__cover h2 {
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 34px;
  line-height: 1.06;
}

.shelf-card__body {
  padding: 18px;
}

.shelf-card__desc {
  color: #684f44;
  line-height: 1.85;
}

.shelf-card__progress {
  margin-top: 18px;
}

.shelf-card__bar {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #f0dfd1;
}

.shelf-card__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #8c3f2c, #e48d5d);
}

.shelf-card__progress strong {
  display: block;
  margin-top: 10px;
  color: #785c4e;
}

.shelf-card__actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.action-primary,
.action-secondary {
  border-radius: 999px;
  padding: 11px 18px;
  text-decoration: none;
}

.action-primary {
  border: 0;
  background: linear-gradient(135deg, #201317, #8c3f2c);
  color: white;
}

.action-secondary {
  border: 1px solid rgba(127, 63, 44, 0.16);
  background: rgba(255, 255, 255, 0.84);
  color: #7f3f2c;
}

@media (max-width: 1024px) {
  .shelf-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .page-shell {
    width: min(100vw - 24px, 1280px);
  }

  .shelf-header__inner,
  .shelf-hero,
  .shelf-card__actions {
    flex-direction: column;
    align-items: start;
  }

  .shelf-grid {
    grid-template-columns: 1fr;
  }
}
</style>
