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
          <input
            v-model="fields.username.value"
            type="text"
            placeholder="3 个字符以上"
            @blur="touchField('username')"
          />
          <p v-if="fields.username.touched && fields.username.error" class="auth-field__error">{{ fields.username.error }}</p>
        </label>
        <label class="auth-field">
          <span>密码</span>
          <input
            v-model="fields.password.value"
            type="password"
            placeholder="至少 6 位，包含字母和数字"
            @blur="touchField('password')"
          />
          <p v-if="fields.password.touched && fields.password.error" class="auth-field__error">{{ fields.password.error }}</p>
        </label>
        <label class="auth-field">
          <span>确认密码</span>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="再次输入密码"
            @blur="confirmError = validateConfirmPassword()"
          />
          <p v-if="confirmError" class="auth-field__error">{{ confirmError }}</p>
        </label>

        <button class="auth-submit" :disabled="submitting">
          {{ submitting ? '注册中…' : '注册并登录' }}
        </button>

        <p v-if="submitError" class="auth-submit__error">{{ submitError }}</p>

        <p class="auth-switch">
          已有账号？
          <router-link :to="loginLink">去登录</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFormValidation } from '@/composables/useFormValidation'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const confirmPassword = ref('')

const { fields, validateAll, touchField, reset } = useFormValidation({
  username: [
    { required: true, message: '请输入用户名' },
    { minLength: 2, message: '用户名至少 2 个字符' },
    { maxLength: 20, message: '用户名不超过 20 个字符' },
    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { minLength: 6, message: '密码至少 6 个字符' },
    {
      validate: (value: string) => {
        if (!/[A-Z]/.test(value) && !/[a-z]/.test(value)) return '密码需要包含字母'
        if (!/[0-9]/.test(value)) return '密码需要包含数字'
        return true
      },
      message: '密码需要包含字母和数字',
    },
  ],
})

const submitting = ref(false)
const submitError = ref('')

const loginLink = computed(() => ({
  path: '/login',
  query: route.query.redirect ? { redirect: String(route.query.redirect) } : {},
}))

function validateConfirmPassword(): string {
  if (!confirmPassword.value.trim()) return '请确认密码'
  if (confirmPassword.value !== fields.password.value) return '两次输入的密码不一致'
  return ''
}

const confirmError = ref('')

async function handleSubmit() {
  submitError.value = ''
  confirmError.value = validateConfirmPassword()
  if (confirmError.value) return
  if (!validateAll()) return

  submitting.value = true
  try {
    await authStore.register({
      username: fields.username.value.trim(),
      password: fields.password.value,
    })
    router.replace(String(route.query.redirect || '/bookshelf'))
  } catch (error: any) {
    const detail = error?.response?.data?.detail
    if (detail) {
      if (detail.includes('用户名')) {
        fields.username.error = detail
        fields.username.touched = true
      } else if (detail.includes('密码')) {
        fields.password.error = detail
        fields.password.touched = true
      } else {
        submitError.value = detail
      }
    } else {
      submitError.value = '注册失败，请检查后端服务是否为当前项目实例'
    }
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

.auth-field__error {
  margin: 4px 0 0;
  font-size: 12px;
  color: #c44040;
}

.auth-field input.auth-field--error {
  border-color: rgba(196, 64, 64, 0.4);
}

.auth-submit {
  height: 52px;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(135deg, #201317, #8c3f2c);
  color: white;
}

.auth-submit__error {
  margin: -6px 0 0;
  font-size: 13px;
  color: #c44040;
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
