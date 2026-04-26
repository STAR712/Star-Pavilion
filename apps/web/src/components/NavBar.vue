<template>
  <nav
    class="nav-shell"
    :class="isVisible ? 'nav-shell--visible' : 'nav-shell--hidden'"
  >
    <div class="nav-shell__inner">
      <router-link to="/" class="nav-brand">
        <span class="nav-brand__mark">星</span>
        <span>
          <strong>Star Pavilion</strong>
          <small>FICTION SALON</small>
        </span>
      </router-link>

      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/library" class="nav-link">全部作品</router-link>
        <router-link to="/rank" class="nav-link">排行榜</router-link>
        <router-link to="/author" class="nav-link">作家专区</router-link>
        <router-link to="/bookshelf" class="nav-link">我的书架</router-link>
      </div>

      <div class="nav-actions">
        <label class="nav-search">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索小说..."
            @keyup.enter="handleSearch"
          />
        </label>

        <template v-if="authStore.isAuthenticated">
          <router-link to="/bookshelf" class="nav-pill nav-pill--accent">
            书架 {{ bookshelfStore.books.length }}
          </router-link>
          <span class="nav-user">{{ authStore.user?.username }}</span>
          <button class="nav-pill" @click="handleLogout">退出</button>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-pill">登录</router-link>
          <router-link to="/register" class="nav-pill nav-pill--accent">注册</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBookshelfStore } from '@/stores/bookshelf'

defineProps<{
  isVisible: boolean
}>()

const router = useRouter()
const authStore = useAuthStore()
const bookshelfStore = useBookshelfStore()
const searchQuery = ref('')

function handleSearch() {
  router.push({
    path: '/',
    query: searchQuery.value.trim() ? { q: searchQuery.value.trim() } : {},
  })
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
.nav-shell {
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(26, 21, 21, 0.86);
  backdrop-filter: blur(20px);
  transition: transform 0.3s ease;
}

.nav-shell--visible {
  transform: translateY(0);
}

.nav-shell--hidden {
  transform: translateY(-100%);
}

.nav-shell__inner {
  width: min(1280px, calc(100vw - 32px));
  min-height: 76px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
}

.nav-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: white;
  text-decoration: none;
}

.nav-brand__mark {
  display: grid;
  height: 40px;
  width: 40px;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(135deg, #bf7350, #f0c088);
  color: #201317;
  font-weight: 700;
}

.nav-brand strong,
.nav-brand small {
  display: block;
}

.nav-brand strong {
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 24px;
}

.nav-brand small {
  margin-top: 4px;
  letter-spacing: 0.24em;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.58);
}

.nav-links,
.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-links {
  justify-content: center;
}

.nav-link,
.nav-pill {
  border-radius: 999px;
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.82);
  text-decoration: none;
}

.nav-link:hover,
.nav-pill:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

.nav-pill {
  border: 0;
  background: rgba(255, 255, 255, 0.08);
}

.nav-pill--accent {
  background: linear-gradient(135deg, #bf7350, #f0c088);
  color: #201317;
}

.nav-search input {
  height: 42px;
  min-width: 200px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  padding: 0 16px;
  color: white;
  outline: none;
}

.nav-search input::placeholder {
  color: rgba(255, 255, 255, 0.44);
}

.nav-user {
  color: rgba(255, 255, 255, 0.68);
}

@media (max-width: 1100px) {
  .nav-shell__inner {
    grid-template-columns: 1fr;
    justify-items: start;
    padding: 14px 0;
  }

  .nav-links,
  .nav-actions {
    flex-wrap: wrap;
  }

  .nav-links {
    justify-content: start;
  }

  .nav-search {
    width: 100%;
  }

  .nav-search input {
    width: 100%;
  }
}
</style>
