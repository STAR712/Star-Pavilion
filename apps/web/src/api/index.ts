import axios from 'axios'

// ===== access_token 仅存内存（刷新页面后丢失，通过 refresh_token 自动续期） =====
let accessToken: string | null = null

export function setAccessToken(token: string) {
  accessToken = token
}

export function getAccessToken(): string | null {
  return accessToken
}

export function clearAccessToken() {
  accessToken = null
}

// ===== Axios 实例 =====
const api = axios.create({
  baseURL: '',
  timeout: 10000,
})

// ===== 请求拦截器：从内存取 token 注入 Authorization =====
api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

// ===== 响应拦截器：401 无感刷新 =====
let isRefreshing = false
let pendingRequests: Array<{ resolve: (value: unknown) => void; config: any }> = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // 401 且未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      // 如果是 refresh 接口本身返回 401，直接登出
      if (originalRequest.url?.includes('/auth/refresh')) {
        clearAccessToken()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // 其他请求排队等待刷新完成
        return new Promise((resolve) => {
          pendingRequests.push({ resolve, config: originalRequest })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // refresh_token 在 HttpOnly Cookie 中，浏览器自动携带
        const { data } = await axios.post('/api/auth/refresh', null, {
          withCredentials: true,
        })
        accessToken = data.access_token

        // 重发所有排队的请求
        pendingRequests.forEach(({ resolve, config }) => {
          config.headers.Authorization = `Bearer ${accessToken}`
          resolve(api(config))
        })
        pendingRequests = []

        // 重发原始请求
        return api(originalRequest)
      } catch {
        // refresh 也失败 → 清除状态 → 跳转登录页
        clearAccessToken()
        window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

// ===== 用户系统 API =====
export const login = (payload: { username: string; password: string }) =>
  api.post('/api/auth/login', payload)

export const register = (payload: { username: string; password: string }) =>
  api.post('/api/auth/register', payload)

export const getMe = () => api.get('/api/auth/me')

export const logout = () =>
  api.post('/api/auth/logout', null, { withCredentials: true })

// ===== 书籍 API =====
export const getBooks = (params?: { category?: string; page?: number; size?: number }) =>
  api.get('/api/books', { params })

export const getBookDetail = (id: number) => api.get(`/api/books/${id}`)

export const getChapters = (bookId: number) => api.get(`/api/books/${bookId}/chapters`)

export const getChapterContent = (bookId: number, chapterNum: number) =>
  api.get(`/api/books/${bookId}/chapters/${chapterNum}`)

// ===== 书架 API =====
export const getBookshelf = () => api.get('/api/bookshelf')

export const addToBookshelf = (bookId: number) => api.post('/api/bookshelf', { book_id: bookId })

export const updateProgress = (bookId: number, chapter: number, progress: number) =>
  api.put(`/api/bookshelf/${bookId}`, { current_chapter: chapter, progress })

export const removeFromBookshelf = (bookId: number) => api.delete(`/api/bookshelf/${bookId}`)

// ===== SSE 流式对话（使用原生 fetch，手动注入内存中的 token） =====
export const streamChat = (
  messages: Array<{ role: string; content: string }>,
  bookId?: number,
  chapterId?: number,
  allowSpoiler: boolean = false,
  conversationId?: number | null,
) => {
  return fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify({
      messages,
      book_id: bookId,
      chapter_id: chapterId,
      search_all: allowSpoiler,
      ...(conversationId ? { conversation_id: conversationId } : {}),
    }),
  })
}

// ===== 会话 API =====
export const getConversations = (params?: { book_id?: number }) =>
  api.get('/api/conversations', { params })

export const createConversation = (data: { book_id?: number; chapter_id?: number; name?: string }) =>
  api.post('/api/conversations', data)

export const getConversation = (id: number) =>
  api.get(`/api/conversations/${id}`)

export const updateConversation = (id: number, data: { messages?: Array<{ role: string; content: string }>; name?: string }) =>
  api.put(`/api/conversations/${id}`, data)

export const deleteConversation = (id: number) =>
  api.delete(`/api/conversations/${id}`)

export default api
