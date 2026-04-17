<template>
  <div class="auth-shell">
    <div class="auth-panel">
      <div class="auth-panel__intro">
        <router-link to="/" class="auth-back">返回首页</router-link>
        <p class="auth-eyebrow">REGISTER</p>
        <h1>创建新的阅读账户</h1>
        <p class="auth-copy">
          注册后即可拥有自己的书架、阅读进度和跨页面同步的登录状态。
        </p>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <label class="auth-field">
          <span>用户名</span>
          <input v-model="form.username" type="text" placeholder="3 个字符以上" />
        </label>
        <label class="auth-field">
          <span>密码</span>
          <input v-model="form.password" type="password" placeholder="设置密码" />
        </label>
        <label class="auth-field">
          <span>确认密码</span>
          <input v-model="form.confirmPassword" type="password" placeholder="再次输入密码" />
        </label>

        <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

        <button class="auth-submit" :disabled="submitting">
          {{ submitting ? '注册中…' : '注册并登录' }}
        </button>

        <p class="auth-switch">
          已有账号？
          <router-link :to="loginLink">去登录</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

const submitting = ref(false)
const errorMessage = ref('')

const loginLink = computed(() => ({
  path: '/login',
  query: route.query.redirect ? { redirect: String(route.query.redirect) } : {},
}))

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.username.trim() || !form.password.trim()) {
    errorMessage.value = '请完整填写注册信息'
    return
  }
  if (form.password !== form.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  submitting.value = true
  try {
    await authStore.register({
      username: form.username.trim(),
      password: form.password,
    })
    router.replace(String(route.query.redirect || '/bookshelf'))
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || '注册失败，请稍后重试'
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
    radial-gradient(circle at top right, rgba(220, 197, 176, 0.24), transparent 28%),
    linear-gradient(180deg, #f8f3ee 0%, #efe4d8 100%);
  padding: 24px;
}

.auth-panel {
  display: grid;
  width: min(920px, 100%);
  grid-template-columns: minmax(0, 1fr) 400px;
  overflow: hidden;
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 34px;
  background: rgba(255, 251, 247, 0.84);
  box-shadow: 0 26px 60px rgba(96, 60, 42, 0.1);
  backdrop-filter: blur(16px);
}

.auth-panel__intro,
.auth-form {
  padding: 34px;
}

.auth-panel__intro {
  background:
    radial-gradient(circle at top left, rgba(232, 161, 115, 0.18), transparent 34%),
    rgba(255, 251, 247, 0.68);
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
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1.08;
  color: #261914;
}

.auth-copy {
  margin-top: 18px;
  color: #6a5549;
  line-height: 1.9;
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
