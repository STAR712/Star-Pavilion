<template>
  <div class="auth-shell">
    <div class="auth-panel">
      <div class="auth-panel__intro">
        <router-link to="/" class="auth-back">返回首页</router-link>
        <p class="auth-eyebrow">LOGIN</p>
        <h1>登录你的阅读身份</h1>
        <p class="auth-copy">
          登录后可以同步书架、保存阅读进度，并让 AI 助手记住你的上下文。
        </p>
        <div class="auth-tip">
          <strong>预设管理员账号</strong>
          <span>账号 `admin`，密码 `123`</span>
        </div>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <label class="auth-field">
          <span>用户名</span>
          <input v-model="form.username" type="text" placeholder="输入用户名" />
        </label>
        <label class="auth-field">
          <span>密码</span>
          <input v-model="form.password" type="password" placeholder="输入密码" />
        </label>

        <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

        <button class="auth-submit" :disabled="submitting">
          {{ submitting ? '登录中…' : '登录' }}
        </button>

        <p class="auth-switch">
          还没有账号？
          <router-link :to="registerLink">去注册</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBookshelfStore } from '@/stores/bookshelf'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const bookshelfStore = useBookshelfStore()

const form = reactive({
  username: '',
  password: '',
})

const submitting = ref(false)
const errorMessage = ref('')

const registerLink = computed(() => ({
  path: '/register',
  query: route.query.redirect ? { redirect: String(route.query.redirect) } : {},
}))

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.username.trim() || !form.password.trim()) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  submitting.value = true
  try {
    await authStore.login({
      username: form.username.trim(),
      password: form.password,
    })
    await bookshelfStore.fetchBookshelf()
    router.replace(String(route.query.redirect || '/bookshelf'))
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || '登录失败，请检查账号或密码'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-shell {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background:
    radial-gradient(circle at top left, rgba(255, 220, 186, 0.32), transparent 26%),
    linear-gradient(180deg, #f9f4ee 0%, #f0e6db 100%);
  padding: 24px;
}

.auth-panel {
  display: grid;
  width: min(980px, 100%);
  grid-template-columns: minmax(0, 1fr) 380px;
  overflow: hidden;
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 34px;
  background: rgba(255, 251, 247, 0.84);
  box-shadow: 0 26px 60px rgba(96, 60, 42, 0.1);
  backdrop-filter: blur(16px);
}

.auth-panel__intro,
.auth-form {
  padding: 36px;
}

.auth-panel__intro {
  background:
    radial-gradient(circle at top right, rgba(232, 161, 115, 0.22), transparent 35%),
    rgba(255, 251, 247, 0.72);
}

.auth-back {
  color: #7a4d3b;
  text-decoration: none;
}

.auth-eyebrow {
  margin-top: 26px;
  font-size: 11px;
  letter-spacing: 0.3em;
  color: #a67255;
}

.auth-panel__intro h1 {
  margin-top: 14px;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: clamp(2rem, 4vw, 3.6rem);
  line-height: 1.08;
  color: #261914;
}

.auth-copy {
  margin-top: 18px;
  color: #6a5549;
  line-height: 1.9;
}

.auth-tip {
  margin-top: 28px;
  display: grid;
  gap: 8px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.74);
  padding: 18px;
  color: #6d5448;
}

.auth-tip strong {
  color: #2b1c17;
}

.auth-form {
  display: grid;
  gap: 18px;
  align-content: center;
}

.auth-field {
  display: grid;
  gap: 10px;
}

.auth-field span {
  font-size: 14px;
  color: #866656;
}

.auth-field input {
  height: 52px;
  border: 1px solid rgba(129, 96, 75, 0.14);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  padding: 0 16px;
  color: #261914;
  outline: none;
}

.auth-field input:focus {
  border-color: rgba(140, 63, 44, 0.35);
}

.auth-error {
  border-radius: 16px;
  background: rgba(197, 75, 75, 0.08);
  padding: 12px 14px;
  color: #a43737;
}

.auth-submit {
  height: 52px;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(135deg, #201317, #8c3f2c);
  color: white;
}

.auth-submit:disabled {
  opacity: 0.6;
}

.auth-switch {
  color: #7b5f52;
}

.auth-switch a {
  color: #8c3f2c;
  text-decoration: none;
}

@media (max-width: 860px) {
  .auth-panel {
    grid-template-columns: 1fr;
  }

  .auth-panel__intro,
  .auth-form {
    padding: 24px;
  }
}
</style>
