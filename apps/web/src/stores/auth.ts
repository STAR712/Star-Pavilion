import { defineStore } from 'pinia'
import { clearAuthToken, getMe, login as apiLogin, register as apiRegister, setAuthToken } from '@/api'

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
    setSession(payload: { token: string; user: any }) {
      this.token = payload.token
      this.user = payload.user
      setAuthToken(payload.token)
    },
    async hydrateSession() {
      if (this.initialized) return
      this.initialized = true
      if (!this.token) {
        clearAuthToken()
        return
      }
      setAuthToken(this.token)
      if (!this.user) {
        try {
          const { data } = await getMe()
          this.user = data
        } catch {
          this.logout()
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
    logout() {
      this.token = ''
      this.user = null
      clearAuthToken()
    },
  },
  persist: true,
})
