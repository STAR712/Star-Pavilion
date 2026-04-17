import axios from 'axios'

export const AUTH_TOKEN_KEY = 'star-pavilion-auth-token'

const api = axios.create({
  baseURL: '',
  timeout: 10000,
})

export function getStoredToken() {
  if (typeof window === 'undefined') return ''
  return window.localStorage.getItem(AUTH_TOKEN_KEY) || ''
}

export function setAuthToken(token: string) {
  if (typeof window === 'undefined') return
  if (token) {
    window.localStorage.setItem(AUTH_TOKEN_KEY, token)
  } else {
    window.localStorage.removeItem(AUTH_TOKEN_KEY)
  }
}

export function clearAuthToken() {
  setAuthToken('')
}

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  } else if (config.headers?.Authorization) {
    delete config.headers.Authorization
  }
  return config
})

// 用户系统
export const login = (payload: { username: string; password: string }) =>
  api.post('/api/auth/login', payload)

export const register = (payload: { username: string; password: string }) =>
  api.post('/api/auth/register', payload)

export const getMe = () => api.get('/api/auth/me')

// 获取书籍列表
export const getBooks = (params?: { category?: string; page?: number; size?: number }) =>
  api.get('/api/books', { params })

// 获取书籍详情
export const getBookDetail = (id: number) => api.get(`/api/books/${id}`)

// 获取章节列表
export const getChapters = (bookId: number) => api.get(`/api/books/${bookId}/chapters`)

// 获取章节内容
export const getChapterContent = (bookId: number, chapterNum: number) =>
  api.get(`/api/books/${bookId}/chapters/${chapterNum}`)

// 获取书架
export const getBookshelf = () => api.get('/api/bookshelf')

// 加入书架
export const addToBookshelf = (bookId: number) => api.post('/api/bookshelf', { book_id: bookId })

// 更新阅读进度
export const updateProgress = (bookId: number, chapter: number, progress: number) =>
  api.put(`/api/bookshelf/${bookId}`, { current_chapter: chapter, progress })

// 移出书架
export const removeFromBookshelf = (bookId: number) => api.delete(`/api/bookshelf/${bookId}`)

// SSE 流式对话
export const streamChat = (
  messages: Array<{ role: string; content: string }>,
  bookId?: number,
  chapterId?: number,
  allowSpoiler: boolean = false,
) => {
  const token = getStoredToken()
  return fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      messages,
      book_id: bookId,
      chapter_id: chapterId,
      search_all: allowSpoiler,
    }),
  })
}

export default api
