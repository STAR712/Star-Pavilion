import { defineStore } from 'pinia'
import axios from 'axios'
import { clearAccessToken, getMe, login as apiLogin, logout as apiLogout, register as apiRegister, setAccessToken } from '@/api'

type AuthSessionPayload = {
  access_token?: string
  token?: string
  user: any
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: '',
    user: null as null | {
      id: number
      username: string
      role: string
      avatar?: string
      created_at?: string | null
    },
    loading: false,
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user),
  },
  actions: {
    setSession(payload: AuthSessionPayload) {
      const accessToken = payload.access_token || payload.token || ''
      this.token = accessToken
      this.user = payload.user
      setAccessToken(accessToken)
    },
    async hydrateSession() {
      // 兼容旧版后端：如果 persisted state 里已有 token，先恢复到内存。
      if (this.token) {
        setAccessToken(this.token)
      }

      if (this.initialized) return
      this.initialized = true

      // 兼容旧版 token-only 鉴权：有 token 但没有 user 时，主动拉一次用户信息。
      if (this.token && !this.user) {
        try {
          const { data } = await getMe()
          this.user = data
          return
        } catch {
          this.token = ''
          clearAccessToken()
        }
      }

      // 新版后端：通过 HttpOnly refresh_token 静默续期。
      if (!this.user) {
        try {
          const { data } = await axios.post('/api/auth/refresh', null, {
            withCredentials: true,
          })
          this.setSession(data)
        } catch {
          // refresh 失败，保持未登录状态
          this.token = ''
          this.user = null
        }
      }
    },
    async login(payload: { username: string; password: string }) {
      this.loading = true
      try {
        const { data } = await apiLogin(payload)
        this.setSession(data)
        return data
      } finally {
        this.loading = false
      }
    },
    async register(payload: { username: string; password: string }) {
      this.loading = true
      try {
        const { data } = await apiRegister(payload)
        this.setSession(data)
        return data
      } finally {
        this.loading = false
      }
    },
    async logout() {
      // 调用后端 logout（将 refresh_token 加入黑名单 + 清除 Cookie）
      try {
        await apiLogout()
      } catch {
        // 忽略网络错误
      }
      this.token = ''
      this.user = null
      this.initialized = false
      clearAccessToken()
    },
  },
  persist: {
    paths: ['token', 'user'],
  },
})
